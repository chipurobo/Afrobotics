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

#### Code Breakdown

##### Imported Libraries

###### General Purpose Libraries
- **`threading` and `queue`**: Used for running pose estimation in a separate thread and managing wrist position updates.
- **`random`**: Generates random brick spawn positions.
- **`math`**: Provides mathematical operations (though unused here).

###### Gaming Framework
- **`pygame`**: For creating the game window, handling events, and rendering graphics.

###### Pose Estimation
- **`gi` and `Gst`**: For managing multimedia pipelines via GStreamer.
- **`hailo` and `hailo_rpi_common`**: For pose detection and landmarks extraction using Hailo's SDK.

###### Helper Libraries
- **`numpy`**: Efficient numerical operations.
- **`collections.namedtuple`**: For defining simple game objects like `Player`, `Bullet`, and `Brick`.

---

##### Constants

###### Game Constants
- **Window and FPS**: Dimensions (`WINDOW_WIDTH`/`WINDOW_HEIGHT`) and refresh rate (`FPS`).
- **Object Dimensions and Speeds**: Sizes and velocities of the player, bullets, and bricks.
- **Spawn Rate**: Determines how frequently bricks spawn.
- **Lives**: Number of lives the player starts with.
- **Position Queue Size**: Capacity for storing wrist position updates.

###### Colors
Common RGB tuples:
- White, Red, Green, Blue, and Black.

---

##### Game Objects
Defined using `namedtuple` for simplicity and immutability:
- **`Player`**: Paddle position and dimensions.
- **`Bullet`**: Bullet position, dimensions, and velocity.
- **`Brick`**: Brick position, dimensions, and velocity.

---

##### Pose Estimation

###### Pose Shooter Callback
- Handles the communication between the pose estimation pipeline and the game logic.
- Tracks default wrist positions and updates a queue for real-time paddle control.

###### Pose Shooter Class

###### Initialization
1. **Game Setup**: Creates the game window, initializes paddle position, and resets the game state.
2. **Pose Estimation**: Sets up callbacks to process wrist positions for paddle movement.

###### Reset Game
- Resets player position, score, lives, and clears bullets and bricks for a fresh session.

###### Pose Estimation Callback
1. Processes buffer data from the GStreamer pipeline.
2. Extracts ROI and landmarks.
3. Normalizes wrist positions relative to the frame height.
4. Updates the position queue for paddle control.

---

##### Game Logic

###### Brick Spawning
- **`spawn_brick()`**: Generates bricks at random x-coordinates with fixed velocity.

###### Updating Game Elements
- **Bricks**: Move downward and deduct a life if they fall out of bounds.
- **Bullets**: Move upward and are removed when out of bounds.
- **Collisions**: Detects bullet-brick collisions, increasing the score when a hit occurs.

###### Player Movement
- **`update_player()`**: Updates the paddle's position based on the average x-coordinate of the player's wrists.

---

##### Rendering

###### Draw Function
- Clears the screen.
- Renders the player, bullets, bricks, score, and remaining lives.

---

##### Pose Estimation and Game Loop

###### Pose Estimation Thread
- Runs the pose estimation pipeline separately to ensure smooth gameplay.

###### Game Loop
Handles:
- Event processing (e.g., quitting the game).
- Spawning and updating game objects.
- Rendering frames.
- Maintaining the FPS.

###### Game Over Handling
- Resets the game state when all lives are lost.

---

##### Cleanup
- Releases resources such as the Pygame window and the pose estimation pipeline when the game exits.

---

##### Main Function
- Initializes the `PoseShooter` class and starts the game using the `run()` method.

---

## Requirements

Make sure to install the required libraries before running the scripts. You can install the dependencies using the following command:

```sh
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.
