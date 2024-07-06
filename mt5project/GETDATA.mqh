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
    void Getprice(string symbol, int count);
    void Getdate (string symbol, int count);
    int  Searchdateidx(int tint);
    void Printdata() const;
    datetime Getdateinfo(int idx);
    double Getpriceinfo(int idx);
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
void Fetcher::Printdata()const{
    for (int i=0; i<ArraySize(Vec_rawdata.rawprices); i++){
        string timeStr = TimeToString(Vec_rawdata.datadate[i], TIME_DATE | TIME_MINUTES);
        Print("date in idx: ", i, ":", timeStr, "\n", "prices in idx ", i, ":", Vec_rawdata.rawprices[i]);
    }
}
int Fetcher::Searchdateidx(int tint) {
    int i = 0;
    while (true) {
        int timeint = (Vec_rawdata.datadate[i]%86400);
        if(timeint == tint) {
            return i;
        }
        i++;
    }
}
datetime Fetcher::Getdateinfo(int idx){
   return Vec_rawdata.datadate[idx];
}
double Fetcher::Getpriceinfo(int idx){
   return Vec_rawdata.rawprices[idx];
}      
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful //
#endif

