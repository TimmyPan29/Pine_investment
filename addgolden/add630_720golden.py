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
var CandleSet htfadd630                     = CandleSet.new()
var CandleSettings SettingsHTFadd630        = CandleSettings.new(htf='630',htfint=630,max_memory=3)
var Candle[] candlesadd630                  = array.new<Candle>(0)
var BOSdata bosdataadd630                   = BOSdata.new()
htfadd630.settings                 := SettingsHTFadd630
htfadd630.candles                  := candlesadd630
htfadd630.bosdata                  := bosdataadd630
var CandleSet htfadd631                     = CandleSet.new()
var CandleSettings SettingsHTFadd631        = CandleSettings.new(htf='631',htfint=631,max_memory=3)
var Candle[] candlesadd631                  = array.new<Candle>(0)
var BOSdata bosdataadd631                   = BOSdata.new()
htfadd631.settings                 := SettingsHTFadd631
htfadd631.candles                  := candlesadd631
htfadd631.bosdata                  := bosdataadd631
var CandleSet htfadd632                     = CandleSet.new()
var CandleSettings SettingsHTFadd632        = CandleSettings.new(htf='632',htfint=632,max_memory=3)
var Candle[] candlesadd632                  = array.new<Candle>(0)
var BOSdata bosdataadd632                   = BOSdata.new()
htfadd632.settings                 := SettingsHTFadd632
htfadd632.candles                  := candlesadd632
htfadd632.bosdata                  := bosdataadd632
var CandleSet htfadd633                     = CandleSet.new()
var CandleSettings SettingsHTFadd633        = CandleSettings.new(htf='633',htfint=633,max_memory=3)
var Candle[] candlesadd633                  = array.new<Candle>(0)
var BOSdata bosdataadd633                   = BOSdata.new()
htfadd633.settings                 := SettingsHTFadd633
htfadd633.candles                  := candlesadd633
htfadd633.bosdata                  := bosdataadd633
var CandleSet htfadd634                     = CandleSet.new()
var CandleSettings SettingsHTFadd634        = CandleSettings.new(htf='634',htfint=634,max_memory=3)
var Candle[] candlesadd634                  = array.new<Candle>(0)
var BOSdata bosdataadd634                   = BOSdata.new()
htfadd634.settings                 := SettingsHTFadd634
htfadd634.candles                  := candlesadd634
htfadd634.bosdata                  := bosdataadd634
var CandleSet htfadd635                     = CandleSet.new()
var CandleSettings SettingsHTFadd635        = CandleSettings.new(htf='635',htfint=635,max_memory=3)
var Candle[] candlesadd635                  = array.new<Candle>(0)
var BOSdata bosdataadd635                   = BOSdata.new()
htfadd635.settings                 := SettingsHTFadd635
htfadd635.candles                  := candlesadd635
htfadd635.bosdata                  := bosdataadd635
var CandleSet htfadd636                     = CandleSet.new()
var CandleSettings SettingsHTFadd636        = CandleSettings.new(htf='636',htfint=636,max_memory=3)
var Candle[] candlesadd636                  = array.new<Candle>(0)
var BOSdata bosdataadd636                   = BOSdata.new()
htfadd636.settings                 := SettingsHTFadd636
htfadd636.candles                  := candlesadd636
htfadd636.bosdata                  := bosdataadd636
var CandleSet htfadd637                     = CandleSet.new()
var CandleSettings SettingsHTFadd637        = CandleSettings.new(htf='637',htfint=637,max_memory=3)
var Candle[] candlesadd637                  = array.new<Candle>(0)
var BOSdata bosdataadd637                   = BOSdata.new()
htfadd637.settings                 := SettingsHTFadd637
htfadd637.candles                  := candlesadd637
htfadd637.bosdata                  := bosdataadd637
var CandleSet htfadd638                     = CandleSet.new()
var CandleSettings SettingsHTFadd638        = CandleSettings.new(htf='638',htfint=638,max_memory=3)
var Candle[] candlesadd638                  = array.new<Candle>(0)
var BOSdata bosdataadd638                   = BOSdata.new()
htfadd638.settings                 := SettingsHTFadd638
htfadd638.candles                  := candlesadd638
htfadd638.bosdata                  := bosdataadd638
var CandleSet htfadd639                     = CandleSet.new()
var CandleSettings SettingsHTFadd639        = CandleSettings.new(htf='639',htfint=639,max_memory=3)
var Candle[] candlesadd639                  = array.new<Candle>(0)
var BOSdata bosdataadd639                   = BOSdata.new()
htfadd639.settings                 := SettingsHTFadd639
htfadd639.candles                  := candlesadd639
htfadd639.bosdata                  := bosdataadd639
var CandleSet htfadd640                     = CandleSet.new()
var CandleSettings SettingsHTFadd640        = CandleSettings.new(htf='640',htfint=640,max_memory=3)
var Candle[] candlesadd640                  = array.new<Candle>(0)
var BOSdata bosdataadd640                   = BOSdata.new()
htfadd640.settings                 := SettingsHTFadd640
htfadd640.candles                  := candlesadd640
htfadd640.bosdata                  := bosdataadd640
var CandleSet htfadd641                     = CandleSet.new()
var CandleSettings SettingsHTFadd641        = CandleSettings.new(htf='641',htfint=641,max_memory=3)
var Candle[] candlesadd641                  = array.new<Candle>(0)
var BOSdata bosdataadd641                   = BOSdata.new()
htfadd641.settings                 := SettingsHTFadd641
htfadd641.candles                  := candlesadd641
htfadd641.bosdata                  := bosdataadd641
var CandleSet htfadd642                     = CandleSet.new()
var CandleSettings SettingsHTFadd642        = CandleSettings.new(htf='642',htfint=642,max_memory=3)
var Candle[] candlesadd642                  = array.new<Candle>(0)
var BOSdata bosdataadd642                   = BOSdata.new()
htfadd642.settings                 := SettingsHTFadd642
htfadd642.candles                  := candlesadd642
htfadd642.bosdata                  := bosdataadd642
var CandleSet htfadd643                     = CandleSet.new()
var CandleSettings SettingsHTFadd643        = CandleSettings.new(htf='643',htfint=643,max_memory=3)
var Candle[] candlesadd643                  = array.new<Candle>(0)
var BOSdata bosdataadd643                   = BOSdata.new()
htfadd643.settings                 := SettingsHTFadd643
htfadd643.candles                  := candlesadd643
htfadd643.bosdata                  := bosdataadd643
var CandleSet htfadd644                     = CandleSet.new()
var CandleSettings SettingsHTFadd644        = CandleSettings.new(htf='644',htfint=644,max_memory=3)
var Candle[] candlesadd644                  = array.new<Candle>(0)
var BOSdata bosdataadd644                   = BOSdata.new()
htfadd644.settings                 := SettingsHTFadd644
htfadd644.candles                  := candlesadd644
htfadd644.bosdata                  := bosdataadd644
var CandleSet htfadd645                     = CandleSet.new()
var CandleSettings SettingsHTFadd645        = CandleSettings.new(htf='645',htfint=645,max_memory=3)
var Candle[] candlesadd645                  = array.new<Candle>(0)
var BOSdata bosdataadd645                   = BOSdata.new()
htfadd645.settings                 := SettingsHTFadd645
htfadd645.candles                  := candlesadd645
htfadd645.bosdata                  := bosdataadd645
var CandleSet htfadd646                     = CandleSet.new()
var CandleSettings SettingsHTFadd646        = CandleSettings.new(htf='646',htfint=646,max_memory=3)
var Candle[] candlesadd646                  = array.new<Candle>(0)
var BOSdata bosdataadd646                   = BOSdata.new()
htfadd646.settings                 := SettingsHTFadd646
htfadd646.candles                  := candlesadd646
htfadd646.bosdata                  := bosdataadd646
var CandleSet htfadd647                     = CandleSet.new()
var CandleSettings SettingsHTFadd647        = CandleSettings.new(htf='647',htfint=647,max_memory=3)
var Candle[] candlesadd647                  = array.new<Candle>(0)
var BOSdata bosdataadd647                   = BOSdata.new()
htfadd647.settings                 := SettingsHTFadd647
htfadd647.candles                  := candlesadd647
htfadd647.bosdata                  := bosdataadd647
var CandleSet htfadd648                     = CandleSet.new()
var CandleSettings SettingsHTFadd648        = CandleSettings.new(htf='648',htfint=648,max_memory=3)
var Candle[] candlesadd648                  = array.new<Candle>(0)
var BOSdata bosdataadd648                   = BOSdata.new()
htfadd648.settings                 := SettingsHTFadd648
htfadd648.candles                  := candlesadd648
htfadd648.bosdata                  := bosdataadd648
var CandleSet htfadd649                     = CandleSet.new()
var CandleSettings SettingsHTFadd649        = CandleSettings.new(htf='649',htfint=649,max_memory=3)
var Candle[] candlesadd649                  = array.new<Candle>(0)
var BOSdata bosdataadd649                   = BOSdata.new()
htfadd649.settings                 := SettingsHTFadd649
htfadd649.candles                  := candlesadd649
htfadd649.bosdata                  := bosdataadd649
var CandleSet htfadd650                     = CandleSet.new()
var CandleSettings SettingsHTFadd650        = CandleSettings.new(htf='650',htfint=650,max_memory=3)
var Candle[] candlesadd650                  = array.new<Candle>(0)
var BOSdata bosdataadd650                   = BOSdata.new()
htfadd650.settings                 := SettingsHTFadd650
htfadd650.candles                  := candlesadd650
htfadd650.bosdata                  := bosdataadd650
var CandleSet htfadd651                     = CandleSet.new()
var CandleSettings SettingsHTFadd651        = CandleSettings.new(htf='651',htfint=651,max_memory=3)
var Candle[] candlesadd651                  = array.new<Candle>(0)
var BOSdata bosdataadd651                   = BOSdata.new()
htfadd651.settings                 := SettingsHTFadd651
htfadd651.candles                  := candlesadd651
htfadd651.bosdata                  := bosdataadd651
var CandleSet htfadd652                     = CandleSet.new()
var CandleSettings SettingsHTFadd652        = CandleSettings.new(htf='652',htfint=652,max_memory=3)
var Candle[] candlesadd652                  = array.new<Candle>(0)
var BOSdata bosdataadd652                   = BOSdata.new()
htfadd652.settings                 := SettingsHTFadd652
htfadd652.candles                  := candlesadd652
htfadd652.bosdata                  := bosdataadd652
var CandleSet htfadd653                     = CandleSet.new()
var CandleSettings SettingsHTFadd653        = CandleSettings.new(htf='653',htfint=653,max_memory=3)
var Candle[] candlesadd653                  = array.new<Candle>(0)
var BOSdata bosdataadd653                   = BOSdata.new()
htfadd653.settings                 := SettingsHTFadd653
htfadd653.candles                  := candlesadd653
htfadd653.bosdata                  := bosdataadd653
var CandleSet htfadd654                     = CandleSet.new()
var CandleSettings SettingsHTFadd654        = CandleSettings.new(htf='654',htfint=654,max_memory=3)
var Candle[] candlesadd654                  = array.new<Candle>(0)
var BOSdata bosdataadd654                   = BOSdata.new()
htfadd654.settings                 := SettingsHTFadd654
htfadd654.candles                  := candlesadd654
htfadd654.bosdata                  := bosdataadd654
var CandleSet htfadd655                     = CandleSet.new()
var CandleSettings SettingsHTFadd655        = CandleSettings.new(htf='655',htfint=655,max_memory=3)
var Candle[] candlesadd655                  = array.new<Candle>(0)
var BOSdata bosdataadd655                   = BOSdata.new()
htfadd655.settings                 := SettingsHTFadd655
htfadd655.candles                  := candlesadd655
htfadd655.bosdata                  := bosdataadd655
var CandleSet htfadd656                     = CandleSet.new()
var CandleSettings SettingsHTFadd656        = CandleSettings.new(htf='656',htfint=656,max_memory=3)
var Candle[] candlesadd656                  = array.new<Candle>(0)
var BOSdata bosdataadd656                   = BOSdata.new()
htfadd656.settings                 := SettingsHTFadd656
htfadd656.candles                  := candlesadd656
htfadd656.bosdata                  := bosdataadd656
var CandleSet htfadd657                     = CandleSet.new()
var CandleSettings SettingsHTFadd657        = CandleSettings.new(htf='657',htfint=657,max_memory=3)
var Candle[] candlesadd657                  = array.new<Candle>(0)
var BOSdata bosdataadd657                   = BOSdata.new()
htfadd657.settings                 := SettingsHTFadd657
htfadd657.candles                  := candlesadd657
htfadd657.bosdata                  := bosdataadd657
var CandleSet htfadd658                     = CandleSet.new()
var CandleSettings SettingsHTFadd658        = CandleSettings.new(htf='658',htfint=658,max_memory=3)
var Candle[] candlesadd658                  = array.new<Candle>(0)
var BOSdata bosdataadd658                   = BOSdata.new()
htfadd658.settings                 := SettingsHTFadd658
htfadd658.candles                  := candlesadd658
htfadd658.bosdata                  := bosdataadd658
var CandleSet htfadd659                     = CandleSet.new()
var CandleSettings SettingsHTFadd659        = CandleSettings.new(htf='659',htfint=659,max_memory=3)
var Candle[] candlesadd659                  = array.new<Candle>(0)
var BOSdata bosdataadd659                   = BOSdata.new()
htfadd659.settings                 := SettingsHTFadd659
htfadd659.candles                  := candlesadd659
htfadd659.bosdata                  := bosdataadd659
var CandleSet htfadd660                     = CandleSet.new()
var CandleSettings SettingsHTFadd660        = CandleSettings.new(htf='660',htfint=660,max_memory=3)
var Candle[] candlesadd660                  = array.new<Candle>(0)
var BOSdata bosdataadd660                   = BOSdata.new()
htfadd660.settings                 := SettingsHTFadd660
htfadd660.candles                  := candlesadd660
htfadd660.bosdata                  := bosdataadd660
var CandleSet htfadd661                     = CandleSet.new()
var CandleSettings SettingsHTFadd661        = CandleSettings.new(htf='661',htfint=661,max_memory=3)
var Candle[] candlesadd661                  = array.new<Candle>(0)
var BOSdata bosdataadd661                   = BOSdata.new()
htfadd661.settings                 := SettingsHTFadd661
htfadd661.candles                  := candlesadd661
htfadd661.bosdata                  := bosdataadd661
var CandleSet htfadd662                     = CandleSet.new()
var CandleSettings SettingsHTFadd662        = CandleSettings.new(htf='662',htfint=662,max_memory=3)
var Candle[] candlesadd662                  = array.new<Candle>(0)
var BOSdata bosdataadd662                   = BOSdata.new()
htfadd662.settings                 := SettingsHTFadd662
htfadd662.candles                  := candlesadd662
htfadd662.bosdata                  := bosdataadd662
var CandleSet htfadd663                     = CandleSet.new()
var CandleSettings SettingsHTFadd663        = CandleSettings.new(htf='663',htfint=663,max_memory=3)
var Candle[] candlesadd663                  = array.new<Candle>(0)
var BOSdata bosdataadd663                   = BOSdata.new()
htfadd663.settings                 := SettingsHTFadd663
htfadd663.candles                  := candlesadd663
htfadd663.bosdata                  := bosdataadd663
var CandleSet htfadd664                     = CandleSet.new()
var CandleSettings SettingsHTFadd664        = CandleSettings.new(htf='664',htfint=664,max_memory=3)
var Candle[] candlesadd664                  = array.new<Candle>(0)
var BOSdata bosdataadd664                   = BOSdata.new()
htfadd664.settings                 := SettingsHTFadd664
htfadd664.candles                  := candlesadd664
htfadd664.bosdata                  := bosdataadd664
var CandleSet htfadd665                     = CandleSet.new()
var CandleSettings SettingsHTFadd665        = CandleSettings.new(htf='665',htfint=665,max_memory=3)
var Candle[] candlesadd665                  = array.new<Candle>(0)
var BOSdata bosdataadd665                   = BOSdata.new()
htfadd665.settings                 := SettingsHTFadd665
htfadd665.candles                  := candlesadd665
htfadd665.bosdata                  := bosdataadd665
var CandleSet htfadd666                     = CandleSet.new()
var CandleSettings SettingsHTFadd666        = CandleSettings.new(htf='666',htfint=666,max_memory=3)
var Candle[] candlesadd666                  = array.new<Candle>(0)
var BOSdata bosdataadd666                   = BOSdata.new()
htfadd666.settings                 := SettingsHTFadd666
htfadd666.candles                  := candlesadd666
htfadd666.bosdata                  := bosdataadd666
var CandleSet htfadd667                     = CandleSet.new()
var CandleSettings SettingsHTFadd667        = CandleSettings.new(htf='667',htfint=667,max_memory=3)
var Candle[] candlesadd667                  = array.new<Candle>(0)
var BOSdata bosdataadd667                   = BOSdata.new()
htfadd667.settings                 := SettingsHTFadd667
htfadd667.candles                  := candlesadd667
htfadd667.bosdata                  := bosdataadd667
var CandleSet htfadd668                     = CandleSet.new()
var CandleSettings SettingsHTFadd668        = CandleSettings.new(htf='668',htfint=668,max_memory=3)
var Candle[] candlesadd668                  = array.new<Candle>(0)
var BOSdata bosdataadd668                   = BOSdata.new()
htfadd668.settings                 := SettingsHTFadd668
htfadd668.candles                  := candlesadd668
htfadd668.bosdata                  := bosdataadd668
var CandleSet htfadd669                     = CandleSet.new()
var CandleSettings SettingsHTFadd669        = CandleSettings.new(htf='669',htfint=669,max_memory=3)
var Candle[] candlesadd669                  = array.new<Candle>(0)
var BOSdata bosdataadd669                   = BOSdata.new()
htfadd669.settings                 := SettingsHTFadd669
htfadd669.candles                  := candlesadd669
htfadd669.bosdata                  := bosdataadd669
var CandleSet htfadd670                     = CandleSet.new()
var CandleSettings SettingsHTFadd670        = CandleSettings.new(htf='670',htfint=670,max_memory=3)
var Candle[] candlesadd670                  = array.new<Candle>(0)
var BOSdata bosdataadd670                   = BOSdata.new()
htfadd670.settings                 := SettingsHTFadd670
htfadd670.candles                  := candlesadd670
htfadd670.bosdata                  := bosdataadd670
var CandleSet htfadd671                     = CandleSet.new()
var CandleSettings SettingsHTFadd671        = CandleSettings.new(htf='671',htfint=671,max_memory=3)
var Candle[] candlesadd671                  = array.new<Candle>(0)
var BOSdata bosdataadd671                   = BOSdata.new()
htfadd671.settings                 := SettingsHTFadd671
htfadd671.candles                  := candlesadd671
htfadd671.bosdata                  := bosdataadd671
var CandleSet htfadd672                     = CandleSet.new()
var CandleSettings SettingsHTFadd672        = CandleSettings.new(htf='672',htfint=672,max_memory=3)
var Candle[] candlesadd672                  = array.new<Candle>(0)
var BOSdata bosdataadd672                   = BOSdata.new()
htfadd672.settings                 := SettingsHTFadd672
htfadd672.candles                  := candlesadd672
htfadd672.bosdata                  := bosdataadd672
var CandleSet htfadd673                     = CandleSet.new()
var CandleSettings SettingsHTFadd673        = CandleSettings.new(htf='673',htfint=673,max_memory=3)
var Candle[] candlesadd673                  = array.new<Candle>(0)
var BOSdata bosdataadd673                   = BOSdata.new()
htfadd673.settings                 := SettingsHTFadd673
htfadd673.candles                  := candlesadd673
htfadd673.bosdata                  := bosdataadd673
var CandleSet htfadd674                     = CandleSet.new()
var CandleSettings SettingsHTFadd674        = CandleSettings.new(htf='674',htfint=674,max_memory=3)
var Candle[] candlesadd674                  = array.new<Candle>(0)
var BOSdata bosdataadd674                   = BOSdata.new()
htfadd674.settings                 := SettingsHTFadd674
htfadd674.candles                  := candlesadd674
htfadd674.bosdata                  := bosdataadd674
var CandleSet htfadd675                     = CandleSet.new()
var CandleSettings SettingsHTFadd675        = CandleSettings.new(htf='675',htfint=675,max_memory=3)
var Candle[] candlesadd675                  = array.new<Candle>(0)
var BOSdata bosdataadd675                   = BOSdata.new()
htfadd675.settings                 := SettingsHTFadd675
htfadd675.candles                  := candlesadd675
htfadd675.bosdata                  := bosdataadd675
var CandleSet htfadd676                     = CandleSet.new()
var CandleSettings SettingsHTFadd676        = CandleSettings.new(htf='676',htfint=676,max_memory=3)
var Candle[] candlesadd676                  = array.new<Candle>(0)
var BOSdata bosdataadd676                   = BOSdata.new()
htfadd676.settings                 := SettingsHTFadd676
htfadd676.candles                  := candlesadd676
htfadd676.bosdata                  := bosdataadd676
var CandleSet htfadd677                     = CandleSet.new()
var CandleSettings SettingsHTFadd677        = CandleSettings.new(htf='677',htfint=677,max_memory=3)
var Candle[] candlesadd677                  = array.new<Candle>(0)
var BOSdata bosdataadd677                   = BOSdata.new()
htfadd677.settings                 := SettingsHTFadd677
htfadd677.candles                  := candlesadd677
htfadd677.bosdata                  := bosdataadd677
var CandleSet htfadd678                     = CandleSet.new()
var CandleSettings SettingsHTFadd678        = CandleSettings.new(htf='678',htfint=678,max_memory=3)
var Candle[] candlesadd678                  = array.new<Candle>(0)
var BOSdata bosdataadd678                   = BOSdata.new()
htfadd678.settings                 := SettingsHTFadd678
htfadd678.candles                  := candlesadd678
htfadd678.bosdata                  := bosdataadd678
var CandleSet htfadd679                     = CandleSet.new()
var CandleSettings SettingsHTFadd679        = CandleSettings.new(htf='679',htfint=679,max_memory=3)
var Candle[] candlesadd679                  = array.new<Candle>(0)
var BOSdata bosdataadd679                   = BOSdata.new()
htfadd679.settings                 := SettingsHTFadd679
htfadd679.candles                  := candlesadd679
htfadd679.bosdata                  := bosdataadd679
var CandleSet htfadd680                     = CandleSet.new()
var CandleSettings SettingsHTFadd680        = CandleSettings.new(htf='680',htfint=680,max_memory=3)
var Candle[] candlesadd680                  = array.new<Candle>(0)
var BOSdata bosdataadd680                   = BOSdata.new()
htfadd680.settings                 := SettingsHTFadd680
htfadd680.candles                  := candlesadd680
htfadd680.bosdata                  := bosdataadd680
var CandleSet htfadd681                     = CandleSet.new()
var CandleSettings SettingsHTFadd681        = CandleSettings.new(htf='681',htfint=681,max_memory=3)
var Candle[] candlesadd681                  = array.new<Candle>(0)
var BOSdata bosdataadd681                   = BOSdata.new()
htfadd681.settings                 := SettingsHTFadd681
htfadd681.candles                  := candlesadd681
htfadd681.bosdata                  := bosdataadd681
var CandleSet htfadd682                     = CandleSet.new()
var CandleSettings SettingsHTFadd682        = CandleSettings.new(htf='682',htfint=682,max_memory=3)
var Candle[] candlesadd682                  = array.new<Candle>(0)
var BOSdata bosdataadd682                   = BOSdata.new()
htfadd682.settings                 := SettingsHTFadd682
htfadd682.candles                  := candlesadd682
htfadd682.bosdata                  := bosdataadd682
var CandleSet htfadd683                     = CandleSet.new()
var CandleSettings SettingsHTFadd683        = CandleSettings.new(htf='683',htfint=683,max_memory=3)
var Candle[] candlesadd683                  = array.new<Candle>(0)
var BOSdata bosdataadd683                   = BOSdata.new()
htfadd683.settings                 := SettingsHTFadd683
htfadd683.candles                  := candlesadd683
htfadd683.bosdata                  := bosdataadd683
var CandleSet htfadd684                     = CandleSet.new()
var CandleSettings SettingsHTFadd684        = CandleSettings.new(htf='684',htfint=684,max_memory=3)
var Candle[] candlesadd684                  = array.new<Candle>(0)
var BOSdata bosdataadd684                   = BOSdata.new()
htfadd684.settings                 := SettingsHTFadd684
htfadd684.candles                  := candlesadd684
htfadd684.bosdata                  := bosdataadd684
var CandleSet htfadd685                     = CandleSet.new()
var CandleSettings SettingsHTFadd685        = CandleSettings.new(htf='685',htfint=685,max_memory=3)
var Candle[] candlesadd685                  = array.new<Candle>(0)
var BOSdata bosdataadd685                   = BOSdata.new()
htfadd685.settings                 := SettingsHTFadd685
htfadd685.candles                  := candlesadd685
htfadd685.bosdata                  := bosdataadd685
var CandleSet htfadd686                     = CandleSet.new()
var CandleSettings SettingsHTFadd686        = CandleSettings.new(htf='686',htfint=686,max_memory=3)
var Candle[] candlesadd686                  = array.new<Candle>(0)
var BOSdata bosdataadd686                   = BOSdata.new()
htfadd686.settings                 := SettingsHTFadd686
htfadd686.candles                  := candlesadd686
htfadd686.bosdata                  := bosdataadd686
var CandleSet htfadd687                     = CandleSet.new()
var CandleSettings SettingsHTFadd687        = CandleSettings.new(htf='687',htfint=687,max_memory=3)
var Candle[] candlesadd687                  = array.new<Candle>(0)
var BOSdata bosdataadd687                   = BOSdata.new()
htfadd687.settings                 := SettingsHTFadd687
htfadd687.candles                  := candlesadd687
htfadd687.bosdata                  := bosdataadd687
var CandleSet htfadd688                     = CandleSet.new()
var CandleSettings SettingsHTFadd688        = CandleSettings.new(htf='688',htfint=688,max_memory=3)
var Candle[] candlesadd688                  = array.new<Candle>(0)
var BOSdata bosdataadd688                   = BOSdata.new()
htfadd688.settings                 := SettingsHTFadd688
htfadd688.candles                  := candlesadd688
htfadd688.bosdata                  := bosdataadd688
var CandleSet htfadd689                     = CandleSet.new()
var CandleSettings SettingsHTFadd689        = CandleSettings.new(htf='689',htfint=689,max_memory=3)
var Candle[] candlesadd689                  = array.new<Candle>(0)
var BOSdata bosdataadd689                   = BOSdata.new()
htfadd689.settings                 := SettingsHTFadd689
htfadd689.candles                  := candlesadd689
htfadd689.bosdata                  := bosdataadd689
var CandleSet htfadd690                     = CandleSet.new()
var CandleSettings SettingsHTFadd690        = CandleSettings.new(htf='690',htfint=690,max_memory=3)
var Candle[] candlesadd690                  = array.new<Candle>(0)
var BOSdata bosdataadd690                   = BOSdata.new()
htfadd690.settings                 := SettingsHTFadd690
htfadd690.candles                  := candlesadd690
htfadd690.bosdata                  := bosdataadd690
var CandleSet htfadd691                     = CandleSet.new()
var CandleSettings SettingsHTFadd691        = CandleSettings.new(htf='691',htfint=691,max_memory=3)
var Candle[] candlesadd691                  = array.new<Candle>(0)
var BOSdata bosdataadd691                   = BOSdata.new()
htfadd691.settings                 := SettingsHTFadd691
htfadd691.candles                  := candlesadd691
htfadd691.bosdata                  := bosdataadd691
var CandleSet htfadd692                     = CandleSet.new()
var CandleSettings SettingsHTFadd692        = CandleSettings.new(htf='692',htfint=692,max_memory=3)
var Candle[] candlesadd692                  = array.new<Candle>(0)
var BOSdata bosdataadd692                   = BOSdata.new()
htfadd692.settings                 := SettingsHTFadd692
htfadd692.candles                  := candlesadd692
htfadd692.bosdata                  := bosdataadd692
var CandleSet htfadd693                     = CandleSet.new()
var CandleSettings SettingsHTFadd693        = CandleSettings.new(htf='693',htfint=693,max_memory=3)
var Candle[] candlesadd693                  = array.new<Candle>(0)
var BOSdata bosdataadd693                   = BOSdata.new()
htfadd693.settings                 := SettingsHTFadd693
htfadd693.candles                  := candlesadd693
htfadd693.bosdata                  := bosdataadd693
var CandleSet htfadd694                     = CandleSet.new()
var CandleSettings SettingsHTFadd694        = CandleSettings.new(htf='694',htfint=694,max_memory=3)
var Candle[] candlesadd694                  = array.new<Candle>(0)
var BOSdata bosdataadd694                   = BOSdata.new()
htfadd694.settings                 := SettingsHTFadd694
htfadd694.candles                  := candlesadd694
htfadd694.bosdata                  := bosdataadd694
var CandleSet htfadd695                     = CandleSet.new()
var CandleSettings SettingsHTFadd695        = CandleSettings.new(htf='695',htfint=695,max_memory=3)
var Candle[] candlesadd695                  = array.new<Candle>(0)
var BOSdata bosdataadd695                   = BOSdata.new()
htfadd695.settings                 := SettingsHTFadd695
htfadd695.candles                  := candlesadd695
htfadd695.bosdata                  := bosdataadd695
var CandleSet htfadd696                     = CandleSet.new()
var CandleSettings SettingsHTFadd696        = CandleSettings.new(htf='696',htfint=696,max_memory=3)
var Candle[] candlesadd696                  = array.new<Candle>(0)
var BOSdata bosdataadd696                   = BOSdata.new()
htfadd696.settings                 := SettingsHTFadd696
htfadd696.candles                  := candlesadd696
htfadd696.bosdata                  := bosdataadd696
var CandleSet htfadd697                     = CandleSet.new()
var CandleSettings SettingsHTFadd697        = CandleSettings.new(htf='697',htfint=697,max_memory=3)
var Candle[] candlesadd697                  = array.new<Candle>(0)
var BOSdata bosdataadd697                   = BOSdata.new()
htfadd697.settings                 := SettingsHTFadd697
htfadd697.candles                  := candlesadd697
htfadd697.bosdata                  := bosdataadd697
var CandleSet htfadd698                     = CandleSet.new()
var CandleSettings SettingsHTFadd698        = CandleSettings.new(htf='698',htfint=698,max_memory=3)
var Candle[] candlesadd698                  = array.new<Candle>(0)
var BOSdata bosdataadd698                   = BOSdata.new()
htfadd698.settings                 := SettingsHTFadd698
htfadd698.candles                  := candlesadd698
htfadd698.bosdata                  := bosdataadd698
var CandleSet htfadd699                     = CandleSet.new()
var CandleSettings SettingsHTFadd699        = CandleSettings.new(htf='699',htfint=699,max_memory=3)
var Candle[] candlesadd699                  = array.new<Candle>(0)
var BOSdata bosdataadd699                   = BOSdata.new()
htfadd699.settings                 := SettingsHTFadd699
htfadd699.candles                  := candlesadd699
htfadd699.bosdata                  := bosdataadd699
var CandleSet htfadd700                     = CandleSet.new()
var CandleSettings SettingsHTFadd700        = CandleSettings.new(htf='700',htfint=700,max_memory=3)
var Candle[] candlesadd700                  = array.new<Candle>(0)
var BOSdata bosdataadd700                   = BOSdata.new()
htfadd700.settings                 := SettingsHTFadd700
htfadd700.candles                  := candlesadd700
htfadd700.bosdata                  := bosdataadd700
var CandleSet htfadd701                     = CandleSet.new()
var CandleSettings SettingsHTFadd701        = CandleSettings.new(htf='701',htfint=701,max_memory=3)
var Candle[] candlesadd701                  = array.new<Candle>(0)
var BOSdata bosdataadd701                   = BOSdata.new()
htfadd701.settings                 := SettingsHTFadd701
htfadd701.candles                  := candlesadd701
htfadd701.bosdata                  := bosdataadd701
var CandleSet htfadd702                     = CandleSet.new()
var CandleSettings SettingsHTFadd702        = CandleSettings.new(htf='702',htfint=702,max_memory=3)
var Candle[] candlesadd702                  = array.new<Candle>(0)
var BOSdata bosdataadd702                   = BOSdata.new()
htfadd702.settings                 := SettingsHTFadd702
htfadd702.candles                  := candlesadd702
htfadd702.bosdata                  := bosdataadd702
var CandleSet htfadd703                     = CandleSet.new()
var CandleSettings SettingsHTFadd703        = CandleSettings.new(htf='703',htfint=703,max_memory=3)
var Candle[] candlesadd703                  = array.new<Candle>(0)
var BOSdata bosdataadd703                   = BOSdata.new()
htfadd703.settings                 := SettingsHTFadd703
htfadd703.candles                  := candlesadd703
htfadd703.bosdata                  := bosdataadd703
var CandleSet htfadd704                     = CandleSet.new()
var CandleSettings SettingsHTFadd704        = CandleSettings.new(htf='704',htfint=704,max_memory=3)
var Candle[] candlesadd704                  = array.new<Candle>(0)
var BOSdata bosdataadd704                   = BOSdata.new()
htfadd704.settings                 := SettingsHTFadd704
htfadd704.candles                  := candlesadd704
htfadd704.bosdata                  := bosdataadd704
var CandleSet htfadd705                     = CandleSet.new()
var CandleSettings SettingsHTFadd705        = CandleSettings.new(htf='705',htfint=705,max_memory=3)
var Candle[] candlesadd705                  = array.new<Candle>(0)
var BOSdata bosdataadd705                   = BOSdata.new()
htfadd705.settings                 := SettingsHTFadd705
htfadd705.candles                  := candlesadd705
htfadd705.bosdata                  := bosdataadd705
var CandleSet htfadd706                     = CandleSet.new()
var CandleSettings SettingsHTFadd706        = CandleSettings.new(htf='706',htfint=706,max_memory=3)
var Candle[] candlesadd706                  = array.new<Candle>(0)
var BOSdata bosdataadd706                   = BOSdata.new()
htfadd706.settings                 := SettingsHTFadd706
htfadd706.candles                  := candlesadd706
htfadd706.bosdata                  := bosdataadd706
var CandleSet htfadd707                     = CandleSet.new()
var CandleSettings SettingsHTFadd707        = CandleSettings.new(htf='707',htfint=707,max_memory=3)
var Candle[] candlesadd707                  = array.new<Candle>(0)
var BOSdata bosdataadd707                   = BOSdata.new()
htfadd707.settings                 := SettingsHTFadd707
htfadd707.candles                  := candlesadd707
htfadd707.bosdata                  := bosdataadd707
var CandleSet htfadd708                     = CandleSet.new()
var CandleSettings SettingsHTFadd708        = CandleSettings.new(htf='708',htfint=708,max_memory=3)
var Candle[] candlesadd708                  = array.new<Candle>(0)
var BOSdata bosdataadd708                   = BOSdata.new()
htfadd708.settings                 := SettingsHTFadd708
htfadd708.candles                  := candlesadd708
htfadd708.bosdata                  := bosdataadd708
var CandleSet htfadd709                     = CandleSet.new()
var CandleSettings SettingsHTFadd709        = CandleSettings.new(htf='709',htfint=709,max_memory=3)
var Candle[] candlesadd709                  = array.new<Candle>(0)
var BOSdata bosdataadd709                   = BOSdata.new()
htfadd709.settings                 := SettingsHTFadd709
htfadd709.candles                  := candlesadd709
htfadd709.bosdata                  := bosdataadd709
var CandleSet htfadd710                     = CandleSet.new()
var CandleSettings SettingsHTFadd710        = CandleSettings.new(htf='710',htfint=710,max_memory=3)
var Candle[] candlesadd710                  = array.new<Candle>(0)
var BOSdata bosdataadd710                   = BOSdata.new()
htfadd710.settings                 := SettingsHTFadd710
htfadd710.candles                  := candlesadd710
htfadd710.bosdata                  := bosdataadd710
var CandleSet htfadd711                     = CandleSet.new()
var CandleSettings SettingsHTFadd711        = CandleSettings.new(htf='711',htfint=711,max_memory=3)
var Candle[] candlesadd711                  = array.new<Candle>(0)
var BOSdata bosdataadd711                   = BOSdata.new()
htfadd711.settings                 := SettingsHTFadd711
htfadd711.candles                  := candlesadd711
htfadd711.bosdata                  := bosdataadd711
var CandleSet htfadd712                     = CandleSet.new()
var CandleSettings SettingsHTFadd712        = CandleSettings.new(htf='712',htfint=712,max_memory=3)
var Candle[] candlesadd712                  = array.new<Candle>(0)
var BOSdata bosdataadd712                   = BOSdata.new()
htfadd712.settings                 := SettingsHTFadd712
htfadd712.candles                  := candlesadd712
htfadd712.bosdata                  := bosdataadd712
var CandleSet htfadd713                     = CandleSet.new()
var CandleSettings SettingsHTFadd713        = CandleSettings.new(htf='713',htfint=713,max_memory=3)
var Candle[] candlesadd713                  = array.new<Candle>(0)
var BOSdata bosdataadd713                   = BOSdata.new()
htfadd713.settings                 := SettingsHTFadd713
htfadd713.candles                  := candlesadd713
htfadd713.bosdata                  := bosdataadd713
var CandleSet htfadd714                     = CandleSet.new()
var CandleSettings SettingsHTFadd714        = CandleSettings.new(htf='714',htfint=714,max_memory=3)
var Candle[] candlesadd714                  = array.new<Candle>(0)
var BOSdata bosdataadd714                   = BOSdata.new()
htfadd714.settings                 := SettingsHTFadd714
htfadd714.candles                  := candlesadd714
htfadd714.bosdata                  := bosdataadd714
var CandleSet htfadd715                     = CandleSet.new()
var CandleSettings SettingsHTFadd715        = CandleSettings.new(htf='715',htfint=715,max_memory=3)
var Candle[] candlesadd715                  = array.new<Candle>(0)
var BOSdata bosdataadd715                   = BOSdata.new()
htfadd715.settings                 := SettingsHTFadd715
htfadd715.candles                  := candlesadd715
htfadd715.bosdata                  := bosdataadd715
var CandleSet htfadd716                     = CandleSet.new()
var CandleSettings SettingsHTFadd716        = CandleSettings.new(htf='716',htfint=716,max_memory=3)
var Candle[] candlesadd716                  = array.new<Candle>(0)
var BOSdata bosdataadd716                   = BOSdata.new()
htfadd716.settings                 := SettingsHTFadd716
htfadd716.candles                  := candlesadd716
htfadd716.bosdata                  := bosdataadd716
var CandleSet htfadd717                     = CandleSet.new()
var CandleSettings SettingsHTFadd717        = CandleSettings.new(htf='717',htfint=717,max_memory=3)
var Candle[] candlesadd717                  = array.new<Candle>(0)
var BOSdata bosdataadd717                   = BOSdata.new()
htfadd717.settings                 := SettingsHTFadd717
htfadd717.candles                  := candlesadd717
htfadd717.bosdata                  := bosdataadd717
var CandleSet htfadd718                     = CandleSet.new()
var CandleSettings SettingsHTFadd718        = CandleSettings.new(htf='718',htfint=718,max_memory=3)
var Candle[] candlesadd718                  = array.new<Candle>(0)
var BOSdata bosdataadd718                   = BOSdata.new()
htfadd718.settings                 := SettingsHTFadd718
htfadd718.candles                  := candlesadd718
htfadd718.bosdata                  := bosdataadd718
var CandleSet htfadd719                     = CandleSet.new()
var CandleSettings SettingsHTFadd719        = CandleSettings.new(htf='719',htfint=719,max_memory=3)
var Candle[] candlesadd719                  = array.new<Candle>(0)
var BOSdata bosdataadd719                   = BOSdata.new()
htfadd719.settings                 := SettingsHTFadd719
htfadd719.candles                  := candlesadd719
htfadd719.bosdata                  := bosdataadd719
var CandleSet htfadd720                     = CandleSet.new()
var CandleSettings SettingsHTFadd720        = CandleSettings.new(htf='720',htfint=720,max_memory=3)
var Candle[] candlesadd720                  = array.new<Candle>(0)
var BOSdata bosdataadd720                   = BOSdata.new()
htfadd720.settings                 := SettingsHTFadd720
htfadd720.candles                  := candlesadd720
htfadd720.bosdata                  := bosdataadd720

htfadd630.Monitor().BOSJudge()
htfadd631.Monitor().BOSJudge()
htfadd632.Monitor().BOSJudge()
htfadd633.Monitor().BOSJudge()
htfadd634.Monitor().BOSJudge()
htfadd635.Monitor().BOSJudge()
htfadd636.Monitor().BOSJudge()
htfadd637.Monitor().BOSJudge()
htfadd638.Monitor().BOSJudge()
htfadd639.Monitor().BOSJudge()
htfadd640.Monitor().BOSJudge()
htfadd641.Monitor().BOSJudge()
htfadd642.Monitor().BOSJudge()
htfadd643.Monitor().BOSJudge()
htfadd644.Monitor().BOSJudge()
htfadd645.Monitor().BOSJudge()
htfadd646.Monitor().BOSJudge()
htfadd647.Monitor().BOSJudge()
htfadd648.Monitor().BOSJudge()
htfadd649.Monitor().BOSJudge()
htfadd650.Monitor().BOSJudge()
htfadd651.Monitor().BOSJudge()
htfadd652.Monitor().BOSJudge()
htfadd653.Monitor().BOSJudge()
htfadd654.Monitor().BOSJudge()
htfadd655.Monitor().BOSJudge()
htfadd656.Monitor().BOSJudge()
htfadd657.Monitor().BOSJudge()
htfadd658.Monitor().BOSJudge()
htfadd659.Monitor().BOSJudge()
htfadd660.Monitor().BOSJudge()
htfadd661.Monitor().BOSJudge()
htfadd662.Monitor().BOSJudge()
htfadd663.Monitor().BOSJudge()
htfadd664.Monitor().BOSJudge()
htfadd665.Monitor().BOSJudge()
htfadd666.Monitor().BOSJudge()
htfadd667.Monitor().BOSJudge()
htfadd668.Monitor().BOSJudge()
htfadd669.Monitor().BOSJudge()
htfadd670.Monitor().BOSJudge()
htfadd671.Monitor().BOSJudge()
htfadd672.Monitor().BOSJudge()
htfadd673.Monitor().BOSJudge()
htfadd674.Monitor().BOSJudge()
htfadd675.Monitor().BOSJudge()
htfadd676.Monitor().BOSJudge()
htfadd677.Monitor().BOSJudge()
htfadd678.Monitor().BOSJudge()
htfadd679.Monitor().BOSJudge()
htfadd680.Monitor().BOSJudge()
htfadd681.Monitor().BOSJudge()
htfadd682.Monitor().BOSJudge()
htfadd683.Monitor().BOSJudge()
htfadd684.Monitor().BOSJudge()
htfadd685.Monitor().BOSJudge()
htfadd686.Monitor().BOSJudge()
htfadd687.Monitor().BOSJudge()
htfadd688.Monitor().BOSJudge()
htfadd689.Monitor().BOSJudge()
htfadd690.Monitor().BOSJudge()
htfadd691.Monitor().BOSJudge()
htfadd692.Monitor().BOSJudge()
htfadd693.Monitor().BOSJudge()
htfadd694.Monitor().BOSJudge()
htfadd695.Monitor().BOSJudge()
htfadd696.Monitor().BOSJudge()
htfadd697.Monitor().BOSJudge()
htfadd698.Monitor().BOSJudge()
htfadd699.Monitor().BOSJudge()
htfadd700.Monitor().BOSJudge()
htfadd701.Monitor().BOSJudge()
htfadd702.Monitor().BOSJudge()
htfadd703.Monitor().BOSJudge()
htfadd704.Monitor().BOSJudge()
htfadd705.Monitor().BOSJudge()
htfadd706.Monitor().BOSJudge()
htfadd707.Monitor().BOSJudge()
htfadd708.Monitor().BOSJudge()
htfadd709.Monitor().BOSJudge()
htfadd710.Monitor().BOSJudge()
htfadd711.Monitor().BOSJudge()
htfadd712.Monitor().BOSJudge()
htfadd713.Monitor().BOSJudge()
htfadd714.Monitor().BOSJudge()
htfadd715.Monitor().BOSJudge()
htfadd716.Monitor().BOSJudge()
htfadd717.Monitor().BOSJudge()
htfadd718.Monitor().BOSJudge()
htfadd719.Monitor().BOSJudge()
htfadd720.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd630)
    LowestsbuSet(lowestsbu, htfadd630)
    HighestsbdSet(highestsbd, htfadd631)
    LowestsbuSet(lowestsbu, htfadd631)
    HighestsbdSet(highestsbd, htfadd632)
    LowestsbuSet(lowestsbu, htfadd632)
    HighestsbdSet(highestsbd, htfadd633)
    LowestsbuSet(lowestsbu, htfadd633)
    HighestsbdSet(highestsbd, htfadd634)
    LowestsbuSet(lowestsbu, htfadd634)
    HighestsbdSet(highestsbd, htfadd635)
    LowestsbuSet(lowestsbu, htfadd635)
    HighestsbdSet(highestsbd, htfadd636)
    LowestsbuSet(lowestsbu, htfadd636)
    HighestsbdSet(highestsbd, htfadd637)
    LowestsbuSet(lowestsbu, htfadd637)
    HighestsbdSet(highestsbd, htfadd638)
    LowestsbuSet(lowestsbu, htfadd638)
    HighestsbdSet(highestsbd, htfadd639)
    LowestsbuSet(lowestsbu, htfadd639)
    HighestsbdSet(highestsbd, htfadd640)
    LowestsbuSet(lowestsbu, htfadd640)
    HighestsbdSet(highestsbd, htfadd641)
    LowestsbuSet(lowestsbu, htfadd641)
    HighestsbdSet(highestsbd, htfadd642)
    LowestsbuSet(lowestsbu, htfadd642)
    HighestsbdSet(highestsbd, htfadd643)
    LowestsbuSet(lowestsbu, htfadd643)
    HighestsbdSet(highestsbd, htfadd644)
    LowestsbuSet(lowestsbu, htfadd644)
    HighestsbdSet(highestsbd, htfadd645)
    LowestsbuSet(lowestsbu, htfadd645)
    HighestsbdSet(highestsbd, htfadd646)
    LowestsbuSet(lowestsbu, htfadd646)
    HighestsbdSet(highestsbd, htfadd647)
    LowestsbuSet(lowestsbu, htfadd647)
    HighestsbdSet(highestsbd, htfadd648)
    LowestsbuSet(lowestsbu, htfadd648)
    HighestsbdSet(highestsbd, htfadd649)
    LowestsbuSet(lowestsbu, htfadd649)
    HighestsbdSet(highestsbd, htfadd650)
    LowestsbuSet(lowestsbu, htfadd650)
    HighestsbdSet(highestsbd, htfadd651)
    LowestsbuSet(lowestsbu, htfadd651)
    HighestsbdSet(highestsbd, htfadd652)
    LowestsbuSet(lowestsbu, htfadd652)
    HighestsbdSet(highestsbd, htfadd653)
    LowestsbuSet(lowestsbu, htfadd653)
    HighestsbdSet(highestsbd, htfadd654)
    LowestsbuSet(lowestsbu, htfadd654)
    HighestsbdSet(highestsbd, htfadd655)
    LowestsbuSet(lowestsbu, htfadd655)
    HighestsbdSet(highestsbd, htfadd656)
    LowestsbuSet(lowestsbu, htfadd656)
    HighestsbdSet(highestsbd, htfadd657)
    LowestsbuSet(lowestsbu, htfadd657)
    HighestsbdSet(highestsbd, htfadd658)
    LowestsbuSet(lowestsbu, htfadd658)
    HighestsbdSet(highestsbd, htfadd659)
    LowestsbuSet(lowestsbu, htfadd659)
    HighestsbdSet(highestsbd, htfadd660)
    LowestsbuSet(lowestsbu, htfadd660)
    HighestsbdSet(highestsbd, htfadd661)
    LowestsbuSet(lowestsbu, htfadd661)
    HighestsbdSet(highestsbd, htfadd662)
    LowestsbuSet(lowestsbu, htfadd662)
    HighestsbdSet(highestsbd, htfadd663)
    LowestsbuSet(lowestsbu, htfadd663)
    HighestsbdSet(highestsbd, htfadd664)
    LowestsbuSet(lowestsbu, htfadd664)
    HighestsbdSet(highestsbd, htfadd665)
    LowestsbuSet(lowestsbu, htfadd665)
    HighestsbdSet(highestsbd, htfadd666)
    LowestsbuSet(lowestsbu, htfadd666)
    HighestsbdSet(highestsbd, htfadd667)
    LowestsbuSet(lowestsbu, htfadd667)
    HighestsbdSet(highestsbd, htfadd668)
    LowestsbuSet(lowestsbu, htfadd668)
    HighestsbdSet(highestsbd, htfadd669)
    LowestsbuSet(lowestsbu, htfadd669)
    HighestsbdSet(highestsbd, htfadd670)
    LowestsbuSet(lowestsbu, htfadd670)
    HighestsbdSet(highestsbd, htfadd671)
    LowestsbuSet(lowestsbu, htfadd671)
    HighestsbdSet(highestsbd, htfadd672)
    LowestsbuSet(lowestsbu, htfadd672)
    HighestsbdSet(highestsbd, htfadd673)
    LowestsbuSet(lowestsbu, htfadd673)
    HighestsbdSet(highestsbd, htfadd674)
    LowestsbuSet(lowestsbu, htfadd674)
    HighestsbdSet(highestsbd, htfadd675)
    LowestsbuSet(lowestsbu, htfadd675)
    HighestsbdSet(highestsbd, htfadd676)
    LowestsbuSet(lowestsbu, htfadd676)
    HighestsbdSet(highestsbd, htfadd677)
    LowestsbuSet(lowestsbu, htfadd677)
    HighestsbdSet(highestsbd, htfadd678)
    LowestsbuSet(lowestsbu, htfadd678)
    HighestsbdSet(highestsbd, htfadd679)
    LowestsbuSet(lowestsbu, htfadd679)
    HighestsbdSet(highestsbd, htfadd680)
    LowestsbuSet(lowestsbu, htfadd680)
    HighestsbdSet(highestsbd, htfadd681)
    LowestsbuSet(lowestsbu, htfadd681)
    HighestsbdSet(highestsbd, htfadd682)
    LowestsbuSet(lowestsbu, htfadd682)
    HighestsbdSet(highestsbd, htfadd683)
    LowestsbuSet(lowestsbu, htfadd683)
    HighestsbdSet(highestsbd, htfadd684)
    LowestsbuSet(lowestsbu, htfadd684)
    HighestsbdSet(highestsbd, htfadd685)
    LowestsbuSet(lowestsbu, htfadd685)
    HighestsbdSet(highestsbd, htfadd686)
    LowestsbuSet(lowestsbu, htfadd686)
    HighestsbdSet(highestsbd, htfadd687)
    LowestsbuSet(lowestsbu, htfadd687)
    HighestsbdSet(highestsbd, htfadd688)
    LowestsbuSet(lowestsbu, htfadd688)
    HighestsbdSet(highestsbd, htfadd689)
    LowestsbuSet(lowestsbu, htfadd689)
    HighestsbdSet(highestsbd, htfadd690)
    LowestsbuSet(lowestsbu, htfadd690)
    HighestsbdSet(highestsbd, htfadd691)
    LowestsbuSet(lowestsbu, htfadd691)
    HighestsbdSet(highestsbd, htfadd692)
    LowestsbuSet(lowestsbu, htfadd692)
    HighestsbdSet(highestsbd, htfadd693)
    LowestsbuSet(lowestsbu, htfadd693)
    HighestsbdSet(highestsbd, htfadd694)
    LowestsbuSet(lowestsbu, htfadd694)
    HighestsbdSet(highestsbd, htfadd695)
    LowestsbuSet(lowestsbu, htfadd695)
    HighestsbdSet(highestsbd, htfadd696)
    LowestsbuSet(lowestsbu, htfadd696)
    HighestsbdSet(highestsbd, htfadd697)
    LowestsbuSet(lowestsbu, htfadd697)
    HighestsbdSet(highestsbd, htfadd698)
    LowestsbuSet(lowestsbu, htfadd698)
    HighestsbdSet(highestsbd, htfadd699)
    LowestsbuSet(lowestsbu, htfadd699)
    HighestsbdSet(highestsbd, htfadd700)
    LowestsbuSet(lowestsbu, htfadd700)
    HighestsbdSet(highestsbd, htfadd701)
    LowestsbuSet(lowestsbu, htfadd701)
    HighestsbdSet(highestsbd, htfadd702)
    LowestsbuSet(lowestsbu, htfadd702)
    HighestsbdSet(highestsbd, htfadd703)
    LowestsbuSet(lowestsbu, htfadd703)
    HighestsbdSet(highestsbd, htfadd704)
    LowestsbuSet(lowestsbu, htfadd704)
    HighestsbdSet(highestsbd, htfadd705)
    LowestsbuSet(lowestsbu, htfadd705)
    HighestsbdSet(highestsbd, htfadd706)
    LowestsbuSet(lowestsbu, htfadd706)
    HighestsbdSet(highestsbd, htfadd707)
    LowestsbuSet(lowestsbu, htfadd707)
    HighestsbdSet(highestsbd, htfadd708)
    LowestsbuSet(lowestsbu, htfadd708)
    HighestsbdSet(highestsbd, htfadd709)
    LowestsbuSet(lowestsbu, htfadd709)
    HighestsbdSet(highestsbd, htfadd710)
    LowestsbuSet(lowestsbu, htfadd710)
    HighestsbdSet(highestsbd, htfadd711)
    LowestsbuSet(lowestsbu, htfadd711)
    HighestsbdSet(highestsbd, htfadd712)
    LowestsbuSet(lowestsbu, htfadd712)
    HighestsbdSet(highestsbd, htfadd713)
    LowestsbuSet(lowestsbu, htfadd713)
    HighestsbdSet(highestsbd, htfadd714)
    LowestsbuSet(lowestsbu, htfadd714)
    HighestsbdSet(highestsbd, htfadd715)
    LowestsbuSet(lowestsbu, htfadd715)
    HighestsbdSet(highestsbd, htfadd716)
    LowestsbuSet(lowestsbu, htfadd716)
    HighestsbdSet(highestsbd, htfadd717)
    LowestsbuSet(lowestsbu, htfadd717)
    HighestsbdSet(highestsbd, htfadd718)
    LowestsbuSet(lowestsbu, htfadd718)
    HighestsbdSet(highestsbd, htfadd719)
    LowestsbuSet(lowestsbu, htfadd719)
    HighestsbdSet(highestsbd, htfadd720)
    LowestsbuSet(lowestsbu, htfadd720)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd630).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd631).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd632).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd633).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd634).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd635).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd636).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd637).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd638).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd639).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd640).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd641).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd642).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd643).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd644).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd645).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd646).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd647).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd648).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd649).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd650).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd651).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd652).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd653).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd654).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd655).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd656).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd657).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd658).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd659).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd660).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd661).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd662).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd663).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd664).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd665).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd666).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd667).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd668).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd669).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd670).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd671).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd672).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd673).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd674).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd675).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd676).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd677).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd678).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd679).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd680).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd681).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd682).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd683).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd684).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd685).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd686).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd687).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd688).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd689).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd690).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd691).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd692).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd693).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd694).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd695).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd696).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd697).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd698).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd699).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd700).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd701).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd702).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd703).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd704).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd705).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd706).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd707).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd708).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd709).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd710).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd711).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd712).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd713).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd714).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd715).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd716).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd717).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd718).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd719).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd720).Monitor_Est().BOSJudge()
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


