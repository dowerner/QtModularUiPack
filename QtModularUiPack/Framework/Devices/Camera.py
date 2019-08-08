import cv2
import queue
import numpy as np
from threading import Thread


VALID_EXPOSURE_TIMES = [640, 320, 160, 80, 40, 20, 10, 5, 2.5, 1.25, 0.65, 0.312, 0.15]
VALID_EXPOSURE_SETTINGS = [-1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13]


def closest_valid_exposure_time(value):
    return VALID_EXPOSURE_TIMES[np.argmin(np.abs(np.asarray(VALID_EXPOSURE_TIMES) - value))]


def exposure_time_to_setting(value):
    return VALID_EXPOSURE_SETTINGS[np.argmin(np.abs(np.asarray(VALID_EXPOSURE_TIMES) - value))]


def exposure_setting_to_time(value):
    return VALID_EXPOSURE_TIMES[np.argmin(np.abs(np.asarray(VALID_EXPOSURE_SETTINGS) - value))]


def exposure_time_to_index(value):
    return np.argmin(np.abs(np.asarray(VALID_EXPOSURE_TIMES) - value))


def get_available_cameras():
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
        return arr


class Camera(object):

    @property
    def connected(self):
        return self._capture is not None

    @property
    def cam_index(self):
        return self._cam_index

    @cam_index.setter
    def cam_index(self, value):
        self._cam_index = value
        self.close()
        self.connect()

    @property
    def exposure_setting(self):
        return self._exposure_setting

    @exposure_setting.setter
    def exposure_setting(self, value):
        if value in VALID_EXPOSURE_SETTINGS:
            if self._capture is not None:
                self._capture.set(cv2.CAP_PROP_EXPOSURE, value)
                self._exposure_time = exposure_setting_to_time(self._exposure_setting)
        elif self.verbose:
            print('The value given is not a valid exposure setting.')

    @property
    def exposure_time(self):
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value):
        if self._capture is not None:
            self._exposure_time = closest_valid_exposure_time(value)
            self._exposure_setting = exposure_time_to_setting(self.exposure_time)
            self._capture.set(cv2.CAP_PROP_EXPOSURE, self._exposure_setting)

    def __init__(self, cam_index=0):
        self._cam_index = cam_index
        self._capture = None
        self.new_frame_ready = list()
        self.frame_queue = queue.Queue()
        self._capture_thread = None
        self.is_capturing = False
        self.frame_buffer_size = 10
        self._exposure_setting = -1
        self._exposure_time = exposure_setting_to_time(self._exposure_setting)
        self.verbose = False

    def _capture_worker(self, *args):
        self.is_capturing = True

        while self.is_capturing and self._capture is not None:
            self._capture.grab()
            try:
                retval, img = self._capture.retrieve(0)
            except:
                break

            if self.frame_queue.qsize() < self.frame_buffer_size:
                self.frame_queue.put({'frame': img})
            elif self.verbose:
                print('Frame buffer full.')

            for callback in self.new_frame_ready:
                callback(img)
        if self.verbose:
            print('Capture stopped.')

    def connect(self):
        self.close()
        self._capture = cv2.VideoCapture(self._cam_index)
        self._exposure_setting = self._capture.get(cv2.CAP_PROP_EXPOSURE)
        self._exposure_time = exposure_setting_to_time(self._exposure_setting)
        self._capture_thread = Thread(target=self._capture_worker)
        self._capture_thread.daemon = True
        self._capture_thread.start()

    def close(self):
        self.is_capturing = False
        if self._capture is not None:
            self._capture.release()
        self._capture = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    for i in range(700):
        t = closest_valid_exposure_time(i)
        print(i, t)
        print(exposure_time_to_setting(t))
    """with Camera() as camera:
        camera."""
