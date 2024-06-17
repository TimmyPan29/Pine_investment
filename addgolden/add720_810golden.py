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
var CandleSet htfadd720                     = CandleSet.new()
var CandleSettings SettingsHTFadd720        = CandleSettings.new(htf='720',htfint=720,max_memory=3)
var Candle[] candlesadd720                  = array.new<Candle>(0)
var BOSdata bosdataadd720                   = BOSdata.new()
htfadd720.settings                 := SettingsHTFadd720
htfadd720.candles                  := candlesadd720
htfadd720.bosdata                  := bosdataadd720
var CandleSet htfadd721                     = CandleSet.new()
var CandleSettings SettingsHTFadd721        = CandleSettings.new(htf='721',htfint=721,max_memory=3)
var Candle[] candlesadd721                  = array.new<Candle>(0)
var BOSdata bosdataadd721                   = BOSdata.new()
htfadd721.settings                 := SettingsHTFadd721
htfadd721.candles                  := candlesadd721
htfadd721.bosdata                  := bosdataadd721
var CandleSet htfadd722                     = CandleSet.new()
var CandleSettings SettingsHTFadd722        = CandleSettings.new(htf='722',htfint=722,max_memory=3)
var Candle[] candlesadd722                  = array.new<Candle>(0)
var BOSdata bosdataadd722                   = BOSdata.new()
htfadd722.settings                 := SettingsHTFadd722
htfadd722.candles                  := candlesadd722
htfadd722.bosdata                  := bosdataadd722
var CandleSet htfadd723                     = CandleSet.new()
var CandleSettings SettingsHTFadd723        = CandleSettings.new(htf='723',htfint=723,max_memory=3)
var Candle[] candlesadd723                  = array.new<Candle>(0)
var BOSdata bosdataadd723                   = BOSdata.new()
htfadd723.settings                 := SettingsHTFadd723
htfadd723.candles                  := candlesadd723
htfadd723.bosdata                  := bosdataadd723
var CandleSet htfadd724                     = CandleSet.new()
var CandleSettings SettingsHTFadd724        = CandleSettings.new(htf='724',htfint=724,max_memory=3)
var Candle[] candlesadd724                  = array.new<Candle>(0)
var BOSdata bosdataadd724                   = BOSdata.new()
htfadd724.settings                 := SettingsHTFadd724
htfadd724.candles                  := candlesadd724
htfadd724.bosdata                  := bosdataadd724
var CandleSet htfadd725                     = CandleSet.new()
var CandleSettings SettingsHTFadd725        = CandleSettings.new(htf='725',htfint=725,max_memory=3)
var Candle[] candlesadd725                  = array.new<Candle>(0)
var BOSdata bosdataadd725                   = BOSdata.new()
htfadd725.settings                 := SettingsHTFadd725
htfadd725.candles                  := candlesadd725
htfadd725.bosdata                  := bosdataadd725
var CandleSet htfadd726                     = CandleSet.new()
var CandleSettings SettingsHTFadd726        = CandleSettings.new(htf='726',htfint=726,max_memory=3)
var Candle[] candlesadd726                  = array.new<Candle>(0)
var BOSdata bosdataadd726                   = BOSdata.new()
htfadd726.settings                 := SettingsHTFadd726
htfadd726.candles                  := candlesadd726
htfadd726.bosdata                  := bosdataadd726
var CandleSet htfadd727                     = CandleSet.new()
var CandleSettings SettingsHTFadd727        = CandleSettings.new(htf='727',htfint=727,max_memory=3)
var Candle[] candlesadd727                  = array.new<Candle>(0)
var BOSdata bosdataadd727                   = BOSdata.new()
htfadd727.settings                 := SettingsHTFadd727
htfadd727.candles                  := candlesadd727
htfadd727.bosdata                  := bosdataadd727
var CandleSet htfadd728                     = CandleSet.new()
var CandleSettings SettingsHTFadd728        = CandleSettings.new(htf='728',htfint=728,max_memory=3)
var Candle[] candlesadd728                  = array.new<Candle>(0)
var BOSdata bosdataadd728                   = BOSdata.new()
htfadd728.settings                 := SettingsHTFadd728
htfadd728.candles                  := candlesadd728
htfadd728.bosdata                  := bosdataadd728
var CandleSet htfadd729                     = CandleSet.new()
var CandleSettings SettingsHTFadd729        = CandleSettings.new(htf='729',htfint=729,max_memory=3)
var Candle[] candlesadd729                  = array.new<Candle>(0)
var BOSdata bosdataadd729                   = BOSdata.new()
htfadd729.settings                 := SettingsHTFadd729
htfadd729.candles                  := candlesadd729
htfadd729.bosdata                  := bosdataadd729
var CandleSet htfadd730                     = CandleSet.new()
var CandleSettings SettingsHTFadd730        = CandleSettings.new(htf='730',htfint=730,max_memory=3)
var Candle[] candlesadd730                  = array.new<Candle>(0)
var BOSdata bosdataadd730                   = BOSdata.new()
htfadd730.settings                 := SettingsHTFadd730
htfadd730.candles                  := candlesadd730
htfadd730.bosdata                  := bosdataadd730
var CandleSet htfadd731                     = CandleSet.new()
var CandleSettings SettingsHTFadd731        = CandleSettings.new(htf='731',htfint=731,max_memory=3)
var Candle[] candlesadd731                  = array.new<Candle>(0)
var BOSdata bosdataadd731                   = BOSdata.new()
htfadd731.settings                 := SettingsHTFadd731
htfadd731.candles                  := candlesadd731
htfadd731.bosdata                  := bosdataadd731
var CandleSet htfadd732                     = CandleSet.new()
var CandleSettings SettingsHTFadd732        = CandleSettings.new(htf='732',htfint=732,max_memory=3)
var Candle[] candlesadd732                  = array.new<Candle>(0)
var BOSdata bosdataadd732                   = BOSdata.new()
htfadd732.settings                 := SettingsHTFadd732
htfadd732.candles                  := candlesadd732
htfadd732.bosdata                  := bosdataadd732
var CandleSet htfadd733                     = CandleSet.new()
var CandleSettings SettingsHTFadd733        = CandleSettings.new(htf='733',htfint=733,max_memory=3)
var Candle[] candlesadd733                  = array.new<Candle>(0)
var BOSdata bosdataadd733                   = BOSdata.new()
htfadd733.settings                 := SettingsHTFadd733
htfadd733.candles                  := candlesadd733
htfadd733.bosdata                  := bosdataadd733
var CandleSet htfadd734                     = CandleSet.new()
var CandleSettings SettingsHTFadd734        = CandleSettings.new(htf='734',htfint=734,max_memory=3)
var Candle[] candlesadd734                  = array.new<Candle>(0)
var BOSdata bosdataadd734                   = BOSdata.new()
htfadd734.settings                 := SettingsHTFadd734
htfadd734.candles                  := candlesadd734
htfadd734.bosdata                  := bosdataadd734
var CandleSet htfadd735                     = CandleSet.new()
var CandleSettings SettingsHTFadd735        = CandleSettings.new(htf='735',htfint=735,max_memory=3)
var Candle[] candlesadd735                  = array.new<Candle>(0)
var BOSdata bosdataadd735                   = BOSdata.new()
htfadd735.settings                 := SettingsHTFadd735
htfadd735.candles                  := candlesadd735
htfadd735.bosdata                  := bosdataadd735
var CandleSet htfadd736                     = CandleSet.new()
var CandleSettings SettingsHTFadd736        = CandleSettings.new(htf='736',htfint=736,max_memory=3)
var Candle[] candlesadd736                  = array.new<Candle>(0)
var BOSdata bosdataadd736                   = BOSdata.new()
htfadd736.settings                 := SettingsHTFadd736
htfadd736.candles                  := candlesadd736
htfadd736.bosdata                  := bosdataadd736
var CandleSet htfadd737                     = CandleSet.new()
var CandleSettings SettingsHTFadd737        = CandleSettings.new(htf='737',htfint=737,max_memory=3)
var Candle[] candlesadd737                  = array.new<Candle>(0)
var BOSdata bosdataadd737                   = BOSdata.new()
htfadd737.settings                 := SettingsHTFadd737
htfadd737.candles                  := candlesadd737
htfadd737.bosdata                  := bosdataadd737
var CandleSet htfadd738                     = CandleSet.new()
var CandleSettings SettingsHTFadd738        = CandleSettings.new(htf='738',htfint=738,max_memory=3)
var Candle[] candlesadd738                  = array.new<Candle>(0)
var BOSdata bosdataadd738                   = BOSdata.new()
htfadd738.settings                 := SettingsHTFadd738
htfadd738.candles                  := candlesadd738
htfadd738.bosdata                  := bosdataadd738
var CandleSet htfadd739                     = CandleSet.new()
var CandleSettings SettingsHTFadd739        = CandleSettings.new(htf='739',htfint=739,max_memory=3)
var Candle[] candlesadd739                  = array.new<Candle>(0)
var BOSdata bosdataadd739                   = BOSdata.new()
htfadd739.settings                 := SettingsHTFadd739
htfadd739.candles                  := candlesadd739
htfadd739.bosdata                  := bosdataadd739
var CandleSet htfadd740                     = CandleSet.new()
var CandleSettings SettingsHTFadd740        = CandleSettings.new(htf='740',htfint=740,max_memory=3)
var Candle[] candlesadd740                  = array.new<Candle>(0)
var BOSdata bosdataadd740                   = BOSdata.new()
htfadd740.settings                 := SettingsHTFadd740
htfadd740.candles                  := candlesadd740
htfadd740.bosdata                  := bosdataadd740
var CandleSet htfadd741                     = CandleSet.new()
var CandleSettings SettingsHTFadd741        = CandleSettings.new(htf='741',htfint=741,max_memory=3)
var Candle[] candlesadd741                  = array.new<Candle>(0)
var BOSdata bosdataadd741                   = BOSdata.new()
htfadd741.settings                 := SettingsHTFadd741
htfadd741.candles                  := candlesadd741
htfadd741.bosdata                  := bosdataadd741
var CandleSet htfadd742                     = CandleSet.new()
var CandleSettings SettingsHTFadd742        = CandleSettings.new(htf='742',htfint=742,max_memory=3)
var Candle[] candlesadd742                  = array.new<Candle>(0)
var BOSdata bosdataadd742                   = BOSdata.new()
htfadd742.settings                 := SettingsHTFadd742
htfadd742.candles                  := candlesadd742
htfadd742.bosdata                  := bosdataadd742
var CandleSet htfadd743                     = CandleSet.new()
var CandleSettings SettingsHTFadd743        = CandleSettings.new(htf='743',htfint=743,max_memory=3)
var Candle[] candlesadd743                  = array.new<Candle>(0)
var BOSdata bosdataadd743                   = BOSdata.new()
htfadd743.settings                 := SettingsHTFadd743
htfadd743.candles                  := candlesadd743
htfadd743.bosdata                  := bosdataadd743
var CandleSet htfadd744                     = CandleSet.new()
var CandleSettings SettingsHTFadd744        = CandleSettings.new(htf='744',htfint=744,max_memory=3)
var Candle[] candlesadd744                  = array.new<Candle>(0)
var BOSdata bosdataadd744                   = BOSdata.new()
htfadd744.settings                 := SettingsHTFadd744
htfadd744.candles                  := candlesadd744
htfadd744.bosdata                  := bosdataadd744
var CandleSet htfadd745                     = CandleSet.new()
var CandleSettings SettingsHTFadd745        = CandleSettings.new(htf='745',htfint=745,max_memory=3)
var Candle[] candlesadd745                  = array.new<Candle>(0)
var BOSdata bosdataadd745                   = BOSdata.new()
htfadd745.settings                 := SettingsHTFadd745
htfadd745.candles                  := candlesadd745
htfadd745.bosdata                  := bosdataadd745
var CandleSet htfadd746                     = CandleSet.new()
var CandleSettings SettingsHTFadd746        = CandleSettings.new(htf='746',htfint=746,max_memory=3)
var Candle[] candlesadd746                  = array.new<Candle>(0)
var BOSdata bosdataadd746                   = BOSdata.new()
htfadd746.settings                 := SettingsHTFadd746
htfadd746.candles                  := candlesadd746
htfadd746.bosdata                  := bosdataadd746
var CandleSet htfadd747                     = CandleSet.new()
var CandleSettings SettingsHTFadd747        = CandleSettings.new(htf='747',htfint=747,max_memory=3)
var Candle[] candlesadd747                  = array.new<Candle>(0)
var BOSdata bosdataadd747                   = BOSdata.new()
htfadd747.settings                 := SettingsHTFadd747
htfadd747.candles                  := candlesadd747
htfadd747.bosdata                  := bosdataadd747
var CandleSet htfadd748                     = CandleSet.new()
var CandleSettings SettingsHTFadd748        = CandleSettings.new(htf='748',htfint=748,max_memory=3)
var Candle[] candlesadd748                  = array.new<Candle>(0)
var BOSdata bosdataadd748                   = BOSdata.new()
htfadd748.settings                 := SettingsHTFadd748
htfadd748.candles                  := candlesadd748
htfadd748.bosdata                  := bosdataadd748
var CandleSet htfadd749                     = CandleSet.new()
var CandleSettings SettingsHTFadd749        = CandleSettings.new(htf='749',htfint=749,max_memory=3)
var Candle[] candlesadd749                  = array.new<Candle>(0)
var BOSdata bosdataadd749                   = BOSdata.new()
htfadd749.settings                 := SettingsHTFadd749
htfadd749.candles                  := candlesadd749
htfadd749.bosdata                  := bosdataadd749
var CandleSet htfadd750                     = CandleSet.new()
var CandleSettings SettingsHTFadd750        = CandleSettings.new(htf='750',htfint=750,max_memory=3)
var Candle[] candlesadd750                  = array.new<Candle>(0)
var BOSdata bosdataadd750                   = BOSdata.new()
htfadd750.settings                 := SettingsHTFadd750
htfadd750.candles                  := candlesadd750
htfadd750.bosdata                  := bosdataadd750
var CandleSet htfadd751                     = CandleSet.new()
var CandleSettings SettingsHTFadd751        = CandleSettings.new(htf='751',htfint=751,max_memory=3)
var Candle[] candlesadd751                  = array.new<Candle>(0)
var BOSdata bosdataadd751                   = BOSdata.new()
htfadd751.settings                 := SettingsHTFadd751
htfadd751.candles                  := candlesadd751
htfadd751.bosdata                  := bosdataadd751
var CandleSet htfadd752                     = CandleSet.new()
var CandleSettings SettingsHTFadd752        = CandleSettings.new(htf='752',htfint=752,max_memory=3)
var Candle[] candlesadd752                  = array.new<Candle>(0)
var BOSdata bosdataadd752                   = BOSdata.new()
htfadd752.settings                 := SettingsHTFadd752
htfadd752.candles                  := candlesadd752
htfadd752.bosdata                  := bosdataadd752
var CandleSet htfadd753                     = CandleSet.new()
var CandleSettings SettingsHTFadd753        = CandleSettings.new(htf='753',htfint=753,max_memory=3)
var Candle[] candlesadd753                  = array.new<Candle>(0)
var BOSdata bosdataadd753                   = BOSdata.new()
htfadd753.settings                 := SettingsHTFadd753
htfadd753.candles                  := candlesadd753
htfadd753.bosdata                  := bosdataadd753
var CandleSet htfadd754                     = CandleSet.new()
var CandleSettings SettingsHTFadd754        = CandleSettings.new(htf='754',htfint=754,max_memory=3)
var Candle[] candlesadd754                  = array.new<Candle>(0)
var BOSdata bosdataadd754                   = BOSdata.new()
htfadd754.settings                 := SettingsHTFadd754
htfadd754.candles                  := candlesadd754
htfadd754.bosdata                  := bosdataadd754
var CandleSet htfadd755                     = CandleSet.new()
var CandleSettings SettingsHTFadd755        = CandleSettings.new(htf='755',htfint=755,max_memory=3)
var Candle[] candlesadd755                  = array.new<Candle>(0)
var BOSdata bosdataadd755                   = BOSdata.new()
htfadd755.settings                 := SettingsHTFadd755
htfadd755.candles                  := candlesadd755
htfadd755.bosdata                  := bosdataadd755
var CandleSet htfadd756                     = CandleSet.new()
var CandleSettings SettingsHTFadd756        = CandleSettings.new(htf='756',htfint=756,max_memory=3)
var Candle[] candlesadd756                  = array.new<Candle>(0)
var BOSdata bosdataadd756                   = BOSdata.new()
htfadd756.settings                 := SettingsHTFadd756
htfadd756.candles                  := candlesadd756
htfadd756.bosdata                  := bosdataadd756
var CandleSet htfadd757                     = CandleSet.new()
var CandleSettings SettingsHTFadd757        = CandleSettings.new(htf='757',htfint=757,max_memory=3)
var Candle[] candlesadd757                  = array.new<Candle>(0)
var BOSdata bosdataadd757                   = BOSdata.new()
htfadd757.settings                 := SettingsHTFadd757
htfadd757.candles                  := candlesadd757
htfadd757.bosdata                  := bosdataadd757
var CandleSet htfadd758                     = CandleSet.new()
var CandleSettings SettingsHTFadd758        = CandleSettings.new(htf='758',htfint=758,max_memory=3)
var Candle[] candlesadd758                  = array.new<Candle>(0)
var BOSdata bosdataadd758                   = BOSdata.new()
htfadd758.settings                 := SettingsHTFadd758
htfadd758.candles                  := candlesadd758
htfadd758.bosdata                  := bosdataadd758
var CandleSet htfadd759                     = CandleSet.new()
var CandleSettings SettingsHTFadd759        = CandleSettings.new(htf='759',htfint=759,max_memory=3)
var Candle[] candlesadd759                  = array.new<Candle>(0)
var BOSdata bosdataadd759                   = BOSdata.new()
htfadd759.settings                 := SettingsHTFadd759
htfadd759.candles                  := candlesadd759
htfadd759.bosdata                  := bosdataadd759
var CandleSet htfadd760                     = CandleSet.new()
var CandleSettings SettingsHTFadd760        = CandleSettings.new(htf='760',htfint=760,max_memory=3)
var Candle[] candlesadd760                  = array.new<Candle>(0)
var BOSdata bosdataadd760                   = BOSdata.new()
htfadd760.settings                 := SettingsHTFadd760
htfadd760.candles                  := candlesadd760
htfadd760.bosdata                  := bosdataadd760
var CandleSet htfadd761                     = CandleSet.new()
var CandleSettings SettingsHTFadd761        = CandleSettings.new(htf='761',htfint=761,max_memory=3)
var Candle[] candlesadd761                  = array.new<Candle>(0)
var BOSdata bosdataadd761                   = BOSdata.new()
htfadd761.settings                 := SettingsHTFadd761
htfadd761.candles                  := candlesadd761
htfadd761.bosdata                  := bosdataadd761
var CandleSet htfadd762                     = CandleSet.new()
var CandleSettings SettingsHTFadd762        = CandleSettings.new(htf='762',htfint=762,max_memory=3)
var Candle[] candlesadd762                  = array.new<Candle>(0)
var BOSdata bosdataadd762                   = BOSdata.new()
htfadd762.settings                 := SettingsHTFadd762
htfadd762.candles                  := candlesadd762
htfadd762.bosdata                  := bosdataadd762
var CandleSet htfadd763                     = CandleSet.new()
var CandleSettings SettingsHTFadd763        = CandleSettings.new(htf='763',htfint=763,max_memory=3)
var Candle[] candlesadd763                  = array.new<Candle>(0)
var BOSdata bosdataadd763                   = BOSdata.new()
htfadd763.settings                 := SettingsHTFadd763
htfadd763.candles                  := candlesadd763
htfadd763.bosdata                  := bosdataadd763
var CandleSet htfadd764                     = CandleSet.new()
var CandleSettings SettingsHTFadd764        = CandleSettings.new(htf='764',htfint=764,max_memory=3)
var Candle[] candlesadd764                  = array.new<Candle>(0)
var BOSdata bosdataadd764                   = BOSdata.new()
htfadd764.settings                 := SettingsHTFadd764
htfadd764.candles                  := candlesadd764
htfadd764.bosdata                  := bosdataadd764
var CandleSet htfadd765                     = CandleSet.new()
var CandleSettings SettingsHTFadd765        = CandleSettings.new(htf='765',htfint=765,max_memory=3)
var Candle[] candlesadd765                  = array.new<Candle>(0)
var BOSdata bosdataadd765                   = BOSdata.new()
htfadd765.settings                 := SettingsHTFadd765
htfadd765.candles                  := candlesadd765
htfadd765.bosdata                  := bosdataadd765
var CandleSet htfadd766                     = CandleSet.new()
var CandleSettings SettingsHTFadd766        = CandleSettings.new(htf='766',htfint=766,max_memory=3)
var Candle[] candlesadd766                  = array.new<Candle>(0)
var BOSdata bosdataadd766                   = BOSdata.new()
htfadd766.settings                 := SettingsHTFadd766
htfadd766.candles                  := candlesadd766
htfadd766.bosdata                  := bosdataadd766
var CandleSet htfadd767                     = CandleSet.new()
var CandleSettings SettingsHTFadd767        = CandleSettings.new(htf='767',htfint=767,max_memory=3)
var Candle[] candlesadd767                  = array.new<Candle>(0)
var BOSdata bosdataadd767                   = BOSdata.new()
htfadd767.settings                 := SettingsHTFadd767
htfadd767.candles                  := candlesadd767
htfadd767.bosdata                  := bosdataadd767
var CandleSet htfadd768                     = CandleSet.new()
var CandleSettings SettingsHTFadd768        = CandleSettings.new(htf='768',htfint=768,max_memory=3)
var Candle[] candlesadd768                  = array.new<Candle>(0)
var BOSdata bosdataadd768                   = BOSdata.new()
htfadd768.settings                 := SettingsHTFadd768
htfadd768.candles                  := candlesadd768
htfadd768.bosdata                  := bosdataadd768
var CandleSet htfadd769                     = CandleSet.new()
var CandleSettings SettingsHTFadd769        = CandleSettings.new(htf='769',htfint=769,max_memory=3)
var Candle[] candlesadd769                  = array.new<Candle>(0)
var BOSdata bosdataadd769                   = BOSdata.new()
htfadd769.settings                 := SettingsHTFadd769
htfadd769.candles                  := candlesadd769
htfadd769.bosdata                  := bosdataadd769
var CandleSet htfadd770                     = CandleSet.new()
var CandleSettings SettingsHTFadd770        = CandleSettings.new(htf='770',htfint=770,max_memory=3)
var Candle[] candlesadd770                  = array.new<Candle>(0)
var BOSdata bosdataadd770                   = BOSdata.new()
htfadd770.settings                 := SettingsHTFadd770
htfadd770.candles                  := candlesadd770
htfadd770.bosdata                  := bosdataadd770
var CandleSet htfadd771                     = CandleSet.new()
var CandleSettings SettingsHTFadd771        = CandleSettings.new(htf='771',htfint=771,max_memory=3)
var Candle[] candlesadd771                  = array.new<Candle>(0)
var BOSdata bosdataadd771                   = BOSdata.new()
htfadd771.settings                 := SettingsHTFadd771
htfadd771.candles                  := candlesadd771
htfadd771.bosdata                  := bosdataadd771
var CandleSet htfadd772                     = CandleSet.new()
var CandleSettings SettingsHTFadd772        = CandleSettings.new(htf='772',htfint=772,max_memory=3)
var Candle[] candlesadd772                  = array.new<Candle>(0)
var BOSdata bosdataadd772                   = BOSdata.new()
htfadd772.settings                 := SettingsHTFadd772
htfadd772.candles                  := candlesadd772
htfadd772.bosdata                  := bosdataadd772
var CandleSet htfadd773                     = CandleSet.new()
var CandleSettings SettingsHTFadd773        = CandleSettings.new(htf='773',htfint=773,max_memory=3)
var Candle[] candlesadd773                  = array.new<Candle>(0)
var BOSdata bosdataadd773                   = BOSdata.new()
htfadd773.settings                 := SettingsHTFadd773
htfadd773.candles                  := candlesadd773
htfadd773.bosdata                  := bosdataadd773
var CandleSet htfadd774                     = CandleSet.new()
var CandleSettings SettingsHTFadd774        = CandleSettings.new(htf='774',htfint=774,max_memory=3)
var Candle[] candlesadd774                  = array.new<Candle>(0)
var BOSdata bosdataadd774                   = BOSdata.new()
htfadd774.settings                 := SettingsHTFadd774
htfadd774.candles                  := candlesadd774
htfadd774.bosdata                  := bosdataadd774
var CandleSet htfadd775                     = CandleSet.new()
var CandleSettings SettingsHTFadd775        = CandleSettings.new(htf='775',htfint=775,max_memory=3)
var Candle[] candlesadd775                  = array.new<Candle>(0)
var BOSdata bosdataadd775                   = BOSdata.new()
htfadd775.settings                 := SettingsHTFadd775
htfadd775.candles                  := candlesadd775
htfadd775.bosdata                  := bosdataadd775
var CandleSet htfadd776                     = CandleSet.new()
var CandleSettings SettingsHTFadd776        = CandleSettings.new(htf='776',htfint=776,max_memory=3)
var Candle[] candlesadd776                  = array.new<Candle>(0)
var BOSdata bosdataadd776                   = BOSdata.new()
htfadd776.settings                 := SettingsHTFadd776
htfadd776.candles                  := candlesadd776
htfadd776.bosdata                  := bosdataadd776
var CandleSet htfadd777                     = CandleSet.new()
var CandleSettings SettingsHTFadd777        = CandleSettings.new(htf='777',htfint=777,max_memory=3)
var Candle[] candlesadd777                  = array.new<Candle>(0)
var BOSdata bosdataadd777                   = BOSdata.new()
htfadd777.settings                 := SettingsHTFadd777
htfadd777.candles                  := candlesadd777
htfadd777.bosdata                  := bosdataadd777
var CandleSet htfadd778                     = CandleSet.new()
var CandleSettings SettingsHTFadd778        = CandleSettings.new(htf='778',htfint=778,max_memory=3)
var Candle[] candlesadd778                  = array.new<Candle>(0)
var BOSdata bosdataadd778                   = BOSdata.new()
htfadd778.settings                 := SettingsHTFadd778
htfadd778.candles                  := candlesadd778
htfadd778.bosdata                  := bosdataadd778
var CandleSet htfadd779                     = CandleSet.new()
var CandleSettings SettingsHTFadd779        = CandleSettings.new(htf='779',htfint=779,max_memory=3)
var Candle[] candlesadd779                  = array.new<Candle>(0)
var BOSdata bosdataadd779                   = BOSdata.new()
htfadd779.settings                 := SettingsHTFadd779
htfadd779.candles                  := candlesadd779
htfadd779.bosdata                  := bosdataadd779
var CandleSet htfadd780                     = CandleSet.new()
var CandleSettings SettingsHTFadd780        = CandleSettings.new(htf='780',htfint=780,max_memory=3)
var Candle[] candlesadd780                  = array.new<Candle>(0)
var BOSdata bosdataadd780                   = BOSdata.new()
htfadd780.settings                 := SettingsHTFadd780
htfadd780.candles                  := candlesadd780
htfadd780.bosdata                  := bosdataadd780
var CandleSet htfadd781                     = CandleSet.new()
var CandleSettings SettingsHTFadd781        = CandleSettings.new(htf='781',htfint=781,max_memory=3)
var Candle[] candlesadd781                  = array.new<Candle>(0)
var BOSdata bosdataadd781                   = BOSdata.new()
htfadd781.settings                 := SettingsHTFadd781
htfadd781.candles                  := candlesadd781
htfadd781.bosdata                  := bosdataadd781
var CandleSet htfadd782                     = CandleSet.new()
var CandleSettings SettingsHTFadd782        = CandleSettings.new(htf='782',htfint=782,max_memory=3)
var Candle[] candlesadd782                  = array.new<Candle>(0)
var BOSdata bosdataadd782                   = BOSdata.new()
htfadd782.settings                 := SettingsHTFadd782
htfadd782.candles                  := candlesadd782
htfadd782.bosdata                  := bosdataadd782
var CandleSet htfadd783                     = CandleSet.new()
var CandleSettings SettingsHTFadd783        = CandleSettings.new(htf='783',htfint=783,max_memory=3)
var Candle[] candlesadd783                  = array.new<Candle>(0)
var BOSdata bosdataadd783                   = BOSdata.new()
htfadd783.settings                 := SettingsHTFadd783
htfadd783.candles                  := candlesadd783
htfadd783.bosdata                  := bosdataadd783
var CandleSet htfadd784                     = CandleSet.new()
var CandleSettings SettingsHTFadd784        = CandleSettings.new(htf='784',htfint=784,max_memory=3)
var Candle[] candlesadd784                  = array.new<Candle>(0)
var BOSdata bosdataadd784                   = BOSdata.new()
htfadd784.settings                 := SettingsHTFadd784
htfadd784.candles                  := candlesadd784
htfadd784.bosdata                  := bosdataadd784
var CandleSet htfadd785                     = CandleSet.new()
var CandleSettings SettingsHTFadd785        = CandleSettings.new(htf='785',htfint=785,max_memory=3)
var Candle[] candlesadd785                  = array.new<Candle>(0)
var BOSdata bosdataadd785                   = BOSdata.new()
htfadd785.settings                 := SettingsHTFadd785
htfadd785.candles                  := candlesadd785
htfadd785.bosdata                  := bosdataadd785
var CandleSet htfadd786                     = CandleSet.new()
var CandleSettings SettingsHTFadd786        = CandleSettings.new(htf='786',htfint=786,max_memory=3)
var Candle[] candlesadd786                  = array.new<Candle>(0)
var BOSdata bosdataadd786                   = BOSdata.new()
htfadd786.settings                 := SettingsHTFadd786
htfadd786.candles                  := candlesadd786
htfadd786.bosdata                  := bosdataadd786
var CandleSet htfadd787                     = CandleSet.new()
var CandleSettings SettingsHTFadd787        = CandleSettings.new(htf='787',htfint=787,max_memory=3)
var Candle[] candlesadd787                  = array.new<Candle>(0)
var BOSdata bosdataadd787                   = BOSdata.new()
htfadd787.settings                 := SettingsHTFadd787
htfadd787.candles                  := candlesadd787
htfadd787.bosdata                  := bosdataadd787
var CandleSet htfadd788                     = CandleSet.new()
var CandleSettings SettingsHTFadd788        = CandleSettings.new(htf='788',htfint=788,max_memory=3)
var Candle[] candlesadd788                  = array.new<Candle>(0)
var BOSdata bosdataadd788                   = BOSdata.new()
htfadd788.settings                 := SettingsHTFadd788
htfadd788.candles                  := candlesadd788
htfadd788.bosdata                  := bosdataadd788
var CandleSet htfadd789                     = CandleSet.new()
var CandleSettings SettingsHTFadd789        = CandleSettings.new(htf='789',htfint=789,max_memory=3)
var Candle[] candlesadd789                  = array.new<Candle>(0)
var BOSdata bosdataadd789                   = BOSdata.new()
htfadd789.settings                 := SettingsHTFadd789
htfadd789.candles                  := candlesadd789
htfadd789.bosdata                  := bosdataadd789
var CandleSet htfadd790                     = CandleSet.new()
var CandleSettings SettingsHTFadd790        = CandleSettings.new(htf='790',htfint=790,max_memory=3)
var Candle[] candlesadd790                  = array.new<Candle>(0)
var BOSdata bosdataadd790                   = BOSdata.new()
htfadd790.settings                 := SettingsHTFadd790
htfadd790.candles                  := candlesadd790
htfadd790.bosdata                  := bosdataadd790
var CandleSet htfadd791                     = CandleSet.new()
var CandleSettings SettingsHTFadd791        = CandleSettings.new(htf='791',htfint=791,max_memory=3)
var Candle[] candlesadd791                  = array.new<Candle>(0)
var BOSdata bosdataadd791                   = BOSdata.new()
htfadd791.settings                 := SettingsHTFadd791
htfadd791.candles                  := candlesadd791
htfadd791.bosdata                  := bosdataadd791
var CandleSet htfadd792                     = CandleSet.new()
var CandleSettings SettingsHTFadd792        = CandleSettings.new(htf='792',htfint=792,max_memory=3)
var Candle[] candlesadd792                  = array.new<Candle>(0)
var BOSdata bosdataadd792                   = BOSdata.new()
htfadd792.settings                 := SettingsHTFadd792
htfadd792.candles                  := candlesadd792
htfadd792.bosdata                  := bosdataadd792
var CandleSet htfadd793                     = CandleSet.new()
var CandleSettings SettingsHTFadd793        = CandleSettings.new(htf='793',htfint=793,max_memory=3)
var Candle[] candlesadd793                  = array.new<Candle>(0)
var BOSdata bosdataadd793                   = BOSdata.new()
htfadd793.settings                 := SettingsHTFadd793
htfadd793.candles                  := candlesadd793
htfadd793.bosdata                  := bosdataadd793
var CandleSet htfadd794                     = CandleSet.new()
var CandleSettings SettingsHTFadd794        = CandleSettings.new(htf='794',htfint=794,max_memory=3)
var Candle[] candlesadd794                  = array.new<Candle>(0)
var BOSdata bosdataadd794                   = BOSdata.new()
htfadd794.settings                 := SettingsHTFadd794
htfadd794.candles                  := candlesadd794
htfadd794.bosdata                  := bosdataadd794
var CandleSet htfadd795                     = CandleSet.new()
var CandleSettings SettingsHTFadd795        = CandleSettings.new(htf='795',htfint=795,max_memory=3)
var Candle[] candlesadd795                  = array.new<Candle>(0)
var BOSdata bosdataadd795                   = BOSdata.new()
htfadd795.settings                 := SettingsHTFadd795
htfadd795.candles                  := candlesadd795
htfadd795.bosdata                  := bosdataadd795
var CandleSet htfadd796                     = CandleSet.new()
var CandleSettings SettingsHTFadd796        = CandleSettings.new(htf='796',htfint=796,max_memory=3)
var Candle[] candlesadd796                  = array.new<Candle>(0)
var BOSdata bosdataadd796                   = BOSdata.new()
htfadd796.settings                 := SettingsHTFadd796
htfadd796.candles                  := candlesadd796
htfadd796.bosdata                  := bosdataadd796
var CandleSet htfadd797                     = CandleSet.new()
var CandleSettings SettingsHTFadd797        = CandleSettings.new(htf='797',htfint=797,max_memory=3)
var Candle[] candlesadd797                  = array.new<Candle>(0)
var BOSdata bosdataadd797                   = BOSdata.new()
htfadd797.settings                 := SettingsHTFadd797
htfadd797.candles                  := candlesadd797
htfadd797.bosdata                  := bosdataadd797
var CandleSet htfadd798                     = CandleSet.new()
var CandleSettings SettingsHTFadd798        = CandleSettings.new(htf='798',htfint=798,max_memory=3)
var Candle[] candlesadd798                  = array.new<Candle>(0)
var BOSdata bosdataadd798                   = BOSdata.new()
htfadd798.settings                 := SettingsHTFadd798
htfadd798.candles                  := candlesadd798
htfadd798.bosdata                  := bosdataadd798
var CandleSet htfadd799                     = CandleSet.new()
var CandleSettings SettingsHTFadd799        = CandleSettings.new(htf='799',htfint=799,max_memory=3)
var Candle[] candlesadd799                  = array.new<Candle>(0)
var BOSdata bosdataadd799                   = BOSdata.new()
htfadd799.settings                 := SettingsHTFadd799
htfadd799.candles                  := candlesadd799
htfadd799.bosdata                  := bosdataadd799
var CandleSet htfadd800                     = CandleSet.new()
var CandleSettings SettingsHTFadd800        = CandleSettings.new(htf='800',htfint=800,max_memory=3)
var Candle[] candlesadd800                  = array.new<Candle>(0)
var BOSdata bosdataadd800                   = BOSdata.new()
htfadd800.settings                 := SettingsHTFadd800
htfadd800.candles                  := candlesadd800
htfadd800.bosdata                  := bosdataadd800
var CandleSet htfadd801                     = CandleSet.new()
var CandleSettings SettingsHTFadd801        = CandleSettings.new(htf='801',htfint=801,max_memory=3)
var Candle[] candlesadd801                  = array.new<Candle>(0)
var BOSdata bosdataadd801                   = BOSdata.new()
htfadd801.settings                 := SettingsHTFadd801
htfadd801.candles                  := candlesadd801
htfadd801.bosdata                  := bosdataadd801
var CandleSet htfadd802                     = CandleSet.new()
var CandleSettings SettingsHTFadd802        = CandleSettings.new(htf='802',htfint=802,max_memory=3)
var Candle[] candlesadd802                  = array.new<Candle>(0)
var BOSdata bosdataadd802                   = BOSdata.new()
htfadd802.settings                 := SettingsHTFadd802
htfadd802.candles                  := candlesadd802
htfadd802.bosdata                  := bosdataadd802
var CandleSet htfadd803                     = CandleSet.new()
var CandleSettings SettingsHTFadd803        = CandleSettings.new(htf='803',htfint=803,max_memory=3)
var Candle[] candlesadd803                  = array.new<Candle>(0)
var BOSdata bosdataadd803                   = BOSdata.new()
htfadd803.settings                 := SettingsHTFadd803
htfadd803.candles                  := candlesadd803
htfadd803.bosdata                  := bosdataadd803
var CandleSet htfadd804                     = CandleSet.new()
var CandleSettings SettingsHTFadd804        = CandleSettings.new(htf='804',htfint=804,max_memory=3)
var Candle[] candlesadd804                  = array.new<Candle>(0)
var BOSdata bosdataadd804                   = BOSdata.new()
htfadd804.settings                 := SettingsHTFadd804
htfadd804.candles                  := candlesadd804
htfadd804.bosdata                  := bosdataadd804
var CandleSet htfadd805                     = CandleSet.new()
var CandleSettings SettingsHTFadd805        = CandleSettings.new(htf='805',htfint=805,max_memory=3)
var Candle[] candlesadd805                  = array.new<Candle>(0)
var BOSdata bosdataadd805                   = BOSdata.new()
htfadd805.settings                 := SettingsHTFadd805
htfadd805.candles                  := candlesadd805
htfadd805.bosdata                  := bosdataadd805
var CandleSet htfadd806                     = CandleSet.new()
var CandleSettings SettingsHTFadd806        = CandleSettings.new(htf='806',htfint=806,max_memory=3)
var Candle[] candlesadd806                  = array.new<Candle>(0)
var BOSdata bosdataadd806                   = BOSdata.new()
htfadd806.settings                 := SettingsHTFadd806
htfadd806.candles                  := candlesadd806
htfadd806.bosdata                  := bosdataadd806
var CandleSet htfadd807                     = CandleSet.new()
var CandleSettings SettingsHTFadd807        = CandleSettings.new(htf='807',htfint=807,max_memory=3)
var Candle[] candlesadd807                  = array.new<Candle>(0)
var BOSdata bosdataadd807                   = BOSdata.new()
htfadd807.settings                 := SettingsHTFadd807
htfadd807.candles                  := candlesadd807
htfadd807.bosdata                  := bosdataadd807
var CandleSet htfadd808                     = CandleSet.new()
var CandleSettings SettingsHTFadd808        = CandleSettings.new(htf='808',htfint=808,max_memory=3)
var Candle[] candlesadd808                  = array.new<Candle>(0)
var BOSdata bosdataadd808                   = BOSdata.new()
htfadd808.settings                 := SettingsHTFadd808
htfadd808.candles                  := candlesadd808
htfadd808.bosdata                  := bosdataadd808
var CandleSet htfadd809                     = CandleSet.new()
var CandleSettings SettingsHTFadd809        = CandleSettings.new(htf='809',htfint=809,max_memory=3)
var Candle[] candlesadd809                  = array.new<Candle>(0)
var BOSdata bosdataadd809                   = BOSdata.new()
htfadd809.settings                 := SettingsHTFadd809
htfadd809.candles                  := candlesadd809
htfadd809.bosdata                  := bosdataadd809
var CandleSet htfadd810                     = CandleSet.new()
var CandleSettings SettingsHTFadd810        = CandleSettings.new(htf='810',htfint=810,max_memory=3)
var Candle[] candlesadd810                  = array.new<Candle>(0)
var BOSdata bosdataadd810                   = BOSdata.new()
htfadd810.settings                 := SettingsHTFadd810
htfadd810.candles                  := candlesadd810
htfadd810.bosdata                  := bosdataadd810

htfadd720.Monitor().BOSJudge()
htfadd721.Monitor().BOSJudge()
htfadd722.Monitor().BOSJudge()
htfadd723.Monitor().BOSJudge()
htfadd724.Monitor().BOSJudge()
htfadd725.Monitor().BOSJudge()
htfadd726.Monitor().BOSJudge()
htfadd727.Monitor().BOSJudge()
htfadd728.Monitor().BOSJudge()
htfadd729.Monitor().BOSJudge()
htfadd730.Monitor().BOSJudge()
htfadd731.Monitor().BOSJudge()
htfadd732.Monitor().BOSJudge()
htfadd733.Monitor().BOSJudge()
htfadd734.Monitor().BOSJudge()
htfadd735.Monitor().BOSJudge()
htfadd736.Monitor().BOSJudge()
htfadd737.Monitor().BOSJudge()
htfadd738.Monitor().BOSJudge()
htfadd739.Monitor().BOSJudge()
htfadd740.Monitor().BOSJudge()
htfadd741.Monitor().BOSJudge()
htfadd742.Monitor().BOSJudge()
htfadd743.Monitor().BOSJudge()
htfadd744.Monitor().BOSJudge()
htfadd745.Monitor().BOSJudge()
htfadd746.Monitor().BOSJudge()
htfadd747.Monitor().BOSJudge()
htfadd748.Monitor().BOSJudge()
htfadd749.Monitor().BOSJudge()
htfadd750.Monitor().BOSJudge()
htfadd751.Monitor().BOSJudge()
htfadd752.Monitor().BOSJudge()
htfadd753.Monitor().BOSJudge()
htfadd754.Monitor().BOSJudge()
htfadd755.Monitor().BOSJudge()
htfadd756.Monitor().BOSJudge()
htfadd757.Monitor().BOSJudge()
htfadd758.Monitor().BOSJudge()
htfadd759.Monitor().BOSJudge()
htfadd760.Monitor().BOSJudge()
htfadd761.Monitor().BOSJudge()
htfadd762.Monitor().BOSJudge()
htfadd763.Monitor().BOSJudge()
htfadd764.Monitor().BOSJudge()
htfadd765.Monitor().BOSJudge()
htfadd766.Monitor().BOSJudge()
htfadd767.Monitor().BOSJudge()
htfadd768.Monitor().BOSJudge()
htfadd769.Monitor().BOSJudge()
htfadd770.Monitor().BOSJudge()
htfadd771.Monitor().BOSJudge()
htfadd772.Monitor().BOSJudge()
htfadd773.Monitor().BOSJudge()
htfadd774.Monitor().BOSJudge()
htfadd775.Monitor().BOSJudge()
htfadd776.Monitor().BOSJudge()
htfadd777.Monitor().BOSJudge()
htfadd778.Monitor().BOSJudge()
htfadd779.Monitor().BOSJudge()
htfadd780.Monitor().BOSJudge()
htfadd781.Monitor().BOSJudge()
htfadd782.Monitor().BOSJudge()
htfadd783.Monitor().BOSJudge()
htfadd784.Monitor().BOSJudge()
htfadd785.Monitor().BOSJudge()
htfadd786.Monitor().BOSJudge()
htfadd787.Monitor().BOSJudge()
htfadd788.Monitor().BOSJudge()
htfadd789.Monitor().BOSJudge()
htfadd790.Monitor().BOSJudge()
htfadd791.Monitor().BOSJudge()
htfadd792.Monitor().BOSJudge()
htfadd793.Monitor().BOSJudge()
htfadd794.Monitor().BOSJudge()
htfadd795.Monitor().BOSJudge()
htfadd796.Monitor().BOSJudge()
htfadd797.Monitor().BOSJudge()
htfadd798.Monitor().BOSJudge()
htfadd799.Monitor().BOSJudge()
htfadd800.Monitor().BOSJudge()
htfadd801.Monitor().BOSJudge()
htfadd802.Monitor().BOSJudge()
htfadd803.Monitor().BOSJudge()
htfadd804.Monitor().BOSJudge()
htfadd805.Monitor().BOSJudge()
htfadd806.Monitor().BOSJudge()
htfadd807.Monitor().BOSJudge()
htfadd808.Monitor().BOSJudge()
htfadd809.Monitor().BOSJudge()
htfadd810.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd720)
    LowestsbuSet(lowestsbu, htfadd720)
    HighestsbdSet(highestsbd, htfadd721)
    LowestsbuSet(lowestsbu, htfadd721)
    HighestsbdSet(highestsbd, htfadd722)
    LowestsbuSet(lowestsbu, htfadd722)
    HighestsbdSet(highestsbd, htfadd723)
    LowestsbuSet(lowestsbu, htfadd723)
    HighestsbdSet(highestsbd, htfadd724)
    LowestsbuSet(lowestsbu, htfadd724)
    HighestsbdSet(highestsbd, htfadd725)
    LowestsbuSet(lowestsbu, htfadd725)
    HighestsbdSet(highestsbd, htfadd726)
    LowestsbuSet(lowestsbu, htfadd726)
    HighestsbdSet(highestsbd, htfadd727)
    LowestsbuSet(lowestsbu, htfadd727)
    HighestsbdSet(highestsbd, htfadd728)
    LowestsbuSet(lowestsbu, htfadd728)
    HighestsbdSet(highestsbd, htfadd729)
    LowestsbuSet(lowestsbu, htfadd729)
    HighestsbdSet(highestsbd, htfadd730)
    LowestsbuSet(lowestsbu, htfadd730)
    HighestsbdSet(highestsbd, htfadd731)
    LowestsbuSet(lowestsbu, htfadd731)
    HighestsbdSet(highestsbd, htfadd732)
    LowestsbuSet(lowestsbu, htfadd732)
    HighestsbdSet(highestsbd, htfadd733)
    LowestsbuSet(lowestsbu, htfadd733)
    HighestsbdSet(highestsbd, htfadd734)
    LowestsbuSet(lowestsbu, htfadd734)
    HighestsbdSet(highestsbd, htfadd735)
    LowestsbuSet(lowestsbu, htfadd735)
    HighestsbdSet(highestsbd, htfadd736)
    LowestsbuSet(lowestsbu, htfadd736)
    HighestsbdSet(highestsbd, htfadd737)
    LowestsbuSet(lowestsbu, htfadd737)
    HighestsbdSet(highestsbd, htfadd738)
    LowestsbuSet(lowestsbu, htfadd738)
    HighestsbdSet(highestsbd, htfadd739)
    LowestsbuSet(lowestsbu, htfadd739)
    HighestsbdSet(highestsbd, htfadd740)
    LowestsbuSet(lowestsbu, htfadd740)
    HighestsbdSet(highestsbd, htfadd741)
    LowestsbuSet(lowestsbu, htfadd741)
    HighestsbdSet(highestsbd, htfadd742)
    LowestsbuSet(lowestsbu, htfadd742)
    HighestsbdSet(highestsbd, htfadd743)
    LowestsbuSet(lowestsbu, htfadd743)
    HighestsbdSet(highestsbd, htfadd744)
    LowestsbuSet(lowestsbu, htfadd744)
    HighestsbdSet(highestsbd, htfadd745)
    LowestsbuSet(lowestsbu, htfadd745)
    HighestsbdSet(highestsbd, htfadd746)
    LowestsbuSet(lowestsbu, htfadd746)
    HighestsbdSet(highestsbd, htfadd747)
    LowestsbuSet(lowestsbu, htfadd747)
    HighestsbdSet(highestsbd, htfadd748)
    LowestsbuSet(lowestsbu, htfadd748)
    HighestsbdSet(highestsbd, htfadd749)
    LowestsbuSet(lowestsbu, htfadd749)
    HighestsbdSet(highestsbd, htfadd750)
    LowestsbuSet(lowestsbu, htfadd750)
    HighestsbdSet(highestsbd, htfadd751)
    LowestsbuSet(lowestsbu, htfadd751)
    HighestsbdSet(highestsbd, htfadd752)
    LowestsbuSet(lowestsbu, htfadd752)
    HighestsbdSet(highestsbd, htfadd753)
    LowestsbuSet(lowestsbu, htfadd753)
    HighestsbdSet(highestsbd, htfadd754)
    LowestsbuSet(lowestsbu, htfadd754)
    HighestsbdSet(highestsbd, htfadd755)
    LowestsbuSet(lowestsbu, htfadd755)
    HighestsbdSet(highestsbd, htfadd756)
    LowestsbuSet(lowestsbu, htfadd756)
    HighestsbdSet(highestsbd, htfadd757)
    LowestsbuSet(lowestsbu, htfadd757)
    HighestsbdSet(highestsbd, htfadd758)
    LowestsbuSet(lowestsbu, htfadd758)
    HighestsbdSet(highestsbd, htfadd759)
    LowestsbuSet(lowestsbu, htfadd759)
    HighestsbdSet(highestsbd, htfadd760)
    LowestsbuSet(lowestsbu, htfadd760)
    HighestsbdSet(highestsbd, htfadd761)
    LowestsbuSet(lowestsbu, htfadd761)
    HighestsbdSet(highestsbd, htfadd762)
    LowestsbuSet(lowestsbu, htfadd762)
    HighestsbdSet(highestsbd, htfadd763)
    LowestsbuSet(lowestsbu, htfadd763)
    HighestsbdSet(highestsbd, htfadd764)
    LowestsbuSet(lowestsbu, htfadd764)
    HighestsbdSet(highestsbd, htfadd765)
    LowestsbuSet(lowestsbu, htfadd765)
    HighestsbdSet(highestsbd, htfadd766)
    LowestsbuSet(lowestsbu, htfadd766)
    HighestsbdSet(highestsbd, htfadd767)
    LowestsbuSet(lowestsbu, htfadd767)
    HighestsbdSet(highestsbd, htfadd768)
    LowestsbuSet(lowestsbu, htfadd768)
    HighestsbdSet(highestsbd, htfadd769)
    LowestsbuSet(lowestsbu, htfadd769)
    HighestsbdSet(highestsbd, htfadd770)
    LowestsbuSet(lowestsbu, htfadd770)
    HighestsbdSet(highestsbd, htfadd771)
    LowestsbuSet(lowestsbu, htfadd771)
    HighestsbdSet(highestsbd, htfadd772)
    LowestsbuSet(lowestsbu, htfadd772)
    HighestsbdSet(highestsbd, htfadd773)
    LowestsbuSet(lowestsbu, htfadd773)
    HighestsbdSet(highestsbd, htfadd774)
    LowestsbuSet(lowestsbu, htfadd774)
    HighestsbdSet(highestsbd, htfadd775)
    LowestsbuSet(lowestsbu, htfadd775)
    HighestsbdSet(highestsbd, htfadd776)
    LowestsbuSet(lowestsbu, htfadd776)
    HighestsbdSet(highestsbd, htfadd777)
    LowestsbuSet(lowestsbu, htfadd777)
    HighestsbdSet(highestsbd, htfadd778)
    LowestsbuSet(lowestsbu, htfadd778)
    HighestsbdSet(highestsbd, htfadd779)
    LowestsbuSet(lowestsbu, htfadd779)
    HighestsbdSet(highestsbd, htfadd780)
    LowestsbuSet(lowestsbu, htfadd780)
    HighestsbdSet(highestsbd, htfadd781)
    LowestsbuSet(lowestsbu, htfadd781)
    HighestsbdSet(highestsbd, htfadd782)
    LowestsbuSet(lowestsbu, htfadd782)
    HighestsbdSet(highestsbd, htfadd783)
    LowestsbuSet(lowestsbu, htfadd783)
    HighestsbdSet(highestsbd, htfadd784)
    LowestsbuSet(lowestsbu, htfadd784)
    HighestsbdSet(highestsbd, htfadd785)
    LowestsbuSet(lowestsbu, htfadd785)
    HighestsbdSet(highestsbd, htfadd786)
    LowestsbuSet(lowestsbu, htfadd786)
    HighestsbdSet(highestsbd, htfadd787)
    LowestsbuSet(lowestsbu, htfadd787)
    HighestsbdSet(highestsbd, htfadd788)
    LowestsbuSet(lowestsbu, htfadd788)
    HighestsbdSet(highestsbd, htfadd789)
    LowestsbuSet(lowestsbu, htfadd789)
    HighestsbdSet(highestsbd, htfadd790)
    LowestsbuSet(lowestsbu, htfadd790)
    HighestsbdSet(highestsbd, htfadd791)
    LowestsbuSet(lowestsbu, htfadd791)
    HighestsbdSet(highestsbd, htfadd792)
    LowestsbuSet(lowestsbu, htfadd792)
    HighestsbdSet(highestsbd, htfadd793)
    LowestsbuSet(lowestsbu, htfadd793)
    HighestsbdSet(highestsbd, htfadd794)
    LowestsbuSet(lowestsbu, htfadd794)
    HighestsbdSet(highestsbd, htfadd795)
    LowestsbuSet(lowestsbu, htfadd795)
    HighestsbdSet(highestsbd, htfadd796)
    LowestsbuSet(lowestsbu, htfadd796)
    HighestsbdSet(highestsbd, htfadd797)
    LowestsbuSet(lowestsbu, htfadd797)
    HighestsbdSet(highestsbd, htfadd798)
    LowestsbuSet(lowestsbu, htfadd798)
    HighestsbdSet(highestsbd, htfadd799)
    LowestsbuSet(lowestsbu, htfadd799)
    HighestsbdSet(highestsbd, htfadd800)
    LowestsbuSet(lowestsbu, htfadd800)
    HighestsbdSet(highestsbd, htfadd801)
    LowestsbuSet(lowestsbu, htfadd801)
    HighestsbdSet(highestsbd, htfadd802)
    LowestsbuSet(lowestsbu, htfadd802)
    HighestsbdSet(highestsbd, htfadd803)
    LowestsbuSet(lowestsbu, htfadd803)
    HighestsbdSet(highestsbd, htfadd804)
    LowestsbuSet(lowestsbu, htfadd804)
    HighestsbdSet(highestsbd, htfadd805)
    LowestsbuSet(lowestsbu, htfadd805)
    HighestsbdSet(highestsbd, htfadd806)
    LowestsbuSet(lowestsbu, htfadd806)
    HighestsbdSet(highestsbd, htfadd807)
    LowestsbuSet(lowestsbu, htfadd807)
    HighestsbdSet(highestsbd, htfadd808)
    LowestsbuSet(lowestsbu, htfadd808)
    HighestsbdSet(highestsbd, htfadd809)
    LowestsbuSet(lowestsbu, htfadd809)
    HighestsbdSet(highestsbd, htfadd810)
    LowestsbuSet(lowestsbu, htfadd810)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd720).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd721).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd722).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd723).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd724).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd725).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd726).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd727).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd728).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd729).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd730).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd731).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd732).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd733).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd734).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd735).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd736).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd737).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd738).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd739).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd740).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd741).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd742).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd743).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd744).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd745).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd746).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd747).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd748).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd749).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd750).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd751).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd752).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd753).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd754).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd755).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd756).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd757).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd758).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd759).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd760).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd761).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd762).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd763).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd764).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd765).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd766).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd767).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd768).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd769).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd770).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd771).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd772).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd773).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd774).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd775).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd776).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd777).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd778).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd779).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd780).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd781).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd782).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd783).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd784).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd785).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd786).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd787).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd788).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd789).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd790).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd791).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd792).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd793).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd794).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd795).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd796).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd797).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd798).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd799).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd800).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd801).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd802).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd803).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd804).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd805).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd806).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd807).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd808).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd809).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd810).Monitor_Est().BOSJudge()
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


