# Raspberry Pi Motor Control Project

## Overview
This project is designed to control motors connected to a Raspberry Pi. It provides a foundation for future enhancements, including the integration of computer vision and LiDAR sensor functionalities.

## Project Structure
```
raspberry-pi-motor-control
├── src
│   ├── motor_control
│   │   └── motor_control.py
│   ├── computer_vision
│   │   └── computer_vision.py
│   ├── lidar
│   │   └── lidar_control.py
│   └── utils
│       └── __init__.py
├── requirements.txt
└── README.md
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd raspberry-pi-motor-control
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

## Usage

### Motor Control
To control the motors, you will interact with the `MotorControl` class defined in `src/motor_control/motor_control.py`. This class provides methods to start and stop the motors, as well as to set their speed.

#### Example
```python
from motor_control.motor_control import MotorControl

motor = MotorControl()
motor.start_motor()
motor.set_speed(50)
motor.stop_motor()
```

### Computer Vision
To capture and process images using the AI camera, you will interact with the `ComputerVision` class defined in `src/computer_vision/computer_vision.py`.

#### Example
```python
from computer_vision.computer_vision import ComputerVision

cv = ComputerVision()
image = cv.capture_image()
processed_image = cv.process_image(image)
cv.display_image(processed_image)
```

### LiDAR Control
To start scanning with the LiDAR sensor, you will interact with the `LidarControl` class defined in `src/lidar/lidar_control.py`.

#### Example
```python
from lidar.lidar_control import LidarControl

lidar_control = LidarControl(port='/dev/ttyUSB0')
try:
    lidar_control.start_scan()
except KeyboardInterrupt:
    print("Stopping scan...")
finally:
    lidar_control.stop_scan()
```

## Future Plans
- **Computer Vision Integration:** Develop functionalities to enable the Raspberry Pi to process visual data, which could include object detection and tracking.
- **LiDAR Sensor Integration:** Implement features to utilize LiDAR data for mapping and navigation purposes.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.