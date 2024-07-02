#include <iostream>

// 交换函数
void swap(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

// 插入排序函数
void insertionSort(int arr[], int index[], int n) {//這個函數的思考重點 必須記憶的重點是 因為在每個i變大的過程 i-1的那個index的值會是最大的, 第二個重點是 while迴圈會一直跟現在的index i暫存成的key比較，所以成功時就把j+1的位換成被比較的值和其index 如果失敗 則j+1就是原本key和其index的落腳處
    for (int i = 1; i < n; ++i) {
        int key = arr[i];
        int keyIndex = index[i];
        int j = i - 1; // 
        while (j >= 0 && arr[j] > key) {//從左比到現在的key 有種n階梯比較的概念 
            arr[j + 1] = arr[j];
            index[j + 1] = index[j];
            j = j - 1;
        }
        arr[j + 1] = key; //swap
        index[j + 1] = keyIndex;
    }
}

int main() {
    // 初始化数据
    int values[] = {34, 0, 23, 32, 5, 62, 0, };
    const int size = sizeof(values) / sizeof(values[0]);
    int index[size];

    // 初始化索引数组
    for (int i = 0; i < size; ++i) {
        index[i] = i;
    }

    // 使用插入排序对数组进行排序，同时维护索引
    insertionSort(values, index, size);

    // 输出排序后的结果和原始索引
    std::cout << "Sorted values and their original indices:" << std::endl;
    for (int i = 0; i < size; ++i) {
        std::cout << "Value: " << values[i] << ", Original index: " << index[i] << std::endl;
    }

    return 0;
}