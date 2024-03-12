////**up-break, down-break, surrounded between sky and ground
// 
//  *local parameter : section where all the state is.
//  *NOSKY or NOGRD : bounded to boundedless
//  *state3 : maintain bounded
//  *state4 : maintain non-bounded or non-bounded to bounded
//  *state5 : plot
//  *破的轉點一律叫key2，缺少突破的控制訊號
//  *支撐被破之後 SBU要馬上跟上，而在嚴格遞減的情況下，此時的SBD不可以長出來 
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
currentperiod_div4_str = str.tostring(str.tonumber(currentperiod)/4)
currentYear = year(time)
currentMon = month(time)
currentDay = dayofmonth(time) //必須對準交易所的第幾天
currentHr = hour(time) // hour 和 minute是對準交易所得時差
currentMin = mimute(time)
var int summerhour = 6 
//**

//common variable
var int Number_index = na
var int NumShift = 0
var int state = na
var int nextstate = na
var int statelevel = na
var int count = na 
var int level = na 
var int BarCount = 0
var float Quotient = na
var int Remainder = na
var bool GoGoFlag = na
var float start_low = na
var float start_high = na
var bool SizeFlag = na
var array<float> arrayclose = array.new(currentperiod_div4,0)
var array<float> arraybuff =  array.new(20,0)
//**

//figure variable 
var line line_start = na
var label label_start  = na
var line Line_Bar_1over4 = na
var label Label_Bar_1over4  = na
var label Label_SBU_1over4 = na
var label Label_SBD_1over4 = na
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
var int slope1 = na
var int slope2 = na
var int index_key1_1over4 = na
var int index_key2_1over4 = na
var int index_SBU_1over4 = 0
var int index_SBD_1over4 = 0
var float close_SBU_1over4= 0
var float close_SBD_1over4= 0
var float Buff_key1_1over4 = na
var float Buff_key2_1over4 = na
//**

////**state ctrl
//  *
//  *//
BarCount := BarCount+1
ReqClose := request.security_lower_tf(syminfo.tickerid,currentperiod_div4,close)
SizeFlag := array.size(ReqClose)==4? true : false
if(BarCount != 0 and currentYear==2023 and currentMon==8 and currentDay==7 and currentHr==5) //BarCount = bar_index+1, example BarCount=1,bar_index=0
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

