import sys
import shlex
import subprocess
import datetime

from PyQt6.QtWidgets import (
	QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton,
	QFileDialog, QColorDialog, QProgressBar,
	QTextEdit, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


class FFmpegWorker(QThread):
	progress = pyqtSignal(int)          # 0–100 (grob)
	finished_ok = pyqtSignal(str)
	finished_error = pyqtSignal(str)
	log_line = pyqtSignal(str)

	def __init__(self, cmd_list, output_path):
		super().__init__()
		self.cmd_list = cmd_list
		self.output_path = output_path

	def run(self):
		try:
			self.log_line.emit("Starte FFmpeg:\n" + " ".join(self.cmd_list) + "\n")
			proc = subprocess.Popen(
				self.cmd_list,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				bufsize=1
			)

			line_count = 0
			for line in proc.stdout:
				line_count += 1
				self.log_line.emit(line.rstrip())
				pct = min(99, line_count // 5)
				self.progress.emit(pct)

			ret = proc.wait()
			if ret == 0:
				self.progress.emit(100)
				self.finished_ok.emit(self.output_path)
			else:
				self.finished_error.emit(f"FFmpeg Rückgabecode: {ret}")
		except Exception as e:
			self.finished_error.emit(str(e))


class ImageWorker(QThread):
	finished_ok = pyqtSignal(str)
	finished_error = pyqtSignal(str)
	log_line = pyqtSignal(str)

	def __init__(self, cmd_list, output_path):
		super().__init__()
		self.cmd_list = cmd_list
		self.output_path = output_path

	def run(self):
		try:
			self.log_line.emit("Starte FFmpeg:\n" + " ".join(self.cmd_list) + "\n")
			proc = subprocess.Popen(
				self.cmd_list,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				bufsize=1
			)
			for line in proc.stdout:
				self.log_line.emit(line.rstrip())
			ret = proc.wait()
			if ret == 0:
				self.finished_ok.emit(self.output_path)
			else:
				self.finished_error.emit(f"FFmpeg Rückgabecode: {ret}")
		except Exception as e:
			self.finished_error.emit(str(e))


class FFmpegTestVideoWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("FFmpeg Testvideo-Generator")
		self.setMinimumSize(900, 650)

		central = QWidget()
		self.setCentralWidget(central)
		root_layout = QVBoxLayout(central)

		tabs = QTabWidget()
		root_layout.addWidget(tabs)

		# ---------- Tab 1: Einstellungen ----------
		tab1 = QWidget()
		tabs.addTab(tab1, "Einstellungen")
		t1 = QVBoxLayout(tab1)

		# Presets
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

		btn_apply_preset = QPushButton("Preset laden")
		btn_apply_preset.clicked.connect(self.apply_preset)
		preset_layout.addWidget(btn_apply_preset)

		# Auflösung
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

		# FPS & Dauer
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
		self.dur_spin.setValue(300)  # 5 Minuten
		fd.addWidget(self.dur_spin)

		# Encoder-Auswahl
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

		# Hintergrundfarbe / Quelle
		col = QHBoxLayout()
		t1.addLayout(col)

		col.addWidget(QLabel("Hintergrund (FFmpeg color= / Quelle):"))
		self.bg_edit = QLineEdit("black")
		col.addWidget(self.bg_edit)

		# Overlays / Timecode
		ov = QHBoxLayout()
		t1.addLayout(ov)

		self.chk_timecode_overlay = QCheckBox("Timecode im Bild")
		self.chk_timecode_overlay.setChecked(True)
		ov.addWidget(self.chk_timecode_overlay)

		self.chk_pts_overlay = QCheckBox("PTS + Frame im Bild")
		self.chk_pts_overlay.setChecked(True)
		ov.addWidget(self.chk_pts_overlay)

		self.chk_container_timecode = QCheckBox("Timecode-Metadaten setzen")
		self.chk_container_timecode.setChecked(True)
		ov.addWidget(self.chk_container_timecode)

		# Schriftart / Textoptionen
		font_layout = QHBoxLayout()
		t1.addLayout(font_layout)

		font_layout.addWidget(QLabel("Font-Datei (drawtext):"))
		self.font_edit = QLineEdit("C\\:/Windows/Fonts/arial.ttf")
		font_layout.addWidget(self.font_edit)

		# Ausgabedatei
		out = QHBoxLayout()
		t1.addLayout(out)

		out.addWidget(QLabel("Ausgabedatei:"))
		self.out_edit = QLineEdit("ffmpeg_testvideo.mp4")
		out.addWidget(self.out_edit)

		btn_browse = QPushButton("…")
		btn_browse.clicked.connect(self.choose_output)
		out.addWidget(btn_browse)

		# Encoder-Metadaten (bleibt hier als Kurzfeld)
		meta = QHBoxLayout()
		t1.addLayout(meta)

		meta.addWidget(QLabel("Encoder-Metadaten:"))
		self.encoder_edit = QLineEdit("FFmpeg Testvideo Generator")
		meta.addWidget(self.encoder_edit)

		# Progress + Start
		self.progress = QProgressBar()
		self.progress.setRange(0, 100)
		t1.addWidget(self.progress)

		self.btn_start = QPushButton("Video erzeugen")
		self.btn_start.clicked.connect(self.start_ffmpeg)
		t1.addWidget(self.btn_start)

		# Log-Ausgabe
		t1.addWidget(QLabel("FFmpeg-Log:"))
		self.log_view = QTextEdit()
		self.log_view.setReadOnly(True)
		t1.addWidget(self.log_view)

		self.worker = None

		# ---------- Tab 2: Forensik-Metadaten ----------
		tab2 = QWidget()
		tabs.addTab(tab2, "Metadaten")
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

		# ---------- Tab 3: Bild / Photo ----------
		tab3 = QWidget()
		tabs.addTab(tab3, "Bild")
		t3 = QVBoxLayout(tab3)

		# Format
		fmt_row = QHBoxLayout()
		t3.addLayout(fmt_row)
		fmt_row.addWidget(QLabel("Format:"))
		self.img_format = QComboBox()
		self.img_format.addItems(["png", "jpg", "bmp", "tif", "webp"])
		fmt_row.addWidget(self.img_format)

		# Auflösung
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

		# Hintergrund
		ibg = QHBoxLayout()
		t3.addLayout(ibg)
		ibg.addWidget(QLabel("Hintergrund:"))
		self.img_bg = QLineEdit("black")
		ibg.addWidget(self.img_bg)
		btn_img_color = QPushButton("Farbe …")
		btn_img_color.clicked.connect(self.choose_img_bg_color)
		ibg.addWidget(btn_img_color)

		# Font
		ifont = QHBoxLayout()
		t3.addLayout(ifont)
		ifont.addWidget(QLabel("Font-Datei:"))
		self.img_font = QLineEdit("C\\:/Windows/Fonts/arial.ttf")
		ifont.addWidget(self.img_font)

		# Ausgabe
		io = QHBoxLayout()
		t3.addLayout(io)
		io.addWidget(QLabel("Ausgabedatei:"))
		self.img_out = QLineEdit("testbild.png")
		io.addWidget(self.img_out)
		btn_img_browse = QPushButton("…")
		btn_img_browse.clicked.connect(self.choose_img_output)
		io.addWidget(btn_img_browse)

		self.img_format.currentTextChanged.connect(self._update_img_extension)

		# Status + Button
		self.img_btn = QPushButton("Bild erzeugen")
		self.img_btn.clicked.connect(self.generate_image)
		t3.addWidget(self.img_btn)

		self.img_status = QLabel()
		t3.addWidget(self.img_status)

		t3.addWidget(QLabel("FFmpeg-Log:"))
		self.img_log = QTextEdit()
		self.img_log.setReadOnly(True)
		t3.addWidget(self.img_log)

		self.img_worker = None

		# Direkt ein sinnvolles Preset laden
		self.apply_preset()

	# ---------------- Presets ----------------

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
			# hier nutzen wir FFmpeg testquelle smptebars
			self.bg_edit.setText("smptebars")
			self.chk_timecode_overlay.setChecked(True)
			self.chk_pts_overlay.setChecked(False)
			self.chk_container_timecode.setChecked(True)
			self.crf_spin.setValue(23)
			self.bitrate_edit.clear()
			self.gop_spin.setValue(50)

		self.statusBar().showMessage(f"Preset geladen: {preset}", 3000)

	# ---------------- GUI-Aktionen ----------------

	def choose_output(self):
		path, _ = QFileDialog.getSaveFileName(
			self, "Ausgabedatei wählen",
			self.out_edit.text(),
			"MP4 (*.mp4);;Alle Dateien (*.*)"
		)
		if path:
			self.out_edit.setText(path)

	# ---------------- FFmpeg-Kommando ----------------

	def build_ffmpeg_command(self):
		width = self.w_spin.value()
		height = self.h_spin.value()
		fps = self.fps_spin.value()
		duration = self.dur_spin.value()
		source = self.bg_edit.text().strip()
		fontfile = self.font_edit.text().strip()
		output = self.out_edit.text().strip()
		encoder_meta = self.encoder_edit.text().strip()

		# Quelle: color oder Testquelle
		# Wenn "smptebars" oder "testsrc" → andere lavfi-Quelle
		if source.lower() in ("smptebars", "testsrc", "testsrc2"):
			input_filter = f"{source}=s={width}x{height}:r={fps}:d={duration}"
		else:
			input_filter = f"color=c={source}:s={width}x{height}:r={fps}:d={duration}"

		vf_parts = []

		if self.chk_timecode_overlay.isChecked():
			tc = (
				f"drawtext=fontfile='{fontfile}':"
				f"timecode='00\\:00\\:00\\:00':"
				f"r={fps}:"
				f"x=40:y=40:fontsize=48:fontcolor=white"
			)
			vf_parts.append(tc)

		if self.chk_pts_overlay.isChecked():
			pts = (
				f"drawtext=fontfile='{fontfile}':"
				f"text='%{{pts\\:hms}}.%{{eif:n}}':"
				f"x=40:y=120:fontsize=36:fontcolor=yellow"
			)
			vf_parts.append(pts)

		vf_filter = ",".join(vf_parts) if vf_parts else "null"

		codec = self.encoder_box.currentText()
		qp_val = str(self.crf_spin.value())

		if "nvenc" in codec:
			cmd = [
				"ffmpeg", "-y",
				"-f", "lavfi", "-i", input_filter,
				"-vf", vf_filter,
				"-c:v", "h264_nvenc",
				"-qp", qp_val,
				"-pix_fmt", "yuv420p",
				"-g", str(self.gop_spin.value()),
			]
		else:
			cmd = [
				"ffmpeg", "-y",
				"-f", "lavfi", "-i", input_filter,
				"-vf", vf_filter,
				"-c:v", "libx264",
				"-crf", qp_val,
				"-pix_fmt", "yuv420p",
				"-g", str(self.gop_spin.value()),
			]

		bitrate = self.bitrate_edit.text().strip()
		if bitrate:
			cmd += ["-b:v", bitrate]

		ct_val = self.meta_creation_time.text().strip()
		if ct_val:
			cmd += ["-metadata", f"creation_time={ct_val}"]
		if encoder_meta:
			cmd += ["-metadata", f"encoder={encoder_meta}"]

		if self.chk_container_timecode.isChecked():
			cmd += ["-metadata", "timecode=00:00:00:00"]

		# Forensik-Metadaten aus Tab 2 (nur wenn nicht leer)
		meta_map = [
			("title", self.meta_title),
			("artist", self.meta_artist),
			("copyright", self.meta_copyright),
			("description", self.meta_description),
			("language", self.meta_language),
			("show", self.meta_show),
			("episode_id", self.meta_episode_id),
			("genre", self.meta_genre),
			("comment", self.meta_comment),
			("date", self.meta_date),
		]
		for key, edit in meta_map:
			val = edit.text().strip()
			if val:
				cmd += ["-metadata", f"{key}={val}"]

		cmd.append(output)
		return cmd, output

	# ---------------- Start / Worker ----------------

	def start_ffmpeg(self):
		cmd, output = self.build_ffmpeg_command()
		self.log_view.clear()
		self.progress.setValue(0)
		self.btn_start.setEnabled(False)

		self.worker = FFmpegWorker(cmd, output)
		self.worker.progress.connect(self.progress.setValue)
		self.worker.finished_ok.connect(self.on_finished_ok)
		self.worker.finished_error.connect(self.on_finished_error)
		self.worker.log_line.connect(self.append_log)
		self.worker.start()

	def append_log(self, line: str):
		self.log_view.append(line)

	def on_finished_ok(self, path: str):
		self.btn_start.setEnabled(True)
		self.statusBar().showMessage(f"Fertig: {path}", 5000)

	def on_finished_error(self, msg: str):
		self.btn_start.setEnabled(True)
		self.statusBar().showMessage(f"Fehler: {msg}", 8000)
		self.log_view.append(f"\nFEHLER: {msg}")

	# ---------------- Bild / Photo ----------------

	def choose_img_output(self):
		path, _ = QFileDialog.getSaveFileName(
			self, "Ausgabedatei wählen",
			self.img_out.text(),
			"Bilder (*.png *.jpg *.bmp *.tif *.webp);;Alle Dateien (*.*)"
		)
		if path:
			self.img_out.setText(path)

	def choose_img_bg_color(self):
		color = QColorDialog.getColor(
			QColor(self.img_bg.text()), self, "Hintergrundfarbe"
		)
		if color.isValid():
			self.img_bg.setText(color.name())

	def _update_img_extension(self, fmt: str):
		path = self.img_out.text()
		base, _ = path.rsplit(".", 1) if "." in path else (path, "")
		self.img_out.setText(f"{base}.{fmt}")

	def generate_image(self):
		fmt = self.img_format.currentText()
		w = self.img_w.value()
		h = self.img_h.value()
		bg = self.img_bg.text().strip()
		fontfile = self.img_font.text().strip()
		output = self.img_out.text().strip()

		date_str = datetime.datetime.now().strftime("%d.%m.%Y")
		time_str = datetime.datetime.now().strftime("%H:%M:%S")
		time_esc = time_str.replace(":", "\\:")

		if bg.lower() in ("smptebars", "testsrc", "testsrc2"):
			input_filter = f"{bg}=s={w}x{h}:d=1"
		else:
			input_filter = f"color=c={bg}:s={w}x{h}:d=1"

		fontsize = max(20, h // 20)
		offset = fontsize // 2

		vf = (
			f"drawtext=fontfile='{fontfile}':"
			f"text='{date_str}':"
			f"fontsize={fontsize}:fontcolor=white:"
			f"x=(w-text_w)/2:y=(h-text_h)/2-{offset},"
			f"drawtext=fontfile='{fontfile}':"
			f"text='{time_esc}':"
			f"fontsize={fontsize}:fontcolor=white:"
			f"x=(w-text_w)/2:y=(h-text_h)/2+{offset}"
		)

		cmd = [
			"ffmpeg", "-y",
			"-f", "lavfi", "-i", input_filter,
			"-vf", vf,
			"-frames:v", "1",
			"-update", "1",
			output,
		]

		self.img_log.clear()
		self.img_status.setText("")
		self.img_btn.setEnabled(False)

		self.img_worker = ImageWorker(cmd, output)
		self.img_worker.finished_ok.connect(self.on_img_finished)
		self.img_worker.finished_error.connect(self.on_img_error)
		self.img_worker.log_line.connect(self.img_log.append)
		self.img_worker.start()

	def on_img_finished(self, path: str):
		self.img_btn.setEnabled(True)
		self.img_status.setText(f"Fertig: {path}")
		self.statusBar().showMessage(f"Bild erstellt: {path}", 5000)

	def on_img_error(self, msg: str):
		self.img_btn.setEnabled(True)
		self.img_status.setText(f"Fehler: {msg}")
		self.statusBar().showMessage(f"Bild-Fehler: {msg}", 8000)
		self.img_log.append(f"\nFEHLER: {msg}")


def main():
	app = QApplication(sys.argv)
	win = FFmpegTestVideoWindow()
	win.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()