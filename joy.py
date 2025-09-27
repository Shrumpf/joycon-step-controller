
from pyjoycon import GyroTrackingJoyCon, get_R_id
import time

# --- Configurable Parameters ---
STEP_THRESHOLD = 0.2           # Threshold for axis difference to count as a step
MIN_TIME_BETWEEN_STEPS = 0.3   # Minimum seconds between steps
CALIBRATION_SECONDS = 3        # Calibration duration in seconds
SAMPLE_INTERVAL = 0.05         # Sampling interval in seconds

def get_accel_tuple(accel):
    """Convert JoyCon accel (glm.vec3) to tuple."""
    return (accel.x, accel.y, accel.z)

def calibrate_axis(joycon, duration=CALIBRATION_SECONDS):
    """Record axis data for a few seconds and select the axis with the largest average difference."""
    print("Calibrating... Please move the JoyCon as you would for steps.")
    axis_data = []
    start_time = time.time()
    while time.time() - start_time < duration:
        accel = get_accel_tuple(joycon.direction)
        axis_data.append(accel)
        time.sleep(SAMPLE_INTERVAL)
    # Calculate average difference for each axis
    diffs = {'x': [], 'y': [], 'z': []}
    for i in range(1, len(axis_data)):
        prev = axis_data[i-1]
        curr = axis_data[i]
        diffs['x'].append(abs(curr[0] - prev[0]))
        diffs['y'].append(abs(curr[1] - prev[1]))
        diffs['z'].append(abs(curr[2] - prev[2]))
    avg_diffs = {k: sum(v)/len(v) if v else 0 for k, v in diffs.items()}
    chosen_axis = max(avg_diffs, key=avg_diffs.get)
    print(f"Calibration complete. Using axis '{chosen_axis.upper()}' for step detection.")
    print(f"Average diffs: {avg_diffs}")
    return chosen_axis

def detect_steps(joycon, chosen_axis):
    """Main loop for step detection using the selected axis."""
    last_step_time = 0
    step_count = 0
    prev_val = None
    was_below_threshold = True
    print("Starting improved step detection. Move your leg or arm with the JoyCon.")
    print(f"Step threshold: {STEP_THRESHOLD}, Min time between steps: {MIN_TIME_BETWEEN_STEPS}s")
    try:
        while True:
            accel = get_accel_tuple(joycon.direction)
            axis_val = {'x': accel[0], 'y': accel[1], 'z': accel[2]}[chosen_axis]
            current_time = time.time()
            if prev_val is not None:
                diff = abs(axis_val - prev_val)
                if diff > STEP_THRESHOLD and was_below_threshold and (current_time - last_step_time) > MIN_TIME_BETWEEN_STEPS:
                    step_count += 1
                    last_step_time = current_time
                    print(f"Step detected! Total steps: {step_count}")
                    was_below_threshold = False
                elif diff < STEP_THRESHOLD:
                    was_below_threshold = True
            prev_val = axis_val
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        print(f"Stopped. Total steps counted: {step_count}")

def main():
    joycon_id = get_R_id()
    if not joycon_id:
        raise Exception("No JoyCon detected. Please connect/pair your JoyCon first.")
    joycon = GyroTrackingJoyCon(*joycon_id)
    chosen_axis = calibrate_axis(joycon)
    detect_steps(joycon, chosen_axis)

if __name__ == "__main__":
    main()
