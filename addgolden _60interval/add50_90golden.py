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

var CandleSet htfadd50                     = CandleSet.new()
var CandleSettings SettingsHTFadd50        = CandleSettings.new(htf='50',htfint=50,max_memory=3)
var Candle[] candlesadd50                  = array.new<Candle>(0)
var BOSdata bosdataadd50                   = BOSdata.new()
htfadd50.settings                 := SettingsHTFadd50
htfadd50.candles                  := candlesadd50
htfadd50.bosdata                  := bosdataadd50
var CandleSet htfadd51                     = CandleSet.new()
var CandleSettings SettingsHTFadd51        = CandleSettings.new(htf='51',htfint=51,max_memory=3)
var Candle[] candlesadd51                  = array.new<Candle>(0)
var BOSdata bosdataadd51                   = BOSdata.new()
htfadd51.settings                 := SettingsHTFadd51
htfadd51.candles                  := candlesadd51
htfadd51.bosdata                  := bosdataadd51
var CandleSet htfadd52                     = CandleSet.new()
var CandleSettings SettingsHTFadd52        = CandleSettings.new(htf='52',htfint=52,max_memory=3)
var Candle[] candlesadd52                  = array.new<Candle>(0)
var BOSdata bosdataadd52                   = BOSdata.new()
htfadd52.settings                 := SettingsHTFadd52
htfadd52.candles                  := candlesadd52
htfadd52.bosdata                  := bosdataadd52
var CandleSet htfadd53                     = CandleSet.new()
var CandleSettings SettingsHTFadd53        = CandleSettings.new(htf='53',htfint=53,max_memory=3)
var Candle[] candlesadd53                  = array.new<Candle>(0)
var BOSdata bosdataadd53                   = BOSdata.new()
htfadd53.settings                 := SettingsHTFadd53
htfadd53.candles                  := candlesadd53
htfadd53.bosdata                  := bosdataadd53
var CandleSet htfadd54                     = CandleSet.new()
var CandleSettings SettingsHTFadd54        = CandleSettings.new(htf='54',htfint=54,max_memory=3)
var Candle[] candlesadd54                  = array.new<Candle>(0)
var BOSdata bosdataadd54                   = BOSdata.new()
htfadd54.settings                 := SettingsHTFadd54
htfadd54.candles                  := candlesadd54
htfadd54.bosdata                  := bosdataadd54
var CandleSet htfadd55                     = CandleSet.new()
var CandleSettings SettingsHTFadd55        = CandleSettings.new(htf='55',htfint=55,max_memory=3)
var Candle[] candlesadd55                  = array.new<Candle>(0)
var BOSdata bosdataadd55                   = BOSdata.new()
htfadd55.settings                 := SettingsHTFadd55
htfadd55.candles                  := candlesadd55
htfadd55.bosdata                  := bosdataadd55
var CandleSet htfadd56                     = CandleSet.new()
var CandleSettings SettingsHTFadd56        = CandleSettings.new(htf='56',htfint=56,max_memory=3)
var Candle[] candlesadd56                  = array.new<Candle>(0)
var BOSdata bosdataadd56                   = BOSdata.new()
htfadd56.settings                 := SettingsHTFadd56
htfadd56.candles                  := candlesadd56
htfadd56.bosdata                  := bosdataadd56
var CandleSet htfadd57                     = CandleSet.new()
var CandleSettings SettingsHTFadd57        = CandleSettings.new(htf='57',htfint=57,max_memory=3)
var Candle[] candlesadd57                  = array.new<Candle>(0)
var BOSdata bosdataadd57                   = BOSdata.new()
htfadd57.settings                 := SettingsHTFadd57
htfadd57.candles                  := candlesadd57
htfadd57.bosdata                  := bosdataadd57
var CandleSet htfadd58                     = CandleSet.new()
var CandleSettings SettingsHTFadd58        = CandleSettings.new(htf='58',htfint=58,max_memory=3)
var Candle[] candlesadd58                  = array.new<Candle>(0)
var BOSdata bosdataadd58                   = BOSdata.new()
htfadd58.settings                 := SettingsHTFadd58
htfadd58.candles                  := candlesadd58
htfadd58.bosdata                  := bosdataadd58
var CandleSet htfadd59                     = CandleSet.new()
var CandleSettings SettingsHTFadd59        = CandleSettings.new(htf='59',htfint=59,max_memory=3)
var Candle[] candlesadd59                  = array.new<Candle>(0)
var BOSdata bosdataadd59                   = BOSdata.new()
htfadd59.settings                 := SettingsHTFadd59
htfadd59.candles                  := candlesadd59
htfadd59.bosdata                  := bosdataadd59
var CandleSet htfadd60                     = CandleSet.new()
var CandleSettings SettingsHTFadd60        = CandleSettings.new(htf='60',htfint=60,max_memory=3)
var Candle[] candlesadd60                  = array.new<Candle>(0)
var BOSdata bosdataadd60                   = BOSdata.new()
htfadd60.settings                 := SettingsHTFadd60
htfadd60.candles                  := candlesadd60
htfadd60.bosdata                  := bosdataadd60
var CandleSet htfadd61                     = CandleSet.new()
var CandleSettings SettingsHTFadd61        = CandleSettings.new(htf='61',htfint=61,max_memory=3)
var Candle[] candlesadd61                  = array.new<Candle>(0)
var BOSdata bosdataadd61                   = BOSdata.new()
htfadd61.settings                 := SettingsHTFadd61
htfadd61.candles                  := candlesadd61
htfadd61.bosdata                  := bosdataadd61
var CandleSet htfadd62                     = CandleSet.new()
var CandleSettings SettingsHTFadd62        = CandleSettings.new(htf='62',htfint=62,max_memory=3)
var Candle[] candlesadd62                  = array.new<Candle>(0)
var BOSdata bosdataadd62                   = BOSdata.new()
htfadd62.settings                 := SettingsHTFadd62
htfadd62.candles                  := candlesadd62
htfadd62.bosdata                  := bosdataadd62
var CandleSet htfadd63                     = CandleSet.new()
var CandleSettings SettingsHTFadd63        = CandleSettings.new(htf='63',htfint=63,max_memory=3)
var Candle[] candlesadd63                  = array.new<Candle>(0)
var BOSdata bosdataadd63                   = BOSdata.new()
htfadd63.settings                 := SettingsHTFadd63
htfadd63.candles                  := candlesadd63
htfadd63.bosdata                  := bosdataadd63
var CandleSet htfadd64                     = CandleSet.new()
var CandleSettings SettingsHTFadd64        = CandleSettings.new(htf='64',htfint=64,max_memory=3)
var Candle[] candlesadd64                  = array.new<Candle>(0)
var BOSdata bosdataadd64                   = BOSdata.new()
htfadd64.settings                 := SettingsHTFadd64
htfadd64.candles                  := candlesadd64
htfadd64.bosdata                  := bosdataadd64
var CandleSet htfadd65                     = CandleSet.new()
var CandleSettings SettingsHTFadd65        = CandleSettings.new(htf='65',htfint=65,max_memory=3)
var Candle[] candlesadd65                  = array.new<Candle>(0)
var BOSdata bosdataadd65                   = BOSdata.new()
htfadd65.settings                 := SettingsHTFadd65
htfadd65.candles                  := candlesadd65
htfadd65.bosdata                  := bosdataadd65
var CandleSet htfadd66                     = CandleSet.new()
var CandleSettings SettingsHTFadd66        = CandleSettings.new(htf='66',htfint=66,max_memory=3)
var Candle[] candlesadd66                  = array.new<Candle>(0)
var BOSdata bosdataadd66                   = BOSdata.new()
htfadd66.settings                 := SettingsHTFadd66
htfadd66.candles                  := candlesadd66
htfadd66.bosdata                  := bosdataadd66
var CandleSet htfadd67                     = CandleSet.new()
var CandleSettings SettingsHTFadd67        = CandleSettings.new(htf='67',htfint=67,max_memory=3)
var Candle[] candlesadd67                  = array.new<Candle>(0)
var BOSdata bosdataadd67                   = BOSdata.new()
htfadd67.settings                 := SettingsHTFadd67
htfadd67.candles                  := candlesadd67
htfadd67.bosdata                  := bosdataadd67
var CandleSet htfadd68                     = CandleSet.new()
var CandleSettings SettingsHTFadd68        = CandleSettings.new(htf='68',htfint=68,max_memory=3)
var Candle[] candlesadd68                  = array.new<Candle>(0)
var BOSdata bosdataadd68                   = BOSdata.new()
htfadd68.settings                 := SettingsHTFadd68
htfadd68.candles                  := candlesadd68
htfadd68.bosdata                  := bosdataadd68
var CandleSet htfadd69                     = CandleSet.new()
var CandleSettings SettingsHTFadd69        = CandleSettings.new(htf='69',htfint=69,max_memory=3)
var Candle[] candlesadd69                  = array.new<Candle>(0)
var BOSdata bosdataadd69                   = BOSdata.new()
htfadd69.settings                 := SettingsHTFadd69
htfadd69.candles                  := candlesadd69
htfadd69.bosdata                  := bosdataadd69
var CandleSet htfadd70                     = CandleSet.new()
var CandleSettings SettingsHTFadd70        = CandleSettings.new(htf='70',htfint=70,max_memory=3)
var Candle[] candlesadd70                  = array.new<Candle>(0)
var BOSdata bosdataadd70                   = BOSdata.new()
htfadd70.settings                 := SettingsHTFadd70
htfadd70.candles                  := candlesadd70
htfadd70.bosdata                  := bosdataadd70
var CandleSet htfadd71                     = CandleSet.new()
var CandleSettings SettingsHTFadd71        = CandleSettings.new(htf='71',htfint=71,max_memory=3)
var Candle[] candlesadd71                  = array.new<Candle>(0)
var BOSdata bosdataadd71                   = BOSdata.new()
htfadd71.settings                 := SettingsHTFadd71
htfadd71.candles                  := candlesadd71
htfadd71.bosdata                  := bosdataadd71
var CandleSet htfadd72                     = CandleSet.new()
var CandleSettings SettingsHTFadd72        = CandleSettings.new(htf='72',htfint=72,max_memory=3)
var Candle[] candlesadd72                  = array.new<Candle>(0)
var BOSdata bosdataadd72                   = BOSdata.new()
htfadd72.settings                 := SettingsHTFadd72
htfadd72.candles                  := candlesadd72
htfadd72.bosdata                  := bosdataadd72
var CandleSet htfadd73                     = CandleSet.new()
var CandleSettings SettingsHTFadd73        = CandleSettings.new(htf='73',htfint=73,max_memory=3)
var Candle[] candlesadd73                  = array.new<Candle>(0)
var BOSdata bosdataadd73                   = BOSdata.new()
htfadd73.settings                 := SettingsHTFadd73
htfadd73.candles                  := candlesadd73
htfadd73.bosdata                  := bosdataadd73
var CandleSet htfadd74                     = CandleSet.new()
var CandleSettings SettingsHTFadd74        = CandleSettings.new(htf='74',htfint=74,max_memory=3)
var Candle[] candlesadd74                  = array.new<Candle>(0)
var BOSdata bosdataadd74                   = BOSdata.new()
htfadd74.settings                 := SettingsHTFadd74
htfadd74.candles                  := candlesadd74
htfadd74.bosdata                  := bosdataadd74
var CandleSet htfadd75                     = CandleSet.new()
var CandleSettings SettingsHTFadd75        = CandleSettings.new(htf='75',htfint=75,max_memory=3)
var Candle[] candlesadd75                  = array.new<Candle>(0)
var BOSdata bosdataadd75                   = BOSdata.new()
htfadd75.settings                 := SettingsHTFadd75
htfadd75.candles                  := candlesadd75
htfadd75.bosdata                  := bosdataadd75
var CandleSet htfadd76                     = CandleSet.new()
var CandleSettings SettingsHTFadd76        = CandleSettings.new(htf='76',htfint=76,max_memory=3)
var Candle[] candlesadd76                  = array.new<Candle>(0)
var BOSdata bosdataadd76                   = BOSdata.new()
htfadd76.settings                 := SettingsHTFadd76
htfadd76.candles                  := candlesadd76
htfadd76.bosdata                  := bosdataadd76
var CandleSet htfadd77                     = CandleSet.new()
var CandleSettings SettingsHTFadd77        = CandleSettings.new(htf='77',htfint=77,max_memory=3)
var Candle[] candlesadd77                  = array.new<Candle>(0)
var BOSdata bosdataadd77                   = BOSdata.new()
htfadd77.settings                 := SettingsHTFadd77
htfadd77.candles                  := candlesadd77
htfadd77.bosdata                  := bosdataadd77
var CandleSet htfadd78                     = CandleSet.new()
var CandleSettings SettingsHTFadd78        = CandleSettings.new(htf='78',htfint=78,max_memory=3)
var Candle[] candlesadd78                  = array.new<Candle>(0)
var BOSdata bosdataadd78                   = BOSdata.new()
htfadd78.settings                 := SettingsHTFadd78
htfadd78.candles                  := candlesadd78
htfadd78.bosdata                  := bosdataadd78
var CandleSet htfadd79                     = CandleSet.new()
var CandleSettings SettingsHTFadd79        = CandleSettings.new(htf='79',htfint=79,max_memory=3)
var Candle[] candlesadd79                  = array.new<Candle>(0)
var BOSdata bosdataadd79                   = BOSdata.new()
htfadd79.settings                 := SettingsHTFadd79
htfadd79.candles                  := candlesadd79
htfadd79.bosdata                  := bosdataadd79
var CandleSet htfadd80                     = CandleSet.new()
var CandleSettings SettingsHTFadd80        = CandleSettings.new(htf='80',htfint=80,max_memory=3)
var Candle[] candlesadd80                  = array.new<Candle>(0)
var BOSdata bosdataadd80                   = BOSdata.new()
htfadd80.settings                 := SettingsHTFadd80
htfadd80.candles                  := candlesadd80
htfadd80.bosdata                  := bosdataadd80
var CandleSet htfadd81                     = CandleSet.new()
var CandleSettings SettingsHTFadd81        = CandleSettings.new(htf='81',htfint=81,max_memory=3)
var Candle[] candlesadd81                  = array.new<Candle>(0)
var BOSdata bosdataadd81                   = BOSdata.new()
htfadd81.settings                 := SettingsHTFadd81
htfadd81.candles                  := candlesadd81
htfadd81.bosdata                  := bosdataadd81
var CandleSet htfadd82                     = CandleSet.new()
var CandleSettings SettingsHTFadd82        = CandleSettings.new(htf='82',htfint=82,max_memory=3)
var Candle[] candlesadd82                  = array.new<Candle>(0)
var BOSdata bosdataadd82                   = BOSdata.new()
htfadd82.settings                 := SettingsHTFadd82
htfadd82.candles                  := candlesadd82
htfadd82.bosdata                  := bosdataadd82
var CandleSet htfadd83                     = CandleSet.new()
var CandleSettings SettingsHTFadd83        = CandleSettings.new(htf='83',htfint=83,max_memory=3)
var Candle[] candlesadd83                  = array.new<Candle>(0)
var BOSdata bosdataadd83                   = BOSdata.new()
htfadd83.settings                 := SettingsHTFadd83
htfadd83.candles                  := candlesadd83
htfadd83.bosdata                  := bosdataadd83
var CandleSet htfadd84                     = CandleSet.new()
var CandleSettings SettingsHTFadd84        = CandleSettings.new(htf='84',htfint=84,max_memory=3)
var Candle[] candlesadd84                  = array.new<Candle>(0)
var BOSdata bosdataadd84                   = BOSdata.new()
htfadd84.settings                 := SettingsHTFadd84
htfadd84.candles                  := candlesadd84
htfadd84.bosdata                  := bosdataadd84
var CandleSet htfadd85                     = CandleSet.new()
var CandleSettings SettingsHTFadd85        = CandleSettings.new(htf='85',htfint=85,max_memory=3)
var Candle[] candlesadd85                  = array.new<Candle>(0)
var BOSdata bosdataadd85                   = BOSdata.new()
htfadd85.settings                 := SettingsHTFadd85
htfadd85.candles                  := candlesadd85
htfadd85.bosdata                  := bosdataadd85
var CandleSet htfadd86                     = CandleSet.new()
var CandleSettings SettingsHTFadd86        = CandleSettings.new(htf='86',htfint=86,max_memory=3)
var Candle[] candlesadd86                  = array.new<Candle>(0)
var BOSdata bosdataadd86                   = BOSdata.new()
htfadd86.settings                 := SettingsHTFadd86
htfadd86.candles                  := candlesadd86
htfadd86.bosdata                  := bosdataadd86
var CandleSet htfadd87                     = CandleSet.new()
var CandleSettings SettingsHTFadd87        = CandleSettings.new(htf='87',htfint=87,max_memory=3)
var Candle[] candlesadd87                  = array.new<Candle>(0)
var BOSdata bosdataadd87                   = BOSdata.new()
htfadd87.settings                 := SettingsHTFadd87
htfadd87.candles                  := candlesadd87
htfadd87.bosdata                  := bosdataadd87
var CandleSet htfadd88                     = CandleSet.new()
var CandleSettings SettingsHTFadd88        = CandleSettings.new(htf='88',htfint=88,max_memory=3)
var Candle[] candlesadd88                  = array.new<Candle>(0)
var BOSdata bosdataadd88                   = BOSdata.new()
htfadd88.settings                 := SettingsHTFadd88
htfadd88.candles                  := candlesadd88
htfadd88.bosdata                  := bosdataadd88
var CandleSet htfadd89                     = CandleSet.new()
var CandleSettings SettingsHTFadd89        = CandleSettings.new(htf='89',htfint=89,max_memory=3)
var Candle[] candlesadd89                  = array.new<Candle>(0)
var BOSdata bosdataadd89                   = BOSdata.new()
htfadd89.settings                 := SettingsHTFadd89
htfadd89.candles                  := candlesadd89
htfadd89.bosdata                  := bosdataadd89
var CandleSet htfadd90                     = CandleSet.new()
var CandleSettings SettingsHTFadd90        = CandleSettings.new(htf='90',htfint=90,max_memory=3)
var Candle[] candlesadd90                  = array.new<Candle>(0)
var BOSdata bosdataadd90                   = BOSdata.new()
htfadd90.settings                 := SettingsHTFadd90
htfadd90.candles                  := candlesadd90
htfadd90.bosdata                  := bosdataadd90


htfadd50.Monitor().BOSJudge()
htfadd51.Monitor().BOSJudge()
htfadd52.Monitor().BOSJudge()
htfadd53.Monitor().BOSJudge()
htfadd54.Monitor().BOSJudge()
htfadd55.Monitor().BOSJudge()
htfadd56.Monitor().BOSJudge()
htfadd57.Monitor().BOSJudge()
htfadd58.Monitor().BOSJudge()
htfadd59.Monitor().BOSJudge()
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

if bar_index == last_bar_index
    
    HighestsbdSet(highestsbd, htfadd50)
    LowestsbuSet(lowestsbu, htfadd50) 
    HighestsbdSet(highestsbd, htfadd51)
    LowestsbuSet(lowestsbu, htfadd51) 
    HighestsbdSet(highestsbd, htfadd52)
    LowestsbuSet(lowestsbu, htfadd52) 
    HighestsbdSet(highestsbd, htfadd53)
    LowestsbuSet(lowestsbu, htfadd53) 
    HighestsbdSet(highestsbd, htfadd54)
    LowestsbuSet(lowestsbu, htfadd54) 
    HighestsbdSet(highestsbd, htfadd55)
    LowestsbuSet(lowestsbu, htfadd55) 
    HighestsbdSet(highestsbd, htfadd56)
    LowestsbuSet(lowestsbu, htfadd56) 
    HighestsbdSet(highestsbd, htfadd57)
    LowestsbuSet(lowestsbu, htfadd57) 
    HighestsbdSet(highestsbd, htfadd58)
    LowestsbuSet(lowestsbu, htfadd58) 
    HighestsbdSet(highestsbd, htfadd59)
    LowestsbuSet(lowestsbu, htfadd59) 
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

    fggetnowclose := true
    
    htfshadow.Shadowing(htfadd50).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd51).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd52).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd53).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd54).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd55).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd56).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd57).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd58).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd59).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd60).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd61).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd62).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd63).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd64).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd65).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd66).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd67).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd68).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd69).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd70).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd71).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd72).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd73).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd74).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd75).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd76).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd77).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd78).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd79).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd80).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd81).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd82).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd83).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd84).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd85).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd86).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd87).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd88).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd89).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd90).Monitor_Est().BOSJudge()
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


