import argparse
import sys
import time
import cv2
import numpy as np
import subprocess
from picamera2 import Picamera2, Preview, CompletedRequest, MappedArray
from picamera2.devices import IMX500
from picamera2.devices.imx500.postprocess import softmax

class ComputerVision:
    def __init__(self, model_file="path/to/model/file", camera_num=0):
        self.imx500 = IMX500(model_file)
        self.intrinsics = self.imx500.network_intrinsics
        if not self.intrinsics:
            self.intrinsics = self.imx500.NetworkIntrinsics()
            self.intrinsics.task = "classification"
        elif self.intrinsics.task != "classification":
            print("Network is not a classification task", file=sys.stderr)
            exit()

        self.picam2 = Picamera2(camera_num=camera_num)
        config = self.picam2.create_preview_configuration(controls={"FrameRate": self.intrinsics.inference_rate}, buffer_count=12)
        self.picam2.start(config, show_preview=True)
        if self.intrinsics.preserve_aspect_ratio:
            self.imx500.set_auto_aspect_ratio()
        self.picam2.pre_callback = self.parse_and_draw_classification_results

    def capture_image(self):
        frame = self.picam2.capture_array()
        return frame

    def process_image(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        return edges

    def parse_and_draw_classification_results(self, request: CompletedRequest):
        results = self.parse_classification_results(request)
        self.draw_classification_results(request, results)

    def parse_classification_results(self, request: CompletedRequest):
        np_outputs = self.imx500.get_outputs(request.get_metadata())
        if np_outputs is None:
            return []
        np_output = np_outputs[0]
        if self.intrinsics.softmax:
            np_output = softmax(np_output)
        top_indices = np.argpartition(-np_output, 3)[:3]
        top_indices = top_indices[np.argsort(-np_output[top_indices])]
        return [self.Classification(index, np_output[index]) for index in top_indices]

    class Classification:
        def __init__(self, idx: int, score: float):
            self.idx = idx
            self.score = score

    def draw_classification_results(self, request: CompletedRequest, results, stream="main"):
        with MappedArray(request, stream) as m:
            if self.intrinsics.preserve_aspect_ratio:
                b_x, b_y, b_w, b_h = self.imx500.get_roi_scaled(request)
                cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))
                text_left, text_top = b_x, b_y + 20
            else:
                text_left, text_top = 0, 0
            for index, result in enumerate(results):
                label = self.get_label(request, idx=result.idx)
                text = f"{label}: {result.score:.3f}"
                (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                text_x = text_left + 5
                text_y = text_top + 15 + index * 20
                overlay = m.array.copy()
                cv2.rectangle(overlay, (text_x, text_y - text_height), (text_x + text_width, text_y + baseline), (255, 255, 255), cv2.FILLED)
                alpha = 0.3
                cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)
                cv2.putText(m.array, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    def get_label(self, request: CompletedRequest, idx: int):
        if self.intrinsics.labels is None:
            with open("assets/imagenet_labels.txt", "r") as f:
                self.intrinsics.labels = f.read().splitlines()
        return self.intrinsics.labels[idx]

    def display_image(self, image):
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run_rpicam_hello(self):
        command = [
            "rpicam-hello",
            "-t", "0s",
            "--post-process-file", "/usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json",
            "--viewfinder-width", "1920",
            "--viewfinder-height", "1080",
            "--framerate", "30"
        ]
        subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model", default="/usr/share/imx500-models/imx500_network_mobilenet_v2.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("-s", "--softmax", action=argparse.BooleanOptionalAction, help="Add post-process softmax")
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction, help="Preprocess the image with preserve aspect ratio")
    parser.add_argument("--labels", type=str, help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true", help="Print JSON network_intrinsics then exit")
    parser.add_argument("--camera-num", type=int, help="Camera number", default=0)
    args = parser.parse_args()

    cv = ComputerVision(model_file=args.model, camera_num=args.camera_num)
    if args.print_intrinsics:
        print(cv.intrinsics)
        exit()

    cv.run_rpicam_hello()

    image = cv.capture_image()
    processed_image = cv.process_image(image)
    cv.display_image(processed_image)

    while True:
        time.sleep(0.5)