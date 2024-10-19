from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import math
from pynput import mouse

class ClickVisualizer(QtWidgets.QWidget):
    click_signal = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super().__init__(None)  # Parent set to None to ensure it's independent
        # Create main window
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setWindowTitle("Mouse Click Visualizer Settings")
        self.main_window.setGeometry(100, 100, 220, 225)

        # Create main widget
        self.main_widget = QtWidgets.QWidget()
        self.main_window.setCentralWidget(self.main_widget)
        layout = QtWidgets.QGridLayout(self.main_widget)

        # Enable Click Animation Toggle
        self.toggle_button = QtWidgets.QCheckBox("Enable Click Animation")
        self.toggle_button.setChecked(True)
        self.toggle_button.stateChanged.connect(self.toggle_animation)
        layout.addWidget(self.toggle_button, 0, 0, 1, 2)

        # Duration Slider
        self.duration_label = QtWidgets.QLabel(f"Duration: {500} ms")
        self.duration_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.duration_slider.setMinimum(5)
        self.duration_slider.setMaximum(3000)
        self.duration_slider.setValue(500)
        self.duration_slider.valueChanged.connect(self.update_duration)
        layout.addWidget(self.duration_label, 1, 0)
        layout.addWidget(self.duration_slider, 1, 1)

        # Shape Dropdown
        self.shape_label = QtWidgets.QLabel("Overlay Shape")
        self.shape_dropdown = QtWidgets.QComboBox()
        self.shape_dropdown.addItems(["Circle", "Square", "Triangle", "Star", "Pentagon", "Hexagon", "Heptagon", "Octagon", "Heart", "Diamond"])
        self.shape_dropdown.currentTextChanged.connect(self.update_shape)
        layout.addWidget(self.shape_label, 2, 0)
        layout.addWidget(self.shape_dropdown, 2, 1)

        # Animation Effect Dropdown
        self.effect_label = QtWidgets.QLabel("Animation Effect")
        self.effect_dropdown = QtWidgets.QComboBox()
        self.effect_dropdown.addItems(["None", "Fade Out", "Grow and Shrink", "Bounce", "Flash"])
        self.effect_dropdown.setCurrentText("None")
        self.effect_dropdown.currentTextChanged.connect(self.update_effect)
        layout.addWidget(self.effect_label, 3, 0)
        layout.addWidget(self.effect_dropdown, 3, 1)

        # Color Picker Button
        self.color_button = QtWidgets.QPushButton("Pick Overlay Color")
        self.color_button.clicked.connect(self.pick_color)
        layout.addWidget(self.color_button, 4, 0, 1, 2)

        # Transparency Slider
        self.transparency_label = QtWidgets.QLabel(f"Transparency: {0.5:.2f}")
        self.transparency_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.transparency_slider.setMinimum(1)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(50)
        self.transparency_slider.valueChanged.connect(self.update_alpha)
        layout.addWidget(self.transparency_label, 5, 0)
        layout.addWidget(self.transparency_slider, 5, 1)

        # Size Slider
        self.size_label = QtWidgets.QLabel(f"Size: {100} px")
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setMinimum(20)
        self.size_slider.setMaximum(200)
        self.size_slider.setValue(100)
        self.size_slider.valueChanged.connect(self.update_size)
        layout.addWidget(self.size_label, 6, 0)
        layout.addWidget(self.size_slider, 6, 1)

        # Show main window
        self.main_window.show()

        # Click Overlay Settings
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.resize(100, 100)
        self.animation_enabled = True
        self.overlay_duration = 500
        self.overlay_shape = "Circle"
        self.overlay_color = "#ff0000"
        self.overlay_size = 100
        self.overlay_effect = "None"
        self.setWindowOpacity(0.5)

        # Start global mouse listener
        self.listener = mouse.Listener(on_click=self.on_global_click)
        self.listener.start()

        # Signal for handling click events in the main thread
        self.click_signal.connect(self.handle_click_signal)

    def toggle_animation(self, state):
        self.animation_enabled = bool(state)
        print(f"Animation Enabled: {self.animation_enabled}")

    def update_duration(self, value):
        self.overlay_duration = value
        self.duration_label.setText(f"Duration: {value} ms")
        print(f"Overlay Duration Updated: {self.overlay_duration} ms")

    def update_shape(self, shape):
        self.overlay_shape = shape
        print(f"Overlay Shape Updated: {self.overlay_shape}")

    def update_effect(self, effect):
        self.overlay_effect = effect
        print(f"Overlay Effect Updated: {self.overlay_effect}")

    def pick_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.overlay_color = color.name()
            print(f"Overlay Color Updated: {self.overlay_color}")

    def update_alpha(self, value):
        alpha = value / 100
        self.transparency_label.setText(f"Transparency: {alpha:.2f}")
        self.setWindowOpacity(alpha)
        print(f"Overlay Transparency Updated: {alpha}")

    def update_size(self, value):
        self.overlay_size = value
        self.size_label.setText(f"Size: {value} px")
        print(f"Overlay Size Updated: {self.overlay_size} px")

    def on_global_click(self, x, y, button, pressed):
        if pressed and self.animation_enabled:
            print(f"Global Mouse Click Detected at ({x}, {y})")
            # Emit signal to handle the click in the main thread
            self.click_signal.emit(x, y)

    @QtCore.pyqtSlot(int, int)
    def handle_click_signal(self, x, y):
        self.show_click(x, y, self.overlay_size, self.overlay_color)

    def show_click(self, x, y, size=100, color="#ff0000"):
        print(f"Showing Click Animation at ({x}, {y}) with size {size} and color {color}")
        self.resize(size, size)
        self.move(x - size // 2, y - size // 2)
        self.overlay_color = color  # Update the overlay color
        self.setWindowOpacity(self.transparency_slider.value() / 100)  # Ensure correct opacity
        self.update()
        self.show()

        if self.overlay_effect == "Fade Out":
            self.fade_out_effect()
        elif self.overlay_effect == "Grow and Shrink":
            self.grow_and_shrink_effect()
        elif self.overlay_effect == "Bounce":
            self.bounce_effect()
        elif self.overlay_effect == "Flash":
            self.flash_effect()
        else:
            QtCore.QTimer.singleShot(self.overlay_duration, self.hide)

    def fade_out_effect(self):
        print("Fade Out Effect")
        # Implement a smooth fade out effect (gradually reduce opacity)
        for i in range(20):
            QtCore.QTimer.singleShot(i * 25, lambda i=i: self.setWindowOpacity(1.0 - i * 0.05))
        QtCore.QTimer.singleShot(self.overlay_duration, self.hide)

    def grow_and_shrink_effect(self):
        print("Grow and Shrink Effect")
        # Implement a grow and shrink effect
        original_size = self.overlay_size
        for i in range(10):
            QtCore.QTimer.singleShot(i * 50, lambda i=i: self.resize(original_size + 10 * i, original_size + 10 * i) if i < 5 else self.resize(original_size + 10 * (10 - i), original_size + 10 * (10 - i)))
        QtCore.QTimer.singleShot(self.overlay_duration, self.hide)

    def bounce_effect(self):
        print("Bounce Effect")
        # Implement a smoother and more exaggerated bounce effect
        original_size = self.overlay_size
        bounce_height = 40  # Increased bounce height for a more pronounced effect
        for i in range(10):
            QtCore.QTimer.singleShot(i * 50, lambda i=i, bounce_height=bounce_height: self.move(self.x(), int(self.y() - bounce_height) if i % 2 == 0 else int(self.y() + bounce_height)))
            bounce_height *= 0.8  # Gradually reduce bounce height for smoother effect
        QtCore.QTimer.singleShot(self.overlay_duration, self.hide)

    def flash_effect(self):
        print("Flash Effect")
        # Implement a flash effect (opacity alternates between high and low)
        for i in range(10):
            QtCore.QTimer.singleShot(i * 100, lambda i=i: self.setWindowOpacity(1.0 if i % 2 == 0 else 0.2))
        QtCore.QTimer.singleShot(self.overlay_duration, self.hide)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.overlay_color)))
        painter.setPen(QtCore.Qt.NoPen)
        if self.overlay_shape == "Circle":
            painter.drawEllipse(0, 0, self.width(), self.height())
        elif self.overlay_shape == "Square":
            painter.drawRect(0, 0, self.width(), self.height())
        elif self.overlay_shape == "Triangle":
            points = [
                QtCore.QPoint(int(self.width() / 2), 0),
                QtCore.QPoint(int(self.width() - 1), int(self.height() - 1)),
                QtCore.QPoint(0, int(self.height() - 1))
            ]
            painter.drawPolygon(QtGui.QPolygon(points))
        elif self.overlay_shape == "Star":
            self.draw_star(painter)
        elif self.overlay_shape == "Pentagon":
            self.draw_polygon(painter, 5)
        elif self.overlay_shape == "Hexagon":
            self.draw_polygon(painter, 6)
        elif self.overlay_shape == "Heptagon":
            self.draw_polygon(painter, 7)
        elif self.overlay_shape == "Octagon":
            self.draw_polygon(painter, 8)
        elif self.overlay_shape == "Heart":
            self.draw_heart(painter)
        elif self.overlay_shape == "Diamond":
            self.draw_diamond(painter)

    def draw_star(self, painter):
        x, y, r, points, ratio = self.width() / 2, self.height() / 2, self.width() / 2, 5, 0.5
        angle = 360 / points
        coords = []
        for i in range(points * 2):
            radius = r if i % 2 == 0 else r * ratio
            theta = (angle * i - 90) * (math.pi / 180)
            coords.append(QtCore.QPointF(x + radius * math.cos(theta), y + radius * math.sin(theta)))
        painter.drawPolygon(QtGui.QPolygonF(coords))

    def draw_polygon(self, painter, sides):
        x, y, r = self.width() / 2, self.height() / 2, self.width() / 2
        angle = 360 / sides
        coords = []
        for i in range(sides):
            theta = (angle * i - 90) * (math.pi / 180)
            coords.append(QtCore.QPointF(x + r * math.cos(theta), y + r * math.sin(theta)))
        painter.drawPolygon(QtGui.QPolygonF(coords))

    def draw_heart(self, painter):
        path = QtGui.QPainterPath()
        width, height = self.width(), self.height()
        path.moveTo(width / 2, height * 0.75)
        path.cubicTo(width, height * 0.25, width * 0.5, 0, width / 2, height * 0.5)
        path.cubicTo(width * 0.5, 0, 0, height * 0.25, width / 2, height * 0.75)
        painter.drawPath(path)

    def draw_diamond(self, painter):
        points = [
            QtCore.QPoint(int(self.width() / 2), 0),
            QtCore.QPoint(self.width() - 1, int(self.height() / 2)),
            QtCore.QPoint(int(self.width() / 2), self.height() - 1),
            QtCore.QPoint(0, int(self.height() / 2))
        ]
        painter.drawPolygon(QtGui.QPolygon(points))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    visualizer = ClickVisualizer()
    sys.exit(app.exec_())
