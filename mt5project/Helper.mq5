#include "Helper.mqh"

int Helper::BarTimeCal(Helper helper, datetime dt) {
    helper.name = "BarTimeCal";
    dt          =  TimeHour(dt)*60 + TimeMinute(dt); 
    return int(dt);
}
int Helper::xtimeoffset(Helper helper){
    helper.name = "serverTimeZoneCal";
    datetime serverTime = TimeCurrent(); 
    datetime utcTime    = TimeGMT();
    return (int)(serverTime - utcTime)/3600;
}
int Helper::inputtimebase(Helper helper,Timebase tb){
    switch (tb){
        case OANDA_FOREX:
            return __OANDA_FOREX ;
        case OANDA_CFD:
            return __OANDA_FOREX ;
        case OANDA_CRYPTO:
            return __OANDA_FOREX ;
        case BINANCE_CRYPTO:
            return __OANDA_FOREX ;
        case SAXO_FOREX:
            return __OANDA_FOREX ;
        case SAXO_CFD:
            return __OANDA_FOREX ;
        case SAXO_CRYPTO:
            return __OANDA_FOREX ;
        case EIGHTCAP_FOREX:
            return __OANDA_FOREX ;
        case EIGHTCAP_CFD:
            return __OANDA_FOREX ;
        case EIGHTCAP_CRYPTO:
            return __OANDA_FOREX ;
        default:
            return __TIME00_00   ;
    }
}