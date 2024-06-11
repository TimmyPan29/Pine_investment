//+-----filter the multiline after the timing and show that on figure -----+//
// © T.PanShuai29
//@version=5
indicator("4line_", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)

type Candle //for fourline candle
    float           c
    int             c_idx

type BOSdata
    float           sbu         = 0
    float           sbd         = 0
    int             sbu_idx     = 0
    int             sbd_idx     = 0
    float           slope1      = 0
    float           slope2      = 0
    int             state       = 1 //ini
    float           reg1key     = 0
    int             reg1key_idx = 0
    float           reg2key     = 0
    int             reg2key_idx = 0
    float           regclose1   = 0
    float           regclose2   = 0
    float           regclose3   = 0
    label           sbu_l
    label           sbu_date
    string          s_dateu
    label           sbu_price
    line            sbu_line
    label           sbd_l
    label           sbd_date
    string          s_dated
    label           sbd_price
    line            sbd_line       
    float           temp        = 0
    float           temp2
    float           temp3
    string          strtemp1
    string          strtemp2
    int             dateinnumber = 0


type CandleSettings
    bool            show
    string          htf
    int             max_memory

type Settings
    int             offset
    int             text_buffer
    int             max_sets
    string          sbu_label_size 
    color           sbu_label_color
    bool            sbu_label_show
    string          sbd_label_size 
    color           sbd_label_color
    bool            sbd_label_show

    string          htf_timer_size
    color           htf_timer_color
    string          htf_label_size 
    color           htf_label_color
    string          date_label_size
    color           date_label_color
    string          price_label_size
    color           price_label_color
    bool            add_show

type Trace
    int             trace_c_size 
    color           trace_c_color 
    string          trace_c_style 

type CandleSet
    Candle[]        candles
    CandleSettings  settings
    BOSdata         bosdata
    Trace           trace
    label           tfName
    label           tfTimer        
type ValueDecisionReg
    float           value
    int             vidx 
    string          vdate
    string          vname
    string          vtext
    string          vremntime
    string          vdecisionname
    label           vlb
    line            vln
    float           vtemp


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

var Trace   trace_1         = Trace.new()
var Trace   trace_2         = Trace.new()
var Trace   trace_3         = Trace.new()
var Trace   trace_4         = Trace.new()

var CandleSet htf1          = CandleSet.new()
htf1.settings               := SettingsHTF1
htf1.candles                := candles_1
htf1.bosdata                := bosdata_1
htf1.trace                  := trace_1

var CandleSet htf2          = CandleSet.new()
htf2.settings               := SettingsHTF2
htf2.candles                := candles_2
htf2.bosdata                := bosdata_2
htf2.trace                  := trace_2

var CandleSet htf3          = CandleSet.new()
htf3.settings               := SettingsHTF3
htf3.candles                := candles_3
htf3.bosdata                := bosdata_3
htf3.trace                  := trace_3

var CandleSet htf4          = CandleSet.new()
htf4.settings               := SettingsHTF4
htf4.candles                := candles_4
htf4.bosdata                := bosdata_4
htf4.trace                  := trace_4

//+---------------ValueDeicsion------------------+//
var ValueDecisionReg maxnormal  = ValueDecisionReg.new()
var ValueDecisionReg minnormal  = ValueDecisionReg.new()
var ValueDecisionReg highestsbd = ValueDecisionReg.new()
var ValueDecisionReg lowestsbu  = ValueDecisionReg.new()
//+---------------ValueDeicsionEND------------------+//

//+----------------------------------------+//
//+-settings    

//+----------------------------------------+//

settings.add_show          := input.bool(true, "add function enable?       ", inline="add enable")
htf1.settings.show         := input.bool(true, "HTF 1      ", inline="htf1")
htf_1                       = input.timeframe("1", "", inline="htf1")
htf1.settings.htf          := htf_1
htf1.settings.max_memory   := input.int(10, "", inline="htf1")

htf2.settings.show         := input.bool(true, "HTF 2      ", inline="htf2")
htf_2                       = input.timeframe("60", "", inline="htf2")
htf2.settings.htf          := htf_2
htf2.settings.max_memory   := input.int(10, "", inline="htf2")

htf3.settings.show         := input.bool(true, "HTF 3      ", inline="htf3")
htf_3                       = input.timeframe("120", "", inline="htf3")
htf3.settings.htf          := htf_3
htf3.settings.max_memory   := input.int(10, "", inline="htf3")

htf4.settings.show         := input.bool(true, "HTF 4      ", inline="htf4")
htf_4                       = input.timeframe("240", "", inline="htf4")
htf4.settings.htf          := htf_4
htf4.settings.max_memory   := input.int(10, "", inline="htf4")

settings.max_sets          := input.int(4, "Limit to next HTFs only", minval=1, maxval=4)

settings.offset            := input.int(10, "padding from current candles", minval = 1)
settings.text_buffer       := input.int(10, "space between text features", minval = 1, maxval = 10)
// sbu sbd, period, date happen, remain time, price, line color

settings.sbu_label_color   := input.color(color.new(color.black, 10), "sbu_label", inline='11')
settings.sbu_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.sbd_label_color   := input.color(color.new(color.black, 10), "sbd_label", inline='11')
settings.sbd_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.htf_label_color   := input.color(color.new(color.black, 10), "htf_label", inline='21')
settings.htf_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.date_label_color  := input.color(color.new(color.black, 10), "date_label", inline='21')
settings.date_label_size   := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.htf_timer_color   := input.color(color.new(color.black, 10), "htf_timer", inline='31')
settings.htf_timer_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

settings.price_label_color := input.color(color.new(color.black, 10), "price_label", inline='31')
settings.price_label_size  := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

htf1.trace.trace_c_color   := input.color(color.new(color.red, 50), "level1    ", inline='level 1', group="trace")
htf1.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='level 1', group="trace")
htf1.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='level 1', group="trace")

htf2.trace.trace_c_color   := input.color(color.new(color.orange, 50), "level2    ", inline='level 2', group="trace")
htf2.trace.trace_c_style   := input.string('----', '', options = ['⎯⎯⎯', '----', '····'], inline='level 2', group="trace")
htf2.trace.trace_c_size    := input.int(3, '', options = [1,2,3,4], inline='level 2', group="trace")

htf3.trace.trace_c_color   := input.color(color.new(color.yellow, 50), "level3    ", inline='level 3', group="trace")
htf3.trace.trace_c_style   := input.string('····', '', options = ['⎯⎯⎯', '----', '····'], inline='level 3', group="trace")
htf3.trace.trace_c_size    := input.int(4, '', options = [1,2,3,4], inline='level 3', group="trace")

htf4.trace.trace_c_color   := input.color(color.new(color.green, 50), "level4    ", inline='level 4', group="trace")
htf4.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='level 4', group="trace")
htf4.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='level 4', group="trace")

//+----------------------------------------+//
//+- Variables   

//+----------------------------------------+//
Helper    helper        = Helper.new()

color color_transparent = #ffffff00
var index               = 0  //不要動
var InitialPeriod       = 1  //你想從第幾分鐘開始
var totaladdPeriod      = 60 //總共想要做幾條等差的週期?  預設60條 你也可以1440條 但我電腦會爆掉,1440條的話 間隔要設定成1
var Interval            = 1  //間隔 也就是等差

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

method formattedtime(Helper helper, int i_HTF) =>
    helper.name := "THE DATE OF BAR"
    r = str.format("{0,date,yyyy-MM-dd HH:mm}", i_HTF)
    r

    
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

method Monitor(CandleSet candleSet) =>
    BOSdata bosdata = candleSet.bosdata
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    if isNewHTFCandle != 0 or barstate.isrealtime
        Candle candle    = Candle.new()
        candle.c        := bar_index==0 or barstate.isrealtime ? close : bosdata.temp
        candle.c_idx    := bar_index
        candleSet.candles.unshift(candle) //從這句話可以知道 index越靠近零 資料越新

        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)
    bosdata.temp := close //in fact "temp" is the lastest close price
    candleSet
 
method BOSJudge(CandleSet candleSet) =>
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    BOSdata bosdata = candleSet.bosdata
    int tf = time(timeframe.period)
    int tp = timeframe.in_seconds(timeframe.period)
    int tn = timeframe.in_seconds(candleSet.settings.htf)
    int k  = tn/tp
    if not barstate.isrealtime
        bosdata.dateinnumber := tf-tp*2000*k+tp*(k-1)*1000
    string strresult = helper.formattedtime(bosdata.dateinnumber)
    if candleSet.candles.size() > 0 and (isNewHTFCandle != 0 or barstate.isrealtime)
        Candle candle = candleSet.candles.first()
        if(bosdata.state == 1)
            bosdata.regclose1 := bosdata.regclose2
            bosdata.regclose2 := bosdata.regclose3
            bosdata.regclose3 := candle.c
            bosdata.slope1 := bosdata.regclose2 - bosdata.regclose1>0? 1 : -1
            bosdata.slope2 := bosdata.regclose3 - bosdata.regclose2>0? 1 : -1
            if((not na(bosdata.sbd)) and (not na(bosdata.sbu)))
                bosdata.state := 2 
            else if(not na(bosdata.sbd) and na(bosdata.sbu))  //no sky
                bosdata.state := 3
            else if(na(bosdata.sbd) and (not na(bosdata.sbu)))
                bosdata.state := 4
            else
                label.new(bar_index,high,text="GG")

        if(bosdata.state == 2)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.reg1key := bosdata.regclose2
                bosdata.reg1key_idx := index==0? 0 : index - 1 - k
                bosdata.strtemp1    := strresult
            //else //Buff_key1維持原樣
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx := na
                bosdata.sbd := bosdata.reg1key
                bosdata.sbd_idx := bosdata.reg1key_idx
                bosdata.s_dated := bosdata.strtemp1
                bosdata.temp2   := bosdata.regclose3
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd := na 
                bosdata.sbd_idx := na
                bosdata.sbu := bosdata.reg1key
                bosdata.sbu_idx := bosdata.reg1key_idx
                bosdata.s_dateu := bosdata.strtemp1
                bosdata.temp3   := bosdata.regclose3
            bosdata.state := 1
            
        if(bosdata.state == 3)//no sky
            if(bosdata.slope1 != bosdata.slope2) // build sky
                bosdata.strtemp2    := strresult
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index - 1 - k
                bosdata.sbu := bosdata.reg2key
                bosdata.sbu_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
                bosdata.s_dateu := bosdata.strtemp2
                bosdata.strtemp1 := bosdata.strtemp2
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd    := na
                bosdata.sbd_idx:= na
                bosdata.temp3  := bosdata.regclose3
            bosdata.state := 1
            
        if(bosdata.state == 4)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.strtemp2    := strresult
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index - 1 - k
                bosdata.sbd := bosdata.reg2key
                bosdata.sbd_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
                bosdata.s_dated := bosdata.strtemp2
                bosdata.strtemp1 := bosdata.strtemp2
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx:= na
                bosdata.temp2   := bosdata.regclose3
            bosdata.state := 1
            
    candleSet

method plotdata(CandleSet candleSet, int offset, int delta) =>
    int pcnt = 0
    BOSdata bosdata = candleSet.bosdata
    Trace   trace   = candleSet.trace
    var label l = candleSet.tfName
    var label l2 = na
    var label l_sbu = bosdata.sbu_l
    var label l_sbd = bosdata.sbd_l
    var label l_datesbu = bosdata.sbu_date
    var label l_datesbd = bosdata.sbd_date
    var label lt = candleSet.tfTimer
    var label lt2 = na
    var label l_pricesbu = bosdata.sbu_price
    var label l_pricesbd = bosdata.sbd_price
    var line  li_sbu   = bosdata.sbu_line
    var line  li_sbd   = bosdata.sbd_line
    string lbn  = helper.HTFName(candleSet.settings.htf)
    if candleSet.settings.show
        if not na(l_pricesbu)
            label.set_xy(l_pricesbu, offset+pcnt*delta, bosdata.sbu)
            label.set_text(l_pricesbu, str.tostring(bosdata.sbu))
        else
            l_pricesbu := label.new(offset+pcnt*delta, bosdata.sbu, 'err', color = color_transparent, textcolor = settings.price_label_color, size = settings.price_label_size, textalign = text.align_center)
        if not na(l_pricesbd)
            label.set_xy(l_pricesbd, offset+pcnt*delta, bosdata.sbd)
            label.set_text(l_pricesbd, str.tostring(bosdata.sbd))
        else
            l_pricesbd := label.new(offset+pcnt*delta, bosdata.sbd, 'err', color = color_transparent, textcolor = settings.price_label_color, size = settings.price_label_size, textalign = text.align_center)
        
        pcnt += 1
        if not na(l)
            label.set_xy(l, offset+pcnt*delta,bosdata.sbu)
        else
            l := label.new(offset+pcnt*delta, bosdata.sbu, lbn, color = color_transparent, textcolor = settings.htf_label_color, size = settings.htf_label_size, textalign = text.align_center)
        if not na(l2)
            label.set_xy(l2, offset+pcnt*delta,bosdata.sbd)
        else
            l2 := label.new(offset+pcnt*delta, bosdata.sbd, lbn, color = color_transparent, textcolor = settings.htf_label_color, size = settings.htf_label_size, textalign = text.align_center)
        pcnt += 1
        if not na(l_datesbu)
            label.set_xy(l_datesbu, offset+pcnt*delta,bosdata.sbu)
            label.set_text(l_datesbu, bosdata.s_dateu)
        else
            l_datesbu := label.new(offset+pcnt*delta, bosdata.sbu, 'ini', color = color_transparent, textcolor = settings.date_label_color, size = settings.date_label_size, textalign = text.align_center)
        if not na(l_datesbd)
            label.set_xy(l_datesbd, offset+pcnt*delta,bosdata.sbd)
            label.set_text(l_datesbd, bosdata.s_dated)
        else
            l_datesbd := label.new(offset+pcnt*delta, bosdata.sbd, 'ini', color = color_transparent, textcolor = settings.date_label_color, size = settings.date_label_size, textalign = text.align_center)
        pcnt += 1
        if not na(lt)
            label.set_xy(lt, offset+pcnt*delta,bosdata.sbu)
            label.set_text(lt,helper.RemainingTime(candleSet.settings.htf))
        else
            lt := label.new(offset+pcnt*delta, bosdata.sbu, helper.RemainingTime(candleSet.settings.htf), color = color_transparent, textcolor = settings.htf_timer_color, size = settings.htf_timer_size, textalign = text.align_center)
        if not na(lt2)
            label.set_xy(lt2, offset+pcnt*delta,bosdata.sbd)
            label.set_text(lt2,helper.RemainingTime(candleSet.settings.htf))
        else
            lt2 := label.new(offset+pcnt*delta, bosdata.sbd, helper.RemainingTime(candleSet.settings.htf), color = color_transparent, textcolor = settings.htf_timer_color, size = settings.htf_timer_size, textalign = text.align_center)
        pcnt += 1
        if not na(l_sbu)
            label.set_xy(l_sbu, offset+pcnt*delta,bosdata.sbu)
        else
            l_sbu := label.new(offset+pcnt*delta, bosdata.sbu, "SBU", color = color_transparent, textcolor = settings.sbu_label_color, size = settings.sbu_label_size, textalign = text.align_center)
        if not na(l_sbd)
            label.set_xy(l_sbd, offset+pcnt*delta,bosdata.sbd)
        else
            l_sbd := label.new(offset+pcnt*delta, bosdata.sbd, "SBD", color = color_transparent, textcolor = settings.sbd_label_color, size = settings.sbd_label_size, textalign = text.align_center)
        pcnt += 1    
        if not na(li_sbu)
            line.set_xy1(li_sbu, bosdata.sbu_idx, bosdata.sbu)
            line.set_xy2(li_sbu, offset, bosdata.sbu)
        else
            li_sbu := line.new(bar_index, bosdata.sbu, offset, bosdata.sbu, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
        if not na(li_sbd)
            line.set_xy1(li_sbd, bosdata.sbd_idx, bosdata.sbd)
            line.set_xy2(li_sbd, offset, bosdata.sbd)
        else
            li_sbd := line.new(bar_index, bosdata.sbd, offset, bosdata.sbd, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
    candleSet

method MaxNormalSet(ValueDecisionReg maxnormal, CandleSet candleSet) =>
    ValueDecisionReg m1 = maxnormal
    CandleSet        cs = candleSet
    var bool         fg = true 
    if fg
        m1.value            := 0
        m1.vtext            := "maxprice (possible sbd): "
        m1.vdecisionname    := "MaxNormalSet"
        fg                  := false
    m1.vtemp  := cs.bosdata.temp3
    if m1.vtemp > m1.value
        m1.value        := m1.vtemp
        m1.vname        := cs.settings.htf
    m1.vremntime    := helper.RemainingTime(m1.vname)
    maxnormal

method MinNormalSet(ValueDecisionReg minnormal, CandleSet candleSet) =>
    ValueDecisionReg m1 = minnormal
    CandleSet        cs = candleSet
    var bool         fg = true 
    if fg
        m1.value            := 99999999
        m1.vtext            := "minprice (possible sbu): "
        m1.vdecisionname    := "MinNormalSet"
        fg                  := false
    m1.vtemp  := cs.bosdata.temp2
    if m1.vtemp < m1.value
        m1.value  := m1.vtemp
        m1.vname  := cs.settings.htf
    m1.vremntime    := helper.RemainingTime(m1.vname)
    minnormal

method HighestsbdSet(ValueDecisionReg highestsbd, CandleSet candleSet) =>
    ValueDecisionReg m1 = highestsbd
    CandleSet        cs = candleSet
    var bool         fg = true 
    if fg
        m1.value            := 0
        m1.vtext            := "highestsbd: "
        m1.vdecisionname    := "HighestsbdSet"
        fg                  := false
    if cs.bosdata.sbd > m1.value
        m1.value := cs.bosdata.sbd
        m1.vidx  := cs.bosdata.sbd_idx
        m1.vname := cs.settings.htf
        m1.vdate := cs.bosdata.s_dated
    m1.vremntime    := helper.RemainingTime(m1.vname)
    highestsbd

method LowestsbuSet (ValueDecisionReg lowestsbu, CandleSet candleSet) =>
    ValueDecisionReg m1 = lowestsbu
    CandleSet        cs = candleSet
    var bool         fg = true 
    if fg
        m1.value            := 99999999
        m1.vtext            := "lowestsbu: "
        m1.vdecisionname    := "LowestsbuSet"
        fg                  := false
    if cs.bosdata.sbu < m1.value
        m1.value := cs.bosdata.sbu
        m1.vidx  := cs.bosdata.sbu_idx
        m1.vname := cs.settings.htf
        m1.vdate := cs.bosdata.s_dateu
    m1.vremntime    := helper.RemainingTime(m1.vname)
    lowestsbu

method addplot (ValueDecisionReg decision, int offset) =>
    ValueDecisionReg m1 = decision
    if m1.vdecisionname == "LowestsbuSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+5, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value            := 99999999
    if m1.vdecisionname == "HighestsbdSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value            := 0
    if m1.vdecisionname == "MaxNormalSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+5, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value            := 0
    if m1.vdecisionname == "MinNormalSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value)  + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value            := 99999999
    decision

//+---------------Main------------------+//
int cnt    = 0
int last   = helper.HTFEnabled()
int delta  = settings.text_buffer
int offset = settings.offset + bar_index
//+---------------ADD------------------+//

//+---------------add var------------------+//

var CandleSet htfadd1                     = CandleSet.new()
var CandleSettings SettingsHTFadd1        = CandleSettings.new()
var Candle[] candlesadd1                  = array.new<Candle>(0)
var BOSdata bosdataadd1                   = BOSdata.new()

htfadd1.settings                 := SettingsHTFadd1
htfadd1.candles                  := candlesadd1
htfadd1.bosdata                  := bosdataadd1
htfadd1.settings.htf             := '1'
htfadd1.settings.max_memory      := 10
htfadd1.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd1)
    LowestsbuSet(lowestsbu, htfadd1) 
    MaxNormalSet(maxnormal, htfadd1)
    MinNormalSet(minnormal, htfadd1)

var CandleSet htfadd2                     = CandleSet.new()
var CandleSettings SettingsHTFadd2        = CandleSettings.new()
var Candle[] candlesadd2                  = array.new<Candle>(0)
var BOSdata bosdataadd2                   = BOSdata.new()

htfadd2.settings                 := SettingsHTFadd2
htfadd2.candles                  := candlesadd2
htfadd2.bosdata                  := bosdataadd2
htfadd2.settings.htf             := '2'
htfadd2.settings.max_memory      := 10
htfadd2.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd2)
    LowestsbuSet(lowestsbu, htfadd2) 
    MaxNormalSet(maxnormal, htfadd2)
    MinNormalSet(minnormal, htfadd2)

var CandleSet htfadd3                     = CandleSet.new()
var CandleSettings SettingsHTFadd3        = CandleSettings.new()
var Candle[] candlesadd3                  = array.new<Candle>(0)
var BOSdata bosdataadd3                   = BOSdata.new()

htfadd3.settings                 := SettingsHTFadd3
htfadd3.candles                  := candlesadd3
htfadd3.bosdata                  := bosdataadd3
htfadd3.settings.htf             := '3'
htfadd3.settings.max_memory      := 10
htfadd3.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd3)
    LowestsbuSet(lowestsbu, htfadd3) 
    MaxNormalSet(maxnormal, htfadd3)
    MinNormalSet(minnormal, htfadd3)

var CandleSet htfadd4                     = CandleSet.new()
var CandleSettings SettingsHTFadd4        = CandleSettings.new()
var Candle[] candlesadd4                  = array.new<Candle>(0)
var BOSdata bosdataadd4                   = BOSdata.new()

htfadd4.settings                 := SettingsHTFadd4
htfadd4.candles                  := candlesadd4
htfadd4.bosdata                  := bosdataadd4
htfadd4.settings.htf             := '4'
htfadd4.settings.max_memory      := 10
htfadd4.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd4)
    LowestsbuSet(lowestsbu, htfadd4) 
    MaxNormalSet(maxnormal, htfadd4)
    MinNormalSet(minnormal, htfadd4)

var CandleSet htfadd5                     = CandleSet.new()
var CandleSettings SettingsHTFadd5        = CandleSettings.new()
var Candle[] candlesadd5                  = array.new<Candle>(0)
var BOSdata bosdataadd5                   = BOSdata.new()

htfadd5.settings                 := SettingsHTFadd5
htfadd5.candles                  := candlesadd5
htfadd5.bosdata                  := bosdataadd5
htfadd5.settings.htf             := '5'
htfadd5.settings.max_memory      := 10
htfadd5.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd5)
    LowestsbuSet(lowestsbu, htfadd5) 
    MaxNormalSet(maxnormal, htfadd5)
    MinNormalSet(minnormal, htfadd5)

var CandleSet htfadd6                     = CandleSet.new()
var CandleSettings SettingsHTFadd6        = CandleSettings.new()
var Candle[] candlesadd6                  = array.new<Candle>(0)
var BOSdata bosdataadd6                   = BOSdata.new()

htfadd6.settings                 := SettingsHTFadd6
htfadd6.candles                  := candlesadd6
htfadd6.bosdata                  := bosdataadd6
htfadd6.settings.htf             := '6'
htfadd6.settings.max_memory      := 10
htfadd6.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd6)
    LowestsbuSet(lowestsbu, htfadd6) 
    MaxNormalSet(maxnormal, htfadd6)
    MinNormalSet(minnormal, htfadd6)

var CandleSet htfadd7                     = CandleSet.new()
var CandleSettings SettingsHTFadd7        = CandleSettings.new()
var Candle[] candlesadd7                  = array.new<Candle>(0)
var BOSdata bosdataadd7                   = BOSdata.new()

htfadd7.settings                 := SettingsHTFadd7
htfadd7.candles                  := candlesadd7
htfadd7.bosdata                  := bosdataadd7
htfadd7.settings.htf             := '7'
htfadd7.settings.max_memory      := 10
htfadd7.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd7)
    LowestsbuSet(lowestsbu, htfadd7) 
    MaxNormalSet(maxnormal, htfadd7)
    MinNormalSet(minnormal, htfadd7)

var CandleSet htfadd8                     = CandleSet.new()
var CandleSettings SettingsHTFadd8        = CandleSettings.new()
var Candle[] candlesadd8                  = array.new<Candle>(0)
var BOSdata bosdataadd8                   = BOSdata.new()

htfadd8.settings                 := SettingsHTFadd8
htfadd8.candles                  := candlesadd8
htfadd8.bosdata                  := bosdataadd8
htfadd8.settings.htf             := '8'
htfadd8.settings.max_memory      := 10
htfadd8.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd8)
    LowestsbuSet(lowestsbu, htfadd8) 
    MaxNormalSet(maxnormal, htfadd8)
    MinNormalSet(minnormal, htfadd8)

var CandleSet htfadd9                     = CandleSet.new()
var CandleSettings SettingsHTFadd9        = CandleSettings.new()
var Candle[] candlesadd9                  = array.new<Candle>(0)
var BOSdata bosdataadd9                   = BOSdata.new()

htfadd9.settings                 := SettingsHTFadd9
htfadd9.candles                  := candlesadd9
htfadd9.bosdata                  := bosdataadd9
htfadd9.settings.htf             := '9'
htfadd9.settings.max_memory      := 10
htfadd9.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd9)
    LowestsbuSet(lowestsbu, htfadd9) 
    MaxNormalSet(maxnormal, htfadd9)
    MinNormalSet(minnormal, htfadd9)

var CandleSet htfadd10                     = CandleSet.new()
var CandleSettings SettingsHTFadd10        = CandleSettings.new()
var Candle[] candlesadd10                  = array.new<Candle>(0)
var BOSdata bosdataadd10                   = BOSdata.new()

htfadd10.settings                 := SettingsHTFadd10
htfadd10.candles                  := candlesadd10
htfadd10.bosdata                  := bosdataadd10
htfadd10.settings.htf             := '10'
htfadd10.settings.max_memory      := 10
htfadd10.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd10)
    LowestsbuSet(lowestsbu, htfadd10) 
    MaxNormalSet(maxnormal, htfadd10)
    MinNormalSet(minnormal, htfadd10)

var CandleSet htfadd11                     = CandleSet.new()
var CandleSettings SettingsHTFadd11        = CandleSettings.new()
var Candle[] candlesadd11                  = array.new<Candle>(0)
var BOSdata bosdataadd11                   = BOSdata.new()

htfadd11.settings                 := SettingsHTFadd11
htfadd11.candles                  := candlesadd11
htfadd11.bosdata                  := bosdataadd11
htfadd11.settings.htf             := '11'
htfadd11.settings.max_memory      := 10
htfadd11.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd11)
    LowestsbuSet(lowestsbu, htfadd11) 
    MaxNormalSet(maxnormal, htfadd11)
    MinNormalSet(minnormal, htfadd11)

var CandleSet htfadd12                     = CandleSet.new()
var CandleSettings SettingsHTFadd12        = CandleSettings.new()
var Candle[] candlesadd12                  = array.new<Candle>(0)
var BOSdata bosdataadd12                   = BOSdata.new()

htfadd12.settings                 := SettingsHTFadd12
htfadd12.candles                  := candlesadd12
htfadd12.bosdata                  := bosdataadd12
htfadd12.settings.htf             := '12'
htfadd12.settings.max_memory      := 10
htfadd12.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd12)
    LowestsbuSet(lowestsbu, htfadd12) 
    MaxNormalSet(maxnormal, htfadd12)
    MinNormalSet(minnormal, htfadd12)

var CandleSet htfadd13                     = CandleSet.new()
var CandleSettings SettingsHTFadd13        = CandleSettings.new()
var Candle[] candlesadd13                  = array.new<Candle>(0)
var BOSdata bosdataadd13                   = BOSdata.new()

htfadd13.settings                 := SettingsHTFadd13
htfadd13.candles                  := candlesadd13
htfadd13.bosdata                  := bosdataadd13
htfadd13.settings.htf             := '13'
htfadd13.settings.max_memory      := 10
htfadd13.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd13)
    LowestsbuSet(lowestsbu, htfadd13) 
    MaxNormalSet(maxnormal, htfadd13)
    MinNormalSet(minnormal, htfadd13)

var CandleSet htfadd14                     = CandleSet.new()
var CandleSettings SettingsHTFadd14        = CandleSettings.new()
var Candle[] candlesadd14                  = array.new<Candle>(0)
var BOSdata bosdataadd14                   = BOSdata.new()

htfadd14.settings                 := SettingsHTFadd14
htfadd14.candles                  := candlesadd14
htfadd14.bosdata                  := bosdataadd14
htfadd14.settings.htf             := '14'
htfadd14.settings.max_memory      := 10
htfadd14.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd14)
    LowestsbuSet(lowestsbu, htfadd14) 
    MaxNormalSet(maxnormal, htfadd14)
    MinNormalSet(minnormal, htfadd14)

var CandleSet htfadd15                     = CandleSet.new()
var CandleSettings SettingsHTFadd15        = CandleSettings.new()
var Candle[] candlesadd15                  = array.new<Candle>(0)
var BOSdata bosdataadd15                   = BOSdata.new()

htfadd15.settings                 := SettingsHTFadd15
htfadd15.candles                  := candlesadd15
htfadd15.bosdata                  := bosdataadd15
htfadd15.settings.htf             := '15'
htfadd15.settings.max_memory      := 10
htfadd15.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd15)
    LowestsbuSet(lowestsbu, htfadd15) 
    MaxNormalSet(maxnormal, htfadd15)
    MinNormalSet(minnormal, htfadd15)

var CandleSet htfadd16                     = CandleSet.new()
var CandleSettings SettingsHTFadd16        = CandleSettings.new()
var Candle[] candlesadd16                  = array.new<Candle>(0)
var BOSdata bosdataadd16                   = BOSdata.new()

htfadd16.settings                 := SettingsHTFadd16
htfadd16.candles                  := candlesadd16
htfadd16.bosdata                  := bosdataadd16
htfadd16.settings.htf             := '16'
htfadd16.settings.max_memory      := 10
htfadd16.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd16)
    LowestsbuSet(lowestsbu, htfadd16) 
    MaxNormalSet(maxnormal, htfadd16)
    MinNormalSet(minnormal, htfadd16)

var CandleSet htfadd17                     = CandleSet.new()
var CandleSettings SettingsHTFadd17        = CandleSettings.new()
var Candle[] candlesadd17                  = array.new<Candle>(0)
var BOSdata bosdataadd17                   = BOSdata.new()

htfadd17.settings                 := SettingsHTFadd17
htfadd17.candles                  := candlesadd17
htfadd17.bosdata                  := bosdataadd17
htfadd17.settings.htf             := '17'
htfadd17.settings.max_memory      := 10
htfadd17.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd17)
    LowestsbuSet(lowestsbu, htfadd17) 
    MaxNormalSet(maxnormal, htfadd17)
    MinNormalSet(minnormal, htfadd17)

var CandleSet htfadd18                     = CandleSet.new()
var CandleSettings SettingsHTFadd18        = CandleSettings.new()
var Candle[] candlesadd18                  = array.new<Candle>(0)
var BOSdata bosdataadd18                   = BOSdata.new()

htfadd18.settings                 := SettingsHTFadd18
htfadd18.candles                  := candlesadd18
htfadd18.bosdata                  := bosdataadd18
htfadd18.settings.htf             := '18'
htfadd18.settings.max_memory      := 10
htfadd18.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd18)
    LowestsbuSet(lowestsbu, htfadd18) 
    MaxNormalSet(maxnormal, htfadd18)
    MinNormalSet(minnormal, htfadd18)

var CandleSet htfadd19                     = CandleSet.new()
var CandleSettings SettingsHTFadd19        = CandleSettings.new()
var Candle[] candlesadd19                  = array.new<Candle>(0)
var BOSdata bosdataadd19                   = BOSdata.new()

htfadd19.settings                 := SettingsHTFadd19
htfadd19.candles                  := candlesadd19
htfadd19.bosdata                  := bosdataadd19
htfadd19.settings.htf             := '19'
htfadd19.settings.max_memory      := 10
htfadd19.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd19)
    LowestsbuSet(lowestsbu, htfadd19) 
    MaxNormalSet(maxnormal, htfadd19)
    MinNormalSet(minnormal, htfadd19)

var CandleSet htfadd20                     = CandleSet.new()
var CandleSettings SettingsHTFadd20        = CandleSettings.new()
var Candle[] candlesadd20                  = array.new<Candle>(0)
var BOSdata bosdataadd20                   = BOSdata.new()

htfadd20.settings                 := SettingsHTFadd20
htfadd20.candles                  := candlesadd20
htfadd20.bosdata                  := bosdataadd20
htfadd20.settings.htf             := '20'
htfadd20.settings.max_memory      := 10
htfadd20.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd20)
    LowestsbuSet(lowestsbu, htfadd20) 
    MaxNormalSet(maxnormal, htfadd20)
    MinNormalSet(minnormal, htfadd20)

var CandleSet htfadd21                     = CandleSet.new()
var CandleSettings SettingsHTFadd21        = CandleSettings.new()
var Candle[] candlesadd21                  = array.new<Candle>(0)
var BOSdata bosdataadd21                   = BOSdata.new()

htfadd21.settings                 := SettingsHTFadd21
htfadd21.candles                  := candlesadd21
htfadd21.bosdata                  := bosdataadd21
htfadd21.settings.htf             := '21'
htfadd21.settings.max_memory      := 10
htfadd21.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd21)
    LowestsbuSet(lowestsbu, htfadd21) 
    MaxNormalSet(maxnormal, htfadd21)
    MinNormalSet(minnormal, htfadd21)

var CandleSet htfadd22                     = CandleSet.new()
var CandleSettings SettingsHTFadd22        = CandleSettings.new()
var Candle[] candlesadd22                  = array.new<Candle>(0)
var BOSdata bosdataadd22                   = BOSdata.new()

htfadd22.settings                 := SettingsHTFadd22
htfadd22.candles                  := candlesadd22
htfadd22.bosdata                  := bosdataadd22
htfadd22.settings.htf             := '22'
htfadd22.settings.max_memory      := 10
htfadd22.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd22)
    LowestsbuSet(lowestsbu, htfadd22) 
    MaxNormalSet(maxnormal, htfadd22)
    MinNormalSet(minnormal, htfadd22)

var CandleSet htfadd23                     = CandleSet.new()
var CandleSettings SettingsHTFadd23        = CandleSettings.new()
var Candle[] candlesadd23                  = array.new<Candle>(0)
var BOSdata bosdataadd23                   = BOSdata.new()

htfadd23.settings                 := SettingsHTFadd23
htfadd23.candles                  := candlesadd23
htfadd23.bosdata                  := bosdataadd23
htfadd23.settings.htf             := '23'
htfadd23.settings.max_memory      := 10
htfadd23.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd23)
    LowestsbuSet(lowestsbu, htfadd23) 
    MaxNormalSet(maxnormal, htfadd23)
    MinNormalSet(minnormal, htfadd23)

var CandleSet htfadd24                     = CandleSet.new()
var CandleSettings SettingsHTFadd24        = CandleSettings.new()
var Candle[] candlesadd24                  = array.new<Candle>(0)
var BOSdata bosdataadd24                   = BOSdata.new()

htfadd24.settings                 := SettingsHTFadd24
htfadd24.candles                  := candlesadd24
htfadd24.bosdata                  := bosdataadd24
htfadd24.settings.htf             := '24'
htfadd24.settings.max_memory      := 10
htfadd24.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd24)
    LowestsbuSet(lowestsbu, htfadd24) 
    MaxNormalSet(maxnormal, htfadd24)
    MinNormalSet(minnormal, htfadd24)

var CandleSet htfadd25                     = CandleSet.new()
var CandleSettings SettingsHTFadd25        = CandleSettings.new()
var Candle[] candlesadd25                  = array.new<Candle>(0)
var BOSdata bosdataadd25                   = BOSdata.new()

htfadd25.settings                 := SettingsHTFadd25
htfadd25.candles                  := candlesadd25
htfadd25.bosdata                  := bosdataadd25
htfadd25.settings.htf             := '25'
htfadd25.settings.max_memory      := 10
htfadd25.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd25)
    LowestsbuSet(lowestsbu, htfadd25) 
    MaxNormalSet(maxnormal, htfadd25)
    MinNormalSet(minnormal, htfadd25)

var CandleSet htfadd26                     = CandleSet.new()
var CandleSettings SettingsHTFadd26        = CandleSettings.new()
var Candle[] candlesadd26                  = array.new<Candle>(0)
var BOSdata bosdataadd26                   = BOSdata.new()

htfadd26.settings                 := SettingsHTFadd26
htfadd26.candles                  := candlesadd26
htfadd26.bosdata                  := bosdataadd26
htfadd26.settings.htf             := '26'
htfadd26.settings.max_memory      := 10
htfadd26.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd26)
    LowestsbuSet(lowestsbu, htfadd26) 
    MaxNormalSet(maxnormal, htfadd26)
    MinNormalSet(minnormal, htfadd26)

var CandleSet htfadd27                     = CandleSet.new()
var CandleSettings SettingsHTFadd27        = CandleSettings.new()
var Candle[] candlesadd27                  = array.new<Candle>(0)
var BOSdata bosdataadd27                   = BOSdata.new()

htfadd27.settings                 := SettingsHTFadd27
htfadd27.candles                  := candlesadd27
htfadd27.bosdata                  := bosdataadd27
htfadd27.settings.htf             := '27'
htfadd27.settings.max_memory      := 10
htfadd27.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd27)
    LowestsbuSet(lowestsbu, htfadd27) 
    MaxNormalSet(maxnormal, htfadd27)
    MinNormalSet(minnormal, htfadd27)

var CandleSet htfadd28                     = CandleSet.new()
var CandleSettings SettingsHTFadd28        = CandleSettings.new()
var Candle[] candlesadd28                  = array.new<Candle>(0)
var BOSdata bosdataadd28                   = BOSdata.new()

htfadd28.settings                 := SettingsHTFadd28
htfadd28.candles                  := candlesadd28
htfadd28.bosdata                  := bosdataadd28
htfadd28.settings.htf             := '28'
htfadd28.settings.max_memory      := 10
htfadd28.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd28)
    LowestsbuSet(lowestsbu, htfadd28) 
    MaxNormalSet(maxnormal, htfadd28)
    MinNormalSet(minnormal, htfadd28)

var CandleSet htfadd29                     = CandleSet.new()
var CandleSettings SettingsHTFadd29        = CandleSettings.new()
var Candle[] candlesadd29                  = array.new<Candle>(0)
var BOSdata bosdataadd29                   = BOSdata.new()

htfadd29.settings                 := SettingsHTFadd29
htfadd29.candles                  := candlesadd29
htfadd29.bosdata                  := bosdataadd29
htfadd29.settings.htf             := '29'
htfadd29.settings.max_memory      := 10
htfadd29.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd29)
    LowestsbuSet(lowestsbu, htfadd29) 
    MaxNormalSet(maxnormal, htfadd29)
    MinNormalSet(minnormal, htfadd29)

var CandleSet htfadd30                     = CandleSet.new()
var CandleSettings SettingsHTFadd30        = CandleSettings.new()
var Candle[] candlesadd30                  = array.new<Candle>(0)
var BOSdata bosdataadd30                   = BOSdata.new()

htfadd30.settings                 := SettingsHTFadd30
htfadd30.candles                  := candlesadd30
htfadd30.bosdata                  := bosdataadd30
htfadd30.settings.htf             := '30'
htfadd30.settings.max_memory      := 10
htfadd30.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd30)
    LowestsbuSet(lowestsbu, htfadd30) 
    MaxNormalSet(maxnormal, htfadd30)
    MinNormalSet(minnormal, htfadd30)

var CandleSet htfadd31                     = CandleSet.new()
var CandleSettings SettingsHTFadd31        = CandleSettings.new()
var Candle[] candlesadd31                  = array.new<Candle>(0)
var BOSdata bosdataadd31                   = BOSdata.new()

htfadd31.settings                 := SettingsHTFadd31
htfadd31.candles                  := candlesadd31
htfadd31.bosdata                  := bosdataadd31
htfadd31.settings.htf             := '31'
htfadd31.settings.max_memory      := 10
htfadd31.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd31)
    LowestsbuSet(lowestsbu, htfadd31) 
    MaxNormalSet(maxnormal, htfadd31)
    MinNormalSet(minnormal, htfadd31)

var CandleSet htfadd32                     = CandleSet.new()
var CandleSettings SettingsHTFadd32        = CandleSettings.new()
var Candle[] candlesadd32                  = array.new<Candle>(0)
var BOSdata bosdataadd32                   = BOSdata.new()

htfadd32.settings                 := SettingsHTFadd32
htfadd32.candles                  := candlesadd32
htfadd32.bosdata                  := bosdataadd32
htfadd32.settings.htf             := '32'
htfadd32.settings.max_memory      := 10
htfadd32.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd32)
    LowestsbuSet(lowestsbu, htfadd32) 
    MaxNormalSet(maxnormal, htfadd32)
    MinNormalSet(minnormal, htfadd32)

var CandleSet htfadd33                     = CandleSet.new()
var CandleSettings SettingsHTFadd33        = CandleSettings.new()
var Candle[] candlesadd33                  = array.new<Candle>(0)
var BOSdata bosdataadd33                   = BOSdata.new()

htfadd33.settings                 := SettingsHTFadd33
htfadd33.candles                  := candlesadd33
htfadd33.bosdata                  := bosdataadd33
htfadd33.settings.htf             := '33'
htfadd33.settings.max_memory      := 10
htfadd33.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd33)
    LowestsbuSet(lowestsbu, htfadd33) 
    MaxNormalSet(maxnormal, htfadd33)
    MinNormalSet(minnormal, htfadd33)

var CandleSet htfadd34                     = CandleSet.new()
var CandleSettings SettingsHTFadd34        = CandleSettings.new()
var Candle[] candlesadd34                  = array.new<Candle>(0)
var BOSdata bosdataadd34                   = BOSdata.new()

htfadd34.settings                 := SettingsHTFadd34
htfadd34.candles                  := candlesadd34
htfadd34.bosdata                  := bosdataadd34
htfadd34.settings.htf             := '34'
htfadd34.settings.max_memory      := 10
htfadd34.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd34)
    LowestsbuSet(lowestsbu, htfadd34) 
    MaxNormalSet(maxnormal, htfadd34)
    MinNormalSet(minnormal, htfadd34)

var CandleSet htfadd35                     = CandleSet.new()
var CandleSettings SettingsHTFadd35        = CandleSettings.new()
var Candle[] candlesadd35                  = array.new<Candle>(0)
var BOSdata bosdataadd35                   = BOSdata.new()

htfadd35.settings                 := SettingsHTFadd35
htfadd35.candles                  := candlesadd35
htfadd35.bosdata                  := bosdataadd35
htfadd35.settings.htf             := '35'
htfadd35.settings.max_memory      := 10
htfadd35.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd35)
    LowestsbuSet(lowestsbu, htfadd35) 
    MaxNormalSet(maxnormal, htfadd35)
    MinNormalSet(minnormal, htfadd35)

var CandleSet htfadd36                     = CandleSet.new()
var CandleSettings SettingsHTFadd36        = CandleSettings.new()
var Candle[] candlesadd36                  = array.new<Candle>(0)
var BOSdata bosdataadd36                   = BOSdata.new()

htfadd36.settings                 := SettingsHTFadd36
htfadd36.candles                  := candlesadd36
htfadd36.bosdata                  := bosdataadd36
htfadd36.settings.htf             := '36'
htfadd36.settings.max_memory      := 10
htfadd36.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd36)
    LowestsbuSet(lowestsbu, htfadd36) 
    MaxNormalSet(maxnormal, htfadd36)
    MinNormalSet(minnormal, htfadd36)

var CandleSet htfadd37                     = CandleSet.new()
var CandleSettings SettingsHTFadd37        = CandleSettings.new()
var Candle[] candlesadd37                  = array.new<Candle>(0)
var BOSdata bosdataadd37                   = BOSdata.new()

htfadd37.settings                 := SettingsHTFadd37
htfadd37.candles                  := candlesadd37
htfadd37.bosdata                  := bosdataadd37
htfadd37.settings.htf             := '37'
htfadd37.settings.max_memory      := 10
htfadd37.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd37)
    LowestsbuSet(lowestsbu, htfadd37) 
    MaxNormalSet(maxnormal, htfadd37)
    MinNormalSet(minnormal, htfadd37)

var CandleSet htfadd38                     = CandleSet.new()
var CandleSettings SettingsHTFadd38        = CandleSettings.new()
var Candle[] candlesadd38                  = array.new<Candle>(0)
var BOSdata bosdataadd38                   = BOSdata.new()

htfadd38.settings                 := SettingsHTFadd38
htfadd38.candles                  := candlesadd38
htfadd38.bosdata                  := bosdataadd38
htfadd38.settings.htf             := '38'
htfadd38.settings.max_memory      := 10
htfadd38.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd38)
    LowestsbuSet(lowestsbu, htfadd38) 
    MaxNormalSet(maxnormal, htfadd38)
    MinNormalSet(minnormal, htfadd38)

var CandleSet htfadd39                     = CandleSet.new()
var CandleSettings SettingsHTFadd39        = CandleSettings.new()
var Candle[] candlesadd39                  = array.new<Candle>(0)
var BOSdata bosdataadd39                   = BOSdata.new()

htfadd39.settings                 := SettingsHTFadd39
htfadd39.candles                  := candlesadd39
htfadd39.bosdata                  := bosdataadd39
htfadd39.settings.htf             := '39'
htfadd39.settings.max_memory      := 10
htfadd39.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd39)
    LowestsbuSet(lowestsbu, htfadd39) 
    MaxNormalSet(maxnormal, htfadd39)
    MinNormalSet(minnormal, htfadd39)

var CandleSet htfadd40                     = CandleSet.new()
var CandleSettings SettingsHTFadd40        = CandleSettings.new()
var Candle[] candlesadd40                  = array.new<Candle>(0)
var BOSdata bosdataadd40                   = BOSdata.new()

htfadd40.settings                 := SettingsHTFadd40
htfadd40.candles                  := candlesadd40
htfadd40.bosdata                  := bosdataadd40
htfadd40.settings.htf             := '40'
htfadd40.settings.max_memory      := 10
htfadd40.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd40)
    LowestsbuSet(lowestsbu, htfadd40) 
    MaxNormalSet(maxnormal, htfadd40)
    MinNormalSet(minnormal, htfadd40)

var CandleSet htfadd41                     = CandleSet.new()
var CandleSettings SettingsHTFadd41        = CandleSettings.new()
var Candle[] candlesadd41                  = array.new<Candle>(0)
var BOSdata bosdataadd41                   = BOSdata.new()

htfadd41.settings                 := SettingsHTFadd41
htfadd41.candles                  := candlesadd41
htfadd41.bosdata                  := bosdataadd41
htfadd41.settings.htf             := '41'
htfadd41.settings.max_memory      := 10
htfadd41.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd41)
    LowestsbuSet(lowestsbu, htfadd41) 
    MaxNormalSet(maxnormal, htfadd41)
    MinNormalSet(minnormal, htfadd41)

var CandleSet htfadd42                     = CandleSet.new()
var CandleSettings SettingsHTFadd42        = CandleSettings.new()
var Candle[] candlesadd42                  = array.new<Candle>(0)
var BOSdata bosdataadd42                   = BOSdata.new()

htfadd42.settings                 := SettingsHTFadd42
htfadd42.candles                  := candlesadd42
htfadd42.bosdata                  := bosdataadd42
htfadd42.settings.htf             := '42'
htfadd42.settings.max_memory      := 10
htfadd42.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd42)
    LowestsbuSet(lowestsbu, htfadd42) 
    MaxNormalSet(maxnormal, htfadd42)
    MinNormalSet(minnormal, htfadd42)

var CandleSet htfadd43                     = CandleSet.new()
var CandleSettings SettingsHTFadd43        = CandleSettings.new()
var Candle[] candlesadd43                  = array.new<Candle>(0)
var BOSdata bosdataadd43                   = BOSdata.new()

htfadd43.settings                 := SettingsHTFadd43
htfadd43.candles                  := candlesadd43
htfadd43.bosdata                  := bosdataadd43
htfadd43.settings.htf             := '43'
htfadd43.settings.max_memory      := 10
htfadd43.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd43)
    LowestsbuSet(lowestsbu, htfadd43) 
    MaxNormalSet(maxnormal, htfadd43)
    MinNormalSet(minnormal, htfadd43)

var CandleSet htfadd44                     = CandleSet.new()
var CandleSettings SettingsHTFadd44        = CandleSettings.new()
var Candle[] candlesadd44                  = array.new<Candle>(0)
var BOSdata bosdataadd44                   = BOSdata.new()

htfadd44.settings                 := SettingsHTFadd44
htfadd44.candles                  := candlesadd44
htfadd44.bosdata                  := bosdataadd44
htfadd44.settings.htf             := '44'
htfadd44.settings.max_memory      := 10
htfadd44.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd44)
    LowestsbuSet(lowestsbu, htfadd44) 
    MaxNormalSet(maxnormal, htfadd44)
    MinNormalSet(minnormal, htfadd44)

var CandleSet htfadd45                     = CandleSet.new()
var CandleSettings SettingsHTFadd45        = CandleSettings.new()
var Candle[] candlesadd45                  = array.new<Candle>(0)
var BOSdata bosdataadd45                   = BOSdata.new()

htfadd45.settings                 := SettingsHTFadd45
htfadd45.candles                  := candlesadd45
htfadd45.bosdata                  := bosdataadd45
htfadd45.settings.htf             := '45'
htfadd45.settings.max_memory      := 10
htfadd45.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd45)
    LowestsbuSet(lowestsbu, htfadd45) 
    MaxNormalSet(maxnormal, htfadd45)
    MinNormalSet(minnormal, htfadd45)

var CandleSet htfadd46                     = CandleSet.new()
var CandleSettings SettingsHTFadd46        = CandleSettings.new()
var Candle[] candlesadd46                  = array.new<Candle>(0)
var BOSdata bosdataadd46                   = BOSdata.new()

htfadd46.settings                 := SettingsHTFadd46
htfadd46.candles                  := candlesadd46
htfadd46.bosdata                  := bosdataadd46
htfadd46.settings.htf             := '46'
htfadd46.settings.max_memory      := 10
htfadd46.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd46)
    LowestsbuSet(lowestsbu, htfadd46) 
    MaxNormalSet(maxnormal, htfadd46)
    MinNormalSet(minnormal, htfadd46)

var CandleSet htfadd47                     = CandleSet.new()
var CandleSettings SettingsHTFadd47        = CandleSettings.new()
var Candle[] candlesadd47                  = array.new<Candle>(0)
var BOSdata bosdataadd47                   = BOSdata.new()

htfadd47.settings                 := SettingsHTFadd47
htfadd47.candles                  := candlesadd47
htfadd47.bosdata                  := bosdataadd47
htfadd47.settings.htf             := '47'
htfadd47.settings.max_memory      := 10
htfadd47.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd47)
    LowestsbuSet(lowestsbu, htfadd47) 
    MaxNormalSet(maxnormal, htfadd47)
    MinNormalSet(minnormal, htfadd47)

var CandleSet htfadd48                     = CandleSet.new()
var CandleSettings SettingsHTFadd48        = CandleSettings.new()
var Candle[] candlesadd48                  = array.new<Candle>(0)
var BOSdata bosdataadd48                   = BOSdata.new()

htfadd48.settings                 := SettingsHTFadd48
htfadd48.candles                  := candlesadd48
htfadd48.bosdata                  := bosdataadd48
htfadd48.settings.htf             := '48'
htfadd48.settings.max_memory      := 10
htfadd48.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd48)
    LowestsbuSet(lowestsbu, htfadd48) 
    MaxNormalSet(maxnormal, htfadd48)
    MinNormalSet(minnormal, htfadd48)

var CandleSet htfadd49                     = CandleSet.new()
var CandleSettings SettingsHTFadd49        = CandleSettings.new()
var Candle[] candlesadd49                  = array.new<Candle>(0)
var BOSdata bosdataadd49                   = BOSdata.new()

htfadd49.settings                 := SettingsHTFadd49
htfadd49.candles                  := candlesadd49
htfadd49.bosdata                  := bosdataadd49
htfadd49.settings.htf             := '49'
htfadd49.settings.max_memory      := 10
htfadd49.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd49)
    LowestsbuSet(lowestsbu, htfadd49) 
    MaxNormalSet(maxnormal, htfadd49)
    MinNormalSet(minnormal, htfadd49)

var CandleSet htfadd50                     = CandleSet.new()
var CandleSettings SettingsHTFadd50        = CandleSettings.new()
var Candle[] candlesadd50                  = array.new<Candle>(0)
var BOSdata bosdataadd50                   = BOSdata.new()

htfadd50.settings                 := SettingsHTFadd50
htfadd50.candles                  := candlesadd50
htfadd50.bosdata                  := bosdataadd50
htfadd50.settings.htf             := '50'
htfadd50.settings.max_memory      := 10
htfadd50.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd50)
    LowestsbuSet(lowestsbu, htfadd50) 
    MaxNormalSet(maxnormal, htfadd50)
    MinNormalSet(minnormal, htfadd50)

var CandleSet htfadd51                     = CandleSet.new()
var CandleSettings SettingsHTFadd51        = CandleSettings.new()
var Candle[] candlesadd51                  = array.new<Candle>(0)
var BOSdata bosdataadd51                   = BOSdata.new()

htfadd51.settings                 := SettingsHTFadd51
htfadd51.candles                  := candlesadd51
htfadd51.bosdata                  := bosdataadd51
htfadd51.settings.htf             := '51'
htfadd51.settings.max_memory      := 10
htfadd51.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd51)
    LowestsbuSet(lowestsbu, htfadd51) 
    MaxNormalSet(maxnormal, htfadd51)
    MinNormalSet(minnormal, htfadd51)

var CandleSet htfadd52                     = CandleSet.new()
var CandleSettings SettingsHTFadd52        = CandleSettings.new()
var Candle[] candlesadd52                  = array.new<Candle>(0)
var BOSdata bosdataadd52                   = BOSdata.new()

htfadd52.settings                 := SettingsHTFadd52
htfadd52.candles                  := candlesadd52
htfadd52.bosdata                  := bosdataadd52
htfadd52.settings.htf             := '52'
htfadd52.settings.max_memory      := 10
htfadd52.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd52)
    LowestsbuSet(lowestsbu, htfadd52) 
    MaxNormalSet(maxnormal, htfadd52)
    MinNormalSet(minnormal, htfadd52)

var CandleSet htfadd53                     = CandleSet.new()
var CandleSettings SettingsHTFadd53        = CandleSettings.new()
var Candle[] candlesadd53                  = array.new<Candle>(0)
var BOSdata bosdataadd53                   = BOSdata.new()

htfadd53.settings                 := SettingsHTFadd53
htfadd53.candles                  := candlesadd53
htfadd53.bosdata                  := bosdataadd53
htfadd53.settings.htf             := '53'
htfadd53.settings.max_memory      := 10
htfadd53.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd53)
    LowestsbuSet(lowestsbu, htfadd53) 
    MaxNormalSet(maxnormal, htfadd53)
    MinNormalSet(minnormal, htfadd53)

var CandleSet htfadd54                     = CandleSet.new()
var CandleSettings SettingsHTFadd54        = CandleSettings.new()
var Candle[] candlesadd54                  = array.new<Candle>(0)
var BOSdata bosdataadd54                   = BOSdata.new()

htfadd54.settings                 := SettingsHTFadd54
htfadd54.candles                  := candlesadd54
htfadd54.bosdata                  := bosdataadd54
htfadd54.settings.htf             := '54'
htfadd54.settings.max_memory      := 10
htfadd54.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd54)
    LowestsbuSet(lowestsbu, htfadd54) 
    MaxNormalSet(maxnormal, htfadd54)
    MinNormalSet(minnormal, htfadd54)

var CandleSet htfadd55                     = CandleSet.new()
var CandleSettings SettingsHTFadd55        = CandleSettings.new()
var Candle[] candlesadd55                  = array.new<Candle>(0)
var BOSdata bosdataadd55                   = BOSdata.new()

htfadd55.settings                 := SettingsHTFadd55
htfadd55.candles                  := candlesadd55
htfadd55.bosdata                  := bosdataadd55
htfadd55.settings.htf             := '55'
htfadd55.settings.max_memory      := 10
htfadd55.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd55)
    LowestsbuSet(lowestsbu, htfadd55) 
    MaxNormalSet(maxnormal, htfadd55)
    MinNormalSet(minnormal, htfadd55)

var CandleSet htfadd56                     = CandleSet.new()
var CandleSettings SettingsHTFadd56        = CandleSettings.new()
var Candle[] candlesadd56                  = array.new<Candle>(0)
var BOSdata bosdataadd56                   = BOSdata.new()

htfadd56.settings                 := SettingsHTFadd56
htfadd56.candles                  := candlesadd56
htfadd56.bosdata                  := bosdataadd56
htfadd56.settings.htf             := '56'
htfadd56.settings.max_memory      := 10
htfadd56.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd56)
    LowestsbuSet(lowestsbu, htfadd56) 
    MaxNormalSet(maxnormal, htfadd56)
    MinNormalSet(minnormal, htfadd56)

var CandleSet htfadd57                     = CandleSet.new()
var CandleSettings SettingsHTFadd57        = CandleSettings.new()
var Candle[] candlesadd57                  = array.new<Candle>(0)
var BOSdata bosdataadd57                   = BOSdata.new()

htfadd57.settings                 := SettingsHTFadd57
htfadd57.candles                  := candlesadd57
htfadd57.bosdata                  := bosdataadd57
htfadd57.settings.htf             := '57'
htfadd57.settings.max_memory      := 10
htfadd57.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd57)
    LowestsbuSet(lowestsbu, htfadd57) 
    MaxNormalSet(maxnormal, htfadd57)
    MinNormalSet(minnormal, htfadd57)

var CandleSet htfadd58                     = CandleSet.new()
var CandleSettings SettingsHTFadd58        = CandleSettings.new()
var Candle[] candlesadd58                  = array.new<Candle>(0)
var BOSdata bosdataadd58                   = BOSdata.new()

htfadd58.settings                 := SettingsHTFadd58
htfadd58.candles                  := candlesadd58
htfadd58.bosdata                  := bosdataadd58
htfadd58.settings.htf             := '58'
htfadd58.settings.max_memory      := 10
htfadd58.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd58)
    LowestsbuSet(lowestsbu, htfadd58) 
    MaxNormalSet(maxnormal, htfadd58)
    MinNormalSet(minnormal, htfadd58)

var CandleSet htfadd59                     = CandleSet.new()
var CandleSettings SettingsHTFadd59        = CandleSettings.new()
var Candle[] candlesadd59                  = array.new<Candle>(0)
var BOSdata bosdataadd59                   = BOSdata.new()

htfadd59.settings                 := SettingsHTFadd59
htfadd59.candles                  := candlesadd59
htfadd59.bosdata                  := bosdataadd59
htfadd59.settings.htf             := '59'
htfadd59.settings.max_memory      := 10
htfadd59.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd59)
    LowestsbuSet(lowestsbu, htfadd59) 
    MaxNormalSet(maxnormal, htfadd59)
    MinNormalSet(minnormal, htfadd59)

var CandleSet htfadd60                     = CandleSet.new()
var CandleSettings SettingsHTFadd60        = CandleSettings.new()
var Candle[] candlesadd60                  = array.new<Candle>(0)
var BOSdata bosdataadd60                   = BOSdata.new()

htfadd60.settings                 := SettingsHTFadd60
htfadd60.candles                  := candlesadd60
htfadd60.bosdata                  := bosdataadd60
htfadd60.settings.htf             := '60'
htfadd60.settings.max_memory      := 10
htfadd60.Monitor().BOSJudge()
if barstate.islast
    HighestsbdSet(highestsbd, htfadd60)
    LowestsbuSet(lowestsbu, htfadd60) 
    MaxNormalSet(maxnormal, htfadd60)
    MinNormalSet(minnormal, htfadd60)
//+---------------add var end------------------+//
if settings.add_show and barstate.isrealtime
    maxnormal.addplot(offset)
    minnormal.addplot(offset)
    highestsbd.addplot(offset)
    lowestsbu.addplot(offset)
    var line nowcloseline = na
    if not na(nowcloseline)
        line.set_xy1(nowcloseline, bar_index, close)
        line.set_xy2(nowcloseline, bar_index+2, close)
    else
        nowcloseline := line.new(bar_index, close, bar_index, close, xloc= xloc.bar_index, color = color.new(color.gray, 10), style = line.style_dotted , width = 4)       
//if barstate.islast
//    label.new(bar_index,close, str.tostring(htfadd15.bosdata.sbu) + "\n" + str.tostring(htfadd15.bosdata.sbd) + "\n" + "hello")
//+---------------ADD END------------------+//

if  htf1.settings.show and helper.ValidTimeframe(htf1.settings.htf)
    htf1.Monitor().BOSJudge()
    plotdata(htf1, offset, delta)
    cnt +=1
if  htf2.settings.show and helper.ValidTimeframe(htf2.settings.htf)
    htf2.Monitor().BOSJudge()
    plotdata(htf2, offset, delta)
    cnt +=1
if  htf3.settings.show and helper.ValidTimeframe(htf3.settings.htf)
    htf3.Monitor().BOSJudge()
    plotdata(htf3, offset, delta)
    cnt +=1
if  htf4.settings.show and helper.ValidTimeframe(htf4.settings.htf)
    htf4.Monitor().BOSJudge()
    plotdata(htf4, offset, delta)
if cnt>last
    label.new(bar_index,high,"over the 4line count limit")

////+------value ValueDecisionReg-----+//
//if settings.add_show 
//    for i = 0 to (totaladdPeriod-1)
//        MaxNormalSet(maxnormal, mulhtf.get(i))
//        MinNormalSet(minnormal, mulhtf.get(i))
//        HighestsbdSet(highestsbd, mulhtf.get(i))
//        LowestsbuSet(lowestsbu, mulhtf.get(i))
//    maxnormal.addplot(offset)
//    minnormal.addplot(offset)
//    highestsbd.addplot(offset)
//    lowestsbu.addplot(offset)
//if barstate.islast
//    label.new(bar_index, high, str.tostring(mulhtf.get(0).bosdata.sbu))
index += 1


