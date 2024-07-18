#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
#include "Helper.mqh"
struct Rawdatagroup{
   double      rawprices[];
   datetime    datadate[];
   int         dataQuo     [__DAYMIN];
   int         dataRm      [__DAYMIN];  
};
class Fetcher{
private:
    Rawdatagroup Vec_rawdata;
public:
    void Setarrsize(int count);
    void Getprice(string symbol, int count);
    void Getdate (string symbol, int count);
    //void GetRawData(string symbol, int size);
    // int  Searchdateidx(int tint, int starti);
    void Printdata() const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
    Rawdatagroup GetRaw();
    void RenewQuo_Rm(int htfint, Helper& helper);
};

void Fetcher::Setarrsize(int count){
    ArrayResize(Vec_rawdata.rawprices, count);
    ArrayResize(Vec_rawdata.datadate, count);
}
void Fetcher::Getprice(string symbol, int count){
    int copiedPrices = CopyClose(symbol, PERIOD_M1, 0 , count, Vec_rawdata.rawprices);
        if (copiedPrices < count) {
            Print("Error fetching prices, only fetched ", copiedPrices, " prices.");
        }
}
void Fetcher::Getdate(string symbol, int count){
    int copiedTimes = CopyTime(symbol, PERIOD_M1, 0 , count, Vec_rawdata.datadate);
        if (copiedTimes < count) {
            Print("Error fetching times, only fetched ", copiedTimes, " times.");
        }
}
// void Fetcher::GetRawData(string symbol, int size){
//     int cnt  = 1;
//     int cnti = 1 ; //bar from iTime iClose
//     int barrm ;
//     datetime temptime;
//     double   tempprice;
//     Vec_rawdata.datadate[0] = iTime(symbol, PERIOD_M1, 0);
//     Vec_rawdata.rawprices[0]= iClose(symbol, PERIOD_M1, 0);
//     for(int i=1; i<size; ++i){
//         if((iTime(symbol, PERIOD_M1, cnti-1) - iTime(symbol, PERIOD_M1, cnti)) != 60){
//             temptime = iTime(symbol, PERIOD_M1, cnti-1) ;
//             tempprice= iOpen(symbol, PERIOD_M1, cnti-1) ;
//             barrm = ((temptime - iTime(symbol, PERIOD_M1, cnti))%3600)/60-1;
//             while(cnt<=barrm){
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

void Fetcher::Printdata()const{
    for (int i=0; i<ArraySize(Vec_rawdata.rawprices); i++){
        string timeStr = TimeToString(Vec_rawdata.datadate[i], TIME_DATE | TIME_MINUTES);
        //Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.rawprices[i]);
    }
}
// int Fetcher::Searchdateidx(int tint, int starti) {
//     int i = starti;
//     while (true) {
//         int timeint = (Vec_rawdata.datadate[i]%86400)/60;
//         if(timeint == tint) return i;
//         ++i;
//     }
// }
datetime Fetcher::Getdateinfo(int idx){
   return Vec_rawdata.datadate[idx];
}
double Fetcher::Getpriceinfo(int idx){
   return Vec_rawdata.rawprices[idx];
}
Rawdatagroup Fetcher::GetRaw(){
   return Vec_rawdata;
} 
void Fetcher::RenewQuo_Rm(int htfint, Helper& helper){
    for (int i=0; i<__DAYMIN; ++i){
        Vec_rawdata.dataQuo[i] = helper.GetQuo(i+1, htfint);
        Vec_rawdata.dataRm[i]  = helper.GetRm(i+1, htfint);
    }
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful //



