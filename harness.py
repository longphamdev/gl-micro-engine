import time
import statistics
import glfw
from OpenGL.GL import *


class OpenGLTimerHarness:
    def __init__(self, width=1280, height=720, duration_sec=10.0):
        self.width = width
        self.height = height
        self.duration_sec = duration_sec
        self.gpu_frame_times_ms = []

    def init_context(self):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self.window = glfw.create_window(self.width, self.height, "ProxyBench", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create offscreen OpenGL context")
        glfw.make_context_current(self.window)

    def render_proxy_workload(self, frame_idx: int):
        glClearColor(0.08, 0.09, 0.11, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for i in range(250):
            glScissor((i + frame_idx) % 64, (i * 2) % 64, 32, 32)
            glEnable(GL_SCISSOR_TEST)
            glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_SCISSOR_TEST)

    def run(self):
        self.init_context()
        query_id = glGenQueries(1)
        start_time = time.perf_counter()
        frame_idx = 0

        try:
            while (time.perf_counter() - start_time) < self.duration_sec:
                glBeginQuery(GL_TIME_ELAPSED, query_id)
                self.render_proxy_workload(frame_idx)
                glEndQuery(GL_TIME_ELAPSED)

                elapsed_ns = glGetQueryObjectui64v(query_id, GL_QUERY_RESULT)
                self.gpu_frame_times_ms.append(elapsed_ns / 1_000_000.0)
                frame_idx += 1
        finally:
            glDeleteQueries(1, [query_id])
            glfw.terminate()

        sorted_ms = sorted(self.gpu_frame_times_ms)
        n = len(sorted_ms)
        p95 = sorted_ms[min(int(n * 0.95), n - 1)] if n else 0.0
        return {
            "frames": n,
            "mean_gpu_ms": round(statistics.mean(sorted_ms), 4) if n else 0.0,
            "p95_gpu_ms": round(p95, 4),
        }


if __name__ == "__main__":
    print(OpenGLTimerHarness().run())