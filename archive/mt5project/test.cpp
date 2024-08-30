#include <cstdio>

// 函数声明
void Insertalg(double arr[], int index[], int size);
void Boolcheck(double arr[], bool bl[], int size);
int main(){
    double arr[8] = {4.2323, 6.151343, 6.151343, 5, 6.151343, 7, 8,1};
    int idx[8] = {1, 2, 3, 4, 5, 6, 7,8};
    bool bl[8] ;
    Insertalg(arr, idx, 8);
    Boolcheck(arr,bl,8);
    for (int i = 0; i < 8; ++i){
        printf("value = %.6f, idx = %d\n", arr[i], idx[i]);
    }
    for (int i = 0; i < 8; ++i){
        printf("value = %.6f, bool = %d\n", arr[i], bl[i]);
    }
    return 0;
}

// 插入排序算法函数
void Insertalg(double arr[], int index[], int size){
    for (int i = 1; i < size; ++i) {
        double key = arr[i];
        int keyIndex = index[i];
        int j = i - 1;
        
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            index[j + 1] = index[j];
            j = j - 1;
        }
        arr[j + 1] = key;
        index[j + 1] = keyIndex;
    }
}
void Boolcheck(double arr[],bool bl[], int size){
    bl[0] = false ;
    for (int i=1; i<size; ++i){
        bl[i] = (arr[i]==arr[i-1]);
    }
}