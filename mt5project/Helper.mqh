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
enum Timebase{
    OANDA_FOREX    
    OANDA_CFD    
    OANDA_CRYPTO   
    BINANCE_CRYPTO 
    SAXO_FOREX     
    SAXO_CFD       
    SAXO_CRYPTO    
    EIGHTCAP_FOREX 
    EIGHTCAP_CFD   
    EIGHTCAP_CRYPTO
    TIME00_00
};
struct Helper{
    string      name;
    int BarTimeCal(Helper helper, datetime t);
    int Extimeoffset(Helper helper);
    int inputtimebase(Helper helper,Timebase tb);
};



#endif