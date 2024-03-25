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
//  *the turnpoint is called key2 anyway. 
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

//common variable
var int numbershift := last_bar_index
var int state = na
var int nextstate = na
var int statelevel = na
var float Quotient = na
var int Remainder = na
var float diff = na
var float start_low = na
var float start_high = na
var string TICKERID = syminfo.tickerid
var array<float> arrayclose = array.new(0)
var array<float> arraybuff = array.new(0)

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

//test variable
var label test = na
var int testint = 0
var string teststr = na
var bool testbool = na
//**

//time variable
type CurrentTime_Type
    float currentperiod
    float currentperiod_div4
    string currentperiod_div4_str
    int currentYear 
    int currentMon
    int currentDay
    int currentHr
    int currentMin
    int HrMin2Min
    float starttime
    int HrMin2Min2
    float lasttime
//**

//Flag
type Flag_Type
    bool SizeFlag
    bool GoFlag
    bool resetFlag 
//**
type Count_Type
    int levelcount = 0
    int count1 = 0 
    int count2 = 0
    int Barcount = 0
    int RmnBarcount = 0
method init_count(Count_Type this) =>
    this.levelcount := 0
    this.count1 := 0 
    this.count2 := 0
    this.Barcount := 0
    this.RmnBarcount := 0
//**

//variable
type BOS_Type
    int slope1 = na
    int slope2 = na
    int index_key1_1over4 = na
    int index_key2_1over4 = na
    int index_key1_2over4 = na
    int index_key2_2over4 = na
    int index_key1_3over4 = na
    int index_key2_3over4 = na
    int index_key1_4over4 = na
    int index_key2_4over4 = na
    int index_SBU_1over4 = 0
    int index_SBD_1over4 = 0
    int index_SBU_2over4 = 0
    int index_SBD_2over4 = 0
    int index_SBU_3over4 = 0
    int index_SBD_3over4 = 0
    int index_SBU_4over4 = 0
    int index_SBD_4over4 = 0
    float close_SBU_1over4 = 0
    float close_SBD_1over4 = 0
    float close_SBU_2over4 = 0
    float close_SBD_2over4 = 0
    float close_SBU_3over4 = 0
    float close_SBD_3over4 = 0
    float close_SBU_4over4 = 0
    float close_SBD_4over4 = 0
    float Buff_key1_1over4 = na
    float Buff_key2_1over4 = na
    float Buff_key1_2over4 = na
    float Buff_key2_2over4 = na
    float Buff_key1_3over4 = na
    float Buff_key2_3over4 = na
    float Buff_key1_4over4 = na
    float Buff_key2_4over4 = na

method init_BOS(BOS_Type this) =>
    this.slope1 := na
    this.slope2 := na
    this.index_key1_1over4 := na
    this.index_key2_1over4 := na
    this.index_key1_2over4 := na
    this.index_key2_2over4 := na
    this.index_key1_3over4 := na
    this.index_key2_3over4 := na
    this.index_key1_4over4 := na
    this.index_key2_4over4 := na
    this.index_SBU_1over4 := 0
    this.index_SBD_1over4 := 0
    this.index_SBU_2over4 := 0
    this.index_SBD_2over4 := 0
    this.index_SBU_3over4 := 0
    this.index_SBD_3over4 := 0
    this.index_SBU_4over4 := 0
    this.index_SBD_4over4 := 0
    this.close_SBU_1over4 := 0
    this.close_SBD_1over4 := 0
    this.close_SBU_2over4 := 0
    this.close_SBD_2over4 := 0
    this.close_SBU_3over4 := 0
    this.close_SBD_3over4 := 0
    this.close_SBU_4over4 := 0
    this.close_SBD_4over4 := 0
    this.Buff_key1_1over4 := na
    this.Buff_key2_1over4 := na
    this.Buff_key1_2over4 := na
    this.Buff_key2_2over4 := na
    this.Buff_key1_3over4 := na
    this.Buff_key2_3over4 := na
    this.Buff_key1_4over4 := na
    this.Buff_key2_4over4 := na
//**
var timeInfo = CurrentTime_Type.new(na, na, "", na, na, na, na, na, na,na,na,na)
var countInfo = Count_Type.new(0,0,0,0) // levelcount count1 count2 Barcount
var flagInfo = Flag_Type.new(na,false,true) //size ,go,resetFlag
var BOSInfo = BOS_Type.new()

if barstate.isfirst // 只在脚本加载时执行一次
    timeInfo.currentperiod := str.tonumber(timeframe.period)
    timeInfo.currentperiod_div4 := timeInfo.currentperiod / 4
    timeInfo.currentperiod_div4_str := str.tostring(timeInfo.currentperiod_div4)
timeInfo.currentYear := year(time)
timeInfo.currentMon := month(time)
timeInfo.currentDay := dayofmonth(time) 
timeInfo.currentHr := hour(time) 
timeInfo.currentMin := minute(time) 
timeInfo.HrMin2Min := timeInfo.currentHr * 60 + timeInfo.currentMin
if(timeInfo.HrMin2Min<FOREX_OANDATIME and HrMin2Min>=0)
    HrMin2Min2 := HrMin2Min+DAY2MINUTE
else
    HrMin2Min2 := HrMin2Min
////**state ctrl
//  *
//  *//
countInfo.Barcount += 1
ReqClose := request.security_lower_tf(syminfo.tickerid,currentperiod_div4,close)
flagInfo.SizeFlag := array.size(ReqClose)==4? true : false
Quotient := math.floor(float(DAY2MINUTE)/currentperiod)
Remainder := DAY2MINUTE%currentperiod

if(timeInfo.HrMin2Min2 == FOREX_OANDATIME and flagInfo.GoFlag == false and str.contains(TICKERID,"OANDA"))
            flagInfo.resetFlag := false
if(flagInfo.resetFlag) //Barcount = bar_index+1, example Barcount=1,bar_index=0
    state := RESET
else
    state := nextstate
    
switch state
    RESET =>
        nextstate := ARRAYGEN
    ARRAYGEN =>

    SURRD => 
        if(level==1)
            nextstate := 
        if(level)

////**data flow
//  *
//  *//
switch state
    RESET =>
        init_BOS(BOSInfo)
        init_count(countInfo)
    ARRAYGEN =>
        countInfo.Barcount := 0
        timeInfo.starttime := HrMin2Min2
        timeInfo.lasttime := FOREX_OANDATIME
        flagInfo.GoFlag := true
        if(flagInfo.GoFlag)
            if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 != FOREX_OANDATIME)
                countInfo.Barcount := 1+(timeInfo.HrMin2Min2-FOREX_OANDATIME)/timeInfo.currentperiod
                timeInfo.starttime := FOREX_OANDATIME + (countInfo.Barcount-1)*timeInfo.currentperiod
                diff := countInfo.Barcount
            else if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 == FOREX_OANDATIME)
                countInfo.Barcount := 1
                diff := 0
                timeInfo.starttime := timeInfo.HrMin2Min2
            else
                if(timeInfo.starttime + timeInfo.currentperiod == timeInfo.HrMin2Min2)
                    diff := 1
                    timeInfo.Barcount := timeInfo.Barcount + diff
                    timeInfo.lasttime := timeInfo.starttime
                    timeInfo.starttime += timeInfo.currentperiod
                else
                    timeInfo.lasttime := timeInfo.starttime
                    diff := (timeInfo.HrMin2Min2-timeInfo.lasttime)/timeInfo.currentperiod
                    if(diff<0)
                        countInfo.RmnBarcount := (FOREX_OANDATIME + timeInfo.currentperiod*Quotient-timeInfo.lasttime)/timeInfo.currentperiod
                        GoFlag := false
                        diff := countInfo.RmnBarcount
                        //這個情況表示新的開市日有可能從17:00 或17:28之類的開始 要討論
                    else
                        countInfo.Barcount += diff
                        timeInfo.lasttime := timeInfo.HrMin2Min2
                        timeInfo.starttime := FOREX_OANDATIME + (countInfo.Barcount-1)*timeInfo.currentperiod
    SURRD=>





////**custom define function
//  *
//  *//

