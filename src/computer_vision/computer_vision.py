import argparse
import sys
import time
import cv2
import numpy as np
from picamera2 import Picamera2, MappedArray, CompletedRequest
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics
from gpiozero import Motor, PWMOutputDevice


class RobotFollower:
    def __init__(self, model_file, camera_num=0):
        self.imx500 = IMX500(model_file)
        self.intrinsics = self.imx500.network_intrinsics or NetworkIntrinsics()
        self.intrinsics.task = "object detection"

        self.picam2 = Picamera2(camera_num=camera_num)
        config = self.picam2.create_preview_configuration(
            main={"format": "XRGB8888"},  # ✅ Fixed preview crash
            controls={"FrameRate": self.intrinsics.inference_rate},
            buffer_count=12
        )
        self.picam2.start(config, show_preview=True)
        if self.intrinsics.preserve_aspect_ratio:
            self.imx500.set_auto_aspect_ratio()

        self.labels = self._load_labels()

        # Setup motors
        self.motor_a = Motor(forward=17, backward=27)
        self.motor_b = Motor(forward=22, backward=23)
        self.enable_a = PWMOutputDevice(24, frequency=1000)
        self.enable_b = PWMOutputDevice(25, frequency=1000)
        self.stop_motors()

    def _load_labels(self):
        if self.intrinsics.labels is None:
            with open("assets/coco_labels.txt", "r") as f:
                self.intrinsics.labels = f.read().splitlines()
        return self.intrinsics.labels

    def stop_motors(self):
        print("[STOP] Motors")
        self.motor_a.stop()
        self.motor_b.stop()
        self.enable_a.value = 0
        self.enable_b.value = 0

    def move_robot(self, left_speed, right_speed):
        self.enable_a.value = left_speed
        self.enable_b.value = right_speed
        self.motor_a.forward()
        self.motor_b.forward()
        print(f"[MOVE] L={left_speed:.2f}, R={right_speed:.2f}")

    def get_detections(self, request):
        try:
            metadata = request.get_metadata()
            outputs = self.imx500.get_outputs(metadata, add_batch=True)
            if outputs is None:
                return []
            boxes, scores, classes = outputs[0][0], outputs[1][0], outputs[2][0]
            return [
                {
                    "box": self.imx500.convert_inference_coords(b, metadata, self.picam2),
                    "score": s,
                    "class_id": int(c)
                }
                for b, s, c in zip(boxes, scores, classes)
                if s >= 0.5 and self.labels[int(c)] == "person"
            ]
        except Exception as e:
            print(f"[ERROR] get_detections: {e}")
            return []

    def draw_and_control(self, request: CompletedRequest):
        try:
            detections = self.get_detections(request)
            if not detections:
                self.stop_motors()
                return

            best = max(detections, key=lambda d: d["box"][2] * d["box"][3], default=None)
            if not best:
                self.stop_motors()
                return

            x, y, w, h = map(int, best["box"])
            if h < 40 or w < 20:
                print("[WARN] Small person box ignored.")
                self.stop_motors()
                return

            with MappedArray(request, "main") as m:
                frame_h, frame_w = m.array.shape[:2]
                label = f"person ({best['score']:.2f})"
                overlay = m.array.copy()
                (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                text_x, text_y = x + 5, y + 15
                cv2.rectangle(overlay, (text_x, text_y - th), (text_x + tw, text_y + baseline), (255, 255, 255), -1)
                alpha = 0.3
                cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)
                cv2.putText(m.array, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Control logic
            frame_center = frame_w // 2
            person_center_x = x + w // 2
            error_x = (frame_center - person_center_x) / frame_center
            distance_error = 1.0 - min(h / frame_h, 1.0)

            if distance_error < 0.05:
                print("[INFO] Too close.")
                self.stop_motors()
                return

            MIN_SPEED = 0.55
            MAX_SPEED = 1.0

            # === NEW TURN-IN-PLACE LOGIC ===
            if abs(error_x) > 0.7:
                print("[TURN] Person far off-center. Rotating in place.")
                if error_x > 0:
                    left_speed = MIN_SPEED
                    right_speed = MAX_SPEED
                else:
                    left_speed = MAX_SPEED
                    right_speed = MIN_SPEED
            else:
                # Smooth gain-based steering
                steering_gain = 1.2
                steering = np.clip(error_x * steering_gain, -0.6, 0.6)
                forward = np.clip(distance_error * 0.6, 0.0, 1.0)

                left_speed = np.clip(forward + steering, MIN_SPEED, MAX_SPEED)
                right_speed = np.clip(forward - steering, MIN_SPEED, MAX_SPEED)

            self.move_robot(left_speed, right_speed)
        except Exception as e:
            print(f"[ERROR] draw_and_control: {e}")
            self.stop_motors()

    def run(self):
        try:
            while True:
                request = self.picam2.capture_request()
                self.draw_and_control(request)
                request.release()
        except KeyboardInterrupt:
            print("Interrupted.")
        finally:
            self.stop_motors()
            self.picam2.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    parser.add_argument("--camera-num", type=int, default=0)
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction)
    parser.add_argument("--labels", type=str, help="Path to custom labels")
    parser.add_argument("--print-intrinsics", action="store_true")
    args = parser.parse_args()

    robot = RobotFollower(model_file=args.model, camera_num=args.camera_num)
    if args.print_intrinsics:
        print(robot.intrinsics)
        sys.exit(0)

    robot.run()
