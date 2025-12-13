import time
import yaml
from pathlib import Path

class SquatEvaluator:
    def __init__(self, config_path="config/squat_rules.yaml"):
        with open(config_path) as f:
            self.rules = yaml.safe_load(f)
        self.reset()

    def reset(self):
        self.current_set = 1
        self.total_reps = 0
        self.is_resting = False
        self.rest_start_time = None
        self.squat_position = "UP"
        self.rule1_passed = False  # Knee depth
        self.rule2_passed = False  # Torso alignment
        self.rule3_passed = False  # Heel-ankle-knee

    def update(self, knee_angle, torso_angle, heel_angle, now):
        if self.is_resting:
            elapsed = now - self.rest_start_time
            if elapsed >= self.rules['workout']['rest_seconds']:
                self.is_resting = False
                return "REST_END"
            return "RESTING"

        # State machine: UP → DOWN → UP (complete rep)
        if self.squat_position == "UP" and knee_angle < 140:
            self.squat_position = "DOWN"
            self.rule1_passed = self.rule2_passed = self.rule3_passed = False
            return "DESCENDING"

        elif self.squat_position == "DOWN":
            # Check rules while in bottom position
            if self.rules['squat']['knee_min'] <= knee_angle <= self.rules['squat']['knee_max']:
                self.rule1_passed = True
            if self.rules['squat']['torso_min'] <= torso_angle <= self.rules['squat']['torso_max']:
                self.rule2_passed = True
            if self.rules['squat']['heel_ankle_knee_min'] <= heel_angle <= self.rules['squat']['heel_ankle_knee_max']:
                self.rule3_passed = True

            # Transition back up
            if knee_angle > 155:
                if self.rule1_passed and self.rule2_passed and self.rule3_passed:
                    self.total_reps += 1
                    rep_in_set = (self.total_reps - 1) % self.rules['workout']['reps_per_set'] + 1

                    if rep_in_set == self.rules['workout']['reps_per_set']:
                        self.current_set += 1
                        if self.current_set > self.rules['workout']['sets']:
                            return "FINISHED"
                        else:
                            self.is_resting = True
                            self.rest_start_time = now
                            return "SET_COMPLETE"
                    return "REP_COMPLETE"
                else:
                    return "REP_INVALID"
                self.squat_position = "UP"

        return "IDLE"

    @property
    def status(self):
        return {
            'set': self.current_set,
            'total_sets': self.rules['workout']['sets'],
            'reps_per_set': self.rules['workout']['reps_per_set'],
            'rep': (self.total_reps % self.rules['workout']['reps_per_set']) or self.rules['workout']['reps_per_set'],
            'position': self.squat_position,
            'is_resting': self.is_resting,
            'rest_time_left': int(self.rules['workout']['rest_seconds'] - (time.time() - self.rest_start_time))
                        if self.is_resting else 0,
            'knee_ok': self.rule1_passed,
            'torso_ok': self.rule2_passed,
            'heel_ok': self.rule3_passed,
            'rules': self.rules
        }
