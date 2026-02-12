"""
run with: python -m scripts.gui_v2
"""
import sys, time
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSlider, QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QLabel, QProgressBar
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread

from scripts.fluent_processing import FluentPostProcesser

class Images():
    def __init__(self, folder):
        self.folder = Path(folder)
        self.n_images = 0
        self.current_image_index = 0
        self.images: list[QPixmap] = []

        for f in sorted(self.folder.glob("*.png")):
            pixmap = QPixmap(str(f))
            if not pixmap.isNull():
                self.n_images += 1
                self.images.append(pixmap)
    
    def get_image(self, index):
        if 0 <= index < self.n_images:
            return self.images[index]
        return None

class ImageViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        self.parentLayout = QVBoxLayout(central_widget)
        self.sliderLayout = QVBoxLayout()
        self.controllsLayout = QHBoxLayout()

        self.imageContainer = QWidget()
        self.imageLayout = QHBoxLayout(self.imageContainer)
        form = uic.loadUi(r"data\ui\btnAddImage.ui")
        self.btnAddImage: QPushButton = form.findChild(QPushButton, "btnAddImage")
        self.btnAddImage.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.btnsAddImage: list[QPushButton] = [self.btnAddImage]
        self.imageLayout.addWidget(self.btnsAddImage[0])
        self.parentLayout.addWidget(self.imageContainer)
        self.btnAddImage.clicked.connect(self.click_add_image)

        self.imageSlider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self.imageSlider.valueChanged.connect(self.on_slider_change)
        self.sliderLayout.addWidget(self.imageSlider)
        self.parentLayout.addLayout(self.sliderLayout)

        self.btnStop: QPushButton = QPushButton("⏯")
        self.play_state = False
        self.btnStop.clicked.connect(self.click_start_stop)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image_animation)
        self.btnPrevious: QPushButton = QPushButton("⏮")
        self.btnPrevious.clicked.connect(self.click_previous)
        self.btnNext: QPushButton = QPushButton("⏭")
        self.btnNext.clicked.connect(self.click_next)

        for btn in (self.btnPrevious, self.btnStop, self.btnNext):
            btn.setMinimumWidth(60)
            btn.setMaximumWidth(60)
            btn.setMinimumHeight(30)

        self.controllsLayout.addWidget(self.btnPrevious)
        self.controllsLayout.addWidget(self.btnStop)
        self.controllsLayout.addWidget(self.btnNext)
        self.parentLayout.addLayout(self.controllsLayout)

        self.parentLayout.setStretch(0, 5)
        self.parentLayout.setStretch(1, 1)
        self.parentLayout.setStretch(2, 1)

        self.image_series: list[Images] = []
        self.thumb_pixmaps: list[QPixmap] = []

        self.showMaximized()

    def click_add_image(self):
        btn = self.sender()
        if btn not in self.btnsAddImage:
            return
        
        i = self.btnsAddImage.index(btn)

        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return
        
        btn.setText("")

        imgs = Images(folder)
        print(len(self.image_series), i)
        
        if i < len(self.image_series):
            self.image_series[i] = imgs
            thumb_px = imgs.get_image(0)
            self.imageSlider.setValue(0)
            for imgs in self.image_series:
                imgs.current_image_index = 0
            self.thumb_pixmaps[i] = thumb_px
            self.update_thumbnails()
        else:
            self.image_series.append(imgs)
            thumb_px = imgs.get_image(0)
            self.imageSlider.setValue(0)
            for imgs in self.image_series:
                imgs.current_image_index = 0
            self.thumb_pixmaps.append(thumb_px)
            self.create_add_image_button()
            self.update_thumbnails()

    def create_add_image_button(self):
        new_btn = self.btnAddImage.__class__("+")
        new_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        new_btn.clicked.connect(self.click_add_image)

        self.btnsAddImage.append(new_btn)
        self.imageLayout.addWidget(new_btn)

        self.img_width = self.imageContainer.width() // (len(self.btnsAddImage) - 1) - 50
        
        for i, btn in enumerate(self.btnsAddImage):
            if i < len(self.btnsAddImage) - 1:
                btn.setMinimumWidth(self.img_width)
                self.imageLayout.setStretch(i, 1)
            else:
                btn.setMinimumWidth(40)
                self.imageLayout.setStretch(i, 0)
    
    def update_thumbnails(self):
        if not self.thumb_pixmaps:
            return
        
        # size of square-ish thumbnail that fits button
        self.thumb_side = int(min(self.img_width, self.imageContainer.height()))
        if self.thumb_side <= 0:
            return
        for btn, imgs in zip(self.btnsAddImage[:len(self.thumb_pixmaps)], self.image_series):
            orig_px = imgs.get_image(imgs.current_image_index)
            scaled = orig_px.scaled(
                self.thumb_side,
                self.thumb_side,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            btn.setIcon(QIcon(scaled))
            btn.setIconSize(scaled.size())

    def on_slider_change(self, value: int):
        print("Slider value:", value)
        for imgs in self.image_series:
            imgs.current_image_index = round(imgs.n_images * value // 100)
        self.update_thumbnails()

    def click_start_stop(self):
        if self.play_state:
            self.play_state = False
            self.timer.stop()
        else:
            self.play_state = True
            self.timer.start(200)

    def update_image_animation(self):
        for imgs in self.image_series:
            imgs.current_image_index = imgs.current_image_index + 1
            if imgs.current_image_index >= imgs.n_images:
                imgs.current_image_index = 0
        self.visual_update_slider()
        self.update_thumbnails()

    def click_previous(self):
        idx_img_1 = self.image_series[0].current_image_index - 1
        n_imgs = self.image_series[0].n_images
        spot = idx_img_1 / n_imgs
        for imgs in self.image_series:
            imgs.current_image_index = round(spot * imgs.n_images)
            if imgs.current_image_index < 0:
                imgs.current_image_index = 0
        self.visual_update_slider()
        self.update_thumbnails()

    def click_next(self):
        idx_img_1 = self.image_series[0].current_image_index + 1
        n_imgs = self.image_series[0].n_images
        spot = idx_img_1 / n_imgs
        for imgs in self.image_series:
            imgs.current_image_index = round(spot * imgs.n_images)
            if imgs.current_image_index >= imgs.n_images:
                imgs.current_image_index = imgs.n_images - 1
        self.visual_update_slider()
        self.update_thumbnails()

    def visual_update_slider(self):
        slider_idx = round(self.image_series[0].current_image_index / self.image_series[0].n_images * 100)
        self.imageSlider.blockSignals(True)
        self.imageSlider.setValue(slider_idx)
        self.imageSlider.blockSignals(False)



class Worker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, fluent_processor: FluentPostProcesser):
        super().__init__()
        self.fluent_processor = fluent_processor

    def run(self):
        try:
            self.fluent_processor.run()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class AddSimulationWindow(QMainWindow):
    def __init__(self, file_path: Path, fluent_exe_path: Path):
        super().__init__()
        self.setWindowTitle(f"Processing: {file_path.name}")
        self.setMinimumSize(400, 200)
        self.statusBar().showMessage("Processing simulation...")
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.parentLayout = QVBoxLayout(central_widget)

        self.labelContainer = QWidget()
        self.labelLayout = QHBoxLayout(self.labelContainer)
        self.infoLabel = QLabel(f"File to process: {file_path.name}")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelLayout.addWidget(self.infoLabel)
        self.parentLayout.addWidget(self.labelContainer)

        self.buttonLayout = QHBoxLayout()
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.startButton = QPushButton("Start Processing")
        self.startButton.clicked.connect(self.start_processing)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.startButton)
        self.parentLayout.addLayout(self.buttonLayout)

        self.progressBarContainer = QWidget()
        self.progressBarLayout = QHBoxLayout(self.progressBarContainer)
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBarLayout.addWidget(self.progressBar)
        self.parentLayout.addWidget(self.progressBarContainer)

        try:
            self.fluent_processor = FluentPostProcesser(fluent_exe_path, file_path, callback=None)
        except Exception as e:
            fluent_exe_path = QFileDialog.getOpenFileName(self, "Select Fluent Executable", filter="Executable Files (*.exe)")[0]
            if fluent_exe_path:
                try:
                    self.fluent_processor = FluentPostProcesser(fluent_exe_path, file_path, callback=None)
                except Exception as e:
                    print(f"Error initializing FluentPostProcesser: {e}")
                    self.close()
                    return
            else:
                self.close()
                return
        self.show()

    def start_processing(self):
        self.startButton.setEnabled(False)
        self.cancelButton.setEnabled(False)

        self.thread: QThread = QThread()
        self.worker = Worker(self.fluent_processor)
        self.fluent_processor.progress_callback = self.worker.progress.emit
        self.worker.moveToThread(self.thread)

       # Wire signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)      # updates progressBar + status
        self.worker.error.connect(lambda msg: self.statusBar().showMessage(f"Error: {msg}"))
        self.worker.finished.connect(self.thread.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.finished.connect(lambda: self.startButton.setEnabled(True))
        self.thread.finished.connect(lambda: self.cancelButton.setEnabled(True))

        self.thread.start()

    def cancel_processing(self):
        self.close()

    def update_progress(self, value: int):
        self.progressBar.setValue(value)
        if value >= 100:
            self.statusBar().showMessage("Processing complete!")
        else:
            self.statusBar().showMessage(f"Processing... {value}%")



class MainWindow(QMainWindow):
    def __init__(self):
        self.fluent_exe_path = r"C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe"
        super().__init__()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.parentLayout = QVBoxLayout(central_widget)
        self.titleWidget = QWidget()
        self.titleWidget.setMinimumHeight(200)
        self.logoWidget = QWidget()
        self.buttonsWidget = QWidget()
        self.buttonsWidget.setMinimumHeight(200)
        self.parentLayout.addWidget(self.titleWidget)
        self.parentLayout.addWidget(self.logoWidget)
        self.parentLayout.addWidget(self.buttonsWidget)

        self.title_layout = QHBoxLayout(self.titleWidget)
        form = uic.loadUi(r"data\ui\titleMainWindow.ui")
        self.title: QLabel = form.findChild(QLabel, "titleMainWindow")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_layout.addWidget(self.title)

        self.logo_layout = QHBoxLayout(self.logoWidget)
        form = uic.loadUi(r"data\ui\logoBRT.ui")
        self.logo: QLabel = form.findChild(QLabel, "logoBRT")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setScaledContents(True)
        self.logo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.logo.setFixedSize(400, 200)
        self.logo_layout.addWidget(self.logo)

        self.buttons_layout = QHBoxLayout(self.buttonsWidget)
        self.btnViewImages: QPushButton = QPushButton("View Images")
        self.btnViewImages.setMinimumWidth(100)
        self.btnViewImages.setMaximumWidth(100)
        self.btnViewImages.clicked.connect(self.click_view_images)
        self.btnAddSimulation: QPushButton = QPushButton("Add Simulation")
        self.btnAddSimulation.setMinimumWidth(100)
        self.btnAddSimulation.setMaximumWidth(100)
        self.btnAddSimulation.clicked.connect(self.click_add_simulation)
        self.buttons_layout.addWidget(self.btnViewImages)
        self.buttons_layout.addWidget(self.btnAddSimulation)

        # Set size policies to respect layout stretch
        self.titleWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.logoWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.buttonsWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.showMaximized()
        self.parentLayout.setStretch(0, 1)
        self.parentLayout.setStretch(1, 3)
        self.parentLayout.setStretch(2, 3)

    def click_view_images(self):
        print("View images button clicked")
        self.image_viewer = ImageViewerWindow()

    def click_add_simulation(self):
        file_path = QFileDialog.getOpenFileName(self, "Select Simulation File", filter="Simulation Files (*.cas.h5)")[0]
        if file_path:
            print("Selected simulation file:", file_path)
            self.add_simulation_window = AddSimulationWindow(Path(file_path), Path(self.fluent_exe_path))
        

app = QApplication(sys.argv)
main_window = MainWindow()

app.exec()
