#include "Bos.mqh"
#include "WriteTri.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb           = __TIME00_00;
input Exchange ex           = OANDA ; 
input int      period       = 359; 
input int      datasize     = 100000;
SymbolSet Symbolset                 ;
FVG       fvgtemp;
int OnInit() {
    EventSetTimer(300);
    //+----------initiation---------+//
    Symbolset.InitSymbol(ex,Symbolset);
    Helper helper;
    int      tint ;
    int      starti ;
    tint                   = helper.Inputtimebase(tb); //
    string symboltemp ;
    string sectornametemp ;
    Fetcher fc ;
    BOS Bosarr[1436] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    symboltemp = Symbolset.Commodities[0] ;
    sectornametemp = Symbolset.Sectorname[1];
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    fc.Setarrsize(datasize);
    fc.GetRawData(symboltemp, datasize);
    RawCandles rd   = fc.GetRaw();
    starti          = fc.Searchdateidx(tint, datasize);
    Print("Exchange Time initiation: ",tint,"min","\nyou choose: ",helper.Inputtimetostring(tb));
    Print("EA has been initialized.");
    Print("Starti: ", starti);
    Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    //fc.Printdata();
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
                Tri[0].TriCode(Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j);
            }
            else if(i!=0 && j==0){
                Tri[i].TriCode(Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j);
            }
            else{
                Tri[i].TriCode(Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j);
            }
        }
    }
    int z = 685 ;
    string s_sbudate = TimeToString(Bosarr[z-1].sbu_t,TIME_DATE|TIME_MINUTES); 
    string s_sbddate = TimeToString(Bosarr[z-1].sbd_t,TIME_DATE|TIME_MINUTES);  
    printf("Period %d.sbu= %.6f\t Period %d.sbd= %.6f", z, Bosarr[z-1].sbu, z, Bosarr[z-1].sbd);
    printf("Period %d.sbu_t= %s\t Period %d.sbd_t= %s", z, s_sbudate, z, s_sbddate);
    Print("diff zone  ", helper.Extime());
    TriWrite(symboltemp, Tri, sectornametemp);



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