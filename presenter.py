from model import (
	VideoCommandBuilder, ImageCommandBuilder,
	WriteCommandBuilder, WriteWorker,
	WriteFileEntry,
	SettingsManager, FFmpegWorker, ImageWorker,
	set_file_creation_time,
	write_exif_to_image,
)


class Presenter:
	def __init__(self, view):
		self.view = view
		self._video_worker = None
		self._image_worker = None
		self._write_worker = None
		self._pending_video_ctime = ""
		self._pending_image_ctime = ""

		# View-Signale verbinden
		self.view.video_start_requested.connect(self._on_start_video)
		self.view.image_generate_requested.connect(self._on_generate_image)
		self.view.write_start_requested.connect(self._on_write)
		self.view.btn_apply_preset.clicked.connect(self.view.apply_preset)

		# Settings laden
		self.view.apply_preset()
		settings = SettingsManager.load()
		self.view.load_settings_to_ui(settings)

	def _on_start_video(self):
		params = self.view.get_video_params()
		self._pending_video_ctime = params.meta_creation_time

		self.view.clear_video_log()
		self.view.set_video_progress(0)
		self.view.set_video_controls_enabled(False)

		cmd = VideoCommandBuilder.build(params)

		self._video_worker = FFmpegWorker(cmd, params.output)
		self._video_worker.progress.connect(self.view.set_video_progress)
		self._video_worker.finished_ok.connect(self._on_video_finished)
		self._video_worker.finished_error.connect(self._on_video_error)
		self._video_worker.log_line.connect(self.view.append_video_log)
		self._video_worker.start()

		SettingsManager.save(self.view.collect_settings_from_ui())

	def _on_video_finished(self, path: str):
		set_file_creation_time(path, self._pending_video_ctime)
		self._pending_video_ctime = ""
		self.view.set_video_controls_enabled(True)
		self.view.show_video_finished(path)

	def _on_video_error(self, msg: str):
		self._pending_video_ctime = ""
		self.view.set_video_controls_enabled(True)
		self.view.show_video_error(msg)

	def _on_generate_image(self):
		params = self.view.get_image_params()
		self._pending_image_ctime = params.meta_creation_time
		# EXIF-Parameter speichern für nachträgliches Schreiben
		self._pending_image_exif = {
			"title": params.meta_title,
			"artist": params.meta_artist,
			"copyright": params.meta_copyright,
			"comment": params.meta_comment,
			"location": params.meta_location,
			"make": params.exif_make,
			"model": params.exif_model,
			"software": params.exif_software,
			"datetime_original": params.exif_datetime_original,
			"datetime_digitized": params.exif_datetime_digitized,
		}

		self.view.clear_img_log()
		self.view.set_img_status("")
		self.view.set_img_controls_enabled(False)

		cmd = ImageCommandBuilder.build(params)

		self._image_worker = ImageWorker(cmd, params.output)
		self._image_worker.finished_ok.connect(self._on_image_finished)
		self._image_worker.finished_error.connect(self._on_image_error)
		self._image_worker.log_line.connect(self.view.append_img_log)
		self._image_worker.start()

		SettingsManager.save(self.view.collect_settings_from_ui())

	def _on_image_finished(self, path: str):
		set_file_creation_time(path, self._pending_image_ctime)

		# EXIF-Metadaten nachträglich schreiben
		exif_params = getattr(self, '_pending_image_exif', {})
		if exif_params and exif_params.get("title") or exif_params.get("artist") or exif_params.get("copyright") or exif_params.get("comment") or exif_params.get("location") or exif_params.get("make") or exif_params.get("model") or exif_params.get("software") or exif_params.get("datetime_original") or exif_params.get("datetime_digitized"):
			success = write_exif_to_image(
				path,
				creation_time=self._pending_image_ctime,
				title=exif_params.get("title", ""),
				artist=exif_params.get("artist", ""),
				copyright=exif_params.get("copyright", ""),
				comment=exif_params.get("comment", ""),
				location=exif_params.get("location", ""),
				make=exif_params.get("make", ""),
				model=exif_params.get("model", ""),
				software=exif_params.get("software", ""),
				datetime_original=exif_params.get("datetime_original", ""),
				datetime_digitized=exif_params.get("datetime_digitized", ""),
			)
			if success:
				self.view.append_img_log("✅ EXIF-Metadaten geschrieben")
			else:
				self.view.append_img_log("⚠️ EXIF-Metadaten konnten nicht geschrieben werden (piexif nicht verfügbar oder Fehler)")

		self._pending_image_ctime = ""
		self._pending_image_exif = {}
		self.view.set_img_controls_enabled(True)
		self.view.show_img_finished(path)

	def _on_image_error(self, msg: str):
		self._pending_image_ctime = ""
		self.view.set_img_controls_enabled(True)
		self.view.show_img_error(msg)

	def _on_write(self):
		entries = self.view.get_write_files()
		if not entries:
			return
		meta = self.view.get_write_meta()

		self.view.clear_write_log()
		self.view.set_write_controls_enabled(False)

		jobs = []
		for src, ct in entries:
			entry = WriteFileEntry(source=src, creation_time=ct)
			cmd, temp = WriteCommandBuilder.build(src, entry, meta)
			jobs.append((cmd, src, ct))

		self._write_worker = WriteWorker(jobs)
		self._write_worker.log_line.connect(self.view.append_write_log)
		self._write_worker.file_done.connect(self._on_write_file_done)
		self._write_worker.finished_ok.connect(self._on_write_finished)
		self._write_worker.finished_error.connect(self._on_write_error)
		self._write_worker.start()

	def _on_write_file_done(self, index: int, path: str):
		self.view.append_write_log(f"✅ {path}")

	def _on_write_finished(self):
		self.view.set_write_controls_enabled(True)
		self.view.append_write_log("✅ Alle Dateien verarbeitet.")

	def _on_write_error(self, msg: str):
		self.view.set_write_controls_enabled(True)
		self.view.append_write_log(f"❌ {msg}")
