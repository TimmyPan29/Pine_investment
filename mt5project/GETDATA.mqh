#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__

struct Rawdatagroup{
   double      rawprices[];
   datetime    datadate[];
};
class Fetcher{
private:
    Rawdatagroup Vec_rawdata;
public:
    void Setarrsize(int count);
    // void Getprice(string symbol, int count);
    // void Getdate (string symbol, int count);
    void GetRawData(string symbol, int size, int offset, int timeoffset);
    int  Searchdateidx(int tint, int size);
    void Printdata() const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
    Rawdatagroup GetRaw();
};

void Fetcher::Setarrsize(int count){
    ArrayResize(Vec_rawdata.rawprices, count);
    ArrayResize(Vec_rawdata.datadate, count);
}
void Fetcher::GetRawData(string symbol, int size, int offset, int timeoffset){
    int cnt ;
    int cnti = 0 ;
    datetime temptime;
    for(int i=0; i<size; ++i){
        Vec_rawdata.datadate[i] = iTime(symbol, PERIOD_M1, cnti);
        Vec_rawdata.rawprices[i]= iClose(symbol, PERIOD_M1, cnti);
        if(((Vec_rawdata.datadate[i]%86400)/60) == timeoffset){
            temptime    = Vec_rawdata.datadate[i];
            cnt         = 1;
            while(cnt<=offset){
                ++i;
                if(Vec_rawdata.datadate[cnt+1]-temptime < 86400){
                    Vec_rawdata.datadate[i]  = temptime-60*cnt;
                    Vec_rawdata.rawprices[i] = iOpen(symbol, PERIOD_M1, cnti);
                }
                else{
                    Vec_rawdata.datadate[i]  = Vec_rawdata.datadate[cnt+1]+60;
                    Vec_rawdata.rawprices[i] = iOpen(symbol, PERIOD_M1, cnti);
                }
                ++cnt;
            }
        }
        ++cnti ;

    }
    

}
// void Fetcher::Getprice(string symbol, int count){
//     int copiedPrices = CopyClose(symbol, PERIOD_M1, 0 , count, Vec_rawdata.rawprices);
//         if (copiedPrices < count) {
//             Print("Error fetching prices, only fetched ", copiedPrices, " prices.");
//         }
// }
// void Fetcher::Getdate(string symbol, int count){
//     int copiedTimes = CopyTime(symbol, PERIOD_M1, 0 , count, Vec_rawdata.datadate);
//         if (copiedTimes < count) {
//             Print("Error fetching times, only fetched ", copiedTimes, " times.");
//         }
// }
void Fetcher::Printdata()const{
    for (int i=0; i<ArraySize(Vec_rawdata.rawprices); i++){
        string timeStr = TimeToString(Vec_rawdata.datadate[i], TIME_DATE | TIME_MINUTES);
        Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.rawprices[i]);
    }
}
int Fetcher::Searchdateidx(int tint, int size) {
    int i = size-1;
    while (true) {
        int timeint = (Vec_rawdata.datadate[i]%86400)/60;
        if(timeint == tint) {
            return i;
        }
        --i;
    }
}
datetime Fetcher::Getdateinfo(int idx){
   return Vec_rawdata.datadate[idx];
}
double Fetcher::Getpriceinfo(int idx){
   return Vec_rawdata.rawprices[idx];
}
Rawdatagroup Fetcher::GetRaw(){
   return Vec_rawdata;
} 
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful //
#endif

