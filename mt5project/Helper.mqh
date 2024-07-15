#ifndef __HELPER_MQH__
#define __HELPER_MQH__

#define __OANDA_FOREX         1020
#define __OANDA_CFD           1020
#define __OANDA_CRYPTO        1020
#define __BINANCE_CRYPTO      0
#define __SAXO_FOREX          1020
#define __SAXO_CFD            1080
#define __SAXO_CRYPTO         1020
#define __EIGHTCAP_FOREX      0
#define __EIGHTCAP_CFD        60
#define __EIGHTCAP_CRYPTO     0
#define __TIME00_00           0
#define __DAYMIN              1440
#define __LEVEL4SBDMASK       0xf0000000
#define __LEVEL3SBDMASK       0x0f000000  
#define __LEVEL2SBDMASK       0x00f00000
#define __LEVEL1SBDMASK       0x000f0000
#define __LEVEL1SBUMASK       0x0000f000
#define __LEVEL2SBUMASK       0x00000f00
#define __LEVEL3SBUMASK       0x000000f0
#define __LEVEL4SBUMASK       0x0000000f
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
    int ServerExtime();
    int Inputoffset(Timebase tb);
    int Inputtimeoffset(Timebase tb);
    int TurnMin(datetime dt);
    int GetQuo(int minute, int htfint);
    int GetRm(int minute, int htfint);
};


int Helper::BarTimeCal(datetime dt) {
    name        = "BarTimeCal";
    dt          =  (dt%86400);
    return int(dt);
}
int Helper::Extime(){
    MqlDateTime tm={}; 
    name = "localoffsetTimeZoneCal";
    datetime    time1=TimeLocal();            
    datetime    time2=TimeGMT(tm);           
    int         shift=int(time1-time2)/3600;
    return shift ;
}
int Helper::ServerExtime(){
    MqlDateTime tm={}; 
    name = "localoffsetTimeZoneCal";
    datetime    time1=TimeCurrent();            
    datetime    time2=TimeGMT(tm);           
    int         shift=int(time1-time2)/3600;
    return shift ;
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
int Helper::Inputoffset(Timebase tb){
    name = "Inputoffset";
    switch (tb){
        case OANDA_FOREX:
            return 6 ;
        case OANDA_CFD:
            return 6 ;
        case OANDA_CRYPTO:
            return 6 ;
        case BINANCE_CRYPTO:
            return 6 ;
        case SAXO_FOREX:
            return 6 ;
        case SAXO_CFD:
            return 6 ;
        case SAXO_CRYPTO:
            return 6 ;
        case EIGHTCAP_FOREX:
            return 6 ;
        case EIGHTCAP_CFD:
            return 6 ;
        case EIGHTCAP_CRYPTO:
            return 6 ;
        default:
            return 6 ;
    }
}
int Helper::Inputtimeoffset(Timebase tb){
    name = "Inputtimeoffset";
    switch (tb){
        case OANDA_FOREX:
            return 5 ;
        case OANDA_CFD:
            return 5 ;
        case OANDA_CRYPTO:
            return 5 ;
        case BINANCE_CRYPTO:
            return 5 ;
        case SAXO_FOREX:
            return 5 ;
        case SAXO_CFD:
            return 5 ;
        case SAXO_CRYPTO:
            return 5 ;
        case EIGHTCAP_FOREX:
            return 5 ;
        case EIGHTCAP_CFD:
            return 5 ;
        case EIGHTCAP_CRYPTO:
            return 5 ;
        default:
            return 5 ;
    }
}
int Helper::TurnMin(datetime dt){
    name = "TurnMin" ;
    return (dt%86400)/60;
}
int Helper::GetQuo(int minute, int htfint){
    name = "GetQuo" ;
    float m =float(minute);
    float h =float(htfint);
    return MathFloor(m/h) ;
}
int Helper::GetRm(int minute, int htfint){
    name = "GetRm" ;
    return (minute%htfint) ;
}
#endif