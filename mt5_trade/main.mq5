#include "Readfile.mqh"
#property strict
#include <Trade\Trade.mqh>
CTrade trade ;

// 創建交易對象

// 輸入參數
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
input double _lot_size       = 0.01;     // 每次交易的手數
input double _profitpercent  = 0.5;   // 目標獲利率
int gdcolume                 = 11; //商品名稱(第一列) code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用應該要引線) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用應該要引線) 時間點)]
int gdboscolume              = 21; //P bosd H L T T T i2bsbd H L T bosu H L T T T i2bsbu H L T
                                   //0 1    2 3 4 5 6 7      8 9 10 11  121314151617     181920
SymbolSet Symbolset        ;
Helper helper              ;
string symboltemp[10]      ;
string sectornametemp[10]  ;

Golder G[10];
DealGolder WDG;
long _magic = 3245012;  // 设置魔术号
datetime _EAexetime ;
int OnInit(){
    printf("In initiation");
    _EAexetime = TimeCurrent();
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
    printf("total orders= %d", OrdersTotal());
    DeleteMagicPendingOrder(_magic) ;
    for(int k=0; k<10; ++k){
        G[k] = Golder(gdcolume, gdboscolume);
    }
    EventSetTimer(2);
    return(INIT_SUCCEEDED) ;
}
void OnDeinit(const int reason) {
    // Print a message to indicate the EA has been deinitialized
    //DeleteMagicPendingOrder(_magic) ; useless command after disable ea
    Print("EA has been deinitialized.");
    // Add your deinitialization code here
    EventKillTimer();
}
//code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用) 時間點)], 訂單編號(掛單後取得)
//如果掛單編號所在的列的元素只剩下自己 則此掛單取消
void OnTick() {
    //Print("In tick");
    for(int k=0; k<10; ++k){
        if(sectornametemp[k]==NULL) continue ;
        MonitorPendingOrder(G[k]);
    }
}

void OnTimer(){
    //printf("in timer");
    for(int k=0; k<10; ++k){//{p bosd H L T T T  i2b H L T bosu H L T T T  i2b H L T}
        if(sectornametemp[k]==NULL) continue ;
        G[k].Init();
        RSfile(symboltemp[k], sectornametemp[k], G[k]);
        //printf("rows size= %d columes size= %d", G[k].GD.Rows(), G[k].GD.Cols() );
        // printf("GBOS.code=%.0f", G[k].GD[0][1]);
        // printf("GBOS.p=%.0f", G[k].GD[0][0]);
        //printf("sym=%s", G[k].symbol);
        for(int i=0; i<PERIODX4; ++i){
            SendPendingAndStore(G[k], i, symboltemp[k]) ;
        }
    }
}

void OnTrade(){
    printf("In ISR");
    for(int k=0; k<10; ++k){
        if(sectornametemp[k]==NULL) continue ;
        DealCheck(G[k], _EAexetime, WDG, sectornametemp[k]);
        PositionCheck(G[k]);
    }
}
