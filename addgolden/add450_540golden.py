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
var CandleSet htfadd450                     = CandleSet.new()
var CandleSettings SettingsHTFadd450        = CandleSettings.new(htf='450',htfint=450,max_memory=3)
var Candle[] candlesadd450                  = array.new<Candle>(0)
var BOSdata bosdataadd450                   = BOSdata.new()
htfadd450.settings                 := SettingsHTFadd450
htfadd450.candles                  := candlesadd450
htfadd450.bosdata                  := bosdataadd450
var CandleSet htfadd451                     = CandleSet.new()
var CandleSettings SettingsHTFadd451        = CandleSettings.new(htf='451',htfint=451,max_memory=3)
var Candle[] candlesadd451                  = array.new<Candle>(0)
var BOSdata bosdataadd451                   = BOSdata.new()
htfadd451.settings                 := SettingsHTFadd451
htfadd451.candles                  := candlesadd451
htfadd451.bosdata                  := bosdataadd451
var CandleSet htfadd452                     = CandleSet.new()
var CandleSettings SettingsHTFadd452        = CandleSettings.new(htf='452',htfint=452,max_memory=3)
var Candle[] candlesadd452                  = array.new<Candle>(0)
var BOSdata bosdataadd452                   = BOSdata.new()
htfadd452.settings                 := SettingsHTFadd452
htfadd452.candles                  := candlesadd452
htfadd452.bosdata                  := bosdataadd452
var CandleSet htfadd453                     = CandleSet.new()
var CandleSettings SettingsHTFadd453        = CandleSettings.new(htf='453',htfint=453,max_memory=3)
var Candle[] candlesadd453                  = array.new<Candle>(0)
var BOSdata bosdataadd453                   = BOSdata.new()
htfadd453.settings                 := SettingsHTFadd453
htfadd453.candles                  := candlesadd453
htfadd453.bosdata                  := bosdataadd453
var CandleSet htfadd454                     = CandleSet.new()
var CandleSettings SettingsHTFadd454        = CandleSettings.new(htf='454',htfint=454,max_memory=3)
var Candle[] candlesadd454                  = array.new<Candle>(0)
var BOSdata bosdataadd454                   = BOSdata.new()
htfadd454.settings                 := SettingsHTFadd454
htfadd454.candles                  := candlesadd454
htfadd454.bosdata                  := bosdataadd454
var CandleSet htfadd455                     = CandleSet.new()
var CandleSettings SettingsHTFadd455        = CandleSettings.new(htf='455',htfint=455,max_memory=3)
var Candle[] candlesadd455                  = array.new<Candle>(0)
var BOSdata bosdataadd455                   = BOSdata.new()
htfadd455.settings                 := SettingsHTFadd455
htfadd455.candles                  := candlesadd455
htfadd455.bosdata                  := bosdataadd455
var CandleSet htfadd456                     = CandleSet.new()
var CandleSettings SettingsHTFadd456        = CandleSettings.new(htf='456',htfint=456,max_memory=3)
var Candle[] candlesadd456                  = array.new<Candle>(0)
var BOSdata bosdataadd456                   = BOSdata.new()
htfadd456.settings                 := SettingsHTFadd456
htfadd456.candles                  := candlesadd456
htfadd456.bosdata                  := bosdataadd456
var CandleSet htfadd457                     = CandleSet.new()
var CandleSettings SettingsHTFadd457        = CandleSettings.new(htf='457',htfint=457,max_memory=3)
var Candle[] candlesadd457                  = array.new<Candle>(0)
var BOSdata bosdataadd457                   = BOSdata.new()
htfadd457.settings                 := SettingsHTFadd457
htfadd457.candles                  := candlesadd457
htfadd457.bosdata                  := bosdataadd457
var CandleSet htfadd458                     = CandleSet.new()
var CandleSettings SettingsHTFadd458        = CandleSettings.new(htf='458',htfint=458,max_memory=3)
var Candle[] candlesadd458                  = array.new<Candle>(0)
var BOSdata bosdataadd458                   = BOSdata.new()
htfadd458.settings                 := SettingsHTFadd458
htfadd458.candles                  := candlesadd458
htfadd458.bosdata                  := bosdataadd458
var CandleSet htfadd459                     = CandleSet.new()
var CandleSettings SettingsHTFadd459        = CandleSettings.new(htf='459',htfint=459,max_memory=3)
var Candle[] candlesadd459                  = array.new<Candle>(0)
var BOSdata bosdataadd459                   = BOSdata.new()
htfadd459.settings                 := SettingsHTFadd459
htfadd459.candles                  := candlesadd459
htfadd459.bosdata                  := bosdataadd459
var CandleSet htfadd460                     = CandleSet.new()
var CandleSettings SettingsHTFadd460        = CandleSettings.new(htf='460',htfint=460,max_memory=3)
var Candle[] candlesadd460                  = array.new<Candle>(0)
var BOSdata bosdataadd460                   = BOSdata.new()
htfadd460.settings                 := SettingsHTFadd460
htfadd460.candles                  := candlesadd460
htfadd460.bosdata                  := bosdataadd460
var CandleSet htfadd461                     = CandleSet.new()
var CandleSettings SettingsHTFadd461        = CandleSettings.new(htf='461',htfint=461,max_memory=3)
var Candle[] candlesadd461                  = array.new<Candle>(0)
var BOSdata bosdataadd461                   = BOSdata.new()
htfadd461.settings                 := SettingsHTFadd461
htfadd461.candles                  := candlesadd461
htfadd461.bosdata                  := bosdataadd461
var CandleSet htfadd462                     = CandleSet.new()
var CandleSettings SettingsHTFadd462        = CandleSettings.new(htf='462',htfint=462,max_memory=3)
var Candle[] candlesadd462                  = array.new<Candle>(0)
var BOSdata bosdataadd462                   = BOSdata.new()
htfadd462.settings                 := SettingsHTFadd462
htfadd462.candles                  := candlesadd462
htfadd462.bosdata                  := bosdataadd462
var CandleSet htfadd463                     = CandleSet.new()
var CandleSettings SettingsHTFadd463        = CandleSettings.new(htf='463',htfint=463,max_memory=3)
var Candle[] candlesadd463                  = array.new<Candle>(0)
var BOSdata bosdataadd463                   = BOSdata.new()
htfadd463.settings                 := SettingsHTFadd463
htfadd463.candles                  := candlesadd463
htfadd463.bosdata                  := bosdataadd463
var CandleSet htfadd464                     = CandleSet.new()
var CandleSettings SettingsHTFadd464        = CandleSettings.new(htf='464',htfint=464,max_memory=3)
var Candle[] candlesadd464                  = array.new<Candle>(0)
var BOSdata bosdataadd464                   = BOSdata.new()
htfadd464.settings                 := SettingsHTFadd464
htfadd464.candles                  := candlesadd464
htfadd464.bosdata                  := bosdataadd464
var CandleSet htfadd465                     = CandleSet.new()
var CandleSettings SettingsHTFadd465        = CandleSettings.new(htf='465',htfint=465,max_memory=3)
var Candle[] candlesadd465                  = array.new<Candle>(0)
var BOSdata bosdataadd465                   = BOSdata.new()
htfadd465.settings                 := SettingsHTFadd465
htfadd465.candles                  := candlesadd465
htfadd465.bosdata                  := bosdataadd465
var CandleSet htfadd466                     = CandleSet.new()
var CandleSettings SettingsHTFadd466        = CandleSettings.new(htf='466',htfint=466,max_memory=3)
var Candle[] candlesadd466                  = array.new<Candle>(0)
var BOSdata bosdataadd466                   = BOSdata.new()
htfadd466.settings                 := SettingsHTFadd466
htfadd466.candles                  := candlesadd466
htfadd466.bosdata                  := bosdataadd466
var CandleSet htfadd467                     = CandleSet.new()
var CandleSettings SettingsHTFadd467        = CandleSettings.new(htf='467',htfint=467,max_memory=3)
var Candle[] candlesadd467                  = array.new<Candle>(0)
var BOSdata bosdataadd467                   = BOSdata.new()
htfadd467.settings                 := SettingsHTFadd467
htfadd467.candles                  := candlesadd467
htfadd467.bosdata                  := bosdataadd467
var CandleSet htfadd468                     = CandleSet.new()
var CandleSettings SettingsHTFadd468        = CandleSettings.new(htf='468',htfint=468,max_memory=3)
var Candle[] candlesadd468                  = array.new<Candle>(0)
var BOSdata bosdataadd468                   = BOSdata.new()
htfadd468.settings                 := SettingsHTFadd468
htfadd468.candles                  := candlesadd468
htfadd468.bosdata                  := bosdataadd468
var CandleSet htfadd469                     = CandleSet.new()
var CandleSettings SettingsHTFadd469        = CandleSettings.new(htf='469',htfint=469,max_memory=3)
var Candle[] candlesadd469                  = array.new<Candle>(0)
var BOSdata bosdataadd469                   = BOSdata.new()
htfadd469.settings                 := SettingsHTFadd469
htfadd469.candles                  := candlesadd469
htfadd469.bosdata                  := bosdataadd469
var CandleSet htfadd470                     = CandleSet.new()
var CandleSettings SettingsHTFadd470        = CandleSettings.new(htf='470',htfint=470,max_memory=3)
var Candle[] candlesadd470                  = array.new<Candle>(0)
var BOSdata bosdataadd470                   = BOSdata.new()
htfadd470.settings                 := SettingsHTFadd470
htfadd470.candles                  := candlesadd470
htfadd470.bosdata                  := bosdataadd470
var CandleSet htfadd471                     = CandleSet.new()
var CandleSettings SettingsHTFadd471        = CandleSettings.new(htf='471',htfint=471,max_memory=3)
var Candle[] candlesadd471                  = array.new<Candle>(0)
var BOSdata bosdataadd471                   = BOSdata.new()
htfadd471.settings                 := SettingsHTFadd471
htfadd471.candles                  := candlesadd471
htfadd471.bosdata                  := bosdataadd471
var CandleSet htfadd472                     = CandleSet.new()
var CandleSettings SettingsHTFadd472        = CandleSettings.new(htf='472',htfint=472,max_memory=3)
var Candle[] candlesadd472                  = array.new<Candle>(0)
var BOSdata bosdataadd472                   = BOSdata.new()
htfadd472.settings                 := SettingsHTFadd472
htfadd472.candles                  := candlesadd472
htfadd472.bosdata                  := bosdataadd472
var CandleSet htfadd473                     = CandleSet.new()
var CandleSettings SettingsHTFadd473        = CandleSettings.new(htf='473',htfint=473,max_memory=3)
var Candle[] candlesadd473                  = array.new<Candle>(0)
var BOSdata bosdataadd473                   = BOSdata.new()
htfadd473.settings                 := SettingsHTFadd473
htfadd473.candles                  := candlesadd473
htfadd473.bosdata                  := bosdataadd473
var CandleSet htfadd474                     = CandleSet.new()
var CandleSettings SettingsHTFadd474        = CandleSettings.new(htf='474',htfint=474,max_memory=3)
var Candle[] candlesadd474                  = array.new<Candle>(0)
var BOSdata bosdataadd474                   = BOSdata.new()
htfadd474.settings                 := SettingsHTFadd474
htfadd474.candles                  := candlesadd474
htfadd474.bosdata                  := bosdataadd474
var CandleSet htfadd475                     = CandleSet.new()
var CandleSettings SettingsHTFadd475        = CandleSettings.new(htf='475',htfint=475,max_memory=3)
var Candle[] candlesadd475                  = array.new<Candle>(0)
var BOSdata bosdataadd475                   = BOSdata.new()
htfadd475.settings                 := SettingsHTFadd475
htfadd475.candles                  := candlesadd475
htfadd475.bosdata                  := bosdataadd475
var CandleSet htfadd476                     = CandleSet.new()
var CandleSettings SettingsHTFadd476        = CandleSettings.new(htf='476',htfint=476,max_memory=3)
var Candle[] candlesadd476                  = array.new<Candle>(0)
var BOSdata bosdataadd476                   = BOSdata.new()
htfadd476.settings                 := SettingsHTFadd476
htfadd476.candles                  := candlesadd476
htfadd476.bosdata                  := bosdataadd476
var CandleSet htfadd477                     = CandleSet.new()
var CandleSettings SettingsHTFadd477        = CandleSettings.new(htf='477',htfint=477,max_memory=3)
var Candle[] candlesadd477                  = array.new<Candle>(0)
var BOSdata bosdataadd477                   = BOSdata.new()
htfadd477.settings                 := SettingsHTFadd477
htfadd477.candles                  := candlesadd477
htfadd477.bosdata                  := bosdataadd477
var CandleSet htfadd478                     = CandleSet.new()
var CandleSettings SettingsHTFadd478        = CandleSettings.new(htf='478',htfint=478,max_memory=3)
var Candle[] candlesadd478                  = array.new<Candle>(0)
var BOSdata bosdataadd478                   = BOSdata.new()
htfadd478.settings                 := SettingsHTFadd478
htfadd478.candles                  := candlesadd478
htfadd478.bosdata                  := bosdataadd478
var CandleSet htfadd479                     = CandleSet.new()
var CandleSettings SettingsHTFadd479        = CandleSettings.new(htf='479',htfint=479,max_memory=3)
var Candle[] candlesadd479                  = array.new<Candle>(0)
var BOSdata bosdataadd479                   = BOSdata.new()
htfadd479.settings                 := SettingsHTFadd479
htfadd479.candles                  := candlesadd479
htfadd479.bosdata                  := bosdataadd479
var CandleSet htfadd480                     = CandleSet.new()
var CandleSettings SettingsHTFadd480        = CandleSettings.new(htf='480',htfint=480,max_memory=3)
var Candle[] candlesadd480                  = array.new<Candle>(0)
var BOSdata bosdataadd480                   = BOSdata.new()
htfadd480.settings                 := SettingsHTFadd480
htfadd480.candles                  := candlesadd480
htfadd480.bosdata                  := bosdataadd480
var CandleSet htfadd481                     = CandleSet.new()
var CandleSettings SettingsHTFadd481        = CandleSettings.new(htf='481',htfint=481,max_memory=3)
var Candle[] candlesadd481                  = array.new<Candle>(0)
var BOSdata bosdataadd481                   = BOSdata.new()
htfadd481.settings                 := SettingsHTFadd481
htfadd481.candles                  := candlesadd481
htfadd481.bosdata                  := bosdataadd481
var CandleSet htfadd482                     = CandleSet.new()
var CandleSettings SettingsHTFadd482        = CandleSettings.new(htf='482',htfint=482,max_memory=3)
var Candle[] candlesadd482                  = array.new<Candle>(0)
var BOSdata bosdataadd482                   = BOSdata.new()
htfadd482.settings                 := SettingsHTFadd482
htfadd482.candles                  := candlesadd482
htfadd482.bosdata                  := bosdataadd482
var CandleSet htfadd483                     = CandleSet.new()
var CandleSettings SettingsHTFadd483        = CandleSettings.new(htf='483',htfint=483,max_memory=3)
var Candle[] candlesadd483                  = array.new<Candle>(0)
var BOSdata bosdataadd483                   = BOSdata.new()
htfadd483.settings                 := SettingsHTFadd483
htfadd483.candles                  := candlesadd483
htfadd483.bosdata                  := bosdataadd483
var CandleSet htfadd484                     = CandleSet.new()
var CandleSettings SettingsHTFadd484        = CandleSettings.new(htf='484',htfint=484,max_memory=3)
var Candle[] candlesadd484                  = array.new<Candle>(0)
var BOSdata bosdataadd484                   = BOSdata.new()
htfadd484.settings                 := SettingsHTFadd484
htfadd484.candles                  := candlesadd484
htfadd484.bosdata                  := bosdataadd484
var CandleSet htfadd485                     = CandleSet.new()
var CandleSettings SettingsHTFadd485        = CandleSettings.new(htf='485',htfint=485,max_memory=3)
var Candle[] candlesadd485                  = array.new<Candle>(0)
var BOSdata bosdataadd485                   = BOSdata.new()
htfadd485.settings                 := SettingsHTFadd485
htfadd485.candles                  := candlesadd485
htfadd485.bosdata                  := bosdataadd485
var CandleSet htfadd486                     = CandleSet.new()
var CandleSettings SettingsHTFadd486        = CandleSettings.new(htf='486',htfint=486,max_memory=3)
var Candle[] candlesadd486                  = array.new<Candle>(0)
var BOSdata bosdataadd486                   = BOSdata.new()
htfadd486.settings                 := SettingsHTFadd486
htfadd486.candles                  := candlesadd486
htfadd486.bosdata                  := bosdataadd486
var CandleSet htfadd487                     = CandleSet.new()
var CandleSettings SettingsHTFadd487        = CandleSettings.new(htf='487',htfint=487,max_memory=3)
var Candle[] candlesadd487                  = array.new<Candle>(0)
var BOSdata bosdataadd487                   = BOSdata.new()
htfadd487.settings                 := SettingsHTFadd487
htfadd487.candles                  := candlesadd487
htfadd487.bosdata                  := bosdataadd487
var CandleSet htfadd488                     = CandleSet.new()
var CandleSettings SettingsHTFadd488        = CandleSettings.new(htf='488',htfint=488,max_memory=3)
var Candle[] candlesadd488                  = array.new<Candle>(0)
var BOSdata bosdataadd488                   = BOSdata.new()
htfadd488.settings                 := SettingsHTFadd488
htfadd488.candles                  := candlesadd488
htfadd488.bosdata                  := bosdataadd488
var CandleSet htfadd489                     = CandleSet.new()
var CandleSettings SettingsHTFadd489        = CandleSettings.new(htf='489',htfint=489,max_memory=3)
var Candle[] candlesadd489                  = array.new<Candle>(0)
var BOSdata bosdataadd489                   = BOSdata.new()
htfadd489.settings                 := SettingsHTFadd489
htfadd489.candles                  := candlesadd489
htfadd489.bosdata                  := bosdataadd489
var CandleSet htfadd490                     = CandleSet.new()
var CandleSettings SettingsHTFadd490        = CandleSettings.new(htf='490',htfint=490,max_memory=3)
var Candle[] candlesadd490                  = array.new<Candle>(0)
var BOSdata bosdataadd490                   = BOSdata.new()
htfadd490.settings                 := SettingsHTFadd490
htfadd490.candles                  := candlesadd490
htfadd490.bosdata                  := bosdataadd490
var CandleSet htfadd491                     = CandleSet.new()
var CandleSettings SettingsHTFadd491        = CandleSettings.new(htf='491',htfint=491,max_memory=3)
var Candle[] candlesadd491                  = array.new<Candle>(0)
var BOSdata bosdataadd491                   = BOSdata.new()
htfadd491.settings                 := SettingsHTFadd491
htfadd491.candles                  := candlesadd491
htfadd491.bosdata                  := bosdataadd491
var CandleSet htfadd492                     = CandleSet.new()
var CandleSettings SettingsHTFadd492        = CandleSettings.new(htf='492',htfint=492,max_memory=3)
var Candle[] candlesadd492                  = array.new<Candle>(0)
var BOSdata bosdataadd492                   = BOSdata.new()
htfadd492.settings                 := SettingsHTFadd492
htfadd492.candles                  := candlesadd492
htfadd492.bosdata                  := bosdataadd492
var CandleSet htfadd493                     = CandleSet.new()
var CandleSettings SettingsHTFadd493        = CandleSettings.new(htf='493',htfint=493,max_memory=3)
var Candle[] candlesadd493                  = array.new<Candle>(0)
var BOSdata bosdataadd493                   = BOSdata.new()
htfadd493.settings                 := SettingsHTFadd493
htfadd493.candles                  := candlesadd493
htfadd493.bosdata                  := bosdataadd493
var CandleSet htfadd494                     = CandleSet.new()
var CandleSettings SettingsHTFadd494        = CandleSettings.new(htf='494',htfint=494,max_memory=3)
var Candle[] candlesadd494                  = array.new<Candle>(0)
var BOSdata bosdataadd494                   = BOSdata.new()
htfadd494.settings                 := SettingsHTFadd494
htfadd494.candles                  := candlesadd494
htfadd494.bosdata                  := bosdataadd494
var CandleSet htfadd495                     = CandleSet.new()
var CandleSettings SettingsHTFadd495        = CandleSettings.new(htf='495',htfint=495,max_memory=3)
var Candle[] candlesadd495                  = array.new<Candle>(0)
var BOSdata bosdataadd495                   = BOSdata.new()
htfadd495.settings                 := SettingsHTFadd495
htfadd495.candles                  := candlesadd495
htfadd495.bosdata                  := bosdataadd495
var CandleSet htfadd496                     = CandleSet.new()
var CandleSettings SettingsHTFadd496        = CandleSettings.new(htf='496',htfint=496,max_memory=3)
var Candle[] candlesadd496                  = array.new<Candle>(0)
var BOSdata bosdataadd496                   = BOSdata.new()
htfadd496.settings                 := SettingsHTFadd496
htfadd496.candles                  := candlesadd496
htfadd496.bosdata                  := bosdataadd496
var CandleSet htfadd497                     = CandleSet.new()
var CandleSettings SettingsHTFadd497        = CandleSettings.new(htf='497',htfint=497,max_memory=3)
var Candle[] candlesadd497                  = array.new<Candle>(0)
var BOSdata bosdataadd497                   = BOSdata.new()
htfadd497.settings                 := SettingsHTFadd497
htfadd497.candles                  := candlesadd497
htfadd497.bosdata                  := bosdataadd497
var CandleSet htfadd498                     = CandleSet.new()
var CandleSettings SettingsHTFadd498        = CandleSettings.new(htf='498',htfint=498,max_memory=3)
var Candle[] candlesadd498                  = array.new<Candle>(0)
var BOSdata bosdataadd498                   = BOSdata.new()
htfadd498.settings                 := SettingsHTFadd498
htfadd498.candles                  := candlesadd498
htfadd498.bosdata                  := bosdataadd498
var CandleSet htfadd499                     = CandleSet.new()
var CandleSettings SettingsHTFadd499        = CandleSettings.new(htf='499',htfint=499,max_memory=3)
var Candle[] candlesadd499                  = array.new<Candle>(0)
var BOSdata bosdataadd499                   = BOSdata.new()
htfadd499.settings                 := SettingsHTFadd499
htfadd499.candles                  := candlesadd499
htfadd499.bosdata                  := bosdataadd499
var CandleSet htfadd500                     = CandleSet.new()
var CandleSettings SettingsHTFadd500        = CandleSettings.new(htf='500',htfint=500,max_memory=3)
var Candle[] candlesadd500                  = array.new<Candle>(0)
var BOSdata bosdataadd500                   = BOSdata.new()
htfadd500.settings                 := SettingsHTFadd500
htfadd500.candles                  := candlesadd500
htfadd500.bosdata                  := bosdataadd500
var CandleSet htfadd501                     = CandleSet.new()
var CandleSettings SettingsHTFadd501        = CandleSettings.new(htf='501',htfint=501,max_memory=3)
var Candle[] candlesadd501                  = array.new<Candle>(0)
var BOSdata bosdataadd501                   = BOSdata.new()
htfadd501.settings                 := SettingsHTFadd501
htfadd501.candles                  := candlesadd501
htfadd501.bosdata                  := bosdataadd501
var CandleSet htfadd502                     = CandleSet.new()
var CandleSettings SettingsHTFadd502        = CandleSettings.new(htf='502',htfint=502,max_memory=3)
var Candle[] candlesadd502                  = array.new<Candle>(0)
var BOSdata bosdataadd502                   = BOSdata.new()
htfadd502.settings                 := SettingsHTFadd502
htfadd502.candles                  := candlesadd502
htfadd502.bosdata                  := bosdataadd502
var CandleSet htfadd503                     = CandleSet.new()
var CandleSettings SettingsHTFadd503        = CandleSettings.new(htf='503',htfint=503,max_memory=3)
var Candle[] candlesadd503                  = array.new<Candle>(0)
var BOSdata bosdataadd503                   = BOSdata.new()
htfadd503.settings                 := SettingsHTFadd503
htfadd503.candles                  := candlesadd503
htfadd503.bosdata                  := bosdataadd503
var CandleSet htfadd504                     = CandleSet.new()
var CandleSettings SettingsHTFadd504        = CandleSettings.new(htf='504',htfint=504,max_memory=3)
var Candle[] candlesadd504                  = array.new<Candle>(0)
var BOSdata bosdataadd504                   = BOSdata.new()
htfadd504.settings                 := SettingsHTFadd504
htfadd504.candles                  := candlesadd504
htfadd504.bosdata                  := bosdataadd504
var CandleSet htfadd505                     = CandleSet.new()
var CandleSettings SettingsHTFadd505        = CandleSettings.new(htf='505',htfint=505,max_memory=3)
var Candle[] candlesadd505                  = array.new<Candle>(0)
var BOSdata bosdataadd505                   = BOSdata.new()
htfadd505.settings                 := SettingsHTFadd505
htfadd505.candles                  := candlesadd505
htfadd505.bosdata                  := bosdataadd505
var CandleSet htfadd506                     = CandleSet.new()
var CandleSettings SettingsHTFadd506        = CandleSettings.new(htf='506',htfint=506,max_memory=3)
var Candle[] candlesadd506                  = array.new<Candle>(0)
var BOSdata bosdataadd506                   = BOSdata.new()
htfadd506.settings                 := SettingsHTFadd506
htfadd506.candles                  := candlesadd506
htfadd506.bosdata                  := bosdataadd506
var CandleSet htfadd507                     = CandleSet.new()
var CandleSettings SettingsHTFadd507        = CandleSettings.new(htf='507',htfint=507,max_memory=3)
var Candle[] candlesadd507                  = array.new<Candle>(0)
var BOSdata bosdataadd507                   = BOSdata.new()
htfadd507.settings                 := SettingsHTFadd507
htfadd507.candles                  := candlesadd507
htfadd507.bosdata                  := bosdataadd507
var CandleSet htfadd508                     = CandleSet.new()
var CandleSettings SettingsHTFadd508        = CandleSettings.new(htf='508',htfint=508,max_memory=3)
var Candle[] candlesadd508                  = array.new<Candle>(0)
var BOSdata bosdataadd508                   = BOSdata.new()
htfadd508.settings                 := SettingsHTFadd508
htfadd508.candles                  := candlesadd508
htfadd508.bosdata                  := bosdataadd508
var CandleSet htfadd509                     = CandleSet.new()
var CandleSettings SettingsHTFadd509        = CandleSettings.new(htf='509',htfint=509,max_memory=3)
var Candle[] candlesadd509                  = array.new<Candle>(0)
var BOSdata bosdataadd509                   = BOSdata.new()
htfadd509.settings                 := SettingsHTFadd509
htfadd509.candles                  := candlesadd509
htfadd509.bosdata                  := bosdataadd509
var CandleSet htfadd510                     = CandleSet.new()
var CandleSettings SettingsHTFadd510        = CandleSettings.new(htf='510',htfint=510,max_memory=3)
var Candle[] candlesadd510                  = array.new<Candle>(0)
var BOSdata bosdataadd510                   = BOSdata.new()
htfadd510.settings                 := SettingsHTFadd510
htfadd510.candles                  := candlesadd510
htfadd510.bosdata                  := bosdataadd510
var CandleSet htfadd511                     = CandleSet.new()
var CandleSettings SettingsHTFadd511        = CandleSettings.new(htf='511',htfint=511,max_memory=3)
var Candle[] candlesadd511                  = array.new<Candle>(0)
var BOSdata bosdataadd511                   = BOSdata.new()
htfadd511.settings                 := SettingsHTFadd511
htfadd511.candles                  := candlesadd511
htfadd511.bosdata                  := bosdataadd511
var CandleSet htfadd512                     = CandleSet.new()
var CandleSettings SettingsHTFadd512        = CandleSettings.new(htf='512',htfint=512,max_memory=3)
var Candle[] candlesadd512                  = array.new<Candle>(0)
var BOSdata bosdataadd512                   = BOSdata.new()
htfadd512.settings                 := SettingsHTFadd512
htfadd512.candles                  := candlesadd512
htfadd512.bosdata                  := bosdataadd512
var CandleSet htfadd513                     = CandleSet.new()
var CandleSettings SettingsHTFadd513        = CandleSettings.new(htf='513',htfint=513,max_memory=3)
var Candle[] candlesadd513                  = array.new<Candle>(0)
var BOSdata bosdataadd513                   = BOSdata.new()
htfadd513.settings                 := SettingsHTFadd513
htfadd513.candles                  := candlesadd513
htfadd513.bosdata                  := bosdataadd513
var CandleSet htfadd514                     = CandleSet.new()
var CandleSettings SettingsHTFadd514        = CandleSettings.new(htf='514',htfint=514,max_memory=3)
var Candle[] candlesadd514                  = array.new<Candle>(0)
var BOSdata bosdataadd514                   = BOSdata.new()
htfadd514.settings                 := SettingsHTFadd514
htfadd514.candles                  := candlesadd514
htfadd514.bosdata                  := bosdataadd514
var CandleSet htfadd515                     = CandleSet.new()
var CandleSettings SettingsHTFadd515        = CandleSettings.new(htf='515',htfint=515,max_memory=3)
var Candle[] candlesadd515                  = array.new<Candle>(0)
var BOSdata bosdataadd515                   = BOSdata.new()
htfadd515.settings                 := SettingsHTFadd515
htfadd515.candles                  := candlesadd515
htfadd515.bosdata                  := bosdataadd515
var CandleSet htfadd516                     = CandleSet.new()
var CandleSettings SettingsHTFadd516        = CandleSettings.new(htf='516',htfint=516,max_memory=3)
var Candle[] candlesadd516                  = array.new<Candle>(0)
var BOSdata bosdataadd516                   = BOSdata.new()
htfadd516.settings                 := SettingsHTFadd516
htfadd516.candles                  := candlesadd516
htfadd516.bosdata                  := bosdataadd516
var CandleSet htfadd517                     = CandleSet.new()
var CandleSettings SettingsHTFadd517        = CandleSettings.new(htf='517',htfint=517,max_memory=3)
var Candle[] candlesadd517                  = array.new<Candle>(0)
var BOSdata bosdataadd517                   = BOSdata.new()
htfadd517.settings                 := SettingsHTFadd517
htfadd517.candles                  := candlesadd517
htfadd517.bosdata                  := bosdataadd517
var CandleSet htfadd518                     = CandleSet.new()
var CandleSettings SettingsHTFadd518        = CandleSettings.new(htf='518',htfint=518,max_memory=3)
var Candle[] candlesadd518                  = array.new<Candle>(0)
var BOSdata bosdataadd518                   = BOSdata.new()
htfadd518.settings                 := SettingsHTFadd518
htfadd518.candles                  := candlesadd518
htfadd518.bosdata                  := bosdataadd518
var CandleSet htfadd519                     = CandleSet.new()
var CandleSettings SettingsHTFadd519        = CandleSettings.new(htf='519',htfint=519,max_memory=3)
var Candle[] candlesadd519                  = array.new<Candle>(0)
var BOSdata bosdataadd519                   = BOSdata.new()
htfadd519.settings                 := SettingsHTFadd519
htfadd519.candles                  := candlesadd519
htfadd519.bosdata                  := bosdataadd519
var CandleSet htfadd520                     = CandleSet.new()
var CandleSettings SettingsHTFadd520        = CandleSettings.new(htf='520',htfint=520,max_memory=3)
var Candle[] candlesadd520                  = array.new<Candle>(0)
var BOSdata bosdataadd520                   = BOSdata.new()
htfadd520.settings                 := SettingsHTFadd520
htfadd520.candles                  := candlesadd520
htfadd520.bosdata                  := bosdataadd520
var CandleSet htfadd521                     = CandleSet.new()
var CandleSettings SettingsHTFadd521        = CandleSettings.new(htf='521',htfint=521,max_memory=3)
var Candle[] candlesadd521                  = array.new<Candle>(0)
var BOSdata bosdataadd521                   = BOSdata.new()
htfadd521.settings                 := SettingsHTFadd521
htfadd521.candles                  := candlesadd521
htfadd521.bosdata                  := bosdataadd521
var CandleSet htfadd522                     = CandleSet.new()
var CandleSettings SettingsHTFadd522        = CandleSettings.new(htf='522',htfint=522,max_memory=3)
var Candle[] candlesadd522                  = array.new<Candle>(0)
var BOSdata bosdataadd522                   = BOSdata.new()
htfadd522.settings                 := SettingsHTFadd522
htfadd522.candles                  := candlesadd522
htfadd522.bosdata                  := bosdataadd522
var CandleSet htfadd523                     = CandleSet.new()
var CandleSettings SettingsHTFadd523        = CandleSettings.new(htf='523',htfint=523,max_memory=3)
var Candle[] candlesadd523                  = array.new<Candle>(0)
var BOSdata bosdataadd523                   = BOSdata.new()
htfadd523.settings                 := SettingsHTFadd523
htfadd523.candles                  := candlesadd523
htfadd523.bosdata                  := bosdataadd523
var CandleSet htfadd524                     = CandleSet.new()
var CandleSettings SettingsHTFadd524        = CandleSettings.new(htf='524',htfint=524,max_memory=3)
var Candle[] candlesadd524                  = array.new<Candle>(0)
var BOSdata bosdataadd524                   = BOSdata.new()
htfadd524.settings                 := SettingsHTFadd524
htfadd524.candles                  := candlesadd524
htfadd524.bosdata                  := bosdataadd524
var CandleSet htfadd525                     = CandleSet.new()
var CandleSettings SettingsHTFadd525        = CandleSettings.new(htf='525',htfint=525,max_memory=3)
var Candle[] candlesadd525                  = array.new<Candle>(0)
var BOSdata bosdataadd525                   = BOSdata.new()
htfadd525.settings                 := SettingsHTFadd525
htfadd525.candles                  := candlesadd525
htfadd525.bosdata                  := bosdataadd525
var CandleSet htfadd526                     = CandleSet.new()
var CandleSettings SettingsHTFadd526        = CandleSettings.new(htf='526',htfint=526,max_memory=3)
var Candle[] candlesadd526                  = array.new<Candle>(0)
var BOSdata bosdataadd526                   = BOSdata.new()
htfadd526.settings                 := SettingsHTFadd526
htfadd526.candles                  := candlesadd526
htfadd526.bosdata                  := bosdataadd526
var CandleSet htfadd527                     = CandleSet.new()
var CandleSettings SettingsHTFadd527        = CandleSettings.new(htf='527',htfint=527,max_memory=3)
var Candle[] candlesadd527                  = array.new<Candle>(0)
var BOSdata bosdataadd527                   = BOSdata.new()
htfadd527.settings                 := SettingsHTFadd527
htfadd527.candles                  := candlesadd527
htfadd527.bosdata                  := bosdataadd527
var CandleSet htfadd528                     = CandleSet.new()
var CandleSettings SettingsHTFadd528        = CandleSettings.new(htf='528',htfint=528,max_memory=3)
var Candle[] candlesadd528                  = array.new<Candle>(0)
var BOSdata bosdataadd528                   = BOSdata.new()
htfadd528.settings                 := SettingsHTFadd528
htfadd528.candles                  := candlesadd528
htfadd528.bosdata                  := bosdataadd528
var CandleSet htfadd529                     = CandleSet.new()
var CandleSettings SettingsHTFadd529        = CandleSettings.new(htf='529',htfint=529,max_memory=3)
var Candle[] candlesadd529                  = array.new<Candle>(0)
var BOSdata bosdataadd529                   = BOSdata.new()
htfadd529.settings                 := SettingsHTFadd529
htfadd529.candles                  := candlesadd529
htfadd529.bosdata                  := bosdataadd529
var CandleSet htfadd530                     = CandleSet.new()
var CandleSettings SettingsHTFadd530        = CandleSettings.new(htf='530',htfint=530,max_memory=3)
var Candle[] candlesadd530                  = array.new<Candle>(0)
var BOSdata bosdataadd530                   = BOSdata.new()
htfadd530.settings                 := SettingsHTFadd530
htfadd530.candles                  := candlesadd530
htfadd530.bosdata                  := bosdataadd530
var CandleSet htfadd531                     = CandleSet.new()
var CandleSettings SettingsHTFadd531        = CandleSettings.new(htf='531',htfint=531,max_memory=3)
var Candle[] candlesadd531                  = array.new<Candle>(0)
var BOSdata bosdataadd531                   = BOSdata.new()
htfadd531.settings                 := SettingsHTFadd531
htfadd531.candles                  := candlesadd531
htfadd531.bosdata                  := bosdataadd531
var CandleSet htfadd532                     = CandleSet.new()
var CandleSettings SettingsHTFadd532        = CandleSettings.new(htf='532',htfint=532,max_memory=3)
var Candle[] candlesadd532                  = array.new<Candle>(0)
var BOSdata bosdataadd532                   = BOSdata.new()
htfadd532.settings                 := SettingsHTFadd532
htfadd532.candles                  := candlesadd532
htfadd532.bosdata                  := bosdataadd532
var CandleSet htfadd533                     = CandleSet.new()
var CandleSettings SettingsHTFadd533        = CandleSettings.new(htf='533',htfint=533,max_memory=3)
var Candle[] candlesadd533                  = array.new<Candle>(0)
var BOSdata bosdataadd533                   = BOSdata.new()
htfadd533.settings                 := SettingsHTFadd533
htfadd533.candles                  := candlesadd533
htfadd533.bosdata                  := bosdataadd533
var CandleSet htfadd534                     = CandleSet.new()
var CandleSettings SettingsHTFadd534        = CandleSettings.new(htf='534',htfint=534,max_memory=3)
var Candle[] candlesadd534                  = array.new<Candle>(0)
var BOSdata bosdataadd534                   = BOSdata.new()
htfadd534.settings                 := SettingsHTFadd534
htfadd534.candles                  := candlesadd534
htfadd534.bosdata                  := bosdataadd534
var CandleSet htfadd535                     = CandleSet.new()
var CandleSettings SettingsHTFadd535        = CandleSettings.new(htf='535',htfint=535,max_memory=3)
var Candle[] candlesadd535                  = array.new<Candle>(0)
var BOSdata bosdataadd535                   = BOSdata.new()
htfadd535.settings                 := SettingsHTFadd535
htfadd535.candles                  := candlesadd535
htfadd535.bosdata                  := bosdataadd535
var CandleSet htfadd536                     = CandleSet.new()
var CandleSettings SettingsHTFadd536        = CandleSettings.new(htf='536',htfint=536,max_memory=3)
var Candle[] candlesadd536                  = array.new<Candle>(0)
var BOSdata bosdataadd536                   = BOSdata.new()
htfadd536.settings                 := SettingsHTFadd536
htfadd536.candles                  := candlesadd536
htfadd536.bosdata                  := bosdataadd536
var CandleSet htfadd537                     = CandleSet.new()
var CandleSettings SettingsHTFadd537        = CandleSettings.new(htf='537',htfint=537,max_memory=3)
var Candle[] candlesadd537                  = array.new<Candle>(0)
var BOSdata bosdataadd537                   = BOSdata.new()
htfadd537.settings                 := SettingsHTFadd537
htfadd537.candles                  := candlesadd537
htfadd537.bosdata                  := bosdataadd537
var CandleSet htfadd538                     = CandleSet.new()
var CandleSettings SettingsHTFadd538        = CandleSettings.new(htf='538',htfint=538,max_memory=3)
var Candle[] candlesadd538                  = array.new<Candle>(0)
var BOSdata bosdataadd538                   = BOSdata.new()
htfadd538.settings                 := SettingsHTFadd538
htfadd538.candles                  := candlesadd538
htfadd538.bosdata                  := bosdataadd538
var CandleSet htfadd539                     = CandleSet.new()
var CandleSettings SettingsHTFadd539        = CandleSettings.new(htf='539',htfint=539,max_memory=3)
var Candle[] candlesadd539                  = array.new<Candle>(0)
var BOSdata bosdataadd539                   = BOSdata.new()
htfadd539.settings                 := SettingsHTFadd539
htfadd539.candles                  := candlesadd539
htfadd539.bosdata                  := bosdataadd539
var CandleSet htfadd540                     = CandleSet.new()
var CandleSettings SettingsHTFadd540        = CandleSettings.new(htf='540',htfint=540,max_memory=3)
var Candle[] candlesadd540                  = array.new<Candle>(0)
var BOSdata bosdataadd540                   = BOSdata.new()
htfadd540.settings                 := SettingsHTFadd540
htfadd540.candles                  := candlesadd540
htfadd540.bosdata                  := bosdataadd540

htfadd450.Monitor().BOSJudge()
htfadd451.Monitor().BOSJudge()
htfadd452.Monitor().BOSJudge()
htfadd453.Monitor().BOSJudge()
htfadd454.Monitor().BOSJudge()
htfadd455.Monitor().BOSJudge()
htfadd456.Monitor().BOSJudge()
htfadd457.Monitor().BOSJudge()
htfadd458.Monitor().BOSJudge()
htfadd459.Monitor().BOSJudge()
htfadd460.Monitor().BOSJudge()
htfadd461.Monitor().BOSJudge()
htfadd462.Monitor().BOSJudge()
htfadd463.Monitor().BOSJudge()
htfadd464.Monitor().BOSJudge()
htfadd465.Monitor().BOSJudge()
htfadd466.Monitor().BOSJudge()
htfadd467.Monitor().BOSJudge()
htfadd468.Monitor().BOSJudge()
htfadd469.Monitor().BOSJudge()
htfadd470.Monitor().BOSJudge()
htfadd471.Monitor().BOSJudge()
htfadd472.Monitor().BOSJudge()
htfadd473.Monitor().BOSJudge()
htfadd474.Monitor().BOSJudge()
htfadd475.Monitor().BOSJudge()
htfadd476.Monitor().BOSJudge()
htfadd477.Monitor().BOSJudge()
htfadd478.Monitor().BOSJudge()
htfadd479.Monitor().BOSJudge()
htfadd480.Monitor().BOSJudge()
htfadd481.Monitor().BOSJudge()
htfadd482.Monitor().BOSJudge()
htfadd483.Monitor().BOSJudge()
htfadd484.Monitor().BOSJudge()
htfadd485.Monitor().BOSJudge()
htfadd486.Monitor().BOSJudge()
htfadd487.Monitor().BOSJudge()
htfadd488.Monitor().BOSJudge()
htfadd489.Monitor().BOSJudge()
htfadd490.Monitor().BOSJudge()
htfadd491.Monitor().BOSJudge()
htfadd492.Monitor().BOSJudge()
htfadd493.Monitor().BOSJudge()
htfadd494.Monitor().BOSJudge()
htfadd495.Monitor().BOSJudge()
htfadd496.Monitor().BOSJudge()
htfadd497.Monitor().BOSJudge()
htfadd498.Monitor().BOSJudge()
htfadd499.Monitor().BOSJudge()
htfadd500.Monitor().BOSJudge()
htfadd501.Monitor().BOSJudge()
htfadd502.Monitor().BOSJudge()
htfadd503.Monitor().BOSJudge()
htfadd504.Monitor().BOSJudge()
htfadd505.Monitor().BOSJudge()
htfadd506.Monitor().BOSJudge()
htfadd507.Monitor().BOSJudge()
htfadd508.Monitor().BOSJudge()
htfadd509.Monitor().BOSJudge()
htfadd510.Monitor().BOSJudge()
htfadd511.Monitor().BOSJudge()
htfadd512.Monitor().BOSJudge()
htfadd513.Monitor().BOSJudge()
htfadd514.Monitor().BOSJudge()
htfadd515.Monitor().BOSJudge()
htfadd516.Monitor().BOSJudge()
htfadd517.Monitor().BOSJudge()
htfadd518.Monitor().BOSJudge()
htfadd519.Monitor().BOSJudge()
htfadd520.Monitor().BOSJudge()
htfadd521.Monitor().BOSJudge()
htfadd522.Monitor().BOSJudge()
htfadd523.Monitor().BOSJudge()
htfadd524.Monitor().BOSJudge()
htfadd525.Monitor().BOSJudge()
htfadd526.Monitor().BOSJudge()
htfadd527.Monitor().BOSJudge()
htfadd528.Monitor().BOSJudge()
htfadd529.Monitor().BOSJudge()
htfadd530.Monitor().BOSJudge()
htfadd531.Monitor().BOSJudge()
htfadd532.Monitor().BOSJudge()
htfadd533.Monitor().BOSJudge()
htfadd534.Monitor().BOSJudge()
htfadd535.Monitor().BOSJudge()
htfadd536.Monitor().BOSJudge()
htfadd537.Monitor().BOSJudge()
htfadd538.Monitor().BOSJudge()
htfadd539.Monitor().BOSJudge()
htfadd540.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd450)
    LowestsbuSet(lowestsbu, htfadd450)
    HighestsbdSet(highestsbd, htfadd451)
    LowestsbuSet(lowestsbu, htfadd451)
    HighestsbdSet(highestsbd, htfadd452)
    LowestsbuSet(lowestsbu, htfadd452)
    HighestsbdSet(highestsbd, htfadd453)
    LowestsbuSet(lowestsbu, htfadd453)
    HighestsbdSet(highestsbd, htfadd454)
    LowestsbuSet(lowestsbu, htfadd454)
    HighestsbdSet(highestsbd, htfadd455)
    LowestsbuSet(lowestsbu, htfadd455)
    HighestsbdSet(highestsbd, htfadd456)
    LowestsbuSet(lowestsbu, htfadd456)
    HighestsbdSet(highestsbd, htfadd457)
    LowestsbuSet(lowestsbu, htfadd457)
    HighestsbdSet(highestsbd, htfadd458)
    LowestsbuSet(lowestsbu, htfadd458)
    HighestsbdSet(highestsbd, htfadd459)
    LowestsbuSet(lowestsbu, htfadd459)
    HighestsbdSet(highestsbd, htfadd460)
    LowestsbuSet(lowestsbu, htfadd460)
    HighestsbdSet(highestsbd, htfadd461)
    LowestsbuSet(lowestsbu, htfadd461)
    HighestsbdSet(highestsbd, htfadd462)
    LowestsbuSet(lowestsbu, htfadd462)
    HighestsbdSet(highestsbd, htfadd463)
    LowestsbuSet(lowestsbu, htfadd463)
    HighestsbdSet(highestsbd, htfadd464)
    LowestsbuSet(lowestsbu, htfadd464)
    HighestsbdSet(highestsbd, htfadd465)
    LowestsbuSet(lowestsbu, htfadd465)
    HighestsbdSet(highestsbd, htfadd466)
    LowestsbuSet(lowestsbu, htfadd466)
    HighestsbdSet(highestsbd, htfadd467)
    LowestsbuSet(lowestsbu, htfadd467)
    HighestsbdSet(highestsbd, htfadd468)
    LowestsbuSet(lowestsbu, htfadd468)
    HighestsbdSet(highestsbd, htfadd469)
    LowestsbuSet(lowestsbu, htfadd469)
    HighestsbdSet(highestsbd, htfadd470)
    LowestsbuSet(lowestsbu, htfadd470)
    HighestsbdSet(highestsbd, htfadd471)
    LowestsbuSet(lowestsbu, htfadd471)
    HighestsbdSet(highestsbd, htfadd472)
    LowestsbuSet(lowestsbu, htfadd472)
    HighestsbdSet(highestsbd, htfadd473)
    LowestsbuSet(lowestsbu, htfadd473)
    HighestsbdSet(highestsbd, htfadd474)
    LowestsbuSet(lowestsbu, htfadd474)
    HighestsbdSet(highestsbd, htfadd475)
    LowestsbuSet(lowestsbu, htfadd475)
    HighestsbdSet(highestsbd, htfadd476)
    LowestsbuSet(lowestsbu, htfadd476)
    HighestsbdSet(highestsbd, htfadd477)
    LowestsbuSet(lowestsbu, htfadd477)
    HighestsbdSet(highestsbd, htfadd478)
    LowestsbuSet(lowestsbu, htfadd478)
    HighestsbdSet(highestsbd, htfadd479)
    LowestsbuSet(lowestsbu, htfadd479)
    HighestsbdSet(highestsbd, htfadd480)
    LowestsbuSet(lowestsbu, htfadd480)
    HighestsbdSet(highestsbd, htfadd481)
    LowestsbuSet(lowestsbu, htfadd481)
    HighestsbdSet(highestsbd, htfadd482)
    LowestsbuSet(lowestsbu, htfadd482)
    HighestsbdSet(highestsbd, htfadd483)
    LowestsbuSet(lowestsbu, htfadd483)
    HighestsbdSet(highestsbd, htfadd484)
    LowestsbuSet(lowestsbu, htfadd484)
    HighestsbdSet(highestsbd, htfadd485)
    LowestsbuSet(lowestsbu, htfadd485)
    HighestsbdSet(highestsbd, htfadd486)
    LowestsbuSet(lowestsbu, htfadd486)
    HighestsbdSet(highestsbd, htfadd487)
    LowestsbuSet(lowestsbu, htfadd487)
    HighestsbdSet(highestsbd, htfadd488)
    LowestsbuSet(lowestsbu, htfadd488)
    HighestsbdSet(highestsbd, htfadd489)
    LowestsbuSet(lowestsbu, htfadd489)
    HighestsbdSet(highestsbd, htfadd490)
    LowestsbuSet(lowestsbu, htfadd490)
    HighestsbdSet(highestsbd, htfadd491)
    LowestsbuSet(lowestsbu, htfadd491)
    HighestsbdSet(highestsbd, htfadd492)
    LowestsbuSet(lowestsbu, htfadd492)
    HighestsbdSet(highestsbd, htfadd493)
    LowestsbuSet(lowestsbu, htfadd493)
    HighestsbdSet(highestsbd, htfadd494)
    LowestsbuSet(lowestsbu, htfadd494)
    HighestsbdSet(highestsbd, htfadd495)
    LowestsbuSet(lowestsbu, htfadd495)
    HighestsbdSet(highestsbd, htfadd496)
    LowestsbuSet(lowestsbu, htfadd496)
    HighestsbdSet(highestsbd, htfadd497)
    LowestsbuSet(lowestsbu, htfadd497)
    HighestsbdSet(highestsbd, htfadd498)
    LowestsbuSet(lowestsbu, htfadd498)
    HighestsbdSet(highestsbd, htfadd499)
    LowestsbuSet(lowestsbu, htfadd499)
    HighestsbdSet(highestsbd, htfadd500)
    LowestsbuSet(lowestsbu, htfadd500)
    HighestsbdSet(highestsbd, htfadd501)
    LowestsbuSet(lowestsbu, htfadd501)
    HighestsbdSet(highestsbd, htfadd502)
    LowestsbuSet(lowestsbu, htfadd502)
    HighestsbdSet(highestsbd, htfadd503)
    LowestsbuSet(lowestsbu, htfadd503)
    HighestsbdSet(highestsbd, htfadd504)
    LowestsbuSet(lowestsbu, htfadd504)
    HighestsbdSet(highestsbd, htfadd505)
    LowestsbuSet(lowestsbu, htfadd505)
    HighestsbdSet(highestsbd, htfadd506)
    LowestsbuSet(lowestsbu, htfadd506)
    HighestsbdSet(highestsbd, htfadd507)
    LowestsbuSet(lowestsbu, htfadd507)
    HighestsbdSet(highestsbd, htfadd508)
    LowestsbuSet(lowestsbu, htfadd508)
    HighestsbdSet(highestsbd, htfadd509)
    LowestsbuSet(lowestsbu, htfadd509)
    HighestsbdSet(highestsbd, htfadd510)
    LowestsbuSet(lowestsbu, htfadd510)
    HighestsbdSet(highestsbd, htfadd511)
    LowestsbuSet(lowestsbu, htfadd511)
    HighestsbdSet(highestsbd, htfadd512)
    LowestsbuSet(lowestsbu, htfadd512)
    HighestsbdSet(highestsbd, htfadd513)
    LowestsbuSet(lowestsbu, htfadd513)
    HighestsbdSet(highestsbd, htfadd514)
    LowestsbuSet(lowestsbu, htfadd514)
    HighestsbdSet(highestsbd, htfadd515)
    LowestsbuSet(lowestsbu, htfadd515)
    HighestsbdSet(highestsbd, htfadd516)
    LowestsbuSet(lowestsbu, htfadd516)
    HighestsbdSet(highestsbd, htfadd517)
    LowestsbuSet(lowestsbu, htfadd517)
    HighestsbdSet(highestsbd, htfadd518)
    LowestsbuSet(lowestsbu, htfadd518)
    HighestsbdSet(highestsbd, htfadd519)
    LowestsbuSet(lowestsbu, htfadd519)
    HighestsbdSet(highestsbd, htfadd520)
    LowestsbuSet(lowestsbu, htfadd520)
    HighestsbdSet(highestsbd, htfadd521)
    LowestsbuSet(lowestsbu, htfadd521)
    HighestsbdSet(highestsbd, htfadd522)
    LowestsbuSet(lowestsbu, htfadd522)
    HighestsbdSet(highestsbd, htfadd523)
    LowestsbuSet(lowestsbu, htfadd523)
    HighestsbdSet(highestsbd, htfadd524)
    LowestsbuSet(lowestsbu, htfadd524)
    HighestsbdSet(highestsbd, htfadd525)
    LowestsbuSet(lowestsbu, htfadd525)
    HighestsbdSet(highestsbd, htfadd526)
    LowestsbuSet(lowestsbu, htfadd526)
    HighestsbdSet(highestsbd, htfadd527)
    LowestsbuSet(lowestsbu, htfadd527)
    HighestsbdSet(highestsbd, htfadd528)
    LowestsbuSet(lowestsbu, htfadd528)
    HighestsbdSet(highestsbd, htfadd529)
    LowestsbuSet(lowestsbu, htfadd529)
    HighestsbdSet(highestsbd, htfadd530)
    LowestsbuSet(lowestsbu, htfadd530)
    HighestsbdSet(highestsbd, htfadd531)
    LowestsbuSet(lowestsbu, htfadd531)
    HighestsbdSet(highestsbd, htfadd532)
    LowestsbuSet(lowestsbu, htfadd532)
    HighestsbdSet(highestsbd, htfadd533)
    LowestsbuSet(lowestsbu, htfadd533)
    HighestsbdSet(highestsbd, htfadd534)
    LowestsbuSet(lowestsbu, htfadd534)
    HighestsbdSet(highestsbd, htfadd535)
    LowestsbuSet(lowestsbu, htfadd535)
    HighestsbdSet(highestsbd, htfadd536)
    LowestsbuSet(lowestsbu, htfadd536)
    HighestsbdSet(highestsbd, htfadd537)
    LowestsbuSet(lowestsbu, htfadd537)
    HighestsbdSet(highestsbd, htfadd538)
    LowestsbuSet(lowestsbu, htfadd538)
    HighestsbdSet(highestsbd, htfadd539)
    LowestsbuSet(lowestsbu, htfadd539)
    HighestsbdSet(highestsbd, htfadd540)
    LowestsbuSet(lowestsbu, htfadd540)

    fggetnowclose := true
    htfshadow.Shadowing(htfadd450).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd451).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd452).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd453).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd454).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd455).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd456).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd457).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd458).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd459).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd460).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd461).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd462).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd463).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd464).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd465).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd466).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd467).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd468).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd469).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd470).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd471).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd472).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd473).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd474).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd475).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd476).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd477).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd478).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd479).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd480).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd481).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd482).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd483).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd484).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd485).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd486).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd487).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd488).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd489).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd490).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd491).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd492).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd493).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd494).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd495).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd496).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd497).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd498).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd499).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd500).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd501).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd502).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd503).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd504).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd505).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd506).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd507).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd508).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd509).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd510).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd511).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd512).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd513).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd514).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd515).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd516).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd517).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd518).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd519).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd520).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd521).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd522).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd523).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd524).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd525).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd526).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd527).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd528).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd529).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd530).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd531).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd532).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd533).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd534).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd535).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd536).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd537).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd538).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd539).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd540).Monitor_Est().BOSJudge()
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


