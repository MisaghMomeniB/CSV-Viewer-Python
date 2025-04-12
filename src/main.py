import sys
import csv
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QFileDialog,
    QVBoxLayout, QWidget, QPushButton, QLabel, QStatusBar,
    QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QAction,
    QMenu, QDockWidget, QTextEdit, QTabWidget, QProgressBar,
    QInputDialog, QDialog, QFormLayout, QSpinBox, QCheckBox,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
import json

# A separate thread for loading large CSV files to avoid UI freezing
class FileLoaderThread(QThread):
    progress = pyqtSignal(int)  # Signal to update progress bar
    finished = pyqtSignal(list)  # Signal to return loaded data
    error = pyqtSignal(str)  # Signal to return error messages

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path  # Store file path

    def run(self):
        try:
            data = []  # Initialize list to store CSV data
            with open(self.file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                total_lines = sum(1 for _ in reader)  # Count total lines
                csv_file.seek(0)  # Reset file pointer
                
                for i, row in enumerate(reader):
                    data.append(row)  # Append row data
                    self.progress.emit(int((i+1)/total_lines*100))  # Emit progress
            
            self.finished.emit(data)  # Emit loaded data
        except Exception as e:
            self.error.emit(str(e))  # Emit error message

# Main class for the Ultimate CSV Reader application
class UltimateCSVReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate CSV Reader")  # Set window title
        self.setGeometry(100, 100, 1200, 800)  # Set window size
        
        self.current_file = None  # Store the currently loaded file path
        self.data_df = None  # Store data as a Pandas DataFrame
        self.unsaved_changes = False  # Track if there are unsaved changes
        
        self.init_ui()  # Initialize UI components
        
        self.source_model = QStandardItemModel()  # Model to hold table data
        self.filter_proxy = QSortFilterProxyModel()  # Proxy model for filtering
        self.filter_proxy.setSourceModel(self.source_model)  # Set data source

        # Create the table view and set the proxy model to it
        self.table_view = QTableView(self)
        self.table_view.setModel(self.filter_proxy)  # Set proxy model to table
        self.table_view.setSortingEnabled(True)  # Enable sorting
        
        self.table_view.doubleClicked.connect(self.edit_cell)  # Enable cell editing
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        self.create_dock_widgets()  # Create dock widgets
        self.create_menu_bar()  # Create menu bar
        self.create_toolbars()  # Create toolbars
        self.create_filter_controls()  # Create filter controls
        self.create_main_tabs()  # Create main tabs (Data, SQL)
        self.create_status_bar()  # Create status bar
        
        # Add the table view to the main layout
        self.main_layout.addWidget(self.table_view)  # Ensure this line comes after table_view is defined
    
    def create_filter_controls(self):
        # Create filter controls
        filter_layout = QHBoxLayout()
        
        # Label for the filter controls
        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)
        
        # ComboBox for selecting a column to filter by
        self.filter_column = QComboBox()
        filter_layout.addWidget(self.filter_column)
        
        # LineEdit for entering filter text
        self.filter_text = QLineEdit()
        filter_layout.addWidget(self.filter_text)
        
        # Add the filter controls layout to the main layout
        self.main_layout.addLayout(filter_layout)
        
        # Connect the filter text input to the filtering function
        self.filter_text.textChanged.connect(self.apply_filter)
        self.filter_column.currentIndexChanged.connect(self.apply_filter)

    def apply_filter(self):
        # Get the selected column and filter text
        column = self.filter_column.currentText()
        filter_value = self.filter_text.text()
        
        # If "All Columns" is selected, show all rows
        if column == "All Columns":
            self.filter_proxy.setFilterRegExp(filter_value)
        else:
            column_index = self.source_model.horizontalHeaderLabels().index(column)
            self.filter_proxy.setFilterKeyColumn(column_index)
            self.filter_proxy.setFilterRegExp(filter_value)

    def create_dock_widgets(self):
        # You can implement additional dock widgets here if needed
        pass

    def create_toolbars(self):
        # You can implement toolbars here if needed
        pass
    
    def create_main_tabs(self):
        self.tab_widget = QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)
        
        self.data_tab = QWidget()
        self.sql_tab = QWidget()
        
        self.tab_widget.addTab(self.data_tab, "Data")
        self.tab_widget.addTab(self.sql_tab, "SQL")
        
        self.data_layout = QVBoxLayout()
        self.data_tab.setLayout(self.data_layout)
        
        self.sql_layout = QVBoxLayout()
        self.sql_tab.setLayout(self.sql_layout)
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)  # Initially hidden
        self.status_bar.addWidget(self.progress_bar)
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_csv_file)
        file_menu.addAction(open_action)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_csv_file)
        file_menu.addAction(self.save_action)
        
        export_menu = file_menu.addMenu("&Export")
        
        export_csv = QAction("As CSV...", self)
        export_csv.triggered.connect(lambda: self.export_file('csv'))
        export_menu.addAction(export_csv)
        
        export_excel = QAction("As Excel...", self)
        export_excel.triggered.connect(lambda: self.export_file('excel'))
        export_menu.addAction(export_excel)
        
        export_json = QAction("As JSON...", self)
        export_json.triggered.connect(lambda: self.export_file('json'))
        export_menu.addAction(export_json)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # Function to open a CSV file
    def open_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", 
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)

    # Function to load file asynchronously
    def load_file(self, file_path):
        self.progress_bar.setVisible(True)  # Show progress bar
        self.status_bar.showMessage(f"Loading {file_path}...")

        self.loader_thread = FileLoaderThread(file_path)
        self.loader_thread.progress.connect(self.progress_bar.setValue)
        self.loader_thread.finished.connect(self.file_loaded)
        self.loader_thread.error.connect(self.file_load_error)
        self.loader_thread.start()

    # Function to handle successful file load
    def file_loaded(self, data):
        try:
            self.current_file = self.loader_thread.file_path  # Store file path
            self.source_model.clear()  # Clear existing data

            if data:
                headers = data[0]  # First row as headers
                self.source_model.setHorizontalHeaderLabels(headers)  # Set headers
                
                self.filter_column.clear()
                self.filter_column.addItem("All Columns")
                self.filter_column.addItems(headers)

                for row in data[1:]:  # Add data rows
                    items = [QStandardItem(item) for item in row]
                    self.source_model.appendRow(items)

                self.data_df = pd.DataFrame(data[1:], columns=headers)  # Create DataFrame

                self.update_stats()  # Update statistics panel
                self.row_count_label.setText(f"Rows: {len(data)-1}")  # Update row count
                self.save_action.setEnabled(True)  # Enable save action
                self.unsaved_changes = False  # Reset unsaved changes flag

                self.status_bar.showMessage(f"Successfully loaded {len(data)-1} rows", 5000)
                self.log_text.append(f"Loaded file: {self.current_file}.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process file:\n{str(e)}")
        finally:
            self.progress_bar.setVisible(False)  # Hide progress bar

    # Function to handle file load errors
    def file_load_error(self, error_msg):
        self.progress_bar.setVisible(False)  # Hide progress bar
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error_msg}")

    def save_csv_file(self):
        # Implement saving functionality here
        pass

    def export_file(self, file_type):
        # Implement file export functionality here (CSV, Excel, JSON)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltimateCSVReader()
    window.show()
    sys.exit(app.exec_())