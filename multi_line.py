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
        candle.c        := bar_index==0? close : bosdata.temp
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
    if candleSet.candles.size() > 0 and isNewHTFCandle != 0
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
int cnt = 0
int last = helper.HTFEnabled()
int delta = settings.text_buffer
int offset = settings.offset + bar_index
//+---------------ADD------------------+//
var CandleSet[] mulhtf                          = array.new<CandleSet>(totaladdPeriod)
var Candle[] mulcandles                         = array.new<Candle>(0)
for i = 0 to (totaladdPeriod-1) //這邊初始化很重要 背起來
    if barstate.isfirst
        BOSdata addBosdata                          = BOSdata.new()   
        Candle  addcandle                           = Candle.new()
        CandleSettings addsettings                  = CandleSettings.new()
        addsettings.htf                             := str.tostring(InitialPeriod+Interval*i)
        addsettings.max_memory                      := 10            
        CandleSet addCandleSet                      = CandleSet.new()
        mulcandles.unshift(addcandle)
        addCandleSet.bosdata                        := addBosdata     
        addCandleSet.candles                        := mulcandles
        addCandleSet.settings                       := addsettings  
        mulhtf.set(i,addCandleSet) 
    //end if
    mulhtf.get(i).Monitor().BOSJudge()

    HighestsbdSet(highestsbd, mulhtf.get(i))
    LowestsbuSet(lowestsbu, mulhtf.get(i)) 
    MaxNormalSet(maxnormal, mulhtf.get(i))
    MinNormalSet(minnormal, mulhtf.get(i))
    
//end for
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
if barstate.islast
    label.new(bar_index,close, str.tostring(mulhtf.get(8).bosdata.sbu))
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


