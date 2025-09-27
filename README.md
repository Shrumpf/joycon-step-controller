# JoyCon Step Detection

## Project Idea

This project transforms a Nintendo Switch JoyCon into a real-life step detector for controlling a character in a game. By analyzing the JoyCon's built-in accelerometer, the script detects physical steps or movements and translates them into in-game actions. The goal is to create a more immersive and active gaming experience, where your real steps move your character!

## How It Works
- Connect a JoyCon to your computer via Bluetooth.
- The script calibrates for a few seconds, analyzing which axis (X, Y, or Z) best captures your step movement.
- It then continuously monitors the chosen axis for significant changes, counting each detected step.
- Each step can be used to trigger in-game movement or other actions.

## Current State
- **Step detection is reliable:** The script automatically calibrates and selects the best axis for your movement style.
- **Code is clean and modular:** Easy to read, extend, and integrate into other projects.
- **Console output:** Shows step count and calibration info for debugging and tuning.

## Future Plans
- **Game integration:** Connect the step detection to actual game controls (e.g., move a character in Unity, Godot, or other engines).
- **Multiple JoyCons:** Support for using both JoyCons for more complex movement or actions.
- **Customizable sensitivity:** Allow users to tune thresholds and calibration duration via command-line or config file.
- **Visualization:** Add a simple UI or graph to visualize movement and step detection in real time.
- **Cross-platform support:** Make it easy to use on Windows, macOS, and Linux.

## Getting Started
1. Install Python and the `pyjoycon` library.
2. Connect your JoyCon via Bluetooth.
3. Run `joy.py` and follow the instructions in the terminal.
4. Move your leg or arm with the JoyCon during calibration, then start stepping!

## Why?
This project is perfect for:
- Fitness games and exergaming
- VR/AR movement experiments
- Accessibility solutions
- Fun hacks and prototypes

---


---

**Attribution**

This project idea is by me but most of the code and this README were written with the help of GitHub Copilot.
(I don't like to write python and while its still a proof of concept I don't care about code quality)

**Contributions and ideas are welcome!**

