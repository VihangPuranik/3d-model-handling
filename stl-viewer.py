from pyqtgraph.Qt import QtCore, QtWidgets
import pyqtgraph as pg
import pyqtgraph.opengl as gl

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *  

import numpy as np
from stl import mesh

from pathlib import Path
        
class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(700, 300, 900, 600) 
        self.setAcceptDrops(True)
        
        self.initUI()
        
        self.currentSTL = None
        self.lastDir = None
        self.filename = None
        
        self.droppedFilename = None
    
    def initUI(self):
        centerWidget = QWidget()
        self.setCentralWidget(centerWidget)
        
        layout = QVBoxLayout()
        centerWidget.setLayout(layout)
        
        self.viewer = gl.GLViewWidget()
        layout.addWidget(self.viewer, 1)
        
        self.viewer.setWindowTitle('STL Viewer')
        self.viewer.setCameraPosition(distance=5)
        
        #g = gl.GLGridItem()
        #g.setSize(200, 200)
        #g.setSpacing(5, 5)
        #self.viewer.addItem(g)

        btn = QPushButton(text="Load STL")
        btn.clicked.connect(self.showDialog)
        btn.setFont(QFont("Ricty Diminished", 14))
        layout.addWidget(btn)

        btn2 = QPushButton(text="Refine STL")
        btn2.clicked.connect(self.refineSTL)
        btn2.setFont(QFont("Ricty Diminished", 14))
        layout.addWidget(btn2)
            
    def showDialog(self):
        directory = Path("")
        if self.lastDir:
            directory = self.lastDir
        fname = QFileDialog.getOpenFileName(self, "Open file", str(directory), "STL (*.stl)")
        if fname[0]:
            self.filename = fname[0]
            self.showSTL()
            self.lastDir = Path(fname[0]).parent

    def refineSTL(self):
        points, faces = self.loadSTL(self.filename)
        numfaces = len(faces)
        numpoints = len(points)

        numedges = numfaces + numpoints - 2
        
        new_points = np.empty((numpoints+3*numedges,3))
        new_points[:numpoints] = points
        new_faces = np.empty_like(faces)
        new_faces[:numfaces] = faces
        
        for i in range(numfaces):
            p1 = points[faces[i][0]]
            p2 = points[faces[i][1]]
            p3 = points[faces[i][2]]

            p4 = (p1 + p2)/2
            p4 = p4/np.linalg.norm(p4)
            p5 = (p2 + p3)/2
            p5 = p5/np.linalg.norm(p5)
            p6 = (p3 + p1)/2
            p6 = p6/np.linalg.norm(p6)

            if p4 not in new_points:
                new_points[numpoints,:] = p4
                numpoints += 1
                p4_id = numpoints
            else:
                p4_id = np.where(new_points == p4)[0]

            if p5 not in new_points:
                new_points[numpoints,:] = p5
                numpoints += 1
                p5_id = numpoints
            else:
                p5_id = np.where(new_points == p5)[0]

            if p6 not in new_points:
                new_points[numpoints,:] = p6
                numpoints += 1
                p6_id = numpoints
            else:
                p6_id = np.where(new_points == p6)[0]

            np.concatenate(new_faces, [faces[i][0], p4_id, p6_id])
            np.concatenate(new_faces, [faces[i][1], p4_id, p5_id])
            np.concatenate(new_faces, [faces[i][2], p5_id, p6_id])
                
        print('Okay')
        if self.currentSTL:
            self.viewer.removeItem(self.currentSTL)

        meshdata = gl.MeshData(vertexes=new_points, faces=new_faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.viewer.addItem(mesh)
            
    def showSTL(self):
        if self.currentSTL:
            self.viewer.removeItem(self.currentSTL)

        points, faces = self.loadSTL(self.filename)
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        mesh = gl.GLMeshItem(meshdata=meshdata, smooth=True, drawFaces=False, drawEdges=True, edgeColor=(0, 1, 0, 1))
        self.viewer.addItem(mesh)
        
        self.currentSTL = mesh
        
    def loadSTL(self, filename):
        m = mesh.Mesh.from_file(filename)
        shape = m.points.shape
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces

    def dragEnterEvent(self, e):
        print("enter")
        mimeData = e.mimeData()
        mimeList = mimeData.formats()
        filename = None
        
        if "text/uri-list" in mimeList:
            filename = mimeData.data("text/uri-list")
            filename = str(filename, encoding="utf-8")
            filename = filename.replace("file:///", "").replace("\r\n", "").replace("%20", " ")
            filename = Path(filename)
            
        if filename.exists() and filename.suffix == ".stl":
            e.accept()
            self.droppedFilename = filename
        else:
            e.ignore()
            self.droppedFilename = None
        
    def dropEvent(self, e):
        if self.droppedFilename:
            self.showSTL(self.droppedFilename)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
