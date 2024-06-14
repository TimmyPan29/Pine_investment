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
var CandleSet htfadd540                     = CandleSet.new()
var CandleSettings SettingsHTFadd540        = CandleSettings.new(htf='540',htfint=540,max_memory=3)
var Candle[] candlesadd540                  = array.new<Candle>(0)
var BOSdata bosdataadd540                   = BOSdata.new()
htfadd540.settings                 := SettingsHTFadd540
htfadd540.candles                  := candlesadd540
htfadd540.bosdata                  := bosdataadd540
var CandleSet htfadd541                     = CandleSet.new()
var CandleSettings SettingsHTFadd541        = CandleSettings.new(htf='541',htfint=541,max_memory=3)
var Candle[] candlesadd541                  = array.new<Candle>(0)
var BOSdata bosdataadd541                   = BOSdata.new()
htfadd541.settings                 := SettingsHTFadd541
htfadd541.candles                  := candlesadd541
htfadd541.bosdata                  := bosdataadd541
var CandleSet htfadd542                     = CandleSet.new()
var CandleSettings SettingsHTFadd542        = CandleSettings.new(htf='542',htfint=542,max_memory=3)
var Candle[] candlesadd542                  = array.new<Candle>(0)
var BOSdata bosdataadd542                   = BOSdata.new()
htfadd542.settings                 := SettingsHTFadd542
htfadd542.candles                  := candlesadd542
htfadd542.bosdata                  := bosdataadd542
var CandleSet htfadd543                     = CandleSet.new()
var CandleSettings SettingsHTFadd543        = CandleSettings.new(htf='543',htfint=543,max_memory=3)
var Candle[] candlesadd543                  = array.new<Candle>(0)
var BOSdata bosdataadd543                   = BOSdata.new()
htfadd543.settings                 := SettingsHTFadd543
htfadd543.candles                  := candlesadd543
htfadd543.bosdata                  := bosdataadd543
var CandleSet htfadd544                     = CandleSet.new()
var CandleSettings SettingsHTFadd544        = CandleSettings.new(htf='544',htfint=544,max_memory=3)
var Candle[] candlesadd544                  = array.new<Candle>(0)
var BOSdata bosdataadd544                   = BOSdata.new()
htfadd544.settings                 := SettingsHTFadd544
htfadd544.candles                  := candlesadd544
htfadd544.bosdata                  := bosdataadd544
var CandleSet htfadd545                     = CandleSet.new()
var CandleSettings SettingsHTFadd545        = CandleSettings.new(htf='545',htfint=545,max_memory=3)
var Candle[] candlesadd545                  = array.new<Candle>(0)
var BOSdata bosdataadd545                   = BOSdata.new()
htfadd545.settings                 := SettingsHTFadd545
htfadd545.candles                  := candlesadd545
htfadd545.bosdata                  := bosdataadd545
var CandleSet htfadd546                     = CandleSet.new()
var CandleSettings SettingsHTFadd546        = CandleSettings.new(htf='546',htfint=546,max_memory=3)
var Candle[] candlesadd546                  = array.new<Candle>(0)
var BOSdata bosdataadd546                   = BOSdata.new()
htfadd546.settings                 := SettingsHTFadd546
htfadd546.candles                  := candlesadd546
htfadd546.bosdata                  := bosdataadd546
var CandleSet htfadd547                     = CandleSet.new()
var CandleSettings SettingsHTFadd547        = CandleSettings.new(htf='547',htfint=547,max_memory=3)
var Candle[] candlesadd547                  = array.new<Candle>(0)
var BOSdata bosdataadd547                   = BOSdata.new()
htfadd547.settings                 := SettingsHTFadd547
htfadd547.candles                  := candlesadd547
htfadd547.bosdata                  := bosdataadd547
var CandleSet htfadd548                     = CandleSet.new()
var CandleSettings SettingsHTFadd548        = CandleSettings.new(htf='548',htfint=548,max_memory=3)
var Candle[] candlesadd548                  = array.new<Candle>(0)
var BOSdata bosdataadd548                   = BOSdata.new()
htfadd548.settings                 := SettingsHTFadd548
htfadd548.candles                  := candlesadd548
htfadd548.bosdata                  := bosdataadd548
var CandleSet htfadd549                     = CandleSet.new()
var CandleSettings SettingsHTFadd549        = CandleSettings.new(htf='549',htfint=549,max_memory=3)
var Candle[] candlesadd549                  = array.new<Candle>(0)
var BOSdata bosdataadd549                   = BOSdata.new()
htfadd549.settings                 := SettingsHTFadd549
htfadd549.candles                  := candlesadd549
htfadd549.bosdata                  := bosdataadd549
var CandleSet htfadd550                     = CandleSet.new()
var CandleSettings SettingsHTFadd550        = CandleSettings.new(htf='550',htfint=550,max_memory=3)
var Candle[] candlesadd550                  = array.new<Candle>(0)
var BOSdata bosdataadd550                   = BOSdata.new()
htfadd550.settings                 := SettingsHTFadd550
htfadd550.candles                  := candlesadd550
htfadd550.bosdata                  := bosdataadd550
var CandleSet htfadd551                     = CandleSet.new()
var CandleSettings SettingsHTFadd551        = CandleSettings.new(htf='551',htfint=551,max_memory=3)
var Candle[] candlesadd551                  = array.new<Candle>(0)
var BOSdata bosdataadd551                   = BOSdata.new()
htfadd551.settings                 := SettingsHTFadd551
htfadd551.candles                  := candlesadd551
htfadd551.bosdata                  := bosdataadd551
var CandleSet htfadd552                     = CandleSet.new()
var CandleSettings SettingsHTFadd552        = CandleSettings.new(htf='552',htfint=552,max_memory=3)
var Candle[] candlesadd552                  = array.new<Candle>(0)
var BOSdata bosdataadd552                   = BOSdata.new()
htfadd552.settings                 := SettingsHTFadd552
htfadd552.candles                  := candlesadd552
htfadd552.bosdata                  := bosdataadd552
var CandleSet htfadd553                     = CandleSet.new()
var CandleSettings SettingsHTFadd553        = CandleSettings.new(htf='553',htfint=553,max_memory=3)
var Candle[] candlesadd553                  = array.new<Candle>(0)
var BOSdata bosdataadd553                   = BOSdata.new()
htfadd553.settings                 := SettingsHTFadd553
htfadd553.candles                  := candlesadd553
htfadd553.bosdata                  := bosdataadd553
var CandleSet htfadd554                     = CandleSet.new()
var CandleSettings SettingsHTFadd554        = CandleSettings.new(htf='554',htfint=554,max_memory=3)
var Candle[] candlesadd554                  = array.new<Candle>(0)
var BOSdata bosdataadd554                   = BOSdata.new()
htfadd554.settings                 := SettingsHTFadd554
htfadd554.candles                  := candlesadd554
htfadd554.bosdata                  := bosdataadd554
var CandleSet htfadd555                     = CandleSet.new()
var CandleSettings SettingsHTFadd555        = CandleSettings.new(htf='555',htfint=555,max_memory=3)
var Candle[] candlesadd555                  = array.new<Candle>(0)
var BOSdata bosdataadd555                   = BOSdata.new()
htfadd555.settings                 := SettingsHTFadd555
htfadd555.candles                  := candlesadd555
htfadd555.bosdata                  := bosdataadd555
var CandleSet htfadd556                     = CandleSet.new()
var CandleSettings SettingsHTFadd556        = CandleSettings.new(htf='556',htfint=556,max_memory=3)
var Candle[] candlesadd556                  = array.new<Candle>(0)
var BOSdata bosdataadd556                   = BOSdata.new()
htfadd556.settings                 := SettingsHTFadd556
htfadd556.candles                  := candlesadd556
htfadd556.bosdata                  := bosdataadd556
var CandleSet htfadd557                     = CandleSet.new()
var CandleSettings SettingsHTFadd557        = CandleSettings.new(htf='557',htfint=557,max_memory=3)
var Candle[] candlesadd557                  = array.new<Candle>(0)
var BOSdata bosdataadd557                   = BOSdata.new()
htfadd557.settings                 := SettingsHTFadd557
htfadd557.candles                  := candlesadd557
htfadd557.bosdata                  := bosdataadd557
var CandleSet htfadd558                     = CandleSet.new()
var CandleSettings SettingsHTFadd558        = CandleSettings.new(htf='558',htfint=558,max_memory=3)
var Candle[] candlesadd558                  = array.new<Candle>(0)
var BOSdata bosdataadd558                   = BOSdata.new()
htfadd558.settings                 := SettingsHTFadd558
htfadd558.candles                  := candlesadd558
htfadd558.bosdata                  := bosdataadd558
var CandleSet htfadd559                     = CandleSet.new()
var CandleSettings SettingsHTFadd559        = CandleSettings.new(htf='559',htfint=559,max_memory=3)
var Candle[] candlesadd559                  = array.new<Candle>(0)
var BOSdata bosdataadd559                   = BOSdata.new()
htfadd559.settings                 := SettingsHTFadd559
htfadd559.candles                  := candlesadd559
htfadd559.bosdata                  := bosdataadd559
var CandleSet htfadd560                     = CandleSet.new()
var CandleSettings SettingsHTFadd560        = CandleSettings.new(htf='560',htfint=560,max_memory=3)
var Candle[] candlesadd560                  = array.new<Candle>(0)
var BOSdata bosdataadd560                   = BOSdata.new()
htfadd560.settings                 := SettingsHTFadd560
htfadd560.candles                  := candlesadd560
htfadd560.bosdata                  := bosdataadd560
var CandleSet htfadd561                     = CandleSet.new()
var CandleSettings SettingsHTFadd561        = CandleSettings.new(htf='561',htfint=561,max_memory=3)
var Candle[] candlesadd561                  = array.new<Candle>(0)
var BOSdata bosdataadd561                   = BOSdata.new()
htfadd561.settings                 := SettingsHTFadd561
htfadd561.candles                  := candlesadd561
htfadd561.bosdata                  := bosdataadd561
var CandleSet htfadd562                     = CandleSet.new()
var CandleSettings SettingsHTFadd562        = CandleSettings.new(htf='562',htfint=562,max_memory=3)
var Candle[] candlesadd562                  = array.new<Candle>(0)
var BOSdata bosdataadd562                   = BOSdata.new()
htfadd562.settings                 := SettingsHTFadd562
htfadd562.candles                  := candlesadd562
htfadd562.bosdata                  := bosdataadd562
var CandleSet htfadd563                     = CandleSet.new()
var CandleSettings SettingsHTFadd563        = CandleSettings.new(htf='563',htfint=563,max_memory=3)
var Candle[] candlesadd563                  = array.new<Candle>(0)
var BOSdata bosdataadd563                   = BOSdata.new()
htfadd563.settings                 := SettingsHTFadd563
htfadd563.candles                  := candlesadd563
htfadd563.bosdata                  := bosdataadd563
var CandleSet htfadd564                     = CandleSet.new()
var CandleSettings SettingsHTFadd564        = CandleSettings.new(htf='564',htfint=564,max_memory=3)
var Candle[] candlesadd564                  = array.new<Candle>(0)
var BOSdata bosdataadd564                   = BOSdata.new()
htfadd564.settings                 := SettingsHTFadd564
htfadd564.candles                  := candlesadd564
htfadd564.bosdata                  := bosdataadd564
var CandleSet htfadd565                     = CandleSet.new()
var CandleSettings SettingsHTFadd565        = CandleSettings.new(htf='565',htfint=565,max_memory=3)
var Candle[] candlesadd565                  = array.new<Candle>(0)
var BOSdata bosdataadd565                   = BOSdata.new()
htfadd565.settings                 := SettingsHTFadd565
htfadd565.candles                  := candlesadd565
htfadd565.bosdata                  := bosdataadd565
var CandleSet htfadd566                     = CandleSet.new()
var CandleSettings SettingsHTFadd566        = CandleSettings.new(htf='566',htfint=566,max_memory=3)
var Candle[] candlesadd566                  = array.new<Candle>(0)
var BOSdata bosdataadd566                   = BOSdata.new()
htfadd566.settings                 := SettingsHTFadd566
htfadd566.candles                  := candlesadd566
htfadd566.bosdata                  := bosdataadd566
var CandleSet htfadd567                     = CandleSet.new()
var CandleSettings SettingsHTFadd567        = CandleSettings.new(htf='567',htfint=567,max_memory=3)
var Candle[] candlesadd567                  = array.new<Candle>(0)
var BOSdata bosdataadd567                   = BOSdata.new()
htfadd567.settings                 := SettingsHTFadd567
htfadd567.candles                  := candlesadd567
htfadd567.bosdata                  := bosdataadd567
var CandleSet htfadd568                     = CandleSet.new()
var CandleSettings SettingsHTFadd568        = CandleSettings.new(htf='568',htfint=568,max_memory=3)
var Candle[] candlesadd568                  = array.new<Candle>(0)
var BOSdata bosdataadd568                   = BOSdata.new()
htfadd568.settings                 := SettingsHTFadd568
htfadd568.candles                  := candlesadd568
htfadd568.bosdata                  := bosdataadd568
var CandleSet htfadd569                     = CandleSet.new()
var CandleSettings SettingsHTFadd569        = CandleSettings.new(htf='569',htfint=569,max_memory=3)
var Candle[] candlesadd569                  = array.new<Candle>(0)
var BOSdata bosdataadd569                   = BOSdata.new()
htfadd569.settings                 := SettingsHTFadd569
htfadd569.candles                  := candlesadd569
htfadd569.bosdata                  := bosdataadd569
var CandleSet htfadd570                     = CandleSet.new()
var CandleSettings SettingsHTFadd570        = CandleSettings.new(htf='570',htfint=570,max_memory=3)
var Candle[] candlesadd570                  = array.new<Candle>(0)
var BOSdata bosdataadd570                   = BOSdata.new()
htfadd570.settings                 := SettingsHTFadd570
htfadd570.candles                  := candlesadd570
htfadd570.bosdata                  := bosdataadd570
var CandleSet htfadd571                     = CandleSet.new()
var CandleSettings SettingsHTFadd571        = CandleSettings.new(htf='571',htfint=571,max_memory=3)
var Candle[] candlesadd571                  = array.new<Candle>(0)
var BOSdata bosdataadd571                   = BOSdata.new()
htfadd571.settings                 := SettingsHTFadd571
htfadd571.candles                  := candlesadd571
htfadd571.bosdata                  := bosdataadd571
var CandleSet htfadd572                     = CandleSet.new()
var CandleSettings SettingsHTFadd572        = CandleSettings.new(htf='572',htfint=572,max_memory=3)
var Candle[] candlesadd572                  = array.new<Candle>(0)
var BOSdata bosdataadd572                   = BOSdata.new()
htfadd572.settings                 := SettingsHTFadd572
htfadd572.candles                  := candlesadd572
htfadd572.bosdata                  := bosdataadd572
var CandleSet htfadd573                     = CandleSet.new()
var CandleSettings SettingsHTFadd573        = CandleSettings.new(htf='573',htfint=573,max_memory=3)
var Candle[] candlesadd573                  = array.new<Candle>(0)
var BOSdata bosdataadd573                   = BOSdata.new()
htfadd573.settings                 := SettingsHTFadd573
htfadd573.candles                  := candlesadd573
htfadd573.bosdata                  := bosdataadd573
var CandleSet htfadd574                     = CandleSet.new()
var CandleSettings SettingsHTFadd574        = CandleSettings.new(htf='574',htfint=574,max_memory=3)
var Candle[] candlesadd574                  = array.new<Candle>(0)
var BOSdata bosdataadd574                   = BOSdata.new()
htfadd574.settings                 := SettingsHTFadd574
htfadd574.candles                  := candlesadd574
htfadd574.bosdata                  := bosdataadd574
var CandleSet htfadd575                     = CandleSet.new()
var CandleSettings SettingsHTFadd575        = CandleSettings.new(htf='575',htfint=575,max_memory=3)
var Candle[] candlesadd575                  = array.new<Candle>(0)
var BOSdata bosdataadd575                   = BOSdata.new()
htfadd575.settings                 := SettingsHTFadd575
htfadd575.candles                  := candlesadd575
htfadd575.bosdata                  := bosdataadd575
var CandleSet htfadd576                     = CandleSet.new()
var CandleSettings SettingsHTFadd576        = CandleSettings.new(htf='576',htfint=576,max_memory=3)
var Candle[] candlesadd576                  = array.new<Candle>(0)
var BOSdata bosdataadd576                   = BOSdata.new()
htfadd576.settings                 := SettingsHTFadd576
htfadd576.candles                  := candlesadd576
htfadd576.bosdata                  := bosdataadd576
var CandleSet htfadd577                     = CandleSet.new()
var CandleSettings SettingsHTFadd577        = CandleSettings.new(htf='577',htfint=577,max_memory=3)
var Candle[] candlesadd577                  = array.new<Candle>(0)
var BOSdata bosdataadd577                   = BOSdata.new()
htfadd577.settings                 := SettingsHTFadd577
htfadd577.candles                  := candlesadd577
htfadd577.bosdata                  := bosdataadd577
var CandleSet htfadd578                     = CandleSet.new()
var CandleSettings SettingsHTFadd578        = CandleSettings.new(htf='578',htfint=578,max_memory=3)
var Candle[] candlesadd578                  = array.new<Candle>(0)
var BOSdata bosdataadd578                   = BOSdata.new()
htfadd578.settings                 := SettingsHTFadd578
htfadd578.candles                  := candlesadd578
htfadd578.bosdata                  := bosdataadd578
var CandleSet htfadd579                     = CandleSet.new()
var CandleSettings SettingsHTFadd579        = CandleSettings.new(htf='579',htfint=579,max_memory=3)
var Candle[] candlesadd579                  = array.new<Candle>(0)
var BOSdata bosdataadd579                   = BOSdata.new()
htfadd579.settings                 := SettingsHTFadd579
htfadd579.candles                  := candlesadd579
htfadd579.bosdata                  := bosdataadd579
var CandleSet htfadd580                     = CandleSet.new()
var CandleSettings SettingsHTFadd580        = CandleSettings.new(htf='580',htfint=580,max_memory=3)
var Candle[] candlesadd580                  = array.new<Candle>(0)
var BOSdata bosdataadd580                   = BOSdata.new()
htfadd580.settings                 := SettingsHTFadd580
htfadd580.candles                  := candlesadd580
htfadd580.bosdata                  := bosdataadd580
var CandleSet htfadd581                     = CandleSet.new()
var CandleSettings SettingsHTFadd581        = CandleSettings.new(htf='581',htfint=581,max_memory=3)
var Candle[] candlesadd581                  = array.new<Candle>(0)
var BOSdata bosdataadd581                   = BOSdata.new()
htfadd581.settings                 := SettingsHTFadd581
htfadd581.candles                  := candlesadd581
htfadd581.bosdata                  := bosdataadd581
var CandleSet htfadd582                     = CandleSet.new()
var CandleSettings SettingsHTFadd582        = CandleSettings.new(htf='582',htfint=582,max_memory=3)
var Candle[] candlesadd582                  = array.new<Candle>(0)
var BOSdata bosdataadd582                   = BOSdata.new()
htfadd582.settings                 := SettingsHTFadd582
htfadd582.candles                  := candlesadd582
htfadd582.bosdata                  := bosdataadd582
var CandleSet htfadd583                     = CandleSet.new()
var CandleSettings SettingsHTFadd583        = CandleSettings.new(htf='583',htfint=583,max_memory=3)
var Candle[] candlesadd583                  = array.new<Candle>(0)
var BOSdata bosdataadd583                   = BOSdata.new()
htfadd583.settings                 := SettingsHTFadd583
htfadd583.candles                  := candlesadd583
htfadd583.bosdata                  := bosdataadd583
var CandleSet htfadd584                     = CandleSet.new()
var CandleSettings SettingsHTFadd584        = CandleSettings.new(htf='584',htfint=584,max_memory=3)
var Candle[] candlesadd584                  = array.new<Candle>(0)
var BOSdata bosdataadd584                   = BOSdata.new()
htfadd584.settings                 := SettingsHTFadd584
htfadd584.candles                  := candlesadd584
htfadd584.bosdata                  := bosdataadd584
var CandleSet htfadd585                     = CandleSet.new()
var CandleSettings SettingsHTFadd585        = CandleSettings.new(htf='585',htfint=585,max_memory=3)
var Candle[] candlesadd585                  = array.new<Candle>(0)
var BOSdata bosdataadd585                   = BOSdata.new()
htfadd585.settings                 := SettingsHTFadd585
htfadd585.candles                  := candlesadd585
htfadd585.bosdata                  := bosdataadd585
var CandleSet htfadd586                     = CandleSet.new()
var CandleSettings SettingsHTFadd586        = CandleSettings.new(htf='586',htfint=586,max_memory=3)
var Candle[] candlesadd586                  = array.new<Candle>(0)
var BOSdata bosdataadd586                   = BOSdata.new()
htfadd586.settings                 := SettingsHTFadd586
htfadd586.candles                  := candlesadd586
htfadd586.bosdata                  := bosdataadd586
var CandleSet htfadd587                     = CandleSet.new()
var CandleSettings SettingsHTFadd587        = CandleSettings.new(htf='587',htfint=587,max_memory=3)
var Candle[] candlesadd587                  = array.new<Candle>(0)
var BOSdata bosdataadd587                   = BOSdata.new()
htfadd587.settings                 := SettingsHTFadd587
htfadd587.candles                  := candlesadd587
htfadd587.bosdata                  := bosdataadd587
var CandleSet htfadd588                     = CandleSet.new()
var CandleSettings SettingsHTFadd588        = CandleSettings.new(htf='588',htfint=588,max_memory=3)
var Candle[] candlesadd588                  = array.new<Candle>(0)
var BOSdata bosdataadd588                   = BOSdata.new()
htfadd588.settings                 := SettingsHTFadd588
htfadd588.candles                  := candlesadd588
htfadd588.bosdata                  := bosdataadd588
var CandleSet htfadd589                     = CandleSet.new()
var CandleSettings SettingsHTFadd589        = CandleSettings.new(htf='589',htfint=589,max_memory=3)
var Candle[] candlesadd589                  = array.new<Candle>(0)
var BOSdata bosdataadd589                   = BOSdata.new()
htfadd589.settings                 := SettingsHTFadd589
htfadd589.candles                  := candlesadd589
htfadd589.bosdata                  := bosdataadd589
var CandleSet htfadd590                     = CandleSet.new()
var CandleSettings SettingsHTFadd590        = CandleSettings.new(htf='590',htfint=590,max_memory=3)
var Candle[] candlesadd590                  = array.new<Candle>(0)
var BOSdata bosdataadd590                   = BOSdata.new()
htfadd590.settings                 := SettingsHTFadd590
htfadd590.candles                  := candlesadd590
htfadd590.bosdata                  := bosdataadd590
var CandleSet htfadd591                     = CandleSet.new()
var CandleSettings SettingsHTFadd591        = CandleSettings.new(htf='591',htfint=591,max_memory=3)
var Candle[] candlesadd591                  = array.new<Candle>(0)
var BOSdata bosdataadd591                   = BOSdata.new()
htfadd591.settings                 := SettingsHTFadd591
htfadd591.candles                  := candlesadd591
htfadd591.bosdata                  := bosdataadd591
var CandleSet htfadd592                     = CandleSet.new()
var CandleSettings SettingsHTFadd592        = CandleSettings.new(htf='592',htfint=592,max_memory=3)
var Candle[] candlesadd592                  = array.new<Candle>(0)
var BOSdata bosdataadd592                   = BOSdata.new()
htfadd592.settings                 := SettingsHTFadd592
htfadd592.candles                  := candlesadd592
htfadd592.bosdata                  := bosdataadd592
var CandleSet htfadd593                     = CandleSet.new()
var CandleSettings SettingsHTFadd593        = CandleSettings.new(htf='593',htfint=593,max_memory=3)
var Candle[] candlesadd593                  = array.new<Candle>(0)
var BOSdata bosdataadd593                   = BOSdata.new()
htfadd593.settings                 := SettingsHTFadd593
htfadd593.candles                  := candlesadd593
htfadd593.bosdata                  := bosdataadd593
var CandleSet htfadd594                     = CandleSet.new()
var CandleSettings SettingsHTFadd594        = CandleSettings.new(htf='594',htfint=594,max_memory=3)
var Candle[] candlesadd594                  = array.new<Candle>(0)
var BOSdata bosdataadd594                   = BOSdata.new()
htfadd594.settings                 := SettingsHTFadd594
htfadd594.candles                  := candlesadd594
htfadd594.bosdata                  := bosdataadd594
var CandleSet htfadd595                     = CandleSet.new()
var CandleSettings SettingsHTFadd595        = CandleSettings.new(htf='595',htfint=595,max_memory=3)
var Candle[] candlesadd595                  = array.new<Candle>(0)
var BOSdata bosdataadd595                   = BOSdata.new()
htfadd595.settings                 := SettingsHTFadd595
htfadd595.candles                  := candlesadd595
htfadd595.bosdata                  := bosdataadd595
var CandleSet htfadd596                     = CandleSet.new()
var CandleSettings SettingsHTFadd596        = CandleSettings.new(htf='596',htfint=596,max_memory=3)
var Candle[] candlesadd596                  = array.new<Candle>(0)
var BOSdata bosdataadd596                   = BOSdata.new()
htfadd596.settings                 := SettingsHTFadd596
htfadd596.candles                  := candlesadd596
htfadd596.bosdata                  := bosdataadd596
var CandleSet htfadd597                     = CandleSet.new()
var CandleSettings SettingsHTFadd597        = CandleSettings.new(htf='597',htfint=597,max_memory=3)
var Candle[] candlesadd597                  = array.new<Candle>(0)
var BOSdata bosdataadd597                   = BOSdata.new()
htfadd597.settings                 := SettingsHTFadd597
htfadd597.candles                  := candlesadd597
htfadd597.bosdata                  := bosdataadd597
var CandleSet htfadd598                     = CandleSet.new()
var CandleSettings SettingsHTFadd598        = CandleSettings.new(htf='598',htfint=598,max_memory=3)
var Candle[] candlesadd598                  = array.new<Candle>(0)
var BOSdata bosdataadd598                   = BOSdata.new()
htfadd598.settings                 := SettingsHTFadd598
htfadd598.candles                  := candlesadd598
htfadd598.bosdata                  := bosdataadd598
var CandleSet htfadd599                     = CandleSet.new()
var CandleSettings SettingsHTFadd599        = CandleSettings.new(htf='599',htfint=599,max_memory=3)
var Candle[] candlesadd599                  = array.new<Candle>(0)
var BOSdata bosdataadd599                   = BOSdata.new()
htfadd599.settings                 := SettingsHTFadd599
htfadd599.candles                  := candlesadd599
htfadd599.bosdata                  := bosdataadd599
var CandleSet htfadd600                     = CandleSet.new()
var CandleSettings SettingsHTFadd600        = CandleSettings.new(htf='600',htfint=600,max_memory=3)
var Candle[] candlesadd600                  = array.new<Candle>(0)
var BOSdata bosdataadd600                   = BOSdata.new()
htfadd600.settings                 := SettingsHTFadd600
htfadd600.candles                  := candlesadd600
htfadd600.bosdata                  := bosdataadd600
var CandleSet htfadd601                     = CandleSet.new()
var CandleSettings SettingsHTFadd601        = CandleSettings.new(htf='601',htfint=601,max_memory=3)
var Candle[] candlesadd601                  = array.new<Candle>(0)
var BOSdata bosdataadd601                   = BOSdata.new()
htfadd601.settings                 := SettingsHTFadd601
htfadd601.candles                  := candlesadd601
htfadd601.bosdata                  := bosdataadd601
var CandleSet htfadd602                     = CandleSet.new()
var CandleSettings SettingsHTFadd602        = CandleSettings.new(htf='602',htfint=602,max_memory=3)
var Candle[] candlesadd602                  = array.new<Candle>(0)
var BOSdata bosdataadd602                   = BOSdata.new()
htfadd602.settings                 := SettingsHTFadd602
htfadd602.candles                  := candlesadd602
htfadd602.bosdata                  := bosdataadd602
var CandleSet htfadd603                     = CandleSet.new()
var CandleSettings SettingsHTFadd603        = CandleSettings.new(htf='603',htfint=603,max_memory=3)
var Candle[] candlesadd603                  = array.new<Candle>(0)
var BOSdata bosdataadd603                   = BOSdata.new()
htfadd603.settings                 := SettingsHTFadd603
htfadd603.candles                  := candlesadd603
htfadd603.bosdata                  := bosdataadd603
var CandleSet htfadd604                     = CandleSet.new()
var CandleSettings SettingsHTFadd604        = CandleSettings.new(htf='604',htfint=604,max_memory=3)
var Candle[] candlesadd604                  = array.new<Candle>(0)
var BOSdata bosdataadd604                   = BOSdata.new()
htfadd604.settings                 := SettingsHTFadd604
htfadd604.candles                  := candlesadd604
htfadd604.bosdata                  := bosdataadd604
var CandleSet htfadd605                     = CandleSet.new()
var CandleSettings SettingsHTFadd605        = CandleSettings.new(htf='605',htfint=605,max_memory=3)
var Candle[] candlesadd605                  = array.new<Candle>(0)
var BOSdata bosdataadd605                   = BOSdata.new()
htfadd605.settings                 := SettingsHTFadd605
htfadd605.candles                  := candlesadd605
htfadd605.bosdata                  := bosdataadd605
var CandleSet htfadd606                     = CandleSet.new()
var CandleSettings SettingsHTFadd606        = CandleSettings.new(htf='606',htfint=606,max_memory=3)
var Candle[] candlesadd606                  = array.new<Candle>(0)
var BOSdata bosdataadd606                   = BOSdata.new()
htfadd606.settings                 := SettingsHTFadd606
htfadd606.candles                  := candlesadd606
htfadd606.bosdata                  := bosdataadd606
var CandleSet htfadd607                     = CandleSet.new()
var CandleSettings SettingsHTFadd607        = CandleSettings.new(htf='607',htfint=607,max_memory=3)
var Candle[] candlesadd607                  = array.new<Candle>(0)
var BOSdata bosdataadd607                   = BOSdata.new()
htfadd607.settings                 := SettingsHTFadd607
htfadd607.candles                  := candlesadd607
htfadd607.bosdata                  := bosdataadd607
var CandleSet htfadd608                     = CandleSet.new()
var CandleSettings SettingsHTFadd608        = CandleSettings.new(htf='608',htfint=608,max_memory=3)
var Candle[] candlesadd608                  = array.new<Candle>(0)
var BOSdata bosdataadd608                   = BOSdata.new()
htfadd608.settings                 := SettingsHTFadd608
htfadd608.candles                  := candlesadd608
htfadd608.bosdata                  := bosdataadd608
var CandleSet htfadd609                     = CandleSet.new()
var CandleSettings SettingsHTFadd609        = CandleSettings.new(htf='609',htfint=609,max_memory=3)
var Candle[] candlesadd609                  = array.new<Candle>(0)
var BOSdata bosdataadd609                   = BOSdata.new()
htfadd609.settings                 := SettingsHTFadd609
htfadd609.candles                  := candlesadd609
htfadd609.bosdata                  := bosdataadd609
var CandleSet htfadd610                     = CandleSet.new()
var CandleSettings SettingsHTFadd610        = CandleSettings.new(htf='610',htfint=610,max_memory=3)
var Candle[] candlesadd610                  = array.new<Candle>(0)
var BOSdata bosdataadd610                   = BOSdata.new()
htfadd610.settings                 := SettingsHTFadd610
htfadd610.candles                  := candlesadd610
htfadd610.bosdata                  := bosdataadd610
var CandleSet htfadd611                     = CandleSet.new()
var CandleSettings SettingsHTFadd611        = CandleSettings.new(htf='611',htfint=611,max_memory=3)
var Candle[] candlesadd611                  = array.new<Candle>(0)
var BOSdata bosdataadd611                   = BOSdata.new()
htfadd611.settings                 := SettingsHTFadd611
htfadd611.candles                  := candlesadd611
htfadd611.bosdata                  := bosdataadd611
var CandleSet htfadd612                     = CandleSet.new()
var CandleSettings SettingsHTFadd612        = CandleSettings.new(htf='612',htfint=612,max_memory=3)
var Candle[] candlesadd612                  = array.new<Candle>(0)
var BOSdata bosdataadd612                   = BOSdata.new()
htfadd612.settings                 := SettingsHTFadd612
htfadd612.candles                  := candlesadd612
htfadd612.bosdata                  := bosdataadd612
var CandleSet htfadd613                     = CandleSet.new()
var CandleSettings SettingsHTFadd613        = CandleSettings.new(htf='613',htfint=613,max_memory=3)
var Candle[] candlesadd613                  = array.new<Candle>(0)
var BOSdata bosdataadd613                   = BOSdata.new()
htfadd613.settings                 := SettingsHTFadd613
htfadd613.candles                  := candlesadd613
htfadd613.bosdata                  := bosdataadd613
var CandleSet htfadd614                     = CandleSet.new()
var CandleSettings SettingsHTFadd614        = CandleSettings.new(htf='614',htfint=614,max_memory=3)
var Candle[] candlesadd614                  = array.new<Candle>(0)
var BOSdata bosdataadd614                   = BOSdata.new()
htfadd614.settings                 := SettingsHTFadd614
htfadd614.candles                  := candlesadd614
htfadd614.bosdata                  := bosdataadd614
var CandleSet htfadd615                     = CandleSet.new()
var CandleSettings SettingsHTFadd615        = CandleSettings.new(htf='615',htfint=615,max_memory=3)
var Candle[] candlesadd615                  = array.new<Candle>(0)
var BOSdata bosdataadd615                   = BOSdata.new()
htfadd615.settings                 := SettingsHTFadd615
htfadd615.candles                  := candlesadd615
htfadd615.bosdata                  := bosdataadd615
var CandleSet htfadd616                     = CandleSet.new()
var CandleSettings SettingsHTFadd616        = CandleSettings.new(htf='616',htfint=616,max_memory=3)
var Candle[] candlesadd616                  = array.new<Candle>(0)
var BOSdata bosdataadd616                   = BOSdata.new()
htfadd616.settings                 := SettingsHTFadd616
htfadd616.candles                  := candlesadd616
htfadd616.bosdata                  := bosdataadd616
var CandleSet htfadd617                     = CandleSet.new()
var CandleSettings SettingsHTFadd617        = CandleSettings.new(htf='617',htfint=617,max_memory=3)
var Candle[] candlesadd617                  = array.new<Candle>(0)
var BOSdata bosdataadd617                   = BOSdata.new()
htfadd617.settings                 := SettingsHTFadd617
htfadd617.candles                  := candlesadd617
htfadd617.bosdata                  := bosdataadd617
var CandleSet htfadd618                     = CandleSet.new()
var CandleSettings SettingsHTFadd618        = CandleSettings.new(htf='618',htfint=618,max_memory=3)
var Candle[] candlesadd618                  = array.new<Candle>(0)
var BOSdata bosdataadd618                   = BOSdata.new()
htfadd618.settings                 := SettingsHTFadd618
htfadd618.candles                  := candlesadd618
htfadd618.bosdata                  := bosdataadd618
var CandleSet htfadd619                     = CandleSet.new()
var CandleSettings SettingsHTFadd619        = CandleSettings.new(htf='619',htfint=619,max_memory=3)
var Candle[] candlesadd619                  = array.new<Candle>(0)
var BOSdata bosdataadd619                   = BOSdata.new()
htfadd619.settings                 := SettingsHTFadd619
htfadd619.candles                  := candlesadd619
htfadd619.bosdata                  := bosdataadd619
var CandleSet htfadd620                     = CandleSet.new()
var CandleSettings SettingsHTFadd620        = CandleSettings.new(htf='620',htfint=620,max_memory=3)
var Candle[] candlesadd620                  = array.new<Candle>(0)
var BOSdata bosdataadd620                   = BOSdata.new()
htfadd620.settings                 := SettingsHTFadd620
htfadd620.candles                  := candlesadd620
htfadd620.bosdata                  := bosdataadd620
var CandleSet htfadd621                     = CandleSet.new()
var CandleSettings SettingsHTFadd621        = CandleSettings.new(htf='621',htfint=621,max_memory=3)
var Candle[] candlesadd621                  = array.new<Candle>(0)
var BOSdata bosdataadd621                   = BOSdata.new()
htfadd621.settings                 := SettingsHTFadd621
htfadd621.candles                  := candlesadd621
htfadd621.bosdata                  := bosdataadd621
var CandleSet htfadd622                     = CandleSet.new()
var CandleSettings SettingsHTFadd622        = CandleSettings.new(htf='622',htfint=622,max_memory=3)
var Candle[] candlesadd622                  = array.new<Candle>(0)
var BOSdata bosdataadd622                   = BOSdata.new()
htfadd622.settings                 := SettingsHTFadd622
htfadd622.candles                  := candlesadd622
htfadd622.bosdata                  := bosdataadd622
var CandleSet htfadd623                     = CandleSet.new()
var CandleSettings SettingsHTFadd623        = CandleSettings.new(htf='623',htfint=623,max_memory=3)
var Candle[] candlesadd623                  = array.new<Candle>(0)
var BOSdata bosdataadd623                   = BOSdata.new()
htfadd623.settings                 := SettingsHTFadd623
htfadd623.candles                  := candlesadd623
htfadd623.bosdata                  := bosdataadd623
var CandleSet htfadd624                     = CandleSet.new()
var CandleSettings SettingsHTFadd624        = CandleSettings.new(htf='624',htfint=624,max_memory=3)
var Candle[] candlesadd624                  = array.new<Candle>(0)
var BOSdata bosdataadd624                   = BOSdata.new()
htfadd624.settings                 := SettingsHTFadd624
htfadd624.candles                  := candlesadd624
htfadd624.bosdata                  := bosdataadd624
var CandleSet htfadd625                     = CandleSet.new()
var CandleSettings SettingsHTFadd625        = CandleSettings.new(htf='625',htfint=625,max_memory=3)
var Candle[] candlesadd625                  = array.new<Candle>(0)
var BOSdata bosdataadd625                   = BOSdata.new()
htfadd625.settings                 := SettingsHTFadd625
htfadd625.candles                  := candlesadd625
htfadd625.bosdata                  := bosdataadd625
var CandleSet htfadd626                     = CandleSet.new()
var CandleSettings SettingsHTFadd626        = CandleSettings.new(htf='626',htfint=626,max_memory=3)
var Candle[] candlesadd626                  = array.new<Candle>(0)
var BOSdata bosdataadd626                   = BOSdata.new()
htfadd626.settings                 := SettingsHTFadd626
htfadd626.candles                  := candlesadd626
htfadd626.bosdata                  := bosdataadd626
var CandleSet htfadd627                     = CandleSet.new()
var CandleSettings SettingsHTFadd627        = CandleSettings.new(htf='627',htfint=627,max_memory=3)
var Candle[] candlesadd627                  = array.new<Candle>(0)
var BOSdata bosdataadd627                   = BOSdata.new()
htfadd627.settings                 := SettingsHTFadd627
htfadd627.candles                  := candlesadd627
htfadd627.bosdata                  := bosdataadd627
var CandleSet htfadd628                     = CandleSet.new()
var CandleSettings SettingsHTFadd628        = CandleSettings.new(htf='628',htfint=628,max_memory=3)
var Candle[] candlesadd628                  = array.new<Candle>(0)
var BOSdata bosdataadd628                   = BOSdata.new()
htfadd628.settings                 := SettingsHTFadd628
htfadd628.candles                  := candlesadd628
htfadd628.bosdata                  := bosdataadd628
var CandleSet htfadd629                     = CandleSet.new()
var CandleSettings SettingsHTFadd629        = CandleSettings.new(htf='629',htfint=629,max_memory=3)
var Candle[] candlesadd629                  = array.new<Candle>(0)
var BOSdata bosdataadd629                   = BOSdata.new()
htfadd629.settings                 := SettingsHTFadd629
htfadd629.candles                  := candlesadd629
htfadd629.bosdata                  := bosdataadd629
var CandleSet htfadd630                     = CandleSet.new()
var CandleSettings SettingsHTFadd630        = CandleSettings.new(htf='630',htfint=630,max_memory=3)
var Candle[] candlesadd630                  = array.new<Candle>(0)
var BOSdata bosdataadd630                   = BOSdata.new()
htfadd630.settings                 := SettingsHTFadd630
htfadd630.candles                  := candlesadd630
htfadd630.bosdata                  := bosdataadd630

htfadd540.Monitor().BOSJudge()
htfadd541.Monitor().BOSJudge()
htfadd542.Monitor().BOSJudge()
htfadd543.Monitor().BOSJudge()
htfadd544.Monitor().BOSJudge()
htfadd545.Monitor().BOSJudge()
htfadd546.Monitor().BOSJudge()
htfadd547.Monitor().BOSJudge()
htfadd548.Monitor().BOSJudge()
htfadd549.Monitor().BOSJudge()
htfadd550.Monitor().BOSJudge()
htfadd551.Monitor().BOSJudge()
htfadd552.Monitor().BOSJudge()
htfadd553.Monitor().BOSJudge()
htfadd554.Monitor().BOSJudge()
htfadd555.Monitor().BOSJudge()
htfadd556.Monitor().BOSJudge()
htfadd557.Monitor().BOSJudge()
htfadd558.Monitor().BOSJudge()
htfadd559.Monitor().BOSJudge()
htfadd560.Monitor().BOSJudge()
htfadd561.Monitor().BOSJudge()
htfadd562.Monitor().BOSJudge()
htfadd563.Monitor().BOSJudge()
htfadd564.Monitor().BOSJudge()
htfadd565.Monitor().BOSJudge()
htfadd566.Monitor().BOSJudge()
htfadd567.Monitor().BOSJudge()
htfadd568.Monitor().BOSJudge()
htfadd569.Monitor().BOSJudge()
htfadd570.Monitor().BOSJudge()
htfadd571.Monitor().BOSJudge()
htfadd572.Monitor().BOSJudge()
htfadd573.Monitor().BOSJudge()
htfadd574.Monitor().BOSJudge()
htfadd575.Monitor().BOSJudge()
htfadd576.Monitor().BOSJudge()
htfadd577.Monitor().BOSJudge()
htfadd578.Monitor().BOSJudge()
htfadd579.Monitor().BOSJudge()
htfadd580.Monitor().BOSJudge()
htfadd581.Monitor().BOSJudge()
htfadd582.Monitor().BOSJudge()
htfadd583.Monitor().BOSJudge()
htfadd584.Monitor().BOSJudge()
htfadd585.Monitor().BOSJudge()
htfadd586.Monitor().BOSJudge()
htfadd587.Monitor().BOSJudge()
htfadd588.Monitor().BOSJudge()
htfadd589.Monitor().BOSJudge()
htfadd590.Monitor().BOSJudge()
htfadd591.Monitor().BOSJudge()
htfadd592.Monitor().BOSJudge()
htfadd593.Monitor().BOSJudge()
htfadd594.Monitor().BOSJudge()
htfadd595.Monitor().BOSJudge()
htfadd596.Monitor().BOSJudge()
htfadd597.Monitor().BOSJudge()
htfadd598.Monitor().BOSJudge()
htfadd599.Monitor().BOSJudge()
htfadd600.Monitor().BOSJudge()
htfadd601.Monitor().BOSJudge()
htfadd602.Monitor().BOSJudge()
htfadd603.Monitor().BOSJudge()
htfadd604.Monitor().BOSJudge()
htfadd605.Monitor().BOSJudge()
htfadd606.Monitor().BOSJudge()
htfadd607.Monitor().BOSJudge()
htfadd608.Monitor().BOSJudge()
htfadd609.Monitor().BOSJudge()
htfadd610.Monitor().BOSJudge()
htfadd611.Monitor().BOSJudge()
htfadd612.Monitor().BOSJudge()
htfadd613.Monitor().BOSJudge()
htfadd614.Monitor().BOSJudge()
htfadd615.Monitor().BOSJudge()
htfadd616.Monitor().BOSJudge()
htfadd617.Monitor().BOSJudge()
htfadd618.Monitor().BOSJudge()
htfadd619.Monitor().BOSJudge()
htfadd620.Monitor().BOSJudge()
htfadd621.Monitor().BOSJudge()
htfadd622.Monitor().BOSJudge()
htfadd623.Monitor().BOSJudge()
htfadd624.Monitor().BOSJudge()
htfadd625.Monitor().BOSJudge()
htfadd626.Monitor().BOSJudge()
htfadd627.Monitor().BOSJudge()
htfadd628.Monitor().BOSJudge()
htfadd629.Monitor().BOSJudge()
htfadd630.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd540)
    LowestsbuSet(lowestsbu, htfadd540)
    HighestsbdSet(highestsbd, htfadd541)
    LowestsbuSet(lowestsbu, htfadd541)
    HighestsbdSet(highestsbd, htfadd542)
    LowestsbuSet(lowestsbu, htfadd542)
    HighestsbdSet(highestsbd, htfadd543)
    LowestsbuSet(lowestsbu, htfadd543)
    HighestsbdSet(highestsbd, htfadd544)
    LowestsbuSet(lowestsbu, htfadd544)
    HighestsbdSet(highestsbd, htfadd545)
    LowestsbuSet(lowestsbu, htfadd545)
    HighestsbdSet(highestsbd, htfadd546)
    LowestsbuSet(lowestsbu, htfadd546)
    HighestsbdSet(highestsbd, htfadd547)
    LowestsbuSet(lowestsbu, htfadd547)
    HighestsbdSet(highestsbd, htfadd548)
    LowestsbuSet(lowestsbu, htfadd548)
    HighestsbdSet(highestsbd, htfadd549)
    LowestsbuSet(lowestsbu, htfadd549)
    HighestsbdSet(highestsbd, htfadd550)
    LowestsbuSet(lowestsbu, htfadd550)
    HighestsbdSet(highestsbd, htfadd551)
    LowestsbuSet(lowestsbu, htfadd551)
    HighestsbdSet(highestsbd, htfadd552)
    LowestsbuSet(lowestsbu, htfadd552)
    HighestsbdSet(highestsbd, htfadd553)
    LowestsbuSet(lowestsbu, htfadd553)
    HighestsbdSet(highestsbd, htfadd554)
    LowestsbuSet(lowestsbu, htfadd554)
    HighestsbdSet(highestsbd, htfadd555)
    LowestsbuSet(lowestsbu, htfadd555)
    HighestsbdSet(highestsbd, htfadd556)
    LowestsbuSet(lowestsbu, htfadd556)
    HighestsbdSet(highestsbd, htfadd557)
    LowestsbuSet(lowestsbu, htfadd557)
    HighestsbdSet(highestsbd, htfadd558)
    LowestsbuSet(lowestsbu, htfadd558)
    HighestsbdSet(highestsbd, htfadd559)
    LowestsbuSet(lowestsbu, htfadd559)
    HighestsbdSet(highestsbd, htfadd560)
    LowestsbuSet(lowestsbu, htfadd560)
    HighestsbdSet(highestsbd, htfadd561)
    LowestsbuSet(lowestsbu, htfadd561)
    HighestsbdSet(highestsbd, htfadd562)
    LowestsbuSet(lowestsbu, htfadd562)
    HighestsbdSet(highestsbd, htfadd563)
    LowestsbuSet(lowestsbu, htfadd563)
    HighestsbdSet(highestsbd, htfadd564)
    LowestsbuSet(lowestsbu, htfadd564)
    HighestsbdSet(highestsbd, htfadd565)
    LowestsbuSet(lowestsbu, htfadd565)
    HighestsbdSet(highestsbd, htfadd566)
    LowestsbuSet(lowestsbu, htfadd566)
    HighestsbdSet(highestsbd, htfadd567)
    LowestsbuSet(lowestsbu, htfadd567)
    HighestsbdSet(highestsbd, htfadd568)
    LowestsbuSet(lowestsbu, htfadd568)
    HighestsbdSet(highestsbd, htfadd569)
    LowestsbuSet(lowestsbu, htfadd569)
    HighestsbdSet(highestsbd, htfadd570)
    LowestsbuSet(lowestsbu, htfadd570)
    HighestsbdSet(highestsbd, htfadd571)
    LowestsbuSet(lowestsbu, htfadd571)
    HighestsbdSet(highestsbd, htfadd572)
    LowestsbuSet(lowestsbu, htfadd572)
    HighestsbdSet(highestsbd, htfadd573)
    LowestsbuSet(lowestsbu, htfadd573)
    HighestsbdSet(highestsbd, htfadd574)
    LowestsbuSet(lowestsbu, htfadd574)
    HighestsbdSet(highestsbd, htfadd575)
    LowestsbuSet(lowestsbu, htfadd575)
    HighestsbdSet(highestsbd, htfadd576)
    LowestsbuSet(lowestsbu, htfadd576)
    HighestsbdSet(highestsbd, htfadd577)
    LowestsbuSet(lowestsbu, htfadd577)
    HighestsbdSet(highestsbd, htfadd578)
    LowestsbuSet(lowestsbu, htfadd578)
    HighestsbdSet(highestsbd, htfadd579)
    LowestsbuSet(lowestsbu, htfadd579)
    HighestsbdSet(highestsbd, htfadd580)
    LowestsbuSet(lowestsbu, htfadd580)
    HighestsbdSet(highestsbd, htfadd581)
    LowestsbuSet(lowestsbu, htfadd581)
    HighestsbdSet(highestsbd, htfadd582)
    LowestsbuSet(lowestsbu, htfadd582)
    HighestsbdSet(highestsbd, htfadd583)
    LowestsbuSet(lowestsbu, htfadd583)
    HighestsbdSet(highestsbd, htfadd584)
    LowestsbuSet(lowestsbu, htfadd584)
    HighestsbdSet(highestsbd, htfadd585)
    LowestsbuSet(lowestsbu, htfadd585)
    HighestsbdSet(highestsbd, htfadd586)
    LowestsbuSet(lowestsbu, htfadd586)
    HighestsbdSet(highestsbd, htfadd587)
    LowestsbuSet(lowestsbu, htfadd587)
    HighestsbdSet(highestsbd, htfadd588)
    LowestsbuSet(lowestsbu, htfadd588)
    HighestsbdSet(highestsbd, htfadd589)
    LowestsbuSet(lowestsbu, htfadd589)
    HighestsbdSet(highestsbd, htfadd590)
    LowestsbuSet(lowestsbu, htfadd590)
    HighestsbdSet(highestsbd, htfadd591)
    LowestsbuSet(lowestsbu, htfadd591)
    HighestsbdSet(highestsbd, htfadd592)
    LowestsbuSet(lowestsbu, htfadd592)
    HighestsbdSet(highestsbd, htfadd593)
    LowestsbuSet(lowestsbu, htfadd593)
    HighestsbdSet(highestsbd, htfadd594)
    LowestsbuSet(lowestsbu, htfadd594)
    HighestsbdSet(highestsbd, htfadd595)
    LowestsbuSet(lowestsbu, htfadd595)
    HighestsbdSet(highestsbd, htfadd596)
    LowestsbuSet(lowestsbu, htfadd596)
    HighestsbdSet(highestsbd, htfadd597)
    LowestsbuSet(lowestsbu, htfadd597)
    HighestsbdSet(highestsbd, htfadd598)
    LowestsbuSet(lowestsbu, htfadd598)
    HighestsbdSet(highestsbd, htfadd599)
    LowestsbuSet(lowestsbu, htfadd599)
    HighestsbdSet(highestsbd, htfadd600)
    LowestsbuSet(lowestsbu, htfadd600)
    HighestsbdSet(highestsbd, htfadd601)
    LowestsbuSet(lowestsbu, htfadd601)
    HighestsbdSet(highestsbd, htfadd602)
    LowestsbuSet(lowestsbu, htfadd602)
    HighestsbdSet(highestsbd, htfadd603)
    LowestsbuSet(lowestsbu, htfadd603)
    HighestsbdSet(highestsbd, htfadd604)
    LowestsbuSet(lowestsbu, htfadd604)
    HighestsbdSet(highestsbd, htfadd605)
    LowestsbuSet(lowestsbu, htfadd605)
    HighestsbdSet(highestsbd, htfadd606)
    LowestsbuSet(lowestsbu, htfadd606)
    HighestsbdSet(highestsbd, htfadd607)
    LowestsbuSet(lowestsbu, htfadd607)
    HighestsbdSet(highestsbd, htfadd608)
    LowestsbuSet(lowestsbu, htfadd608)
    HighestsbdSet(highestsbd, htfadd609)
    LowestsbuSet(lowestsbu, htfadd609)
    HighestsbdSet(highestsbd, htfadd610)
    LowestsbuSet(lowestsbu, htfadd610)
    HighestsbdSet(highestsbd, htfadd611)
    LowestsbuSet(lowestsbu, htfadd611)
    HighestsbdSet(highestsbd, htfadd612)
    LowestsbuSet(lowestsbu, htfadd612)
    HighestsbdSet(highestsbd, htfadd613)
    LowestsbuSet(lowestsbu, htfadd613)
    HighestsbdSet(highestsbd, htfadd614)
    LowestsbuSet(lowestsbu, htfadd614)
    HighestsbdSet(highestsbd, htfadd615)
    LowestsbuSet(lowestsbu, htfadd615)
    HighestsbdSet(highestsbd, htfadd616)
    LowestsbuSet(lowestsbu, htfadd616)
    HighestsbdSet(highestsbd, htfadd617)
    LowestsbuSet(lowestsbu, htfadd617)
    HighestsbdSet(highestsbd, htfadd618)
    LowestsbuSet(lowestsbu, htfadd618)
    HighestsbdSet(highestsbd, htfadd619)
    LowestsbuSet(lowestsbu, htfadd619)
    HighestsbdSet(highestsbd, htfadd620)
    LowestsbuSet(lowestsbu, htfadd620)
    HighestsbdSet(highestsbd, htfadd621)
    LowestsbuSet(lowestsbu, htfadd621)
    HighestsbdSet(highestsbd, htfadd622)
    LowestsbuSet(lowestsbu, htfadd622)
    HighestsbdSet(highestsbd, htfadd623)
    LowestsbuSet(lowestsbu, htfadd623)
    HighestsbdSet(highestsbd, htfadd624)
    LowestsbuSet(lowestsbu, htfadd624)
    HighestsbdSet(highestsbd, htfadd625)
    LowestsbuSet(lowestsbu, htfadd625)
    HighestsbdSet(highestsbd, htfadd626)
    LowestsbuSet(lowestsbu, htfadd626)
    HighestsbdSet(highestsbd, htfadd627)
    LowestsbuSet(lowestsbu, htfadd627)
    HighestsbdSet(highestsbd, htfadd628)
    LowestsbuSet(lowestsbu, htfadd628)
    HighestsbdSet(highestsbd, htfadd629)
    LowestsbuSet(lowestsbu, htfadd629)
    HighestsbdSet(highestsbd, htfadd630)
    LowestsbuSet(lowestsbu, htfadd630)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd540).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd541).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd542).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd543).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd544).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd545).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd546).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd547).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd548).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd549).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd550).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd551).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd552).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd553).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd554).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd555).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd556).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd557).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd558).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd559).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd560).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd561).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd562).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd563).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd564).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd565).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd566).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd567).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd568).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd569).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd570).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd571).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd572).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd573).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd574).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd575).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd576).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd577).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd578).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd579).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd580).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd581).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd582).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd583).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd584).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd585).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd586).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd587).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd588).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd589).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd590).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd591).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd592).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd593).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd594).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd595).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd596).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd597).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd598).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd599).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd600).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd601).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd602).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd603).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd604).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd605).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd606).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd607).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd608).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd609).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd610).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd611).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd612).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd613).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd614).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd615).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd616).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd617).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd618).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd619).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd620).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd621).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd622).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd623).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd624).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd625).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd626).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd627).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd628).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd629).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd630).Monitor_Est().BOSJudge()
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


