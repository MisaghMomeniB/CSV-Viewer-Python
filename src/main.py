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
        
        self.open_button = QPushButton("باز کردن فایل CSV")
        self.open_button.clicked.connect(self.open_csv_file)
        self.layout.addWidget(self.open_button)
        
        self.file_info_label = QLabel("هیچ فایلی انتخاب نشده است")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_info_label)