////**up-break, down-break, surrounded between sky and ground
// 
//  *local parameter : section where all the state is.
//  *RESET
//  *ARRAY Generator
//  *Comparator
//  * -NOSKY
//  * -NOGRD
//  * -BOUNDED
//  *PLOT
//  *破的轉點一律叫key2，缺少突破的控制訊號
//  *支撐被破之後 SBU要馬上跟上，而在嚴格遞減的情況下，此時的SBD不可以長出來 
//  *如果第一個BAR 不在17:00 (以OANDA為例) 怎麼辦? FLAG來偵測第一個在17時長出來的bar嗎
//  *// 

//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true) 

//**
////**Variable define
//  *time variable
//  *local parameter
//  *variable
//  *common variable
//  *figure variable
//  *test variable
//  *//

//time variable
currentperiod = str.tonumber(timeframe.period)
currentperiod_div4 = currentperiod/4
currentperiod_div4_str = str.tostring(currentperiod_div4)
currentYear = year(time)
currentMon = month(time)
currentDay = dayofmonth(time) //必須對準交易所的第幾天
currentHr = hour(time) // hour 和 minute是對準交易所得時差
currentMin = mimute(time)
var int HrMin2Min = currentHr*60+currentMin 
//**

//common variable
var int Number_index = na
var int NumShift = 0
var int state = na
var int nextstate = na
var int statelevel = na
var int count = 0 
var int level = na 
var int BarCount = 0
var float Quotient = na
var int Remainder = na
var bool GoGoFlag = false
var float start_low = na
var float start_high = na
var bool SizeFlag = na
var string TICKERID = syminfo.tickerid
var array<float> arrayclose = array.new(currentperiod_div4,0)
var array<float> arraybuff = array.new(0)
//**

//figure variable 
var line line_start = na
var label label_start  = na
var line Line_Bar_1over4 = na
var label Label_Bar_1over4  = na
var label Label_SBU_1over4 = na
var label Label_SBD_1over4 = na
//**

//local parameter and constant
var const int RESET = 1
var const int ARRAYGEN = 2
var const int NOSKY = 3
var const int NOGRD = 4
var const int SURRD = 5
var const int PLOT = 6
var const int DAY2MINUTE = 1440
var const int FOREX_OPENTIMEOANDA = 1020
var const int FOREX_OPENTIMEEIGHTCAP = 0
var const int LEVEL1 = 1
var const int LEVEL2 = 2
var const int LEVEL3 = 3
var const int LEVEL4 = 4 
//**

//test variable
var label test = na
var int testint = 0
var string teststr = na
var bool testbool = na
//**

//variable
var int slope1 = na
var int slope2 = na
var int index_key1_1over4 = na
var int index_key2_1over4 = na
var int index_key1_2over4 = na
var int index_key2_2over4 = na
var int index_key1_3over4 = na
var int index_key2_3over4 = na
var int index_key1_4over4 = na
var int index_key2_4over4 = na
var int index_SBU_1over4 = 0
var int index_SBD_1over4 = 0
var int index_SBU_2over4 = 0
var int index_SBD_2over4 = 0
var int index_SBU_3over4 = 0
var int index_SBD_3over4 = 0
var int index_SBU_4over4 = 0
var int index_SBD_4over4 = 0
var float close_SBU_1over4= 0
var float close_SBD_1over4= 0
var float close_SBU_2over4= 0
var float close_SBD_2over4= 0
var float close_SBU_3over4= 0
var float close_SBD_3over4= 0
var float close_SBU_4over4= 0
var float close_SBD_4over4= 0
var float Buff_key1_1over4 = na
var float Buff_key2_1over4 = na
var float Buff_key1_2over4 = na
var float Buff_key2_2over4 = na
var float Buff_key1_3over4 = na
var float Buff_key2_3over4 = na
var float Buff_key1_4over4 = na
var float Buff_key2_4over4 = na
//**

////**state ctrl
//  *
//  *//
BarCount := BarCount+1
ReqClose := request.security_lower_tf(syminfo.tickerid,currentperiod_div4,close)
SizeFlag := array.size(ReqClose)==4? true : false
Quotient := math.floor(float(DAY2MINUTE)/currentperiod)
Remainder := DAY2MINUTE%currentperiod
if(HrMin2Min==1024 and str.contains(TICKERID,"OANDA"))
    GoGoFlag = true
if(HrMin2Min==0 and str.contains(TICKERID,"EIGHTCAP"))
    GoGoFlag = true
if(GoGoFlag) //BarCount = bar_index+1, example BarCount=1,bar_index=0
    state := SURRD
else
    state := nextstate
    
switch state
    RESET =>
        nextstate := SURRD
    SURRD => 
        if(level==1)
            nextstate := 
        if(level)

////**data flow
//  *
//  *//
switch state
    RESET =>
        if(currentperiod==4)
            array.push(arraybuff,array.get())
    SURRD=>


////**custom define function
//  *
//  *//

