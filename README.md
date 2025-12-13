# Smartan-Fittech-AI-Assingment

# Squat Form Assessor

A real-time, webcam-based system for **therapeutic squat assessment**, providing biomechanical feedback and rep counting — designed for local deployment (no cloud, no cost).

## Features
- Real-time pose detection (MediaPipe, CPU/GPU compatible)
- Rule-based form validation (knee depth, torso angle, heel alignment)
- Visual & voice feedback (`pyttsx3`)
- Configurable thresholds & workout plan (YAML)
- No special sensors — works with standard webcam

## Quick Start
```bash
git clone https://github.com/yourname/squat-form-assessor.git
cd squat-form-assessor
pip install -r requirements.txt
python -m src.main demo/sample_squat.mp4
