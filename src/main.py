import cv2
import time
import sys
from pathlib import Path
from .pose_detector import PoseDetector
from .form_evaluator import SquatEvaluator
from .feedback import FeedbackSystem

def main(video_path: str = "demo/sample_squat.mp4"):
    detector = PoseDetector()
    evaluator = SquatEvaluator()
    feedback = FeedbackSystem()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open video {video_path}")
        sys.exit(1)

    feedback.speak("Starting squat assessment", force=True)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop
            continue

        annotated_frame, angles = detector.process_frame(frame)

        if angles:
            now = time.time()
            event = evaluator.update(
                angles['knee_angle'],
                angles['torso_angle'],
                angles['heel_angle'],
                now
            )

            status = evaluator.status
            feedback.draw_status(annotated_frame, {
                **status,
                'knee_angle': angles['knee_angle'],
                'torso_angle': angles['torso_angle'],
                'heel_angle': angles['heel_angle']
            })

            if status['is_resting']:
                feedback.draw_rest_timer(annotated_frame, status['rest_time_left'])

            # Voice feedback (non-blocking in real app — here synced for demo clarity)
            if event == "REP_COMPLETE":
                rep_num = status['rep']
                feedback.speak(f"Rep {rep_num}")
            elif event == "SET_COMPLETE":
                feedback.speak(f"Set {status['set'] - 1} complete. Rest now.")
            elif event == "REST_END":
                feedback.speak(f"Starting set {status['set']}")
            elif event == "FINISHED":
                feedback.speak("Workout complete. Well done!")
                break
            elif event == "REP_INVALID":
                feedback.speak("Incomplete rep — check form!")

        cv2.imshow('Squat Form Assessor', annotated_frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    feedback.speak(f"Session ended. Total reps: {evaluator.total_reps}")

if __name__ == "__main__":
    video = sys.argv[1] if len(sys.argv) > 1 else "demo/sample_squat.mp4"
    main(video)
