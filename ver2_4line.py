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
var int numbershift = 100
var int state = na
var int nextstate = na
var int statelevel = na
var float Quotient = na
var float Remainder = na
var float diff = na
var float start_low = na
var float start_high = na
var int buffyear = na
var int buffmonth = na
var int buffday = na
var int buffhour = na
var int buffmin = na
var int arraysize = na
var int Remainder2Bar = na
var int index = 0
var string TICKERID = syminfo.tickerid
var arrayclose = array.new<float>(0)
var arraybuff = array.new<float>(0)

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
var const int PLOT = 3
var const int SURRD = 4
var const int NOSKY = 5
var const int NOGRD = 6
var const int DAY2MINUTE = 1440
var const int FOREX_OANDATIME = 1020
var const int FOREX_OPENTIMEEIGHTCAP = 0

//test variable
var label test = na
var int testint = 0
var string teststr = na
var bool testbool = na
var float testfloat = na
var testarray = array.new<float>(0)
var float testcount = na

//**

//time variable
type CurrentTime_Type
    float currentperiod
    float currentperiod_div4
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
    bool plotFlag
    bool diffFlag
    bool bosFlag
    bool jumpFlag
//**
type Count_Type
    int levelcount = 0
    float count1 = 0 
    int boscount = 0
    float Barcount = 0
    float RmnBarcount = 0
//**
type BOS_Type 
    int slope1 = na
    int slope2 = na
    int state_1over4 = SURRD //SURRD defalut
    int state_2over4 = SURRD //SURRD defalut
    int state_3over4 = SURRD //SURRD defalut
    int state_4over4 = SURRD //SURRD defalut
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
//**
//*****custom define function*****//
method init_count(Count_Type this) =>
    this.levelcount := 0
    this.count1 := 0 
    this.boscount := 0
    this.Barcount := 0
    this.RmnBarcount := 0

method init_BOS(BOS_Type this) =>
    this.slope1 := na
    this.slope2 := na
    this.state_1over4 = SURRD
    this.state_2over4 = SURRD
    this.state_3over4 = SURRD
    this.state_4over4 = SURRD
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

method init_Flag(Flag_Type this) =>
    this.SizeFlag := na
    this.GoFlag := false
    this.resetFlag := false
    this.plotFlag := false
    this.diffFlag := false
    this.bosFlag := false
    this.jumpFlag := false
//**

var timeInfo = CurrentTime_Type.new(na, na, na, na, na, na, na, na,na,na,na)
var countInfo = Count_Type.new(0,0,0,0,0) // levelcount count1 boscount Barcount,RmnBarcount
var flagInfo = Flag_Type.new(na,false,false,false,false,false) //size ,go,resetFlag,plotFlag, diffFlag, jumpFlag
var BOSInfo = BOS_Type.new()
if barstate.isfirst // execute once when script started
    timeInfo.currentperiod := str.tonumber(timeframe.period)
    timeInfo.currentperiod_div4 := timeInfo.currentperiod / 4
timeframe = str.tostring(str.tonumber(timeframe.period)/4)
timeInfo.currentYear := year(time)
timeInfo.currentMon := month(time)
timeInfo.currentDay := dayofmonth(time) 
timeInfo.currentHr := hour(time) 
timeInfo.currentMin := minute(time) 
timeInfo.HrMin2Min := timeInfo.currentHr * 60 + timeInfo.currentMin
if(timeInfo.HrMin2Min<FOREX_OANDATIME and timeInfo.HrMin2Min>=0)
    timeInfo.HrMin2Min2 := timeInfo.HrMin2Min + DAY2MINUTE
else
    timeInfo.HrMin2Min2 := timeInfo.HrMin2Min

arrayclose := request.security_lower_tf(syminfo.tickerid,timeframe,close)
flagInfo.SizeFlag := array.size(arrayclose)==4? true : false
Quotient := math.floor(float(DAY2MINUTE)/timeInfo.currentperiod)
Remainder := DAY2MINUTE%timeInfo.currentperiod
Remainder2Bar := Remainder%currentperiod_div4+1
testarray := arrayclose
////*****state init*****////
if(timeInfo.HrMin2Min2 == FOREX_OANDATIME and flagInfo.GoFlag == false and str.contains(TICKERID,"OANDA"))
    countInfo.Barcount := 0
    timeInfo.starttime := timeInfo.HrMin2Min2
    timeInfo.lasttime := FOREX_OANDATIME
    flagInfo.GoFlag := true
    nextstate := ARRAYGEN
if(flagInfo.resetFlag) //Barcount = bar_index+1, example Barcount=1,bar_index=0
    state := RESET
else
    state := nextstate

////*****state ctrl*****////
switch state
    RESET =>
        nextstate := ARRAYGEN
    ARRAYGEN =>
        nextstate := flagInfo.plotFlag? PLOT : nextstate
    PLOT =>
        nextstate := na
    => 
        nextstate := nextstate
        

////*****data flow****////
switch state
    RESET =>
        init_Flag(flagInfo)
        init_BOS(BOSInfo)
        init_count(countInfo)
    ARRAYGEN =>
        if(barstate.isfirst)
            init_BOS(BOSInfo)
            init_count(countInfo)
        if(flagInfo.GoFlag)
            if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 != FOREX_OANDATIME)
                countInfo.Barcount := 1+(timeInfo.HrMin2Min2-FOREX_OANDATIME)/timeInfo.currentperiod
                diff := (timeInfo.HrMin2Min2-FOREX_OANDATIME)/timeInfo.currentperiod
                timeInfo.starttime := FOREX_OANDATIME + (countInfo.Barcount-1)*timeInfo.currentperiod
                testfloat := 7
                flagInfo.jumpFlag := true
            else if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 == FOREX_OANDATIME)
                countInfo.Barcount := 1
                diff := 0
                timeInfo.starttime := timeInfo.HrMin2Min2
            else
                if(timeInfo.starttime + timeInfo.currentperiod == timeInfo.HrMin2Min2)
                    diff := 1
                    countInfo.Barcount += diff
                    timeInfo.lasttime := timeInfo.starttime
                    timeInfo.starttime += timeInfo.currentperiod
                else
                    timeInfo.lasttime := timeInfo.starttime
                    diff := (timeInfo.HrMin2Min2-timeInfo.lasttime)/timeInfo.currentperiod
                    flagInfo.jumpFlag := true
                    if(diff<0)
                        countInfo.RmnBarcount := (FOREX_OANDATIME + timeInfo.currentperiod*Quotient-timeInfo.lasttime)/timeInfo.currentperiod
                        countInfo.count1 := (timeInfo.HrMin2Min2-FOREX_OANDATIME)/timeInfo.currentperiod
                        diff := countInfo.RmnBarcount
                        countInfo.Barcount += diff + countInfo.count1 + 1
                        flagInfo.diffFlag := true
                        //這個情況表示新的開市日有可能從17:00 或17:28之類的開始 要討論
                    else
                        countInfo.Barcount += diff
                        timeInfo.lasttime := timeInfo.HrMin2Min2
                        timeInfo.starttime := FOREX_OANDATIME + (countInfo.Barcount-1)*timeInfo.currentperiod

        arraysize := array.size(arrayclose) 
        if(flagInfo.diffFlag) //跳天 往前插值補滿
            for i=0 to 4*(diff+countInfo.count1)-1
                array.unshift(arrayclose,array.get(arrayclose,0))
        else if(flagInfo.jumpFlag and countInfo.Barcount==Quotient+1) //跳 且 跳到當天最後一根
            for i=0 to 4*(diff)-1
                array.unshift(arrayclose,array.get(arrayclose,0))
            for i= 0 to Remainder2Bar-1
                array.push(arrayclose,array.get(arrayclose,arraysize-1))
        else if(not(flagInfo.jumpFlag) and countInfo.Barcount==Quotient+1) //沒有跳 但是已經最後根
            for i= 0 to Remainder2Bar-1
                array.push(arrayclose,array.get(arrayclose,arraysize-1))
        else //沒有跳 一根一根進來 且不是最後一根
            label.new(bar_index,low,"normal one by one input")
            //arrayclose := arrayclose    

        flagInfo.bosFlag := true
        //level1
        //level2
        //level3
        //level4         
        countInfo.boscount := countInfo.Barcount
        if(countInfo.boscount == Quotient+1) //當天資料已經處理完
            timeInfo.lasttime := FOREX_OANDATIME
            countInfo.Barcount := 0
            countInfo.boscount := 0
            flagInfo.diffFlag := false 
        else if(countInfo.boscount > Quotient+1) //表示有跳天
            timeInfo.lasttime := FOREX_OANDATIME
            countInfo.Barcount := countInfo.boscount%(Quotient+1)
            countInfo.boscount := ountInfo.Barcount
            flagInfo.diffFlag := false 
        if bar_index == last_bar_index - numbershift-2 //state要等到倒數第二根跑完arraygen才會進入畫圖狀態，所以倒數第三根nextstate要提前準備
            flagInfo.plotFlag := true
            
    PLOT=>
        if(not na(test))
            label.delete(test)
        test := label.new(last_bar_index-numbershift-1, low, "GoFlag=\t" + str.tostring(flagInfo.GoFlag)+"\n state: "+str.tostring(state)+"\n Barcount: "+str.tostring(countInfo.Barcount)+"\n count1: "+str.tostring(countInfo.count1)+"\n levelcount: "+str.tostring(countInfo.levelcount)+"\n arrayclose : "+str.tostring(testarray)+"\n resetFlag : "+str.tostring(flagInfo.resetFlag)+"\n starttime : "+str.tostring(timeInfo.starttime)+"\n lasttime : "+str.tostring(timeInfo.lasttime)+"\n testfloat : "+str.tostring(testfloat),style=label.style_triangledown,color = color.green)
    =>
        diff := 0

//*****test plot*****//
if bar_index == last_bar_index - numbershift
    //label.new(last_bar_index-numbershift, high, str.tostring(arrayclose),color orange,size = size.normal)
    buffyear := year(time)
    buffmonth := month(time)
    buffday := dayofmonth(time) 
    buffhour := hour(time)
    buffmin := minute(time)
if bar_index == last_bar_index - numbershift
    label.new(last_bar_index, low, "\n label bufftime at : "+ str.tostring(buffyear)+ "\t" +str.tostring(buffmonth) +"\t" + str.tostring(buffday)+"\t" + str.tostring(buffhour)+"\t" + str.tostring(buffmin)+"\n\t OANDA?\t" + str.tostring(str.contains(syminfo.tickerid,"OANDA"))+"\n period=\t" + str.tostring(timeInfo.currentperiod_div4) +"\n state=\t" + str.tostring(state)+"\n testint=\t" + str.tostring(testint),style=label.style_triangledown,color = color.green)
index += 1
////**
//  *
//  *//

