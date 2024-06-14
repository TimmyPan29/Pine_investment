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
var CandleSet htfadd360                     = CandleSet.new()
var CandleSettings SettingsHTFadd360        = CandleSettings.new(htf='360',htfint=360,max_memory=3)
var Candle[] candlesadd360                  = array.new<Candle>(0)
var BOSdata bosdataadd360                   = BOSdata.new()
htfadd360.settings                 := SettingsHTFadd360
htfadd360.candles                  := candlesadd360
htfadd360.bosdata                  := bosdataadd360
var CandleSet htfadd361                     = CandleSet.new()
var CandleSettings SettingsHTFadd361        = CandleSettings.new(htf='361',htfint=361,max_memory=3)
var Candle[] candlesadd361                  = array.new<Candle>(0)
var BOSdata bosdataadd361                   = BOSdata.new()
htfadd361.settings                 := SettingsHTFadd361
htfadd361.candles                  := candlesadd361
htfadd361.bosdata                  := bosdataadd361
var CandleSet htfadd362                     = CandleSet.new()
var CandleSettings SettingsHTFadd362        = CandleSettings.new(htf='362',htfint=362,max_memory=3)
var Candle[] candlesadd362                  = array.new<Candle>(0)
var BOSdata bosdataadd362                   = BOSdata.new()
htfadd362.settings                 := SettingsHTFadd362
htfadd362.candles                  := candlesadd362
htfadd362.bosdata                  := bosdataadd362
var CandleSet htfadd363                     = CandleSet.new()
var CandleSettings SettingsHTFadd363        = CandleSettings.new(htf='363',htfint=363,max_memory=3)
var Candle[] candlesadd363                  = array.new<Candle>(0)
var BOSdata bosdataadd363                   = BOSdata.new()
htfadd363.settings                 := SettingsHTFadd363
htfadd363.candles                  := candlesadd363
htfadd363.bosdata                  := bosdataadd363
var CandleSet htfadd364                     = CandleSet.new()
var CandleSettings SettingsHTFadd364        = CandleSettings.new(htf='364',htfint=364,max_memory=3)
var Candle[] candlesadd364                  = array.new<Candle>(0)
var BOSdata bosdataadd364                   = BOSdata.new()
htfadd364.settings                 := SettingsHTFadd364
htfadd364.candles                  := candlesadd364
htfadd364.bosdata                  := bosdataadd364
var CandleSet htfadd365                     = CandleSet.new()
var CandleSettings SettingsHTFadd365        = CandleSettings.new(htf='365',htfint=365,max_memory=3)
var Candle[] candlesadd365                  = array.new<Candle>(0)
var BOSdata bosdataadd365                   = BOSdata.new()
htfadd365.settings                 := SettingsHTFadd365
htfadd365.candles                  := candlesadd365
htfadd365.bosdata                  := bosdataadd365
var CandleSet htfadd366                     = CandleSet.new()
var CandleSettings SettingsHTFadd366        = CandleSettings.new(htf='366',htfint=366,max_memory=3)
var Candle[] candlesadd366                  = array.new<Candle>(0)
var BOSdata bosdataadd366                   = BOSdata.new()
htfadd366.settings                 := SettingsHTFadd366
htfadd366.candles                  := candlesadd366
htfadd366.bosdata                  := bosdataadd366
var CandleSet htfadd367                     = CandleSet.new()
var CandleSettings SettingsHTFadd367        = CandleSettings.new(htf='367',htfint=367,max_memory=3)
var Candle[] candlesadd367                  = array.new<Candle>(0)
var BOSdata bosdataadd367                   = BOSdata.new()
htfadd367.settings                 := SettingsHTFadd367
htfadd367.candles                  := candlesadd367
htfadd367.bosdata                  := bosdataadd367
var CandleSet htfadd368                     = CandleSet.new()
var CandleSettings SettingsHTFadd368        = CandleSettings.new(htf='368',htfint=368,max_memory=3)
var Candle[] candlesadd368                  = array.new<Candle>(0)
var BOSdata bosdataadd368                   = BOSdata.new()
htfadd368.settings                 := SettingsHTFadd368
htfadd368.candles                  := candlesadd368
htfadd368.bosdata                  := bosdataadd368
var CandleSet htfadd369                     = CandleSet.new()
var CandleSettings SettingsHTFadd369        = CandleSettings.new(htf='369',htfint=369,max_memory=3)
var Candle[] candlesadd369                  = array.new<Candle>(0)
var BOSdata bosdataadd369                   = BOSdata.new()
htfadd369.settings                 := SettingsHTFadd369
htfadd369.candles                  := candlesadd369
htfadd369.bosdata                  := bosdataadd369
var CandleSet htfadd370                     = CandleSet.new()
var CandleSettings SettingsHTFadd370        = CandleSettings.new(htf='370',htfint=370,max_memory=3)
var Candle[] candlesadd370                  = array.new<Candle>(0)
var BOSdata bosdataadd370                   = BOSdata.new()
htfadd370.settings                 := SettingsHTFadd370
htfadd370.candles                  := candlesadd370
htfadd370.bosdata                  := bosdataadd370
var CandleSet htfadd371                     = CandleSet.new()
var CandleSettings SettingsHTFadd371        = CandleSettings.new(htf='371',htfint=371,max_memory=3)
var Candle[] candlesadd371                  = array.new<Candle>(0)
var BOSdata bosdataadd371                   = BOSdata.new()
htfadd371.settings                 := SettingsHTFadd371
htfadd371.candles                  := candlesadd371
htfadd371.bosdata                  := bosdataadd371
var CandleSet htfadd372                     = CandleSet.new()
var CandleSettings SettingsHTFadd372        = CandleSettings.new(htf='372',htfint=372,max_memory=3)
var Candle[] candlesadd372                  = array.new<Candle>(0)
var BOSdata bosdataadd372                   = BOSdata.new()
htfadd372.settings                 := SettingsHTFadd372
htfadd372.candles                  := candlesadd372
htfadd372.bosdata                  := bosdataadd372
var CandleSet htfadd373                     = CandleSet.new()
var CandleSettings SettingsHTFadd373        = CandleSettings.new(htf='373',htfint=373,max_memory=3)
var Candle[] candlesadd373                  = array.new<Candle>(0)
var BOSdata bosdataadd373                   = BOSdata.new()
htfadd373.settings                 := SettingsHTFadd373
htfadd373.candles                  := candlesadd373
htfadd373.bosdata                  := bosdataadd373
var CandleSet htfadd374                     = CandleSet.new()
var CandleSettings SettingsHTFadd374        = CandleSettings.new(htf='374',htfint=374,max_memory=3)
var Candle[] candlesadd374                  = array.new<Candle>(0)
var BOSdata bosdataadd374                   = BOSdata.new()
htfadd374.settings                 := SettingsHTFadd374
htfadd374.candles                  := candlesadd374
htfadd374.bosdata                  := bosdataadd374
var CandleSet htfadd375                     = CandleSet.new()
var CandleSettings SettingsHTFadd375        = CandleSettings.new(htf='375',htfint=375,max_memory=3)
var Candle[] candlesadd375                  = array.new<Candle>(0)
var BOSdata bosdataadd375                   = BOSdata.new()
htfadd375.settings                 := SettingsHTFadd375
htfadd375.candles                  := candlesadd375
htfadd375.bosdata                  := bosdataadd375
var CandleSet htfadd376                     = CandleSet.new()
var CandleSettings SettingsHTFadd376        = CandleSettings.new(htf='376',htfint=376,max_memory=3)
var Candle[] candlesadd376                  = array.new<Candle>(0)
var BOSdata bosdataadd376                   = BOSdata.new()
htfadd376.settings                 := SettingsHTFadd376
htfadd376.candles                  := candlesadd376
htfadd376.bosdata                  := bosdataadd376
var CandleSet htfadd377                     = CandleSet.new()
var CandleSettings SettingsHTFadd377        = CandleSettings.new(htf='377',htfint=377,max_memory=3)
var Candle[] candlesadd377                  = array.new<Candle>(0)
var BOSdata bosdataadd377                   = BOSdata.new()
htfadd377.settings                 := SettingsHTFadd377
htfadd377.candles                  := candlesadd377
htfadd377.bosdata                  := bosdataadd377
var CandleSet htfadd378                     = CandleSet.new()
var CandleSettings SettingsHTFadd378        = CandleSettings.new(htf='378',htfint=378,max_memory=3)
var Candle[] candlesadd378                  = array.new<Candle>(0)
var BOSdata bosdataadd378                   = BOSdata.new()
htfadd378.settings                 := SettingsHTFadd378
htfadd378.candles                  := candlesadd378
htfadd378.bosdata                  := bosdataadd378
var CandleSet htfadd379                     = CandleSet.new()
var CandleSettings SettingsHTFadd379        = CandleSettings.new(htf='379',htfint=379,max_memory=3)
var Candle[] candlesadd379                  = array.new<Candle>(0)
var BOSdata bosdataadd379                   = BOSdata.new()
htfadd379.settings                 := SettingsHTFadd379
htfadd379.candles                  := candlesadd379
htfadd379.bosdata                  := bosdataadd379
var CandleSet htfadd380                     = CandleSet.new()
var CandleSettings SettingsHTFadd380        = CandleSettings.new(htf='380',htfint=380,max_memory=3)
var Candle[] candlesadd380                  = array.new<Candle>(0)
var BOSdata bosdataadd380                   = BOSdata.new()
htfadd380.settings                 := SettingsHTFadd380
htfadd380.candles                  := candlesadd380
htfadd380.bosdata                  := bosdataadd380
var CandleSet htfadd381                     = CandleSet.new()
var CandleSettings SettingsHTFadd381        = CandleSettings.new(htf='381',htfint=381,max_memory=3)
var Candle[] candlesadd381                  = array.new<Candle>(0)
var BOSdata bosdataadd381                   = BOSdata.new()
htfadd381.settings                 := SettingsHTFadd381
htfadd381.candles                  := candlesadd381
htfadd381.bosdata                  := bosdataadd381
var CandleSet htfadd382                     = CandleSet.new()
var CandleSettings SettingsHTFadd382        = CandleSettings.new(htf='382',htfint=382,max_memory=3)
var Candle[] candlesadd382                  = array.new<Candle>(0)
var BOSdata bosdataadd382                   = BOSdata.new()
htfadd382.settings                 := SettingsHTFadd382
htfadd382.candles                  := candlesadd382
htfadd382.bosdata                  := bosdataadd382
var CandleSet htfadd383                     = CandleSet.new()
var CandleSettings SettingsHTFadd383        = CandleSettings.new(htf='383',htfint=383,max_memory=3)
var Candle[] candlesadd383                  = array.new<Candle>(0)
var BOSdata bosdataadd383                   = BOSdata.new()
htfadd383.settings                 := SettingsHTFadd383
htfadd383.candles                  := candlesadd383
htfadd383.bosdata                  := bosdataadd383
var CandleSet htfadd384                     = CandleSet.new()
var CandleSettings SettingsHTFadd384        = CandleSettings.new(htf='384',htfint=384,max_memory=3)
var Candle[] candlesadd384                  = array.new<Candle>(0)
var BOSdata bosdataadd384                   = BOSdata.new()
htfadd384.settings                 := SettingsHTFadd384
htfadd384.candles                  := candlesadd384
htfadd384.bosdata                  := bosdataadd384
var CandleSet htfadd385                     = CandleSet.new()
var CandleSettings SettingsHTFadd385        = CandleSettings.new(htf='385',htfint=385,max_memory=3)
var Candle[] candlesadd385                  = array.new<Candle>(0)
var BOSdata bosdataadd385                   = BOSdata.new()
htfadd385.settings                 := SettingsHTFadd385
htfadd385.candles                  := candlesadd385
htfadd385.bosdata                  := bosdataadd385
var CandleSet htfadd386                     = CandleSet.new()
var CandleSettings SettingsHTFadd386        = CandleSettings.new(htf='386',htfint=386,max_memory=3)
var Candle[] candlesadd386                  = array.new<Candle>(0)
var BOSdata bosdataadd386                   = BOSdata.new()
htfadd386.settings                 := SettingsHTFadd386
htfadd386.candles                  := candlesadd386
htfadd386.bosdata                  := bosdataadd386
var CandleSet htfadd387                     = CandleSet.new()
var CandleSettings SettingsHTFadd387        = CandleSettings.new(htf='387',htfint=387,max_memory=3)
var Candle[] candlesadd387                  = array.new<Candle>(0)
var BOSdata bosdataadd387                   = BOSdata.new()
htfadd387.settings                 := SettingsHTFadd387
htfadd387.candles                  := candlesadd387
htfadd387.bosdata                  := bosdataadd387
var CandleSet htfadd388                     = CandleSet.new()
var CandleSettings SettingsHTFadd388        = CandleSettings.new(htf='388',htfint=388,max_memory=3)
var Candle[] candlesadd388                  = array.new<Candle>(0)
var BOSdata bosdataadd388                   = BOSdata.new()
htfadd388.settings                 := SettingsHTFadd388
htfadd388.candles                  := candlesadd388
htfadd388.bosdata                  := bosdataadd388
var CandleSet htfadd389                     = CandleSet.new()
var CandleSettings SettingsHTFadd389        = CandleSettings.new(htf='389',htfint=389,max_memory=3)
var Candle[] candlesadd389                  = array.new<Candle>(0)
var BOSdata bosdataadd389                   = BOSdata.new()
htfadd389.settings                 := SettingsHTFadd389
htfadd389.candles                  := candlesadd389
htfadd389.bosdata                  := bosdataadd389
var CandleSet htfadd390                     = CandleSet.new()
var CandleSettings SettingsHTFadd390        = CandleSettings.new(htf='390',htfint=390,max_memory=3)
var Candle[] candlesadd390                  = array.new<Candle>(0)
var BOSdata bosdataadd390                   = BOSdata.new()
htfadd390.settings                 := SettingsHTFadd390
htfadd390.candles                  := candlesadd390
htfadd390.bosdata                  := bosdataadd390
var CandleSet htfadd391                     = CandleSet.new()
var CandleSettings SettingsHTFadd391        = CandleSettings.new(htf='391',htfint=391,max_memory=3)
var Candle[] candlesadd391                  = array.new<Candle>(0)
var BOSdata bosdataadd391                   = BOSdata.new()
htfadd391.settings                 := SettingsHTFadd391
htfadd391.candles                  := candlesadd391
htfadd391.bosdata                  := bosdataadd391
var CandleSet htfadd392                     = CandleSet.new()
var CandleSettings SettingsHTFadd392        = CandleSettings.new(htf='392',htfint=392,max_memory=3)
var Candle[] candlesadd392                  = array.new<Candle>(0)
var BOSdata bosdataadd392                   = BOSdata.new()
htfadd392.settings                 := SettingsHTFadd392
htfadd392.candles                  := candlesadd392
htfadd392.bosdata                  := bosdataadd392
var CandleSet htfadd393                     = CandleSet.new()
var CandleSettings SettingsHTFadd393        = CandleSettings.new(htf='393',htfint=393,max_memory=3)
var Candle[] candlesadd393                  = array.new<Candle>(0)
var BOSdata bosdataadd393                   = BOSdata.new()
htfadd393.settings                 := SettingsHTFadd393
htfadd393.candles                  := candlesadd393
htfadd393.bosdata                  := bosdataadd393
var CandleSet htfadd394                     = CandleSet.new()
var CandleSettings SettingsHTFadd394        = CandleSettings.new(htf='394',htfint=394,max_memory=3)
var Candle[] candlesadd394                  = array.new<Candle>(0)
var BOSdata bosdataadd394                   = BOSdata.new()
htfadd394.settings                 := SettingsHTFadd394
htfadd394.candles                  := candlesadd394
htfadd394.bosdata                  := bosdataadd394
var CandleSet htfadd395                     = CandleSet.new()
var CandleSettings SettingsHTFadd395        = CandleSettings.new(htf='395',htfint=395,max_memory=3)
var Candle[] candlesadd395                  = array.new<Candle>(0)
var BOSdata bosdataadd395                   = BOSdata.new()
htfadd395.settings                 := SettingsHTFadd395
htfadd395.candles                  := candlesadd395
htfadd395.bosdata                  := bosdataadd395
var CandleSet htfadd396                     = CandleSet.new()
var CandleSettings SettingsHTFadd396        = CandleSettings.new(htf='396',htfint=396,max_memory=3)
var Candle[] candlesadd396                  = array.new<Candle>(0)
var BOSdata bosdataadd396                   = BOSdata.new()
htfadd396.settings                 := SettingsHTFadd396
htfadd396.candles                  := candlesadd396
htfadd396.bosdata                  := bosdataadd396
var CandleSet htfadd397                     = CandleSet.new()
var CandleSettings SettingsHTFadd397        = CandleSettings.new(htf='397',htfint=397,max_memory=3)
var Candle[] candlesadd397                  = array.new<Candle>(0)
var BOSdata bosdataadd397                   = BOSdata.new()
htfadd397.settings                 := SettingsHTFadd397
htfadd397.candles                  := candlesadd397
htfadd397.bosdata                  := bosdataadd397
var CandleSet htfadd398                     = CandleSet.new()
var CandleSettings SettingsHTFadd398        = CandleSettings.new(htf='398',htfint=398,max_memory=3)
var Candle[] candlesadd398                  = array.new<Candle>(0)
var BOSdata bosdataadd398                   = BOSdata.new()
htfadd398.settings                 := SettingsHTFadd398
htfadd398.candles                  := candlesadd398
htfadd398.bosdata                  := bosdataadd398
var CandleSet htfadd399                     = CandleSet.new()
var CandleSettings SettingsHTFadd399        = CandleSettings.new(htf='399',htfint=399,max_memory=3)
var Candle[] candlesadd399                  = array.new<Candle>(0)
var BOSdata bosdataadd399                   = BOSdata.new()
htfadd399.settings                 := SettingsHTFadd399
htfadd399.candles                  := candlesadd399
htfadd399.bosdata                  := bosdataadd399
var CandleSet htfadd400                     = CandleSet.new()
var CandleSettings SettingsHTFadd400        = CandleSettings.new(htf='400',htfint=400,max_memory=3)
var Candle[] candlesadd400                  = array.new<Candle>(0)
var BOSdata bosdataadd400                   = BOSdata.new()
htfadd400.settings                 := SettingsHTFadd400
htfadd400.candles                  := candlesadd400
htfadd400.bosdata                  := bosdataadd400
var CandleSet htfadd401                     = CandleSet.new()
var CandleSettings SettingsHTFadd401        = CandleSettings.new(htf='401',htfint=401,max_memory=3)
var Candle[] candlesadd401                  = array.new<Candle>(0)
var BOSdata bosdataadd401                   = BOSdata.new()
htfadd401.settings                 := SettingsHTFadd401
htfadd401.candles                  := candlesadd401
htfadd401.bosdata                  := bosdataadd401
var CandleSet htfadd402                     = CandleSet.new()
var CandleSettings SettingsHTFadd402        = CandleSettings.new(htf='402',htfint=402,max_memory=3)
var Candle[] candlesadd402                  = array.new<Candle>(0)
var BOSdata bosdataadd402                   = BOSdata.new()
htfadd402.settings                 := SettingsHTFadd402
htfadd402.candles                  := candlesadd402
htfadd402.bosdata                  := bosdataadd402
var CandleSet htfadd403                     = CandleSet.new()
var CandleSettings SettingsHTFadd403        = CandleSettings.new(htf='403',htfint=403,max_memory=3)
var Candle[] candlesadd403                  = array.new<Candle>(0)
var BOSdata bosdataadd403                   = BOSdata.new()
htfadd403.settings                 := SettingsHTFadd403
htfadd403.candles                  := candlesadd403
htfadd403.bosdata                  := bosdataadd403
var CandleSet htfadd404                     = CandleSet.new()
var CandleSettings SettingsHTFadd404        = CandleSettings.new(htf='404',htfint=404,max_memory=3)
var Candle[] candlesadd404                  = array.new<Candle>(0)
var BOSdata bosdataadd404                   = BOSdata.new()
htfadd404.settings                 := SettingsHTFadd404
htfadd404.candles                  := candlesadd404
htfadd404.bosdata                  := bosdataadd404
var CandleSet htfadd405                     = CandleSet.new()
var CandleSettings SettingsHTFadd405        = CandleSettings.new(htf='405',htfint=405,max_memory=3)
var Candle[] candlesadd405                  = array.new<Candle>(0)
var BOSdata bosdataadd405                   = BOSdata.new()
htfadd405.settings                 := SettingsHTFadd405
htfadd405.candles                  := candlesadd405
htfadd405.bosdata                  := bosdataadd405
var CandleSet htfadd406                     = CandleSet.new()
var CandleSettings SettingsHTFadd406        = CandleSettings.new(htf='406',htfint=406,max_memory=3)
var Candle[] candlesadd406                  = array.new<Candle>(0)
var BOSdata bosdataadd406                   = BOSdata.new()
htfadd406.settings                 := SettingsHTFadd406
htfadd406.candles                  := candlesadd406
htfadd406.bosdata                  := bosdataadd406
var CandleSet htfadd407                     = CandleSet.new()
var CandleSettings SettingsHTFadd407        = CandleSettings.new(htf='407',htfint=407,max_memory=3)
var Candle[] candlesadd407                  = array.new<Candle>(0)
var BOSdata bosdataadd407                   = BOSdata.new()
htfadd407.settings                 := SettingsHTFadd407
htfadd407.candles                  := candlesadd407
htfadd407.bosdata                  := bosdataadd407
var CandleSet htfadd408                     = CandleSet.new()
var CandleSettings SettingsHTFadd408        = CandleSettings.new(htf='408',htfint=408,max_memory=3)
var Candle[] candlesadd408                  = array.new<Candle>(0)
var BOSdata bosdataadd408                   = BOSdata.new()
htfadd408.settings                 := SettingsHTFadd408
htfadd408.candles                  := candlesadd408
htfadd408.bosdata                  := bosdataadd408
var CandleSet htfadd409                     = CandleSet.new()
var CandleSettings SettingsHTFadd409        = CandleSettings.new(htf='409',htfint=409,max_memory=3)
var Candle[] candlesadd409                  = array.new<Candle>(0)
var BOSdata bosdataadd409                   = BOSdata.new()
htfadd409.settings                 := SettingsHTFadd409
htfadd409.candles                  := candlesadd409
htfadd409.bosdata                  := bosdataadd409
var CandleSet htfadd410                     = CandleSet.new()
var CandleSettings SettingsHTFadd410        = CandleSettings.new(htf='410',htfint=410,max_memory=3)
var Candle[] candlesadd410                  = array.new<Candle>(0)
var BOSdata bosdataadd410                   = BOSdata.new()
htfadd410.settings                 := SettingsHTFadd410
htfadd410.candles                  := candlesadd410
htfadd410.bosdata                  := bosdataadd410
var CandleSet htfadd411                     = CandleSet.new()
var CandleSettings SettingsHTFadd411        = CandleSettings.new(htf='411',htfint=411,max_memory=3)
var Candle[] candlesadd411                  = array.new<Candle>(0)
var BOSdata bosdataadd411                   = BOSdata.new()
htfadd411.settings                 := SettingsHTFadd411
htfadd411.candles                  := candlesadd411
htfadd411.bosdata                  := bosdataadd411
var CandleSet htfadd412                     = CandleSet.new()
var CandleSettings SettingsHTFadd412        = CandleSettings.new(htf='412',htfint=412,max_memory=3)
var Candle[] candlesadd412                  = array.new<Candle>(0)
var BOSdata bosdataadd412                   = BOSdata.new()
htfadd412.settings                 := SettingsHTFadd412
htfadd412.candles                  := candlesadd412
htfadd412.bosdata                  := bosdataadd412
var CandleSet htfadd413                     = CandleSet.new()
var CandleSettings SettingsHTFadd413        = CandleSettings.new(htf='413',htfint=413,max_memory=3)
var Candle[] candlesadd413                  = array.new<Candle>(0)
var BOSdata bosdataadd413                   = BOSdata.new()
htfadd413.settings                 := SettingsHTFadd413
htfadd413.candles                  := candlesadd413
htfadd413.bosdata                  := bosdataadd413
var CandleSet htfadd414                     = CandleSet.new()
var CandleSettings SettingsHTFadd414        = CandleSettings.new(htf='414',htfint=414,max_memory=3)
var Candle[] candlesadd414                  = array.new<Candle>(0)
var BOSdata bosdataadd414                   = BOSdata.new()
htfadd414.settings                 := SettingsHTFadd414
htfadd414.candles                  := candlesadd414
htfadd414.bosdata                  := bosdataadd414
var CandleSet htfadd415                     = CandleSet.new()
var CandleSettings SettingsHTFadd415        = CandleSettings.new(htf='415',htfint=415,max_memory=3)
var Candle[] candlesadd415                  = array.new<Candle>(0)
var BOSdata bosdataadd415                   = BOSdata.new()
htfadd415.settings                 := SettingsHTFadd415
htfadd415.candles                  := candlesadd415
htfadd415.bosdata                  := bosdataadd415
var CandleSet htfadd416                     = CandleSet.new()
var CandleSettings SettingsHTFadd416        = CandleSettings.new(htf='416',htfint=416,max_memory=3)
var Candle[] candlesadd416                  = array.new<Candle>(0)
var BOSdata bosdataadd416                   = BOSdata.new()
htfadd416.settings                 := SettingsHTFadd416
htfadd416.candles                  := candlesadd416
htfadd416.bosdata                  := bosdataadd416
var CandleSet htfadd417                     = CandleSet.new()
var CandleSettings SettingsHTFadd417        = CandleSettings.new(htf='417',htfint=417,max_memory=3)
var Candle[] candlesadd417                  = array.new<Candle>(0)
var BOSdata bosdataadd417                   = BOSdata.new()
htfadd417.settings                 := SettingsHTFadd417
htfadd417.candles                  := candlesadd417
htfadd417.bosdata                  := bosdataadd417
var CandleSet htfadd418                     = CandleSet.new()
var CandleSettings SettingsHTFadd418        = CandleSettings.new(htf='418',htfint=418,max_memory=3)
var Candle[] candlesadd418                  = array.new<Candle>(0)
var BOSdata bosdataadd418                   = BOSdata.new()
htfadd418.settings                 := SettingsHTFadd418
htfadd418.candles                  := candlesadd418
htfadd418.bosdata                  := bosdataadd418
var CandleSet htfadd419                     = CandleSet.new()
var CandleSettings SettingsHTFadd419        = CandleSettings.new(htf='419',htfint=419,max_memory=3)
var Candle[] candlesadd419                  = array.new<Candle>(0)
var BOSdata bosdataadd419                   = BOSdata.new()
htfadd419.settings                 := SettingsHTFadd419
htfadd419.candles                  := candlesadd419
htfadd419.bosdata                  := bosdataadd419
var CandleSet htfadd420                     = CandleSet.new()
var CandleSettings SettingsHTFadd420        = CandleSettings.new(htf='420',htfint=420,max_memory=3)
var Candle[] candlesadd420                  = array.new<Candle>(0)
var BOSdata bosdataadd420                   = BOSdata.new()
htfadd420.settings                 := SettingsHTFadd420
htfadd420.candles                  := candlesadd420
htfadd420.bosdata                  := bosdataadd420
var CandleSet htfadd421                     = CandleSet.new()
var CandleSettings SettingsHTFadd421        = CandleSettings.new(htf='421',htfint=421,max_memory=3)
var Candle[] candlesadd421                  = array.new<Candle>(0)
var BOSdata bosdataadd421                   = BOSdata.new()
htfadd421.settings                 := SettingsHTFadd421
htfadd421.candles                  := candlesadd421
htfadd421.bosdata                  := bosdataadd421
var CandleSet htfadd422                     = CandleSet.new()
var CandleSettings SettingsHTFadd422        = CandleSettings.new(htf='422',htfint=422,max_memory=3)
var Candle[] candlesadd422                  = array.new<Candle>(0)
var BOSdata bosdataadd422                   = BOSdata.new()
htfadd422.settings                 := SettingsHTFadd422
htfadd422.candles                  := candlesadd422
htfadd422.bosdata                  := bosdataadd422
var CandleSet htfadd423                     = CandleSet.new()
var CandleSettings SettingsHTFadd423        = CandleSettings.new(htf='423',htfint=423,max_memory=3)
var Candle[] candlesadd423                  = array.new<Candle>(0)
var BOSdata bosdataadd423                   = BOSdata.new()
htfadd423.settings                 := SettingsHTFadd423
htfadd423.candles                  := candlesadd423
htfadd423.bosdata                  := bosdataadd423
var CandleSet htfadd424                     = CandleSet.new()
var CandleSettings SettingsHTFadd424        = CandleSettings.new(htf='424',htfint=424,max_memory=3)
var Candle[] candlesadd424                  = array.new<Candle>(0)
var BOSdata bosdataadd424                   = BOSdata.new()
htfadd424.settings                 := SettingsHTFadd424
htfadd424.candles                  := candlesadd424
htfadd424.bosdata                  := bosdataadd424
var CandleSet htfadd425                     = CandleSet.new()
var CandleSettings SettingsHTFadd425        = CandleSettings.new(htf='425',htfint=425,max_memory=3)
var Candle[] candlesadd425                  = array.new<Candle>(0)
var BOSdata bosdataadd425                   = BOSdata.new()
htfadd425.settings                 := SettingsHTFadd425
htfadd425.candles                  := candlesadd425
htfadd425.bosdata                  := bosdataadd425
var CandleSet htfadd426                     = CandleSet.new()
var CandleSettings SettingsHTFadd426        = CandleSettings.new(htf='426',htfint=426,max_memory=3)
var Candle[] candlesadd426                  = array.new<Candle>(0)
var BOSdata bosdataadd426                   = BOSdata.new()
htfadd426.settings                 := SettingsHTFadd426
htfadd426.candles                  := candlesadd426
htfadd426.bosdata                  := bosdataadd426
var CandleSet htfadd427                     = CandleSet.new()
var CandleSettings SettingsHTFadd427        = CandleSettings.new(htf='427',htfint=427,max_memory=3)
var Candle[] candlesadd427                  = array.new<Candle>(0)
var BOSdata bosdataadd427                   = BOSdata.new()
htfadd427.settings                 := SettingsHTFadd427
htfadd427.candles                  := candlesadd427
htfadd427.bosdata                  := bosdataadd427
var CandleSet htfadd428                     = CandleSet.new()
var CandleSettings SettingsHTFadd428        = CandleSettings.new(htf='428',htfint=428,max_memory=3)
var Candle[] candlesadd428                  = array.new<Candle>(0)
var BOSdata bosdataadd428                   = BOSdata.new()
htfadd428.settings                 := SettingsHTFadd428
htfadd428.candles                  := candlesadd428
htfadd428.bosdata                  := bosdataadd428
var CandleSet htfadd429                     = CandleSet.new()
var CandleSettings SettingsHTFadd429        = CandleSettings.new(htf='429',htfint=429,max_memory=3)
var Candle[] candlesadd429                  = array.new<Candle>(0)
var BOSdata bosdataadd429                   = BOSdata.new()
htfadd429.settings                 := SettingsHTFadd429
htfadd429.candles                  := candlesadd429
htfadd429.bosdata                  := bosdataadd429
var CandleSet htfadd430                     = CandleSet.new()
var CandleSettings SettingsHTFadd430        = CandleSettings.new(htf='430',htfint=430,max_memory=3)
var Candle[] candlesadd430                  = array.new<Candle>(0)
var BOSdata bosdataadd430                   = BOSdata.new()
htfadd430.settings                 := SettingsHTFadd430
htfadd430.candles                  := candlesadd430
htfadd430.bosdata                  := bosdataadd430
var CandleSet htfadd431                     = CandleSet.new()
var CandleSettings SettingsHTFadd431        = CandleSettings.new(htf='431',htfint=431,max_memory=3)
var Candle[] candlesadd431                  = array.new<Candle>(0)
var BOSdata bosdataadd431                   = BOSdata.new()
htfadd431.settings                 := SettingsHTFadd431
htfadd431.candles                  := candlesadd431
htfadd431.bosdata                  := bosdataadd431
var CandleSet htfadd432                     = CandleSet.new()
var CandleSettings SettingsHTFadd432        = CandleSettings.new(htf='432',htfint=432,max_memory=3)
var Candle[] candlesadd432                  = array.new<Candle>(0)
var BOSdata bosdataadd432                   = BOSdata.new()
htfadd432.settings                 := SettingsHTFadd432
htfadd432.candles                  := candlesadd432
htfadd432.bosdata                  := bosdataadd432
var CandleSet htfadd433                     = CandleSet.new()
var CandleSettings SettingsHTFadd433        = CandleSettings.new(htf='433',htfint=433,max_memory=3)
var Candle[] candlesadd433                  = array.new<Candle>(0)
var BOSdata bosdataadd433                   = BOSdata.new()
htfadd433.settings                 := SettingsHTFadd433
htfadd433.candles                  := candlesadd433
htfadd433.bosdata                  := bosdataadd433
var CandleSet htfadd434                     = CandleSet.new()
var CandleSettings SettingsHTFadd434        = CandleSettings.new(htf='434',htfint=434,max_memory=3)
var Candle[] candlesadd434                  = array.new<Candle>(0)
var BOSdata bosdataadd434                   = BOSdata.new()
htfadd434.settings                 := SettingsHTFadd434
htfadd434.candles                  := candlesadd434
htfadd434.bosdata                  := bosdataadd434
var CandleSet htfadd435                     = CandleSet.new()
var CandleSettings SettingsHTFadd435        = CandleSettings.new(htf='435',htfint=435,max_memory=3)
var Candle[] candlesadd435                  = array.new<Candle>(0)
var BOSdata bosdataadd435                   = BOSdata.new()
htfadd435.settings                 := SettingsHTFadd435
htfadd435.candles                  := candlesadd435
htfadd435.bosdata                  := bosdataadd435
var CandleSet htfadd436                     = CandleSet.new()
var CandleSettings SettingsHTFadd436        = CandleSettings.new(htf='436',htfint=436,max_memory=3)
var Candle[] candlesadd436                  = array.new<Candle>(0)
var BOSdata bosdataadd436                   = BOSdata.new()
htfadd436.settings                 := SettingsHTFadd436
htfadd436.candles                  := candlesadd436
htfadd436.bosdata                  := bosdataadd436
var CandleSet htfadd437                     = CandleSet.new()
var CandleSettings SettingsHTFadd437        = CandleSettings.new(htf='437',htfint=437,max_memory=3)
var Candle[] candlesadd437                  = array.new<Candle>(0)
var BOSdata bosdataadd437                   = BOSdata.new()
htfadd437.settings                 := SettingsHTFadd437
htfadd437.candles                  := candlesadd437
htfadd437.bosdata                  := bosdataadd437
var CandleSet htfadd438                     = CandleSet.new()
var CandleSettings SettingsHTFadd438        = CandleSettings.new(htf='438',htfint=438,max_memory=3)
var Candle[] candlesadd438                  = array.new<Candle>(0)
var BOSdata bosdataadd438                   = BOSdata.new()
htfadd438.settings                 := SettingsHTFadd438
htfadd438.candles                  := candlesadd438
htfadd438.bosdata                  := bosdataadd438
var CandleSet htfadd439                     = CandleSet.new()
var CandleSettings SettingsHTFadd439        = CandleSettings.new(htf='439',htfint=439,max_memory=3)
var Candle[] candlesadd439                  = array.new<Candle>(0)
var BOSdata bosdataadd439                   = BOSdata.new()
htfadd439.settings                 := SettingsHTFadd439
htfadd439.candles                  := candlesadd439
htfadd439.bosdata                  := bosdataadd439
var CandleSet htfadd440                     = CandleSet.new()
var CandleSettings SettingsHTFadd440        = CandleSettings.new(htf='440',htfint=440,max_memory=3)
var Candle[] candlesadd440                  = array.new<Candle>(0)
var BOSdata bosdataadd440                   = BOSdata.new()
htfadd440.settings                 := SettingsHTFadd440
htfadd440.candles                  := candlesadd440
htfadd440.bosdata                  := bosdataadd440
var CandleSet htfadd441                     = CandleSet.new()
var CandleSettings SettingsHTFadd441        = CandleSettings.new(htf='441',htfint=441,max_memory=3)
var Candle[] candlesadd441                  = array.new<Candle>(0)
var BOSdata bosdataadd441                   = BOSdata.new()
htfadd441.settings                 := SettingsHTFadd441
htfadd441.candles                  := candlesadd441
htfadd441.bosdata                  := bosdataadd441
var CandleSet htfadd442                     = CandleSet.new()
var CandleSettings SettingsHTFadd442        = CandleSettings.new(htf='442',htfint=442,max_memory=3)
var Candle[] candlesadd442                  = array.new<Candle>(0)
var BOSdata bosdataadd442                   = BOSdata.new()
htfadd442.settings                 := SettingsHTFadd442
htfadd442.candles                  := candlesadd442
htfadd442.bosdata                  := bosdataadd442
var CandleSet htfadd443                     = CandleSet.new()
var CandleSettings SettingsHTFadd443        = CandleSettings.new(htf='443',htfint=443,max_memory=3)
var Candle[] candlesadd443                  = array.new<Candle>(0)
var BOSdata bosdataadd443                   = BOSdata.new()
htfadd443.settings                 := SettingsHTFadd443
htfadd443.candles                  := candlesadd443
htfadd443.bosdata                  := bosdataadd443
var CandleSet htfadd444                     = CandleSet.new()
var CandleSettings SettingsHTFadd444        = CandleSettings.new(htf='444',htfint=444,max_memory=3)
var Candle[] candlesadd444                  = array.new<Candle>(0)
var BOSdata bosdataadd444                   = BOSdata.new()
htfadd444.settings                 := SettingsHTFadd444
htfadd444.candles                  := candlesadd444
htfadd444.bosdata                  := bosdataadd444
var CandleSet htfadd445                     = CandleSet.new()
var CandleSettings SettingsHTFadd445        = CandleSettings.new(htf='445',htfint=445,max_memory=3)
var Candle[] candlesadd445                  = array.new<Candle>(0)
var BOSdata bosdataadd445                   = BOSdata.new()
htfadd445.settings                 := SettingsHTFadd445
htfadd445.candles                  := candlesadd445
htfadd445.bosdata                  := bosdataadd445
var CandleSet htfadd446                     = CandleSet.new()
var CandleSettings SettingsHTFadd446        = CandleSettings.new(htf='446',htfint=446,max_memory=3)
var Candle[] candlesadd446                  = array.new<Candle>(0)
var BOSdata bosdataadd446                   = BOSdata.new()
htfadd446.settings                 := SettingsHTFadd446
htfadd446.candles                  := candlesadd446
htfadd446.bosdata                  := bosdataadd446
var CandleSet htfadd447                     = CandleSet.new()
var CandleSettings SettingsHTFadd447        = CandleSettings.new(htf='447',htfint=447,max_memory=3)
var Candle[] candlesadd447                  = array.new<Candle>(0)
var BOSdata bosdataadd447                   = BOSdata.new()
htfadd447.settings                 := SettingsHTFadd447
htfadd447.candles                  := candlesadd447
htfadd447.bosdata                  := bosdataadd447
var CandleSet htfadd448                     = CandleSet.new()
var CandleSettings SettingsHTFadd448        = CandleSettings.new(htf='448',htfint=448,max_memory=3)
var Candle[] candlesadd448                  = array.new<Candle>(0)
var BOSdata bosdataadd448                   = BOSdata.new()
htfadd448.settings                 := SettingsHTFadd448
htfadd448.candles                  := candlesadd448
htfadd448.bosdata                  := bosdataadd448
var CandleSet htfadd449                     = CandleSet.new()
var CandleSettings SettingsHTFadd449        = CandleSettings.new(htf='449',htfint=449,max_memory=3)
var Candle[] candlesadd449                  = array.new<Candle>(0)
var BOSdata bosdataadd449                   = BOSdata.new()
htfadd449.settings                 := SettingsHTFadd449
htfadd449.candles                  := candlesadd449
htfadd449.bosdata                  := bosdataadd449
var CandleSet htfadd450                     = CandleSet.new()
var CandleSettings SettingsHTFadd450        = CandleSettings.new(htf='450',htfint=450,max_memory=3)
var Candle[] candlesadd450                  = array.new<Candle>(0)
var BOSdata bosdataadd450                   = BOSdata.new()
htfadd450.settings                 := SettingsHTFadd450
htfadd450.candles                  := candlesadd450
htfadd450.bosdata                  := bosdataadd450

htfadd360.Monitor().BOSJudge()
htfadd361.Monitor().BOSJudge()
htfadd362.Monitor().BOSJudge()
htfadd363.Monitor().BOSJudge()
htfadd364.Monitor().BOSJudge()
htfadd365.Monitor().BOSJudge()
htfadd366.Monitor().BOSJudge()
htfadd367.Monitor().BOSJudge()
htfadd368.Monitor().BOSJudge()
htfadd369.Monitor().BOSJudge()
htfadd370.Monitor().BOSJudge()
htfadd371.Monitor().BOSJudge()
htfadd372.Monitor().BOSJudge()
htfadd373.Monitor().BOSJudge()
htfadd374.Monitor().BOSJudge()
htfadd375.Monitor().BOSJudge()
htfadd376.Monitor().BOSJudge()
htfadd377.Monitor().BOSJudge()
htfadd378.Monitor().BOSJudge()
htfadd379.Monitor().BOSJudge()
htfadd380.Monitor().BOSJudge()
htfadd381.Monitor().BOSJudge()
htfadd382.Monitor().BOSJudge()
htfadd383.Monitor().BOSJudge()
htfadd384.Monitor().BOSJudge()
htfadd385.Monitor().BOSJudge()
htfadd386.Monitor().BOSJudge()
htfadd387.Monitor().BOSJudge()
htfadd388.Monitor().BOSJudge()
htfadd389.Monitor().BOSJudge()
htfadd390.Monitor().BOSJudge()
htfadd391.Monitor().BOSJudge()
htfadd392.Monitor().BOSJudge()
htfadd393.Monitor().BOSJudge()
htfadd394.Monitor().BOSJudge()
htfadd395.Monitor().BOSJudge()
htfadd396.Monitor().BOSJudge()
htfadd397.Monitor().BOSJudge()
htfadd398.Monitor().BOSJudge()
htfadd399.Monitor().BOSJudge()
htfadd400.Monitor().BOSJudge()
htfadd401.Monitor().BOSJudge()
htfadd402.Monitor().BOSJudge()
htfadd403.Monitor().BOSJudge()
htfadd404.Monitor().BOSJudge()
htfadd405.Monitor().BOSJudge()
htfadd406.Monitor().BOSJudge()
htfadd407.Monitor().BOSJudge()
htfadd408.Monitor().BOSJudge()
htfadd409.Monitor().BOSJudge()
htfadd410.Monitor().BOSJudge()
htfadd411.Monitor().BOSJudge()
htfadd412.Monitor().BOSJudge()
htfadd413.Monitor().BOSJudge()
htfadd414.Monitor().BOSJudge()
htfadd415.Monitor().BOSJudge()
htfadd416.Monitor().BOSJudge()
htfadd417.Monitor().BOSJudge()
htfadd418.Monitor().BOSJudge()
htfadd419.Monitor().BOSJudge()
htfadd420.Monitor().BOSJudge()
htfadd421.Monitor().BOSJudge()
htfadd422.Monitor().BOSJudge()
htfadd423.Monitor().BOSJudge()
htfadd424.Monitor().BOSJudge()
htfadd425.Monitor().BOSJudge()
htfadd426.Monitor().BOSJudge()
htfadd427.Monitor().BOSJudge()
htfadd428.Monitor().BOSJudge()
htfadd429.Monitor().BOSJudge()
htfadd430.Monitor().BOSJudge()
htfadd431.Monitor().BOSJudge()
htfadd432.Monitor().BOSJudge()
htfadd433.Monitor().BOSJudge()
htfadd434.Monitor().BOSJudge()
htfadd435.Monitor().BOSJudge()
htfadd436.Monitor().BOSJudge()
htfadd437.Monitor().BOSJudge()
htfadd438.Monitor().BOSJudge()
htfadd439.Monitor().BOSJudge()
htfadd440.Monitor().BOSJudge()
htfadd441.Monitor().BOSJudge()
htfadd442.Monitor().BOSJudge()
htfadd443.Monitor().BOSJudge()
htfadd444.Monitor().BOSJudge()
htfadd445.Monitor().BOSJudge()
htfadd446.Monitor().BOSJudge()
htfadd447.Monitor().BOSJudge()
htfadd448.Monitor().BOSJudge()
htfadd449.Monitor().BOSJudge()
htfadd450.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd360)
    LowestsbuSet(lowestsbu, htfadd360)
    HighestsbdSet(highestsbd, htfadd361)
    LowestsbuSet(lowestsbu, htfadd361)
    HighestsbdSet(highestsbd, htfadd362)
    LowestsbuSet(lowestsbu, htfadd362)
    HighestsbdSet(highestsbd, htfadd363)
    LowestsbuSet(lowestsbu, htfadd363)
    HighestsbdSet(highestsbd, htfadd364)
    LowestsbuSet(lowestsbu, htfadd364)
    HighestsbdSet(highestsbd, htfadd365)
    LowestsbuSet(lowestsbu, htfadd365)
    HighestsbdSet(highestsbd, htfadd366)
    LowestsbuSet(lowestsbu, htfadd366)
    HighestsbdSet(highestsbd, htfadd367)
    LowestsbuSet(lowestsbu, htfadd367)
    HighestsbdSet(highestsbd, htfadd368)
    LowestsbuSet(lowestsbu, htfadd368)
    HighestsbdSet(highestsbd, htfadd369)
    LowestsbuSet(lowestsbu, htfadd369)
    HighestsbdSet(highestsbd, htfadd370)
    LowestsbuSet(lowestsbu, htfadd370)
    HighestsbdSet(highestsbd, htfadd371)
    LowestsbuSet(lowestsbu, htfadd371)
    HighestsbdSet(highestsbd, htfadd372)
    LowestsbuSet(lowestsbu, htfadd372)
    HighestsbdSet(highestsbd, htfadd373)
    LowestsbuSet(lowestsbu, htfadd373)
    HighestsbdSet(highestsbd, htfadd374)
    LowestsbuSet(lowestsbu, htfadd374)
    HighestsbdSet(highestsbd, htfadd375)
    LowestsbuSet(lowestsbu, htfadd375)
    HighestsbdSet(highestsbd, htfadd376)
    LowestsbuSet(lowestsbu, htfadd376)
    HighestsbdSet(highestsbd, htfadd377)
    LowestsbuSet(lowestsbu, htfadd377)
    HighestsbdSet(highestsbd, htfadd378)
    LowestsbuSet(lowestsbu, htfadd378)
    HighestsbdSet(highestsbd, htfadd379)
    LowestsbuSet(lowestsbu, htfadd379)
    HighestsbdSet(highestsbd, htfadd380)
    LowestsbuSet(lowestsbu, htfadd380)
    HighestsbdSet(highestsbd, htfadd381)
    LowestsbuSet(lowestsbu, htfadd381)
    HighestsbdSet(highestsbd, htfadd382)
    LowestsbuSet(lowestsbu, htfadd382)
    HighestsbdSet(highestsbd, htfadd383)
    LowestsbuSet(lowestsbu, htfadd383)
    HighestsbdSet(highestsbd, htfadd384)
    LowestsbuSet(lowestsbu, htfadd384)
    HighestsbdSet(highestsbd, htfadd385)
    LowestsbuSet(lowestsbu, htfadd385)
    HighestsbdSet(highestsbd, htfadd386)
    LowestsbuSet(lowestsbu, htfadd386)
    HighestsbdSet(highestsbd, htfadd387)
    LowestsbuSet(lowestsbu, htfadd387)
    HighestsbdSet(highestsbd, htfadd388)
    LowestsbuSet(lowestsbu, htfadd388)
    HighestsbdSet(highestsbd, htfadd389)
    LowestsbuSet(lowestsbu, htfadd389)
    HighestsbdSet(highestsbd, htfadd390)
    LowestsbuSet(lowestsbu, htfadd390)
    HighestsbdSet(highestsbd, htfadd391)
    LowestsbuSet(lowestsbu, htfadd391)
    HighestsbdSet(highestsbd, htfadd392)
    LowestsbuSet(lowestsbu, htfadd392)
    HighestsbdSet(highestsbd, htfadd393)
    LowestsbuSet(lowestsbu, htfadd393)
    HighestsbdSet(highestsbd, htfadd394)
    LowestsbuSet(lowestsbu, htfadd394)
    HighestsbdSet(highestsbd, htfadd395)
    LowestsbuSet(lowestsbu, htfadd395)
    HighestsbdSet(highestsbd, htfadd396)
    LowestsbuSet(lowestsbu, htfadd396)
    HighestsbdSet(highestsbd, htfadd397)
    LowestsbuSet(lowestsbu, htfadd397)
    HighestsbdSet(highestsbd, htfadd398)
    LowestsbuSet(lowestsbu, htfadd398)
    HighestsbdSet(highestsbd, htfadd399)
    LowestsbuSet(lowestsbu, htfadd399)
    HighestsbdSet(highestsbd, htfadd400)
    LowestsbuSet(lowestsbu, htfadd400)
    HighestsbdSet(highestsbd, htfadd401)
    LowestsbuSet(lowestsbu, htfadd401)
    HighestsbdSet(highestsbd, htfadd402)
    LowestsbuSet(lowestsbu, htfadd402)
    HighestsbdSet(highestsbd, htfadd403)
    LowestsbuSet(lowestsbu, htfadd403)
    HighestsbdSet(highestsbd, htfadd404)
    LowestsbuSet(lowestsbu, htfadd404)
    HighestsbdSet(highestsbd, htfadd405)
    LowestsbuSet(lowestsbu, htfadd405)
    HighestsbdSet(highestsbd, htfadd406)
    LowestsbuSet(lowestsbu, htfadd406)
    HighestsbdSet(highestsbd, htfadd407)
    LowestsbuSet(lowestsbu, htfadd407)
    HighestsbdSet(highestsbd, htfadd408)
    LowestsbuSet(lowestsbu, htfadd408)
    HighestsbdSet(highestsbd, htfadd409)
    LowestsbuSet(lowestsbu, htfadd409)
    HighestsbdSet(highestsbd, htfadd410)
    LowestsbuSet(lowestsbu, htfadd410)
    HighestsbdSet(highestsbd, htfadd411)
    LowestsbuSet(lowestsbu, htfadd411)
    HighestsbdSet(highestsbd, htfadd412)
    LowestsbuSet(lowestsbu, htfadd412)
    HighestsbdSet(highestsbd, htfadd413)
    LowestsbuSet(lowestsbu, htfadd413)
    HighestsbdSet(highestsbd, htfadd414)
    LowestsbuSet(lowestsbu, htfadd414)
    HighestsbdSet(highestsbd, htfadd415)
    LowestsbuSet(lowestsbu, htfadd415)
    HighestsbdSet(highestsbd, htfadd416)
    LowestsbuSet(lowestsbu, htfadd416)
    HighestsbdSet(highestsbd, htfadd417)
    LowestsbuSet(lowestsbu, htfadd417)
    HighestsbdSet(highestsbd, htfadd418)
    LowestsbuSet(lowestsbu, htfadd418)
    HighestsbdSet(highestsbd, htfadd419)
    LowestsbuSet(lowestsbu, htfadd419)
    HighestsbdSet(highestsbd, htfadd420)
    LowestsbuSet(lowestsbu, htfadd420)
    HighestsbdSet(highestsbd, htfadd421)
    LowestsbuSet(lowestsbu, htfadd421)
    HighestsbdSet(highestsbd, htfadd422)
    LowestsbuSet(lowestsbu, htfadd422)
    HighestsbdSet(highestsbd, htfadd423)
    LowestsbuSet(lowestsbu, htfadd423)
    HighestsbdSet(highestsbd, htfadd424)
    LowestsbuSet(lowestsbu, htfadd424)
    HighestsbdSet(highestsbd, htfadd425)
    LowestsbuSet(lowestsbu, htfadd425)
    HighestsbdSet(highestsbd, htfadd426)
    LowestsbuSet(lowestsbu, htfadd426)
    HighestsbdSet(highestsbd, htfadd427)
    LowestsbuSet(lowestsbu, htfadd427)
    HighestsbdSet(highestsbd, htfadd428)
    LowestsbuSet(lowestsbu, htfadd428)
    HighestsbdSet(highestsbd, htfadd429)
    LowestsbuSet(lowestsbu, htfadd429)
    HighestsbdSet(highestsbd, htfadd430)
    LowestsbuSet(lowestsbu, htfadd430)
    HighestsbdSet(highestsbd, htfadd431)
    LowestsbuSet(lowestsbu, htfadd431)
    HighestsbdSet(highestsbd, htfadd432)
    LowestsbuSet(lowestsbu, htfadd432)
    HighestsbdSet(highestsbd, htfadd433)
    LowestsbuSet(lowestsbu, htfadd433)
    HighestsbdSet(highestsbd, htfadd434)
    LowestsbuSet(lowestsbu, htfadd434)
    HighestsbdSet(highestsbd, htfadd435)
    LowestsbuSet(lowestsbu, htfadd435)
    HighestsbdSet(highestsbd, htfadd436)
    LowestsbuSet(lowestsbu, htfadd436)
    HighestsbdSet(highestsbd, htfadd437)
    LowestsbuSet(lowestsbu, htfadd437)
    HighestsbdSet(highestsbd, htfadd438)
    LowestsbuSet(lowestsbu, htfadd438)
    HighestsbdSet(highestsbd, htfadd439)
    LowestsbuSet(lowestsbu, htfadd439)
    HighestsbdSet(highestsbd, htfadd440)
    LowestsbuSet(lowestsbu, htfadd440)
    HighestsbdSet(highestsbd, htfadd441)
    LowestsbuSet(lowestsbu, htfadd441)
    HighestsbdSet(highestsbd, htfadd442)
    LowestsbuSet(lowestsbu, htfadd442)
    HighestsbdSet(highestsbd, htfadd443)
    LowestsbuSet(lowestsbu, htfadd443)
    HighestsbdSet(highestsbd, htfadd444)
    LowestsbuSet(lowestsbu, htfadd444)
    HighestsbdSet(highestsbd, htfadd445)
    LowestsbuSet(lowestsbu, htfadd445)
    HighestsbdSet(highestsbd, htfadd446)
    LowestsbuSet(lowestsbu, htfadd446)
    HighestsbdSet(highestsbd, htfadd447)
    LowestsbuSet(lowestsbu, htfadd447)
    HighestsbdSet(highestsbd, htfadd448)
    LowestsbuSet(lowestsbu, htfadd448)
    HighestsbdSet(highestsbd, htfadd449)
    LowestsbuSet(lowestsbu, htfadd449)
    HighestsbdSet(highestsbd, htfadd450)
    LowestsbuSet(lowestsbu, htfadd450)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd360).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd361).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd362).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd363).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd364).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd365).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd366).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd367).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd368).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd369).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd370).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd371).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd372).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd373).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd374).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd375).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd376).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd377).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd378).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd379).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd380).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd381).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd382).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd383).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd384).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd385).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd386).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd387).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd388).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd389).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd390).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd391).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd392).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd393).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd394).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd395).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd396).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd397).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd398).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd399).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd400).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd401).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd402).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd403).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd404).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd405).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd406).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd407).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd408).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd409).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd410).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd411).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd412).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd413).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd414).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd415).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd416).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd417).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd418).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd419).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd420).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd421).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd422).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd423).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd424).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd425).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd426).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd427).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd428).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd429).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd430).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd431).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd432).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd433).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd434).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd435).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd436).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd437).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd438).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd439).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd440).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd441).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd442).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd443).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd444).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd445).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd446).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd447).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd448).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd449).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd450).Monitor_Est().BOSJudge()
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


