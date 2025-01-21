import sys
import json
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QMenuBar,
    QStatusBar,
    QFileDialog,
    QMessageBox,
    QColorDialog,
)
from PySide6.QtGui import QAction, QImage, QPainter 
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import inputfilereader
import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D-Viewer mit VTK")
        self.resize(800, 600)

        # Initialize model
        self.model = None

        # Create main layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Add VTK render window
        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        self.layout.addWidget(self.vtk_widget)

        # Create VTK renderer
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # Setup menu
        self._create_menu()

        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.show()

    def _create_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_model)
        file_menu.addAction(save_action)

        import_action = QAction("Import FDD", self)
        import_action.triggered.connect(self.import_fdd)
        file_menu.addAction(import_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        #######
        background_menu = menu_bar.addMenu("Background")

        white_action = QAction("white", self)
        white_action.triggered.connect(self.white)
        background_menu.addAction(white_action)    

        black_action = QAction("black", self)
        black_action.triggered.connect(self.black)
        background_menu.addAction(black_action) 

        ######
        screenshot_menu = menu_bar.addMenu("Screenshot")

        jpg_screenshot_action = QAction("Save Screenshot as jpg", self)
        jpg_screenshot_action.triggered.connect(self.save_screenshot_as_jpg)
        screenshot_menu.addAction(jpg_screenshot_action)



        self.setMenuBar(menu_bar)

    def load_model(self):
        """Load a model from a JSON file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Model", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.model = mbsModel.mbsModel()  # Initialize the model
                self.model.loadDatabase(file_name)  # Load the model from JSON
                self.status_bar.showMessage(f"Model loaded: {file_name}")
                self.render_model()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model: {e}")

    def save_model(self):
        """Save the current model to a JSON file."""
        if not self.model:
            QMessageBox.warning(self, "Warning", "No model to save.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "JSON Files (*.json)")
        if file_name:
            try:
                self.model.saveDatabase(file_name)  # Save the model as JSON
                self.status_bar.showMessage(f"Model saved: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save model: {e}")

    def import_fdd(self):
        """Import a model from a .fdd file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Import FDD File", "", "FDD Files (*.fdd)")
        if file_name:
            try:
                self.model = mbsModel.mbsModel()  # Initialize the model
                if self.model.importFddFile(file_name):  # Import the model from FDD
                    self.status_bar.showMessage(f"FDD file imported: {file_name}")
                    self.render_model()
                else:
                    QMessageBox.critical(self, "Error", "Failed to import FDD file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import FDD file: {e}")

    def white(self):

        color = "#FFFFFF"  # White color in hex format
        self.central_widget.setStyleSheet(f"background-color: {color};")
        self.renderer.SetBackground(1.0, 1.0, 1.0)  # RGB values for white
        self.vtk_widget.GetRenderWindow().Render()  # Update the VTK render window

        # Update the status bar
        self.status_bar.showMessage("Background color changed to white.")

    def black(self):
   
        color = "#000000"  # Black color in hex format
        self.central_widget.setStyleSheet(f"background-color: {color};")
        self.renderer.SetBackground(0.0, 0.0, 0.0)  # RGB values for black
        self.vtk_widget.GetRenderWindow().Render()  # Update the VTK render window

        # Update the status bar
        self.status_bar.showMessage("Background color changed to black.")



    def save_screenshot_as_jpg(self):
        """Capture a screenshot of the current window and save it as a jpg."""
        try:
            render_window = self.vtk_widget.GetRenderWindow()
            window_to_image_filter = vtk.vtkWindowToImageFilter()
            window_to_image_filter.SetInput(render_window)
            window_to_image_filter.Update()

            vtk_image = window_to_image_filter.GetOutput()

            # Convert the VTK image to a QImage
            width, height, _ = vtk_image.GetDimensions()
            vtk_data = vtk_image.GetPointData().GetScalars()
            components = vtk_data.GetNumberOfComponents()

            # Create a QImage from the VTK image data
            if components == 3:
                format = QImage.Format_RGB888
            elif components == 4:
                format = QImage.Format_RGBA8888
            else:
                raise ValueError("Unsupported number of components in VTK image")

            qimage = QImage(vtk_data, width, height, width * components, format)
            qimage = qimage.mirrored(False, True)

            # Ask user for file location to save the JPG
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "JPEG Files (*.jpg)")
            if file_name:
                # Save the QImage to a JPG file
                if qimage.save(file_name, "JPG"):
                    self.status_bar.showMessage(f"Screenshot saved as JPG: {file_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save screenshot as JPG.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save screenshot as JPG: {e}")

    def render_model(self):
        """Render the model in the VTK window."""
        if not self.model:
            return

        self.renderer.RemoveAllViewProps()  # Clear the renderer

    #    if Body:
    #        self.model.showFilteredModel(self.renderer,Body)
    #   else:
        self.model.showModel(self.renderer)  # Use model's showModel method

        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

def main():
    # If there's a command line argument for the .fdd file, handle that first
    if len(sys.argv) > 1:
        fdd_file_path = sys.argv[1]
        app = QApplication(sys.argv)
        window = MainWindow()

        if window.model is None:
            window.model = mbsModel.mbsModel()
        window.model.importFddFile(fdd_file_path)
        window.render_model()
        sys.exit(app.exec())

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
