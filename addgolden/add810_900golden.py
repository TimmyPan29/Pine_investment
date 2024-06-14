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
var CandleSet htfadd810                     = CandleSet.new()
var CandleSettings SettingsHTFadd810        = CandleSettings.new(htf='810',htfint=810,max_memory=3)
var Candle[] candlesadd810                  = array.new<Candle>(0)
var BOSdata bosdataadd810                   = BOSdata.new()
htfadd810.settings                 := SettingsHTFadd810
htfadd810.candles                  := candlesadd810
htfadd810.bosdata                  := bosdataadd810
var CandleSet htfadd811                     = CandleSet.new()
var CandleSettings SettingsHTFadd811        = CandleSettings.new(htf='811',htfint=811,max_memory=3)
var Candle[] candlesadd811                  = array.new<Candle>(0)
var BOSdata bosdataadd811                   = BOSdata.new()
htfadd811.settings                 := SettingsHTFadd811
htfadd811.candles                  := candlesadd811
htfadd811.bosdata                  := bosdataadd811
var CandleSet htfadd812                     = CandleSet.new()
var CandleSettings SettingsHTFadd812        = CandleSettings.new(htf='812',htfint=812,max_memory=3)
var Candle[] candlesadd812                  = array.new<Candle>(0)
var BOSdata bosdataadd812                   = BOSdata.new()
htfadd812.settings                 := SettingsHTFadd812
htfadd812.candles                  := candlesadd812
htfadd812.bosdata                  := bosdataadd812
var CandleSet htfadd813                     = CandleSet.new()
var CandleSettings SettingsHTFadd813        = CandleSettings.new(htf='813',htfint=813,max_memory=3)
var Candle[] candlesadd813                  = array.new<Candle>(0)
var BOSdata bosdataadd813                   = BOSdata.new()
htfadd813.settings                 := SettingsHTFadd813
htfadd813.candles                  := candlesadd813
htfadd813.bosdata                  := bosdataadd813
var CandleSet htfadd814                     = CandleSet.new()
var CandleSettings SettingsHTFadd814        = CandleSettings.new(htf='814',htfint=814,max_memory=3)
var Candle[] candlesadd814                  = array.new<Candle>(0)
var BOSdata bosdataadd814                   = BOSdata.new()
htfadd814.settings                 := SettingsHTFadd814
htfadd814.candles                  := candlesadd814
htfadd814.bosdata                  := bosdataadd814
var CandleSet htfadd815                     = CandleSet.new()
var CandleSettings SettingsHTFadd815        = CandleSettings.new(htf='815',htfint=815,max_memory=3)
var Candle[] candlesadd815                  = array.new<Candle>(0)
var BOSdata bosdataadd815                   = BOSdata.new()
htfadd815.settings                 := SettingsHTFadd815
htfadd815.candles                  := candlesadd815
htfadd815.bosdata                  := bosdataadd815
var CandleSet htfadd816                     = CandleSet.new()
var CandleSettings SettingsHTFadd816        = CandleSettings.new(htf='816',htfint=816,max_memory=3)
var Candle[] candlesadd816                  = array.new<Candle>(0)
var BOSdata bosdataadd816                   = BOSdata.new()
htfadd816.settings                 := SettingsHTFadd816
htfadd816.candles                  := candlesadd816
htfadd816.bosdata                  := bosdataadd816
var CandleSet htfadd817                     = CandleSet.new()
var CandleSettings SettingsHTFadd817        = CandleSettings.new(htf='817',htfint=817,max_memory=3)
var Candle[] candlesadd817                  = array.new<Candle>(0)
var BOSdata bosdataadd817                   = BOSdata.new()
htfadd817.settings                 := SettingsHTFadd817
htfadd817.candles                  := candlesadd817
htfadd817.bosdata                  := bosdataadd817
var CandleSet htfadd818                     = CandleSet.new()
var CandleSettings SettingsHTFadd818        = CandleSettings.new(htf='818',htfint=818,max_memory=3)
var Candle[] candlesadd818                  = array.new<Candle>(0)
var BOSdata bosdataadd818                   = BOSdata.new()
htfadd818.settings                 := SettingsHTFadd818
htfadd818.candles                  := candlesadd818
htfadd818.bosdata                  := bosdataadd818
var CandleSet htfadd819                     = CandleSet.new()
var CandleSettings SettingsHTFadd819        = CandleSettings.new(htf='819',htfint=819,max_memory=3)
var Candle[] candlesadd819                  = array.new<Candle>(0)
var BOSdata bosdataadd819                   = BOSdata.new()
htfadd819.settings                 := SettingsHTFadd819
htfadd819.candles                  := candlesadd819
htfadd819.bosdata                  := bosdataadd819
var CandleSet htfadd820                     = CandleSet.new()
var CandleSettings SettingsHTFadd820        = CandleSettings.new(htf='820',htfint=820,max_memory=3)
var Candle[] candlesadd820                  = array.new<Candle>(0)
var BOSdata bosdataadd820                   = BOSdata.new()
htfadd820.settings                 := SettingsHTFadd820
htfadd820.candles                  := candlesadd820
htfadd820.bosdata                  := bosdataadd820
var CandleSet htfadd821                     = CandleSet.new()
var CandleSettings SettingsHTFadd821        = CandleSettings.new(htf='821',htfint=821,max_memory=3)
var Candle[] candlesadd821                  = array.new<Candle>(0)
var BOSdata bosdataadd821                   = BOSdata.new()
htfadd821.settings                 := SettingsHTFadd821
htfadd821.candles                  := candlesadd821
htfadd821.bosdata                  := bosdataadd821
var CandleSet htfadd822                     = CandleSet.new()
var CandleSettings SettingsHTFadd822        = CandleSettings.new(htf='822',htfint=822,max_memory=3)
var Candle[] candlesadd822                  = array.new<Candle>(0)
var BOSdata bosdataadd822                   = BOSdata.new()
htfadd822.settings                 := SettingsHTFadd822
htfadd822.candles                  := candlesadd822
htfadd822.bosdata                  := bosdataadd822
var CandleSet htfadd823                     = CandleSet.new()
var CandleSettings SettingsHTFadd823        = CandleSettings.new(htf='823',htfint=823,max_memory=3)
var Candle[] candlesadd823                  = array.new<Candle>(0)
var BOSdata bosdataadd823                   = BOSdata.new()
htfadd823.settings                 := SettingsHTFadd823
htfadd823.candles                  := candlesadd823
htfadd823.bosdata                  := bosdataadd823
var CandleSet htfadd824                     = CandleSet.new()
var CandleSettings SettingsHTFadd824        = CandleSettings.new(htf='824',htfint=824,max_memory=3)
var Candle[] candlesadd824                  = array.new<Candle>(0)
var BOSdata bosdataadd824                   = BOSdata.new()
htfadd824.settings                 := SettingsHTFadd824
htfadd824.candles                  := candlesadd824
htfadd824.bosdata                  := bosdataadd824
var CandleSet htfadd825                     = CandleSet.new()
var CandleSettings SettingsHTFadd825        = CandleSettings.new(htf='825',htfint=825,max_memory=3)
var Candle[] candlesadd825                  = array.new<Candle>(0)
var BOSdata bosdataadd825                   = BOSdata.new()
htfadd825.settings                 := SettingsHTFadd825
htfadd825.candles                  := candlesadd825
htfadd825.bosdata                  := bosdataadd825
var CandleSet htfadd826                     = CandleSet.new()
var CandleSettings SettingsHTFadd826        = CandleSettings.new(htf='826',htfint=826,max_memory=3)
var Candle[] candlesadd826                  = array.new<Candle>(0)
var BOSdata bosdataadd826                   = BOSdata.new()
htfadd826.settings                 := SettingsHTFadd826
htfadd826.candles                  := candlesadd826
htfadd826.bosdata                  := bosdataadd826
var CandleSet htfadd827                     = CandleSet.new()
var CandleSettings SettingsHTFadd827        = CandleSettings.new(htf='827',htfint=827,max_memory=3)
var Candle[] candlesadd827                  = array.new<Candle>(0)
var BOSdata bosdataadd827                   = BOSdata.new()
htfadd827.settings                 := SettingsHTFadd827
htfadd827.candles                  := candlesadd827
htfadd827.bosdata                  := bosdataadd827
var CandleSet htfadd828                     = CandleSet.new()
var CandleSettings SettingsHTFadd828        = CandleSettings.new(htf='828',htfint=828,max_memory=3)
var Candle[] candlesadd828                  = array.new<Candle>(0)
var BOSdata bosdataadd828                   = BOSdata.new()
htfadd828.settings                 := SettingsHTFadd828
htfadd828.candles                  := candlesadd828
htfadd828.bosdata                  := bosdataadd828
var CandleSet htfadd829                     = CandleSet.new()
var CandleSettings SettingsHTFadd829        = CandleSettings.new(htf='829',htfint=829,max_memory=3)
var Candle[] candlesadd829                  = array.new<Candle>(0)
var BOSdata bosdataadd829                   = BOSdata.new()
htfadd829.settings                 := SettingsHTFadd829
htfadd829.candles                  := candlesadd829
htfadd829.bosdata                  := bosdataadd829
var CandleSet htfadd830                     = CandleSet.new()
var CandleSettings SettingsHTFadd830        = CandleSettings.new(htf='830',htfint=830,max_memory=3)
var Candle[] candlesadd830                  = array.new<Candle>(0)
var BOSdata bosdataadd830                   = BOSdata.new()
htfadd830.settings                 := SettingsHTFadd830
htfadd830.candles                  := candlesadd830
htfadd830.bosdata                  := bosdataadd830
var CandleSet htfadd831                     = CandleSet.new()
var CandleSettings SettingsHTFadd831        = CandleSettings.new(htf='831',htfint=831,max_memory=3)
var Candle[] candlesadd831                  = array.new<Candle>(0)
var BOSdata bosdataadd831                   = BOSdata.new()
htfadd831.settings                 := SettingsHTFadd831
htfadd831.candles                  := candlesadd831
htfadd831.bosdata                  := bosdataadd831
var CandleSet htfadd832                     = CandleSet.new()
var CandleSettings SettingsHTFadd832        = CandleSettings.new(htf='832',htfint=832,max_memory=3)
var Candle[] candlesadd832                  = array.new<Candle>(0)
var BOSdata bosdataadd832                   = BOSdata.new()
htfadd832.settings                 := SettingsHTFadd832
htfadd832.candles                  := candlesadd832
htfadd832.bosdata                  := bosdataadd832
var CandleSet htfadd833                     = CandleSet.new()
var CandleSettings SettingsHTFadd833        = CandleSettings.new(htf='833',htfint=833,max_memory=3)
var Candle[] candlesadd833                  = array.new<Candle>(0)
var BOSdata bosdataadd833                   = BOSdata.new()
htfadd833.settings                 := SettingsHTFadd833
htfadd833.candles                  := candlesadd833
htfadd833.bosdata                  := bosdataadd833
var CandleSet htfadd834                     = CandleSet.new()
var CandleSettings SettingsHTFadd834        = CandleSettings.new(htf='834',htfint=834,max_memory=3)
var Candle[] candlesadd834                  = array.new<Candle>(0)
var BOSdata bosdataadd834                   = BOSdata.new()
htfadd834.settings                 := SettingsHTFadd834
htfadd834.candles                  := candlesadd834
htfadd834.bosdata                  := bosdataadd834
var CandleSet htfadd835                     = CandleSet.new()
var CandleSettings SettingsHTFadd835        = CandleSettings.new(htf='835',htfint=835,max_memory=3)
var Candle[] candlesadd835                  = array.new<Candle>(0)
var BOSdata bosdataadd835                   = BOSdata.new()
htfadd835.settings                 := SettingsHTFadd835
htfadd835.candles                  := candlesadd835
htfadd835.bosdata                  := bosdataadd835
var CandleSet htfadd836                     = CandleSet.new()
var CandleSettings SettingsHTFadd836        = CandleSettings.new(htf='836',htfint=836,max_memory=3)
var Candle[] candlesadd836                  = array.new<Candle>(0)
var BOSdata bosdataadd836                   = BOSdata.new()
htfadd836.settings                 := SettingsHTFadd836
htfadd836.candles                  := candlesadd836
htfadd836.bosdata                  := bosdataadd836
var CandleSet htfadd837                     = CandleSet.new()
var CandleSettings SettingsHTFadd837        = CandleSettings.new(htf='837',htfint=837,max_memory=3)
var Candle[] candlesadd837                  = array.new<Candle>(0)
var BOSdata bosdataadd837                   = BOSdata.new()
htfadd837.settings                 := SettingsHTFadd837
htfadd837.candles                  := candlesadd837
htfadd837.bosdata                  := bosdataadd837
var CandleSet htfadd838                     = CandleSet.new()
var CandleSettings SettingsHTFadd838        = CandleSettings.new(htf='838',htfint=838,max_memory=3)
var Candle[] candlesadd838                  = array.new<Candle>(0)
var BOSdata bosdataadd838                   = BOSdata.new()
htfadd838.settings                 := SettingsHTFadd838
htfadd838.candles                  := candlesadd838
htfadd838.bosdata                  := bosdataadd838
var CandleSet htfadd839                     = CandleSet.new()
var CandleSettings SettingsHTFadd839        = CandleSettings.new(htf='839',htfint=839,max_memory=3)
var Candle[] candlesadd839                  = array.new<Candle>(0)
var BOSdata bosdataadd839                   = BOSdata.new()
htfadd839.settings                 := SettingsHTFadd839
htfadd839.candles                  := candlesadd839
htfadd839.bosdata                  := bosdataadd839
var CandleSet htfadd840                     = CandleSet.new()
var CandleSettings SettingsHTFadd840        = CandleSettings.new(htf='840',htfint=840,max_memory=3)
var Candle[] candlesadd840                  = array.new<Candle>(0)
var BOSdata bosdataadd840                   = BOSdata.new()
htfadd840.settings                 := SettingsHTFadd840
htfadd840.candles                  := candlesadd840
htfadd840.bosdata                  := bosdataadd840
var CandleSet htfadd841                     = CandleSet.new()
var CandleSettings SettingsHTFadd841        = CandleSettings.new(htf='841',htfint=841,max_memory=3)
var Candle[] candlesadd841                  = array.new<Candle>(0)
var BOSdata bosdataadd841                   = BOSdata.new()
htfadd841.settings                 := SettingsHTFadd841
htfadd841.candles                  := candlesadd841
htfadd841.bosdata                  := bosdataadd841
var CandleSet htfadd842                     = CandleSet.new()
var CandleSettings SettingsHTFadd842        = CandleSettings.new(htf='842',htfint=842,max_memory=3)
var Candle[] candlesadd842                  = array.new<Candle>(0)
var BOSdata bosdataadd842                   = BOSdata.new()
htfadd842.settings                 := SettingsHTFadd842
htfadd842.candles                  := candlesadd842
htfadd842.bosdata                  := bosdataadd842
var CandleSet htfadd843                     = CandleSet.new()
var CandleSettings SettingsHTFadd843        = CandleSettings.new(htf='843',htfint=843,max_memory=3)
var Candle[] candlesadd843                  = array.new<Candle>(0)
var BOSdata bosdataadd843                   = BOSdata.new()
htfadd843.settings                 := SettingsHTFadd843
htfadd843.candles                  := candlesadd843
htfadd843.bosdata                  := bosdataadd843
var CandleSet htfadd844                     = CandleSet.new()
var CandleSettings SettingsHTFadd844        = CandleSettings.new(htf='844',htfint=844,max_memory=3)
var Candle[] candlesadd844                  = array.new<Candle>(0)
var BOSdata bosdataadd844                   = BOSdata.new()
htfadd844.settings                 := SettingsHTFadd844
htfadd844.candles                  := candlesadd844
htfadd844.bosdata                  := bosdataadd844
var CandleSet htfadd845                     = CandleSet.new()
var CandleSettings SettingsHTFadd845        = CandleSettings.new(htf='845',htfint=845,max_memory=3)
var Candle[] candlesadd845                  = array.new<Candle>(0)
var BOSdata bosdataadd845                   = BOSdata.new()
htfadd845.settings                 := SettingsHTFadd845
htfadd845.candles                  := candlesadd845
htfadd845.bosdata                  := bosdataadd845
var CandleSet htfadd846                     = CandleSet.new()
var CandleSettings SettingsHTFadd846        = CandleSettings.new(htf='846',htfint=846,max_memory=3)
var Candle[] candlesadd846                  = array.new<Candle>(0)
var BOSdata bosdataadd846                   = BOSdata.new()
htfadd846.settings                 := SettingsHTFadd846
htfadd846.candles                  := candlesadd846
htfadd846.bosdata                  := bosdataadd846
var CandleSet htfadd847                     = CandleSet.new()
var CandleSettings SettingsHTFadd847        = CandleSettings.new(htf='847',htfint=847,max_memory=3)
var Candle[] candlesadd847                  = array.new<Candle>(0)
var BOSdata bosdataadd847                   = BOSdata.new()
htfadd847.settings                 := SettingsHTFadd847
htfadd847.candles                  := candlesadd847
htfadd847.bosdata                  := bosdataadd847
var CandleSet htfadd848                     = CandleSet.new()
var CandleSettings SettingsHTFadd848        = CandleSettings.new(htf='848',htfint=848,max_memory=3)
var Candle[] candlesadd848                  = array.new<Candle>(0)
var BOSdata bosdataadd848                   = BOSdata.new()
htfadd848.settings                 := SettingsHTFadd848
htfadd848.candles                  := candlesadd848
htfadd848.bosdata                  := bosdataadd848
var CandleSet htfadd849                     = CandleSet.new()
var CandleSettings SettingsHTFadd849        = CandleSettings.new(htf='849',htfint=849,max_memory=3)
var Candle[] candlesadd849                  = array.new<Candle>(0)
var BOSdata bosdataadd849                   = BOSdata.new()
htfadd849.settings                 := SettingsHTFadd849
htfadd849.candles                  := candlesadd849
htfadd849.bosdata                  := bosdataadd849
var CandleSet htfadd850                     = CandleSet.new()
var CandleSettings SettingsHTFadd850        = CandleSettings.new(htf='850',htfint=850,max_memory=3)
var Candle[] candlesadd850                  = array.new<Candle>(0)
var BOSdata bosdataadd850                   = BOSdata.new()
htfadd850.settings                 := SettingsHTFadd850
htfadd850.candles                  := candlesadd850
htfadd850.bosdata                  := bosdataadd850
var CandleSet htfadd851                     = CandleSet.new()
var CandleSettings SettingsHTFadd851        = CandleSettings.new(htf='851',htfint=851,max_memory=3)
var Candle[] candlesadd851                  = array.new<Candle>(0)
var BOSdata bosdataadd851                   = BOSdata.new()
htfadd851.settings                 := SettingsHTFadd851
htfadd851.candles                  := candlesadd851
htfadd851.bosdata                  := bosdataadd851
var CandleSet htfadd852                     = CandleSet.new()
var CandleSettings SettingsHTFadd852        = CandleSettings.new(htf='852',htfint=852,max_memory=3)
var Candle[] candlesadd852                  = array.new<Candle>(0)
var BOSdata bosdataadd852                   = BOSdata.new()
htfadd852.settings                 := SettingsHTFadd852
htfadd852.candles                  := candlesadd852
htfadd852.bosdata                  := bosdataadd852
var CandleSet htfadd853                     = CandleSet.new()
var CandleSettings SettingsHTFadd853        = CandleSettings.new(htf='853',htfint=853,max_memory=3)
var Candle[] candlesadd853                  = array.new<Candle>(0)
var BOSdata bosdataadd853                   = BOSdata.new()
htfadd853.settings                 := SettingsHTFadd853
htfadd853.candles                  := candlesadd853
htfadd853.bosdata                  := bosdataadd853
var CandleSet htfadd854                     = CandleSet.new()
var CandleSettings SettingsHTFadd854        = CandleSettings.new(htf='854',htfint=854,max_memory=3)
var Candle[] candlesadd854                  = array.new<Candle>(0)
var BOSdata bosdataadd854                   = BOSdata.new()
htfadd854.settings                 := SettingsHTFadd854
htfadd854.candles                  := candlesadd854
htfadd854.bosdata                  := bosdataadd854
var CandleSet htfadd855                     = CandleSet.new()
var CandleSettings SettingsHTFadd855        = CandleSettings.new(htf='855',htfint=855,max_memory=3)
var Candle[] candlesadd855                  = array.new<Candle>(0)
var BOSdata bosdataadd855                   = BOSdata.new()
htfadd855.settings                 := SettingsHTFadd855
htfadd855.candles                  := candlesadd855
htfadd855.bosdata                  := bosdataadd855
var CandleSet htfadd856                     = CandleSet.new()
var CandleSettings SettingsHTFadd856        = CandleSettings.new(htf='856',htfint=856,max_memory=3)
var Candle[] candlesadd856                  = array.new<Candle>(0)
var BOSdata bosdataadd856                   = BOSdata.new()
htfadd856.settings                 := SettingsHTFadd856
htfadd856.candles                  := candlesadd856
htfadd856.bosdata                  := bosdataadd856
var CandleSet htfadd857                     = CandleSet.new()
var CandleSettings SettingsHTFadd857        = CandleSettings.new(htf='857',htfint=857,max_memory=3)
var Candle[] candlesadd857                  = array.new<Candle>(0)
var BOSdata bosdataadd857                   = BOSdata.new()
htfadd857.settings                 := SettingsHTFadd857
htfadd857.candles                  := candlesadd857
htfadd857.bosdata                  := bosdataadd857
var CandleSet htfadd858                     = CandleSet.new()
var CandleSettings SettingsHTFadd858        = CandleSettings.new(htf='858',htfint=858,max_memory=3)
var Candle[] candlesadd858                  = array.new<Candle>(0)
var BOSdata bosdataadd858                   = BOSdata.new()
htfadd858.settings                 := SettingsHTFadd858
htfadd858.candles                  := candlesadd858
htfadd858.bosdata                  := bosdataadd858
var CandleSet htfadd859                     = CandleSet.new()
var CandleSettings SettingsHTFadd859        = CandleSettings.new(htf='859',htfint=859,max_memory=3)
var Candle[] candlesadd859                  = array.new<Candle>(0)
var BOSdata bosdataadd859                   = BOSdata.new()
htfadd859.settings                 := SettingsHTFadd859
htfadd859.candles                  := candlesadd859
htfadd859.bosdata                  := bosdataadd859
var CandleSet htfadd860                     = CandleSet.new()
var CandleSettings SettingsHTFadd860        = CandleSettings.new(htf='860',htfint=860,max_memory=3)
var Candle[] candlesadd860                  = array.new<Candle>(0)
var BOSdata bosdataadd860                   = BOSdata.new()
htfadd860.settings                 := SettingsHTFadd860
htfadd860.candles                  := candlesadd860
htfadd860.bosdata                  := bosdataadd860
var CandleSet htfadd861                     = CandleSet.new()
var CandleSettings SettingsHTFadd861        = CandleSettings.new(htf='861',htfint=861,max_memory=3)
var Candle[] candlesadd861                  = array.new<Candle>(0)
var BOSdata bosdataadd861                   = BOSdata.new()
htfadd861.settings                 := SettingsHTFadd861
htfadd861.candles                  := candlesadd861
htfadd861.bosdata                  := bosdataadd861
var CandleSet htfadd862                     = CandleSet.new()
var CandleSettings SettingsHTFadd862        = CandleSettings.new(htf='862',htfint=862,max_memory=3)
var Candle[] candlesadd862                  = array.new<Candle>(0)
var BOSdata bosdataadd862                   = BOSdata.new()
htfadd862.settings                 := SettingsHTFadd862
htfadd862.candles                  := candlesadd862
htfadd862.bosdata                  := bosdataadd862
var CandleSet htfadd863                     = CandleSet.new()
var CandleSettings SettingsHTFadd863        = CandleSettings.new(htf='863',htfint=863,max_memory=3)
var Candle[] candlesadd863                  = array.new<Candle>(0)
var BOSdata bosdataadd863                   = BOSdata.new()
htfadd863.settings                 := SettingsHTFadd863
htfadd863.candles                  := candlesadd863
htfadd863.bosdata                  := bosdataadd863
var CandleSet htfadd864                     = CandleSet.new()
var CandleSettings SettingsHTFadd864        = CandleSettings.new(htf='864',htfint=864,max_memory=3)
var Candle[] candlesadd864                  = array.new<Candle>(0)
var BOSdata bosdataadd864                   = BOSdata.new()
htfadd864.settings                 := SettingsHTFadd864
htfadd864.candles                  := candlesadd864
htfadd864.bosdata                  := bosdataadd864
var CandleSet htfadd865                     = CandleSet.new()
var CandleSettings SettingsHTFadd865        = CandleSettings.new(htf='865',htfint=865,max_memory=3)
var Candle[] candlesadd865                  = array.new<Candle>(0)
var BOSdata bosdataadd865                   = BOSdata.new()
htfadd865.settings                 := SettingsHTFadd865
htfadd865.candles                  := candlesadd865
htfadd865.bosdata                  := bosdataadd865
var CandleSet htfadd866                     = CandleSet.new()
var CandleSettings SettingsHTFadd866        = CandleSettings.new(htf='866',htfint=866,max_memory=3)
var Candle[] candlesadd866                  = array.new<Candle>(0)
var BOSdata bosdataadd866                   = BOSdata.new()
htfadd866.settings                 := SettingsHTFadd866
htfadd866.candles                  := candlesadd866
htfadd866.bosdata                  := bosdataadd866
var CandleSet htfadd867                     = CandleSet.new()
var CandleSettings SettingsHTFadd867        = CandleSettings.new(htf='867',htfint=867,max_memory=3)
var Candle[] candlesadd867                  = array.new<Candle>(0)
var BOSdata bosdataadd867                   = BOSdata.new()
htfadd867.settings                 := SettingsHTFadd867
htfadd867.candles                  := candlesadd867
htfadd867.bosdata                  := bosdataadd867
var CandleSet htfadd868                     = CandleSet.new()
var CandleSettings SettingsHTFadd868        = CandleSettings.new(htf='868',htfint=868,max_memory=3)
var Candle[] candlesadd868                  = array.new<Candle>(0)
var BOSdata bosdataadd868                   = BOSdata.new()
htfadd868.settings                 := SettingsHTFadd868
htfadd868.candles                  := candlesadd868
htfadd868.bosdata                  := bosdataadd868
var CandleSet htfadd869                     = CandleSet.new()
var CandleSettings SettingsHTFadd869        = CandleSettings.new(htf='869',htfint=869,max_memory=3)
var Candle[] candlesadd869                  = array.new<Candle>(0)
var BOSdata bosdataadd869                   = BOSdata.new()
htfadd869.settings                 := SettingsHTFadd869
htfadd869.candles                  := candlesadd869
htfadd869.bosdata                  := bosdataadd869
var CandleSet htfadd870                     = CandleSet.new()
var CandleSettings SettingsHTFadd870        = CandleSettings.new(htf='870',htfint=870,max_memory=3)
var Candle[] candlesadd870                  = array.new<Candle>(0)
var BOSdata bosdataadd870                   = BOSdata.new()
htfadd870.settings                 := SettingsHTFadd870
htfadd870.candles                  := candlesadd870
htfadd870.bosdata                  := bosdataadd870
var CandleSet htfadd871                     = CandleSet.new()
var CandleSettings SettingsHTFadd871        = CandleSettings.new(htf='871',htfint=871,max_memory=3)
var Candle[] candlesadd871                  = array.new<Candle>(0)
var BOSdata bosdataadd871                   = BOSdata.new()
htfadd871.settings                 := SettingsHTFadd871
htfadd871.candles                  := candlesadd871
htfadd871.bosdata                  := bosdataadd871
var CandleSet htfadd872                     = CandleSet.new()
var CandleSettings SettingsHTFadd872        = CandleSettings.new(htf='872',htfint=872,max_memory=3)
var Candle[] candlesadd872                  = array.new<Candle>(0)
var BOSdata bosdataadd872                   = BOSdata.new()
htfadd872.settings                 := SettingsHTFadd872
htfadd872.candles                  := candlesadd872
htfadd872.bosdata                  := bosdataadd872
var CandleSet htfadd873                     = CandleSet.new()
var CandleSettings SettingsHTFadd873        = CandleSettings.new(htf='873',htfint=873,max_memory=3)
var Candle[] candlesadd873                  = array.new<Candle>(0)
var BOSdata bosdataadd873                   = BOSdata.new()
htfadd873.settings                 := SettingsHTFadd873
htfadd873.candles                  := candlesadd873
htfadd873.bosdata                  := bosdataadd873
var CandleSet htfadd874                     = CandleSet.new()
var CandleSettings SettingsHTFadd874        = CandleSettings.new(htf='874',htfint=874,max_memory=3)
var Candle[] candlesadd874                  = array.new<Candle>(0)
var BOSdata bosdataadd874                   = BOSdata.new()
htfadd874.settings                 := SettingsHTFadd874
htfadd874.candles                  := candlesadd874
htfadd874.bosdata                  := bosdataadd874
var CandleSet htfadd875                     = CandleSet.new()
var CandleSettings SettingsHTFadd875        = CandleSettings.new(htf='875',htfint=875,max_memory=3)
var Candle[] candlesadd875                  = array.new<Candle>(0)
var BOSdata bosdataadd875                   = BOSdata.new()
htfadd875.settings                 := SettingsHTFadd875
htfadd875.candles                  := candlesadd875
htfadd875.bosdata                  := bosdataadd875
var CandleSet htfadd876                     = CandleSet.new()
var CandleSettings SettingsHTFadd876        = CandleSettings.new(htf='876',htfint=876,max_memory=3)
var Candle[] candlesadd876                  = array.new<Candle>(0)
var BOSdata bosdataadd876                   = BOSdata.new()
htfadd876.settings                 := SettingsHTFadd876
htfadd876.candles                  := candlesadd876
htfadd876.bosdata                  := bosdataadd876
var CandleSet htfadd877                     = CandleSet.new()
var CandleSettings SettingsHTFadd877        = CandleSettings.new(htf='877',htfint=877,max_memory=3)
var Candle[] candlesadd877                  = array.new<Candle>(0)
var BOSdata bosdataadd877                   = BOSdata.new()
htfadd877.settings                 := SettingsHTFadd877
htfadd877.candles                  := candlesadd877
htfadd877.bosdata                  := bosdataadd877
var CandleSet htfadd878                     = CandleSet.new()
var CandleSettings SettingsHTFadd878        = CandleSettings.new(htf='878',htfint=878,max_memory=3)
var Candle[] candlesadd878                  = array.new<Candle>(0)
var BOSdata bosdataadd878                   = BOSdata.new()
htfadd878.settings                 := SettingsHTFadd878
htfadd878.candles                  := candlesadd878
htfadd878.bosdata                  := bosdataadd878
var CandleSet htfadd879                     = CandleSet.new()
var CandleSettings SettingsHTFadd879        = CandleSettings.new(htf='879',htfint=879,max_memory=3)
var Candle[] candlesadd879                  = array.new<Candle>(0)
var BOSdata bosdataadd879                   = BOSdata.new()
htfadd879.settings                 := SettingsHTFadd879
htfadd879.candles                  := candlesadd879
htfadd879.bosdata                  := bosdataadd879
var CandleSet htfadd880                     = CandleSet.new()
var CandleSettings SettingsHTFadd880        = CandleSettings.new(htf='880',htfint=880,max_memory=3)
var Candle[] candlesadd880                  = array.new<Candle>(0)
var BOSdata bosdataadd880                   = BOSdata.new()
htfadd880.settings                 := SettingsHTFadd880
htfadd880.candles                  := candlesadd880
htfadd880.bosdata                  := bosdataadd880
var CandleSet htfadd881                     = CandleSet.new()
var CandleSettings SettingsHTFadd881        = CandleSettings.new(htf='881',htfint=881,max_memory=3)
var Candle[] candlesadd881                  = array.new<Candle>(0)
var BOSdata bosdataadd881                   = BOSdata.new()
htfadd881.settings                 := SettingsHTFadd881
htfadd881.candles                  := candlesadd881
htfadd881.bosdata                  := bosdataadd881
var CandleSet htfadd882                     = CandleSet.new()
var CandleSettings SettingsHTFadd882        = CandleSettings.new(htf='882',htfint=882,max_memory=3)
var Candle[] candlesadd882                  = array.new<Candle>(0)
var BOSdata bosdataadd882                   = BOSdata.new()
htfadd882.settings                 := SettingsHTFadd882
htfadd882.candles                  := candlesadd882
htfadd882.bosdata                  := bosdataadd882
var CandleSet htfadd883                     = CandleSet.new()
var CandleSettings SettingsHTFadd883        = CandleSettings.new(htf='883',htfint=883,max_memory=3)
var Candle[] candlesadd883                  = array.new<Candle>(0)
var BOSdata bosdataadd883                   = BOSdata.new()
htfadd883.settings                 := SettingsHTFadd883
htfadd883.candles                  := candlesadd883
htfadd883.bosdata                  := bosdataadd883
var CandleSet htfadd884                     = CandleSet.new()
var CandleSettings SettingsHTFadd884        = CandleSettings.new(htf='884',htfint=884,max_memory=3)
var Candle[] candlesadd884                  = array.new<Candle>(0)
var BOSdata bosdataadd884                   = BOSdata.new()
htfadd884.settings                 := SettingsHTFadd884
htfadd884.candles                  := candlesadd884
htfadd884.bosdata                  := bosdataadd884
var CandleSet htfadd885                     = CandleSet.new()
var CandleSettings SettingsHTFadd885        = CandleSettings.new(htf='885',htfint=885,max_memory=3)
var Candle[] candlesadd885                  = array.new<Candle>(0)
var BOSdata bosdataadd885                   = BOSdata.new()
htfadd885.settings                 := SettingsHTFadd885
htfadd885.candles                  := candlesadd885
htfadd885.bosdata                  := bosdataadd885
var CandleSet htfadd886                     = CandleSet.new()
var CandleSettings SettingsHTFadd886        = CandleSettings.new(htf='886',htfint=886,max_memory=3)
var Candle[] candlesadd886                  = array.new<Candle>(0)
var BOSdata bosdataadd886                   = BOSdata.new()
htfadd886.settings                 := SettingsHTFadd886
htfadd886.candles                  := candlesadd886
htfadd886.bosdata                  := bosdataadd886
var CandleSet htfadd887                     = CandleSet.new()
var CandleSettings SettingsHTFadd887        = CandleSettings.new(htf='887',htfint=887,max_memory=3)
var Candle[] candlesadd887                  = array.new<Candle>(0)
var BOSdata bosdataadd887                   = BOSdata.new()
htfadd887.settings                 := SettingsHTFadd887
htfadd887.candles                  := candlesadd887
htfadd887.bosdata                  := bosdataadd887
var CandleSet htfadd888                     = CandleSet.new()
var CandleSettings SettingsHTFadd888        = CandleSettings.new(htf='888',htfint=888,max_memory=3)
var Candle[] candlesadd888                  = array.new<Candle>(0)
var BOSdata bosdataadd888                   = BOSdata.new()
htfadd888.settings                 := SettingsHTFadd888
htfadd888.candles                  := candlesadd888
htfadd888.bosdata                  := bosdataadd888
var CandleSet htfadd889                     = CandleSet.new()
var CandleSettings SettingsHTFadd889        = CandleSettings.new(htf='889',htfint=889,max_memory=3)
var Candle[] candlesadd889                  = array.new<Candle>(0)
var BOSdata bosdataadd889                   = BOSdata.new()
htfadd889.settings                 := SettingsHTFadd889
htfadd889.candles                  := candlesadd889
htfadd889.bosdata                  := bosdataadd889
var CandleSet htfadd890                     = CandleSet.new()
var CandleSettings SettingsHTFadd890        = CandleSettings.new(htf='890',htfint=890,max_memory=3)
var Candle[] candlesadd890                  = array.new<Candle>(0)
var BOSdata bosdataadd890                   = BOSdata.new()
htfadd890.settings                 := SettingsHTFadd890
htfadd890.candles                  := candlesadd890
htfadd890.bosdata                  := bosdataadd890
var CandleSet htfadd891                     = CandleSet.new()
var CandleSettings SettingsHTFadd891        = CandleSettings.new(htf='891',htfint=891,max_memory=3)
var Candle[] candlesadd891                  = array.new<Candle>(0)
var BOSdata bosdataadd891                   = BOSdata.new()
htfadd891.settings                 := SettingsHTFadd891
htfadd891.candles                  := candlesadd891
htfadd891.bosdata                  := bosdataadd891
var CandleSet htfadd892                     = CandleSet.new()
var CandleSettings SettingsHTFadd892        = CandleSettings.new(htf='892',htfint=892,max_memory=3)
var Candle[] candlesadd892                  = array.new<Candle>(0)
var BOSdata bosdataadd892                   = BOSdata.new()
htfadd892.settings                 := SettingsHTFadd892
htfadd892.candles                  := candlesadd892
htfadd892.bosdata                  := bosdataadd892
var CandleSet htfadd893                     = CandleSet.new()
var CandleSettings SettingsHTFadd893        = CandleSettings.new(htf='893',htfint=893,max_memory=3)
var Candle[] candlesadd893                  = array.new<Candle>(0)
var BOSdata bosdataadd893                   = BOSdata.new()
htfadd893.settings                 := SettingsHTFadd893
htfadd893.candles                  := candlesadd893
htfadd893.bosdata                  := bosdataadd893
var CandleSet htfadd894                     = CandleSet.new()
var CandleSettings SettingsHTFadd894        = CandleSettings.new(htf='894',htfint=894,max_memory=3)
var Candle[] candlesadd894                  = array.new<Candle>(0)
var BOSdata bosdataadd894                   = BOSdata.new()
htfadd894.settings                 := SettingsHTFadd894
htfadd894.candles                  := candlesadd894
htfadd894.bosdata                  := bosdataadd894
var CandleSet htfadd895                     = CandleSet.new()
var CandleSettings SettingsHTFadd895        = CandleSettings.new(htf='895',htfint=895,max_memory=3)
var Candle[] candlesadd895                  = array.new<Candle>(0)
var BOSdata bosdataadd895                   = BOSdata.new()
htfadd895.settings                 := SettingsHTFadd895
htfadd895.candles                  := candlesadd895
htfadd895.bosdata                  := bosdataadd895
var CandleSet htfadd896                     = CandleSet.new()
var CandleSettings SettingsHTFadd896        = CandleSettings.new(htf='896',htfint=896,max_memory=3)
var Candle[] candlesadd896                  = array.new<Candle>(0)
var BOSdata bosdataadd896                   = BOSdata.new()
htfadd896.settings                 := SettingsHTFadd896
htfadd896.candles                  := candlesadd896
htfadd896.bosdata                  := bosdataadd896
var CandleSet htfadd897                     = CandleSet.new()
var CandleSettings SettingsHTFadd897        = CandleSettings.new(htf='897',htfint=897,max_memory=3)
var Candle[] candlesadd897                  = array.new<Candle>(0)
var BOSdata bosdataadd897                   = BOSdata.new()
htfadd897.settings                 := SettingsHTFadd897
htfadd897.candles                  := candlesadd897
htfadd897.bosdata                  := bosdataadd897
var CandleSet htfadd898                     = CandleSet.new()
var CandleSettings SettingsHTFadd898        = CandleSettings.new(htf='898',htfint=898,max_memory=3)
var Candle[] candlesadd898                  = array.new<Candle>(0)
var BOSdata bosdataadd898                   = BOSdata.new()
htfadd898.settings                 := SettingsHTFadd898
htfadd898.candles                  := candlesadd898
htfadd898.bosdata                  := bosdataadd898
var CandleSet htfadd899                     = CandleSet.new()
var CandleSettings SettingsHTFadd899        = CandleSettings.new(htf='899',htfint=899,max_memory=3)
var Candle[] candlesadd899                  = array.new<Candle>(0)
var BOSdata bosdataadd899                   = BOSdata.new()
htfadd899.settings                 := SettingsHTFadd899
htfadd899.candles                  := candlesadd899
htfadd899.bosdata                  := bosdataadd899
var CandleSet htfadd900                     = CandleSet.new()
var CandleSettings SettingsHTFadd900        = CandleSettings.new(htf='900',htfint=900,max_memory=3)
var Candle[] candlesadd900                  = array.new<Candle>(0)
var BOSdata bosdataadd900                   = BOSdata.new()
htfadd900.settings                 := SettingsHTFadd900
htfadd900.candles                  := candlesadd900
htfadd900.bosdata                  := bosdataadd900

htfadd810.Monitor().BOSJudge()
htfadd811.Monitor().BOSJudge()
htfadd812.Monitor().BOSJudge()
htfadd813.Monitor().BOSJudge()
htfadd814.Monitor().BOSJudge()
htfadd815.Monitor().BOSJudge()
htfadd816.Monitor().BOSJudge()
htfadd817.Monitor().BOSJudge()
htfadd818.Monitor().BOSJudge()
htfadd819.Monitor().BOSJudge()
htfadd820.Monitor().BOSJudge()
htfadd821.Monitor().BOSJudge()
htfadd822.Monitor().BOSJudge()
htfadd823.Monitor().BOSJudge()
htfadd824.Monitor().BOSJudge()
htfadd825.Monitor().BOSJudge()
htfadd826.Monitor().BOSJudge()
htfadd827.Monitor().BOSJudge()
htfadd828.Monitor().BOSJudge()
htfadd829.Monitor().BOSJudge()
htfadd830.Monitor().BOSJudge()
htfadd831.Monitor().BOSJudge()
htfadd832.Monitor().BOSJudge()
htfadd833.Monitor().BOSJudge()
htfadd834.Monitor().BOSJudge()
htfadd835.Monitor().BOSJudge()
htfadd836.Monitor().BOSJudge()
htfadd837.Monitor().BOSJudge()
htfadd838.Monitor().BOSJudge()
htfadd839.Monitor().BOSJudge()
htfadd840.Monitor().BOSJudge()
htfadd841.Monitor().BOSJudge()
htfadd842.Monitor().BOSJudge()
htfadd843.Monitor().BOSJudge()
htfadd844.Monitor().BOSJudge()
htfadd845.Monitor().BOSJudge()
htfadd846.Monitor().BOSJudge()
htfadd847.Monitor().BOSJudge()
htfadd848.Monitor().BOSJudge()
htfadd849.Monitor().BOSJudge()
htfadd850.Monitor().BOSJudge()
htfadd851.Monitor().BOSJudge()
htfadd852.Monitor().BOSJudge()
htfadd853.Monitor().BOSJudge()
htfadd854.Monitor().BOSJudge()
htfadd855.Monitor().BOSJudge()
htfadd856.Monitor().BOSJudge()
htfadd857.Monitor().BOSJudge()
htfadd858.Monitor().BOSJudge()
htfadd859.Monitor().BOSJudge()
htfadd860.Monitor().BOSJudge()
htfadd861.Monitor().BOSJudge()
htfadd862.Monitor().BOSJudge()
htfadd863.Monitor().BOSJudge()
htfadd864.Monitor().BOSJudge()
htfadd865.Monitor().BOSJudge()
htfadd866.Monitor().BOSJudge()
htfadd867.Monitor().BOSJudge()
htfadd868.Monitor().BOSJudge()
htfadd869.Monitor().BOSJudge()
htfadd870.Monitor().BOSJudge()
htfadd871.Monitor().BOSJudge()
htfadd872.Monitor().BOSJudge()
htfadd873.Monitor().BOSJudge()
htfadd874.Monitor().BOSJudge()
htfadd875.Monitor().BOSJudge()
htfadd876.Monitor().BOSJudge()
htfadd877.Monitor().BOSJudge()
htfadd878.Monitor().BOSJudge()
htfadd879.Monitor().BOSJudge()
htfadd880.Monitor().BOSJudge()
htfadd881.Monitor().BOSJudge()
htfadd882.Monitor().BOSJudge()
htfadd883.Monitor().BOSJudge()
htfadd884.Monitor().BOSJudge()
htfadd885.Monitor().BOSJudge()
htfadd886.Monitor().BOSJudge()
htfadd887.Monitor().BOSJudge()
htfadd888.Monitor().BOSJudge()
htfadd889.Monitor().BOSJudge()
htfadd890.Monitor().BOSJudge()
htfadd891.Monitor().BOSJudge()
htfadd892.Monitor().BOSJudge()
htfadd893.Monitor().BOSJudge()
htfadd894.Monitor().BOSJudge()
htfadd895.Monitor().BOSJudge()
htfadd896.Monitor().BOSJudge()
htfadd897.Monitor().BOSJudge()
htfadd898.Monitor().BOSJudge()
htfadd899.Monitor().BOSJudge()
htfadd900.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd810)
    LowestsbuSet(lowestsbu, htfadd810)
    HighestsbdSet(highestsbd, htfadd811)
    LowestsbuSet(lowestsbu, htfadd811)
    HighestsbdSet(highestsbd, htfadd812)
    LowestsbuSet(lowestsbu, htfadd812)
    HighestsbdSet(highestsbd, htfadd813)
    LowestsbuSet(lowestsbu, htfadd813)
    HighestsbdSet(highestsbd, htfadd814)
    LowestsbuSet(lowestsbu, htfadd814)
    HighestsbdSet(highestsbd, htfadd815)
    LowestsbuSet(lowestsbu, htfadd815)
    HighestsbdSet(highestsbd, htfadd816)
    LowestsbuSet(lowestsbu, htfadd816)
    HighestsbdSet(highestsbd, htfadd817)
    LowestsbuSet(lowestsbu, htfadd817)
    HighestsbdSet(highestsbd, htfadd818)
    LowestsbuSet(lowestsbu, htfadd818)
    HighestsbdSet(highestsbd, htfadd819)
    LowestsbuSet(lowestsbu, htfadd819)
    HighestsbdSet(highestsbd, htfadd820)
    LowestsbuSet(lowestsbu, htfadd820)
    HighestsbdSet(highestsbd, htfadd821)
    LowestsbuSet(lowestsbu, htfadd821)
    HighestsbdSet(highestsbd, htfadd822)
    LowestsbuSet(lowestsbu, htfadd822)
    HighestsbdSet(highestsbd, htfadd823)
    LowestsbuSet(lowestsbu, htfadd823)
    HighestsbdSet(highestsbd, htfadd824)
    LowestsbuSet(lowestsbu, htfadd824)
    HighestsbdSet(highestsbd, htfadd825)
    LowestsbuSet(lowestsbu, htfadd825)
    HighestsbdSet(highestsbd, htfadd826)
    LowestsbuSet(lowestsbu, htfadd826)
    HighestsbdSet(highestsbd, htfadd827)
    LowestsbuSet(lowestsbu, htfadd827)
    HighestsbdSet(highestsbd, htfadd828)
    LowestsbuSet(lowestsbu, htfadd828)
    HighestsbdSet(highestsbd, htfadd829)
    LowestsbuSet(lowestsbu, htfadd829)
    HighestsbdSet(highestsbd, htfadd830)
    LowestsbuSet(lowestsbu, htfadd830)
    HighestsbdSet(highestsbd, htfadd831)
    LowestsbuSet(lowestsbu, htfadd831)
    HighestsbdSet(highestsbd, htfadd832)
    LowestsbuSet(lowestsbu, htfadd832)
    HighestsbdSet(highestsbd, htfadd833)
    LowestsbuSet(lowestsbu, htfadd833)
    HighestsbdSet(highestsbd, htfadd834)
    LowestsbuSet(lowestsbu, htfadd834)
    HighestsbdSet(highestsbd, htfadd835)
    LowestsbuSet(lowestsbu, htfadd835)
    HighestsbdSet(highestsbd, htfadd836)
    LowestsbuSet(lowestsbu, htfadd836)
    HighestsbdSet(highestsbd, htfadd837)
    LowestsbuSet(lowestsbu, htfadd837)
    HighestsbdSet(highestsbd, htfadd838)
    LowestsbuSet(lowestsbu, htfadd838)
    HighestsbdSet(highestsbd, htfadd839)
    LowestsbuSet(lowestsbu, htfadd839)
    HighestsbdSet(highestsbd, htfadd840)
    LowestsbuSet(lowestsbu, htfadd840)
    HighestsbdSet(highestsbd, htfadd841)
    LowestsbuSet(lowestsbu, htfadd841)
    HighestsbdSet(highestsbd, htfadd842)
    LowestsbuSet(lowestsbu, htfadd842)
    HighestsbdSet(highestsbd, htfadd843)
    LowestsbuSet(lowestsbu, htfadd843)
    HighestsbdSet(highestsbd, htfadd844)
    LowestsbuSet(lowestsbu, htfadd844)
    HighestsbdSet(highestsbd, htfadd845)
    LowestsbuSet(lowestsbu, htfadd845)
    HighestsbdSet(highestsbd, htfadd846)
    LowestsbuSet(lowestsbu, htfadd846)
    HighestsbdSet(highestsbd, htfadd847)
    LowestsbuSet(lowestsbu, htfadd847)
    HighestsbdSet(highestsbd, htfadd848)
    LowestsbuSet(lowestsbu, htfadd848)
    HighestsbdSet(highestsbd, htfadd849)
    LowestsbuSet(lowestsbu, htfadd849)
    HighestsbdSet(highestsbd, htfadd850)
    LowestsbuSet(lowestsbu, htfadd850)
    HighestsbdSet(highestsbd, htfadd851)
    LowestsbuSet(lowestsbu, htfadd851)
    HighestsbdSet(highestsbd, htfadd852)
    LowestsbuSet(lowestsbu, htfadd852)
    HighestsbdSet(highestsbd, htfadd853)
    LowestsbuSet(lowestsbu, htfadd853)
    HighestsbdSet(highestsbd, htfadd854)
    LowestsbuSet(lowestsbu, htfadd854)
    HighestsbdSet(highestsbd, htfadd855)
    LowestsbuSet(lowestsbu, htfadd855)
    HighestsbdSet(highestsbd, htfadd856)
    LowestsbuSet(lowestsbu, htfadd856)
    HighestsbdSet(highestsbd, htfadd857)
    LowestsbuSet(lowestsbu, htfadd857)
    HighestsbdSet(highestsbd, htfadd858)
    LowestsbuSet(lowestsbu, htfadd858)
    HighestsbdSet(highestsbd, htfadd859)
    LowestsbuSet(lowestsbu, htfadd859)
    HighestsbdSet(highestsbd, htfadd860)
    LowestsbuSet(lowestsbu, htfadd860)
    HighestsbdSet(highestsbd, htfadd861)
    LowestsbuSet(lowestsbu, htfadd861)
    HighestsbdSet(highestsbd, htfadd862)
    LowestsbuSet(lowestsbu, htfadd862)
    HighestsbdSet(highestsbd, htfadd863)
    LowestsbuSet(lowestsbu, htfadd863)
    HighestsbdSet(highestsbd, htfadd864)
    LowestsbuSet(lowestsbu, htfadd864)
    HighestsbdSet(highestsbd, htfadd865)
    LowestsbuSet(lowestsbu, htfadd865)
    HighestsbdSet(highestsbd, htfadd866)
    LowestsbuSet(lowestsbu, htfadd866)
    HighestsbdSet(highestsbd, htfadd867)
    LowestsbuSet(lowestsbu, htfadd867)
    HighestsbdSet(highestsbd, htfadd868)
    LowestsbuSet(lowestsbu, htfadd868)
    HighestsbdSet(highestsbd, htfadd869)
    LowestsbuSet(lowestsbu, htfadd869)
    HighestsbdSet(highestsbd, htfadd870)
    LowestsbuSet(lowestsbu, htfadd870)
    HighestsbdSet(highestsbd, htfadd871)
    LowestsbuSet(lowestsbu, htfadd871)
    HighestsbdSet(highestsbd, htfadd872)
    LowestsbuSet(lowestsbu, htfadd872)
    HighestsbdSet(highestsbd, htfadd873)
    LowestsbuSet(lowestsbu, htfadd873)
    HighestsbdSet(highestsbd, htfadd874)
    LowestsbuSet(lowestsbu, htfadd874)
    HighestsbdSet(highestsbd, htfadd875)
    LowestsbuSet(lowestsbu, htfadd875)
    HighestsbdSet(highestsbd, htfadd876)
    LowestsbuSet(lowestsbu, htfadd876)
    HighestsbdSet(highestsbd, htfadd877)
    LowestsbuSet(lowestsbu, htfadd877)
    HighestsbdSet(highestsbd, htfadd878)
    LowestsbuSet(lowestsbu, htfadd878)
    HighestsbdSet(highestsbd, htfadd879)
    LowestsbuSet(lowestsbu, htfadd879)
    HighestsbdSet(highestsbd, htfadd880)
    LowestsbuSet(lowestsbu, htfadd880)
    HighestsbdSet(highestsbd, htfadd881)
    LowestsbuSet(lowestsbu, htfadd881)
    HighestsbdSet(highestsbd, htfadd882)
    LowestsbuSet(lowestsbu, htfadd882)
    HighestsbdSet(highestsbd, htfadd883)
    LowestsbuSet(lowestsbu, htfadd883)
    HighestsbdSet(highestsbd, htfadd884)
    LowestsbuSet(lowestsbu, htfadd884)
    HighestsbdSet(highestsbd, htfadd885)
    LowestsbuSet(lowestsbu, htfadd885)
    HighestsbdSet(highestsbd, htfadd886)
    LowestsbuSet(lowestsbu, htfadd886)
    HighestsbdSet(highestsbd, htfadd887)
    LowestsbuSet(lowestsbu, htfadd887)
    HighestsbdSet(highestsbd, htfadd888)
    LowestsbuSet(lowestsbu, htfadd888)
    HighestsbdSet(highestsbd, htfadd889)
    LowestsbuSet(lowestsbu, htfadd889)
    HighestsbdSet(highestsbd, htfadd890)
    LowestsbuSet(lowestsbu, htfadd890)
    HighestsbdSet(highestsbd, htfadd891)
    LowestsbuSet(lowestsbu, htfadd891)
    HighestsbdSet(highestsbd, htfadd892)
    LowestsbuSet(lowestsbu, htfadd892)
    HighestsbdSet(highestsbd, htfadd893)
    LowestsbuSet(lowestsbu, htfadd893)
    HighestsbdSet(highestsbd, htfadd894)
    LowestsbuSet(lowestsbu, htfadd894)
    HighestsbdSet(highestsbd, htfadd895)
    LowestsbuSet(lowestsbu, htfadd895)
    HighestsbdSet(highestsbd, htfadd896)
    LowestsbuSet(lowestsbu, htfadd896)
    HighestsbdSet(highestsbd, htfadd897)
    LowestsbuSet(lowestsbu, htfadd897)
    HighestsbdSet(highestsbd, htfadd898)
    LowestsbuSet(lowestsbu, htfadd898)
    HighestsbdSet(highestsbd, htfadd899)
    LowestsbuSet(lowestsbu, htfadd899)
    HighestsbdSet(highestsbd, htfadd900)
    LowestsbuSet(lowestsbu, htfadd900)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd810).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd811).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd812).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd813).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd814).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd815).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd816).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd817).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd818).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd819).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd820).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd821).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd822).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd823).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd824).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd825).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd826).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd827).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd828).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd829).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd830).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd831).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd832).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd833).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd834).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd835).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd836).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd837).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd838).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd839).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd840).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd841).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd842).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd843).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd844).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd845).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd846).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd847).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd848).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd849).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd850).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd851).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd852).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd853).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd854).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd855).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd856).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd857).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd858).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd859).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd860).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd861).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd862).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd863).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd864).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd865).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd866).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd867).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd868).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd869).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd870).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd871).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd872).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd873).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd874).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd875).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd876).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd877).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd878).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd879).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd880).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd881).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd882).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd883).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd884).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd885).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd886).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd887).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd888).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd889).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd890).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd891).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd892).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd893).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd894).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd895).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd896).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd897).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd898).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd899).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd900).Monitor_Est().BOSJudge()
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


