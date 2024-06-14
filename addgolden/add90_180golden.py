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
    int             htfint

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

settings.offset            := input.int(10, "padding from current candles", minval = 1)
settings.text_buffer       := input.int(10, "space between text features", minval = 1, maxval = 10)
// sbu sbd, period, date happen, remain time, price, line color

//+----------------------------------------+//
//+- Variables   

//+----------------------------------------+//
Helper    helper        = Helper.new()

color color_transparent = #ffffff00
var index               = 0  //不要動
var bool fggetnowclose  = false
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

method Monitor(CandleSet candleSet) =>
    BOSdata bosdata = candleSet.bosdata
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    if isNewHTFCandle != 0 
        Candle candle    = Candle.new()
        candle.c        := bar_index==0? close : bosdata.temp
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
    if (candleSet.candles.size() > 0 and isNewHTFCandle != 0) or fggetnowclose// 就算最新的出現 也必須遵守這個規定 為了讓結構穩定不亂序
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
        m1.value   := 99999999
    if m1.vdecisionname == "HighestsbdSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset-2, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min"+ "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset-2,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 0
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
        m1.value   := 99999999
    decision

method Shadowing(CandleSet sh, CandleSet cd) =>
    sh.settings.htf         := cd.settings.htf
    sh.bosdata.state        := cd.bosdata.state
    sh.bosdata.sbu          := cd.bosdata.sbu
    sh.bosdata.sbd          := cd.bosdata.sbd
    sh.bosdata.sbu_idx      := cd.bosdata.sbu_idx
    sh.bosdata.sbd_idx      := cd.bosdata.sbd_idx
    sh.bosdata.regclose3    := cd.bosdata.regclose3
    sh.bosdata.regclose2    := cd.bosdata.regclose2
    sh.bosdata.regclose1    := cd.bosdata.regclose1
    sh.bosdata.reg2key      := cd.bosdata.reg2key
    sh.bosdata.reg1key      := cd.bosdata.reg1key
    sh.bosdata.reg2key_idx  := cd.bosdata.reg2key_idx
    sh.bosdata.reg1key_idx  := cd.bosdata.reg1key_idx
    sh.bosdata.s_dated      := cd.bosdata.s_dated
    sh.bosdata.s_dateu      := cd.bosdata.s_dateu
    Candle candleshadow = Candle.new()
    candleshadow := cd.candles.first()
    sh.candles.unshift(candleshadow)
    sh
//+---------------Main------------------+//
int cnt    = 0
int delta  = settings.text_buffer
int offset = settings.offset + bar_index
//+---------------ADD------------------+//

//+---------------addbase var------------------+//
var CandleSet htfshadow                    = CandleSet.new()
var CandleSettings SettingsHTFshadow       = CandleSettings.new()
var Candle[] candlesshadow                 = array.new<Candle>(0)
var BOSdata bosdatashadow                  = BOSdata.new()
htfshadow.settings                 := SettingsHTFshadow
htfshadow.candles                  := candlesshadow
htfshadow.bosdata                  := bosdatashadow
var CandleSet htfadd1                     = CandleSet.new()
var CandleSettings SettingsHTFadd1        = CandleSettings.new(htf='1',htfint=1,max_memory=3)
var Candle[] candlesadd1                  = array.new<Candle>(0)
var BOSdata bosdataadd1                   = BOSdata.new()
htfadd1.settings                 := SettingsHTFadd1
htfadd1.candles                  := candlesadd1
htfadd1.bosdata                  := bosdataadd1
//+---------------addbase var------------------+//
var CandleSet htfadd90                     = CandleSet.new()
var CandleSettings SettingsHTFadd90        = CandleSettings.new(htf='90',htfint=90,max_memory=3)
var Candle[] candlesadd90                  = array.new<Candle>(0)
var BOSdata bosdataadd90                   = BOSdata.new()
htfadd90.settings                 := SettingsHTFadd90
htfadd90.candles                  := candlesadd90
htfadd90.bosdata                  := bosdataadd90
var CandleSet htfadd91                     = CandleSet.new()
var CandleSettings SettingsHTFadd91        = CandleSettings.new(htf='91',htfint=91,max_memory=3)
var Candle[] candlesadd91                  = array.new<Candle>(0)
var BOSdata bosdataadd91                   = BOSdata.new()
htfadd91.settings                 := SettingsHTFadd91
htfadd91.candles                  := candlesadd91
htfadd91.bosdata                  := bosdataadd91
var CandleSet htfadd92                     = CandleSet.new()
var CandleSettings SettingsHTFadd92        = CandleSettings.new(htf='92',htfint=92,max_memory=3)
var Candle[] candlesadd92                  = array.new<Candle>(0)
var BOSdata bosdataadd92                   = BOSdata.new()
htfadd92.settings                 := SettingsHTFadd92
htfadd92.candles                  := candlesadd92
htfadd92.bosdata                  := bosdataadd92
var CandleSet htfadd93                     = CandleSet.new()
var CandleSettings SettingsHTFadd93        = CandleSettings.new(htf='93',htfint=93,max_memory=3)
var Candle[] candlesadd93                  = array.new<Candle>(0)
var BOSdata bosdataadd93                   = BOSdata.new()
htfadd93.settings                 := SettingsHTFadd93
htfadd93.candles                  := candlesadd93
htfadd93.bosdata                  := bosdataadd93
var CandleSet htfadd94                     = CandleSet.new()
var CandleSettings SettingsHTFadd94        = CandleSettings.new(htf='94',htfint=94,max_memory=3)
var Candle[] candlesadd94                  = array.new<Candle>(0)
var BOSdata bosdataadd94                   = BOSdata.new()
htfadd94.settings                 := SettingsHTFadd94
htfadd94.candles                  := candlesadd94
htfadd94.bosdata                  := bosdataadd94
var CandleSet htfadd95                     = CandleSet.new()
var CandleSettings SettingsHTFadd95        = CandleSettings.new(htf='95',htfint=95,max_memory=3)
var Candle[] candlesadd95                  = array.new<Candle>(0)
var BOSdata bosdataadd95                   = BOSdata.new()
htfadd95.settings                 := SettingsHTFadd95
htfadd95.candles                  := candlesadd95
htfadd95.bosdata                  := bosdataadd95
var CandleSet htfadd96                     = CandleSet.new()
var CandleSettings SettingsHTFadd96        = CandleSettings.new(htf='96',htfint=96,max_memory=3)
var Candle[] candlesadd96                  = array.new<Candle>(0)
var BOSdata bosdataadd96                   = BOSdata.new()
htfadd96.settings                 := SettingsHTFadd96
htfadd96.candles                  := candlesadd96
htfadd96.bosdata                  := bosdataadd96
var CandleSet htfadd97                     = CandleSet.new()
var CandleSettings SettingsHTFadd97        = CandleSettings.new(htf='97',htfint=97,max_memory=3)
var Candle[] candlesadd97                  = array.new<Candle>(0)
var BOSdata bosdataadd97                   = BOSdata.new()
htfadd97.settings                 := SettingsHTFadd97
htfadd97.candles                  := candlesadd97
htfadd97.bosdata                  := bosdataadd97
var CandleSet htfadd98                     = CandleSet.new()
var CandleSettings SettingsHTFadd98        = CandleSettings.new(htf='98',htfint=98,max_memory=3)
var Candle[] candlesadd98                  = array.new<Candle>(0)
var BOSdata bosdataadd98                   = BOSdata.new()
htfadd98.settings                 := SettingsHTFadd98
htfadd98.candles                  := candlesadd98
htfadd98.bosdata                  := bosdataadd98
var CandleSet htfadd99                     = CandleSet.new()
var CandleSettings SettingsHTFadd99        = CandleSettings.new(htf='99',htfint=99,max_memory=3)
var Candle[] candlesadd99                  = array.new<Candle>(0)
var BOSdata bosdataadd99                   = BOSdata.new()
htfadd99.settings                 := SettingsHTFadd99
htfadd99.candles                  := candlesadd99
htfadd99.bosdata                  := bosdataadd99
var CandleSet htfadd100                     = CandleSet.new()
var CandleSettings SettingsHTFadd100        = CandleSettings.new(htf='100',htfint=100,max_memory=3)
var Candle[] candlesadd100                  = array.new<Candle>(0)
var BOSdata bosdataadd100                   = BOSdata.new()
htfadd100.settings                 := SettingsHTFadd100
htfadd100.candles                  := candlesadd100
htfadd100.bosdata                  := bosdataadd100
var CandleSet htfadd101                     = CandleSet.new()
var CandleSettings SettingsHTFadd101        = CandleSettings.new(htf='101',htfint=101,max_memory=3)
var Candle[] candlesadd101                  = array.new<Candle>(0)
var BOSdata bosdataadd101                   = BOSdata.new()
htfadd101.settings                 := SettingsHTFadd101
htfadd101.candles                  := candlesadd101
htfadd101.bosdata                  := bosdataadd101
var CandleSet htfadd102                     = CandleSet.new()
var CandleSettings SettingsHTFadd102        = CandleSettings.new(htf='102',htfint=102,max_memory=3)
var Candle[] candlesadd102                  = array.new<Candle>(0)
var BOSdata bosdataadd102                   = BOSdata.new()
htfadd102.settings                 := SettingsHTFadd102
htfadd102.candles                  := candlesadd102
htfadd102.bosdata                  := bosdataadd102
var CandleSet htfadd103                     = CandleSet.new()
var CandleSettings SettingsHTFadd103        = CandleSettings.new(htf='103',htfint=103,max_memory=3)
var Candle[] candlesadd103                  = array.new<Candle>(0)
var BOSdata bosdataadd103                   = BOSdata.new()
htfadd103.settings                 := SettingsHTFadd103
htfadd103.candles                  := candlesadd103
htfadd103.bosdata                  := bosdataadd103
var CandleSet htfadd104                     = CandleSet.new()
var CandleSettings SettingsHTFadd104        = CandleSettings.new(htf='104',htfint=104,max_memory=3)
var Candle[] candlesadd104                  = array.new<Candle>(0)
var BOSdata bosdataadd104                   = BOSdata.new()
htfadd104.settings                 := SettingsHTFadd104
htfadd104.candles                  := candlesadd104
htfadd104.bosdata                  := bosdataadd104
var CandleSet htfadd105                     = CandleSet.new()
var CandleSettings SettingsHTFadd105        = CandleSettings.new(htf='105',htfint=105,max_memory=3)
var Candle[] candlesadd105                  = array.new<Candle>(0)
var BOSdata bosdataadd105                   = BOSdata.new()
htfadd105.settings                 := SettingsHTFadd105
htfadd105.candles                  := candlesadd105
htfadd105.bosdata                  := bosdataadd105
var CandleSet htfadd106                     = CandleSet.new()
var CandleSettings SettingsHTFadd106        = CandleSettings.new(htf='106',htfint=106,max_memory=3)
var Candle[] candlesadd106                  = array.new<Candle>(0)
var BOSdata bosdataadd106                   = BOSdata.new()
htfadd106.settings                 := SettingsHTFadd106
htfadd106.candles                  := candlesadd106
htfadd106.bosdata                  := bosdataadd106
var CandleSet htfadd107                     = CandleSet.new()
var CandleSettings SettingsHTFadd107        = CandleSettings.new(htf='107',htfint=107,max_memory=3)
var Candle[] candlesadd107                  = array.new<Candle>(0)
var BOSdata bosdataadd107                   = BOSdata.new()
htfadd107.settings                 := SettingsHTFadd107
htfadd107.candles                  := candlesadd107
htfadd107.bosdata                  := bosdataadd107
var CandleSet htfadd108                     = CandleSet.new()
var CandleSettings SettingsHTFadd108        = CandleSettings.new(htf='108',htfint=108,max_memory=3)
var Candle[] candlesadd108                  = array.new<Candle>(0)
var BOSdata bosdataadd108                   = BOSdata.new()
htfadd108.settings                 := SettingsHTFadd108
htfadd108.candles                  := candlesadd108
htfadd108.bosdata                  := bosdataadd108
var CandleSet htfadd109                     = CandleSet.new()
var CandleSettings SettingsHTFadd109        = CandleSettings.new(htf='109',htfint=109,max_memory=3)
var Candle[] candlesadd109                  = array.new<Candle>(0)
var BOSdata bosdataadd109                   = BOSdata.new()
htfadd109.settings                 := SettingsHTFadd109
htfadd109.candles                  := candlesadd109
htfadd109.bosdata                  := bosdataadd109
var CandleSet htfadd110                     = CandleSet.new()
var CandleSettings SettingsHTFadd110        = CandleSettings.new(htf='110',htfint=110,max_memory=3)
var Candle[] candlesadd110                  = array.new<Candle>(0)
var BOSdata bosdataadd110                   = BOSdata.new()
htfadd110.settings                 := SettingsHTFadd110
htfadd110.candles                  := candlesadd110
htfadd110.bosdata                  := bosdataadd110
var CandleSet htfadd111                     = CandleSet.new()
var CandleSettings SettingsHTFadd111        = CandleSettings.new(htf='111',htfint=111,max_memory=3)
var Candle[] candlesadd111                  = array.new<Candle>(0)
var BOSdata bosdataadd111                   = BOSdata.new()
htfadd111.settings                 := SettingsHTFadd111
htfadd111.candles                  := candlesadd111
htfadd111.bosdata                  := bosdataadd111
var CandleSet htfadd112                     = CandleSet.new()
var CandleSettings SettingsHTFadd112        = CandleSettings.new(htf='112',htfint=112,max_memory=3)
var Candle[] candlesadd112                  = array.new<Candle>(0)
var BOSdata bosdataadd112                   = BOSdata.new()
htfadd112.settings                 := SettingsHTFadd112
htfadd112.candles                  := candlesadd112
htfadd112.bosdata                  := bosdataadd112
var CandleSet htfadd113                     = CandleSet.new()
var CandleSettings SettingsHTFadd113        = CandleSettings.new(htf='113',htfint=113,max_memory=3)
var Candle[] candlesadd113                  = array.new<Candle>(0)
var BOSdata bosdataadd113                   = BOSdata.new()
htfadd113.settings                 := SettingsHTFadd113
htfadd113.candles                  := candlesadd113
htfadd113.bosdata                  := bosdataadd113
var CandleSet htfadd114                     = CandleSet.new()
var CandleSettings SettingsHTFadd114        = CandleSettings.new(htf='114',htfint=114,max_memory=3)
var Candle[] candlesadd114                  = array.new<Candle>(0)
var BOSdata bosdataadd114                   = BOSdata.new()
htfadd114.settings                 := SettingsHTFadd114
htfadd114.candles                  := candlesadd114
htfadd114.bosdata                  := bosdataadd114
var CandleSet htfadd115                     = CandleSet.new()
var CandleSettings SettingsHTFadd115        = CandleSettings.new(htf='115',htfint=115,max_memory=3)
var Candle[] candlesadd115                  = array.new<Candle>(0)
var BOSdata bosdataadd115                   = BOSdata.new()
htfadd115.settings                 := SettingsHTFadd115
htfadd115.candles                  := candlesadd115
htfadd115.bosdata                  := bosdataadd115
var CandleSet htfadd116                     = CandleSet.new()
var CandleSettings SettingsHTFadd116        = CandleSettings.new(htf='116',htfint=116,max_memory=3)
var Candle[] candlesadd116                  = array.new<Candle>(0)
var BOSdata bosdataadd116                   = BOSdata.new()
htfadd116.settings                 := SettingsHTFadd116
htfadd116.candles                  := candlesadd116
htfadd116.bosdata                  := bosdataadd116
var CandleSet htfadd117                     = CandleSet.new()
var CandleSettings SettingsHTFadd117        = CandleSettings.new(htf='117',htfint=117,max_memory=3)
var Candle[] candlesadd117                  = array.new<Candle>(0)
var BOSdata bosdataadd117                   = BOSdata.new()
htfadd117.settings                 := SettingsHTFadd117
htfadd117.candles                  := candlesadd117
htfadd117.bosdata                  := bosdataadd117
var CandleSet htfadd118                     = CandleSet.new()
var CandleSettings SettingsHTFadd118        = CandleSettings.new(htf='118',htfint=118,max_memory=3)
var Candle[] candlesadd118                  = array.new<Candle>(0)
var BOSdata bosdataadd118                   = BOSdata.new()
htfadd118.settings                 := SettingsHTFadd118
htfadd118.candles                  := candlesadd118
htfadd118.bosdata                  := bosdataadd118
var CandleSet htfadd119                     = CandleSet.new()
var CandleSettings SettingsHTFadd119        = CandleSettings.new(htf='119',htfint=119,max_memory=3)
var Candle[] candlesadd119                  = array.new<Candle>(0)
var BOSdata bosdataadd119                   = BOSdata.new()
htfadd119.settings                 := SettingsHTFadd119
htfadd119.candles                  := candlesadd119
htfadd119.bosdata                  := bosdataadd119
var CandleSet htfadd120                     = CandleSet.new()
var CandleSettings SettingsHTFadd120        = CandleSettings.new(htf='120',htfint=120,max_memory=3)
var Candle[] candlesadd120                  = array.new<Candle>(0)
var BOSdata bosdataadd120                   = BOSdata.new()
htfadd120.settings                 := SettingsHTFadd120
htfadd120.candles                  := candlesadd120
htfadd120.bosdata                  := bosdataadd120
var CandleSet htfadd121                     = CandleSet.new()
var CandleSettings SettingsHTFadd121        = CandleSettings.new(htf='121',htfint=121,max_memory=3)
var Candle[] candlesadd121                  = array.new<Candle>(0)
var BOSdata bosdataadd121                   = BOSdata.new()
htfadd121.settings                 := SettingsHTFadd121
htfadd121.candles                  := candlesadd121
htfadd121.bosdata                  := bosdataadd121
var CandleSet htfadd122                     = CandleSet.new()
var CandleSettings SettingsHTFadd122        = CandleSettings.new(htf='122',htfint=122,max_memory=3)
var Candle[] candlesadd122                  = array.new<Candle>(0)
var BOSdata bosdataadd122                   = BOSdata.new()
htfadd122.settings                 := SettingsHTFadd122
htfadd122.candles                  := candlesadd122
htfadd122.bosdata                  := bosdataadd122
var CandleSet htfadd123                     = CandleSet.new()
var CandleSettings SettingsHTFadd123        = CandleSettings.new(htf='123',htfint=123,max_memory=3)
var Candle[] candlesadd123                  = array.new<Candle>(0)
var BOSdata bosdataadd123                   = BOSdata.new()
htfadd123.settings                 := SettingsHTFadd123
htfadd123.candles                  := candlesadd123
htfadd123.bosdata                  := bosdataadd123
var CandleSet htfadd124                     = CandleSet.new()
var CandleSettings SettingsHTFadd124        = CandleSettings.new(htf='124',htfint=124,max_memory=3)
var Candle[] candlesadd124                  = array.new<Candle>(0)
var BOSdata bosdataadd124                   = BOSdata.new()
htfadd124.settings                 := SettingsHTFadd124
htfadd124.candles                  := candlesadd124
htfadd124.bosdata                  := bosdataadd124
var CandleSet htfadd125                     = CandleSet.new()
var CandleSettings SettingsHTFadd125        = CandleSettings.new(htf='125',htfint=125,max_memory=3)
var Candle[] candlesadd125                  = array.new<Candle>(0)
var BOSdata bosdataadd125                   = BOSdata.new()
htfadd125.settings                 := SettingsHTFadd125
htfadd125.candles                  := candlesadd125
htfadd125.bosdata                  := bosdataadd125
var CandleSet htfadd126                     = CandleSet.new()
var CandleSettings SettingsHTFadd126        = CandleSettings.new(htf='126',htfint=126,max_memory=3)
var Candle[] candlesadd126                  = array.new<Candle>(0)
var BOSdata bosdataadd126                   = BOSdata.new()
htfadd126.settings                 := SettingsHTFadd126
htfadd126.candles                  := candlesadd126
htfadd126.bosdata                  := bosdataadd126
var CandleSet htfadd127                     = CandleSet.new()
var CandleSettings SettingsHTFadd127        = CandleSettings.new(htf='127',htfint=127,max_memory=3)
var Candle[] candlesadd127                  = array.new<Candle>(0)
var BOSdata bosdataadd127                   = BOSdata.new()
htfadd127.settings                 := SettingsHTFadd127
htfadd127.candles                  := candlesadd127
htfadd127.bosdata                  := bosdataadd127
var CandleSet htfadd128                     = CandleSet.new()
var CandleSettings SettingsHTFadd128        = CandleSettings.new(htf='128',htfint=128,max_memory=3)
var Candle[] candlesadd128                  = array.new<Candle>(0)
var BOSdata bosdataadd128                   = BOSdata.new()
htfadd128.settings                 := SettingsHTFadd128
htfadd128.candles                  := candlesadd128
htfadd128.bosdata                  := bosdataadd128
var CandleSet htfadd129                     = CandleSet.new()
var CandleSettings SettingsHTFadd129        = CandleSettings.new(htf='129',htfint=129,max_memory=3)
var Candle[] candlesadd129                  = array.new<Candle>(0)
var BOSdata bosdataadd129                   = BOSdata.new()
htfadd129.settings                 := SettingsHTFadd129
htfadd129.candles                  := candlesadd129
htfadd129.bosdata                  := bosdataadd129
var CandleSet htfadd130                     = CandleSet.new()
var CandleSettings SettingsHTFadd130        = CandleSettings.new(htf='130',htfint=130,max_memory=3)
var Candle[] candlesadd130                  = array.new<Candle>(0)
var BOSdata bosdataadd130                   = BOSdata.new()
htfadd130.settings                 := SettingsHTFadd130
htfadd130.candles                  := candlesadd130
htfadd130.bosdata                  := bosdataadd130
var CandleSet htfadd131                     = CandleSet.new()
var CandleSettings SettingsHTFadd131        = CandleSettings.new(htf='131',htfint=131,max_memory=3)
var Candle[] candlesadd131                  = array.new<Candle>(0)
var BOSdata bosdataadd131                   = BOSdata.new()
htfadd131.settings                 := SettingsHTFadd131
htfadd131.candles                  := candlesadd131
htfadd131.bosdata                  := bosdataadd131
var CandleSet htfadd132                     = CandleSet.new()
var CandleSettings SettingsHTFadd132        = CandleSettings.new(htf='132',htfint=132,max_memory=3)
var Candle[] candlesadd132                  = array.new<Candle>(0)
var BOSdata bosdataadd132                   = BOSdata.new()
htfadd132.settings                 := SettingsHTFadd132
htfadd132.candles                  := candlesadd132
htfadd132.bosdata                  := bosdataadd132
var CandleSet htfadd133                     = CandleSet.new()
var CandleSettings SettingsHTFadd133        = CandleSettings.new(htf='133',htfint=133,max_memory=3)
var Candle[] candlesadd133                  = array.new<Candle>(0)
var BOSdata bosdataadd133                   = BOSdata.new()
htfadd133.settings                 := SettingsHTFadd133
htfadd133.candles                  := candlesadd133
htfadd133.bosdata                  := bosdataadd133
var CandleSet htfadd134                     = CandleSet.new()
var CandleSettings SettingsHTFadd134        = CandleSettings.new(htf='134',htfint=134,max_memory=3)
var Candle[] candlesadd134                  = array.new<Candle>(0)
var BOSdata bosdataadd134                   = BOSdata.new()
htfadd134.settings                 := SettingsHTFadd134
htfadd134.candles                  := candlesadd134
htfadd134.bosdata                  := bosdataadd134
var CandleSet htfadd135                     = CandleSet.new()
var CandleSettings SettingsHTFadd135        = CandleSettings.new(htf='135',htfint=135,max_memory=3)
var Candle[] candlesadd135                  = array.new<Candle>(0)
var BOSdata bosdataadd135                   = BOSdata.new()
htfadd135.settings                 := SettingsHTFadd135
htfadd135.candles                  := candlesadd135
htfadd135.bosdata                  := bosdataadd135
var CandleSet htfadd136                     = CandleSet.new()
var CandleSettings SettingsHTFadd136        = CandleSettings.new(htf='136',htfint=136,max_memory=3)
var Candle[] candlesadd136                  = array.new<Candle>(0)
var BOSdata bosdataadd136                   = BOSdata.new()
htfadd136.settings                 := SettingsHTFadd136
htfadd136.candles                  := candlesadd136
htfadd136.bosdata                  := bosdataadd136
var CandleSet htfadd137                     = CandleSet.new()
var CandleSettings SettingsHTFadd137        = CandleSettings.new(htf='137',htfint=137,max_memory=3)
var Candle[] candlesadd137                  = array.new<Candle>(0)
var BOSdata bosdataadd137                   = BOSdata.new()
htfadd137.settings                 := SettingsHTFadd137
htfadd137.candles                  := candlesadd137
htfadd137.bosdata                  := bosdataadd137
var CandleSet htfadd138                     = CandleSet.new()
var CandleSettings SettingsHTFadd138        = CandleSettings.new(htf='138',htfint=138,max_memory=3)
var Candle[] candlesadd138                  = array.new<Candle>(0)
var BOSdata bosdataadd138                   = BOSdata.new()
htfadd138.settings                 := SettingsHTFadd138
htfadd138.candles                  := candlesadd138
htfadd138.bosdata                  := bosdataadd138
var CandleSet htfadd139                     = CandleSet.new()
var CandleSettings SettingsHTFadd139        = CandleSettings.new(htf='139',htfint=139,max_memory=3)
var Candle[] candlesadd139                  = array.new<Candle>(0)
var BOSdata bosdataadd139                   = BOSdata.new()
htfadd139.settings                 := SettingsHTFadd139
htfadd139.candles                  := candlesadd139
htfadd139.bosdata                  := bosdataadd139
var CandleSet htfadd140                     = CandleSet.new()
var CandleSettings SettingsHTFadd140        = CandleSettings.new(htf='140',htfint=140,max_memory=3)
var Candle[] candlesadd140                  = array.new<Candle>(0)
var BOSdata bosdataadd140                   = BOSdata.new()
htfadd140.settings                 := SettingsHTFadd140
htfadd140.candles                  := candlesadd140
htfadd140.bosdata                  := bosdataadd140
var CandleSet htfadd141                     = CandleSet.new()
var CandleSettings SettingsHTFadd141        = CandleSettings.new(htf='141',htfint=141,max_memory=3)
var Candle[] candlesadd141                  = array.new<Candle>(0)
var BOSdata bosdataadd141                   = BOSdata.new()
htfadd141.settings                 := SettingsHTFadd141
htfadd141.candles                  := candlesadd141
htfadd141.bosdata                  := bosdataadd141
var CandleSet htfadd142                     = CandleSet.new()
var CandleSettings SettingsHTFadd142        = CandleSettings.new(htf='142',htfint=142,max_memory=3)
var Candle[] candlesadd142                  = array.new<Candle>(0)
var BOSdata bosdataadd142                   = BOSdata.new()
htfadd142.settings                 := SettingsHTFadd142
htfadd142.candles                  := candlesadd142
htfadd142.bosdata                  := bosdataadd142
var CandleSet htfadd143                     = CandleSet.new()
var CandleSettings SettingsHTFadd143        = CandleSettings.new(htf='143',htfint=143,max_memory=3)
var Candle[] candlesadd143                  = array.new<Candle>(0)
var BOSdata bosdataadd143                   = BOSdata.new()
htfadd143.settings                 := SettingsHTFadd143
htfadd143.candles                  := candlesadd143
htfadd143.bosdata                  := bosdataadd143
var CandleSet htfadd144                     = CandleSet.new()
var CandleSettings SettingsHTFadd144        = CandleSettings.new(htf='144',htfint=144,max_memory=3)
var Candle[] candlesadd144                  = array.new<Candle>(0)
var BOSdata bosdataadd144                   = BOSdata.new()
htfadd144.settings                 := SettingsHTFadd144
htfadd144.candles                  := candlesadd144
htfadd144.bosdata                  := bosdataadd144
var CandleSet htfadd145                     = CandleSet.new()
var CandleSettings SettingsHTFadd145        = CandleSettings.new(htf='145',htfint=145,max_memory=3)
var Candle[] candlesadd145                  = array.new<Candle>(0)
var BOSdata bosdataadd145                   = BOSdata.new()
htfadd145.settings                 := SettingsHTFadd145
htfadd145.candles                  := candlesadd145
htfadd145.bosdata                  := bosdataadd145
var CandleSet htfadd146                     = CandleSet.new()
var CandleSettings SettingsHTFadd146        = CandleSettings.new(htf='146',htfint=146,max_memory=3)
var Candle[] candlesadd146                  = array.new<Candle>(0)
var BOSdata bosdataadd146                   = BOSdata.new()
htfadd146.settings                 := SettingsHTFadd146
htfadd146.candles                  := candlesadd146
htfadd146.bosdata                  := bosdataadd146
var CandleSet htfadd147                     = CandleSet.new()
var CandleSettings SettingsHTFadd147        = CandleSettings.new(htf='147',htfint=147,max_memory=3)
var Candle[] candlesadd147                  = array.new<Candle>(0)
var BOSdata bosdataadd147                   = BOSdata.new()
htfadd147.settings                 := SettingsHTFadd147
htfadd147.candles                  := candlesadd147
htfadd147.bosdata                  := bosdataadd147
var CandleSet htfadd148                     = CandleSet.new()
var CandleSettings SettingsHTFadd148        = CandleSettings.new(htf='148',htfint=148,max_memory=3)
var Candle[] candlesadd148                  = array.new<Candle>(0)
var BOSdata bosdataadd148                   = BOSdata.new()
htfadd148.settings                 := SettingsHTFadd148
htfadd148.candles                  := candlesadd148
htfadd148.bosdata                  := bosdataadd148
var CandleSet htfadd149                     = CandleSet.new()
var CandleSettings SettingsHTFadd149        = CandleSettings.new(htf='149',htfint=149,max_memory=3)
var Candle[] candlesadd149                  = array.new<Candle>(0)
var BOSdata bosdataadd149                   = BOSdata.new()
htfadd149.settings                 := SettingsHTFadd149
htfadd149.candles                  := candlesadd149
htfadd149.bosdata                  := bosdataadd149
var CandleSet htfadd150                     = CandleSet.new()
var CandleSettings SettingsHTFadd150        = CandleSettings.new(htf='150',htfint=150,max_memory=3)
var Candle[] candlesadd150                  = array.new<Candle>(0)
var BOSdata bosdataadd150                   = BOSdata.new()
htfadd150.settings                 := SettingsHTFadd150
htfadd150.candles                  := candlesadd150
htfadd150.bosdata                  := bosdataadd150
var CandleSet htfadd151                     = CandleSet.new()
var CandleSettings SettingsHTFadd151        = CandleSettings.new(htf='151',htfint=151,max_memory=3)
var Candle[] candlesadd151                  = array.new<Candle>(0)
var BOSdata bosdataadd151                   = BOSdata.new()
htfadd151.settings                 := SettingsHTFadd151
htfadd151.candles                  := candlesadd151
htfadd151.bosdata                  := bosdataadd151
var CandleSet htfadd152                     = CandleSet.new()
var CandleSettings SettingsHTFadd152        = CandleSettings.new(htf='152',htfint=152,max_memory=3)
var Candle[] candlesadd152                  = array.new<Candle>(0)
var BOSdata bosdataadd152                   = BOSdata.new()
htfadd152.settings                 := SettingsHTFadd152
htfadd152.candles                  := candlesadd152
htfadd152.bosdata                  := bosdataadd152
var CandleSet htfadd153                     = CandleSet.new()
var CandleSettings SettingsHTFadd153        = CandleSettings.new(htf='153',htfint=153,max_memory=3)
var Candle[] candlesadd153                  = array.new<Candle>(0)
var BOSdata bosdataadd153                   = BOSdata.new()
htfadd153.settings                 := SettingsHTFadd153
htfadd153.candles                  := candlesadd153
htfadd153.bosdata                  := bosdataadd153
var CandleSet htfadd154                     = CandleSet.new()
var CandleSettings SettingsHTFadd154        = CandleSettings.new(htf='154',htfint=154,max_memory=3)
var Candle[] candlesadd154                  = array.new<Candle>(0)
var BOSdata bosdataadd154                   = BOSdata.new()
htfadd154.settings                 := SettingsHTFadd154
htfadd154.candles                  := candlesadd154
htfadd154.bosdata                  := bosdataadd154
var CandleSet htfadd155                     = CandleSet.new()
var CandleSettings SettingsHTFadd155        = CandleSettings.new(htf='155',htfint=155,max_memory=3)
var Candle[] candlesadd155                  = array.new<Candle>(0)
var BOSdata bosdataadd155                   = BOSdata.new()
htfadd155.settings                 := SettingsHTFadd155
htfadd155.candles                  := candlesadd155
htfadd155.bosdata                  := bosdataadd155
var CandleSet htfadd156                     = CandleSet.new()
var CandleSettings SettingsHTFadd156        = CandleSettings.new(htf='156',htfint=156,max_memory=3)
var Candle[] candlesadd156                  = array.new<Candle>(0)
var BOSdata bosdataadd156                   = BOSdata.new()
htfadd156.settings                 := SettingsHTFadd156
htfadd156.candles                  := candlesadd156
htfadd156.bosdata                  := bosdataadd156
var CandleSet htfadd157                     = CandleSet.new()
var CandleSettings SettingsHTFadd157        = CandleSettings.new(htf='157',htfint=157,max_memory=3)
var Candle[] candlesadd157                  = array.new<Candle>(0)
var BOSdata bosdataadd157                   = BOSdata.new()
htfadd157.settings                 := SettingsHTFadd157
htfadd157.candles                  := candlesadd157
htfadd157.bosdata                  := bosdataadd157
var CandleSet htfadd158                     = CandleSet.new()
var CandleSettings SettingsHTFadd158        = CandleSettings.new(htf='158',htfint=158,max_memory=3)
var Candle[] candlesadd158                  = array.new<Candle>(0)
var BOSdata bosdataadd158                   = BOSdata.new()
htfadd158.settings                 := SettingsHTFadd158
htfadd158.candles                  := candlesadd158
htfadd158.bosdata                  := bosdataadd158
var CandleSet htfadd159                     = CandleSet.new()
var CandleSettings SettingsHTFadd159        = CandleSettings.new(htf='159',htfint=159,max_memory=3)
var Candle[] candlesadd159                  = array.new<Candle>(0)
var BOSdata bosdataadd159                   = BOSdata.new()
htfadd159.settings                 := SettingsHTFadd159
htfadd159.candles                  := candlesadd159
htfadd159.bosdata                  := bosdataadd159
var CandleSet htfadd160                     = CandleSet.new()
var CandleSettings SettingsHTFadd160        = CandleSettings.new(htf='160',htfint=160,max_memory=3)
var Candle[] candlesadd160                  = array.new<Candle>(0)
var BOSdata bosdataadd160                   = BOSdata.new()
htfadd160.settings                 := SettingsHTFadd160
htfadd160.candles                  := candlesadd160
htfadd160.bosdata                  := bosdataadd160
var CandleSet htfadd161                     = CandleSet.new()
var CandleSettings SettingsHTFadd161        = CandleSettings.new(htf='161',htfint=161,max_memory=3)
var Candle[] candlesadd161                  = array.new<Candle>(0)
var BOSdata bosdataadd161                   = BOSdata.new()
htfadd161.settings                 := SettingsHTFadd161
htfadd161.candles                  := candlesadd161
htfadd161.bosdata                  := bosdataadd161
var CandleSet htfadd162                     = CandleSet.new()
var CandleSettings SettingsHTFadd162        = CandleSettings.new(htf='162',htfint=162,max_memory=3)
var Candle[] candlesadd162                  = array.new<Candle>(0)
var BOSdata bosdataadd162                   = BOSdata.new()
htfadd162.settings                 := SettingsHTFadd162
htfadd162.candles                  := candlesadd162
htfadd162.bosdata                  := bosdataadd162
var CandleSet htfadd163                     = CandleSet.new()
var CandleSettings SettingsHTFadd163        = CandleSettings.new(htf='163',htfint=163,max_memory=3)
var Candle[] candlesadd163                  = array.new<Candle>(0)
var BOSdata bosdataadd163                   = BOSdata.new()
htfadd163.settings                 := SettingsHTFadd163
htfadd163.candles                  := candlesadd163
htfadd163.bosdata                  := bosdataadd163
var CandleSet htfadd164                     = CandleSet.new()
var CandleSettings SettingsHTFadd164        = CandleSettings.new(htf='164',htfint=164,max_memory=3)
var Candle[] candlesadd164                  = array.new<Candle>(0)
var BOSdata bosdataadd164                   = BOSdata.new()
htfadd164.settings                 := SettingsHTFadd164
htfadd164.candles                  := candlesadd164
htfadd164.bosdata                  := bosdataadd164
var CandleSet htfadd165                     = CandleSet.new()
var CandleSettings SettingsHTFadd165        = CandleSettings.new(htf='165',htfint=165,max_memory=3)
var Candle[] candlesadd165                  = array.new<Candle>(0)
var BOSdata bosdataadd165                   = BOSdata.new()
htfadd165.settings                 := SettingsHTFadd165
htfadd165.candles                  := candlesadd165
htfadd165.bosdata                  := bosdataadd165
var CandleSet htfadd166                     = CandleSet.new()
var CandleSettings SettingsHTFadd166        = CandleSettings.new(htf='166',htfint=166,max_memory=3)
var Candle[] candlesadd166                  = array.new<Candle>(0)
var BOSdata bosdataadd166                   = BOSdata.new()
htfadd166.settings                 := SettingsHTFadd166
htfadd166.candles                  := candlesadd166
htfadd166.bosdata                  := bosdataadd166
var CandleSet htfadd167                     = CandleSet.new()
var CandleSettings SettingsHTFadd167        = CandleSettings.new(htf='167',htfint=167,max_memory=3)
var Candle[] candlesadd167                  = array.new<Candle>(0)
var BOSdata bosdataadd167                   = BOSdata.new()
htfadd167.settings                 := SettingsHTFadd167
htfadd167.candles                  := candlesadd167
htfadd167.bosdata                  := bosdataadd167
var CandleSet htfadd168                     = CandleSet.new()
var CandleSettings SettingsHTFadd168        = CandleSettings.new(htf='168',htfint=168,max_memory=3)
var Candle[] candlesadd168                  = array.new<Candle>(0)
var BOSdata bosdataadd168                   = BOSdata.new()
htfadd168.settings                 := SettingsHTFadd168
htfadd168.candles                  := candlesadd168
htfadd168.bosdata                  := bosdataadd168
var CandleSet htfadd169                     = CandleSet.new()
var CandleSettings SettingsHTFadd169        = CandleSettings.new(htf='169',htfint=169,max_memory=3)
var Candle[] candlesadd169                  = array.new<Candle>(0)
var BOSdata bosdataadd169                   = BOSdata.new()
htfadd169.settings                 := SettingsHTFadd169
htfadd169.candles                  := candlesadd169
htfadd169.bosdata                  := bosdataadd169
var CandleSet htfadd170                     = CandleSet.new()
var CandleSettings SettingsHTFadd170        = CandleSettings.new(htf='170',htfint=170,max_memory=3)
var Candle[] candlesadd170                  = array.new<Candle>(0)
var BOSdata bosdataadd170                   = BOSdata.new()
htfadd170.settings                 := SettingsHTFadd170
htfadd170.candles                  := candlesadd170
htfadd170.bosdata                  := bosdataadd170
var CandleSet htfadd171                     = CandleSet.new()
var CandleSettings SettingsHTFadd171        = CandleSettings.new(htf='171',htfint=171,max_memory=3)
var Candle[] candlesadd171                  = array.new<Candle>(0)
var BOSdata bosdataadd171                   = BOSdata.new()
htfadd171.settings                 := SettingsHTFadd171
htfadd171.candles                  := candlesadd171
htfadd171.bosdata                  := bosdataadd171
var CandleSet htfadd172                     = CandleSet.new()
var CandleSettings SettingsHTFadd172        = CandleSettings.new(htf='172',htfint=172,max_memory=3)
var Candle[] candlesadd172                  = array.new<Candle>(0)
var BOSdata bosdataadd172                   = BOSdata.new()
htfadd172.settings                 := SettingsHTFadd172
htfadd172.candles                  := candlesadd172
htfadd172.bosdata                  := bosdataadd172
var CandleSet htfadd173                     = CandleSet.new()
var CandleSettings SettingsHTFadd173        = CandleSettings.new(htf='173',htfint=173,max_memory=3)
var Candle[] candlesadd173                  = array.new<Candle>(0)
var BOSdata bosdataadd173                   = BOSdata.new()
htfadd173.settings                 := SettingsHTFadd173
htfadd173.candles                  := candlesadd173
htfadd173.bosdata                  := bosdataadd173
var CandleSet htfadd174                     = CandleSet.new()
var CandleSettings SettingsHTFadd174        = CandleSettings.new(htf='174',htfint=174,max_memory=3)
var Candle[] candlesadd174                  = array.new<Candle>(0)
var BOSdata bosdataadd174                   = BOSdata.new()
htfadd174.settings                 := SettingsHTFadd174
htfadd174.candles                  := candlesadd174
htfadd174.bosdata                  := bosdataadd174
var CandleSet htfadd175                     = CandleSet.new()
var CandleSettings SettingsHTFadd175        = CandleSettings.new(htf='175',htfint=175,max_memory=3)
var Candle[] candlesadd175                  = array.new<Candle>(0)
var BOSdata bosdataadd175                   = BOSdata.new()
htfadd175.settings                 := SettingsHTFadd175
htfadd175.candles                  := candlesadd175
htfadd175.bosdata                  := bosdataadd175
var CandleSet htfadd176                     = CandleSet.new()
var CandleSettings SettingsHTFadd176        = CandleSettings.new(htf='176',htfint=176,max_memory=3)
var Candle[] candlesadd176                  = array.new<Candle>(0)
var BOSdata bosdataadd176                   = BOSdata.new()
htfadd176.settings                 := SettingsHTFadd176
htfadd176.candles                  := candlesadd176
htfadd176.bosdata                  := bosdataadd176
var CandleSet htfadd177                     = CandleSet.new()
var CandleSettings SettingsHTFadd177        = CandleSettings.new(htf='177',htfint=177,max_memory=3)
var Candle[] candlesadd177                  = array.new<Candle>(0)
var BOSdata bosdataadd177                   = BOSdata.new()
htfadd177.settings                 := SettingsHTFadd177
htfadd177.candles                  := candlesadd177
htfadd177.bosdata                  := bosdataadd177
var CandleSet htfadd178                     = CandleSet.new()
var CandleSettings SettingsHTFadd178        = CandleSettings.new(htf='178',htfint=178,max_memory=3)
var Candle[] candlesadd178                  = array.new<Candle>(0)
var BOSdata bosdataadd178                   = BOSdata.new()
htfadd178.settings                 := SettingsHTFadd178
htfadd178.candles                  := candlesadd178
htfadd178.bosdata                  := bosdataadd178
var CandleSet htfadd179                     = CandleSet.new()
var CandleSettings SettingsHTFadd179        = CandleSettings.new(htf='179',htfint=179,max_memory=3)
var Candle[] candlesadd179                  = array.new<Candle>(0)
var BOSdata bosdataadd179                   = BOSdata.new()
htfadd179.settings                 := SettingsHTFadd179
htfadd179.candles                  := candlesadd179
htfadd179.bosdata                  := bosdataadd179
var CandleSet htfadd180                     = CandleSet.new()
var CandleSettings SettingsHTFadd180        = CandleSettings.new(htf='180',htfint=180,max_memory=3)
var Candle[] candlesadd180                  = array.new<Candle>(0)
var BOSdata bosdataadd180                   = BOSdata.new()
htfadd180.settings                 := SettingsHTFadd180
htfadd180.candles                  := candlesadd180
htfadd180.bosdata                  := bosdataadd180

htfadd90.Monitor().BOSJudge()
htfadd91.Monitor().BOSJudge()
htfadd92.Monitor().BOSJudge()
htfadd93.Monitor().BOSJudge()
htfadd94.Monitor().BOSJudge()
htfadd95.Monitor().BOSJudge()
htfadd96.Monitor().BOSJudge()
htfadd97.Monitor().BOSJudge()
htfadd98.Monitor().BOSJudge()
htfadd99.Monitor().BOSJudge()
htfadd100.Monitor().BOSJudge()
htfadd101.Monitor().BOSJudge()
htfadd102.Monitor().BOSJudge()
htfadd103.Monitor().BOSJudge()
htfadd104.Monitor().BOSJudge()
htfadd105.Monitor().BOSJudge()
htfadd106.Monitor().BOSJudge()
htfadd107.Monitor().BOSJudge()
htfadd108.Monitor().BOSJudge()
htfadd109.Monitor().BOSJudge()
htfadd110.Monitor().BOSJudge()
htfadd111.Monitor().BOSJudge()
htfadd112.Monitor().BOSJudge()
htfadd113.Monitor().BOSJudge()
htfadd114.Monitor().BOSJudge()
htfadd115.Monitor().BOSJudge()
htfadd116.Monitor().BOSJudge()
htfadd117.Monitor().BOSJudge()
htfadd118.Monitor().BOSJudge()
htfadd119.Monitor().BOSJudge()
htfadd120.Monitor().BOSJudge()
htfadd121.Monitor().BOSJudge()
htfadd122.Monitor().BOSJudge()
htfadd123.Monitor().BOSJudge()
htfadd124.Monitor().BOSJudge()
htfadd125.Monitor().BOSJudge()
htfadd126.Monitor().BOSJudge()
htfadd127.Monitor().BOSJudge()
htfadd128.Monitor().BOSJudge()
htfadd129.Monitor().BOSJudge()
htfadd130.Monitor().BOSJudge()
htfadd131.Monitor().BOSJudge()
htfadd132.Monitor().BOSJudge()
htfadd133.Monitor().BOSJudge()
htfadd134.Monitor().BOSJudge()
htfadd135.Monitor().BOSJudge()
htfadd136.Monitor().BOSJudge()
htfadd137.Monitor().BOSJudge()
htfadd138.Monitor().BOSJudge()
htfadd139.Monitor().BOSJudge()
htfadd140.Monitor().BOSJudge()
htfadd141.Monitor().BOSJudge()
htfadd142.Monitor().BOSJudge()
htfadd143.Monitor().BOSJudge()
htfadd144.Monitor().BOSJudge()
htfadd145.Monitor().BOSJudge()
htfadd146.Monitor().BOSJudge()
htfadd147.Monitor().BOSJudge()
htfadd148.Monitor().BOSJudge()
htfadd149.Monitor().BOSJudge()
htfadd150.Monitor().BOSJudge()
htfadd151.Monitor().BOSJudge()
htfadd152.Monitor().BOSJudge()
htfadd153.Monitor().BOSJudge()
htfadd154.Monitor().BOSJudge()
htfadd155.Monitor().BOSJudge()
htfadd156.Monitor().BOSJudge()
htfadd157.Monitor().BOSJudge()
htfadd158.Monitor().BOSJudge()
htfadd159.Monitor().BOSJudge()
htfadd160.Monitor().BOSJudge()
htfadd161.Monitor().BOSJudge()
htfadd162.Monitor().BOSJudge()
htfadd163.Monitor().BOSJudge()
htfadd164.Monitor().BOSJudge()
htfadd165.Monitor().BOSJudge()
htfadd166.Monitor().BOSJudge()
htfadd167.Monitor().BOSJudge()
htfadd168.Monitor().BOSJudge()
htfadd169.Monitor().BOSJudge()
htfadd170.Monitor().BOSJudge()
htfadd171.Monitor().BOSJudge()
htfadd172.Monitor().BOSJudge()
htfadd173.Monitor().BOSJudge()
htfadd174.Monitor().BOSJudge()
htfadd175.Monitor().BOSJudge()
htfadd176.Monitor().BOSJudge()
htfadd177.Monitor().BOSJudge()
htfadd178.Monitor().BOSJudge()
htfadd179.Monitor().BOSJudge()
htfadd180.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd90)
    LowestsbuSet(lowestsbu, htfadd90)
    HighestsbdSet(highestsbd, htfadd91)
    LowestsbuSet(lowestsbu, htfadd91)
    HighestsbdSet(highestsbd, htfadd92)
    LowestsbuSet(lowestsbu, htfadd92)
    HighestsbdSet(highestsbd, htfadd93)
    LowestsbuSet(lowestsbu, htfadd93)
    HighestsbdSet(highestsbd, htfadd94)
    LowestsbuSet(lowestsbu, htfadd94)
    HighestsbdSet(highestsbd, htfadd95)
    LowestsbuSet(lowestsbu, htfadd95)
    HighestsbdSet(highestsbd, htfadd96)
    LowestsbuSet(lowestsbu, htfadd96)
    HighestsbdSet(highestsbd, htfadd97)
    LowestsbuSet(lowestsbu, htfadd97)
    HighestsbdSet(highestsbd, htfadd98)
    LowestsbuSet(lowestsbu, htfadd98)
    HighestsbdSet(highestsbd, htfadd99)
    LowestsbuSet(lowestsbu, htfadd99)
    HighestsbdSet(highestsbd, htfadd100)
    LowestsbuSet(lowestsbu, htfadd100)
    HighestsbdSet(highestsbd, htfadd101)
    LowestsbuSet(lowestsbu, htfadd101)
    HighestsbdSet(highestsbd, htfadd102)
    LowestsbuSet(lowestsbu, htfadd102)
    HighestsbdSet(highestsbd, htfadd103)
    LowestsbuSet(lowestsbu, htfadd103)
    HighestsbdSet(highestsbd, htfadd104)
    LowestsbuSet(lowestsbu, htfadd104)
    HighestsbdSet(highestsbd, htfadd105)
    LowestsbuSet(lowestsbu, htfadd105)
    HighestsbdSet(highestsbd, htfadd106)
    LowestsbuSet(lowestsbu, htfadd106)
    HighestsbdSet(highestsbd, htfadd107)
    LowestsbuSet(lowestsbu, htfadd107)
    HighestsbdSet(highestsbd, htfadd108)
    LowestsbuSet(lowestsbu, htfadd108)
    HighestsbdSet(highestsbd, htfadd109)
    LowestsbuSet(lowestsbu, htfadd109)
    HighestsbdSet(highestsbd, htfadd110)
    LowestsbuSet(lowestsbu, htfadd110)
    HighestsbdSet(highestsbd, htfadd111)
    LowestsbuSet(lowestsbu, htfadd111)
    HighestsbdSet(highestsbd, htfadd112)
    LowestsbuSet(lowestsbu, htfadd112)
    HighestsbdSet(highestsbd, htfadd113)
    LowestsbuSet(lowestsbu, htfadd113)
    HighestsbdSet(highestsbd, htfadd114)
    LowestsbuSet(lowestsbu, htfadd114)
    HighestsbdSet(highestsbd, htfadd115)
    LowestsbuSet(lowestsbu, htfadd115)
    HighestsbdSet(highestsbd, htfadd116)
    LowestsbuSet(lowestsbu, htfadd116)
    HighestsbdSet(highestsbd, htfadd117)
    LowestsbuSet(lowestsbu, htfadd117)
    HighestsbdSet(highestsbd, htfadd118)
    LowestsbuSet(lowestsbu, htfadd118)
    HighestsbdSet(highestsbd, htfadd119)
    LowestsbuSet(lowestsbu, htfadd119)
    HighestsbdSet(highestsbd, htfadd120)
    LowestsbuSet(lowestsbu, htfadd120)
    HighestsbdSet(highestsbd, htfadd121)
    LowestsbuSet(lowestsbu, htfadd121)
    HighestsbdSet(highestsbd, htfadd122)
    LowestsbuSet(lowestsbu, htfadd122)
    HighestsbdSet(highestsbd, htfadd123)
    LowestsbuSet(lowestsbu, htfadd123)
    HighestsbdSet(highestsbd, htfadd124)
    LowestsbuSet(lowestsbu, htfadd124)
    HighestsbdSet(highestsbd, htfadd125)
    LowestsbuSet(lowestsbu, htfadd125)
    HighestsbdSet(highestsbd, htfadd126)
    LowestsbuSet(lowestsbu, htfadd126)
    HighestsbdSet(highestsbd, htfadd127)
    LowestsbuSet(lowestsbu, htfadd127)
    HighestsbdSet(highestsbd, htfadd128)
    LowestsbuSet(lowestsbu, htfadd128)
    HighestsbdSet(highestsbd, htfadd129)
    LowestsbuSet(lowestsbu, htfadd129)
    HighestsbdSet(highestsbd, htfadd130)
    LowestsbuSet(lowestsbu, htfadd130)
    HighestsbdSet(highestsbd, htfadd131)
    LowestsbuSet(lowestsbu, htfadd131)
    HighestsbdSet(highestsbd, htfadd132)
    LowestsbuSet(lowestsbu, htfadd132)
    HighestsbdSet(highestsbd, htfadd133)
    LowestsbuSet(lowestsbu, htfadd133)
    HighestsbdSet(highestsbd, htfadd134)
    LowestsbuSet(lowestsbu, htfadd134)
    HighestsbdSet(highestsbd, htfadd135)
    LowestsbuSet(lowestsbu, htfadd135)
    HighestsbdSet(highestsbd, htfadd136)
    LowestsbuSet(lowestsbu, htfadd136)
    HighestsbdSet(highestsbd, htfadd137)
    LowestsbuSet(lowestsbu, htfadd137)
    HighestsbdSet(highestsbd, htfadd138)
    LowestsbuSet(lowestsbu, htfadd138)
    HighestsbdSet(highestsbd, htfadd139)
    LowestsbuSet(lowestsbu, htfadd139)
    HighestsbdSet(highestsbd, htfadd140)
    LowestsbuSet(lowestsbu, htfadd140)
    HighestsbdSet(highestsbd, htfadd141)
    LowestsbuSet(lowestsbu, htfadd141)
    HighestsbdSet(highestsbd, htfadd142)
    LowestsbuSet(lowestsbu, htfadd142)
    HighestsbdSet(highestsbd, htfadd143)
    LowestsbuSet(lowestsbu, htfadd143)
    HighestsbdSet(highestsbd, htfadd144)
    LowestsbuSet(lowestsbu, htfadd144)
    HighestsbdSet(highestsbd, htfadd145)
    LowestsbuSet(lowestsbu, htfadd145)
    HighestsbdSet(highestsbd, htfadd146)
    LowestsbuSet(lowestsbu, htfadd146)
    HighestsbdSet(highestsbd, htfadd147)
    LowestsbuSet(lowestsbu, htfadd147)
    HighestsbdSet(highestsbd, htfadd148)
    LowestsbuSet(lowestsbu, htfadd148)
    HighestsbdSet(highestsbd, htfadd149)
    LowestsbuSet(lowestsbu, htfadd149)
    HighestsbdSet(highestsbd, htfadd150)
    LowestsbuSet(lowestsbu, htfadd150)
    HighestsbdSet(highestsbd, htfadd151)
    LowestsbuSet(lowestsbu, htfadd151)
    HighestsbdSet(highestsbd, htfadd152)
    LowestsbuSet(lowestsbu, htfadd152)
    HighestsbdSet(highestsbd, htfadd153)
    LowestsbuSet(lowestsbu, htfadd153)
    HighestsbdSet(highestsbd, htfadd154)
    LowestsbuSet(lowestsbu, htfadd154)
    HighestsbdSet(highestsbd, htfadd155)
    LowestsbuSet(lowestsbu, htfadd155)
    HighestsbdSet(highestsbd, htfadd156)
    LowestsbuSet(lowestsbu, htfadd156)
    HighestsbdSet(highestsbd, htfadd157)
    LowestsbuSet(lowestsbu, htfadd157)
    HighestsbdSet(highestsbd, htfadd158)
    LowestsbuSet(lowestsbu, htfadd158)
    HighestsbdSet(highestsbd, htfadd159)
    LowestsbuSet(lowestsbu, htfadd159)
    HighestsbdSet(highestsbd, htfadd160)
    LowestsbuSet(lowestsbu, htfadd160)
    HighestsbdSet(highestsbd, htfadd161)
    LowestsbuSet(lowestsbu, htfadd161)
    HighestsbdSet(highestsbd, htfadd162)
    LowestsbuSet(lowestsbu, htfadd162)
    HighestsbdSet(highestsbd, htfadd163)
    LowestsbuSet(lowestsbu, htfadd163)
    HighestsbdSet(highestsbd, htfadd164)
    LowestsbuSet(lowestsbu, htfadd164)
    HighestsbdSet(highestsbd, htfadd165)
    LowestsbuSet(lowestsbu, htfadd165)
    HighestsbdSet(highestsbd, htfadd166)
    LowestsbuSet(lowestsbu, htfadd166)
    HighestsbdSet(highestsbd, htfadd167)
    LowestsbuSet(lowestsbu, htfadd167)
    HighestsbdSet(highestsbd, htfadd168)
    LowestsbuSet(lowestsbu, htfadd168)
    HighestsbdSet(highestsbd, htfadd169)
    LowestsbuSet(lowestsbu, htfadd169)
    HighestsbdSet(highestsbd, htfadd170)
    LowestsbuSet(lowestsbu, htfadd170)
    HighestsbdSet(highestsbd, htfadd171)
    LowestsbuSet(lowestsbu, htfadd171)
    HighestsbdSet(highestsbd, htfadd172)
    LowestsbuSet(lowestsbu, htfadd172)
    HighestsbdSet(highestsbd, htfadd173)
    LowestsbuSet(lowestsbu, htfadd173)
    HighestsbdSet(highestsbd, htfadd174)
    LowestsbuSet(lowestsbu, htfadd174)
    HighestsbdSet(highestsbd, htfadd175)
    LowestsbuSet(lowestsbu, htfadd175)
    HighestsbdSet(highestsbd, htfadd176)
    LowestsbuSet(lowestsbu, htfadd176)
    HighestsbdSet(highestsbd, htfadd177)
    LowestsbuSet(lowestsbu, htfadd177)
    HighestsbdSet(highestsbd, htfadd178)
    LowestsbuSet(lowestsbu, htfadd178)
    HighestsbdSet(highestsbd, htfadd179)
    LowestsbuSet(lowestsbu, htfadd179)
    HighestsbdSet(highestsbd, htfadd180)
    LowestsbuSet(lowestsbu, htfadd180)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd90).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd91).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd92).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd93).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd94).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd95).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd96).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd97).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd98).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd99).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd100).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd101).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd102).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd103).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd104).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd105).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd106).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd107).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd108).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd109).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd110).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd111).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd112).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd113).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd114).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd115).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd116).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd117).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd118).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd119).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd120).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd121).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd122).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd123).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd124).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd125).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd126).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd127).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd128).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd129).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd130).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd131).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd132).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd133).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd134).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd135).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd136).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd137).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd138).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd139).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd140).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd141).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd142).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd143).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd144).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd145).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd146).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd147).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd148).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd149).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd150).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd151).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd152).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd153).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd154).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd155).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd156).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd157).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd158).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd159).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd160).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd161).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd162).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd163).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd164).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd165).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd166).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd167).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd168).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd169).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd170).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd171).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd172).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd173).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd174).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd175).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd176).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd177).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd178).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd179).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd180).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)

    fggetnowclose := false
//+---------------add var end------------------+//
if settings.add_show and barstate.isrealtime
    estminsbu.addplot(offset)
    estmaxsbd.addplot(offset)
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

index += 1


