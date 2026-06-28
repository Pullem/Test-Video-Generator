import subprocess
import datetime
import configparser
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


# ---------- GPS-Hilfsfunktion ----------

def _parse_iso6709(coords: str) -> list[tuple[str, str]]:
	"""Parst "+49.1234+008.5678/" → EXIF-Metadaten-Liste."""
	try:
		import re
		m = re.match(r"([+-]\d+\.?\d*)([+-]\d+\.?\d*)/?", coords.strip())
		if not m:
			return []
		lat = float(m.group(1))
		lon = float(m.group(2))
	except (ValueError, TypeError):
		return []

	def _to_dms(deg: float) -> tuple[int, int, int]:
		d = int(abs(deg))
		mf = (abs(deg) - d) * 60
		mi = int(mf)
		sf = (mf - mi) * 60
		return d, mi, int(round(sf * 100))  # 2 Nachkommastellen als Rational

	lat_ref = "N" if lat >= 0 else "S"
	lat_d, lat_m, lat_s = _to_dms(lat)
	lon_ref = "E" if lon >= 0 else "W"
	lon_d, lon_m, lon_s = _to_dms(lon)

	return [
		("GPSLatitudeRef", lat_ref),
		("GPSLatitude", f"{lat_d}/1 {lat_m}/1 {lat_s}/100"),
		("GPSLongitudeRef", lon_ref),
		("GPSLongitude", f"{lon_d}/1 {lon_m}/1 {lon_s}/100"),
	]


def set_file_creation_time(path: str, creation_time_str: str):
	"""Setzt die Datei-Erstellungszeit auf Windows (creation_time als Lokalzeit)."""
	if sys.platform != "win32" or not creation_time_str:
		return
	try:
		dt_local = datetime.datetime.fromisoformat(creation_time_str)
	except (ValueError, TypeError):
		return
	if dt_local.tzinfo is None:
		dt_local = dt_local.replace(tzinfo=datetime.datetime.now().astimezone().tzinfo)
	dt_utc = dt_local.astimezone(datetime.timezone.utc)
	epoch = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
	ft = int((dt_utc - epoch).total_seconds() * 10_000_000)

	import ctypes
	from ctypes import wintypes

	kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

	handle = kernel32.CreateFileW(
		path,
		0x100,                    # FILE_WRITE_ATTRIBUTES
		0x7,                      # FILE_SHARE_READ|WRITE|DELETE
		None,
		3,                        # OPEN_EXISTING
		0,
		None,
	)
	if handle in (wintypes.HANDLE(-1).value, wintypes.HANDLE(0).value, None):
		return

	try:
		class FILETIME(ctypes.Structure):
			_fields_ = [("dwLowDateTime", wintypes.DWORD),
						("dwHighDateTime", wintypes.DWORD)]
		ft_s = FILETIME(ft & 0xFFFFFFFF, ft >> 32)
		kernel32.SetFileTime(handle, ctypes.byref(ft_s), None, None)
	finally:
		kernel32.CloseHandle(handle)


# ---------- Datenklassen ----------

@dataclass
class VideoParams:
	width: int = 1280
	height: int = 720
	fps: int = 25
	duration: int = 300
	source: str = "black"
	fontfile: str = "C\\:/Windows/Fonts/arial.ttf"
	font_size: int = 48
	encoder: str = "libx264 (CPU)"
	crf: int = 23
	bitrate: str = ""
	gop: int = 50
	timecode_overlay: bool = True
	pts_overlay: bool = True
	datetime_overlay: bool = False
	container_timecode: bool = True
	encoder_meta: str = "FFmpeg Testvideo Generator"
	output: str = "ffmpeg_testvideo.mp4"
	meta_title: str = ""
	meta_artist: str = ""
	meta_copyright: str = ""
	meta_description: str = ""
	meta_language: str = ""
	meta_show: str = ""
	meta_episode_id: str = ""
	meta_genre: str = ""
	meta_comment: str = ""
	meta_creation_time: str = ""
	meta_date: str = ""
	meta_location: str = ""


@dataclass
class ImageParams:
	width: int = 1920
	height: int = 1080
	source: str = "black"
	fontfile: str = "C\\:/Windows/Fonts/arial.ttf"
	font_size: int = 54
	output: str = "testbild.png"
	meta_title: str = ""
	meta_artist: str = ""
	meta_copyright: str = ""
	meta_comment: str = ""
	meta_creation_time: str = ""
	meta_location: str = ""


# ---------- Settings ----------

INI_PATH = Path(__file__).parent / "video.ini"


class SettingsManager:
	@staticmethod
	def load() -> dict:
		settings = {}
		if not INI_PATH.exists():
			return settings
		try:
			ini = configparser.ConfigParser()
			ini.read(INI_PATH, encoding="utf-8")
			if "Settings" in ini:
				for k, v in ini["Settings"].items():
					settings[k] = v
		except Exception:
			pass
		return settings

	@staticmethod
	def save(settings: dict):
		try:
			ini = configparser.ConfigParser()
			ini["Settings"] = settings
			with open(INI_PATH, "w", encoding="utf-8") as f:
				ini.write(f)
		except Exception:
			pass


# ---------- Kommando-Builder ----------

class VideoCommandBuilder:
	@staticmethod
	def build(params: VideoParams) -> list[str]:
		fontfile_esc = params.fontfile.replace(":", "\\:")
		source_lower = params.source.lower()

		if source_lower in ("smptebars", "testsrc", "testsrc2"):
			input_filter = f"{source_lower}=s={params.width}x{params.height}:r={params.fps}:d={params.duration}"
		else:
			input_filter = f"color=c={params.source}:s={params.width}x{params.height}:r={params.fps}:d={params.duration}"

		vf_parts = []

		if params.timecode_overlay:
			tc = (
				f"drawtext=fontfile='{fontfile_esc}':"
				f"timecode='00\\:00\\:00\\:00':"
				f"r={params.fps}:"
				f"x=40:y=40:fontsize={params.font_size}:fontcolor=white"
			)
			vf_parts.append(tc)

		if params.pts_overlay:
			pts = (
				f"drawtext=fontfile='{fontfile_esc}':"
				f"text='%{{pts\\:hms}}.%{{n}}':"
				f"x=40:y=120:fontsize={max(8, params.font_size - 12)}:fontcolor=yellow"
			)
			vf_parts.append(pts)

		if params.datetime_overlay:
			ct = params.meta_creation_time
			try:
				dt = datetime.datetime.fromisoformat(ct)
			except (ValueError, TypeError):
				dt = datetime.datetime.now()
			date_str = dt.strftime("%d.%m.%Y")
			start_str = dt.strftime("%H:%M:%S")
			dur_mm = params.duration // 60
			dur_ss = params.duration % 60
			dur_str = f"{dur_mm:02d}:{dur_ss:02d}"
			end_dt = dt + datetime.timedelta(seconds=params.duration)
			end_str = end_dt.strftime("%H:%M:%S")
			start_esc = start_str.replace(":", "\\:")
			dur_esc = dur_str.replace(":", "\\:")
			end_esc = end_str.replace(":", "\\:")
			fs = params.font_size
			off = fs // 2
			fs_small = max(8, fs - 6)
			vf_parts.append(
				f"drawtext=fontfile='{fontfile_esc}':"
				f"text='{date_str}':"
				f"fontsize={fs}:fontcolor=white:"
				f"x=(w-text_w)/2:y=(h-text_h)/2-{off}"
			)
			vf_parts.append(
				f"drawtext=fontfile='{fontfile_esc}':"
				f"text='{start_esc}  +  {dur_esc}  ->  {end_esc}':"
				f"fontsize={fs_small}:fontcolor=white:"
				f"x=(w-text_w)/2:y=(h-text_h)/2+{off}"
			)

		vf_filter = ",".join(vf_parts) if vf_parts else "null"

		if "nvenc" in params.encoder:
			cmd = [
				"ffmpeg", "-y",
				"-f", "lavfi", "-i", input_filter,
				"-vf", vf_filter,
				"-c:v", "h264_nvenc",
				"-qp", str(params.crf),
				"-pix_fmt", "yuv420p",
				"-g", str(params.gop),
			]
		else:
			cmd = [
				"ffmpeg", "-y",
				"-f", "lavfi", "-i", input_filter,
				"-vf", vf_filter,
				"-c:v", "libx264",
				"-crf", str(params.crf),
				"-pix_fmt", "yuv420p",
				"-g", str(params.gop),
			]

		if params.bitrate:
			cmd += ["-b:v", params.bitrate]

		if params.encoder_meta:
			cmd += ["-metadata", f"encoder={params.encoder_meta}"]
		if params.container_timecode:
			cmd += ["-metadata", "timecode=00:00:00:00"]

		meta_map = [
			("title", params.meta_title),
			("artist", params.meta_artist),
			("copyright", params.meta_copyright),
			("description", params.meta_description),
			("language", params.meta_language),
			("show", params.meta_show),
			("episode_id", params.meta_episode_id),
			("genre", params.meta_genre),
			("comment", params.meta_comment),
			("date", params.meta_date),
			("location", params.meta_location),
		]
		for key, val in meta_map:
			if val:
				cmd += ["-metadata", f"{key}={val}"]
		if params.meta_location:
			cmd += ["-metadata", f"location-eng={params.meta_location}"]

		cmd.append(params.output)
		return cmd


class ImageCommandBuilder:
	@staticmethod
	def build(params: ImageParams) -> list[str]:
		fontfile_esc = params.fontfile.replace(":", "\\:")
		date_str = datetime.datetime.now().strftime("%d.%m.%Y")
		time_str = datetime.datetime.now().strftime("%H:%M:%S")
		time_esc = time_str.replace(":", "\\:")

		source_lower = params.source.lower()
		if source_lower in ("smptebars", "testsrc", "testsrc2"):
			input_filter = f"{source_lower}=s={params.width}x{params.height}:d=1"
		else:
			input_filter = f"color=c={params.source}:s={params.width}x{params.height}:d=1"

		fontsize = params.font_size
		offset = fontsize // 2

		vf = (
			f"drawtext=fontfile='{fontfile_esc}':"
			f"text='{date_str}':"
			f"fontsize={fontsize}:fontcolor=white:"
			f"x=(w-text_w)/2:y=(h-text_h)/2-{offset},"
			f"drawtext=fontfile='{fontfile_esc}':"
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
		]

		if params.meta_title:
			cmd += ["-metadata", f"title={params.meta_title}"]
		if params.meta_artist:
			cmd += ["-metadata", f"artist={params.meta_artist}"]
		if params.meta_copyright:
			cmd += ["-metadata", f"copyright={params.meta_copyright}"]
		if params.meta_comment:
			cmd += ["-metadata", f"comment={params.meta_comment}"]
		if params.meta_location:
			cmd += ["-metadata", f"location={params.meta_location}"]
			for key, val in _parse_iso6709(params.meta_location):
				cmd += ["-metadata", f"{key}={val}"]

		cmd.append(params.output)
		return cmd


# ---------- Worker-Threads ----------

class FFmpegWorker(QThread):
	progress = pyqtSignal(int)
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
				self.progress.emit(min(99, line_count // 5))
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
