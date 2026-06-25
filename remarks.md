MVP-Architektur ist fertig. Neue Dateistruktur:

model.py       → Datenklassen (VideoParams, ImageParams)
                  SettingsManager (video.ini)
                  VideoCommandBuilder / ImageCommandBuilder
                  FFmpegWorker / ImageWorker (Threads)

view.py        → MainWindow (Qt-UI, 3 Tabs)
                  Signale: video_start_requested, image_generate_requested
                  Properties: get_video_params(), apply_preset()
                  Update-Methoden: set_video_progress(), append_log(), etc.

presenter.py   → Verbindet View-Signale mit Model-Logik
                  Startet Worker, Settings laden/speichern

main.py        → QApplication + View + Presenter