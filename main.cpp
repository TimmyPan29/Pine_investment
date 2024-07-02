//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
Helper helper;
input Timebase tb   = Time00_00;
int            tint = helper.inputtimebase(tb)
int OnInit() {
    int timezone = helper.Extimeoffset();
    // 调用自定义的OnStart函数
    OnStart();

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
void OnStart() {
    // This function is called once when the EA starts
    // Add your startup code here
    
    // Example: Print a startup message
    Print("OnStart function has been called.");
}

//+------------------------------------------------------------------+
//| Custom functions                                                 |
//+------------------------------------------------------------------+

// Add your custom functions here