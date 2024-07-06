#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb       = __TIME00_00;
input int      period   =359; 
input int      datasize =100000;


int OnInit() {
    EventSetTimer(5);
    //+----------initiation---------+//
    Helper helper;
    int      tint ;
    int      starti ;
    Timebase tb_temp       = tb;
    tint                   = helper.Inputtimebase(tb)*3600; //second
    Fetcher fc ;
    BOS Bosarr[1436] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[1436] ;
    
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    
    fc.Setarrsize(datasize);
    fc.Getprice(_Symbol, datasize);
    fc.Getdate(_Symbol, datasize);
    Rawdatagroup rd = fc.GetRaw();
    starti          = fc.Searchdateidx(tint);
    Print("Exchange Time initiation:",tint/60,"min","\nyou choose: ",helper.Inputtimetostring(tb));
    Print("EA has been initialized.");
    Print("Starti: ", starti);
    Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    //+----------Put Data end---------+//
    
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    
    for (int i=0; i<(period<<2); ++i){
        Bosarr[i] = BOS(i+1);
        BOSJudge(Bosarr[i], datasize, rd, starti);
    }
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j);
            }
        }
    }

    Print("BOS[1435].baraday= ", Bosarr[1435].baraday);
    //Print("BOS[0].htfint= ", Bosarr[0].htfint);
    //Print("rd.rawprices[37]= ", rd.rawprices[37]);
    Print("Bosarr[37].sbu= ", Bosarr[37].sbu);
    PrintFormat("Tri[333].comparecode= %x", Tri[333].comparecode[333]);
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
    Print("Hi");

}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here