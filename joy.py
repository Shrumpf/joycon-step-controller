

from pyjoycon import GyroTrackingJoyCon, get_R_id, get_L_id
import time

from pynput.keyboard import Controller, Listener, Key, KeyCode
keyboard_controller = Controller()


# Track last movement key pressed (WASD or arrows)
last_direction = ['w']  # Use list for mutability in nested functions

MOVEMENT_KEYS = {
    'w': 'w', 'a': 'a', 's': 's', 'd': 'd',
    'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right
}

def on_key_press(key):
    try:
        # WASD
        if hasattr(key, 'char') and key.char and key.char.lower() in MOVEMENT_KEYS:
            last_direction[0] = MOVEMENT_KEYS[key.char.lower()]
        # Arrow keys
        elif hasattr(key, 'name') and key.name in MOVEMENT_KEYS:
            last_direction[0] = MOVEMENT_KEYS[key.name]
    except Exception:
        pass

# Start listener in background
listener = Listener(on_press=on_key_press)
listener.daemon = True
listener.start()


# --- Configurable Parameters ---
STEP_THRESHOLD = 0.04           # Threshold for axis difference to count as a step
MIN_TIME_BETWEEN_STEPS = 0.2   # Minimum seconds between steps
CALIBRATION_SECONDS = 3        # Calibration duration in seconds
SAMPLE_INTERVAL = 0.05         # Sampling interval in seconds
STEP_MODE = 'hold'             # 'tile' for press per step, 'hold' for hold key while stepping
HOLD_TIMEOUT = 0.4             # seconds to release key after last step in hold mode
STEP_PRESS_DURATION = 0.25     # seconds to hold key down for each step in tile mode

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



def on_step_detected_tile():
    """Tile mode: Press and release last WASD/arrow key for each step, with configurable duration."""
    key = last_direction[0]
    keyboard_controller.press(key)
    time.sleep(STEP_PRESS_DURATION)
    keyboard_controller.release(key)

def on_step_detected_hold(state):
    """Hold mode: Hold last WASD/arrow key while stepping, release after timeout."""
    now = time.time()
    state['last_step_time'] = now
    key = last_direction[0]
    if not state.get('holding_key') == key:
        # Release previous key if holding
        if state.get('holding_key'):
            keyboard_controller.release(state['holding_key'])
        keyboard_controller.press(key)
        state['holding_key'] = key
        state['holding'] = True

def hold_mode_release_if_needed(state):
    """Release 'W' if timeout since last step."""
    if state['holding']:
        remaining = HOLD_TIMEOUT - (time.time() - state['last_step_time'])
        print(f"Currently holding key: {state.get('holding_key')}, release in {max(0, remaining):.2f}s", end='\r')
        if (time.time() - state['last_step_time'] > HOLD_TIMEOUT):
            if state.get('holding_key'):
                keyboard_controller.release(state['holding_key'])
            print(f"Released key: {state.get('holding_key')}")
            state['holding'] = False
            state['holding_key'] = None

def detect_steps(joycon, chosen_axis, mode=STEP_MODE):
    """Main loop for step detection using the selected axis. Supports 'tile' and 'hold' modes."""
    last_step_time = 0
    step_count = 0
    prev_val = None
    was_below_threshold = True
    print("Starting improved step detection. Move your leg or arm with the JoyCon.")
    print(f"Step threshold: {STEP_THRESHOLD}, Min time between steps: {MIN_TIME_BETWEEN_STEPS}s, Mode: {mode}")
    hold_state = {'holding': False, 'last_step_time': 0}
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
                    if mode == 'tile':
                        on_step_detected_tile()
                    elif mode == 'hold':
                        on_step_detected_hold(hold_state)
                    was_below_threshold = False
                elif diff < STEP_THRESHOLD:
                    was_below_threshold = True
            prev_val = axis_val
            if mode == 'hold':
                hold_mode_release_if_needed(hold_state)
            time.sleep(SAMPLE_INTERVAL)
    except KeyboardInterrupt:
        if mode == 'hold' and hold_state['holding']:
            keyboard_controller.release('w')
        print(f"Stopped. Total steps counted: {step_count}")


def main():
    joycon_r_id = get_R_id()
    joycon_l_id = get_L_id()

    if not joycon_l_id:
        raise Exception("No JoyCon detected. Please connect/pair your JoyCon first.")
    joycon_l = GyroTrackingJoyCon(*joycon_l_id)
    chosen_axis = calibrate_axis(joycon_l)
    detect_steps(joycon_l, chosen_axis, mode=STEP_MODE)

if __name__ == "__main__":
    main()
