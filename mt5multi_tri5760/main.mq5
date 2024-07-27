#include "Bos.mqh"
#include "WriteTri.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Exchange ex            = OANDA ;
input Treasure tr1           = Forex;
input int      symbol_n1     = 0     ;
input Treasure tr2           = Forex;
input int      symbol_n2     = 1     ;
input Treasure tr3           = Forex;
input int      symbol_n3     = 2     ;
input Treasure tr4           = Forex;
input int      symbol_n4     = 3    ;
input Treasure tr5           = Forex;
input int      symbol_n5     = 4     ;
input Treasure tr6           = Forex;
input int      symbol_n6     = 5     ;
input Treasure tr7           = Forex;
input int      symbol_n7     = 6     ;
input Treasure tr8           = Forex;
input int      symbol_n8     = 7     ;
input Treasure tr9           = Forex;
input int      symbol_n9     = 8     ;
input Treasure tr10          = Forex;
input int      symbol_n10    = 9     ;

input int      datasize      = 1000000;
input Barchoice bar          = Bar1000;
int OnInit() {

    //+----------initiation---------+//
    int      starti        ;
    SymbolSet Symbolset    ;
    RawCandles rd          ;
    Helper helper          ;
    string symboltemp[10]      ;
    string sectornametemp[10]  ;
    helper.Ext = helper.ChooseEx(ex)        ;
    printf("In initiation");
    
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    
    if(!Symbolset.InitSymbol(ex,Symbolset)){
        printf("WRONG TRADE EXCHANGE ⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄  =>  (ノ▼Д▼)ノ");
        return (INIT_FAILED);
    }
    else{
        sectornametemp[0] = helper.Sectorchooser(tr1, Symbolset);
        sectornametemp[1] = helper.Sectorchooser(tr2, Symbolset);
        sectornametemp[2] = helper.Sectorchooser(tr3, Symbolset);
        sectornametemp[3] = helper.Sectorchooser(tr4, Symbolset);
        sectornametemp[4] = helper.Sectorchooser(tr5, Symbolset);
        sectornametemp[5] = helper.Sectorchooser(tr6, Symbolset);
        sectornametemp[6] = helper.Sectorchooser(tr7, Symbolset);
        sectornametemp[7] = helper.Sectorchooser(tr8, Symbolset);
        sectornametemp[8] = helper.Sectorchooser(tr9, Symbolset);
        sectornametemp[9] = helper.Sectorchooser(tr10, Symbolset);

        symboltemp[0] = helper.Symbolchooser(tr1, Symbolset, symbol_n1);
        symboltemp[1] = helper.Symbolchooser(tr2, Symbolset, symbol_n2);
        symboltemp[2] = helper.Symbolchooser(tr3, Symbolset, symbol_n3);
        symboltemp[3] = helper.Symbolchooser(tr4, Symbolset, symbol_n4);
        symboltemp[4] = helper.Symbolchooser(tr5, Symbolset, symbol_n5);
        symboltemp[5] = helper.Symbolchooser(tr6, Symbolset, symbol_n6);
        symboltemp[6] = helper.Symbolchooser(tr7, Symbolset, symbol_n7);
        symboltemp[7] = helper.Symbolchooser(tr8, Symbolset, symbol_n8);
        symboltemp[8] = helper.Symbolchooser(tr9, Symbolset, symbol_n9);
        symboltemp[9] = helper.Symbolchooser(tr10, Symbolset, symbol_n10);
    }
    for(int k=0; k<10; ++k){
        Fetcher fc(datasize)       ;
        FVG       fvgarr[]         ;
        ArrayResize(fvgarr, PERIODX16, PERIODX16) ;
        BOS Bosarr[PERIODX16]       ;//設一天會卡死 base最多到359 超過360要再想辦法
        Triset Tri[PERIODX4]         ;
        if(sectornametemp[k]==NULL) continue ;
        fc.Getprice(symboltemp[k], datasize);
        fc.Getopen (symboltemp[k], datasize);
        fc.Gethigh(symboltemp[k], datasize);
        fc.Getlow(symboltemp[k], datasize);
        fc.Getdate (symboltemp[k], datasize);
        printf("You choose %s: %s",sectornametemp[k], symboltemp[k]);
        Print(AccountInfoString(ACCOUNT_COMPANY)+", ",AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", Period= ", PERIODX4);
        //+----------Put Data end---------+//
        // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
        // cuz u s still have not initialize the BOS type;
        int barx = helper.Bartoint(bar) ;
        for (int i=0; i<(PERIODX16); ++i){
            if ((i+1)*barx <datasize) starti = (datasize-(i+1)*barx) ;
            else starti = 0 ;
            fc.RenewQuo_Rm(i+1, helper);
            Bosarr[i] = BOS(i+1);
            fvgarr[i] = FVG(i+1);
            rd   = fc.GetRaw();
            BOSJudge(Bosarr[i], datasize, rd, starti, helper, fvgarr[i], i);
        }
        for (int i=0; i<(PERIODX16); ++i){  
            int barsize = fvgarr[i].Getfvgkbarsize() ;
            for(int j=0; j<barsize; ++j){
                fvgarr[i].Putfvg_chlo(rd, j,i+1) ;
            }
            fvgarr[i].Putefffvg() ;
        }
        double tempd  ;
        double tempu  ;
        double temp0X ;
        double tempXF ;
        for (int i=0; i<(PERIODX4); ++i){
            ArrayResize(Tri[i].comparecode,i+1,i+1);
            ArrayResize(Tri[i].comparecode0F,i+1,i+1);
            ArrayResize(Tri[i].u_inside,i+1,i+1);
            ArrayResize(Tri[i].d_inside,i+1,i+1);
            ArrayResize(Tri[i].fvgtype0F,i+1,i+1);
            for(int j=0; j<=i; ++j){
                if(i==0 && j==0){
                    Tri[0]=TriCode(fvgarr[i], Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu, temp0X, tempXF);
                }
                else if(i!=0 && j==0){
                    Tri[i]=TriCode(fvgarr[i], Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu, temp0X, tempXF);
                }
                else{
                    Tri[i]=TriCode(fvgarr[i], Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu, temp0X, tempXF);
                }
            }
            tempd = 0;
            tempu = 0;
        }
        Print("diff zone  ", helper.Extime());
        TriWrite(symboltemp[k], Tri, sectornametemp[k]);
        FvgWrite(symboltemp[k], fvgarr, sectornametemp[k]);
        EventSetTimer(50);
        Print("EA has been initialized, then go into timer event");
    }
    return(INIT_SUCCEEDED) ;
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
    int      starti        ;
    SymbolSet Symbolset    ;
    RawCandles rd          ;
    Helper helper          ;
    string symboltemp[10]      ;
    string sectornametemp[10]  ;
    helper.ChooseEx(ex)        ;
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    Symbolset.InitSymbol(ex,Symbolset);
    sectornametemp[0] = helper.Sectorchooser(tr1, Symbolset);
    sectornametemp[1] = helper.Sectorchooser(tr2, Symbolset);
    sectornametemp[2] = helper.Sectorchooser(tr3, Symbolset);
    sectornametemp[3] = helper.Sectorchooser(tr4, Symbolset);
    sectornametemp[4] = helper.Sectorchooser(tr5, Symbolset);
    sectornametemp[5] = helper.Sectorchooser(tr6, Symbolset);
    sectornametemp[6] = helper.Sectorchooser(tr7, Symbolset);
    sectornametemp[7] = helper.Sectorchooser(tr8, Symbolset);
    sectornametemp[8] = helper.Sectorchooser(tr9, Symbolset);
    sectornametemp[9] = helper.Sectorchooser(tr10, Symbolset);

    symboltemp[0] = helper.Symbolchooser(tr1, Symbolset, symbol_n1);
    symboltemp[1] = helper.Symbolchooser(tr2, Symbolset, symbol_n2);
    symboltemp[2] = helper.Symbolchooser(tr3, Symbolset, symbol_n3);
    symboltemp[3] = helper.Symbolchooser(tr4, Symbolset, symbol_n4);
    symboltemp[4] = helper.Symbolchooser(tr5, Symbolset, symbol_n5);
    symboltemp[5] = helper.Symbolchooser(tr6, Symbolset, symbol_n6);
    symboltemp[6] = helper.Symbolchooser(tr7, Symbolset, symbol_n7);
    symboltemp[7] = helper.Symbolchooser(tr8, Symbolset, symbol_n8);
    symboltemp[8] = helper.Symbolchooser(tr9, Symbolset, symbol_n9);
    symboltemp[9] = helper.Symbolchooser(tr10, Symbolset, symbol_n10);
    for(int k=0; k<10; ++k){
        Fetcher fc(datasize)       ;
        FVG       fvgarr[]         ;
        ArrayResize(fvgarr, PERIODX16, PERIODX16) ;
        BOS Bosarr[PERIODX16]      ;//設一天會卡死 base最多到359 超過360要再想辦法
        Triset Tri[PERIODX4]       ;
        if(sectornametemp[k]==NULL) continue ;
        fc.Getprice(symboltemp[k], datasize);
        fc.Getopen (symboltemp[k], datasize);
        fc.Gethigh(symboltemp[k], datasize);
        fc.Getlow(symboltemp[k], datasize);
        fc.Getdate (symboltemp[k], datasize);
        printf("You choose %s: %s",sectornametemp[k], symboltemp[k]);
        Print(AccountInfoString(ACCOUNT_COMPANY)+", ",AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", Period= ", PERIODX4);
        Print("In timer");
    //+----------Put Data end---------+//
        int barx = helper.Bartoint(bar) ;
        for (int i=0; i<(PERIODX16); ++i){
            if ((i+1)*barx <datasize) starti = (datasize-(i+1)*barx) ;
            else starti = 0 ;
            fc.RenewQuo_Rm(i+1, helper);
            Bosarr[i] = BOS(i+1);
            fvgarr[i] = FVG(i+1);
            rd   = fc.GetRaw();
            BOSJudge(Bosarr[i], datasize, rd, starti, helper, fvgarr[i], i);
        }
        for (int i=0; i<(PERIODX16); ++i){  
            int barsize = fvgarr[i].Getfvgkbarsize() ;
            for(int j=0; j<barsize; ++j){
                fvgarr[i].Putfvg_chlo(rd, j, i+1) ;
            }
            fvgarr[i].Putefffvg() ;
        }
        double tempd  ;
        double tempu  ;
        double temp0X ;
        double tempXF ;
        for (int i=0; i<(PERIODX4); ++i){
            ArrayResize(Tri[i].comparecode,i+1,i+1);
            ArrayResize(Tri[i].comparecode0F,i+1,i+1);
            ArrayResize(Tri[i].u_inside,i+1,i+1);
            ArrayResize(Tri[i].d_inside,i+1,i+1);
            ArrayResize(Tri[i].fvgtype0F,i+1,i+1);
            for(int j=0; j<=i; ++j){
                if(i==0 && j==0){
                    Tri[0]=TriCode(fvgarr[i], Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j, tempd, tempu, temp0X, tempXF);
                }
                else if(i!=0 && j==0){
                    Tri[i]=TriCode(fvgarr[i], Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j, tempd, tempu, temp0X, tempXF);
                }
                else{
                    int m = Bosarr[i].htfint ;
                    Tri[i]=TriCode(fvgarr[i], Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j, tempd, tempu, temp0X, tempXF);
                }
            }
            tempd = 0;
            tempu = 0;
        }
        Print("diff zone  ", helper.Extime()); 
        TriWrite(symboltemp[k], Tri, sectornametemp[k]);
        FvgWrite(symboltemp[k], fvgarr, sectornametemp[k]);
    }
}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here