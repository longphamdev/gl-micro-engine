#include <iostream>
#include <vector>
#include <algorithm>

struct DrawBatch {
    unsigned int vao = 0;
    unsigned int vertexCount = 0;
    unsigned int shaderId = 0;
};

class MicroRenderer {
public:
    void submit(const DrawBatch& batch) {
        queue_.push_back(batch);
    }

    void flush() {
        // Group batches by shader and VAO to minimize OpenGL state transitions
        std::sort(queue_.begin(), queue_.end(), [](const DrawBatch& a, const DrawBatch& b) {
            if (a.shaderId != b.shaderId) return a.shaderId < b.shaderId;
            return a.vao < b.vao;
        });

        for (const auto& batch : queue_) {
            (void)batch;
        }
        queue_.clear();
    }

private:
    std::vector<DrawBatch> queue_;
};

int main() {
    MicroRenderer renderer;
    renderer.submit({1, 36, 1});
    renderer.submit({2, 128, 1});
    renderer.flush();
    std::cout << "MicroRenderer baseline initialized.\n";
    return 0;
}