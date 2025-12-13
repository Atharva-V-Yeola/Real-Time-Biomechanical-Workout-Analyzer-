import cv2
import pyttsx3

class FeedbackSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 1.0)
        self.last_spoken = ""

    def speak(self, text, force=False):
        if not force and text == self.last_spoken:
            return  # Avoid repetition
        self.engine.say(text)
        self.engine.runAndWait()
        self.last_spoken = text

    def draw_status(self, frame, status):
        y = 50
        cv2.putText(frame, f"Set: {status['set']}/{status['total_sets']} | Rep: {status['rep']}/{status['reps_per_set']}",
                   (50, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        y += 50
        cv2.putText(frame, f"Position: {status['position']}",
                   (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        y += 45

        self._draw_metric(frame, "Knee", status['knee_angle'],
                         status['knee_ok'], status['rules']['squat']['knee_min'],
                         status['rules']['squat']['knee_max'], y)
        y += 35
        self._draw_metric(frame, "Torso", status['torso_angle'],
                         status['torso_ok'], status['rules']['squat']['torso_min'],
                         status['rules']['squat']['torso_max'], y)
        y += 35
        self._draw_metric(frame, "Heel-Ankle-Knee", status['heel_angle'],
                         status['heel_ok'], status['rules']['squat']['heel_ankle_knee_min'],
                         status['rules']['squat']['heel_ankle_knee_max'], y)

    def _draw_metric(self, frame, name, value, ok, min_val, max_val, y):
        color = (0, 255, 0) if ok else (255, 255, 255)
        cv2.putText(frame, f"{name}: {value:.1f}° [{min_val}-{max_val}]",
                   (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def draw_rest_timer(self, frame, seconds_left):
        cv2.putText(frame, f"Rest: {seconds_left}s",
                   (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 3)
