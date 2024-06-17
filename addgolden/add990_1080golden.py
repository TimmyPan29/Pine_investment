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
var CandleSet htfadd990                     = CandleSet.new()
var CandleSettings SettingsHTFadd990        = CandleSettings.new(htf='990',htfint=990,max_memory=3)
var Candle[] candlesadd990                  = array.new<Candle>(0)
var BOSdata bosdataadd990                   = BOSdata.new()
htfadd990.settings                 := SettingsHTFadd990
htfadd990.candles                  := candlesadd990
htfadd990.bosdata                  := bosdataadd990
var CandleSet htfadd991                     = CandleSet.new()
var CandleSettings SettingsHTFadd991        = CandleSettings.new(htf='991',htfint=991,max_memory=3)
var Candle[] candlesadd991                  = array.new<Candle>(0)
var BOSdata bosdataadd991                   = BOSdata.new()
htfadd991.settings                 := SettingsHTFadd991
htfadd991.candles                  := candlesadd991
htfadd991.bosdata                  := bosdataadd991
var CandleSet htfadd992                     = CandleSet.new()
var CandleSettings SettingsHTFadd992        = CandleSettings.new(htf='992',htfint=992,max_memory=3)
var Candle[] candlesadd992                  = array.new<Candle>(0)
var BOSdata bosdataadd992                   = BOSdata.new()
htfadd992.settings                 := SettingsHTFadd992
htfadd992.candles                  := candlesadd992
htfadd992.bosdata                  := bosdataadd992
var CandleSet htfadd993                     = CandleSet.new()
var CandleSettings SettingsHTFadd993        = CandleSettings.new(htf='993',htfint=993,max_memory=3)
var Candle[] candlesadd993                  = array.new<Candle>(0)
var BOSdata bosdataadd993                   = BOSdata.new()
htfadd993.settings                 := SettingsHTFadd993
htfadd993.candles                  := candlesadd993
htfadd993.bosdata                  := bosdataadd993
var CandleSet htfadd994                     = CandleSet.new()
var CandleSettings SettingsHTFadd994        = CandleSettings.new(htf='994',htfint=994,max_memory=3)
var Candle[] candlesadd994                  = array.new<Candle>(0)
var BOSdata bosdataadd994                   = BOSdata.new()
htfadd994.settings                 := SettingsHTFadd994
htfadd994.candles                  := candlesadd994
htfadd994.bosdata                  := bosdataadd994
var CandleSet htfadd995                     = CandleSet.new()
var CandleSettings SettingsHTFadd995        = CandleSettings.new(htf='995',htfint=995,max_memory=3)
var Candle[] candlesadd995                  = array.new<Candle>(0)
var BOSdata bosdataadd995                   = BOSdata.new()
htfadd995.settings                 := SettingsHTFadd995
htfadd995.candles                  := candlesadd995
htfadd995.bosdata                  := bosdataadd995
var CandleSet htfadd996                     = CandleSet.new()
var CandleSettings SettingsHTFadd996        = CandleSettings.new(htf='996',htfint=996,max_memory=3)
var Candle[] candlesadd996                  = array.new<Candle>(0)
var BOSdata bosdataadd996                   = BOSdata.new()
htfadd996.settings                 := SettingsHTFadd996
htfadd996.candles                  := candlesadd996
htfadd996.bosdata                  := bosdataadd996
var CandleSet htfadd997                     = CandleSet.new()
var CandleSettings SettingsHTFadd997        = CandleSettings.new(htf='997',htfint=997,max_memory=3)
var Candle[] candlesadd997                  = array.new<Candle>(0)
var BOSdata bosdataadd997                   = BOSdata.new()
htfadd997.settings                 := SettingsHTFadd997
htfadd997.candles                  := candlesadd997
htfadd997.bosdata                  := bosdataadd997
var CandleSet htfadd998                     = CandleSet.new()
var CandleSettings SettingsHTFadd998        = CandleSettings.new(htf='998',htfint=998,max_memory=3)
var Candle[] candlesadd998                  = array.new<Candle>(0)
var BOSdata bosdataadd998                   = BOSdata.new()
htfadd998.settings                 := SettingsHTFadd998
htfadd998.candles                  := candlesadd998
htfadd998.bosdata                  := bosdataadd998
var CandleSet htfadd999                     = CandleSet.new()
var CandleSettings SettingsHTFadd999        = CandleSettings.new(htf='999',htfint=999,max_memory=3)
var Candle[] candlesadd999                  = array.new<Candle>(0)
var BOSdata bosdataadd999                   = BOSdata.new()
htfadd999.settings                 := SettingsHTFadd999
htfadd999.candles                  := candlesadd999
htfadd999.bosdata                  := bosdataadd999
var CandleSet htfadd1000                     = CandleSet.new()
var CandleSettings SettingsHTFadd1000        = CandleSettings.new(htf='1000',htfint=1000,max_memory=3)
var Candle[] candlesadd1000                  = array.new<Candle>(0)
var BOSdata bosdataadd1000                   = BOSdata.new()
htfadd1000.settings                 := SettingsHTFadd1000
htfadd1000.candles                  := candlesadd1000
htfadd1000.bosdata                  := bosdataadd1000
var CandleSet htfadd1001                     = CandleSet.new()
var CandleSettings SettingsHTFadd1001        = CandleSettings.new(htf='1001',htfint=1001,max_memory=3)
var Candle[] candlesadd1001                  = array.new<Candle>(0)
var BOSdata bosdataadd1001                   = BOSdata.new()
htfadd1001.settings                 := SettingsHTFadd1001
htfadd1001.candles                  := candlesadd1001
htfadd1001.bosdata                  := bosdataadd1001
var CandleSet htfadd1002                     = CandleSet.new()
var CandleSettings SettingsHTFadd1002        = CandleSettings.new(htf='1002',htfint=1002,max_memory=3)
var Candle[] candlesadd1002                  = array.new<Candle>(0)
var BOSdata bosdataadd1002                   = BOSdata.new()
htfadd1002.settings                 := SettingsHTFadd1002
htfadd1002.candles                  := candlesadd1002
htfadd1002.bosdata                  := bosdataadd1002
var CandleSet htfadd1003                     = CandleSet.new()
var CandleSettings SettingsHTFadd1003        = CandleSettings.new(htf='1003',htfint=1003,max_memory=3)
var Candle[] candlesadd1003                  = array.new<Candle>(0)
var BOSdata bosdataadd1003                   = BOSdata.new()
htfadd1003.settings                 := SettingsHTFadd1003
htfadd1003.candles                  := candlesadd1003
htfadd1003.bosdata                  := bosdataadd1003
var CandleSet htfadd1004                     = CandleSet.new()
var CandleSettings SettingsHTFadd1004        = CandleSettings.new(htf='1004',htfint=1004,max_memory=3)
var Candle[] candlesadd1004                  = array.new<Candle>(0)
var BOSdata bosdataadd1004                   = BOSdata.new()
htfadd1004.settings                 := SettingsHTFadd1004
htfadd1004.candles                  := candlesadd1004
htfadd1004.bosdata                  := bosdataadd1004
var CandleSet htfadd1005                     = CandleSet.new()
var CandleSettings SettingsHTFadd1005        = CandleSettings.new(htf='1005',htfint=1005,max_memory=3)
var Candle[] candlesadd1005                  = array.new<Candle>(0)
var BOSdata bosdataadd1005                   = BOSdata.new()
htfadd1005.settings                 := SettingsHTFadd1005
htfadd1005.candles                  := candlesadd1005
htfadd1005.bosdata                  := bosdataadd1005
var CandleSet htfadd1006                     = CandleSet.new()
var CandleSettings SettingsHTFadd1006        = CandleSettings.new(htf='1006',htfint=1006,max_memory=3)
var Candle[] candlesadd1006                  = array.new<Candle>(0)
var BOSdata bosdataadd1006                   = BOSdata.new()
htfadd1006.settings                 := SettingsHTFadd1006
htfadd1006.candles                  := candlesadd1006
htfadd1006.bosdata                  := bosdataadd1006
var CandleSet htfadd1007                     = CandleSet.new()
var CandleSettings SettingsHTFadd1007        = CandleSettings.new(htf='1007',htfint=1007,max_memory=3)
var Candle[] candlesadd1007                  = array.new<Candle>(0)
var BOSdata bosdataadd1007                   = BOSdata.new()
htfadd1007.settings                 := SettingsHTFadd1007
htfadd1007.candles                  := candlesadd1007
htfadd1007.bosdata                  := bosdataadd1007
var CandleSet htfadd1008                     = CandleSet.new()
var CandleSettings SettingsHTFadd1008        = CandleSettings.new(htf='1008',htfint=1008,max_memory=3)
var Candle[] candlesadd1008                  = array.new<Candle>(0)
var BOSdata bosdataadd1008                   = BOSdata.new()
htfadd1008.settings                 := SettingsHTFadd1008
htfadd1008.candles                  := candlesadd1008
htfadd1008.bosdata                  := bosdataadd1008
var CandleSet htfadd1009                     = CandleSet.new()
var CandleSettings SettingsHTFadd1009        = CandleSettings.new(htf='1009',htfint=1009,max_memory=3)
var Candle[] candlesadd1009                  = array.new<Candle>(0)
var BOSdata bosdataadd1009                   = BOSdata.new()
htfadd1009.settings                 := SettingsHTFadd1009
htfadd1009.candles                  := candlesadd1009
htfadd1009.bosdata                  := bosdataadd1009
var CandleSet htfadd1010                     = CandleSet.new()
var CandleSettings SettingsHTFadd1010        = CandleSettings.new(htf='1010',htfint=1010,max_memory=3)
var Candle[] candlesadd1010                  = array.new<Candle>(0)
var BOSdata bosdataadd1010                   = BOSdata.new()
htfadd1010.settings                 := SettingsHTFadd1010
htfadd1010.candles                  := candlesadd1010
htfadd1010.bosdata                  := bosdataadd1010
var CandleSet htfadd1011                     = CandleSet.new()
var CandleSettings SettingsHTFadd1011        = CandleSettings.new(htf='1011',htfint=1011,max_memory=3)
var Candle[] candlesadd1011                  = array.new<Candle>(0)
var BOSdata bosdataadd1011                   = BOSdata.new()
htfadd1011.settings                 := SettingsHTFadd1011
htfadd1011.candles                  := candlesadd1011
htfadd1011.bosdata                  := bosdataadd1011
var CandleSet htfadd1012                     = CandleSet.new()
var CandleSettings SettingsHTFadd1012        = CandleSettings.new(htf='1012',htfint=1012,max_memory=3)
var Candle[] candlesadd1012                  = array.new<Candle>(0)
var BOSdata bosdataadd1012                   = BOSdata.new()
htfadd1012.settings                 := SettingsHTFadd1012
htfadd1012.candles                  := candlesadd1012
htfadd1012.bosdata                  := bosdataadd1012
var CandleSet htfadd1013                     = CandleSet.new()
var CandleSettings SettingsHTFadd1013        = CandleSettings.new(htf='1013',htfint=1013,max_memory=3)
var Candle[] candlesadd1013                  = array.new<Candle>(0)
var BOSdata bosdataadd1013                   = BOSdata.new()
htfadd1013.settings                 := SettingsHTFadd1013
htfadd1013.candles                  := candlesadd1013
htfadd1013.bosdata                  := bosdataadd1013
var CandleSet htfadd1014                     = CandleSet.new()
var CandleSettings SettingsHTFadd1014        = CandleSettings.new(htf='1014',htfint=1014,max_memory=3)
var Candle[] candlesadd1014                  = array.new<Candle>(0)
var BOSdata bosdataadd1014                   = BOSdata.new()
htfadd1014.settings                 := SettingsHTFadd1014
htfadd1014.candles                  := candlesadd1014
htfadd1014.bosdata                  := bosdataadd1014
var CandleSet htfadd1015                     = CandleSet.new()
var CandleSettings SettingsHTFadd1015        = CandleSettings.new(htf='1015',htfint=1015,max_memory=3)
var Candle[] candlesadd1015                  = array.new<Candle>(0)
var BOSdata bosdataadd1015                   = BOSdata.new()
htfadd1015.settings                 := SettingsHTFadd1015
htfadd1015.candles                  := candlesadd1015
htfadd1015.bosdata                  := bosdataadd1015
var CandleSet htfadd1016                     = CandleSet.new()
var CandleSettings SettingsHTFadd1016        = CandleSettings.new(htf='1016',htfint=1016,max_memory=3)
var Candle[] candlesadd1016                  = array.new<Candle>(0)
var BOSdata bosdataadd1016                   = BOSdata.new()
htfadd1016.settings                 := SettingsHTFadd1016
htfadd1016.candles                  := candlesadd1016
htfadd1016.bosdata                  := bosdataadd1016
var CandleSet htfadd1017                     = CandleSet.new()
var CandleSettings SettingsHTFadd1017        = CandleSettings.new(htf='1017',htfint=1017,max_memory=3)
var Candle[] candlesadd1017                  = array.new<Candle>(0)
var BOSdata bosdataadd1017                   = BOSdata.new()
htfadd1017.settings                 := SettingsHTFadd1017
htfadd1017.candles                  := candlesadd1017
htfadd1017.bosdata                  := bosdataadd1017
var CandleSet htfadd1018                     = CandleSet.new()
var CandleSettings SettingsHTFadd1018        = CandleSettings.new(htf='1018',htfint=1018,max_memory=3)
var Candle[] candlesadd1018                  = array.new<Candle>(0)
var BOSdata bosdataadd1018                   = BOSdata.new()
htfadd1018.settings                 := SettingsHTFadd1018
htfadd1018.candles                  := candlesadd1018
htfadd1018.bosdata                  := bosdataadd1018
var CandleSet htfadd1019                     = CandleSet.new()
var CandleSettings SettingsHTFadd1019        = CandleSettings.new(htf='1019',htfint=1019,max_memory=3)
var Candle[] candlesadd1019                  = array.new<Candle>(0)
var BOSdata bosdataadd1019                   = BOSdata.new()
htfadd1019.settings                 := SettingsHTFadd1019
htfadd1019.candles                  := candlesadd1019
htfadd1019.bosdata                  := bosdataadd1019
var CandleSet htfadd1020                     = CandleSet.new()
var CandleSettings SettingsHTFadd1020        = CandleSettings.new(htf='1020',htfint=1020,max_memory=3)
var Candle[] candlesadd1020                  = array.new<Candle>(0)
var BOSdata bosdataadd1020                   = BOSdata.new()
htfadd1020.settings                 := SettingsHTFadd1020
htfadd1020.candles                  := candlesadd1020
htfadd1020.bosdata                  := bosdataadd1020
var CandleSet htfadd1021                     = CandleSet.new()
var CandleSettings SettingsHTFadd1021        = CandleSettings.new(htf='1021',htfint=1021,max_memory=3)
var Candle[] candlesadd1021                  = array.new<Candle>(0)
var BOSdata bosdataadd1021                   = BOSdata.new()
htfadd1021.settings                 := SettingsHTFadd1021
htfadd1021.candles                  := candlesadd1021
htfadd1021.bosdata                  := bosdataadd1021
var CandleSet htfadd1022                     = CandleSet.new()
var CandleSettings SettingsHTFadd1022        = CandleSettings.new(htf='1022',htfint=1022,max_memory=3)
var Candle[] candlesadd1022                  = array.new<Candle>(0)
var BOSdata bosdataadd1022                   = BOSdata.new()
htfadd1022.settings                 := SettingsHTFadd1022
htfadd1022.candles                  := candlesadd1022
htfadd1022.bosdata                  := bosdataadd1022
var CandleSet htfadd1023                     = CandleSet.new()
var CandleSettings SettingsHTFadd1023        = CandleSettings.new(htf='1023',htfint=1023,max_memory=3)
var Candle[] candlesadd1023                  = array.new<Candle>(0)
var BOSdata bosdataadd1023                   = BOSdata.new()
htfadd1023.settings                 := SettingsHTFadd1023
htfadd1023.candles                  := candlesadd1023
htfadd1023.bosdata                  := bosdataadd1023
var CandleSet htfadd1024                     = CandleSet.new()
var CandleSettings SettingsHTFadd1024        = CandleSettings.new(htf='1024',htfint=1024,max_memory=3)
var Candle[] candlesadd1024                  = array.new<Candle>(0)
var BOSdata bosdataadd1024                   = BOSdata.new()
htfadd1024.settings                 := SettingsHTFadd1024
htfadd1024.candles                  := candlesadd1024
htfadd1024.bosdata                  := bosdataadd1024
var CandleSet htfadd1025                     = CandleSet.new()
var CandleSettings SettingsHTFadd1025        = CandleSettings.new(htf='1025',htfint=1025,max_memory=3)
var Candle[] candlesadd1025                  = array.new<Candle>(0)
var BOSdata bosdataadd1025                   = BOSdata.new()
htfadd1025.settings                 := SettingsHTFadd1025
htfadd1025.candles                  := candlesadd1025
htfadd1025.bosdata                  := bosdataadd1025
var CandleSet htfadd1026                     = CandleSet.new()
var CandleSettings SettingsHTFadd1026        = CandleSettings.new(htf='1026',htfint=1026,max_memory=3)
var Candle[] candlesadd1026                  = array.new<Candle>(0)
var BOSdata bosdataadd1026                   = BOSdata.new()
htfadd1026.settings                 := SettingsHTFadd1026
htfadd1026.candles                  := candlesadd1026
htfadd1026.bosdata                  := bosdataadd1026
var CandleSet htfadd1027                     = CandleSet.new()
var CandleSettings SettingsHTFadd1027        = CandleSettings.new(htf='1027',htfint=1027,max_memory=3)
var Candle[] candlesadd1027                  = array.new<Candle>(0)
var BOSdata bosdataadd1027                   = BOSdata.new()
htfadd1027.settings                 := SettingsHTFadd1027
htfadd1027.candles                  := candlesadd1027
htfadd1027.bosdata                  := bosdataadd1027
var CandleSet htfadd1028                     = CandleSet.new()
var CandleSettings SettingsHTFadd1028        = CandleSettings.new(htf='1028',htfint=1028,max_memory=3)
var Candle[] candlesadd1028                  = array.new<Candle>(0)
var BOSdata bosdataadd1028                   = BOSdata.new()
htfadd1028.settings                 := SettingsHTFadd1028
htfadd1028.candles                  := candlesadd1028
htfadd1028.bosdata                  := bosdataadd1028
var CandleSet htfadd1029                     = CandleSet.new()
var CandleSettings SettingsHTFadd1029        = CandleSettings.new(htf='1029',htfint=1029,max_memory=3)
var Candle[] candlesadd1029                  = array.new<Candle>(0)
var BOSdata bosdataadd1029                   = BOSdata.new()
htfadd1029.settings                 := SettingsHTFadd1029
htfadd1029.candles                  := candlesadd1029
htfadd1029.bosdata                  := bosdataadd1029
var CandleSet htfadd1030                     = CandleSet.new()
var CandleSettings SettingsHTFadd1030        = CandleSettings.new(htf='1030',htfint=1030,max_memory=3)
var Candle[] candlesadd1030                  = array.new<Candle>(0)
var BOSdata bosdataadd1030                   = BOSdata.new()
htfadd1030.settings                 := SettingsHTFadd1030
htfadd1030.candles                  := candlesadd1030
htfadd1030.bosdata                  := bosdataadd1030
var CandleSet htfadd1031                     = CandleSet.new()
var CandleSettings SettingsHTFadd1031        = CandleSettings.new(htf='1031',htfint=1031,max_memory=3)
var Candle[] candlesadd1031                  = array.new<Candle>(0)
var BOSdata bosdataadd1031                   = BOSdata.new()
htfadd1031.settings                 := SettingsHTFadd1031
htfadd1031.candles                  := candlesadd1031
htfadd1031.bosdata                  := bosdataadd1031
var CandleSet htfadd1032                     = CandleSet.new()
var CandleSettings SettingsHTFadd1032        = CandleSettings.new(htf='1032',htfint=1032,max_memory=3)
var Candle[] candlesadd1032                  = array.new<Candle>(0)
var BOSdata bosdataadd1032                   = BOSdata.new()
htfadd1032.settings                 := SettingsHTFadd1032
htfadd1032.candles                  := candlesadd1032
htfadd1032.bosdata                  := bosdataadd1032
var CandleSet htfadd1033                     = CandleSet.new()
var CandleSettings SettingsHTFadd1033        = CandleSettings.new(htf='1033',htfint=1033,max_memory=3)
var Candle[] candlesadd1033                  = array.new<Candle>(0)
var BOSdata bosdataadd1033                   = BOSdata.new()
htfadd1033.settings                 := SettingsHTFadd1033
htfadd1033.candles                  := candlesadd1033
htfadd1033.bosdata                  := bosdataadd1033
var CandleSet htfadd1034                     = CandleSet.new()
var CandleSettings SettingsHTFadd1034        = CandleSettings.new(htf='1034',htfint=1034,max_memory=3)
var Candle[] candlesadd1034                  = array.new<Candle>(0)
var BOSdata bosdataadd1034                   = BOSdata.new()
htfadd1034.settings                 := SettingsHTFadd1034
htfadd1034.candles                  := candlesadd1034
htfadd1034.bosdata                  := bosdataadd1034
var CandleSet htfadd1035                     = CandleSet.new()
var CandleSettings SettingsHTFadd1035        = CandleSettings.new(htf='1035',htfint=1035,max_memory=3)
var Candle[] candlesadd1035                  = array.new<Candle>(0)
var BOSdata bosdataadd1035                   = BOSdata.new()
htfadd1035.settings                 := SettingsHTFadd1035
htfadd1035.candles                  := candlesadd1035
htfadd1035.bosdata                  := bosdataadd1035
var CandleSet htfadd1036                     = CandleSet.new()
var CandleSettings SettingsHTFadd1036        = CandleSettings.new(htf='1036',htfint=1036,max_memory=3)
var Candle[] candlesadd1036                  = array.new<Candle>(0)
var BOSdata bosdataadd1036                   = BOSdata.new()
htfadd1036.settings                 := SettingsHTFadd1036
htfadd1036.candles                  := candlesadd1036
htfadd1036.bosdata                  := bosdataadd1036
var CandleSet htfadd1037                     = CandleSet.new()
var CandleSettings SettingsHTFadd1037        = CandleSettings.new(htf='1037',htfint=1037,max_memory=3)
var Candle[] candlesadd1037                  = array.new<Candle>(0)
var BOSdata bosdataadd1037                   = BOSdata.new()
htfadd1037.settings                 := SettingsHTFadd1037
htfadd1037.candles                  := candlesadd1037
htfadd1037.bosdata                  := bosdataadd1037
var CandleSet htfadd1038                     = CandleSet.new()
var CandleSettings SettingsHTFadd1038        = CandleSettings.new(htf='1038',htfint=1038,max_memory=3)
var Candle[] candlesadd1038                  = array.new<Candle>(0)
var BOSdata bosdataadd1038                   = BOSdata.new()
htfadd1038.settings                 := SettingsHTFadd1038
htfadd1038.candles                  := candlesadd1038
htfadd1038.bosdata                  := bosdataadd1038
var CandleSet htfadd1039                     = CandleSet.new()
var CandleSettings SettingsHTFadd1039        = CandleSettings.new(htf='1039',htfint=1039,max_memory=3)
var Candle[] candlesadd1039                  = array.new<Candle>(0)
var BOSdata bosdataadd1039                   = BOSdata.new()
htfadd1039.settings                 := SettingsHTFadd1039
htfadd1039.candles                  := candlesadd1039
htfadd1039.bosdata                  := bosdataadd1039
var CandleSet htfadd1040                     = CandleSet.new()
var CandleSettings SettingsHTFadd1040        = CandleSettings.new(htf='1040',htfint=1040,max_memory=3)
var Candle[] candlesadd1040                  = array.new<Candle>(0)
var BOSdata bosdataadd1040                   = BOSdata.new()
htfadd1040.settings                 := SettingsHTFadd1040
htfadd1040.candles                  := candlesadd1040
htfadd1040.bosdata                  := bosdataadd1040
var CandleSet htfadd1041                     = CandleSet.new()
var CandleSettings SettingsHTFadd1041        = CandleSettings.new(htf='1041',htfint=1041,max_memory=3)
var Candle[] candlesadd1041                  = array.new<Candle>(0)
var BOSdata bosdataadd1041                   = BOSdata.new()
htfadd1041.settings                 := SettingsHTFadd1041
htfadd1041.candles                  := candlesadd1041
htfadd1041.bosdata                  := bosdataadd1041
var CandleSet htfadd1042                     = CandleSet.new()
var CandleSettings SettingsHTFadd1042        = CandleSettings.new(htf='1042',htfint=1042,max_memory=3)
var Candle[] candlesadd1042                  = array.new<Candle>(0)
var BOSdata bosdataadd1042                   = BOSdata.new()
htfadd1042.settings                 := SettingsHTFadd1042
htfadd1042.candles                  := candlesadd1042
htfadd1042.bosdata                  := bosdataadd1042
var CandleSet htfadd1043                     = CandleSet.new()
var CandleSettings SettingsHTFadd1043        = CandleSettings.new(htf='1043',htfint=1043,max_memory=3)
var Candle[] candlesadd1043                  = array.new<Candle>(0)
var BOSdata bosdataadd1043                   = BOSdata.new()
htfadd1043.settings                 := SettingsHTFadd1043
htfadd1043.candles                  := candlesadd1043
htfadd1043.bosdata                  := bosdataadd1043
var CandleSet htfadd1044                     = CandleSet.new()
var CandleSettings SettingsHTFadd1044        = CandleSettings.new(htf='1044',htfint=1044,max_memory=3)
var Candle[] candlesadd1044                  = array.new<Candle>(0)
var BOSdata bosdataadd1044                   = BOSdata.new()
htfadd1044.settings                 := SettingsHTFadd1044
htfadd1044.candles                  := candlesadd1044
htfadd1044.bosdata                  := bosdataadd1044
var CandleSet htfadd1045                     = CandleSet.new()
var CandleSettings SettingsHTFadd1045        = CandleSettings.new(htf='1045',htfint=1045,max_memory=3)
var Candle[] candlesadd1045                  = array.new<Candle>(0)
var BOSdata bosdataadd1045                   = BOSdata.new()
htfadd1045.settings                 := SettingsHTFadd1045
htfadd1045.candles                  := candlesadd1045
htfadd1045.bosdata                  := bosdataadd1045
var CandleSet htfadd1046                     = CandleSet.new()
var CandleSettings SettingsHTFadd1046        = CandleSettings.new(htf='1046',htfint=1046,max_memory=3)
var Candle[] candlesadd1046                  = array.new<Candle>(0)
var BOSdata bosdataadd1046                   = BOSdata.new()
htfadd1046.settings                 := SettingsHTFadd1046
htfadd1046.candles                  := candlesadd1046
htfadd1046.bosdata                  := bosdataadd1046
var CandleSet htfadd1047                     = CandleSet.new()
var CandleSettings SettingsHTFadd1047        = CandleSettings.new(htf='1047',htfint=1047,max_memory=3)
var Candle[] candlesadd1047                  = array.new<Candle>(0)
var BOSdata bosdataadd1047                   = BOSdata.new()
htfadd1047.settings                 := SettingsHTFadd1047
htfadd1047.candles                  := candlesadd1047
htfadd1047.bosdata                  := bosdataadd1047
var CandleSet htfadd1048                     = CandleSet.new()
var CandleSettings SettingsHTFadd1048        = CandleSettings.new(htf='1048',htfint=1048,max_memory=3)
var Candle[] candlesadd1048                  = array.new<Candle>(0)
var BOSdata bosdataadd1048                   = BOSdata.new()
htfadd1048.settings                 := SettingsHTFadd1048
htfadd1048.candles                  := candlesadd1048
htfadd1048.bosdata                  := bosdataadd1048
var CandleSet htfadd1049                     = CandleSet.new()
var CandleSettings SettingsHTFadd1049        = CandleSettings.new(htf='1049',htfint=1049,max_memory=3)
var Candle[] candlesadd1049                  = array.new<Candle>(0)
var BOSdata bosdataadd1049                   = BOSdata.new()
htfadd1049.settings                 := SettingsHTFadd1049
htfadd1049.candles                  := candlesadd1049
htfadd1049.bosdata                  := bosdataadd1049
var CandleSet htfadd1050                     = CandleSet.new()
var CandleSettings SettingsHTFadd1050        = CandleSettings.new(htf='1050',htfint=1050,max_memory=3)
var Candle[] candlesadd1050                  = array.new<Candle>(0)
var BOSdata bosdataadd1050                   = BOSdata.new()
htfadd1050.settings                 := SettingsHTFadd1050
htfadd1050.candles                  := candlesadd1050
htfadd1050.bosdata                  := bosdataadd1050
var CandleSet htfadd1051                     = CandleSet.new()
var CandleSettings SettingsHTFadd1051        = CandleSettings.new(htf='1051',htfint=1051,max_memory=3)
var Candle[] candlesadd1051                  = array.new<Candle>(0)
var BOSdata bosdataadd1051                   = BOSdata.new()
htfadd1051.settings                 := SettingsHTFadd1051
htfadd1051.candles                  := candlesadd1051
htfadd1051.bosdata                  := bosdataadd1051
var CandleSet htfadd1052                     = CandleSet.new()
var CandleSettings SettingsHTFadd1052        = CandleSettings.new(htf='1052',htfint=1052,max_memory=3)
var Candle[] candlesadd1052                  = array.new<Candle>(0)
var BOSdata bosdataadd1052                   = BOSdata.new()
htfadd1052.settings                 := SettingsHTFadd1052
htfadd1052.candles                  := candlesadd1052
htfadd1052.bosdata                  := bosdataadd1052
var CandleSet htfadd1053                     = CandleSet.new()
var CandleSettings SettingsHTFadd1053        = CandleSettings.new(htf='1053',htfint=1053,max_memory=3)
var Candle[] candlesadd1053                  = array.new<Candle>(0)
var BOSdata bosdataadd1053                   = BOSdata.new()
htfadd1053.settings                 := SettingsHTFadd1053
htfadd1053.candles                  := candlesadd1053
htfadd1053.bosdata                  := bosdataadd1053
var CandleSet htfadd1054                     = CandleSet.new()
var CandleSettings SettingsHTFadd1054        = CandleSettings.new(htf='1054',htfint=1054,max_memory=3)
var Candle[] candlesadd1054                  = array.new<Candle>(0)
var BOSdata bosdataadd1054                   = BOSdata.new()
htfadd1054.settings                 := SettingsHTFadd1054
htfadd1054.candles                  := candlesadd1054
htfadd1054.bosdata                  := bosdataadd1054
var CandleSet htfadd1055                     = CandleSet.new()
var CandleSettings SettingsHTFadd1055        = CandleSettings.new(htf='1055',htfint=1055,max_memory=3)
var Candle[] candlesadd1055                  = array.new<Candle>(0)
var BOSdata bosdataadd1055                   = BOSdata.new()
htfadd1055.settings                 := SettingsHTFadd1055
htfadd1055.candles                  := candlesadd1055
htfadd1055.bosdata                  := bosdataadd1055
var CandleSet htfadd1056                     = CandleSet.new()
var CandleSettings SettingsHTFadd1056        = CandleSettings.new(htf='1056',htfint=1056,max_memory=3)
var Candle[] candlesadd1056                  = array.new<Candle>(0)
var BOSdata bosdataadd1056                   = BOSdata.new()
htfadd1056.settings                 := SettingsHTFadd1056
htfadd1056.candles                  := candlesadd1056
htfadd1056.bosdata                  := bosdataadd1056
var CandleSet htfadd1057                     = CandleSet.new()
var CandleSettings SettingsHTFadd1057        = CandleSettings.new(htf='1057',htfint=1057,max_memory=3)
var Candle[] candlesadd1057                  = array.new<Candle>(0)
var BOSdata bosdataadd1057                   = BOSdata.new()
htfadd1057.settings                 := SettingsHTFadd1057
htfadd1057.candles                  := candlesadd1057
htfadd1057.bosdata                  := bosdataadd1057
var CandleSet htfadd1058                     = CandleSet.new()
var CandleSettings SettingsHTFadd1058        = CandleSettings.new(htf='1058',htfint=1058,max_memory=3)
var Candle[] candlesadd1058                  = array.new<Candle>(0)
var BOSdata bosdataadd1058                   = BOSdata.new()
htfadd1058.settings                 := SettingsHTFadd1058
htfadd1058.candles                  := candlesadd1058
htfadd1058.bosdata                  := bosdataadd1058
var CandleSet htfadd1059                     = CandleSet.new()
var CandleSettings SettingsHTFadd1059        = CandleSettings.new(htf='1059',htfint=1059,max_memory=3)
var Candle[] candlesadd1059                  = array.new<Candle>(0)
var BOSdata bosdataadd1059                   = BOSdata.new()
htfadd1059.settings                 := SettingsHTFadd1059
htfadd1059.candles                  := candlesadd1059
htfadd1059.bosdata                  := bosdataadd1059
var CandleSet htfadd1060                     = CandleSet.new()
var CandleSettings SettingsHTFadd1060        = CandleSettings.new(htf='1060',htfint=1060,max_memory=3)
var Candle[] candlesadd1060                  = array.new<Candle>(0)
var BOSdata bosdataadd1060                   = BOSdata.new()
htfadd1060.settings                 := SettingsHTFadd1060
htfadd1060.candles                  := candlesadd1060
htfadd1060.bosdata                  := bosdataadd1060
var CandleSet htfadd1061                     = CandleSet.new()
var CandleSettings SettingsHTFadd1061        = CandleSettings.new(htf='1061',htfint=1061,max_memory=3)
var Candle[] candlesadd1061                  = array.new<Candle>(0)
var BOSdata bosdataadd1061                   = BOSdata.new()
htfadd1061.settings                 := SettingsHTFadd1061
htfadd1061.candles                  := candlesadd1061
htfadd1061.bosdata                  := bosdataadd1061
var CandleSet htfadd1062                     = CandleSet.new()
var CandleSettings SettingsHTFadd1062        = CandleSettings.new(htf='1062',htfint=1062,max_memory=3)
var Candle[] candlesadd1062                  = array.new<Candle>(0)
var BOSdata bosdataadd1062                   = BOSdata.new()
htfadd1062.settings                 := SettingsHTFadd1062
htfadd1062.candles                  := candlesadd1062
htfadd1062.bosdata                  := bosdataadd1062
var CandleSet htfadd1063                     = CandleSet.new()
var CandleSettings SettingsHTFadd1063        = CandleSettings.new(htf='1063',htfint=1063,max_memory=3)
var Candle[] candlesadd1063                  = array.new<Candle>(0)
var BOSdata bosdataadd1063                   = BOSdata.new()
htfadd1063.settings                 := SettingsHTFadd1063
htfadd1063.candles                  := candlesadd1063
htfadd1063.bosdata                  := bosdataadd1063
var CandleSet htfadd1064                     = CandleSet.new()
var CandleSettings SettingsHTFadd1064        = CandleSettings.new(htf='1064',htfint=1064,max_memory=3)
var Candle[] candlesadd1064                  = array.new<Candle>(0)
var BOSdata bosdataadd1064                   = BOSdata.new()
htfadd1064.settings                 := SettingsHTFadd1064
htfadd1064.candles                  := candlesadd1064
htfadd1064.bosdata                  := bosdataadd1064
var CandleSet htfadd1065                     = CandleSet.new()
var CandleSettings SettingsHTFadd1065        = CandleSettings.new(htf='1065',htfint=1065,max_memory=3)
var Candle[] candlesadd1065                  = array.new<Candle>(0)
var BOSdata bosdataadd1065                   = BOSdata.new()
htfadd1065.settings                 := SettingsHTFadd1065
htfadd1065.candles                  := candlesadd1065
htfadd1065.bosdata                  := bosdataadd1065
var CandleSet htfadd1066                     = CandleSet.new()
var CandleSettings SettingsHTFadd1066        = CandleSettings.new(htf='1066',htfint=1066,max_memory=3)
var Candle[] candlesadd1066                  = array.new<Candle>(0)
var BOSdata bosdataadd1066                   = BOSdata.new()
htfadd1066.settings                 := SettingsHTFadd1066
htfadd1066.candles                  := candlesadd1066
htfadd1066.bosdata                  := bosdataadd1066
var CandleSet htfadd1067                     = CandleSet.new()
var CandleSettings SettingsHTFadd1067        = CandleSettings.new(htf='1067',htfint=1067,max_memory=3)
var Candle[] candlesadd1067                  = array.new<Candle>(0)
var BOSdata bosdataadd1067                   = BOSdata.new()
htfadd1067.settings                 := SettingsHTFadd1067
htfadd1067.candles                  := candlesadd1067
htfadd1067.bosdata                  := bosdataadd1067
var CandleSet htfadd1068                     = CandleSet.new()
var CandleSettings SettingsHTFadd1068        = CandleSettings.new(htf='1068',htfint=1068,max_memory=3)
var Candle[] candlesadd1068                  = array.new<Candle>(0)
var BOSdata bosdataadd1068                   = BOSdata.new()
htfadd1068.settings                 := SettingsHTFadd1068
htfadd1068.candles                  := candlesadd1068
htfadd1068.bosdata                  := bosdataadd1068
var CandleSet htfadd1069                     = CandleSet.new()
var CandleSettings SettingsHTFadd1069        = CandleSettings.new(htf='1069',htfint=1069,max_memory=3)
var Candle[] candlesadd1069                  = array.new<Candle>(0)
var BOSdata bosdataadd1069                   = BOSdata.new()
htfadd1069.settings                 := SettingsHTFadd1069
htfadd1069.candles                  := candlesadd1069
htfadd1069.bosdata                  := bosdataadd1069
var CandleSet htfadd1070                     = CandleSet.new()
var CandleSettings SettingsHTFadd1070        = CandleSettings.new(htf='1070',htfint=1070,max_memory=3)
var Candle[] candlesadd1070                  = array.new<Candle>(0)
var BOSdata bosdataadd1070                   = BOSdata.new()
htfadd1070.settings                 := SettingsHTFadd1070
htfadd1070.candles                  := candlesadd1070
htfadd1070.bosdata                  := bosdataadd1070
var CandleSet htfadd1071                     = CandleSet.new()
var CandleSettings SettingsHTFadd1071        = CandleSettings.new(htf='1071',htfint=1071,max_memory=3)
var Candle[] candlesadd1071                  = array.new<Candle>(0)
var BOSdata bosdataadd1071                   = BOSdata.new()
htfadd1071.settings                 := SettingsHTFadd1071
htfadd1071.candles                  := candlesadd1071
htfadd1071.bosdata                  := bosdataadd1071
var CandleSet htfadd1072                     = CandleSet.new()
var CandleSettings SettingsHTFadd1072        = CandleSettings.new(htf='1072',htfint=1072,max_memory=3)
var Candle[] candlesadd1072                  = array.new<Candle>(0)
var BOSdata bosdataadd1072                   = BOSdata.new()
htfadd1072.settings                 := SettingsHTFadd1072
htfadd1072.candles                  := candlesadd1072
htfadd1072.bosdata                  := bosdataadd1072
var CandleSet htfadd1073                     = CandleSet.new()
var CandleSettings SettingsHTFadd1073        = CandleSettings.new(htf='1073',htfint=1073,max_memory=3)
var Candle[] candlesadd1073                  = array.new<Candle>(0)
var BOSdata bosdataadd1073                   = BOSdata.new()
htfadd1073.settings                 := SettingsHTFadd1073
htfadd1073.candles                  := candlesadd1073
htfadd1073.bosdata                  := bosdataadd1073
var CandleSet htfadd1074                     = CandleSet.new()
var CandleSettings SettingsHTFadd1074        = CandleSettings.new(htf='1074',htfint=1074,max_memory=3)
var Candle[] candlesadd1074                  = array.new<Candle>(0)
var BOSdata bosdataadd1074                   = BOSdata.new()
htfadd1074.settings                 := SettingsHTFadd1074
htfadd1074.candles                  := candlesadd1074
htfadd1074.bosdata                  := bosdataadd1074
var CandleSet htfadd1075                     = CandleSet.new()
var CandleSettings SettingsHTFadd1075        = CandleSettings.new(htf='1075',htfint=1075,max_memory=3)
var Candle[] candlesadd1075                  = array.new<Candle>(0)
var BOSdata bosdataadd1075                   = BOSdata.new()
htfadd1075.settings                 := SettingsHTFadd1075
htfadd1075.candles                  := candlesadd1075
htfadd1075.bosdata                  := bosdataadd1075
var CandleSet htfadd1076                     = CandleSet.new()
var CandleSettings SettingsHTFadd1076        = CandleSettings.new(htf='1076',htfint=1076,max_memory=3)
var Candle[] candlesadd1076                  = array.new<Candle>(0)
var BOSdata bosdataadd1076                   = BOSdata.new()
htfadd1076.settings                 := SettingsHTFadd1076
htfadd1076.candles                  := candlesadd1076
htfadd1076.bosdata                  := bosdataadd1076
var CandleSet htfadd1077                     = CandleSet.new()
var CandleSettings SettingsHTFadd1077        = CandleSettings.new(htf='1077',htfint=1077,max_memory=3)
var Candle[] candlesadd1077                  = array.new<Candle>(0)
var BOSdata bosdataadd1077                   = BOSdata.new()
htfadd1077.settings                 := SettingsHTFadd1077
htfadd1077.candles                  := candlesadd1077
htfadd1077.bosdata                  := bosdataadd1077
var CandleSet htfadd1078                     = CandleSet.new()
var CandleSettings SettingsHTFadd1078        = CandleSettings.new(htf='1078',htfint=1078,max_memory=3)
var Candle[] candlesadd1078                  = array.new<Candle>(0)
var BOSdata bosdataadd1078                   = BOSdata.new()
htfadd1078.settings                 := SettingsHTFadd1078
htfadd1078.candles                  := candlesadd1078
htfadd1078.bosdata                  := bosdataadd1078
var CandleSet htfadd1079                     = CandleSet.new()
var CandleSettings SettingsHTFadd1079        = CandleSettings.new(htf='1079',htfint=1079,max_memory=3)
var Candle[] candlesadd1079                  = array.new<Candle>(0)
var BOSdata bosdataadd1079                   = BOSdata.new()
htfadd1079.settings                 := SettingsHTFadd1079
htfadd1079.candles                  := candlesadd1079
htfadd1079.bosdata                  := bosdataadd1079
var CandleSet htfadd1080                     = CandleSet.new()
var CandleSettings SettingsHTFadd1080        = CandleSettings.new(htf='1080',htfint=1080,max_memory=3)
var Candle[] candlesadd1080                  = array.new<Candle>(0)
var BOSdata bosdataadd1080                   = BOSdata.new()
htfadd1080.settings                 := SettingsHTFadd1080
htfadd1080.candles                  := candlesadd1080
htfadd1080.bosdata                  := bosdataadd1080

htfadd990.Monitor().BOSJudge()
htfadd991.Monitor().BOSJudge()
htfadd992.Monitor().BOSJudge()
htfadd993.Monitor().BOSJudge()
htfadd994.Monitor().BOSJudge()
htfadd995.Monitor().BOSJudge()
htfadd996.Monitor().BOSJudge()
htfadd997.Monitor().BOSJudge()
htfadd998.Monitor().BOSJudge()
htfadd999.Monitor().BOSJudge()
htfadd1000.Monitor().BOSJudge()
htfadd1001.Monitor().BOSJudge()
htfadd1002.Monitor().BOSJudge()
htfadd1003.Monitor().BOSJudge()
htfadd1004.Monitor().BOSJudge()
htfadd1005.Monitor().BOSJudge()
htfadd1006.Monitor().BOSJudge()
htfadd1007.Monitor().BOSJudge()
htfadd1008.Monitor().BOSJudge()
htfadd1009.Monitor().BOSJudge()
htfadd1010.Monitor().BOSJudge()
htfadd1011.Monitor().BOSJudge()
htfadd1012.Monitor().BOSJudge()
htfadd1013.Monitor().BOSJudge()
htfadd1014.Monitor().BOSJudge()
htfadd1015.Monitor().BOSJudge()
htfadd1016.Monitor().BOSJudge()
htfadd1017.Monitor().BOSJudge()
htfadd1018.Monitor().BOSJudge()
htfadd1019.Monitor().BOSJudge()
htfadd1020.Monitor().BOSJudge()
htfadd1021.Monitor().BOSJudge()
htfadd1022.Monitor().BOSJudge()
htfadd1023.Monitor().BOSJudge()
htfadd1024.Monitor().BOSJudge()
htfadd1025.Monitor().BOSJudge()
htfadd1026.Monitor().BOSJudge()
htfadd1027.Monitor().BOSJudge()
htfadd1028.Monitor().BOSJudge()
htfadd1029.Monitor().BOSJudge()
htfadd1030.Monitor().BOSJudge()
htfadd1031.Monitor().BOSJudge()
htfadd1032.Monitor().BOSJudge()
htfadd1033.Monitor().BOSJudge()
htfadd1034.Monitor().BOSJudge()
htfadd1035.Monitor().BOSJudge()
htfadd1036.Monitor().BOSJudge()
htfadd1037.Monitor().BOSJudge()
htfadd1038.Monitor().BOSJudge()
htfadd1039.Monitor().BOSJudge()
htfadd1040.Monitor().BOSJudge()
htfadd1041.Monitor().BOSJudge()
htfadd1042.Monitor().BOSJudge()
htfadd1043.Monitor().BOSJudge()
htfadd1044.Monitor().BOSJudge()
htfadd1045.Monitor().BOSJudge()
htfadd1046.Monitor().BOSJudge()
htfadd1047.Monitor().BOSJudge()
htfadd1048.Monitor().BOSJudge()
htfadd1049.Monitor().BOSJudge()
htfadd1050.Monitor().BOSJudge()
htfadd1051.Monitor().BOSJudge()
htfadd1052.Monitor().BOSJudge()
htfadd1053.Monitor().BOSJudge()
htfadd1054.Monitor().BOSJudge()
htfadd1055.Monitor().BOSJudge()
htfadd1056.Monitor().BOSJudge()
htfadd1057.Monitor().BOSJudge()
htfadd1058.Monitor().BOSJudge()
htfadd1059.Monitor().BOSJudge()
htfadd1060.Monitor().BOSJudge()
htfadd1061.Monitor().BOSJudge()
htfadd1062.Monitor().BOSJudge()
htfadd1063.Monitor().BOSJudge()
htfadd1064.Monitor().BOSJudge()
htfadd1065.Monitor().BOSJudge()
htfadd1066.Monitor().BOSJudge()
htfadd1067.Monitor().BOSJudge()
htfadd1068.Monitor().BOSJudge()
htfadd1069.Monitor().BOSJudge()
htfadd1070.Monitor().BOSJudge()
htfadd1071.Monitor().BOSJudge()
htfadd1072.Monitor().BOSJudge()
htfadd1073.Monitor().BOSJudge()
htfadd1074.Monitor().BOSJudge()
htfadd1075.Monitor().BOSJudge()
htfadd1076.Monitor().BOSJudge()
htfadd1077.Monitor().BOSJudge()
htfadd1078.Monitor().BOSJudge()
htfadd1079.Monitor().BOSJudge()
htfadd1080.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd990)
    LowestsbuSet(lowestsbu, htfadd990)
    HighestsbdSet(highestsbd, htfadd991)
    LowestsbuSet(lowestsbu, htfadd991)
    HighestsbdSet(highestsbd, htfadd992)
    LowestsbuSet(lowestsbu, htfadd992)
    HighestsbdSet(highestsbd, htfadd993)
    LowestsbuSet(lowestsbu, htfadd993)
    HighestsbdSet(highestsbd, htfadd994)
    LowestsbuSet(lowestsbu, htfadd994)
    HighestsbdSet(highestsbd, htfadd995)
    LowestsbuSet(lowestsbu, htfadd995)
    HighestsbdSet(highestsbd, htfadd996)
    LowestsbuSet(lowestsbu, htfadd996)
    HighestsbdSet(highestsbd, htfadd997)
    LowestsbuSet(lowestsbu, htfadd997)
    HighestsbdSet(highestsbd, htfadd998)
    LowestsbuSet(lowestsbu, htfadd998)
    HighestsbdSet(highestsbd, htfadd999)
    LowestsbuSet(lowestsbu, htfadd999)
    HighestsbdSet(highestsbd, htfadd1000)
    LowestsbuSet(lowestsbu, htfadd1000)
    HighestsbdSet(highestsbd, htfadd1001)
    LowestsbuSet(lowestsbu, htfadd1001)
    HighestsbdSet(highestsbd, htfadd1002)
    LowestsbuSet(lowestsbu, htfadd1002)
    HighestsbdSet(highestsbd, htfadd1003)
    LowestsbuSet(lowestsbu, htfadd1003)
    HighestsbdSet(highestsbd, htfadd1004)
    LowestsbuSet(lowestsbu, htfadd1004)
    HighestsbdSet(highestsbd, htfadd1005)
    LowestsbuSet(lowestsbu, htfadd1005)
    HighestsbdSet(highestsbd, htfadd1006)
    LowestsbuSet(lowestsbu, htfadd1006)
    HighestsbdSet(highestsbd, htfadd1007)
    LowestsbuSet(lowestsbu, htfadd1007)
    HighestsbdSet(highestsbd, htfadd1008)
    LowestsbuSet(lowestsbu, htfadd1008)
    HighestsbdSet(highestsbd, htfadd1009)
    LowestsbuSet(lowestsbu, htfadd1009)
    HighestsbdSet(highestsbd, htfadd1010)
    LowestsbuSet(lowestsbu, htfadd1010)
    HighestsbdSet(highestsbd, htfadd1011)
    LowestsbuSet(lowestsbu, htfadd1011)
    HighestsbdSet(highestsbd, htfadd1012)
    LowestsbuSet(lowestsbu, htfadd1012)
    HighestsbdSet(highestsbd, htfadd1013)
    LowestsbuSet(lowestsbu, htfadd1013)
    HighestsbdSet(highestsbd, htfadd1014)
    LowestsbuSet(lowestsbu, htfadd1014)
    HighestsbdSet(highestsbd, htfadd1015)
    LowestsbuSet(lowestsbu, htfadd1015)
    HighestsbdSet(highestsbd, htfadd1016)
    LowestsbuSet(lowestsbu, htfadd1016)
    HighestsbdSet(highestsbd, htfadd1017)
    LowestsbuSet(lowestsbu, htfadd1017)
    HighestsbdSet(highestsbd, htfadd1018)
    LowestsbuSet(lowestsbu, htfadd1018)
    HighestsbdSet(highestsbd, htfadd1019)
    LowestsbuSet(lowestsbu, htfadd1019)
    HighestsbdSet(highestsbd, htfadd1020)
    LowestsbuSet(lowestsbu, htfadd1020)
    HighestsbdSet(highestsbd, htfadd1021)
    LowestsbuSet(lowestsbu, htfadd1021)
    HighestsbdSet(highestsbd, htfadd1022)
    LowestsbuSet(lowestsbu, htfadd1022)
    HighestsbdSet(highestsbd, htfadd1023)
    LowestsbuSet(lowestsbu, htfadd1023)
    HighestsbdSet(highestsbd, htfadd1024)
    LowestsbuSet(lowestsbu, htfadd1024)
    HighestsbdSet(highestsbd, htfadd1025)
    LowestsbuSet(lowestsbu, htfadd1025)
    HighestsbdSet(highestsbd, htfadd1026)
    LowestsbuSet(lowestsbu, htfadd1026)
    HighestsbdSet(highestsbd, htfadd1027)
    LowestsbuSet(lowestsbu, htfadd1027)
    HighestsbdSet(highestsbd, htfadd1028)
    LowestsbuSet(lowestsbu, htfadd1028)
    HighestsbdSet(highestsbd, htfadd1029)
    LowestsbuSet(lowestsbu, htfadd1029)
    HighestsbdSet(highestsbd, htfadd1030)
    LowestsbuSet(lowestsbu, htfadd1030)
    HighestsbdSet(highestsbd, htfadd1031)
    LowestsbuSet(lowestsbu, htfadd1031)
    HighestsbdSet(highestsbd, htfadd1032)
    LowestsbuSet(lowestsbu, htfadd1032)
    HighestsbdSet(highestsbd, htfadd1033)
    LowestsbuSet(lowestsbu, htfadd1033)
    HighestsbdSet(highestsbd, htfadd1034)
    LowestsbuSet(lowestsbu, htfadd1034)
    HighestsbdSet(highestsbd, htfadd1035)
    LowestsbuSet(lowestsbu, htfadd1035)
    HighestsbdSet(highestsbd, htfadd1036)
    LowestsbuSet(lowestsbu, htfadd1036)
    HighestsbdSet(highestsbd, htfadd1037)
    LowestsbuSet(lowestsbu, htfadd1037)
    HighestsbdSet(highestsbd, htfadd1038)
    LowestsbuSet(lowestsbu, htfadd1038)
    HighestsbdSet(highestsbd, htfadd1039)
    LowestsbuSet(lowestsbu, htfadd1039)
    HighestsbdSet(highestsbd, htfadd1040)
    LowestsbuSet(lowestsbu, htfadd1040)
    HighestsbdSet(highestsbd, htfadd1041)
    LowestsbuSet(lowestsbu, htfadd1041)
    HighestsbdSet(highestsbd, htfadd1042)
    LowestsbuSet(lowestsbu, htfadd1042)
    HighestsbdSet(highestsbd, htfadd1043)
    LowestsbuSet(lowestsbu, htfadd1043)
    HighestsbdSet(highestsbd, htfadd1044)
    LowestsbuSet(lowestsbu, htfadd1044)
    HighestsbdSet(highestsbd, htfadd1045)
    LowestsbuSet(lowestsbu, htfadd1045)
    HighestsbdSet(highestsbd, htfadd1046)
    LowestsbuSet(lowestsbu, htfadd1046)
    HighestsbdSet(highestsbd, htfadd1047)
    LowestsbuSet(lowestsbu, htfadd1047)
    HighestsbdSet(highestsbd, htfadd1048)
    LowestsbuSet(lowestsbu, htfadd1048)
    HighestsbdSet(highestsbd, htfadd1049)
    LowestsbuSet(lowestsbu, htfadd1049)
    HighestsbdSet(highestsbd, htfadd1050)
    LowestsbuSet(lowestsbu, htfadd1050)
    HighestsbdSet(highestsbd, htfadd1051)
    LowestsbuSet(lowestsbu, htfadd1051)
    HighestsbdSet(highestsbd, htfadd1052)
    LowestsbuSet(lowestsbu, htfadd1052)
    HighestsbdSet(highestsbd, htfadd1053)
    LowestsbuSet(lowestsbu, htfadd1053)
    HighestsbdSet(highestsbd, htfadd1054)
    LowestsbuSet(lowestsbu, htfadd1054)
    HighestsbdSet(highestsbd, htfadd1055)
    LowestsbuSet(lowestsbu, htfadd1055)
    HighestsbdSet(highestsbd, htfadd1056)
    LowestsbuSet(lowestsbu, htfadd1056)
    HighestsbdSet(highestsbd, htfadd1057)
    LowestsbuSet(lowestsbu, htfadd1057)
    HighestsbdSet(highestsbd, htfadd1058)
    LowestsbuSet(lowestsbu, htfadd1058)
    HighestsbdSet(highestsbd, htfadd1059)
    LowestsbuSet(lowestsbu, htfadd1059)
    HighestsbdSet(highestsbd, htfadd1060)
    LowestsbuSet(lowestsbu, htfadd1060)
    HighestsbdSet(highestsbd, htfadd1061)
    LowestsbuSet(lowestsbu, htfadd1061)
    HighestsbdSet(highestsbd, htfadd1062)
    LowestsbuSet(lowestsbu, htfadd1062)
    HighestsbdSet(highestsbd, htfadd1063)
    LowestsbuSet(lowestsbu, htfadd1063)
    HighestsbdSet(highestsbd, htfadd1064)
    LowestsbuSet(lowestsbu, htfadd1064)
    HighestsbdSet(highestsbd, htfadd1065)
    LowestsbuSet(lowestsbu, htfadd1065)
    HighestsbdSet(highestsbd, htfadd1066)
    LowestsbuSet(lowestsbu, htfadd1066)
    HighestsbdSet(highestsbd, htfadd1067)
    LowestsbuSet(lowestsbu, htfadd1067)
    HighestsbdSet(highestsbd, htfadd1068)
    LowestsbuSet(lowestsbu, htfadd1068)
    HighestsbdSet(highestsbd, htfadd1069)
    LowestsbuSet(lowestsbu, htfadd1069)
    HighestsbdSet(highestsbd, htfadd1070)
    LowestsbuSet(lowestsbu, htfadd1070)
    HighestsbdSet(highestsbd, htfadd1071)
    LowestsbuSet(lowestsbu, htfadd1071)
    HighestsbdSet(highestsbd, htfadd1072)
    LowestsbuSet(lowestsbu, htfadd1072)
    HighestsbdSet(highestsbd, htfadd1073)
    LowestsbuSet(lowestsbu, htfadd1073)
    HighestsbdSet(highestsbd, htfadd1074)
    LowestsbuSet(lowestsbu, htfadd1074)
    HighestsbdSet(highestsbd, htfadd1075)
    LowestsbuSet(lowestsbu, htfadd1075)
    HighestsbdSet(highestsbd, htfadd1076)
    LowestsbuSet(lowestsbu, htfadd1076)
    HighestsbdSet(highestsbd, htfadd1077)
    LowestsbuSet(lowestsbu, htfadd1077)
    HighestsbdSet(highestsbd, htfadd1078)
    LowestsbuSet(lowestsbu, htfadd1078)
    HighestsbdSet(highestsbd, htfadd1079)
    LowestsbuSet(lowestsbu, htfadd1079)
    HighestsbdSet(highestsbd, htfadd1080)
    LowestsbuSet(lowestsbu, htfadd1080)

    htfshadow.Shadowing(htfadd990).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd991).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd992).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd993).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd994).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd995).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd996).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd997).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd998).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd999).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1000).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1001).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1002).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1003).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1004).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1005).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1006).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1007).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1008).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1009).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1010).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1011).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1012).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1013).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1014).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1015).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1016).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1017).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1018).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1019).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1020).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1021).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1022).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1023).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1024).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1025).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1026).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1027).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1028).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1029).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1030).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1031).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1032).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1033).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1034).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1035).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1036).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1037).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1038).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1039).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1040).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1041).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1042).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1043).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1044).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1045).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1046).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1047).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1048).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1049).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1050).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1051).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1052).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1053).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1054).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1055).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1056).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1057).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1058).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1059).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1060).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1061).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1062).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1063).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1064).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1065).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1066).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1067).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1068).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1069).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1070).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1071).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1072).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1073).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1074).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1075).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1076).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1077).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1078).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1079).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1080).Monitor_Est().BOSJudge()
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


