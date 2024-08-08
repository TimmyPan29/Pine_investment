#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
#include "Helper.mqh"
struct RawCandles{
   double      rawprices[];
   double      rawopen[];
   double      rawhigh[];
   double      rawlow[];
   datetime    datadate[];
   int         dataQuo[PERIODX16];
   int         head;
   int         neck;
   int         barrenew;
};
class Fetcher{
private:
    RawCandles Vec_rawdata;
public:
    void Getprice(string symbol, int size);
    void Getopen(string symbol, int size);
    void Gethigh(string symbol, int size);
    void Getlow(string symbol, int size);
    void Getdate (string symbol, int size);
    //void GetRawData(string symbol, int size);
    // int  Searchdateidx(int tint, int starti);
    void Printdata() const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
    RawCandles GetRaw();
    void RenewQuo_Rm(int htfint, Helper& helper);
    bool RenewRawdata(int size);
    Fetcher(int size){
        ArrayResize(Vec_rawdata.rawprices, size);
        ArrayResize(Vec_rawdata.datadate, size);
        ArrayResize(Vec_rawdata.rawopen, size);
        ArrayResize(Vec_rawdata.rawhigh, size);
        ArrayResize(Vec_rawdata.rawlow, size);
        head = size;
        neck = size-1;
        barrenew = 1;
    }
};
bool Fetcher::RenewRawdata(string symbol, int size){   
    matrix matrix_rates; 
    matrix_rates.CopyRates(symbol, PERIOD_M1, COPY_RATES_OHLCT, 1, 1);
    if(matrix_rates[3][0]!=Vec_rawdata.rawprices[head]){
        head = (size+barrenew)%size ;
        neck = (size+barrenew-1)%size ;
        ++barrenew ;
        Vec_rawdata.rawprices[head] = matrix_rates[3][0];
        Vec_rawdata.rawhigh[head]   = matrix_rates[1][0];
        Vec_rawdata.rawlow[head]    = matrix_rates[2][0];
        Vec_rawdata.rawopen[head]   = matrix_rates[0][0];
        Vec_rawdata.datadate[head]  = matrix_rates[4][0];
        return true;
    }
    else false;
}
void Fetcher::Getprice(string symbol, int size){
    int copiedPrices = CopyClose(symbol, PERIOD_M1, 0 , size, Vec_rawdata.rawprices);
        if (copiedPrices < size) {
            Print("Error fetching prices, only fetched ", copiedPrices, " prices.");
        }
}
void Fetcher::Gethigh(string symbol, int size){
    int copiedHigh = CopyHigh(symbol, PERIOD_M1, 0 , size, Vec_rawdata.rawhigh);
        if (copiedHigh < size) {
            Print("Error fetching High, only fetched ", copiedHigh, " High.");
        }
}
void Fetcher::Getlow(string symbol, int size){
    int copiedLow = CopyLow(symbol, PERIOD_M1, 0 , size, Vec_rawdata.rawlow);
        if (copiedLow < size) {
            Print("Error fetching Low, only fetched ", copiedLow, " Low.");
        }
}
void Fetcher::Getopen(string symbol, int size){
    int copiedOpen = CopyOpen(symbol, PERIOD_M1, 0 , size, Vec_rawdata.rawopen);
        if (copiedOpen < size) {
            Print("Error fetching Open, only fetched ", copiedOpen, " Open.");
        }
}
void Fetcher::Getdate(string symbol, int size){
    int copiedTimes = CopyTime(symbol, PERIOD_M1, 0 , size, Vec_rawdata.datadate);
        if (copiedTimes < size) {
            Print("Error fetching times, only fetched ", copiedTimes, " times.");
        }
}
void Fetcher::Printdata()const{
    for (int i=0; i<ArraySize(Vec_rawdata.rawprices); i++){
        string timeStr = TimeToString(Vec_rawdata.datadate[i], TIME_DATE | TIME_MINUTES);
        Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.rawprices[i]);
    }
}
datetime Fetcher::Getdateinfo(int idx){
    return Vec_rawdata.datadate[idx];
}
double Fetcher::Getpriceinfo(int idx){
    return Vec_rawdata.rawprices[idx];
}
RawCandles Fetcher::GetRaw(){
    return Vec_rawdata;
}
void Fetcher::RenewQuo_Rm(int htfint, Helper& helper){
    for (int i=0; i<PERIODX4; ++i){
        Vec_rawdata.dataQuo[i] = helper.GetQuo(i+1, htfint);
        //Vec_rawdata.dataRm[i]  = helper.GetRm(i+1, htfint);
    }
}
bool Bull(const RawCandles& candle, int k){
    bool b;
    b = (candle.rawprices[k] - candle.rawopen[k] > 0)? true : false ;
    return b ;
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful //

// void Fetcher::GetRawData(string symbol, int size){
//     int cnt  = 1;
//     int cnti = 1 ; //bar from iTime iClose
//     int barrm ;
//     datetime temptime;
//     double   tempprice;
//     Vec_rawdata.datadate[0] = iTime(symbol, PERIOD_M1, 0);
//     Vec_rawdata.rawprices[0]= iClose(symbol, PERIOD_M1, 0);
//     for(int i=0; i<size; ++i){
//         if((iTime(symbol, PERIOD_M1, cnti-1) - iTime(symbol, PERIOD_M1, cnti)) != 60){
//             temptime = iTime(symbol, PERIOD_M1, cnti-1) ;
//             tempprice= iOpen(symbol, PERIOD_M1, cnti-1) ;
//             barrm = ((temptime - iTime(symbol, PERIOD_M1, cnti))%86400)/60-1;
//             //Print("barrm= ", barrm);
//             while(cnt<=barrm && i<size-1){
//                 Vec_rawdata.datadate[i] = temptime-60*cnt;
//                 Vec_rawdata.rawprices[i]= tempprice;
//                 ++i  ;
//                 ++cnt;
//             }
//             cnt = 1;
//         }
//         Vec_rawdata.datadate[i] = iTime(symbol, PERIOD_M1, cnti);
//         Vec_rawdata.rawprices[i]= iClose(symbol, PERIOD_M1, cnti);
//         ++cnti ;
//     }
// }

// int Fetcher::Searchdateidx(int tint, int size) {
//     int i = size-1;
//     while (true) {
//         int timeint = (Vec_rawdata.datadate[i]%86400)/60;
//         if(timeint == tint) {
//             return i;
//         }
//         --i;
//     }
// }