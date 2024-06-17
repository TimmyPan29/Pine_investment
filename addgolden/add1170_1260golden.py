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
var CandleSet htfadd1170                     = CandleSet.new()
var CandleSettings SettingsHTFadd1170        = CandleSettings.new(htf='1170',htfint=1170,max_memory=3)
var Candle[] candlesadd1170                  = array.new<Candle>(0)
var BOSdata bosdataadd1170                   = BOSdata.new()
htfadd1170.settings                 := SettingsHTFadd1170
htfadd1170.candles                  := candlesadd1170
htfadd1170.bosdata                  := bosdataadd1170
var CandleSet htfadd1171                     = CandleSet.new()
var CandleSettings SettingsHTFadd1171        = CandleSettings.new(htf='1171',htfint=1171,max_memory=3)
var Candle[] candlesadd1171                  = array.new<Candle>(0)
var BOSdata bosdataadd1171                   = BOSdata.new()
htfadd1171.settings                 := SettingsHTFadd1171
htfadd1171.candles                  := candlesadd1171
htfadd1171.bosdata                  := bosdataadd1171
var CandleSet htfadd1172                     = CandleSet.new()
var CandleSettings SettingsHTFadd1172        = CandleSettings.new(htf='1172',htfint=1172,max_memory=3)
var Candle[] candlesadd1172                  = array.new<Candle>(0)
var BOSdata bosdataadd1172                   = BOSdata.new()
htfadd1172.settings                 := SettingsHTFadd1172
htfadd1172.candles                  := candlesadd1172
htfadd1172.bosdata                  := bosdataadd1172
var CandleSet htfadd1173                     = CandleSet.new()
var CandleSettings SettingsHTFadd1173        = CandleSettings.new(htf='1173',htfint=1173,max_memory=3)
var Candle[] candlesadd1173                  = array.new<Candle>(0)
var BOSdata bosdataadd1173                   = BOSdata.new()
htfadd1173.settings                 := SettingsHTFadd1173
htfadd1173.candles                  := candlesadd1173
htfadd1173.bosdata                  := bosdataadd1173
var CandleSet htfadd1174                     = CandleSet.new()
var CandleSettings SettingsHTFadd1174        = CandleSettings.new(htf='1174',htfint=1174,max_memory=3)
var Candle[] candlesadd1174                  = array.new<Candle>(0)
var BOSdata bosdataadd1174                   = BOSdata.new()
htfadd1174.settings                 := SettingsHTFadd1174
htfadd1174.candles                  := candlesadd1174
htfadd1174.bosdata                  := bosdataadd1174
var CandleSet htfadd1175                     = CandleSet.new()
var CandleSettings SettingsHTFadd1175        = CandleSettings.new(htf='1175',htfint=1175,max_memory=3)
var Candle[] candlesadd1175                  = array.new<Candle>(0)
var BOSdata bosdataadd1175                   = BOSdata.new()
htfadd1175.settings                 := SettingsHTFadd1175
htfadd1175.candles                  := candlesadd1175
htfadd1175.bosdata                  := bosdataadd1175
var CandleSet htfadd1176                     = CandleSet.new()
var CandleSettings SettingsHTFadd1176        = CandleSettings.new(htf='1176',htfint=1176,max_memory=3)
var Candle[] candlesadd1176                  = array.new<Candle>(0)
var BOSdata bosdataadd1176                   = BOSdata.new()
htfadd1176.settings                 := SettingsHTFadd1176
htfadd1176.candles                  := candlesadd1176
htfadd1176.bosdata                  := bosdataadd1176
var CandleSet htfadd1177                     = CandleSet.new()
var CandleSettings SettingsHTFadd1177        = CandleSettings.new(htf='1177',htfint=1177,max_memory=3)
var Candle[] candlesadd1177                  = array.new<Candle>(0)
var BOSdata bosdataadd1177                   = BOSdata.new()
htfadd1177.settings                 := SettingsHTFadd1177
htfadd1177.candles                  := candlesadd1177
htfadd1177.bosdata                  := bosdataadd1177
var CandleSet htfadd1178                     = CandleSet.new()
var CandleSettings SettingsHTFadd1178        = CandleSettings.new(htf='1178',htfint=1178,max_memory=3)
var Candle[] candlesadd1178                  = array.new<Candle>(0)
var BOSdata bosdataadd1178                   = BOSdata.new()
htfadd1178.settings                 := SettingsHTFadd1178
htfadd1178.candles                  := candlesadd1178
htfadd1178.bosdata                  := bosdataadd1178
var CandleSet htfadd1179                     = CandleSet.new()
var CandleSettings SettingsHTFadd1179        = CandleSettings.new(htf='1179',htfint=1179,max_memory=3)
var Candle[] candlesadd1179                  = array.new<Candle>(0)
var BOSdata bosdataadd1179                   = BOSdata.new()
htfadd1179.settings                 := SettingsHTFadd1179
htfadd1179.candles                  := candlesadd1179
htfadd1179.bosdata                  := bosdataadd1179
var CandleSet htfadd1180                     = CandleSet.new()
var CandleSettings SettingsHTFadd1180        = CandleSettings.new(htf='1180',htfint=1180,max_memory=3)
var Candle[] candlesadd1180                  = array.new<Candle>(0)
var BOSdata bosdataadd1180                   = BOSdata.new()
htfadd1180.settings                 := SettingsHTFadd1180
htfadd1180.candles                  := candlesadd1180
htfadd1180.bosdata                  := bosdataadd1180
var CandleSet htfadd1181                     = CandleSet.new()
var CandleSettings SettingsHTFadd1181        = CandleSettings.new(htf='1181',htfint=1181,max_memory=3)
var Candle[] candlesadd1181                  = array.new<Candle>(0)
var BOSdata bosdataadd1181                   = BOSdata.new()
htfadd1181.settings                 := SettingsHTFadd1181
htfadd1181.candles                  := candlesadd1181
htfadd1181.bosdata                  := bosdataadd1181
var CandleSet htfadd1182                     = CandleSet.new()
var CandleSettings SettingsHTFadd1182        = CandleSettings.new(htf='1182',htfint=1182,max_memory=3)
var Candle[] candlesadd1182                  = array.new<Candle>(0)
var BOSdata bosdataadd1182                   = BOSdata.new()
htfadd1182.settings                 := SettingsHTFadd1182
htfadd1182.candles                  := candlesadd1182
htfadd1182.bosdata                  := bosdataadd1182
var CandleSet htfadd1183                     = CandleSet.new()
var CandleSettings SettingsHTFadd1183        = CandleSettings.new(htf='1183',htfint=1183,max_memory=3)
var Candle[] candlesadd1183                  = array.new<Candle>(0)
var BOSdata bosdataadd1183                   = BOSdata.new()
htfadd1183.settings                 := SettingsHTFadd1183
htfadd1183.candles                  := candlesadd1183
htfadd1183.bosdata                  := bosdataadd1183
var CandleSet htfadd1184                     = CandleSet.new()
var CandleSettings SettingsHTFadd1184        = CandleSettings.new(htf='1184',htfint=1184,max_memory=3)
var Candle[] candlesadd1184                  = array.new<Candle>(0)
var BOSdata bosdataadd1184                   = BOSdata.new()
htfadd1184.settings                 := SettingsHTFadd1184
htfadd1184.candles                  := candlesadd1184
htfadd1184.bosdata                  := bosdataadd1184
var CandleSet htfadd1185                     = CandleSet.new()
var CandleSettings SettingsHTFadd1185        = CandleSettings.new(htf='1185',htfint=1185,max_memory=3)
var Candle[] candlesadd1185                  = array.new<Candle>(0)
var BOSdata bosdataadd1185                   = BOSdata.new()
htfadd1185.settings                 := SettingsHTFadd1185
htfadd1185.candles                  := candlesadd1185
htfadd1185.bosdata                  := bosdataadd1185
var CandleSet htfadd1186                     = CandleSet.new()
var CandleSettings SettingsHTFadd1186        = CandleSettings.new(htf='1186',htfint=1186,max_memory=3)
var Candle[] candlesadd1186                  = array.new<Candle>(0)
var BOSdata bosdataadd1186                   = BOSdata.new()
htfadd1186.settings                 := SettingsHTFadd1186
htfadd1186.candles                  := candlesadd1186
htfadd1186.bosdata                  := bosdataadd1186
var CandleSet htfadd1187                     = CandleSet.new()
var CandleSettings SettingsHTFadd1187        = CandleSettings.new(htf='1187',htfint=1187,max_memory=3)
var Candle[] candlesadd1187                  = array.new<Candle>(0)
var BOSdata bosdataadd1187                   = BOSdata.new()
htfadd1187.settings                 := SettingsHTFadd1187
htfadd1187.candles                  := candlesadd1187
htfadd1187.bosdata                  := bosdataadd1187
var CandleSet htfadd1188                     = CandleSet.new()
var CandleSettings SettingsHTFadd1188        = CandleSettings.new(htf='1188',htfint=1188,max_memory=3)
var Candle[] candlesadd1188                  = array.new<Candle>(0)
var BOSdata bosdataadd1188                   = BOSdata.new()
htfadd1188.settings                 := SettingsHTFadd1188
htfadd1188.candles                  := candlesadd1188
htfadd1188.bosdata                  := bosdataadd1188
var CandleSet htfadd1189                     = CandleSet.new()
var CandleSettings SettingsHTFadd1189        = CandleSettings.new(htf='1189',htfint=1189,max_memory=3)
var Candle[] candlesadd1189                  = array.new<Candle>(0)
var BOSdata bosdataadd1189                   = BOSdata.new()
htfadd1189.settings                 := SettingsHTFadd1189
htfadd1189.candles                  := candlesadd1189
htfadd1189.bosdata                  := bosdataadd1189
var CandleSet htfadd1190                     = CandleSet.new()
var CandleSettings SettingsHTFadd1190        = CandleSettings.new(htf='1190',htfint=1190,max_memory=3)
var Candle[] candlesadd1190                  = array.new<Candle>(0)
var BOSdata bosdataadd1190                   = BOSdata.new()
htfadd1190.settings                 := SettingsHTFadd1190
htfadd1190.candles                  := candlesadd1190
htfadd1190.bosdata                  := bosdataadd1190
var CandleSet htfadd1191                     = CandleSet.new()
var CandleSettings SettingsHTFadd1191        = CandleSettings.new(htf='1191',htfint=1191,max_memory=3)
var Candle[] candlesadd1191                  = array.new<Candle>(0)
var BOSdata bosdataadd1191                   = BOSdata.new()
htfadd1191.settings                 := SettingsHTFadd1191
htfadd1191.candles                  := candlesadd1191
htfadd1191.bosdata                  := bosdataadd1191
var CandleSet htfadd1192                     = CandleSet.new()
var CandleSettings SettingsHTFadd1192        = CandleSettings.new(htf='1192',htfint=1192,max_memory=3)
var Candle[] candlesadd1192                  = array.new<Candle>(0)
var BOSdata bosdataadd1192                   = BOSdata.new()
htfadd1192.settings                 := SettingsHTFadd1192
htfadd1192.candles                  := candlesadd1192
htfadd1192.bosdata                  := bosdataadd1192
var CandleSet htfadd1193                     = CandleSet.new()
var CandleSettings SettingsHTFadd1193        = CandleSettings.new(htf='1193',htfint=1193,max_memory=3)
var Candle[] candlesadd1193                  = array.new<Candle>(0)
var BOSdata bosdataadd1193                   = BOSdata.new()
htfadd1193.settings                 := SettingsHTFadd1193
htfadd1193.candles                  := candlesadd1193
htfadd1193.bosdata                  := bosdataadd1193
var CandleSet htfadd1194                     = CandleSet.new()
var CandleSettings SettingsHTFadd1194        = CandleSettings.new(htf='1194',htfint=1194,max_memory=3)
var Candle[] candlesadd1194                  = array.new<Candle>(0)
var BOSdata bosdataadd1194                   = BOSdata.new()
htfadd1194.settings                 := SettingsHTFadd1194
htfadd1194.candles                  := candlesadd1194
htfadd1194.bosdata                  := bosdataadd1194
var CandleSet htfadd1195                     = CandleSet.new()
var CandleSettings SettingsHTFadd1195        = CandleSettings.new(htf='1195',htfint=1195,max_memory=3)
var Candle[] candlesadd1195                  = array.new<Candle>(0)
var BOSdata bosdataadd1195                   = BOSdata.new()
htfadd1195.settings                 := SettingsHTFadd1195
htfadd1195.candles                  := candlesadd1195
htfadd1195.bosdata                  := bosdataadd1195
var CandleSet htfadd1196                     = CandleSet.new()
var CandleSettings SettingsHTFadd1196        = CandleSettings.new(htf='1196',htfint=1196,max_memory=3)
var Candle[] candlesadd1196                  = array.new<Candle>(0)
var BOSdata bosdataadd1196                   = BOSdata.new()
htfadd1196.settings                 := SettingsHTFadd1196
htfadd1196.candles                  := candlesadd1196
htfadd1196.bosdata                  := bosdataadd1196
var CandleSet htfadd1197                     = CandleSet.new()
var CandleSettings SettingsHTFadd1197        = CandleSettings.new(htf='1197',htfint=1197,max_memory=3)
var Candle[] candlesadd1197                  = array.new<Candle>(0)
var BOSdata bosdataadd1197                   = BOSdata.new()
htfadd1197.settings                 := SettingsHTFadd1197
htfadd1197.candles                  := candlesadd1197
htfadd1197.bosdata                  := bosdataadd1197
var CandleSet htfadd1198                     = CandleSet.new()
var CandleSettings SettingsHTFadd1198        = CandleSettings.new(htf='1198',htfint=1198,max_memory=3)
var Candle[] candlesadd1198                  = array.new<Candle>(0)
var BOSdata bosdataadd1198                   = BOSdata.new()
htfadd1198.settings                 := SettingsHTFadd1198
htfadd1198.candles                  := candlesadd1198
htfadd1198.bosdata                  := bosdataadd1198
var CandleSet htfadd1199                     = CandleSet.new()
var CandleSettings SettingsHTFadd1199        = CandleSettings.new(htf='1199',htfint=1199,max_memory=3)
var Candle[] candlesadd1199                  = array.new<Candle>(0)
var BOSdata bosdataadd1199                   = BOSdata.new()
htfadd1199.settings                 := SettingsHTFadd1199
htfadd1199.candles                  := candlesadd1199
htfadd1199.bosdata                  := bosdataadd1199
var CandleSet htfadd1200                     = CandleSet.new()
var CandleSettings SettingsHTFadd1200        = CandleSettings.new(htf='1200',htfint=1200,max_memory=3)
var Candle[] candlesadd1200                  = array.new<Candle>(0)
var BOSdata bosdataadd1200                   = BOSdata.new()
htfadd1200.settings                 := SettingsHTFadd1200
htfadd1200.candles                  := candlesadd1200
htfadd1200.bosdata                  := bosdataadd1200
var CandleSet htfadd1201                     = CandleSet.new()
var CandleSettings SettingsHTFadd1201        = CandleSettings.new(htf='1201',htfint=1201,max_memory=3)
var Candle[] candlesadd1201                  = array.new<Candle>(0)
var BOSdata bosdataadd1201                   = BOSdata.new()
htfadd1201.settings                 := SettingsHTFadd1201
htfadd1201.candles                  := candlesadd1201
htfadd1201.bosdata                  := bosdataadd1201
var CandleSet htfadd1202                     = CandleSet.new()
var CandleSettings SettingsHTFadd1202        = CandleSettings.new(htf='1202',htfint=1202,max_memory=3)
var Candle[] candlesadd1202                  = array.new<Candle>(0)
var BOSdata bosdataadd1202                   = BOSdata.new()
htfadd1202.settings                 := SettingsHTFadd1202
htfadd1202.candles                  := candlesadd1202
htfadd1202.bosdata                  := bosdataadd1202
var CandleSet htfadd1203                     = CandleSet.new()
var CandleSettings SettingsHTFadd1203        = CandleSettings.new(htf='1203',htfint=1203,max_memory=3)
var Candle[] candlesadd1203                  = array.new<Candle>(0)
var BOSdata bosdataadd1203                   = BOSdata.new()
htfadd1203.settings                 := SettingsHTFadd1203
htfadd1203.candles                  := candlesadd1203
htfadd1203.bosdata                  := bosdataadd1203
var CandleSet htfadd1204                     = CandleSet.new()
var CandleSettings SettingsHTFadd1204        = CandleSettings.new(htf='1204',htfint=1204,max_memory=3)
var Candle[] candlesadd1204                  = array.new<Candle>(0)
var BOSdata bosdataadd1204                   = BOSdata.new()
htfadd1204.settings                 := SettingsHTFadd1204
htfadd1204.candles                  := candlesadd1204
htfadd1204.bosdata                  := bosdataadd1204
var CandleSet htfadd1205                     = CandleSet.new()
var CandleSettings SettingsHTFadd1205        = CandleSettings.new(htf='1205',htfint=1205,max_memory=3)
var Candle[] candlesadd1205                  = array.new<Candle>(0)
var BOSdata bosdataadd1205                   = BOSdata.new()
htfadd1205.settings                 := SettingsHTFadd1205
htfadd1205.candles                  := candlesadd1205
htfadd1205.bosdata                  := bosdataadd1205
var CandleSet htfadd1206                     = CandleSet.new()
var CandleSettings SettingsHTFadd1206        = CandleSettings.new(htf='1206',htfint=1206,max_memory=3)
var Candle[] candlesadd1206                  = array.new<Candle>(0)
var BOSdata bosdataadd1206                   = BOSdata.new()
htfadd1206.settings                 := SettingsHTFadd1206
htfadd1206.candles                  := candlesadd1206
htfadd1206.bosdata                  := bosdataadd1206
var CandleSet htfadd1207                     = CandleSet.new()
var CandleSettings SettingsHTFadd1207        = CandleSettings.new(htf='1207',htfint=1207,max_memory=3)
var Candle[] candlesadd1207                  = array.new<Candle>(0)
var BOSdata bosdataadd1207                   = BOSdata.new()
htfadd1207.settings                 := SettingsHTFadd1207
htfadd1207.candles                  := candlesadd1207
htfadd1207.bosdata                  := bosdataadd1207
var CandleSet htfadd1208                     = CandleSet.new()
var CandleSettings SettingsHTFadd1208        = CandleSettings.new(htf='1208',htfint=1208,max_memory=3)
var Candle[] candlesadd1208                  = array.new<Candle>(0)
var BOSdata bosdataadd1208                   = BOSdata.new()
htfadd1208.settings                 := SettingsHTFadd1208
htfadd1208.candles                  := candlesadd1208
htfadd1208.bosdata                  := bosdataadd1208
var CandleSet htfadd1209                     = CandleSet.new()
var CandleSettings SettingsHTFadd1209        = CandleSettings.new(htf='1209',htfint=1209,max_memory=3)
var Candle[] candlesadd1209                  = array.new<Candle>(0)
var BOSdata bosdataadd1209                   = BOSdata.new()
htfadd1209.settings                 := SettingsHTFadd1209
htfadd1209.candles                  := candlesadd1209
htfadd1209.bosdata                  := bosdataadd1209
var CandleSet htfadd1210                     = CandleSet.new()
var CandleSettings SettingsHTFadd1210        = CandleSettings.new(htf='1210',htfint=1210,max_memory=3)
var Candle[] candlesadd1210                  = array.new<Candle>(0)
var BOSdata bosdataadd1210                   = BOSdata.new()
htfadd1210.settings                 := SettingsHTFadd1210
htfadd1210.candles                  := candlesadd1210
htfadd1210.bosdata                  := bosdataadd1210
var CandleSet htfadd1211                     = CandleSet.new()
var CandleSettings SettingsHTFadd1211        = CandleSettings.new(htf='1211',htfint=1211,max_memory=3)
var Candle[] candlesadd1211                  = array.new<Candle>(0)
var BOSdata bosdataadd1211                   = BOSdata.new()
htfadd1211.settings                 := SettingsHTFadd1211
htfadd1211.candles                  := candlesadd1211
htfadd1211.bosdata                  := bosdataadd1211
var CandleSet htfadd1212                     = CandleSet.new()
var CandleSettings SettingsHTFadd1212        = CandleSettings.new(htf='1212',htfint=1212,max_memory=3)
var Candle[] candlesadd1212                  = array.new<Candle>(0)
var BOSdata bosdataadd1212                   = BOSdata.new()
htfadd1212.settings                 := SettingsHTFadd1212
htfadd1212.candles                  := candlesadd1212
htfadd1212.bosdata                  := bosdataadd1212
var CandleSet htfadd1213                     = CandleSet.new()
var CandleSettings SettingsHTFadd1213        = CandleSettings.new(htf='1213',htfint=1213,max_memory=3)
var Candle[] candlesadd1213                  = array.new<Candle>(0)
var BOSdata bosdataadd1213                   = BOSdata.new()
htfadd1213.settings                 := SettingsHTFadd1213
htfadd1213.candles                  := candlesadd1213
htfadd1213.bosdata                  := bosdataadd1213
var CandleSet htfadd1214                     = CandleSet.new()
var CandleSettings SettingsHTFadd1214        = CandleSettings.new(htf='1214',htfint=1214,max_memory=3)
var Candle[] candlesadd1214                  = array.new<Candle>(0)
var BOSdata bosdataadd1214                   = BOSdata.new()
htfadd1214.settings                 := SettingsHTFadd1214
htfadd1214.candles                  := candlesadd1214
htfadd1214.bosdata                  := bosdataadd1214
var CandleSet htfadd1215                     = CandleSet.new()
var CandleSettings SettingsHTFadd1215        = CandleSettings.new(htf='1215',htfint=1215,max_memory=3)
var Candle[] candlesadd1215                  = array.new<Candle>(0)
var BOSdata bosdataadd1215                   = BOSdata.new()
htfadd1215.settings                 := SettingsHTFadd1215
htfadd1215.candles                  := candlesadd1215
htfadd1215.bosdata                  := bosdataadd1215
var CandleSet htfadd1216                     = CandleSet.new()
var CandleSettings SettingsHTFadd1216        = CandleSettings.new(htf='1216',htfint=1216,max_memory=3)
var Candle[] candlesadd1216                  = array.new<Candle>(0)
var BOSdata bosdataadd1216                   = BOSdata.new()
htfadd1216.settings                 := SettingsHTFadd1216
htfadd1216.candles                  := candlesadd1216
htfadd1216.bosdata                  := bosdataadd1216
var CandleSet htfadd1217                     = CandleSet.new()
var CandleSettings SettingsHTFadd1217        = CandleSettings.new(htf='1217',htfint=1217,max_memory=3)
var Candle[] candlesadd1217                  = array.new<Candle>(0)
var BOSdata bosdataadd1217                   = BOSdata.new()
htfadd1217.settings                 := SettingsHTFadd1217
htfadd1217.candles                  := candlesadd1217
htfadd1217.bosdata                  := bosdataadd1217
var CandleSet htfadd1218                     = CandleSet.new()
var CandleSettings SettingsHTFadd1218        = CandleSettings.new(htf='1218',htfint=1218,max_memory=3)
var Candle[] candlesadd1218                  = array.new<Candle>(0)
var BOSdata bosdataadd1218                   = BOSdata.new()
htfadd1218.settings                 := SettingsHTFadd1218
htfadd1218.candles                  := candlesadd1218
htfadd1218.bosdata                  := bosdataadd1218
var CandleSet htfadd1219                     = CandleSet.new()
var CandleSettings SettingsHTFadd1219        = CandleSettings.new(htf='1219',htfint=1219,max_memory=3)
var Candle[] candlesadd1219                  = array.new<Candle>(0)
var BOSdata bosdataadd1219                   = BOSdata.new()
htfadd1219.settings                 := SettingsHTFadd1219
htfadd1219.candles                  := candlesadd1219
htfadd1219.bosdata                  := bosdataadd1219
var CandleSet htfadd1220                     = CandleSet.new()
var CandleSettings SettingsHTFadd1220        = CandleSettings.new(htf='1220',htfint=1220,max_memory=3)
var Candle[] candlesadd1220                  = array.new<Candle>(0)
var BOSdata bosdataadd1220                   = BOSdata.new()
htfadd1220.settings                 := SettingsHTFadd1220
htfadd1220.candles                  := candlesadd1220
htfadd1220.bosdata                  := bosdataadd1220
var CandleSet htfadd1221                     = CandleSet.new()
var CandleSettings SettingsHTFadd1221        = CandleSettings.new(htf='1221',htfint=1221,max_memory=3)
var Candle[] candlesadd1221                  = array.new<Candle>(0)
var BOSdata bosdataadd1221                   = BOSdata.new()
htfadd1221.settings                 := SettingsHTFadd1221
htfadd1221.candles                  := candlesadd1221
htfadd1221.bosdata                  := bosdataadd1221
var CandleSet htfadd1222                     = CandleSet.new()
var CandleSettings SettingsHTFadd1222        = CandleSettings.new(htf='1222',htfint=1222,max_memory=3)
var Candle[] candlesadd1222                  = array.new<Candle>(0)
var BOSdata bosdataadd1222                   = BOSdata.new()
htfadd1222.settings                 := SettingsHTFadd1222
htfadd1222.candles                  := candlesadd1222
htfadd1222.bosdata                  := bosdataadd1222
var CandleSet htfadd1223                     = CandleSet.new()
var CandleSettings SettingsHTFadd1223        = CandleSettings.new(htf='1223',htfint=1223,max_memory=3)
var Candle[] candlesadd1223                  = array.new<Candle>(0)
var BOSdata bosdataadd1223                   = BOSdata.new()
htfadd1223.settings                 := SettingsHTFadd1223
htfadd1223.candles                  := candlesadd1223
htfadd1223.bosdata                  := bosdataadd1223
var CandleSet htfadd1224                     = CandleSet.new()
var CandleSettings SettingsHTFadd1224        = CandleSettings.new(htf='1224',htfint=1224,max_memory=3)
var Candle[] candlesadd1224                  = array.new<Candle>(0)
var BOSdata bosdataadd1224                   = BOSdata.new()
htfadd1224.settings                 := SettingsHTFadd1224
htfadd1224.candles                  := candlesadd1224
htfadd1224.bosdata                  := bosdataadd1224
var CandleSet htfadd1225                     = CandleSet.new()
var CandleSettings SettingsHTFadd1225        = CandleSettings.new(htf='1225',htfint=1225,max_memory=3)
var Candle[] candlesadd1225                  = array.new<Candle>(0)
var BOSdata bosdataadd1225                   = BOSdata.new()
htfadd1225.settings                 := SettingsHTFadd1225
htfadd1225.candles                  := candlesadd1225
htfadd1225.bosdata                  := bosdataadd1225
var CandleSet htfadd1226                     = CandleSet.new()
var CandleSettings SettingsHTFadd1226        = CandleSettings.new(htf='1226',htfint=1226,max_memory=3)
var Candle[] candlesadd1226                  = array.new<Candle>(0)
var BOSdata bosdataadd1226                   = BOSdata.new()
htfadd1226.settings                 := SettingsHTFadd1226
htfadd1226.candles                  := candlesadd1226
htfadd1226.bosdata                  := bosdataadd1226
var CandleSet htfadd1227                     = CandleSet.new()
var CandleSettings SettingsHTFadd1227        = CandleSettings.new(htf='1227',htfint=1227,max_memory=3)
var Candle[] candlesadd1227                  = array.new<Candle>(0)
var BOSdata bosdataadd1227                   = BOSdata.new()
htfadd1227.settings                 := SettingsHTFadd1227
htfadd1227.candles                  := candlesadd1227
htfadd1227.bosdata                  := bosdataadd1227
var CandleSet htfadd1228                     = CandleSet.new()
var CandleSettings SettingsHTFadd1228        = CandleSettings.new(htf='1228',htfint=1228,max_memory=3)
var Candle[] candlesadd1228                  = array.new<Candle>(0)
var BOSdata bosdataadd1228                   = BOSdata.new()
htfadd1228.settings                 := SettingsHTFadd1228
htfadd1228.candles                  := candlesadd1228
htfadd1228.bosdata                  := bosdataadd1228
var CandleSet htfadd1229                     = CandleSet.new()
var CandleSettings SettingsHTFadd1229        = CandleSettings.new(htf='1229',htfint=1229,max_memory=3)
var Candle[] candlesadd1229                  = array.new<Candle>(0)
var BOSdata bosdataadd1229                   = BOSdata.new()
htfadd1229.settings                 := SettingsHTFadd1229
htfadd1229.candles                  := candlesadd1229
htfadd1229.bosdata                  := bosdataadd1229
var CandleSet htfadd1230                     = CandleSet.new()
var CandleSettings SettingsHTFadd1230        = CandleSettings.new(htf='1230',htfint=1230,max_memory=3)
var Candle[] candlesadd1230                  = array.new<Candle>(0)
var BOSdata bosdataadd1230                   = BOSdata.new()
htfadd1230.settings                 := SettingsHTFadd1230
htfadd1230.candles                  := candlesadd1230
htfadd1230.bosdata                  := bosdataadd1230
var CandleSet htfadd1231                     = CandleSet.new()
var CandleSettings SettingsHTFadd1231        = CandleSettings.new(htf='1231',htfint=1231,max_memory=3)
var Candle[] candlesadd1231                  = array.new<Candle>(0)
var BOSdata bosdataadd1231                   = BOSdata.new()
htfadd1231.settings                 := SettingsHTFadd1231
htfadd1231.candles                  := candlesadd1231
htfadd1231.bosdata                  := bosdataadd1231
var CandleSet htfadd1232                     = CandleSet.new()
var CandleSettings SettingsHTFadd1232        = CandleSettings.new(htf='1232',htfint=1232,max_memory=3)
var Candle[] candlesadd1232                  = array.new<Candle>(0)
var BOSdata bosdataadd1232                   = BOSdata.new()
htfadd1232.settings                 := SettingsHTFadd1232
htfadd1232.candles                  := candlesadd1232
htfadd1232.bosdata                  := bosdataadd1232
var CandleSet htfadd1233                     = CandleSet.new()
var CandleSettings SettingsHTFadd1233        = CandleSettings.new(htf='1233',htfint=1233,max_memory=3)
var Candle[] candlesadd1233                  = array.new<Candle>(0)
var BOSdata bosdataadd1233                   = BOSdata.new()
htfadd1233.settings                 := SettingsHTFadd1233
htfadd1233.candles                  := candlesadd1233
htfadd1233.bosdata                  := bosdataadd1233
var CandleSet htfadd1234                     = CandleSet.new()
var CandleSettings SettingsHTFadd1234        = CandleSettings.new(htf='1234',htfint=1234,max_memory=3)
var Candle[] candlesadd1234                  = array.new<Candle>(0)
var BOSdata bosdataadd1234                   = BOSdata.new()
htfadd1234.settings                 := SettingsHTFadd1234
htfadd1234.candles                  := candlesadd1234
htfadd1234.bosdata                  := bosdataadd1234
var CandleSet htfadd1235                     = CandleSet.new()
var CandleSettings SettingsHTFadd1235        = CandleSettings.new(htf='1235',htfint=1235,max_memory=3)
var Candle[] candlesadd1235                  = array.new<Candle>(0)
var BOSdata bosdataadd1235                   = BOSdata.new()
htfadd1235.settings                 := SettingsHTFadd1235
htfadd1235.candles                  := candlesadd1235
htfadd1235.bosdata                  := bosdataadd1235
var CandleSet htfadd1236                     = CandleSet.new()
var CandleSettings SettingsHTFadd1236        = CandleSettings.new(htf='1236',htfint=1236,max_memory=3)
var Candle[] candlesadd1236                  = array.new<Candle>(0)
var BOSdata bosdataadd1236                   = BOSdata.new()
htfadd1236.settings                 := SettingsHTFadd1236
htfadd1236.candles                  := candlesadd1236
htfadd1236.bosdata                  := bosdataadd1236
var CandleSet htfadd1237                     = CandleSet.new()
var CandleSettings SettingsHTFadd1237        = CandleSettings.new(htf='1237',htfint=1237,max_memory=3)
var Candle[] candlesadd1237                  = array.new<Candle>(0)
var BOSdata bosdataadd1237                   = BOSdata.new()
htfadd1237.settings                 := SettingsHTFadd1237
htfadd1237.candles                  := candlesadd1237
htfadd1237.bosdata                  := bosdataadd1237
var CandleSet htfadd1238                     = CandleSet.new()
var CandleSettings SettingsHTFadd1238        = CandleSettings.new(htf='1238',htfint=1238,max_memory=3)
var Candle[] candlesadd1238                  = array.new<Candle>(0)
var BOSdata bosdataadd1238                   = BOSdata.new()
htfadd1238.settings                 := SettingsHTFadd1238
htfadd1238.candles                  := candlesadd1238
htfadd1238.bosdata                  := bosdataadd1238
var CandleSet htfadd1239                     = CandleSet.new()
var CandleSettings SettingsHTFadd1239        = CandleSettings.new(htf='1239',htfint=1239,max_memory=3)
var Candle[] candlesadd1239                  = array.new<Candle>(0)
var BOSdata bosdataadd1239                   = BOSdata.new()
htfadd1239.settings                 := SettingsHTFadd1239
htfadd1239.candles                  := candlesadd1239
htfadd1239.bosdata                  := bosdataadd1239
var CandleSet htfadd1240                     = CandleSet.new()
var CandleSettings SettingsHTFadd1240        = CandleSettings.new(htf='1240',htfint=1240,max_memory=3)
var Candle[] candlesadd1240                  = array.new<Candle>(0)
var BOSdata bosdataadd1240                   = BOSdata.new()
htfadd1240.settings                 := SettingsHTFadd1240
htfadd1240.candles                  := candlesadd1240
htfadd1240.bosdata                  := bosdataadd1240
var CandleSet htfadd1241                     = CandleSet.new()
var CandleSettings SettingsHTFadd1241        = CandleSettings.new(htf='1241',htfint=1241,max_memory=3)
var Candle[] candlesadd1241                  = array.new<Candle>(0)
var BOSdata bosdataadd1241                   = BOSdata.new()
htfadd1241.settings                 := SettingsHTFadd1241
htfadd1241.candles                  := candlesadd1241
htfadd1241.bosdata                  := bosdataadd1241
var CandleSet htfadd1242                     = CandleSet.new()
var CandleSettings SettingsHTFadd1242        = CandleSettings.new(htf='1242',htfint=1242,max_memory=3)
var Candle[] candlesadd1242                  = array.new<Candle>(0)
var BOSdata bosdataadd1242                   = BOSdata.new()
htfadd1242.settings                 := SettingsHTFadd1242
htfadd1242.candles                  := candlesadd1242
htfadd1242.bosdata                  := bosdataadd1242
var CandleSet htfadd1243                     = CandleSet.new()
var CandleSettings SettingsHTFadd1243        = CandleSettings.new(htf='1243',htfint=1243,max_memory=3)
var Candle[] candlesadd1243                  = array.new<Candle>(0)
var BOSdata bosdataadd1243                   = BOSdata.new()
htfadd1243.settings                 := SettingsHTFadd1243
htfadd1243.candles                  := candlesadd1243
htfadd1243.bosdata                  := bosdataadd1243
var CandleSet htfadd1244                     = CandleSet.new()
var CandleSettings SettingsHTFadd1244        = CandleSettings.new(htf='1244',htfint=1244,max_memory=3)
var Candle[] candlesadd1244                  = array.new<Candle>(0)
var BOSdata bosdataadd1244                   = BOSdata.new()
htfadd1244.settings                 := SettingsHTFadd1244
htfadd1244.candles                  := candlesadd1244
htfadd1244.bosdata                  := bosdataadd1244
var CandleSet htfadd1245                     = CandleSet.new()
var CandleSettings SettingsHTFadd1245        = CandleSettings.new(htf='1245',htfint=1245,max_memory=3)
var Candle[] candlesadd1245                  = array.new<Candle>(0)
var BOSdata bosdataadd1245                   = BOSdata.new()
htfadd1245.settings                 := SettingsHTFadd1245
htfadd1245.candles                  := candlesadd1245
htfadd1245.bosdata                  := bosdataadd1245
var CandleSet htfadd1246                     = CandleSet.new()
var CandleSettings SettingsHTFadd1246        = CandleSettings.new(htf='1246',htfint=1246,max_memory=3)
var Candle[] candlesadd1246                  = array.new<Candle>(0)
var BOSdata bosdataadd1246                   = BOSdata.new()
htfadd1246.settings                 := SettingsHTFadd1246
htfadd1246.candles                  := candlesadd1246
htfadd1246.bosdata                  := bosdataadd1246
var CandleSet htfadd1247                     = CandleSet.new()
var CandleSettings SettingsHTFadd1247        = CandleSettings.new(htf='1247',htfint=1247,max_memory=3)
var Candle[] candlesadd1247                  = array.new<Candle>(0)
var BOSdata bosdataadd1247                   = BOSdata.new()
htfadd1247.settings                 := SettingsHTFadd1247
htfadd1247.candles                  := candlesadd1247
htfadd1247.bosdata                  := bosdataadd1247
var CandleSet htfadd1248                     = CandleSet.new()
var CandleSettings SettingsHTFadd1248        = CandleSettings.new(htf='1248',htfint=1248,max_memory=3)
var Candle[] candlesadd1248                  = array.new<Candle>(0)
var BOSdata bosdataadd1248                   = BOSdata.new()
htfadd1248.settings                 := SettingsHTFadd1248
htfadd1248.candles                  := candlesadd1248
htfadd1248.bosdata                  := bosdataadd1248
var CandleSet htfadd1249                     = CandleSet.new()
var CandleSettings SettingsHTFadd1249        = CandleSettings.new(htf='1249',htfint=1249,max_memory=3)
var Candle[] candlesadd1249                  = array.new<Candle>(0)
var BOSdata bosdataadd1249                   = BOSdata.new()
htfadd1249.settings                 := SettingsHTFadd1249
htfadd1249.candles                  := candlesadd1249
htfadd1249.bosdata                  := bosdataadd1249
var CandleSet htfadd1250                     = CandleSet.new()
var CandleSettings SettingsHTFadd1250        = CandleSettings.new(htf='1250',htfint=1250,max_memory=3)
var Candle[] candlesadd1250                  = array.new<Candle>(0)
var BOSdata bosdataadd1250                   = BOSdata.new()
htfadd1250.settings                 := SettingsHTFadd1250
htfadd1250.candles                  := candlesadd1250
htfadd1250.bosdata                  := bosdataadd1250
var CandleSet htfadd1251                     = CandleSet.new()
var CandleSettings SettingsHTFadd1251        = CandleSettings.new(htf='1251',htfint=1251,max_memory=3)
var Candle[] candlesadd1251                  = array.new<Candle>(0)
var BOSdata bosdataadd1251                   = BOSdata.new()
htfadd1251.settings                 := SettingsHTFadd1251
htfadd1251.candles                  := candlesadd1251
htfadd1251.bosdata                  := bosdataadd1251
var CandleSet htfadd1252                     = CandleSet.new()
var CandleSettings SettingsHTFadd1252        = CandleSettings.new(htf='1252',htfint=1252,max_memory=3)
var Candle[] candlesadd1252                  = array.new<Candle>(0)
var BOSdata bosdataadd1252                   = BOSdata.new()
htfadd1252.settings                 := SettingsHTFadd1252
htfadd1252.candles                  := candlesadd1252
htfadd1252.bosdata                  := bosdataadd1252
var CandleSet htfadd1253                     = CandleSet.new()
var CandleSettings SettingsHTFadd1253        = CandleSettings.new(htf='1253',htfint=1253,max_memory=3)
var Candle[] candlesadd1253                  = array.new<Candle>(0)
var BOSdata bosdataadd1253                   = BOSdata.new()
htfadd1253.settings                 := SettingsHTFadd1253
htfadd1253.candles                  := candlesadd1253
htfadd1253.bosdata                  := bosdataadd1253
var CandleSet htfadd1254                     = CandleSet.new()
var CandleSettings SettingsHTFadd1254        = CandleSettings.new(htf='1254',htfint=1254,max_memory=3)
var Candle[] candlesadd1254                  = array.new<Candle>(0)
var BOSdata bosdataadd1254                   = BOSdata.new()
htfadd1254.settings                 := SettingsHTFadd1254
htfadd1254.candles                  := candlesadd1254
htfadd1254.bosdata                  := bosdataadd1254
var CandleSet htfadd1255                     = CandleSet.new()
var CandleSettings SettingsHTFadd1255        = CandleSettings.new(htf='1255',htfint=1255,max_memory=3)
var Candle[] candlesadd1255                  = array.new<Candle>(0)
var BOSdata bosdataadd1255                   = BOSdata.new()
htfadd1255.settings                 := SettingsHTFadd1255
htfadd1255.candles                  := candlesadd1255
htfadd1255.bosdata                  := bosdataadd1255
var CandleSet htfadd1256                     = CandleSet.new()
var CandleSettings SettingsHTFadd1256        = CandleSettings.new(htf='1256',htfint=1256,max_memory=3)
var Candle[] candlesadd1256                  = array.new<Candle>(0)
var BOSdata bosdataadd1256                   = BOSdata.new()
htfadd1256.settings                 := SettingsHTFadd1256
htfadd1256.candles                  := candlesadd1256
htfadd1256.bosdata                  := bosdataadd1256
var CandleSet htfadd1257                     = CandleSet.new()
var CandleSettings SettingsHTFadd1257        = CandleSettings.new(htf='1257',htfint=1257,max_memory=3)
var Candle[] candlesadd1257                  = array.new<Candle>(0)
var BOSdata bosdataadd1257                   = BOSdata.new()
htfadd1257.settings                 := SettingsHTFadd1257
htfadd1257.candles                  := candlesadd1257
htfadd1257.bosdata                  := bosdataadd1257
var CandleSet htfadd1258                     = CandleSet.new()
var CandleSettings SettingsHTFadd1258        = CandleSettings.new(htf='1258',htfint=1258,max_memory=3)
var Candle[] candlesadd1258                  = array.new<Candle>(0)
var BOSdata bosdataadd1258                   = BOSdata.new()
htfadd1258.settings                 := SettingsHTFadd1258
htfadd1258.candles                  := candlesadd1258
htfadd1258.bosdata                  := bosdataadd1258
var CandleSet htfadd1259                     = CandleSet.new()
var CandleSettings SettingsHTFadd1259        = CandleSettings.new(htf='1259',htfint=1259,max_memory=3)
var Candle[] candlesadd1259                  = array.new<Candle>(0)
var BOSdata bosdataadd1259                   = BOSdata.new()
htfadd1259.settings                 := SettingsHTFadd1259
htfadd1259.candles                  := candlesadd1259
htfadd1259.bosdata                  := bosdataadd1259
var CandleSet htfadd1260                     = CandleSet.new()
var CandleSettings SettingsHTFadd1260        = CandleSettings.new(htf='1260',htfint=1260,max_memory=3)
var Candle[] candlesadd1260                  = array.new<Candle>(0)
var BOSdata bosdataadd1260                   = BOSdata.new()
htfadd1260.settings                 := SettingsHTFadd1260
htfadd1260.candles                  := candlesadd1260
htfadd1260.bosdata                  := bosdataadd1260

htfadd1170.Monitor().BOSJudge()
htfadd1171.Monitor().BOSJudge()
htfadd1172.Monitor().BOSJudge()
htfadd1173.Monitor().BOSJudge()
htfadd1174.Monitor().BOSJudge()
htfadd1175.Monitor().BOSJudge()
htfadd1176.Monitor().BOSJudge()
htfadd1177.Monitor().BOSJudge()
htfadd1178.Monitor().BOSJudge()
htfadd1179.Monitor().BOSJudge()
htfadd1180.Monitor().BOSJudge()
htfadd1181.Monitor().BOSJudge()
htfadd1182.Monitor().BOSJudge()
htfadd1183.Monitor().BOSJudge()
htfadd1184.Monitor().BOSJudge()
htfadd1185.Monitor().BOSJudge()
htfadd1186.Monitor().BOSJudge()
htfadd1187.Monitor().BOSJudge()
htfadd1188.Monitor().BOSJudge()
htfadd1189.Monitor().BOSJudge()
htfadd1190.Monitor().BOSJudge()
htfadd1191.Monitor().BOSJudge()
htfadd1192.Monitor().BOSJudge()
htfadd1193.Monitor().BOSJudge()
htfadd1194.Monitor().BOSJudge()
htfadd1195.Monitor().BOSJudge()
htfadd1196.Monitor().BOSJudge()
htfadd1197.Monitor().BOSJudge()
htfadd1198.Monitor().BOSJudge()
htfadd1199.Monitor().BOSJudge()
htfadd1200.Monitor().BOSJudge()
htfadd1201.Monitor().BOSJudge()
htfadd1202.Monitor().BOSJudge()
htfadd1203.Monitor().BOSJudge()
htfadd1204.Monitor().BOSJudge()
htfadd1205.Monitor().BOSJudge()
htfadd1206.Monitor().BOSJudge()
htfadd1207.Monitor().BOSJudge()
htfadd1208.Monitor().BOSJudge()
htfadd1209.Monitor().BOSJudge()
htfadd1210.Monitor().BOSJudge()
htfadd1211.Monitor().BOSJudge()
htfadd1212.Monitor().BOSJudge()
htfadd1213.Monitor().BOSJudge()
htfadd1214.Monitor().BOSJudge()
htfadd1215.Monitor().BOSJudge()
htfadd1216.Monitor().BOSJudge()
htfadd1217.Monitor().BOSJudge()
htfadd1218.Monitor().BOSJudge()
htfadd1219.Monitor().BOSJudge()
htfadd1220.Monitor().BOSJudge()
htfadd1221.Monitor().BOSJudge()
htfadd1222.Monitor().BOSJudge()
htfadd1223.Monitor().BOSJudge()
htfadd1224.Monitor().BOSJudge()
htfadd1225.Monitor().BOSJudge()
htfadd1226.Monitor().BOSJudge()
htfadd1227.Monitor().BOSJudge()
htfadd1228.Monitor().BOSJudge()
htfadd1229.Monitor().BOSJudge()
htfadd1230.Monitor().BOSJudge()
htfadd1231.Monitor().BOSJudge()
htfadd1232.Monitor().BOSJudge()
htfadd1233.Monitor().BOSJudge()
htfadd1234.Monitor().BOSJudge()
htfadd1235.Monitor().BOSJudge()
htfadd1236.Monitor().BOSJudge()
htfadd1237.Monitor().BOSJudge()
htfadd1238.Monitor().BOSJudge()
htfadd1239.Monitor().BOSJudge()
htfadd1240.Monitor().BOSJudge()
htfadd1241.Monitor().BOSJudge()
htfadd1242.Monitor().BOSJudge()
htfadd1243.Monitor().BOSJudge()
htfadd1244.Monitor().BOSJudge()
htfadd1245.Monitor().BOSJudge()
htfadd1246.Monitor().BOSJudge()
htfadd1247.Monitor().BOSJudge()
htfadd1248.Monitor().BOSJudge()
htfadd1249.Monitor().BOSJudge()
htfadd1250.Monitor().BOSJudge()
htfadd1251.Monitor().BOSJudge()
htfadd1252.Monitor().BOSJudge()
htfadd1253.Monitor().BOSJudge()
htfadd1254.Monitor().BOSJudge()
htfadd1255.Monitor().BOSJudge()
htfadd1256.Monitor().BOSJudge()
htfadd1257.Monitor().BOSJudge()
htfadd1258.Monitor().BOSJudge()
htfadd1259.Monitor().BOSJudge()
htfadd1260.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfadd1170)
    LowestsbuSet(lowestsbu, htfadd1170)
    HighestsbdSet(highestsbd, htfadd1171)
    LowestsbuSet(lowestsbu, htfadd1171)
    HighestsbdSet(highestsbd, htfadd1172)
    LowestsbuSet(lowestsbu, htfadd1172)
    HighestsbdSet(highestsbd, htfadd1173)
    LowestsbuSet(lowestsbu, htfadd1173)
    HighestsbdSet(highestsbd, htfadd1174)
    LowestsbuSet(lowestsbu, htfadd1174)
    HighestsbdSet(highestsbd, htfadd1175)
    LowestsbuSet(lowestsbu, htfadd1175)
    HighestsbdSet(highestsbd, htfadd1176)
    LowestsbuSet(lowestsbu, htfadd1176)
    HighestsbdSet(highestsbd, htfadd1177)
    LowestsbuSet(lowestsbu, htfadd1177)
    HighestsbdSet(highestsbd, htfadd1178)
    LowestsbuSet(lowestsbu, htfadd1178)
    HighestsbdSet(highestsbd, htfadd1179)
    LowestsbuSet(lowestsbu, htfadd1179)
    HighestsbdSet(highestsbd, htfadd1180)
    LowestsbuSet(lowestsbu, htfadd1180)
    HighestsbdSet(highestsbd, htfadd1181)
    LowestsbuSet(lowestsbu, htfadd1181)
    HighestsbdSet(highestsbd, htfadd1182)
    LowestsbuSet(lowestsbu, htfadd1182)
    HighestsbdSet(highestsbd, htfadd1183)
    LowestsbuSet(lowestsbu, htfadd1183)
    HighestsbdSet(highestsbd, htfadd1184)
    LowestsbuSet(lowestsbu, htfadd1184)
    HighestsbdSet(highestsbd, htfadd1185)
    LowestsbuSet(lowestsbu, htfadd1185)
    HighestsbdSet(highestsbd, htfadd1186)
    LowestsbuSet(lowestsbu, htfadd1186)
    HighestsbdSet(highestsbd, htfadd1187)
    LowestsbuSet(lowestsbu, htfadd1187)
    HighestsbdSet(highestsbd, htfadd1188)
    LowestsbuSet(lowestsbu, htfadd1188)
    HighestsbdSet(highestsbd, htfadd1189)
    LowestsbuSet(lowestsbu, htfadd1189)
    HighestsbdSet(highestsbd, htfadd1190)
    LowestsbuSet(lowestsbu, htfadd1190)
    HighestsbdSet(highestsbd, htfadd1191)
    LowestsbuSet(lowestsbu, htfadd1191)
    HighestsbdSet(highestsbd, htfadd1192)
    LowestsbuSet(lowestsbu, htfadd1192)
    HighestsbdSet(highestsbd, htfadd1193)
    LowestsbuSet(lowestsbu, htfadd1193)
    HighestsbdSet(highestsbd, htfadd1194)
    LowestsbuSet(lowestsbu, htfadd1194)
    HighestsbdSet(highestsbd, htfadd1195)
    LowestsbuSet(lowestsbu, htfadd1195)
    HighestsbdSet(highestsbd, htfadd1196)
    LowestsbuSet(lowestsbu, htfadd1196)
    HighestsbdSet(highestsbd, htfadd1197)
    LowestsbuSet(lowestsbu, htfadd1197)
    HighestsbdSet(highestsbd, htfadd1198)
    LowestsbuSet(lowestsbu, htfadd1198)
    HighestsbdSet(highestsbd, htfadd1199)
    LowestsbuSet(lowestsbu, htfadd1199)
    HighestsbdSet(highestsbd, htfadd1200)
    LowestsbuSet(lowestsbu, htfadd1200)
    HighestsbdSet(highestsbd, htfadd1201)
    LowestsbuSet(lowestsbu, htfadd1201)
    HighestsbdSet(highestsbd, htfadd1202)
    LowestsbuSet(lowestsbu, htfadd1202)
    HighestsbdSet(highestsbd, htfadd1203)
    LowestsbuSet(lowestsbu, htfadd1203)
    HighestsbdSet(highestsbd, htfadd1204)
    LowestsbuSet(lowestsbu, htfadd1204)
    HighestsbdSet(highestsbd, htfadd1205)
    LowestsbuSet(lowestsbu, htfadd1205)
    HighestsbdSet(highestsbd, htfadd1206)
    LowestsbuSet(lowestsbu, htfadd1206)
    HighestsbdSet(highestsbd, htfadd1207)
    LowestsbuSet(lowestsbu, htfadd1207)
    HighestsbdSet(highestsbd, htfadd1208)
    LowestsbuSet(lowestsbu, htfadd1208)
    HighestsbdSet(highestsbd, htfadd1209)
    LowestsbuSet(lowestsbu, htfadd1209)
    HighestsbdSet(highestsbd, htfadd1210)
    LowestsbuSet(lowestsbu, htfadd1210)
    HighestsbdSet(highestsbd, htfadd1211)
    LowestsbuSet(lowestsbu, htfadd1211)
    HighestsbdSet(highestsbd, htfadd1212)
    LowestsbuSet(lowestsbu, htfadd1212)
    HighestsbdSet(highestsbd, htfadd1213)
    LowestsbuSet(lowestsbu, htfadd1213)
    HighestsbdSet(highestsbd, htfadd1214)
    LowestsbuSet(lowestsbu, htfadd1214)
    HighestsbdSet(highestsbd, htfadd1215)
    LowestsbuSet(lowestsbu, htfadd1215)
    HighestsbdSet(highestsbd, htfadd1216)
    LowestsbuSet(lowestsbu, htfadd1216)
    HighestsbdSet(highestsbd, htfadd1217)
    LowestsbuSet(lowestsbu, htfadd1217)
    HighestsbdSet(highestsbd, htfadd1218)
    LowestsbuSet(lowestsbu, htfadd1218)
    HighestsbdSet(highestsbd, htfadd1219)
    LowestsbuSet(lowestsbu, htfadd1219)
    HighestsbdSet(highestsbd, htfadd1220)
    LowestsbuSet(lowestsbu, htfadd1220)
    HighestsbdSet(highestsbd, htfadd1221)
    LowestsbuSet(lowestsbu, htfadd1221)
    HighestsbdSet(highestsbd, htfadd1222)
    LowestsbuSet(lowestsbu, htfadd1222)
    HighestsbdSet(highestsbd, htfadd1223)
    LowestsbuSet(lowestsbu, htfadd1223)
    HighestsbdSet(highestsbd, htfadd1224)
    LowestsbuSet(lowestsbu, htfadd1224)
    HighestsbdSet(highestsbd, htfadd1225)
    LowestsbuSet(lowestsbu, htfadd1225)
    HighestsbdSet(highestsbd, htfadd1226)
    LowestsbuSet(lowestsbu, htfadd1226)
    HighestsbdSet(highestsbd, htfadd1227)
    LowestsbuSet(lowestsbu, htfadd1227)
    HighestsbdSet(highestsbd, htfadd1228)
    LowestsbuSet(lowestsbu, htfadd1228)
    HighestsbdSet(highestsbd, htfadd1229)
    LowestsbuSet(lowestsbu, htfadd1229)
    HighestsbdSet(highestsbd, htfadd1230)
    LowestsbuSet(lowestsbu, htfadd1230)
    HighestsbdSet(highestsbd, htfadd1231)
    LowestsbuSet(lowestsbu, htfadd1231)
    HighestsbdSet(highestsbd, htfadd1232)
    LowestsbuSet(lowestsbu, htfadd1232)
    HighestsbdSet(highestsbd, htfadd1233)
    LowestsbuSet(lowestsbu, htfadd1233)
    HighestsbdSet(highestsbd, htfadd1234)
    LowestsbuSet(lowestsbu, htfadd1234)
    HighestsbdSet(highestsbd, htfadd1235)
    LowestsbuSet(lowestsbu, htfadd1235)
    HighestsbdSet(highestsbd, htfadd1236)
    LowestsbuSet(lowestsbu, htfadd1236)
    HighestsbdSet(highestsbd, htfadd1237)
    LowestsbuSet(lowestsbu, htfadd1237)
    HighestsbdSet(highestsbd, htfadd1238)
    LowestsbuSet(lowestsbu, htfadd1238)
    HighestsbdSet(highestsbd, htfadd1239)
    LowestsbuSet(lowestsbu, htfadd1239)
    HighestsbdSet(highestsbd, htfadd1240)
    LowestsbuSet(lowestsbu, htfadd1240)
    HighestsbdSet(highestsbd, htfadd1241)
    LowestsbuSet(lowestsbu, htfadd1241)
    HighestsbdSet(highestsbd, htfadd1242)
    LowestsbuSet(lowestsbu, htfadd1242)
    HighestsbdSet(highestsbd, htfadd1243)
    LowestsbuSet(lowestsbu, htfadd1243)
    HighestsbdSet(highestsbd, htfadd1244)
    LowestsbuSet(lowestsbu, htfadd1244)
    HighestsbdSet(highestsbd, htfadd1245)
    LowestsbuSet(lowestsbu, htfadd1245)
    HighestsbdSet(highestsbd, htfadd1246)
    LowestsbuSet(lowestsbu, htfadd1246)
    HighestsbdSet(highestsbd, htfadd1247)
    LowestsbuSet(lowestsbu, htfadd1247)
    HighestsbdSet(highestsbd, htfadd1248)
    LowestsbuSet(lowestsbu, htfadd1248)
    HighestsbdSet(highestsbd, htfadd1249)
    LowestsbuSet(lowestsbu, htfadd1249)
    HighestsbdSet(highestsbd, htfadd1250)
    LowestsbuSet(lowestsbu, htfadd1250)
    HighestsbdSet(highestsbd, htfadd1251)
    LowestsbuSet(lowestsbu, htfadd1251)
    HighestsbdSet(highestsbd, htfadd1252)
    LowestsbuSet(lowestsbu, htfadd1252)
    HighestsbdSet(highestsbd, htfadd1253)
    LowestsbuSet(lowestsbu, htfadd1253)
    HighestsbdSet(highestsbd, htfadd1254)
    LowestsbuSet(lowestsbu, htfadd1254)
    HighestsbdSet(highestsbd, htfadd1255)
    LowestsbuSet(lowestsbu, htfadd1255)
    HighestsbdSet(highestsbd, htfadd1256)
    LowestsbuSet(lowestsbu, htfadd1256)
    HighestsbdSet(highestsbd, htfadd1257)
    LowestsbuSet(lowestsbu, htfadd1257)
    HighestsbdSet(highestsbd, htfadd1258)
    LowestsbuSet(lowestsbu, htfadd1258)
    HighestsbdSet(highestsbd, htfadd1259)
    LowestsbuSet(lowestsbu, htfadd1259)
    HighestsbdSet(highestsbd, htfadd1260)
    LowestsbuSet(lowestsbu, htfadd1260)

    htfshadow.Shadowing(htfadd1170).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1171).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1172).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1173).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1174).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1175).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1176).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1177).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1178).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1179).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1180).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1181).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1182).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1183).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1184).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1185).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1186).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1187).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1188).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1189).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1190).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1191).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1192).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1193).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1194).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1195).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1196).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1197).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1198).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1199).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1200).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1201).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1202).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1203).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1204).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1205).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1206).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1207).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1208).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1209).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1210).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1211).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1212).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1213).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1214).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1215).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1216).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1217).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1218).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1219).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1220).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1221).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1222).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1223).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1224).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1225).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1226).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1227).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1228).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1229).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1230).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1231).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1232).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1233).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1234).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1235).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1236).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1237).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1238).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1239).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1240).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1241).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1242).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1243).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1244).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1245).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1246).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1247).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1248).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1249).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1250).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1251).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1252).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1253).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1254).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1255).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1256).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1257).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1258).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1259).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfadd1260).Monitor_Est().BOSJudge()
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


