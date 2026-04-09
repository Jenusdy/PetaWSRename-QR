from PyQt5.QtCore import QObject, QRunnable, pyqtSignal as Signal, pyqtSlot as Slot

from config.constants import METHOD_OCR, METHOD_QR
from models.process_result import ProcessResult


class WorkerSignals(QObject):
    completed = Signal(object)


class ImageWorker(QRunnable):
    def __init__(self, image_path, output_dir, method, qr_service, ocr_service, file_service):
        super().__init__()
        self.image_path = image_path
        self.output_dir = output_dir
        self.method = method
        self.qr_service = qr_service
        self.ocr_service = ocr_service
        self.file_service = file_service
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            if self.method == METHOD_QR:
                self.process_qr()
            elif self.method == METHOD_OCR:
                self.process_ocr()
        except Exception as e:
            self.signals.completed.emit(
                ProcessResult(self.image_path.split('\\')[-1], '', 'Gagal', str(e))
            )

    def process_qr(self):
        idsls = self.qr_service.detect(self.image_path)

        if not idsls:
            self.signals.completed.emit(
                ProcessResult(self.image_path.split('\\')[-1], '', 'Gagal', 'Tidak ada QR ditemukan!')
            )
            return

        self.file_service.save(self.image_path, self.output_dir, idsls)

        self.signals.completed.emit(
            ProcessResult(self.image_path.split('\\')[-1], idsls, 'Berhasil', 'Berhasil melakukan rename file!')
        )

    def process_ocr(self):
        idsls = self.ocr_service.detect(self.image_path)

        if not idsls:
            self.signals.completed.emit(
                ProcessResult(self.image_path.split('\\')[-1], '', 'Gagal', 'Tidak ada nomor SLS ditemukan!')
            )
            return

        self.file_service.save(self.image_path, self.output_dir, idsls)

        self.signals.completed.emit(
            ProcessResult(self.image_path.split('\\')[-1], idsls, 'Berhasil', 'Berhasil melakukan rename file!')
        )