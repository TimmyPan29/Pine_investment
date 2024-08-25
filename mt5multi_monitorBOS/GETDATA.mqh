#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
#include "Helper.mqh"
struct RawCandles{
    matrix      mat_rates; 
    int         dataQuo[PERIODX4];
};
class Fetcher{
public:
    RawCandles Vec_rawdata;
public:
    //void GetRawData(string symbol, int size);
    // int  Searchdateidx(int tint, int starti);
    void GetOHLCT(string symbol, int count);
    void Printdata(int number)const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
    RawCandles GetRaw();
    void RenewQuo_Rm(int htfint, Helper& helper, int quooffset);
    // Fetcher(int count){

    // }
};
void Fetcher::GetOHLCT(string symbol, int count){
    if(Vec_rawdata.mat_rates.CopyRates(symbol, PERIOD_M1, COPY_RATES_OHLCT, 0, count)) printf("getOHLCT success") ;
    else printf("getOHLCT fail") ;
}
void Fetcher::Printdata(int number)const{
    int size = Vec_rawdata.mat_rates.Cols() ;
    for (int i=size-number; i<size; i++){
        string timeStr = TimeToString(Vec_rawdata.mat_rates[4][i], TIME_DATE | TIME_MINUTES);
        Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.mat_rates[3][i]);
    }
}
datetime Fetcher::Getdateinfo(int idx){
   return Vec_rawdata.mat_rates[4][idx];
}
double Fetcher::Getpriceinfo(int idx){
   return Vec_rawdata.mat_rates[3][idx];
}
RawCandles Fetcher::GetRaw(){
   return Vec_rawdata;
} 
void Fetcher::RenewQuo_Rm(int htfint, Helper& helper, int quooffset){
    for (int i=0; i<PERIODX4; ++i){
        Vec_rawdata.dataQuo[i] = helper.GetQuo(i+1, htfint, quooffset);
        //Vec_rawdata.dataRm[i]  = helper.GetRm(i+1, htfint);
    }
}
bool Bull(const RawCandles& candle, int k){
    bool b;
    b = (candle.mat_rates[3][k] - candle.mat_rates[0][k] > 0)? true : false ; // Close-Open
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