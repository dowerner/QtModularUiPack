"""
Copyright 2019 Dominik Werner

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from PyQt5.QtMultimedia import QAbstractVideoSurface, QAbstractVideoBuffer, QVideoFrame, QVideoSurfaceFormat
from PyQt5.QtCore import QSize, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, pyqtSignal


class VideoFrameGrabber(QAbstractVideoSurface):
    """
    This video surface can be used as a QMediaPlayer target but also allows access to the data
    """

    frameAvailable = pyqtSignal(QImage)

    def __init__(self, widget, *args, **kwargs):
        super().__init__(widget, *args, **kwargs)
        self.imageFormat = QImage.Format_Invalid
        self.widget = widget
        self.targetRect = QRect()
        self.sourceRect = QRect()
        self.imageSize = QSize()
        self.currentFrame = None

    @staticmethod
    def _format_size_(surface_format):
        image_format = QVideoFrame.imageFormatFromPixelFormat(surface_format.pixelFormat())
        size = surface_format.frameSize()
        return image_format, size

    def isFormatSupported(self, surface_format):
        """
        True if format is supported
        :param surface_format: format
        """
        image_format, size = self._format_size_(surface_format)
        return image_format != QImage.Format_Invalid and not size.isEmpty() and surface_format.handleType() == QAbstractVideoBuffer.NoHandle

    def start(self, surface_format):
        """
        Start capturing
        :param surface_format: surface format
        """
        image_format, size = self._format_size_(surface_format)

        if image_format != QImage.Format_Invalid and not size.isEmpty():
            self.imageFormat = image_format
            self.imageSize = size
            self.sourceRect = surface_format.viewport()

            super().start(surface_format)

            self.widget.updateGeometry()
            self.update_video_rect()

            return True
        else:
            return False

    def stop(self):
        """
        Stop capturing
        """
        self.currentFrame = QVideoFrame()
        self.targetRect = QRect()
        super().stop()
        self.widget.update()

    def present(self, frame: QVideoFrame):
        """
        Called by the video player
        :param frame: frame to present
        """
        if frame.isValid():
            clone_frame = QVideoFrame(frame)
            clone_frame.map(QAbstractVideoBuffer.ReadOnly)
            image = QImage(clone_frame.bits(), clone_frame.width(), clone_frame.height(),
                           QVideoFrame.imageFormatFromPixelFormat(clone_frame.pixelFormat()))

            self.frameAvailable.emit(image)
            clone_frame.unmap()

        if self.surfaceFormat().pixelFormat() != frame.pixelFormat() or self.surfaceFormat().frameSize() != frame.size():
            self.setError(self.IncorrectFormatError)
            self.stop()
            return False
        else:
            self.currentFrame = frame
            self.widget.repaint()
            return True

    def paint(self, painter: QPainter):
        """
        Paint frame
        :param painter: painter to use
        """
        if self.currentFrame.map(QAbstractVideoBuffer.ReadOnly):
            old_transform = painter.transform()

            if self.surfaceFormat().scanLineDirection() == QVideoSurfaceFormat.BottomToTop:
                painter.scale(1, -1)
                painter.translate(0, -self.widget.height())

            image = QImage(self.currentFrame.bits(), self.currentFrame.width(), self.currentFrame.height(),
                           self.currentFrame.bytesPerLine(), self.imageFormat)

            painter.drawImage(self.targetRect, image, self.sourceRect)
            painter.setTransform(old_transform)

            self.currentFrame.unmap()

    def update_video_rect(self):
        """
        Update dimensions
        """
        size = self.surfaceFormat().sizeHint()
        size.scale(self.widget.size().boundedTo(size), Qt.KeepAspectRatio)
        self.targetRect = QRect(QPoint(0, 0), size)
        self.targetRect.moveCenter(self.widget.rect().center())

    def supportedPixelFormats(self, handle_type=None):
        """
        Get all supported formats
        :param handle_type: handle_type
        """
        return [QVideoFrame.Format_ARGB32,
                QVideoFrame.Format_ARGB32_Premultiplied,
                QVideoFrame.Format_RGB32,
                QVideoFrame.Format_RGB24,
                QVideoFrame.Format_RGB565,
                QVideoFrame.Format_RGB555,
                QVideoFrame.Format_ARGB8565_Premultiplied,
                QVideoFrame.Format_BGRA32,
                QVideoFrame.Format_BGRA32_Premultiplied,
                QVideoFrame.Format_BGR32,
                QVideoFrame.Format_BGR24,
                QVideoFrame.Format_BGR565,
                QVideoFrame.Format_BGR555,
                QVideoFrame.Format_BGRA5658_Premultiplied,
                QVideoFrame.Format_AYUV444,
                QVideoFrame.Format_AYUV444_Premultiplied,
                QVideoFrame.Format_YUV444,
                QVideoFrame.Format_YUV420P,
                QVideoFrame.Format_YV12,
                QVideoFrame.Format_UYVY,
                QVideoFrame.Format_YUYV,
                QVideoFrame.Format_NV12,
                QVideoFrame.Format_NV21,
                QVideoFrame.Format_IMC1,
                QVideoFrame.Format_IMC2,
                QVideoFrame.Format_IMC3,
                QVideoFrame.Format_IMC4,
                QVideoFrame.Format_Y8,
                QVideoFrame.Format_Y16,
                QVideoFrame.Format_Jpeg,
                QVideoFrame.Format_CameraRaw,
                QVideoFrame.Format_AdobeDng]
