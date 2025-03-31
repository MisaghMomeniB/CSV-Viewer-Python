import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QFileDialog, 
    QVBoxLayout, QWidget, QPushButton, QLabel, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class CSVReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Reader با PyQt5")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)