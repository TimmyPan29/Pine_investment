#include "Bos.mqh"
#include "WriteTri.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Exchange ex           = OANDA ; 
input int      period       = 359; 
input int      datasize     = 100000;

int OnInit() {
    
    //+----------initiation---------+//
    SymbolSet Symbolset    ;
    Fetcher fc(datasize)           ;
    RawCandles rd          ;
    FVG       fvgarr[1436]     ;
    Symbolset.InitSymbol(ex,Symbolset);
    Helper helper          ;
    BOS Bosarr[1436] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    int      starti        ;
    string symboltemp      ;
    string sectornametemp  ;
    printf("START!");
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    symboltemp = Symbolset.Bullion[0] ;
    sectornametemp = Symbolset.Sectorname[0];
    fc.Getprice(symboltemp, datasize);
    fc.Getopen (symboltemp, datasize);
    fc.Gethigh(symboltemp, datasize);
    fc.Getlow(symboltemp, datasize);
    fc.Getdate (symboltemp, datasize);
    
    Print(AccountInfoString(ACCOUNT_COMPANY)+", ",AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symboltemp);
    Print("EA has been initialized.");
    //Print("Starti: ", starti);
    //Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    //fc.Printdata();
    //+----------Put Data end---------+//
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    int gain ;
    for (int i=0; i<(period<<2); ++i){
        if (i+1<91) starti = datasize-1000*(i+1);
        else starti = 0 ;
        fc.RenewQuo_Rm(i+1, helper);
        Bosarr[i] = BOS(i+1);
        fvgarr[i] = FVG(i+1);
        rd   = fc.GetRaw();
        gain = BOSJudge(Bosarr[i], datasize, rd, starti, helper, fvgarr[i]);
    }
    for (int i=0; i<(period<<2); ++i){
        fvgarr[i].Putefffvg(rd) ;
    }
    double tempd ;
    double tempu ;
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu);
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
    FvgWrite(symboltemp, fvgarr[0], sectornametemp);

    return(INIT_SUCCEEDED);
    EventSetTimer(60);
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
    SymbolSet Symbolset    ;
    Fetcher fc(datasize)           ;
    RawCandles rd          ;
    FVG       fvgarr[1436]     ;
    Symbolset.InitSymbol(ex,Symbolset);
    Helper helper          ;
    BOS Bosarr[1436] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    int      starti        ;
    string symboltemp      ;
    string sectornametemp  ;
    
    
    symboltemp = Symbolset.Bullion[0] ;
    sectornametemp = Symbolset.Sectorname[0];
    fc.Getprice(symboltemp, datasize);
    fc.Getopen (symboltemp, datasize);
    fc.Gethigh(symboltemp, datasize);
    fc.Getlow(symboltemp, datasize);
    fc.Getdate (symboltemp, datasize);
    
    Print(AccountInfoString(ACCOUNT_COMPANY)+", ",AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symboltemp);
    Print("EA has been initialized.");
    //Print("Starti: ", starti);
    //Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    //fc.Printdata();
    //+----------Put Data end---------+//
    
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    int gain ;
    for (int i=0; i<(period<<2); ++i){
        if (i+1<91) starti = datasize-1000*(i+1);
        else starti = 0 ;
        fc.RenewQuo_Rm(i+1, helper);
        Bosarr[i] = BOS(i+1);
        fvgarr[i] = FVG(i+1);
        rd   = fc.GetRaw();
        gain = BOSJudge(Bosarr[i], datasize, rd, starti, helper, fvgarr[i]);
    }
    for (int i=0; i<(period<<2); ++i){
        fvgarr[i].Putefffvg(rd) ;
    }
    double tempd ;
    double tempu ;
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu);
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
    FvgWrite(symboltemp, fvgarr[0], sectornametemp);

}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here