import cv2
import numpy as np
from picamera2 import Picamera2

class ComputerVision:
    def __init__(self, resolution=(640, 480)):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_still_configuration(main={"size": resolution}))

    def capture_image(self):
        self.camera.start()
        frame = self.camera.capture_array()
        self.camera.stop()
        return frame

    def process_image(self, image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Detect edges using Canny
        edges = cv2.Canny(blurred, 50, 150)
        return edges

    def display_image(self, image):
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    cv = ComputerVision()
    image = cv.capture_image()
    processed_image = cv.process_image(image)
    cv.display_image(processed_image)