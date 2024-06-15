//+-----filter the multiline after the timing and show that on figure -----+//
// © T.PanShuai29
//@version=5
indicator("addline", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)

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
var ValueDecisionReg highestsbd  = ValueDecisionReg.new(value=0)
var ValueDecisionReg lowestsbu  = ValueDecisionReg.new(value=99999999)
var ValueDecisionReg estmaxsbd  = ValueDecisionReg.new(vdecisionname="estmaxsbd", value=0, vtext="estmaxsbd: ")
var ValueDecisionReg estminsbu  = ValueDecisionReg.new(vdecisionname="estminsbu", value=99999999, vtext="estminsbu: ")


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
    if isNewHTFCandle != 0 
        Candle candle    = Candle.new()
        candle.c        := bar_index==0 ? close : bosdata.temp
        candle.c_idx    := bar_index
        candleSet.candles.unshift(candle) //從這句話可以知道 index越靠近零 資料越新

        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)
    bosdata.temp := close //in fact "temp" is the lastest close price
    candleSet

method Monitor_Est(CandleSet candleSet) =>
    if barstate.isrealtime
        Candle candle    = Candle.new()
        candle.c        := close
        candle.c_idx    := bar_index
        candleSet.candles.unshift(candle)
        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)
    candleSet

method BOSJudge(CandleSet candleSet) =>
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    BOSdata bosdata = candleSet.bosdata
    var bool fg          = true
    int tf = time(timeframe.period)
    int tp = timeframe.in_seconds(timeframe.period)
    int tn = timeframe.in_seconds(candleSet.settings.htf)
    int k  = tn/tp
    if fg
        bosdata.dateinnumber := tf-tp*2000*k+tp*(k-1)*1000
        fg                   := false
    string strresult = helper.formattedtime(bosdata.dateinnumber)
    if candleSet.candles.size() > 0 and isNewHTFCandle != 0 // 就算最新的出現 也必須遵守這個規定 為了讓結構穩定不亂序
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
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd := na 
                bosdata.sbd_idx := na
                bosdata.sbu := bosdata.reg1key
                bosdata.sbu_idx := bosdata.reg1key_idx
                bosdata.s_dateu := bosdata.strtemp1
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
            line.set_xy1(li_sbu, bar_index, bosdata.sbu)
            line.set_xy2(li_sbu, offset, bosdata.sbu)
        else
            li_sbu := line.new(bar_index, bosdata.sbu, offset, bosdata.sbu, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
        if not na(li_sbd)
            line.set_xy1(li_sbd, bar_index, bosdata.sbd)
            line.set_xy2(li_sbd, offset, bosdata.sbd)
        else
            li_sbd := line.new(bar_index, bosdata.sbd, offset, bosdata.sbd, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
    candleSet

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
    lowestsbu

method Predictor (CandleSet candleSet, ValueDecisionReg predictor) =>
    CandleSet        cs = candleSet
    ValueDecisionReg pt = predictor
    if pt.vdecisionname == "estmaxsbd"
        if pt.value < cs.bosdata.sbd  
            pt.value := cs.bosdata.sbd
            pt.vidx  := cs.bosdata.sbd_idx
            pt.vname := cs.settings.htf
            pt.vdate := cs.bosdata.s_dated
    if pt.vdecisionname == "estminsbu"
        if pt.value > cs.bosdata.sbu  
            pt.value := cs.bosdata.sbu
            pt.vidx  := cs.bosdata.sbu_idx
            pt.vname := cs.settings.htf
            pt.vdate := cs.bosdata.s_dateu
    predictor

method addplot (ValueDecisionReg decision, int offset) =>
    ValueDecisionReg m1 = decision
    m1.vremntime := helper.RemainingTime(m1.vname)
    if m1.vdecisionname == "LowestsbuSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset-5, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new( offset-5,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
    if m1.vdecisionname == "HighestsbdSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset-2, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset-2,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
    if m1.vdecisionname == "estmaxsbd"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+3, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset+3,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 0
    if m1.vdecisionname == "estminsbu"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+3, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value)  + "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset+3,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
    decision

//+---------------Main------------------+//
int cnt    = 0
int last   = helper.HTFEnabled()
int delta  = settings.text_buffer
int offset = settings.offset + bar_index
//+---------------ADD------------------+//

//+---------------add var------------------+//

var CandleSet htfadd60                     = CandleSet.new()
var CandleSettings SettingsHTFadd60        = CandleSettings.new()
var Candle[] candlesadd60                  = array.new<Candle>(0)
var BOSdata bosdataadd60                   = BOSdata.new()
htfadd60.settings                 := SettingsHTFadd60
htfadd60.candles                  := candlesadd60
htfadd60.bosdata                  := bosdataadd60
htfadd60.settings.htf             := '60'
htfadd60.settings.max_memory      := 10
var CandleSet htfadd61                     = CandleSet.new()
var CandleSettings SettingsHTFadd61        = CandleSettings.new()
var Candle[] candlesadd61                  = array.new<Candle>(0)
var BOSdata bosdataadd61                   = BOSdata.new()
htfadd61.settings                 := SettingsHTFadd61
htfadd61.candles                  := candlesadd61
htfadd61.bosdata                  := bosdataadd61
htfadd61.settings.htf             := '61'
htfadd61.settings.max_memory      := 10
var CandleSet htfadd62                     = CandleSet.new()
var CandleSettings SettingsHTFadd62        = CandleSettings.new()
var Candle[] candlesadd62                  = array.new<Candle>(0)
var BOSdata bosdataadd62                   = BOSdata.new()
htfadd62.settings                 := SettingsHTFadd62
htfadd62.candles                  := candlesadd62
htfadd62.bosdata                  := bosdataadd62
htfadd62.settings.htf             := '62'
htfadd62.settings.max_memory      := 10
var CandleSet htfadd63                     = CandleSet.new()
var CandleSettings SettingsHTFadd63        = CandleSettings.new()
var Candle[] candlesadd63                  = array.new<Candle>(0)
var BOSdata bosdataadd63                   = BOSdata.new()
htfadd63.settings                 := SettingsHTFadd63
htfadd63.candles                  := candlesadd63
htfadd63.bosdata                  := bosdataadd63
htfadd63.settings.htf             := '63'
htfadd63.settings.max_memory      := 10
var CandleSet htfadd64                     = CandleSet.new()
var CandleSettings SettingsHTFadd64        = CandleSettings.new()
var Candle[] candlesadd64                  = array.new<Candle>(0)
var BOSdata bosdataadd64                   = BOSdata.new()
htfadd64.settings                 := SettingsHTFadd64
htfadd64.candles                  := candlesadd64
htfadd64.bosdata                  := bosdataadd64
htfadd64.settings.htf             := '64'
htfadd64.settings.max_memory      := 10
var CandleSet htfadd65                     = CandleSet.new()
var CandleSettings SettingsHTFadd65        = CandleSettings.new()
var Candle[] candlesadd65                  = array.new<Candle>(0)
var BOSdata bosdataadd65                   = BOSdata.new()
htfadd65.settings                 := SettingsHTFadd65
htfadd65.candles                  := candlesadd65
htfadd65.bosdata                  := bosdataadd65
htfadd65.settings.htf             := '65'
htfadd65.settings.max_memory      := 10
var CandleSet htfadd66                     = CandleSet.new()
var CandleSettings SettingsHTFadd66        = CandleSettings.new()
var Candle[] candlesadd66                  = array.new<Candle>(0)
var BOSdata bosdataadd66                   = BOSdata.new()
htfadd66.settings                 := SettingsHTFadd66
htfadd66.candles                  := candlesadd66
htfadd66.bosdata                  := bosdataadd66
htfadd66.settings.htf             := '66'
htfadd66.settings.max_memory      := 10
var CandleSet htfadd67                     = CandleSet.new()
var CandleSettings SettingsHTFadd67        = CandleSettings.new()
var Candle[] candlesadd67                  = array.new<Candle>(0)
var BOSdata bosdataadd67                   = BOSdata.new()
htfadd67.settings                 := SettingsHTFadd67
htfadd67.candles                  := candlesadd67
htfadd67.bosdata                  := bosdataadd67
htfadd67.settings.htf             := '67'
htfadd67.settings.max_memory      := 10
var CandleSet htfadd68                     = CandleSet.new()
var CandleSettings SettingsHTFadd68        = CandleSettings.new()
var Candle[] candlesadd68                  = array.new<Candle>(0)
var BOSdata bosdataadd68                   = BOSdata.new()
htfadd68.settings                 := SettingsHTFadd68
htfadd68.candles                  := candlesadd68
htfadd68.bosdata                  := bosdataadd68
htfadd68.settings.htf             := '68'
htfadd68.settings.max_memory      := 10
var CandleSet htfadd69                     = CandleSet.new()
var CandleSettings SettingsHTFadd69        = CandleSettings.new()
var Candle[] candlesadd69                  = array.new<Candle>(0)
var BOSdata bosdataadd69                   = BOSdata.new()
htfadd69.settings                 := SettingsHTFadd69
htfadd69.candles                  := candlesadd69
htfadd69.bosdata                  := bosdataadd69
htfadd69.settings.htf             := '69'
htfadd69.settings.max_memory      := 10
var CandleSet htfadd70                     = CandleSet.new()
var CandleSettings SettingsHTFadd70        = CandleSettings.new()
var Candle[] candlesadd70                  = array.new<Candle>(0)
var BOSdata bosdataadd70                   = BOSdata.new()
htfadd70.settings                 := SettingsHTFadd70
htfadd70.candles                  := candlesadd70
htfadd70.bosdata                  := bosdataadd70
htfadd70.settings.htf             := '70'
htfadd70.settings.max_memory      := 10
var CandleSet htfadd71                     = CandleSet.new()
var CandleSettings SettingsHTFadd71        = CandleSettings.new()
var Candle[] candlesadd71                  = array.new<Candle>(0)
var BOSdata bosdataadd71                   = BOSdata.new()
htfadd71.settings                 := SettingsHTFadd71
htfadd71.candles                  := candlesadd71
htfadd71.bosdata                  := bosdataadd71
htfadd71.settings.htf             := '71'
htfadd71.settings.max_memory      := 10
var CandleSet htfadd72                     = CandleSet.new()
var CandleSettings SettingsHTFadd72        = CandleSettings.new()
var Candle[] candlesadd72                  = array.new<Candle>(0)
var BOSdata bosdataadd72                   = BOSdata.new()
htfadd72.settings                 := SettingsHTFadd72
htfadd72.candles                  := candlesadd72
htfadd72.bosdata                  := bosdataadd72
htfadd72.settings.htf             := '72'
htfadd72.settings.max_memory      := 10
var CandleSet htfadd73                     = CandleSet.new()
var CandleSettings SettingsHTFadd73        = CandleSettings.new()
var Candle[] candlesadd73                  = array.new<Candle>(0)
var BOSdata bosdataadd73                   = BOSdata.new()
htfadd73.settings                 := SettingsHTFadd73
htfadd73.candles                  := candlesadd73
htfadd73.bosdata                  := bosdataadd73
htfadd73.settings.htf             := '73'
htfadd73.settings.max_memory      := 10
var CandleSet htfadd74                     = CandleSet.new()
var CandleSettings SettingsHTFadd74        = CandleSettings.new()
var Candle[] candlesadd74                  = array.new<Candle>(0)
var BOSdata bosdataadd74                   = BOSdata.new()
htfadd74.settings                 := SettingsHTFadd74
htfadd74.candles                  := candlesadd74
htfadd74.bosdata                  := bosdataadd74
htfadd74.settings.htf             := '74'
htfadd74.settings.max_memory      := 10
var CandleSet htfadd75                     = CandleSet.new()
var CandleSettings SettingsHTFadd75        = CandleSettings.new()
var Candle[] candlesadd75                  = array.new<Candle>(0)
var BOSdata bosdataadd75                   = BOSdata.new()
htfadd75.settings                 := SettingsHTFadd75
htfadd75.candles                  := candlesadd75
htfadd75.bosdata                  := bosdataadd75
htfadd75.settings.htf             := '75'
htfadd75.settings.max_memory      := 10
var CandleSet htfadd76                     = CandleSet.new()
var CandleSettings SettingsHTFadd76        = CandleSettings.new()
var Candle[] candlesadd76                  = array.new<Candle>(0)
var BOSdata bosdataadd76                   = BOSdata.new()
htfadd76.settings                 := SettingsHTFadd76
htfadd76.candles                  := candlesadd76
htfadd76.bosdata                  := bosdataadd76
htfadd76.settings.htf             := '76'
htfadd76.settings.max_memory      := 10
var CandleSet htfadd77                     = CandleSet.new()
var CandleSettings SettingsHTFadd77        = CandleSettings.new()
var Candle[] candlesadd77                  = array.new<Candle>(0)
var BOSdata bosdataadd77                   = BOSdata.new()
htfadd77.settings                 := SettingsHTFadd77
htfadd77.candles                  := candlesadd77
htfadd77.bosdata                  := bosdataadd77
htfadd77.settings.htf             := '77'
htfadd77.settings.max_memory      := 10
var CandleSet htfadd78                     = CandleSet.new()
var CandleSettings SettingsHTFadd78        = CandleSettings.new()
var Candle[] candlesadd78                  = array.new<Candle>(0)
var BOSdata bosdataadd78                   = BOSdata.new()
htfadd78.settings                 := SettingsHTFadd78
htfadd78.candles                  := candlesadd78
htfadd78.bosdata                  := bosdataadd78
htfadd78.settings.htf             := '78'
htfadd78.settings.max_memory      := 10
var CandleSet htfadd79                     = CandleSet.new()
var CandleSettings SettingsHTFadd79        = CandleSettings.new()
var Candle[] candlesadd79                  = array.new<Candle>(0)
var BOSdata bosdataadd79                   = BOSdata.new()
htfadd79.settings                 := SettingsHTFadd79
htfadd79.candles                  := candlesadd79
htfadd79.bosdata                  := bosdataadd79
htfadd79.settings.htf             := '79'
htfadd79.settings.max_memory      := 10
var CandleSet htfadd80                     = CandleSet.new()
var CandleSettings SettingsHTFadd80        = CandleSettings.new()
var Candle[] candlesadd80                  = array.new<Candle>(0)
var BOSdata bosdataadd80                   = BOSdata.new()
htfadd80.settings                 := SettingsHTFadd80
htfadd80.candles                  := candlesadd80
htfadd80.bosdata                  := bosdataadd80
htfadd80.settings.htf             := '80'
htfadd80.settings.max_memory      := 10
var CandleSet htfadd81                     = CandleSet.new()
var CandleSettings SettingsHTFadd81        = CandleSettings.new()
var Candle[] candlesadd81                  = array.new<Candle>(0)
var BOSdata bosdataadd81                   = BOSdata.new()
htfadd81.settings                 := SettingsHTFadd81
htfadd81.candles                  := candlesadd81
htfadd81.bosdata                  := bosdataadd81
htfadd81.settings.htf             := '81'
htfadd81.settings.max_memory      := 10
var CandleSet htfadd82                     = CandleSet.new()
var CandleSettings SettingsHTFadd82        = CandleSettings.new()
var Candle[] candlesadd82                  = array.new<Candle>(0)
var BOSdata bosdataadd82                   = BOSdata.new()
htfadd82.settings                 := SettingsHTFadd82
htfadd82.candles                  := candlesadd82
htfadd82.bosdata                  := bosdataadd82
htfadd82.settings.htf             := '82'
htfadd82.settings.max_memory      := 10
var CandleSet htfadd83                     = CandleSet.new()
var CandleSettings SettingsHTFadd83        = CandleSettings.new()
var Candle[] candlesadd83                  = array.new<Candle>(0)
var BOSdata bosdataadd83                   = BOSdata.new()
htfadd83.settings                 := SettingsHTFadd83
htfadd83.candles                  := candlesadd83
htfadd83.bosdata                  := bosdataadd83
htfadd83.settings.htf             := '83'
htfadd83.settings.max_memory      := 10
var CandleSet htfadd84                     = CandleSet.new()
var CandleSettings SettingsHTFadd84        = CandleSettings.new()
var Candle[] candlesadd84                  = array.new<Candle>(0)
var BOSdata bosdataadd84                   = BOSdata.new()
htfadd84.settings                 := SettingsHTFadd84
htfadd84.candles                  := candlesadd84
htfadd84.bosdata                  := bosdataadd84
htfadd84.settings.htf             := '84'
htfadd84.settings.max_memory      := 10
var CandleSet htfadd85                     = CandleSet.new()
var CandleSettings SettingsHTFadd85        = CandleSettings.new()
var Candle[] candlesadd85                  = array.new<Candle>(0)
var BOSdata bosdataadd85                   = BOSdata.new()
htfadd85.settings                 := SettingsHTFadd85
htfadd85.candles                  := candlesadd85
htfadd85.bosdata                  := bosdataadd85
htfadd85.settings.htf             := '85'
htfadd85.settings.max_memory      := 10
var CandleSet htfadd86                     = CandleSet.new()
var CandleSettings SettingsHTFadd86        = CandleSettings.new()
var Candle[] candlesadd86                  = array.new<Candle>(0)
var BOSdata bosdataadd86                   = BOSdata.new()
htfadd86.settings                 := SettingsHTFadd86
htfadd86.candles                  := candlesadd86
htfadd86.bosdata                  := bosdataadd86
htfadd86.settings.htf             := '86'
htfadd86.settings.max_memory      := 10
var CandleSet htfadd87                     = CandleSet.new()
var CandleSettings SettingsHTFadd87        = CandleSettings.new()
var Candle[] candlesadd87                  = array.new<Candle>(0)
var BOSdata bosdataadd87                   = BOSdata.new()
htfadd87.settings                 := SettingsHTFadd87
htfadd87.candles                  := candlesadd87
htfadd87.bosdata                  := bosdataadd87
htfadd87.settings.htf             := '87'
htfadd87.settings.max_memory      := 10
var CandleSet htfadd88                     = CandleSet.new()
var CandleSettings SettingsHTFadd88        = CandleSettings.new()
var Candle[] candlesadd88                  = array.new<Candle>(0)
var BOSdata bosdataadd88                   = BOSdata.new()
htfadd88.settings                 := SettingsHTFadd88
htfadd88.candles                  := candlesadd88
htfadd88.bosdata                  := bosdataadd88
htfadd88.settings.htf             := '88'
htfadd88.settings.max_memory      := 10
var CandleSet htfadd89                     = CandleSet.new()
var CandleSettings SettingsHTFadd89        = CandleSettings.new()
var Candle[] candlesadd89                  = array.new<Candle>(0)
var BOSdata bosdataadd89                   = BOSdata.new()
htfadd89.settings                 := SettingsHTFadd89
htfadd89.candles                  := candlesadd89
htfadd89.bosdata                  := bosdataadd89
htfadd89.settings.htf             := '89'
htfadd89.settings.max_memory      := 10
var CandleSet htfadd90                     = CandleSet.new()
var CandleSettings SettingsHTFadd90        = CandleSettings.new()
var Candle[] candlesadd90                  = array.new<Candle>(0)
var BOSdata bosdataadd90                   = BOSdata.new()
htfadd90.settings                 := SettingsHTFadd90
htfadd90.candles                  := candlesadd90
htfadd90.bosdata                  := bosdataadd90
htfadd90.settings.htf             := '90'
htfadd90.settings.max_memory      := 10

if bar_index <= last_bar_index
    htfadd60.Monitor().BOSJudge()
    htfadd61.Monitor().BOSJudge()
    htfadd62.Monitor().BOSJudge()
    htfadd63.Monitor().BOSJudge()
    htfadd64.Monitor().BOSJudge()
    htfadd65.Monitor().BOSJudge()
    htfadd66.Monitor().BOSJudge()
    htfadd67.Monitor().BOSJudge()
    htfadd68.Monitor().BOSJudge()
    htfadd69.Monitor().BOSJudge()
    htfadd70.Monitor().BOSJudge()
    htfadd71.Monitor().BOSJudge()
    htfadd72.Monitor().BOSJudge()
    htfadd73.Monitor().BOSJudge()
    htfadd74.Monitor().BOSJudge()
    htfadd75.Monitor().BOSJudge()
    htfadd76.Monitor().BOSJudge()
    htfadd77.Monitor().BOSJudge()
    htfadd78.Monitor().BOSJudge()
    htfadd79.Monitor().BOSJudge()
    htfadd80.Monitor().BOSJudge()
    htfadd81.Monitor().BOSJudge()
    htfadd82.Monitor().BOSJudge()
    htfadd83.Monitor().BOSJudge()
    htfadd84.Monitor().BOSJudge()
    htfadd85.Monitor().BOSJudge()
    htfadd86.Monitor().BOSJudge()
    htfadd87.Monitor().BOSJudge()
    htfadd88.Monitor().BOSJudge()
    htfadd89.Monitor().BOSJudge()
    htfadd90.Monitor().BOSJudge()

if bar_index == last_bar_index-1
    HighestsbdSet(highestsbd, htfadd60)
    LowestsbuSet(lowestsbu, htfadd60) 
    HighestsbdSet(highestsbd, htfadd61)
    LowestsbuSet(lowestsbu, htfadd61) 
    HighestsbdSet(highestsbd, htfadd62)
    LowestsbuSet(lowestsbu, htfadd62) 
    HighestsbdSet(highestsbd, htfadd63)
    LowestsbuSet(lowestsbu, htfadd63) 
    HighestsbdSet(highestsbd, htfadd64)
    LowestsbuSet(lowestsbu, htfadd64) 
    HighestsbdSet(highestsbd, htfadd65)
    LowestsbuSet(lowestsbu, htfadd65) 
    HighestsbdSet(highestsbd, htfadd66)
    LowestsbuSet(lowestsbu, htfadd66) 
    HighestsbdSet(highestsbd, htfadd67)
    LowestsbuSet(lowestsbu, htfadd67) 
    HighestsbdSet(highestsbd, htfadd68)
    LowestsbuSet(lowestsbu, htfadd68) 
    HighestsbdSet(highestsbd, htfadd69)
    LowestsbuSet(lowestsbu, htfadd69) 
    HighestsbdSet(highestsbd, htfadd70)
    LowestsbuSet(lowestsbu, htfadd70) 
    HighestsbdSet(highestsbd, htfadd71)
    LowestsbuSet(lowestsbu, htfadd71) 
    HighestsbdSet(highestsbd, htfadd72)
    LowestsbuSet(lowestsbu, htfadd72) 
    HighestsbdSet(highestsbd, htfadd73)
    LowestsbuSet(lowestsbu, htfadd73) 
    HighestsbdSet(highestsbd, htfadd74)
    LowestsbuSet(lowestsbu, htfadd74) 
    HighestsbdSet(highestsbd, htfadd75)
    LowestsbuSet(lowestsbu, htfadd75) 
    HighestsbdSet(highestsbd, htfadd76)
    LowestsbuSet(lowestsbu, htfadd76) 
    HighestsbdSet(highestsbd, htfadd77)
    LowestsbuSet(lowestsbu, htfadd77) 
    HighestsbdSet(highestsbd, htfadd78)
    LowestsbuSet(lowestsbu, htfadd78) 
    HighestsbdSet(highestsbd, htfadd79)
    LowestsbuSet(lowestsbu, htfadd79) 
    HighestsbdSet(highestsbd, htfadd80)
    LowestsbuSet(lowestsbu, htfadd80) 
    HighestsbdSet(highestsbd, htfadd81)
    LowestsbuSet(lowestsbu, htfadd81) 
    HighestsbdSet(highestsbd, htfadd82)
    LowestsbuSet(lowestsbu, htfadd82) 
    HighestsbdSet(highestsbd, htfadd83)
    LowestsbuSet(lowestsbu, htfadd83) 
    HighestsbdSet(highestsbd, htfadd84)
    LowestsbuSet(lowestsbu, htfadd84) 
    HighestsbdSet(highestsbd, htfadd85)
    LowestsbuSet(lowestsbu, htfadd85) 
    HighestsbdSet(highestsbd, htfadd86)
    LowestsbuSet(lowestsbu, htfadd86) 
    HighestsbdSet(highestsbd, htfadd87)
    LowestsbuSet(lowestsbu, htfadd87) 
    HighestsbdSet(highestsbd, htfadd88)
    LowestsbuSet(lowestsbu, htfadd88) 
    HighestsbdSet(highestsbd, htfadd89)
    LowestsbuSet(lowestsbu, htfadd89) 
    HighestsbdSet(highestsbd, htfadd90)
    LowestsbuSet(lowestsbu, htfadd90) 
if barstate.islast or barstate.isrealtime
    htfadd60.Monitor_Est().BOSJudge()
    htfadd61.Monitor_Est().BOSJudge()
    htfadd62.Monitor_Est().BOSJudge()
    htfadd63.Monitor_Est().BOSJudge()
    htfadd64.Monitor_Est().BOSJudge()
    htfadd65.Monitor_Est().BOSJudge()
    htfadd66.Monitor_Est().BOSJudge()
    htfadd67.Monitor_Est().BOSJudge()
    htfadd68.Monitor_Est().BOSJudge()
    htfadd69.Monitor_Est().BOSJudge()
    htfadd70.Monitor_Est().BOSJudge()
    htfadd71.Monitor_Est().BOSJudge()
    htfadd72.Monitor_Est().BOSJudge()
    htfadd73.Monitor_Est().BOSJudge()
    htfadd74.Monitor_Est().BOSJudge()
    htfadd75.Monitor_Est().BOSJudge()
    htfadd76.Monitor_Est().BOSJudge()
    htfadd77.Monitor_Est().BOSJudge()
    htfadd78.Monitor_Est().BOSJudge()
    htfadd79.Monitor_Est().BOSJudge()
    htfadd80.Monitor_Est().BOSJudge()
    htfadd81.Monitor_Est().BOSJudge()
    htfadd82.Monitor_Est().BOSJudge()
    htfadd83.Monitor_Est().BOSJudge()
    htfadd84.Monitor_Est().BOSJudge()
    htfadd85.Monitor_Est().BOSJudge()
    htfadd86.Monitor_Est().BOSJudge()
    htfadd87.Monitor_Est().BOSJudge()
    htfadd88.Monitor_Est().BOSJudge()
    htfadd89.Monitor_Est().BOSJudge()
    htfadd90.Monitor_Est().BOSJudge()
    Predictor(htfadd60, estminsbu)
    Predictor(htfadd60, estmaxsbd) 
    Predictor(htfadd61, estminsbu)
    Predictor(htfadd61, estmaxsbd) 
    Predictor(htfadd62, estminsbu)
    Predictor(htfadd62, estmaxsbd) 
    Predictor(htfadd63, estminsbu)
    Predictor(htfadd63, estmaxsbd) 
    Predictor(htfadd64, estminsbu)
    Predictor(htfadd64, estmaxsbd) 
    Predictor(htfadd65, estminsbu)
    Predictor(htfadd65, estmaxsbd) 
    Predictor(htfadd66, estminsbu)
    Predictor(htfadd66, estmaxsbd) 
    Predictor(htfadd67, estminsbu)
    Predictor(htfadd67, estmaxsbd) 
    Predictor(htfadd68, estminsbu)
    Predictor(htfadd68, estmaxsbd) 
    Predictor(htfadd69, estminsbu)
    Predictor(htfadd69, estmaxsbd) 
    Predictor(htfadd70, estminsbu)
    Predictor(htfadd70, estmaxsbd) 
    Predictor(htfadd71, estminsbu)
    Predictor(htfadd71, estmaxsbd) 
    Predictor(htfadd72, estminsbu)
    Predictor(htfadd72, estmaxsbd) 
    Predictor(htfadd73, estminsbu)
    Predictor(htfadd73, estmaxsbd) 
    Predictor(htfadd74, estminsbu)
    Predictor(htfadd74, estmaxsbd) 
    Predictor(htfadd75, estminsbu)
    Predictor(htfadd75, estmaxsbd) 
    Predictor(htfadd76, estminsbu)
    Predictor(htfadd76, estmaxsbd) 
    Predictor(htfadd77, estminsbu)
    Predictor(htfadd77, estmaxsbd) 
    Predictor(htfadd78, estminsbu)
    Predictor(htfadd78, estmaxsbd) 
    Predictor(htfadd79, estminsbu)
    Predictor(htfadd79, estmaxsbd) 
    Predictor(htfadd80, estminsbu)
    Predictor(htfadd80, estmaxsbd) 
    Predictor(htfadd81, estminsbu)
    Predictor(htfadd81, estmaxsbd) 
    Predictor(htfadd82, estminsbu)
    Predictor(htfadd82, estmaxsbd) 
    Predictor(htfadd83, estminsbu)
    Predictor(htfadd83, estmaxsbd) 
    Predictor(htfadd84, estminsbu)
    Predictor(htfadd84, estmaxsbd) 
    Predictor(htfadd85, estminsbu)
    Predictor(htfadd85, estmaxsbd) 
    Predictor(htfadd86, estminsbu)
    Predictor(htfadd86, estmaxsbd) 
    Predictor(htfadd87, estminsbu)
    Predictor(htfadd87, estmaxsbd) 
    Predictor(htfadd88, estminsbu)
    Predictor(htfadd88, estmaxsbd) 
    Predictor(htfadd89, estminsbu)
    Predictor(htfadd89, estmaxsbd) 
    Predictor(htfadd90, estminsbu)
    Predictor(htfadd90, estmaxsbd) 

//+---------------add var end------------------+//
if settings.add_show and barstate.isrealtime
    highestsbd.addplot(offset)
    lowestsbu.addplot(offset)
    estminsbu.addplot(offset)
    estmaxsbd.addplot(offset)

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

index += 1


