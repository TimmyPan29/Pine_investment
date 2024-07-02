#include <iostream>

int main() {
    int x = 5;      // 定义一个整数变量
    int y = 10;     // 定义另一个整数变量
    int& ref = x;   // 初始化引用，引用变量 x

    std::cout << "ref (initial): " << ref << std::endl; // 输出初始值

    ref = y;        // 修改引用的值，实际是将 x 的值改为 y 的值
    std::cout << "x: " << x << std::endl; // x 的值现在是 y 的值
    std::cout << "ref: " << ref << std::endl; // ref 仍然引用 x，所以 ref 的值是 x 的值

    // ref = &y;    // 错误：不能更改引用以指向其他变量

    return 0;
}