#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb   = __TIME00_00;


int OnInit() {
    Helper helper;
    int    tint ;
    Timebase tb_temp = tb;
    tint = helper.Inputtimebase(tb);
    Print("Exchange Time initiation:",tint,"hr","\nyou choose: ",helper.Inputtimetostring(tb));
    // 调用自定义的OnStart函数

    // Print a message to indicate the EA has been initialized
    Print("EA has been initialized.");
    
    // Add your initialization code here
    
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