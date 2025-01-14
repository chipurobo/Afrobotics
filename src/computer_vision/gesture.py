import threading
import queue
import pygame
import random
import math
from collections import namedtuple
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import cv2
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from pose_estimation_pipeline import GStreamerPoseEstimationApp
import time


# Game constants
WINDOW_WIDTH = 600  # Adjusted window width
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 20
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 7
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
BRICK_DROP_SPEED = 2
SPAWN_RATE = 30  # Frames between brick spawns
STARTING_LIVES = 3
POSITION_QUEUE_SIZE = 1

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)
BLACK = (0, 0, 0)

# Game objects
Player = namedtuple('Player', ['x', 'y', 'width', 'height'])
Bullet = namedtuple('Bullet', ['x', 'y', 'width', 'height', 'vel_y'])
Brick = namedtuple('Brick', ['x', 'y', 'width', 'height', 'vel_y'])

class PoseShooterCallback(app_callback_class):
    def __init__(self):
        super().__init__()
        self.left_hand_pos = (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2)
        self.right_hand_pos = (3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2)
        self.use_frame = True
        self.position_queue = queue.Queue(maxsize=POSITION_QUEUE_SIZE)

class PoseShooter:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pose Shooter")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.reset_game()
        
        # Initialize pose estimation
        self.user_data = PoseShooterCallback()
        self.app = GStreamerPoseEstimationApp(self.pose_callback, self.user_data)

    def reset_game(self):
        self.player = Player(WINDOW_WIDTH // 2 - PLAYER_WIDTH // 2, WINDOW_HEIGHT - 50, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.bullets = []
        self.bricks = []
        self.score = 0
        self.lives = STARTING_LIVES
        self.frame_count = 0
        self.game_over = False
        self.running = True

    def pose_callback(self, pad, info, user_data):
        buffer = info.get_buffer()
        if buffer is None:
            return Gst.PadProbeReturn.OK

        roi = hailo.get_roi_from_buffer(buffer)
        detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

        for detection in detections:
            if detection.get_label() == "person":
                landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
                if len(landmarks) != 0:
                    points = landmarks[0].get_points()
                    bbox = detection.get_bbox()
                    format, width, height = get_caps_from_pad(pad)
                    
                    # Constants for y-axis scaling relative to frame height
                    Y_MIN = 0.22 * height
                    Y_MAX = 0.78 * height
                    Y_RANGE = Y_MAX - Y_MIN

                    # Left wrist (index 9)
                    left_point = points[9]
                    left_x = WINDOW_WIDTH - int((left_point.x() * bbox.width() + bbox.xmin()) * width)
                    raw_y = (left_point.y() * bbox.height() + bbox.ymin()) * height
                    normalized_y = (raw_y - Y_MIN) / Y_RANGE
                    left_y = int(normalized_y * WINDOW_HEIGHT)

                    # Right wrist (index 10)
                    right_point = points[10]
                    right_x = WINDOW_WIDTH - int((right_point.x() * bbox.width() + bbox.xmin()) * width)
                    raw_y = (right_point.y() * bbox.height() + bbox.ymin()) * height
                    normalized_y = (raw_y - Y_MIN) / Y_RANGE
                    right_y = int(normalized_y * WINDOW_HEIGHT)

                    try:
                        while not self.user_data.position_queue.empty():
                            self.user_data.position_queue.get_nowait()
                        self.user_data.position_queue.put_nowait(((left_x, left_y), (right_x, right_y)))
                    except queue.Full:
                        pass

        return Gst.PadProbeReturn.OK

    def spawn_brick(self):
        x = random.randint(0, WINDOW_WIDTH - BRICK_WIDTH)
        y = -BRICK_HEIGHT
        return Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, BRICK_DROP_SPEED)

    def update_bricks(self):
        new_bricks = []
        for brick in self.bricks:
            new_y = brick.y + brick.vel_y
            if new_y > WINDOW_HEIGHT:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
            else:
                new_bricks.append(brick._replace(y=new_y))
        self.bricks = new_bricks

    def update_bullets(self):
        new_bullets = []
        for bullet in self.bullets:
            new_y = bullet.y - BULLET_SPEED
            if new_y > 0:
                new_bullets.append(bullet._replace(y=new_y))
        self.bullets = new_bullets

    def check_collisions(self):
        new_bricks = []
        for brick in self.bricks:
            hit = False
            for bullet in self.bullets:
                if (bullet.x > brick.x and bullet.x < brick.x + brick.width and
                    bullet.y > brick.y and bullet.y < brick.y + brick.height):
                    self.score += 1
                    hit = True
                    break
            if not hit:
                new_bricks.append(brick)
        self.bricks = new_bricks

    def update_player(self):
        try:
            left_pos, right_pos = self.user_data.position_queue.get_nowait()
            # Use the average x-coordinate of both wrists to move the player
            new_x = (left_pos[0] + right_pos[0]) // 2 - self.player.width // 2
            # Ensure the player stays within the window bounds
            new_x = max(0, min(WINDOW_WIDTH - self.player.width, new_x))
            self.player = self.player._replace(x=new_x)
        except queue.Empty:
            pass

    def draw(self):
        self.screen.fill(BLACK)

        # Draw player
        pygame.draw.rect(self.screen, GREEN, 
                         (self.player.x, self.player.y, self.player.width, self.player.height))

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, RED, 
                             (bullet.x, bullet.y, bullet.width, bullet.height))

        # Draw bricks
        for brick in self.bricks:
            pygame.draw.rect(self.screen, BLUE, 
                             (brick.x, brick.y, brick.width, brick.height))

        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        lives_text = font.render(f'Lives: {self.lives}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))

        pygame.display.flip()

    def run_pose_estimation(self):
        self.app.run()

    def run(self):
        # Start pose estimation in a separate thread
        pose_thread = threading.Thread(target=self.run_pose_estimation)
        pose_thread.daemon = True
        pose_thread.start()

        # Step 1: Wait for pose estimation to initialize (we can use a sleep or a check here)
        # We are ensuring pose estimation has started before opening the game window
        time.sleep(1)  # Give pose estimation a bit of time to start (adjust as necessary)

        # Step 2: Now, create the game window after pose estimation has started
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pose Shooter")

        # Step 3: Run the game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            if self.game_over:
                self.reset_game()
            else:
                # Spawn new bricks based on spawn rate
                if self.frame_count % SPAWN_RATE == 0:
                    self.bricks.append(self.spawn_brick())

                # Update game state
                self.update_bricks()
                self.update_bullets()
                self.check_collisions()
                self.update_player()

                # Shoot bullets
                if self.frame_count % 10 == 0:
                    self.bullets.append(Bullet(self.player.x + self.player.width // 2, self.player.y, BULLET_WIDTH, BULLET_HEIGHT, -BULLET_SPEED))

            # Draw everything on the game screen
            self.draw()

            # Update frame counter
            self.frame_count += 1
            self.clock.tick(FPS)

        # Cleanup: Close game and pose estimation app when done
        pygame.quit()
        self.app.quit()


if __name__ == "__main__":
    game = PoseShooter()
    game.run()