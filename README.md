# gl-micro-engine

A low-overhead 2D/3D rendering runtime paired with an automated GPU frame-pacing benchmark harness.
The runtime provides a small, extensible batch-renderer foundation; the harness measures real GPU
elapsed time with OpenGL timer queries so that graphics changes can be compared consistently.

## Structure

```text
benchmarks/
  harness.py       # Standalone 10-second OpenGL timer-query benchmark
src/
  engine/
    __init__.py    # Engine package exports
    renderer.py    # Batch renderer skeleton
  shaders/
    basic.vert     # GLSL 330 core vertex shader
    basic.frag     # GLSL 330 core fragment shader
tests/
  test_harness.py  # Metric and headless fallback tests
```

## Setup

Python 3.9 or newer is recommended. GLFW 2.7+ and PyOpenGL 3.1.7+ are required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python benchmarks/harness.py
```

The benchmark creates a hidden 3.3 Core context and reports frame count, mean GPU frame time, and
p95 GPU frame time. In environments without a GPU display, it exits with a zero-frame fallback
instead of raising a platform error.
