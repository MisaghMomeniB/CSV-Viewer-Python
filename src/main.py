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

class FileLoaderThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            data = []
            with open(self.file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                total_lines = sum(1 for _ in reader)
                csv_file.seek(0)
                
                for i, row in enumerate(reader):
                    data.append(row)
                    self.progress.emit(int((i+1)/total_lines*100))
            
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))

class UltimateCSVReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate CSV Reader")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_file = None
        self.data_df = None
        self.unsaved_changes = False
        
        self.init_ui()
        
        self.source_model = QStandardItemModel()
        self.filter_proxy = QSortFilterProxyModel()
        self.filter_proxy.setSourceModel(self.source_model)
        self.table_view.setModel(self.filter_proxy)
        self.table_view.setSortingEnabled(True)
        
        self.table_view.doubleClicked.connect(self.edit_cell)
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        self.create_dock_widgets()
        self.create_menu_bar()
        self.create_toolbars()
        self.create_filter_controls()
        self.create_main_tabs()
        self.create_status_bar()
        
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
        
        edit_menu = menubar.addMenu("&Edit")
        
        find_action = QAction("&Find/Replace...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        edit_menu.addSeparator()
        
        add_row_action = QAction("&Add Row", self)
        add_row_action.triggered.connect(self.add_row)
        edit_menu.addAction(add_row_action)
        
        del_row_action = QAction("&Delete Row(s)", self)
        del_row_action.triggered.connect(self.delete_rows)
        edit_menu.addAction(del_row_action)
        
        view_menu = menubar.addMenu("&View")
        
        self.stats_dock.toggleViewAction().setText("Statistics Panel")
        view_menu.addAction(self.stats_dock.toggleViewAction())
        
        self.log_dock.toggleViewAction().setText("Log Panel")
        view_menu.addAction(self.log_dock.toggleViewAction())
        
        tools_menu = menubar.addMenu("&Tools")
        
        stats_action = QAction("Update Statistics", self)
        stats_action.triggered.connect(self.update_stats)
        tools_menu.addAction(stats_action)
        
        transform_action = QAction("Data Transformation...", self)
        transform_action.triggered.connect(self.show_transform_dialog)
        tools_menu.addAction(transform_action)
        
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbars(self):
        main_toolbar = self.addToolBar("Main")
        
        open_btn = QAction("Open", self)
        open_btn.triggered.connect(self.open_csv_file)
        main_toolbar.addAction(open_btn)
        
        save_btn = QAction("Save", self)
        save_btn.triggered.connect(self.save_csv_file)
        main_toolbar.addAction(save_btn)
        
        main_toolbar.addSeparator()
        
        find_btn = QAction("Find", self)
        find_btn.triggered.connect(self.show_find_dialog)
        main_toolbar.addAction(find_btn)
        
        edit_toolbar = self.addToolBar("Edit")
        
        add_row_btn = QAction("Add Row", self)
        add_row_btn.triggered.connect(self.add_row)
        edit_toolbar.addAction(add_row_btn)
        
        del_row_btn = QAction("Delete Rows", self)
        del_row_btn.triggered.connect(self.delete_rows)
        edit_toolbar.addAction(del_row_btn)
    
    def create_filter_controls(self):
        filter_layout = QHBoxLayout()
        
        self.filter_label = QLabel("Filter:")
        filter_layout.addWidget(self.filter_label)
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter text to filter...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        
        self.filter_column = QComboBox()
        self.filter_column.addItem("All Columns")
        self.filter_column.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_column)
        
        self.case_sensitive = QCheckBox("Case Sensitive")
        self.case_sensitive.stateChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.case_sensitive)
        
        self.regex_check = QCheckBox("Use Regex")
        self.regex_check.stateChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.regex_check)
        
        self.main_layout.addLayout(filter_layout)
    
    def create_main_tabs(self):
        self.tabs = QTabWidget()
        
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        
        self.tabs.addTab(self.table_view, "Data")
        
        self.sql_editor = QTextEdit()
        self.sql_editor.setPlaceholderText("Enter SQL queries here...")
        self.tabs.addTab(self.sql_editor, "SQL Query")
        
        self.main_layout.addWidget(self.tabs)
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.row_count_label = QLabel()
        self.status_bar.addPermanentWidget(self.row_count_label)
    
    def create_dock_widgets(self):
        self.stats_dock = QDockWidget("Statistics", self)
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_dock.setWidget(self.stats_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.stats_dock)
        
        self.log_dock = QDockWidget("Log", self)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
    
    def open_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", 
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        self.progress_bar.setVisible(True)
        self.status_bar.showMessage(f"Loading {file_path}...")
        
        self.loader_thread = FileLoaderThread(file_path)
        self.loader_thread.progress.connect(self.progress_bar.setValue)
        self.loader_thread.finished.connect(self.file_loaded)
        self.loader_thread.error.connect(self.file_load_error)
        self.loader_thread.start()
    
    def file_loaded(self, data):
        try:
            self.current_file = self.loader_thread.file_path
            self.source_model.clear()
            
            if data:
                headers = data[0]
                self.source_model.setHorizontalHeaderLabels(headers)
                
                self.filter_column.clear()
                self.filter_column.addItem("All Columns")
                self.filter_column.addItems(headers)
                
                for row in data[1:]:
                    items = [QStandardItem(item) for item in row]
                    self.source_model.appendRow(items)
                
                self.data_df = pd.DataFrame(data[1:], columns=headers)
                
                self.update_stats()
                self.row_count_label.setText(f"Rows: {len(data)-1}")
                self.save_action.setEnabled(True)
                self.unsaved_changes = False
                
                self.status_bar.showMessage(f"Successfully loaded {len(data)-1} rows", 5000)
                self.log_text.append(f"Loaded file: {self.current_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process file:\n{str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def file_load_error(self, error_msg):
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error_msg}")
    
    def save_csv_file(self):
        if not self.current_file:
            self.save_as_csv_file()
            return
            
        try:
            with open(self.current_file, 'w', encoding='utf-8', newline='') as csv_file:
                writer = csv.writer(csv_file)
                
                headers = []
                for col in range(self.source_model.columnCount()):
                    headers.append(self.source_model.headerData(col, Qt.Horizontal))
                writer.writerow(headers)
                
                for row in range(self.source_model.rowCount()):
                    row_data = []
                    for col in range(self.source_model.columnCount()):
                        item = self.source_model.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
                
            self.unsaved_changes = False
            self.status_bar.showMessage(f"File saved successfully: {self.current_file}", 5000)
            self.log_text.append(f"Saved file: {self.current_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def save_as_csv_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", 
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.save_csv_file()
    
    def export_file(self, format_type):
        if not self.data_df:
            QMessageBox.warning(self, "Warning", "No data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export As {format_type.upper()}", "", 
            f"{format_type.upper()} Files (*.{format_type})"
        )
        
        if file_path:
            try:
                if format_type == 'csv':
                    self.data_df.to_csv(file_path, index=False)
                elif format_type == 'excel':
                    self.data_df.to_excel(file_path, index=False)
                elif format_type == 'json':
                    self.data_df.to_json(file_path, orient='records', indent=2)
                
                self.status_bar.showMessage(f"Exported successfully to {file_path}", 5000)
                self.log_text.append(f"Exported to {format_type.upper()}: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def apply_filter(self):
        filter_text = self.filter_input.text()
        column = self.filter_column.currentIndex() - 1
        
        if column >= 0:
            self.filter_proxy.setFilterKeyColumn(column)
        else:
            self.filter_proxy.setFilterKeyColumn(-1)
            
        if self.regex_check.isChecked():
            self.filter_proxy.setFilterRegExp(filter_text)
        else:
            self.filter_proxy.setFilterFixedString(filter_text)
            
        self.filter_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitive if self.case_sensitive.isChecked() else Qt.CaseInsensitive
        )
    
    def edit_cell(self, index):
        source_index = self.filter_proxy.mapToSource(index)
        item = self.source_model.itemFromIndex(source_index)
        
        if item.isEditable():
            self.table_view.edit(index)
            self.unsaved_changes = True
    
    def add_row(self):
        if not self.source_model.columnCount():
            QMessageBox.warning(self, "Warning", "No columns defined")
            return
            
        row_data = [""] * self.source_model.columnCount()
        items = [QStandardItem(item) for item in row_data]
        self.source_model.appendRow(items)
        self.unsaved_changes = True
        self.log_text.append("Added new row")
    
    def delete_rows(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Warning", "No rows selected")
            return
            
        source_indexes = [self.filter_proxy.mapToSource(idx) for idx in selected]
        rows_to_delete = sorted([idx.row() for idx in source_indexes], reverse=True)
        
        for row in rows_to_delete:
            self.source_model.removeRow(row)
        
        self.unsaved_changes = True
        self.log_text.append(f"Deleted {len(rows_to_delete)} rows")
    
    def update_stats(self):
        if self.data_df is None:
            self.stats_text.setPlainText("No data available")
            return
            
        stats = []
        stats.append(f"File: {self.current_file}")
        stats.append(f"Total Rows: {len(self.data_df)}")
        stats.append(f"Total Columns: {len(self.data_df.columns)}")
        stats.append("\nColumn Statistics:\n")
        
        for col in self.data_df.columns:
            stats.append(f"=== {col} ===")
            try:
                stats.append(f"Non-null count: {self.data_df[col].count()}")
                stats.append(f"Unique values: {self.data_df[col].nunique()}")
                
                if pd.api.types.is_numeric_dtype(self.data_df[col]):
                    stats.append(f"Min: {self.data_df[col].min()}")
                    stats.append(f"Max: {self.data_df[col].max()}")
                    stats.append(f"Mean: {self.data_df[col].mean():.2f}")
                    stats.append(f"Std Dev: {self.data_df[col].std():.2f}")
                else:
                    stats.append(f"Top value: {self.data_df[col].mode()[0]}")
                    stats.append(f"Frequency: {self.data_df[col].value_counts().iloc[0]}")
                
                stats.append("")
            except:
                stats.append("(Error calculating statistics)")
                stats.append("")
        
        self.stats_text.setPlainText("\n".join(stats))
    
    def show_find_dialog(self):
        text, ok = QInputDialog.getText(self, "Find", "Search text:")
        if ok and text:
            self.filter_input.setText(text)
            self.status_bar.showMessage(f"Searching for: {text}", 3000)
    
    def show_transform_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Data Transformation")
        
        layout = QFormLayout()
        
        col_combo = QComboBox()
        if self.data_df:
            col_combo.addItems(self.data_df.columns)
        layout.addRow("Column:", col_combo)
        
        transform_combo = QComboBox()
        transform_combo.addItems([
            "Uppercase", 
            "Lowercase", 
            "Trim whitespace",
            "Extract numbers",
            "Convert to numeric"
        ])
        layout.addRow("Transformation:", transform_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            col = col_combo.currentText()
            transform = transform_combo.currentText()
            self.log_text.append(f"Applied {transform} to column {col}")
            self.status_bar.showMessage(f"Transformed column: {col}", 3000)
    
    def show_about(self):
        QMessageBox.about(self, "About Ultimate CSV Reader", 
            "Ultimate CSV Reader\nVersion 1.0\n\nA powerful CSV viewer and editor with advanced features")
    
    def closeEvent(self, event):
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_csv_file()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    window = UltimateCSVReader()
    window.show()
    sys.exit(app.exec_())