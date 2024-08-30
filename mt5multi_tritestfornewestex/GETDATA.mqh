#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
#include "Helper.mqh"
struct RawCandles{
    matrix      mat_rates; 
    int         dataQuo[PERIODX16];
};
class Fetcher{
public:
    RawCandles Vec_rawdata;
public:
    void GetOHLCT(string symbol, int count);
    void Printdata(int number)const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
    RawCandles GetRaw();
    void RenewQuo_Rm(int htfint, Helper& helper, int quooffset);
    // Fetcher(int count){
    //     ArrayResize(Vec_rawdata.rawprices, count);
    //     ArrayResize(Vec_rawdata.datadate, count);
    //     ArrayResize(Vec_rawdata.rawopen, count);
    //     ArrayResize(Vec_rawdata.rawhigh, count);
    //     ArrayResize(Vec_rawdata.rawlow, count);
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
bool Bull(const RawCandles& candle, int k){ //OHLCT
    bool b;
    b = (candle.mat_rates[3][k] - candle.mat_rates[0][k] > 0)? true : false ;
    return b ;
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful //
