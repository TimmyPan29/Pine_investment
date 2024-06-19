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