#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb       = __TIME00_00;
input int      period   =360; 
input int      datasize =100000;

int OnInit() {
    Helper helper;
    int    tint ;
    int    temp ;
    Timebase tb_temp = tb;
    tint = helper.Inputtimebase(tb)*60;
    Print("Exchange Time initiation:",tint,"min","\nyou choose: ",helper.Inputtimetostring(tb));
    Print("EA has been initialized.");
    Fetcher fc ;
    fc.Setarrsize(datasize);
    fc.Getprice(_Symbol, datasize);
    fc.Getdate(_Symbol, datasize);
    temp = fc.Searchdateidx(tint);
    Print("Tint: ", temp);
    Print("price: ",fc.Getpriceinfo(temp),"date: ",fc.Getdateinfo(temp));
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

// Add your custom functions here