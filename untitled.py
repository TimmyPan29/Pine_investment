//@version=5
indicator("4level_line", shorttitle="fourlinetest", overlay=true) 
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
var int numbershift = na
var int state = na
var int nextstate = na
var int statelevel = na
var float Quotient = na
var float Remainder = na
var float Remainder_3over4 = na
var float Remainder_2over4 = na
var float Remainder_1over4 = na
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
var float fourminus_Remainger2Bar = na
var int index = 0
var string str_timeframe = na
var float flt_timeframe = na 
var string TICKERID = syminfo.tickerid
var string ITSTYPE = syminfo.type
var arrayclose = array.new<float>(0)
var int BASETIME = 0
var string EXCHANGE = na
var float ttlbar = na

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
var const int EIGHTCAP_CRYPTO = 0
var const int EIGHTCAP_FOREX = 0
var const int EIGHTCAP_CFD = 60
var const int SAXO_CRYPTO = 1020
var const int SAXO_FOREX = 1020
var const int SAXO_CFD = 1080
var const int OANDA_CRYPTO = 1020
var const int OANDA_FOREX = 1020
var const int OANDA_CFD= 1020
var const int BINANCE_CRYPTO = 0

//test variable
var label test = na
var int testint = 0
var string teststr = na
var bool testbool = na
var float testfloat = na
var testarray = array.new<float>(0)
var float testcount = na
var bool testbool2 = na
var bool testbool3 = na
var float testfloat2 = na
var float testfloat3 = na
var float testfloat4 = na
var float testfloat5 = na
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
    float levelcount = 0
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
type Delta_Type
    float x_U1o4 = 0
    float x_U2o4 = 0
    float x_U3o4 = 0
    float x_U4o4 = 0
    float x_D1o4 = 0    
    float x_D2o4 = 0    
    float x_D3o4 = 0    
    float x_D4o4 = 0    
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
method BOScal_level1(BOS_Type b, Count_Type c, Flag_Type f, CurrentTime_Type t, array<float> arr, float Quotient, int index, float Remainder, float Remainder_1over4, float ttlbar, float diff) => 
    float NowBar = na
    int j = na
    bool done = false
    bool fg_whenlast = false
    bool fg_whenRmn0 = false
    bool fg_whenRmn0levle1 = false
    int k = na

    k := math.ceil(Remainder/t.currentperiod_div4)
    fg_whenRmn0 := Remainder==0? true : false
    fg_whenRmn0levle1 := Remainder_1over4==0? true : false
    NowBar := c.boscount + diff + c.count1 + c. RmnBarcount
    fg_whenlast := NowBar == ttlbar? true : false
    j := 0
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
                        b.index_SBD_1over4 := b.index_key1_1over4
                    else if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.close_SBD_1over4 := na
                        b.close_SBU_1over4 := b.Buff_key1_1over4
                        b.index_SBU_1over4 := b.index_key1_1over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index-1
                        b.close_SBU_1over4 := b.Buff_key2_1over4
                        b.index_SBU_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                        b.index_key1_1over4 := b.index_key2_1over4
                    if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.close_SBD_1over4 := na
                        b.index_SBD_1over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index-1
                        b.close_SBD_1over4 := b.Buff_key2_1over4
                        b.index_SBD_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                        b.index_key1_1over4 := b.index_key2_1over4
                    if(b.Buff_close3_1over4>b.close_SBU_1over4)
                        b.close_SBU_1over4 := na
                        b.index_SBU_1over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            if(not done)
                if(fg_whenlast and not fg_whenRmn0)
                    j += 1
                    done := j==k? true : false
                else if(fg_whenlast and fg_whenRmn0)
                    j := 3
                    done := true
                else
                    j += 1
            else
                j += 999
            break
        //end while
        c.levelcount := j
        if(j>=4)
            break
    //end while
//end method   
method BOScal_level2(BOS_Type b, Count_Type c, Flag_Type f, CurrentTime_Type t, array<float> arr, float Quotient, int index, float Remainder, float Remainder_2over4, float ttlbar, float diff) => 
    float NowBar = na
    int j = na
    bool done = false
    bool fg_whenlast = false
    bool fg_whenRmn0 = false
    bool fg_whenRmn0levle2 = false
    int k = na

    k := math.ceil(Remainder/t.currentperiod_div4)
    fg_whenRmn0 := Remainder==0? true : false
    fg_whenRmn0levle2 := Remainder_2over4==0? true : false
    NowBar := c.boscount + diff + c.count1 + c. RmnBarcount
    fg_whenlast := NowBar == ttlbar? true : false
    j := 1
    while f.bosFlag 
        if((not na(b.close_SBU_2over4)) and (not na(b.close_SBD_2over4)) )//有天地 留在SURRD 依此類推
            b.state_2over4 := SURRD
        else if ((na(b.close_SBU_2over4)) and (not na(b.close_SBD_2over4)) )
            b.state_2over4 := NOSKY
        else
            b.state_2over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_2over4 := b.Buff_close2_2over4
            b.Buff_close2_2over4 := b.Buff_close3_2over4 
            b.Buff_close3_2over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_2over4 - b.Buff_close1_2over4>0? 1 : -1
            b.slope2 := b.Buff_close3_2over4 - b.Buff_close2_2over4>0? 1 : -1
            switch b.state_2over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_2over4 := b.Buff_close2_2over4
                        b.index_key1_2over4 := index-1
                    if(b.Buff_close3_2over4>b.close_SBU_2over4)
                        b.close_SBU_2over4 := na
                        b.close_SBD_2over4 := b.Buff_key1_2over4
                        b.index_SBD_2over4 := b.index_key1_2over4
                    else if(b.Buff_close3_2over4<b.close_SBD_2over4)
                        b.close_SBD_2over4 := na
                        b.close_SBU_2over4 := b.Buff_key1_2over4
                        b.index_SBU_2over4 := b.index_key1_2over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_2over4 := b.Buff_close2_2over4
                        b.index_key2_2over4 := index-1
                        b.close_SBU_2over4 := b.Buff_key2_2over4
                        b.index_SBU_2over4 := b.index_key2_2over4
                        b.Buff_key1_2over4 := b.Buff_key2_2over4
                        b.index_key1_2over4 := b.index_key2_2over4
                    if(b.Buff_close3_2over4<b.close_SBD_2over4)
                        b.close_SBD_2over4 := na
                        b.index_SBD_2over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_2over4 := b.Buff_close2_2over4
                        b.index_key2_2over4 := index-1
                        b.close_SBD_2over4 := b.Buff_key2_2over4
                        b.index_SBD_2over4 := b.index_key2_2over4
                        b.Buff_key1_2over4 := b.Buff_key2_2over4
                        b.index_key1_2over4 := b.index_key2_2over4
                    if(b.Buff_close3_2over4>b.close_SBU_2over4)
                        b.close_SBU_2over4 := na
                        b.index_SBU_2over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            if(not done)
                if(fg_whenlast and not fg_whenRmn0levle2)
                    j := k
                    done := true
                else if(fg_whenlast and fg_whenRmn0levle2 and fg_whenRmn0)
                    j += 2
                    done := true
                else if(fg_whenlast and fg_whenRmn0levle2 and not fg_whenRmn0)
                    j := 999
                    done := true
                else
                    j += 2
            else
                j := 2222
            break
        //end while
        if(j>=4)
            break
    //end while
//end method  
method BOScal_level3(BOS_Type b, Count_Type c, Flag_Type f, CurrentTime_Type t, array<float> arr, float Quotient, int index, float Remainder, float Remainder_3over4,float ttlbar, float diff) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = na
    if(NowBar>Quotient+1)
        NowBar := NowBar-(Quotient+1)
    if(t.currentperiod!=1440)
        j := NowBar%3==1? 2 : NowBar%3==2? 1 : 0
    else
        j := 2
    while f.bosFlag 
        if((not na(b.close_SBU_3over4)) and (not na(b.close_SBD_3over4)) )//有天地 留在SURRD 依此類推
            b.state_3over4 := SURRD
        else if ((na(b.close_SBU_3over4)) and (not na(b.close_SBD_3over4)) )
            b.state_3over4 := NOSKY
        else
            b.state_3over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_3over4 := b.Buff_close2_3over4
            b.Buff_close2_3over4 := b.Buff_close3_3over4 
            b.Buff_close3_3over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_3over4 - b.Buff_close1_3over4>0? 1 : -1
            b.slope2 := b.Buff_close3_3over4 - b.Buff_close2_3over4>0? 1 : -1
            switch b.state_3over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_3over4 := b.Buff_close2_3over4
                        b.index_key1_3over4 := index-1
                    if(b.Buff_close3_3over4>b.close_SBU_3over4)
                        b.close_SBU_3over4 := na
                        b.close_SBD_3over4 := b.Buff_key1_3over4
                        b.index_SBD_3over4 := b.index_key1_3over4
                    else if(b.Buff_close3_3over4<b.close_SBD_3over4)
                        b.close_SBD_3over4 := na
                        b.close_SBU_3over4 := b.Buff_key1_3over4
                        b.index_SBU_3over4 := b.index_key1_3over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_3over4 := b.Buff_close2_3over4
                        b.index_key2_3over4 := index-1
                        b.close_SBU_3over4 := b.Buff_key2_3over4
                        b.index_SBU_3over4 := b.index_key2_3over4
                        b.Buff_key1_3over4 := b.Buff_key2_3over4
                        b.index_key1_3over4 := b.index_key2_3over4
                    if(b.Buff_close3_3over4<b.close_SBD_3over4)
                        b.close_SBD_3over4 := na
                        b.index_SBD_3over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_3over4 := b.Buff_close2_3over4
                        b.index_key2_3over4 := index-1
                        b.close_SBD_3over4 := b.Buff_key2_3over4
                        b.index_SBD_3over4 := b.index_key2_3over4
                        b.Buff_key1_3over4 := b.Buff_key2_3over4
                        b.index_key1_3over4 := b.index_key2_3over4
                    if(b.Buff_close3_3over4>b.close_SBU_3over4)
                        b.close_SBU_3over4 := na
                        b.index_SBU_3over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 3
            break
        //end while
        if(j>=4)
            break
        else
            continue
//        count := j%4==0? count+1 : count
//        if((count == c.Barcount and f.diffFlag) or (count == Quotient+1 and not(f.diffFlag))) //it means diff<0, jump over the day or today is at the end. 
//            break
    //end while
//end method     
method BOScal_level4(BOS_Type b, Count_Type c, Flag_Type f, CurrentTime_Type t, array<float> arr, float Quotient, int index, float Remainder, float ttlbar, float diff) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    int j = 3
    while f.bosFlag 
        if((not na(b.close_SBU_4over4)) and (not na(b.close_SBD_4over4)) )//有天地 留在SURRD 依此類推
            b.state_4over4 := SURRD
        else if ((na(b.close_SBU_4over4)) and (not na(b.close_SBD_4over4)) )
            b.state_4over4 := NOSKY
        else
            b.state_4over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_4over4 := b.Buff_close2_4over4
            b.Buff_close2_4over4 := b.Buff_close3_4over4 
            b.Buff_close3_4over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_4over4 - b.Buff_close1_4over4>0? 1 : -1
            b.slope2 := b.Buff_close3_4over4 - b.Buff_close2_4over4>0? 1 : -1
            switch b.state_4over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_4over4 := b.Buff_close2_4over4
                        b.index_key1_4over4 := index-1
                    if(b.Buff_close3_4over4>b.close_SBU_4over4)
                        b.close_SBU_4over4 := na
                        b.close_SBD_4over4 := b.Buff_key1_4over4
                        b.index_SBD_4over4 := b.index_key1_4over4
                    if(b.Buff_close3_4over4<b.close_SBD_4over4)
                        b.close_SBD_4over4 := na
                        b.close_SBU_4over4 := b.Buff_key1_4over4
                        b.index_SBU_4over4 := b.index_key1_4over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_4over4 := b.Buff_close2_4over4
                        b.index_key2_4over4 := index-1
                        b.close_SBU_4over4 := b.Buff_key2_4over4
                        b.index_SBU_4over4 := b.index_key2_4over4
                        b.Buff_key1_4over4 := b.Buff_key2_4over4
                        b.index_key1_4over4 := b.index_key2_4over4
                    if(b.Buff_close3_4over4<b.close_SBD_4over4)
                        b.close_SBD_4over4 := na
                        b.index_SBD_4over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_4over4 := b.Buff_close2_4over4
                        b.index_key2_4over4 := index-1
                        b.close_SBD_4over4 := b.Buff_key2_4over4
                        b.index_SBD_4over4 := b.index_key2_4over4
                        b.Buff_key1_4over4 := b.Buff_key2_4over4
                        b.index_key1_4over4 := b.index_key2_4over4
                    if(b.Buff_close3_4over4>b.close_SBU_4over4)
                        b.close_SBU_4over4 := na
                        b.index_SBU_4over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 4
            break
        //end while
        if(j>=4)
            break
    //end while
//end method     

method reorderSBlabel(BOS_Type b, Delta_Type d, close) =>
    int x = na
    float base = 0.05
    arr = array.from(b.close_SBU_1over4, b.close_SBU_2over4, b.close_SBU_3over4, b.close_SBU_4over4,b.close_SBD_1over4, b.close_SBD_2over4, b.close_SBD_3over4, b.close_SBD_4over4)
    arrd = array.new<float>(8,0)
    arrindices = array.sort_indices(arr,order.ascending)
    if(close>=10000)
        x := 400
    else if(close>=1000 and close<10000)
        x := 40
    else if(close>=100 and close<1000)
        x := 4
    else
        x := 1
    for i=0 to 7
        array.set(arrd,array.get(arrindices,i),base * x * i)
    //end for
    d.x_U1o4 := array.get(arrd,0)
    d.x_U2o4 := array.get(arrd,1)
    d.x_U3o4 := array.get(arrd,2)
    d.x_U4o4 := array.get(arrd,3)
    d.x_D1o4 := array.get(arrd,4)
    d.x_D2o4 := array.get(arrd,5)
    d.x_D3o4 := array.get(arrd,6)
    d.x_D4o4 := array.get(arrd,7)
//end method
//*****custom option*****//
numbershift := 0
EXCHANGE := str.contains(TICKERID,"OANDA")?  "OANDA" : str.contains(TICKERID,"SAXO")? "SAXO" : str.contains(TICKERID,"EIGHTCAP")? "EIGHTCAP" : str.contains(TICKERID,"BINANCE")? "BINANCE" : na
if(EXCHANGE=="OANDA" and ITSTYPE=="forex")
    BASETIME := OANDA_FOREX
else if(EXCHANGE=="OANDA" and ITSTYPE=="crypto")
    BASETIME := OANDA_CRYPTO
else if(EXCHANGE=="OANDA" and ITSTYPE=="cfd")
    BASETIME := OANDA_CFD
else if(EXCHANGE=="EIGHTCAP" and ITSTYPE=="forex")
    BASETIME := EIGHTCAP_FOREX
else if(EXCHANGE=="EIGHTCAP" and ITSTYPE=="crypto")
    BASETIME := EIGHTCAP_CRYPTO
else if(EXCHANGE=="EIGHTCAP" and ITSTYPE=="cfd")
    BASETIME := EIGHTCAP_CFD    
else if(EXCHANGE=="SAXO" and ITSTYPE=="forex")
    BASETIME := SAXO_FOREX
else if(EXCHANGE=="SAXO" and ITSTYPE=="crypto")
    BASETIME := SAXO_CRYPTO
else if(EXCHANGE=="SAXO" and ITSTYPE=="cfd")
    BASETIME := SAXO_CFD
else if(EXCHANGE=="BINANCE" and ITSTYPE=="crypto")
    BASETIME := BINANCE_CRYPTO
else
    BASETIME := na
//*****var initialization*****//
var timeInfo = CurrentTime_Type.new(na, na, na, na, na, na, na, na,na,na,na)
var countInfo = Count_Type.new(0,0,0,0,0) // levelcount count1 boscount Barcount,RmnBarcount
var flagInfo = Flag_Type.new(na,false,false,false,false,false) //size ,go,resetFlag,plotFlag, diffFlag, jumpFlag
var BOSInfo = BOS_Type.new()
var DeltaInfo = Delta_Type.new()
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
if(timeInfo.HrMin2Min<BASETIME and timeInfo.HrMin2Min>=0)
    timeInfo.HrMin2Min2 := timeInfo.HrMin2Min + DAY2MINUTE
else
    timeInfo.HrMin2Min2 := timeInfo.HrMin2Min

arrayclose := request.security_lower_tf(syminfo.tickerid,str_timeframe,close)
arraysize := array.size(arrayclose)
if(arraysize == 0)
    for i=0 to 3
        array.push(arrayclose,close)
flagInfo.SizeFlag := array.size(arrayclose)==4? true : false
Quotient := math.floor(float(DAY2MINUTE)/timeInfo.currentperiod)
Remainder := DAY2MINUTE%timeInfo.currentperiod
Remainder_3over4 := DAY2MINUTE%(3*timeInfo.currentperiod_div4)
Remainder_2over4 := DAY2MINUTE%(2*timeInfo.currentperiod_div4)
Remainder_1over4 := DAY2MINUTE%(timeInfo.currentperiod_div4)
ttlbar := Remainder==0? Quotient : Quotient+1
//Remainder2Bar := math.floor(Remainder/timeInfo.currentperiod_div4)+1
//fourminus_Remainger2Bar := 4-Remainder2Bar
////*****state init*****////
if(timeInfo.HrMin2Min2 == BASETIME and flagInfo.GoFlag == false)//start!!!
    index := bar_index
    countInfo.Barcount := 0
    timeInfo.starttime := timeInfo.HrMin2Min2
    timeInfo.lasttime := BASETIME
    flagInfo.GoFlag := true
    nextstate := ARRAYGEN
if(barstate.isfirst)
    init_BOS(BOSInfo)
    init_count(countInfo)
if(flagInfo.resetFlag) //Barcount := bar_index+1, example Barcount=1,bar_index=0
    state := RESET
else
    state := nextstate
if bar_index == last_bar_index - numbershift
    flagInfo.plotFlag := true
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

////*****data flow*****////
switch state
    RESET =>
        init_Flag(flagInfo)
        init_BOS(BOSInfo)
        init_count(countInfo)
    ARRAYGEN =>
        countInfo.RmnBarcount := 0
        countInfo.count1 := 0
        if(flagInfo.GoFlag)
            if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 != BASETIME)
                countInfo.Barcount := 1+(timeInfo.HrMin2Min2-BASETIME)/timeInfo.currentperiod
                diff := (timeInfo.HrMin2Min2-BASETIME)/timeInfo.currentperiod
                timeInfo.starttime := BASETIME + (countInfo.Barcount-1)*timeInfo.currentperiod
                flagInfo.jumpFlag := true
                flagInfo.diffFlag := false
            else if(countInfo.Barcount == 0 and timeInfo.HrMin2Min2 == BASETIME)
                countInfo.Barcount := 1
                diff := 0
                timeInfo.starttime := timeInfo.HrMin2Min2
                flagInfo.jumpFlag := false
                flagInfo.diffFlag := false
            else
                if(timeInfo.starttime + timeInfo.currentperiod == timeInfo.HrMin2Min2)
                    diff := 1
                    countInfo.Barcount += diff
                    timeInfo.lasttime := timeInfo.starttime
                    timeInfo.starttime += timeInfo.currentperiod
                    flagInfo.jumpFlag := false
                    flagInfo.diffFlag := false
                else
                    timeInfo.lasttime := timeInfo.starttime
                    diff := (timeInfo.HrMin2Min2-timeInfo.lasttime)/timeInfo.currentperiod
                    flagInfo.jumpFlag := true
                    if(diff<0)//跳過最後一根 從1700 or 1728 or more開始
                        countInfo.RmnBarcount := (BASETIME + timeInfo.currentperiod*Quotient-timeInfo.lasttime)/timeInfo.currentperiod
                        countInfo.count1 := (timeInfo.HrMin2Min2-BASETIME)/timeInfo.currentperiod
                        diff := countInfo.RmnBarcount
                        countInfo.Barcount := Remainder==0? countInfo.Barcount + diff + countInfo.count1 : countInfo.Barcount+ diff + countInfo.count1 + 1
                        flagInfo.diffFlag := true
                        timeInfo.starttime := timeInfo.HrMin2Min2
                        //這個情況表示新的開市日有可能從17:00 或17:28之類的開始 要討論
                    else
                        countInfo.Barcount += diff
                        timeInfo.lasttime := timeInfo.HrMin2Min2
                        timeInfo.starttime := BASETIME + (countInfo.Barcount-1)*timeInfo.currentperiod
                        flagInfo.diffFlag := false

        if(arraysize!=4)
            for i=0 to (3-arraysize)
                array.push(arrayclose,close)
//        if(flagInfo.diffFlag) //跳天 往前插值補滿
//            for i=0 to 4*(diff+countInfo.count1+1)-1
//                array.unshift(arrayclose,array.get(arrayclose,0))
//        else if(flagInfo.jumpFlag and countInfo.Barcount==Quotient+1) //跳 且 跳到當天最後一根
//            for i=0 to 4*(diff)-1
//                array.unshift(arrayclose,array.get(arrayclose,0))
//            for i= 0 to Remainder2Bar-1
//                array.push(arrayclose,array.get(arrayclose,arraysize-1))
//        else if(flagInfo.jumpFlag and countInfo.Barcount!=Quotient+1)//跳 但沒跳到最後一根
//            for i=0 to 4*(diff)-1
//                array.unshift(arrayclose,array.get(arrayclose,0))
//        else if(not(flagInfo.jumpFlag) and countInfo.Barcount==Quotient+1) //沒有跳 但是已經最後根
//            for i= 0 to fourminus_Remainger2Bar-1
//                array.push(arrayclose,close)
//        else //沒有跳 一根一根進來 且不是最後一根
//            if(bar_index == 9075)
//                label.new(bar_index,low-low/20,"one by one input")
//            //arrayclose := arrayclose    
        testfloat := countInfo.Barcount
        testbool2 := flagInfo.jumpFlag
        testbool3 := flagInfo.diffFlag
        flagInfo.bosFlag := true
//      testfloat2 := diff
        testfloat3 := timeInfo.starttime
        testfloat4 := timeInfo.lasttime
        testfloat5 := countInfo.boscount
        testarray := arrayclose
        if(bar_index>=0)
            BOScal_level1(BOSInfo,countInfo,flagInfo,timeInfo,arrayclose,Quotient,index,Remainder,Remainder_1over4,ttlbar,diff)
            BOScal_level2(BOSInfo,countInfo,flagInfo,timeInfo,arrayclose,Quotient,index,Remainder,Remainder_2over4,ttlbar,diff)
            BOScal_level3(BOSInfo,countInfo,flagInfo,timeInfo,arrayclose,Quotient,index,Remainder,Remainder_3over4,ttlbar,diff)
            BOScal_level4(BOSInfo,countInfo,flagInfo,timeInfo,arrayclose,Quotient,index,Remainder,ttlbar,diff)
        countInfo.boscount := countInfo.Barcount
        flagInfo.diffFlag := false
        flagInfo.jumpFlag := false
        if(countInfo.boscount == ttlbar and timeInfo.currentperiod != DAY2MINUTE) //當天資料已經處理完
            timeInfo.lasttime := BASETIME
            countInfo.Barcount := 0
            countInfo.boscount := 0
        else if(countInfo.boscount > ttlbar and timeInfo.currentperiod != DAY2MINUTE) //表示有跳天
            timeInfo.lasttime := BASETIME
            countInfo.Barcount := countInfo.Barcount%(ttlbar)
            countInfo.boscount := countInfo.Barcount

        index += 1
    PLOT=>
        testfloat2 := BOSInfo.close_SBU_3over4
    =>
        testfloat5 := testfloat5 //nothing happen
//        label.new(bar_index,low+0.1,"run into wrong state")
if(barstate.islast)
    reorderSBlabel(BOSInfo, DeltaInfo, close)
//    if(not na(test))
//        label.delete(test)
//    test := label.new(last_bar_index-numbershift, low, "GoFlag=\t" + str.tostring(countInfo.levelcount)+"\n jumpFlag: "+str.tostring(testbool2)+"\n diffFlag: "+str.tostring(testbool3)+"\n testfloat2 close_SBU_3over4: "+str.tostring(testfloat2)+"\n state: "+str.tostring(state)+"\n Barcount: "+str.tostring(countInfo.Barcount)+"\n count1: "+str.tostring(countInfo.count1)+"\nRmnBarcount: "+str.tostring(countInfo.RmnBarcount)+"\n testarray @this pos is arrayclose  : "+str.tostring(testarray)+"\n resetFlag : "+str.tostring(flagInfo.resetFlag)+"\n testfloat3 starttime : "+str.tostring(testfloat3)+"\n testfloat4 lasttime : "+str.tostring(testfloat4)+"\n testfloat5 not updated boscount : "+str.tostring(testfloat5)+"\n testfloat now is barcount : "+str.tostring(testfloat)+"\n this bar is not allowed to be cal,but is bar now...\nnewest time.HrMin2Min2: "+str.tostring(timeInfo.HrMin2Min2)+"\n newest arrayclose : "+str.tostring(arrayclose),style = label.style_triangledown,color = color.green)

//1over4 start 
    line.new(x1=BOSInfo.index_SBU_1over4, y1=BOSInfo.close_SBU_1over4, x2=BOSInfo.index_SBU_1over4 +100, y2=BOSInfo.close_SBU_1over4, width=3, color=color.red, style=line.style_dashed)
    line.new(x1=BOSInfo.index_SBD_1over4, y1=BOSInfo.close_SBD_1over4, x2=BOSInfo.index_SBD_1over4 +100, y2=BOSInfo.close_SBD_1over4, width=3, color=color.red, style=line.style_dashed)

    if(na(Label_SBU_1over4)==false)
        label.delete(Label_SBU_1over4)
    Label_SBU_1over4 := label.new(x=BOSInfo.index_SBU_1over4, y=BOSInfo.close_SBU_1over4+DeltaInfo.x_U1o4, text="SBU_1over4: " + str.tostring(BOSInfo.close_SBU_1over4), xloc = xloc.bar_index, yloc=yloc.price,color=color.red) 

    if(na(Label_SBD_1over4)==false)
        label.delete(Label_SBD_1over4)
    Label_SBD_1over4 := label.new(x=BOSInfo.index_SBD_1over4, y=BOSInfo.close_SBD_1over4+DeltaInfo.x_D1o4, text="SBD_1over4: " + str.tostring(BOSInfo.close_SBD_1over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up)
//1over4 end
//2over4 start        
    line.new(x1=BOSInfo.index_SBU_2over4, y1=BOSInfo.close_SBU_2over4, x2=BOSInfo.index_SBU_2over4 +100, y2=BOSInfo.close_SBU_2over4, width=2, color=color.orange)
    line.new(x1=BOSInfo.index_SBD_2over4, y1=BOSInfo.close_SBD_2over4, x2=BOSInfo.index_SBD_2over4 +100, y2=BOSInfo.close_SBD_2over4, width=2, color=color.orange)

    if(na(Label_SBU_2over4)==false)
        label.delete(Label_SBU_2over4)
    Label_SBU_2over4 := label.new(x=BOSInfo.index_SBU_2over4, y=BOSInfo.close_SBU_2over4+DeltaInfo.x_U2o4, text="SBU_2over4: " + str.tostring(BOSInfo.close_SBU_2over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.orange) 

    if(na(Label_SBD_2over4)==false)
        label.delete(Label_SBD_2over4)
    Label_SBD_2over4 := label.new(x=BOSInfo.index_SBD_2over4, y=BOSInfo.close_SBD_2over4+DeltaInfo.x_D2o4, text="SBD_2over4: " + str.tostring(BOSInfo.close_SBD_2over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.orange,style = label.style_label_up)
//2over4 end
//3over4 start
    line.new(x1=BOSInfo.index_SBU_3over4, y1=BOSInfo.close_SBU_3over4, x2=BOSInfo.index_SBU_3over4 +100, y2=BOSInfo.close_SBU_3over4, width=4, color=color.yellow, style=line.style_dotted)
    line.new(x1=BOSInfo.index_SBD_3over4, y1=BOSInfo.close_SBD_3over4, x2=BOSInfo.index_SBD_3over4 +100, y2=BOSInfo.close_SBD_3over4, width=4, color=color.yellow, style=line.style_dotted)

    if(na(Label_SBU_3over4)==false)
        label.delete(Label_SBU_3over4)
    Label_SBU_3over4 := label.new(x=BOSInfo.index_SBU_3over4, y=BOSInfo.close_SBU_3over4+DeltaInfo.x_U3o4, text="SBU_3over4: " + str.tostring(BOSInfo.close_SBU_3over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.yellow) 

    if(na(Label_SBD_3over4)==false)
        label.delete(Label_SBD_3over4)
    Label_SBD_3over4 := label.new(x=BOSInfo.index_SBD_3over4, y=BOSInfo.close_SBD_3over4+DeltaInfo.x_D3o4, text="SBD_3over4: " + str.tostring(BOSInfo.close_SBD_3over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.yellow,style = label.style_label_up)
//3over4 end
//4over4 start
    line.new(x1=BOSInfo.index_SBU_4over4, y1=BOSInfo.close_SBU_4over4, x2=BOSInfo.index_SBU_4over4 +100, y2=BOSInfo.close_SBU_4over4, width=2, color=color.green)
    line.new(x1=BOSInfo.index_SBD_4over4, y1=BOSInfo.close_SBD_4over4, x2=BOSInfo.index_SBD_4over4 +100, y2=BOSInfo.close_SBD_4over4, width=2, color=color.green)

    if(na(Label_SBU_4over4)==false)
        label.delete(Label_SBU_4over4)
    Label_SBU_4over4 := label.new(x=BOSInfo.index_SBU_4over4, y=BOSInfo.close_SBU_4over4+DeltaInfo.x_U4o4, text="SBU_4over4: " + str.tostring(BOSInfo.close_SBU_4over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.green) 

    if(na(Label_SBD_4over4)==false)
        label.delete(Label_SBD_4over4)
    Label_SBD_4over4 := label.new(x=BOSInfo.index_SBD_4over4, y=BOSInfo.close_SBD_4over4+DeltaInfo.x_D4o4 , text="SBD_4over4: " + str.tostring(BOSInfo.close_SBD_4over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.green,style = label.style_label_up)
//4over4 end
    

//plot end
//*****test plot*****//
//if bar_index == last_bar_index - numbershift
//    //label.new(last_bar_index-numbershift, high, str.tostring(arrayclose),color orange,size := size.normal)
//    buffyear := year(time)
//    buffmonth := month(time)
//    buffday := dayofmonth(time) 
//    buffhour := hour(time)
//    buffmin := minute(time)
//if bar_index == last_bar_index
//    label.new(last_bar_index, low-0.05, "\n label bufftime at : "+ str.tostring(buffyear)+ "\t" +str.tostring(buffmonth) +"\t" + str.tostring(buffday)+"\t" + str.tostring(buffhour)+"\t" + str.tostring(buffmin)+"\n\t EXCHANGE RIGHT??\t" + str.tostring(str.contains(syminfo.tickerid,EXCHANGE))+"\n period=\t" + str.tostring(timeInfo.currentperiod_div4) +"\n state=\t" + str.tostring(state)+"\n Go flag?=\t" + str.tostring(flagInfo.GoFlag)+"\n testint=\t" + str.tostring(testint)+"\n testfloat=\t" + str.tostring(testfloat),style=label.style_triangledown,color = color.green)