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
var CandleSet htfadd1350                     = CandleSet.new()
var CandleSettings SettingsHTFadd1350        = CandleSettings.new(htf='1350',htfint=1350,max_memory=3)
var Candle[] candlesadd1350                  = array.new<Candle>(0)
var BOSdata bosdataadd1350                   = BOSdata.new()
htfadd1350.settings                 := SettingsHTFadd1350
htfadd1350.candles                  := candlesadd1350
htfadd1350.bosdata                  := bosdataadd1350
var CandleSet htfadd1351                     = CandleSet.new()
var CandleSettings SettingsHTFadd1351        = CandleSettings.new(htf='1351',htfint=1351,max_memory=3)
var Candle[] candlesadd1351                  = array.new<Candle>(0)
var BOSdata bosdataadd1351                   = BOSdata.new()
htfadd1351.settings                 := SettingsHTFadd1351
htfadd1351.candles                  := candlesadd1351
htfadd1351.bosdata                  := bosdataadd1351
var CandleSet htfadd1352                     = CandleSet.new()
var CandleSettings SettingsHTFadd1352        = CandleSettings.new(htf='1352',htfint=1352,max_memory=3)
var Candle[] candlesadd1352                  = array.new<Candle>(0)
var BOSdata bosdataadd1352                   = BOSdata.new()
htfadd1352.settings                 := SettingsHTFadd1352
htfadd1352.candles                  := candlesadd1352
htfadd1352.bosdata                  := bosdataadd1352
var CandleSet htfadd1353                     = CandleSet.new()
var CandleSettings SettingsHTFadd1353        = CandleSettings.new(htf='1353',htfint=1353,max_memory=3)
var Candle[] candlesadd1353                  = array.new<Candle>(0)
var BOSdata bosdataadd1353                   = BOSdata.new()
htfadd1353.settings                 := SettingsHTFadd1353
htfadd1353.candles                  := candlesadd1353
htfadd1353.bosdata                  := bosdataadd1353
var CandleSet htfadd1354                     = CandleSet.new()
var CandleSettings SettingsHTFadd1354        = CandleSettings.new(htf='1354',htfint=1354,max_memory=3)
var Candle[] candlesadd1354                  = array.new<Candle>(0)
var BOSdata bosdataadd1354                   = BOSdata.new()
htfadd1354.settings                 := SettingsHTFadd1354
htfadd1354.candles                  := candlesadd1354
htfadd1354.bosdata                  := bosdataadd1354
var CandleSet htfadd1355                     = CandleSet.new()
var CandleSettings SettingsHTFadd1355        = CandleSettings.new(htf='1355',htfint=1355,max_memory=3)
var Candle[] candlesadd1355                  = array.new<Candle>(0)
var BOSdata bosdataadd1355                   = BOSdata.new()
htfadd1355.settings                 := SettingsHTFadd1355
htfadd1355.candles                  := candlesadd1355
htfadd1355.bosdata                  := bosdataadd1355
var CandleSet htfadd1356                     = CandleSet.new()
var CandleSettings SettingsHTFadd1356        = CandleSettings.new(htf='1356',htfint=1356,max_memory=3)
var Candle[] candlesadd1356                  = array.new<Candle>(0)
var BOSdata bosdataadd1356                   = BOSdata.new()
htfadd1356.settings                 := SettingsHTFadd1356
htfadd1356.candles                  := candlesadd1356
htfadd1356.bosdata                  := bosdataadd1356
var CandleSet htfadd1357                     = CandleSet.new()
var CandleSettings SettingsHTFadd1357        = CandleSettings.new(htf='1357',htfint=1357,max_memory=3)
var Candle[] candlesadd1357                  = array.new<Candle>(0)
var BOSdata bosdataadd1357                   = BOSdata.new()
htfadd1357.settings                 := SettingsHTFadd1357
htfadd1357.candles                  := candlesadd1357
htfadd1357.bosdata                  := bosdataadd1357
var CandleSet htfadd1358                     = CandleSet.new()
var CandleSettings SettingsHTFadd1358        = CandleSettings.new(htf='1358',htfint=1358,max_memory=3)
var Candle[] candlesadd1358                  = array.new<Candle>(0)
var BOSdata bosdataadd1358                   = BOSdata.new()
htfadd1358.settings                 := SettingsHTFadd1358
htfadd1358.candles                  := candlesadd1358
htfadd1358.bosdata                  := bosdataadd1358
var CandleSet htfadd1359                     = CandleSet.new()
var CandleSettings SettingsHTFadd1359        = CandleSettings.new(htf='1359',htfint=1359,max_memory=3)
var Candle[] candlesadd1359                  = array.new<Candle>(0)
var BOSdata bosdataadd1359                   = BOSdata.new()
htfadd1359.settings                 := SettingsHTFadd1359
htfadd1359.candles                  := candlesadd1359
htfadd1359.bosdata                  := bosdataadd1359
var CandleSet htfadd1360                     = CandleSet.new()
var CandleSettings SettingsHTFadd1360        = CandleSettings.new(htf='1360',htfint=1360,max_memory=3)
var Candle[] candlesadd1360                  = array.new<Candle>(0)
var BOSdata bosdataadd1360                   = BOSdata.new()
htfadd1360.settings                 := SettingsHTFadd1360
htfadd1360.candles                  := candlesadd1360
htfadd1360.bosdata                  := bosdataadd1360
var CandleSet htfadd1361                     = CandleSet.new()
var CandleSettings SettingsHTFadd1361        = CandleSettings.new(htf='1361',htfint=1361,max_memory=3)
var Candle[] candlesadd1361                  = array.new<Candle>(0)
var BOSdata bosdataadd1361                   = BOSdata.new()
htfadd1361.settings                 := SettingsHTFadd1361
htfadd1361.candles                  := candlesadd1361
htfadd1361.bosdata                  := bosdataadd1361
var CandleSet htfadd1362                     = CandleSet.new()
var CandleSettings SettingsHTFadd1362        = CandleSettings.new(htf='1362',htfint=1362,max_memory=3)
var Candle[] candlesadd1362                  = array.new<Candle>(0)
var BOSdata bosdataadd1362                   = BOSdata.new()
htfadd1362.settings                 := SettingsHTFadd1362
htfadd1362.candles                  := candlesadd1362
htfadd1362.bosdata                  := bosdataadd1362
var CandleSet htfadd1363                     = CandleSet.new()
var CandleSettings SettingsHTFadd1363        = CandleSettings.new(htf='1363',htfint=1363,max_memory=3)
var Candle[] candlesadd1363                  = array.new<Candle>(0)
var BOSdata bosdataadd1363                   = BOSdata.new()
htfadd1363.settings                 := SettingsHTFadd1363
htfadd1363.candles                  := candlesadd1363
htfadd1363.bosdata                  := bosdataadd1363
var CandleSet htfadd1364                     = CandleSet.new()
var CandleSettings SettingsHTFadd1364        = CandleSettings.new(htf='1364',htfint=1364,max_memory=3)
var Candle[] candlesadd1364                  = array.new<Candle>(0)
var BOSdata bosdataadd1364                   = BOSdata.new()
htfadd1364.settings                 := SettingsHTFadd1364
htfadd1364.candles                  := candlesadd1364
htfadd1364.bosdata                  := bosdataadd1364
var CandleSet htfadd1365                     = CandleSet.new()
var CandleSettings SettingsHTFadd1365        = CandleSettings.new(htf='1365',htfint=1365,max_memory=3)
var Candle[] candlesadd1365                  = array.new<Candle>(0)
var BOSdata bosdataadd1365                   = BOSdata.new()
htfadd1365.settings                 := SettingsHTFadd1365
htfadd1365.candles                  := candlesadd1365
htfadd1365.bosdata                  := bosdataadd1365
var CandleSet htfadd1366                     = CandleSet.new()
var CandleSettings SettingsHTFadd1366        = CandleSettings.new(htf='1366',htfint=1366,max_memory=3)
var Candle[] candlesadd1366                  = array.new<Candle>(0)
var BOSdata bosdataadd1366                   = BOSdata.new()
htfadd1366.settings                 := SettingsHTFadd1366
htfadd1366.candles                  := candlesadd1366
htfadd1366.bosdata                  := bosdataadd1366
var CandleSet htfadd1367                     = CandleSet.new()
var CandleSettings SettingsHTFadd1367        = CandleSettings.new(htf='1367',htfint=1367,max_memory=3)
var Candle[] candlesadd1367                  = array.new<Candle>(0)
var BOSdata bosdataadd1367                   = BOSdata.new()
htfadd1367.settings                 := SettingsHTFadd1367
htfadd1367.candles                  := candlesadd1367
htfadd1367.bosdata                  := bosdataadd1367
var CandleSet htfadd1368                     = CandleSet.new()
var CandleSettings SettingsHTFadd1368        = CandleSettings.new(htf='1368',htfint=1368,max_memory=3)
var Candle[] candlesadd1368                  = array.new<Candle>(0)
var BOSdata bosdataadd1368                   = BOSdata.new()
htfadd1368.settings                 := SettingsHTFadd1368
htfadd1368.candles                  := candlesadd1368
htfadd1368.bosdata                  := bosdataadd1368
var CandleSet htfadd1369                     = CandleSet.new()
var CandleSettings SettingsHTFadd1369        = CandleSettings.new(htf='1369',htfint=1369,max_memory=3)
var Candle[] candlesadd1369                  = array.new<Candle>(0)
var BOSdata bosdataadd1369                   = BOSdata.new()
htfadd1369.settings                 := SettingsHTFadd1369
htfadd1369.candles                  := candlesadd1369
htfadd1369.bosdata                  := bosdataadd1369
var CandleSet htfadd1370                     = CandleSet.new()
var CandleSettings SettingsHTFadd1370        = CandleSettings.new(htf='1370',htfint=1370,max_memory=3)
var Candle[] candlesadd1370                  = array.new<Candle>(0)
var BOSdata bosdataadd1370                   = BOSdata.new()
htfadd1370.settings                 := SettingsHTFadd1370
htfadd1370.candles                  := candlesadd1370
htfadd1370.bosdata                  := bosdataadd1370
var CandleSet htfadd1371                     = CandleSet.new()
var CandleSettings SettingsHTFadd1371        = CandleSettings.new(htf='1371',htfint=1371,max_memory=3)
var Candle[] candlesadd1371                  = array.new<Candle>(0)
var BOSdata bosdataadd1371                   = BOSdata.new()
htfadd1371.settings                 := SettingsHTFadd1371
htfadd1371.candles                  := candlesadd1371
htfadd1371.bosdata                  := bosdataadd1371
var CandleSet htfadd1372                     = CandleSet.new()
var CandleSettings SettingsHTFadd1372        = CandleSettings.new(htf='1372',htfint=1372,max_memory=3)
var Candle[] candlesadd1372                  = array.new<Candle>(0)
var BOSdata bosdataadd1372                   = BOSdata.new()
htfadd1372.settings                 := SettingsHTFadd1372
htfadd1372.candles                  := candlesadd1372
htfadd1372.bosdata                  := bosdataadd1372
var CandleSet htfadd1373                     = CandleSet.new()
var CandleSettings SettingsHTFadd1373        = CandleSettings.new(htf='1373',htfint=1373,max_memory=3)
var Candle[] candlesadd1373                  = array.new<Candle>(0)
var BOSdata bosdataadd1373                   = BOSdata.new()
htfadd1373.settings                 := SettingsHTFadd1373
htfadd1373.candles                  := candlesadd1373
htfadd1373.bosdata                  := bosdataadd1373
var CandleSet htfadd1374                     = CandleSet.new()
var CandleSettings SettingsHTFadd1374        = CandleSettings.new(htf='1374',htfint=1374,max_memory=3)
var Candle[] candlesadd1374                  = array.new<Candle>(0)
var BOSdata bosdataadd1374                   = BOSdata.new()
htfadd1374.settings                 := SettingsHTFadd1374
htfadd1374.candles                  := candlesadd1374
htfadd1374.bosdata                  := bosdataadd1374
var CandleSet htfadd1375                     = CandleSet.new()
var CandleSettings SettingsHTFadd1375        = CandleSettings.new(htf='1375',htfint=1375,max_memory=3)
var Candle[] candlesadd1375                  = array.new<Candle>(0)
var BOSdata bosdataadd1375                   = BOSdata.new()
htfadd1375.settings                 := SettingsHTFadd1375
htfadd1375.candles                  := candlesadd1375
htfadd1375.bosdata                  := bosdataadd1375
var CandleSet htfadd1376                     = CandleSet.new()
var CandleSettings SettingsHTFadd1376        = CandleSettings.new(htf='1376',htfint=1376,max_memory=3)
var Candle[] candlesadd1376                  = array.new<Candle>(0)
var BOSdata bosdataadd1376                   = BOSdata.new()
htfadd1376.settings                 := SettingsHTFadd1376
htfadd1376.candles                  := candlesadd1376
htfadd1376.bosdata                  := bosdataadd1376
var CandleSet htfadd1377                     = CandleSet.new()
var CandleSettings SettingsHTFadd1377        = CandleSettings.new(htf='1377',htfint=1377,max_memory=3)
var Candle[] candlesadd1377                  = array.new<Candle>(0)
var BOSdata bosdataadd1377                   = BOSdata.new()
htfadd1377.settings                 := SettingsHTFadd1377
htfadd1377.candles                  := candlesadd1377
htfadd1377.bosdata                  := bosdataadd1377
var CandleSet htfadd1378                     = CandleSet.new()
var CandleSettings SettingsHTFadd1378        = CandleSettings.new(htf='1378',htfint=1378,max_memory=3)
var Candle[] candlesadd1378                  = array.new<Candle>(0)
var BOSdata bosdataadd1378                   = BOSdata.new()
htfadd1378.settings                 := SettingsHTFadd1378
htfadd1378.candles                  := candlesadd1378
htfadd1378.bosdata                  := bosdataadd1378
var CandleSet htfadd1379                     = CandleSet.new()
var CandleSettings SettingsHTFadd1379        = CandleSettings.new(htf='1379',htfint=1379,max_memory=3)
var Candle[] candlesadd1379                  = array.new<Candle>(0)
var BOSdata bosdataadd1379                   = BOSdata.new()
htfadd1379.settings                 := SettingsHTFadd1379
htfadd1379.candles                  := candlesadd1379
htfadd1379.bosdata                  := bosdataadd1379
var CandleSet htfadd1380                     = CandleSet.new()
var CandleSettings SettingsHTFadd1380        = CandleSettings.new(htf='1380',htfint=1380,max_memory=3)
var Candle[] candlesadd1380                  = array.new<Candle>(0)
var BOSdata bosdataadd1380                   = BOSdata.new()
htfadd1380.settings                 := SettingsHTFadd1380
htfadd1380.candles                  := candlesadd1380
htfadd1380.bosdata                  := bosdataadd1380
var CandleSet htfadd1381                     = CandleSet.new()
var CandleSettings SettingsHTFadd1381        = CandleSettings.new(htf='1381',htfint=1381,max_memory=3)
var Candle[] candlesadd1381                  = array.new<Candle>(0)
var BOSdata bosdataadd1381                   = BOSdata.new()
htfadd1381.settings                 := SettingsHTFadd1381
htfadd1381.candles                  := candlesadd1381
htfadd1381.bosdata                  := bosdataadd1381
var CandleSet htfadd1382                     = CandleSet.new()
var CandleSettings SettingsHTFadd1382        = CandleSettings.new(htf='1382',htfint=1382,max_memory=3)
var Candle[] candlesadd1382                  = array.new<Candle>(0)
var BOSdata bosdataadd1382                   = BOSdata.new()
htfadd1382.settings                 := SettingsHTFadd1382
htfadd1382.candles                  := candlesadd1382
htfadd1382.bosdata                  := bosdataadd1382
var CandleSet htfadd1383                     = CandleSet.new()
var CandleSettings SettingsHTFadd1383        = CandleSettings.new(htf='1383',htfint=1383,max_memory=3)
var Candle[] candlesadd1383                  = array.new<Candle>(0)
var BOSdata bosdataadd1383                   = BOSdata.new()
htfadd1383.settings                 := SettingsHTFadd1383
htfadd1383.candles                  := candlesadd1383
htfadd1383.bosdata                  := bosdataadd1383
var CandleSet htfadd1384                     = CandleSet.new()
var CandleSettings SettingsHTFadd1384        = CandleSettings.new(htf='1384',htfint=1384,max_memory=3)
var Candle[] candlesadd1384                  = array.new<Candle>(0)
var BOSdata bosdataadd1384                   = BOSdata.new()
htfadd1384.settings                 := SettingsHTFadd1384
htfadd1384.candles                  := candlesadd1384
htfadd1384.bosdata                  := bosdataadd1384
var CandleSet htfadd1385                     = CandleSet.new()
var CandleSettings SettingsHTFadd1385        = CandleSettings.new(htf='1385',htfint=1385,max_memory=3)
var Candle[] candlesadd1385                  = array.new<Candle>(0)
var BOSdata bosdataadd1385                   = BOSdata.new()
htfadd1385.settings                 := SettingsHTFadd1385
htfadd1385.candles                  := candlesadd1385
htfadd1385.bosdata                  := bosdataadd1385
var CandleSet htfadd1386                     = CandleSet.new()
var CandleSettings SettingsHTFadd1386        = CandleSettings.new(htf='1386',htfint=1386,max_memory=3)
var Candle[] candlesadd1386                  = array.new<Candle>(0)
var BOSdata bosdataadd1386                   = BOSdata.new()
htfadd1386.settings                 := SettingsHTFadd1386
htfadd1386.candles                  := candlesadd1386
htfadd1386.bosdata                  := bosdataadd1386
var CandleSet htfadd1387                     = CandleSet.new()
var CandleSettings SettingsHTFadd1387        = CandleSettings.new(htf='1387',htfint=1387,max_memory=3)
var Candle[] candlesadd1387                  = array.new<Candle>(0)
var BOSdata bosdataadd1387                   = BOSdata.new()
htfadd1387.settings                 := SettingsHTFadd1387
htfadd1387.candles                  := candlesadd1387
htfadd1387.bosdata                  := bosdataadd1387
var CandleSet htfadd1388                     = CandleSet.new()
var CandleSettings SettingsHTFadd1388        = CandleSettings.new(htf='1388',htfint=1388,max_memory=3)
var Candle[] candlesadd1388                  = array.new<Candle>(0)
var BOSdata bosdataadd1388                   = BOSdata.new()
htfadd1388.settings                 := SettingsHTFadd1388
htfadd1388.candles                  := candlesadd1388
htfadd1388.bosdata                  := bosdataadd1388
var CandleSet htfadd1389                     = CandleSet.new()
var CandleSettings SettingsHTFadd1389        = CandleSettings.new(htf='1389',htfint=1389,max_memory=3)
var Candle[] candlesadd1389                  = array.new<Candle>(0)
var BOSdata bosdataadd1389                   = BOSdata.new()
htfadd1389.settings                 := SettingsHTFadd1389
htfadd1389.candles                  := candlesadd1389
htfadd1389.bosdata                  := bosdataadd1389
var CandleSet htfadd1390                     = CandleSet.new()
var CandleSettings SettingsHTFadd1390        = CandleSettings.new(htf='1390',htfint=1390,max_memory=3)
var Candle[] candlesadd1390                  = array.new<Candle>(0)
var BOSdata bosdataadd1390                   = BOSdata.new()
htfadd1390.settings                 := SettingsHTFadd1390
htfadd1390.candles                  := candlesadd1390
htfadd1390.bosdata                  := bosdataadd1390
var CandleSet htfadd1391                     = CandleSet.new()
var CandleSettings SettingsHTFadd1391        = CandleSettings.new(htf='1391',htfint=1391,max_memory=3)
var Candle[] candlesadd1391                  = array.new<Candle>(0)
var BOSdata bosdataadd1391                   = BOSdata.new()
htfadd1391.settings                 := SettingsHTFadd1391
htfadd1391.candles                  := candlesadd1391
htfadd1391.bosdata                  := bosdataadd1391
var CandleSet htfadd1392                     = CandleSet.new()
var CandleSettings SettingsHTFadd1392        = CandleSettings.new(htf='1392',htfint=1392,max_memory=3)
var Candle[] candlesadd1392                  = array.new<Candle>(0)
var BOSdata bosdataadd1392                   = BOSdata.new()
htfadd1392.settings                 := SettingsHTFadd1392
htfadd1392.candles                  := candlesadd1392
htfadd1392.bosdata                  := bosdataadd1392
var CandleSet htfadd1393                     = CandleSet.new()
var CandleSettings SettingsHTFadd1393        = CandleSettings.new(htf='1393',htfint=1393,max_memory=3)
var Candle[] candlesadd1393                  = array.new<Candle>(0)
var BOSdata bosdataadd1393                   = BOSdata.new()
htfadd1393.settings                 := SettingsHTFadd1393
htfadd1393.candles                  := candlesadd1393
htfadd1393.bosdata                  := bosdataadd1393
var CandleSet htfadd1394                     = CandleSet.new()
var CandleSettings SettingsHTFadd1394        = CandleSettings.new(htf='1394',htfint=1394,max_memory=3)
var Candle[] candlesadd1394                  = array.new<Candle>(0)
var BOSdata bosdataadd1394                   = BOSdata.new()
htfadd1394.settings                 := SettingsHTFadd1394
htfadd1394.candles                  := candlesadd1394
htfadd1394.bosdata                  := bosdataadd1394
var CandleSet htfadd1395                     = CandleSet.new()
var CandleSettings SettingsHTFadd1395        = CandleSettings.new(htf='1395',htfint=1395,max_memory=3)
var Candle[] candlesadd1395                  = array.new<Candle>(0)
var BOSdata bosdataadd1395                   = BOSdata.new()
htfadd1395.settings                 := SettingsHTFadd1395
htfadd1395.candles                  := candlesadd1395
htfadd1395.bosdata                  := bosdataadd1395
var CandleSet htfadd1396                     = CandleSet.new()
var CandleSettings SettingsHTFadd1396        = CandleSettings.new(htf='1396',htfint=1396,max_memory=3)
var Candle[] candlesadd1396                  = array.new<Candle>(0)
var BOSdata bosdataadd1396                   = BOSdata.new()
htfadd1396.settings                 := SettingsHTFadd1396
htfadd1396.candles                  := candlesadd1396
htfadd1396.bosdata                  := bosdataadd1396
var CandleSet htfadd1397                     = CandleSet.new()
var CandleSettings SettingsHTFadd1397        = CandleSettings.new(htf='1397',htfint=1397,max_memory=3)
var Candle[] candlesadd1397                  = array.new<Candle>(0)
var BOSdata bosdataadd1397                   = BOSdata.new()
htfadd1397.settings                 := SettingsHTFadd1397
htfadd1397.candles                  := candlesadd1397
htfadd1397.bosdata                  := bosdataadd1397
var CandleSet htfadd1398                     = CandleSet.new()
var CandleSettings SettingsHTFadd1398        = CandleSettings.new(htf='1398',htfint=1398,max_memory=3)
var Candle[] candlesadd1398                  = array.new<Candle>(0)
var BOSdata bosdataadd1398                   = BOSdata.new()
htfadd1398.settings                 := SettingsHTFadd1398
htfadd1398.candles                  := candlesadd1398
htfadd1398.bosdata                  := bosdataadd1398
var CandleSet htfadd1399                     = CandleSet.new()
var CandleSettings SettingsHTFadd1399        = CandleSettings.new(htf='1399',htfint=1399,max_memory=3)
var Candle[] candlesadd1399                  = array.new<Candle>(0)
var BOSdata bosdataadd1399                   = BOSdata.new()
htfadd1399.settings                 := SettingsHTFadd1399
htfadd1399.candles                  := candlesadd1399
htfadd1399.bosdata                  := bosdataadd1399
var CandleSet htfadd1400                     = CandleSet.new()
var CandleSettings SettingsHTFadd1400        = CandleSettings.new(htf='1400',htfint=1400,max_memory=3)
var Candle[] candlesadd1400                  = array.new<Candle>(0)
var BOSdata bosdataadd1400                   = BOSdata.new()
htfadd1400.settings                 := SettingsHTFadd1400
htfadd1400.candles                  := candlesadd1400
htfadd1400.bosdata                  := bosdataadd1400
var CandleSet htfadd1401                     = CandleSet.new()
var CandleSettings SettingsHTFadd1401        = CandleSettings.new(htf='1401',htfint=1401,max_memory=3)
var Candle[] candlesadd1401                  = array.new<Candle>(0)
var BOSdata bosdataadd1401                   = BOSdata.new()
htfadd1401.settings                 := SettingsHTFadd1401
htfadd1401.candles                  := candlesadd1401
htfadd1401.bosdata                  := bosdataadd1401
var CandleSet htfadd1402                     = CandleSet.new()
var CandleSettings SettingsHTFadd1402        = CandleSettings.new(htf='1402',htfint=1402,max_memory=3)
var Candle[] candlesadd1402                  = array.new<Candle>(0)
var BOSdata bosdataadd1402                   = BOSdata.new()
htfadd1402.settings                 := SettingsHTFadd1402
htfadd1402.candles                  := candlesadd1402
htfadd1402.bosdata                  := bosdataadd1402
var CandleSet htfadd1403                     = CandleSet.new()
var CandleSettings SettingsHTFadd1403        = CandleSettings.new(htf='1403',htfint=1403,max_memory=3)
var Candle[] candlesadd1403                  = array.new<Candle>(0)
var BOSdata bosdataadd1403                   = BOSdata.new()
htfadd1403.settings                 := SettingsHTFadd1403
htfadd1403.candles                  := candlesadd1403
htfadd1403.bosdata                  := bosdataadd1403
var CandleSet htfadd1404                     = CandleSet.new()
var CandleSettings SettingsHTFadd1404        = CandleSettings.new(htf='1404',htfint=1404,max_memory=3)
var Candle[] candlesadd1404                  = array.new<Candle>(0)
var BOSdata bosdataadd1404                   = BOSdata.new()
htfadd1404.settings                 := SettingsHTFadd1404
htfadd1404.candles                  := candlesadd1404
htfadd1404.bosdata                  := bosdataadd1404
var CandleSet htfadd1405                     = CandleSet.new()
var CandleSettings SettingsHTFadd1405        = CandleSettings.new(htf='1405',htfint=1405,max_memory=3)
var Candle[] candlesadd1405                  = array.new<Candle>(0)
var BOSdata bosdataadd1405                   = BOSdata.new()
htfadd1405.settings                 := SettingsHTFadd1405
htfadd1405.candles                  := candlesadd1405
htfadd1405.bosdata                  := bosdataadd1405
var CandleSet htfadd1406                     = CandleSet.new()
var CandleSettings SettingsHTFadd1406        = CandleSettings.new(htf='1406',htfint=1406,max_memory=3)
var Candle[] candlesadd1406                  = array.new<Candle>(0)
var BOSdata bosdataadd1406                   = BOSdata.new()
htfadd1406.settings                 := SettingsHTFadd1406
htfadd1406.candles                  := candlesadd1406
htfadd1406.bosdata                  := bosdataadd1406
var CandleSet htfadd1407                     = CandleSet.new()
var CandleSettings SettingsHTFadd1407        = CandleSettings.new(htf='1407',htfint=1407,max_memory=3)
var Candle[] candlesadd1407                  = array.new<Candle>(0)
var BOSdata bosdataadd1407                   = BOSdata.new()
htfadd1407.settings                 := SettingsHTFadd1407
htfadd1407.candles                  := candlesadd1407
htfadd1407.bosdata                  := bosdataadd1407
var CandleSet htfadd1408                     = CandleSet.new()
var CandleSettings SettingsHTFadd1408        = CandleSettings.new(htf='1408',htfint=1408,max_memory=3)
var Candle[] candlesadd1408                  = array.new<Candle>(0)
var BOSdata bosdataadd1408                   = BOSdata.new()
htfadd1408.settings                 := SettingsHTFadd1408
htfadd1408.candles                  := candlesadd1408
htfadd1408.bosdata                  := bosdataadd1408
var CandleSet htfadd1409                     = CandleSet.new()
var CandleSettings SettingsHTFadd1409        = CandleSettings.new(htf='1409',htfint=1409,max_memory=3)
var Candle[] candlesadd1409                  = array.new<Candle>(0)
var BOSdata bosdataadd1409                   = BOSdata.new()
htfadd1409.settings                 := SettingsHTFadd1409
htfadd1409.candles                  := candlesadd1409
htfadd1409.bosdata                  := bosdataadd1409
var CandleSet htfadd1410                     = CandleSet.new()
var CandleSettings SettingsHTFadd1410        = CandleSettings.new(htf='1410',htfint=1410,max_memory=3)
var Candle[] candlesadd1410                  = array.new<Candle>(0)
var BOSdata bosdataadd1410                   = BOSdata.new()
htfadd1410.settings                 := SettingsHTFadd1410
htfadd1410.candles                  := candlesadd1410
htfadd1410.bosdata                  := bosdataadd1410
var CandleSet htfadd1411                     = CandleSet.new()
var CandleSettings SettingsHTFadd1411        = CandleSettings.new(htf='1411',htfint=1411,max_memory=3)
var Candle[] candlesadd1411                  = array.new<Candle>(0)
var BOSdata bosdataadd1411                   = BOSdata.new()
htfadd1411.settings                 := SettingsHTFadd1411
htfadd1411.candles                  := candlesadd1411
htfadd1411.bosdata                  := bosdataadd1411
var CandleSet htfadd1412                     = CandleSet.new()
var CandleSettings SettingsHTFadd1412        = CandleSettings.new(htf='1412',htfint=1412,max_memory=3)
var Candle[] candlesadd1412                  = array.new<Candle>(0)
var BOSdata bosdataadd1412                   = BOSdata.new()
htfadd1412.settings                 := SettingsHTFadd1412
htfadd1412.candles                  := candlesadd1412
htfadd1412.bosdata                  := bosdataadd1412
var CandleSet htfadd1413                     = CandleSet.new()
var CandleSettings SettingsHTFadd1413        = CandleSettings.new(htf='1413',htfint=1413,max_memory=3)
var Candle[] candlesadd1413                  = array.new<Candle>(0)
var BOSdata bosdataadd1413                   = BOSdata.new()
htfadd1413.settings                 := SettingsHTFadd1413
htfadd1413.candles                  := candlesadd1413
htfadd1413.bosdata                  := bosdataadd1413
var CandleSet htfadd1414                     = CandleSet.new()
var CandleSettings SettingsHTFadd1414        = CandleSettings.new(htf='1414',htfint=1414,max_memory=3)
var Candle[] candlesadd1414                  = array.new<Candle>(0)
var BOSdata bosdataadd1414                   = BOSdata.new()
htfadd1414.settings                 := SettingsHTFadd1414
htfadd1414.candles                  := candlesadd1414
htfadd1414.bosdata                  := bosdataadd1414
var CandleSet htfadd1415                     = CandleSet.new()
var CandleSettings SettingsHTFadd1415        = CandleSettings.new(htf='1415',htfint=1415,max_memory=3)
var Candle[] candlesadd1415                  = array.new<Candle>(0)
var BOSdata bosdataadd1415                   = BOSdata.new()
htfadd1415.settings                 := SettingsHTFadd1415
htfadd1415.candles                  := candlesadd1415
htfadd1415.bosdata                  := bosdataadd1415
var CandleSet htfadd1416                     = CandleSet.new()
var CandleSettings SettingsHTFadd1416        = CandleSettings.new(htf='1416',htfint=1416,max_memory=3)
var Candle[] candlesadd1416                  = array.new<Candle>(0)
var BOSdata bosdataadd1416                   = BOSdata.new()
htfadd1416.settings                 := SettingsHTFadd1416
htfadd1416.candles                  := candlesadd1416
htfadd1416.bosdata                  := bosdataadd1416
var CandleSet htfadd1417                     = CandleSet.new()
var CandleSettings SettingsHTFadd1417        = CandleSettings.new(htf='1417',htfint=1417,max_memory=3)
var Candle[] candlesadd1417                  = array.new<Candle>(0)
var BOSdata bosdataadd1417                   = BOSdata.new()
htfadd1417.settings                 := SettingsHTFadd1417
htfadd1417.candles                  := candlesadd1417
htfadd1417.bosdata                  := bosdataadd1417
var CandleSet htfadd1418                     = CandleSet.new()
var CandleSettings SettingsHTFadd1418        = CandleSettings.new(htf='1418',htfint=1418,max_memory=3)
var Candle[] candlesadd1418                  = array.new<Candle>(0)
var BOSdata bosdataadd1418                   = BOSdata.new()
htfadd1418.settings                 := SettingsHTFadd1418
htfadd1418.candles                  := candlesadd1418
htfadd1418.bosdata                  := bosdataadd1418
var CandleSet htfadd1419                     = CandleSet.new()
var CandleSettings SettingsHTFadd1419        = CandleSettings.new(htf='1419',htfint=1419,max_memory=3)
var Candle[] candlesadd1419                  = array.new<Candle>(0)
var BOSdata bosdataadd1419                   = BOSdata.new()
htfadd1419.settings                 := SettingsHTFadd1419
htfadd1419.candles                  := candlesadd1419
htfadd1419.bosdata                  := bosdataadd1419
var CandleSet htfadd1420                     = CandleSet.new()
var CandleSettings SettingsHTFadd1420        = CandleSettings.new(htf='1420',htfint=1420,max_memory=3)
var Candle[] candlesadd1420                  = array.new<Candle>(0)
var BOSdata bosdataadd1420                   = BOSdata.new()
htfadd1420.settings                 := SettingsHTFadd1420
htfadd1420.candles                  := candlesadd1420
htfadd1420.bosdata                  := bosdataadd1420
var CandleSet htfadd1421                     = CandleSet.new()
var CandleSettings SettingsHTFadd1421        = CandleSettings.new(htf='1421',htfint=1421,max_memory=3)
var Candle[] candlesadd1421                  = array.new<Candle>(0)
var BOSdata bosdataadd1421                   = BOSdata.new()
htfadd1421.settings                 := SettingsHTFadd1421
htfadd1421.candles                  := candlesadd1421
htfadd1421.bosdata                  := bosdataadd1421
var CandleSet htfadd1422                     = CandleSet.new()
var CandleSettings SettingsHTFadd1422        = CandleSettings.new(htf='1422',htfint=1422,max_memory=3)
var Candle[] candlesadd1422                  = array.new<Candle>(0)
var BOSdata bosdataadd1422                   = BOSdata.new()
htfadd1422.settings                 := SettingsHTFadd1422
htfadd1422.candles                  := candlesadd1422
htfadd1422.bosdata                  := bosdataadd1422
var CandleSet htfadd1423                     = CandleSet.new()
var CandleSettings SettingsHTFadd1423        = CandleSettings.new(htf='1423',htfint=1423,max_memory=3)
var Candle[] candlesadd1423                  = array.new<Candle>(0)
var BOSdata bosdataadd1423                   = BOSdata.new()
htfadd1423.settings                 := SettingsHTFadd1423
htfadd1423.candles                  := candlesadd1423
htfadd1423.bosdata                  := bosdataadd1423
var CandleSet htfadd1424                     = CandleSet.new()
var CandleSettings SettingsHTFadd1424        = CandleSettings.new(htf='1424',htfint=1424,max_memory=3)
var Candle[] candlesadd1424                  = array.new<Candle>(0)
var BOSdata bosdataadd1424                   = BOSdata.new()
htfadd1424.settings                 := SettingsHTFadd1424
htfadd1424.candles                  := candlesadd1424
htfadd1424.bosdata                  := bosdataadd1424
var CandleSet htfadd1425                     = CandleSet.new()
var CandleSettings SettingsHTFadd1425        = CandleSettings.new(htf='1425',htfint=1425,max_memory=3)
var Candle[] candlesadd1425                  = array.new<Candle>(0)
var BOSdata bosdataadd1425                   = BOSdata.new()
htfadd1425.settings                 := SettingsHTFadd1425
htfadd1425.candles                  := candlesadd1425
htfadd1425.bosdata                  := bosdataadd1425
var CandleSet htfadd1426                     = CandleSet.new()
var CandleSettings SettingsHTFadd1426        = CandleSettings.new(htf='1426',htfint=1426,max_memory=3)
var Candle[] candlesadd1426                  = array.new<Candle>(0)
var BOSdata bosdataadd1426                   = BOSdata.new()
htfadd1426.settings                 := SettingsHTFadd1426
htfadd1426.candles                  := candlesadd1426
htfadd1426.bosdata                  := bosdataadd1426
var CandleSet htfadd1427                     = CandleSet.new()
var CandleSettings SettingsHTFadd1427        = CandleSettings.new(htf='1427',htfint=1427,max_memory=3)
var Candle[] candlesadd1427                  = array.new<Candle>(0)
var BOSdata bosdataadd1427                   = BOSdata.new()
htfadd1427.settings                 := SettingsHTFadd1427
htfadd1427.candles                  := candlesadd1427
htfadd1427.bosdata                  := bosdataadd1427
var CandleSet htfadd1428                     = CandleSet.new()
var CandleSettings SettingsHTFadd1428        = CandleSettings.new(htf='1428',htfint=1428,max_memory=3)
var Candle[] candlesadd1428                  = array.new<Candle>(0)
var BOSdata bosdataadd1428                   = BOSdata.new()
htfadd1428.settings                 := SettingsHTFadd1428
htfadd1428.candles                  := candlesadd1428
htfadd1428.bosdata                  := bosdataadd1428
var CandleSet htfadd1429                     = CandleSet.new()
var CandleSettings SettingsHTFadd1429        = CandleSettings.new(htf='1429',htfint=1429,max_memory=3)
var Candle[] candlesadd1429                  = array.new<Candle>(0)
var BOSdata bosdataadd1429                   = BOSdata.new()
htfadd1429.settings                 := SettingsHTFadd1429
htfadd1429.candles                  := candlesadd1429
htfadd1429.bosdata                  := bosdataadd1429
var CandleSet htfadd1430                     = CandleSet.new()
var CandleSettings SettingsHTFadd1430        = CandleSettings.new(htf='1430',htfint=1430,max_memory=3)
var Candle[] candlesadd1430                  = array.new<Candle>(0)
var BOSdata bosdataadd1430                   = BOSdata.new()
htfadd1430.settings                 := SettingsHTFadd1430
htfadd1430.candles                  := candlesadd1430
htfadd1430.bosdata                  := bosdataadd1430
var CandleSet htfadd1431                     = CandleSet.new()
var CandleSettings SettingsHTFadd1431        = CandleSettings.new(htf='1431',htfint=1431,max_memory=3)
var Candle[] candlesadd1431                  = array.new<Candle>(0)
var BOSdata bosdataadd1431                   = BOSdata.new()
htfadd1431.settings                 := SettingsHTFadd1431
htfadd1431.candles                  := candlesadd1431
htfadd1431.bosdata                  := bosdataadd1431
var CandleSet htfadd1432                     = CandleSet.new()
var CandleSettings SettingsHTFadd1432        = CandleSettings.new(htf='1432',htfint=1432,max_memory=3)
var Candle[] candlesadd1432                  = array.new<Candle>(0)
var BOSdata bosdataadd1432                   = BOSdata.new()
htfadd1432.settings                 := SettingsHTFadd1432
htfadd1432.candles                  := candlesadd1432
htfadd1432.bosdata                  := bosdataadd1432
var CandleSet htfadd1433                     = CandleSet.new()
var CandleSettings SettingsHTFadd1433        = CandleSettings.new(htf='1433',htfint=1433,max_memory=3)
var Candle[] candlesadd1433                  = array.new<Candle>(0)
var BOSdata bosdataadd1433                   = BOSdata.new()
htfadd1433.settings                 := SettingsHTFadd1433
htfadd1433.candles                  := candlesadd1433
htfadd1433.bosdata                  := bosdataadd1433
var CandleSet htfadd1434                     = CandleSet.new()
var CandleSettings SettingsHTFadd1434        = CandleSettings.new(htf='1434',htfint=1434,max_memory=3)
var Candle[] candlesadd1434                  = array.new<Candle>(0)
var BOSdata bosdataadd1434                   = BOSdata.new()
htfadd1434.settings                 := SettingsHTFadd1434
htfadd1434.candles                  := candlesadd1434
htfadd1434.bosdata                  := bosdataadd1434
var CandleSet htfadd1435                     = CandleSet.new()
var CandleSettings SettingsHTFadd1435        = CandleSettings.new(htf='1435',htfint=1435,max_memory=3)
var Candle[] candlesadd1435                  = array.new<Candle>(0)
var BOSdata bosdataadd1435                   = BOSdata.new()
htfadd1435.settings                 := SettingsHTFadd1435
htfadd1435.candles                  := candlesadd1435
htfadd1435.bosdata                  := bosdataadd1435
var CandleSet htfadd1436                     = CandleSet.new()
var CandleSettings SettingsHTFadd1436        = CandleSettings.new(htf='1436',htfint=1436,max_memory=3)
var Candle[] candlesadd1436                  = array.new<Candle>(0)
var BOSdata bosdataadd1436                   = BOSdata.new()
htfadd1436.settings                 := SettingsHTFadd1436
htfadd1436.candles                  := candlesadd1436
htfadd1436.bosdata                  := bosdataadd1436
var CandleSet htfadd1437                     = CandleSet.new()
var CandleSettings SettingsHTFadd1437        = CandleSettings.new(htf='1437',htfint=1437,max_memory=3)
var Candle[] candlesadd1437                  = array.new<Candle>(0)
var BOSdata bosdataadd1437                   = BOSdata.new()
htfadd1437.settings                 := SettingsHTFadd1437
htfadd1437.candles                  := candlesadd1437
htfadd1437.bosdata                  := bosdataadd1437
var CandleSet htfadd1438                     = CandleSet.new()
var CandleSettings SettingsHTFadd1438        = CandleSettings.new(htf='1438',htfint=1438,max_memory=3)
var Candle[] candlesadd1438                  = array.new<Candle>(0)
var BOSdata bosdataadd1438                   = BOSdata.new()
htfadd1438.settings                 := SettingsHTFadd1438
htfadd1438.candles                  := candlesadd1438
htfadd1438.bosdata                  := bosdataadd1438
var CandleSet htfadd1439                     = CandleSet.new()
var CandleSettings SettingsHTFadd1439        = CandleSettings.new(htf='1439',htfint=1439,max_memory=3)
var Candle[] candlesadd1439                  = array.new<Candle>(0)
var BOSdata bosdataadd1439                   = BOSdata.new()
htfadd1439.settings                 := SettingsHTFadd1439
htfadd1439.candles                  := candlesadd1439
htfadd1439.bosdata                  := bosdataadd1439
var CandleSet htfadd1440                     = CandleSet.new()
var CandleSettings SettingsHTFadd1440        = CandleSettings.new(htf='1440',htfint=1440,max_memory=3)
var Candle[] candlesadd1440                  = array.new<Candle>(0)
var BOSdata bosdataadd1440                   = BOSdata.new()
htfadd1440.settings                 := SettingsHTFadd1440
htfadd1440.candles                  := candlesadd1440
htfadd1440.bosdata                  := bosdataadd1440

htfadd1350.Monitor().BOSJudge()
htfadd1351.Monitor().BOSJudge()
htfadd1352.Monitor().BOSJudge()
htfadd1353.Monitor().BOSJudge()
htfadd1354.Monitor().BOSJudge()
htfadd1355.Monitor().BOSJudge()
htfadd1356.Monitor().BOSJudge()
htfadd1357.Monitor().BOSJudge()
htfadd1358.Monitor().BOSJudge()
htfadd1359.Monitor().BOSJudge()
htfadd1360.Monitor().BOSJudge()
htfadd1361.Monitor().BOSJudge()
htfadd1362.Monitor().BOSJudge()
htfadd1363.Monitor().BOSJudge()
htfadd1364.Monitor().BOSJudge()
htfadd1365.Monitor().BOSJudge()
htfadd1366.Monitor().BOSJudge()
htfadd1367.Monitor().BOSJudge()
htfadd1368.Monitor().BOSJudge()
htfadd1369.Monitor().BOSJudge()
htfadd1370.Monitor().BOSJudge()
htfadd1371.Monitor().BOSJudge()
htfadd1372.Monitor().BOSJudge()
htfadd1373.Monitor().BOSJudge()
htfadd1374.Monitor().BOSJudge()
htfadd1375.Monitor().BOSJudge()
htfadd1376.Monitor().BOSJudge()
htfadd1377.Monitor().BOSJudge()
htfadd1378.Monitor().BOSJudge()
htfadd1379.Monitor().BOSJudge()
htfadd1380.Monitor().BOSJudge()
htfadd1381.Monitor().BOSJudge()
htfadd1382.Monitor().BOSJudge()
htfadd1383.Monitor().BOSJudge()
htfadd1384.Monitor().BOSJudge()
htfadd1385.Monitor().BOSJudge()
htfadd1386.Monitor().BOSJudge()
htfadd1387.Monitor().BOSJudge()
htfadd1388.Monitor().BOSJudge()
htfadd1389.Monitor().BOSJudge()
htfadd1390.Monitor().BOSJudge()
htfadd1391.Monitor().BOSJudge()
htfadd1392.Monitor().BOSJudge()
htfadd1393.Monitor().BOSJudge()
htfadd1394.Monitor().BOSJudge()
htfadd1395.Monitor().BOSJudge()
htfadd1396.Monitor().BOSJudge()
htfadd1397.Monitor().BOSJudge()
htfadd1398.Monitor().BOSJudge()
htfadd1399.Monitor().BOSJudge()
htfadd1400.Monitor().BOSJudge()
htfadd1401.Monitor().BOSJudge()
htfadd1402.Monitor().BOSJudge()
htfadd1403.Monitor().BOSJudge()
htfadd1404.Monitor().BOSJudge()
htfadd1405.Monitor().BOSJudge()
htfadd1406.Monitor().BOSJudge()
htfadd1407.Monitor().BOSJudge()
htfadd1408.Monitor().BOSJudge()
htfadd1409.Monitor().BOSJudge()
htfadd1410.Monitor().BOSJudge()
htfadd1411.Monitor().BOSJudge()
htfadd1412.Monitor().BOSJudge()
htfadd1413.Monitor().BOSJudge()
htfadd1414.Monitor().BOSJudge()
htfadd1415.Monitor().BOSJudge()
htfadd1416.Monitor().BOSJudge()
htfadd1417.Monitor().BOSJudge()
htfadd1418.Monitor().BOSJudge()
htfadd1419.Monitor().BOSJudge()
htfadd1420.Monitor().BOSJudge()
htfadd1421.Monitor().BOSJudge()
htfadd1422.Monitor().BOSJudge()
htfadd1423.Monitor().BOSJudge()
htfadd1424.Monitor().BOSJudge()
htfadd1425.Monitor().BOSJudge()
htfadd1426.Monitor().BOSJudge()
htfadd1427.Monitor().BOSJudge()
htfadd1428.Monitor().BOSJudge()
htfadd1429.Monitor().BOSJudge()
htfadd1430.Monitor().BOSJudge()
htfadd1431.Monitor().BOSJudge()
htfadd1432.Monitor().BOSJudge()
htfadd1433.Monitor().BOSJudge()
htfadd1434.Monitor().BOSJudge()
htfadd1435.Monitor().BOSJudge()
htfadd1436.Monitor().BOSJudge()
htfadd1437.Monitor().BOSJudge()
htfadd1438.Monitor().BOSJudge()
htfadd1439.Monitor().BOSJudge()
htfadd1440.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd1350)
    LowestsbuSet(lowestsbu, htfadd1350)
    HighestsbdSet(highestsbd, htfadd1351)
    LowestsbuSet(lowestsbu, htfadd1351)
    HighestsbdSet(highestsbd, htfadd1352)
    LowestsbuSet(lowestsbu, htfadd1352)
    HighestsbdSet(highestsbd, htfadd1353)
    LowestsbuSet(lowestsbu, htfadd1353)
    HighestsbdSet(highestsbd, htfadd1354)
    LowestsbuSet(lowestsbu, htfadd1354)
    HighestsbdSet(highestsbd, htfadd1355)
    LowestsbuSet(lowestsbu, htfadd1355)
    HighestsbdSet(highestsbd, htfadd1356)
    LowestsbuSet(lowestsbu, htfadd1356)
    HighestsbdSet(highestsbd, htfadd1357)
    LowestsbuSet(lowestsbu, htfadd1357)
    HighestsbdSet(highestsbd, htfadd1358)
    LowestsbuSet(lowestsbu, htfadd1358)
    HighestsbdSet(highestsbd, htfadd1359)
    LowestsbuSet(lowestsbu, htfadd1359)
    HighestsbdSet(highestsbd, htfadd1360)
    LowestsbuSet(lowestsbu, htfadd1360)
    HighestsbdSet(highestsbd, htfadd1361)
    LowestsbuSet(lowestsbu, htfadd1361)
    HighestsbdSet(highestsbd, htfadd1362)
    LowestsbuSet(lowestsbu, htfadd1362)
    HighestsbdSet(highestsbd, htfadd1363)
    LowestsbuSet(lowestsbu, htfadd1363)
    HighestsbdSet(highestsbd, htfadd1364)
    LowestsbuSet(lowestsbu, htfadd1364)
    HighestsbdSet(highestsbd, htfadd1365)
    LowestsbuSet(lowestsbu, htfadd1365)
    HighestsbdSet(highestsbd, htfadd1366)
    LowestsbuSet(lowestsbu, htfadd1366)
    HighestsbdSet(highestsbd, htfadd1367)
    LowestsbuSet(lowestsbu, htfadd1367)
    HighestsbdSet(highestsbd, htfadd1368)
    LowestsbuSet(lowestsbu, htfadd1368)
    HighestsbdSet(highestsbd, htfadd1369)
    LowestsbuSet(lowestsbu, htfadd1369)
    HighestsbdSet(highestsbd, htfadd1370)
    LowestsbuSet(lowestsbu, htfadd1370)
    HighestsbdSet(highestsbd, htfadd1371)
    LowestsbuSet(lowestsbu, htfadd1371)
    HighestsbdSet(highestsbd, htfadd1372)
    LowestsbuSet(lowestsbu, htfadd1372)
    HighestsbdSet(highestsbd, htfadd1373)
    LowestsbuSet(lowestsbu, htfadd1373)
    HighestsbdSet(highestsbd, htfadd1374)
    LowestsbuSet(lowestsbu, htfadd1374)
    HighestsbdSet(highestsbd, htfadd1375)
    LowestsbuSet(lowestsbu, htfadd1375)
    HighestsbdSet(highestsbd, htfadd1376)
    LowestsbuSet(lowestsbu, htfadd1376)
    HighestsbdSet(highestsbd, htfadd1377)
    LowestsbuSet(lowestsbu, htfadd1377)
    HighestsbdSet(highestsbd, htfadd1378)
    LowestsbuSet(lowestsbu, htfadd1378)
    HighestsbdSet(highestsbd, htfadd1379)
    LowestsbuSet(lowestsbu, htfadd1379)
    HighestsbdSet(highestsbd, htfadd1380)
    LowestsbuSet(lowestsbu, htfadd1380)
    HighestsbdSet(highestsbd, htfadd1381)
    LowestsbuSet(lowestsbu, htfadd1381)
    HighestsbdSet(highestsbd, htfadd1382)
    LowestsbuSet(lowestsbu, htfadd1382)
    HighestsbdSet(highestsbd, htfadd1383)
    LowestsbuSet(lowestsbu, htfadd1383)
    HighestsbdSet(highestsbd, htfadd1384)
    LowestsbuSet(lowestsbu, htfadd1384)
    HighestsbdSet(highestsbd, htfadd1385)
    LowestsbuSet(lowestsbu, htfadd1385)
    HighestsbdSet(highestsbd, htfadd1386)
    LowestsbuSet(lowestsbu, htfadd1386)
    HighestsbdSet(highestsbd, htfadd1387)
    LowestsbuSet(lowestsbu, htfadd1387)
    HighestsbdSet(highestsbd, htfadd1388)
    LowestsbuSet(lowestsbu, htfadd1388)
    HighestsbdSet(highestsbd, htfadd1389)
    LowestsbuSet(lowestsbu, htfadd1389)
    HighestsbdSet(highestsbd, htfadd1390)
    LowestsbuSet(lowestsbu, htfadd1390)
    HighestsbdSet(highestsbd, htfadd1391)
    LowestsbuSet(lowestsbu, htfadd1391)
    HighestsbdSet(highestsbd, htfadd1392)
    LowestsbuSet(lowestsbu, htfadd1392)
    HighestsbdSet(highestsbd, htfadd1393)
    LowestsbuSet(lowestsbu, htfadd1393)
    HighestsbdSet(highestsbd, htfadd1394)
    LowestsbuSet(lowestsbu, htfadd1394)
    HighestsbdSet(highestsbd, htfadd1395)
    LowestsbuSet(lowestsbu, htfadd1395)
    HighestsbdSet(highestsbd, htfadd1396)
    LowestsbuSet(lowestsbu, htfadd1396)
    HighestsbdSet(highestsbd, htfadd1397)
    LowestsbuSet(lowestsbu, htfadd1397)
    HighestsbdSet(highestsbd, htfadd1398)
    LowestsbuSet(lowestsbu, htfadd1398)
    HighestsbdSet(highestsbd, htfadd1399)
    LowestsbuSet(lowestsbu, htfadd1399)
    HighestsbdSet(highestsbd, htfadd1400)
    LowestsbuSet(lowestsbu, htfadd1400)
    HighestsbdSet(highestsbd, htfadd1401)
    LowestsbuSet(lowestsbu, htfadd1401)
    HighestsbdSet(highestsbd, htfadd1402)
    LowestsbuSet(lowestsbu, htfadd1402)
    HighestsbdSet(highestsbd, htfadd1403)
    LowestsbuSet(lowestsbu, htfadd1403)
    HighestsbdSet(highestsbd, htfadd1404)
    LowestsbuSet(lowestsbu, htfadd1404)
    HighestsbdSet(highestsbd, htfadd1405)
    LowestsbuSet(lowestsbu, htfadd1405)
    HighestsbdSet(highestsbd, htfadd1406)
    LowestsbuSet(lowestsbu, htfadd1406)
    HighestsbdSet(highestsbd, htfadd1407)
    LowestsbuSet(lowestsbu, htfadd1407)
    HighestsbdSet(highestsbd, htfadd1408)
    LowestsbuSet(lowestsbu, htfadd1408)
    HighestsbdSet(highestsbd, htfadd1409)
    LowestsbuSet(lowestsbu, htfadd1409)
    HighestsbdSet(highestsbd, htfadd1410)
    LowestsbuSet(lowestsbu, htfadd1410)
    HighestsbdSet(highestsbd, htfadd1411)
    LowestsbuSet(lowestsbu, htfadd1411)
    HighestsbdSet(highestsbd, htfadd1412)
    LowestsbuSet(lowestsbu, htfadd1412)
    HighestsbdSet(highestsbd, htfadd1413)
    LowestsbuSet(lowestsbu, htfadd1413)
    HighestsbdSet(highestsbd, htfadd1414)
    LowestsbuSet(lowestsbu, htfadd1414)
    HighestsbdSet(highestsbd, htfadd1415)
    LowestsbuSet(lowestsbu, htfadd1415)
    HighestsbdSet(highestsbd, htfadd1416)
    LowestsbuSet(lowestsbu, htfadd1416)
    HighestsbdSet(highestsbd, htfadd1417)
    LowestsbuSet(lowestsbu, htfadd1417)
    HighestsbdSet(highestsbd, htfadd1418)
    LowestsbuSet(lowestsbu, htfadd1418)
    HighestsbdSet(highestsbd, htfadd1419)
    LowestsbuSet(lowestsbu, htfadd1419)
    HighestsbdSet(highestsbd, htfadd1420)
    LowestsbuSet(lowestsbu, htfadd1420)
    HighestsbdSet(highestsbd, htfadd1421)
    LowestsbuSet(lowestsbu, htfadd1421)
    HighestsbdSet(highestsbd, htfadd1422)
    LowestsbuSet(lowestsbu, htfadd1422)
    HighestsbdSet(highestsbd, htfadd1423)
    LowestsbuSet(lowestsbu, htfadd1423)
    HighestsbdSet(highestsbd, htfadd1424)
    LowestsbuSet(lowestsbu, htfadd1424)
    HighestsbdSet(highestsbd, htfadd1425)
    LowestsbuSet(lowestsbu, htfadd1425)
    HighestsbdSet(highestsbd, htfadd1426)
    LowestsbuSet(lowestsbu, htfadd1426)
    HighestsbdSet(highestsbd, htfadd1427)
    LowestsbuSet(lowestsbu, htfadd1427)
    HighestsbdSet(highestsbd, htfadd1428)
    LowestsbuSet(lowestsbu, htfadd1428)
    HighestsbdSet(highestsbd, htfadd1429)
    LowestsbuSet(lowestsbu, htfadd1429)
    HighestsbdSet(highestsbd, htfadd1430)
    LowestsbuSet(lowestsbu, htfadd1430)
    HighestsbdSet(highestsbd, htfadd1431)
    LowestsbuSet(lowestsbu, htfadd1431)
    HighestsbdSet(highestsbd, htfadd1432)
    LowestsbuSet(lowestsbu, htfadd1432)
    HighestsbdSet(highestsbd, htfadd1433)
    LowestsbuSet(lowestsbu, htfadd1433)
    HighestsbdSet(highestsbd, htfadd1434)
    LowestsbuSet(lowestsbu, htfadd1434)
    HighestsbdSet(highestsbd, htfadd1435)
    LowestsbuSet(lowestsbu, htfadd1435)
    HighestsbdSet(highestsbd, htfadd1436)
    LowestsbuSet(lowestsbu, htfadd1436)
    HighestsbdSet(highestsbd, htfadd1437)
    LowestsbuSet(lowestsbu, htfadd1437)
    HighestsbdSet(highestsbd, htfadd1438)
    LowestsbuSet(lowestsbu, htfadd1438)
    HighestsbdSet(highestsbd, htfadd1439)
    LowestsbuSet(lowestsbu, htfadd1439)
    HighestsbdSet(highestsbd, htfadd1440)
    LowestsbuSet(lowestsbu, htfadd1440)

    htfshadow.Shadowing(htfadd1350).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1351).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1352).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1353).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1354).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1355).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1356).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1357).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1358).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1359).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1360).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1361).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1362).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1363).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1364).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1365).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1366).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1367).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1368).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1369).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1370).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1371).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1372).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1373).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1374).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1375).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1376).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1377).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1378).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1379).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1380).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1381).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1382).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1383).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1384).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1385).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1386).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1387).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1388).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1389).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1390).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1391).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1392).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1393).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1394).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1395).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1396).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1397).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1398).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1399).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1400).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1401).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1402).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1403).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1404).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1405).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1406).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1407).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1408).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1409).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1410).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1411).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1412).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1413).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1414).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1415).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1416).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1417).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1418).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1419).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1420).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1421).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1422).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1423).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1424).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1425).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1426).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1427).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1428).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1429).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1430).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1431).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1432).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1433).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1434).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1435).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1436).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1437).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1438).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1439).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1440).Monitor_Est().BOSJudge()
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


