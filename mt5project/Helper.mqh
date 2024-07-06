#ifndef __HELPER_MQH__
#define __HELPER_MQH__

#define __OANDA_FOREX         17
#define __OANDA_CFD           17
#define __OANDA_CRYPTO        17
#define __BINANCE_CRYPTO      0
#define __SAXO_FOREX          17
#define __SAXO_CFD            18
#define __SAXO_CRYPTO         17
#define __EIGHTCAP_FOREX      0
#define __EIGHTCAP_CFD        1
#define __EIGHTCAP_CRYPTO     0
#define __TIME00_00           0
#define __DAYMIN              1440
#define __LEVEL4SBUMASK       0xf0000000
#define __LEVEL2SBUMASK       0x0f000000  
#define __LEVEL3SBUMASK       0x00f00000
#define __LEVEL1SBUMASK       0x000f0000
#define __LEVEL1SBDMASK       0x0000f000
#define __LEVEL2SBDMASK       0x00000f00
#define __LEVEL3SBDMASK       0x000000f0
#define __LEVEL4SBDMASK       0x0000000f
#define __7f10fMASK           0xfffffff0
#define __701ffMASK           0x0000000f
enum Timebase{
    OANDA_FOREX,    
    OANDA_CFD,    
    OANDA_CRYPTO,   
    BINANCE_CRYPTO, 
    SAXO_FOREX,     
    SAXO_CFD,       
    SAXO_CRYPTO,    
    EIGHTCAP_FOREX, 
    EIGHTCAP_CFD,   
    EIGHTCAP_CRYPTO,
    TIME00_00
};
struct Helper{
    string      name;
    int BarTimeCal(datetime dt);
    int Extime();
    int Inputtimebase(Timebase tb);
    string Inputtimetostring(Timebase tb);
};


int Helper::BarTimeCal(datetime dt) {
    name        = "BarTimeCal";
    dt          =  (dt%86400);
    return int(dt);
}
int Helper::Extime(){
    int d ;
    name = "serverTimeZoneCal";
    datetime serverTime = TimeCurrent(); 
    datetime utcTime    = TimeGMT();
    d = (serverTime - utcTime)/3600 ;
    return d ;
}
int Helper::Inputtimebase(Timebase tb){
    name = "Inputtimebase";
    switch (tb){
        case OANDA_FOREX:
            return __OANDA_FOREX ;
        case OANDA_CFD:
            return __OANDA_CFD ;
        case OANDA_CRYPTO:
            return __OANDA_CRYPTO ;
        case BINANCE_CRYPTO:
            return __BINANCE_CRYPTO ;
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
    name = "Inputtimetostring";
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
            return "SAXO_CRYPTO" ;
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


#endif