import cv2
import mediapipe as mp
from utils.angles import calculate_angle
from utils.landmarks import LANDMARKS

class PoseDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if not results.pose_landmarks:
            return bgr, None

        self.mp_drawing.draw_landmarks(
            bgr, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
        )

        landmarks = results.pose_landmarks.landmark
        try:
            hip = landmarks[LANDMARKS['hip']]
            knee = landmarks[LANDMARKS['knee']]
            ankle = landmarks[LANDMARKS['ankle']]
            shoulder = landmarks[LANDMARKS['shoulder']]
            ear = landmarks[LANDMARKS['ear']]
            heel = landmarks[LANDMARKS['heel']]

            knee_angle = calculate_angle(hip, knee, ankle)
            torso_angle = calculate_angle(hip, shoulder, ear)
            heel_angle = calculate_angle(heel, ankle, knee)

            return bgr, {
                'knee_angle': knee_angle,
                'torso_angle': torso_angle,
                'heel_angle': heel_angle
            }
        except (IndexError, AttributeError):
            return bgr, None
