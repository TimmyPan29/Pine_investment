#include "Helper.mqh"

int BarTimeCal(Helper helper, datetime dt) {
    helper.name = "BarTimeCal";
    dt          =  TimeHour(dt)*60 + TimeMinute(dt); 
    return int(dt)
}