//@version=5
indicator("4level_line", shorttitle="BOStest", overlay=true) 
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
var int numbershift = 2
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
var float Remainder2Bar = na
var int index = 0
var string str_timeframe = na
var float flt_timeframe = na 
var string TICKERID = syminfo.tickerid
var arrayclose = array.new<float>(0)
var arraybuff = array.new<float>(0)

//figure variable 
var label Label_SBU_1over4 = na
var label Label_SBD_1over4 = na
var label Label_SBU_2over4 = na
var label Label_SBD_2over4 = na
var label Label_SBU_3over4 = na
var label Label_SBD_3over4 = na
var label Label_SBU_4over4 = na
var label Label_SBD_4over4 = na
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
    float boscount = 0
    float Barcount = 0
    float RmnBarcount = 0
//**
type BOS_Type 
    int slope1 = na
    int slope2 = na
    int state_1over4 = 4 //SURRD defalut
    int state_2over4 = 4 //SURRD defalut
    int state_3over4 = 4 //SURRD defalut
    int state_4over4 = 4 //SURRD defalut
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
    float Buff_close1_1over4 = 0
    float Buff_close2_1over4 = 0
    float Buff_close3_1over4 = 0
    float Buff_close1_2over4 = 0
    float Buff_close2_2over4 = 0
    float Buff_close3_2over4 = 0
    float Buff_close1_3over4 = 0
    float Buff_close2_3over4 = 0
    float Buff_close3_3over4 = 0
    float Buff_close1_4over4 = 0
    float Buff_close2_4over4 = 0
    float Buff_close3_4over4 = 0
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
    this.state_1over4 := SURRD
    this.state_2over4 := SURRD
    this.state_3over4 := SURRD
    this.state_4over4 := SURRD
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
    this.Buff_close1_1over4 := 0
    this.Buff_close2_1over4 := 0
    this.Buff_close3_1over4 := 0
    this.Buff_close1_2over4 := 0
    this.Buff_close2_2over4 := 0
    this.Buff_close3_2over4 := 0
    this.Buff_close1_3over4 := 0
    this.Buff_close2_3over4 := 0
    this.Buff_close3_3over4 := 0
    this.Buff_close1_4over4 := 0
    this.Buff_close2_4over4 := 0
    this.Buff_close3_4over4 := 0

method init_Flag(Flag_Type this) =>
    this.SizeFlag := na
    this.GoFlag := false
    this.resetFlag := false
    this.plotFlag := false
    this.diffFlag := false
    this.bosFlag := false
    this.jumpFlag := false
//**
method BOScal_level1(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = 0
    while f.bosFlag 
        if((not na(b.close_SBU_1over4)) and (not na(b.close_SBD_1over4)) )//有天地 留在SURRD 依此類推
            b.state_1over4 := SURRD
        else if ((na(b.close_SBU_1over4)) and (not na(b.close_SBD_1over4)) )
            b.state_1over4 := NOSKY
        else
            b.state_1over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_1over4 := b.Buff_close2_1over4
            b.Buff_close2_1over4 := b.Buff_close3_1over4 
            b.Buff_close3_1over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_1over4 - b.Buff_close1_1over4>0? 1 : -1
            b.slope2 := b.Buff_close3_1over4 - b.Buff_close2_1over4>0? 1 : -1
            switch b.state_1over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_1over4 := b.Buff_close2_1over4
                        b.index_key1_1over4 := index-1
                    if(b.Buff_close3_1over4>b.close_SBU_1over4)
                        b.close_SBU_1over4 := na
                        b.close_SBD_1over4 := b.Buff_key1_1over4
                        b.index_SBD_1over4 := index
                    else if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.close_SBD_1over4 := na
                        b.close_SBU_1over4 := b.Buff_key1_1over4
                        b.index_SBU_1over4 := index
                    else //maintain SURRD
                        label.new(bar_index,low,"still in bounded box")
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index
                        b.close_SBU_1over4 := b.Buff_key2_1over4
                        b.index_SBU_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                    if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.Buff_key1_1over4 := b.Buff_close2_1over4
                        b.close_SBD_1over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index
                        b.close_SBD_1over4 := b.Buff_key2_1over4
                        b.index_SBD_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                    if(b.Buff_close3_1over4>b.close_SBU_1over4)
                        b.Buff_key1_1over4 := b.Buff_close2_1over4
                        b.close_SBU_1over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 1
            break
        //end while
        count := j%4==0? count+1 : count
        if((count == c.Barcount and f.diffFlag) or (count == 3 and not(f.diffFlag))) //it means diff<0, jump over the day or today is at the end. 
            break
    //end while
//end method   

//*****var initialization*****//
var timeInfo = CurrentTime_Type.new(na, na, na, na, na, na, na, na,na,na,na)
var countInfo = Count_Type.new(0,0,0,0,0) // levelcount count1 boscount Barcount,RmnBarcount
var flagInfo = Flag_Type.new(na,false,false,false,false,false) //size ,go,resetFlag,plotFlag, diffFlag, jumpFlag
var BOSInfo = BOS_Type.new()
if barstate.isfirst // execute once when script started
    timeInfo.currentperiod := str.tonumber(timeframe.period)
    timeInfo.currentperiod_div4 := timeInfo.currentperiod / 4
flt_timeframe := str.tonumber(timeframe.period)/4
str_timeframe := str.tostring(flt_timeframe)
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

arrayclose := request.security_lower_tf(syminfo.tickerid,str_timeframe,close)
flagInfo.SizeFlag := array.size(arrayclose)==4? true : false
Quotient := math.floor(float(DAY2MINUTE)/timeInfo.currentperiod)
Remainder := DAY2MINUTE%timeInfo.currentperiod
Remainder2Bar := Remainder%timeInfo.currentperiod_div4+1
testarray := arrayclose    
if(barstate.isfirst)
    for i=0 to 4*(4)-1
        array.unshift(arraybuff,array.get(arrayclose,0))
    countInfo.boscount := 0
    countInfo.Barcount := 3
    flagInfo.bosFlag := true
    BOScal_level1(BOSInfo,countInfo,flagInfo,arraybuff,Quotient,index)
    countInfo.boscount := countInfo.Barcount
index += 1
//1over4 start 

if(na(Label_SBU_1over4)==false)
    label.delete(Label_SBU_1over4)
Label_SBU_1over4 := label.new(x=last_bar_index - numbershift, y=BOSInfo.close_SBU_1over4, text="SBU_1over4: " + str.tostring(BOSInfo.close_SBU_1over4), xloc = xloc.bar_index, yloc=yloc.price,color=color.red) 

if(na(Label_SBD_1over4)==false)
    label.delete(Label_SBD_1over4)
Label_SBD_1over4 := label.new(x=last_bar_index - numbershift, y=BOSInfo.close_SBD_1over4, text="SBD_1over4: " + str.tostring(BOSInfo.close_SBD_1over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up)
//1over4 end
if bar_index == last_bar_index - numbershift
    //label.new(last_bar_index-numbershift, high, str.tostring(arrayclose),color orange,size := size.normal)
    buffyear := year(time)
    buffmonth := month(time)
    buffday := dayofmonth(time) 
    buffhour := hour(time)
    buffmin := minute(time)
    line.new(x1=last_bar_index - numbershift, y1=BOSInfo.close_SBU_1over4, x2=last_bar_index - numbershift +100, y2=BOSInfo.close_SBU_1over4, width=2, color=color.black)
    line.new(x1=last_bar_index - numbershift, y1=BOSInfo.close_SBD_1over4, x2=last_bar_index - numbershift +100, y2=BOSInfo.close_SBD_1over4, width=2, color=color.black)
if bar_index == last_bar_index - numbershift
    label.new(bar_index, low-0.05, "\n label bufftime at : "+ str.tostring(buffyear)+ "\t" +str.tostring(buffmonth) +"\t" + str.tostring(buffday)+"\t" + str.tostring(buffhour)+"\t" + str.tostring(buffmin)+"\n\t OANDA?\t" + str.tostring(str.contains(syminfo.tickerid,"OANDA"))+"\n period=\t" + str.tostring(timeInfo.currentperiod_div4) +"\n state=\t" + str.tostring(BOSInfo.state_1over4)+"\n testint=\t" + str.tostring(BOSInfo.Buff_close3_1over4),style=label.style_triangledown,color = color.green)