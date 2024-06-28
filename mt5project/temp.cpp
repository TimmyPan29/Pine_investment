#ifndef MYCLASS_H
#define MYCLASS_H

class MyClass {
public:
    MyClass(int value);  // 构造函数声明
    void setValue(int value);  // 成员函数声明
    int getValue() const;  // 成员函数声明

private:
    int value_;  // 成员变量声明
};

#endif // MYCLASS_H

#include "MyClass.h"

// 构造函数定义
MyClass::MyClass(int value) : value_(value) {
}

// 成员函数定义
void MyClass::setValue(int value) {
    value_ = value;
}

int MyClass::getValue() const {
    return value_;
}



class PriceFetcher {
public:
    double prices[]; // 数组存储价格

    // 获取指定数量的每分钟价格
    void FetchPrices(string symbol, int count) {
        // 重新初始化数组大小
        ArrayResize(prices, count);

        // 获取价格数据
        int copied = CopyClose(symbol, PERIOD_M1, 0, count, prices);
        if (copied < count) {
            Print("Error fetching prices, only fetched ", copied, " prices.");
        }
    }

    // 打印价格数据
    void PrintPrices() {
        for (int i = 0; i < ArraySize(prices); i++) {
            Print("Price at index ", i, ": ", prices[i]);
        }
    }
};