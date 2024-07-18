#ifndef __HANDLER_ONTICK_MQH__
#define __HANDLER_ONTICK_MQH__
struct comedata{
    double      lastprice;
    double      nowprice;
    datetime    lasttime;
    datetime    nowtime;
};

class Handler_ontick{
private:
    comedata    &cd;
    MqlTick     mtick;
    bool        mtickflag;
public:
    Handler_ontick(comedata &ini, MqlTick mk, bool fg):cd(ini),mtick(mk),mtickflag(fg) {}//at start, let lastprice=nowprice
    void Update(comedata &cd){
        if(SymbolInfoTick(_Symbol, mtick)){
            cd.nowprice = mtick.last;
            cd.nowtime  = mtick.time;
        }
        if(cd.nowtime != cd.lasttime){
            cd.lastprice = cd.nowprice;
            cd.lasttime  = cd.lasttime;
            mtickflag    = true;
        }
        else{
            mtickflag    = false;
        }

    bool Getflag(){
        return mtickflag;
    }
    
};


#endif