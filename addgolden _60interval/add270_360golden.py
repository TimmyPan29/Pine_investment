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
var CandleSet htfadd270                     = CandleSet.new()
var CandleSettings SettingsHTFadd270        = CandleSettings.new(htf='270',htfint=270,max_memory=3)
var Candle[] candlesadd270                  = array.new<Candle>(0)
var BOSdata bosdataadd270                   = BOSdata.new()
htfadd270.settings                 := SettingsHTFadd270
htfadd270.candles                  := candlesadd270
htfadd270.bosdata                  := bosdataadd270
var CandleSet htfadd271                     = CandleSet.new()
var CandleSettings SettingsHTFadd271        = CandleSettings.new(htf='271',htfint=271,max_memory=3)
var Candle[] candlesadd271                  = array.new<Candle>(0)
var BOSdata bosdataadd271                   = BOSdata.new()
htfadd271.settings                 := SettingsHTFadd271
htfadd271.candles                  := candlesadd271
htfadd271.bosdata                  := bosdataadd271
var CandleSet htfadd272                     = CandleSet.new()
var CandleSettings SettingsHTFadd272        = CandleSettings.new(htf='272',htfint=272,max_memory=3)
var Candle[] candlesadd272                  = array.new<Candle>(0)
var BOSdata bosdataadd272                   = BOSdata.new()
htfadd272.settings                 := SettingsHTFadd272
htfadd272.candles                  := candlesadd272
htfadd272.bosdata                  := bosdataadd272
var CandleSet htfadd273                     = CandleSet.new()
var CandleSettings SettingsHTFadd273        = CandleSettings.new(htf='273',htfint=273,max_memory=3)
var Candle[] candlesadd273                  = array.new<Candle>(0)
var BOSdata bosdataadd273                   = BOSdata.new()
htfadd273.settings                 := SettingsHTFadd273
htfadd273.candles                  := candlesadd273
htfadd273.bosdata                  := bosdataadd273
var CandleSet htfadd274                     = CandleSet.new()
var CandleSettings SettingsHTFadd274        = CandleSettings.new(htf='274',htfint=274,max_memory=3)
var Candle[] candlesadd274                  = array.new<Candle>(0)
var BOSdata bosdataadd274                   = BOSdata.new()
htfadd274.settings                 := SettingsHTFadd274
htfadd274.candles                  := candlesadd274
htfadd274.bosdata                  := bosdataadd274
var CandleSet htfadd275                     = CandleSet.new()
var CandleSettings SettingsHTFadd275        = CandleSettings.new(htf='275',htfint=275,max_memory=3)
var Candle[] candlesadd275                  = array.new<Candle>(0)
var BOSdata bosdataadd275                   = BOSdata.new()
htfadd275.settings                 := SettingsHTFadd275
htfadd275.candles                  := candlesadd275
htfadd275.bosdata                  := bosdataadd275
var CandleSet htfadd276                     = CandleSet.new()
var CandleSettings SettingsHTFadd276        = CandleSettings.new(htf='276',htfint=276,max_memory=3)
var Candle[] candlesadd276                  = array.new<Candle>(0)
var BOSdata bosdataadd276                   = BOSdata.new()
htfadd276.settings                 := SettingsHTFadd276
htfadd276.candles                  := candlesadd276
htfadd276.bosdata                  := bosdataadd276
var CandleSet htfadd277                     = CandleSet.new()
var CandleSettings SettingsHTFadd277        = CandleSettings.new(htf='277',htfint=277,max_memory=3)
var Candle[] candlesadd277                  = array.new<Candle>(0)
var BOSdata bosdataadd277                   = BOSdata.new()
htfadd277.settings                 := SettingsHTFadd277
htfadd277.candles                  := candlesadd277
htfadd277.bosdata                  := bosdataadd277
var CandleSet htfadd278                     = CandleSet.new()
var CandleSettings SettingsHTFadd278        = CandleSettings.new(htf='278',htfint=278,max_memory=3)
var Candle[] candlesadd278                  = array.new<Candle>(0)
var BOSdata bosdataadd278                   = BOSdata.new()
htfadd278.settings                 := SettingsHTFadd278
htfadd278.candles                  := candlesadd278
htfadd278.bosdata                  := bosdataadd278
var CandleSet htfadd279                     = CandleSet.new()
var CandleSettings SettingsHTFadd279        = CandleSettings.new(htf='279',htfint=279,max_memory=3)
var Candle[] candlesadd279                  = array.new<Candle>(0)
var BOSdata bosdataadd279                   = BOSdata.new()
htfadd279.settings                 := SettingsHTFadd279
htfadd279.candles                  := candlesadd279
htfadd279.bosdata                  := bosdataadd279
var CandleSet htfadd280                     = CandleSet.new()
var CandleSettings SettingsHTFadd280        = CandleSettings.new(htf='280',htfint=280,max_memory=3)
var Candle[] candlesadd280                  = array.new<Candle>(0)
var BOSdata bosdataadd280                   = BOSdata.new()
htfadd280.settings                 := SettingsHTFadd280
htfadd280.candles                  := candlesadd280
htfadd280.bosdata                  := bosdataadd280
var CandleSet htfadd281                     = CandleSet.new()
var CandleSettings SettingsHTFadd281        = CandleSettings.new(htf='281',htfint=281,max_memory=3)
var Candle[] candlesadd281                  = array.new<Candle>(0)
var BOSdata bosdataadd281                   = BOSdata.new()
htfadd281.settings                 := SettingsHTFadd281
htfadd281.candles                  := candlesadd281
htfadd281.bosdata                  := bosdataadd281
var CandleSet htfadd282                     = CandleSet.new()
var CandleSettings SettingsHTFadd282        = CandleSettings.new(htf='282',htfint=282,max_memory=3)
var Candle[] candlesadd282                  = array.new<Candle>(0)
var BOSdata bosdataadd282                   = BOSdata.new()
htfadd282.settings                 := SettingsHTFadd282
htfadd282.candles                  := candlesadd282
htfadd282.bosdata                  := bosdataadd282
var CandleSet htfadd283                     = CandleSet.new()
var CandleSettings SettingsHTFadd283        = CandleSettings.new(htf='283',htfint=283,max_memory=3)
var Candle[] candlesadd283                  = array.new<Candle>(0)
var BOSdata bosdataadd283                   = BOSdata.new()
htfadd283.settings                 := SettingsHTFadd283
htfadd283.candles                  := candlesadd283
htfadd283.bosdata                  := bosdataadd283
var CandleSet htfadd284                     = CandleSet.new()
var CandleSettings SettingsHTFadd284        = CandleSettings.new(htf='284',htfint=284,max_memory=3)
var Candle[] candlesadd284                  = array.new<Candle>(0)
var BOSdata bosdataadd284                   = BOSdata.new()
htfadd284.settings                 := SettingsHTFadd284
htfadd284.candles                  := candlesadd284
htfadd284.bosdata                  := bosdataadd284
var CandleSet htfadd285                     = CandleSet.new()
var CandleSettings SettingsHTFadd285        = CandleSettings.new(htf='285',htfint=285,max_memory=3)
var Candle[] candlesadd285                  = array.new<Candle>(0)
var BOSdata bosdataadd285                   = BOSdata.new()
htfadd285.settings                 := SettingsHTFadd285
htfadd285.candles                  := candlesadd285
htfadd285.bosdata                  := bosdataadd285
var CandleSet htfadd286                     = CandleSet.new()
var CandleSettings SettingsHTFadd286        = CandleSettings.new(htf='286',htfint=286,max_memory=3)
var Candle[] candlesadd286                  = array.new<Candle>(0)
var BOSdata bosdataadd286                   = BOSdata.new()
htfadd286.settings                 := SettingsHTFadd286
htfadd286.candles                  := candlesadd286
htfadd286.bosdata                  := bosdataadd286
var CandleSet htfadd287                     = CandleSet.new()
var CandleSettings SettingsHTFadd287        = CandleSettings.new(htf='287',htfint=287,max_memory=3)
var Candle[] candlesadd287                  = array.new<Candle>(0)
var BOSdata bosdataadd287                   = BOSdata.new()
htfadd287.settings                 := SettingsHTFadd287
htfadd287.candles                  := candlesadd287
htfadd287.bosdata                  := bosdataadd287
var CandleSet htfadd288                     = CandleSet.new()
var CandleSettings SettingsHTFadd288        = CandleSettings.new(htf='288',htfint=288,max_memory=3)
var Candle[] candlesadd288                  = array.new<Candle>(0)
var BOSdata bosdataadd288                   = BOSdata.new()
htfadd288.settings                 := SettingsHTFadd288
htfadd288.candles                  := candlesadd288
htfadd288.bosdata                  := bosdataadd288
var CandleSet htfadd289                     = CandleSet.new()
var CandleSettings SettingsHTFadd289        = CandleSettings.new(htf='289',htfint=289,max_memory=3)
var Candle[] candlesadd289                  = array.new<Candle>(0)
var BOSdata bosdataadd289                   = BOSdata.new()
htfadd289.settings                 := SettingsHTFadd289
htfadd289.candles                  := candlesadd289
htfadd289.bosdata                  := bosdataadd289
var CandleSet htfadd290                     = CandleSet.new()
var CandleSettings SettingsHTFadd290        = CandleSettings.new(htf='290',htfint=290,max_memory=3)
var Candle[] candlesadd290                  = array.new<Candle>(0)
var BOSdata bosdataadd290                   = BOSdata.new()
htfadd290.settings                 := SettingsHTFadd290
htfadd290.candles                  := candlesadd290
htfadd290.bosdata                  := bosdataadd290
var CandleSet htfadd291                     = CandleSet.new()
var CandleSettings SettingsHTFadd291        = CandleSettings.new(htf='291',htfint=291,max_memory=3)
var Candle[] candlesadd291                  = array.new<Candle>(0)
var BOSdata bosdataadd291                   = BOSdata.new()
htfadd291.settings                 := SettingsHTFadd291
htfadd291.candles                  := candlesadd291
htfadd291.bosdata                  := bosdataadd291
var CandleSet htfadd292                     = CandleSet.new()
var CandleSettings SettingsHTFadd292        = CandleSettings.new(htf='292',htfint=292,max_memory=3)
var Candle[] candlesadd292                  = array.new<Candle>(0)
var BOSdata bosdataadd292                   = BOSdata.new()
htfadd292.settings                 := SettingsHTFadd292
htfadd292.candles                  := candlesadd292
htfadd292.bosdata                  := bosdataadd292
var CandleSet htfadd293                     = CandleSet.new()
var CandleSettings SettingsHTFadd293        = CandleSettings.new(htf='293',htfint=293,max_memory=3)
var Candle[] candlesadd293                  = array.new<Candle>(0)
var BOSdata bosdataadd293                   = BOSdata.new()
htfadd293.settings                 := SettingsHTFadd293
htfadd293.candles                  := candlesadd293
htfadd293.bosdata                  := bosdataadd293
var CandleSet htfadd294                     = CandleSet.new()
var CandleSettings SettingsHTFadd294        = CandleSettings.new(htf='294',htfint=294,max_memory=3)
var Candle[] candlesadd294                  = array.new<Candle>(0)
var BOSdata bosdataadd294                   = BOSdata.new()
htfadd294.settings                 := SettingsHTFadd294
htfadd294.candles                  := candlesadd294
htfadd294.bosdata                  := bosdataadd294
var CandleSet htfadd295                     = CandleSet.new()
var CandleSettings SettingsHTFadd295        = CandleSettings.new(htf='295',htfint=295,max_memory=3)
var Candle[] candlesadd295                  = array.new<Candle>(0)
var BOSdata bosdataadd295                   = BOSdata.new()
htfadd295.settings                 := SettingsHTFadd295
htfadd295.candles                  := candlesadd295
htfadd295.bosdata                  := bosdataadd295
var CandleSet htfadd296                     = CandleSet.new()
var CandleSettings SettingsHTFadd296        = CandleSettings.new(htf='296',htfint=296,max_memory=3)
var Candle[] candlesadd296                  = array.new<Candle>(0)
var BOSdata bosdataadd296                   = BOSdata.new()
htfadd296.settings                 := SettingsHTFadd296
htfadd296.candles                  := candlesadd296
htfadd296.bosdata                  := bosdataadd296
var CandleSet htfadd297                     = CandleSet.new()
var CandleSettings SettingsHTFadd297        = CandleSettings.new(htf='297',htfint=297,max_memory=3)
var Candle[] candlesadd297                  = array.new<Candle>(0)
var BOSdata bosdataadd297                   = BOSdata.new()
htfadd297.settings                 := SettingsHTFadd297
htfadd297.candles                  := candlesadd297
htfadd297.bosdata                  := bosdataadd297
var CandleSet htfadd298                     = CandleSet.new()
var CandleSettings SettingsHTFadd298        = CandleSettings.new(htf='298',htfint=298,max_memory=3)
var Candle[] candlesadd298                  = array.new<Candle>(0)
var BOSdata bosdataadd298                   = BOSdata.new()
htfadd298.settings                 := SettingsHTFadd298
htfadd298.candles                  := candlesadd298
htfadd298.bosdata                  := bosdataadd298
var CandleSet htfadd299                     = CandleSet.new()
var CandleSettings SettingsHTFadd299        = CandleSettings.new(htf='299',htfint=299,max_memory=3)
var Candle[] candlesadd299                  = array.new<Candle>(0)
var BOSdata bosdataadd299                   = BOSdata.new()
htfadd299.settings                 := SettingsHTFadd299
htfadd299.candles                  := candlesadd299
htfadd299.bosdata                  := bosdataadd299
var CandleSet htfadd300                     = CandleSet.new()
var CandleSettings SettingsHTFadd300        = CandleSettings.new(htf='300',htfint=300,max_memory=3)
var Candle[] candlesadd300                  = array.new<Candle>(0)
var BOSdata bosdataadd300                   = BOSdata.new()
htfadd300.settings                 := SettingsHTFadd300
htfadd300.candles                  := candlesadd300
htfadd300.bosdata                  := bosdataadd300
var CandleSet htfadd301                     = CandleSet.new()
var CandleSettings SettingsHTFadd301        = CandleSettings.new(htf='301',htfint=301,max_memory=3)
var Candle[] candlesadd301                  = array.new<Candle>(0)
var BOSdata bosdataadd301                   = BOSdata.new()
htfadd301.settings                 := SettingsHTFadd301
htfadd301.candles                  := candlesadd301
htfadd301.bosdata                  := bosdataadd301
var CandleSet htfadd302                     = CandleSet.new()
var CandleSettings SettingsHTFadd302        = CandleSettings.new(htf='302',htfint=302,max_memory=3)
var Candle[] candlesadd302                  = array.new<Candle>(0)
var BOSdata bosdataadd302                   = BOSdata.new()
htfadd302.settings                 := SettingsHTFadd302
htfadd302.candles                  := candlesadd302
htfadd302.bosdata                  := bosdataadd302
var CandleSet htfadd303                     = CandleSet.new()
var CandleSettings SettingsHTFadd303        = CandleSettings.new(htf='303',htfint=303,max_memory=3)
var Candle[] candlesadd303                  = array.new<Candle>(0)
var BOSdata bosdataadd303                   = BOSdata.new()
htfadd303.settings                 := SettingsHTFadd303
htfadd303.candles                  := candlesadd303
htfadd303.bosdata                  := bosdataadd303
var CandleSet htfadd304                     = CandleSet.new()
var CandleSettings SettingsHTFadd304        = CandleSettings.new(htf='304',htfint=304,max_memory=3)
var Candle[] candlesadd304                  = array.new<Candle>(0)
var BOSdata bosdataadd304                   = BOSdata.new()
htfadd304.settings                 := SettingsHTFadd304
htfadd304.candles                  := candlesadd304
htfadd304.bosdata                  := bosdataadd304
var CandleSet htfadd305                     = CandleSet.new()
var CandleSettings SettingsHTFadd305        = CandleSettings.new(htf='305',htfint=305,max_memory=3)
var Candle[] candlesadd305                  = array.new<Candle>(0)
var BOSdata bosdataadd305                   = BOSdata.new()
htfadd305.settings                 := SettingsHTFadd305
htfadd305.candles                  := candlesadd305
htfadd305.bosdata                  := bosdataadd305
var CandleSet htfadd306                     = CandleSet.new()
var CandleSettings SettingsHTFadd306        = CandleSettings.new(htf='306',htfint=306,max_memory=3)
var Candle[] candlesadd306                  = array.new<Candle>(0)
var BOSdata bosdataadd306                   = BOSdata.new()
htfadd306.settings                 := SettingsHTFadd306
htfadd306.candles                  := candlesadd306
htfadd306.bosdata                  := bosdataadd306
var CandleSet htfadd307                     = CandleSet.new()
var CandleSettings SettingsHTFadd307        = CandleSettings.new(htf='307',htfint=307,max_memory=3)
var Candle[] candlesadd307                  = array.new<Candle>(0)
var BOSdata bosdataadd307                   = BOSdata.new()
htfadd307.settings                 := SettingsHTFadd307
htfadd307.candles                  := candlesadd307
htfadd307.bosdata                  := bosdataadd307
var CandleSet htfadd308                     = CandleSet.new()
var CandleSettings SettingsHTFadd308        = CandleSettings.new(htf='308',htfint=308,max_memory=3)
var Candle[] candlesadd308                  = array.new<Candle>(0)
var BOSdata bosdataadd308                   = BOSdata.new()
htfadd308.settings                 := SettingsHTFadd308
htfadd308.candles                  := candlesadd308
htfadd308.bosdata                  := bosdataadd308
var CandleSet htfadd309                     = CandleSet.new()
var CandleSettings SettingsHTFadd309        = CandleSettings.new(htf='309',htfint=309,max_memory=3)
var Candle[] candlesadd309                  = array.new<Candle>(0)
var BOSdata bosdataadd309                   = BOSdata.new()
htfadd309.settings                 := SettingsHTFadd309
htfadd309.candles                  := candlesadd309
htfadd309.bosdata                  := bosdataadd309
var CandleSet htfadd310                     = CandleSet.new()
var CandleSettings SettingsHTFadd310        = CandleSettings.new(htf='310',htfint=310,max_memory=3)
var Candle[] candlesadd310                  = array.new<Candle>(0)
var BOSdata bosdataadd310                   = BOSdata.new()
htfadd310.settings                 := SettingsHTFadd310
htfadd310.candles                  := candlesadd310
htfadd310.bosdata                  := bosdataadd310
var CandleSet htfadd311                     = CandleSet.new()
var CandleSettings SettingsHTFadd311        = CandleSettings.new(htf='311',htfint=311,max_memory=3)
var Candle[] candlesadd311                  = array.new<Candle>(0)
var BOSdata bosdataadd311                   = BOSdata.new()
htfadd311.settings                 := SettingsHTFadd311
htfadd311.candles                  := candlesadd311
htfadd311.bosdata                  := bosdataadd311
var CandleSet htfadd312                     = CandleSet.new()
var CandleSettings SettingsHTFadd312        = CandleSettings.new(htf='312',htfint=312,max_memory=3)
var Candle[] candlesadd312                  = array.new<Candle>(0)
var BOSdata bosdataadd312                   = BOSdata.new()
htfadd312.settings                 := SettingsHTFadd312
htfadd312.candles                  := candlesadd312
htfadd312.bosdata                  := bosdataadd312
var CandleSet htfadd313                     = CandleSet.new()
var CandleSettings SettingsHTFadd313        = CandleSettings.new(htf='313',htfint=313,max_memory=3)
var Candle[] candlesadd313                  = array.new<Candle>(0)
var BOSdata bosdataadd313                   = BOSdata.new()
htfadd313.settings                 := SettingsHTFadd313
htfadd313.candles                  := candlesadd313
htfadd313.bosdata                  := bosdataadd313
var CandleSet htfadd314                     = CandleSet.new()
var CandleSettings SettingsHTFadd314        = CandleSettings.new(htf='314',htfint=314,max_memory=3)
var Candle[] candlesadd314                  = array.new<Candle>(0)
var BOSdata bosdataadd314                   = BOSdata.new()
htfadd314.settings                 := SettingsHTFadd314
htfadd314.candles                  := candlesadd314
htfadd314.bosdata                  := bosdataadd314
var CandleSet htfadd315                     = CandleSet.new()
var CandleSettings SettingsHTFadd315        = CandleSettings.new(htf='315',htfint=315,max_memory=3)
var Candle[] candlesadd315                  = array.new<Candle>(0)
var BOSdata bosdataadd315                   = BOSdata.new()
htfadd315.settings                 := SettingsHTFadd315
htfadd315.candles                  := candlesadd315
htfadd315.bosdata                  := bosdataadd315
var CandleSet htfadd316                     = CandleSet.new()
var CandleSettings SettingsHTFadd316        = CandleSettings.new(htf='316',htfint=316,max_memory=3)
var Candle[] candlesadd316                  = array.new<Candle>(0)
var BOSdata bosdataadd316                   = BOSdata.new()
htfadd316.settings                 := SettingsHTFadd316
htfadd316.candles                  := candlesadd316
htfadd316.bosdata                  := bosdataadd316
var CandleSet htfadd317                     = CandleSet.new()
var CandleSettings SettingsHTFadd317        = CandleSettings.new(htf='317',htfint=317,max_memory=3)
var Candle[] candlesadd317                  = array.new<Candle>(0)
var BOSdata bosdataadd317                   = BOSdata.new()
htfadd317.settings                 := SettingsHTFadd317
htfadd317.candles                  := candlesadd317
htfadd317.bosdata                  := bosdataadd317
var CandleSet htfadd318                     = CandleSet.new()
var CandleSettings SettingsHTFadd318        = CandleSettings.new(htf='318',htfint=318,max_memory=3)
var Candle[] candlesadd318                  = array.new<Candle>(0)
var BOSdata bosdataadd318                   = BOSdata.new()
htfadd318.settings                 := SettingsHTFadd318
htfadd318.candles                  := candlesadd318
htfadd318.bosdata                  := bosdataadd318
var CandleSet htfadd319                     = CandleSet.new()
var CandleSettings SettingsHTFadd319        = CandleSettings.new(htf='319',htfint=319,max_memory=3)
var Candle[] candlesadd319                  = array.new<Candle>(0)
var BOSdata bosdataadd319                   = BOSdata.new()
htfadd319.settings                 := SettingsHTFadd319
htfadd319.candles                  := candlesadd319
htfadd319.bosdata                  := bosdataadd319
var CandleSet htfadd320                     = CandleSet.new()
var CandleSettings SettingsHTFadd320        = CandleSettings.new(htf='320',htfint=320,max_memory=3)
var Candle[] candlesadd320                  = array.new<Candle>(0)
var BOSdata bosdataadd320                   = BOSdata.new()
htfadd320.settings                 := SettingsHTFadd320
htfadd320.candles                  := candlesadd320
htfadd320.bosdata                  := bosdataadd320
var CandleSet htfadd321                     = CandleSet.new()
var CandleSettings SettingsHTFadd321        = CandleSettings.new(htf='321',htfint=321,max_memory=3)
var Candle[] candlesadd321                  = array.new<Candle>(0)
var BOSdata bosdataadd321                   = BOSdata.new()
htfadd321.settings                 := SettingsHTFadd321
htfadd321.candles                  := candlesadd321
htfadd321.bosdata                  := bosdataadd321
var CandleSet htfadd322                     = CandleSet.new()
var CandleSettings SettingsHTFadd322        = CandleSettings.new(htf='322',htfint=322,max_memory=3)
var Candle[] candlesadd322                  = array.new<Candle>(0)
var BOSdata bosdataadd322                   = BOSdata.new()
htfadd322.settings                 := SettingsHTFadd322
htfadd322.candles                  := candlesadd322
htfadd322.bosdata                  := bosdataadd322
var CandleSet htfadd323                     = CandleSet.new()
var CandleSettings SettingsHTFadd323        = CandleSettings.new(htf='323',htfint=323,max_memory=3)
var Candle[] candlesadd323                  = array.new<Candle>(0)
var BOSdata bosdataadd323                   = BOSdata.new()
htfadd323.settings                 := SettingsHTFadd323
htfadd323.candles                  := candlesadd323
htfadd323.bosdata                  := bosdataadd323
var CandleSet htfadd324                     = CandleSet.new()
var CandleSettings SettingsHTFadd324        = CandleSettings.new(htf='324',htfint=324,max_memory=3)
var Candle[] candlesadd324                  = array.new<Candle>(0)
var BOSdata bosdataadd324                   = BOSdata.new()
htfadd324.settings                 := SettingsHTFadd324
htfadd324.candles                  := candlesadd324
htfadd324.bosdata                  := bosdataadd324
var CandleSet htfadd325                     = CandleSet.new()
var CandleSettings SettingsHTFadd325        = CandleSettings.new(htf='325',htfint=325,max_memory=3)
var Candle[] candlesadd325                  = array.new<Candle>(0)
var BOSdata bosdataadd325                   = BOSdata.new()
htfadd325.settings                 := SettingsHTFadd325
htfadd325.candles                  := candlesadd325
htfadd325.bosdata                  := bosdataadd325
var CandleSet htfadd326                     = CandleSet.new()
var CandleSettings SettingsHTFadd326        = CandleSettings.new(htf='326',htfint=326,max_memory=3)
var Candle[] candlesadd326                  = array.new<Candle>(0)
var BOSdata bosdataadd326                   = BOSdata.new()
htfadd326.settings                 := SettingsHTFadd326
htfadd326.candles                  := candlesadd326
htfadd326.bosdata                  := bosdataadd326
var CandleSet htfadd327                     = CandleSet.new()
var CandleSettings SettingsHTFadd327        = CandleSettings.new(htf='327',htfint=327,max_memory=3)
var Candle[] candlesadd327                  = array.new<Candle>(0)
var BOSdata bosdataadd327                   = BOSdata.new()
htfadd327.settings                 := SettingsHTFadd327
htfadd327.candles                  := candlesadd327
htfadd327.bosdata                  := bosdataadd327
var CandleSet htfadd328                     = CandleSet.new()
var CandleSettings SettingsHTFadd328        = CandleSettings.new(htf='328',htfint=328,max_memory=3)
var Candle[] candlesadd328                  = array.new<Candle>(0)
var BOSdata bosdataadd328                   = BOSdata.new()
htfadd328.settings                 := SettingsHTFadd328
htfadd328.candles                  := candlesadd328
htfadd328.bosdata                  := bosdataadd328
var CandleSet htfadd329                     = CandleSet.new()
var CandleSettings SettingsHTFadd329        = CandleSettings.new(htf='329',htfint=329,max_memory=3)
var Candle[] candlesadd329                  = array.new<Candle>(0)
var BOSdata bosdataadd329                   = BOSdata.new()
htfadd329.settings                 := SettingsHTFadd329
htfadd329.candles                  := candlesadd329
htfadd329.bosdata                  := bosdataadd329
var CandleSet htfadd330                     = CandleSet.new()
var CandleSettings SettingsHTFadd330        = CandleSettings.new(htf='330',htfint=330,max_memory=3)
var Candle[] candlesadd330                  = array.new<Candle>(0)
var BOSdata bosdataadd330                   = BOSdata.new()
htfadd330.settings                 := SettingsHTFadd330
htfadd330.candles                  := candlesadd330
htfadd330.bosdata                  := bosdataadd330
var CandleSet htfadd331                     = CandleSet.new()
var CandleSettings SettingsHTFadd331        = CandleSettings.new(htf='331',htfint=331,max_memory=3)
var Candle[] candlesadd331                  = array.new<Candle>(0)
var BOSdata bosdataadd331                   = BOSdata.new()
htfadd331.settings                 := SettingsHTFadd331
htfadd331.candles                  := candlesadd331
htfadd331.bosdata                  := bosdataadd331
var CandleSet htfadd332                     = CandleSet.new()
var CandleSettings SettingsHTFadd332        = CandleSettings.new(htf='332',htfint=332,max_memory=3)
var Candle[] candlesadd332                  = array.new<Candle>(0)
var BOSdata bosdataadd332                   = BOSdata.new()
htfadd332.settings                 := SettingsHTFadd332
htfadd332.candles                  := candlesadd332
htfadd332.bosdata                  := bosdataadd332
var CandleSet htfadd333                     = CandleSet.new()
var CandleSettings SettingsHTFadd333        = CandleSettings.new(htf='333',htfint=333,max_memory=3)
var Candle[] candlesadd333                  = array.new<Candle>(0)
var BOSdata bosdataadd333                   = BOSdata.new()
htfadd333.settings                 := SettingsHTFadd333
htfadd333.candles                  := candlesadd333
htfadd333.bosdata                  := bosdataadd333
var CandleSet htfadd334                     = CandleSet.new()
var CandleSettings SettingsHTFadd334        = CandleSettings.new(htf='334',htfint=334,max_memory=3)
var Candle[] candlesadd334                  = array.new<Candle>(0)
var BOSdata bosdataadd334                   = BOSdata.new()
htfadd334.settings                 := SettingsHTFadd334
htfadd334.candles                  := candlesadd334
htfadd334.bosdata                  := bosdataadd334
var CandleSet htfadd335                     = CandleSet.new()
var CandleSettings SettingsHTFadd335        = CandleSettings.new(htf='335',htfint=335,max_memory=3)
var Candle[] candlesadd335                  = array.new<Candle>(0)
var BOSdata bosdataadd335                   = BOSdata.new()
htfadd335.settings                 := SettingsHTFadd335
htfadd335.candles                  := candlesadd335
htfadd335.bosdata                  := bosdataadd335
var CandleSet htfadd336                     = CandleSet.new()
var CandleSettings SettingsHTFadd336        = CandleSettings.new(htf='336',htfint=336,max_memory=3)
var Candle[] candlesadd336                  = array.new<Candle>(0)
var BOSdata bosdataadd336                   = BOSdata.new()
htfadd336.settings                 := SettingsHTFadd336
htfadd336.candles                  := candlesadd336
htfadd336.bosdata                  := bosdataadd336
var CandleSet htfadd337                     = CandleSet.new()
var CandleSettings SettingsHTFadd337        = CandleSettings.new(htf='337',htfint=337,max_memory=3)
var Candle[] candlesadd337                  = array.new<Candle>(0)
var BOSdata bosdataadd337                   = BOSdata.new()
htfadd337.settings                 := SettingsHTFadd337
htfadd337.candles                  := candlesadd337
htfadd337.bosdata                  := bosdataadd337
var CandleSet htfadd338                     = CandleSet.new()
var CandleSettings SettingsHTFadd338        = CandleSettings.new(htf='338',htfint=338,max_memory=3)
var Candle[] candlesadd338                  = array.new<Candle>(0)
var BOSdata bosdataadd338                   = BOSdata.new()
htfadd338.settings                 := SettingsHTFadd338
htfadd338.candles                  := candlesadd338
htfadd338.bosdata                  := bosdataadd338
var CandleSet htfadd339                     = CandleSet.new()
var CandleSettings SettingsHTFadd339        = CandleSettings.new(htf='339',htfint=339,max_memory=3)
var Candle[] candlesadd339                  = array.new<Candle>(0)
var BOSdata bosdataadd339                   = BOSdata.new()
htfadd339.settings                 := SettingsHTFadd339
htfadd339.candles                  := candlesadd339
htfadd339.bosdata                  := bosdataadd339
var CandleSet htfadd340                     = CandleSet.new()
var CandleSettings SettingsHTFadd340        = CandleSettings.new(htf='340',htfint=340,max_memory=3)
var Candle[] candlesadd340                  = array.new<Candle>(0)
var BOSdata bosdataadd340                   = BOSdata.new()
htfadd340.settings                 := SettingsHTFadd340
htfadd340.candles                  := candlesadd340
htfadd340.bosdata                  := bosdataadd340
var CandleSet htfadd341                     = CandleSet.new()
var CandleSettings SettingsHTFadd341        = CandleSettings.new(htf='341',htfint=341,max_memory=3)
var Candle[] candlesadd341                  = array.new<Candle>(0)
var BOSdata bosdataadd341                   = BOSdata.new()
htfadd341.settings                 := SettingsHTFadd341
htfadd341.candles                  := candlesadd341
htfadd341.bosdata                  := bosdataadd341
var CandleSet htfadd342                     = CandleSet.new()
var CandleSettings SettingsHTFadd342        = CandleSettings.new(htf='342',htfint=342,max_memory=3)
var Candle[] candlesadd342                  = array.new<Candle>(0)
var BOSdata bosdataadd342                   = BOSdata.new()
htfadd342.settings                 := SettingsHTFadd342
htfadd342.candles                  := candlesadd342
htfadd342.bosdata                  := bosdataadd342
var CandleSet htfadd343                     = CandleSet.new()
var CandleSettings SettingsHTFadd343        = CandleSettings.new(htf='343',htfint=343,max_memory=3)
var Candle[] candlesadd343                  = array.new<Candle>(0)
var BOSdata bosdataadd343                   = BOSdata.new()
htfadd343.settings                 := SettingsHTFadd343
htfadd343.candles                  := candlesadd343
htfadd343.bosdata                  := bosdataadd343
var CandleSet htfadd344                     = CandleSet.new()
var CandleSettings SettingsHTFadd344        = CandleSettings.new(htf='344',htfint=344,max_memory=3)
var Candle[] candlesadd344                  = array.new<Candle>(0)
var BOSdata bosdataadd344                   = BOSdata.new()
htfadd344.settings                 := SettingsHTFadd344
htfadd344.candles                  := candlesadd344
htfadd344.bosdata                  := bosdataadd344
var CandleSet htfadd345                     = CandleSet.new()
var CandleSettings SettingsHTFadd345        = CandleSettings.new(htf='345',htfint=345,max_memory=3)
var Candle[] candlesadd345                  = array.new<Candle>(0)
var BOSdata bosdataadd345                   = BOSdata.new()
htfadd345.settings                 := SettingsHTFadd345
htfadd345.candles                  := candlesadd345
htfadd345.bosdata                  := bosdataadd345
var CandleSet htfadd346                     = CandleSet.new()
var CandleSettings SettingsHTFadd346        = CandleSettings.new(htf='346',htfint=346,max_memory=3)
var Candle[] candlesadd346                  = array.new<Candle>(0)
var BOSdata bosdataadd346                   = BOSdata.new()
htfadd346.settings                 := SettingsHTFadd346
htfadd346.candles                  := candlesadd346
htfadd346.bosdata                  := bosdataadd346
var CandleSet htfadd347                     = CandleSet.new()
var CandleSettings SettingsHTFadd347        = CandleSettings.new(htf='347',htfint=347,max_memory=3)
var Candle[] candlesadd347                  = array.new<Candle>(0)
var BOSdata bosdataadd347                   = BOSdata.new()
htfadd347.settings                 := SettingsHTFadd347
htfadd347.candles                  := candlesadd347
htfadd347.bosdata                  := bosdataadd347
var CandleSet htfadd348                     = CandleSet.new()
var CandleSettings SettingsHTFadd348        = CandleSettings.new(htf='348',htfint=348,max_memory=3)
var Candle[] candlesadd348                  = array.new<Candle>(0)
var BOSdata bosdataadd348                   = BOSdata.new()
htfadd348.settings                 := SettingsHTFadd348
htfadd348.candles                  := candlesadd348
htfadd348.bosdata                  := bosdataadd348
var CandleSet htfadd349                     = CandleSet.new()
var CandleSettings SettingsHTFadd349        = CandleSettings.new(htf='349',htfint=349,max_memory=3)
var Candle[] candlesadd349                  = array.new<Candle>(0)
var BOSdata bosdataadd349                   = BOSdata.new()
htfadd349.settings                 := SettingsHTFadd349
htfadd349.candles                  := candlesadd349
htfadd349.bosdata                  := bosdataadd349
var CandleSet htfadd350                     = CandleSet.new()
var CandleSettings SettingsHTFadd350        = CandleSettings.new(htf='350',htfint=350,max_memory=3)
var Candle[] candlesadd350                  = array.new<Candle>(0)
var BOSdata bosdataadd350                   = BOSdata.new()
htfadd350.settings                 := SettingsHTFadd350
htfadd350.candles                  := candlesadd350
htfadd350.bosdata                  := bosdataadd350
var CandleSet htfadd351                     = CandleSet.new()
var CandleSettings SettingsHTFadd351        = CandleSettings.new(htf='351',htfint=351,max_memory=3)
var Candle[] candlesadd351                  = array.new<Candle>(0)
var BOSdata bosdataadd351                   = BOSdata.new()
htfadd351.settings                 := SettingsHTFadd351
htfadd351.candles                  := candlesadd351
htfadd351.bosdata                  := bosdataadd351
var CandleSet htfadd352                     = CandleSet.new()
var CandleSettings SettingsHTFadd352        = CandleSettings.new(htf='352',htfint=352,max_memory=3)
var Candle[] candlesadd352                  = array.new<Candle>(0)
var BOSdata bosdataadd352                   = BOSdata.new()
htfadd352.settings                 := SettingsHTFadd352
htfadd352.candles                  := candlesadd352
htfadd352.bosdata                  := bosdataadd352
var CandleSet htfadd353                     = CandleSet.new()
var CandleSettings SettingsHTFadd353        = CandleSettings.new(htf='353',htfint=353,max_memory=3)
var Candle[] candlesadd353                  = array.new<Candle>(0)
var BOSdata bosdataadd353                   = BOSdata.new()
htfadd353.settings                 := SettingsHTFadd353
htfadd353.candles                  := candlesadd353
htfadd353.bosdata                  := bosdataadd353
var CandleSet htfadd354                     = CandleSet.new()
var CandleSettings SettingsHTFadd354        = CandleSettings.new(htf='354',htfint=354,max_memory=3)
var Candle[] candlesadd354                  = array.new<Candle>(0)
var BOSdata bosdataadd354                   = BOSdata.new()
htfadd354.settings                 := SettingsHTFadd354
htfadd354.candles                  := candlesadd354
htfadd354.bosdata                  := bosdataadd354
var CandleSet htfadd355                     = CandleSet.new()
var CandleSettings SettingsHTFadd355        = CandleSettings.new(htf='355',htfint=355,max_memory=3)
var Candle[] candlesadd355                  = array.new<Candle>(0)
var BOSdata bosdataadd355                   = BOSdata.new()
htfadd355.settings                 := SettingsHTFadd355
htfadd355.candles                  := candlesadd355
htfadd355.bosdata                  := bosdataadd355
var CandleSet htfadd356                     = CandleSet.new()
var CandleSettings SettingsHTFadd356        = CandleSettings.new(htf='356',htfint=356,max_memory=3)
var Candle[] candlesadd356                  = array.new<Candle>(0)
var BOSdata bosdataadd356                   = BOSdata.new()
htfadd356.settings                 := SettingsHTFadd356
htfadd356.candles                  := candlesadd356
htfadd356.bosdata                  := bosdataadd356
var CandleSet htfadd357                     = CandleSet.new()
var CandleSettings SettingsHTFadd357        = CandleSettings.new(htf='357',htfint=357,max_memory=3)
var Candle[] candlesadd357                  = array.new<Candle>(0)
var BOSdata bosdataadd357                   = BOSdata.new()
htfadd357.settings                 := SettingsHTFadd357
htfadd357.candles                  := candlesadd357
htfadd357.bosdata                  := bosdataadd357
var CandleSet htfadd358                     = CandleSet.new()
var CandleSettings SettingsHTFadd358        = CandleSettings.new(htf='358',htfint=358,max_memory=3)
var Candle[] candlesadd358                  = array.new<Candle>(0)
var BOSdata bosdataadd358                   = BOSdata.new()
htfadd358.settings                 := SettingsHTFadd358
htfadd358.candles                  := candlesadd358
htfadd358.bosdata                  := bosdataadd358
var CandleSet htfadd359                     = CandleSet.new()
var CandleSettings SettingsHTFadd359        = CandleSettings.new(htf='359',htfint=359,max_memory=3)
var Candle[] candlesadd359                  = array.new<Candle>(0)
var BOSdata bosdataadd359                   = BOSdata.new()
htfadd359.settings                 := SettingsHTFadd359
htfadd359.candles                  := candlesadd359
htfadd359.bosdata                  := bosdataadd359
var CandleSet htfadd360                     = CandleSet.new()
var CandleSettings SettingsHTFadd360        = CandleSettings.new(htf='360',htfint=360,max_memory=3)
var Candle[] candlesadd360                  = array.new<Candle>(0)
var BOSdata bosdataadd360                   = BOSdata.new()
htfadd360.settings                 := SettingsHTFadd360
htfadd360.candles                  := candlesadd360
htfadd360.bosdata                  := bosdataadd360

htfadd270.Monitor().BOSJudge()
htfadd271.Monitor().BOSJudge()
htfadd272.Monitor().BOSJudge()
htfadd273.Monitor().BOSJudge()
htfadd274.Monitor().BOSJudge()
htfadd275.Monitor().BOSJudge()
htfadd276.Monitor().BOSJudge()
htfadd277.Monitor().BOSJudge()
htfadd278.Monitor().BOSJudge()
htfadd279.Monitor().BOSJudge()
htfadd280.Monitor().BOSJudge()
htfadd281.Monitor().BOSJudge()
htfadd282.Monitor().BOSJudge()
htfadd283.Monitor().BOSJudge()
htfadd284.Monitor().BOSJudge()
htfadd285.Monitor().BOSJudge()
htfadd286.Monitor().BOSJudge()
htfadd287.Monitor().BOSJudge()
htfadd288.Monitor().BOSJudge()
htfadd289.Monitor().BOSJudge()
htfadd290.Monitor().BOSJudge()
htfadd291.Monitor().BOSJudge()
htfadd292.Monitor().BOSJudge()
htfadd293.Monitor().BOSJudge()
htfadd294.Monitor().BOSJudge()
htfadd295.Monitor().BOSJudge()
htfadd296.Monitor().BOSJudge()
htfadd297.Monitor().BOSJudge()
htfadd298.Monitor().BOSJudge()
htfadd299.Monitor().BOSJudge()
htfadd300.Monitor().BOSJudge()
htfadd301.Monitor().BOSJudge()
htfadd302.Monitor().BOSJudge()
htfadd303.Monitor().BOSJudge()
htfadd304.Monitor().BOSJudge()
htfadd305.Monitor().BOSJudge()
htfadd306.Monitor().BOSJudge()
htfadd307.Monitor().BOSJudge()
htfadd308.Monitor().BOSJudge()
htfadd309.Monitor().BOSJudge()
htfadd310.Monitor().BOSJudge()
htfadd311.Monitor().BOSJudge()
htfadd312.Monitor().BOSJudge()
htfadd313.Monitor().BOSJudge()
htfadd314.Monitor().BOSJudge()
htfadd315.Monitor().BOSJudge()
htfadd316.Monitor().BOSJudge()
htfadd317.Monitor().BOSJudge()
htfadd318.Monitor().BOSJudge()
htfadd319.Monitor().BOSJudge()
htfadd320.Monitor().BOSJudge()
htfadd321.Monitor().BOSJudge()
htfadd322.Monitor().BOSJudge()
htfadd323.Monitor().BOSJudge()
htfadd324.Monitor().BOSJudge()
htfadd325.Monitor().BOSJudge()
htfadd326.Monitor().BOSJudge()
htfadd327.Monitor().BOSJudge()
htfadd328.Monitor().BOSJudge()
htfadd329.Monitor().BOSJudge()
htfadd330.Monitor().BOSJudge()
htfadd331.Monitor().BOSJudge()
htfadd332.Monitor().BOSJudge()
htfadd333.Monitor().BOSJudge()
htfadd334.Monitor().BOSJudge()
htfadd335.Monitor().BOSJudge()
htfadd336.Monitor().BOSJudge()
htfadd337.Monitor().BOSJudge()
htfadd338.Monitor().BOSJudge()
htfadd339.Monitor().BOSJudge()
htfadd340.Monitor().BOSJudge()
htfadd341.Monitor().BOSJudge()
htfadd342.Monitor().BOSJudge()
htfadd343.Monitor().BOSJudge()
htfadd344.Monitor().BOSJudge()
htfadd345.Monitor().BOSJudge()
htfadd346.Monitor().BOSJudge()
htfadd347.Monitor().BOSJudge()
htfadd348.Monitor().BOSJudge()
htfadd349.Monitor().BOSJudge()
htfadd350.Monitor().BOSJudge()
htfadd351.Monitor().BOSJudge()
htfadd352.Monitor().BOSJudge()
htfadd353.Monitor().BOSJudge()
htfadd354.Monitor().BOSJudge()
htfadd355.Monitor().BOSJudge()
htfadd356.Monitor().BOSJudge()
htfadd357.Monitor().BOSJudge()
htfadd358.Monitor().BOSJudge()
htfadd359.Monitor().BOSJudge()
htfadd360.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd270)
    LowestsbuSet(lowestsbu, htfadd270)
    HighestsbdSet(highestsbd, htfadd271)
    LowestsbuSet(lowestsbu, htfadd271)
    HighestsbdSet(highestsbd, htfadd272)
    LowestsbuSet(lowestsbu, htfadd272)
    HighestsbdSet(highestsbd, htfadd273)
    LowestsbuSet(lowestsbu, htfadd273)
    HighestsbdSet(highestsbd, htfadd274)
    LowestsbuSet(lowestsbu, htfadd274)
    HighestsbdSet(highestsbd, htfadd275)
    LowestsbuSet(lowestsbu, htfadd275)
    HighestsbdSet(highestsbd, htfadd276)
    LowestsbuSet(lowestsbu, htfadd276)
    HighestsbdSet(highestsbd, htfadd277)
    LowestsbuSet(lowestsbu, htfadd277)
    HighestsbdSet(highestsbd, htfadd278)
    LowestsbuSet(lowestsbu, htfadd278)
    HighestsbdSet(highestsbd, htfadd279)
    LowestsbuSet(lowestsbu, htfadd279)
    HighestsbdSet(highestsbd, htfadd280)
    LowestsbuSet(lowestsbu, htfadd280)
    HighestsbdSet(highestsbd, htfadd281)
    LowestsbuSet(lowestsbu, htfadd281)
    HighestsbdSet(highestsbd, htfadd282)
    LowestsbuSet(lowestsbu, htfadd282)
    HighestsbdSet(highestsbd, htfadd283)
    LowestsbuSet(lowestsbu, htfadd283)
    HighestsbdSet(highestsbd, htfadd284)
    LowestsbuSet(lowestsbu, htfadd284)
    HighestsbdSet(highestsbd, htfadd285)
    LowestsbuSet(lowestsbu, htfadd285)
    HighestsbdSet(highestsbd, htfadd286)
    LowestsbuSet(lowestsbu, htfadd286)
    HighestsbdSet(highestsbd, htfadd287)
    LowestsbuSet(lowestsbu, htfadd287)
    HighestsbdSet(highestsbd, htfadd288)
    LowestsbuSet(lowestsbu, htfadd288)
    HighestsbdSet(highestsbd, htfadd289)
    LowestsbuSet(lowestsbu, htfadd289)
    HighestsbdSet(highestsbd, htfadd290)
    LowestsbuSet(lowestsbu, htfadd290)
    HighestsbdSet(highestsbd, htfadd291)
    LowestsbuSet(lowestsbu, htfadd291)
    HighestsbdSet(highestsbd, htfadd292)
    LowestsbuSet(lowestsbu, htfadd292)
    HighestsbdSet(highestsbd, htfadd293)
    LowestsbuSet(lowestsbu, htfadd293)
    HighestsbdSet(highestsbd, htfadd294)
    LowestsbuSet(lowestsbu, htfadd294)
    HighestsbdSet(highestsbd, htfadd295)
    LowestsbuSet(lowestsbu, htfadd295)
    HighestsbdSet(highestsbd, htfadd296)
    LowestsbuSet(lowestsbu, htfadd296)
    HighestsbdSet(highestsbd, htfadd297)
    LowestsbuSet(lowestsbu, htfadd297)
    HighestsbdSet(highestsbd, htfadd298)
    LowestsbuSet(lowestsbu, htfadd298)
    HighestsbdSet(highestsbd, htfadd299)
    LowestsbuSet(lowestsbu, htfadd299)
    HighestsbdSet(highestsbd, htfadd300)
    LowestsbuSet(lowestsbu, htfadd300)
    HighestsbdSet(highestsbd, htfadd301)
    LowestsbuSet(lowestsbu, htfadd301)
    HighestsbdSet(highestsbd, htfadd302)
    LowestsbuSet(lowestsbu, htfadd302)
    HighestsbdSet(highestsbd, htfadd303)
    LowestsbuSet(lowestsbu, htfadd303)
    HighestsbdSet(highestsbd, htfadd304)
    LowestsbuSet(lowestsbu, htfadd304)
    HighestsbdSet(highestsbd, htfadd305)
    LowestsbuSet(lowestsbu, htfadd305)
    HighestsbdSet(highestsbd, htfadd306)
    LowestsbuSet(lowestsbu, htfadd306)
    HighestsbdSet(highestsbd, htfadd307)
    LowestsbuSet(lowestsbu, htfadd307)
    HighestsbdSet(highestsbd, htfadd308)
    LowestsbuSet(lowestsbu, htfadd308)
    HighestsbdSet(highestsbd, htfadd309)
    LowestsbuSet(lowestsbu, htfadd309)
    HighestsbdSet(highestsbd, htfadd310)
    LowestsbuSet(lowestsbu, htfadd310)
    HighestsbdSet(highestsbd, htfadd311)
    LowestsbuSet(lowestsbu, htfadd311)
    HighestsbdSet(highestsbd, htfadd312)
    LowestsbuSet(lowestsbu, htfadd312)
    HighestsbdSet(highestsbd, htfadd313)
    LowestsbuSet(lowestsbu, htfadd313)
    HighestsbdSet(highestsbd, htfadd314)
    LowestsbuSet(lowestsbu, htfadd314)
    HighestsbdSet(highestsbd, htfadd315)
    LowestsbuSet(lowestsbu, htfadd315)
    HighestsbdSet(highestsbd, htfadd316)
    LowestsbuSet(lowestsbu, htfadd316)
    HighestsbdSet(highestsbd, htfadd317)
    LowestsbuSet(lowestsbu, htfadd317)
    HighestsbdSet(highestsbd, htfadd318)
    LowestsbuSet(lowestsbu, htfadd318)
    HighestsbdSet(highestsbd, htfadd319)
    LowestsbuSet(lowestsbu, htfadd319)
    HighestsbdSet(highestsbd, htfadd320)
    LowestsbuSet(lowestsbu, htfadd320)
    HighestsbdSet(highestsbd, htfadd321)
    LowestsbuSet(lowestsbu, htfadd321)
    HighestsbdSet(highestsbd, htfadd322)
    LowestsbuSet(lowestsbu, htfadd322)
    HighestsbdSet(highestsbd, htfadd323)
    LowestsbuSet(lowestsbu, htfadd323)
    HighestsbdSet(highestsbd, htfadd324)
    LowestsbuSet(lowestsbu, htfadd324)
    HighestsbdSet(highestsbd, htfadd325)
    LowestsbuSet(lowestsbu, htfadd325)
    HighestsbdSet(highestsbd, htfadd326)
    LowestsbuSet(lowestsbu, htfadd326)
    HighestsbdSet(highestsbd, htfadd327)
    LowestsbuSet(lowestsbu, htfadd327)
    HighestsbdSet(highestsbd, htfadd328)
    LowestsbuSet(lowestsbu, htfadd328)
    HighestsbdSet(highestsbd, htfadd329)
    LowestsbuSet(lowestsbu, htfadd329)
    HighestsbdSet(highestsbd, htfadd330)
    LowestsbuSet(lowestsbu, htfadd330)
    HighestsbdSet(highestsbd, htfadd331)
    LowestsbuSet(lowestsbu, htfadd331)
    HighestsbdSet(highestsbd, htfadd332)
    LowestsbuSet(lowestsbu, htfadd332)
    HighestsbdSet(highestsbd, htfadd333)
    LowestsbuSet(lowestsbu, htfadd333)
    HighestsbdSet(highestsbd, htfadd334)
    LowestsbuSet(lowestsbu, htfadd334)
    HighestsbdSet(highestsbd, htfadd335)
    LowestsbuSet(lowestsbu, htfadd335)
    HighestsbdSet(highestsbd, htfadd336)
    LowestsbuSet(lowestsbu, htfadd336)
    HighestsbdSet(highestsbd, htfadd337)
    LowestsbuSet(lowestsbu, htfadd337)
    HighestsbdSet(highestsbd, htfadd338)
    LowestsbuSet(lowestsbu, htfadd338)
    HighestsbdSet(highestsbd, htfadd339)
    LowestsbuSet(lowestsbu, htfadd339)
    HighestsbdSet(highestsbd, htfadd340)
    LowestsbuSet(lowestsbu, htfadd340)
    HighestsbdSet(highestsbd, htfadd341)
    LowestsbuSet(lowestsbu, htfadd341)
    HighestsbdSet(highestsbd, htfadd342)
    LowestsbuSet(lowestsbu, htfadd342)
    HighestsbdSet(highestsbd, htfadd343)
    LowestsbuSet(lowestsbu, htfadd343)
    HighestsbdSet(highestsbd, htfadd344)
    LowestsbuSet(lowestsbu, htfadd344)
    HighestsbdSet(highestsbd, htfadd345)
    LowestsbuSet(lowestsbu, htfadd345)
    HighestsbdSet(highestsbd, htfadd346)
    LowestsbuSet(lowestsbu, htfadd346)
    HighestsbdSet(highestsbd, htfadd347)
    LowestsbuSet(lowestsbu, htfadd347)
    HighestsbdSet(highestsbd, htfadd348)
    LowestsbuSet(lowestsbu, htfadd348)
    HighestsbdSet(highestsbd, htfadd349)
    LowestsbuSet(lowestsbu, htfadd349)
    HighestsbdSet(highestsbd, htfadd350)
    LowestsbuSet(lowestsbu, htfadd350)
    HighestsbdSet(highestsbd, htfadd351)
    LowestsbuSet(lowestsbu, htfadd351)
    HighestsbdSet(highestsbd, htfadd352)
    LowestsbuSet(lowestsbu, htfadd352)
    HighestsbdSet(highestsbd, htfadd353)
    LowestsbuSet(lowestsbu, htfadd353)
    HighestsbdSet(highestsbd, htfadd354)
    LowestsbuSet(lowestsbu, htfadd354)
    HighestsbdSet(highestsbd, htfadd355)
    LowestsbuSet(lowestsbu, htfadd355)
    HighestsbdSet(highestsbd, htfadd356)
    LowestsbuSet(lowestsbu, htfadd356)
    HighestsbdSet(highestsbd, htfadd357)
    LowestsbuSet(lowestsbu, htfadd357)
    HighestsbdSet(highestsbd, htfadd358)
    LowestsbuSet(lowestsbu, htfadd358)
    HighestsbdSet(highestsbd, htfadd359)
    LowestsbuSet(lowestsbu, htfadd359)
    HighestsbdSet(highestsbd, htfadd360)
    LowestsbuSet(lowestsbu, htfadd360)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd270).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd271).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd272).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd273).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd274).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd275).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd276).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd277).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd278).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd279).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd280).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd281).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd282).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd283).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd284).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd285).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd286).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd287).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd288).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd289).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd290).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd291).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd292).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd293).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd294).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd295).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd296).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd297).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd298).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd299).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd300).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd301).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd302).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd303).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd304).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd305).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd306).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd307).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd308).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd309).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd310).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd311).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd312).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd313).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd314).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd315).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd316).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd317).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd318).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd319).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd320).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd321).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd322).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd323).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd324).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd325).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd326).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd327).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd328).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd329).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd330).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd331).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd332).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd333).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd334).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd335).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd336).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd337).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd338).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd339).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd340).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd341).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd342).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd343).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd344).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd345).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd346).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd347).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd348).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd349).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd350).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd351).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd352).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd353).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd354).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd355).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd356).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd357).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd358).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd359).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd360).Monitor_Est().BOSJudge()
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


