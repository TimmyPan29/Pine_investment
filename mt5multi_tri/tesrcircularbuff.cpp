#include <iostream>
#include <vector>

class CircularBuffer {
public:
    CircularBuffer(size_t size) : buffer(size), head(0), tail(0), full(false) {}

    void add(int value) {
        buffer[tail] = value;
        if (full) {
            head = (head + 1) % buffer.size();
        }
        tail = (tail + 1) % buffer.size();
        full = tail == head;
    }

    void printBuffer() const {
        size_t idx = head;
        for (size_t i = 0; i < buffer.size(); ++i) {
            std::cout << buffer[idx] << " ";
            idx = (idx + 1) % buffer.size();
        }
        std::cout << std::endl;
    }

private:
    std::vector<int> buffer;
    size_t head;
    size_t tail;
    bool full;
};

int main() {
    CircularBuffer cb(3000);
    
    // 模擬新增資料
    for (int i = 0; i < 3050; ++i) {
        cb.add(i);
    }

    // 輸出環形緩衝區的內容
    cb.printBuffer();

    return 0;
}
