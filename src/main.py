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
        