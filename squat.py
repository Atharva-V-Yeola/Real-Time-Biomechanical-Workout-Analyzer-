import cv2
import mediapipe as mp
import pyttsx3
import time
import numpy as np

engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

SETS = 3
REPS_PER_SET = 15
REST_TIME = 60

STANDING_KNEE_MIN = 160
STANDING_KNEE_MAX = 180
SQUAT_KNEE_MIN = 90
SQUAT_KNEE_MAX = 120

TORSO_MIN = 140
TORSO_MAX = 190

HEEL_ANKLE_KNEE_MIN = 150
HEEL_ANKLE_KNEE_MAX = 165

current_set = 1
total_reps = 0
is_resting = False
rest_started = None

squat_position = "UP"
rule1_passed = False
rule2_passed = False
rule3_passed = False

speak("Starting squat counter")

def get_angle(point_a, point_b, point_c):
    point_a = np.array([point_a.x, point_a.y])
    point_b = np.array([point_b.x, point_b.y])
    point_c = np.array([point_c.x, point_c.y])
    
    vector_ba = point_a - point_b
    vector_bc = point_c - point_b
    
    dot_product = np.dot(vector_ba, vector_bc)
    magnitude = np.linalg.norm(vector_ba) * np.linalg.norm(vector_bc)
    cos_value = dot_product / magnitude
    cos_value = np.clip(cos_value, -1.0, 1.0)
    angle_rad = np.arccos(cos_value)
    
    return np.degrees(angle_rad)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(frame_rgb)
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        if pose_results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            body_points = pose_results.pose_landmarks.landmark

            hip_point = body_points[mp_pose.PoseLandmark.LEFT_HIP]
            knee_point = body_points[mp_pose.PoseLandmark.LEFT_KNEE]
            ankle_point = body_points[mp_pose.PoseLandmark.LEFT_ANKLE]
            shoulder_point = body_points[mp_pose.PoseLandmark.LEFT_SHOULDER]
            ear_point = body_points[mp_pose.PoseLandmark.LEFT_EAR]
            heel_point = body_points[mp_pose.PoseLandmark.LEFT_HEEL]

            knee_angle = get_angle(hip_point, knee_point, ankle_point)
            torso_angle = get_angle(hip_point, shoulder_point, ear_point)
            heel_angle = get_angle(heel_point, ankle_point, knee_point)

            now = time.time()

            if is_resting:
                time_left = int(REST_TIME - (now - rest_started))
                
                cv2.putText(frame, f"Rest: {time_left}s", 
                           (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)
                
                if now - rest_started >= REST_TIME:
                    is_resting = False
                    speak(f"Starting set {current_set}")

            else:
                if squat_position == "UP":
                    if knee_angle < 140:
                        squat_position = "DOWN"
                        rule1_passed = False
                        rule2_passed = False
                        rule3_passed = False

                elif squat_position == "DOWN":
                    if SQUAT_KNEE_MIN <= knee_angle <= SQUAT_KNEE_MAX:
                        rule1_passed = True
                    
                    if TORSO_MIN <= torso_angle <= TORSO_MAX:
                        rule2_passed = True
                    
                    if HEEL_ANKLE_KNEE_MIN <= heel_angle <= HEEL_ANKLE_KNEE_MAX:
                        rule3_passed = True

                    if knee_angle > 155:
                        if rule1_passed and rule2_passed and rule3_passed:
                            total_reps += 1
                            speak(f"Rep {total_reps % REPS_PER_SET or REPS_PER_SET}")
                            
                            if total_reps % REPS_PER_SET == 0:
                                current_set += 1
                                if current_set > SETS:
                                    speak("All sets done")
                                    break
                                else:
                                    is_resting = True
                                    rest_started = now
                                    speak(f"Set {current_set - 1} finished. Rest now.")
                        
                        squat_position = "UP"

            line_y = 50
            cv2.putText(frame, f"Set: {current_set}/{SETS} | Rep: {total_reps % REPS_PER_SET}/{REPS_PER_SET}", 
                       (50, line_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            line_y += 50
            cv2.putText(frame, f"Position: {squat_position}", 
                       (50, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            line_y += 45
            color1 = (0, 255, 0) if rule1_passed else (255, 255, 255)
            cv2.putText(frame, f"Knee: {knee_angle:.1f}° [{SQUAT_KNEE_MIN}-{SQUAT_KNEE_MAX}]", 
                       (50, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color1, 2)
            
            line_y += 35
            color2 = (0, 255, 0) if rule2_passed else (255, 255, 255)
            cv2.putText(frame, f"Torso: {torso_angle:.1f}° [{TORSO_MIN}-{TORSO_MAX}]", 
                       (50, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color2, 2)
            
            line_y += 35
            color3 = (0, 255, 0) if rule3_passed else (255, 255, 255)
            cv2.putText(frame, f"Heel-Ankle-Knee: {heel_angle:.1f}° [{HEEL_ANKLE_KNEE_MIN}-{HEEL_ANKLE_KNEE_MAX}]", 
                       (50, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color3, 2)

        cv2.imshow('Squat Counter', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
speak(f"Finished. Total reps: {total_reps}")
