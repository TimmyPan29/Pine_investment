#include <iostream>
#include <vector>

class CircularBuffer {
private:
    std::vector<double> buffer;
    int index;
    int count;
    const int BUFFER_SIZE;

public:
    // 構造函數，設置緩衝區大小
    CircularBuffer(int size) : BUFFER_SIZE(size), index(0), count(0) {
        buffer.resize(BUFFER_SIZE, 0); // {0, 0, 0}
    }

    // 添加新元素
    void Add(double value) {
        buffer[index] = value;
        index = (index + 1) % BUFFER_SIZE; //新的index往右邊指 超過size就回來第一個
        if (count < BUFFER_SIZE)
            count++;
    }

    // 獲取緩衝區內容
    std::vector<double> GetContents() {
        std::vector<double> contents;
        for (int i = 0; i < count; i++) {
            contents.push_back(buffer[(index + i) % BUFFER_SIZE]);
        }
        return contents;
    }

    // 獲取緩衝區大小
    int GetSize() {
        return count;
    }

    // 打印緩衝區內容
    void PrintContents() {
        std::vector<double> contents = GetContents();
        std::cout << "Contents: [";
        for (size_t i = 0; i < contents.size(); i++) {
            if (i > 0) std::cout << ", ";
            std::cout << contents[i];
        }
        std::cout << "]" << std::endl;
    }
};

int main() {
    CircularBuffer cb(3);

    // 添加數據並顯示
    cb.Add(1.1);
    cb.PrintContents();

    cb.Add(2.2);
    cb.PrintContents();

    cb.Add(3.3);
    cb.PrintContents();

    cb.Add(4.4);
    cb.PrintContents();

    cb.Add(5.5);
    cb.PrintContents();

    return 0;
}
