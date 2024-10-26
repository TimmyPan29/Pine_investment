#include "Bos.mqh"
#include "WriteTri.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Exchange ex            = OANDA ;
input Treasure tr1           = Forex;
input int      symbol_n1     = 0     ;
input Treasure tr2           = Forex ;
input int      symbol_n2     = 1     ;
input Treasure tr3           = Forex ;
input int      symbol_n3     = 2     ;
input Treasure tr4           = Forex ;
input int      symbol_n4     = 3     ;
input Treasure tr5           = Forex ;
input int      symbol_n5     = 4     ;
input Treasure tr6           = Forex ;
input int      symbol_n6     = 5     ;
input Treasure tr7           = Forex ;
input int      symbol_n7     = 6     ;
input Treasure tr8           = Forex ;
input int      symbol_n8     = 7     ;
input Treasure tr9           = Forex ;
input int      symbol_n9     = 8     ;
input Treasure tr10          = Forex ;
input int      symbol_n10    = 9     ;


input int      datasize      = 1000000;
input Barchoice bar          = Bar1000;
int      starti            ;
SymbolSet Symbolset        ;
RawCandles rd              ;
Helper helper              ;
string symboltemp[10]      ;
string sectornametemp[10]  ;
Fetcher fc                 ;
FVG fvgarr[PERIODX4]       ;
BOS Bosarr[PERIODX4]       ;//設一天會卡死 base最多到359 超過360要再想辦法
Triset Tri[PERIOD]         ;

int quooffset = 0;
bool timerfg  = true        ;
//vector quooffset{symbol1Off, symbol2Off, symbol3Off, symbol4Off, symbol5Off, symbol6Off, symbol7Off, symbol8Off, symbol9Off, symbol10Off};
int OnInit() {
    printf("In initiation");
    helper.Ext = helper.ChooseEx(ex)        ;
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
    Print("end initiation");
    EventSetTimer(60);
    return(INIT_SUCCEEDED) ;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Print a message to indicate the EA has been deinitialized
    Print("EA has been deinitialized.");
    // Add your deinitialization code here
    EventKillTimer();
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    if(timerfg){
        printf("In tick");
        //+----------initiation---------+//
        
        //+----------initiation end---------+//
        //+----------Put Data---------+//
        for(int k=0; k<10; ++k){
            if(sectornametemp[k]==NULL) continue ;
            fc.GetOHLCT(symboltemp[k], datasize);
            printf("You choose %s: %s",sectornametemp[k], symboltemp[k]);
            Print(AccountInfoString(ACCOUNT_COMPANY)+", ",AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", Period= ", PERIOD);
            //+----------Put Data end---------+//
            // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
            // cuz u s still have not initialize the BOS type;
            int barx = helper.Bartoint(bar) ;
            for (int i=0; i<(PERIODX4); ++i){
                if ((i+1)*barx <datasize) starti = (datasize-(i+1)*barx) ;
                else starti = 0 ;
                fc.RenewQuo_Rm(i+1, helper, quooffset);
                Bosarr[i] = BOS(i+1);
                fvgarr[i] = FVG(i+1);
                BOSJudge(Bosarr[i], datasize, fc.Vec_rawdata, starti, helper, fvgarr[i], i);
            }
            for (int i=0; i<(PERIODX4); ++i){  
                int barsize = fvgarr[i].Getfvgkbarsize() ;
                for(int j=0; j<barsize; ++j){
                    fvgarr[i].Putfvg_chlo(fc.Vec_rawdata.mat_rates, j,i+1) ;
                }
                fvgarr[i].Putefffvg(Bosarr[i]) ;
            }
            printf("putfvg success");

            for (int i=0; i<(PERIOD); ++i){ 
                Tri[i].SearchNearbox(fvgarr[i], Bosarr[i]);
                Tri[i].TouchfvgDetect(Bosarr[i], symboltemp[k]);
            }
            printf("single level search and check touching flag successfully");
            Print("diff zone  ", helper.Extime());
            printf("in Outputfile process");
            TriWrite(symboltemp[k], Bosarr, Tri, sectornametemp[k]);
        }
        timerfg = false ;
        for (int i=0; i<(PERIOD); ++i){
            Tri[i].TriInit();
        }
    }
}
void OnTimer(){
    printf("in timer");
    timerfg = true ;
}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here