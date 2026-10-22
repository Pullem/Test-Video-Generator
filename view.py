import datetime

from PyQt6.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
	QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton,
	QFileDialog, QColorDialog, QProgressBar,
	QTextEdit, QComboBox, QTabWidget, QGroupBox, QFormLayout,
	QTableWidget, QTableWidgetItem, QHeaderView,
	QAbstractItemView, QScrollArea, QFrame, QSizePolicy,
	QMenu, QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QSettings
from PyQt6.QtGui import QColor, QFont, QPalette, QIcon, QAction, QKeySequence, QPainter, QPixmap

from model import VideoParams, ImageParams


# ---------- Stil-Konstanten ----------

SPACING = 8
MARGIN = 12
GROUP_PADDING = 16

# ---------- Zentrale Farbpalette ----------

COLOR_PRIMARY    = "#3498db"   # Blau (Video)
COLOR_SUCCESS    = "#27ae60"   # Grün (Bild)
COLOR_ACCENT     = "#9b59b6"   # Lila (Write)
COLOR_DANGER     = "#e74c3c"   # Rot (Löschen)
COLOR_DARK       = "#2c3e50"   # Dunkler Text / Log-Hintergrund
COLOR_LIGHT_BG   = "#ecf0f1"   # Helle Flächen (Action-Bar)
COLOR_BORDER     = "#bdc3c7"   # Rahmen
COLOR_MUTED      = "#7f8c8d"   # Gedämpfter Text
COLOR_SURFACE    = "#34495e"   # Log-Rahmen

# ---------- App-weites QSS-Stylesheet ----------

APP_STYLESHEET = """
/* ---------- Globale Schrift ---------- */
QMainWindow, QDialog {
	font-family: "Segoe UI", "Arial", sans-serif;
	font-size: 9pt;
}

/* ---------- GroupBoxes ---------- */
QGroupBox {
	font-weight: bold;
	border: 1px solid #bdc3c7;
	border-radius: 4px;
	margin-top: 8px;
	padding-top: 8px;
}
QGroupBox::title {
	subcontrol-origin: margin;
	left: 10px;
	padding: 0 5px;
}

/* ---------- Eingabefelder ---------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
	padding: 4px 6px;
	border: 1px solid #bdc3c7;
	border-radius: 3px;
	background-color: white;
	min-height: 22px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
	border: 1px solid #3498db;
}
QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
	border: 1px solid #95a5a6;
}
QComboBox::drop-down {
	border: none;
	padding-right: 8px;
}

/* ---------- Buttons (Standard) ---------- */
QPushButton {
	padding: 5px 12px;
	border: 1px solid #bdc3c7;
	border-radius: 3px;
	background-color: #fdfdfd;
	min-height: 22px;
}
QPushButton:hover {
	background-color: #eaf2f8;
	border-color: #3498db;
}
QPushButton:pressed {
	background-color: #d6eaf8;
}
QPushButton:disabled {
	color: #95a5a6;
	background-color: #f2f3f4;
	border-color: #d5d8dc;
}

/* ---------- CheckBox / RadioButton ---------- */
QCheckBox, QRadioButton {
	spacing: 6px;
	min-height: 20px;
}
QCheckBox::indicator, QRadioButton::indicator {
	width: 16px;
	height: 16px;
}

/* ---------- TabWidget ---------- */
QTabWidget::pane {
	border: 1px solid #bdc3c7;
	border-radius: 3px;
	top: -1px;
}
QTabBar::tab {
	padding: 8px 20px;
	margin-right: 2px;
	border: 1px solid #bdc3c7;
	border-bottom: none;
	border-top-left-radius: 4px;
	border-top-right-radius: 4px;
	background-color: #eaecee;
	color: #566573;
	font-weight: normal;
	min-width: 100px;
}
QTabBar::tab:selected {
	background-color: white;
	color: #2c3e50;
	font-weight: bold;
	border-bottom: 2px solid #3498db;
}
QTabBar::tab:hover:!selected {
	background-color: #d5dbdb;
}

/* ---------- Tabellen ---------- */
QTableWidget {
	gridline-color: #d5dbdb;
	selection-background-color: #d4e6f1;
	selection-color: #2c3e50;
	border: 1px solid #bdc3c7;
	border-radius: 3px;
	alternate-background-color: #f8f9f9;
}
QHeaderView::section {
	background-color: #eaecee;
	padding: 5px;
	border: none;
	border-right: 1px solid #d5dbdb;
	border-bottom: 1px solid #bdc3c7;
	font-weight: bold;
	color: #2c3e50;
}

/* ---------- Fortschrittsbalken ---------- */
QProgressBar {
	border: 1px solid #bdc3c7;
	border-radius: 3px;
	text-align: center;
	background-color: #f2f3f4;
	min-height: 20px;
}
QProgressBar::chunk {
	background-color: #3498db;
	border-radius: 2px;
}

/* ---------- ScrollBar ---------- */
QScrollBar:vertical {
	background-color: #f2f3f4;
	width: 12px;
	border-radius: 6px;
}
QScrollBar::handle:vertical {
	background-color: #bdc3c7;
	border-radius: 5px;
	min-height: 30px;
	margin: 2px;
}
QScrollBar::handle:vertical:hover {
	background-color: #95a5a6;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
	height: 0px;
}

/* ---------- Statusbar ---------- */
QStatusBar {
	background-color: #eaecee;
	border-top: 1px solid #d5dbdb;
	color: #566573;
}

/* ---------- Tooltips ---------- */
QToolTip {
	background-color: #2c3e50;
	color: #ecf0f1;
	border: 1px solid #34495e;
	padding: 4px 8px;
	border-radius: 3px;
}
"""


def create_app_icon() -> QIcon:
	"""Erstellt ein einfaches App-Icon programmiert (kein externes Icon-File nötig)."""
	pixmap = QPixmap(64, 64)
	pixmap.fill(Qt.GlobalColor.transparent)
	painter = QPainter(pixmap)
	painter.setRenderHint(QPainter.RenderHint.Antialiasing)

	# Hintergrund-Quad mit abgerundeten Ecken
	painter.setPen(Qt.PenStyle.NoPen)
	painter.setBrush(QColor("#3498db"))
	painter.drawRoundedRect(4, 4, 56, 56, 12, 12)

	# Weißes "Play"-Dreieck
	painter.setBrush(QColor("white"))
	from PyQt6.QtGui import QPolygon
	from PyQt6.QtCore import QPoint
	points = [QPoint(24, 18), QPoint(24, 46), QPoint(48, 32)]
	painter.drawPolygon(QPolygon(points))

	painter.end()
	return QIcon(pixmap)


class DropTableWidget(QTableWidget):
	"""QTableWidget mit Drag & Drop Unterstützung für Dateien."""
	files_dropped = pyqtSignal(list)  # list[str]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setAcceptDrops(True)
		self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()

	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()

	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
			if paths:
				self.files_dropped.emit(paths)
			event.acceptProposedAction()


class MainWindow(QMainWindow):
	video_start_requested = pyqtSignal()
	image_generate_requested = pyqtSignal()
	write_start_requested = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.setWindowTitle("FFmpeg Testvideo-Generator")
		self.setMinimumSize(960, 720)
		self.resize(1100, 800)

		# App-weites Stylesheet anwenden
		self.setStyleSheet(APP_STYLESHEET)

		# App-Icon setzen
		app_icon = create_app_icon()
		self.setWindowIcon(app_icon)

		# Zentrale Speicherung für QSettings (Fenstergeometrie etc.)
		self._qsettings = QSettings("ForensicTools", "TestVideoGenerator")

		central = QWidget()
		self.setCentralWidget(central)
		root_layout = QVBoxLayout(central)
		root_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		root_layout.setSpacing(SPACING)

		tabs = QTabWidget()
		tabs.setDocumentMode(True)
		self.tabs = tabs  # Referenz speichern (Phase 1-Note)
		root_layout.addWidget(tabs)

		self._build_video_tab(tabs)
		self._build_image_tab(tabs)
		self._build_write_tab(tabs)

		self._build_menu_bar()
		self._setup_shortcuts()

		self.worker = None
		self.img_worker = None

		# Fenstergeometrie wiederherstellen
		self._restore_window_geometry()

	# ---------- Menüleiste (Phase 5) ----------

	def _build_menu_bar(self):
		"""Erstellt die Menüleiste mit Datei- und Hilfe-Menü."""
		menubar = self.menuBar()

		# Datei-Menü
		file_menu = menubar.addMenu("&Datei")

		action_exit = QAction("B&eenden", self)
		action_exit.setShortcut(QKeySequence.StandardKey.Quit)
		action_exit.setStatusTip("Anwendung beenden")
		action_exit.triggered.connect(self.close)
		file_menu.addAction(action_exit)

		# Bearbeiten-Menü
		edit_menu = menubar.addMenu("&Bearbeiten")

		action_video = QAction("Video-Tab öffnen", self)
		action_video.setShortcut(QKeySequence("Ctrl+1"))
		action_video.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
		edit_menu.addAction(action_video)

		action_image = QAction("Bild-Tab öffnen", self)
		action_image.setShortcut(QKeySequence("Ctrl+2"))
		action_image.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
		edit_menu.addAction(action_image)

		action_write = QAction("Write-Tab öffnen", self)
		action_write.setShortcut(QKeySequence("Ctrl+3"))
		action_write.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
		edit_menu.addAction(action_write)

		# Hilfe-Menü
		help_menu = menubar.addMenu("&Hilfe")

		action_about = QAction("&Über", self)
		action_about.setShortcut(QKeySequence.StandardKey.HelpContents)
		action_about.setStatusTip("Informationen über diese Anwendung")
		action_about.triggered.connect(self._show_about_dialog)
		help_menu.addAction(action_about)

	# ---------- Keyboard-Shortcuts (Phase 5) ----------

	def _setup_shortcuts(self):
		"""Richtet globale Keyboard-Shortcuts ein."""
		# Strg+Enter: Video erzeugen
		shortcut_video = QAction(self)
		shortcut_video.setShortcut(QKeySequence("Ctrl+Return"))
		shortcut_video.triggered.connect(self.video_start_requested.emit)
		self.addAction(shortcut_video)

		# Strg+Shift+Enter: Bild erzeugen
		shortcut_img = QAction(self)
		shortcut_img.setShortcut(QKeySequence("Ctrl+Shift+Return"))
		shortcut_img.triggered.connect(self.image_generate_requested.emit)
		self.addAction(shortcut_img)

	# ---------- Über-Dialog (Phase 5) ----------

	def _show_about_dialog(self):
		"""Zeigt den Über-Dialog an."""
		QMessageBox.about(
			self,
			"Über FFmpeg Testvideo-Generator",
			"<h2>FFmpeg Testvideo-Generator</h2>"
			"<p>Version 2.0</p>"
			"<p>Forensische Testdaten-Generierung für Video und Bild.</p>"
			"<p>Features:</p>"
			"<ul>"
			"<li>Video-Generierung mit Timecode-Overlays</li>"
			"<li>Bild-Generierung mit EXIF-Metadaten</li>"
			"<li>Metadaten-Schreiben in bestehende Dateien</li>"
			"<li>GPS-Unterstützung (ISO 6709)</li>"
			"</ul>"
			"<p>© 2026 ForensicTools</p>"
		)

	# ---------- Fenstergeometrie-Persistenz (Phase 5) ----------

	def _restore_window_geometry(self):
		"""Stellt die Fenstergeometrie aus QSettings wieder her."""
		geometry = self._qsettings.value("window_geometry")
		if geometry:
			self.restoreGeometry(geometry)

	def _save_window_geometry(self):
		"""Speichert die aktuelle Fenstergeometrie in QSettings."""
		self._qsettings.setValue("window_geometry", self.saveGeometry())

	def closeEvent(self, event):
		"""Wird beim Schließen des Fensters aufgerufen."""
		self._save_window_geometry()
		super().closeEvent(event)

	# ---------- Hilfsfunktionen ----------

	def _create_scroll_area(self, parent_widget) -> QScrollArea:
		"""Erstellt eine ScrollArea mit den Inhalt im parent_widget."""
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setFrameShape(QFrame.Shape.NoFrame)
		scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		
		container = QWidget()
		container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		scroll.setWidget(container)
		return scroll, container

	def _add_section_label(self, layout, text: str):
		"""Fügt eine Abschnitts-Überschrift hinzu."""
		label = QLabel(text)
		font = label.font()
		font.setBold(True)
		font.setPointSize(font.pointSize() + 1)
		label.setFont(font)
		label.setStyleSheet("color: #2c3e50; margin-top: 4px;")
		layout.addWidget(label)
		return label

	def _create_info_row(self, label_text: str, widget: QWidget) -> QHBoxLayout:
		"""Erstellt eine Zeile mit Label links und Widget rechts."""
		row = QHBoxLayout()
		row.setSpacing(SPACING)
		label = QLabel(label_text)
		label.setMinimumWidth(120)
		row.addWidget(label)
		row.addWidget(widget, 1)
		return row

	# ---------- Video-Tab ----------

	def _build_video_tab(self, tabs):
		tab1 = QWidget()
		tabs.addTab(tab1, "Video")
		
		# ScrollArea für den Video-Tab
		scroll, container = self._create_scroll_area(tab1)
		t1 = QVBoxLayout(container)
		t1.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		t1.setSpacing(SPACING)

		# ========== Preset-Bereich ==========
		preset_group = QGroupBox("Schnelleinstellungen")
		preset_group.setStyleSheet("""
			QGroupBox {
				font-weight: bold;
				border: 1px solid #bdc3c7;
				border-radius: 4px;
				margin-top: 8px;
				padding-top: 8px;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 10px;
				padding: 0 5px;
			}
		""")
		preset_layout = QHBoxLayout(preset_group)
		preset_layout.setSpacing(SPACING)
		
		preset_label = QLabel("Preset:")
		preset_label.setMinimumWidth(60)
		preset_layout.addWidget(preset_label)
		
		self.preset_box = QComboBox()
		self.preset_box.addItems([
			"720p Standard (5min, 25fps)",
			"1080p Broadcast (10min, 25fps)",
			"720p High Motion (60fps, 1min)",
			"Low-Light Test (2min, dark)",
			"Colorbars + Timecode (30s)"
		])
		self.preset_box.setMinimumWidth(280)
		preset_layout.addWidget(self.preset_box, 1)
		
		self.btn_apply_preset = QPushButton("Preset laden")
		self.btn_apply_preset.setMinimumWidth(100)
		preset_layout.addWidget(self.btn_apply_preset)
		
		t1.addWidget(preset_group)

		# ========== Video-Einstellungen ==========
		video_group = QGroupBox("Video-Einstellungen")
		video_layout = QGridLayout(video_group)
		video_layout.setSpacing(SPACING)
		video_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Auflösung
		res_label = QLabel("Auflösung:")
		video_layout.addWidget(res_label, 0, 0)
		
		res_row = QHBoxLayout()
		res_row.setSpacing(4)
		self.w_spin = QSpinBox()
		self.w_spin.setRange(160, 7680)
		self.w_spin.setValue(1280)
		self.w_spin.setSuffix(" px")
		self.w_spin.setMinimumWidth(100)
		res_row.addWidget(self.w_spin)
		res_row.addWidget(QLabel("x"))
		self.h_spin = QSpinBox()
		self.h_spin.setRange(120, 4320)
		self.h_spin.setValue(720)
		self.h_spin.setSuffix(" px")
		self.h_spin.setMinimumWidth(100)
		res_row.addWidget(self.h_spin)
		res_row.addStretch()
		video_layout.addLayout(res_row, 0, 1)

		# FPS
		fps_label = QLabel("FPS:")
		video_layout.addWidget(fps_label, 1, 0)
		self.fps_spin = QSpinBox()
		self.fps_spin.setRange(1, 240)
		self.fps_spin.setValue(25)
		self.fps_spin.setMinimumWidth(100)
		video_layout.addWidget(self.fps_spin, 1, 1)

		# Dauer
		dur_label = QLabel("Dauer:")
		video_layout.addWidget(dur_label, 1, 2)
		self.dur_spin = QSpinBox()
		self.dur_spin.setRange(1, 3600)
		self.dur_spin.setValue(300)
		self.dur_spin.setSuffix(" s")
		self.dur_spin.setMinimumWidth(100)
		video_layout.addWidget(self.dur_spin, 1, 3)

		# Hintergrund
		bg_label = QLabel("Hintergrund:")
		video_layout.addWidget(bg_label, 2, 0)
		bg_row = QHBoxLayout()
		bg_row.setSpacing(4)
		self.bg_edit = QLineEdit("black")
		self.bg_edit.setMinimumWidth(150)
		self.bg_edit.setPlaceholderText("Farbe oder Quelle (z.B. black, smptebars, testsrc)")
		bg_row.addWidget(self.bg_edit, 1)
		btn_vid_color = QPushButton("Farbe …")
		btn_vid_color.clicked.connect(self._choose_vid_bg_color)
		btn_vid_color.setFixedWidth(80)
		bg_row.addWidget(btn_vid_color)
		video_layout.addLayout(bg_row, 2, 1, 1, 3)

		t1.addWidget(video_group)

		# ========== Encoder-Einstellungen ==========
		enc_group = QGroupBox("Encoder & Qualität")
		enc_layout = QGridLayout(enc_group)
		enc_layout.setSpacing(SPACING)
		enc_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Encoder
		enc_label = QLabel("Encoder:")
		enc_layout.addWidget(enc_label, 0, 0)
		self.encoder_box = QComboBox()
		self.encoder_box.addItems(["libx264 (CPU)", "h264_nvenc (NVIDIA)"])
		self.encoder_box.setMinimumWidth(200)
		enc_layout.addWidget(self.encoder_box, 0, 1)

		# CRF
		crf_label = QLabel("QP/CRF:")
		enc_layout.addWidget(crf_label, 0, 2)
		self.crf_spin = QSpinBox()
		self.crf_spin.setRange(0, 51)
		self.crf_spin.setValue(23)
		self.crf_spin.setMinimumWidth(80)
		self.crf_spin.setToolTip("Quality Parameter (0=lossless, 51=worst)\nNVENC: QP (0=best, 51=worst)")
		enc_layout.addWidget(self.crf_spin, 0, 3)

		# Bitrate
		bitrate_label = QLabel("Bitrate:")
		enc_layout.addWidget(bitrate_label, 1, 0)
		self.bitrate_edit = QLineEdit()
		self.bitrate_edit.setPlaceholderText("leer = CRF-Modus (z.B. 2000k, 5M)")
		self.bitrate_edit.setMinimumWidth(180)
		enc_layout.addWidget(self.bitrate_edit, 1, 1, 1, 3)

		# GOP
		gop_label = QLabel("GOP:")
		enc_layout.addWidget(gop_label, 2, 0)
		self.gop_spin = QSpinBox()
		self.gop_spin.setRange(1, 1000)
		self.gop_spin.setValue(50)
		self.gop_spin.setMinimumWidth(80)
		self.gop_spin.setToolTip("Group of Pictures - Keyframe-Abstand in Frames")
		enc_layout.addWidget(self.gop_spin, 2, 1)

		t1.addWidget(enc_group)

		# ========== Overlay-Einstellungen ==========
		ov_group = QGroupBox("Overlay im Video")
		ov_layout = QVBoxLayout(ov_group)
		ov_layout.setSpacing(SPACING)
		ov_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Checkboxen in 2 Spalten
		ov_grid = QGridLayout()
		ov_grid.setSpacing(SPACING)
		
		self.chk_timecode_overlay = QCheckBox("Timecode im Bild")
		self.chk_timecode_overlay.setChecked(True)
		self.chk_timecode_overlay.setToolTip("Zeigt den laufenden Timecode an")
		ov_grid.addWidget(self.chk_timecode_overlay, 0, 0)

		self.chk_pts_overlay = QCheckBox("PTS + Frame im Bild")
		self.chk_pts_overlay.setChecked(True)
		self.chk_pts_overlay.setToolTip("Presentation Timestamp und Frame-Nummer")
		ov_grid.addWidget(self.chk_pts_overlay, 0, 1)

		self.chk_datetime_overlay = QCheckBox("Datum + Uhrzeit mittig")
		self.chk_datetime_overlay.setToolTip("Zeigt Erstellungsdatum und Zeit zentriert")
		ov_grid.addWidget(self.chk_datetime_overlay, 1, 0)

		self.chk_container_timecode = QCheckBox("Timecode-Metadaten setzen")
		self.chk_container_timecode.setChecked(True)
		self.chk_container_timecode.setToolTip("Schreibt Timecode in die Container-Metadaten")
		ov_grid.addWidget(self.chk_container_timecode, 1, 1)

		ov_layout.addLayout(ov_grid)
		t1.addWidget(ov_group)

		# ========== Timecode-Einstellungen ==========
		tc_box = QGroupBox("Timecode-Format & Position")
		tc_form = QGridLayout(tc_box)
		tc_form.setSpacing(SPACING)
		tc_form.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)
		
		# Startzeitcode
		tc_start_label = QLabel("Startzeitcode:")
		tc_form.addWidget(tc_start_label, 0, 0)
		tc_start_row = QHBoxLayout()
		tc_start_row.setSpacing(4)
		self.tc_start_edit = QLineEdit("00:00:00:00")
		self.tc_start_edit.setPlaceholderText("HH:MM:SS:FF oder HH:MM:SS;FF")
		self.tc_start_edit.setMinimumWidth(140)
		self.tc_start_edit.setToolTip("Format: HH:MM:SS:FF (Non-Drop) oder HH:MM:SS;FF (Drop-Frame)")
		tc_start_row.addWidget(self.tc_start_edit)
		
		self.chk_drop_frame = QCheckBox("Drop-Frame")
		self.chk_drop_frame.setToolTip("Drop-Frame Timecode (für 30/60fps)\nVerwendet ';' statt ':'")
		tc_start_row.addWidget(self.chk_drop_frame)
		tc_start_row.addStretch()
		tc_form.addLayout(tc_start_row, 0, 1)
		
		# Format
		tc_format_label = QLabel("Standard:")
		tc_form.addWidget(tc_format_label, 0, 2)
		self.tc_format_box = QComboBox()
		self.tc_format_box.addItems(["SMPTE", "EBU"])
		self.tc_format_box.setMinimumWidth(100)
		self.tc_format_box.setToolTip("SMPTE: Nordamerika, Japan\nEBU: Europa")
		tc_form.addWidget(self.tc_format_box, 0, 3)
		
		# Position
		tc_pos_label = QLabel("Position:")
		tc_form.addWidget(tc_pos_label, 1, 0)
		tc_pos_row = QHBoxLayout()
		tc_pos_row.setSpacing(4)
		tc_pos_row.addWidget(QLabel("X:"))
		self.tc_x_spin = QSpinBox()
		self.tc_x_spin.setRange(0, 7680)
		self.tc_x_spin.setValue(40)
		self.tc_x_spin.setMinimumWidth(80)
		tc_pos_row.addWidget(self.tc_x_spin)
		tc_pos_row.addWidget(QLabel("Y:"))
		self.tc_y_spin = QSpinBox()
		self.tc_y_spin.setRange(0, 4320)
		self.tc_y_spin.setValue(40)
		self.tc_y_spin.setMinimumWidth(80)
		tc_pos_row.addWidget(self.tc_y_spin)
		tc_pos_row.addStretch()
		tc_form.addLayout(tc_pos_row, 1, 1)
		
		# Schrift
		tc_font_label = QLabel("Darstellung:")
		tc_form.addWidget(tc_font_label, 1, 2)
		tc_font_row = QHBoxLayout()
		tc_font_row.setSpacing(4)
		tc_font_row.addWidget(QLabel("Größe:"))
		self.tc_font_size_spin = QSpinBox()
		self.tc_font_size_spin.setRange(8, 300)
		self.tc_font_size_spin.setValue(48)
		self.tc_font_size_spin.setMinimumWidth(60)
		tc_font_row.addWidget(self.tc_font_size_spin)
		tc_font_row.addWidget(QLabel("Farbe:"))
		self.tc_color_edit = QLineEdit("white")
		self.tc_color_edit.setMinimumWidth(80)
		self.tc_color_edit.setToolTip("CSS-Farbe oder Farbname (z.B. white, #FF0000, yellow)")
		tc_font_row.addWidget(self.tc_color_edit)
		tc_form.addLayout(tc_font_row, 1, 3)
		
		# PTS-Einstellungen
		pts_label = QLabel("PTS-Overlay:")
		tc_form.addWidget(pts_label, 2, 0)
		pts_row = QHBoxLayout()
		pts_row.setSpacing(4)
		pts_row.addWidget(QLabel("X:"))
		self.pts_x_spin = QSpinBox()
		self.pts_x_spin.setRange(0, 7680)
		self.pts_x_spin.setValue(40)
		self.pts_x_spin.setMinimumWidth(80)
		pts_row.addWidget(self.pts_x_spin)
		pts_row.addWidget(QLabel("Y:"))
		self.pts_y_spin = QSpinBox()
		self.pts_y_spin.setRange(0, 4320)
		self.pts_y_spin.setValue(120)
		self.pts_y_spin.setMinimumWidth(80)
		pts_row.addWidget(self.pts_y_spin)
		pts_row.addWidget(QLabel("Größe:"))
		self.pts_font_size_spin = QSpinBox()
		self.pts_font_size_spin.setRange(8, 300)
		self.pts_font_size_spin.setValue(36)
		self.pts_font_size_spin.setMinimumWidth(60)
		pts_row.addWidget(self.pts_font_size_spin)
		pts_row.addWidget(QLabel("Farbe:"))
		self.pts_color_edit = QLineEdit("yellow")
		self.pts_color_edit.setMinimumWidth(80)
		pts_row.addWidget(self.pts_color_edit)
		pts_row.addStretch()
		tc_form.addLayout(pts_row, 2, 1, 1, 3)
		
		t1.addWidget(tc_box)

		# ========== Schrift-Einstellungen ==========
		font_group = QGroupBox("Schrift für Overlays")
		font_layout = QGridLayout(font_group)
		font_layout.setSpacing(SPACING)
		font_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Font-Pfad
		font_label = QLabel("Schriftart:")
		font_layout.addWidget(font_label, 0, 0)
		font_row = QHBoxLayout()
		font_row.setSpacing(4)
		self.font_edit = QLineEdit("C:/Windows/Fonts/arial.ttf")
		self.font_edit.setPlaceholderText("Pfad zur .ttf oder .otf Datei")
		font_row.addWidget(self.font_edit, 1)
		btn_font = QPushButton("Durchsuchen …")
		btn_font.clicked.connect(lambda: self._choose_font(self.font_edit))
		btn_font.setFixedWidth(110)
		font_row.addWidget(btn_font)
		font_layout.addLayout(font_row, 0, 1)

		# Schriftgröße
		font_size_label = QLabel("Standardgröße:")
		font_layout.addWidget(font_size_label, 1, 0)
		self.font_size = QSpinBox()
		self.font_size.setRange(8, 300)
		self.font_size.setValue(48)
		self.font_size.setSuffix(" px")
		self.font_size.setMinimumWidth(100)
		font_layout.addWidget(self.font_size, 1, 1)

		t1.addWidget(font_group)

		# ========== Ausgabe ==========
		out_group = QGroupBox("Ausgabe")
		out_layout = QGridLayout(out_group)
		out_layout.setSpacing(SPACING)
		out_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Ausgabedatei
		out_label = QLabel("Datei:")
		out_layout.addWidget(out_label, 0, 0)
		out_row = QHBoxLayout()
		out_row.setSpacing(4)
		self.out_edit = QLineEdit("ffmpeg_testvideo.mp4")
		out_row.addWidget(self.out_edit, 1)
		btn_browse = QPushButton("Speichern unter …")
		btn_browse.clicked.connect(self._choose_output)
		btn_browse.setFixedWidth(140)
		out_row.addWidget(btn_browse)
		out_layout.addLayout(out_row, 0, 1)

		# Encoder-Metadaten
		enc_meta_label = QLabel("Encoder-Tag:")
		out_layout.addWidget(enc_meta_label, 1, 0)
		self.encoder_edit = QLineEdit("FFmpeg Testvideo Generator")
		self.encoder_edit.setToolTip("Wird als 'encoder'-Metadaten-Tag geschrieben")
		out_layout.addWidget(self.encoder_edit, 1, 1)

		t1.addWidget(out_group)

		# ========== Container-Metadaten ==========
		meta_box = QGroupBox("Container-Metadaten (MP4/MOV Tags)")
		mg = QGridLayout(meta_box)
		mg.setSpacing(SPACING)
		mg.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Zeile 1: Titel, Ersteller, Copyright
		mg.addWidget(QLabel("Titel:"), 0, 0)
		self.meta_title = QLineEdit("Forensik-Testvideo")
		mg.addWidget(self.meta_title, 0, 1)

		mg.addWidget(QLabel("Ersteller:"), 0, 2)
		self.meta_artist = QLineEdit()
		mg.addWidget(self.meta_artist, 0, 3)

		mg.addWidget(QLabel("Copyright:"), 1, 0)
		self.meta_copyright = QLineEdit()
		mg.addWidget(self.meta_copyright, 1, 1)

		mg.addWidget(QLabel("Sprache:"), 1, 2)
		self.meta_language = QLineEdit("ger")
		self.meta_language.setMaximumWidth(80)
		mg.addWidget(self.meta_language, 1, 3)

		# Zeile 2: Beschreibung, Genre
		mg.addWidget(QLabel("Beschreibung:"), 2, 0)
		self.meta_description = QLineEdit()
		mg.addWidget(self.meta_description, 2, 1, 1, 3)

		mg.addWidget(QLabel("Genre:"), 3, 0)
		self.meta_genre = QLineEdit("Forensic Test")
		mg.addWidget(self.meta_genre, 3, 1)

		# Zeile 3: Projekt, Testfall-ID
		mg.addWidget(QLabel("Projekt/Fall:"), 3, 2)
		self.meta_show = QLineEdit()
		mg.addWidget(self.meta_show, 3, 3)

		# Zeile 4: creation_time, date
		now_def = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		mg.addWidget(QLabel("creation_time:"), 4, 0)
		self.meta_creation_time = QLineEdit(now_def)
		self.meta_creation_time.setToolTip("ISO 8601 Format: YYYY-MM-DDTHH:MM:SS")
		mg.addWidget(self.meta_creation_time, 4, 1)

		mg.addWidget(QLabel("date:"), 4, 2)
		self.meta_date = QLineEdit()
		mg.addWidget(self.meta_date, 4, 3)

		# Zeile 5: Episode-ID, GPS
		mg.addWidget(QLabel("Testfall-ID:"), 5, 0)
		self.meta_episode_id = QLineEdit()
		mg.addWidget(self.meta_episode_id, 5, 1)

		mg.addWidget(QLabel("GPS (ISO 6709):"), 5, 2)
		self.meta_location = QLineEdit("+49.1234+008.5678/")
		self.meta_location.setToolTip("Format: +LAT+LON/ (z.B. +49.1234+008.5678/)")
		mg.addWidget(self.meta_location, 5, 3)

		# Zeile 6: Kommentar (volle Breite)
		mg.addWidget(QLabel("Kommentar:"), 6, 0)
		self.meta_comment = QLineEdit()
		mg.addWidget(self.meta_comment, 6, 1, 1, 3)

		t1.addWidget(meta_box)

		# Spacer für Abstand zur Action-Bar
		t1.addStretch()

		# ========== Action-Bar (fest am unteren Rand) ==========
		action_frame = QFrame()
		action_frame.setFrameShape(QFrame.Shape.StyledPanel)
		action_frame.setStyleSheet("QFrame { background-color: #ecf0f1; border-radius: 4px; }")
		action_layout = QHBoxLayout(action_frame)
		action_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		action_layout.setSpacing(SPACING)

		# Fortschrittsbalken
		self.progress = QProgressBar()
		self.progress.setRange(0, 100)
		self.progress.setValue(0)
		self.progress.setMinimumWidth(200)
		self.progress.setMaximumHeight(24)
		self.progress.setTextVisible(True)
		self.progress.setFormat("%p%")
		action_layout.addWidget(self.progress, 1)

		# Start-Button (Primary Action)
		self.btn_start = QPushButton("▶ Video erzeugen")
		self.btn_start.clicked.connect(self.video_start_requested)
		self.btn_start.setMinimumWidth(160)
		self.btn_start.setMinimumHeight(36)
		self.btn_start.setStyleSheet("""
			QPushButton {
				background-color: #3498db;
				color: white;
				border: none;
				border-radius: 4px;
				font-weight: bold;
				font-size: 11pt;
				padding: 8px 16px;
			}
			QPushButton:hover {
				background-color: #2980b9;
			}
			QPushButton:pressed {
				background-color: #21618c;
			}
			QPushButton:disabled {
				background-color: #95a5a6;
			}
		""")
		action_layout.addWidget(self.btn_start)

		t1.addWidget(action_frame)

		# ========== Log-Bereich ==========
		log_label = QLabel("FFmpeg-Log:")
		log_label.setStyleSheet("margin-top: 4px; color: #7f8c8d;")
		t1.addWidget(log_label)
		
		self.log_view = QTextEdit()
		self.log_view.setReadOnly(True)
		self.log_view.setFont(QFont("Consolas", 9))
		self.log_view.setMinimumHeight(120)
		self.log_view.setMaximumHeight(200)
		self.log_view.setStyleSheet("""
			QTextEdit {
				background-color: #2c3e50;
				color: #ecf0f1;
				border: 1px solid #34495e;
				border-radius: 4px;
				padding: 4px;
			}
		""")
		t1.addWidget(self.log_view)

		# ScrollArea zum Tab hinzufügen
		tab_layout = QVBoxLayout(tab1)
		tab_layout.setContentsMargins(0, 0, 0, 0)
		tab_layout.addWidget(scroll)

	# ---------- Bild-Tab ----------

	def _build_image_tab(self, tabs):
		tab3 = QWidget()
		tabs.addTab(tab3, "Bild")
		
		scroll, container = self._create_scroll_area(tab3)
		t3 = QVBoxLayout(container)
		t3.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		t3.setSpacing(SPACING)

		# ========== Bild-Einstellungen ==========
		img_group = QGroupBox("Bild-Einstellungen")
		img_layout = QGridLayout(img_group)
		img_layout.setSpacing(SPACING)
		img_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Format + Auflösung in einer Zeile
		fmt_label = QLabel("Format:")
		img_layout.addWidget(fmt_label, 0, 0)
		self.img_format = QComboBox()
		self.img_format.addItems(["png", "jpg", "bmp", "tif", "webp"])
		self.img_format.setMinimumWidth(100)
		img_layout.addWidget(self.img_format, 0, 1)

		res_label = QLabel("Auflösung:")
		img_layout.addWidget(res_label, 0, 2)
		res_row = QHBoxLayout()
		res_row.setSpacing(4)
		self.img_w = QSpinBox()
		self.img_w.setRange(160, 7680)
		self.img_w.setValue(1920)
		self.img_w.setSuffix(" px")
		self.img_w.setMinimumWidth(100)
		res_row.addWidget(self.img_w)
		res_row.addWidget(QLabel("x"))
		self.img_h = QSpinBox()
		self.img_h.setRange(120, 4320)
		self.img_h.setValue(1080)
		self.img_h.setSuffix(" px")
		self.img_h.setMinimumWidth(100)
		res_row.addWidget(self.img_h)
		img_layout.addLayout(res_row, 0, 3)

		# Auflösungs-Presets
		preset_label = QLabel("Presets:")
		img_layout.addWidget(preset_label, 1, 0)
		preset_row = QHBoxLayout()
		preset_row.setSpacing(4)
		res_presets = [
			("HD 720p", 1280, 720),
			("Full HD", 1920, 1080),
			("4K UHD", 3840, 2160),
			("Square", 1080, 1080),
		]
		for name, w, h in res_presets:
			btn = QPushButton(name)
			btn.setFixedWidth(90)
			btn.setToolTip(f"Setze Auflösung auf {w}x{h}")
			btn.clicked.connect(lambda checked, w=w, h=h: self._set_img_resolution(w, h))
			preset_row.addWidget(btn)
		preset_row.addStretch()
		img_layout.addLayout(preset_row, 1, 1, 1, 3)

		# Hintergrund
		bg_label = QLabel("Hintergrund:")
		img_layout.addWidget(bg_label, 2, 0)
		bg_row = QHBoxLayout()
		bg_row.setSpacing(4)
		self.img_bg = QLineEdit("black")
		self.img_bg.setMinimumWidth(150)
		self.img_bg.setToolTip("FFmpeg color name oder #RRGGBB")
		bg_row.addWidget(self.img_bg, 1)
		btn_img_color = QPushButton("Farbe …")
		btn_img_color.clicked.connect(self._choose_img_bg_color)
		btn_img_color.setFixedWidth(80)
		bg_row.addWidget(btn_img_color)
		img_layout.addLayout(bg_row, 2, 1, 1, 3)

		# Schrift
		font_label = QLabel("Schriftart:")
		img_layout.addWidget(font_label, 3, 0)
		font_row = QHBoxLayout()
		font_row.setSpacing(4)
		self.img_font = QLineEdit("C:/Windows/Fonts/arial.ttf")
		font_row.addWidget(self.img_font, 1)
		btn_imgfont = QPushButton("Durchsuchen …")
		btn_imgfont.clicked.connect(lambda: self._choose_font(self.img_font))
		btn_imgfont.setFixedWidth(110)
		font_row.addWidget(btn_imgfont)
		img_layout.addLayout(font_row, 3, 1)

		# Schriftgröße
		font_size_label = QLabel("Größe:")
		img_layout.addWidget(font_size_label, 3, 2)
		self.img_font_size = QSpinBox()
		self.img_font_size.setRange(8, 300)
		self.img_font_size.setValue(54)
		self.img_font_size.setSuffix(" px")
		self.img_font_size.setMinimumWidth(100)
		img_layout.addWidget(self.img_font_size, 3, 3)

		# Ausgabedatei
		out_label = QLabel("Ausgabedatei:")
		img_layout.addWidget(out_label, 4, 0)
		out_row = QHBoxLayout()
		out_row.setSpacing(4)
		self.img_out = QLineEdit("testbild.png")
		out_row.addWidget(self.img_out, 1)
		btn_img_browse = QPushButton("Speichern unter …")
		btn_img_browse.clicked.connect(self._choose_img_output)
		btn_img_browse.setFixedWidth(140)
		out_row.addWidget(btn_img_browse)
		img_layout.addLayout(out_row, 4, 1, 1, 3)

		t3.addWidget(img_group)

		self.img_format.currentTextChanged.connect(self._update_img_extension)

		# ========== Container-Metadaten ==========
		container_group = QGroupBox("Container-Metadaten (PNG/JPEG Chunk)")
		container_layout = QGridLayout(container_group)
		container_layout.setSpacing(SPACING)
		container_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Titel
		container_layout.addWidget(QLabel("Titel:"), 0, 0)
		self.img_meta_title = QLineEdit()
		self.img_meta_title.setToolTip("PNG tEXt 'Title' / JPEG comment")
		container_layout.addWidget(self.img_meta_title, 0, 1)

		# Ersteller
		container_layout.addWidget(QLabel("Ersteller:"), 0, 2)
		self.img_meta_artist = QLineEdit()
		self.img_meta_artist.setToolTip("PNG tEXt 'Author'")
		container_layout.addWidget(self.img_meta_artist, 0, 3)

		# Copyright
		container_layout.addWidget(QLabel("Copyright:"), 1, 0)
		self.img_meta_copyright = QLineEdit()
		container_layout.addWidget(self.img_meta_copyright, 1, 1)

		# Kommentar
		container_layout.addWidget(QLabel("Kommentar:"), 1, 2)
		self.img_meta_comment = QLineEdit()
		self.img_meta_comment.setToolTip("PNG tEXt 'Comment'")
		container_layout.addWidget(self.img_meta_comment, 1, 3)

		# creation_time
		now_def = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		container_layout.addWidget(QLabel("creation_time:"), 2, 0)
		ctime_row = QHBoxLayout()
		ctime_row.setSpacing(4)
		self.img_meta_ctime = QLineEdit(now_def)
		self.img_meta_ctime.setToolTip("ISO 8601: YYYY-MM-DDTHH:MM:SS")
		ctime_row.addWidget(self.img_meta_ctime, 1)
		
		# Zeitstempel-Quickbuttons
		btn_now = QPushButton("Jetzt")
		btn_now.setFixedWidth(60)
		btn_now.setToolTip("Aktuelle Zeit einfügen")
		btn_now.clicked.connect(lambda: self._set_img_timestamp_now())
		ctime_row.addWidget(btn_now)
		
		btn_yesterday = QPushButton("Gestern")
		btn_yesterday.setFixedWidth(70)
		btn_yesterday.clicked.connect(lambda: self._set_img_timestamp_offset(days=-1))
		ctime_row.addWidget(btn_yesterday)
		
		btn_lastweek = QPushButton("-7 Tage")
		btn_lastweek.setFixedWidth(70)
		btn_lastweek.clicked.connect(lambda: self._set_img_timestamp_offset(days=-7))
		ctime_row.addWidget(btn_lastweek)
		
		container_layout.addLayout(ctime_row, 2, 1, 1, 3)

		# GPS
		container_layout.addWidget(QLabel("GPS (ISO 6709):"), 3, 0)
		self.img_meta_location = QLineEdit("+49.1234+008.5678/")
		self.img_meta_location.setToolTip("Format: +LAT+LON/ (z.B. +49.1234+008.5678/)")
		container_layout.addWidget(self.img_meta_location, 3, 1)

		# GPS-Presets
		gps_label = QLabel("GPS-Presets:")
		container_layout.addWidget(gps_label, 3, 2)
		gps_row = QHBoxLayout()
		gps_row.setSpacing(4)
		gps_presets = [
			("Berlin", "+52.5200+013.4050/"),
			("München", "+48.1351+011.5820/"),
			("Hamburg", "+53.5511+009.9937/"),
			("Köln", "+50.9375+006.9603/"),
		]
		for name, coords in gps_presets:
			btn = QPushButton(name)
			btn.setFixedWidth(70)
			btn.setToolTip(coords)
			btn.clicked.connect(lambda checked, c=coords: self._set_img_gps(c))
			gps_row.addWidget(btn)
		gps_row.addStretch()
		container_layout.addLayout(gps_row, 3, 3)

		t3.addWidget(container_group)

		# ========== EXIF-Metadaten ==========
		exif_group = QGroupBox("EXIF-Metadaten (eingebettet in Bilddatei)")
		exif_group.setStyleSheet("""
			QGroupBox {
				border: 1px solid #3498db;
				border-radius: 4px;
				margin-top: 8px;
				padding-top: 8px;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 10px;
				padding: 0 5px;
				color: #2980b9;
				font-weight: bold;
			}
		""")
		exif_layout = QGridLayout(exif_group)
		exif_layout.setSpacing(SPACING)
		exif_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# EXIF Make
		exif_layout.addWidget(QLabel("Hersteller (Make):"), 0, 0)
		self.img_exif_make = QLineEdit()
		self.img_exif_make.setPlaceholderText("z.B. Canon, Sony, Nikon")
		self.img_exif_make.setToolTip("EXIF Tag: Make (0x010F)")
		exif_layout.addWidget(self.img_exif_make, 0, 1)

		# EXIF Model
		exif_layout.addWidget(QLabel("Modell (Model):"), 0, 2)
		self.img_exif_model = QLineEdit()
		self.img_exif_model.setPlaceholderText("z.B. EOS R5, A7 IV")
		self.img_exif_model.setToolTip("EXIF Tag: Model (0x0110)")
		exif_layout.addWidget(self.img_exif_model, 0, 3)

		# EXIF Software
		exif_layout.addWidget(QLabel("Software:"), 1, 0)
		self.img_exif_software = QLineEdit("FFmpeg Testvideo Generator")
		self.img_exif_software.setToolTip("EXIF Tag: Software (0x0131)")
		exif_layout.addWidget(self.img_exif_software, 1, 1, 1, 3)

		# DateTimeOriginal
		exif_layout.addWidget(QLabel("DateTimeOriginal:"), 2, 0)
		dto_row = QHBoxLayout()
		dto_row.setSpacing(4)
		self.img_exif_dt_original = QLineEdit()
		self.img_exif_dt_original.setPlaceholderText("YYYY-MM-DDTHH:MM:SS")
		self.img_exif_dt_original.setToolTip("EXIF Tag: DateTimeOriginal (0x9003)\nWICHTIGSTER Forensik-Zeitstempel!")
		dto_row.addWidget(self.img_exif_dt_original, 1)
		
		btn_dto_now = QPushButton("Jetzt")
		btn_dto_now.setFixedWidth(60)
		btn_dto_now.clicked.connect(lambda: self._set_img_exif_dt_original_now())
		dto_row.addWidget(btn_dto_now)
		
		exif_layout.addLayout(dto_row, 2, 1, 1, 3)

		# DateTimeDigitized
		exif_layout.addWidget(QLabel("DateTimeDigitized:"), 3, 0)
		dtd_row = QHBoxLayout()
		dtd_row.setSpacing(4)
		self.img_exif_dt_digitized = QLineEdit()
		self.img_exif_dt_digitized.setPlaceholderText("YYYY-MM-DDTHH:MM:SS")
		self.img_exif_dt_digitized.setToolTip("EXIF Tag: DateTimeDigitized (0x9004)")
		dtd_row.addWidget(self.img_exif_dt_digitized, 1)
		
		btn_dtd_now = QPushButton("Jetzt")
		btn_dtd_now.setFixedWidth(60)
		btn_dtd_now.clicked.connect(lambda: self._set_img_exif_dt_digitized_now())
		dtd_row.addWidget(btn_dtd_now)
		
		# Sync-Button: DateTimeDigitized = DateTimeOriginal
		btn_sync_dt = QPushButton("= Original")
		btn_sync_dt.setFixedWidth(80)
		btn_sync_dt.setToolTip("Kopiert DateTimeOriginal nach DateTimeDigitized")
		btn_sync_dt.clicked.connect(lambda: self._sync_img_exif_datetimes())
		dtd_row.addWidget(btn_sync_dt)
		
		exif_layout.addLayout(dtd_row, 3, 1, 1, 3)

		# Info-Label
		info_label = QLabel("Hinweis: EXIF-Tags werden nach FFmpeg-Generierung mit piexif eingefügt.")
		info_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 4px;")
		info_label.setWordWrap(True)
		exif_layout.addWidget(info_label, 4, 0, 1, 4)

		t3.addWidget(exif_group)

		# Spacer
		t3.addStretch()

		# ========== Action-Bar ==========
		action_frame = QFrame()
		action_frame.setFrameShape(QFrame.Shape.StyledPanel)
		action_frame.setStyleSheet("QFrame { background-color: #ecf0f1; border-radius: 4px; }")
		action_layout = QHBoxLayout(action_frame)
		action_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		action_layout.setSpacing(SPACING)

		# Fortschrittsbalken (wie im Video-Tab)
		self.img_progress = QProgressBar()
		self.img_progress.setRange(0, 100)
		self.img_progress.setValue(0)
		self.img_progress.setMinimumWidth(200)
		self.img_progress.setMaximumHeight(24)
		self.img_progress.setTextVisible(True)
		self.img_progress.setFormat("%p%")
		action_layout.addWidget(self.img_progress, 1)

		# Status-Label
		self.img_status = QLabel()
		self.img_status.setStyleSheet("color: #2c3e50; font-weight: bold;")
		self.img_status.setMinimumWidth(200)
		action_layout.addWidget(self.img_status)

		# Start-Button
		self.img_btn = QPushButton("▶ Bild erzeugen")
		self.img_btn.clicked.connect(self.image_generate_requested)
		self.img_btn.setMinimumWidth(160)
		self.img_btn.setMinimumHeight(36)
		self.img_btn.setStyleSheet("""
			QPushButton {
				background-color: #27ae60;
				color: white;
				border: none;
				border-radius: 4px;
				font-weight: bold;
				font-size: 11pt;
				padding: 8px 16px;
			}
			QPushButton:hover {
				background-color: #219a52;
			}
			QPushButton:pressed {
				background-color: #1e8449;
			}
			QPushButton:disabled {
				background-color: #95a5a6;
			}
		""")
		action_layout.addWidget(self.img_btn)

		t3.addWidget(action_frame)

		# ========== Log-Bereich ==========
		log_label = QLabel("FFmpeg-Log:")
		log_label.setStyleSheet("margin-top: 4px; color: #7f8c8d;")
		t3.addWidget(log_label)
		
		self.img_log = QTextEdit()
		self.img_log.setReadOnly(True)
		self.img_log.setFont(QFont("Consolas", 9))
		self.img_log.setMinimumHeight(120)
		self.img_log.setMaximumHeight(200)
		self.img_log.setStyleSheet("""
			QTextEdit {
				background-color: #2c3e50;
				color: #ecf0f1;
				border: 1px solid #34495e;
				border-radius: 4px;
				padding: 4px;
			}
		""")
		t3.addWidget(self.img_log)

		# ScrollArea zum Tab hinzufügen
		tab_layout = QVBoxLayout(tab3)
		tab_layout.setContentsMargins(0, 0, 0, 0)
		tab_layout.addWidget(scroll)

	# ---------- Bild-Tab Hilfsfunktionen ----------

	def _set_img_resolution(self, width: int, height: int):
		"""Setzt die Bildauflösung auf die angegebenen Werte."""
		self.img_w.setValue(width)
		self.img_h.setValue(height)

	def _set_img_timestamp_now(self):
		"""Setzt creation_time auf die aktuelle Zeit."""
		now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.img_meta_ctime.setText(now)

	def _set_img_timestamp_offset(self, days: int = 0, hours: int = 0, minutes: int = 0):
		"""Setzt creation_time mit Offset."""
		dt = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes)
		self.img_meta_ctime.setText(dt.strftime("%Y-%m-%dT%H:%M:%S"))

	def _set_img_gps(self, coords: str):
		"""Setzt die GPS-Koordinaten."""
		self.img_meta_location.setText(coords)

	def _set_img_exif_dt_original_now(self):
		"""Setzt EXIF DateTimeOriginal auf die aktuelle Zeit."""
		now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.img_exif_dt_original.setText(now)

	def _set_img_exif_dt_digitized_now(self):
		"""Setzt EXIF DateTimeDigitized auf die aktuelle Zeit."""
		now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.img_exif_dt_digitized.setText(now)

	def _sync_img_exif_datetimes(self):
		"""Kopiert DateTimeOriginal nach DateTimeDigitized."""
		self.img_exif_dt_digitized.setText(self.img_exif_dt_original.text())

	# ---------- Write-Tab ----------

	def _build_write_tab(self, tabs):
		tab4 = QWidget()
		tabs.addTab(tab4, "Write")
		
		scroll, container = self._create_scroll_area(tab4)
		t4 = QVBoxLayout(container)
		t4.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		t4.setSpacing(SPACING)

		# ========== Basis-Einstellungen ==========
		base_group = QGroupBox("Zeit-Grundlagen")
		base_group.setStyleSheet("""
			QGroupBox {
				font-weight: bold;
				border: 1px solid #bdc3c7;
				border-radius: 4px;
				margin-top: 8px;
				padding-top: 8px;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 10px;
				padding: 0 5px;
			}
		""")
		base_layout = QGridLayout(base_group)
		base_layout.setSpacing(SPACING)
		base_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Basis-Zeit
		base_label = QLabel("Basis-Zeit:")
		base_layout.addWidget(base_label, 0, 0)
		now_def = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.write_base_time = QLineEdit(now_def)
		self.write_base_time.setToolTip("Start-Zeit für die erste Datei (ISO 8601)")
		self.write_base_time.setMinimumWidth(200)
		base_layout.addWidget(self.write_base_time, 0, 1)

		# Zeitstempel-Quickbuttons (wie im Bild-Tab)
		time_btn_row = QHBoxLayout()
		time_btn_row.setSpacing(4)
		
		btn_w_now = QPushButton("Jetzt")
		btn_w_now.setFixedWidth(60)
		btn_w_now.setToolTip("Aktuelle Zeit einfügen")
		btn_w_now.clicked.connect(lambda: self._set_write_base_time_now())
		time_btn_row.addWidget(btn_w_now)
		
		btn_w_yesterday = QPushButton("Gestern")
		btn_w_yesterday.setFixedWidth(70)
		btn_w_yesterday.clicked.connect(lambda: self._set_write_base_time_offset(days=-1))
		time_btn_row.addWidget(btn_w_yesterday)
		
		btn_w_lastweek = QPushButton("-7 Tage")
		btn_w_lastweek.setFixedWidth(70)
		btn_w_lastweek.clicked.connect(lambda: self._set_write_base_time_offset(days=-7))
		time_btn_row.addWidget(btn_w_lastweek)
		
		btn_w_lastmonth = QPushButton("-30 Tage")
		btn_w_lastmonth.setFixedWidth(80)
		btn_w_lastmonth.clicked.connect(lambda: self._set_write_base_time_offset(days=-30))
		time_btn_row.addWidget(btn_w_lastmonth)
		
		time_btn_row.addStretch()
		base_layout.addLayout(time_btn_row, 0, 2)

		# Offset
		offset_label = QLabel("Offset pro Datei:")
		base_layout.addWidget(offset_label, 1, 0)
		offset_row = QHBoxLayout()
		offset_row.setSpacing(4)
		self.write_offset = QSpinBox()
		self.write_offset.setRange(0, 3600)
		self.write_offset.setValue(30)
		self.write_offset.setSuffix(" s")
		self.write_offset.setMinimumWidth(100)
		self.write_offset.setToolTip("Zeit-Offset zwischen aufeinanderfolgenden Dateien")
		offset_row.addWidget(self.write_offset)
		
		# Schnell-Offsets
		offset_presets = [
			("10s", 10), ("30s", 30), ("1min", 60), ("5min", 300), ("1h", 3600)
		]
		for name, val in offset_presets:
			btn = QPushButton(name)
			btn.setFixedWidth(50)
			btn.setToolTip(f"Offset auf {val} Sekunden setzen")
			btn.clicked.connect(lambda checked, v=val: self.write_offset.setValue(v))
			offset_row.addWidget(btn)
		
		offset_row.addStretch()
		base_layout.addLayout(offset_row, 1, 1, 1, 2)

		t4.addWidget(base_group)

		# ========== Datei-Tabelle ==========
		table_group = QGroupBox("Dateien")
		table_layout = QVBoxLayout(table_group)
		table_layout.setSpacing(SPACING)
		table_layout.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Toolbar für Tabellen-Aktionen
		toolbar = QHBoxLayout()
		toolbar.setSpacing(4)
		
		btn_add = QPushButton(" Dateien hinzufügen")
		btn_add.clicked.connect(self._write_add_files)
		btn_add.setMinimumWidth(150)
		btn_add.setToolTip("Dateien über Dialog auswählen")
		toolbar.addWidget(btn_add)
		
		# Drag & Drop Info
		drop_info = QLabel("oder Dateien hierher ziehen")
		drop_info.setStyleSheet("color: #7f8c8d; font-style: italic;")
		toolbar.addWidget(drop_info)
		
		toolbar.addStretch()
		
		btn_clear_sel = QPushButton("Auswahl entfernen")
		btn_clear_sel.clicked.connect(self._write_remove_selected)
		btn_clear_sel.setMinimumWidth(140)
		btn_clear_sel.setToolTip("Entfernt nur die markierten Zeilen")
		toolbar.addWidget(btn_clear_sel)
		
		btn_clear = QPushButton("Alle entfernen")
		btn_clear.clicked.connect(self._write_clear)
		btn_clear.setMinimumWidth(120)
		btn_clear.setStyleSheet("""
			QPushButton {
				background-color: #e74c3c;
				color: white;
				border: none;
				border-radius: 4px;
				padding: 6px 12px;
			}
			QPushButton:hover {
				background-color: #c0392b;
			}
		""")
		btn_clear.setToolTip("Entfernt alle Dateien aus der Tabelle")
		toolbar.addWidget(btn_clear)
		
		table_layout.addLayout(toolbar)

		# Tabelle mit Drag & Drop
		self.write_table = DropTableWidget(0, 3)
		self.write_table.setHorizontalHeaderLabels(["Dateipfad", "Erstellungszeit", "Status"])
		self.write_table.horizontalHeader().setStretchLastSection(False)
		self.write_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
		self.write_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
		self.write_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
		self.write_table.setColumnWidth(2, 80)
		self.write_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
		self.write_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
		self.write_table.setAlternatingRowColors(True)
		self.write_table.setMinimumHeight(200)
		self.write_table.itemChanged.connect(self._write_on_item_changed)
		self.write_table.files_dropped.connect(self._write_on_files_dropped)
		table_layout.addWidget(self.write_table)

		# Aktualisieren-Button
		btn_row = QHBoxLayout()
		btn_row.setSpacing(4)
		
		btn_update_times = QPushButton("Zeiten neu berechnen")
		btn_update_times.clicked.connect(self._write_recalculate_times)
		btn_update_times.setToolTip("Berechnet Erstellungszeiten für alle Dateien neu")
		btn_row.addWidget(btn_update_times)
		
		btn_row.addStretch()
		table_layout.addLayout(btn_row)

		t4.addWidget(table_group)

		# ========== Metadaten ==========
		wmeta = QGroupBox("Metadaten (in alle Dateien schreiben)")
		wmeta.setStyleSheet("""
			QGroupBox {
				font-weight: bold;
				border: 1px solid #9b59b6;
				border-radius: 4px;
				margin-top: 8px;
				padding-top: 8px;
			}
			QGroupBox::title {
				subcontrol-origin: margin;
				left: 10px;
				padding: 0 5px;
				color: #8e44ad;
			}
		""")
		wg = QGridLayout(wmeta)
		wg.setSpacing(SPACING)
		wg.setContentsMargins(GROUP_PADDING, GROUP_PADDING, GROUP_PADDING, GROUP_PADDING)

		# Titel + Ersteller
		wg.addWidget(QLabel("Titel:"), 0, 0)
		self.write_meta_title = QLineEdit("Forensik-Testvideo")
		self.write_meta_title.setToolTip("Metadaten-Titel (z.B. TIT2 in MP4)")
		wg.addWidget(self.write_meta_title, 0, 1)

		wg.addWidget(QLabel("Ersteller:"), 0, 2)
		self.write_meta_artist = QLineEdit()
		self.write_meta_artist.setToolTip("Ersteller/Künstler (z.B. artist in MP4)")
		wg.addWidget(self.write_meta_artist, 0, 3)

		# Copyright + Sprache
		wg.addWidget(QLabel("Copyright:"), 1, 0)
		self.write_meta_copyright = QLineEdit()
		wg.addWidget(self.write_meta_copyright, 1, 1)

		wg.addWidget(QLabel("Sprache:"), 1, 2)
		self.write_meta_language = QLineEdit("ger")
		self.write_meta_language.setMaximumWidth(80)
		self.write_meta_language.setToolTip("3-stelliger Sprachcode (ISO 639-2)")
		wg.addWidget(self.write_meta_language, 1, 3)

		# Beschreibung (volle Breite)
		wg.addWidget(QLabel("Beschreibung:"), 2, 0)
		self.write_meta_description = QLineEdit()
		self.write_meta_description.setToolTip("Freitext-Beschreibung")
		wg.addWidget(self.write_meta_description, 2, 1, 1, 3)

		# Genre + Projekt/Fall
		wg.addWidget(QLabel("Genre:"), 3, 0)
		self.write_meta_genre = QLineEdit("Forensic Test")
		wg.addWidget(self.write_meta_genre, 3, 1)

		wg.addWidget(QLabel("Projekt/Fall:"), 3, 2)
		self.write_meta_show = QLineEdit()
		self.write_meta_show.setToolTip("Projektname oder Fall-ID")
		wg.addWidget(self.write_meta_show, 3, 3)

		# creation_time + date
		now_def2 = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		wg.addWidget(QLabel("creation_time:"), 4, 0)
		self.write_meta_creation_time = QLineEdit(now_def2)
		self.write_meta_creation_time.setToolTip("Globale creation_time-Metadaten (ISO 8601)")
		wg.addWidget(self.write_meta_creation_time, 4, 1)

		wg.addWidget(QLabel("date:"), 4, 2)
		self.write_meta_date = QLineEdit()
		self.write_meta_date.setToolTip("Datum im Format YYYY-MM-DD")
		wg.addWidget(self.write_meta_date, 4, 3)

		# Testfall-ID + GPS
		wg.addWidget(QLabel("Testfall-ID:"), 5, 0)
		self.write_meta_episode_id = QLineEdit()
		self.write_meta_episode_id.setToolTip("Eindeutige Kennung für den Testfall")
		wg.addWidget(self.write_meta_episode_id, 5, 1)

		wg.addWidget(QLabel("GPS (ISO 6709):"), 5, 2)
		self.write_meta_location = QLineEdit("+49.1234+008.5678/")
		self.write_meta_location.setToolTip("GPS-Koordinaten im ISO 6709 Format")
		wg.addWidget(self.write_meta_location, 5, 3)

		# GPS-Presets
		gps_row = QHBoxLayout()
		gps_row.setSpacing(4)
		gps_presets = [
			("Berlin", "+52.5200+013.4050/"),
			("München", "+48.1351+011.5820/"),
			("Hamburg", "+53.5511+009.9937/"),
			("Köln", "+50.9375+006.9603/"),
		]
		for name, coords in gps_presets:
			btn = QPushButton(name)
			btn.setFixedWidth(70)
			btn.setToolTip(coords)
			btn.clicked.connect(lambda checked, c=coords: self._set_write_gps(c))
			gps_row.addWidget(btn)
		gps_row.addStretch()
		wg.addLayout(gps_row, 5, 4)

		# Kommentar (volle Breite)
		wg.addWidget(QLabel("Kommentar:"), 6, 0)
		self.write_meta_comment = QLineEdit()
		self.write_meta_comment.setToolTip("Zusätzlicher Kommentar")
		wg.addWidget(self.write_meta_comment, 6, 1, 1, 3)

		# Info-Label
		info_label = QLabel("Hinweis: Metadaten werden in die Container aller ausgewählten Dateien geschrieben.")
		info_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 8px;")
		info_label.setWordWrap(True)
		wg.addWidget(info_label, 7, 0, 1, 4)

		t4.addWidget(wmeta)

		# Spacer
		t4.addStretch()

		# ========== Action-Bar ==========
		action_frame = QFrame()
		action_frame.setFrameShape(QFrame.Shape.StyledPanel)
		action_frame.setStyleSheet("QFrame { background-color: #ecf0f1; border-radius: 4px; }")
		action_layout = QHBoxLayout(action_frame)
		action_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
		action_layout.setSpacing(SPACING)

		# Fortschrittsbalken (wie in anderen Tabs)
		self.write_progress = QProgressBar()
		self.write_progress.setRange(0, 100)
		self.write_progress.setValue(0)
		self.write_progress.setMinimumWidth(200)
		self.write_progress.setMaximumHeight(24)
		self.write_progress.setTextVisible(True)
		self.write_progress.setFormat("%p%")
		action_layout.addWidget(self.write_progress, 1)

		# Status-Label
		self.write_status = QLabel()
		self.write_status.setStyleSheet("color: #2c3e50; font-weight: bold;")
		self.write_status.setMinimumWidth(200)
		action_layout.addWidget(self.write_status)

		# Start-Button
		self.write_btn = QPushButton("▶ Metadaten schreiben")
		self.write_btn.clicked.connect(self.write_start_requested)
		self.write_btn.setMinimumWidth(180)
		self.write_btn.setMinimumHeight(36)
		self.write_btn.setStyleSheet("""
			QPushButton {
				background-color: #9b59b6;
				color: white;
				border: none;
				border-radius: 4px;
				font-weight: bold;
				font-size: 11pt;
				padding: 8px 16px;
			}
			QPushButton:hover {
				background-color: #8e44ad;
			}
			QPushButton:pressed {
				background-color: #7d3c98;
			}
			QPushButton:disabled {
				background-color: #95a5a6;
			}
		""")
		action_layout.addWidget(self.write_btn)

		t4.addWidget(action_frame)

		# ========== Log-Bereich ==========
		log_label = QLabel("FFmpeg-Log:")
		log_label.setStyleSheet("margin-top: 4px; color: #7f8c8d;")
		t4.addWidget(log_label)
		
		self.write_log = QTextEdit()
		self.write_log.setReadOnly(True)
		self.write_log.setFont(QFont("Consolas", 9))
		self.write_log.setMinimumHeight(120)
		self.write_log.setMaximumHeight(200)
		self.write_log.setStyleSheet("""
			QTextEdit {
				background-color: #2c3e50;
				color: #ecf0f1;
				border: 1px solid #34495e;
				border-radius: 4px;
				padding: 4px;
			}
		""")
		t4.addWidget(self.write_log)

		# ScrollArea zum Tab hinzufügen
		tab_layout = QVBoxLayout(tab4)
		tab_layout.setContentsMargins(0, 0, 0, 0)
		tab_layout.addWidget(scroll)

	# ---------- Tabellen-Funktionen (Write-Tab) ----------

	def _write_add_files(self):
		paths, _ = QFileDialog.getOpenFileNames(
			self, "Dateien auswählen",
			"",
			"Video/Bilder (*.mp4 *.mkv *.avi *.mov *.wmv *.ts *.mxf *.jpg *.jpeg *.png *.tif *.tiff *.bmp *.webp);;Alle Dateien (*.*)")
		if not paths:
			return
		base = self.write_base_time.text().strip()
		offset = self.write_offset.value()
		self.write_table.itemChanged.disconnect(self._write_on_item_changed)
		try:
			dt = datetime.datetime.fromisoformat(base)
		except ValueError:
			dt = datetime.datetime.now()
		for i, p in enumerate(paths):
			row = self.write_table.rowCount()
			self.write_table.insertRow(row)
			item_path = QTableWidgetItem(p)
			item_path.setFlags(item_path.flags() & ~Qt.ItemFlag.ItemIsEditable)
			self.write_table.setItem(row, 0, item_path)
			ct = dt + datetime.timedelta(seconds=offset * row)
			item_time = QTableWidgetItem(ct.strftime("%Y-%m-%dT%H:%M:%S"))
			self.write_table.setItem(row, 1, item_time)
		self.write_table.itemChanged.connect(self._write_on_item_changed)

	def _write_clear(self):
		self.write_table.setRowCount(0)

	def _write_on_item_changed(self, item):
		pass  # placeholder; user edits times directly

	def _write_remove_selected(self):
		"""Entfernt die ausgewählten Zeilen aus der Tabelle."""
		selected_rows = set()
		for index in self.write_table.selectedIndexes():
			selected_rows.add(index.row())
		
		# Von unten nach oben löschen, um Indizes nicht zu verschieben
		for row in sorted(selected_rows, reverse=True):
			self.write_table.removeRow(row)

	def _write_recalculate_times(self):
		"""Berechnet alle Erstellungszeiten basierend auf Basis-Zeit und Offset neu."""
		base = self.write_base_time.text().strip()
		offset = self.write_offset.value()
		
		try:
			dt = datetime.datetime.fromisoformat(base)
		except ValueError:
			self.write_status.setText("Fehler: Ungültiges Basis-Zeitformat")
			return
		
		self.write_table.itemChanged.disconnect(self._write_on_item_changed)
		for row in range(self.write_table.rowCount()):
			item_time = self.write_table.item(row, 1)
			if item_time:
				ct = dt + datetime.timedelta(seconds=offset * row)
				item_time.setText(ct.strftime("%Y-%m-%dT%H:%M:%S"))
		self.write_table.itemChanged.connect(self._write_on_item_changed)
		
		self.write_status.setText(f"Zeiten aktualisiert ({self.write_table.rowCount()} Dateien)")

	def _set_write_base_time_now(self):
		"""Setzt die Basis-Zeit auf die aktuelle Zeit."""
		now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		self.write_base_time.setText(now)

	def _set_write_base_time_offset(self, days: int = 0, hours: int = 0, minutes: int = 0):
		"""Setzt die Basis-Zeit mit Offset."""
		dt = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes)
		self.write_base_time.setText(dt.strftime("%Y-%m-%dT%H:%M:%S"))

	def _set_write_gps(self, coords: str):
		"""Setzt die GPS-Koordinaten."""
		self.write_meta_location.setText(coords)

	def _write_on_files_dropped(self, paths: list):
		"""Wird aufgerufen, wenn Dateien per Drag & Drop auf die Tabelle gezogen werden."""
		base = self.write_base_time.text().strip()
		offset = self.write_offset.value()
		
		try:
			dt = datetime.datetime.fromisoformat(base)
		except ValueError:
			dt = datetime.datetime.now()
		
		self.write_table.itemChanged.disconnect(self._write_on_item_changed)
		for p in paths:
			row = self.write_table.rowCount()
			self.write_table.insertRow(row)
			item_path = QTableWidgetItem(p)
			item_path.setFlags(item_path.flags() & ~Qt.ItemFlag.ItemIsEditable)
			self.write_table.setItem(row, 0, item_path)
			ct = dt + datetime.timedelta(seconds=offset * row)
			item_time = QTableWidgetItem(ct.strftime("%Y-%m-%dT%H:%M:%S"))
			self.write_table.setItem(row, 1, item_time)
		self.write_table.itemChanged.connect(self._write_on_item_changed)
		
		self.write_status.setText(f"{len(paths)} Dateien hinzugefügt")

	def get_write_files(self) -> list[tuple[str, str]]:
		"""Gibt [(source_path, creation_time), …] aus der Tabelle."""
		result = []
		for row in range(self.write_table.rowCount()):
			src = self.write_table.item(row, 0)
			ct = self.write_table.item(row, 1)
			if src and ct and src.text().strip():
				result.append((src.text().strip(), ct.text().strip()))
		return result

	def get_write_meta(self):
		from model import WriteParams
		return WriteParams(
			files=[],
			meta_title=self.write_meta_title.text().strip(),
			meta_artist=self.write_meta_artist.text().strip(),
			meta_copyright=self.write_meta_copyright.text().strip(),
			meta_description=self.write_meta_description.text().strip(),
			meta_language=self.write_meta_language.text().strip(),
			meta_show=self.write_meta_show.text().strip(),
			meta_episode_id=self.write_meta_episode_id.text().strip(),
			meta_genre=self.write_meta_genre.text().strip(),
			meta_comment=self.write_meta_comment.text().strip(),
			meta_creation_time=self.write_meta_creation_time.text().strip(),
			meta_date=self.write_meta_date.text().strip(),
			meta_location=self.write_meta_location.text().strip(),
		)

	def set_write_controls_enabled(self, enabled: bool):
		self.write_btn.setEnabled(enabled)

	def append_write_log(self, text: str):
		self.write_log.append(text)

	def clear_write_log(self):
		self.write_log.clear()

	# ---------- Video-Parameter auslesen ----------

	def get_video_params(self) -> VideoParams:
		return VideoParams(
			width=self.w_spin.value(),
			height=self.h_spin.value(),
			fps=self.fps_spin.value(),
			duration=self.dur_spin.value(),
			source=self.bg_edit.text().strip(),
			fontfile=self.font_edit.text().strip(),
			font_size=self.font_size.value(),
			encoder=self.encoder_box.currentText(),
			crf=self.crf_spin.value(),
			bitrate=self.bitrate_edit.text().strip(),
			gop=self.gop_spin.value(),
			timecode_overlay=self.chk_timecode_overlay.isChecked(),
			pts_overlay=self.chk_pts_overlay.isChecked(),
			datetime_overlay=self.chk_datetime_overlay.isChecked(),
			container_timecode=self.chk_container_timecode.isChecked(),
			timecode_start=self.tc_start_edit.text().strip() or "00:00:00:00",
			timecode_drop_frame=self.chk_drop_frame.isChecked(),
			timecode_format=self.tc_format_box.currentText(),
			timecode_x=self.tc_x_spin.value(),
			timecode_y=self.tc_y_spin.value(),
			timecode_font_size=self.tc_font_size_spin.value(),
			timecode_font_color=self.tc_color_edit.text().strip() or "white",
			pts_x=self.pts_x_spin.value(),
			pts_y=self.pts_y_spin.value(),
			pts_font_size=self.pts_font_size_spin.value(),
			pts_font_color=self.pts_color_edit.text().strip() or "yellow",
			encoder_meta=self.encoder_edit.text().strip(),
			output=self.out_edit.text().strip(),
			meta_title=self.meta_title.text().strip(),
			meta_artist=self.meta_artist.text().strip(),
			meta_copyright=self.meta_copyright.text().strip(),
			meta_description=self.meta_description.text().strip(),
			meta_language=self.meta_language.text().strip(),
			meta_show=self.meta_show.text().strip(),
			meta_episode_id=self.meta_episode_id.text().strip(),
			meta_genre=self.meta_genre.text().strip(),
			meta_comment=self.meta_comment.text().strip(),
			meta_creation_time=self.meta_creation_time.text().strip(),
			meta_date=self.meta_date.text().strip(),
			meta_location=self.meta_location.text().strip(),
		)

	def get_image_params(self) -> "ImageParams":
		from model import ImageParams
		return ImageParams(
			width=self.img_w.value(),
			height=self.img_h.value(),
			source=self.img_bg.text().strip(),
			fontfile=self.img_font.text().strip(),
			font_size=self.img_font_size.value(),
			output=self.img_out.text().strip(),
			meta_title=self.img_meta_title.text().strip(),
			meta_artist=self.img_meta_artist.text().strip(),
			meta_copyright=self.img_meta_copyright.text().strip(),
			meta_comment=self.img_meta_comment.text().strip(),
			meta_creation_time=self.img_meta_ctime.text().strip(),
			meta_location=self.img_meta_location.text().strip(),
			exif_make=self.img_exif_make.text().strip(),
			exif_model=self.img_exif_model.text().strip(),
			exif_software=self.img_exif_software.text().strip(),
			exif_datetime_original=self.img_exif_dt_original.text().strip(),
			exif_datetime_digitized=self.img_exif_dt_digitized.text().strip(),
		)

	def apply_preset(self):
		preset = self.preset_box.currentText()
		if preset.startswith("720p Standard"):
			self.w_spin.setValue(1280)
			self.h_spin.setValue(720)
			self.fps_spin.setValue(25)
			self.dur_spin.setValue(300)
			self.bg_edit.setText("black")
			self.chk_timecode_overlay.setChecked(True)
			self.chk_pts_overlay.setChecked(True)
			self.chk_container_timecode.setChecked(True)
			self.crf_spin.setValue(23)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(50)
			self.tc_start_edit.setText("00:00:00:00")
			self.chk_drop_frame.setChecked(False)
			self.tc_format_box.setCurrentText("SMPTE")
		elif preset.startswith("1080p Broadcast"):
			self.w_spin.setValue(1920)
			self.h_spin.setValue(1080)
			self.fps_spin.setValue(25)
			self.dur_spin.setValue(600)
			self.bg_edit.setText("black")
			self.chk_timecode_overlay.setChecked(True)
			self.chk_pts_overlay.setChecked(False)
			self.chk_container_timecode.setChecked(True)
			self.crf_spin.setValue(18)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(50)
			self.tc_start_edit.setText("10:00:00:00")
			self.chk_drop_frame.setChecked(False)
			self.tc_format_box.setCurrentText("EBU")
		elif preset.startswith("720p High Motion"):
			self.w_spin.setValue(1280)
			self.h_spin.setValue(720)
			self.fps_spin.setValue(60)
			self.dur_spin.setValue(60)
			self.bg_edit.setText("black")
			self.chk_timecode_overlay.setChecked(False)
			self.chk_pts_overlay.setChecked(True)
			self.chk_container_timecode.setChecked(False)
			self.crf_spin.setValue(23)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(30)
			self.tc_start_edit.setText("00:00:00;00")
			self.chk_drop_frame.setChecked(True)
			self.tc_format_box.setCurrentText("SMPTE")
		elif preset.startswith("Low-Light"):
			self.w_spin.setValue(1280)
			self.h_spin.setValue(720)
			self.fps_spin.setValue(25)
			self.dur_spin.setValue(120)
			self.bg_edit.setText("#050505")
			self.chk_timecode_overlay.setChecked(True)
			self.chk_pts_overlay.setChecked(False)
			self.chk_container_timecode.setChecked(True)
			self.crf_spin.setValue(23)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(50)
			self.tc_start_edit.setText("00:00:00:00")
			self.chk_drop_frame.setChecked(False)
			self.tc_format_box.setCurrentText("SMPTE")
		elif preset.startswith("Colorbars"):
			self.w_spin.setValue(1280)
			self.h_spin.setValue(720)
			self.fps_spin.setValue(25)
			self.dur_spin.setValue(30)
			self.bg_edit.setText("smptebars")
			self.chk_timecode_overlay.setChecked(True)
			self.chk_pts_overlay.setChecked(False)
			self.chk_container_timecode.setChecked(True)
			self.crf_spin.setValue(23)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(50)
			self.tc_start_edit.setText("12:00:00:00")
			self.chk_drop_frame.setChecked(False)
			self.tc_format_box.setCurrentText("SMPTE")
		self.statusBar().showMessage(f"Preset geladen: {preset}", 3000)

	# ---------- View-Update-Methoden (vom Presenter gerufen) ----------

	def set_video_controls_enabled(self, enabled: bool):
		self.btn_start.setEnabled(enabled)

	def set_video_progress(self, value: int):
		self.progress.setValue(value)

	def clear_video_log(self):
		self.log_view.clear()

	def append_video_log(self, line: str):
		self.log_view.append(line)

	def show_video_finished(self, path: str):
		self.statusBar().showMessage(f"Fertig: {path}", 5000)

	def show_video_error(self, msg: str):
		self.statusBar().showMessage(f"Fehler: {msg}", 8000)
		self.log_view.append(f"\nFEHLER: {msg}")

	def set_img_controls_enabled(self, enabled: bool):
		self.img_btn.setEnabled(enabled)

	def clear_img_log(self):
		self.img_log.clear()

	def append_img_log(self, line: str):
		self.img_log.append(line)

	def set_img_status(self, text: str):
		self.img_status.setText(text)

	def show_img_finished(self, path: str):
		self.img_status.setText(f"Fertig: {path}")
		self.statusBar().showMessage(f"Bild erstellt: {path}", 5000)

	def show_img_error(self, msg: str):
		self.img_status.setText(f"Fehler: {msg}")
		self.statusBar().showMessage(f"Bild-Fehler: {msg}", 8000)
		self.img_log.append(f"\nFEHLER: {msg}")

	def load_settings_to_ui(self, settings: dict):
		if "encoder" in settings:
			idx = self.encoder_box.findText(settings["encoder"])
			if idx >= 0:
				self.encoder_box.setCurrentIndex(idx)
		if "font_path" in settings:
			self.font_edit.setText(settings["font_path"])
		if "font_size" in settings:
			try:
				self.font_size.setValue(int(settings["font_size"]))
			except ValueError:
				pass
		if "output_folder" in settings and settings["output_folder"].strip():
			from pathlib import Path
			base = Path(self.out_edit.text()).name
			self.out_edit.setText(str(Path(settings["output_folder"].strip()) / base))

		def _bool(key: str, default: bool = True) -> bool:
			v = settings.get(key)
			if v is None:
				return default
			return v.lower() in ("1", "true", "yes")

		def _int(key: str, default: int) -> int:
			v = settings.get(key)
			if v is None:
				return default
			try:
				return int(v)
			except ValueError:
				return default

		def _str(key: str, default: str) -> str:
			v = settings.get(key)
			return v if v is not None else default

		self.chk_timecode_overlay.setChecked(_bool("timecode_overlay"))
		self.chk_pts_overlay.setChecked(_bool("pts_overlay"))
		self.chk_datetime_overlay.setChecked(_bool("datetime_overlay", False))
		self.chk_container_timecode.setChecked(_bool("container_timecode"))

		# Timecode-Einstellungen laden
		self.tc_start_edit.setText(_str("timecode_start", "00:00:00:00"))
		self.chk_drop_frame.setChecked(_bool("timecode_drop_frame", False))
		idx = self.tc_format_box.findText(_str("timecode_format", "SMPTE"))
		if idx >= 0:
			self.tc_format_box.setCurrentIndex(idx)
		self.tc_x_spin.setValue(_int("timecode_x", 40))
		self.tc_y_spin.setValue(_int("timecode_y", 40))
		self.tc_font_size_spin.setValue(_int("timecode_font_size", 48))
		self.tc_color_edit.setText(_str("timecode_font_color", "white"))
		self.pts_x_spin.setValue(_int("pts_x", 40))
		self.pts_y_spin.setValue(_int("pts_y", 120))
		self.pts_font_size_spin.setValue(_int("pts_font_size", 36))
		self.pts_color_edit.setText(_str("pts_font_color", "yellow"))

	def collect_settings_from_ui(self) -> dict:
		from pathlib import Path
		return {
			"encoder": self.encoder_box.currentText(),
			"font_path": self.font_edit.text(),
			"font_size": str(self.font_size.value()),
			"output_folder": str(Path(self.out_edit.text()).parent),
			"timecode_overlay": "1" if self.chk_timecode_overlay.isChecked() else "0",
			"pts_overlay": "1" if self.chk_pts_overlay.isChecked() else "0",
			"datetime_overlay": "1" if self.chk_datetime_overlay.isChecked() else "0",
			"container_timecode": "1" if self.chk_container_timecode.isChecked() else "0",
			"timecode_start": self.tc_start_edit.text(),
			"timecode_drop_frame": "1" if self.chk_drop_frame.isChecked() else "0",
			"timecode_format": self.tc_format_box.currentText(),
			"timecode_x": str(self.tc_x_spin.value()),
			"timecode_y": str(self.tc_y_spin.value()),
			"timecode_font_size": str(self.tc_font_size_spin.value()),
			"timecode_font_color": self.tc_color_edit.text(),
			"pts_x": str(self.pts_x_spin.value()),
			"pts_y": str(self.pts_y_spin.value()),
			"pts_font_size": str(self.pts_font_size_spin.value()),
			"pts_font_color": self.pts_color_edit.text(),
		}

	# ---------- Dialoge ----------

	def _choose_output(self):
		path, _ = QFileDialog.getSaveFileName(
			self, "Ausgabedatei wählen",
			self.out_edit.text(),
			"MP4 (*.mp4);;Alle Dateien (*.*)"
		)
		if path:
			self.out_edit.setText(path)

	def _choose_img_output(self):
		path, _ = QFileDialog.getSaveFileName(
			self, "Ausgabedatei wählen",
			self.img_out.text(),
			"Bilder (*.png *.jpg *.bmp *.tif *.webp);;Alle Dateien (*.*)"
		)
		if path:
			self.img_out.setText(path)

	def _choose_font(self, target_edit):
		path, _ = QFileDialog.getOpenFileName(
			self, "Font-Datei wählen",
			"",
			"Schriftarten (*.ttf *.otf);;Alle Dateien (*.*)"
		)
		if path:
			target_edit.setText(path)

	def _choose_vid_bg_color(self):
		color = QColorDialog.getColor(
			QColor(self.bg_edit.text()), self, "Hintergrundfarbe"
		)
		if color.isValid():
			self.bg_edit.setText(color.name())

	def _choose_img_bg_color(self):
		color = QColorDialog.getColor(
			QColor(self.img_bg.text()), self, "Hintergrundfarbe"
		)
		if color.isValid():
			self.img_bg.setText(color.name())

	def _update_img_extension(self, fmt: str):
		path = self.img_out.text()
		base, _ = path.rsplit(".", 1) if "." in path else (path, "")
		self.img_out.setText(f"{base}.{fmt}")