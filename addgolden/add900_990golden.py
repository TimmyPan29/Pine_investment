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
var CandleSet htfadd900                     = CandleSet.new()
var CandleSettings SettingsHTFadd900        = CandleSettings.new(htf='900',htfint=900,max_memory=3)
var Candle[] candlesadd900                  = array.new<Candle>(0)
var BOSdata bosdataadd900                   = BOSdata.new()
htfadd900.settings                 := SettingsHTFadd900
htfadd900.candles                  := candlesadd900
htfadd900.bosdata                  := bosdataadd900
var CandleSet htfadd901                     = CandleSet.new()
var CandleSettings SettingsHTFadd901        = CandleSettings.new(htf='901',htfint=901,max_memory=3)
var Candle[] candlesadd901                  = array.new<Candle>(0)
var BOSdata bosdataadd901                   = BOSdata.new()
htfadd901.settings                 := SettingsHTFadd901
htfadd901.candles                  := candlesadd901
htfadd901.bosdata                  := bosdataadd901
var CandleSet htfadd902                     = CandleSet.new()
var CandleSettings SettingsHTFadd902        = CandleSettings.new(htf='902',htfint=902,max_memory=3)
var Candle[] candlesadd902                  = array.new<Candle>(0)
var BOSdata bosdataadd902                   = BOSdata.new()
htfadd902.settings                 := SettingsHTFadd902
htfadd902.candles                  := candlesadd902
htfadd902.bosdata                  := bosdataadd902
var CandleSet htfadd903                     = CandleSet.new()
var CandleSettings SettingsHTFadd903        = CandleSettings.new(htf='903',htfint=903,max_memory=3)
var Candle[] candlesadd903                  = array.new<Candle>(0)
var BOSdata bosdataadd903                   = BOSdata.new()
htfadd903.settings                 := SettingsHTFadd903
htfadd903.candles                  := candlesadd903
htfadd903.bosdata                  := bosdataadd903
var CandleSet htfadd904                     = CandleSet.new()
var CandleSettings SettingsHTFadd904        = CandleSettings.new(htf='904',htfint=904,max_memory=3)
var Candle[] candlesadd904                  = array.new<Candle>(0)
var BOSdata bosdataadd904                   = BOSdata.new()
htfadd904.settings                 := SettingsHTFadd904
htfadd904.candles                  := candlesadd904
htfadd904.bosdata                  := bosdataadd904
var CandleSet htfadd905                     = CandleSet.new()
var CandleSettings SettingsHTFadd905        = CandleSettings.new(htf='905',htfint=905,max_memory=3)
var Candle[] candlesadd905                  = array.new<Candle>(0)
var BOSdata bosdataadd905                   = BOSdata.new()
htfadd905.settings                 := SettingsHTFadd905
htfadd905.candles                  := candlesadd905
htfadd905.bosdata                  := bosdataadd905
var CandleSet htfadd906                     = CandleSet.new()
var CandleSettings SettingsHTFadd906        = CandleSettings.new(htf='906',htfint=906,max_memory=3)
var Candle[] candlesadd906                  = array.new<Candle>(0)
var BOSdata bosdataadd906                   = BOSdata.new()
htfadd906.settings                 := SettingsHTFadd906
htfadd906.candles                  := candlesadd906
htfadd906.bosdata                  := bosdataadd906
var CandleSet htfadd907                     = CandleSet.new()
var CandleSettings SettingsHTFadd907        = CandleSettings.new(htf='907',htfint=907,max_memory=3)
var Candle[] candlesadd907                  = array.new<Candle>(0)
var BOSdata bosdataadd907                   = BOSdata.new()
htfadd907.settings                 := SettingsHTFadd907
htfadd907.candles                  := candlesadd907
htfadd907.bosdata                  := bosdataadd907
var CandleSet htfadd908                     = CandleSet.new()
var CandleSettings SettingsHTFadd908        = CandleSettings.new(htf='908',htfint=908,max_memory=3)
var Candle[] candlesadd908                  = array.new<Candle>(0)
var BOSdata bosdataadd908                   = BOSdata.new()
htfadd908.settings                 := SettingsHTFadd908
htfadd908.candles                  := candlesadd908
htfadd908.bosdata                  := bosdataadd908
var CandleSet htfadd909                     = CandleSet.new()
var CandleSettings SettingsHTFadd909        = CandleSettings.new(htf='909',htfint=909,max_memory=3)
var Candle[] candlesadd909                  = array.new<Candle>(0)
var BOSdata bosdataadd909                   = BOSdata.new()
htfadd909.settings                 := SettingsHTFadd909
htfadd909.candles                  := candlesadd909
htfadd909.bosdata                  := bosdataadd909
var CandleSet htfadd910                     = CandleSet.new()
var CandleSettings SettingsHTFadd910        = CandleSettings.new(htf='910',htfint=910,max_memory=3)
var Candle[] candlesadd910                  = array.new<Candle>(0)
var BOSdata bosdataadd910                   = BOSdata.new()
htfadd910.settings                 := SettingsHTFadd910
htfadd910.candles                  := candlesadd910
htfadd910.bosdata                  := bosdataadd910
var CandleSet htfadd911                     = CandleSet.new()
var CandleSettings SettingsHTFadd911        = CandleSettings.new(htf='911',htfint=911,max_memory=3)
var Candle[] candlesadd911                  = array.new<Candle>(0)
var BOSdata bosdataadd911                   = BOSdata.new()
htfadd911.settings                 := SettingsHTFadd911
htfadd911.candles                  := candlesadd911
htfadd911.bosdata                  := bosdataadd911
var CandleSet htfadd912                     = CandleSet.new()
var CandleSettings SettingsHTFadd912        = CandleSettings.new(htf='912',htfint=912,max_memory=3)
var Candle[] candlesadd912                  = array.new<Candle>(0)
var BOSdata bosdataadd912                   = BOSdata.new()
htfadd912.settings                 := SettingsHTFadd912
htfadd912.candles                  := candlesadd912
htfadd912.bosdata                  := bosdataadd912
var CandleSet htfadd913                     = CandleSet.new()
var CandleSettings SettingsHTFadd913        = CandleSettings.new(htf='913',htfint=913,max_memory=3)
var Candle[] candlesadd913                  = array.new<Candle>(0)
var BOSdata bosdataadd913                   = BOSdata.new()
htfadd913.settings                 := SettingsHTFadd913
htfadd913.candles                  := candlesadd913
htfadd913.bosdata                  := bosdataadd913
var CandleSet htfadd914                     = CandleSet.new()
var CandleSettings SettingsHTFadd914        = CandleSettings.new(htf='914',htfint=914,max_memory=3)
var Candle[] candlesadd914                  = array.new<Candle>(0)
var BOSdata bosdataadd914                   = BOSdata.new()
htfadd914.settings                 := SettingsHTFadd914
htfadd914.candles                  := candlesadd914
htfadd914.bosdata                  := bosdataadd914
var CandleSet htfadd915                     = CandleSet.new()
var CandleSettings SettingsHTFadd915        = CandleSettings.new(htf='915',htfint=915,max_memory=3)
var Candle[] candlesadd915                  = array.new<Candle>(0)
var BOSdata bosdataadd915                   = BOSdata.new()
htfadd915.settings                 := SettingsHTFadd915
htfadd915.candles                  := candlesadd915
htfadd915.bosdata                  := bosdataadd915
var CandleSet htfadd916                     = CandleSet.new()
var CandleSettings SettingsHTFadd916        = CandleSettings.new(htf='916',htfint=916,max_memory=3)
var Candle[] candlesadd916                  = array.new<Candle>(0)
var BOSdata bosdataadd916                   = BOSdata.new()
htfadd916.settings                 := SettingsHTFadd916
htfadd916.candles                  := candlesadd916
htfadd916.bosdata                  := bosdataadd916
var CandleSet htfadd917                     = CandleSet.new()
var CandleSettings SettingsHTFadd917        = CandleSettings.new(htf='917',htfint=917,max_memory=3)
var Candle[] candlesadd917                  = array.new<Candle>(0)
var BOSdata bosdataadd917                   = BOSdata.new()
htfadd917.settings                 := SettingsHTFadd917
htfadd917.candles                  := candlesadd917
htfadd917.bosdata                  := bosdataadd917
var CandleSet htfadd918                     = CandleSet.new()
var CandleSettings SettingsHTFadd918        = CandleSettings.new(htf='918',htfint=918,max_memory=3)
var Candle[] candlesadd918                  = array.new<Candle>(0)
var BOSdata bosdataadd918                   = BOSdata.new()
htfadd918.settings                 := SettingsHTFadd918
htfadd918.candles                  := candlesadd918
htfadd918.bosdata                  := bosdataadd918
var CandleSet htfadd919                     = CandleSet.new()
var CandleSettings SettingsHTFadd919        = CandleSettings.new(htf='919',htfint=919,max_memory=3)
var Candle[] candlesadd919                  = array.new<Candle>(0)
var BOSdata bosdataadd919                   = BOSdata.new()
htfadd919.settings                 := SettingsHTFadd919
htfadd919.candles                  := candlesadd919
htfadd919.bosdata                  := bosdataadd919
var CandleSet htfadd920                     = CandleSet.new()
var CandleSettings SettingsHTFadd920        = CandleSettings.new(htf='920',htfint=920,max_memory=3)
var Candle[] candlesadd920                  = array.new<Candle>(0)
var BOSdata bosdataadd920                   = BOSdata.new()
htfadd920.settings                 := SettingsHTFadd920
htfadd920.candles                  := candlesadd920
htfadd920.bosdata                  := bosdataadd920
var CandleSet htfadd921                     = CandleSet.new()
var CandleSettings SettingsHTFadd921        = CandleSettings.new(htf='921',htfint=921,max_memory=3)
var Candle[] candlesadd921                  = array.new<Candle>(0)
var BOSdata bosdataadd921                   = BOSdata.new()
htfadd921.settings                 := SettingsHTFadd921
htfadd921.candles                  := candlesadd921
htfadd921.bosdata                  := bosdataadd921
var CandleSet htfadd922                     = CandleSet.new()
var CandleSettings SettingsHTFadd922        = CandleSettings.new(htf='922',htfint=922,max_memory=3)
var Candle[] candlesadd922                  = array.new<Candle>(0)
var BOSdata bosdataadd922                   = BOSdata.new()
htfadd922.settings                 := SettingsHTFadd922
htfadd922.candles                  := candlesadd922
htfadd922.bosdata                  := bosdataadd922
var CandleSet htfadd923                     = CandleSet.new()
var CandleSettings SettingsHTFadd923        = CandleSettings.new(htf='923',htfint=923,max_memory=3)
var Candle[] candlesadd923                  = array.new<Candle>(0)
var BOSdata bosdataadd923                   = BOSdata.new()
htfadd923.settings                 := SettingsHTFadd923
htfadd923.candles                  := candlesadd923
htfadd923.bosdata                  := bosdataadd923
var CandleSet htfadd924                     = CandleSet.new()
var CandleSettings SettingsHTFadd924        = CandleSettings.new(htf='924',htfint=924,max_memory=3)
var Candle[] candlesadd924                  = array.new<Candle>(0)
var BOSdata bosdataadd924                   = BOSdata.new()
htfadd924.settings                 := SettingsHTFadd924
htfadd924.candles                  := candlesadd924
htfadd924.bosdata                  := bosdataadd924
var CandleSet htfadd925                     = CandleSet.new()
var CandleSettings SettingsHTFadd925        = CandleSettings.new(htf='925',htfint=925,max_memory=3)
var Candle[] candlesadd925                  = array.new<Candle>(0)
var BOSdata bosdataadd925                   = BOSdata.new()
htfadd925.settings                 := SettingsHTFadd925
htfadd925.candles                  := candlesadd925
htfadd925.bosdata                  := bosdataadd925
var CandleSet htfadd926                     = CandleSet.new()
var CandleSettings SettingsHTFadd926        = CandleSettings.new(htf='926',htfint=926,max_memory=3)
var Candle[] candlesadd926                  = array.new<Candle>(0)
var BOSdata bosdataadd926                   = BOSdata.new()
htfadd926.settings                 := SettingsHTFadd926
htfadd926.candles                  := candlesadd926
htfadd926.bosdata                  := bosdataadd926
var CandleSet htfadd927                     = CandleSet.new()
var CandleSettings SettingsHTFadd927        = CandleSettings.new(htf='927',htfint=927,max_memory=3)
var Candle[] candlesadd927                  = array.new<Candle>(0)
var BOSdata bosdataadd927                   = BOSdata.new()
htfadd927.settings                 := SettingsHTFadd927
htfadd927.candles                  := candlesadd927
htfadd927.bosdata                  := bosdataadd927
var CandleSet htfadd928                     = CandleSet.new()
var CandleSettings SettingsHTFadd928        = CandleSettings.new(htf='928',htfint=928,max_memory=3)
var Candle[] candlesadd928                  = array.new<Candle>(0)
var BOSdata bosdataadd928                   = BOSdata.new()
htfadd928.settings                 := SettingsHTFadd928
htfadd928.candles                  := candlesadd928
htfadd928.bosdata                  := bosdataadd928
var CandleSet htfadd929                     = CandleSet.new()
var CandleSettings SettingsHTFadd929        = CandleSettings.new(htf='929',htfint=929,max_memory=3)
var Candle[] candlesadd929                  = array.new<Candle>(0)
var BOSdata bosdataadd929                   = BOSdata.new()
htfadd929.settings                 := SettingsHTFadd929
htfadd929.candles                  := candlesadd929
htfadd929.bosdata                  := bosdataadd929
var CandleSet htfadd930                     = CandleSet.new()
var CandleSettings SettingsHTFadd930        = CandleSettings.new(htf='930',htfint=930,max_memory=3)
var Candle[] candlesadd930                  = array.new<Candle>(0)
var BOSdata bosdataadd930                   = BOSdata.new()
htfadd930.settings                 := SettingsHTFadd930
htfadd930.candles                  := candlesadd930
htfadd930.bosdata                  := bosdataadd930
var CandleSet htfadd931                     = CandleSet.new()
var CandleSettings SettingsHTFadd931        = CandleSettings.new(htf='931',htfint=931,max_memory=3)
var Candle[] candlesadd931                  = array.new<Candle>(0)
var BOSdata bosdataadd931                   = BOSdata.new()
htfadd931.settings                 := SettingsHTFadd931
htfadd931.candles                  := candlesadd931
htfadd931.bosdata                  := bosdataadd931
var CandleSet htfadd932                     = CandleSet.new()
var CandleSettings SettingsHTFadd932        = CandleSettings.new(htf='932',htfint=932,max_memory=3)
var Candle[] candlesadd932                  = array.new<Candle>(0)
var BOSdata bosdataadd932                   = BOSdata.new()
htfadd932.settings                 := SettingsHTFadd932
htfadd932.candles                  := candlesadd932
htfadd932.bosdata                  := bosdataadd932
var CandleSet htfadd933                     = CandleSet.new()
var CandleSettings SettingsHTFadd933        = CandleSettings.new(htf='933',htfint=933,max_memory=3)
var Candle[] candlesadd933                  = array.new<Candle>(0)
var BOSdata bosdataadd933                   = BOSdata.new()
htfadd933.settings                 := SettingsHTFadd933
htfadd933.candles                  := candlesadd933
htfadd933.bosdata                  := bosdataadd933
var CandleSet htfadd934                     = CandleSet.new()
var CandleSettings SettingsHTFadd934        = CandleSettings.new(htf='934',htfint=934,max_memory=3)
var Candle[] candlesadd934                  = array.new<Candle>(0)
var BOSdata bosdataadd934                   = BOSdata.new()
htfadd934.settings                 := SettingsHTFadd934
htfadd934.candles                  := candlesadd934
htfadd934.bosdata                  := bosdataadd934
var CandleSet htfadd935                     = CandleSet.new()
var CandleSettings SettingsHTFadd935        = CandleSettings.new(htf='935',htfint=935,max_memory=3)
var Candle[] candlesadd935                  = array.new<Candle>(0)
var BOSdata bosdataadd935                   = BOSdata.new()
htfadd935.settings                 := SettingsHTFadd935
htfadd935.candles                  := candlesadd935
htfadd935.bosdata                  := bosdataadd935
var CandleSet htfadd936                     = CandleSet.new()
var CandleSettings SettingsHTFadd936        = CandleSettings.new(htf='936',htfint=936,max_memory=3)
var Candle[] candlesadd936                  = array.new<Candle>(0)
var BOSdata bosdataadd936                   = BOSdata.new()
htfadd936.settings                 := SettingsHTFadd936
htfadd936.candles                  := candlesadd936
htfadd936.bosdata                  := bosdataadd936
var CandleSet htfadd937                     = CandleSet.new()
var CandleSettings SettingsHTFadd937        = CandleSettings.new(htf='937',htfint=937,max_memory=3)
var Candle[] candlesadd937                  = array.new<Candle>(0)
var BOSdata bosdataadd937                   = BOSdata.new()
htfadd937.settings                 := SettingsHTFadd937
htfadd937.candles                  := candlesadd937
htfadd937.bosdata                  := bosdataadd937
var CandleSet htfadd938                     = CandleSet.new()
var CandleSettings SettingsHTFadd938        = CandleSettings.new(htf='938',htfint=938,max_memory=3)
var Candle[] candlesadd938                  = array.new<Candle>(0)
var BOSdata bosdataadd938                   = BOSdata.new()
htfadd938.settings                 := SettingsHTFadd938
htfadd938.candles                  := candlesadd938
htfadd938.bosdata                  := bosdataadd938
var CandleSet htfadd939                     = CandleSet.new()
var CandleSettings SettingsHTFadd939        = CandleSettings.new(htf='939',htfint=939,max_memory=3)
var Candle[] candlesadd939                  = array.new<Candle>(0)
var BOSdata bosdataadd939                   = BOSdata.new()
htfadd939.settings                 := SettingsHTFadd939
htfadd939.candles                  := candlesadd939
htfadd939.bosdata                  := bosdataadd939
var CandleSet htfadd940                     = CandleSet.new()
var CandleSettings SettingsHTFadd940        = CandleSettings.new(htf='940',htfint=940,max_memory=3)
var Candle[] candlesadd940                  = array.new<Candle>(0)
var BOSdata bosdataadd940                   = BOSdata.new()
htfadd940.settings                 := SettingsHTFadd940
htfadd940.candles                  := candlesadd940
htfadd940.bosdata                  := bosdataadd940
var CandleSet htfadd941                     = CandleSet.new()
var CandleSettings SettingsHTFadd941        = CandleSettings.new(htf='941',htfint=941,max_memory=3)
var Candle[] candlesadd941                  = array.new<Candle>(0)
var BOSdata bosdataadd941                   = BOSdata.new()
htfadd941.settings                 := SettingsHTFadd941
htfadd941.candles                  := candlesadd941
htfadd941.bosdata                  := bosdataadd941
var CandleSet htfadd942                     = CandleSet.new()
var CandleSettings SettingsHTFadd942        = CandleSettings.new(htf='942',htfint=942,max_memory=3)
var Candle[] candlesadd942                  = array.new<Candle>(0)
var BOSdata bosdataadd942                   = BOSdata.new()
htfadd942.settings                 := SettingsHTFadd942
htfadd942.candles                  := candlesadd942
htfadd942.bosdata                  := bosdataadd942
var CandleSet htfadd943                     = CandleSet.new()
var CandleSettings SettingsHTFadd943        = CandleSettings.new(htf='943',htfint=943,max_memory=3)
var Candle[] candlesadd943                  = array.new<Candle>(0)
var BOSdata bosdataadd943                   = BOSdata.new()
htfadd943.settings                 := SettingsHTFadd943
htfadd943.candles                  := candlesadd943
htfadd943.bosdata                  := bosdataadd943
var CandleSet htfadd944                     = CandleSet.new()
var CandleSettings SettingsHTFadd944        = CandleSettings.new(htf='944',htfint=944,max_memory=3)
var Candle[] candlesadd944                  = array.new<Candle>(0)
var BOSdata bosdataadd944                   = BOSdata.new()
htfadd944.settings                 := SettingsHTFadd944
htfadd944.candles                  := candlesadd944
htfadd944.bosdata                  := bosdataadd944
var CandleSet htfadd945                     = CandleSet.new()
var CandleSettings SettingsHTFadd945        = CandleSettings.new(htf='945',htfint=945,max_memory=3)
var Candle[] candlesadd945                  = array.new<Candle>(0)
var BOSdata bosdataadd945                   = BOSdata.new()
htfadd945.settings                 := SettingsHTFadd945
htfadd945.candles                  := candlesadd945
htfadd945.bosdata                  := bosdataadd945
var CandleSet htfadd946                     = CandleSet.new()
var CandleSettings SettingsHTFadd946        = CandleSettings.new(htf='946',htfint=946,max_memory=3)
var Candle[] candlesadd946                  = array.new<Candle>(0)
var BOSdata bosdataadd946                   = BOSdata.new()
htfadd946.settings                 := SettingsHTFadd946
htfadd946.candles                  := candlesadd946
htfadd946.bosdata                  := bosdataadd946
var CandleSet htfadd947                     = CandleSet.new()
var CandleSettings SettingsHTFadd947        = CandleSettings.new(htf='947',htfint=947,max_memory=3)
var Candle[] candlesadd947                  = array.new<Candle>(0)
var BOSdata bosdataadd947                   = BOSdata.new()
htfadd947.settings                 := SettingsHTFadd947
htfadd947.candles                  := candlesadd947
htfadd947.bosdata                  := bosdataadd947
var CandleSet htfadd948                     = CandleSet.new()
var CandleSettings SettingsHTFadd948        = CandleSettings.new(htf='948',htfint=948,max_memory=3)
var Candle[] candlesadd948                  = array.new<Candle>(0)
var BOSdata bosdataadd948                   = BOSdata.new()
htfadd948.settings                 := SettingsHTFadd948
htfadd948.candles                  := candlesadd948
htfadd948.bosdata                  := bosdataadd948
var CandleSet htfadd949                     = CandleSet.new()
var CandleSettings SettingsHTFadd949        = CandleSettings.new(htf='949',htfint=949,max_memory=3)
var Candle[] candlesadd949                  = array.new<Candle>(0)
var BOSdata bosdataadd949                   = BOSdata.new()
htfadd949.settings                 := SettingsHTFadd949
htfadd949.candles                  := candlesadd949
htfadd949.bosdata                  := bosdataadd949
var CandleSet htfadd950                     = CandleSet.new()
var CandleSettings SettingsHTFadd950        = CandleSettings.new(htf='950',htfint=950,max_memory=3)
var Candle[] candlesadd950                  = array.new<Candle>(0)
var BOSdata bosdataadd950                   = BOSdata.new()
htfadd950.settings                 := SettingsHTFadd950
htfadd950.candles                  := candlesadd950
htfadd950.bosdata                  := bosdataadd950
var CandleSet htfadd951                     = CandleSet.new()
var CandleSettings SettingsHTFadd951        = CandleSettings.new(htf='951',htfint=951,max_memory=3)
var Candle[] candlesadd951                  = array.new<Candle>(0)
var BOSdata bosdataadd951                   = BOSdata.new()
htfadd951.settings                 := SettingsHTFadd951
htfadd951.candles                  := candlesadd951
htfadd951.bosdata                  := bosdataadd951
var CandleSet htfadd952                     = CandleSet.new()
var CandleSettings SettingsHTFadd952        = CandleSettings.new(htf='952',htfint=952,max_memory=3)
var Candle[] candlesadd952                  = array.new<Candle>(0)
var BOSdata bosdataadd952                   = BOSdata.new()
htfadd952.settings                 := SettingsHTFadd952
htfadd952.candles                  := candlesadd952
htfadd952.bosdata                  := bosdataadd952
var CandleSet htfadd953                     = CandleSet.new()
var CandleSettings SettingsHTFadd953        = CandleSettings.new(htf='953',htfint=953,max_memory=3)
var Candle[] candlesadd953                  = array.new<Candle>(0)
var BOSdata bosdataadd953                   = BOSdata.new()
htfadd953.settings                 := SettingsHTFadd953
htfadd953.candles                  := candlesadd953
htfadd953.bosdata                  := bosdataadd953
var CandleSet htfadd954                     = CandleSet.new()
var CandleSettings SettingsHTFadd954        = CandleSettings.new(htf='954',htfint=954,max_memory=3)
var Candle[] candlesadd954                  = array.new<Candle>(0)
var BOSdata bosdataadd954                   = BOSdata.new()
htfadd954.settings                 := SettingsHTFadd954
htfadd954.candles                  := candlesadd954
htfadd954.bosdata                  := bosdataadd954
var CandleSet htfadd955                     = CandleSet.new()
var CandleSettings SettingsHTFadd955        = CandleSettings.new(htf='955',htfint=955,max_memory=3)
var Candle[] candlesadd955                  = array.new<Candle>(0)
var BOSdata bosdataadd955                   = BOSdata.new()
htfadd955.settings                 := SettingsHTFadd955
htfadd955.candles                  := candlesadd955
htfadd955.bosdata                  := bosdataadd955
var CandleSet htfadd956                     = CandleSet.new()
var CandleSettings SettingsHTFadd956        = CandleSettings.new(htf='956',htfint=956,max_memory=3)
var Candle[] candlesadd956                  = array.new<Candle>(0)
var BOSdata bosdataadd956                   = BOSdata.new()
htfadd956.settings                 := SettingsHTFadd956
htfadd956.candles                  := candlesadd956
htfadd956.bosdata                  := bosdataadd956
var CandleSet htfadd957                     = CandleSet.new()
var CandleSettings SettingsHTFadd957        = CandleSettings.new(htf='957',htfint=957,max_memory=3)
var Candle[] candlesadd957                  = array.new<Candle>(0)
var BOSdata bosdataadd957                   = BOSdata.new()
htfadd957.settings                 := SettingsHTFadd957
htfadd957.candles                  := candlesadd957
htfadd957.bosdata                  := bosdataadd957
var CandleSet htfadd958                     = CandleSet.new()
var CandleSettings SettingsHTFadd958        = CandleSettings.new(htf='958',htfint=958,max_memory=3)
var Candle[] candlesadd958                  = array.new<Candle>(0)
var BOSdata bosdataadd958                   = BOSdata.new()
htfadd958.settings                 := SettingsHTFadd958
htfadd958.candles                  := candlesadd958
htfadd958.bosdata                  := bosdataadd958
var CandleSet htfadd959                     = CandleSet.new()
var CandleSettings SettingsHTFadd959        = CandleSettings.new(htf='959',htfint=959,max_memory=3)
var Candle[] candlesadd959                  = array.new<Candle>(0)
var BOSdata bosdataadd959                   = BOSdata.new()
htfadd959.settings                 := SettingsHTFadd959
htfadd959.candles                  := candlesadd959
htfadd959.bosdata                  := bosdataadd959
var CandleSet htfadd960                     = CandleSet.new()
var CandleSettings SettingsHTFadd960        = CandleSettings.new(htf='960',htfint=960,max_memory=3)
var Candle[] candlesadd960                  = array.new<Candle>(0)
var BOSdata bosdataadd960                   = BOSdata.new()
htfadd960.settings                 := SettingsHTFadd960
htfadd960.candles                  := candlesadd960
htfadd960.bosdata                  := bosdataadd960
var CandleSet htfadd961                     = CandleSet.new()
var CandleSettings SettingsHTFadd961        = CandleSettings.new(htf='961',htfint=961,max_memory=3)
var Candle[] candlesadd961                  = array.new<Candle>(0)
var BOSdata bosdataadd961                   = BOSdata.new()
htfadd961.settings                 := SettingsHTFadd961
htfadd961.candles                  := candlesadd961
htfadd961.bosdata                  := bosdataadd961
var CandleSet htfadd962                     = CandleSet.new()
var CandleSettings SettingsHTFadd962        = CandleSettings.new(htf='962',htfint=962,max_memory=3)
var Candle[] candlesadd962                  = array.new<Candle>(0)
var BOSdata bosdataadd962                   = BOSdata.new()
htfadd962.settings                 := SettingsHTFadd962
htfadd962.candles                  := candlesadd962
htfadd962.bosdata                  := bosdataadd962
var CandleSet htfadd963                     = CandleSet.new()
var CandleSettings SettingsHTFadd963        = CandleSettings.new(htf='963',htfint=963,max_memory=3)
var Candle[] candlesadd963                  = array.new<Candle>(0)
var BOSdata bosdataadd963                   = BOSdata.new()
htfadd963.settings                 := SettingsHTFadd963
htfadd963.candles                  := candlesadd963
htfadd963.bosdata                  := bosdataadd963
var CandleSet htfadd964                     = CandleSet.new()
var CandleSettings SettingsHTFadd964        = CandleSettings.new(htf='964',htfint=964,max_memory=3)
var Candle[] candlesadd964                  = array.new<Candle>(0)
var BOSdata bosdataadd964                   = BOSdata.new()
htfadd964.settings                 := SettingsHTFadd964
htfadd964.candles                  := candlesadd964
htfadd964.bosdata                  := bosdataadd964
var CandleSet htfadd965                     = CandleSet.new()
var CandleSettings SettingsHTFadd965        = CandleSettings.new(htf='965',htfint=965,max_memory=3)
var Candle[] candlesadd965                  = array.new<Candle>(0)
var BOSdata bosdataadd965                   = BOSdata.new()
htfadd965.settings                 := SettingsHTFadd965
htfadd965.candles                  := candlesadd965
htfadd965.bosdata                  := bosdataadd965
var CandleSet htfadd966                     = CandleSet.new()
var CandleSettings SettingsHTFadd966        = CandleSettings.new(htf='966',htfint=966,max_memory=3)
var Candle[] candlesadd966                  = array.new<Candle>(0)
var BOSdata bosdataadd966                   = BOSdata.new()
htfadd966.settings                 := SettingsHTFadd966
htfadd966.candles                  := candlesadd966
htfadd966.bosdata                  := bosdataadd966
var CandleSet htfadd967                     = CandleSet.new()
var CandleSettings SettingsHTFadd967        = CandleSettings.new(htf='967',htfint=967,max_memory=3)
var Candle[] candlesadd967                  = array.new<Candle>(0)
var BOSdata bosdataadd967                   = BOSdata.new()
htfadd967.settings                 := SettingsHTFadd967
htfadd967.candles                  := candlesadd967
htfadd967.bosdata                  := bosdataadd967
var CandleSet htfadd968                     = CandleSet.new()
var CandleSettings SettingsHTFadd968        = CandleSettings.new(htf='968',htfint=968,max_memory=3)
var Candle[] candlesadd968                  = array.new<Candle>(0)
var BOSdata bosdataadd968                   = BOSdata.new()
htfadd968.settings                 := SettingsHTFadd968
htfadd968.candles                  := candlesadd968
htfadd968.bosdata                  := bosdataadd968
var CandleSet htfadd969                     = CandleSet.new()
var CandleSettings SettingsHTFadd969        = CandleSettings.new(htf='969',htfint=969,max_memory=3)
var Candle[] candlesadd969                  = array.new<Candle>(0)
var BOSdata bosdataadd969                   = BOSdata.new()
htfadd969.settings                 := SettingsHTFadd969
htfadd969.candles                  := candlesadd969
htfadd969.bosdata                  := bosdataadd969
var CandleSet htfadd970                     = CandleSet.new()
var CandleSettings SettingsHTFadd970        = CandleSettings.new(htf='970',htfint=970,max_memory=3)
var Candle[] candlesadd970                  = array.new<Candle>(0)
var BOSdata bosdataadd970                   = BOSdata.new()
htfadd970.settings                 := SettingsHTFadd970
htfadd970.candles                  := candlesadd970
htfadd970.bosdata                  := bosdataadd970
var CandleSet htfadd971                     = CandleSet.new()
var CandleSettings SettingsHTFadd971        = CandleSettings.new(htf='971',htfint=971,max_memory=3)
var Candle[] candlesadd971                  = array.new<Candle>(0)
var BOSdata bosdataadd971                   = BOSdata.new()
htfadd971.settings                 := SettingsHTFadd971
htfadd971.candles                  := candlesadd971
htfadd971.bosdata                  := bosdataadd971
var CandleSet htfadd972                     = CandleSet.new()
var CandleSettings SettingsHTFadd972        = CandleSettings.new(htf='972',htfint=972,max_memory=3)
var Candle[] candlesadd972                  = array.new<Candle>(0)
var BOSdata bosdataadd972                   = BOSdata.new()
htfadd972.settings                 := SettingsHTFadd972
htfadd972.candles                  := candlesadd972
htfadd972.bosdata                  := bosdataadd972
var CandleSet htfadd973                     = CandleSet.new()
var CandleSettings SettingsHTFadd973        = CandleSettings.new(htf='973',htfint=973,max_memory=3)
var Candle[] candlesadd973                  = array.new<Candle>(0)
var BOSdata bosdataadd973                   = BOSdata.new()
htfadd973.settings                 := SettingsHTFadd973
htfadd973.candles                  := candlesadd973
htfadd973.bosdata                  := bosdataadd973
var CandleSet htfadd974                     = CandleSet.new()
var CandleSettings SettingsHTFadd974        = CandleSettings.new(htf='974',htfint=974,max_memory=3)
var Candle[] candlesadd974                  = array.new<Candle>(0)
var BOSdata bosdataadd974                   = BOSdata.new()
htfadd974.settings                 := SettingsHTFadd974
htfadd974.candles                  := candlesadd974
htfadd974.bosdata                  := bosdataadd974
var CandleSet htfadd975                     = CandleSet.new()
var CandleSettings SettingsHTFadd975        = CandleSettings.new(htf='975',htfint=975,max_memory=3)
var Candle[] candlesadd975                  = array.new<Candle>(0)
var BOSdata bosdataadd975                   = BOSdata.new()
htfadd975.settings                 := SettingsHTFadd975
htfadd975.candles                  := candlesadd975
htfadd975.bosdata                  := bosdataadd975
var CandleSet htfadd976                     = CandleSet.new()
var CandleSettings SettingsHTFadd976        = CandleSettings.new(htf='976',htfint=976,max_memory=3)
var Candle[] candlesadd976                  = array.new<Candle>(0)
var BOSdata bosdataadd976                   = BOSdata.new()
htfadd976.settings                 := SettingsHTFadd976
htfadd976.candles                  := candlesadd976
htfadd976.bosdata                  := bosdataadd976
var CandleSet htfadd977                     = CandleSet.new()
var CandleSettings SettingsHTFadd977        = CandleSettings.new(htf='977',htfint=977,max_memory=3)
var Candle[] candlesadd977                  = array.new<Candle>(0)
var BOSdata bosdataadd977                   = BOSdata.new()
htfadd977.settings                 := SettingsHTFadd977
htfadd977.candles                  := candlesadd977
htfadd977.bosdata                  := bosdataadd977
var CandleSet htfadd978                     = CandleSet.new()
var CandleSettings SettingsHTFadd978        = CandleSettings.new(htf='978',htfint=978,max_memory=3)
var Candle[] candlesadd978                  = array.new<Candle>(0)
var BOSdata bosdataadd978                   = BOSdata.new()
htfadd978.settings                 := SettingsHTFadd978
htfadd978.candles                  := candlesadd978
htfadd978.bosdata                  := bosdataadd978
var CandleSet htfadd979                     = CandleSet.new()
var CandleSettings SettingsHTFadd979        = CandleSettings.new(htf='979',htfint=979,max_memory=3)
var Candle[] candlesadd979                  = array.new<Candle>(0)
var BOSdata bosdataadd979                   = BOSdata.new()
htfadd979.settings                 := SettingsHTFadd979
htfadd979.candles                  := candlesadd979
htfadd979.bosdata                  := bosdataadd979
var CandleSet htfadd980                     = CandleSet.new()
var CandleSettings SettingsHTFadd980        = CandleSettings.new(htf='980',htfint=980,max_memory=3)
var Candle[] candlesadd980                  = array.new<Candle>(0)
var BOSdata bosdataadd980                   = BOSdata.new()
htfadd980.settings                 := SettingsHTFadd980
htfadd980.candles                  := candlesadd980
htfadd980.bosdata                  := bosdataadd980
var CandleSet htfadd981                     = CandleSet.new()
var CandleSettings SettingsHTFadd981        = CandleSettings.new(htf='981',htfint=981,max_memory=3)
var Candle[] candlesadd981                  = array.new<Candle>(0)
var BOSdata bosdataadd981                   = BOSdata.new()
htfadd981.settings                 := SettingsHTFadd981
htfadd981.candles                  := candlesadd981
htfadd981.bosdata                  := bosdataadd981
var CandleSet htfadd982                     = CandleSet.new()
var CandleSettings SettingsHTFadd982        = CandleSettings.new(htf='982',htfint=982,max_memory=3)
var Candle[] candlesadd982                  = array.new<Candle>(0)
var BOSdata bosdataadd982                   = BOSdata.new()
htfadd982.settings                 := SettingsHTFadd982
htfadd982.candles                  := candlesadd982
htfadd982.bosdata                  := bosdataadd982
var CandleSet htfadd983                     = CandleSet.new()
var CandleSettings SettingsHTFadd983        = CandleSettings.new(htf='983',htfint=983,max_memory=3)
var Candle[] candlesadd983                  = array.new<Candle>(0)
var BOSdata bosdataadd983                   = BOSdata.new()
htfadd983.settings                 := SettingsHTFadd983
htfadd983.candles                  := candlesadd983
htfadd983.bosdata                  := bosdataadd983
var CandleSet htfadd984                     = CandleSet.new()
var CandleSettings SettingsHTFadd984        = CandleSettings.new(htf='984',htfint=984,max_memory=3)
var Candle[] candlesadd984                  = array.new<Candle>(0)
var BOSdata bosdataadd984                   = BOSdata.new()
htfadd984.settings                 := SettingsHTFadd984
htfadd984.candles                  := candlesadd984
htfadd984.bosdata                  := bosdataadd984
var CandleSet htfadd985                     = CandleSet.new()
var CandleSettings SettingsHTFadd985        = CandleSettings.new(htf='985',htfint=985,max_memory=3)
var Candle[] candlesadd985                  = array.new<Candle>(0)
var BOSdata bosdataadd985                   = BOSdata.new()
htfadd985.settings                 := SettingsHTFadd985
htfadd985.candles                  := candlesadd985
htfadd985.bosdata                  := bosdataadd985
var CandleSet htfadd986                     = CandleSet.new()
var CandleSettings SettingsHTFadd986        = CandleSettings.new(htf='986',htfint=986,max_memory=3)
var Candle[] candlesadd986                  = array.new<Candle>(0)
var BOSdata bosdataadd986                   = BOSdata.new()
htfadd986.settings                 := SettingsHTFadd986
htfadd986.candles                  := candlesadd986
htfadd986.bosdata                  := bosdataadd986
var CandleSet htfadd987                     = CandleSet.new()
var CandleSettings SettingsHTFadd987        = CandleSettings.new(htf='987',htfint=987,max_memory=3)
var Candle[] candlesadd987                  = array.new<Candle>(0)
var BOSdata bosdataadd987                   = BOSdata.new()
htfadd987.settings                 := SettingsHTFadd987
htfadd987.candles                  := candlesadd987
htfadd987.bosdata                  := bosdataadd987
var CandleSet htfadd988                     = CandleSet.new()
var CandleSettings SettingsHTFadd988        = CandleSettings.new(htf='988',htfint=988,max_memory=3)
var Candle[] candlesadd988                  = array.new<Candle>(0)
var BOSdata bosdataadd988                   = BOSdata.new()
htfadd988.settings                 := SettingsHTFadd988
htfadd988.candles                  := candlesadd988
htfadd988.bosdata                  := bosdataadd988
var CandleSet htfadd989                     = CandleSet.new()
var CandleSettings SettingsHTFadd989        = CandleSettings.new(htf='989',htfint=989,max_memory=3)
var Candle[] candlesadd989                  = array.new<Candle>(0)
var BOSdata bosdataadd989                   = BOSdata.new()
htfadd989.settings                 := SettingsHTFadd989
htfadd989.candles                  := candlesadd989
htfadd989.bosdata                  := bosdataadd989
var CandleSet htfadd990                     = CandleSet.new()
var CandleSettings SettingsHTFadd990        = CandleSettings.new(htf='990',htfint=990,max_memory=3)
var Candle[] candlesadd990                  = array.new<Candle>(0)
var BOSdata bosdataadd990                   = BOSdata.new()
htfadd990.settings                 := SettingsHTFadd990
htfadd990.candles                  := candlesadd990
htfadd990.bosdata                  := bosdataadd990

htfadd900.Monitor().BOSJudge()
htfadd901.Monitor().BOSJudge()
htfadd902.Monitor().BOSJudge()
htfadd903.Monitor().BOSJudge()
htfadd904.Monitor().BOSJudge()
htfadd905.Monitor().BOSJudge()
htfadd906.Monitor().BOSJudge()
htfadd907.Monitor().BOSJudge()
htfadd908.Monitor().BOSJudge()
htfadd909.Monitor().BOSJudge()
htfadd910.Monitor().BOSJudge()
htfadd911.Monitor().BOSJudge()
htfadd912.Monitor().BOSJudge()
htfadd913.Monitor().BOSJudge()
htfadd914.Monitor().BOSJudge()
htfadd915.Monitor().BOSJudge()
htfadd916.Monitor().BOSJudge()
htfadd917.Monitor().BOSJudge()
htfadd918.Monitor().BOSJudge()
htfadd919.Monitor().BOSJudge()
htfadd920.Monitor().BOSJudge()
htfadd921.Monitor().BOSJudge()
htfadd922.Monitor().BOSJudge()
htfadd923.Monitor().BOSJudge()
htfadd924.Monitor().BOSJudge()
htfadd925.Monitor().BOSJudge()
htfadd926.Monitor().BOSJudge()
htfadd927.Monitor().BOSJudge()
htfadd928.Monitor().BOSJudge()
htfadd929.Monitor().BOSJudge()
htfadd930.Monitor().BOSJudge()
htfadd931.Monitor().BOSJudge()
htfadd932.Monitor().BOSJudge()
htfadd933.Monitor().BOSJudge()
htfadd934.Monitor().BOSJudge()
htfadd935.Monitor().BOSJudge()
htfadd936.Monitor().BOSJudge()
htfadd937.Monitor().BOSJudge()
htfadd938.Monitor().BOSJudge()
htfadd939.Monitor().BOSJudge()
htfadd940.Monitor().BOSJudge()
htfadd941.Monitor().BOSJudge()
htfadd942.Monitor().BOSJudge()
htfadd943.Monitor().BOSJudge()
htfadd944.Monitor().BOSJudge()
htfadd945.Monitor().BOSJudge()
htfadd946.Monitor().BOSJudge()
htfadd947.Monitor().BOSJudge()
htfadd948.Monitor().BOSJudge()
htfadd949.Monitor().BOSJudge()
htfadd950.Monitor().BOSJudge()
htfadd951.Monitor().BOSJudge()
htfadd952.Monitor().BOSJudge()
htfadd953.Monitor().BOSJudge()
htfadd954.Monitor().BOSJudge()
htfadd955.Monitor().BOSJudge()
htfadd956.Monitor().BOSJudge()
htfadd957.Monitor().BOSJudge()
htfadd958.Monitor().BOSJudge()
htfadd959.Monitor().BOSJudge()
htfadd960.Monitor().BOSJudge()
htfadd961.Monitor().BOSJudge()
htfadd962.Monitor().BOSJudge()
htfadd963.Monitor().BOSJudge()
htfadd964.Monitor().BOSJudge()
htfadd965.Monitor().BOSJudge()
htfadd966.Monitor().BOSJudge()
htfadd967.Monitor().BOSJudge()
htfadd968.Monitor().BOSJudge()
htfadd969.Monitor().BOSJudge()
htfadd970.Monitor().BOSJudge()
htfadd971.Monitor().BOSJudge()
htfadd972.Monitor().BOSJudge()
htfadd973.Monitor().BOSJudge()
htfadd974.Monitor().BOSJudge()
htfadd975.Monitor().BOSJudge()
htfadd976.Monitor().BOSJudge()
htfadd977.Monitor().BOSJudge()
htfadd978.Monitor().BOSJudge()
htfadd979.Monitor().BOSJudge()
htfadd980.Monitor().BOSJudge()
htfadd981.Monitor().BOSJudge()
htfadd982.Monitor().BOSJudge()
htfadd983.Monitor().BOSJudge()
htfadd984.Monitor().BOSJudge()
htfadd985.Monitor().BOSJudge()
htfadd986.Monitor().BOSJudge()
htfadd987.Monitor().BOSJudge()
htfadd988.Monitor().BOSJudge()
htfadd989.Monitor().BOSJudge()
htfadd990.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd900)
    LowestsbuSet(lowestsbu, htfadd900)
    HighestsbdSet(highestsbd, htfadd901)
    LowestsbuSet(lowestsbu, htfadd901)
    HighestsbdSet(highestsbd, htfadd902)
    LowestsbuSet(lowestsbu, htfadd902)
    HighestsbdSet(highestsbd, htfadd903)
    LowestsbuSet(lowestsbu, htfadd903)
    HighestsbdSet(highestsbd, htfadd904)
    LowestsbuSet(lowestsbu, htfadd904)
    HighestsbdSet(highestsbd, htfadd905)
    LowestsbuSet(lowestsbu, htfadd905)
    HighestsbdSet(highestsbd, htfadd906)
    LowestsbuSet(lowestsbu, htfadd906)
    HighestsbdSet(highestsbd, htfadd907)
    LowestsbuSet(lowestsbu, htfadd907)
    HighestsbdSet(highestsbd, htfadd908)
    LowestsbuSet(lowestsbu, htfadd908)
    HighestsbdSet(highestsbd, htfadd909)
    LowestsbuSet(lowestsbu, htfadd909)
    HighestsbdSet(highestsbd, htfadd910)
    LowestsbuSet(lowestsbu, htfadd910)
    HighestsbdSet(highestsbd, htfadd911)
    LowestsbuSet(lowestsbu, htfadd911)
    HighestsbdSet(highestsbd, htfadd912)
    LowestsbuSet(lowestsbu, htfadd912)
    HighestsbdSet(highestsbd, htfadd913)
    LowestsbuSet(lowestsbu, htfadd913)
    HighestsbdSet(highestsbd, htfadd914)
    LowestsbuSet(lowestsbu, htfadd914)
    HighestsbdSet(highestsbd, htfadd915)
    LowestsbuSet(lowestsbu, htfadd915)
    HighestsbdSet(highestsbd, htfadd916)
    LowestsbuSet(lowestsbu, htfadd916)
    HighestsbdSet(highestsbd, htfadd917)
    LowestsbuSet(lowestsbu, htfadd917)
    HighestsbdSet(highestsbd, htfadd918)
    LowestsbuSet(lowestsbu, htfadd918)
    HighestsbdSet(highestsbd, htfadd919)
    LowestsbuSet(lowestsbu, htfadd919)
    HighestsbdSet(highestsbd, htfadd920)
    LowestsbuSet(lowestsbu, htfadd920)
    HighestsbdSet(highestsbd, htfadd921)
    LowestsbuSet(lowestsbu, htfadd921)
    HighestsbdSet(highestsbd, htfadd922)
    LowestsbuSet(lowestsbu, htfadd922)
    HighestsbdSet(highestsbd, htfadd923)
    LowestsbuSet(lowestsbu, htfadd923)
    HighestsbdSet(highestsbd, htfadd924)
    LowestsbuSet(lowestsbu, htfadd924)
    HighestsbdSet(highestsbd, htfadd925)
    LowestsbuSet(lowestsbu, htfadd925)
    HighestsbdSet(highestsbd, htfadd926)
    LowestsbuSet(lowestsbu, htfadd926)
    HighestsbdSet(highestsbd, htfadd927)
    LowestsbuSet(lowestsbu, htfadd927)
    HighestsbdSet(highestsbd, htfadd928)
    LowestsbuSet(lowestsbu, htfadd928)
    HighestsbdSet(highestsbd, htfadd929)
    LowestsbuSet(lowestsbu, htfadd929)
    HighestsbdSet(highestsbd, htfadd930)
    LowestsbuSet(lowestsbu, htfadd930)
    HighestsbdSet(highestsbd, htfadd931)
    LowestsbuSet(lowestsbu, htfadd931)
    HighestsbdSet(highestsbd, htfadd932)
    LowestsbuSet(lowestsbu, htfadd932)
    HighestsbdSet(highestsbd, htfadd933)
    LowestsbuSet(lowestsbu, htfadd933)
    HighestsbdSet(highestsbd, htfadd934)
    LowestsbuSet(lowestsbu, htfadd934)
    HighestsbdSet(highestsbd, htfadd935)
    LowestsbuSet(lowestsbu, htfadd935)
    HighestsbdSet(highestsbd, htfadd936)
    LowestsbuSet(lowestsbu, htfadd936)
    HighestsbdSet(highestsbd, htfadd937)
    LowestsbuSet(lowestsbu, htfadd937)
    HighestsbdSet(highestsbd, htfadd938)
    LowestsbuSet(lowestsbu, htfadd938)
    HighestsbdSet(highestsbd, htfadd939)
    LowestsbuSet(lowestsbu, htfadd939)
    HighestsbdSet(highestsbd, htfadd940)
    LowestsbuSet(lowestsbu, htfadd940)
    HighestsbdSet(highestsbd, htfadd941)
    LowestsbuSet(lowestsbu, htfadd941)
    HighestsbdSet(highestsbd, htfadd942)
    LowestsbuSet(lowestsbu, htfadd942)
    HighestsbdSet(highestsbd, htfadd943)
    LowestsbuSet(lowestsbu, htfadd943)
    HighestsbdSet(highestsbd, htfadd944)
    LowestsbuSet(lowestsbu, htfadd944)
    HighestsbdSet(highestsbd, htfadd945)
    LowestsbuSet(lowestsbu, htfadd945)
    HighestsbdSet(highestsbd, htfadd946)
    LowestsbuSet(lowestsbu, htfadd946)
    HighestsbdSet(highestsbd, htfadd947)
    LowestsbuSet(lowestsbu, htfadd947)
    HighestsbdSet(highestsbd, htfadd948)
    LowestsbuSet(lowestsbu, htfadd948)
    HighestsbdSet(highestsbd, htfadd949)
    LowestsbuSet(lowestsbu, htfadd949)
    HighestsbdSet(highestsbd, htfadd950)
    LowestsbuSet(lowestsbu, htfadd950)
    HighestsbdSet(highestsbd, htfadd951)
    LowestsbuSet(lowestsbu, htfadd951)
    HighestsbdSet(highestsbd, htfadd952)
    LowestsbuSet(lowestsbu, htfadd952)
    HighestsbdSet(highestsbd, htfadd953)
    LowestsbuSet(lowestsbu, htfadd953)
    HighestsbdSet(highestsbd, htfadd954)
    LowestsbuSet(lowestsbu, htfadd954)
    HighestsbdSet(highestsbd, htfadd955)
    LowestsbuSet(lowestsbu, htfadd955)
    HighestsbdSet(highestsbd, htfadd956)
    LowestsbuSet(lowestsbu, htfadd956)
    HighestsbdSet(highestsbd, htfadd957)
    LowestsbuSet(lowestsbu, htfadd957)
    HighestsbdSet(highestsbd, htfadd958)
    LowestsbuSet(lowestsbu, htfadd958)
    HighestsbdSet(highestsbd, htfadd959)
    LowestsbuSet(lowestsbu, htfadd959)
    HighestsbdSet(highestsbd, htfadd960)
    LowestsbuSet(lowestsbu, htfadd960)
    HighestsbdSet(highestsbd, htfadd961)
    LowestsbuSet(lowestsbu, htfadd961)
    HighestsbdSet(highestsbd, htfadd962)
    LowestsbuSet(lowestsbu, htfadd962)
    HighestsbdSet(highestsbd, htfadd963)
    LowestsbuSet(lowestsbu, htfadd963)
    HighestsbdSet(highestsbd, htfadd964)
    LowestsbuSet(lowestsbu, htfadd964)
    HighestsbdSet(highestsbd, htfadd965)
    LowestsbuSet(lowestsbu, htfadd965)
    HighestsbdSet(highestsbd, htfadd966)
    LowestsbuSet(lowestsbu, htfadd966)
    HighestsbdSet(highestsbd, htfadd967)
    LowestsbuSet(lowestsbu, htfadd967)
    HighestsbdSet(highestsbd, htfadd968)
    LowestsbuSet(lowestsbu, htfadd968)
    HighestsbdSet(highestsbd, htfadd969)
    LowestsbuSet(lowestsbu, htfadd969)
    HighestsbdSet(highestsbd, htfadd970)
    LowestsbuSet(lowestsbu, htfadd970)
    HighestsbdSet(highestsbd, htfadd971)
    LowestsbuSet(lowestsbu, htfadd971)
    HighestsbdSet(highestsbd, htfadd972)
    LowestsbuSet(lowestsbu, htfadd972)
    HighestsbdSet(highestsbd, htfadd973)
    LowestsbuSet(lowestsbu, htfadd973)
    HighestsbdSet(highestsbd, htfadd974)
    LowestsbuSet(lowestsbu, htfadd974)
    HighestsbdSet(highestsbd, htfadd975)
    LowestsbuSet(lowestsbu, htfadd975)
    HighestsbdSet(highestsbd, htfadd976)
    LowestsbuSet(lowestsbu, htfadd976)
    HighestsbdSet(highestsbd, htfadd977)
    LowestsbuSet(lowestsbu, htfadd977)
    HighestsbdSet(highestsbd, htfadd978)
    LowestsbuSet(lowestsbu, htfadd978)
    HighestsbdSet(highestsbd, htfadd979)
    LowestsbuSet(lowestsbu, htfadd979)
    HighestsbdSet(highestsbd, htfadd980)
    LowestsbuSet(lowestsbu, htfadd980)
    HighestsbdSet(highestsbd, htfadd981)
    LowestsbuSet(lowestsbu, htfadd981)
    HighestsbdSet(highestsbd, htfadd982)
    LowestsbuSet(lowestsbu, htfadd982)
    HighestsbdSet(highestsbd, htfadd983)
    LowestsbuSet(lowestsbu, htfadd983)
    HighestsbdSet(highestsbd, htfadd984)
    LowestsbuSet(lowestsbu, htfadd984)
    HighestsbdSet(highestsbd, htfadd985)
    LowestsbuSet(lowestsbu, htfadd985)
    HighestsbdSet(highestsbd, htfadd986)
    LowestsbuSet(lowestsbu, htfadd986)
    HighestsbdSet(highestsbd, htfadd987)
    LowestsbuSet(lowestsbu, htfadd987)
    HighestsbdSet(highestsbd, htfadd988)
    LowestsbuSet(lowestsbu, htfadd988)
    HighestsbdSet(highestsbd, htfadd989)
    LowestsbuSet(lowestsbu, htfadd989)
    HighestsbdSet(highestsbd, htfadd990)
    LowestsbuSet(lowestsbu, htfadd990)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd900).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd901).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd902).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd903).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd904).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd905).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd906).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd907).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd908).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd909).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd910).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd911).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd912).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd913).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd914).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd915).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd916).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd917).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd918).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd919).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd920).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd921).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd922).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd923).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd924).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd925).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd926).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd927).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd928).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd929).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd930).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd931).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd932).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd933).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd934).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd935).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd936).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd937).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd938).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd939).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd940).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd941).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd942).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd943).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd944).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd945).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd946).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd947).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd948).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd949).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd950).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd951).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd952).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd953).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd954).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd955).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd956).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd957).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd958).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd959).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd960).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd961).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd962).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd963).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd964).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd965).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd966).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd967).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd968).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd969).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd970).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd971).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd972).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd973).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd974).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd975).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd976).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd977).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd978).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd979).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd980).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd981).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd982).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd983).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd984).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd985).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd986).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd987).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd988).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd989).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd990).Monitor_Est().BOSJudge()
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


