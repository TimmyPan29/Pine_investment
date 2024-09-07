#include "Bos.mqh"
#include "WriteBos.mqh"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Exchange ex            = OANDA ;
input Treasure tr1           = Forex;
input int      symbol_n1     = 0     ;
input int      d_checkn1     = 1     ;
input int      u_checkn1     = 1     ;
input Treasure tr2           = Forex ;
input int      symbol_n2     = 1     ;
input int      d_checkn2     = 1     ;
input int      u_checkn2     = 1     ;
input Treasure tr3           = Forex ;
input int      symbol_n3     = 2     ;
input int      d_checkn3     = 1     ;
input int      u_checkn3     = 1     ;
input Treasure tr4           = Forex ;
input int      symbol_n4     = 3     ;
input int      d_checkn4     = 1     ;
input int      u_checkn4     = 1     ;
input Treasure tr5           = Forex ;
input int      symbol_n5     = 4     ;
input int      d_checkn5     = 1     ;
input int      u_checkn5     = 1     ;
input Treasure tr6           = Forex ;
input int      symbol_n6     = 5     ;
input int      d_checkn6     = 1     ;
input int      u_checkn6     = 1     ;
input Treasure tr7           = Forex ;
input int      symbol_n7     = 6     ;
input int      d_checkn7     = 1     ;
input int      u_checkn7     = 1     ;
input Treasure tr8           = Forex ;
input int      symbol_n8     = 7     ;
input int      d_checkn8     = 1     ;
input int      u_checkn8     = 1     ;
input Treasure tr9           = Forex ;
input int      symbol_n9     = 8     ;
input int      d_checkn9     = 1     ;
input int      u_checkn9     = 1     ;
input Treasure tr10          = Forex ;
input int      symbol_n10    = 9     ;
input int      d_checkn10    = 1     ;
input int      u_checkn10    = 1     ;

input int      datasize      = 1000000;
input Barchoice bar          = Bar1000;
int      starti            ;
SymbolSet Symbolset        ;
RawCandles rd              ;
Helper helper              ;
string symboltemp[10]      ;
string sectornametemp[10]  ;
int    dpcheck[10]         ;
int    upcheck[10]         ;
Fetcher fc                 ;
FVG fvgarr[PERIODX4]       ;
BOS Bosarr[PERIODX4]       ;//設一天會卡死 base最多到359 超過360要再想辦法
int quooffset   = 0          ;
bool timerfg    = true       ;
matrix M_sbd    = matrix::Zeros(PERIODX4, 14) ;// {p bosd H L O T T T T i2b H L O T}
matrix M_sbu    = matrix::Zeros(PERIODX4, 14) ;// {p bosd H L O T T T T i2b H L O T}
matrix M_sbdo   = matrix::Zeros(PERIODX4, 14) ;// {p bosd H L O T T T T i2b H L O T}
matrix M_sbuo   = matrix::Zeros(PERIODX4, 14) ;// {p bosd H L O T T T T i2b H L O T}
matrix M_sbdCP  = matrix::Zeros(PERIODX4, 5) ;// {p bos H L BT }
matrix M_sbuCP  = matrix::Zeros(PERIODX4, 5) ;// {p bos H L BT }
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

        dpcheck[0] = d_checkn1;
        dpcheck[1] = d_checkn2;
        dpcheck[2] = d_checkn3;
        dpcheck[3] = d_checkn4;
        dpcheck[4] = d_checkn5;
        dpcheck[5] = d_checkn6;
        dpcheck[6] = d_checkn7;
        dpcheck[7] = d_checkn8;
        dpcheck[8] = d_checkn9;
        dpcheck[9] = d_checkn10;

        upcheck[0] = u_checkn1;
        upcheck[1] = u_checkn2;
        upcheck[2] = u_checkn3;
        upcheck[3] = u_checkn4;
        upcheck[4] = u_checkn5;
        upcheck[5] = u_checkn6;
        upcheck[6] = u_checkn7;
        upcheck[7] = u_checkn8;
        upcheck[8] = u_checkn9;
        upcheck[9] = u_checkn10;
    }

    Print("end initiation");
    EventSetTimer(2);
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
            }
            for (int i=0; i<(PERIODX4); ++i){
                fvgarr[i].bos_hlt(fc.Vec_rawdata.mat_rates, M_sbd, M_sbu, Bosarr[i], i);
                fvgarr[i].bosi2b_hlt(fc.Vec_rawdata.mat_rates, M_sbdo, M_sbuo, Bosarr[i], i);
            }
            for (int i=0; i<(PERIODX4); ++i){
                Boscopy(M_sbd, M_sbu, M_sbdo, M_sbuo, i) ;
            }
            BOSInsertalg(M_sbd);
            BOSInsertalg(M_sbu);
            //+----------CheckPeriod---------+//
            CheckClosePosPeriod(M_sbdCP, M_sbuCP, M_sbdo, M_sbuo, dpcheck[k], upcheck[k]);
            //+----------Outputfile---------+//
            printf("in Outputfile process");
            BosWrite(symboltemp[k],  M_sbd,  M_sbu, M_sbdo, M_sbuo, M_sbdCP, M_sbuCP, dpcheck[k], upcheck[k], sectornametemp[k]) ;
            TradeBosWrite(symboltemp[k], M_sbdo, M_sbuo, sectornametemp[k]);
            //+----------printtest---------+//
            // for(int i=0; i<fvgarr[10].Getfvgkbarsize(); ++i){
            //     printf("fvgarr11.kbar= %d", fvgarr[10].kbar[i]);
            // }
            // for(int i=0; i<1440; i++){
            //     printf("fvgarr[%d].sbd= %.5f",i, fvgarr[i].sbd); 
            // }
            //+----------Init---------+//
            MatBosinit(M_sbd, PERIODX4, 9)   ;
            MatBosinit(M_sbu, PERIODX4, 9)   ;
            MatBosinit(M_sbdo, PERIODX4, 13)  ;
            MatBosinit(M_sbuo, PERIODX4, 13)  ;
            MatBosinit(M_sbdCP, PERIODX4, 5) ;
            MatBosinit(M_sbuCP, PERIODX4, 5) ;
        }
        timerfg = false ;
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
        // string timeStr = TimeToString(fc.Vec_rawdata.mat_rates[4][999999], TIME_DATE | TIME_MINUTES);
        // printf("fc.Vec_rawdata.mat_rates= %s", timeStr);
        // printf("M_sbd[399][2]= %.5f\nM_sbu[399][2]= %.5f", M_sbd[399][2], M_sbu[399][2]);
        // printf("M_sbd[399][7]= %d\nM_sbu[399][7]= %d",     M_sbd[399][7], M_sbu[399][7]);
        // for(int i=0; i<fvgarr[399].Getfvgkbarsize(); ++i){
        //     printf("period400_bar%d = %.5f", i, fvgarr[399].kbarclose[i]) ;
        // }
        // TriWrite(symboltemp[k], Tri, sectornametemp[k]);
        // FvgWrite(symboltemp[k], fvgarr, sectornametemp[k]);