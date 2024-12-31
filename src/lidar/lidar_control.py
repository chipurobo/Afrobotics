from rplidar import RPLidar
import matplotlib.pyplot as plt
import numpy as np

class LidarControl:
    def __init__(self, port='/dev/ttyUSB0'):
        self.lidar = RPLidar(port)
        self.info = self.lidar.get_info()
        self.health = self.lidar.get_health()

    def start_scan(self):
        self.lidar.start_motor()
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        scan_data = np.zeros((360, 2))
        try:
            for scan in self.lidar.iter_scans():
                for (_, angle, distance) in scan:
                    scan_data[int(angle)] = (np.radians(angle), distance)
                ax.clear()
                ax.set_ylim(0, 6000)
                ax.plot(scan_data[:, 0], scan_data[:, 1], 'bo')
                plt.pause(0.001)
                print('Got %d measurements' % len(scan))
        except Exception as e:
            print(f"Error during scanning: {e}")
            self.stop_scan()
        finally:
            plt.close(fig)

    def stop_scan(self):
        try:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
        except Exception as e:
            print(f"Error during stopping: {e}")

if __name__ == "__main__":
    # Update the port as needed
    lidar_control = LidarControl(port='/dev/ttyUSB0')
    try:
        lidar_control.start_scan()
    except KeyboardInterrupt:
        print("Stopping scan...")
    finally:
        lidar_control.stop_scan()