# Chipurobo AI Series Documentation

This repository contains the documentation and code for various applications in the Chipurobo AI series. The applications include motor control, lidar-based obstacle avoidance, and gesture control using Hailo.

## Project Structure

```
chipurobo-ai-series/
├── src/
│   ├── motor_control/
│   │   └── motor_control.py
│   ├── lidar/
│   │   └── lidar_control.py
│   └── gesture_control/
│       └── gesture_control.py
├── README.md
└── requirements.txt
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd chipurobo-ai-series
   ```

2. **Install dependencies:**
   Ensure you have Python and pip installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Install additional packages for the AI camera:**
   ```
   sudo apt-get update
   sudo apt-get install -y python3-picamera2
   ```

## Applications

### Motor Control

The motor control application uses GPIO pins to control the motors of a robot. The script `motor_control.py` is responsible for moving the motors forward and stopping them based on lidar input.

#### Running the Motor Control Script

```sh
python -m src.motor_control.motor_control
```

### Lidar-Based Obstacle Avoidance

The lidar-based obstacle avoidance application uses an RPLidar to detect obstacles and stop the motors when an obstacle is detected within a certain distance.

#### Running the Lidar Control Script

```sh
python -m src.lidar.lidar_control
```

### Gesture Control Using Hailo

The gesture control application uses the Hailo AI processor to recognize gestures and control the robot based on the recognized gestures.

#### Running the Gesture Control Script

```sh
python -m src.gesture_control.gesture_control
```

## Requirements

Make sure to install the required libraries before running the scripts. You can install the dependencies using the following command:

```sh
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.