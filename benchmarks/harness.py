from __future__ import annotations

import math
import time
from typing import Iterable

try:
    import glfw
    from OpenGL import GL
except ImportError:  # pragma: no cover - exercised through fallback tests
    glfw = None
    GL = None


def calculate_metrics(samples_ms: Iterable[float]) -> dict[str, float | int]:
    """Calculate frame count and GPU timing statistics from elapsed milliseconds."""
    samples = [float(value) for value in samples_ms if math.isfinite(float(value))]
    if not samples:
        return {"frames": 0, "mean_gpu_ms": 0.0, "p95_gpu_ms": 0.0}

    samples.sort()
    frame_count = len(samples)
    mean = sum(samples) / frame_count

    # Linear percentile interpolation (equivalent to NumPy's default percentile method).
    position = 0.95 * (frame_count - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        p95 = samples[lower]
    else:
        fraction = position - lower
        p95 = samples[lower] + (samples[upper] - samples[lower]) * fraction

    return {
        "frames": frame_count,
        "mean_gpu_ms": mean,
        "p95_gpu_ms": p95,
    }


class OpenGLTimerHarness:
    """Deterministic 10-second offscreen GPU proxy workload."""

    def __init__(self, duration_seconds: float = 10.0) -> None:
        self.duration_seconds = duration_seconds
        self.window = None

    @staticmethod
    def calculate_metrics(samples_ms: Iterable[float]) -> dict[str, float | int]:
        return calculate_metrics(samples_ms)

    def run(self) -> dict[str, float | int]:
        if glfw is None or GL is None:
            return calculate_metrics([])

        if not glfw.init():
            return calculate_metrics([])

        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

        self.window = glfw.create_window(64, 64, "GPU Benchmark", None, None)
        if self.window is None:
            glfw.terminate()
            return calculate_metrics([])

        glfw.make_context_current(self.window)
        return self._run_workload()

    def _run_workload(self) -> dict[str, float | int]:
        vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao)

        elapsed_samples: list[float] = []
        start = time.monotonic()

        while time.monotonic() - start < self.duration_seconds:
            query = GL.glGenQueries(1)
            GL.glBeginQuery(GL.GL_TIME_ELAPSED, query)

            GL.glClearColor(0.0, 0.0, 0.0, 1.0)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            for _ in range(100):
                GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

            GL.glEndQuery(GL.GL_TIME_ELAPSED)

            available = GL.GL_FALSE
            while available != GL.GL_TRUE:
                available = GL.glGetQueryObjectuiv(query, GL.GL_QUERY_RESULT_AVAILABLE)
            elapsed_ns = GL.glGetQueryObjectui64v(query, GL.GL_QUERY_RESULT)
            elapsed_samples.append(float(elapsed_ns) / 1_000_000.0)
            GL.glDeleteQueries(1, [query])

            glfw.poll_events()
            glfw.swap_buffers(self.window)

        GL.glBindVertexArray(0)
        GL.glDeleteVertexArrays(1, [vao])
        glfw.destroy_window(self.window)
        glfw.terminate()
        self.window = None
        return calculate_metrics(elapsed_samples)


def main() -> None:
    metrics = OpenGLTimerHarness().run()
    print(
        "frames={frames} mean_gpu_ms={mean_gpu_ms:.3f} p95_gpu_ms={p95_gpu_ms:.3f}".format(
            **metrics
        )
    )


if __name__ == "__main__":
    main()
