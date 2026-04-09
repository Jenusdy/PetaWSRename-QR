import shutil
import cv2
import pyzbar.pyzbar as pyzbar
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSignal as Signal, QRunnable, pyqtSlot as Slot, QThreadPool
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QDesktopWidget, QPushButton, QMessageBox, QLineEdit, \
    QLabel, QFileDialog, QProgressBar, QRadioButton
from pathlib import Path
import sys
import os
import pandas as pd
import pytesseract
import cv2
from glob import glob
import re

path_input = ''
path_output = ''
list_images = []
list_log = []
metode = 0

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'


class Signals(QObject):
    completed = Signal(list)


class Worker(QRunnable):
    def __init__(self, n):
        super().__init__()
        self.n = n
        self.signals = Signals()

    def get_file_extension(self, file_path):
        if not os.path.exists(file_path):
            return ""

        file_name, file_extension = os.path.splitext(file_path)
        return file_name, file_extension

    def detect_qr_code(self, image_path):
        image = cv2.imread(image_path)
        qr_codes = pyzbar.decode(image)
        return qr_codes

    def detect_ocr_code(self, image_path):
        img = cv2.imread(image_path)

        panjang1 = img.shape[0]
        lebar1 = img.shape[1]

        if panjang1 > lebar1:
            img = cv2.resize(img, (904, 1280))
            panjang1 = img.shape[0]
            lebar1 = img.shape[1]
            panjang0 = round(panjang1 - panjang1 * 96 / 100)
            lebar0 = round(lebar1 - lebar1 * 30 / 100)
        else:
            img = cv2.resize(img, (1280, 904))
            panjang1 = img.shape[0]
            lebar1 = img.shape[1]
            panjang0 = round(panjang1 - panjang1 * 95 / 100)
            lebar0 = round(lebar1 - lebar1 * 20 / 100)

        output = img[0:panjang0, lebar0:lebar1 - 1]
        text = pytesseract.image_to_string(output)
        return text

    def create_folder_if_not_exists(self, folder_path):
        if os.path.exists(folder_path):
            return True
        try:
            os.makedirs(folder_path)
            return True
        except OSError as e:
            print(e)
            return False

    def copy_and_rename_file(self, source_file_path, destination_file_path):
        if not os.path.exists(source_file_path):
            return False
        try:
            shutil.copy(source_file_path, destination_file_path)
            os.rename(destination_file_path, destination_file_path)
            return True
        except Exception as e:
            print(e)
            return False

    @Slot()
    def run(self):
        file_name, file_extension = self.get_file_extension(self.n)
        file_name = file_name.split(os.sep)[-1]

        if metode == 2:
            qr_codes = self.detect_qr_code(self.n)

            result = []
            if len(qr_codes) == 0:
                result = [file_name, "", "Gagal", "Tidak ada QR ditemukan!"]
            else:
                for qr_code in qr_codes:
                    idsls = qr_code.data.decode()
                    idkab = idsls[:4]
                    kdkec = idsls[4:7]
                    kddesa = idsls[7:10]

                    path_folder_destination = path_output + os.path.sep + idkab + os.path.sep + kdkec + os.path.sep + \
                                              kddesa
                    path_file_destination = path_folder_destination + os.path.sep + idsls + file_extension
                    self.create_folder_if_not_exists(path_folder_destination)
                    self.copy_and_rename_file(source_file_path=self.n, destination_file_path=path_file_destination)
                    result = [file_name, idsls, "Berhasil", "Berhasil melakukan rename file!"]
            self.signals.completed.emit(result)

        elif metode == 1:
            text = self.detect_ocr_code(self.n)
            if text != "":
                nama_file = re.findall(r'\d+', text)
                nama_file = "".join(nama_file)

                idsls = nama_file
                idkab = idsls[:4]
                kdkec = idsls[4:7]
                kddesa = idsls[7:10]

                path_folder_destination = path_output + os.path.sep + idkab + os.path.sep + kdkec + os.path.sep + \
                                          kddesa
                path_file_destination = path_folder_destination + os.path.sep + idsls + file_extension
                self.create_folder_if_not_exists(path_folder_destination)
                self.copy_and_rename_file(source_file_path=self.n, destination_file_path=path_file_destination)

                result = [file_name, nama_file, "Berhasil", "Berhasil melakukan rename file!"]
                self.signals.completed.emit(result)
            else:
                result = [file_name, "", "Gagal", "Tidak ada nomor SLS ditemukan!"]
                self.signals.completed.emit(result)


class PetaWSRename(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 400, 600, 100)
        self.completed_jobs = []

        layout = QGridLayout()
        self.setLayout(layout)

        dir_btn_input = QPushButton('Browse', clicked=self.open_dir_input_dialog)
        self.dir_input_name = QLineEdit()
        self.dir_input_name.setReadOnly(True)
        dir_btn_output = QPushButton('Browse', clicked=self.open_dir_output_dialog)
        self.dir_output_name = QLineEdit()
        self.dir_output_name.setReadOnly(True)
        self.prosesBtn = QPushButton('Proses', clicked=self.proses)
        self.progressBar = QProgressBar(minimum=0)
        self.progressBar.setProperty("value", 0)
        self.prosesSekarang = QLabel()
        self.prosesSekarang.setText("Belum ada proses")

        layout.addWidget(QLabel('Metode '), 1, 0, 1, 1)
        cs1 = QRadioButton("OCR", self)
        layout.addWidget(cs1, 2, 0, 1, 2)

        cs1.toggled.connect(self.change_metode_ocr)

        cs2 = QRadioButton("QR-Code", self)
        layout.addWidget(cs2, 2, 1, 1, 1)
        cs2.toggled.connect(self.change_metode_qr)

        layout.addWidget(QLabel('Folder Input'), 3, 0, 1, 1)
        layout.addWidget(self.dir_input_name, 3, 1, 1, 1)
        layout.addWidget(dir_btn_input, 3, 2, 1, 1)

        layout.addWidget(QLabel('Folder Output'), 4, 0, 1, 1)
        layout.addWidget(self.dir_output_name, 4, 1, 1, 1)
        layout.addWidget(dir_btn_output, 4, 2, 1, 1)

        layout.addWidget(QLabel('Proses'), 5, 0, 1, 1)
        layout.addWidget(self.prosesSekarang, 5, 1, 1, 2)

        layout.addWidget(QLabel('Progress'), 6, 0, 1, 1)
        layout.addWidget(self.progressBar, 6, 1, 1, 2)

        layout.addWidget(self.prosesBtn, 7, 2, 1, 1)

        self.setWindowTitle('PetaWS-QRCodeReader (v1.0.2)')
        self.setWindowIcon(QtGui.QIcon('resource/sweety.ico'))
        self.center()
        self.show()

    def open_dir_input_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            global path_input
            path = Path(dir_name)
            path_input = str(path)
            self.dir_input_name.setText(path_input)
            print(path_input)

    def open_dir_output_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            global path_output
            path = Path(dir_name)
            path_output = str(path)
            self.dir_output_name.setText(path_output)
            print(path_output)

    def change_metode_ocr(self):
        global metode
        metode = 1

    def change_metode_qr(self):
        global metode
        metode = 2

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Keluar', 'Apakah Anda yakin ingin keluar?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def is_folder_empty(self, folder_path):
        if not os.path.exists(folder_path):
            return True

        if not os.listdir(folder_path):
            return True
        return False

    def restart(self):
        self.progressBar.setValue(0)
        self.completed_jobs = []

    def proses(self):
        self.restart()

        if metode == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Belum memilih metode")
            msg.setInformativeText('Harap pilih metode terlebih dahulu')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        if path_input == '' or path_output == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Input/Output")
            msg.setInformativeText('Harap memilih folder output dan input terlebih dahulu')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        if not self.is_folder_empty(path_output):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Output")
            msg.setInformativeText('Untuk folder output harap dibuat kosong!')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        types = ('*.jpg', '*.JPEG', '*.jpeg')
        global list_images
        list_images = []
        for files in types:
            list_images.extend(glob(path_input + os.path.sep + files))

        if len(list_images) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Folder Input")
            msg.setInformativeText('Untuk folder input yang Anda pilih tidak terdapat file gambar!')
            msg.setWindowTitle("Galat")
            msg.exec_()
            return

        self.prosesBtn.setDisabled(True)
        self.progressBar.setMaximum(len(list_images))
        self.prosesSekarang.setText("Harap tunggu! Memuat file gambar...")
        pool = QThreadPool.globalInstance()
        for i in list_images:
            worker = Worker(i)
            worker.signals.completed.connect(self.complete)
            pool.start(worker)

    def complete(self, n):
        print("Job {} completed".format(n))
        self.completed_jobs.append(n)
        self.prosesSekarang.setText(n[0])
        self.progressBar.setValue(len(self.completed_jobs))

        if len(self.completed_jobs) == len(list_images):
            self.createRekap()
            self.prosesBtn.setEnabled(True)
            self.prosesSekarang.setText("Proses selesai silahkan cek folder output!")

    def createRekap(self):
        df_result = pd.DataFrame(self.completed_jobs, columns=[
            "Nama File",
            "Nama Hasil",
            "Status",
            "Info"
        ])
        df_result.to_excel(path_output + os.path.sep + "Hasil.xlsx", index=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PetaWSRename()
    win.show()
    sys.exit(app.exec_())
