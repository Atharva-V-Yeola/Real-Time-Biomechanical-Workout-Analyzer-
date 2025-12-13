import mediapipe as mp

POSE = mp.solutions.pose.PoseLandmark

# Default: use LEFT side to reduce variability (you can later add side auto-detection)
LANDMARKS = {
    'hip': POSE.LEFT_HIP,
    'knee': POSE.LEFT_KNEE,
    'ankle': POSE.LEFT_ANKLE,
    'shoulder': POSE.LEFT_SHOULDER,
    'ear': POSE.LEFT_EAR,
    'heel': POSE.LEFT_HEEL,
}
