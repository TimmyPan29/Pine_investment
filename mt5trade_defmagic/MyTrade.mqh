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
//商品名稱(第一列) code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用) 時間點)], 訂單編號(掛單後取得)
//如果掛單編號所在的列的元素只剩下自己 則此掛單取消
//P bosd H L T T T i2bsbd H L T bosu H L T T T i2bsbu H L T
//0 1    2 3 4 5 6 7      8 9 10 11  121314151617     181920
class Golder{
public:
    matrix GD ;
    matrix GDbos ;
    ulong  GDticket[];
    int    GDticketCode[];
    int    GDticketPrd[];
    int    GDticketItv[];
    int    GDticketIng[];
    datetime GDticketsbd_t[];
    datetime GDticketsbu_t[];
    string symbol ;
public:
    void Init();
    Golder(){}
    Golder(int GDcolume, int GDboscolume){
        GD      = matrix::Zeros(PERIODX4, GDcolume);
        GDbos   = matrix::Zeros(PERIODX4, GDboscolume);
        ArrayResize(GDticket, PERIODX4, 0);
        ArrayResize(GDticketCode, PERIODX4, 0);
        ArrayResize(GDticketPrd, PERIODX4, 0);
        ArrayResize(GDticketItv, PERIODX4, 0);
        ArrayResize(GDticketIng, PERIODX4, 0);
        ArrayResize(GDticketsbd_t, PERIODX4, 0);
        ArrayResize(GDticketsbu_t, PERIODX4, 0);
        symbol  = "" ;
    }
};
void Golder::Init(){
    GD      = matrix::Zeros(PERIODX4, GD.Cols());
    GDbos   = matrix::Zeros(PERIODX4, GDbos.Cols());
    symbol  = "" ;
}
void MatBosinit(matrix& mat, const int& rows, const int& columes){
    for(int i=0; i<rows; ++i){
        for(int j=0; j<columes; ++j){
            mat[i][j]=0 ;
        }
    }
}

void SendPendingAndStore(Golder& G, const int& i, string defsymbol){
    trade.SetExpertMagicNumber(_magic);
    if((G.GD[i][0]!=0) && (G.GDticketIng[i]==0)){
        //printf("G.GD_p%d= %.0f", i+1, G.GD[i][0]) ;
        double pendingprice ;
        double nowprice  = SymbolInfoDouble(defsymbol, SYMBOL_BID) ;
        int direction = G.GD[i][3]==0? ORDER_TYPE_SELL_LIMIT : ORDER_TYPE_BUY_LIMIT ;
        switch (direction){
        case ORDER_TYPE_SELL_LIMIT:
            pendingprice = (nowprice + (G.GDbos[i][18] - nowprice) * _profitpercent) ;
            if(trade.SellLimit(_lot_size, pendingprice, defsymbol, G.GDbos[i][18], nowprice) ){
                printf("SellLimit order sended successfully ") ;
                G.GDticket[i]      =  trade.ResultOrder() ;
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
        case ORDER_TYPE_BUY_LIMIT:
            pendingprice = nowprice - (nowprice - G.GDbos[i][9] ) * _profitpercent ;
            if(trade.BuyLimit(_lot_size, pendingprice, defsymbol, G.GDbos[i][9], nowprice) ){
                printf("BuyLimit order sended successfully ") ;
                G.GDticket[i]      =  trade.ResultOrder() ;
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
void MonitorPendingOrder(Golder& G){ // check the period where the ticket is at is exsiting or not
    for(int i=0; i<PERIODX4; ++i){
        ulong ticket    = G.GDticket[i];
        int  ticketing  = G.GDticketIng[i] ;
        int   Itv       = G.GDticketItv[i];
        if(ticketing==0 || ticketing==2) continue ;
        else{
            if(Itv != G.GD[i][2] ){
                if(trade.OrderDelete(ticket)){
                    printf("Order deleted ");
                    G.GDticket[i]      = 0 ;
                    G.GDticketCode[i]  = 0 ;
                    G.GDticketPrd[i]   = 0 ;
                    G.GDticketItv[i]   = 0 ;
                    G.GDticketsbd_t[i] = 0 ;
                    G.GDticketsbu_t[i] = 0 ;
                    G.GDticketIng[i]   = 0 ;
                } 
                else printf("Order delete failed. Error code= %d", trade.ResultRetcode()) ;
            }
        }
    }
}
void DeleteMagicPendingOrder(long magic_number){
    int total_orders = OrdersTotal();
    for (int i = total_orders - 1; i >= 0; --i){
        ulong ticket      = OrderGetTicket(i);
        long order_magic  = OrderGetInteger(ORDER_MAGIC); 
        int  ordertype    = OrderGetInteger(ORDER_TYPE) ;
        if (ticket){
            if(order_magic == magic_number){
                if (ordertype == ORDER_TYPE_BUY_LIMIT || ordertype == ORDER_TYPE_SELL_LIMIT || ordertype == ORDER_TYPE_BUY_STOP || ordertype == ORDER_TYPE_SELL_STOP){
                    if(trade.OrderDelete(ticket)) printf("Order in certain magic number is deleted successfully, magic= %I64u, ticket= %I64u", magic_number, ticket) ;
                    else printf("Delete failed, Error code= %d", trade.ResultRetcode() );
                }
            }
        }
        else printf("Can not choose the ticket order %d", i) ;
    }
}

void PositionCheck(Golder& G){ //execute in ISR OnTrade
    int total_postion = PositionsTotal();
    ulong posticket ;
    string possymbol ;
    if(total_postion>0){
        PrintFormat("total_position: %d", total_postion);
        for(int i=0; i<total_postion; ++i){
            posticket = PositionGetTicket(i);
            if(PositionSelectByTicket(posticket)){
                possymbol = PositionGetString(POSITION_SYMBOL);
                if(possymbol != G.symbol) continue;
                for(int l=0; l<PERIODX4; ++l){
                    if(G.GDticket[l]==0) continue ;
                    if(posticket == G.GDticket[l]) G.GDticketIng[l] = 2;
                    else continue;
                }
            }
            else printf("posselect failed, Error code= %d", trade.ResultRetcode() );
        }
    }
}

void DealCheck(Golder& G, const datetime& fromtime,  DealGolder& DG, const string& sectorname){
    datetime ct = TimeCurrent();
    ulong deal_ticket;           
    ulong dealorder  ;
    long  dealmagic  ;
    string dealsymbol;
    double dealprofit;
    double dealvolume;
    int    dealentry ;
    string fromtime_str = TimeToString(fromtime, TIME_DATE|TIME_MINUTES);
    if(HistorySelect(fromtime, ct)){
        uint total=HistoryDealsTotal();
        PrintFormat("total_history ranged: %d", total);
        for(int i=0; i<total; ++i){
            deal_ticket         = HistoryDealGetTicket(i);
            dealentry           = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
            dealsymbol          = HistoryDealGetString(deal_ticket, DEAL_SYMBOL);
            if(dealsymbol!= G.symbol ) continue ;
            if(dealentry != DEAL_ENTRY_OUT ) continue ;
            dealmagic           = HistoryDealGetInteger(deal_ticket, DEAL_MAGIC);  
            dealorder           = HistoryDealGetInteger(deal_ticket, DEAL_ORDER); 
            dealvolume          = HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
            dealprofit          = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
            for(int l=0; l<PERIODX4; ++l){
                if(G.GDticket[l]==0) continue ;
                if(dealorder == G.GDticket[l]){
                    printf("Get right ticket!") ;
                    DG.dealmagic       = dealmagic;
                    DG.dealorder       = dealorder;
                    DG.dealsymbol      = dealsymbol;
                    DG.dealcode        = G.GDticketCode[l];
                    DG.dealprd         = G.GDticketPrd[l];
                    DG.dealitv         = G.GDticketItv[l];
                    DG.dealsbd_t       = G.GDticketsbd_t[l];
                    DG.dealsbu_t       = G.GDticketsbu_t[l];
                    DG.dealvolume      = dealvolume;
                    DG.dealprofit      = dealprofit;
                    DG.DealWriteOut(sectorname);

                    G.GDticket[l]      = 0 ;
                    G.GDticketCode[l]  = 0 ;
                    G.GDticketPrd[l]   = 0 ;
                    G.GDticketItv[l]   = 0 ;
                    G.GDticketsbd_t[l] = 0 ;
                    G.GDticketsbu_t[l] = 0 ;
                    G.GDticketIng[l]   = 0 ; //so that resending data can start
                } 
            }           
        }
    }
    else printf("no history records after %s", fromtime_str );
}

#endif
