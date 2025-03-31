import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QFileDialog, 
    QVBoxLayout, QWidget, QPushButton, QLabel, QStatusBar,
    QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QAction, QMenu
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class EnhancedCSVReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced CSV Reader")
        self.setGeometry(100, 100, 1000, 700)
        
        # Current file path
        self.current_file = None
        
        # Create main widgets
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create filter controls
        self.create_filter_controls()
        
        # Create table view
        self.table_view = QTableView()
        self.main_layout.addWidget(self.table_view)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Data models
        self.source_model = QStandardItemModel()
        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setSourceModel(self.source_model)
        self.table_view.setModel(self.filter_proxy)
        
        # Enable sorting
        self.table_view.setSortingEnabled(True)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open", self)
        open_action.triggered.connect(self.open_csv_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save_csv_file)
        file_menu.addAction(save_action)
        
        export_action = QAction("&Export to Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)
        
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        find_action = QAction("&Find", self)
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar("Tools")
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_csv_file)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_csv_file)
        toolbar.addWidget(save_btn)
        
        export_btn = QPushButton("Export Excel")
        export_btn.clicked.connect(self.export_to_excel)
        toolbar.addWidget(export_btn)
        
    def create_filter_controls(self):
        filter_layout = QHBoxLayout()
        
        self.filter_label = QLabel("Filter:")
        filter_layout.addWidget(self.filter_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter text to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        self.filter_column = QComboBox()
        self.filter_column.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_column)
        
        self.main_layout.addLayout(filter_layout)
    
    def open_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    data = list(csv_reader)
                
                self.current_file = file_path
                self.source_model.clear()
                
                if data:
                    headers = data[0]
                    self.source_model.setHorizontalHeaderLabels(headers)
                    
                    # Update filter column dropdown
                    self.filter_column.clear()
                    self.filter_column.addItem("All Columns")
                    self.filter_column.addItems(headers)
                    
                    for row in data[1:]:
                        items = [QStandardItem(item) for item in row]
                        self.source_model.appendRow(items)
                
                self.status_bar.showMessage(f"Loaded {len(data)-1} rows from {file_path}", 5000)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def save_csv_file(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "No file is currently open")
            return
            
        try:
            with open(self.current_file, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file)
                
                # Write headers
                headers = []
                for col in range(self.source_model.columnCount()):
                    headers.append(self.source_model.headerData(col, Qt.Horizontal))
                writer.writerow(headers)
                
                # Write data
                for row in range(self.source_model.rowCount()):
                    row_data = []
                    for col in range(self.source_model.columnCount()):
                        item = self.source_model.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                
            self.status_bar.showMessage(f"File saved successfully: {self.current_file}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def export_to_excel(self):
        # Placeholder for Excel export functionality
        QMessageBox.information(self, "Export", "Excel export functionality would be implemented here")
    
    def show_find_dialog(self):
        # Placeholder for find dialog
        QMessageBox.information(self, "Find", "Find functionality would be implemented here")
    
    def apply_filter(self):
        filter_text = self.filter_input.text()
        column = self.filter_column.currentIndex() - 1  # -1 because first item is "All Columns"
        
        if column >= 0:  # Filter specific column
            self.filter_proxy.setFilterKeyColumn(column)
        else:  # Filter all columns
            self.filter_proxy.setFilterKeyColumn(-1)
            
        self.filter_proxy.setFilterFixedString(filter_text)
    
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        
        copy_action = context_menu.addAction("Copy")
        copy_action.triggered.connect(self.copy_selected)
        
        delete_action = context_menu.addAction("Delete Row")
        delete_action.triggered.connect(self.delete_selected_row)
        
        context_menu.exec_(event.globalPos())
    
    def copy_selected(self):
        # Implement copy functionality
        pass
    
    def delete_selected_row(self):
        # Implement row deletion
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnhancedCSVReader()
    window.show()
    sys.exit(app.exec_())