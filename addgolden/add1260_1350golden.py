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
var CandleSet htfadd1260                     = CandleSet.new()
var CandleSettings SettingsHTFadd1260        = CandleSettings.new(htf='1260',htfint=1260,max_memory=3)
var Candle[] candlesadd1260                  = array.new<Candle>(0)
var BOSdata bosdataadd1260                   = BOSdata.new()
htfadd1260.settings                 := SettingsHTFadd1260
htfadd1260.candles                  := candlesadd1260
htfadd1260.bosdata                  := bosdataadd1260
var CandleSet htfadd1261                     = CandleSet.new()
var CandleSettings SettingsHTFadd1261        = CandleSettings.new(htf='1261',htfint=1261,max_memory=3)
var Candle[] candlesadd1261                  = array.new<Candle>(0)
var BOSdata bosdataadd1261                   = BOSdata.new()
htfadd1261.settings                 := SettingsHTFadd1261
htfadd1261.candles                  := candlesadd1261
htfadd1261.bosdata                  := bosdataadd1261
var CandleSet htfadd1262                     = CandleSet.new()
var CandleSettings SettingsHTFadd1262        = CandleSettings.new(htf='1262',htfint=1262,max_memory=3)
var Candle[] candlesadd1262                  = array.new<Candle>(0)
var BOSdata bosdataadd1262                   = BOSdata.new()
htfadd1262.settings                 := SettingsHTFadd1262
htfadd1262.candles                  := candlesadd1262
htfadd1262.bosdata                  := bosdataadd1262
var CandleSet htfadd1263                     = CandleSet.new()
var CandleSettings SettingsHTFadd1263        = CandleSettings.new(htf='1263',htfint=1263,max_memory=3)
var Candle[] candlesadd1263                  = array.new<Candle>(0)
var BOSdata bosdataadd1263                   = BOSdata.new()
htfadd1263.settings                 := SettingsHTFadd1263
htfadd1263.candles                  := candlesadd1263
htfadd1263.bosdata                  := bosdataadd1263
var CandleSet htfadd1264                     = CandleSet.new()
var CandleSettings SettingsHTFadd1264        = CandleSettings.new(htf='1264',htfint=1264,max_memory=3)
var Candle[] candlesadd1264                  = array.new<Candle>(0)
var BOSdata bosdataadd1264                   = BOSdata.new()
htfadd1264.settings                 := SettingsHTFadd1264
htfadd1264.candles                  := candlesadd1264
htfadd1264.bosdata                  := bosdataadd1264
var CandleSet htfadd1265                     = CandleSet.new()
var CandleSettings SettingsHTFadd1265        = CandleSettings.new(htf='1265',htfint=1265,max_memory=3)
var Candle[] candlesadd1265                  = array.new<Candle>(0)
var BOSdata bosdataadd1265                   = BOSdata.new()
htfadd1265.settings                 := SettingsHTFadd1265
htfadd1265.candles                  := candlesadd1265
htfadd1265.bosdata                  := bosdataadd1265
var CandleSet htfadd1266                     = CandleSet.new()
var CandleSettings SettingsHTFadd1266        = CandleSettings.new(htf='1266',htfint=1266,max_memory=3)
var Candle[] candlesadd1266                  = array.new<Candle>(0)
var BOSdata bosdataadd1266                   = BOSdata.new()
htfadd1266.settings                 := SettingsHTFadd1266
htfadd1266.candles                  := candlesadd1266
htfadd1266.bosdata                  := bosdataadd1266
var CandleSet htfadd1267                     = CandleSet.new()
var CandleSettings SettingsHTFadd1267        = CandleSettings.new(htf='1267',htfint=1267,max_memory=3)
var Candle[] candlesadd1267                  = array.new<Candle>(0)
var BOSdata bosdataadd1267                   = BOSdata.new()
htfadd1267.settings                 := SettingsHTFadd1267
htfadd1267.candles                  := candlesadd1267
htfadd1267.bosdata                  := bosdataadd1267
var CandleSet htfadd1268                     = CandleSet.new()
var CandleSettings SettingsHTFadd1268        = CandleSettings.new(htf='1268',htfint=1268,max_memory=3)
var Candle[] candlesadd1268                  = array.new<Candle>(0)
var BOSdata bosdataadd1268                   = BOSdata.new()
htfadd1268.settings                 := SettingsHTFadd1268
htfadd1268.candles                  := candlesadd1268
htfadd1268.bosdata                  := bosdataadd1268
var CandleSet htfadd1269                     = CandleSet.new()
var CandleSettings SettingsHTFadd1269        = CandleSettings.new(htf='1269',htfint=1269,max_memory=3)
var Candle[] candlesadd1269                  = array.new<Candle>(0)
var BOSdata bosdataadd1269                   = BOSdata.new()
htfadd1269.settings                 := SettingsHTFadd1269
htfadd1269.candles                  := candlesadd1269
htfadd1269.bosdata                  := bosdataadd1269
var CandleSet htfadd1270                     = CandleSet.new()
var CandleSettings SettingsHTFadd1270        = CandleSettings.new(htf='1270',htfint=1270,max_memory=3)
var Candle[] candlesadd1270                  = array.new<Candle>(0)
var BOSdata bosdataadd1270                   = BOSdata.new()
htfadd1270.settings                 := SettingsHTFadd1270
htfadd1270.candles                  := candlesadd1270
htfadd1270.bosdata                  := bosdataadd1270
var CandleSet htfadd1271                     = CandleSet.new()
var CandleSettings SettingsHTFadd1271        = CandleSettings.new(htf='1271',htfint=1271,max_memory=3)
var Candle[] candlesadd1271                  = array.new<Candle>(0)
var BOSdata bosdataadd1271                   = BOSdata.new()
htfadd1271.settings                 := SettingsHTFadd1271
htfadd1271.candles                  := candlesadd1271
htfadd1271.bosdata                  := bosdataadd1271
var CandleSet htfadd1272                     = CandleSet.new()
var CandleSettings SettingsHTFadd1272        = CandleSettings.new(htf='1272',htfint=1272,max_memory=3)
var Candle[] candlesadd1272                  = array.new<Candle>(0)
var BOSdata bosdataadd1272                   = BOSdata.new()
htfadd1272.settings                 := SettingsHTFadd1272
htfadd1272.candles                  := candlesadd1272
htfadd1272.bosdata                  := bosdataadd1272
var CandleSet htfadd1273                     = CandleSet.new()
var CandleSettings SettingsHTFadd1273        = CandleSettings.new(htf='1273',htfint=1273,max_memory=3)
var Candle[] candlesadd1273                  = array.new<Candle>(0)
var BOSdata bosdataadd1273                   = BOSdata.new()
htfadd1273.settings                 := SettingsHTFadd1273
htfadd1273.candles                  := candlesadd1273
htfadd1273.bosdata                  := bosdataadd1273
var CandleSet htfadd1274                     = CandleSet.new()
var CandleSettings SettingsHTFadd1274        = CandleSettings.new(htf='1274',htfint=1274,max_memory=3)
var Candle[] candlesadd1274                  = array.new<Candle>(0)
var BOSdata bosdataadd1274                   = BOSdata.new()
htfadd1274.settings                 := SettingsHTFadd1274
htfadd1274.candles                  := candlesadd1274
htfadd1274.bosdata                  := bosdataadd1274
var CandleSet htfadd1275                     = CandleSet.new()
var CandleSettings SettingsHTFadd1275        = CandleSettings.new(htf='1275',htfint=1275,max_memory=3)
var Candle[] candlesadd1275                  = array.new<Candle>(0)
var BOSdata bosdataadd1275                   = BOSdata.new()
htfadd1275.settings                 := SettingsHTFadd1275
htfadd1275.candles                  := candlesadd1275
htfadd1275.bosdata                  := bosdataadd1275
var CandleSet htfadd1276                     = CandleSet.new()
var CandleSettings SettingsHTFadd1276        = CandleSettings.new(htf='1276',htfint=1276,max_memory=3)
var Candle[] candlesadd1276                  = array.new<Candle>(0)
var BOSdata bosdataadd1276                   = BOSdata.new()
htfadd1276.settings                 := SettingsHTFadd1276
htfadd1276.candles                  := candlesadd1276
htfadd1276.bosdata                  := bosdataadd1276
var CandleSet htfadd1277                     = CandleSet.new()
var CandleSettings SettingsHTFadd1277        = CandleSettings.new(htf='1277',htfint=1277,max_memory=3)
var Candle[] candlesadd1277                  = array.new<Candle>(0)
var BOSdata bosdataadd1277                   = BOSdata.new()
htfadd1277.settings                 := SettingsHTFadd1277
htfadd1277.candles                  := candlesadd1277
htfadd1277.bosdata                  := bosdataadd1277
var CandleSet htfadd1278                     = CandleSet.new()
var CandleSettings SettingsHTFadd1278        = CandleSettings.new(htf='1278',htfint=1278,max_memory=3)
var Candle[] candlesadd1278                  = array.new<Candle>(0)
var BOSdata bosdataadd1278                   = BOSdata.new()
htfadd1278.settings                 := SettingsHTFadd1278
htfadd1278.candles                  := candlesadd1278
htfadd1278.bosdata                  := bosdataadd1278
var CandleSet htfadd1279                     = CandleSet.new()
var CandleSettings SettingsHTFadd1279        = CandleSettings.new(htf='1279',htfint=1279,max_memory=3)
var Candle[] candlesadd1279                  = array.new<Candle>(0)
var BOSdata bosdataadd1279                   = BOSdata.new()
htfadd1279.settings                 := SettingsHTFadd1279
htfadd1279.candles                  := candlesadd1279
htfadd1279.bosdata                  := bosdataadd1279
var CandleSet htfadd1280                     = CandleSet.new()
var CandleSettings SettingsHTFadd1280        = CandleSettings.new(htf='1280',htfint=1280,max_memory=3)
var Candle[] candlesadd1280                  = array.new<Candle>(0)
var BOSdata bosdataadd1280                   = BOSdata.new()
htfadd1280.settings                 := SettingsHTFadd1280
htfadd1280.candles                  := candlesadd1280
htfadd1280.bosdata                  := bosdataadd1280
var CandleSet htfadd1281                     = CandleSet.new()
var CandleSettings SettingsHTFadd1281        = CandleSettings.new(htf='1281',htfint=1281,max_memory=3)
var Candle[] candlesadd1281                  = array.new<Candle>(0)
var BOSdata bosdataadd1281                   = BOSdata.new()
htfadd1281.settings                 := SettingsHTFadd1281
htfadd1281.candles                  := candlesadd1281
htfadd1281.bosdata                  := bosdataadd1281
var CandleSet htfadd1282                     = CandleSet.new()
var CandleSettings SettingsHTFadd1282        = CandleSettings.new(htf='1282',htfint=1282,max_memory=3)
var Candle[] candlesadd1282                  = array.new<Candle>(0)
var BOSdata bosdataadd1282                   = BOSdata.new()
htfadd1282.settings                 := SettingsHTFadd1282
htfadd1282.candles                  := candlesadd1282
htfadd1282.bosdata                  := bosdataadd1282
var CandleSet htfadd1283                     = CandleSet.new()
var CandleSettings SettingsHTFadd1283        = CandleSettings.new(htf='1283',htfint=1283,max_memory=3)
var Candle[] candlesadd1283                  = array.new<Candle>(0)
var BOSdata bosdataadd1283                   = BOSdata.new()
htfadd1283.settings                 := SettingsHTFadd1283
htfadd1283.candles                  := candlesadd1283
htfadd1283.bosdata                  := bosdataadd1283
var CandleSet htfadd1284                     = CandleSet.new()
var CandleSettings SettingsHTFadd1284        = CandleSettings.new(htf='1284',htfint=1284,max_memory=3)
var Candle[] candlesadd1284                  = array.new<Candle>(0)
var BOSdata bosdataadd1284                   = BOSdata.new()
htfadd1284.settings                 := SettingsHTFadd1284
htfadd1284.candles                  := candlesadd1284
htfadd1284.bosdata                  := bosdataadd1284
var CandleSet htfadd1285                     = CandleSet.new()
var CandleSettings SettingsHTFadd1285        = CandleSettings.new(htf='1285',htfint=1285,max_memory=3)
var Candle[] candlesadd1285                  = array.new<Candle>(0)
var BOSdata bosdataadd1285                   = BOSdata.new()
htfadd1285.settings                 := SettingsHTFadd1285
htfadd1285.candles                  := candlesadd1285
htfadd1285.bosdata                  := bosdataadd1285
var CandleSet htfadd1286                     = CandleSet.new()
var CandleSettings SettingsHTFadd1286        = CandleSettings.new(htf='1286',htfint=1286,max_memory=3)
var Candle[] candlesadd1286                  = array.new<Candle>(0)
var BOSdata bosdataadd1286                   = BOSdata.new()
htfadd1286.settings                 := SettingsHTFadd1286
htfadd1286.candles                  := candlesadd1286
htfadd1286.bosdata                  := bosdataadd1286
var CandleSet htfadd1287                     = CandleSet.new()
var CandleSettings SettingsHTFadd1287        = CandleSettings.new(htf='1287',htfint=1287,max_memory=3)
var Candle[] candlesadd1287                  = array.new<Candle>(0)
var BOSdata bosdataadd1287                   = BOSdata.new()
htfadd1287.settings                 := SettingsHTFadd1287
htfadd1287.candles                  := candlesadd1287
htfadd1287.bosdata                  := bosdataadd1287
var CandleSet htfadd1288                     = CandleSet.new()
var CandleSettings SettingsHTFadd1288        = CandleSettings.new(htf='1288',htfint=1288,max_memory=3)
var Candle[] candlesadd1288                  = array.new<Candle>(0)
var BOSdata bosdataadd1288                   = BOSdata.new()
htfadd1288.settings                 := SettingsHTFadd1288
htfadd1288.candles                  := candlesadd1288
htfadd1288.bosdata                  := bosdataadd1288
var CandleSet htfadd1289                     = CandleSet.new()
var CandleSettings SettingsHTFadd1289        = CandleSettings.new(htf='1289',htfint=1289,max_memory=3)
var Candle[] candlesadd1289                  = array.new<Candle>(0)
var BOSdata bosdataadd1289                   = BOSdata.new()
htfadd1289.settings                 := SettingsHTFadd1289
htfadd1289.candles                  := candlesadd1289
htfadd1289.bosdata                  := bosdataadd1289
var CandleSet htfadd1290                     = CandleSet.new()
var CandleSettings SettingsHTFadd1290        = CandleSettings.new(htf='1290',htfint=1290,max_memory=3)
var Candle[] candlesadd1290                  = array.new<Candle>(0)
var BOSdata bosdataadd1290                   = BOSdata.new()
htfadd1290.settings                 := SettingsHTFadd1290
htfadd1290.candles                  := candlesadd1290
htfadd1290.bosdata                  := bosdataadd1290
var CandleSet htfadd1291                     = CandleSet.new()
var CandleSettings SettingsHTFadd1291        = CandleSettings.new(htf='1291',htfint=1291,max_memory=3)
var Candle[] candlesadd1291                  = array.new<Candle>(0)
var BOSdata bosdataadd1291                   = BOSdata.new()
htfadd1291.settings                 := SettingsHTFadd1291
htfadd1291.candles                  := candlesadd1291
htfadd1291.bosdata                  := bosdataadd1291
var CandleSet htfadd1292                     = CandleSet.new()
var CandleSettings SettingsHTFadd1292        = CandleSettings.new(htf='1292',htfint=1292,max_memory=3)
var Candle[] candlesadd1292                  = array.new<Candle>(0)
var BOSdata bosdataadd1292                   = BOSdata.new()
htfadd1292.settings                 := SettingsHTFadd1292
htfadd1292.candles                  := candlesadd1292
htfadd1292.bosdata                  := bosdataadd1292
var CandleSet htfadd1293                     = CandleSet.new()
var CandleSettings SettingsHTFadd1293        = CandleSettings.new(htf='1293',htfint=1293,max_memory=3)
var Candle[] candlesadd1293                  = array.new<Candle>(0)
var BOSdata bosdataadd1293                   = BOSdata.new()
htfadd1293.settings                 := SettingsHTFadd1293
htfadd1293.candles                  := candlesadd1293
htfadd1293.bosdata                  := bosdataadd1293
var CandleSet htfadd1294                     = CandleSet.new()
var CandleSettings SettingsHTFadd1294        = CandleSettings.new(htf='1294',htfint=1294,max_memory=3)
var Candle[] candlesadd1294                  = array.new<Candle>(0)
var BOSdata bosdataadd1294                   = BOSdata.new()
htfadd1294.settings                 := SettingsHTFadd1294
htfadd1294.candles                  := candlesadd1294
htfadd1294.bosdata                  := bosdataadd1294
var CandleSet htfadd1295                     = CandleSet.new()
var CandleSettings SettingsHTFadd1295        = CandleSettings.new(htf='1295',htfint=1295,max_memory=3)
var Candle[] candlesadd1295                  = array.new<Candle>(0)
var BOSdata bosdataadd1295                   = BOSdata.new()
htfadd1295.settings                 := SettingsHTFadd1295
htfadd1295.candles                  := candlesadd1295
htfadd1295.bosdata                  := bosdataadd1295
var CandleSet htfadd1296                     = CandleSet.new()
var CandleSettings SettingsHTFadd1296        = CandleSettings.new(htf='1296',htfint=1296,max_memory=3)
var Candle[] candlesadd1296                  = array.new<Candle>(0)
var BOSdata bosdataadd1296                   = BOSdata.new()
htfadd1296.settings                 := SettingsHTFadd1296
htfadd1296.candles                  := candlesadd1296
htfadd1296.bosdata                  := bosdataadd1296
var CandleSet htfadd1297                     = CandleSet.new()
var CandleSettings SettingsHTFadd1297        = CandleSettings.new(htf='1297',htfint=1297,max_memory=3)
var Candle[] candlesadd1297                  = array.new<Candle>(0)
var BOSdata bosdataadd1297                   = BOSdata.new()
htfadd1297.settings                 := SettingsHTFadd1297
htfadd1297.candles                  := candlesadd1297
htfadd1297.bosdata                  := bosdataadd1297
var CandleSet htfadd1298                     = CandleSet.new()
var CandleSettings SettingsHTFadd1298        = CandleSettings.new(htf='1298',htfint=1298,max_memory=3)
var Candle[] candlesadd1298                  = array.new<Candle>(0)
var BOSdata bosdataadd1298                   = BOSdata.new()
htfadd1298.settings                 := SettingsHTFadd1298
htfadd1298.candles                  := candlesadd1298
htfadd1298.bosdata                  := bosdataadd1298
var CandleSet htfadd1299                     = CandleSet.new()
var CandleSettings SettingsHTFadd1299        = CandleSettings.new(htf='1299',htfint=1299,max_memory=3)
var Candle[] candlesadd1299                  = array.new<Candle>(0)
var BOSdata bosdataadd1299                   = BOSdata.new()
htfadd1299.settings                 := SettingsHTFadd1299
htfadd1299.candles                  := candlesadd1299
htfadd1299.bosdata                  := bosdataadd1299
var CandleSet htfadd1300                     = CandleSet.new()
var CandleSettings SettingsHTFadd1300        = CandleSettings.new(htf='1300',htfint=1300,max_memory=3)
var Candle[] candlesadd1300                  = array.new<Candle>(0)
var BOSdata bosdataadd1300                   = BOSdata.new()
htfadd1300.settings                 := SettingsHTFadd1300
htfadd1300.candles                  := candlesadd1300
htfadd1300.bosdata                  := bosdataadd1300
var CandleSet htfadd1301                     = CandleSet.new()
var CandleSettings SettingsHTFadd1301        = CandleSettings.new(htf='1301',htfint=1301,max_memory=3)
var Candle[] candlesadd1301                  = array.new<Candle>(0)
var BOSdata bosdataadd1301                   = BOSdata.new()
htfadd1301.settings                 := SettingsHTFadd1301
htfadd1301.candles                  := candlesadd1301
htfadd1301.bosdata                  := bosdataadd1301
var CandleSet htfadd1302                     = CandleSet.new()
var CandleSettings SettingsHTFadd1302        = CandleSettings.new(htf='1302',htfint=1302,max_memory=3)
var Candle[] candlesadd1302                  = array.new<Candle>(0)
var BOSdata bosdataadd1302                   = BOSdata.new()
htfadd1302.settings                 := SettingsHTFadd1302
htfadd1302.candles                  := candlesadd1302
htfadd1302.bosdata                  := bosdataadd1302
var CandleSet htfadd1303                     = CandleSet.new()
var CandleSettings SettingsHTFadd1303        = CandleSettings.new(htf='1303',htfint=1303,max_memory=3)
var Candle[] candlesadd1303                  = array.new<Candle>(0)
var BOSdata bosdataadd1303                   = BOSdata.new()
htfadd1303.settings                 := SettingsHTFadd1303
htfadd1303.candles                  := candlesadd1303
htfadd1303.bosdata                  := bosdataadd1303
var CandleSet htfadd1304                     = CandleSet.new()
var CandleSettings SettingsHTFadd1304        = CandleSettings.new(htf='1304',htfint=1304,max_memory=3)
var Candle[] candlesadd1304                  = array.new<Candle>(0)
var BOSdata bosdataadd1304                   = BOSdata.new()
htfadd1304.settings                 := SettingsHTFadd1304
htfadd1304.candles                  := candlesadd1304
htfadd1304.bosdata                  := bosdataadd1304
var CandleSet htfadd1305                     = CandleSet.new()
var CandleSettings SettingsHTFadd1305        = CandleSettings.new(htf='1305',htfint=1305,max_memory=3)
var Candle[] candlesadd1305                  = array.new<Candle>(0)
var BOSdata bosdataadd1305                   = BOSdata.new()
htfadd1305.settings                 := SettingsHTFadd1305
htfadd1305.candles                  := candlesadd1305
htfadd1305.bosdata                  := bosdataadd1305
var CandleSet htfadd1306                     = CandleSet.new()
var CandleSettings SettingsHTFadd1306        = CandleSettings.new(htf='1306',htfint=1306,max_memory=3)
var Candle[] candlesadd1306                  = array.new<Candle>(0)
var BOSdata bosdataadd1306                   = BOSdata.new()
htfadd1306.settings                 := SettingsHTFadd1306
htfadd1306.candles                  := candlesadd1306
htfadd1306.bosdata                  := bosdataadd1306
var CandleSet htfadd1307                     = CandleSet.new()
var CandleSettings SettingsHTFadd1307        = CandleSettings.new(htf='1307',htfint=1307,max_memory=3)
var Candle[] candlesadd1307                  = array.new<Candle>(0)
var BOSdata bosdataadd1307                   = BOSdata.new()
htfadd1307.settings                 := SettingsHTFadd1307
htfadd1307.candles                  := candlesadd1307
htfadd1307.bosdata                  := bosdataadd1307
var CandleSet htfadd1308                     = CandleSet.new()
var CandleSettings SettingsHTFadd1308        = CandleSettings.new(htf='1308',htfint=1308,max_memory=3)
var Candle[] candlesadd1308                  = array.new<Candle>(0)
var BOSdata bosdataadd1308                   = BOSdata.new()
htfadd1308.settings                 := SettingsHTFadd1308
htfadd1308.candles                  := candlesadd1308
htfadd1308.bosdata                  := bosdataadd1308
var CandleSet htfadd1309                     = CandleSet.new()
var CandleSettings SettingsHTFadd1309        = CandleSettings.new(htf='1309',htfint=1309,max_memory=3)
var Candle[] candlesadd1309                  = array.new<Candle>(0)
var BOSdata bosdataadd1309                   = BOSdata.new()
htfadd1309.settings                 := SettingsHTFadd1309
htfadd1309.candles                  := candlesadd1309
htfadd1309.bosdata                  := bosdataadd1309
var CandleSet htfadd1310                     = CandleSet.new()
var CandleSettings SettingsHTFadd1310        = CandleSettings.new(htf='1310',htfint=1310,max_memory=3)
var Candle[] candlesadd1310                  = array.new<Candle>(0)
var BOSdata bosdataadd1310                   = BOSdata.new()
htfadd1310.settings                 := SettingsHTFadd1310
htfadd1310.candles                  := candlesadd1310
htfadd1310.bosdata                  := bosdataadd1310
var CandleSet htfadd1311                     = CandleSet.new()
var CandleSettings SettingsHTFadd1311        = CandleSettings.new(htf='1311',htfint=1311,max_memory=3)
var Candle[] candlesadd1311                  = array.new<Candle>(0)
var BOSdata bosdataadd1311                   = BOSdata.new()
htfadd1311.settings                 := SettingsHTFadd1311
htfadd1311.candles                  := candlesadd1311
htfadd1311.bosdata                  := bosdataadd1311
var CandleSet htfadd1312                     = CandleSet.new()
var CandleSettings SettingsHTFadd1312        = CandleSettings.new(htf='1312',htfint=1312,max_memory=3)
var Candle[] candlesadd1312                  = array.new<Candle>(0)
var BOSdata bosdataadd1312                   = BOSdata.new()
htfadd1312.settings                 := SettingsHTFadd1312
htfadd1312.candles                  := candlesadd1312
htfadd1312.bosdata                  := bosdataadd1312
var CandleSet htfadd1313                     = CandleSet.new()
var CandleSettings SettingsHTFadd1313        = CandleSettings.new(htf='1313',htfint=1313,max_memory=3)
var Candle[] candlesadd1313                  = array.new<Candle>(0)
var BOSdata bosdataadd1313                   = BOSdata.new()
htfadd1313.settings                 := SettingsHTFadd1313
htfadd1313.candles                  := candlesadd1313
htfadd1313.bosdata                  := bosdataadd1313
var CandleSet htfadd1314                     = CandleSet.new()
var CandleSettings SettingsHTFadd1314        = CandleSettings.new(htf='1314',htfint=1314,max_memory=3)
var Candle[] candlesadd1314                  = array.new<Candle>(0)
var BOSdata bosdataadd1314                   = BOSdata.new()
htfadd1314.settings                 := SettingsHTFadd1314
htfadd1314.candles                  := candlesadd1314
htfadd1314.bosdata                  := bosdataadd1314
var CandleSet htfadd1315                     = CandleSet.new()
var CandleSettings SettingsHTFadd1315        = CandleSettings.new(htf='1315',htfint=1315,max_memory=3)
var Candle[] candlesadd1315                  = array.new<Candle>(0)
var BOSdata bosdataadd1315                   = BOSdata.new()
htfadd1315.settings                 := SettingsHTFadd1315
htfadd1315.candles                  := candlesadd1315
htfadd1315.bosdata                  := bosdataadd1315
var CandleSet htfadd1316                     = CandleSet.new()
var CandleSettings SettingsHTFadd1316        = CandleSettings.new(htf='1316',htfint=1316,max_memory=3)
var Candle[] candlesadd1316                  = array.new<Candle>(0)
var BOSdata bosdataadd1316                   = BOSdata.new()
htfadd1316.settings                 := SettingsHTFadd1316
htfadd1316.candles                  := candlesadd1316
htfadd1316.bosdata                  := bosdataadd1316
var CandleSet htfadd1317                     = CandleSet.new()
var CandleSettings SettingsHTFadd1317        = CandleSettings.new(htf='1317',htfint=1317,max_memory=3)
var Candle[] candlesadd1317                  = array.new<Candle>(0)
var BOSdata bosdataadd1317                   = BOSdata.new()
htfadd1317.settings                 := SettingsHTFadd1317
htfadd1317.candles                  := candlesadd1317
htfadd1317.bosdata                  := bosdataadd1317
var CandleSet htfadd1318                     = CandleSet.new()
var CandleSettings SettingsHTFadd1318        = CandleSettings.new(htf='1318',htfint=1318,max_memory=3)
var Candle[] candlesadd1318                  = array.new<Candle>(0)
var BOSdata bosdataadd1318                   = BOSdata.new()
htfadd1318.settings                 := SettingsHTFadd1318
htfadd1318.candles                  := candlesadd1318
htfadd1318.bosdata                  := bosdataadd1318
var CandleSet htfadd1319                     = CandleSet.new()
var CandleSettings SettingsHTFadd1319        = CandleSettings.new(htf='1319',htfint=1319,max_memory=3)
var Candle[] candlesadd1319                  = array.new<Candle>(0)
var BOSdata bosdataadd1319                   = BOSdata.new()
htfadd1319.settings                 := SettingsHTFadd1319
htfadd1319.candles                  := candlesadd1319
htfadd1319.bosdata                  := bosdataadd1319
var CandleSet htfadd1320                     = CandleSet.new()
var CandleSettings SettingsHTFadd1320        = CandleSettings.new(htf='1320',htfint=1320,max_memory=3)
var Candle[] candlesadd1320                  = array.new<Candle>(0)
var BOSdata bosdataadd1320                   = BOSdata.new()
htfadd1320.settings                 := SettingsHTFadd1320
htfadd1320.candles                  := candlesadd1320
htfadd1320.bosdata                  := bosdataadd1320
var CandleSet htfadd1321                     = CandleSet.new()
var CandleSettings SettingsHTFadd1321        = CandleSettings.new(htf='1321',htfint=1321,max_memory=3)
var Candle[] candlesadd1321                  = array.new<Candle>(0)
var BOSdata bosdataadd1321                   = BOSdata.new()
htfadd1321.settings                 := SettingsHTFadd1321
htfadd1321.candles                  := candlesadd1321
htfadd1321.bosdata                  := bosdataadd1321
var CandleSet htfadd1322                     = CandleSet.new()
var CandleSettings SettingsHTFadd1322        = CandleSettings.new(htf='1322',htfint=1322,max_memory=3)
var Candle[] candlesadd1322                  = array.new<Candle>(0)
var BOSdata bosdataadd1322                   = BOSdata.new()
htfadd1322.settings                 := SettingsHTFadd1322
htfadd1322.candles                  := candlesadd1322
htfadd1322.bosdata                  := bosdataadd1322
var CandleSet htfadd1323                     = CandleSet.new()
var CandleSettings SettingsHTFadd1323        = CandleSettings.new(htf='1323',htfint=1323,max_memory=3)
var Candle[] candlesadd1323                  = array.new<Candle>(0)
var BOSdata bosdataadd1323                   = BOSdata.new()
htfadd1323.settings                 := SettingsHTFadd1323
htfadd1323.candles                  := candlesadd1323
htfadd1323.bosdata                  := bosdataadd1323
var CandleSet htfadd1324                     = CandleSet.new()
var CandleSettings SettingsHTFadd1324        = CandleSettings.new(htf='1324',htfint=1324,max_memory=3)
var Candle[] candlesadd1324                  = array.new<Candle>(0)
var BOSdata bosdataadd1324                   = BOSdata.new()
htfadd1324.settings                 := SettingsHTFadd1324
htfadd1324.candles                  := candlesadd1324
htfadd1324.bosdata                  := bosdataadd1324
var CandleSet htfadd1325                     = CandleSet.new()
var CandleSettings SettingsHTFadd1325        = CandleSettings.new(htf='1325',htfint=1325,max_memory=3)
var Candle[] candlesadd1325                  = array.new<Candle>(0)
var BOSdata bosdataadd1325                   = BOSdata.new()
htfadd1325.settings                 := SettingsHTFadd1325
htfadd1325.candles                  := candlesadd1325
htfadd1325.bosdata                  := bosdataadd1325
var CandleSet htfadd1326                     = CandleSet.new()
var CandleSettings SettingsHTFadd1326        = CandleSettings.new(htf='1326',htfint=1326,max_memory=3)
var Candle[] candlesadd1326                  = array.new<Candle>(0)
var BOSdata bosdataadd1326                   = BOSdata.new()
htfadd1326.settings                 := SettingsHTFadd1326
htfadd1326.candles                  := candlesadd1326
htfadd1326.bosdata                  := bosdataadd1326
var CandleSet htfadd1327                     = CandleSet.new()
var CandleSettings SettingsHTFadd1327        = CandleSettings.new(htf='1327',htfint=1327,max_memory=3)
var Candle[] candlesadd1327                  = array.new<Candle>(0)
var BOSdata bosdataadd1327                   = BOSdata.new()
htfadd1327.settings                 := SettingsHTFadd1327
htfadd1327.candles                  := candlesadd1327
htfadd1327.bosdata                  := bosdataadd1327
var CandleSet htfadd1328                     = CandleSet.new()
var CandleSettings SettingsHTFadd1328        = CandleSettings.new(htf='1328',htfint=1328,max_memory=3)
var Candle[] candlesadd1328                  = array.new<Candle>(0)
var BOSdata bosdataadd1328                   = BOSdata.new()
htfadd1328.settings                 := SettingsHTFadd1328
htfadd1328.candles                  := candlesadd1328
htfadd1328.bosdata                  := bosdataadd1328
var CandleSet htfadd1329                     = CandleSet.new()
var CandleSettings SettingsHTFadd1329        = CandleSettings.new(htf='1329',htfint=1329,max_memory=3)
var Candle[] candlesadd1329                  = array.new<Candle>(0)
var BOSdata bosdataadd1329                   = BOSdata.new()
htfadd1329.settings                 := SettingsHTFadd1329
htfadd1329.candles                  := candlesadd1329
htfadd1329.bosdata                  := bosdataadd1329
var CandleSet htfadd1330                     = CandleSet.new()
var CandleSettings SettingsHTFadd1330        = CandleSettings.new(htf='1330',htfint=1330,max_memory=3)
var Candle[] candlesadd1330                  = array.new<Candle>(0)
var BOSdata bosdataadd1330                   = BOSdata.new()
htfadd1330.settings                 := SettingsHTFadd1330
htfadd1330.candles                  := candlesadd1330
htfadd1330.bosdata                  := bosdataadd1330
var CandleSet htfadd1331                     = CandleSet.new()
var CandleSettings SettingsHTFadd1331        = CandleSettings.new(htf='1331',htfint=1331,max_memory=3)
var Candle[] candlesadd1331                  = array.new<Candle>(0)
var BOSdata bosdataadd1331                   = BOSdata.new()
htfadd1331.settings                 := SettingsHTFadd1331
htfadd1331.candles                  := candlesadd1331
htfadd1331.bosdata                  := bosdataadd1331
var CandleSet htfadd1332                     = CandleSet.new()
var CandleSettings SettingsHTFadd1332        = CandleSettings.new(htf='1332',htfint=1332,max_memory=3)
var Candle[] candlesadd1332                  = array.new<Candle>(0)
var BOSdata bosdataadd1332                   = BOSdata.new()
htfadd1332.settings                 := SettingsHTFadd1332
htfadd1332.candles                  := candlesadd1332
htfadd1332.bosdata                  := bosdataadd1332
var CandleSet htfadd1333                     = CandleSet.new()
var CandleSettings SettingsHTFadd1333        = CandleSettings.new(htf='1333',htfint=1333,max_memory=3)
var Candle[] candlesadd1333                  = array.new<Candle>(0)
var BOSdata bosdataadd1333                   = BOSdata.new()
htfadd1333.settings                 := SettingsHTFadd1333
htfadd1333.candles                  := candlesadd1333
htfadd1333.bosdata                  := bosdataadd1333
var CandleSet htfadd1334                     = CandleSet.new()
var CandleSettings SettingsHTFadd1334        = CandleSettings.new(htf='1334',htfint=1334,max_memory=3)
var Candle[] candlesadd1334                  = array.new<Candle>(0)
var BOSdata bosdataadd1334                   = BOSdata.new()
htfadd1334.settings                 := SettingsHTFadd1334
htfadd1334.candles                  := candlesadd1334
htfadd1334.bosdata                  := bosdataadd1334
var CandleSet htfadd1335                     = CandleSet.new()
var CandleSettings SettingsHTFadd1335        = CandleSettings.new(htf='1335',htfint=1335,max_memory=3)
var Candle[] candlesadd1335                  = array.new<Candle>(0)
var BOSdata bosdataadd1335                   = BOSdata.new()
htfadd1335.settings                 := SettingsHTFadd1335
htfadd1335.candles                  := candlesadd1335
htfadd1335.bosdata                  := bosdataadd1335
var CandleSet htfadd1336                     = CandleSet.new()
var CandleSettings SettingsHTFadd1336        = CandleSettings.new(htf='1336',htfint=1336,max_memory=3)
var Candle[] candlesadd1336                  = array.new<Candle>(0)
var BOSdata bosdataadd1336                   = BOSdata.new()
htfadd1336.settings                 := SettingsHTFadd1336
htfadd1336.candles                  := candlesadd1336
htfadd1336.bosdata                  := bosdataadd1336
var CandleSet htfadd1337                     = CandleSet.new()
var CandleSettings SettingsHTFadd1337        = CandleSettings.new(htf='1337',htfint=1337,max_memory=3)
var Candle[] candlesadd1337                  = array.new<Candle>(0)
var BOSdata bosdataadd1337                   = BOSdata.new()
htfadd1337.settings                 := SettingsHTFadd1337
htfadd1337.candles                  := candlesadd1337
htfadd1337.bosdata                  := bosdataadd1337
var CandleSet htfadd1338                     = CandleSet.new()
var CandleSettings SettingsHTFadd1338        = CandleSettings.new(htf='1338',htfint=1338,max_memory=3)
var Candle[] candlesadd1338                  = array.new<Candle>(0)
var BOSdata bosdataadd1338                   = BOSdata.new()
htfadd1338.settings                 := SettingsHTFadd1338
htfadd1338.candles                  := candlesadd1338
htfadd1338.bosdata                  := bosdataadd1338
var CandleSet htfadd1339                     = CandleSet.new()
var CandleSettings SettingsHTFadd1339        = CandleSettings.new(htf='1339',htfint=1339,max_memory=3)
var Candle[] candlesadd1339                  = array.new<Candle>(0)
var BOSdata bosdataadd1339                   = BOSdata.new()
htfadd1339.settings                 := SettingsHTFadd1339
htfadd1339.candles                  := candlesadd1339
htfadd1339.bosdata                  := bosdataadd1339
var CandleSet htfadd1340                     = CandleSet.new()
var CandleSettings SettingsHTFadd1340        = CandleSettings.new(htf='1340',htfint=1340,max_memory=3)
var Candle[] candlesadd1340                  = array.new<Candle>(0)
var BOSdata bosdataadd1340                   = BOSdata.new()
htfadd1340.settings                 := SettingsHTFadd1340
htfadd1340.candles                  := candlesadd1340
htfadd1340.bosdata                  := bosdataadd1340
var CandleSet htfadd1341                     = CandleSet.new()
var CandleSettings SettingsHTFadd1341        = CandleSettings.new(htf='1341',htfint=1341,max_memory=3)
var Candle[] candlesadd1341                  = array.new<Candle>(0)
var BOSdata bosdataadd1341                   = BOSdata.new()
htfadd1341.settings                 := SettingsHTFadd1341
htfadd1341.candles                  := candlesadd1341
htfadd1341.bosdata                  := bosdataadd1341
var CandleSet htfadd1342                     = CandleSet.new()
var CandleSettings SettingsHTFadd1342        = CandleSettings.new(htf='1342',htfint=1342,max_memory=3)
var Candle[] candlesadd1342                  = array.new<Candle>(0)
var BOSdata bosdataadd1342                   = BOSdata.new()
htfadd1342.settings                 := SettingsHTFadd1342
htfadd1342.candles                  := candlesadd1342
htfadd1342.bosdata                  := bosdataadd1342
var CandleSet htfadd1343                     = CandleSet.new()
var CandleSettings SettingsHTFadd1343        = CandleSettings.new(htf='1343',htfint=1343,max_memory=3)
var Candle[] candlesadd1343                  = array.new<Candle>(0)
var BOSdata bosdataadd1343                   = BOSdata.new()
htfadd1343.settings                 := SettingsHTFadd1343
htfadd1343.candles                  := candlesadd1343
htfadd1343.bosdata                  := bosdataadd1343
var CandleSet htfadd1344                     = CandleSet.new()
var CandleSettings SettingsHTFadd1344        = CandleSettings.new(htf='1344',htfint=1344,max_memory=3)
var Candle[] candlesadd1344                  = array.new<Candle>(0)
var BOSdata bosdataadd1344                   = BOSdata.new()
htfadd1344.settings                 := SettingsHTFadd1344
htfadd1344.candles                  := candlesadd1344
htfadd1344.bosdata                  := bosdataadd1344
var CandleSet htfadd1345                     = CandleSet.new()
var CandleSettings SettingsHTFadd1345        = CandleSettings.new(htf='1345',htfint=1345,max_memory=3)
var Candle[] candlesadd1345                  = array.new<Candle>(0)
var BOSdata bosdataadd1345                   = BOSdata.new()
htfadd1345.settings                 := SettingsHTFadd1345
htfadd1345.candles                  := candlesadd1345
htfadd1345.bosdata                  := bosdataadd1345
var CandleSet htfadd1346                     = CandleSet.new()
var CandleSettings SettingsHTFadd1346        = CandleSettings.new(htf='1346',htfint=1346,max_memory=3)
var Candle[] candlesadd1346                  = array.new<Candle>(0)
var BOSdata bosdataadd1346                   = BOSdata.new()
htfadd1346.settings                 := SettingsHTFadd1346
htfadd1346.candles                  := candlesadd1346
htfadd1346.bosdata                  := bosdataadd1346
var CandleSet htfadd1347                     = CandleSet.new()
var CandleSettings SettingsHTFadd1347        = CandleSettings.new(htf='1347',htfint=1347,max_memory=3)
var Candle[] candlesadd1347                  = array.new<Candle>(0)
var BOSdata bosdataadd1347                   = BOSdata.new()
htfadd1347.settings                 := SettingsHTFadd1347
htfadd1347.candles                  := candlesadd1347
htfadd1347.bosdata                  := bosdataadd1347
var CandleSet htfadd1348                     = CandleSet.new()
var CandleSettings SettingsHTFadd1348        = CandleSettings.new(htf='1348',htfint=1348,max_memory=3)
var Candle[] candlesadd1348                  = array.new<Candle>(0)
var BOSdata bosdataadd1348                   = BOSdata.new()
htfadd1348.settings                 := SettingsHTFadd1348
htfadd1348.candles                  := candlesadd1348
htfadd1348.bosdata                  := bosdataadd1348
var CandleSet htfadd1349                     = CandleSet.new()
var CandleSettings SettingsHTFadd1349        = CandleSettings.new(htf='1349',htfint=1349,max_memory=3)
var Candle[] candlesadd1349                  = array.new<Candle>(0)
var BOSdata bosdataadd1349                   = BOSdata.new()
htfadd1349.settings                 := SettingsHTFadd1349
htfadd1349.candles                  := candlesadd1349
htfadd1349.bosdata                  := bosdataadd1349
var CandleSet htfadd1350                     = CandleSet.new()
var CandleSettings SettingsHTFadd1350        = CandleSettings.new(htf='1350',htfint=1350,max_memory=3)
var Candle[] candlesadd1350                  = array.new<Candle>(0)
var BOSdata bosdataadd1350                   = BOSdata.new()
htfadd1350.settings                 := SettingsHTFadd1350
htfadd1350.candles                  := candlesadd1350
htfadd1350.bosdata                  := bosdataadd1350

htfadd1260.Monitor().BOSJudge()
htfadd1261.Monitor().BOSJudge()
htfadd1262.Monitor().BOSJudge()
htfadd1263.Monitor().BOSJudge()
htfadd1264.Monitor().BOSJudge()
htfadd1265.Monitor().BOSJudge()
htfadd1266.Monitor().BOSJudge()
htfadd1267.Monitor().BOSJudge()
htfadd1268.Monitor().BOSJudge()
htfadd1269.Monitor().BOSJudge()
htfadd1270.Monitor().BOSJudge()
htfadd1271.Monitor().BOSJudge()
htfadd1272.Monitor().BOSJudge()
htfadd1273.Monitor().BOSJudge()
htfadd1274.Monitor().BOSJudge()
htfadd1275.Monitor().BOSJudge()
htfadd1276.Monitor().BOSJudge()
htfadd1277.Monitor().BOSJudge()
htfadd1278.Monitor().BOSJudge()
htfadd1279.Monitor().BOSJudge()
htfadd1280.Monitor().BOSJudge()
htfadd1281.Monitor().BOSJudge()
htfadd1282.Monitor().BOSJudge()
htfadd1283.Monitor().BOSJudge()
htfadd1284.Monitor().BOSJudge()
htfadd1285.Monitor().BOSJudge()
htfadd1286.Monitor().BOSJudge()
htfadd1287.Monitor().BOSJudge()
htfadd1288.Monitor().BOSJudge()
htfadd1289.Monitor().BOSJudge()
htfadd1290.Monitor().BOSJudge()
htfadd1291.Monitor().BOSJudge()
htfadd1292.Monitor().BOSJudge()
htfadd1293.Monitor().BOSJudge()
htfadd1294.Monitor().BOSJudge()
htfadd1295.Monitor().BOSJudge()
htfadd1296.Monitor().BOSJudge()
htfadd1297.Monitor().BOSJudge()
htfadd1298.Monitor().BOSJudge()
htfadd1299.Monitor().BOSJudge()
htfadd1300.Monitor().BOSJudge()
htfadd1301.Monitor().BOSJudge()
htfadd1302.Monitor().BOSJudge()
htfadd1303.Monitor().BOSJudge()
htfadd1304.Monitor().BOSJudge()
htfadd1305.Monitor().BOSJudge()
htfadd1306.Monitor().BOSJudge()
htfadd1307.Monitor().BOSJudge()
htfadd1308.Monitor().BOSJudge()
htfadd1309.Monitor().BOSJudge()
htfadd1310.Monitor().BOSJudge()
htfadd1311.Monitor().BOSJudge()
htfadd1312.Monitor().BOSJudge()
htfadd1313.Monitor().BOSJudge()
htfadd1314.Monitor().BOSJudge()
htfadd1315.Monitor().BOSJudge()
htfadd1316.Monitor().BOSJudge()
htfadd1317.Monitor().BOSJudge()
htfadd1318.Monitor().BOSJudge()
htfadd1319.Monitor().BOSJudge()
htfadd1320.Monitor().BOSJudge()
htfadd1321.Monitor().BOSJudge()
htfadd1322.Monitor().BOSJudge()
htfadd1323.Monitor().BOSJudge()
htfadd1324.Monitor().BOSJudge()
htfadd1325.Monitor().BOSJudge()
htfadd1326.Monitor().BOSJudge()
htfadd1327.Monitor().BOSJudge()
htfadd1328.Monitor().BOSJudge()
htfadd1329.Monitor().BOSJudge()
htfadd1330.Monitor().BOSJudge()
htfadd1331.Monitor().BOSJudge()
htfadd1332.Monitor().BOSJudge()
htfadd1333.Monitor().BOSJudge()
htfadd1334.Monitor().BOSJudge()
htfadd1335.Monitor().BOSJudge()
htfadd1336.Monitor().BOSJudge()
htfadd1337.Monitor().BOSJudge()
htfadd1338.Monitor().BOSJudge()
htfadd1339.Monitor().BOSJudge()
htfadd1340.Monitor().BOSJudge()
htfadd1341.Monitor().BOSJudge()
htfadd1342.Monitor().BOSJudge()
htfadd1343.Monitor().BOSJudge()
htfadd1344.Monitor().BOSJudge()
htfadd1345.Monitor().BOSJudge()
htfadd1346.Monitor().BOSJudge()
htfadd1347.Monitor().BOSJudge()
htfadd1348.Monitor().BOSJudge()
htfadd1349.Monitor().BOSJudge()
htfadd1350.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd1260)
    LowestsbuSet(lowestsbu, htfadd1260)
    HighestsbdSet(highestsbd, htfadd1261)
    LowestsbuSet(lowestsbu, htfadd1261)
    HighestsbdSet(highestsbd, htfadd1262)
    LowestsbuSet(lowestsbu, htfadd1262)
    HighestsbdSet(highestsbd, htfadd1263)
    LowestsbuSet(lowestsbu, htfadd1263)
    HighestsbdSet(highestsbd, htfadd1264)
    LowestsbuSet(lowestsbu, htfadd1264)
    HighestsbdSet(highestsbd, htfadd1265)
    LowestsbuSet(lowestsbu, htfadd1265)
    HighestsbdSet(highestsbd, htfadd1266)
    LowestsbuSet(lowestsbu, htfadd1266)
    HighestsbdSet(highestsbd, htfadd1267)
    LowestsbuSet(lowestsbu, htfadd1267)
    HighestsbdSet(highestsbd, htfadd1268)
    LowestsbuSet(lowestsbu, htfadd1268)
    HighestsbdSet(highestsbd, htfadd1269)
    LowestsbuSet(lowestsbu, htfadd1269)
    HighestsbdSet(highestsbd, htfadd1270)
    LowestsbuSet(lowestsbu, htfadd1270)
    HighestsbdSet(highestsbd, htfadd1271)
    LowestsbuSet(lowestsbu, htfadd1271)
    HighestsbdSet(highestsbd, htfadd1272)
    LowestsbuSet(lowestsbu, htfadd1272)
    HighestsbdSet(highestsbd, htfadd1273)
    LowestsbuSet(lowestsbu, htfadd1273)
    HighestsbdSet(highestsbd, htfadd1274)
    LowestsbuSet(lowestsbu, htfadd1274)
    HighestsbdSet(highestsbd, htfadd1275)
    LowestsbuSet(lowestsbu, htfadd1275)
    HighestsbdSet(highestsbd, htfadd1276)
    LowestsbuSet(lowestsbu, htfadd1276)
    HighestsbdSet(highestsbd, htfadd1277)
    LowestsbuSet(lowestsbu, htfadd1277)
    HighestsbdSet(highestsbd, htfadd1278)
    LowestsbuSet(lowestsbu, htfadd1278)
    HighestsbdSet(highestsbd, htfadd1279)
    LowestsbuSet(lowestsbu, htfadd1279)
    HighestsbdSet(highestsbd, htfadd1280)
    LowestsbuSet(lowestsbu, htfadd1280)
    HighestsbdSet(highestsbd, htfadd1281)
    LowestsbuSet(lowestsbu, htfadd1281)
    HighestsbdSet(highestsbd, htfadd1282)
    LowestsbuSet(lowestsbu, htfadd1282)
    HighestsbdSet(highestsbd, htfadd1283)
    LowestsbuSet(lowestsbu, htfadd1283)
    HighestsbdSet(highestsbd, htfadd1284)
    LowestsbuSet(lowestsbu, htfadd1284)
    HighestsbdSet(highestsbd, htfadd1285)
    LowestsbuSet(lowestsbu, htfadd1285)
    HighestsbdSet(highestsbd, htfadd1286)
    LowestsbuSet(lowestsbu, htfadd1286)
    HighestsbdSet(highestsbd, htfadd1287)
    LowestsbuSet(lowestsbu, htfadd1287)
    HighestsbdSet(highestsbd, htfadd1288)
    LowestsbuSet(lowestsbu, htfadd1288)
    HighestsbdSet(highestsbd, htfadd1289)
    LowestsbuSet(lowestsbu, htfadd1289)
    HighestsbdSet(highestsbd, htfadd1290)
    LowestsbuSet(lowestsbu, htfadd1290)
    HighestsbdSet(highestsbd, htfadd1291)
    LowestsbuSet(lowestsbu, htfadd1291)
    HighestsbdSet(highestsbd, htfadd1292)
    LowestsbuSet(lowestsbu, htfadd1292)
    HighestsbdSet(highestsbd, htfadd1293)
    LowestsbuSet(lowestsbu, htfadd1293)
    HighestsbdSet(highestsbd, htfadd1294)
    LowestsbuSet(lowestsbu, htfadd1294)
    HighestsbdSet(highestsbd, htfadd1295)
    LowestsbuSet(lowestsbu, htfadd1295)
    HighestsbdSet(highestsbd, htfadd1296)
    LowestsbuSet(lowestsbu, htfadd1296)
    HighestsbdSet(highestsbd, htfadd1297)
    LowestsbuSet(lowestsbu, htfadd1297)
    HighestsbdSet(highestsbd, htfadd1298)
    LowestsbuSet(lowestsbu, htfadd1298)
    HighestsbdSet(highestsbd, htfadd1299)
    LowestsbuSet(lowestsbu, htfadd1299)
    HighestsbdSet(highestsbd, htfadd1300)
    LowestsbuSet(lowestsbu, htfadd1300)
    HighestsbdSet(highestsbd, htfadd1301)
    LowestsbuSet(lowestsbu, htfadd1301)
    HighestsbdSet(highestsbd, htfadd1302)
    LowestsbuSet(lowestsbu, htfadd1302)
    HighestsbdSet(highestsbd, htfadd1303)
    LowestsbuSet(lowestsbu, htfadd1303)
    HighestsbdSet(highestsbd, htfadd1304)
    LowestsbuSet(lowestsbu, htfadd1304)
    HighestsbdSet(highestsbd, htfadd1305)
    LowestsbuSet(lowestsbu, htfadd1305)
    HighestsbdSet(highestsbd, htfadd1306)
    LowestsbuSet(lowestsbu, htfadd1306)
    HighestsbdSet(highestsbd, htfadd1307)
    LowestsbuSet(lowestsbu, htfadd1307)
    HighestsbdSet(highestsbd, htfadd1308)
    LowestsbuSet(lowestsbu, htfadd1308)
    HighestsbdSet(highestsbd, htfadd1309)
    LowestsbuSet(lowestsbu, htfadd1309)
    HighestsbdSet(highestsbd, htfadd1310)
    LowestsbuSet(lowestsbu, htfadd1310)
    HighestsbdSet(highestsbd, htfadd1311)
    LowestsbuSet(lowestsbu, htfadd1311)
    HighestsbdSet(highestsbd, htfadd1312)
    LowestsbuSet(lowestsbu, htfadd1312)
    HighestsbdSet(highestsbd, htfadd1313)
    LowestsbuSet(lowestsbu, htfadd1313)
    HighestsbdSet(highestsbd, htfadd1314)
    LowestsbuSet(lowestsbu, htfadd1314)
    HighestsbdSet(highestsbd, htfadd1315)
    LowestsbuSet(lowestsbu, htfadd1315)
    HighestsbdSet(highestsbd, htfadd1316)
    LowestsbuSet(lowestsbu, htfadd1316)
    HighestsbdSet(highestsbd, htfadd1317)
    LowestsbuSet(lowestsbu, htfadd1317)
    HighestsbdSet(highestsbd, htfadd1318)
    LowestsbuSet(lowestsbu, htfadd1318)
    HighestsbdSet(highestsbd, htfadd1319)
    LowestsbuSet(lowestsbu, htfadd1319)
    HighestsbdSet(highestsbd, htfadd1320)
    LowestsbuSet(lowestsbu, htfadd1320)
    HighestsbdSet(highestsbd, htfadd1321)
    LowestsbuSet(lowestsbu, htfadd1321)
    HighestsbdSet(highestsbd, htfadd1322)
    LowestsbuSet(lowestsbu, htfadd1322)
    HighestsbdSet(highestsbd, htfadd1323)
    LowestsbuSet(lowestsbu, htfadd1323)
    HighestsbdSet(highestsbd, htfadd1324)
    LowestsbuSet(lowestsbu, htfadd1324)
    HighestsbdSet(highestsbd, htfadd1325)
    LowestsbuSet(lowestsbu, htfadd1325)
    HighestsbdSet(highestsbd, htfadd1326)
    LowestsbuSet(lowestsbu, htfadd1326)
    HighestsbdSet(highestsbd, htfadd1327)
    LowestsbuSet(lowestsbu, htfadd1327)
    HighestsbdSet(highestsbd, htfadd1328)
    LowestsbuSet(lowestsbu, htfadd1328)
    HighestsbdSet(highestsbd, htfadd1329)
    LowestsbuSet(lowestsbu, htfadd1329)
    HighestsbdSet(highestsbd, htfadd1330)
    LowestsbuSet(lowestsbu, htfadd1330)
    HighestsbdSet(highestsbd, htfadd1331)
    LowestsbuSet(lowestsbu, htfadd1331)
    HighestsbdSet(highestsbd, htfadd1332)
    LowestsbuSet(lowestsbu, htfadd1332)
    HighestsbdSet(highestsbd, htfadd1333)
    LowestsbuSet(lowestsbu, htfadd1333)
    HighestsbdSet(highestsbd, htfadd1334)
    LowestsbuSet(lowestsbu, htfadd1334)
    HighestsbdSet(highestsbd, htfadd1335)
    LowestsbuSet(lowestsbu, htfadd1335)
    HighestsbdSet(highestsbd, htfadd1336)
    LowestsbuSet(lowestsbu, htfadd1336)
    HighestsbdSet(highestsbd, htfadd1337)
    LowestsbuSet(lowestsbu, htfadd1337)
    HighestsbdSet(highestsbd, htfadd1338)
    LowestsbuSet(lowestsbu, htfadd1338)
    HighestsbdSet(highestsbd, htfadd1339)
    LowestsbuSet(lowestsbu, htfadd1339)
    HighestsbdSet(highestsbd, htfadd1340)
    LowestsbuSet(lowestsbu, htfadd1340)
    HighestsbdSet(highestsbd, htfadd1341)
    LowestsbuSet(lowestsbu, htfadd1341)
    HighestsbdSet(highestsbd, htfadd1342)
    LowestsbuSet(lowestsbu, htfadd1342)
    HighestsbdSet(highestsbd, htfadd1343)
    LowestsbuSet(lowestsbu, htfadd1343)
    HighestsbdSet(highestsbd, htfadd1344)
    LowestsbuSet(lowestsbu, htfadd1344)
    HighestsbdSet(highestsbd, htfadd1345)
    LowestsbuSet(lowestsbu, htfadd1345)
    HighestsbdSet(highestsbd, htfadd1346)
    LowestsbuSet(lowestsbu, htfadd1346)
    HighestsbdSet(highestsbd, htfadd1347)
    LowestsbuSet(lowestsbu, htfadd1347)
    HighestsbdSet(highestsbd, htfadd1348)
    LowestsbuSet(lowestsbu, htfadd1348)
    HighestsbdSet(highestsbd, htfadd1349)
    LowestsbuSet(lowestsbu, htfadd1349)
    HighestsbdSet(highestsbd, htfadd1350)
    LowestsbuSet(lowestsbu, htfadd1350)

    htfshadow.Shadowing(htfadd1260).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1261).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1262).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1263).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1264).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1265).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1266).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1267).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1268).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1269).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1270).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1271).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1272).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1273).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1274).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1275).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1276).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1277).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1278).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1279).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1280).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1281).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1282).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1283).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1284).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1285).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1286).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1287).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1288).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1289).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1290).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1291).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1292).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1293).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1294).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1295).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1296).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1297).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1298).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1299).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1300).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1301).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1302).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1303).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1304).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1305).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1306).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1307).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1308).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1309).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1310).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1311).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1312).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1313).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1314).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1315).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1316).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1317).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1318).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1319).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1320).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1321).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1322).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1323).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1324).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1325).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1326).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1327).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1328).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1329).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1330).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1331).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1332).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1333).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1334).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1335).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1336).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1337).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1338).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1339).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1340).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1341).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1342).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1343).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1344).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1345).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1346).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1347).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1348).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1349).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1350).Monitor_Est().BOSJudge()
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


