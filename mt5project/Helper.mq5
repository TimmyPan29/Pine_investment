#include "Helper.mqh"

int Helper::BarTimeCal(datetime dt) {
    helper.name = "BarTimeCal";
    dt          =  TimeHour(dt)*60 + TimeMinute(dt); 
    return int(dt);
}
int Helper::Extime(Helper& helper){
    int d ;
    helper.name = "serverTimeZoneCal";
    datetime serverTime = TimeCurrent(); 
    datetime utcTime    = TimeGMT();
    d = (serverTime - utcTime)/3600 ;
    return d ;
}
int Helper::Inputtimebase(Timebase tb){
    helper.name = "Inputtimebase";
    switch (tb){
        case OANDA_FOREX:
            return __OANDA_FOREX ;
        case OANDA_CFD:
            return __OANDA_CFD ;
        case OANDA_CRYPTO:
            return __OANDA_CRYPTO ;
        case BINANCE_CRYPTO:
            return __INANCE_CRYPTO ;
        case SAXO_FOREX:
            return __SAXO_FOREX ;
        case SAXO_CFD:
            return __SAXO_CFD ;
        case SAXO_CRYPTO:
            return __SAXO_CRYPTO ;
        case EIGHTCAP_FOREX:
            return __EIGHTCAP_FOREX ;
        case EIGHTCAP_CFD:
            return __EIGHTCAP_CFD ;
        case EIGHTCAP_CRYPTO:
            return __EIGHTCAP_CRYPTO ;
        default:
            return __TIME00_00   ;
    }
}
string Helper::Inputtimetostring(Timebase tb){
    helper.name = "Inputtimetostring";
    switch (tb){
        case OANDA_FOREX:
            return "OANDA_FOREX" ;
        case OANDA_CFD:
            return "OANDA_CFD" ;
        case OANDA_CRYPTO:
            return "OANDA_CRYPTO" ;
        case BINANCE_CRYPTO:
            return "INANCE_CRYPTO" ;
        case SAXO_FOREX:
            return "SAXO_FOREX" ;
        case SAXO_CFD:
            return "SAXO_CFD" ;
        case SAXO_CRYPTO:
            return "AXO_CRYPTO" ;
        case EIGHTCAP_FOREX:
            return "EIGHTCAP_FOREX" ;
        case EIGHTCAP_CFD:
            return "EIGHTCAP_CFD" ;
        case EIGHTCAP_CRYPTO:
            return "IGHTCAP_CRYPTO" ;
        default:
            return "TIME00_00"   ;
    }
}