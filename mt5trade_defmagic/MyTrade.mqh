#ifndef __MYTRADE_MQH__
#define __MYTRADE_MQH__
#include "Helper.mqh"
#include "Writefile.mqh"
//CTrade trade is a global variable in main file, so it does not need to passed as a parameter to functions each times .
//+-----
//+流程 讀BOSMONITOR 和 GOLD 分別進去兩個矩陣A B 這兩個矩陣來自GOLD CLASS
//+馬上做單 條件是必須要有大級別支撐壓力 有的話把做的單子的資訊填入C矩陣, C矩陣存 單子編號 P ITV PRICE SL TP 
//+C矩陣一直去監控B矩陣中和自己相同的period和ITV是否還存在 不存在的話 取消掛單並且初始化那一列週期的所有資訊
//+
//+
//+-----
//商品名稱(第一列) 
//code 基本週期 itv 空單還是多單(0是賣 F是買)  FVG型態 上 下界價錢(如果是賣 上界就是sbu 下界就是剩下三個level中最高的Sbd) 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用) 時間點)]
//以上來自Gold檔案
//如果掛單編號所在的列的元素只剩下自己 則此掛單取消
//P bosd H L T T T i2bsbd H L T bosu H L T T T i2bsbu H L T  sbd_ted  sbu_ted
//0 1    2 3 4 5 6 7      8 9 10 11  121314151617     181920 21       22
//以上是TradeBos檔案

class Golder{
public:
    matrix GD ;
    matrix GDbos ;
    matrix GD2;
    matrix GDbos2;
    double GDposopen[];
    double GDpostp[]  ;
    double GDpossl[]  ;
    int    GDtpprd[]  ;
    datetime GDnewtpt[];
    long   GDticket[];
    long   GDposticket[];
    long   GDposid[];
    int    GDticketCode[];
    int    GDticketPrd[];
    int    GDticketItv[];
    int    GDticketIng[];
    int    GDInPorSprd[];//check if the order match the support or pressure line rule of not.
    datetime GDticketsbd_t[];
    datetime GDticketsbu_t[];
    datetime GDposopen_t[];
    datetime GDordertime[];
    string symbol ;
public:
    void Init();
    Golder(){}
    Golder(int GDcolume, int GDboscolume){
        GD      = matrix::Zeros(PERIODX4, GDcolume);
        GDbos   = matrix::Zeros(PERIODX4, GDboscolume);
        GD2     = matrix::Zeros(PERIODX4, GDcolume);
        GDbos2  = matrix::Zeros(PERIODX4, GDboscolume);
        ArrayResize(GDposopen, PERIODX4, 0);
        ArrayResize(GDpostp, PERIODX4, 0);
        ArrayResize(GDpossl, PERIODX4, 0);
        ArrayResize(GDtpprd, PERIODX4, 0);
        ArrayResize(GDnewtpt, PERIODX4, 0);
        ArrayResize(GDticket, PERIODX4, 0);
        ArrayResize(GDposticket, PERIODX4, 0);
        ArrayResize(GDposid, PERIODX4, 0);
        ArrayResize(GDticketCode, PERIODX4, 0);
        ArrayResize(GDticketPrd, PERIODX4, 0);
        ArrayResize(GDticketItv, PERIODX4, 0);
        ArrayResize(GDticketIng, PERIODX4, 0);
        ArrayResize(GDInPorSprd, PERIODX4, 0);
        ArrayResize(GDticketIng, PERIODX4, 0);
        ArrayResize(GDticketsbd_t, PERIODX4, 0);
        ArrayResize(GDticketsbu_t, PERIODX4, 0);
        ArrayResize(GDposopen_t, PERIODX4, 0);
        ArrayResize(GDordertime, PERIODX4, 0);
        symbol  = "" ;
    }
};
void Golder::Init(){
    GD      = matrix::Zeros(PERIODX4, GD.Cols());
    GDbos   = matrix::Zeros(PERIODX4, GDbos.Cols());
    GD2     = matrix::Zeros(PERIODX4, GD2.Cols());
    GDbos2  = matrix::Zeros(PERIODX4, GDbos2.Cols());
    ArrayResize(GDposopen, PERIODX4, 0);
    ArrayResize(GDpostp, PERIODX4, 0);
    ArrayResize(GDpossl, PERIODX4, 0);
    ArrayResize(GDtpprd, PERIODX4, 0);
    ArrayResize(GDnewtpt, PERIODX4, 0);
    ArrayResize(GDticket, PERIODX4, 0);
    ArrayResize(GDposticket, PERIODX4, 0);
    ArrayResize(GDposid, PERIODX4, 0);
    ArrayResize(GDticketCode, PERIODX4, 0);
    ArrayResize(GDticketPrd, PERIODX4, 0);
    ArrayResize(GDticketItv, PERIODX4, 0);
    ArrayResize(GDticketIng, PERIODX4, 0);
    ArrayResize(GDInPorSprd, PERIODX4, 0);
    ArrayResize(GDticketIng, PERIODX4, 0);
    ArrayResize(GDticketsbd_t, PERIODX4, 0);
    ArrayResize(GDticketsbu_t, PERIODX4, 0);
    ArrayResize(GDposopen_t, PERIODX4, 0);
    ArrayResize(GDordertime, PERIODX4, 0);
    symbol  = "" ;
}
void MatBosinit(matrix& mat, const int& rows, const int& columes){
    for(int i=0; i<rows; ++i){
        for(int j=0; j<columes; ++j){
            mat[i][j]=0 ;
        }
    }
}
bool CheckExchangeMatch(Golder& G, const int& fixidx){ //All position data is sourced from Eighcap, and I wanna check whether the position from orther exchanges comply with the strategy's rule. this function performs as intended. 
    //GD2 may match the pressure and support rule. 
    if(G.GD[fixidx][1]==G.GD2[fixidx][1] && G.GD[fixidx][2]==G.GD2[fixidx][2] && (CheckPressureOrsupportGD2(G, fixidx)) ) return true;
    else return false ;
}
bool Check7LevelsTime(Golder& G, const int& pridm1){
    int type;
    int Itv ;
    bool checkfg = true;
    type = G.GD[pridm1][3];
    Itv  = G.GD[pridm1][2];
    if(type == 0){ //sell ticket
        datetime checksbu1_ted = G.GDbos[pridm1][22];
        for(int i=1; i<4; i++){
            checkfg = checkfg && (checksbu1_ted>G.GDbos[pridm1+i*Itv][22]);
        }
        for(int i=1; i<4; i++){
            checkfg = checkfg && (checksbu1_ted>G.GDbos[pridm1+i*Itv][21]);
        }
    }
    else{
        datetime checksbd1_ted = G.GDbos[pridm1][21];
        for(int i=1; i<4; i++){
            checkfg = checkfg && (checksbd1_ted>G.GDbos[pridm1+i*Itv][22]);
        }
        for(int i=1; i<4; i++){
            checkfg = checkfg && (checksbd1_ted>G.GDbos[pridm1+i*Itv][21]);
        }
    }
    return checkfg;
}
bool CheckPressureOrsupportGD1(Golder& G, const int& pridm1){ //pridm1 = period -1
    bool couldpending;
    double ticketupperbound;
    double ticketlowerbound;
    datetime ticketsbdtimeed; //the time sbd established 成立時間
    datetime ticketsbutimeed;
    int type ;
    int prd = pridm1+1;
    int itv = G.GD[pridm1][2];
    type    = G.GD[pridm1][3];
    if(type == 0){ //sell ticket
        ticketupperbound = G.GDbos[pridm1][12]; 
        ticketlowerbound = G.GD[pridm1][6]    ; //GD has 1440 rows
        ticketsbutimeed  = G.GDbos[pridm1][22];
        for (int l=prd; l < PERIODX4 && l<prd+3*itv; l++) {
            if(G.GDbos[l][22]<ticketsbutimeed && (G.GDbos[l][11]<=ticketupperbound && G.GDbos[l][11]>=ticketlowerbound)){
                G.GDInPorSprd[pridm1] = G.GDbos[l][0] ;
                couldpending = true ; //found it !
                break ; //jump out of for loop cuz found it
            }                        
            else couldpending = false ;             
        }
    }
    else{ // buy ticket
        ticketupperbound = G.GD[pridm1][5]    ;
        ticketlowerbound = G.GDbos[pridm1][3] ;
        ticketsbdtimeed  = G.GDbos[pridm1][21];
        for (int l=prd; l < PERIODX4 && l<prd+3*itv; l++) {
            if(G.GDbos[l][21]<ticketsbdtimeed && (G.GDbos[l][1]<=ticketupperbound && G.GDbos[l][1]>=ticketlowerbound)){
                G.GDInPorSprd[pridm1] = G.GDbos[l][0] ;
                couldpending = true ;
                break ;
            }                        
            else couldpending = false ;             
        }
    }
    return couldpending ;
}

bool CheckPressureOrsupportGD2(Golder& G, const int& pridm1){ //pridm1 = period -1
    bool couldpending;
    double ticketupperbound;
    double ticketlowerbound;
    datetime ticketsbdtimeed; //the time sbd established 成立時間
    datetime ticketsbutimeed;
    int type ;
    int prd = pridm1+1;
    int itv = G.GD2[pridm1][2];
    type    = G.GD2[pridm1][3];
    if(type == 0){ //sell ticket
        ticketupperbound = G.GDbos2[pridm1][12]; 
        ticketlowerbound = G.GD2[pridm1][6]    ; //GD2 has 1440 rows
        ticketsbutimeed  = G.GDbos2[pridm1][22];
        for (int l=prd; l < PERIODX4 && l<prd+3*itv; l++) {
            if(G.GDbos2[l][22]<ticketsbutimeed && (G.GDbos2[l][11]<=ticketupperbound && G.GDbos2[l][11]>=ticketlowerbound)){
                couldpending = true ; //found it !
                break ; //jump out of for loop cuz found it
            }                        
            else couldpending = false ;             
        }
    }
    else{ // buy ticket
        ticketupperbound = G.GD2[pridm1][5]    ;
        ticketlowerbound = G.GDbos2[pridm1][3] ;
        ticketsbdtimeed  = G.GDbos2[pridm1][21];
        for (int l=prd; l < PERIODX4 && l<prd+3*itv; l++) {
            if(G.GDbos2[l][21]<ticketsbdtimeed && (G.GDbos2[l][1]<=ticketupperbound && G.GDbos2[l][1]>=ticketlowerbound)){
                couldpending = true ;
                break ;
            }                        
            else couldpending = false ;             
        }
    }
    return couldpending ;
}
void SendPendingAndStore(Golder& G, const int& i, string defsymbol){
    trade.SetExpertMagicNumber(_magic);
    //if((G.GD[i][0]!=0) && (G.GDticketIng[i]==0) && (CheckExchangeMatch(G,i))) {
    //if((G.GD[i][0]!=0) && (G.GDticketIng[i]==0) && (Check7LevelsTime(G,i))) {
    if((G.GD[i][0]!=0) && (G.GDticketIng[i]==0)){
        //printf("G.GD_p%d= %.0f", i+1, G.GD[i][0]) ;
        double pendingprice ;
        double nowprice  ;
        double pip       ;
        double pdtp      ;
        double pdsl      ;
        bool   Sendfg = false ;
        int direction    = G.GD[i][3]==0? ORDER_TYPE_SELL_STOP_LIMIT : ORDER_TYPE_BUY_STOP_LIMIT ;
        switch (direction){
        case ORDER_TYPE_SELL_STOP_LIMIT:
            nowprice     = SymbolInfoDouble(defsymbol, SYMBOL_BID) ;
            pdtp         = nowprice-1 ;
            pdsl         = nowprice+1;
            pip = nowprice<10? 0.00001 : nowprice<400? 0.001 : nowprice>10000? 10 : 1 ;
            pendingprice = nowprice;
            // nowprice     = SymbolInfoDouble(defsymbol, SYMBOL_ASK) ;
            // pdtp         = G.GDbos[i][7] ;
            // pdsl         = G.GDbos[i][18];
            // pip = nowprice<10? 0.00001 : nowprice<400? 0.001 : nowprice>10000? 10 : 1 ;
            // pendingprice = (pdtp + (pdsl - pdtp) * _profitpercent) ;
            //if(pendingprice-pdtp<0) break ;
            //if(MathAbs(pdtp-pdsl)<50*pip) break;
            //if(pdsl<=0) break ;
            //if(!CheckPressureOrsupportGD1(G,i)) break ;
            trade.SetTypeFilling(SYMBOL_FILLING_FOK);
            if(trade.SellLimit(_lot_size, pendingprice, defsymbol, pdsl, pdtp))Sendfg = true;
            else if(trade.SellStop(_lot_size, pendingprice, defsymbol, pdsl, pdtp)) Sendfg = true;
            // lot pending symbol sl tp
            //if(trade.BuyStop(_lot_size, pendingprice, defsymbol, nowprice, G.GDbos[i][18]) ){ // lot pending symbol sl tp
            //if(trade.SellLimit(_lot_size, nowprice, defsymbol, nowprice+0.5, nowprice-0.5) ){
            if(Sendfg){
                printf("SellLimit order sended successfully ") ;
                G.GDposopen[i]     =  pendingprice   ;
                G.GDpossl[i]       =  pdsl;
                G.GDpostp[i]       =  pdtp;
                G.GDposticket[i]   =  0 ; 
                G.GDticket[i]      =  trade.ResultOrder() ; //this is order ticket
                OrderSelect(trade.ResultOrder());
                G.GDordertime[i]   = OrderGetInteger(ORDER_TIME_SETUP);
                printf("G.GDticket[%d]= %d, G.GDordertime[%d]= %s", i, G.GDticket[i], i, TimeToString(G.GDordertime[i],TIME_DATE|TIME_MINUTES));
                G.GDticketCode[i]  =  G.GD[i][0] ;
                G.GDticketPrd[i]   =  G.GD[i][1] ;
                G.GDticketItv[i]   =  G.GD[i][2] ;
                G.GDticketsbd_t[i] =  G.GDbos[i][4];
                G.GDticketsbu_t[i] =  G.GDbos[i][14];
                G.GDticketIng[i]   =  1 ;
            }
            else{
                printf("SellLimit fail! Errorcode= %d", trade.ResultRetcode());
                //printf("SellLimit order sended fail G.GDbos[i][18] - nowprice= %.5f, nowprice=%.5f", G.GDbos[i][18] - nowprice, nowprice) ;
            }
            break ;
        case ORDER_TYPE_BUY_STOP_LIMIT:
            nowprice  = SymbolInfoDouble(defsymbol, SYMBOL_BID) ;
            pdtp      = G.GDbos[i][17] ;
            pdsl      = G.GDbos[i][9];
            pip = nowprice<10? 0.00001 : nowprice<400? 0.001 : nowprice>10000? 10 : 1 ;
            pendingprice = pdsl + (pdtp - pdsl ) * _profitpercent ;
            if(pendingprice-pdtp>0) break ;
            if(MathAbs(pdtp-pdsl)<50*pip) break;
            //if(MathAbs(nowprice-G.GDbos[i][9])>100*pip) break;
            if(pdsl<=0) break ;
            if(!CheckPressureOrsupportGD1(G,i)) break ;
            trade.SetTypeFilling(SYMBOL_FILLING_FOK);
            if(trade.BuyLimit(_lot_size, pendingprice, defsymbol, pdsl, pdtp))Sendfg = true;
            else if(trade.BuyStop(_lot_size, pendingprice, defsymbol, pdsl, pdtp)) Sendfg = true;
            if(Sendfg){
                //if(trade.SellStop(_lot_size, pendingprice, defsymbol, nowprice, G.GDbos[i][9]) ){
                printf("BuyLimit order sended successfully ") ;
                G.GDposopen[i]     =  pendingprice   ;
                G.GDpossl[i]       =  pdsl;
                G.GDpostp[i]       =  pdtp;
                G.GDposticket[i]   =  0 ; 
                G.GDticket[i]      =  trade.ResultOrder() ; //this is order ticket
                OrderSelect(trade.ResultOrder());
                G.GDordertime[i]   = OrderGetInteger(ORDER_TIME_SETUP);
                printf("G.GDticket[%d]= %d, G.GDordertime[%d]= %s", i, G.GDticket[i], i, TimeToString(G.GDordertime[i],TIME_DATE|TIME_MINUTES));
                G.GDticketCode[i]  =  G.GD[i][0] ;
                G.GDticketPrd[i]   =  G.GD[i][1] ;
                G.GDticketItv[i]   =  G.GD[i][2] ;
                G.GDticketsbd_t[i] =  G.GDbos[i][4];
                G.GDticketsbu_t[i] =  G.GDbos[i][14];
                G.GDticketIng[i]   =  1 ;

            }
            else{
                printf("BuyLimit fail! Errorcode= %d", trade.ResultRetcode());
                //printf("SellLimit order sended fail G.GDbos[i][18] - nowprice= %.5f, nowprice=%.5f", G.GDbos[i][18] - nowprice, nowprice) ;
            }
            break;
        default:
            printf("The order is illegal. ");
            break ;
        }
    }
}
void MonitorPendingOrder(Golder& G){ // check whether the period where the ticket belongs exsits and is valid or not
    for(int i=0; i<PERIODX4; ++i){
        long  ticket     = G.GDticket[i];
        int   ticketing  = G.GDticketIng[i] ;
        int   Itv        = G.GDticketItv[i];
        //if(ticket!=0)printf("G.GDticket[l]= %d", ticket);
        if(ticketing==0 || ticketing==2) continue ; // it means that those pending order whose ticketing==1 will jump into else condition
        else{
            if(Itv != G.GD[i][2] ){
            //if(Itv != G.GD[i][2] || (!CheckPressureOrsupportGD1(G,i)) ){
            //if(Itv != G.GD[i][2] || (!CheckPressureOrsupportGD1(G,i)) || (!CheckPressureOrsupportGD2(G,i)) ){
                if(trade.OrderDelete(ticket)){
                    printf("Order deleted ");
                    G.GDposopen[i]     = 0 ;
                    G.GDpostp[i]       = 0 ;
                    G.GDpossl[i]       = 0 ;
                    G.GDtpprd[i]       = 0 ;
                    G.GDnewtpt[i]      = 0 ;
                    G.GDticket[i]      = 0 ;
                    G.GDposticket[i]   = 0 ;
                    G.GDposid[i]       = 0 ;
                    G.GDticketCode[i]  = 0 ;
                    G.GDticketPrd[i]   = 0 ;
                    G.GDticketItv[i]   = 0 ;
                    G.GDInPorSprd[i]   = 0 ;
                    G.GDticketsbd_t[i] = 0 ;
                    G.GDticketsbu_t[i] = 0 ;
                    G.GDposopen_t[i]   = 0 ;
                    G.GDordertime[i]   = 0 ;
                    G.GDticketIng[i]   = 0 ;
                } 
                else printf("Order delete failed. Error code= %d", trade.ResultRetcode()) ;
            }
        }
    }
}

void PositionCheck(Golder& G){ //execute in ISR OnTrade
    datetime ct = TimeCurrent();
    string   possymbol ;
    long     posid     ;
    long     dealticket ;
    long     orderticket;
    double   checkopen;
    double   checktp;
    double   checksl;
    datetime posopen_t;
    bool     checksum = false ;
    int      orderofs = 0; //orderoffset is for tracking the very first deal order ticket number, because
    //PrintFormat("In PositionCheck total_position: %d", total_postion);
    if(HistorySelect(ct-60, ct)){
        uint total=HistoryDealsTotal();
        printf("total deal= %d", total);
        for(int i=0; i<total && (!checksum); ++i){
            dealticket = HistoryDealGetTicket(i);
            printf("dealticket= %d", dealticket);
            if(HistoryDealSelect(dealticket)){
                orderticket         = HistoryDealGetInteger(dealticket,DEAL_ORDER);
                possymbol           = HistoryDealGetString(dealticket,DEAL_SYMBOL);
                posid               = HistoryDealGetInteger(dealticket,DEAL_POSITION_ID);
                checkopen           = HistoryDealGetDouble(dealticket,DEAL_PRICE);
                checktp             = HistoryDealGetDouble(dealticket,DEAL_TP);
                checksl             = HistoryDealGetDouble(dealticket,DEAL_SL);
                posopen_t           = HistoryDealGetInteger(dealticket,DEAL_TIME);
                if(possymbol != G.symbol) continue;
                printf("orderticket+orderofs= %d, orderofs=%d", orderticket+orderofs, orderofs);
                for(int l=0; l<PERIODX4; ++l){
                    //checksum = (G.GDposticket[l]==0) && (G.GDticketIng[l]==1) && (checktp == G.GDpostp[l]) && (checksl == G.GDpossl[l]) &&(orderticket == G.GDticket[l]);
                    checksum = (G.GDposticket[l]==0) && (G.GDticketIng[l]==1) &&(orderticket+orderofs == G.GDticket[l]);
                    if(checksum){
                        PositionSelectByTicket(orderticket); //will only select one of those positions—typically the most recent one for that symbol.
                        G.GDticketIng[l]   = 2;
                        G.GDposticket[l]   = PositionGetInteger(POSITION_TICKET);
                        G.GDposid[l]       = posid ;
                        G.GDposopen_t[l]   = posopen_t;
                        printf("G.GDticket[%d]= %d, G.GDposticket[%d]= %d posid= %d, ticketing= %d checksum= %d, checkopen= %.5f, G.GDposopen[%d]= %.5f",l, G.GDticket[l], l, G.GDposticket[l], posid, G.GDticketIng[l], checksum, checkopen, l, G.GDposopen[l]);//我後來發現posticket會跟GDticket一樣才這樣寫 but gpt說不一樣
                        printf("checksum= true");
                        checksum = false ;
                        orderofs++;
                        break;
                    } 
                    else continue;

                }
            }
            else ;//printf("posselect failed, Error code= %d", trade.ResultRetcode() );
        }
    }
    Sleep(1000);
}
void MonitorAndModifyPos(Golder& G){ // modify tp cuz dynamic sb rule. ex: buy position: the function activate when the level sbu occurs. 
    double   oldsl       ;
    double   oldtp       ;
    int      level1sbtime;
    double   level1sb    ;
    long     posticket   ;
    double   tptemp      ;
    for(int i=0; i<PERIODX4; ++i){
        if(G.GDticketIng[i] != 2) continue;
        else{
            if(PositionSelectByTicket(G.GDposticket[i])){
                oldsl     = PositionGetDouble(POSITION_SL);
                oldtp     = PositionGetDouble(POSITION_TP);
                posticket = G.GDposticket[i] ;
                switch(PositionGetInteger(POSITION_TYPE) ){
                case POSITION_TYPE_SELL:
                    if(G.GDbos[i][1] == -1) break;
                    else{
                        level1sbtime = G.GDbos[i][21] ;
                        level1sb     = G.GDbos[i][1] ;
                    }
                    for(int l=i; l<PERIODX4; ++l){
                        tptemp = G.GDpostp[i]; //oldtp
                        //printf("tptemp= %.5f oldtp= %.5f", tptemp, oldtp);
                        if(G.GDbos[l][21]>=level1sbtime && G.GDbos[l][1]>=tptemp){
                            if(tptemp!=0 && G.GDbos[l][1]<tptemp) continue;
                            if( trade.PositionModify(posticket, oldsl, G.GDbos[l][1]) ){
                                G.GDpostp[i] = G.GDbos[l][1] ;
                                G.GDtpprd[i] = G.GDbos[l][0] ; //modified tp period
                                G.GDnewtpt[i]= G.GDbos[l][21] ; //new tp time aka. sbd_ted for closing pos usage 
                                printf("the tp is modified");
                            } 
                            else printf("fail to modify the tp ") ;
                        }
                    }
                    break;
                case POSITION_TYPE_BUY:
                    if(G.GDbos[i][11] == -2) break;
                    else{
                        level1sbtime = G.GDbos[i][22] ;
                        level1sb     = G.GDbos[i][11] ;
                    }
                    for(int l=i; l<PERIODX4; ++l){
                        tptemp = G.GDpostp[i]; //oldtp
                        if(G.GDbos[l][22]>=level1sbtime && G.GDbos[l][11]<=tptemp){
                            if(tptemp!=0 && G.GDbos[l][11]>tptemp) continue;
                            if( trade.PositionModify(posticket, oldsl, G.GDbos[l][11]) ){
                                G.GDpostp[i] = G.GDbos[l][11] ;
                                G.GDtpprd[i] = G.GDbos[l][0] ;
                                G.GDnewtpt[i]= G.GDbos[l][22] ; //new tp time aka. sbu_ted for closing pos usage 
                                printf("the tp is modified"); 
                            } 
                            else printf("fail to modify the tp ") ;
                        }
                    }
                    break;
                default:
                    printf("neither sell nor buy");
                    break ;
                }
            }
            else printf("the ticket is void or wrong");
        }
    }
}
void DealCheck(Golder& G, const datetime& fromtime,  DealGolder& DG, const string& sectorname){
    datetime ct = TimeCurrent();
    long   deal_ticket;           
    long   dealorder  ;
    long   dealmagic  ;
    string dealsymbol;
    double dealprofit;
    double dealvolume;
    int    dealentry ;
    long   dealpos   ;
    int    dealdirection;
    bool   searchfg = false ;
    int    idx ;
    string fromtime_str = TimeToString(fromtime, TIME_DATE|TIME_MINUTES);
    //printf("In DealCheck");
    if(HistorySelect(ct-60, ct)){
        uint total=HistoryDealsTotal();
        //PrintFormat("total_history ranged: %d, Numbers of Pos: %d", total, total_postion);

        for(int i=0; i<total && !searchfg; ++i){
            deal_ticket         = HistoryDealGetTicket(i);
            dealentry           = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
            dealsymbol          = HistoryDealGetString(deal_ticket, DEAL_SYMBOL);
            if(dealentry  != DEAL_ENTRY_OUT) continue; 
            dealorder           = HistoryDealGetInteger(deal_ticket, DEAL_ORDER); 
            dealvolume          = HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
            dealprofit          = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
            dealdirection       = HistoryDealGetInteger(deal_ticket, DEAL_TYPE);
            dealpos             = HistoryDealGetInteger(deal_ticket, DEAL_POSITION_ID);
            //printf("dealorder= %d, dealentry=%d", dealorder, dealentry);
            while(!searchfg){
                idx = 0;
                if(G.GDposid[idx]==dealpos && G.GDticketIng[idx]==2 && G.symbol==dealsymbol){
                    searchfg = true;
                    break;
                }
                else idx++;
                if(idx==1440){
                    printf("idx==1440, can not search for right closed position");
                    break;
                }
            }
            if(searchfg){
                printf("Get right posid! dealticket= %d, posid= %d, dealorder= %d, posticket= %d", deal_ticket, dealpos, dealorder, G.GDposticket[idx]) ;
                DG.dealmagic       = dealmagic;
                DG.dealorder       = G.GDticket[idx];
                DG.dealposticket   = G.GDposticket[idx];
                DG.dealposid       = dealpos;
                DG.dealticket      = deal_ticket;
                DG.dealsymbol      = dealsymbol;
                DG.dealdirection   = dealdirection;
                DG.dealopen        = G.GDposopen[idx];
                DG.dealtp          = G.GDpostp[idx];
                DG.dealsl          = G.GDpossl[idx];
                DG.dealtpprd       = G.GDtpprd[idx];
                DG.dealnewtpt      = G.GDnewtpt[idx];
                DG.dealcode        = G.GDticketCode[idx];
                DG.dealprd         = G.GDticketPrd[idx];
                DG.dealitv         = G.GDticketItv[idx];
                DG.dealInPorS      = G.GDInPorSprd[idx];
                DG.dealsbd_t       = G.GDticketsbd_t[idx];
                DG.dealsbu_t       = G.GDticketsbu_t[idx];
                DG.ordertime       = G.GDordertime[idx];
                DG.dealposopen_t   = G.GDposopen_t[idx]  ;
                DG.dealvolume      = dealvolume;
                DG.dealprofit      = dealprofit;
                DG.DealWriteOut(sectorname);
                G.GDposopen[idx]     = 0 ;
                G.GDpostp[idx]       = 0 ;
                G.GDpossl[idx]       = 0 ;
                G.GDtpprd[idx]       = 0 ;
                G.GDnewtpt[idx]      = 0 ;
                G.GDticket[idx]      = 0 ;
                G.GDposticket[idx]   = 0 ;
                G.GDposid[idx]       = 0 ;
                G.GDticketCode[idx]  = 0 ;
                G.GDticketPrd[idx]   = 0 ;
                G.GDticketItv[idx]   = 0 ;
                G.GDInPorSprd[idx]   = 0 ;
                G.GDticketsbd_t[idx] = 0 ;
                G.GDticketsbu_t[idx] = 0 ;
                G.GDordertime[idx]   = 0 ;
                G.GDposopen_t[idx]   = 0 ;
                G.GDticketIng[idx]   = 0 ; //so that resending data can start
            } 
            else continue;      
        }
        if(!searchfg);//printf("can not search for right closed position in all TotalHistoryDeal");
    }
    else printf("no history records after %s", fromtime_str );
}
bool DeleteOrder(Golder& G){
    int total_orders = OrdersTotal();
    for (int i = total_orders - 1 ; i >= 0; --i){
        ulong ticket      = OrderGetTicket(i);
        int  ordertype    = OrderGetInteger(ORDER_TYPE) ;
        if (ticket){
            if (ordertype == ORDER_TYPE_BUY_LIMIT || ordertype == ORDER_TYPE_SELL_LIMIT || ordertype == ORDER_TYPE_BUY_STOP || ordertype == ORDER_TYPE_SELL_STOP){
                if(trade.OrderDelete(ticket)) printf("Order in certain magic number is deleted successfully, ticket= %I64u", ticket) ;
                else printf("Delete failed, Error code= %d", trade.ResultRetcode() );
            }
        }
        else printf("Can not choose the ticket order %d", i) ;
    }
    G.Init();
    return false;
}

bool DeleteMagicPendingOrder(long magic_number){
    int total_orders = OrdersTotal();
    for (int i = total_orders - 1; i >= 0; --i){
        ulong ticket      = OrderGetTicket(i);
        ulong order_magic = OrderGetInteger(ORDER_MAGIC); 
        int   ordertype   = OrderGetInteger(ORDER_TYPE) ;
        if(ticket){
            if(order_magic == magic_number){
                if (ordertype == ORDER_TYPE_BUY_LIMIT || ordertype == ORDER_TYPE_SELL_LIMIT || ordertype == ORDER_TYPE_BUY_STOP || ordertype == ORDER_TYPE_SELL_STOP){
                    if(trade.OrderDelete(ticket)) printf("Order in certain magic number is deleted successfully, magic= %I64u, ticket= %I64u", magic_number, ticket) ;
                    else{
                        printf("Delete failed, Error code= %d", trade.ResultRetcode() );
                        break;
                    } 
                }
            }
        }
        else printf("Can not choose the ticket order %d", i) ;
    }
    return true;
}

#endif
