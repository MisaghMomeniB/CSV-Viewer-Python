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
        self.setWindowTitle("CSV Reader with PyQt5")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widgets
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Create button to open file
        self.open_button = QPushButton("Open CSV File")
        self.open_button.clicked.connect(self.open_csv_file)
        self.layout.addWidget(self.open_button)
        
        # Label to display file info
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_info_label)
        
        # Create table to display CSV data
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Data model for the table
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        
    def open_csv_file(self):
        # Show file selection dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                # Read CSV file
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    data = list(csv_reader)
                
                # Set file info in label
                self.file_info_label.setText(f"File: {file_path} - Rows: {len(data)}")
                
                # Clear previous model
                self.model.clear()
                
                # Set column headers
                if data:
                    headers = data[0]
                    self.model.setHorizontalHeaderLabels(headers)
                    
                    # Fill model with data
                    for row in data[1:]:
                        items = [QStandardItem(item) for item in row]
                        self.model.appendRow(items)
                
                self.status_bar.showMessage("File loaded successfully", 3000)
                
            except Exception as e:
                self.status_bar.showMessage(f"Error: {str(e)}", 5000)
                self.file_info_label.setText("Error reading CSV file")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVReaderApp()
    window.show()
    sys.exit(app.exec_())