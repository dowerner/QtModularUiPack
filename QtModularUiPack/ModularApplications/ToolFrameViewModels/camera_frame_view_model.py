from ViewModels import BaseViewModel
from Framework.Devices import Camera, VALID_EXPOSURE_TIMES, exposure_time_to_index, get_available_cameras


class CameraFrameViewModel(BaseViewModel):

    name = 'camera'

    @property
    def exposure_time(self):
        if self._cam.connected:
            return self._cam.exposure_time
        else:
            return 0

    @exposure_time.setter
    def exposure_time(self, value):
        if self._cam.connected:
            self._cam.exposure_time = value
            self.notify_change('exposure_time')
            self.notify_change('exposure_time_index')

    @property
    def exposure_time_index(self):
        if self._cam.connected:
            return exposure_time_to_index(self.exposure_time)
        else:
            return 0

    @exposure_time_index.setter
    def exposure_time_index(self, value):
        if self._cam.connected:
            self.exposure_time = VALID_EXPOSURE_TIMES[value]
            self.notify_change('exposure_time')
            self.notify_change('exposure_time_index')

    @property
    def available_cameras(self):
        return get_available_cameras()

    @property
    def selected_camera(self):
        return self._selected_camera

    @selected_camera.setter
    def selected_camera(self, value):
        self._selected_camera = value
        self.notify_change('selected_camera')

    @property
    def frame_queue(self):
        return self._cam.frame_queue

    def __init__(self):
        super().__init__()
        self._selected_camera = 0
        self._cam = None
        self.connect_to_cam()

    def __del__(self):
        self._cam.close()

    def connect_to_cam(self):
        try:
            self._cam = Camera(cam_index=self._selected_camera)
            self._cam.verbose = False
            self._cam.connect()
        except Exception as e:
            print('Unable to connect to camera. {}'.format(e))

    def disconnect_cam(self):
        if not self._cam.connected:
            return
        try:
            self._cam.close()
        except Exception as e:
            print('Error while disconnecting camera. {}'.format(e))
