from __future__ import annotations

from typing import Any, Iterable

try:
    from OpenGL import GL
except ImportError:  # pragma: no cover - the skeleton remains importable without dependencies
    GL = None


class VertexBufferManager:
    """Owns OpenGL vertex buffer objects and centralizes uploads."""

    def __init__(self) -> None:
        self.buffers: dict[int, int] = {}
        self._next_id = 1

    def create(self, data: Iterable[float] | None = None) -> int:
        buffer_id = GL.glGenBuffers(1) if GL is not None else 0
        if data is not None and GL is not None:
            import array

            payload = array.array("f", data)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer_id)
            GL.glBufferData(
                GL.GL_ARRAY_BUFFER,
                payload.tobytes(),
                GL.GL_DYNAMIC_DRAW,
            )
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        self.buffers[self._next_id] = buffer_id
        handle = self._next_id
        self._next_id += 1
        return handle

    def update(self, handle: int, data: Iterable[float]) -> None:
        if GL is None:
            return
        import array

        buffer_id = self.buffers[handle]
        payload = array.array("f", data)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer_id)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, payload.tobytes())
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def delete(self, handle: int) -> None:
        buffer_id = self.buffers.pop(handle)
        if GL is not None:
            GL.glDeleteBuffers(1, [buffer_id])


class StateCache:
    """Caches rendering state to avoid redundant OpenGL calls."""

    def __init__(self) -> None:
        self._state: dict[str, Any] = {}

    def set(self, name: str, value: Any) -> bool:
        if self._state.get(name) == value:
            return False
        self._state[name] = value
        return True

    def get(self, name: str, default: Any = None) -> Any:
        return self._state.get(name, default)

    def clear(self) -> None:
        self._state.clear()


class BatchRenderer:
    """Minimal batch renderer skeleton ready for draw-call optimization."""

    def __init__(self) -> None:
        self.buffers = VertexBufferManager()
        self.state = StateCache()
        self._batches: list[dict[str, Any]] = []
        self.drawing = False

    def begin(self) -> None:
        self._batches.clear()
        self.drawing = True

    def submit(self, vertices: Iterable[float], state: dict[str, Any] | None = None) -> None:
        if not self.drawing:
            raise RuntimeError("BatchRenderer.begin() must be called before submit()")
        self._batches.append({"vertices": tuple(vertices), "state": state or {}})

    def flush(self) -> int:
        if not self.drawing:
            return 0

        draw_calls = 0
        for batch in self._batches:
            for name, value in batch["state"].items():
                self.state.set(name, value)
            # Stub: coalesce compatible batches and issue a single draw call here.
            draw_calls += 1
        self._batches.clear()
        return draw_calls

    def end(self) -> int:
        draw_calls = self.flush()
        self.drawing = False
        return draw_calls
