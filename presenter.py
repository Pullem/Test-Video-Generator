from model import (
	VideoCommandBuilder, ImageCommandBuilder,
	SettingsManager, FFmpegWorker, ImageWorker,
)


class Presenter:
	def __init__(self, view):
		self.view = view
		self._video_worker = None
		self._image_worker = None

		# View-Signale verbinden
		self.view.video_start_requested.connect(self._on_start_video)
		self.view.image_generate_requested.connect(self._on_generate_image)
		self.view.btn_apply_preset.clicked.connect(self.view.apply_preset)

		# Settings laden
		self.view.apply_preset()
		settings = SettingsManager.load()
		self.view.load_settings_to_ui(settings)

	def _on_start_video(self):
		params = self.view.get_video_params()

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
		self.view.set_video_controls_enabled(True)
		self.view.show_video_finished(path)

	def _on_video_error(self, msg: str):
		self.view.set_video_controls_enabled(True)
		self.view.show_video_error(msg)

	def _on_generate_image(self):
		params = self.view.get_image_params()

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
		self.view.set_img_controls_enabled(True)
		self.view.show_img_finished(path)

	def _on_image_error(self, msg: str):
		self.view.set_img_controls_enabled(True)
		self.view.show_img_error(msg)
