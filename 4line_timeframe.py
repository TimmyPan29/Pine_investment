//+-----use the way timeframe function support so that we can take advantage fo higher timeframe data-----+//
// © T.PanShuai29
//@version=5
indicator("4line_", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)

type Candle //for fourline candle
    float           o
    float           c
    float           h
    float           l
    int             o_idx
    int             c_idx
    int             h_idx
    int             l_idx

type BOSdata
    float           sbu = 0
    float           sbd = 0
    int             sbu_idx = 0
    int             sbd_idx = 0
    float           slope1 = na
    float           slope2 = na
    int             state  = 1 //GRD
    float           reg1key = 0
    int             reg1key_idx = 0
    float           reg2key = 0
    int             reg2key_idx = 0
    float           regclose1 = 0
    float           regclose2 = 0
    float           regclose3 = 0


type CandleSettings
    bool            show
    string          htf
    int             max_memory

type Settings
    int             offset
    int             buffer
    int             htf_buffer
    int             width


type CandleSet
    Candle[]        candles
    CandleSettings  settings
    label           tfName
    label           tfTimer
    BOSdata         bosdata

type CandleSet_add
    Candle[]        candles
    CandleSettings  settings
    label           tfName
    label           tfTimer
type Helper
    string name             = "Helper"

Settings settings = Settings.new()
//+-----four line-----+//
var CandleSettings SettingsHTF1 = CandleSettings.new()
var CandleSettings SettingsHTF2 = CandleSettings.new()
var CandleSettings SettingsHTF3 = CandleSettings.new()
var CandleSettings SettingsHTF4 = CandleSettings.new()

var Candle[] candles_1        = array.new<Candle>(0)
var Candle[] candles_2        = array.new<Candle>(0)
var Candle[] candles_3        = array.new<Candle>(0)
var Candle[] candles_4        = array.new<Candle>(0)

var BOSdata bosdata_1       = BOSdata.new()
var BOSdata bosdata_2       = BOSdata.new()
var BOSdata bosdata_3       = BOSdata.new()
var BOSdata bosdata_4       = BOSdata.new()

var CandleSet htf1          = CandleSet.new()
htf1.settings               := SettingsHTF1
htf1.candles                := candles_1
htf1.bosdata                := bosdata_1

var CandleSet htf2          = CandleSet.new()
htf2.settings               := SettingsHTF2
htf2.candles                := candles_2
htf2.bosdata                := bosdata_2

var CandleSet htf3          = CandleSet.new()
htf3.settings               := SettingsHTF3
htf3.candles                := candles_3
htf3.bosdata                := bosdata_3

var CandleSet htf4          = CandleSet.new()
htf4.settings               := SettingsHTF4
htf4.candles                := candles_4
htf4.bosdata                := bosdata_4

//+-----add line-----+//
var Candle[] candles_1_add        = array.new<Candle>(0)
var Candle[] candles_2_add        = array.new<Candle>(0)
var Candle[] candles_3_add        = array.new<Candle>(0)
var Candle[] candles_4_add        = array.new<Candle>(0)
var Candle[] candles_3_add        = array.new<Candle>(0)
var Candle[] candles_4_add        = array.new<Candle>(0)

var CandleSettings SettingsHTF1_add = CandleSettings.new()
var CandleSettings SettingsHTF2_add = CandleSettings.new()
var CandleSettings SettingsHTF3_add = CandleSettings.new()
var CandleSettings SettingsHTF4_add = CandleSettings.new()
var CandleSettings SettingsHTF5_add = CandleSettings.new()
var CandleSettings SettingsHTF6_add = CandleSettings.new()

var CandleSet_add htf1_add   = CandleSet_add.new()
htf1_add.settings               := SettingsHTF1_add
htf1_add.candles                := candles_1_add

var CandleSet_add htf2_add   = CandleSet_add.new()
htf2_add.settings               := SettingsHTF2_add
htf2_add.candles                := candles_2_add

var CandleSet_add htf3_add   = CandleSet_add.new()
htf3_add.settings               := SettingsHTF3_add
htf3_add.candles                := candles_3_add

var CandleSet_add htf4_add   = CandleSet_add.new()
htf4_add.settings               := SettingsHTF4_add
htf4_add.candles                := candles_4_add

var CandleSet_add htf5_add   = CandleSet_add.new()
htf5_add.settings               := SettingsHTF5_add
htf5_add.candles                := candles_5_add

var CandleSet_add htf6_add   = CandleSet_add.new()
htf6_add.settings               := SettingsHTF6_add
htf6_add.candles                := candles_6_add

//+----------------------------------------+//
//+-settings    

//+----------------------------------------+//


htf1.settings.show          := input.bool(true, "HTF 1      ", inline="htf1")
htf_1                       = input.timeframe("1", "", inline="htf1")
htf1.settings.htf           := htf_1
htf1.settings.max_memory   := input.int(10, "", inline="htf1")

htf2.settings.show          := input.bool(true, "HTF 2      ", inline="htf2")
htf_2                       = input.timeframe("15", "", inline="htf2")
htf2.settings.htf           := htf_2
htf2.settings.max_memory   := input.int(10, "", inline="htf2")

htf3.settings.show          := input.bool(true, "HTF 3      ", inline="htf3")
htf_3                       = input.timeframe("60", "", inline="htf3")
htf3.settings.htf           := htf_3
htf3.settings.max_memory   := input.int(10, "", inline="htf3")

htf4.settings.show          := input.bool(true, "HTF 4      ", inline="htf4")
htf_4                       = input.timeframe("240", "", inline="htf4")
htf4.settings.htf           := htf_4
htf4.settings.max_memory   := input.int(10, "", inline="htf4")

settings.max_sets        := input.int(4, "Limit to next HTFs only", minval=1, maxval=4)




//+----------------------------------------+//
//+- Variables   

//+----------------------------------------+//
Helper    helper        = Helper.new()
var Trace trace         = Trace.new()
color color_transparent = #ffffff00
var index               = 0
//+----------------------------------------+//
//+- Internal functions   

//+----------------------------------------+//

method LineStyle(Helper helper, string style) =>
    helper.name := style
    out = switch style
        '----' => line.style_dashed
        '····' => line.style_dotted
        => line.style_solid


method ValidTimeframe(Helper helper, string HTF) => //兩個部分 一個是檢查更高週期的是不是大於天，這個部分用轉成秒數的方式來判斷，第二個部分則是如果週期不是以天為單位，則一樣 使用秒的方式 判斷是不是整數倍 以及高週期的輸入要大於當前週期
    helper.name := HTF
    if timeframe.in_seconds(HTF) >= timeframe.in_seconds("D") and timeframe.in_seconds(HTF) > timeframe.in_seconds()
        true 
    else
        n1 = timeframe.in_seconds()
        n2 = timeframe.in_seconds(HTF)
        n3 = n2 % n1 //it is wrong, it should be n2%n1
        (n1 <= n2 and math.round(n2/n1) == n2/n1)

method RemainingTime(Helper helper, string HTF) =>
    helper.name     := HTF
    if barstate.isrealtime
        timeRemaining   = (time_close(HTF) - timenow)/1000
        days            = math.floor(timeRemaining / 86400)
        hours           = math.floor((timeRemaining - (days*86400)) / 3600)
        minutes         = math.floor((timeRemaining - (days*86400) - (hours*3600))/ 60)
        seconds         = math.floor(timeRemaining - (days*86400) - (hours*3600) - (minutes*60))

        r = str.tostring(seconds, "00")
        if minutes > 0 or hours > 0 or days > 0
            r := str.tostring(minutes, "00") + ":" + r
        if hours > 0 or days > 0
            r := str.tostring(hours, "00") + ":" + r
        if days > 0
            r := str.tostring(days) + "D " + r
        r
    else
        "n/a"

method HTFName(Helper helper, string HTF) =>
    helper.name := "HTFName"
    formatted = HTF

    seconds = timeframe.in_seconds(HTF)
    if seconds < 60
        formatted := str.tostring(seconds) + "s"
    else if (seconds / 60) < 60
        formatted := str.tostring((seconds/60)) + "m"
    else if (seconds/60/60) < 24
        formatted := str.tostring((seconds/60/60)) + "H" 
    formatted

method HTFEnabled(Helper helper) =>
    helper.name := "HTFEnabled"
    int enabled =0
    enabled += htf1.settings.show ? 1 : 0
    enabled += htf2.settings.show ? 1 : 0
    enabled += htf3.settings.show ? 1 : 0
    enabled += htf4.settings.show ? 1 : 0
    int last = math.min(enabled, settings.max_sets)

    last

method HTFaddEnabled(Helper helper) =>
    helper.name := "HTFEnabled"
    int enabled =0
    enabled += htf1_add.settings.show ? 1 : 0
    enabled += htf2_add.settings.show ? 1 : 0
    enabled += htf3_add.settings.show ? 1 : 0
    enabled += htf4_add.settings.show ? 1 : 0
    enabled += htf5_add.settings.show ? 1 : 0
    enabled += htf6_add.settings.show ? 1 : 0
    int last = math.min(enabled, settings.max_sets)

    last

method Monitor(CandleSet candleSet) =>
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)

    if isNewHTFCandle 
        Candle candle    = Candle.new()
        candle.c        := close
        candle.c_idx    := bar_index

        candleSet.candles.unshift(candle) //從這句話可以知道 index越靠近零 資料越新

        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)

    candleSet

method Update(CandleSet candleSet) =>//更新最新一根的價格動態 
    if candleSet.candles.size() > 0
        Candle candle   = candleSet.candles.first() //取得candle向量的第一個candle對象
        candle.c       := close
        candle.c_idx   := bar_index
    candleSet    

method BOSJudge(CandleSet candleSet)
    Candle candle = candleSet.candles
    BOSdata bosdata = candleSet.bosdata
    if candleSet.candles.size() > 0
        if(candleSet.bosdata.state == 1)
            bosdata.regclose1 := bosdata.regclose2
            bosdata.regclose2 := bosdata.regclose3
            bosdata.regclose3 := candle.c
            bosdata.slope1 := bosdata.regclose2 - bosdata.regclose1>0? 1 : -1
            bosdata.slope2 := bosdata.regclose3 - bosdata.regclose2>0? 1 : -1
            if((not na(bosdata.sbd)) and (not na(bosdata.sbu)))
                state := 2 //
            else if(not na(bosdata.sbd) and na(bosdata.sbu))
                state := 3
            else if(na(bosdata.sbd) and (not na(bosdata.sbu)))
                state := 4
            else
                label.new(bar_index,high,text="GG")

        if(candleSet.bosdata.state == 2)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.reg1key := bosdata.regclose2
                bosdata.reg1key_idx := bar_index==0? 0 : index - 1
            //else //Buff_key1維持原樣
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx := na
                bosdata.sbd := bosdata.reg1key
                bosdata.sbd_idx := bosdata.reg1key_idx
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd := na 
                bosdata.sbd_idx := na
                bosdata.sbu := bosdata.reg1key
                bosdata.sbu_idx := bosdata.reg1key_idx
            state := 1


        if(candleSet.bosdata.state == 3)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index-1
                bosdata.sbu := bosdata.reg2key
                bosdata.sbu_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd := na
                bosdata.sbd_idx:= na
            state := 1


        if(candleSet.bosdata.state == 4)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index-1
                bosdata.sbd := bosdata.reg2key
                bosdata.sbd_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx:= na
            state := 1

        if barstate.isrealtime or barstate.islast
















