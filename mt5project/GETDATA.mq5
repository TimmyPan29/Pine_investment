#include "GETDATA.mqh"
void Fetcher::void Setarrsize(int count){
    ArrayResize(Vec_rawdata.rawprices, count);
    ArrayResize(Vec_rawdata.datadate, count);
}
void Fetcher::Getprice(string symbol, int count){
    int copiedPrices = CopyClose(symbol, PERIOD_M1, 0 , count, Vec_rawdata.rawprices);
        if (copiedPrices < count) {
            Print("Error fetching prices, only fetched ", copiedPrices, " prices.");
}
void Fetcher::Getdate(string symbol, int count){
    int copiedTimes = CopyTime(symbol, PERIOD_M1, 0 , count, Vec_rawdata.datadate);
        if (copiedTimes < count) {
            Print("Error fetching times, only fetched ", copiedTimes, " times.");
}
void Fetcher::Printdata(){
    for (int i=0; i<ArraySize(Vec_rawdata.rawprices); i++){
        string timeStr = TimeToString(Vec_rawdata.datadate[i], TIME_DATE | TIME_MINUTES);
        Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.rawprices[i])
    }
}
int Fetcher::Searchdateidx(){
    bool flag = true;
    int  i    = 0;
    while (flag) {
        string timestr = TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES);
        if(timestr == "00:00")
            flag = false;
            break;
        i++
    }
    return i;
        
}