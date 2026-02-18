"""Regression tests for TTS playback speed/pitch controls."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt6.QtWidgets import QApplication
except ModuleNotFoundError:  # pragma: no cover - optional GUI dependency
    QApplication = None

if QApplication is not None:
    from ui.tts_panel import TTSPanel
else:  # pragma: no cover - optional GUI dependency
    TTSPanel = None


class TTSPanelPlaybackControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication is None:
            raise unittest.SkipTest("PyQt6 not installed in this environment")
        cls._app = QApplication.instance() or QApplication([])

    def test_speed_step_controls_adjust_both_directions(self):
        panel = TTSPanel()
        panel.set_playback_available(True)

        initial = panel.get_playback_speed()
        panel._step_speed(1)
        self.assertGreater(panel.get_playback_speed(), initial)
        panel._step_speed(-1)
        self.assertAlmostEqual(panel.get_playback_speed(), initial, places=6)

    def test_pitch_step_controls_adjust_both_directions(self):
        panel = TTSPanel()
        panel.set_playback_available(True)

        initial = panel.get_playback_pitch()
        panel._step_pitch(1)
        self.assertGreater(panel.get_playback_pitch(), initial)
        panel._step_pitch(-1)
        self.assertAlmostEqual(panel.get_playback_pitch(), initial, places=6)

    def test_api_speed_control_set_and_clamp(self):
        panel = TTSPanel()
        panel.set_api_speed(0.8)
        self.assertAlmostEqual(panel.get_api_speed(), 0.8, places=6)
        panel.set_api_speed(0.0)
        self.assertGreater(panel.get_api_speed(), 0.0)

    def test_open_saved_audio_button_emits_signal(self):
        panel = TTSPanel()
        seen = []
        panel.open_saved_audio_requested.connect(lambda: seen.append(True))

        panel.btn_open_saved_audio.click()
        self.assertEqual(len(seen), 1)


if __name__ == "__main__":
    unittest.main()
