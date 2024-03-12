////**up-break, down-break, surrounded between sky and ground
// 
//  *local parameter : section where all the state is.
//  *state2 : bounded to boundedless
//  *state3 : maintain bounded
//  *state4 : maintain non-bounded or non-bounded to bounded
//  *state5 : plot
//  *破的轉點一律叫key2，缺少突破的控制訊號
//  *支撐被破之後 SBU要馬上跟上，而在嚴格遞減的情況下，此時的SBD不可以長出來 
//  *// 

//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true) 

//custom variable
currentperiod = timeframe.period
currentperiod_div4 = str.tostring(str.tonumber(currentperiod)/4)
currentYear = year(time)
currentMon= month(time)
currentDay= dayofmonth(time)
var int Number_index = na
var int NumShift = 0

//**
////**Variable define
//  *initialization
//	*local parameter
//  *variable
//  *common variable
//  *test variable
//  *//

//common variable
var int state = na
var int nextstate = na
var line line_start = na
var label label_start  = na
var int BarCountBuff = na
var bool GoGoFlag = na
var int BarCount = 0
var float start_low = na
var float start_high = na
var bool SizeFlag = na
BarCount := BarCount+1
ReqClose = request.security_lower_tf(syminfo.tickerid,currentperiod_div4,close)
SizeFlag := array.size(ReqClose)==4? true : false
var array<float> arrayclose = na
//**

//local parameter
var int RESET = 1
var int NOSKY = 2
var int NOGRD = 3
var int SURRD = 4
var int HOLD = 5
var int PLOT = 6
//**

//test variable
var label test = na
var int testint = 0
var string teststr = na
var bool testbool = na
//**

//variable
var int slope1_1over4 = na
var int slope2_1over4 = na
var int state_1over4 = na
var int index_key1_1over4 = na
var int index_key2_1over4 = na
var int index_SBU_1over4 = 0
var int index_SBD_1over4 = 0
var bool isbreakSBU_1over4 = false
var bool isbreakSBD_1over4 = false
var float close_SBU_1over4= 0
var float close_SBD_1over4= 0
var float Buff_close1_1over4 = na
var float Buff_close2_1over4 = na
var float Buff_close3_1over4 = na
var float Buff_key1_1over4 = na
var float Buff_key2_1over4 = na
var line Line_Bar_1over4 = na
var label Label_Bar_1over4  = na
var label Label_SBU_1over4 = na
var label Label_SBD_1over4 = na
//**

if(BarCount != 0) //BarCount = bar_index+1, example BarCount=1,bar_index=0
    state := SURRD
else
    state := nextstate
    
switch state
    SURRD =>