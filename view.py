import datetime

from PyQt6.QtWidgets import (
	QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton,
	QFileDialog, QColorDialog, QProgressBar,
	QTextEdit, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from model import VideoParams, ImageParams


class MainWindow(QMainWindow):
	video_start_requested = pyqtSignal()
	image_generate_requested = pyqtSignal()

	def __init__(self):
		super().__init__()
		self.setWindowTitle("FFmpeg Testvideo-Generator")
		self.setMinimumSize(900, 650)

		central = QWidget()
		self.setCentralWidget(central)
		root_layout = QVBoxLayout(central)

		tabs = QTabWidget()
		root_layout.addWidget(tabs)

		self._build_video_tab(tabs)
		self._build_metadata_tab(tabs)
		self._build_image_tab(tabs)

		self.worker = None
		self.img_worker = None

	# ---------- Video-Tab ----------

	def _build_video_tab(self, tabs):
		tab1 = QWidget()
		tabs.addTab(tab1, "Video")
		t1 = QVBoxLayout(tab1)

		preset_layout = QHBoxLayout()
		t1.addLayout(preset_layout)
		preset_layout.addWidget(QLabel("Preset:"))
		self.preset_box = QComboBox()
		self.preset_box.addItems([
			"720p Standard (5min, 25fps)",
			"1080p Broadcast (10min, 25fps)",
			"720p High Motion (60fps, 1min)",
			"Low-Light Test (2min, dark)",
			"Colorbars + Timecode (30s)"
		])
		preset_layout.addWidget(self.preset_box)
		self.btn_apply_preset = QPushButton("Preset laden")
		preset_layout.addWidget(self.btn_apply_preset)

		res = QHBoxLayout()
		t1.addLayout(res)
		res.addWidget(QLabel("Breite:"))
		self.w_spin = QSpinBox()
		self.w_spin.setRange(160, 7680)
		self.w_spin.setValue(1280)
		res.addWidget(self.w_spin)
		res.addWidget(QLabel("Höhe:"))
		self.h_spin = QSpinBox()
		self.h_spin.setRange(120, 4320)
		self.h_spin.setValue(720)
		res.addWidget(self.h_spin)

		fd = QHBoxLayout()
		t1.addLayout(fd)
		fd.addWidget(QLabel("FPS:"))
		self.fps_spin = QSpinBox()
		self.fps_spin.setRange(1, 240)
		self.fps_spin.setValue(25)
		fd.addWidget(self.fps_spin)
		fd.addWidget(QLabel("Dauer (Sekunden):"))
		self.dur_spin = QSpinBox()
		self.dur_spin.setRange(1, 3600)
		self.dur_spin.setValue(300)
		fd.addWidget(self.dur_spin)

		enc_row = QHBoxLayout()
		t1.addLayout(enc_row)
		enc_row.addWidget(QLabel("Encoder:"))
		self.encoder_box = QComboBox()
		self.encoder_box.addItems(["libx264 (CPU)", "h264_nvenc (NVIDIA)"])
		enc_row.addWidget(self.encoder_box)
		enc_row.addWidget(QLabel("QP/CRF (0–51):"))
		self.crf_spin = QSpinBox()
		self.crf_spin.setRange(0, 51)
		self.crf_spin.setValue(23)
		enc_row.addWidget(self.crf_spin)
		enc_row.addWidget(QLabel("Bitrate (leer = CRF):"))
		self.bitrate_edit = QLineEdit()
		self.bitrate_edit.setPlaceholderText("z.B. 2000k, 5M")
		enc_row.addWidget(self.bitrate_edit)
		enc_row.addWidget(QLabel("GOP (Frames):"))
		self.gop_spin = QSpinBox()
		self.gop_spin.setRange(1, 1000)
		self.gop_spin.setValue(50)
		enc_row.addWidget(self.gop_spin)

		col = QHBoxLayout()
		t1.addLayout(col)
		col.addWidget(QLabel("Hintergrund (FFmpeg color= / Quelle):"))
		self.bg_edit = QLineEdit("black")
		col.addWidget(self.bg_edit)
		btn_vid_color = QPushButton("Farbe …")
		btn_vid_color.clicked.connect(self._choose_vid_bg_color)
		col.addWidget(btn_vid_color)

		ov = QHBoxLayout()
		t1.addLayout(ov)
		self.chk_timecode_overlay = QCheckBox("Timecode im Bild")
		self.chk_timecode_overlay.setChecked(True)
		ov.addWidget(self.chk_timecode_overlay)
		self.chk_pts_overlay = QCheckBox("PTS + Frame im Bild")
		self.chk_pts_overlay.setChecked(True)
		ov.addWidget(self.chk_pts_overlay)
		self.chk_datetime_overlay = QCheckBox("Datum + Uhrzeit mittig")
		ov.addWidget(self.chk_datetime_overlay)
		self.chk_container_timecode = QCheckBox("Timecode-Metadaten setzen")
		self.chk_container_timecode.setChecked(True)
		ov.addWidget(self.chk_container_timecode)

		font_layout = QHBoxLayout()
		t1.addLayout(font_layout)
		font_layout.addWidget(QLabel("Font:"))
		self.font_edit = QLineEdit("C\\:/Windows/Fonts/arial.ttf")
		font_layout.addWidget(self.font_edit)
		btn_font = QPushButton("Font …")
		btn_font.clicked.connect(lambda: self._choose_font(self.font_edit))
		font_layout.addWidget(btn_font)
		font_layout.addWidget(QLabel("Größe:"))
		self.font_size = QSpinBox()
		self.font_size.setRange(8, 300)
		self.font_size.setValue(48)
		font_layout.addWidget(self.font_size)

		out = QHBoxLayout()
		t1.addLayout(out)
		out.addWidget(QLabel("Ausgabedatei:"))
		self.out_edit = QLineEdit("ffmpeg_testvideo.mp4")
		out.addWidget(self.out_edit)
		btn_browse = QPushButton("…")
		btn_browse.clicked.connect(self._choose_output)
		out.addWidget(btn_browse)

		meta = QHBoxLayout()
		t1.addLayout(meta)
		meta.addWidget(QLabel("Encoder-Metadaten:"))
		self.encoder_edit = QLineEdit("FFmpeg Testvideo Generator")
		meta.addWidget(self.encoder_edit)

		self.progress = QProgressBar()
		self.progress.setRange(0, 100)
		t1.addWidget(self.progress)

		self.btn_start = QPushButton("Video erzeugen")
		self.btn_start.clicked.connect(self.video_start_requested)
		t1.addWidget(self.btn_start)

		t1.addWidget(QLabel("FFmpeg-Log:"))
		self.log_view = QTextEdit()
		self.log_view.setReadOnly(True)
		t1.addWidget(self.log_view)

	# ---------- Metadaten-Tab ----------

	def _build_metadata_tab(self, tabs):
		tab2 = QWidget()
		tabs.addTab(tab2, "Metadaten - Video")
		t2 = QVBoxLayout(tab2)

		def meta_row(label, attr, default=""):
			row = QHBoxLayout()
			t2.addLayout(row)
			row.addWidget(QLabel(label))
			edit = QLineEdit(default)
			setattr(self, attr, edit)
			row.addWidget(edit)

		meta_row("Titel:", "meta_title", "Forensik-Testvideo")
		meta_row("Ersteller:", "meta_artist")
		meta_row("Copyright:", "meta_copyright")
		meta_row("Beschreibung:", "meta_description")
		meta_row("Sprache:", "meta_language", "ger")
		meta_row("Projekt / Fall:", "meta_show")
		meta_row("Testfall-ID:", "meta_episode_id")
		meta_row("Genre:", "meta_genre", "Forensic Test")
		meta_row("Kommentar:", "meta_comment")

		t2.addWidget(QLabel("── Datum / Zeit ──"))
		now_default = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
		meta_row("creation_time:", "meta_creation_time", now_default)
		meta_row("date:", "meta_date")

	# ---------- Bild-Tab ----------

	def _build_image_tab(self, tabs):
		tab3 = QWidget()
		tabs.addTab(tab3, "Bild")
		t3 = QVBoxLayout(tab3)

		fmt_row = QHBoxLayout()
		t3.addLayout(fmt_row)
		fmt_row.addWidget(QLabel("Format:"))
		self.img_format = QComboBox()
		self.img_format.addItems(["png", "jpg", "bmp", "tif", "webp"])
		fmt_row.addWidget(self.img_format)

		ir = QHBoxLayout()
		t3.addLayout(ir)
		ir.addWidget(QLabel("Breite:"))
		self.img_w = QSpinBox()
		self.img_w.setRange(160, 7680)
		self.img_w.setValue(1920)
		ir.addWidget(self.img_w)
		ir.addWidget(QLabel("Höhe:"))
		self.img_h = QSpinBox()
		self.img_h.setRange(120, 4320)
		self.img_h.setValue(1080)
		ir.addWidget(self.img_h)

		ibg = QHBoxLayout()
		t3.addLayout(ibg)
		ibg.addWidget(QLabel("Hintergrund:"))
		self.img_bg = QLineEdit("black")
		ibg.addWidget(self.img_bg)
		btn_img_color = QPushButton("Farbe …")
		btn_img_color.clicked.connect(self._choose_img_bg_color)
		ibg.addWidget(btn_img_color)

		ifont = QHBoxLayout()
		t3.addLayout(ifont)
		ifont.addWidget(QLabel("Font:"))
		self.img_font = QLineEdit("C\\:/Windows/Fonts/arial.ttf")
		ifont.addWidget(self.img_font)
		btn_imgfont = QPushButton("Font …")
		btn_imgfont.clicked.connect(lambda: self._choose_font(self.img_font))
		ifont.addWidget(btn_imgfont)
		ifont.addWidget(QLabel("Größe:"))
		self.img_font_size = QSpinBox()
		self.img_font_size.setRange(8, 300)
		self.img_font_size.setValue(54)
		ifont.addWidget(self.img_font_size)

		io = QHBoxLayout()
		t3.addLayout(io)
		io.addWidget(QLabel("Ausgabedatei:"))
		self.img_out = QLineEdit("testbild.png")
		io.addWidget(self.img_out)
		btn_img_browse = QPushButton("…")
		btn_img_browse.clicked.connect(self._choose_img_output)
		io.addWidget(btn_img_browse)

		self.img_format.currentTextChanged.connect(self._update_img_extension)

		self.img_btn = QPushButton("Bild erzeugen")
		self.img_btn.clicked.connect(self.image_generate_requested)
		t3.addWidget(self.img_btn)

		self.img_status = QLabel()
		t3.addWidget(self.img_status)

		t3.addWidget(QLabel("FFmpeg-Log:"))
		self.img_log = QTextEdit()
		self.img_log.setReadOnly(True)
		t3.addWidget(self.img_log)

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

		self.chk_timecode_overlay.setChecked(_bool("timecode_overlay"))
		self.chk_pts_overlay.setChecked(_bool("pts_overlay"))
		self.chk_datetime_overlay.setChecked(_bool("datetime_overlay", False))
		self.chk_container_timecode.setChecked(_bool("container_timecode"))

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
