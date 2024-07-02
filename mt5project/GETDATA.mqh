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
    int  Searchdateidx(string tstr);
    void Printdata() const;
};

#endif

