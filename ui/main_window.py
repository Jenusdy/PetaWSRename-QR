import os
from glob import glob

from PyQt5 import QtGui
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QLineEdit, QLabel,
    QFileDialog, QProgressBar, QRadioButton, QMessageBox,
    QDesktopWidget
)

from config.constants import METHOD_NONE, METHOD_OCR, METHOD_QR
from services.qr_service import QRService
from services.ocr_service import OCRService
from services.file_service import FileService
from services.report_service import ReportService
from workers.image_worker import ImageWorker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.input_path = ''
        self.output_path = ''
        self.method = METHOD_NONE
        self.completed_jobs = []
        self.image_files = []

        self.qr_service = QRService()
        self.ocr_service = OCRService()
        self.file_service = FileService()
        self.report_service = ReportService()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 400, 600, 100)
        layout = QGridLayout(self)

        self.dir_input = QLineEdit(readOnly=True)
        self.dir_output = QLineEdit(readOnly=True)
        self.progress = QProgressBar(minimum=0)
        self.status_label = QLabel('Belum ada proses')
        self.process_btn = QPushButton('Proses', clicked=self.process_images)

        ocr_radio = QRadioButton('OCR')
        qr_radio = QRadioButton('QR-Code')

        ocr_radio.toggled.connect(lambda c: c and self.set_method(METHOD_OCR))
        qr_radio.toggled.connect(lambda c: c and self.set_method(METHOD_QR))

        layout.addWidget(QLabel('Metode'), 0, 0)
        layout.addWidget(ocr_radio, 0, 1)
        layout.addWidget(qr_radio, 0, 2)

        layout.addWidget(QLabel('Folder Input'), 1, 0)
        layout.addWidget(self.dir_input, 1, 1)
        layout.addWidget(QPushButton('Browse', clicked=self.select_input), 1, 2)

        layout.addWidget(QLabel('Folder Output'), 2, 0)
        layout.addWidget(self.dir_output, 2, 1)
        layout.addWidget(QPushButton('Browse', clicked=self.select_output), 2, 2)

        layout.addWidget(QLabel('Proses'), 3, 0)
        layout.addWidget(self.status_label, 3, 1, 1, 2)

        layout.addWidget(QLabel('Progress'), 4, 0)
        layout.addWidget(self.progress, 4, 1, 1, 2)

        layout.addWidget(self.process_btn, 5, 2)

        self.setWindowTitle('PetaWS-QRCodeReader')
        self.setWindowIcon(QtGui.QIcon('resource/sweety.ico'))
        self.center()
    
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_method(self, method):
        self.method = method

    def select_input(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if path:
            self.input_path = path
            self.dir_input.setText(path)

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if path:
            self.output_path = path
            self.dir_output.setText(path)

    def process_images(self):
        if not self.validate_inputs():
            return

        self.completed_jobs.clear()
        self.load_images()

        self.progress.setMaximum(len(self.image_files))
        self.process_btn.setDisabled(True)

        pool = QThreadPool.globalInstance()

        for image_path in self.image_files:
            worker = ImageWorker(
                image_path,
                self.output_path,
                self.method,
                self.qr_service,
                self.ocr_service,
                self.file_service
            )
            worker.signals.completed.connect(self.on_complete)
            pool.start(worker)

    def validate_inputs(self):
        if self.method == METHOD_NONE:
            QMessageBox.critical(self, 'Galat', 'Pilih metode terlebih dahulu')
            return False

        if not self.input_path or not self.output_path:
            QMessageBox.critical(self, 'Galat', 'Pilih folder input/output terlebih dahulu')
            return False

        if os.path.exists(self.output_path) and os.listdir(self.output_path):
            QMessageBox.critical(self, 'Galat', 'Folder output harus kosong')
            return False

        return True

    def load_images(self):
        self.image_files = []
        for pattern in ('*.jpg', '*.jpeg', '*.JPEG'):
            self.image_files.extend(glob(os.path.join(self.input_path, pattern)))

    def on_complete(self, result):
        self.completed_jobs.append(result)
        self.progress.setValue(len(self.completed_jobs))
        self.status_label.setText(result.file_name)

        if len(self.completed_jobs) == len(self.image_files):
            self.report_service.export(self.output_path, self.completed_jobs)
            self.process_btn.setEnabled(True)
            self.status_label.setText('Proses selesai')