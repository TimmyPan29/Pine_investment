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
#define PERIOD    360
#define PERIODX4  1440
#define PERIODX8  2880
#define PERIODX12 4320
#define PERIODX16 5760
#define BASESEC   86400
enum Barchoice{
     Bar100,
     Bar300,
     Bar500,
     Bar1000
};
struct Helper{
    string      name;
    int BarTimeCal(datetime dt);
    int Extime();
    int ServerExtime();
    int Bartoint(Barchoice bar);
    int TurnMin(datetime dt);
    int TurnMinX2(datetime dt);
    int TurnMinX3(datetime dt);
    int TurnMinX4(datetime dt);
    int GetQuo(int minute, int htfint);
    //int GetRm(int minute, int htfint);
};
int Helper::Bartoint(Barchoice bar){
   switch(bar){
   case Bar100: return 7;
   case Bar300: return 8;
   case Bar500: return 9;
   case Bar1000:return 10;
   default: return 10 ;
   }
}
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
int Helper::TurnMin(datetime dt){
    name = "TurnMin" ;
    return (dt%(BASESEC))/60; //one day
}
int Helper::TurnMinX2(datetime dt){ //two days
    name = "TurnMin" ;
    return (dt%(BASESEC<<1))/60;
}
int Helper::TurnMinX3(datetime dt){ //three days
    name = "TurnMin" ;
    return (dt%(BASESEC*3))/60;
}
int Helper::TurnMinX4(datetime dt){ //four days
    name = "TurnMin" ;
    return (dt%(BASESEC<<2))/60;
}
int Helper::GetQuo(int minute, int htfint){
    name = "GetQuo" ;
    float m =float(minute);
    float h =float(htfint);
    return MathFloor(m/h) ;
}
// int Helper::GetRm(int minute, int htfint){
//     name = "GetRm" ;
//     return (minute%htfint) ;
// }
#endif