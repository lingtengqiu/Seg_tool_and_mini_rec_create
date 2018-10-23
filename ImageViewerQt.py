#-*- coding:utf-8 -*-
""" ImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

"""

import os.path
try:
    from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR
    from PyQt5.QtGui import QImage, QPixmap, QPainterPath
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog
    from PyQt5 import QtCore
except ImportError:
    try:
            from PyQt4 import QtCore
            from PyQt4.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR
            from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QImage, QPixmap, QPainterPath, QFileDialog,QPen,QBrush
    except ImportError:
            raise ImportError("ImageViewerQt: Requires PyQt5 or PyQt4.")


__author__ = "qiulingteng_1259738366@qq.com"
__version__ = '0.9.0'

WINDOW_SIZE = 830, 630
class ImageViewerQt(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.

    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)
    move_event_point_show = pyqtSignal(int,int)
    wheelroute = pyqtSignal(float)
    Moustmove_leftMouseButtonClicked = pyqtSignal(int, int)
    def __init__(self,args):
        super(QGraphicsView,self).__init__(args)
        self.setMouseTracking
        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = False
        self.lbtnpress = False
        self.control = False
        self.setMouseTracking(True)

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image,init):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        if init:
            self.zoomStack = []

        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()

    def mouseMoveEvent(self, QMouseEvent):
        scenePos = self.mapToScene(QMouseEvent.pos())
        row = int(scenePos.y())
        column = int(scenePos.x())
        print(column,row)
        # print("Clicked on image pixel (row=" + str(row) + ", column=" + str(column) + ")")
        if self.lbtnpress:
            self.Moustmove_leftMouseButtonClicked.emit(int(scenePos.x()), int(scenePos.y()))
        if self.hasImage():
            self.move_event_point_show.emit(int(scenePos.x()),int(scenePos.y()))
        QGraphicsView.mouseMoveEvent(self,QMouseEvent)
    def wheelEvent(self,QWheelEvent):
        scenePos = self.mapToScene(QWheelEvent.pos())
        row = int(scenePos.y())
        column = int(scenePos.x())
        if self.control == True:
            delta = QWheelEvent.delta()
            self.wheelroute.emit(delta)
            self.move_event_point_show.emit(int(scenePos.x()),int(scenePos.y()))
        else:    
            super(ImageViewerQt,self).wheelEvent(QWheelEvent)
    def keyPressEvent(self,QKeyEvent):
        if QKeyEvent.key()== QtCore.Qt.Key_Control:
            self.control = True
            print('ok')
        super(ImageViewerQt,self).keyPressEvent(QKeyEvent)
    def keyReleaseEvent(self,QKeyEvent):
        if(QKeyEvent.key() == QtCore.Qt.Key_Control):
            self.control =False
            print('no')
        super(ImageViewerQt,self).keyReleaseEvent(QKeyEvent)

    

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.lbtnpress = True
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
            row = int(scenePos.y())
            column = int(scenePos.x())
            # print("Clicked on image pixel (row=" + str(row) + ", column=" + str(column) + ")")
            # self.scene.addRect(QRectF(scenePos.x(), scenePos.y(),300,300),QPen(Qt.red,2,Qt.SolidLine),QBrush(Qt.red,Qt.SolidPattern))

        elif event.button() == Qt.RightButton:
            self.lbtnpress = False
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    # def keyPressEvent(self, QKeyEvent):
    #     if QKeyEvent.key() == Qt.Key_Control:
    #         self.canPan = True
    #     QGraphicsView.keyPressEvent(self,QKeyEvent)
    #
    # def keyReleaseEvent(self, QKeyEvent):
    #     if QKeyEvent.key() == Qt.Key_Control:
    #         self.canPan = False
    #
    #     QGraphicsView.keyReleaseEvent(self,QKeyEvent)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
            self.lbtnpress = False
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                #this part to zoom our picture
                width = self.image().width()
                heigh = self.image().height()
                print(width,heigh)
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                x_ = selectionBBox.x()
                y_ = selectionBBox.y()
                h_ = selectionBBox.height()
                w_ = selectionBBox.width()
                print('orign',selectionBBox) 
                rate = 1.0*WINDOW_SIZE[0]/WINDOW_SIZE[1]
                rate_we = 1.0*w_/h_
                if(rate_we>rate):
                    #w is to bigger
                    h_change = (w_/rate)
                    delta_h = h_change-h_
                    if(y_+h_+delta_h/2>heigh):
                        print(delta_h)
                        delta_h = delta_h+(y_+h_+delta_h/2-heigh)*2+1
                        print(delta_h)
                    if(y_-delta_h/2<0):
                        delta_h = delta_h-(delta_h/2)*2-y_-1
                        print(delta_h)

                    #protect to 
                    selectionBBox.setY(y_-delta_h/2)
                    selectionBBox.setHeight(h_change)
                else:
                    #h is to bigger
                    w_change = h_*rate
                    delta_w = w_change-w_

                    if(x_+w_+delta_w/2>width):

                        delta_w = delta_w+(x_+w_+delta_w/2-width)*2+1
                    if(x_-delta_w/2<0):
                        delta_w = delta_w-(delta_w/2)*2-x_-1
                    selectionBBox.setX(x_-delta_w/2)
                    selectionBBox.setWidth(w_change)                   
                    

                # print('orign',selectionBBox) 
                # if w_>h_:
                #     h_change = (w_/rate)
                #     if h_change>h_:
                #         deta_h = h_change-h_
                #         selectionBBox.setY(y_-deta_h/2)
                #         selectionBBox.setHeight(h_change)
                #     else:


                # else:
                #     w_ = (h_*rate)
                # selectionBBox.setX(x_-w_/2)

                # selectionBBox.setWidth(w_)
                # selectionBBox.setHeight(h_)
                print('change',selectionBBox) 

                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()

            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)




if __name__ == '__main__':
    import sys
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            from PyQt4.QtGui import QApplication
        except ImportError:
            raise ImportError("ImageViewerQt: Requires PyQt5 or PyQt4.")
    print('ImageViewerQt: Using Qt ' + QT_VERSION_STR)

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")




    # Create the application.
    app = QApplication(sys.argv)

    # Create image viewer and load an image file to display.
    viewer = ImageViewerQt()
    viewer.loadImageFromFile()  # Pops up file dialog.

    # Handle left mouse clicks with custom slot.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec_())
