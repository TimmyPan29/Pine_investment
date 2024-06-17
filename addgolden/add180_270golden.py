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
var CandleSet htfadd180                     = CandleSet.new()
var CandleSettings SettingsHTFadd180        = CandleSettings.new(htf='180',htfint=180,max_memory=3)
var Candle[] candlesadd180                  = array.new<Candle>(0)
var BOSdata bosdataadd180                   = BOSdata.new()
htfadd180.settings                 := SettingsHTFadd180
htfadd180.candles                  := candlesadd180
htfadd180.bosdata                  := bosdataadd180
var CandleSet htfadd181                     = CandleSet.new()
var CandleSettings SettingsHTFadd181        = CandleSettings.new(htf='181',htfint=181,max_memory=3)
var Candle[] candlesadd181                  = array.new<Candle>(0)
var BOSdata bosdataadd181                   = BOSdata.new()
htfadd181.settings                 := SettingsHTFadd181
htfadd181.candles                  := candlesadd181
htfadd181.bosdata                  := bosdataadd181
var CandleSet htfadd182                     = CandleSet.new()
var CandleSettings SettingsHTFadd182        = CandleSettings.new(htf='182',htfint=182,max_memory=3)
var Candle[] candlesadd182                  = array.new<Candle>(0)
var BOSdata bosdataadd182                   = BOSdata.new()
htfadd182.settings                 := SettingsHTFadd182
htfadd182.candles                  := candlesadd182
htfadd182.bosdata                  := bosdataadd182
var CandleSet htfadd183                     = CandleSet.new()
var CandleSettings SettingsHTFadd183        = CandleSettings.new(htf='183',htfint=183,max_memory=3)
var Candle[] candlesadd183                  = array.new<Candle>(0)
var BOSdata bosdataadd183                   = BOSdata.new()
htfadd183.settings                 := SettingsHTFadd183
htfadd183.candles                  := candlesadd183
htfadd183.bosdata                  := bosdataadd183
var CandleSet htfadd184                     = CandleSet.new()
var CandleSettings SettingsHTFadd184        = CandleSettings.new(htf='184',htfint=184,max_memory=3)
var Candle[] candlesadd184                  = array.new<Candle>(0)
var BOSdata bosdataadd184                   = BOSdata.new()
htfadd184.settings                 := SettingsHTFadd184
htfadd184.candles                  := candlesadd184
htfadd184.bosdata                  := bosdataadd184
var CandleSet htfadd185                     = CandleSet.new()
var CandleSettings SettingsHTFadd185        = CandleSettings.new(htf='185',htfint=185,max_memory=3)
var Candle[] candlesadd185                  = array.new<Candle>(0)
var BOSdata bosdataadd185                   = BOSdata.new()
htfadd185.settings                 := SettingsHTFadd185
htfadd185.candles                  := candlesadd185
htfadd185.bosdata                  := bosdataadd185
var CandleSet htfadd186                     = CandleSet.new()
var CandleSettings SettingsHTFadd186        = CandleSettings.new(htf='186',htfint=186,max_memory=3)
var Candle[] candlesadd186                  = array.new<Candle>(0)
var BOSdata bosdataadd186                   = BOSdata.new()
htfadd186.settings                 := SettingsHTFadd186
htfadd186.candles                  := candlesadd186
htfadd186.bosdata                  := bosdataadd186
var CandleSet htfadd187                     = CandleSet.new()
var CandleSettings SettingsHTFadd187        = CandleSettings.new(htf='187',htfint=187,max_memory=3)
var Candle[] candlesadd187                  = array.new<Candle>(0)
var BOSdata bosdataadd187                   = BOSdata.new()
htfadd187.settings                 := SettingsHTFadd187
htfadd187.candles                  := candlesadd187
htfadd187.bosdata                  := bosdataadd187
var CandleSet htfadd188                     = CandleSet.new()
var CandleSettings SettingsHTFadd188        = CandleSettings.new(htf='188',htfint=188,max_memory=3)
var Candle[] candlesadd188                  = array.new<Candle>(0)
var BOSdata bosdataadd188                   = BOSdata.new()
htfadd188.settings                 := SettingsHTFadd188
htfadd188.candles                  := candlesadd188
htfadd188.bosdata                  := bosdataadd188
var CandleSet htfadd189                     = CandleSet.new()
var CandleSettings SettingsHTFadd189        = CandleSettings.new(htf='189',htfint=189,max_memory=3)
var Candle[] candlesadd189                  = array.new<Candle>(0)
var BOSdata bosdataadd189                   = BOSdata.new()
htfadd189.settings                 := SettingsHTFadd189
htfadd189.candles                  := candlesadd189
htfadd189.bosdata                  := bosdataadd189
var CandleSet htfadd190                     = CandleSet.new()
var CandleSettings SettingsHTFadd190        = CandleSettings.new(htf='190',htfint=190,max_memory=3)
var Candle[] candlesadd190                  = array.new<Candle>(0)
var BOSdata bosdataadd190                   = BOSdata.new()
htfadd190.settings                 := SettingsHTFadd190
htfadd190.candles                  := candlesadd190
htfadd190.bosdata                  := bosdataadd190
var CandleSet htfadd191                     = CandleSet.new()
var CandleSettings SettingsHTFadd191        = CandleSettings.new(htf='191',htfint=191,max_memory=3)
var Candle[] candlesadd191                  = array.new<Candle>(0)
var BOSdata bosdataadd191                   = BOSdata.new()
htfadd191.settings                 := SettingsHTFadd191
htfadd191.candles                  := candlesadd191
htfadd191.bosdata                  := bosdataadd191
var CandleSet htfadd192                     = CandleSet.new()
var CandleSettings SettingsHTFadd192        = CandleSettings.new(htf='192',htfint=192,max_memory=3)
var Candle[] candlesadd192                  = array.new<Candle>(0)
var BOSdata bosdataadd192                   = BOSdata.new()
htfadd192.settings                 := SettingsHTFadd192
htfadd192.candles                  := candlesadd192
htfadd192.bosdata                  := bosdataadd192
var CandleSet htfadd193                     = CandleSet.new()
var CandleSettings SettingsHTFadd193        = CandleSettings.new(htf='193',htfint=193,max_memory=3)
var Candle[] candlesadd193                  = array.new<Candle>(0)
var BOSdata bosdataadd193                   = BOSdata.new()
htfadd193.settings                 := SettingsHTFadd193
htfadd193.candles                  := candlesadd193
htfadd193.bosdata                  := bosdataadd193
var CandleSet htfadd194                     = CandleSet.new()
var CandleSettings SettingsHTFadd194        = CandleSettings.new(htf='194',htfint=194,max_memory=3)
var Candle[] candlesadd194                  = array.new<Candle>(0)
var BOSdata bosdataadd194                   = BOSdata.new()
htfadd194.settings                 := SettingsHTFadd194
htfadd194.candles                  := candlesadd194
htfadd194.bosdata                  := bosdataadd194
var CandleSet htfadd195                     = CandleSet.new()
var CandleSettings SettingsHTFadd195        = CandleSettings.new(htf='195',htfint=195,max_memory=3)
var Candle[] candlesadd195                  = array.new<Candle>(0)
var BOSdata bosdataadd195                   = BOSdata.new()
htfadd195.settings                 := SettingsHTFadd195
htfadd195.candles                  := candlesadd195
htfadd195.bosdata                  := bosdataadd195
var CandleSet htfadd196                     = CandleSet.new()
var CandleSettings SettingsHTFadd196        = CandleSettings.new(htf='196',htfint=196,max_memory=3)
var Candle[] candlesadd196                  = array.new<Candle>(0)
var BOSdata bosdataadd196                   = BOSdata.new()
htfadd196.settings                 := SettingsHTFadd196
htfadd196.candles                  := candlesadd196
htfadd196.bosdata                  := bosdataadd196
var CandleSet htfadd197                     = CandleSet.new()
var CandleSettings SettingsHTFadd197        = CandleSettings.new(htf='197',htfint=197,max_memory=3)
var Candle[] candlesadd197                  = array.new<Candle>(0)
var BOSdata bosdataadd197                   = BOSdata.new()
htfadd197.settings                 := SettingsHTFadd197
htfadd197.candles                  := candlesadd197
htfadd197.bosdata                  := bosdataadd197
var CandleSet htfadd198                     = CandleSet.new()
var CandleSettings SettingsHTFadd198        = CandleSettings.new(htf='198',htfint=198,max_memory=3)
var Candle[] candlesadd198                  = array.new<Candle>(0)
var BOSdata bosdataadd198                   = BOSdata.new()
htfadd198.settings                 := SettingsHTFadd198
htfadd198.candles                  := candlesadd198
htfadd198.bosdata                  := bosdataadd198
var CandleSet htfadd199                     = CandleSet.new()
var CandleSettings SettingsHTFadd199        = CandleSettings.new(htf='199',htfint=199,max_memory=3)
var Candle[] candlesadd199                  = array.new<Candle>(0)
var BOSdata bosdataadd199                   = BOSdata.new()
htfadd199.settings                 := SettingsHTFadd199
htfadd199.candles                  := candlesadd199
htfadd199.bosdata                  := bosdataadd199
var CandleSet htfadd200                     = CandleSet.new()
var CandleSettings SettingsHTFadd200        = CandleSettings.new(htf='200',htfint=200,max_memory=3)
var Candle[] candlesadd200                  = array.new<Candle>(0)
var BOSdata bosdataadd200                   = BOSdata.new()
htfadd200.settings                 := SettingsHTFadd200
htfadd200.candles                  := candlesadd200
htfadd200.bosdata                  := bosdataadd200
var CandleSet htfadd201                     = CandleSet.new()
var CandleSettings SettingsHTFadd201        = CandleSettings.new(htf='201',htfint=201,max_memory=3)
var Candle[] candlesadd201                  = array.new<Candle>(0)
var BOSdata bosdataadd201                   = BOSdata.new()
htfadd201.settings                 := SettingsHTFadd201
htfadd201.candles                  := candlesadd201
htfadd201.bosdata                  := bosdataadd201
var CandleSet htfadd202                     = CandleSet.new()
var CandleSettings SettingsHTFadd202        = CandleSettings.new(htf='202',htfint=202,max_memory=3)
var Candle[] candlesadd202                  = array.new<Candle>(0)
var BOSdata bosdataadd202                   = BOSdata.new()
htfadd202.settings                 := SettingsHTFadd202
htfadd202.candles                  := candlesadd202
htfadd202.bosdata                  := bosdataadd202
var CandleSet htfadd203                     = CandleSet.new()
var CandleSettings SettingsHTFadd203        = CandleSettings.new(htf='203',htfint=203,max_memory=3)
var Candle[] candlesadd203                  = array.new<Candle>(0)
var BOSdata bosdataadd203                   = BOSdata.new()
htfadd203.settings                 := SettingsHTFadd203
htfadd203.candles                  := candlesadd203
htfadd203.bosdata                  := bosdataadd203
var CandleSet htfadd204                     = CandleSet.new()
var CandleSettings SettingsHTFadd204        = CandleSettings.new(htf='204',htfint=204,max_memory=3)
var Candle[] candlesadd204                  = array.new<Candle>(0)
var BOSdata bosdataadd204                   = BOSdata.new()
htfadd204.settings                 := SettingsHTFadd204
htfadd204.candles                  := candlesadd204
htfadd204.bosdata                  := bosdataadd204
var CandleSet htfadd205                     = CandleSet.new()
var CandleSettings SettingsHTFadd205        = CandleSettings.new(htf='205',htfint=205,max_memory=3)
var Candle[] candlesadd205                  = array.new<Candle>(0)
var BOSdata bosdataadd205                   = BOSdata.new()
htfadd205.settings                 := SettingsHTFadd205
htfadd205.candles                  := candlesadd205
htfadd205.bosdata                  := bosdataadd205
var CandleSet htfadd206                     = CandleSet.new()
var CandleSettings SettingsHTFadd206        = CandleSettings.new(htf='206',htfint=206,max_memory=3)
var Candle[] candlesadd206                  = array.new<Candle>(0)
var BOSdata bosdataadd206                   = BOSdata.new()
htfadd206.settings                 := SettingsHTFadd206
htfadd206.candles                  := candlesadd206
htfadd206.bosdata                  := bosdataadd206
var CandleSet htfadd207                     = CandleSet.new()
var CandleSettings SettingsHTFadd207        = CandleSettings.new(htf='207',htfint=207,max_memory=3)
var Candle[] candlesadd207                  = array.new<Candle>(0)
var BOSdata bosdataadd207                   = BOSdata.new()
htfadd207.settings                 := SettingsHTFadd207
htfadd207.candles                  := candlesadd207
htfadd207.bosdata                  := bosdataadd207
var CandleSet htfadd208                     = CandleSet.new()
var CandleSettings SettingsHTFadd208        = CandleSettings.new(htf='208',htfint=208,max_memory=3)
var Candle[] candlesadd208                  = array.new<Candle>(0)
var BOSdata bosdataadd208                   = BOSdata.new()
htfadd208.settings                 := SettingsHTFadd208
htfadd208.candles                  := candlesadd208
htfadd208.bosdata                  := bosdataadd208
var CandleSet htfadd209                     = CandleSet.new()
var CandleSettings SettingsHTFadd209        = CandleSettings.new(htf='209',htfint=209,max_memory=3)
var Candle[] candlesadd209                  = array.new<Candle>(0)
var BOSdata bosdataadd209                   = BOSdata.new()
htfadd209.settings                 := SettingsHTFadd209
htfadd209.candles                  := candlesadd209
htfadd209.bosdata                  := bosdataadd209
var CandleSet htfadd210                     = CandleSet.new()
var CandleSettings SettingsHTFadd210        = CandleSettings.new(htf='210',htfint=210,max_memory=3)
var Candle[] candlesadd210                  = array.new<Candle>(0)
var BOSdata bosdataadd210                   = BOSdata.new()
htfadd210.settings                 := SettingsHTFadd210
htfadd210.candles                  := candlesadd210
htfadd210.bosdata                  := bosdataadd210
var CandleSet htfadd211                     = CandleSet.new()
var CandleSettings SettingsHTFadd211        = CandleSettings.new(htf='211',htfint=211,max_memory=3)
var Candle[] candlesadd211                  = array.new<Candle>(0)
var BOSdata bosdataadd211                   = BOSdata.new()
htfadd211.settings                 := SettingsHTFadd211
htfadd211.candles                  := candlesadd211
htfadd211.bosdata                  := bosdataadd211
var CandleSet htfadd212                     = CandleSet.new()
var CandleSettings SettingsHTFadd212        = CandleSettings.new(htf='212',htfint=212,max_memory=3)
var Candle[] candlesadd212                  = array.new<Candle>(0)
var BOSdata bosdataadd212                   = BOSdata.new()
htfadd212.settings                 := SettingsHTFadd212
htfadd212.candles                  := candlesadd212
htfadd212.bosdata                  := bosdataadd212
var CandleSet htfadd213                     = CandleSet.new()
var CandleSettings SettingsHTFadd213        = CandleSettings.new(htf='213',htfint=213,max_memory=3)
var Candle[] candlesadd213                  = array.new<Candle>(0)
var BOSdata bosdataadd213                   = BOSdata.new()
htfadd213.settings                 := SettingsHTFadd213
htfadd213.candles                  := candlesadd213
htfadd213.bosdata                  := bosdataadd213
var CandleSet htfadd214                     = CandleSet.new()
var CandleSettings SettingsHTFadd214        = CandleSettings.new(htf='214',htfint=214,max_memory=3)
var Candle[] candlesadd214                  = array.new<Candle>(0)
var BOSdata bosdataadd214                   = BOSdata.new()
htfadd214.settings                 := SettingsHTFadd214
htfadd214.candles                  := candlesadd214
htfadd214.bosdata                  := bosdataadd214
var CandleSet htfadd215                     = CandleSet.new()
var CandleSettings SettingsHTFadd215        = CandleSettings.new(htf='215',htfint=215,max_memory=3)
var Candle[] candlesadd215                  = array.new<Candle>(0)
var BOSdata bosdataadd215                   = BOSdata.new()
htfadd215.settings                 := SettingsHTFadd215
htfadd215.candles                  := candlesadd215
htfadd215.bosdata                  := bosdataadd215
var CandleSet htfadd216                     = CandleSet.new()
var CandleSettings SettingsHTFadd216        = CandleSettings.new(htf='216',htfint=216,max_memory=3)
var Candle[] candlesadd216                  = array.new<Candle>(0)
var BOSdata bosdataadd216                   = BOSdata.new()
htfadd216.settings                 := SettingsHTFadd216
htfadd216.candles                  := candlesadd216
htfadd216.bosdata                  := bosdataadd216
var CandleSet htfadd217                     = CandleSet.new()
var CandleSettings SettingsHTFadd217        = CandleSettings.new(htf='217',htfint=217,max_memory=3)
var Candle[] candlesadd217                  = array.new<Candle>(0)
var BOSdata bosdataadd217                   = BOSdata.new()
htfadd217.settings                 := SettingsHTFadd217
htfadd217.candles                  := candlesadd217
htfadd217.bosdata                  := bosdataadd217
var CandleSet htfadd218                     = CandleSet.new()
var CandleSettings SettingsHTFadd218        = CandleSettings.new(htf='218',htfint=218,max_memory=3)
var Candle[] candlesadd218                  = array.new<Candle>(0)
var BOSdata bosdataadd218                   = BOSdata.new()
htfadd218.settings                 := SettingsHTFadd218
htfadd218.candles                  := candlesadd218
htfadd218.bosdata                  := bosdataadd218
var CandleSet htfadd219                     = CandleSet.new()
var CandleSettings SettingsHTFadd219        = CandleSettings.new(htf='219',htfint=219,max_memory=3)
var Candle[] candlesadd219                  = array.new<Candle>(0)
var BOSdata bosdataadd219                   = BOSdata.new()
htfadd219.settings                 := SettingsHTFadd219
htfadd219.candles                  := candlesadd219
htfadd219.bosdata                  := bosdataadd219
var CandleSet htfadd220                     = CandleSet.new()
var CandleSettings SettingsHTFadd220        = CandleSettings.new(htf='220',htfint=220,max_memory=3)
var Candle[] candlesadd220                  = array.new<Candle>(0)
var BOSdata bosdataadd220                   = BOSdata.new()
htfadd220.settings                 := SettingsHTFadd220
htfadd220.candles                  := candlesadd220
htfadd220.bosdata                  := bosdataadd220
var CandleSet htfadd221                     = CandleSet.new()
var CandleSettings SettingsHTFadd221        = CandleSettings.new(htf='221',htfint=221,max_memory=3)
var Candle[] candlesadd221                  = array.new<Candle>(0)
var BOSdata bosdataadd221                   = BOSdata.new()
htfadd221.settings                 := SettingsHTFadd221
htfadd221.candles                  := candlesadd221
htfadd221.bosdata                  := bosdataadd221
var CandleSet htfadd222                     = CandleSet.new()
var CandleSettings SettingsHTFadd222        = CandleSettings.new(htf='222',htfint=222,max_memory=3)
var Candle[] candlesadd222                  = array.new<Candle>(0)
var BOSdata bosdataadd222                   = BOSdata.new()
htfadd222.settings                 := SettingsHTFadd222
htfadd222.candles                  := candlesadd222
htfadd222.bosdata                  := bosdataadd222
var CandleSet htfadd223                     = CandleSet.new()
var CandleSettings SettingsHTFadd223        = CandleSettings.new(htf='223',htfint=223,max_memory=3)
var Candle[] candlesadd223                  = array.new<Candle>(0)
var BOSdata bosdataadd223                   = BOSdata.new()
htfadd223.settings                 := SettingsHTFadd223
htfadd223.candles                  := candlesadd223
htfadd223.bosdata                  := bosdataadd223
var CandleSet htfadd224                     = CandleSet.new()
var CandleSettings SettingsHTFadd224        = CandleSettings.new(htf='224',htfint=224,max_memory=3)
var Candle[] candlesadd224                  = array.new<Candle>(0)
var BOSdata bosdataadd224                   = BOSdata.new()
htfadd224.settings                 := SettingsHTFadd224
htfadd224.candles                  := candlesadd224
htfadd224.bosdata                  := bosdataadd224
var CandleSet htfadd225                     = CandleSet.new()
var CandleSettings SettingsHTFadd225        = CandleSettings.new(htf='225',htfint=225,max_memory=3)
var Candle[] candlesadd225                  = array.new<Candle>(0)
var BOSdata bosdataadd225                   = BOSdata.new()
htfadd225.settings                 := SettingsHTFadd225
htfadd225.candles                  := candlesadd225
htfadd225.bosdata                  := bosdataadd225
var CandleSet htfadd226                     = CandleSet.new()
var CandleSettings SettingsHTFadd226        = CandleSettings.new(htf='226',htfint=226,max_memory=3)
var Candle[] candlesadd226                  = array.new<Candle>(0)
var BOSdata bosdataadd226                   = BOSdata.new()
htfadd226.settings                 := SettingsHTFadd226
htfadd226.candles                  := candlesadd226
htfadd226.bosdata                  := bosdataadd226
var CandleSet htfadd227                     = CandleSet.new()
var CandleSettings SettingsHTFadd227        = CandleSettings.new(htf='227',htfint=227,max_memory=3)
var Candle[] candlesadd227                  = array.new<Candle>(0)
var BOSdata bosdataadd227                   = BOSdata.new()
htfadd227.settings                 := SettingsHTFadd227
htfadd227.candles                  := candlesadd227
htfadd227.bosdata                  := bosdataadd227
var CandleSet htfadd228                     = CandleSet.new()
var CandleSettings SettingsHTFadd228        = CandleSettings.new(htf='228',htfint=228,max_memory=3)
var Candle[] candlesadd228                  = array.new<Candle>(0)
var BOSdata bosdataadd228                   = BOSdata.new()
htfadd228.settings                 := SettingsHTFadd228
htfadd228.candles                  := candlesadd228
htfadd228.bosdata                  := bosdataadd228
var CandleSet htfadd229                     = CandleSet.new()
var CandleSettings SettingsHTFadd229        = CandleSettings.new(htf='229',htfint=229,max_memory=3)
var Candle[] candlesadd229                  = array.new<Candle>(0)
var BOSdata bosdataadd229                   = BOSdata.new()
htfadd229.settings                 := SettingsHTFadd229
htfadd229.candles                  := candlesadd229
htfadd229.bosdata                  := bosdataadd229
var CandleSet htfadd230                     = CandleSet.new()
var CandleSettings SettingsHTFadd230        = CandleSettings.new(htf='230',htfint=230,max_memory=3)
var Candle[] candlesadd230                  = array.new<Candle>(0)
var BOSdata bosdataadd230                   = BOSdata.new()
htfadd230.settings                 := SettingsHTFadd230
htfadd230.candles                  := candlesadd230
htfadd230.bosdata                  := bosdataadd230
var CandleSet htfadd231                     = CandleSet.new()
var CandleSettings SettingsHTFadd231        = CandleSettings.new(htf='231',htfint=231,max_memory=3)
var Candle[] candlesadd231                  = array.new<Candle>(0)
var BOSdata bosdataadd231                   = BOSdata.new()
htfadd231.settings                 := SettingsHTFadd231
htfadd231.candles                  := candlesadd231
htfadd231.bosdata                  := bosdataadd231
var CandleSet htfadd232                     = CandleSet.new()
var CandleSettings SettingsHTFadd232        = CandleSettings.new(htf='232',htfint=232,max_memory=3)
var Candle[] candlesadd232                  = array.new<Candle>(0)
var BOSdata bosdataadd232                   = BOSdata.new()
htfadd232.settings                 := SettingsHTFadd232
htfadd232.candles                  := candlesadd232
htfadd232.bosdata                  := bosdataadd232
var CandleSet htfadd233                     = CandleSet.new()
var CandleSettings SettingsHTFadd233        = CandleSettings.new(htf='233',htfint=233,max_memory=3)
var Candle[] candlesadd233                  = array.new<Candle>(0)
var BOSdata bosdataadd233                   = BOSdata.new()
htfadd233.settings                 := SettingsHTFadd233
htfadd233.candles                  := candlesadd233
htfadd233.bosdata                  := bosdataadd233
var CandleSet htfadd234                     = CandleSet.new()
var CandleSettings SettingsHTFadd234        = CandleSettings.new(htf='234',htfint=234,max_memory=3)
var Candle[] candlesadd234                  = array.new<Candle>(0)
var BOSdata bosdataadd234                   = BOSdata.new()
htfadd234.settings                 := SettingsHTFadd234
htfadd234.candles                  := candlesadd234
htfadd234.bosdata                  := bosdataadd234
var CandleSet htfadd235                     = CandleSet.new()
var CandleSettings SettingsHTFadd235        = CandleSettings.new(htf='235',htfint=235,max_memory=3)
var Candle[] candlesadd235                  = array.new<Candle>(0)
var BOSdata bosdataadd235                   = BOSdata.new()
htfadd235.settings                 := SettingsHTFadd235
htfadd235.candles                  := candlesadd235
htfadd235.bosdata                  := bosdataadd235
var CandleSet htfadd236                     = CandleSet.new()
var CandleSettings SettingsHTFadd236        = CandleSettings.new(htf='236',htfint=236,max_memory=3)
var Candle[] candlesadd236                  = array.new<Candle>(0)
var BOSdata bosdataadd236                   = BOSdata.new()
htfadd236.settings                 := SettingsHTFadd236
htfadd236.candles                  := candlesadd236
htfadd236.bosdata                  := bosdataadd236
var CandleSet htfadd237                     = CandleSet.new()
var CandleSettings SettingsHTFadd237        = CandleSettings.new(htf='237',htfint=237,max_memory=3)
var Candle[] candlesadd237                  = array.new<Candle>(0)
var BOSdata bosdataadd237                   = BOSdata.new()
htfadd237.settings                 := SettingsHTFadd237
htfadd237.candles                  := candlesadd237
htfadd237.bosdata                  := bosdataadd237
var CandleSet htfadd238                     = CandleSet.new()
var CandleSettings SettingsHTFadd238        = CandleSettings.new(htf='238',htfint=238,max_memory=3)
var Candle[] candlesadd238                  = array.new<Candle>(0)
var BOSdata bosdataadd238                   = BOSdata.new()
htfadd238.settings                 := SettingsHTFadd238
htfadd238.candles                  := candlesadd238
htfadd238.bosdata                  := bosdataadd238
var CandleSet htfadd239                     = CandleSet.new()
var CandleSettings SettingsHTFadd239        = CandleSettings.new(htf='239',htfint=239,max_memory=3)
var Candle[] candlesadd239                  = array.new<Candle>(0)
var BOSdata bosdataadd239                   = BOSdata.new()
htfadd239.settings                 := SettingsHTFadd239
htfadd239.candles                  := candlesadd239
htfadd239.bosdata                  := bosdataadd239
var CandleSet htfadd240                     = CandleSet.new()
var CandleSettings SettingsHTFadd240        = CandleSettings.new(htf='240',htfint=240,max_memory=3)
var Candle[] candlesadd240                  = array.new<Candle>(0)
var BOSdata bosdataadd240                   = BOSdata.new()
htfadd240.settings                 := SettingsHTFadd240
htfadd240.candles                  := candlesadd240
htfadd240.bosdata                  := bosdataadd240
var CandleSet htfadd241                     = CandleSet.new()
var CandleSettings SettingsHTFadd241        = CandleSettings.new(htf='241',htfint=241,max_memory=3)
var Candle[] candlesadd241                  = array.new<Candle>(0)
var BOSdata bosdataadd241                   = BOSdata.new()
htfadd241.settings                 := SettingsHTFadd241
htfadd241.candles                  := candlesadd241
htfadd241.bosdata                  := bosdataadd241
var CandleSet htfadd242                     = CandleSet.new()
var CandleSettings SettingsHTFadd242        = CandleSettings.new(htf='242',htfint=242,max_memory=3)
var Candle[] candlesadd242                  = array.new<Candle>(0)
var BOSdata bosdataadd242                   = BOSdata.new()
htfadd242.settings                 := SettingsHTFadd242
htfadd242.candles                  := candlesadd242
htfadd242.bosdata                  := bosdataadd242
var CandleSet htfadd243                     = CandleSet.new()
var CandleSettings SettingsHTFadd243        = CandleSettings.new(htf='243',htfint=243,max_memory=3)
var Candle[] candlesadd243                  = array.new<Candle>(0)
var BOSdata bosdataadd243                   = BOSdata.new()
htfadd243.settings                 := SettingsHTFadd243
htfadd243.candles                  := candlesadd243
htfadd243.bosdata                  := bosdataadd243
var CandleSet htfadd244                     = CandleSet.new()
var CandleSettings SettingsHTFadd244        = CandleSettings.new(htf='244',htfint=244,max_memory=3)
var Candle[] candlesadd244                  = array.new<Candle>(0)
var BOSdata bosdataadd244                   = BOSdata.new()
htfadd244.settings                 := SettingsHTFadd244
htfadd244.candles                  := candlesadd244
htfadd244.bosdata                  := bosdataadd244
var CandleSet htfadd245                     = CandleSet.new()
var CandleSettings SettingsHTFadd245        = CandleSettings.new(htf='245',htfint=245,max_memory=3)
var Candle[] candlesadd245                  = array.new<Candle>(0)
var BOSdata bosdataadd245                   = BOSdata.new()
htfadd245.settings                 := SettingsHTFadd245
htfadd245.candles                  := candlesadd245
htfadd245.bosdata                  := bosdataadd245
var CandleSet htfadd246                     = CandleSet.new()
var CandleSettings SettingsHTFadd246        = CandleSettings.new(htf='246',htfint=246,max_memory=3)
var Candle[] candlesadd246                  = array.new<Candle>(0)
var BOSdata bosdataadd246                   = BOSdata.new()
htfadd246.settings                 := SettingsHTFadd246
htfadd246.candles                  := candlesadd246
htfadd246.bosdata                  := bosdataadd246
var CandleSet htfadd247                     = CandleSet.new()
var CandleSettings SettingsHTFadd247        = CandleSettings.new(htf='247',htfint=247,max_memory=3)
var Candle[] candlesadd247                  = array.new<Candle>(0)
var BOSdata bosdataadd247                   = BOSdata.new()
htfadd247.settings                 := SettingsHTFadd247
htfadd247.candles                  := candlesadd247
htfadd247.bosdata                  := bosdataadd247
var CandleSet htfadd248                     = CandleSet.new()
var CandleSettings SettingsHTFadd248        = CandleSettings.new(htf='248',htfint=248,max_memory=3)
var Candle[] candlesadd248                  = array.new<Candle>(0)
var BOSdata bosdataadd248                   = BOSdata.new()
htfadd248.settings                 := SettingsHTFadd248
htfadd248.candles                  := candlesadd248
htfadd248.bosdata                  := bosdataadd248
var CandleSet htfadd249                     = CandleSet.new()
var CandleSettings SettingsHTFadd249        = CandleSettings.new(htf='249',htfint=249,max_memory=3)
var Candle[] candlesadd249                  = array.new<Candle>(0)
var BOSdata bosdataadd249                   = BOSdata.new()
htfadd249.settings                 := SettingsHTFadd249
htfadd249.candles                  := candlesadd249
htfadd249.bosdata                  := bosdataadd249
var CandleSet htfadd250                     = CandleSet.new()
var CandleSettings SettingsHTFadd250        = CandleSettings.new(htf='250',htfint=250,max_memory=3)
var Candle[] candlesadd250                  = array.new<Candle>(0)
var BOSdata bosdataadd250                   = BOSdata.new()
htfadd250.settings                 := SettingsHTFadd250
htfadd250.candles                  := candlesadd250
htfadd250.bosdata                  := bosdataadd250
var CandleSet htfadd251                     = CandleSet.new()
var CandleSettings SettingsHTFadd251        = CandleSettings.new(htf='251',htfint=251,max_memory=3)
var Candle[] candlesadd251                  = array.new<Candle>(0)
var BOSdata bosdataadd251                   = BOSdata.new()
htfadd251.settings                 := SettingsHTFadd251
htfadd251.candles                  := candlesadd251
htfadd251.bosdata                  := bosdataadd251
var CandleSet htfadd252                     = CandleSet.new()
var CandleSettings SettingsHTFadd252        = CandleSettings.new(htf='252',htfint=252,max_memory=3)
var Candle[] candlesadd252                  = array.new<Candle>(0)
var BOSdata bosdataadd252                   = BOSdata.new()
htfadd252.settings                 := SettingsHTFadd252
htfadd252.candles                  := candlesadd252
htfadd252.bosdata                  := bosdataadd252
var CandleSet htfadd253                     = CandleSet.new()
var CandleSettings SettingsHTFadd253        = CandleSettings.new(htf='253',htfint=253,max_memory=3)
var Candle[] candlesadd253                  = array.new<Candle>(0)
var BOSdata bosdataadd253                   = BOSdata.new()
htfadd253.settings                 := SettingsHTFadd253
htfadd253.candles                  := candlesadd253
htfadd253.bosdata                  := bosdataadd253
var CandleSet htfadd254                     = CandleSet.new()
var CandleSettings SettingsHTFadd254        = CandleSettings.new(htf='254',htfint=254,max_memory=3)
var Candle[] candlesadd254                  = array.new<Candle>(0)
var BOSdata bosdataadd254                   = BOSdata.new()
htfadd254.settings                 := SettingsHTFadd254
htfadd254.candles                  := candlesadd254
htfadd254.bosdata                  := bosdataadd254
var CandleSet htfadd255                     = CandleSet.new()
var CandleSettings SettingsHTFadd255        = CandleSettings.new(htf='255',htfint=255,max_memory=3)
var Candle[] candlesadd255                  = array.new<Candle>(0)
var BOSdata bosdataadd255                   = BOSdata.new()
htfadd255.settings                 := SettingsHTFadd255
htfadd255.candles                  := candlesadd255
htfadd255.bosdata                  := bosdataadd255
var CandleSet htfadd256                     = CandleSet.new()
var CandleSettings SettingsHTFadd256        = CandleSettings.new(htf='256',htfint=256,max_memory=3)
var Candle[] candlesadd256                  = array.new<Candle>(0)
var BOSdata bosdataadd256                   = BOSdata.new()
htfadd256.settings                 := SettingsHTFadd256
htfadd256.candles                  := candlesadd256
htfadd256.bosdata                  := bosdataadd256
var CandleSet htfadd257                     = CandleSet.new()
var CandleSettings SettingsHTFadd257        = CandleSettings.new(htf='257',htfint=257,max_memory=3)
var Candle[] candlesadd257                  = array.new<Candle>(0)
var BOSdata bosdataadd257                   = BOSdata.new()
htfadd257.settings                 := SettingsHTFadd257
htfadd257.candles                  := candlesadd257
htfadd257.bosdata                  := bosdataadd257
var CandleSet htfadd258                     = CandleSet.new()
var CandleSettings SettingsHTFadd258        = CandleSettings.new(htf='258',htfint=258,max_memory=3)
var Candle[] candlesadd258                  = array.new<Candle>(0)
var BOSdata bosdataadd258                   = BOSdata.new()
htfadd258.settings                 := SettingsHTFadd258
htfadd258.candles                  := candlesadd258
htfadd258.bosdata                  := bosdataadd258
var CandleSet htfadd259                     = CandleSet.new()
var CandleSettings SettingsHTFadd259        = CandleSettings.new(htf='259',htfint=259,max_memory=3)
var Candle[] candlesadd259                  = array.new<Candle>(0)
var BOSdata bosdataadd259                   = BOSdata.new()
htfadd259.settings                 := SettingsHTFadd259
htfadd259.candles                  := candlesadd259
htfadd259.bosdata                  := bosdataadd259
var CandleSet htfadd260                     = CandleSet.new()
var CandleSettings SettingsHTFadd260        = CandleSettings.new(htf='260',htfint=260,max_memory=3)
var Candle[] candlesadd260                  = array.new<Candle>(0)
var BOSdata bosdataadd260                   = BOSdata.new()
htfadd260.settings                 := SettingsHTFadd260
htfadd260.candles                  := candlesadd260
htfadd260.bosdata                  := bosdataadd260
var CandleSet htfadd261                     = CandleSet.new()
var CandleSettings SettingsHTFadd261        = CandleSettings.new(htf='261',htfint=261,max_memory=3)
var Candle[] candlesadd261                  = array.new<Candle>(0)
var BOSdata bosdataadd261                   = BOSdata.new()
htfadd261.settings                 := SettingsHTFadd261
htfadd261.candles                  := candlesadd261
htfadd261.bosdata                  := bosdataadd261
var CandleSet htfadd262                     = CandleSet.new()
var CandleSettings SettingsHTFadd262        = CandleSettings.new(htf='262',htfint=262,max_memory=3)
var Candle[] candlesadd262                  = array.new<Candle>(0)
var BOSdata bosdataadd262                   = BOSdata.new()
htfadd262.settings                 := SettingsHTFadd262
htfadd262.candles                  := candlesadd262
htfadd262.bosdata                  := bosdataadd262
var CandleSet htfadd263                     = CandleSet.new()
var CandleSettings SettingsHTFadd263        = CandleSettings.new(htf='263',htfint=263,max_memory=3)
var Candle[] candlesadd263                  = array.new<Candle>(0)
var BOSdata bosdataadd263                   = BOSdata.new()
htfadd263.settings                 := SettingsHTFadd263
htfadd263.candles                  := candlesadd263
htfadd263.bosdata                  := bosdataadd263
var CandleSet htfadd264                     = CandleSet.new()
var CandleSettings SettingsHTFadd264        = CandleSettings.new(htf='264',htfint=264,max_memory=3)
var Candle[] candlesadd264                  = array.new<Candle>(0)
var BOSdata bosdataadd264                   = BOSdata.new()
htfadd264.settings                 := SettingsHTFadd264
htfadd264.candles                  := candlesadd264
htfadd264.bosdata                  := bosdataadd264
var CandleSet htfadd265                     = CandleSet.new()
var CandleSettings SettingsHTFadd265        = CandleSettings.new(htf='265',htfint=265,max_memory=3)
var Candle[] candlesadd265                  = array.new<Candle>(0)
var BOSdata bosdataadd265                   = BOSdata.new()
htfadd265.settings                 := SettingsHTFadd265
htfadd265.candles                  := candlesadd265
htfadd265.bosdata                  := bosdataadd265
var CandleSet htfadd266                     = CandleSet.new()
var CandleSettings SettingsHTFadd266        = CandleSettings.new(htf='266',htfint=266,max_memory=3)
var Candle[] candlesadd266                  = array.new<Candle>(0)
var BOSdata bosdataadd266                   = BOSdata.new()
htfadd266.settings                 := SettingsHTFadd266
htfadd266.candles                  := candlesadd266
htfadd266.bosdata                  := bosdataadd266
var CandleSet htfadd267                     = CandleSet.new()
var CandleSettings SettingsHTFadd267        = CandleSettings.new(htf='267',htfint=267,max_memory=3)
var Candle[] candlesadd267                  = array.new<Candle>(0)
var BOSdata bosdataadd267                   = BOSdata.new()
htfadd267.settings                 := SettingsHTFadd267
htfadd267.candles                  := candlesadd267
htfadd267.bosdata                  := bosdataadd267
var CandleSet htfadd268                     = CandleSet.new()
var CandleSettings SettingsHTFadd268        = CandleSettings.new(htf='268',htfint=268,max_memory=3)
var Candle[] candlesadd268                  = array.new<Candle>(0)
var BOSdata bosdataadd268                   = BOSdata.new()
htfadd268.settings                 := SettingsHTFadd268
htfadd268.candles                  := candlesadd268
htfadd268.bosdata                  := bosdataadd268
var CandleSet htfadd269                     = CandleSet.new()
var CandleSettings SettingsHTFadd269        = CandleSettings.new(htf='269',htfint=269,max_memory=3)
var Candle[] candlesadd269                  = array.new<Candle>(0)
var BOSdata bosdataadd269                   = BOSdata.new()
htfadd269.settings                 := SettingsHTFadd269
htfadd269.candles                  := candlesadd269
htfadd269.bosdata                  := bosdataadd269
var CandleSet htfadd270                     = CandleSet.new()
var CandleSettings SettingsHTFadd270        = CandleSettings.new(htf='270',htfint=270,max_memory=3)
var Candle[] candlesadd270                  = array.new<Candle>(0)
var BOSdata bosdataadd270                   = BOSdata.new()
htfadd270.settings                 := SettingsHTFadd270
htfadd270.candles                  := candlesadd270
htfadd270.bosdata                  := bosdataadd270

htfadd180.Monitor().BOSJudge()
htfadd181.Monitor().BOSJudge()
htfadd182.Monitor().BOSJudge()
htfadd183.Monitor().BOSJudge()
htfadd184.Monitor().BOSJudge()
htfadd185.Monitor().BOSJudge()
htfadd186.Monitor().BOSJudge()
htfadd187.Monitor().BOSJudge()
htfadd188.Monitor().BOSJudge()
htfadd189.Monitor().BOSJudge()
htfadd190.Monitor().BOSJudge()
htfadd191.Monitor().BOSJudge()
htfadd192.Monitor().BOSJudge()
htfadd193.Monitor().BOSJudge()
htfadd194.Monitor().BOSJudge()
htfadd195.Monitor().BOSJudge()
htfadd196.Monitor().BOSJudge()
htfadd197.Monitor().BOSJudge()
htfadd198.Monitor().BOSJudge()
htfadd199.Monitor().BOSJudge()
htfadd200.Monitor().BOSJudge()
htfadd201.Monitor().BOSJudge()
htfadd202.Monitor().BOSJudge()
htfadd203.Monitor().BOSJudge()
htfadd204.Monitor().BOSJudge()
htfadd205.Monitor().BOSJudge()
htfadd206.Monitor().BOSJudge()
htfadd207.Monitor().BOSJudge()
htfadd208.Monitor().BOSJudge()
htfadd209.Monitor().BOSJudge()
htfadd210.Monitor().BOSJudge()
htfadd211.Monitor().BOSJudge()
htfadd212.Monitor().BOSJudge()
htfadd213.Monitor().BOSJudge()
htfadd214.Monitor().BOSJudge()
htfadd215.Monitor().BOSJudge()
htfadd216.Monitor().BOSJudge()
htfadd217.Monitor().BOSJudge()
htfadd218.Monitor().BOSJudge()
htfadd219.Monitor().BOSJudge()
htfadd220.Monitor().BOSJudge()
htfadd221.Monitor().BOSJudge()
htfadd222.Monitor().BOSJudge()
htfadd223.Monitor().BOSJudge()
htfadd224.Monitor().BOSJudge()
htfadd225.Monitor().BOSJudge()
htfadd226.Monitor().BOSJudge()
htfadd227.Monitor().BOSJudge()
htfadd228.Monitor().BOSJudge()
htfadd229.Monitor().BOSJudge()
htfadd230.Monitor().BOSJudge()
htfadd231.Monitor().BOSJudge()
htfadd232.Monitor().BOSJudge()
htfadd233.Monitor().BOSJudge()
htfadd234.Monitor().BOSJudge()
htfadd235.Monitor().BOSJudge()
htfadd236.Monitor().BOSJudge()
htfadd237.Monitor().BOSJudge()
htfadd238.Monitor().BOSJudge()
htfadd239.Monitor().BOSJudge()
htfadd240.Monitor().BOSJudge()
htfadd241.Monitor().BOSJudge()
htfadd242.Monitor().BOSJudge()
htfadd243.Monitor().BOSJudge()
htfadd244.Monitor().BOSJudge()
htfadd245.Monitor().BOSJudge()
htfadd246.Monitor().BOSJudge()
htfadd247.Monitor().BOSJudge()
htfadd248.Monitor().BOSJudge()
htfadd249.Monitor().BOSJudge()
htfadd250.Monitor().BOSJudge()
htfadd251.Monitor().BOSJudge()
htfadd252.Monitor().BOSJudge()
htfadd253.Monitor().BOSJudge()
htfadd254.Monitor().BOSJudge()
htfadd255.Monitor().BOSJudge()
htfadd256.Monitor().BOSJudge()
htfadd257.Monitor().BOSJudge()
htfadd258.Monitor().BOSJudge()
htfadd259.Monitor().BOSJudge()
htfadd260.Monitor().BOSJudge()
htfadd261.Monitor().BOSJudge()
htfadd262.Monitor().BOSJudge()
htfadd263.Monitor().BOSJudge()
htfadd264.Monitor().BOSJudge()
htfadd265.Monitor().BOSJudge()
htfadd266.Monitor().BOSJudge()
htfadd267.Monitor().BOSJudge()
htfadd268.Monitor().BOSJudge()
htfadd269.Monitor().BOSJudge()
htfadd270.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd180)
    LowestsbuSet(lowestsbu, htfadd180)
    HighestsbdSet(highestsbd, htfadd181)
    LowestsbuSet(lowestsbu, htfadd181)
    HighestsbdSet(highestsbd, htfadd182)
    LowestsbuSet(lowestsbu, htfadd182)
    HighestsbdSet(highestsbd, htfadd183)
    LowestsbuSet(lowestsbu, htfadd183)
    HighestsbdSet(highestsbd, htfadd184)
    LowestsbuSet(lowestsbu, htfadd184)
    HighestsbdSet(highestsbd, htfadd185)
    LowestsbuSet(lowestsbu, htfadd185)
    HighestsbdSet(highestsbd, htfadd186)
    LowestsbuSet(lowestsbu, htfadd186)
    HighestsbdSet(highestsbd, htfadd187)
    LowestsbuSet(lowestsbu, htfadd187)
    HighestsbdSet(highestsbd, htfadd188)
    LowestsbuSet(lowestsbu, htfadd188)
    HighestsbdSet(highestsbd, htfadd189)
    LowestsbuSet(lowestsbu, htfadd189)
    HighestsbdSet(highestsbd, htfadd190)
    LowestsbuSet(lowestsbu, htfadd190)
    HighestsbdSet(highestsbd, htfadd191)
    LowestsbuSet(lowestsbu, htfadd191)
    HighestsbdSet(highestsbd, htfadd192)
    LowestsbuSet(lowestsbu, htfadd192)
    HighestsbdSet(highestsbd, htfadd193)
    LowestsbuSet(lowestsbu, htfadd193)
    HighestsbdSet(highestsbd, htfadd194)
    LowestsbuSet(lowestsbu, htfadd194)
    HighestsbdSet(highestsbd, htfadd195)
    LowestsbuSet(lowestsbu, htfadd195)
    HighestsbdSet(highestsbd, htfadd196)
    LowestsbuSet(lowestsbu, htfadd196)
    HighestsbdSet(highestsbd, htfadd197)
    LowestsbuSet(lowestsbu, htfadd197)
    HighestsbdSet(highestsbd, htfadd198)
    LowestsbuSet(lowestsbu, htfadd198)
    HighestsbdSet(highestsbd, htfadd199)
    LowestsbuSet(lowestsbu, htfadd199)
    HighestsbdSet(highestsbd, htfadd200)
    LowestsbuSet(lowestsbu, htfadd200)
    HighestsbdSet(highestsbd, htfadd201)
    LowestsbuSet(lowestsbu, htfadd201)
    HighestsbdSet(highestsbd, htfadd202)
    LowestsbuSet(lowestsbu, htfadd202)
    HighestsbdSet(highestsbd, htfadd203)
    LowestsbuSet(lowestsbu, htfadd203)
    HighestsbdSet(highestsbd, htfadd204)
    LowestsbuSet(lowestsbu, htfadd204)
    HighestsbdSet(highestsbd, htfadd205)
    LowestsbuSet(lowestsbu, htfadd205)
    HighestsbdSet(highestsbd, htfadd206)
    LowestsbuSet(lowestsbu, htfadd206)
    HighestsbdSet(highestsbd, htfadd207)
    LowestsbuSet(lowestsbu, htfadd207)
    HighestsbdSet(highestsbd, htfadd208)
    LowestsbuSet(lowestsbu, htfadd208)
    HighestsbdSet(highestsbd, htfadd209)
    LowestsbuSet(lowestsbu, htfadd209)
    HighestsbdSet(highestsbd, htfadd210)
    LowestsbuSet(lowestsbu, htfadd210)
    HighestsbdSet(highestsbd, htfadd211)
    LowestsbuSet(lowestsbu, htfadd211)
    HighestsbdSet(highestsbd, htfadd212)
    LowestsbuSet(lowestsbu, htfadd212)
    HighestsbdSet(highestsbd, htfadd213)
    LowestsbuSet(lowestsbu, htfadd213)
    HighestsbdSet(highestsbd, htfadd214)
    LowestsbuSet(lowestsbu, htfadd214)
    HighestsbdSet(highestsbd, htfadd215)
    LowestsbuSet(lowestsbu, htfadd215)
    HighestsbdSet(highestsbd, htfadd216)
    LowestsbuSet(lowestsbu, htfadd216)
    HighestsbdSet(highestsbd, htfadd217)
    LowestsbuSet(lowestsbu, htfadd217)
    HighestsbdSet(highestsbd, htfadd218)
    LowestsbuSet(lowestsbu, htfadd218)
    HighestsbdSet(highestsbd, htfadd219)
    LowestsbuSet(lowestsbu, htfadd219)
    HighestsbdSet(highestsbd, htfadd220)
    LowestsbuSet(lowestsbu, htfadd220)
    HighestsbdSet(highestsbd, htfadd221)
    LowestsbuSet(lowestsbu, htfadd221)
    HighestsbdSet(highestsbd, htfadd222)
    LowestsbuSet(lowestsbu, htfadd222)
    HighestsbdSet(highestsbd, htfadd223)
    LowestsbuSet(lowestsbu, htfadd223)
    HighestsbdSet(highestsbd, htfadd224)
    LowestsbuSet(lowestsbu, htfadd224)
    HighestsbdSet(highestsbd, htfadd225)
    LowestsbuSet(lowestsbu, htfadd225)
    HighestsbdSet(highestsbd, htfadd226)
    LowestsbuSet(lowestsbu, htfadd226)
    HighestsbdSet(highestsbd, htfadd227)
    LowestsbuSet(lowestsbu, htfadd227)
    HighestsbdSet(highestsbd, htfadd228)
    LowestsbuSet(lowestsbu, htfadd228)
    HighestsbdSet(highestsbd, htfadd229)
    LowestsbuSet(lowestsbu, htfadd229)
    HighestsbdSet(highestsbd, htfadd230)
    LowestsbuSet(lowestsbu, htfadd230)
    HighestsbdSet(highestsbd, htfadd231)
    LowestsbuSet(lowestsbu, htfadd231)
    HighestsbdSet(highestsbd, htfadd232)
    LowestsbuSet(lowestsbu, htfadd232)
    HighestsbdSet(highestsbd, htfadd233)
    LowestsbuSet(lowestsbu, htfadd233)
    HighestsbdSet(highestsbd, htfadd234)
    LowestsbuSet(lowestsbu, htfadd234)
    HighestsbdSet(highestsbd, htfadd235)
    LowestsbuSet(lowestsbu, htfadd235)
    HighestsbdSet(highestsbd, htfadd236)
    LowestsbuSet(lowestsbu, htfadd236)
    HighestsbdSet(highestsbd, htfadd237)
    LowestsbuSet(lowestsbu, htfadd237)
    HighestsbdSet(highestsbd, htfadd238)
    LowestsbuSet(lowestsbu, htfadd238)
    HighestsbdSet(highestsbd, htfadd239)
    LowestsbuSet(lowestsbu, htfadd239)
    HighestsbdSet(highestsbd, htfadd240)
    LowestsbuSet(lowestsbu, htfadd240)
    HighestsbdSet(highestsbd, htfadd241)
    LowestsbuSet(lowestsbu, htfadd241)
    HighestsbdSet(highestsbd, htfadd242)
    LowestsbuSet(lowestsbu, htfadd242)
    HighestsbdSet(highestsbd, htfadd243)
    LowestsbuSet(lowestsbu, htfadd243)
    HighestsbdSet(highestsbd, htfadd244)
    LowestsbuSet(lowestsbu, htfadd244)
    HighestsbdSet(highestsbd, htfadd245)
    LowestsbuSet(lowestsbu, htfadd245)
    HighestsbdSet(highestsbd, htfadd246)
    LowestsbuSet(lowestsbu, htfadd246)
    HighestsbdSet(highestsbd, htfadd247)
    LowestsbuSet(lowestsbu, htfadd247)
    HighestsbdSet(highestsbd, htfadd248)
    LowestsbuSet(lowestsbu, htfadd248)
    HighestsbdSet(highestsbd, htfadd249)
    LowestsbuSet(lowestsbu, htfadd249)
    HighestsbdSet(highestsbd, htfadd250)
    LowestsbuSet(lowestsbu, htfadd250)
    HighestsbdSet(highestsbd, htfadd251)
    LowestsbuSet(lowestsbu, htfadd251)
    HighestsbdSet(highestsbd, htfadd252)
    LowestsbuSet(lowestsbu, htfadd252)
    HighestsbdSet(highestsbd, htfadd253)
    LowestsbuSet(lowestsbu, htfadd253)
    HighestsbdSet(highestsbd, htfadd254)
    LowestsbuSet(lowestsbu, htfadd254)
    HighestsbdSet(highestsbd, htfadd255)
    LowestsbuSet(lowestsbu, htfadd255)
    HighestsbdSet(highestsbd, htfadd256)
    LowestsbuSet(lowestsbu, htfadd256)
    HighestsbdSet(highestsbd, htfadd257)
    LowestsbuSet(lowestsbu, htfadd257)
    HighestsbdSet(highestsbd, htfadd258)
    LowestsbuSet(lowestsbu, htfadd258)
    HighestsbdSet(highestsbd, htfadd259)
    LowestsbuSet(lowestsbu, htfadd259)
    HighestsbdSet(highestsbd, htfadd260)
    LowestsbuSet(lowestsbu, htfadd260)
    HighestsbdSet(highestsbd, htfadd261)
    LowestsbuSet(lowestsbu, htfadd261)
    HighestsbdSet(highestsbd, htfadd262)
    LowestsbuSet(lowestsbu, htfadd262)
    HighestsbdSet(highestsbd, htfadd263)
    LowestsbuSet(lowestsbu, htfadd263)
    HighestsbdSet(highestsbd, htfadd264)
    LowestsbuSet(lowestsbu, htfadd264)
    HighestsbdSet(highestsbd, htfadd265)
    LowestsbuSet(lowestsbu, htfadd265)
    HighestsbdSet(highestsbd, htfadd266)
    LowestsbuSet(lowestsbu, htfadd266)
    HighestsbdSet(highestsbd, htfadd267)
    LowestsbuSet(lowestsbu, htfadd267)
    HighestsbdSet(highestsbd, htfadd268)
    LowestsbuSet(lowestsbu, htfadd268)
    HighestsbdSet(highestsbd, htfadd269)
    LowestsbuSet(lowestsbu, htfadd269)
    HighestsbdSet(highestsbd, htfadd270)
    LowestsbuSet(lowestsbu, htfadd270)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd180).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd181).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd182).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd183).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd184).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd185).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd186).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd187).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd188).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd189).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd190).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd191).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd192).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd193).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd194).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd195).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd196).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd197).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd198).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd199).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd200).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd201).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd202).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd203).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd204).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd205).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd206).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd207).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd208).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd209).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd210).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd211).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd212).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd213).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd214).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd215).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd216).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd217).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd218).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd219).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd220).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd221).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd222).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd223).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd224).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd225).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd226).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd227).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd228).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd229).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd230).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd231).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd232).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd233).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd234).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd235).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd236).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd237).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd238).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd239).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd240).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd241).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd242).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd243).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd244).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd245).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd246).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd247).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd248).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd249).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd250).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd251).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd252).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd253).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd254).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd255).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd256).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd257).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd258).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd259).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd260).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd261).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd262).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd263).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd264).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd265).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd266).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd267).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd268).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd269).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd270).Monitor_Est().BOSJudge()
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


