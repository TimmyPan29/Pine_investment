#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb       = __TIME00_00;
input int      period   =360; 
input int      datasize =100000;


int OnInit() {
    //+----------initiation---------+//
    Helper helper;
    int      tint ;
    int      starti ;
    Timebase tb_temp       = tb;
    tint                   = helper.Inputtimebase(tb)*3600; //second
    Fetcher fc ;
    BOS Bosarr[1440] ;
 
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
    
    for (int i=0; i<ArraySize(Bosarr); ++i){
        Bosarr[i] = BOS(i+1);
        BOSJudge(Bosarr[i], datasize, rd, starti);
    }
    Print("BOS[1438].baraday= ", Bosarr[1438].baraday);
    Print("BOS[0].htfint= ", Bosarr[0].htfint);
    Print("rd.rawprices[37]= ", rd.rawprices[37]);
    Print("Bosarr[37].sbu= ", Bosarr[37].sbu);
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Print a message to indicate the EA has been deinitialized
    Print("EA has been deinitialized.");
    
    // Add your deinitialization code here
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // This function is called on every new tick
    // Add your tick processing code here
    
    // Example: Print the current Bid price
    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    Print("Current Bid price: ", bid,TimeCurrent());
    Sleep(10000);
}

//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

>>>>>>> a518d9b06617ae2412111e10598e354bd1ff88fb
// Add your custom functions here