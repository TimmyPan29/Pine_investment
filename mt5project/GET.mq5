#include "GETDATA.mqh"
PriceFetcher::PriceFetcher(int value)//未完成

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

