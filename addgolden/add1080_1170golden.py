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
var CandleSet htfadd1080                     = CandleSet.new()
var CandleSettings SettingsHTFadd1080        = CandleSettings.new(htf='1080',htfint=1080,max_memory=3)
var Candle[] candlesadd1080                  = array.new<Candle>(0)
var BOSdata bosdataadd1080                   = BOSdata.new()
htfadd1080.settings                 := SettingsHTFadd1080
htfadd1080.candles                  := candlesadd1080
htfadd1080.bosdata                  := bosdataadd1080
var CandleSet htfadd1081                     = CandleSet.new()
var CandleSettings SettingsHTFadd1081        = CandleSettings.new(htf='1081',htfint=1081,max_memory=3)
var Candle[] candlesadd1081                  = array.new<Candle>(0)
var BOSdata bosdataadd1081                   = BOSdata.new()
htfadd1081.settings                 := SettingsHTFadd1081
htfadd1081.candles                  := candlesadd1081
htfadd1081.bosdata                  := bosdataadd1081
var CandleSet htfadd1082                     = CandleSet.new()
var CandleSettings SettingsHTFadd1082        = CandleSettings.new(htf='1082',htfint=1082,max_memory=3)
var Candle[] candlesadd1082                  = array.new<Candle>(0)
var BOSdata bosdataadd1082                   = BOSdata.new()
htfadd1082.settings                 := SettingsHTFadd1082
htfadd1082.candles                  := candlesadd1082
htfadd1082.bosdata                  := bosdataadd1082
var CandleSet htfadd1083                     = CandleSet.new()
var CandleSettings SettingsHTFadd1083        = CandleSettings.new(htf='1083',htfint=1083,max_memory=3)
var Candle[] candlesadd1083                  = array.new<Candle>(0)
var BOSdata bosdataadd1083                   = BOSdata.new()
htfadd1083.settings                 := SettingsHTFadd1083
htfadd1083.candles                  := candlesadd1083
htfadd1083.bosdata                  := bosdataadd1083
var CandleSet htfadd1084                     = CandleSet.new()
var CandleSettings SettingsHTFadd1084        = CandleSettings.new(htf='1084',htfint=1084,max_memory=3)
var Candle[] candlesadd1084                  = array.new<Candle>(0)
var BOSdata bosdataadd1084                   = BOSdata.new()
htfadd1084.settings                 := SettingsHTFadd1084
htfadd1084.candles                  := candlesadd1084
htfadd1084.bosdata                  := bosdataadd1084
var CandleSet htfadd1085                     = CandleSet.new()
var CandleSettings SettingsHTFadd1085        = CandleSettings.new(htf='1085',htfint=1085,max_memory=3)
var Candle[] candlesadd1085                  = array.new<Candle>(0)
var BOSdata bosdataadd1085                   = BOSdata.new()
htfadd1085.settings                 := SettingsHTFadd1085
htfadd1085.candles                  := candlesadd1085
htfadd1085.bosdata                  := bosdataadd1085
var CandleSet htfadd1086                     = CandleSet.new()
var CandleSettings SettingsHTFadd1086        = CandleSettings.new(htf='1086',htfint=1086,max_memory=3)
var Candle[] candlesadd1086                  = array.new<Candle>(0)
var BOSdata bosdataadd1086                   = BOSdata.new()
htfadd1086.settings                 := SettingsHTFadd1086
htfadd1086.candles                  := candlesadd1086
htfadd1086.bosdata                  := bosdataadd1086
var CandleSet htfadd1087                     = CandleSet.new()
var CandleSettings SettingsHTFadd1087        = CandleSettings.new(htf='1087',htfint=1087,max_memory=3)
var Candle[] candlesadd1087                  = array.new<Candle>(0)
var BOSdata bosdataadd1087                   = BOSdata.new()
htfadd1087.settings                 := SettingsHTFadd1087
htfadd1087.candles                  := candlesadd1087
htfadd1087.bosdata                  := bosdataadd1087
var CandleSet htfadd1088                     = CandleSet.new()
var CandleSettings SettingsHTFadd1088        = CandleSettings.new(htf='1088',htfint=1088,max_memory=3)
var Candle[] candlesadd1088                  = array.new<Candle>(0)
var BOSdata bosdataadd1088                   = BOSdata.new()
htfadd1088.settings                 := SettingsHTFadd1088
htfadd1088.candles                  := candlesadd1088
htfadd1088.bosdata                  := bosdataadd1088
var CandleSet htfadd1089                     = CandleSet.new()
var CandleSettings SettingsHTFadd1089        = CandleSettings.new(htf='1089',htfint=1089,max_memory=3)
var Candle[] candlesadd1089                  = array.new<Candle>(0)
var BOSdata bosdataadd1089                   = BOSdata.new()
htfadd1089.settings                 := SettingsHTFadd1089
htfadd1089.candles                  := candlesadd1089
htfadd1089.bosdata                  := bosdataadd1089
var CandleSet htfadd1090                     = CandleSet.new()
var CandleSettings SettingsHTFadd1090        = CandleSettings.new(htf='1090',htfint=1090,max_memory=3)
var Candle[] candlesadd1090                  = array.new<Candle>(0)
var BOSdata bosdataadd1090                   = BOSdata.new()
htfadd1090.settings                 := SettingsHTFadd1090
htfadd1090.candles                  := candlesadd1090
htfadd1090.bosdata                  := bosdataadd1090
var CandleSet htfadd1091                     = CandleSet.new()
var CandleSettings SettingsHTFadd1091        = CandleSettings.new(htf='1091',htfint=1091,max_memory=3)
var Candle[] candlesadd1091                  = array.new<Candle>(0)
var BOSdata bosdataadd1091                   = BOSdata.new()
htfadd1091.settings                 := SettingsHTFadd1091
htfadd1091.candles                  := candlesadd1091
htfadd1091.bosdata                  := bosdataadd1091
var CandleSet htfadd1092                     = CandleSet.new()
var CandleSettings SettingsHTFadd1092        = CandleSettings.new(htf='1092',htfint=1092,max_memory=3)
var Candle[] candlesadd1092                  = array.new<Candle>(0)
var BOSdata bosdataadd1092                   = BOSdata.new()
htfadd1092.settings                 := SettingsHTFadd1092
htfadd1092.candles                  := candlesadd1092
htfadd1092.bosdata                  := bosdataadd1092
var CandleSet htfadd1093                     = CandleSet.new()
var CandleSettings SettingsHTFadd1093        = CandleSettings.new(htf='1093',htfint=1093,max_memory=3)
var Candle[] candlesadd1093                  = array.new<Candle>(0)
var BOSdata bosdataadd1093                   = BOSdata.new()
htfadd1093.settings                 := SettingsHTFadd1093
htfadd1093.candles                  := candlesadd1093
htfadd1093.bosdata                  := bosdataadd1093
var CandleSet htfadd1094                     = CandleSet.new()
var CandleSettings SettingsHTFadd1094        = CandleSettings.new(htf='1094',htfint=1094,max_memory=3)
var Candle[] candlesadd1094                  = array.new<Candle>(0)
var BOSdata bosdataadd1094                   = BOSdata.new()
htfadd1094.settings                 := SettingsHTFadd1094
htfadd1094.candles                  := candlesadd1094
htfadd1094.bosdata                  := bosdataadd1094
var CandleSet htfadd1095                     = CandleSet.new()
var CandleSettings SettingsHTFadd1095        = CandleSettings.new(htf='1095',htfint=1095,max_memory=3)
var Candle[] candlesadd1095                  = array.new<Candle>(0)
var BOSdata bosdataadd1095                   = BOSdata.new()
htfadd1095.settings                 := SettingsHTFadd1095
htfadd1095.candles                  := candlesadd1095
htfadd1095.bosdata                  := bosdataadd1095
var CandleSet htfadd1096                     = CandleSet.new()
var CandleSettings SettingsHTFadd1096        = CandleSettings.new(htf='1096',htfint=1096,max_memory=3)
var Candle[] candlesadd1096                  = array.new<Candle>(0)
var BOSdata bosdataadd1096                   = BOSdata.new()
htfadd1096.settings                 := SettingsHTFadd1096
htfadd1096.candles                  := candlesadd1096
htfadd1096.bosdata                  := bosdataadd1096
var CandleSet htfadd1097                     = CandleSet.new()
var CandleSettings SettingsHTFadd1097        = CandleSettings.new(htf='1097',htfint=1097,max_memory=3)
var Candle[] candlesadd1097                  = array.new<Candle>(0)
var BOSdata bosdataadd1097                   = BOSdata.new()
htfadd1097.settings                 := SettingsHTFadd1097
htfadd1097.candles                  := candlesadd1097
htfadd1097.bosdata                  := bosdataadd1097
var CandleSet htfadd1098                     = CandleSet.new()
var CandleSettings SettingsHTFadd1098        = CandleSettings.new(htf='1098',htfint=1098,max_memory=3)
var Candle[] candlesadd1098                  = array.new<Candle>(0)
var BOSdata bosdataadd1098                   = BOSdata.new()
htfadd1098.settings                 := SettingsHTFadd1098
htfadd1098.candles                  := candlesadd1098
htfadd1098.bosdata                  := bosdataadd1098
var CandleSet htfadd1099                     = CandleSet.new()
var CandleSettings SettingsHTFadd1099        = CandleSettings.new(htf='1099',htfint=1099,max_memory=3)
var Candle[] candlesadd1099                  = array.new<Candle>(0)
var BOSdata bosdataadd1099                   = BOSdata.new()
htfadd1099.settings                 := SettingsHTFadd1099
htfadd1099.candles                  := candlesadd1099
htfadd1099.bosdata                  := bosdataadd1099
var CandleSet htfadd1100                     = CandleSet.new()
var CandleSettings SettingsHTFadd1100        = CandleSettings.new(htf='1100',htfint=1100,max_memory=3)
var Candle[] candlesadd1100                  = array.new<Candle>(0)
var BOSdata bosdataadd1100                   = BOSdata.new()
htfadd1100.settings                 := SettingsHTFadd1100
htfadd1100.candles                  := candlesadd1100
htfadd1100.bosdata                  := bosdataadd1100
var CandleSet htfadd1101                     = CandleSet.new()
var CandleSettings SettingsHTFadd1101        = CandleSettings.new(htf='1101',htfint=1101,max_memory=3)
var Candle[] candlesadd1101                  = array.new<Candle>(0)
var BOSdata bosdataadd1101                   = BOSdata.new()
htfadd1101.settings                 := SettingsHTFadd1101
htfadd1101.candles                  := candlesadd1101
htfadd1101.bosdata                  := bosdataadd1101
var CandleSet htfadd1102                     = CandleSet.new()
var CandleSettings SettingsHTFadd1102        = CandleSettings.new(htf='1102',htfint=1102,max_memory=3)
var Candle[] candlesadd1102                  = array.new<Candle>(0)
var BOSdata bosdataadd1102                   = BOSdata.new()
htfadd1102.settings                 := SettingsHTFadd1102
htfadd1102.candles                  := candlesadd1102
htfadd1102.bosdata                  := bosdataadd1102
var CandleSet htfadd1103                     = CandleSet.new()
var CandleSettings SettingsHTFadd1103        = CandleSettings.new(htf='1103',htfint=1103,max_memory=3)
var Candle[] candlesadd1103                  = array.new<Candle>(0)
var BOSdata bosdataadd1103                   = BOSdata.new()
htfadd1103.settings                 := SettingsHTFadd1103
htfadd1103.candles                  := candlesadd1103
htfadd1103.bosdata                  := bosdataadd1103
var CandleSet htfadd1104                     = CandleSet.new()
var CandleSettings SettingsHTFadd1104        = CandleSettings.new(htf='1104',htfint=1104,max_memory=3)
var Candle[] candlesadd1104                  = array.new<Candle>(0)
var BOSdata bosdataadd1104                   = BOSdata.new()
htfadd1104.settings                 := SettingsHTFadd1104
htfadd1104.candles                  := candlesadd1104
htfadd1104.bosdata                  := bosdataadd1104
var CandleSet htfadd1105                     = CandleSet.new()
var CandleSettings SettingsHTFadd1105        = CandleSettings.new(htf='1105',htfint=1105,max_memory=3)
var Candle[] candlesadd1105                  = array.new<Candle>(0)
var BOSdata bosdataadd1105                   = BOSdata.new()
htfadd1105.settings                 := SettingsHTFadd1105
htfadd1105.candles                  := candlesadd1105
htfadd1105.bosdata                  := bosdataadd1105
var CandleSet htfadd1106                     = CandleSet.new()
var CandleSettings SettingsHTFadd1106        = CandleSettings.new(htf='1106',htfint=1106,max_memory=3)
var Candle[] candlesadd1106                  = array.new<Candle>(0)
var BOSdata bosdataadd1106                   = BOSdata.new()
htfadd1106.settings                 := SettingsHTFadd1106
htfadd1106.candles                  := candlesadd1106
htfadd1106.bosdata                  := bosdataadd1106
var CandleSet htfadd1107                     = CandleSet.new()
var CandleSettings SettingsHTFadd1107        = CandleSettings.new(htf='1107',htfint=1107,max_memory=3)
var Candle[] candlesadd1107                  = array.new<Candle>(0)
var BOSdata bosdataadd1107                   = BOSdata.new()
htfadd1107.settings                 := SettingsHTFadd1107
htfadd1107.candles                  := candlesadd1107
htfadd1107.bosdata                  := bosdataadd1107
var CandleSet htfadd1108                     = CandleSet.new()
var CandleSettings SettingsHTFadd1108        = CandleSettings.new(htf='1108',htfint=1108,max_memory=3)
var Candle[] candlesadd1108                  = array.new<Candle>(0)
var BOSdata bosdataadd1108                   = BOSdata.new()
htfadd1108.settings                 := SettingsHTFadd1108
htfadd1108.candles                  := candlesadd1108
htfadd1108.bosdata                  := bosdataadd1108
var CandleSet htfadd1109                     = CandleSet.new()
var CandleSettings SettingsHTFadd1109        = CandleSettings.new(htf='1109',htfint=1109,max_memory=3)
var Candle[] candlesadd1109                  = array.new<Candle>(0)
var BOSdata bosdataadd1109                   = BOSdata.new()
htfadd1109.settings                 := SettingsHTFadd1109
htfadd1109.candles                  := candlesadd1109
htfadd1109.bosdata                  := bosdataadd1109
var CandleSet htfadd1110                     = CandleSet.new()
var CandleSettings SettingsHTFadd1110        = CandleSettings.new(htf='1110',htfint=1110,max_memory=3)
var Candle[] candlesadd1110                  = array.new<Candle>(0)
var BOSdata bosdataadd1110                   = BOSdata.new()
htfadd1110.settings                 := SettingsHTFadd1110
htfadd1110.candles                  := candlesadd1110
htfadd1110.bosdata                  := bosdataadd1110
var CandleSet htfadd1111                     = CandleSet.new()
var CandleSettings SettingsHTFadd1111        = CandleSettings.new(htf='1111',htfint=1111,max_memory=3)
var Candle[] candlesadd1111                  = array.new<Candle>(0)
var BOSdata bosdataadd1111                   = BOSdata.new()
htfadd1111.settings                 := SettingsHTFadd1111
htfadd1111.candles                  := candlesadd1111
htfadd1111.bosdata                  := bosdataadd1111
var CandleSet htfadd1112                     = CandleSet.new()
var CandleSettings SettingsHTFadd1112        = CandleSettings.new(htf='1112',htfint=1112,max_memory=3)
var Candle[] candlesadd1112                  = array.new<Candle>(0)
var BOSdata bosdataadd1112                   = BOSdata.new()
htfadd1112.settings                 := SettingsHTFadd1112
htfadd1112.candles                  := candlesadd1112
htfadd1112.bosdata                  := bosdataadd1112
var CandleSet htfadd1113                     = CandleSet.new()
var CandleSettings SettingsHTFadd1113        = CandleSettings.new(htf='1113',htfint=1113,max_memory=3)
var Candle[] candlesadd1113                  = array.new<Candle>(0)
var BOSdata bosdataadd1113                   = BOSdata.new()
htfadd1113.settings                 := SettingsHTFadd1113
htfadd1113.candles                  := candlesadd1113
htfadd1113.bosdata                  := bosdataadd1113
var CandleSet htfadd1114                     = CandleSet.new()
var CandleSettings SettingsHTFadd1114        = CandleSettings.new(htf='1114',htfint=1114,max_memory=3)
var Candle[] candlesadd1114                  = array.new<Candle>(0)
var BOSdata bosdataadd1114                   = BOSdata.new()
htfadd1114.settings                 := SettingsHTFadd1114
htfadd1114.candles                  := candlesadd1114
htfadd1114.bosdata                  := bosdataadd1114
var CandleSet htfadd1115                     = CandleSet.new()
var CandleSettings SettingsHTFadd1115        = CandleSettings.new(htf='1115',htfint=1115,max_memory=3)
var Candle[] candlesadd1115                  = array.new<Candle>(0)
var BOSdata bosdataadd1115                   = BOSdata.new()
htfadd1115.settings                 := SettingsHTFadd1115
htfadd1115.candles                  := candlesadd1115
htfadd1115.bosdata                  := bosdataadd1115
var CandleSet htfadd1116                     = CandleSet.new()
var CandleSettings SettingsHTFadd1116        = CandleSettings.new(htf='1116',htfint=1116,max_memory=3)
var Candle[] candlesadd1116                  = array.new<Candle>(0)
var BOSdata bosdataadd1116                   = BOSdata.new()
htfadd1116.settings                 := SettingsHTFadd1116
htfadd1116.candles                  := candlesadd1116
htfadd1116.bosdata                  := bosdataadd1116
var CandleSet htfadd1117                     = CandleSet.new()
var CandleSettings SettingsHTFadd1117        = CandleSettings.new(htf='1117',htfint=1117,max_memory=3)
var Candle[] candlesadd1117                  = array.new<Candle>(0)
var BOSdata bosdataadd1117                   = BOSdata.new()
htfadd1117.settings                 := SettingsHTFadd1117
htfadd1117.candles                  := candlesadd1117
htfadd1117.bosdata                  := bosdataadd1117
var CandleSet htfadd1118                     = CandleSet.new()
var CandleSettings SettingsHTFadd1118        = CandleSettings.new(htf='1118',htfint=1118,max_memory=3)
var Candle[] candlesadd1118                  = array.new<Candle>(0)
var BOSdata bosdataadd1118                   = BOSdata.new()
htfadd1118.settings                 := SettingsHTFadd1118
htfadd1118.candles                  := candlesadd1118
htfadd1118.bosdata                  := bosdataadd1118
var CandleSet htfadd1119                     = CandleSet.new()
var CandleSettings SettingsHTFadd1119        = CandleSettings.new(htf='1119',htfint=1119,max_memory=3)
var Candle[] candlesadd1119                  = array.new<Candle>(0)
var BOSdata bosdataadd1119                   = BOSdata.new()
htfadd1119.settings                 := SettingsHTFadd1119
htfadd1119.candles                  := candlesadd1119
htfadd1119.bosdata                  := bosdataadd1119
var CandleSet htfadd1120                     = CandleSet.new()
var CandleSettings SettingsHTFadd1120        = CandleSettings.new(htf='1120',htfint=1120,max_memory=3)
var Candle[] candlesadd1120                  = array.new<Candle>(0)
var BOSdata bosdataadd1120                   = BOSdata.new()
htfadd1120.settings                 := SettingsHTFadd1120
htfadd1120.candles                  := candlesadd1120
htfadd1120.bosdata                  := bosdataadd1120
var CandleSet htfadd1121                     = CandleSet.new()
var CandleSettings SettingsHTFadd1121        = CandleSettings.new(htf='1121',htfint=1121,max_memory=3)
var Candle[] candlesadd1121                  = array.new<Candle>(0)
var BOSdata bosdataadd1121                   = BOSdata.new()
htfadd1121.settings                 := SettingsHTFadd1121
htfadd1121.candles                  := candlesadd1121
htfadd1121.bosdata                  := bosdataadd1121
var CandleSet htfadd1122                     = CandleSet.new()
var CandleSettings SettingsHTFadd1122        = CandleSettings.new(htf='1122',htfint=1122,max_memory=3)
var Candle[] candlesadd1122                  = array.new<Candle>(0)
var BOSdata bosdataadd1122                   = BOSdata.new()
htfadd1122.settings                 := SettingsHTFadd1122
htfadd1122.candles                  := candlesadd1122
htfadd1122.bosdata                  := bosdataadd1122
var CandleSet htfadd1123                     = CandleSet.new()
var CandleSettings SettingsHTFadd1123        = CandleSettings.new(htf='1123',htfint=1123,max_memory=3)
var Candle[] candlesadd1123                  = array.new<Candle>(0)
var BOSdata bosdataadd1123                   = BOSdata.new()
htfadd1123.settings                 := SettingsHTFadd1123
htfadd1123.candles                  := candlesadd1123
htfadd1123.bosdata                  := bosdataadd1123
var CandleSet htfadd1124                     = CandleSet.new()
var CandleSettings SettingsHTFadd1124        = CandleSettings.new(htf='1124',htfint=1124,max_memory=3)
var Candle[] candlesadd1124                  = array.new<Candle>(0)
var BOSdata bosdataadd1124                   = BOSdata.new()
htfadd1124.settings                 := SettingsHTFadd1124
htfadd1124.candles                  := candlesadd1124
htfadd1124.bosdata                  := bosdataadd1124
var CandleSet htfadd1125                     = CandleSet.new()
var CandleSettings SettingsHTFadd1125        = CandleSettings.new(htf='1125',htfint=1125,max_memory=3)
var Candle[] candlesadd1125                  = array.new<Candle>(0)
var BOSdata bosdataadd1125                   = BOSdata.new()
htfadd1125.settings                 := SettingsHTFadd1125
htfadd1125.candles                  := candlesadd1125
htfadd1125.bosdata                  := bosdataadd1125
var CandleSet htfadd1126                     = CandleSet.new()
var CandleSettings SettingsHTFadd1126        = CandleSettings.new(htf='1126',htfint=1126,max_memory=3)
var Candle[] candlesadd1126                  = array.new<Candle>(0)
var BOSdata bosdataadd1126                   = BOSdata.new()
htfadd1126.settings                 := SettingsHTFadd1126
htfadd1126.candles                  := candlesadd1126
htfadd1126.bosdata                  := bosdataadd1126
var CandleSet htfadd1127                     = CandleSet.new()
var CandleSettings SettingsHTFadd1127        = CandleSettings.new(htf='1127',htfint=1127,max_memory=3)
var Candle[] candlesadd1127                  = array.new<Candle>(0)
var BOSdata bosdataadd1127                   = BOSdata.new()
htfadd1127.settings                 := SettingsHTFadd1127
htfadd1127.candles                  := candlesadd1127
htfadd1127.bosdata                  := bosdataadd1127
var CandleSet htfadd1128                     = CandleSet.new()
var CandleSettings SettingsHTFadd1128        = CandleSettings.new(htf='1128',htfint=1128,max_memory=3)
var Candle[] candlesadd1128                  = array.new<Candle>(0)
var BOSdata bosdataadd1128                   = BOSdata.new()
htfadd1128.settings                 := SettingsHTFadd1128
htfadd1128.candles                  := candlesadd1128
htfadd1128.bosdata                  := bosdataadd1128
var CandleSet htfadd1129                     = CandleSet.new()
var CandleSettings SettingsHTFadd1129        = CandleSettings.new(htf='1129',htfint=1129,max_memory=3)
var Candle[] candlesadd1129                  = array.new<Candle>(0)
var BOSdata bosdataadd1129                   = BOSdata.new()
htfadd1129.settings                 := SettingsHTFadd1129
htfadd1129.candles                  := candlesadd1129
htfadd1129.bosdata                  := bosdataadd1129
var CandleSet htfadd1130                     = CandleSet.new()
var CandleSettings SettingsHTFadd1130        = CandleSettings.new(htf='1130',htfint=1130,max_memory=3)
var Candle[] candlesadd1130                  = array.new<Candle>(0)
var BOSdata bosdataadd1130                   = BOSdata.new()
htfadd1130.settings                 := SettingsHTFadd1130
htfadd1130.candles                  := candlesadd1130
htfadd1130.bosdata                  := bosdataadd1130
var CandleSet htfadd1131                     = CandleSet.new()
var CandleSettings SettingsHTFadd1131        = CandleSettings.new(htf='1131',htfint=1131,max_memory=3)
var Candle[] candlesadd1131                  = array.new<Candle>(0)
var BOSdata bosdataadd1131                   = BOSdata.new()
htfadd1131.settings                 := SettingsHTFadd1131
htfadd1131.candles                  := candlesadd1131
htfadd1131.bosdata                  := bosdataadd1131
var CandleSet htfadd1132                     = CandleSet.new()
var CandleSettings SettingsHTFadd1132        = CandleSettings.new(htf='1132',htfint=1132,max_memory=3)
var Candle[] candlesadd1132                  = array.new<Candle>(0)
var BOSdata bosdataadd1132                   = BOSdata.new()
htfadd1132.settings                 := SettingsHTFadd1132
htfadd1132.candles                  := candlesadd1132
htfadd1132.bosdata                  := bosdataadd1132
var CandleSet htfadd1133                     = CandleSet.new()
var CandleSettings SettingsHTFadd1133        = CandleSettings.new(htf='1133',htfint=1133,max_memory=3)
var Candle[] candlesadd1133                  = array.new<Candle>(0)
var BOSdata bosdataadd1133                   = BOSdata.new()
htfadd1133.settings                 := SettingsHTFadd1133
htfadd1133.candles                  := candlesadd1133
htfadd1133.bosdata                  := bosdataadd1133
var CandleSet htfadd1134                     = CandleSet.new()
var CandleSettings SettingsHTFadd1134        = CandleSettings.new(htf='1134',htfint=1134,max_memory=3)
var Candle[] candlesadd1134                  = array.new<Candle>(0)
var BOSdata bosdataadd1134                   = BOSdata.new()
htfadd1134.settings                 := SettingsHTFadd1134
htfadd1134.candles                  := candlesadd1134
htfadd1134.bosdata                  := bosdataadd1134
var CandleSet htfadd1135                     = CandleSet.new()
var CandleSettings SettingsHTFadd1135        = CandleSettings.new(htf='1135',htfint=1135,max_memory=3)
var Candle[] candlesadd1135                  = array.new<Candle>(0)
var BOSdata bosdataadd1135                   = BOSdata.new()
htfadd1135.settings                 := SettingsHTFadd1135
htfadd1135.candles                  := candlesadd1135
htfadd1135.bosdata                  := bosdataadd1135
var CandleSet htfadd1136                     = CandleSet.new()
var CandleSettings SettingsHTFadd1136        = CandleSettings.new(htf='1136',htfint=1136,max_memory=3)
var Candle[] candlesadd1136                  = array.new<Candle>(0)
var BOSdata bosdataadd1136                   = BOSdata.new()
htfadd1136.settings                 := SettingsHTFadd1136
htfadd1136.candles                  := candlesadd1136
htfadd1136.bosdata                  := bosdataadd1136
var CandleSet htfadd1137                     = CandleSet.new()
var CandleSettings SettingsHTFadd1137        = CandleSettings.new(htf='1137',htfint=1137,max_memory=3)
var Candle[] candlesadd1137                  = array.new<Candle>(0)
var BOSdata bosdataadd1137                   = BOSdata.new()
htfadd1137.settings                 := SettingsHTFadd1137
htfadd1137.candles                  := candlesadd1137
htfadd1137.bosdata                  := bosdataadd1137
var CandleSet htfadd1138                     = CandleSet.new()
var CandleSettings SettingsHTFadd1138        = CandleSettings.new(htf='1138',htfint=1138,max_memory=3)
var Candle[] candlesadd1138                  = array.new<Candle>(0)
var BOSdata bosdataadd1138                   = BOSdata.new()
htfadd1138.settings                 := SettingsHTFadd1138
htfadd1138.candles                  := candlesadd1138
htfadd1138.bosdata                  := bosdataadd1138
var CandleSet htfadd1139                     = CandleSet.new()
var CandleSettings SettingsHTFadd1139        = CandleSettings.new(htf='1139',htfint=1139,max_memory=3)
var Candle[] candlesadd1139                  = array.new<Candle>(0)
var BOSdata bosdataadd1139                   = BOSdata.new()
htfadd1139.settings                 := SettingsHTFadd1139
htfadd1139.candles                  := candlesadd1139
htfadd1139.bosdata                  := bosdataadd1139
var CandleSet htfadd1140                     = CandleSet.new()
var CandleSettings SettingsHTFadd1140        = CandleSettings.new(htf='1140',htfint=1140,max_memory=3)
var Candle[] candlesadd1140                  = array.new<Candle>(0)
var BOSdata bosdataadd1140                   = BOSdata.new()
htfadd1140.settings                 := SettingsHTFadd1140
htfadd1140.candles                  := candlesadd1140
htfadd1140.bosdata                  := bosdataadd1140
var CandleSet htfadd1141                     = CandleSet.new()
var CandleSettings SettingsHTFadd1141        = CandleSettings.new(htf='1141',htfint=1141,max_memory=3)
var Candle[] candlesadd1141                  = array.new<Candle>(0)
var BOSdata bosdataadd1141                   = BOSdata.new()
htfadd1141.settings                 := SettingsHTFadd1141
htfadd1141.candles                  := candlesadd1141
htfadd1141.bosdata                  := bosdataadd1141
var CandleSet htfadd1142                     = CandleSet.new()
var CandleSettings SettingsHTFadd1142        = CandleSettings.new(htf='1142',htfint=1142,max_memory=3)
var Candle[] candlesadd1142                  = array.new<Candle>(0)
var BOSdata bosdataadd1142                   = BOSdata.new()
htfadd1142.settings                 := SettingsHTFadd1142
htfadd1142.candles                  := candlesadd1142
htfadd1142.bosdata                  := bosdataadd1142
var CandleSet htfadd1143                     = CandleSet.new()
var CandleSettings SettingsHTFadd1143        = CandleSettings.new(htf='1143',htfint=1143,max_memory=3)
var Candle[] candlesadd1143                  = array.new<Candle>(0)
var BOSdata bosdataadd1143                   = BOSdata.new()
htfadd1143.settings                 := SettingsHTFadd1143
htfadd1143.candles                  := candlesadd1143
htfadd1143.bosdata                  := bosdataadd1143
var CandleSet htfadd1144                     = CandleSet.new()
var CandleSettings SettingsHTFadd1144        = CandleSettings.new(htf='1144',htfint=1144,max_memory=3)
var Candle[] candlesadd1144                  = array.new<Candle>(0)
var BOSdata bosdataadd1144                   = BOSdata.new()
htfadd1144.settings                 := SettingsHTFadd1144
htfadd1144.candles                  := candlesadd1144
htfadd1144.bosdata                  := bosdataadd1144
var CandleSet htfadd1145                     = CandleSet.new()
var CandleSettings SettingsHTFadd1145        = CandleSettings.new(htf='1145',htfint=1145,max_memory=3)
var Candle[] candlesadd1145                  = array.new<Candle>(0)
var BOSdata bosdataadd1145                   = BOSdata.new()
htfadd1145.settings                 := SettingsHTFadd1145
htfadd1145.candles                  := candlesadd1145
htfadd1145.bosdata                  := bosdataadd1145
var CandleSet htfadd1146                     = CandleSet.new()
var CandleSettings SettingsHTFadd1146        = CandleSettings.new(htf='1146',htfint=1146,max_memory=3)
var Candle[] candlesadd1146                  = array.new<Candle>(0)
var BOSdata bosdataadd1146                   = BOSdata.new()
htfadd1146.settings                 := SettingsHTFadd1146
htfadd1146.candles                  := candlesadd1146
htfadd1146.bosdata                  := bosdataadd1146
var CandleSet htfadd1147                     = CandleSet.new()
var CandleSettings SettingsHTFadd1147        = CandleSettings.new(htf='1147',htfint=1147,max_memory=3)
var Candle[] candlesadd1147                  = array.new<Candle>(0)
var BOSdata bosdataadd1147                   = BOSdata.new()
htfadd1147.settings                 := SettingsHTFadd1147
htfadd1147.candles                  := candlesadd1147
htfadd1147.bosdata                  := bosdataadd1147
var CandleSet htfadd1148                     = CandleSet.new()
var CandleSettings SettingsHTFadd1148        = CandleSettings.new(htf='1148',htfint=1148,max_memory=3)
var Candle[] candlesadd1148                  = array.new<Candle>(0)
var BOSdata bosdataadd1148                   = BOSdata.new()
htfadd1148.settings                 := SettingsHTFadd1148
htfadd1148.candles                  := candlesadd1148
htfadd1148.bosdata                  := bosdataadd1148
var CandleSet htfadd1149                     = CandleSet.new()
var CandleSettings SettingsHTFadd1149        = CandleSettings.new(htf='1149',htfint=1149,max_memory=3)
var Candle[] candlesadd1149                  = array.new<Candle>(0)
var BOSdata bosdataadd1149                   = BOSdata.new()
htfadd1149.settings                 := SettingsHTFadd1149
htfadd1149.candles                  := candlesadd1149
htfadd1149.bosdata                  := bosdataadd1149
var CandleSet htfadd1150                     = CandleSet.new()
var CandleSettings SettingsHTFadd1150        = CandleSettings.new(htf='1150',htfint=1150,max_memory=3)
var Candle[] candlesadd1150                  = array.new<Candle>(0)
var BOSdata bosdataadd1150                   = BOSdata.new()
htfadd1150.settings                 := SettingsHTFadd1150
htfadd1150.candles                  := candlesadd1150
htfadd1150.bosdata                  := bosdataadd1150
var CandleSet htfadd1151                     = CandleSet.new()
var CandleSettings SettingsHTFadd1151        = CandleSettings.new(htf='1151',htfint=1151,max_memory=3)
var Candle[] candlesadd1151                  = array.new<Candle>(0)
var BOSdata bosdataadd1151                   = BOSdata.new()
htfadd1151.settings                 := SettingsHTFadd1151
htfadd1151.candles                  := candlesadd1151
htfadd1151.bosdata                  := bosdataadd1151
var CandleSet htfadd1152                     = CandleSet.new()
var CandleSettings SettingsHTFadd1152        = CandleSettings.new(htf='1152',htfint=1152,max_memory=3)
var Candle[] candlesadd1152                  = array.new<Candle>(0)
var BOSdata bosdataadd1152                   = BOSdata.new()
htfadd1152.settings                 := SettingsHTFadd1152
htfadd1152.candles                  := candlesadd1152
htfadd1152.bosdata                  := bosdataadd1152
var CandleSet htfadd1153                     = CandleSet.new()
var CandleSettings SettingsHTFadd1153        = CandleSettings.new(htf='1153',htfint=1153,max_memory=3)
var Candle[] candlesadd1153                  = array.new<Candle>(0)
var BOSdata bosdataadd1153                   = BOSdata.new()
htfadd1153.settings                 := SettingsHTFadd1153
htfadd1153.candles                  := candlesadd1153
htfadd1153.bosdata                  := bosdataadd1153
var CandleSet htfadd1154                     = CandleSet.new()
var CandleSettings SettingsHTFadd1154        = CandleSettings.new(htf='1154',htfint=1154,max_memory=3)
var Candle[] candlesadd1154                  = array.new<Candle>(0)
var BOSdata bosdataadd1154                   = BOSdata.new()
htfadd1154.settings                 := SettingsHTFadd1154
htfadd1154.candles                  := candlesadd1154
htfadd1154.bosdata                  := bosdataadd1154
var CandleSet htfadd1155                     = CandleSet.new()
var CandleSettings SettingsHTFadd1155        = CandleSettings.new(htf='1155',htfint=1155,max_memory=3)
var Candle[] candlesadd1155                  = array.new<Candle>(0)
var BOSdata bosdataadd1155                   = BOSdata.new()
htfadd1155.settings                 := SettingsHTFadd1155
htfadd1155.candles                  := candlesadd1155
htfadd1155.bosdata                  := bosdataadd1155
var CandleSet htfadd1156                     = CandleSet.new()
var CandleSettings SettingsHTFadd1156        = CandleSettings.new(htf='1156',htfint=1156,max_memory=3)
var Candle[] candlesadd1156                  = array.new<Candle>(0)
var BOSdata bosdataadd1156                   = BOSdata.new()
htfadd1156.settings                 := SettingsHTFadd1156
htfadd1156.candles                  := candlesadd1156
htfadd1156.bosdata                  := bosdataadd1156
var CandleSet htfadd1157                     = CandleSet.new()
var CandleSettings SettingsHTFadd1157        = CandleSettings.new(htf='1157',htfint=1157,max_memory=3)
var Candle[] candlesadd1157                  = array.new<Candle>(0)
var BOSdata bosdataadd1157                   = BOSdata.new()
htfadd1157.settings                 := SettingsHTFadd1157
htfadd1157.candles                  := candlesadd1157
htfadd1157.bosdata                  := bosdataadd1157
var CandleSet htfadd1158                     = CandleSet.new()
var CandleSettings SettingsHTFadd1158        = CandleSettings.new(htf='1158',htfint=1158,max_memory=3)
var Candle[] candlesadd1158                  = array.new<Candle>(0)
var BOSdata bosdataadd1158                   = BOSdata.new()
htfadd1158.settings                 := SettingsHTFadd1158
htfadd1158.candles                  := candlesadd1158
htfadd1158.bosdata                  := bosdataadd1158
var CandleSet htfadd1159                     = CandleSet.new()
var CandleSettings SettingsHTFadd1159        = CandleSettings.new(htf='1159',htfint=1159,max_memory=3)
var Candle[] candlesadd1159                  = array.new<Candle>(0)
var BOSdata bosdataadd1159                   = BOSdata.new()
htfadd1159.settings                 := SettingsHTFadd1159
htfadd1159.candles                  := candlesadd1159
htfadd1159.bosdata                  := bosdataadd1159
var CandleSet htfadd1160                     = CandleSet.new()
var CandleSettings SettingsHTFadd1160        = CandleSettings.new(htf='1160',htfint=1160,max_memory=3)
var Candle[] candlesadd1160                  = array.new<Candle>(0)
var BOSdata bosdataadd1160                   = BOSdata.new()
htfadd1160.settings                 := SettingsHTFadd1160
htfadd1160.candles                  := candlesadd1160
htfadd1160.bosdata                  := bosdataadd1160
var CandleSet htfadd1161                     = CandleSet.new()
var CandleSettings SettingsHTFadd1161        = CandleSettings.new(htf='1161',htfint=1161,max_memory=3)
var Candle[] candlesadd1161                  = array.new<Candle>(0)
var BOSdata bosdataadd1161                   = BOSdata.new()
htfadd1161.settings                 := SettingsHTFadd1161
htfadd1161.candles                  := candlesadd1161
htfadd1161.bosdata                  := bosdataadd1161
var CandleSet htfadd1162                     = CandleSet.new()
var CandleSettings SettingsHTFadd1162        = CandleSettings.new(htf='1162',htfint=1162,max_memory=3)
var Candle[] candlesadd1162                  = array.new<Candle>(0)
var BOSdata bosdataadd1162                   = BOSdata.new()
htfadd1162.settings                 := SettingsHTFadd1162
htfadd1162.candles                  := candlesadd1162
htfadd1162.bosdata                  := bosdataadd1162
var CandleSet htfadd1163                     = CandleSet.new()
var CandleSettings SettingsHTFadd1163        = CandleSettings.new(htf='1163',htfint=1163,max_memory=3)
var Candle[] candlesadd1163                  = array.new<Candle>(0)
var BOSdata bosdataadd1163                   = BOSdata.new()
htfadd1163.settings                 := SettingsHTFadd1163
htfadd1163.candles                  := candlesadd1163
htfadd1163.bosdata                  := bosdataadd1163
var CandleSet htfadd1164                     = CandleSet.new()
var CandleSettings SettingsHTFadd1164        = CandleSettings.new(htf='1164',htfint=1164,max_memory=3)
var Candle[] candlesadd1164                  = array.new<Candle>(0)
var BOSdata bosdataadd1164                   = BOSdata.new()
htfadd1164.settings                 := SettingsHTFadd1164
htfadd1164.candles                  := candlesadd1164
htfadd1164.bosdata                  := bosdataadd1164
var CandleSet htfadd1165                     = CandleSet.new()
var CandleSettings SettingsHTFadd1165        = CandleSettings.new(htf='1165',htfint=1165,max_memory=3)
var Candle[] candlesadd1165                  = array.new<Candle>(0)
var BOSdata bosdataadd1165                   = BOSdata.new()
htfadd1165.settings                 := SettingsHTFadd1165
htfadd1165.candles                  := candlesadd1165
htfadd1165.bosdata                  := bosdataadd1165
var CandleSet htfadd1166                     = CandleSet.new()
var CandleSettings SettingsHTFadd1166        = CandleSettings.new(htf='1166',htfint=1166,max_memory=3)
var Candle[] candlesadd1166                  = array.new<Candle>(0)
var BOSdata bosdataadd1166                   = BOSdata.new()
htfadd1166.settings                 := SettingsHTFadd1166
htfadd1166.candles                  := candlesadd1166
htfadd1166.bosdata                  := bosdataadd1166
var CandleSet htfadd1167                     = CandleSet.new()
var CandleSettings SettingsHTFadd1167        = CandleSettings.new(htf='1167',htfint=1167,max_memory=3)
var Candle[] candlesadd1167                  = array.new<Candle>(0)
var BOSdata bosdataadd1167                   = BOSdata.new()
htfadd1167.settings                 := SettingsHTFadd1167
htfadd1167.candles                  := candlesadd1167
htfadd1167.bosdata                  := bosdataadd1167
var CandleSet htfadd1168                     = CandleSet.new()
var CandleSettings SettingsHTFadd1168        = CandleSettings.new(htf='1168',htfint=1168,max_memory=3)
var Candle[] candlesadd1168                  = array.new<Candle>(0)
var BOSdata bosdataadd1168                   = BOSdata.new()
htfadd1168.settings                 := SettingsHTFadd1168
htfadd1168.candles                  := candlesadd1168
htfadd1168.bosdata                  := bosdataadd1168
var CandleSet htfadd1169                     = CandleSet.new()
var CandleSettings SettingsHTFadd1169        = CandleSettings.new(htf='1169',htfint=1169,max_memory=3)
var Candle[] candlesadd1169                  = array.new<Candle>(0)
var BOSdata bosdataadd1169                   = BOSdata.new()
htfadd1169.settings                 := SettingsHTFadd1169
htfadd1169.candles                  := candlesadd1169
htfadd1169.bosdata                  := bosdataadd1169
var CandleSet htfadd1170                     = CandleSet.new()
var CandleSettings SettingsHTFadd1170        = CandleSettings.new(htf='1170',htfint=1170,max_memory=3)
var Candle[] candlesadd1170                  = array.new<Candle>(0)
var BOSdata bosdataadd1170                   = BOSdata.new()
htfadd1170.settings                 := SettingsHTFadd1170
htfadd1170.candles                  := candlesadd1170
htfadd1170.bosdata                  := bosdataadd1170

htfadd1080.Monitor().BOSJudge()
htfadd1081.Monitor().BOSJudge()
htfadd1082.Monitor().BOSJudge()
htfadd1083.Monitor().BOSJudge()
htfadd1084.Monitor().BOSJudge()
htfadd1085.Monitor().BOSJudge()
htfadd1086.Monitor().BOSJudge()
htfadd1087.Monitor().BOSJudge()
htfadd1088.Monitor().BOSJudge()
htfadd1089.Monitor().BOSJudge()
htfadd1090.Monitor().BOSJudge()
htfadd1091.Monitor().BOSJudge()
htfadd1092.Monitor().BOSJudge()
htfadd1093.Monitor().BOSJudge()
htfadd1094.Monitor().BOSJudge()
htfadd1095.Monitor().BOSJudge()
htfadd1096.Monitor().BOSJudge()
htfadd1097.Monitor().BOSJudge()
htfadd1098.Monitor().BOSJudge()
htfadd1099.Monitor().BOSJudge()
htfadd1100.Monitor().BOSJudge()
htfadd1101.Monitor().BOSJudge()
htfadd1102.Monitor().BOSJudge()
htfadd1103.Monitor().BOSJudge()
htfadd1104.Monitor().BOSJudge()
htfadd1105.Monitor().BOSJudge()
htfadd1106.Monitor().BOSJudge()
htfadd1107.Monitor().BOSJudge()
htfadd1108.Monitor().BOSJudge()
htfadd1109.Monitor().BOSJudge()
htfadd1110.Monitor().BOSJudge()
htfadd1111.Monitor().BOSJudge()
htfadd1112.Monitor().BOSJudge()
htfadd1113.Monitor().BOSJudge()
htfadd1114.Monitor().BOSJudge()
htfadd1115.Monitor().BOSJudge()
htfadd1116.Monitor().BOSJudge()
htfadd1117.Monitor().BOSJudge()
htfadd1118.Monitor().BOSJudge()
htfadd1119.Monitor().BOSJudge()
htfadd1120.Monitor().BOSJudge()
htfadd1121.Monitor().BOSJudge()
htfadd1122.Monitor().BOSJudge()
htfadd1123.Monitor().BOSJudge()
htfadd1124.Monitor().BOSJudge()
htfadd1125.Monitor().BOSJudge()
htfadd1126.Monitor().BOSJudge()
htfadd1127.Monitor().BOSJudge()
htfadd1128.Monitor().BOSJudge()
htfadd1129.Monitor().BOSJudge()
htfadd1130.Monitor().BOSJudge()
htfadd1131.Monitor().BOSJudge()
htfadd1132.Monitor().BOSJudge()
htfadd1133.Monitor().BOSJudge()
htfadd1134.Monitor().BOSJudge()
htfadd1135.Monitor().BOSJudge()
htfadd1136.Monitor().BOSJudge()
htfadd1137.Monitor().BOSJudge()
htfadd1138.Monitor().BOSJudge()
htfadd1139.Monitor().BOSJudge()
htfadd1140.Monitor().BOSJudge()
htfadd1141.Monitor().BOSJudge()
htfadd1142.Monitor().BOSJudge()
htfadd1143.Monitor().BOSJudge()
htfadd1144.Monitor().BOSJudge()
htfadd1145.Monitor().BOSJudge()
htfadd1146.Monitor().BOSJudge()
htfadd1147.Monitor().BOSJudge()
htfadd1148.Monitor().BOSJudge()
htfadd1149.Monitor().BOSJudge()
htfadd1150.Monitor().BOSJudge()
htfadd1151.Monitor().BOSJudge()
htfadd1152.Monitor().BOSJudge()
htfadd1153.Monitor().BOSJudge()
htfadd1154.Monitor().BOSJudge()
htfadd1155.Monitor().BOSJudge()
htfadd1156.Monitor().BOSJudge()
htfadd1157.Monitor().BOSJudge()
htfadd1158.Monitor().BOSJudge()
htfadd1159.Monitor().BOSJudge()
htfadd1160.Monitor().BOSJudge()
htfadd1161.Monitor().BOSJudge()
htfadd1162.Monitor().BOSJudge()
htfadd1163.Monitor().BOSJudge()
htfadd1164.Monitor().BOSJudge()
htfadd1165.Monitor().BOSJudge()
htfadd1166.Monitor().BOSJudge()
htfadd1167.Monitor().BOSJudge()
htfadd1168.Monitor().BOSJudge()
htfadd1169.Monitor().BOSJudge()
htfadd1170.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd1080)
    LowestsbuSet(lowestsbu, htfadd1080)
    HighestsbdSet(highestsbd, htfadd1081)
    LowestsbuSet(lowestsbu, htfadd1081)
    HighestsbdSet(highestsbd, htfadd1082)
    LowestsbuSet(lowestsbu, htfadd1082)
    HighestsbdSet(highestsbd, htfadd1083)
    LowestsbuSet(lowestsbu, htfadd1083)
    HighestsbdSet(highestsbd, htfadd1084)
    LowestsbuSet(lowestsbu, htfadd1084)
    HighestsbdSet(highestsbd, htfadd1085)
    LowestsbuSet(lowestsbu, htfadd1085)
    HighestsbdSet(highestsbd, htfadd1086)
    LowestsbuSet(lowestsbu, htfadd1086)
    HighestsbdSet(highestsbd, htfadd1087)
    LowestsbuSet(lowestsbu, htfadd1087)
    HighestsbdSet(highestsbd, htfadd1088)
    LowestsbuSet(lowestsbu, htfadd1088)
    HighestsbdSet(highestsbd, htfadd1089)
    LowestsbuSet(lowestsbu, htfadd1089)
    HighestsbdSet(highestsbd, htfadd1090)
    LowestsbuSet(lowestsbu, htfadd1090)
    HighestsbdSet(highestsbd, htfadd1091)
    LowestsbuSet(lowestsbu, htfadd1091)
    HighestsbdSet(highestsbd, htfadd1092)
    LowestsbuSet(lowestsbu, htfadd1092)
    HighestsbdSet(highestsbd, htfadd1093)
    LowestsbuSet(lowestsbu, htfadd1093)
    HighestsbdSet(highestsbd, htfadd1094)
    LowestsbuSet(lowestsbu, htfadd1094)
    HighestsbdSet(highestsbd, htfadd1095)
    LowestsbuSet(lowestsbu, htfadd1095)
    HighestsbdSet(highestsbd, htfadd1096)
    LowestsbuSet(lowestsbu, htfadd1096)
    HighestsbdSet(highestsbd, htfadd1097)
    LowestsbuSet(lowestsbu, htfadd1097)
    HighestsbdSet(highestsbd, htfadd1098)
    LowestsbuSet(lowestsbu, htfadd1098)
    HighestsbdSet(highestsbd, htfadd1099)
    LowestsbuSet(lowestsbu, htfadd1099)
    HighestsbdSet(highestsbd, htfadd1100)
    LowestsbuSet(lowestsbu, htfadd1100)
    HighestsbdSet(highestsbd, htfadd1101)
    LowestsbuSet(lowestsbu, htfadd1101)
    HighestsbdSet(highestsbd, htfadd1102)
    LowestsbuSet(lowestsbu, htfadd1102)
    HighestsbdSet(highestsbd, htfadd1103)
    LowestsbuSet(lowestsbu, htfadd1103)
    HighestsbdSet(highestsbd, htfadd1104)
    LowestsbuSet(lowestsbu, htfadd1104)
    HighestsbdSet(highestsbd, htfadd1105)
    LowestsbuSet(lowestsbu, htfadd1105)
    HighestsbdSet(highestsbd, htfadd1106)
    LowestsbuSet(lowestsbu, htfadd1106)
    HighestsbdSet(highestsbd, htfadd1107)
    LowestsbuSet(lowestsbu, htfadd1107)
    HighestsbdSet(highestsbd, htfadd1108)
    LowestsbuSet(lowestsbu, htfadd1108)
    HighestsbdSet(highestsbd, htfadd1109)
    LowestsbuSet(lowestsbu, htfadd1109)
    HighestsbdSet(highestsbd, htfadd1110)
    LowestsbuSet(lowestsbu, htfadd1110)
    HighestsbdSet(highestsbd, htfadd1111)
    LowestsbuSet(lowestsbu, htfadd1111)
    HighestsbdSet(highestsbd, htfadd1112)
    LowestsbuSet(lowestsbu, htfadd1112)
    HighestsbdSet(highestsbd, htfadd1113)
    LowestsbuSet(lowestsbu, htfadd1113)
    HighestsbdSet(highestsbd, htfadd1114)
    LowestsbuSet(lowestsbu, htfadd1114)
    HighestsbdSet(highestsbd, htfadd1115)
    LowestsbuSet(lowestsbu, htfadd1115)
    HighestsbdSet(highestsbd, htfadd1116)
    LowestsbuSet(lowestsbu, htfadd1116)
    HighestsbdSet(highestsbd, htfadd1117)
    LowestsbuSet(lowestsbu, htfadd1117)
    HighestsbdSet(highestsbd, htfadd1118)
    LowestsbuSet(lowestsbu, htfadd1118)
    HighestsbdSet(highestsbd, htfadd1119)
    LowestsbuSet(lowestsbu, htfadd1119)
    HighestsbdSet(highestsbd, htfadd1120)
    LowestsbuSet(lowestsbu, htfadd1120)
    HighestsbdSet(highestsbd, htfadd1121)
    LowestsbuSet(lowestsbu, htfadd1121)
    HighestsbdSet(highestsbd, htfadd1122)
    LowestsbuSet(lowestsbu, htfadd1122)
    HighestsbdSet(highestsbd, htfadd1123)
    LowestsbuSet(lowestsbu, htfadd1123)
    HighestsbdSet(highestsbd, htfadd1124)
    LowestsbuSet(lowestsbu, htfadd1124)
    HighestsbdSet(highestsbd, htfadd1125)
    LowestsbuSet(lowestsbu, htfadd1125)
    HighestsbdSet(highestsbd, htfadd1126)
    LowestsbuSet(lowestsbu, htfadd1126)
    HighestsbdSet(highestsbd, htfadd1127)
    LowestsbuSet(lowestsbu, htfadd1127)
    HighestsbdSet(highestsbd, htfadd1128)
    LowestsbuSet(lowestsbu, htfadd1128)
    HighestsbdSet(highestsbd, htfadd1129)
    LowestsbuSet(lowestsbu, htfadd1129)
    HighestsbdSet(highestsbd, htfadd1130)
    LowestsbuSet(lowestsbu, htfadd1130)
    HighestsbdSet(highestsbd, htfadd1131)
    LowestsbuSet(lowestsbu, htfadd1131)
    HighestsbdSet(highestsbd, htfadd1132)
    LowestsbuSet(lowestsbu, htfadd1132)
    HighestsbdSet(highestsbd, htfadd1133)
    LowestsbuSet(lowestsbu, htfadd1133)
    HighestsbdSet(highestsbd, htfadd1134)
    LowestsbuSet(lowestsbu, htfadd1134)
    HighestsbdSet(highestsbd, htfadd1135)
    LowestsbuSet(lowestsbu, htfadd1135)
    HighestsbdSet(highestsbd, htfadd1136)
    LowestsbuSet(lowestsbu, htfadd1136)
    HighestsbdSet(highestsbd, htfadd1137)
    LowestsbuSet(lowestsbu, htfadd1137)
    HighestsbdSet(highestsbd, htfadd1138)
    LowestsbuSet(lowestsbu, htfadd1138)
    HighestsbdSet(highestsbd, htfadd1139)
    LowestsbuSet(lowestsbu, htfadd1139)
    HighestsbdSet(highestsbd, htfadd1140)
    LowestsbuSet(lowestsbu, htfadd1140)
    HighestsbdSet(highestsbd, htfadd1141)
    LowestsbuSet(lowestsbu, htfadd1141)
    HighestsbdSet(highestsbd, htfadd1142)
    LowestsbuSet(lowestsbu, htfadd1142)
    HighestsbdSet(highestsbd, htfadd1143)
    LowestsbuSet(lowestsbu, htfadd1143)
    HighestsbdSet(highestsbd, htfadd1144)
    LowestsbuSet(lowestsbu, htfadd1144)
    HighestsbdSet(highestsbd, htfadd1145)
    LowestsbuSet(lowestsbu, htfadd1145)
    HighestsbdSet(highestsbd, htfadd1146)
    LowestsbuSet(lowestsbu, htfadd1146)
    HighestsbdSet(highestsbd, htfadd1147)
    LowestsbuSet(lowestsbu, htfadd1147)
    HighestsbdSet(highestsbd, htfadd1148)
    LowestsbuSet(lowestsbu, htfadd1148)
    HighestsbdSet(highestsbd, htfadd1149)
    LowestsbuSet(lowestsbu, htfadd1149)
    HighestsbdSet(highestsbd, htfadd1150)
    LowestsbuSet(lowestsbu, htfadd1150)
    HighestsbdSet(highestsbd, htfadd1151)
    LowestsbuSet(lowestsbu, htfadd1151)
    HighestsbdSet(highestsbd, htfadd1152)
    LowestsbuSet(lowestsbu, htfadd1152)
    HighestsbdSet(highestsbd, htfadd1153)
    LowestsbuSet(lowestsbu, htfadd1153)
    HighestsbdSet(highestsbd, htfadd1154)
    LowestsbuSet(lowestsbu, htfadd1154)
    HighestsbdSet(highestsbd, htfadd1155)
    LowestsbuSet(lowestsbu, htfadd1155)
    HighestsbdSet(highestsbd, htfadd1156)
    LowestsbuSet(lowestsbu, htfadd1156)
    HighestsbdSet(highestsbd, htfadd1157)
    LowestsbuSet(lowestsbu, htfadd1157)
    HighestsbdSet(highestsbd, htfadd1158)
    LowestsbuSet(lowestsbu, htfadd1158)
    HighestsbdSet(highestsbd, htfadd1159)
    LowestsbuSet(lowestsbu, htfadd1159)
    HighestsbdSet(highestsbd, htfadd1160)
    LowestsbuSet(lowestsbu, htfadd1160)
    HighestsbdSet(highestsbd, htfadd1161)
    LowestsbuSet(lowestsbu, htfadd1161)
    HighestsbdSet(highestsbd, htfadd1162)
    LowestsbuSet(lowestsbu, htfadd1162)
    HighestsbdSet(highestsbd, htfadd1163)
    LowestsbuSet(lowestsbu, htfadd1163)
    HighestsbdSet(highestsbd, htfadd1164)
    LowestsbuSet(lowestsbu, htfadd1164)
    HighestsbdSet(highestsbd, htfadd1165)
    LowestsbuSet(lowestsbu, htfadd1165)
    HighestsbdSet(highestsbd, htfadd1166)
    LowestsbuSet(lowestsbu, htfadd1166)
    HighestsbdSet(highestsbd, htfadd1167)
    LowestsbuSet(lowestsbu, htfadd1167)
    HighestsbdSet(highestsbd, htfadd1168)
    LowestsbuSet(lowestsbu, htfadd1168)
    HighestsbdSet(highestsbd, htfadd1169)
    LowestsbuSet(lowestsbu, htfadd1169)
    HighestsbdSet(highestsbd, htfadd1170)
    LowestsbuSet(lowestsbu, htfadd1170)

    htfshadow.Shadowing(htfadd1080).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1081).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1082).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1083).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1084).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1085).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1086).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1087).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1088).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1089).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1090).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1091).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1092).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1093).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1094).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1095).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1096).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1097).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1098).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1099).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1100).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1101).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1102).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1103).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1104).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1105).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1106).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1107).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1108).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1109).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1110).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1111).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1112).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1113).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1114).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1115).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1116).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1117).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1118).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1119).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1120).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1121).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1122).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1123).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1124).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1125).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1126).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1127).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1128).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1129).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1130).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1131).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1132).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1133).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1134).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1135).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1136).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1137).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1138).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1139).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1140).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1141).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1142).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1143).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1144).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1145).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1146).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1147).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1148).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1149).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1150).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1151).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1152).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1153).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1154).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1155).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1156).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1157).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1158).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1159).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1160).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1161).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1162).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1163).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1164).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1165).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1166).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1167).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1168).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1169).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1170).Monitor_Est().BOSJudge()
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


