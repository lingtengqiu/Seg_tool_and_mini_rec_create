#-*- coding:utf-8 -*-
import sys
import os,shutil
from PyQt4 import QtGui, QtCore
import cv2
import numpy as np
from ImageViewerQt import ImageViewerQt
WINDOW_SIZE = 1050, 700
L_WINDOW = 150, WINDOW_SIZE[1]-20
R_WINDOW = QtCore.QRect(200, 50, WINDOW_SIZE[0]-220, WINDOW_SIZE[1]-70)
# here save you file which you want
LIST_IMG_EXT = ['jpg','png','bmp']
SAVE_FILE = {'img':'./result/img','label':'./result/label'}
TEMP_FILE = './result/img_temp'
class Seg_label_tool(QtGui.QMainWindow):

    def __init__(self, args):
        super(Seg_label_tool, self).__init__()
        self.InitUI()

        self.image_view.Moustmove_leftMouseButtonClicked.connect(self.mousemove_slot)
        self.image_view.wheelroute.connect(self.wheelroute)
        self.image_view.move_event_point_show.connect(self.move_event_circle)
        self.curimg = None
        self.showimg = None
        self.curlabel = None
        self.setMouseTracking(True)


    def InitUI(self):
        self.layout_design()
        self.menu_tootbar_design()
        self.sBar = self.statusBar()
        self.ctr_control = False
        self.restore = True        

    def layout_design(self):

        self.setGeometry(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])
        self.move_to_center()
        self.setWindowTitle('seg_label_tool')

        self.left_QWidget = QtGui.QWidget(self)

        self.left_QWidget.setGeometry(10, 10, L_WINDOW[0], L_WINDOW[1])

        vbox = QtGui.QVBoxLayout()

        hbox1 = QtGui.QHBoxLayout()
        labname_lab = QtGui.QLabel('label', self.left_QWidget)
        self.labname_edit = QtGui.QLineEdit('defect', self.left_QWidget)
        hbox1.addWidget(labname_lab)
        hbox1.addWidget(self.labname_edit)
        vbox.addLayout(hbox1)

        hbox2 = QtGui.QHBoxLayout()
        radius_lab = QtGui.QLabel('radius', self.left_QWidget)
        self.radius_edit = QtGui.QLineEdit('50', self.left_QWidget)
        hbox2.addWidget(radius_lab)
        hbox2.addWidget(self.radius_edit)
        vbox.addLayout(hbox2)

        labbtn = QtGui.QPushButton('lab', self.left_QWidget)
        labbtn.clicked.connect(self.labaction)
        vbox.addWidget(labbtn)

        # labsavebtn = QtGui.QPushButton('lab_save',self.left_QWidget)
        # labsavebtn.clicked.connect(self.labSaveAction)
        # labsavebtn.setShortcut('s')
        # vbox.addWidget(labsavebtn)

        labcancelbtn = QtGui.QPushButton('lab_erase', self.left_QWidget)
        labcancelbtn.clicked.connect(self.labCancelAction)
        vbox.addWidget(labcancelbtn)

        self.left_QWidget.setLayout(vbox)
        self.image_view = ImageViewerQt(self)
        self.image_view.setGeometry(R_WINDOW)

    def menu_tootbar_design(self):

        exitAction = QtGui.QAction(QtGui.QIcon('./icon/quit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.QApplication.quit)

        saveAction = QtGui.QAction(QtGui.QIcon('./icon/save.png'), '&save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('save inf')
        saveAction.triggered.connect(self.savefile)

        opendirAction = QtGui.QAction(QtGui.QIcon('./icon/opendir.png'), '&opendir', self)
        opendirAction.setShortcut('Ctrl+O')
        opendirAction.setStatusTip('opendir inf')
        opendirAction.triggered.connect(self.opendir)

        nextAction = QtGui.QAction(QtGui.QIcon('./icon/next.png'), '&nextimg', self)
        nextAction.setShortcut('n')
        nextAction.setStatusTip('nextimg inf')
        nextAction.triggered.connect(self.nextimg)

        prevAction = QtGui.QAction(QtGui.QIcon('./icon/prev.png'), '&previmg', self)
        prevAction.setShortcut('p')
        prevAction.setStatusTip('prevtimg inf')
        prevAction.triggered.connect(self.previmg)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        viewMenu = menubar.addMenu('&View')
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('opendir')
        toolbar.addAction(opendirAction)

        toolbar = self.addToolBar('save')
        toolbar.addAction(saveAction)

        toolbar = self.addToolBar('Next')
        toolbar.addAction(nextAction)

        toolbar = self.addToolBar('prev')
        toolbar.addAction(prevAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAction)

    def savefile(self):
        if self.showimg is not None and self.curlabel is not None:
            cv2.imwrite(self.filelist[self.curimg_index][0],self.showimg[:,:,(2,1,0)])
            print(self.filelist[self.curimg_index][0])
            str1 = self.filelist[self.curimg_index][1].split('.')[1]+'.png'
            str1 = '.'+str1
            cv2.imwrite(str1,self.curlabel[:,:,0])



    def opendir(self):
        dirname = None
        dirname = QtGui.QFileDialog.getExistingDirectory(
            self, 'open dir', './')
        dirname = str(dirname)
        files = os.listdir(dirname)
        list_post = []
        for fil in files:
            IMG_EXT = fil.split('.')[-1]
            if(IMG_EXT in LIST_IMG_EXT):
                if(not (IMG_EXT in list_post)):
                    list_post.append(IMG_EXT)
        print(list_post)

        if dirname:
            # QtGui.QMessageBox.information(self,'inf',dirname)
            self.filelist = []
            if os.path.isdir(dirname):
                #save the result
                self.result_img_dir = SAVE_FILE['img']
                self.result_label_dir = SAVE_FILE['label']

                if os.path.exists(self.result_img_dir):
                    shutil.rmtree(self.result_img_dir)
                if os.path.exists(self.result_label_dir):
                    shutil.rmtree(self.result_label_dir)
                if os.path.exists(TEMP_FILE):
                    shutil.rmtree(TEMP_FILE)
                os.makedirs(self.result_label_dir)

                shutil.copytree(dirname,self.result_img_dir)
                shutil.copytree(dirname,TEMP_FILE)

                for file in os.listdir(dirname):
                    if file.split('.')[-1] in list_post:
                        self.filelist.append((self.result_img_dir + '/' + file,self.result_label_dir+ '/' + file,TEMP_FILE+'/'+file))
                print(len(self.filelist))
                self.filelist.sort()
                print(self.filelist)
                self.curimg_index = -1
                self.nextimg()

            else:
                print('please select a dir')

    def show_img_fun(self,img,init=True):

        frame = QtGui.QImage(img.data, img.shape[1],img.shape[0],img.shape[1]*3, QtGui.QImage.Format_RGB888)
        self.image_view.setImage(frame,init)

    def nextimg(self):
        self.savefile()
        self.curimg_index += 1
        if self.curimg_index == len(self.filelist):
            self.curimg_index -= 1
            QtGui.QMessageBox.information(self, 'inf', 'this is no more image')
        else:
            self.curimg = cv2.imread(self.filelist[self.curimg_index][-1])
            self.curimg = cv2.cvtColor(self.curimg, cv2.COLOR_BGR2RGB)
            self.curlabel = np.zeros_like(self.curimg)
            self.showimg = np.copy(self.curimg)

            self.show_img_fun(self.curimg,True)

            self.isdrawing = True
            self.islabing = True
            self.restore_string = '.'+ (str(self.filelist[self.curimg_index][1].split('.')[1]))+'.png'
            if(os.path.exists('.'+str(self.filelist[self.curimg_index][1].split('.')[1])+'.png')):
                print('exits')
                self.restore = False
            self.sBar.showMessage(self.filelist[self.curimg_index][0].split('/')[-1])
            self.__Restore()

    def previmg(self):
        self.savefile()
        self.curimg_index -= 1
        if self.curimg_index < 0:
            self.curimg_index += 1
            QtGui.QMessageBox.information(self, 'inf', 'this is first image')
        else:

            self.curimg = cv2.imread(self.filelist[self.curimg_index][-1])#grpah use the temp park
            self.curimg = cv2.cvtColor(self.curimg, cv2.COLOR_BGR2RGB)
            self.curlabel = np.zeros_like(self.curimg)
            self.showimg = np.copy(self.curimg)

            self.show_img_fun(self.showimg,True)

            self.isdrawing = True
            self.islabing = True
            self.restore_string = '.'+ (str(self.filelist[self.curimg_index][1].split('.')[1]))+'.png'
            if(os.path.exists('.'+str(self.filelist[self.curimg_index][1].split('.')[1])+'.png')):
                print('exits')
                self.restore = False
            self.__Restore()
            
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Control:
            self.image_view.canPan = True
            self.isdrawing = False
            self.ctr_control = True
        if QtCore.Qt.Key_C  == QKeyEvent.key():
            self.islabing = False

        return super(Seg_label_tool, self).keyReleaseEvent(QKeyEvent)

    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key() == QtCore.Qt.Key_Control:
            self.image_view.canPan = False
            self.isdrawing = True
            self.ctr_control = False
        if QtCore.Qt.Key_C  == QKeyEvent.key():
            self.islabing = True
        if QKeyEvent.key() == QtCore.Qt.Key_Escape:
            if len(self.image_view.zoomStack):
                self.image_view.zoomStack.pop()
            self.image_view.updateViewer()

        return super(Seg_label_tool, self).keyReleaseEvent(QKeyEvent)
    def wheelroute(self,radvalue):
        rad = int(self.radius_edit.text())
        if radvalue>0:
            rad +=5
            self.radius_edit.setText(str(rad))
        else:
            if rad>5:
                rad -= 5
                self.radius_edit.setText(str(rad))

    def labaction(self):
        self.islabing = True
        # self.setCursor(QtCore.Qt.CrossCursor)

    def labCancelAction(self):
        self.islabing = False

    def __Restore(self):
        if not self.restore:
            self.restore = True
            print(self.restore_string)
            self.curlabel = cv2.imread(self.restore_string)
            print(self.curlabel.shape)
            self.showimg = self._cal_showimg(self.curimg,self.curlabel)
            self.show_img_fun(self.showimg,False)
            self.sBar.showMessage('labing')
        # print 'helo'
        # self.setCursor(QtCore.Qt.UpArrowCursor)

    def move_to_center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _cal_showimg(self,curimg,label):

        tmp = np.copy(curimg)
        tmp[np.where(label[:,:,0] == 255)] = (255,0,0)

        return tmp

    def mouseMoveEvent(self, QMouseEvent):
        pass
    def move_event_circle(self,x,y):
        rad = int(self.radius_edit.text())
        if rad<0:
            rad = 5
        self.showimg = self._cal_showimg(self.curimg,self.curlabel)
        temp = np.copy(self.showimg)
        cv2.circle(temp,(x,y),radius = rad,color=(0,0,255),thickness = -1)
        # cv2.circle(self.curlabel,(x,y),radius=rad,color=(255,255,255),thickness= -1)
        self.show_img_fun(temp,False)

    def mousemove_slot(self,x,y):
        if self.isdrawing:
            rad = int(self.radius_edit.text())
            if rad < 0:
                rad = 5
                print('radius is must positive ,now rad:%d'%rad)

            if self.islabing:

                cv2.circle(self.curlabel,(x,y),radius=rad,color=(255,255,255),thickness= -1)
                self.showimg = self._cal_showimg(self.curimg,self.curlabel)
                self.show_img_fun(self.showimg,False)

                self.sBar.showMessage('labing')

            else:

                cv2.circle(self.curlabel, (x, y), radius=rad, color=(0, 0, 0),thickness= -1)
                self.showimg = self._cal_showimg(self.curimg, self.curlabel)
                self.show_img_fun(self.showimg,False)

                self.sBar.showMessage('lab_erase')


def main():
    app = QtGui.QApplication(sys.argv)
    seg = Seg_label_tool(sys.argv)
    seg.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
