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
#define __LEVEL4SBUMASK       4026531840 //0xf0000000
#define __LEVEL2SBUMASK       251658240  //0x0f000000  
#define __LEVEL3SBUMASK       15728640   //0x00f00000
#define __LEVEL1SBUMASK       983040     //0x000f0000
#define __LEVEL1SBDMASK       61440      //0x0000f000
#define __LEVEL2SBDMASK       3840       //0x00000f00
#define __LEVEL3SBDMASK       240        //0x000000f0
#define __LEVEL4SBDMASK       15         //0x0000000f
#define __107fMASK            268435455  //0x0fffffff
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