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

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import QSize, QRect, QPoint, Qt
from PyQt5.QtGui import QPainter, QPen


class ImageRenderWidget(QWidget):
    """
    This widget is optimized to display frames of camera/video footage. (Can also be used for other purposes)
    This widget also provides layers on which to draw over the image.
    """

    @property
    def image_width(self):
        """
        Width of the currently displayed image
        """
        return self._image_width

    @property
    def image_height(self):
        """
        Height of the currently displayed image
        """
        return self._image_height

    @property
    def image_scale_x(self):
        """
        X scale of the currently displayed image (can vary from y-scale if the aspect is not locked)
        """
        return self._scale_x

    @property
    def image_scale_y(self):
        """
        Y scale of the currently displayed image (can vary from x-scale if the aspect is not locked)
        """
        return self._scale_y

    @property
    def image_origin_x(self):
        """
        X coordinate of upper left corner of the image within the widget (image is always centered)
        """
        return self._image_origin_x

    @property
    def image_origin_y(self):
        """
        Y coordinate of upper left corner of the image within the widget (image is always centered)
        """
        return self._image_origin_y

    @property
    def current_frame(self):
        """
        Gets the frame of the sequence that is displayed
        """
        return self._current_frame

    @current_frame.setter
    def current_frame(self, value):
        """
        Sets the frame of the sequence that is displayed. This has only an effect on shapes that have key-frames
        :param value: frame number
        """
        self._current_frame = value
        self.update()

    def __init__(self, parent=None, *args, keep_aspect_ratio=True, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.overlay_layers = list()    # layers to draw on that are displayed over the image
        self._scale_x = 1
        self._scale_y = 1
        self._image_origin_x = 0
        self._image_origin_y = 0
        self._image_width = 0
        self._image_height = 0
        self._current_frame = 0

        self.keep_aspect_ratio = keep_aspect_ratio  # if true the ratio of width and length of the image will be taken into account when scaling
        self.image = None
        self._size_hint = QSize(2000, 2000)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)    # make the widget use as much space as possible
        self.painter = QPainter()   # painter for rendering the image and the draw layers

    def sizeHint(self):
        """
        Needed for filling up widget space. (Should be improved)
        """
        return self._size_hint

    def set_image(self, image):
        """
        Sets image that should be displayed on the widget.
        :param image: image to display
        """
        self.image = image  # assign image
        self.update()   # update widget

    def paintEvent(self, event):
        """
        Callback if the widget is updated.
        :param event: event arguments
        """
        self.painter.begin(self)    # start rendering process
        if self.image:  # check if an image is available to draw
            image_size = self.image.size()  # get the original size of the image
            frame_size = self.size()    # get the size that is currently available for the widget

            # set the image to fill the available space
            render_width = frame_size.width()
            render_height = frame_size.height()

            if self.keep_aspect_ratio:  # if the aspect ratio should be kept, calculate the proper image dimensions
                aspect_ratio = image_size.width() / image_size.height()     # get original aspect ratio

                # sizes in case the image fills the width of the frame
                w_w = frame_size.width()
                h_w = int(w_w / aspect_ratio)

                # sizes in case the image fills the height of the frame
                h_h = frame_size.height()
                w_h = int(h_h * aspect_ratio)

                # choose the proper options such that in every case the entire image is visible
                if h_w <= frame_size.height():
                    render_width = w_w
                    render_height = h_w
                else:
                    render_width = w_h
                    render_height = h_h

            # expose the calculated quantities
            self._image_origin_x = (frame_size.width() - render_width) / 2
            self._image_origin_y = (frame_size.height() - render_height) / 2
            self._image_width = render_width
            self._image_height = render_height
            self._scale_x = render_width / image_size.width()
            self._scale_y = render_height / image_size.height()

            # draw the image
            self.painter.drawImage(QRect(self._image_origin_x, self._image_origin_y, render_width, render_height), self.image)

            # draw the layers with custom shapes on top of the image
            origin = QPoint(self._image_origin_x, self._image_origin_y)
            for layer in self.overlay_layers:
                layer.draw(self.painter, origin, self._scale_x, self._scale_y, self._current_frame)

        self.painter.end()  # end rendering process


class ImageLayer(object):
    """
    A layer that can be placed on top of an image to draw markings.
    """

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.shapes = list()

    def draw(self, painter: QPainter, origin: QPoint, scale_x: float, scale_y: float, current_frame=0):
        """
        Draw the layer
        :param painter: painter to draw the layer with
        :param origin: origin of the image to draw upon
        :param scale_x: scale of the image in x direction
        :param scale_y: scale of the image in y direction
        :param current_frame: frame to be drawn (only has an effect if shapes have keyframes)
        """
        if not self.enabled:    # do nothing if the layer is disabled
            return

        for shape in self.shapes:   # draw all shapes contained in this layer
            shape.draw(painter, origin, scale_x, scale_y, current_frame)


class ImageShape(object):
    """
    Base class for shapes that can be drawn over an image
    """

    @property
    def x(self):
        self._position.x()

    @x.setter
    def x(self, value):
        self._position = QPoint(value, self.position.y())

    @property
    def y(self):
        self._position.y()

    @y.setter
    def y(self, value):
        self._position = QPoint(self.position.x(), value)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if type(value) == tuple or type(value) == list:
            self._position = QPoint(value[0], value[1])
        else:
            self._position = value

    def __init__(self, x=0, y=0, rotation=0, filled=True, show_border=True, fill_color=Qt.black, border_color=Qt.black, border_thickness=1):
        self._position = QPoint(x, y)    # set position of the shape (in image coordinates)
        self.rotation = rotation        # set the rotation of the shape (unused)
        self.filled = filled            # if set to true, the shape will have a fill color
        self.show_border = show_border  # if true the shape will have a border
        self.fill_color = fill_color    # the fill color of the shape
        self.border_color = border_color    # the border color of the shape
        self.border_thickness = border_thickness    # the border thickness of the shape
        self.keyframes = dict()

    def add_keyframe(self, frame_number, **kwargs):
        """
        Capture properties at specific frame
        :param frame_number: position in time
        :param kwargs: properties to capture
        """
        keyframe = dict()
        for prop in kwargs:
            keyframe[prop] = kwargs[prop]
        self.keyframes[frame_number] = keyframe

    def draw(self, painter: QPainter, origin: QPoint, scale_x: float, scale_y: float, current_frame=0):
        """
        Implement this method in order to make the shape drawable
        :param painter: painter to draw the shape with
        :param origin: origin of the image to draw upon on the widget
        :param scale_x: x scale of the image
        :param scale_y: y scale of the image
        :param current_frame: frame to be drawn (only has an effect if shapes have keyframes)
        """
        raise NotImplementedError()

    def setup_keyframe(self, frame_number):
        """
        Sets object properties to keyframe properties
        :param frame_number: frame in time
        """
        if frame_number in self.keyframes:
            for prop in self.keyframes[frame_number]:
                if hasattr(self, prop):
                    setattr(self, prop, self.keyframes[frame_number][prop])

    def setup_painter(self, painter: QPainter):
        """
        Configure the painter to render the shape with the current settings
        :param painter: painter to configure
        """
        if self.filled:
            painter.setBrush(self.fill_color)
        else:
            painter.setBrush(Qt.NoBrush)

        if self.show_border:
            pen = QPen(self.border_color)
            pen.setWidth(self.border_thickness)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)


class ImageRectangle(ImageShape):
    """
    A rectangle to draw on an image
    """

    def __init__(self, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width      # width of the rectangle (in image coordinates)
        self.height = height    # height of the rectangle (in image coordinates)

    def draw(self, painter: QPainter, origin: QPoint, scale_x: float, scale_y: float, current_frame=0):
        """
        Draw the rectangle
        :param painter: painter to draw the rectangle with
        :param origin: origin of the image to draw upon on the widget
        :param scale_x: x scale of the image
        :param scale_y: y scale of the image
        :param current_frame: frame to be drawn (only has an effect if shapes have keyframes)
        """
        self.setup_keyframe(current_frame)
        self.setup_painter(painter)     # setup the colors
        painter.drawRect(QRect(self.position.x()*scale_x+origin.x(),  # draw the rectangle in the coordinate of the image
                               self.position.y()*scale_y+origin.y(),
                               self.width*scale_x,
                               self.height*scale_y))


class ImageEllipse(ImageShape):
    """
    An ellipse to draw on an image
    """

    def __init__(self, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width      # width of the ellipse (in image coordinates)
        self.height = height    # height of the ellipse (in image coordinates)

    def draw(self, painter: QPainter, origin: QPoint, scale_x: float, scale_y: float, current_frame=0):
        """
        Draw the ellipse
        :param painter: painter to draw the rectangle with
        :param origin: origin of the image to draw upon on the widget
        :param scale_x: x scale of the image
        :param scale_y: y scale of the image
        :param current_frame: frame to be drawn (only has an effect if shapes have keyframes)
        """
        self.setup_keyframe(current_frame)
        self.setup_painter(painter)     # setup the colors
        painter.drawEllipse(self.position.x()*scale_x+origin.x(),  # draw the ellipse in the coordinate of the image
                            self.position.y()*scale_y+origin.y(),
                            self.width*scale_x,
                            self.height*scale_y)


class ImageCircle(ImageEllipse):
    """
    Circle to draw on an image
    """

    def __init__(self, radius, *args, **kwargs):
        super().__init__(radius*2, radius*2, *args, **kwargs)  # instantiate ellipse with 2 times the radius as width and height


