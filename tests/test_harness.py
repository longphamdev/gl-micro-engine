import math
import unittest
from unittest.mock import patch

from benchmarks.harness import OpenGLTimerHarness, calculate_metrics


class HarnessTests(unittest.TestCase):
    def test_calculate_metrics(self):
        samples = [1.0, 2.0, 3.0, 4.0, 5.0]
        metrics = calculate_metrics(samples)

        self.assertEqual(metrics["frames"], 5)
        self.assertEqual(metrics["mean_gpu_ms"], 3.0)
        self.assertTrue(math.isclose(metrics["p95_gpu_ms"], 4.8))

    def test_calculate_metrics_empty(self):
        self.assertEqual(
            calculate_metrics([]),
            {"frames": 0, "mean_gpu_ms": 0.0, "p95_gpu_ms": 0.0},
        )

    def test_harness_headless_fallback(self):
        with patch("benchmarks.harness.glfw", None):
            metrics = OpenGLTimerHarness(duration_seconds=0.01).run()

        self.assertEqual(
            set(metrics),
            {"frames", "mean_gpu_ms", "p95_gpu_ms"},
        )
        self.assertTrue(all(value == 0 or value == 0.0 for value in metrics.values()))


if __name__ == "__main__":
    unittest.main()
