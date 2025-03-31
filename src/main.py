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
        
        # ایجاد ویجت‌های اصلی
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # ایجاد دکمه برای باز کردن فایل
        self.open_button = QPushButton("باز کردن فایل CSV")
        self.open_button.clicked.connect(self.open_csv_file)
        self.layout.addWidget(self.open_button)
        
        # برچسب برای نمایش اطلاعات فایل
        self.file_info_label = QLabel("هیچ فایلی انتخاب نشده است")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.file_info_label)
        
        # ایجاد جدول برای نمایش داده‌های CSV
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)
        
        # ایجاد نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # مدل داده برای جدول
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        
    def open_csv_file(self):
        # نمایش دیالوگ انتخاب فایل
        file_path, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل CSV", "", "فایل‌های CSV (*.csv);;همه فایل‌ها (*)"
        )
        
        if file_path:
            try:
                # خواندن فایل CSV
                with open(file_path, 'r', encoding='utf-8') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    data = list(csv_reader)
                
                # تنظیم اطلاعات فایل در برچسب
                self.file_info_label.setText(f"فایل: {file_path} - تعداد سطرها: {len(data)}")
                
                # پاک کردن مدل قبلی
                self.model.clear()
                
                # تنظیم هدرهای ستون
                if data:
                    headers = data[0]
                    self.model.setHorizontalHeaderLabels(headers)
                    
                    # پر کردن مدل با داده‌ها
                    for row in data[1:]:
                        items = [QStandardItem(item) for item in row]
                        self.model.appendRow(items)
                
                self.status_bar.showMessage("فایل با موفقیت بارگذاری شد", 3000)
                
            except Exception as e:
                self.status_bar.showMessage(f"خطا: {str(e)}", 5000)
                self.file_info_label.setText("خطا در خواندن فایل CSV")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVReaderApp()
    window.show()
    sys.exit(app.exec_())