import sys
import time
import random
import os
import math
from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QPlainTextEdit, QFileDialog, QMessageBox,
    QComboBox, QDialog, QFormLayout, QSpinBox, QSplitter
)

# УСТАНОВИТЕ БИБЛИОТЕКУ!!! pip install PyQt6
# --- Диалог настроек ---
class SettingsDialog(QDialog):
    def __init__(self, current_interval, current_theme, parent=None):
        super().__init__(parent)
        lang = parent.current_language if parent else "Русский"
        self.setWindowTitle("Настройки" if lang == "Русский" else "Settings")
        self.resize(300, 150)
        self.interval = current_interval
        self.theme = current_theme
        layout = QFormLayout()

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 50)
        self.interval_spin.setValue(current_interval)
        self.interval_spin.setSuffix(" ms")
        label_interval = "Интервал анимации:" if lang == "Русский" else "Animation interval:"
        layout.addRow(label_interval, self.interval_spin)

        self.theme_combo = QComboBox()
        # Темы в порядке: Light, Dark, Blue, Light Blue, Red, Green, Orange, Yellow, Indigo, Violet, Rainbow, Gradient, Shimmer
        themes = ["Light", "Dark", "Blue", "Light Blue", "Red", "Green", "Orange", "Yellow", "Indigo", "Violet",
                  "Rainbow", "Gradient", "Shimmer"]
        self.theme_combo.addItems(themes)
        self.theme_combo.setCurrentText(current_theme)
        label_theme = "Тема интерфейса:" if lang == "Русский" else "Interface theme:"
        layout.addRow(label_theme, self.theme_combo)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        cancel_text = "Отмена" if lang == "Русский" else "Cancel"
        self.cancel_btn = QPushButton(cancel_text)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

        self.setLayout(layout)

    def getSettings(self):
        return self.interval_spin.value(), self.theme_combo.currentText()


# --- Основное окно ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Задаём язык и тему до вызова setup_ui
        self.current_language = "Русский"  # по умолчанию русский
        self.current_theme = "Light"
        self.animation_interval = 6  # мс (примерно 165 Гц)
        # Дополнительные стили оформления
        self.themes = {
            "Light": "",
            "Dark": """
                QWidget { background-color: #2b2b2b; color: #dcdcdc; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #3c3f41; color: #dcdcdc; }
                QPushButton { background-color: #3c3f41; color: #dcdcdc; }
            """,
            "Blue": """
                QWidget { background-color: #D0E7FF; color: #003366; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #E6F2FF; color: #003366; }
                QPushButton { background-color: #B3D1FF; color: #003366; }
            """,
            "Light Blue": """
                QWidget { background-color: #E0F7FA; color: #006064; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #B2EBF2; color: #006064; }
                QPushButton { background-color: #80DEEA; color: #006064; }
            """,
            "Red": """
                QWidget { background-color: #FFCDD2; color: #B71C1C; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #FFEBEE; color: #B71C1C; }
                QPushButton { background-color: #EF9A9A; color: #B71C1C; }
            """,
            "Green": """
                QWidget { background-color: #C8E6C9; color: #1B5E20; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #E8F5E9; color: #1B5E20; }
                QPushButton { background-color: #A5D6A7; color: #1B5E20; }
            """,
            "Orange": """
                QWidget { background-color: #FFE0B2; color: #E65100; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #FFF3E0; color: #E65100; }
                QPushButton { background-color: #FFCC80; color: #E65100; }
            """,
            "Yellow": """
                QWidget { background-color: #FFF9C4; color: #F57F17; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #FFFDE7; color: #F57F17; }
                QPushButton { background-color: #FFF59D; color: #F57F17; }
            """,
            "Indigo": """
                QWidget { background-color: #C5CAE9; color: #1A237E; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #E8EAF6; color: #1A237E; }
                QPushButton { background-color: #9FA8DA; color: #1A237E; }
            """,
            "Violet": """
                QWidget { background-color: #E1BEE7; color: #4A148C; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #F3E5F5; color: #4A148C; }
                QPushButton { background-color: #CE93D8; color: #4A148C; }
            """,
            "Rainbow": """
                QWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:0.2 orange, stop:0.4 yellow, stop:0.6 green, stop:0.8 blue, stop:1 violet); color: white; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:0.2 orange, stop:0.4 yellow, stop:0.6 green, stop:0.8 blue, stop:1 violet); color: white; }
                QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 violet, stop:1 red); color: white; }
            """,
            "Gradient": """
                QWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7e5f, stop:1 #feb47b); color: #333; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #fff; color: #333; }
                QPushButton { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7e5f, stop:1 #feb47b); color: #333; }
            """,
            "Shimmer": """
                QWidget { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4e54c8, stop:1 #8f94fb); color: white; }
                QLineEdit, QPlainTextEdit, QProgressBar { background-color: #ffffff; color: #4e54c8; }
                QPushButton { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #4e54c8, stop:1 #8f94fb); color: white; }
            """
        }

        self.setWindowTitle("Физический калькулятор" if self.current_language == "Русский" else "Physics Calculator")
        self.resize(600, 800)
        self.setup_ui()

        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(self.animation_interval)
        self.animation_timer.timeout.connect(self.update_animation)

        # Переменные для этапов решения
        self.solution_history = ""
        self.current_stage = 0
        self.stages = []
        self.stage_start_time = None
        self.stage_duration = None

        # Результаты расчёта (будут храниться в словаре)
        self.result_values = {}
        # История расчётов
        self.history_list = []

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # --- Верхняя панель: выбор режима, языка, настройки ---
        top_layout = QHBoxLayout()
        self.mode_label = QLabel("Режим:" if self.current_language == "Русский" else "Mode:")
        top_layout.addWidget(self.mode_label)

        self.mode_combo = QComboBox()
        if self.current_language == "English":
            self.mode_combo.addItems(["Acceleration and Distance", "Kinetic Energy", "Projectile Motion"])
        else:
            self.mode_combo.addItems(["Ускорение и расстояние", "Кинетическая энергия", "Движение снаряда"])
        self.mode_combo.currentTextChanged.connect(self.mode_changed)
        top_layout.addWidget(self.mode_combo)

        self.language_label = QLabel("Язык:" if self.current_language == "Русский" else "Language:")
        top_layout.addWidget(self.language_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        self.lang_combo.currentTextChanged.connect(self.language_changed)
        top_layout.addWidget(self.lang_combo)

        self.settings_btn = QPushButton("Настройки" if self.current_language == "Русский" else "Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(self.settings_btn)
        main_layout.addLayout(top_layout)

        # --- Поля ввода (динамические) ---
        self.inputs_layout = QVBoxLayout()
        self.input_fields = {}
        self.setup_input_fields()
        main_layout.addLayout(self.inputs_layout)

        # --- Кнопка расчёта ---
        self.calc_button = QPushButton("Рассчитать" if self.current_language == "Русский" else "Calculate")
        self.calc_button.clicked.connect(self.start_calculation)
        main_layout.addWidget(self.calc_button)

        # --- Прогресс-бар и метки ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1000)
        main_layout.addWidget(self.progress_bar)

        self.stage_label = QLabel(
            "Нажмите «Рассчитать», чтобы начать" if self.current_language == "Русский" else "Press 'Calculate' to start")
        main_layout.addWidget(self.stage_label)

        self.time_label = QLabel(
            "Оставшееся время: -- сек" if self.current_language == "Русский" else "Remaining time: -- s")
        main_layout.addWidget(self.time_label)

        # --- Область для решения и история (QSplitter) ---
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.solution_edit = QPlainTextEdit()
        self.solution_edit.setReadOnly(True)
        splitter.addWidget(self.solution_edit)
        self.history_edit = QPlainTextEdit()
        self.history_edit.setReadOnly(True)
        placeholder = "История расчётов" if self.current_language == "Русский" else "Calculation history"
        self.history_edit.setPlaceholderText(placeholder)
        splitter.addWidget(self.history_edit)
        splitter.setSizes([400, 150])
        main_layout.addWidget(splitter)

        # --- Финальный результат ---
        self.result_label = QLabel("")
        main_layout.addWidget(self.result_label)

        # --- Кнопки сохранения и сброса ---
        btn_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить решение" if self.current_language == "Русский" else "Save solution")
        self.save_button.clicked.connect(self.save_solution)
        self.save_button.setEnabled(False)
        btn_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Сброс" if self.current_language == "Русский" else "Reset")
        self.reset_button.clicked.connect(self.reset_all)
        btn_layout.addWidget(self.reset_button)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.apply_theme()

    def setup_input_fields(self):
        for i in reversed(range(self.inputs_layout.count())):
            widget = self.inputs_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.input_fields.clear()
        mode = self.mode_combo.currentText()
        if mode in ["Ускорение и расстояние", "Acceleration and Distance"]:
            self.input_fields["v0"] = QLineEdit()
            placeholder = "Initial speed (m/s)" if self.current_language == "English" else "Начальная скорость (м/с)"
            self.input_fields["v0"].setPlaceholderText(placeholder)
            self.input_fields["v0"].setValidator(QDoubleValidator())
            label_text = "Initial speed (v0):" if self.current_language == "English" else "Начальная скорость (v0):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["v0"])

            self.input_fields["v1"] = QLineEdit()
            placeholder = "Final speed (m/s)" if self.current_language == "English" else "Конечная скорость (м/с)"
            self.input_fields["v1"].setPlaceholderText(placeholder)
            self.input_fields["v1"].setValidator(QDoubleValidator())
            label_text = "Final speed (v1):" if self.current_language == "English" else "Конечная скорость (v1):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["v1"])

            self.input_fields["t"] = QLineEdit()
            placeholder = "Time (s)" if self.current_language == "English" else "Время (с)"
            self.input_fields["t"].setPlaceholderText(placeholder)
            self.input_fields["t"].setValidator(QDoubleValidator())
            label_text = "Time (t):" if self.current_language == "English" else "Время (t):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["t"])
        elif mode in ["Кинетическая энергия", "Kinetic Energy"]:
            self.input_fields["m"] = QLineEdit()
            placeholder = "Mass (kg)" if self.current_language == "English" else "Масса (кг)"
            self.input_fields["m"].setPlaceholderText(placeholder)
            self.input_fields["m"].setValidator(QDoubleValidator())
            label_text = "Mass (m):" if self.current_language == "English" else "Масса (m):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["m"])

            self.input_fields["v"] = QLineEdit()
            placeholder = "Speed (m/s)" if self.current_language == "English" else "Скорость (м/с)"
            self.input_fields["v"].setPlaceholderText(placeholder)
            self.input_fields["v"].setValidator(QDoubleValidator())
            label_text = "Speed (v):" if self.current_language == "English" else "Скорость (v):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["v"])
        elif mode in ["Projectile Motion", "Движение снаряда"]:
            self.input_fields["v0"] = QLineEdit()
            placeholder = "Initial speed (m/s)" if self.current_language == "English" else "Начальная скорость (м/с)"
            self.input_fields["v0"].setPlaceholderText(placeholder)
            self.input_fields["v0"].setValidator(QDoubleValidator())
            label_text = "Initial speed (v0):" if self.current_language == "English" else "Начальная скорость (v0):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["v0"])

            self.input_fields["angle"] = QLineEdit()
            placeholder = "Launch angle (°)" if self.current_language == "English" else "Угол броска (°)"
            self.input_fields["angle"].setPlaceholderText(placeholder)
            self.input_fields["angle"].setValidator(QDoubleValidator())
            label_text = "Launch angle (θ):" if self.current_language == "English" else "Угол броска (θ):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["angle"])

            self.input_fields["h0"] = QLineEdit()
            placeholder = "Initial height (m)" if self.current_language == "English" else "Начальная высота (м)"
            self.input_fields["h0"].setPlaceholderText(placeholder)
            self.input_fields["h0"].setValidator(QDoubleValidator())
            label_text = "Initial height (h0):" if self.current_language == "English" else "Начальная высота (h0):"
            self.inputs_layout.addWidget(QLabel(label_text))
            self.inputs_layout.addWidget(self.input_fields["h0"])

    def mode_changed(self, mode_text):
        self.setup_input_fields()

    def language_changed(self, lang):
        self.current_language = lang
        if lang == "English":
            self.setWindowTitle("Physics Calculator")
            self.calc_button.setText("Calculate")
            self.stage_label.setText("Press 'Calculate' to start")
            self.save_button.setText("Save solution")
            self.reset_button.setText("Reset")
            self.time_label.setText("Remaining time: -- s")
            self.history_edit.setPlaceholderText("Calculation history")
            self.mode_label.setText("Mode:")
            self.language_label.setText("Language:")
            self.settings_btn.setText("Settings")
            self.mode_combo.blockSignals(True)
            self.mode_combo.clear()
            self.mode_combo.addItems(["Acceleration and Distance", "Kinetic Energy", "Projectile Motion"])
            self.mode_combo.blockSignals(False)
        else:
            self.setWindowTitle("Физический калькулятор")
            self.calc_button.setText("Рассчитать")
            self.stage_label.setText("Нажмите «Рассчитать», чтобы начать")
            self.save_button.setText("Сохранить решение")
            self.reset_button.setText("Сброс")
            self.time_label.setText("Оставшееся время: -- сек")
            self.history_edit.setPlaceholderText("История расчётов")
            self.mode_label.setText("Режим:")
            self.language_label.setText("Язык:")
            self.settings_btn.setText("Настройки")
            self.mode_combo.blockSignals(True)
            self.mode_combo.clear()
            self.mode_combo.addItems(["Ускорение и расстояние", "Кинетическая энергия", "Движение снаряда"])
            self.mode_combo.blockSignals(False)
        self.setup_input_fields()

    def open_settings(self):
        dlg = SettingsDialog(self.animation_interval, self.current_theme, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            interval, theme = dlg.getSettings()
            self.animation_interval = interval
            self.current_theme = theme
            self.animation_timer.setInterval(self.animation_interval)
            self.apply_theme()

    def apply_theme(self):
        style = self.themes.get(self.current_theme, "")
        self.setStyleSheet(style)

    def start_calculation(self):
        for field in self.input_fields.values():
            field.setEnabled(False)
        self.calc_button.setEnabled(False)
        self.save_button.setEnabled(False)

        self.result_label.setText("")
        self.solution_edit.clear()
        self.solution_history = ""

        mode = self.mode_combo.currentText()
        try:
            if mode in ["Ускорение и расстояние", "Acceleration and Distance"]:
                self.result_values["v0"] = float(self.input_fields["v0"].text())
                self.result_values["v1"] = float(self.input_fields["v1"].text())
                self.result_values["t"] = float(self.input_fields["t"].text())
                if self.result_values["t"] == 0:
                    raise ValueError("Time cannot be 0")
            elif mode in ["Projectile Motion", "Движение снаряда"]:
                self.result_values["v0"] = float(self.input_fields["v0"].text())
                self.result_values["angle"] = float(self.input_fields["angle"].text())
                self.result_values["h0"] = float(self.input_fields["h0"].text())
            elif mode in ["Кинетическая энергия", "Kinetic Energy"]:
                self.result_values["m"] = float(self.input_fields["m"].text())
                self.result_values["v"] = float(self.input_fields["v"].text())
        except ValueError:
            err_text = "Ошибка: Введите корректные числовые значения!" if self.current_language == "Русский" else "Error: Please enter valid numbers!"
            self.result_label.setText(err_text)
            self.enable_inputs()
            return

        # Отдельные расчёты по режимам:
        if mode in ["Ускорение и расстояние", "Acceleration and Distance"]:
            a = (self.result_values["v1"] - self.result_values["v0"]) / self.result_values["t"]
            s = self.result_values["v0"] * self.result_values["t"] + 0.5 * a * self.result_values["t"] ** 2
            if self.current_language == "English":
                self.stages = [
                    {
                        "label": "📊 Data accepted, processing begins...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Given:\n"
                            "  - v0 = {} m/s\n"
                            "  - v1 = {} m/s\n"
                            "  - t = {} s\n"
                            "Find:\n"
                            "  - a (acceleration)\n"
                            "  - s (distance traveled)\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["v1"], self.result_values["t"])
                    },
                    {
                        "label": "🛠 Calculating acceleration...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Solution for a:\n"
                            "  1. a = (v1 - v0) / t\n"
                            "  2. a = ({} - {}) / {}\n"
                            "  3. a = {:.2f} m/s²\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v1"], self.result_values["v0"], self.result_values["t"], a)
                    },
                    {
                        "label": "🔄 Calculating distance traveled...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Solution for s:\n"
                            "  1. s = v0 * t + 0.5 * a * t²\n"
                            "  2. s = {} * {} + 0.5 * {:.2f} * {}²\n"
                            "  3. s = {:.2f} m\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["t"],
                                 a, self.result_values["t"], s)
                    },
                    {
                        "label": "📏 Finishing calculation",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Final solution:\n"
                            "  a = {:.2f} m/s²\n"
                            "  s = {:.2f} m\n"
                            "--------------------------------------------------\n"
                            "Thank you for using the program!\n"
                        ).format(a, s)
                    }
                ]
            else:
                self.stages = [
                    {
                        "label": "📊 Данные приняты, начинаем обработку...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Дано:\n"
                            "  - v0 = {} м/с\n"
                            "  - v1 = {} м/с\n"
                            "  - t = {} с\n"
                            "Необходимо найти:\n"
                            "  - a (ускорение)\n"
                            "  - s (пройденное расстояние)\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["v1"], self.result_values["t"])
                    },
                    {
                        "label": "🛠 Расчёт ускорения...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Решение для a:\n"
                            "  1. a = (v1 - v0) / t\n"
                            "  2. a = ({} - {}) / {}\n"
                            "  3. a = {:.2f} м/с²\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v1"], self.result_values["v0"], self.result_values["t"], a)
                    },
                    {
                        "label": "🔄 Рассчитываем пройденное расстояние...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Решение для s:\n"
                            "  1. s = v0 * t + 0.5 * a * t²\n"
                            "  2. s = {} * {} + 0.5 * {:.2f} * {}²\n"
                            "  3. s = {:.2f} м\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["t"],
                                 a, self.result_values["t"], s)
                    },
                    {
                        "label": "📏 Завершение расчёта",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Итоговое решение:\n"
                            "  a = {:.2f} м/с²\n"
                            "  s = {:.2f} м\n"
                            "--------------------------------------------------\n"
                            "Спасибо за использование программы!\n"
                        ).format(a, s)
                    }
                ]
            self.result_values["a"] = a
            self.result_values["s"] = s

        elif mode in ["Projectile Motion", "Движение снаряда"]:
            try:
                g = 9.81
                # Если начальная высота отрицательная, установить в 0
                h0 = self.result_values["h0"]
                if h0 < 0:
                    h0 = 0
                theta = math.radians(self.result_values["angle"])
                t_flight = (self.result_values["v0"] * math.sin(theta) +
                            math.sqrt((self.result_values["v0"] * math.sin(theta)) ** 2 + 2 * g * h0)) / g
                h_max = h0 + (self.result_values["v0"] * math.sin(theta)) ** 2 / (2 * g)
                R = self.result_values["v0"] * math.cos(theta) * t_flight
                self.result_values["t_flight"] = t_flight
                self.result_values["h_max"] = h_max
                self.result_values["R"] = R
            except Exception as e:
                err_text = "Ошибка в расчётах движения снаряда!" if self.current_language == "Русский" else "Error in projectile motion calculations!"
                self.result_label.setText(err_text)
                self.enable_inputs()
                return
            if self.current_language == "English":
                self.stages = [
                    {
                        "label": "📊 Data accepted, processing begins...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Given:\n"
                            "  - v0 = {} m/s\n"
                            "  - Launch angle = {}°\n"
                            "  - Initial height = {} m\n"
                            "Find:\n"
                            "  - Flight time, t\n"
                            "  - Maximum height, h_max\n"
                            "  - Horizontal range, R\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["angle"], self.result_values["h0"])
                    },
                    {
                        "label": "🛠 Calculating flight time...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Solution for flight time:\n"
                            "  t = (v0*sin(θ) + sqrt((v0*sin(θ))² + 2*g*h0)) / g\n"
                            "  t = ({}*sin({}°) + sqrt(({}*sin({}°))² + 2*9.81*{})) / 9.81\n"
                            "  t = {:.2f} s\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["angle"],
                                 self.result_values["v0"], self.result_values["angle"],
                                 self.result_values["h0"], t_flight)
                    },
                    {
                        "label": "🔄 Calculating maximum height and range...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Solution for maximum height and range:\n"
                            "  h_max = h0 + (v0*sin(θ))² / (2*g)\n"
                            "    h_max = {} + ({}*sin({}°))²/(2*9.81) = {:.2f} m\n"
                            "  R = v0*cos(θ)*t\n"
                            "    R = {}*cos({}°)*{:.2f} = {:.2f} m\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["h0"], self.result_values["v0"], self.result_values["angle"], h_max,
                                 self.result_values["v0"], self.result_values["angle"], t_flight, R)
                    },
                    {
                        "label": "📏 Finishing calculation",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Final solution:\n"
                            "  Flight time, t = {:.2f} s\n"
                            "  Maximum height, h_max = {:.2f} m\n"
                            "  Horizontal range, R = {:.2f} m\n"
                            "--------------------------------------------------\n"
                            "Thank you for using the program!\n"
                        ).format(t_flight, h_max, R)
                    }
                ]
            else:
                self.stages = [
                    {
                        "label": "📊 Данные приняты, начинаем обработку...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Дано:\n"
                            "  - v0 = {} м/с\n"
                            "  - Угол броска = {}°\n"
                            "  - Начальная высота = {} м\n"
                            "Необходимо найти:\n"
                            "  - Время полёта, t\n"
                            "  - Максимальную высоту, h_max\n"
                            "  - Горизонтальную дальность, R\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["angle"], self.result_values["h0"])
                    },
                    {
                        "label": "🛠 Расчёт времени полёта...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Решение для времени полёта:\n"
                            "  t = (v0*sin(θ) + sqrt((v0*sin(θ))² + 2*9.81*h0)) / 9.81\n"
                            "  t = ({}*sin({}°) + sqrt(({}*sin({}°))² + 2*9.81*{})) / 9.81\n"
                            "  t = {:.2f} с\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["v0"], self.result_values["angle"],
                                 self.result_values["v0"], self.result_values["angle"],
                                 self.result_values["h0"], t_flight)
                    },
                    {
                        "label": "🔄 Расчёт максимальной высоты и дальности...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Решение для максимальной высоты и дальности:\n"
                            "  h_max = h0 + (v0*sin(θ))² / (2*9.81)\n"
                            "    h_max = {} + ({}*sin({}°))²/(2*9.81) = {:.2f} м\n"
                            "  R = v0*cos(θ)*t\n"
                            "    R = {}*cos({}°)*{:.2f} = {:.2f} м\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["h0"], self.result_values["v0"], self.result_values["angle"], h_max,
                                 self.result_values["v0"], self.result_values["angle"], t_flight, R)
                    },
                    {
                        "label": "📏 Завершение расчёта",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Итоговое решение:\n"
                            "  Время полёта, t = {:.2f} с\n"
                            "  Максимальная высота, h_max = {:.2f} м\n"
                            "  Горизонтальная дальность, R = {:.2f} м\n"
                            "--------------------------------------------------\n"
                            "Спасибо за использование программы!\n"
                        ).format(t_flight, h_max, R)
                    }
                ]
            # Сохраняем вычисленные значения
            self.result_values["t_flight"] = t_flight
            self.result_values["h_max"] = h_max
            self.result_values["R"] = R

        elif mode in ["Кинетическая энергия", "Kinetic Energy"]:
            ke = 0.5 * self.result_values["m"] * self.result_values["v"] ** 2
            if self.current_language == "English":
                self.stages = [
                    {
                        "label": "📊 Data accepted, processing begins...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Given:\n"
                            "  - m = {} kg\n"
                            "  - v = {} m/s\n"
                            "Find:\n"
                            "  - KE (kinetic energy)\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["m"], self.result_values["v"])
                    },
                    {
                        "label": "🛠 Calculating kinetic energy (Part 1)...",
                        "duration": random.uniform(1, 10),
                        "solution": self.get_kinetic_energy_solution_part1()
                    },
                    {
                        "label": "🔄 Calculating kinetic energy (Part 2)...",
                        "duration": random.uniform(1, 10),
                        "solution": self.get_kinetic_energy_solution_part2()
                    },
                    {
                        "label": "📏 Finishing calculation",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Final solution:\n"
                            "  KE = {:.2f} J\n"
                            "--------------------------------------------------\n"
                            "Thank you for using the program!\n"
                        ).format(ke)
                    }
                ]
            else:
                self.stages = [
                    {
                        "label": "📊 Данные приняты, начинаем обработку...",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Дано:\n"
                            "  - m = {} кг\n"
                            "  - v = {} м/с\n"
                            "Необходимо найти:\n"
                            "  - KE (кинетическая энергия)\n"
                            "--------------------------------------------------\n"
                        ).format(self.result_values["m"], self.result_values["v"])
                    },
                    {
                        "label": "🛠 Расчёт кинетической энергии (Часть 1)...",
                        "duration": random.uniform(1, 10),
                        "solution": self.get_kinetic_energy_solution_part1(russian=True)
                    },
                    {
                        "label": "🔄 Расчёт кинетической энергии (Часть 2)...",
                        "duration": random.uniform(1, 10),
                        "solution": self.get_kinetic_energy_solution_part2(russian=True)
                    },
                    {
                        "label": "📏 Завершение расчёта",
                        "duration": random.uniform(1, 10),
                        "solution": (
                            "Итоговое решение:\n"
                            "  KE = {:.2f} Дж\n"
                            "--------------------------------------------------\n"
                            "Спасибо за использование программы!\n"
                        ).format(ke)
                    }
                ]
            self.result_values["KE"] = ke

        self.current_stage = 0
        self.start_stage()

    def get_kinetic_energy_solution_part1(self, russian=False):
        if russian:
            v = self.result_values["v"]
            m = self.result_values["m"]
            v2 = v ** 2
            m_v2 = m * v2
            return (
                "Решение для KE (Часть 1):\n"
                "  Шаг 1: v² = {:.2f} м²/с²\n"
                "  Шаг 2: m * v² = {:.2f} кг·(м²/с²)\n"
                "--------------------------------------------------\n"
            ).format(v2, m_v2)
        else:
            v = self.result_values["v"]
            m = self.result_values["m"]
            v2 = v ** 2
            m_v2 = m * v2
            return (
                "Solution for KE (Part 1):\n"
                "  Step 1: v² = {:.2f} m²/s²\n"
                "  Step 2: m * v² = {:.2f} kg·(m²/s²)\n"
                "--------------------------------------------------\n"
            ).format(v2, m_v2)

    def get_kinetic_energy_solution_part2(self, russian=False):
        if russian:
            m = self.result_values["m"]
            v = self.result_values["v"]
            ke = 0.5 * m * v ** 2
            momentum = m * v
            energy_per_unit = ke / m if m != 0 else 0
            m_v2 = m * (v ** 2)
            return (
                "Решение для KE (Часть 2):\n"
                "  Шаг 3: KE = 0.5 * (m * v²) = 0.5 * {:.2f} = {:.2f} Дж\n"
                "  Дополнительно:\n"
                "    Импульс, p = m * v = {:.2f} кг·м/с\n"
                "    Энергия на единицу массы, KE/m = {:.2f} Дж/кг\n"
                "--------------------------------------------------\n"
            ).format(m_v2, ke, momentum, energy_per_unit)
        else:
            m = self.result_values["m"]
            v = self.result_values["v"]
            ke = 0.5 * m * v ** 2
            momentum = m * v
            energy_per_unit = ke / m if m != 0 else 0
            m_v2 = m * (v ** 2)
            return (
                "Solution for KE (Part 2):\n"
                "  Step 3: KE = 0.5 * (m * v²) = 0.5 * {:.2f} = {:.2f} J\n"
                "  Additionally:\n"
                "    Momentum, p = m * v = {:.2f} kg·m/s\n"
                "    Energy per unit mass, KE/m = {:.2f} J/kg\n"
                "--------------------------------------------------\n"
            ).format(m_v2, ke, momentum, energy_per_unit)

    def enable_inputs(self):
        for field in self.input_fields.values():
            field.setEnabled(True)
        self.calc_button.setEnabled(True)

    def start_stage(self):
        stage = self.stages[self.current_stage]
        self.stage_start_time = time.time()
        self.stage_duration = stage["duration"]
        self.progress_bar.setValue(0)
        self.update_stage_label(0.0)
        self.animation_timer.start()

    def update_animation(self):
        elapsed = time.time() - self.stage_start_time
        progress_percent = (elapsed / self.stage_duration) * 100
        if progress_percent > 100:
            progress_percent = 100
        self.progress_bar.setValue(int(progress_percent * 10))
        self.update_stage_label(progress_percent)
        self.update_solution_text(progress_percent)
        self.update_time_label(self.stage_duration - elapsed)
        if progress_percent >= 100:
            self.animation_timer.stop()
            self.stage_finished()

    def update_stage_label(self, percent):
        stage_label_text = self.stages[self.current_stage]["label"]
        if self.current_language == "English":
            self.stage_label.setText(f"Stage {self.current_stage + 1}/4: {stage_label_text} ({percent:.1f}%)")
        else:
            self.stage_label.setText(f"Этап {self.current_stage + 1}/4: {stage_label_text} ({percent:.1f}%)")

    def update_solution_text(self, percent):
        full_text = self.stages[self.current_stage].get("solution", "")
        chars_to_show = int((percent / 100) * len(full_text))
        current_text = full_text[:chars_to_show]
        self.solution_edit.setPlainText(self.solution_history + current_text)

    def update_time_label(self, remaining):
        if remaining < 0:
            remaining = 0
        if self.current_language == "English":
            self.time_label.setText(f"Remaining time: {remaining:.1f} s")
        else:
            self.time_label.setText(f"Оставшееся время: {remaining:.1f} сек")

    def stage_finished(self):
        full_text = self.stages[self.current_stage].get("solution", "")
        self.solution_history += full_text + "\n"
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self.start_stage()
        else:
            mode = self.mode_combo.currentText()
            if mode in ["Ускорение и расстояние", "Acceleration and Distance"]:
                if self.current_language == "English":
                    result_text = (f"⚡ a = {self.result_values['a']:.2f} m/s²\n"
                                   f"🚀 s = {self.result_values['s']:.2f} m")
                    hist_line = f"Acceleration: {self.result_values['a']:.2f} m/s²; Distance: {self.result_values['s']:.2f} m"
                else:
                    result_text = (f"⚡ a = {self.result_values['a']:.2f} м/с²\n"
                                   f"🚀 s = {self.result_values['s']:.2f} м")
                    hist_line = f"Ускорение: {self.result_values['a']:.2f} м/с²; Расстояние: {self.result_values['s']:.2f} м"
            elif mode in ["Projectile Motion", "Движение снаряда"]:
                if self.current_language == "English":
                    result_text = (f"✈ Flight time = {self.result_values['t_flight']:.2f} s\n"
                                   f"⛰ Maximum height = {self.result_values['h_max']:.2f} m\n"
                                   f"🏃 Horizontal range = {self.result_values['R']:.2f} m")
                    hist_line = (f"Projectile Motion: Flight time: {self.result_values['t_flight']:.2f} s; "
                                 f"Max height: {self.result_values['h_max']:.2f} m; Range: {self.result_values['R']:.2f} m")
                else:
                    result_text = (f"✈ Время полёта = {self.result_values['t_flight']:.2f} с\n"
                                   f"⛰ Максимальная высота = {self.result_values['h_max']:.2f} м\n"
                                   f"🏃 Горизонтальная дальность = {self.result_values['R']:.2f} м")
                    hist_line = (f"Движение снаряда: Время полёта: {self.result_values['t_flight']:.2f} с; "
                                 f"Макс высота: {self.result_values['h_max']:.2f} м; Дальность: {self.result_values['R']:.2f} м")
            else:
                if self.current_language == "English":
                    result_text = f"KE = {self.result_values['KE']:.2f} J"
                    hist_line = f"Kinetic energy: {self.result_values['KE']:.2f} J"
                else:
                    result_text = f"KE = {self.result_values['KE']:.2f} Дж"
                    hist_line = f"Кинетическая энергия: {self.result_values['KE']:.2f} Дж"
            self.result_label.setText(result_text)
            self.stage_label.setText("All done!" if self.current_language == "English" else "Всё готово!")
            self.progress_bar.setValue(1000)
            self.enable_inputs()
            self.save_button.setEnabled(True)
            self.history_list.append(hist_line)
            self.update_history()

    def update_history(self):
        self.history_edit.setPlainText("\n".join(self.history_list))

    def save_solution(self):
        if not self.solution_history.strip():
            msg = "Решение отсутствует. Сначала выполните расчёт." if self.current_language == "Русский" else "No solution available. Please perform a calculation first."
            QMessageBox.information(self,
                                    "Сохранение решения" if self.current_language == "Русский" else "Save solution",
                                    msg)
            return
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить решение" if self.current_language == "Русский" else "Save solution",
            os.getcwd(),
            "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(self.solution_history)
            except Exception as e:
                err_msg = f"Не удалось сохранить файл:\n{e}" if self.current_language == "Русский" else f"Failed to save file:\n{e}"
                QMessageBox.critical(self, "Ошибка сохранения" if self.current_language == "Русский" else "Save Error",
                                     err_msg)

    def reset_all(self):
        for field in self.input_fields.values():
            field.clear()
            field.setEnabled(True)
        self.calc_button.setEnabled(True)
        self.solution_edit.clear()
        self.solution_history = ""
        self.result_label.setText("")
        self.stage_label.setText(
            "Нажмите «Рассчитать», чтобы начать" if self.current_language == "Русский" else "Press 'Calculate' to start")
        self.progress_bar.setValue(0)
        self.time_label.setText(
            "Оставшееся время: -- сек" if self.current_language == "Русский" else "Remaining time: -- s")
        self.save_button.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
