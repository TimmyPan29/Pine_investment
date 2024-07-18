#include "Bos.mqh"
#include "Writetotxt.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+

input int      period   =359; 
input int      datasize =100000;


int OnInit() {
    
    //+----------initiation---------+//
    Helper helper;
    int      starti ;
    Fetcher fc ;
    BOS Bosarr[1440] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    
    fc.Setarrsize(datasize);
    //fc.GetRawData(_Symbol, datasize);
    fc.Getprice(_Symbol, datasize);
    fc.Getdate (_Symbol, datasize);
    Rawdatagroup rd ;
    Print("EA has been initialized.");
    //Print("Starti: ", starti);
    //Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    fc.Printdata();
    //+----------Put Data end---------+//
    
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    
    for (int i=0; i<(period<<2); ++i){
        if (i+1<91) starti = datasize-1000*(i+1);
        else starti = 0 ;
        fc.RenewQuo_Rm(i+1, helper);
        Bosarr[i] = BOS(i+1);
        rd = fc.GetRaw();
        BOSJudge(Bosarr[i], datasize, rd, starti, helper);
    }
    double tempd  ;
    double tempu  ;
    double temp0X ;
    double tempXF ;
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].comparecode0F,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu, temp0X, tempXF);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu, temp0X, tempXF);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu, temp0X, tempXF);
            }
        }
        tempd = 0;
        tempu = 0;
    }
    string symbolname = _Symbol ;
    TriWrite(symbolname, Tri);
    EventSetTimer(60);
    return(INIT_SUCCEEDED);

}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Print a message to indicate the EA has been deinitialized
    Print("EA has been deinitialized.");
    EventKillTimer() ;
    // Add your deinitialization code here
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // This function is called on every new tick
    // Add your tick processing code here
    
    // Example: Print the current Bid price
    //double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    //Print("Current Bid price: ", bid,TimeCurrent());
    
}
void OnTimer(){
    //+----------initiation---------+//
    Print("Timer START!");
    Helper helper;
    int      starti ;
    Fetcher fc ;
    BOS Bosarr[1440] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    fc.Setarrsize(datasize);
    //fc.GetRawData(_Symbol, datasize);
    fc.Getprice(_Symbol, datasize);
    fc.Getdate (_Symbol, datasize);
    Rawdatagroup rd ;
    Print("EA has been initialized.");
    //Print("Starti: ", starti);
    //Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    fc.Printdata();
    //+----------Put Data end---------+//
    
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    
    for (int i=0; i<(period<<2); ++i){
        if (i+1<91) starti = datasize-1000*(i+1);
        else starti = 0 ;
        fc.RenewQuo_Rm(i+1, helper);
        Bosarr[i] = BOS(i+1);
        rd = fc.GetRaw();
        BOSJudge(Bosarr[i], datasize, rd, starti, helper);
    }
    double tempd  ;
    double tempu  ;
    double temp0X ;
    double tempXF ;
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].comparecode0F,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu, temp0X, tempXF);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu, temp0X, tempXF);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu, temp0X, tempXF);
            }
        }
        tempd = 0;
        tempu = 0;
    }
    string symbolname = _Symbol ;
    TriWrite(symbolname, Tri);

}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here