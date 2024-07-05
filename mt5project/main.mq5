#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb           = __TIME00_00;
input int      maxperiod    = 360   ;

int OnInit() {
    Helper helper;
    int    tint ;
    Timebase tb_temp = tb;
    tint = helper.Inputtimebase(tb);
    Print("Exchange Time initiation:",tint,"hr","\nyou choose: ",helper.Inputtimetostring(tb));
    Print("maxperiod: ", maxperiod);
    Print("EA has been initialized.");
    Fetcher Rawdata ;
    Rawdata.Setarrsize(maxperiod) ;
    Rawdata.Getprice(__)
    
   
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
    Print("Current Bid price: ", bid);
}

//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here