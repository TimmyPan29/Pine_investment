//+-----filter the multiline after the timing and show that on figure -----+//
// © T.PanShuai29
//@version=5
indicator("1440add", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)

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
    bool            nowclosebool = false

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
var ValueDecisionReg highestsbd  = ValueDecisionReg.new(vtext="highestsbd: ", value=0, vdecisionname="HighestsbdSet")
var ValueDecisionReg lowestsbu  = ValueDecisionReg.new(vtext= "lowestsbu: ", vdecisionname="LowestsbuSet" , value=99999999)
var ValueDecisionReg estmaxsbd  = ValueDecisionReg.new(vdecisionname="estmaxsbd", value=0, vtext="estmaxsbd: ")
var ValueDecisionReg estminsbu  = ValueDecisionReg.new(vdecisionname="estminsbu", value=99999999, vtext="estminsbu: ")


//+---------------ValueDeicsionEND------------------+//

//+----------------------------------------+//
//+-settings    

//+----------------------------------------+//

settings.add_show          := input.bool(true, "add function enable?       ", inline="add enable")
settings.max_sets          := input.int(4, "Limit to next HTFs only", minval=1, maxval=4)

settings.offset            := input.int(10, "padding from current candles", minval = 1)
settings.text_buffer       := input.int(10, "space between text features", minval = 1, maxval = 10)
// sbu sbd, period, date happen, remain time, price, line color

settings.sbu_label_color   := input.color(color.new(color.black, 10), "sbu_label", inline='11')
settings.sbu_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.sbd_label_color   := input.color(color.new(color.black, 10), "sbd_label", inline='11')
settings.sbd_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.htf_label_color   := input.color(color.new(color.black, 10), "htf_label", inline='21')
settings.htf_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.date_label_color  := input.color(color.new(color.black, 10), "date_label", inline='21')
settings.date_label_size   := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.htf_timer_color   := input.color(color.new(color.black, 10), "htf_timer", inline='31')
settings.htf_timer_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

settings.price_label_color := input.color(color.new(color.black, 10), "price_label", inline='31')
settings.price_label_size  := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

//+----------------------------------------+//
//+- Variables   

//+----------------------------------------+//
Helper    helper        = Helper.new()

color color_transparent = #ffffff00
var index               = 0  //不要動
var InitialPeriod       = 1  //你想從第幾分鐘的週期開始比?
var totaladdPeriod      = 20 //
var Interval            = 3  //間隔 也就是等差

//+----------------------------------------+//
//+- Internal functions   

//+----------------------------------------+//


method LineStyle(Helper helper, string style) =>
    helper.name := style
    out = switch style
        '----' => line.style_dashed
        '····' => line.style_dotted
        => line.style_solid
method HTFAddValidCheck(CandleSet cs) =>
    cs.settings.show := (cs.settings.htfint-InitialPeriod)%Interval==0 and cs.settings.htfint>=InitialPeriod? true : false
    cs
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
    if candleSet.settings.show
        BOSdata bosdata = candleSet.bosdata
        HTFBarTime = time(candleSet.settings.htf)
        isNewHTFCandle = ta.change(HTFBarTime)
        if isNewHTFCandle != 0 
            Candle candle    = Candle.new()
            candle.c        := bar_index==0 ? close : bosdata.temp
            candle.c_idx    := bar_index
            candleSet.candles.unshift(candle) //從這句話可以知道 index越靠近零 資料越新

            if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
                Candle delCandle = array.pop(candleSet.candles)
        bosdata.temp := close //in fact "temp" is the lastest close price
    candleSet

method Monitor_Est(CandleSet candleSet) =>
    if candleSet.settings.show
        if barstate.isrealtime
            Candle candle    = Candle.new()
            candle.c        := close
            candle.c_idx    := bar_index
            candleSet.candles.unshift(candle)
            if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
                Candle delCandle = array.pop(candleSet.candles)
            candleSet.bosdata.nowclosebool := true
    candleSet

method BOSJudge(CandleSet candleSet) =>
    if candleSet.settings.show
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
        if (candleSet.candles.size() > 0 and isNewHTFCandle != 0) // 就算最新的出現 也必須遵守這個規定 為了讓結構穩定不亂序
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
        bosdata.nowclosebool  := false
    candleSet

method HighestsbdSet(ValueDecisionReg highestsbd, CandleSet candleSet) =>
    if candleSet.settings.show
        ValueDecisionReg m1 = highestsbd
        CandleSet        cs = candleSet
        if cs.bosdata.sbd > m1.value
            m1.value := cs.bosdata.sbd
            m1.vidx  := cs.bosdata.sbd_idx
            m1.vname := cs.settings.htf
            m1.vdate := cs.bosdata.s_dated
    highestsbd

method LowestsbuSet (ValueDecisionReg lowestsbu, CandleSet candleSet) =>
    if candleSet.settings.show
        ValueDecisionReg m1 = lowestsbu
        CandleSet        cs = candleSet
        var bool         fg = true 
        if cs.bosdata.sbu < m1.value
            m1.value := cs.bosdata.sbu
            m1.vidx  := cs.bosdata.sbu_idx
            m1.vname := cs.settings.htf
            m1.vdate := cs.bosdata.s_dateu
    lowestsbu

method Predictor (CandleSet candleSet, ValueDecisionReg predictor) =>
    if candleSet.settings.show
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
    if m1.vdecisionname == "HighestsbdSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset-2, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname +"min" + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset-2,m1.value,text= decision.vtext + str.tostring(m1.value),style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
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
    decision

//+---------------Main------------------+//
int cnt    = 0
int delta  = settings.text_buffer
int offset = settings.offset + bar_index
//+---------------ADD------------------+//

//+---------------add var------------------+//
var CandleSet htfadd1                     = CandleSet.new()
var CandleSettings SettingsHTFadd1        = CandleSettings.new(htf="1", max_memory=3, htfint=1)
var Candle[] candlesadd1                  = array.new<Candle>(0)
var BOSdata bosdataadd1                   = BOSdata.new()
htfadd1.settings                 := SettingsHTFadd1
htfadd1.candles                  := candlesadd1
htfadd1.bosdata                  := bosdataadd1
var CandleSet htfadd2                     = CandleSet.new()
var CandleSettings SettingsHTFadd2        = CandleSettings.new(htf="2", max_memory=3, htfint=2)
var Candle[] candlesadd2                  = array.new<Candle>(0)
var BOSdata bosdataadd2                   = BOSdata.new()
htfadd2.settings                 := SettingsHTFadd2
htfadd2.candles                  := candlesadd2
htfadd2.bosdata                  := bosdataadd2
var CandleSet htfadd3                     = CandleSet.new()
var CandleSettings SettingsHTFadd3        = CandleSettings.new(htf="3", max_memory=3, htfint=3)
var Candle[] candlesadd3                  = array.new<Candle>(0)
var BOSdata bosdataadd3                   = BOSdata.new()
htfadd3.settings                 := SettingsHTFadd3
htfadd3.candles                  := candlesadd3
htfadd3.bosdata                  := bosdataadd3
var CandleSet htfadd4                     = CandleSet.new()
var CandleSettings SettingsHTFadd4        = CandleSettings.new(htf="4", max_memory=3, htfint=4)
var Candle[] candlesadd4                  = array.new<Candle>(0)
var BOSdata bosdataadd4                   = BOSdata.new()
htfadd4.settings                 := SettingsHTFadd4
htfadd4.candles                  := candlesadd4
htfadd4.bosdata                  := bosdataadd4
var CandleSet htfadd5                     = CandleSet.new()
var CandleSettings SettingsHTFadd5        = CandleSettings.new(htf="5", max_memory=3, htfint=5)
var Candle[] candlesadd5                  = array.new<Candle>(0)
var BOSdata bosdataadd5                   = BOSdata.new()
htfadd5.settings                 := SettingsHTFadd5
htfadd5.candles                  := candlesadd5
htfadd5.bosdata                  := bosdataadd5
var CandleSet htfadd6                     = CandleSet.new()
var CandleSettings SettingsHTFadd6        = CandleSettings.new(htf="6", max_memory=3, htfint=6)
var Candle[] candlesadd6                  = array.new<Candle>(0)
var BOSdata bosdataadd6                   = BOSdata.new()
htfadd6.settings                 := SettingsHTFadd6
htfadd6.candles                  := candlesadd6
htfadd6.bosdata                  := bosdataadd6
var CandleSet htfadd7                     = CandleSet.new()
var CandleSettings SettingsHTFadd7        = CandleSettings.new(htf="7", max_memory=3, htfint=7)
var Candle[] candlesadd7                  = array.new<Candle>(0)
var BOSdata bosdataadd7                   = BOSdata.new()
htfadd7.settings                 := SettingsHTFadd7
htfadd7.candles                  := candlesadd7
htfadd7.bosdata                  := bosdataadd7
var CandleSet htfadd8                     = CandleSet.new()
var CandleSettings SettingsHTFadd8        = CandleSettings.new(htf="8", max_memory=3, htfint=8)
var Candle[] candlesadd8                  = array.new<Candle>(0)
var BOSdata bosdataadd8                   = BOSdata.new()
htfadd8.settings                 := SettingsHTFadd8
htfadd8.candles                  := candlesadd8
htfadd8.bosdata                  := bosdataadd8
var CandleSet htfadd9                     = CandleSet.new()
var CandleSettings SettingsHTFadd9        = CandleSettings.new(htf="9", max_memory=3, htfint=9)
var Candle[] candlesadd9                  = array.new<Candle>(0)
var BOSdata bosdataadd9                   = BOSdata.new()
htfadd9.settings                 := SettingsHTFadd9
htfadd9.candles                  := candlesadd9
htfadd9.bosdata                  := bosdataadd9
var CandleSet htfadd10                     = CandleSet.new()
var CandleSettings SettingsHTFadd10        = CandleSettings.new(htf="10", max_memory=3, htfint=10)
var Candle[] candlesadd10                  = array.new<Candle>(0)
var BOSdata bosdataadd10                   = BOSdata.new()
htfadd10.settings                 := SettingsHTFadd10
htfadd10.candles                  := candlesadd10
htfadd10.bosdata                  := bosdataadd10
var CandleSet htfadd11                     = CandleSet.new()
var CandleSettings SettingsHTFadd11        = CandleSettings.new(htf="11", max_memory=3, htfint=11)
var Candle[] candlesadd11                  = array.new<Candle>(0)
var BOSdata bosdataadd11                   = BOSdata.new()
htfadd11.settings                 := SettingsHTFadd11
htfadd11.candles                  := candlesadd11
htfadd11.bosdata                  := bosdataadd11
var CandleSet htfadd12                     = CandleSet.new()
var CandleSettings SettingsHTFadd12        = CandleSettings.new(htf="12", max_memory=3, htfint=12)
var Candle[] candlesadd12                  = array.new<Candle>(0)
var BOSdata bosdataadd12                   = BOSdata.new()
htfadd12.settings                 := SettingsHTFadd12
htfadd12.candles                  := candlesadd12
htfadd12.bosdata                  := bosdataadd12
var CandleSet htfadd13                     = CandleSet.new()
var CandleSettings SettingsHTFadd13        = CandleSettings.new(htf="13", max_memory=3, htfint=13)
var Candle[] candlesadd13                  = array.new<Candle>(0)
var BOSdata bosdataadd13                   = BOSdata.new()
htfadd13.settings                 := SettingsHTFadd13
htfadd13.candles                  := candlesadd13
htfadd13.bosdata                  := bosdataadd13
var CandleSet htfadd14                     = CandleSet.new()
var CandleSettings SettingsHTFadd14        = CandleSettings.new(htf="14", max_memory=3, htfint=14)
var Candle[] candlesadd14                  = array.new<Candle>(0)
var BOSdata bosdataadd14                   = BOSdata.new()
htfadd14.settings                 := SettingsHTFadd14
htfadd14.candles                  := candlesadd14
htfadd14.bosdata                  := bosdataadd14
var CandleSet htfadd15                     = CandleSet.new()
var CandleSettings SettingsHTFadd15        = CandleSettings.new(htf="15", max_memory=3, htfint=15)
var Candle[] candlesadd15                  = array.new<Candle>(0)
var BOSdata bosdataadd15                   = BOSdata.new()
htfadd15.settings                 := SettingsHTFadd15
htfadd15.candles                  := candlesadd15
htfadd15.bosdata                  := bosdataadd15
var CandleSet htfadd16                     = CandleSet.new()
var CandleSettings SettingsHTFadd16        = CandleSettings.new(htf="16", max_memory=3, htfint=16)
var Candle[] candlesadd16                  = array.new<Candle>(0)
var BOSdata bosdataadd16                   = BOSdata.new()
htfadd16.settings                 := SettingsHTFadd16
htfadd16.candles                  := candlesadd16
htfadd16.bosdata                  := bosdataadd16
var CandleSet htfadd17                     = CandleSet.new()
var CandleSettings SettingsHTFadd17        = CandleSettings.new(htf="17", max_memory=3, htfint=17)
var Candle[] candlesadd17                  = array.new<Candle>(0)
var BOSdata bosdataadd17                   = BOSdata.new()
htfadd17.settings                 := SettingsHTFadd17
htfadd17.candles                  := candlesadd17
htfadd17.bosdata                  := bosdataadd17
var CandleSet htfadd18                     = CandleSet.new()
var CandleSettings SettingsHTFadd18        = CandleSettings.new(htf="18", max_memory=3, htfint=18)
var Candle[] candlesadd18                  = array.new<Candle>(0)
var BOSdata bosdataadd18                   = BOSdata.new()
htfadd18.settings                 := SettingsHTFadd18
htfadd18.candles                  := candlesadd18
htfadd18.bosdata                  := bosdataadd18
var CandleSet htfadd19                     = CandleSet.new()
var CandleSettings SettingsHTFadd19        = CandleSettings.new(htf="19", max_memory=3, htfint=19)
var Candle[] candlesadd19                  = array.new<Candle>(0)
var BOSdata bosdataadd19                   = BOSdata.new()
htfadd19.settings                 := SettingsHTFadd19
htfadd19.candles                  := candlesadd19
htfadd19.bosdata                  := bosdataadd19
var CandleSet htfadd20                     = CandleSet.new()
var CandleSettings SettingsHTFadd20        = CandleSettings.new(htf="20", max_memory=3, htfint=20)
var Candle[] candlesadd20                  = array.new<Candle>(0)
var BOSdata bosdataadd20                   = BOSdata.new()
htfadd20.settings                 := SettingsHTFadd20
htfadd20.candles                  := candlesadd20
htfadd20.bosdata                  := bosdataadd20
var CandleSet htfadd21                     = CandleSet.new()
var CandleSettings SettingsHTFadd21        = CandleSettings.new(htf="21", max_memory=3, htfint=21)
var Candle[] candlesadd21                  = array.new<Candle>(0)
var BOSdata bosdataadd21                   = BOSdata.new()
htfadd21.settings                 := SettingsHTFadd21
htfadd21.candles                  := candlesadd21
htfadd21.bosdata                  := bosdataadd21
var CandleSet htfadd22                     = CandleSet.new()
var CandleSettings SettingsHTFadd22        = CandleSettings.new(htf="22", max_memory=3, htfint=22)
var Candle[] candlesadd22                  = array.new<Candle>(0)
var BOSdata bosdataadd22                   = BOSdata.new()
htfadd22.settings                 := SettingsHTFadd22
htfadd22.candles                  := candlesadd22
htfadd22.bosdata                  := bosdataadd22
var CandleSet htfadd23                     = CandleSet.new()
var CandleSettings SettingsHTFadd23        = CandleSettings.new(htf="23", max_memory=3, htfint=23)
var Candle[] candlesadd23                  = array.new<Candle>(0)
var BOSdata bosdataadd23                   = BOSdata.new()
htfadd23.settings                 := SettingsHTFadd23
htfadd23.candles                  := candlesadd23
htfadd23.bosdata                  := bosdataadd23
var CandleSet htfadd24                     = CandleSet.new()
var CandleSettings SettingsHTFadd24        = CandleSettings.new(htf="24", max_memory=3, htfint=24)
var Candle[] candlesadd24                  = array.new<Candle>(0)
var BOSdata bosdataadd24                   = BOSdata.new()
htfadd24.settings                 := SettingsHTFadd24
htfadd24.candles                  := candlesadd24
htfadd24.bosdata                  := bosdataadd24
var CandleSet htfadd25                     = CandleSet.new()
var CandleSettings SettingsHTFadd25        = CandleSettings.new(htf="25", max_memory=3, htfint=25)
var Candle[] candlesadd25                  = array.new<Candle>(0)
var BOSdata bosdataadd25                   = BOSdata.new()
htfadd25.settings                 := SettingsHTFadd25
htfadd25.candles                  := candlesadd25
htfadd25.bosdata                  := bosdataadd25
var CandleSet htfadd26                     = CandleSet.new()
var CandleSettings SettingsHTFadd26        = CandleSettings.new(htf="26", max_memory=3, htfint=26)
var Candle[] candlesadd26                  = array.new<Candle>(0)
var BOSdata bosdataadd26                   = BOSdata.new()
htfadd26.settings                 := SettingsHTFadd26
htfadd26.candles                  := candlesadd26
htfadd26.bosdata                  := bosdataadd26
var CandleSet htfadd27                     = CandleSet.new()
var CandleSettings SettingsHTFadd27        = CandleSettings.new(htf="27", max_memory=3, htfint=27)
var Candle[] candlesadd27                  = array.new<Candle>(0)
var BOSdata bosdataadd27                   = BOSdata.new()
htfadd27.settings                 := SettingsHTFadd27
htfadd27.candles                  := candlesadd27
htfadd27.bosdata                  := bosdataadd27
var CandleSet htfadd28                     = CandleSet.new()
var CandleSettings SettingsHTFadd28        = CandleSettings.new(htf="28", max_memory=3, htfint=28)
var Candle[] candlesadd28                  = array.new<Candle>(0)
var BOSdata bosdataadd28                   = BOSdata.new()
htfadd28.settings                 := SettingsHTFadd28
htfadd28.candles                  := candlesadd28
htfadd28.bosdata                  := bosdataadd28
var CandleSet htfadd29                     = CandleSet.new()
var CandleSettings SettingsHTFadd29        = CandleSettings.new(htf="29", max_memory=3, htfint=29)
var Candle[] candlesadd29                  = array.new<Candle>(0)
var BOSdata bosdataadd29                   = BOSdata.new()
htfadd29.settings                 := SettingsHTFadd29
htfadd29.candles                  := candlesadd29
htfadd29.bosdata                  := bosdataadd29
var CandleSet htfadd30                     = CandleSet.new()
var CandleSettings SettingsHTFadd30        = CandleSettings.new(htf="30", max_memory=3, htfint=30)
var Candle[] candlesadd30                  = array.new<Candle>(0)
var BOSdata bosdataadd30                   = BOSdata.new()
htfadd30.settings                 := SettingsHTFadd30
htfadd30.candles                  := candlesadd30
htfadd30.bosdata                  := bosdataadd30
var CandleSet htfadd31                     = CandleSet.new()
var CandleSettings SettingsHTFadd31        = CandleSettings.new(htf="31", max_memory=3, htfint=31)
var Candle[] candlesadd31                  = array.new<Candle>(0)
var BOSdata bosdataadd31                   = BOSdata.new()
htfadd31.settings                 := SettingsHTFadd31
htfadd31.candles                  := candlesadd31
htfadd31.bosdata                  := bosdataadd31
var CandleSet htfadd32                     = CandleSet.new()
var CandleSettings SettingsHTFadd32        = CandleSettings.new(htf="32", max_memory=3, htfint=32)
var Candle[] candlesadd32                  = array.new<Candle>(0)
var BOSdata bosdataadd32                   = BOSdata.new()
htfadd32.settings                 := SettingsHTFadd32
htfadd32.candles                  := candlesadd32
htfadd32.bosdata                  := bosdataadd32
var CandleSet htfadd33                     = CandleSet.new()
var CandleSettings SettingsHTFadd33        = CandleSettings.new(htf="33", max_memory=3, htfint=33)
var Candle[] candlesadd33                  = array.new<Candle>(0)
var BOSdata bosdataadd33                   = BOSdata.new()
htfadd33.settings                 := SettingsHTFadd33
htfadd33.candles                  := candlesadd33
htfadd33.bosdata                  := bosdataadd33
var CandleSet htfadd34                     = CandleSet.new()
var CandleSettings SettingsHTFadd34        = CandleSettings.new(htf="34", max_memory=3, htfint=34)
var Candle[] candlesadd34                  = array.new<Candle>(0)
var BOSdata bosdataadd34                   = BOSdata.new()
htfadd34.settings                 := SettingsHTFadd34
htfadd34.candles                  := candlesadd34
htfadd34.bosdata                  := bosdataadd34
var CandleSet htfadd35                     = CandleSet.new()
var CandleSettings SettingsHTFadd35        = CandleSettings.new(htf="35", max_memory=3, htfint=35)
var Candle[] candlesadd35                  = array.new<Candle>(0)
var BOSdata bosdataadd35                   = BOSdata.new()
htfadd35.settings                 := SettingsHTFadd35
htfadd35.candles                  := candlesadd35
htfadd35.bosdata                  := bosdataadd35
var CandleSet htfadd36                     = CandleSet.new()
var CandleSettings SettingsHTFadd36        = CandleSettings.new(htf="36", max_memory=3, htfint=36)
var Candle[] candlesadd36                  = array.new<Candle>(0)
var BOSdata bosdataadd36                   = BOSdata.new()
htfadd36.settings                 := SettingsHTFadd36
htfadd36.candles                  := candlesadd36
htfadd36.bosdata                  := bosdataadd36
var CandleSet htfadd37                     = CandleSet.new()
var CandleSettings SettingsHTFadd37        = CandleSettings.new(htf="37", max_memory=3, htfint=37)
var Candle[] candlesadd37                  = array.new<Candle>(0)
var BOSdata bosdataadd37                   = BOSdata.new()
htfadd37.settings                 := SettingsHTFadd37
htfadd37.candles                  := candlesadd37
htfadd37.bosdata                  := bosdataadd37
var CandleSet htfadd38                     = CandleSet.new()
var CandleSettings SettingsHTFadd38        = CandleSettings.new(htf="38", max_memory=3, htfint=38)
var Candle[] candlesadd38                  = array.new<Candle>(0)
var BOSdata bosdataadd38                   = BOSdata.new()
htfadd38.settings                 := SettingsHTFadd38
htfadd38.candles                  := candlesadd38
htfadd38.bosdata                  := bosdataadd38
var CandleSet htfadd39                     = CandleSet.new()
var CandleSettings SettingsHTFadd39        = CandleSettings.new(htf="39", max_memory=3, htfint=39)
var Candle[] candlesadd39                  = array.new<Candle>(0)
var BOSdata bosdataadd39                   = BOSdata.new()
htfadd39.settings                 := SettingsHTFadd39
htfadd39.candles                  := candlesadd39
htfadd39.bosdata                  := bosdataadd39
var CandleSet htfadd40                     = CandleSet.new()
var CandleSettings SettingsHTFadd40        = CandleSettings.new(htf="40", max_memory=3, htfint=40)
var Candle[] candlesadd40                  = array.new<Candle>(0)
var BOSdata bosdataadd40                   = BOSdata.new()
htfadd40.settings                 := SettingsHTFadd40
htfadd40.candles                  := candlesadd40
htfadd40.bosdata                  := bosdataadd40
var CandleSet htfadd41                     = CandleSet.new()
var CandleSettings SettingsHTFadd41        = CandleSettings.new(htf="41", max_memory=3, htfint=41)
var Candle[] candlesadd41                  = array.new<Candle>(0)
var BOSdata bosdataadd41                   = BOSdata.new()
htfadd41.settings                 := SettingsHTFadd41
htfadd41.candles                  := candlesadd41
htfadd41.bosdata                  := bosdataadd41
var CandleSet htfadd42                     = CandleSet.new()
var CandleSettings SettingsHTFadd42        = CandleSettings.new(htf="42", max_memory=3, htfint=42)
var Candle[] candlesadd42                  = array.new<Candle>(0)
var BOSdata bosdataadd42                   = BOSdata.new()
htfadd42.settings                 := SettingsHTFadd42
htfadd42.candles                  := candlesadd42
htfadd42.bosdata                  := bosdataadd42
var CandleSet htfadd43                     = CandleSet.new()
var CandleSettings SettingsHTFadd43        = CandleSettings.new(htf="43", max_memory=3, htfint=43)
var Candle[] candlesadd43                  = array.new<Candle>(0)
var BOSdata bosdataadd43                   = BOSdata.new()
htfadd43.settings                 := SettingsHTFadd43
htfadd43.candles                  := candlesadd43
htfadd43.bosdata                  := bosdataadd43
var CandleSet htfadd44                     = CandleSet.new()
var CandleSettings SettingsHTFadd44        = CandleSettings.new(htf="44", max_memory=3, htfint=44)
var Candle[] candlesadd44                  = array.new<Candle>(0)
var BOSdata bosdataadd44                   = BOSdata.new()
htfadd44.settings                 := SettingsHTFadd44
htfadd44.candles                  := candlesadd44
htfadd44.bosdata                  := bosdataadd44
var CandleSet htfadd45                     = CandleSet.new()
var CandleSettings SettingsHTFadd45        = CandleSettings.new(htf="45", max_memory=3, htfint=45)
var Candle[] candlesadd45                  = array.new<Candle>(0)
var BOSdata bosdataadd45                   = BOSdata.new()
htfadd45.settings                 := SettingsHTFadd45
htfadd45.candles                  := candlesadd45
htfadd45.bosdata                  := bosdataadd45
var CandleSet htfadd46                     = CandleSet.new()
var CandleSettings SettingsHTFadd46        = CandleSettings.new(htf="46", max_memory=3, htfint=46)
var Candle[] candlesadd46                  = array.new<Candle>(0)
var BOSdata bosdataadd46                   = BOSdata.new()
htfadd46.settings                 := SettingsHTFadd46
htfadd46.candles                  := candlesadd46
htfadd46.bosdata                  := bosdataadd46
var CandleSet htfadd47                     = CandleSet.new()
var CandleSettings SettingsHTFadd47        = CandleSettings.new(htf="47", max_memory=3, htfint=47)
var Candle[] candlesadd47                  = array.new<Candle>(0)
var BOSdata bosdataadd47                   = BOSdata.new()
htfadd47.settings                 := SettingsHTFadd47
htfadd47.candles                  := candlesadd47
htfadd47.bosdata                  := bosdataadd47
var CandleSet htfadd48                     = CandleSet.new()
var CandleSettings SettingsHTFadd48        = CandleSettings.new(htf="48", max_memory=3, htfint=48)
var Candle[] candlesadd48                  = array.new<Candle>(0)
var BOSdata bosdataadd48                   = BOSdata.new()
htfadd48.settings                 := SettingsHTFadd48
htfadd48.candles                  := candlesadd48
htfadd48.bosdata                  := bosdataadd48
var CandleSet htfadd49                     = CandleSet.new()
var CandleSettings SettingsHTFadd49        = CandleSettings.new(htf="49", max_memory=3, htfint=49)
var Candle[] candlesadd49                  = array.new<Candle>(0)
var BOSdata bosdataadd49                   = BOSdata.new()
htfadd49.settings                 := SettingsHTFadd49
htfadd49.candles                  := candlesadd49
htfadd49.bosdata                  := bosdataadd49
var CandleSet htfadd50                     = CandleSet.new()
var CandleSettings SettingsHTFadd50        = CandleSettings.new(htf="50", max_memory=3, htfint=50)
var Candle[] candlesadd50                  = array.new<Candle>(0)
var BOSdata bosdataadd50                   = BOSdata.new()
htfadd50.settings                 := SettingsHTFadd50
htfadd50.candles                  := candlesadd50
htfadd50.bosdata                  := bosdataadd50
var CandleSet htfadd51                     = CandleSet.new()
var CandleSettings SettingsHTFadd51        = CandleSettings.new(htf="51", max_memory=3, htfint=51)
var Candle[] candlesadd51                  = array.new<Candle>(0)
var BOSdata bosdataadd51                   = BOSdata.new()
htfadd51.settings                 := SettingsHTFadd51
htfadd51.candles                  := candlesadd51
htfadd51.bosdata                  := bosdataadd51
var CandleSet htfadd52                     = CandleSet.new()
var CandleSettings SettingsHTFadd52        = CandleSettings.new(htf="52", max_memory=3, htfint=52)
var Candle[] candlesadd52                  = array.new<Candle>(0)
var BOSdata bosdataadd52                   = BOSdata.new()
htfadd52.settings                 := SettingsHTFadd52
htfadd52.candles                  := candlesadd52
htfadd52.bosdata                  := bosdataadd52
var CandleSet htfadd53                     = CandleSet.new()
var CandleSettings SettingsHTFadd53        = CandleSettings.new(htf="53", max_memory=3, htfint=53)
var Candle[] candlesadd53                  = array.new<Candle>(0)
var BOSdata bosdataadd53                   = BOSdata.new()
htfadd53.settings                 := SettingsHTFadd53
htfadd53.candles                  := candlesadd53
htfadd53.bosdata                  := bosdataadd53
var CandleSet htfadd54                     = CandleSet.new()
var CandleSettings SettingsHTFadd54        = CandleSettings.new(htf="54", max_memory=3, htfint=54)
var Candle[] candlesadd54                  = array.new<Candle>(0)
var BOSdata bosdataadd54                   = BOSdata.new()
htfadd54.settings                 := SettingsHTFadd54
htfadd54.candles                  := candlesadd54
htfadd54.bosdata                  := bosdataadd54
var CandleSet htfadd55                     = CandleSet.new()
var CandleSettings SettingsHTFadd55        = CandleSettings.new(htf="55", max_memory=3, htfint=55)
var Candle[] candlesadd55                  = array.new<Candle>(0)
var BOSdata bosdataadd55                   = BOSdata.new()
htfadd55.settings                 := SettingsHTFadd55
htfadd55.candles                  := candlesadd55
htfadd55.bosdata                  := bosdataadd55
var CandleSet htfadd56                     = CandleSet.new()
var CandleSettings SettingsHTFadd56        = CandleSettings.new(htf="56", max_memory=3, htfint=56)
var Candle[] candlesadd56                  = array.new<Candle>(0)
var BOSdata bosdataadd56                   = BOSdata.new()
htfadd56.settings                 := SettingsHTFadd56
htfadd56.candles                  := candlesadd56
htfadd56.bosdata                  := bosdataadd56
var CandleSet htfadd57                     = CandleSet.new()
var CandleSettings SettingsHTFadd57        = CandleSettings.new(htf="57", max_memory=3, htfint=57)
var Candle[] candlesadd57                  = array.new<Candle>(0)
var BOSdata bosdataadd57                   = BOSdata.new()
htfadd57.settings                 := SettingsHTFadd57
htfadd57.candles                  := candlesadd57
htfadd57.bosdata                  := bosdataadd57
var CandleSet htfadd58                     = CandleSet.new()
var CandleSettings SettingsHTFadd58        = CandleSettings.new(htf="58", max_memory=3, htfint=58)
var Candle[] candlesadd58                  = array.new<Candle>(0)
var BOSdata bosdataadd58                   = BOSdata.new()
htfadd58.settings                 := SettingsHTFadd58
htfadd58.candles                  := candlesadd58
htfadd58.bosdata                  := bosdataadd58
var CandleSet htfadd59                     = CandleSet.new()
var CandleSettings SettingsHTFadd59        = CandleSettings.new(htf="59", max_memory=3, htfint=59)
var Candle[] candlesadd59                  = array.new<Candle>(0)
var BOSdata bosdataadd59                   = BOSdata.new()
htfadd59.settings                 := SettingsHTFadd59
htfadd59.candles                  := candlesadd59
htfadd59.bosdata                  := bosdataadd59
var CandleSet htfadd60                     = CandleSet.new()
var CandleSettings SettingsHTFadd60        = CandleSettings.new(htf="60", max_memory=3, htfint=60)
var Candle[] candlesadd60                  = array.new<Candle>(0)
var BOSdata bosdataadd60                   = BOSdata.new()
htfadd60.settings                 := SettingsHTFadd60
htfadd60.candles                  := candlesadd60
htfadd60.bosdata                  := bosdataadd60
var CandleSet htfadd61                     = CandleSet.new()
var CandleSettings SettingsHTFadd61        = CandleSettings.new(htf="61", max_memory=3, htfint=61)
var Candle[] candlesadd61                  = array.new<Candle>(0)
var BOSdata bosdataadd61                   = BOSdata.new()
htfadd61.settings                 := SettingsHTFadd61
htfadd61.candles                  := candlesadd61
htfadd61.bosdata                  := bosdataadd61
var CandleSet htfadd62                     = CandleSet.new()
var CandleSettings SettingsHTFadd62        = CandleSettings.new(htf="62", max_memory=3, htfint=62)
var Candle[] candlesadd62                  = array.new<Candle>(0)
var BOSdata bosdataadd62                   = BOSdata.new()
htfadd62.settings                 := SettingsHTFadd62
htfadd62.candles                  := candlesadd62
htfadd62.bosdata                  := bosdataadd62
var CandleSet htfadd63                     = CandleSet.new()
var CandleSettings SettingsHTFadd63        = CandleSettings.new(htf="63", max_memory=3, htfint=63)
var Candle[] candlesadd63                  = array.new<Candle>(0)
var BOSdata bosdataadd63                   = BOSdata.new()
htfadd63.settings                 := SettingsHTFadd63
htfadd63.candles                  := candlesadd63
htfadd63.bosdata                  := bosdataadd63
var CandleSet htfadd64                     = CandleSet.new()
var CandleSettings SettingsHTFadd64        = CandleSettings.new(htf="64", max_memory=3, htfint=64)
var Candle[] candlesadd64                  = array.new<Candle>(0)
var BOSdata bosdataadd64                   = BOSdata.new()
htfadd64.settings                 := SettingsHTFadd64
htfadd64.candles                  := candlesadd64
htfadd64.bosdata                  := bosdataadd64
var CandleSet htfadd65                     = CandleSet.new()
var CandleSettings SettingsHTFadd65        = CandleSettings.new(htf="65", max_memory=3, htfint=65)
var Candle[] candlesadd65                  = array.new<Candle>(0)
var BOSdata bosdataadd65                   = BOSdata.new()
htfadd65.settings                 := SettingsHTFadd65
htfadd65.candles                  := candlesadd65
htfadd65.bosdata                  := bosdataadd65
var CandleSet htfadd66                     = CandleSet.new()
var CandleSettings SettingsHTFadd66        = CandleSettings.new(htf="66", max_memory=3, htfint=66)
var Candle[] candlesadd66                  = array.new<Candle>(0)
var BOSdata bosdataadd66                   = BOSdata.new()
htfadd66.settings                 := SettingsHTFadd66
htfadd66.candles                  := candlesadd66
htfadd66.bosdata                  := bosdataadd66
var CandleSet htfadd67                     = CandleSet.new()
var CandleSettings SettingsHTFadd67        = CandleSettings.new(htf="67", max_memory=3, htfint=67)
var Candle[] candlesadd67                  = array.new<Candle>(0)
var BOSdata bosdataadd67                   = BOSdata.new()
htfadd67.settings                 := SettingsHTFadd67
htfadd67.candles                  := candlesadd67
htfadd67.bosdata                  := bosdataadd67
var CandleSet htfadd68                     = CandleSet.new()
var CandleSettings SettingsHTFadd68        = CandleSettings.new(htf="68", max_memory=3, htfint=68)
var Candle[] candlesadd68                  = array.new<Candle>(0)
var BOSdata bosdataadd68                   = BOSdata.new()
htfadd68.settings                 := SettingsHTFadd68
htfadd68.candles                  := candlesadd68
htfadd68.bosdata                  := bosdataadd68
var CandleSet htfadd69                     = CandleSet.new()
var CandleSettings SettingsHTFadd69        = CandleSettings.new(htf="69", max_memory=3, htfint=69)
var Candle[] candlesadd69                  = array.new<Candle>(0)
var BOSdata bosdataadd69                   = BOSdata.new()
htfadd69.settings                 := SettingsHTFadd69
htfadd69.candles                  := candlesadd69
htfadd69.bosdata                  := bosdataadd69
var CandleSet htfadd70                     = CandleSet.new()
var CandleSettings SettingsHTFadd70        = CandleSettings.new(htf="70", max_memory=3, htfint=70)
var Candle[] candlesadd70                  = array.new<Candle>(0)
var BOSdata bosdataadd70                   = BOSdata.new()
htfadd70.settings                 := SettingsHTFadd70
htfadd70.candles                  := candlesadd70
htfadd70.bosdata                  := bosdataadd70
var CandleSet htfadd71                     = CandleSet.new()
var CandleSettings SettingsHTFadd71        = CandleSettings.new(htf="71", max_memory=3, htfint=71)
var Candle[] candlesadd71                  = array.new<Candle>(0)
var BOSdata bosdataadd71                   = BOSdata.new()
htfadd71.settings                 := SettingsHTFadd71
htfadd71.candles                  := candlesadd71
htfadd71.bosdata                  := bosdataadd71
var CandleSet htfadd72                     = CandleSet.new()
var CandleSettings SettingsHTFadd72        = CandleSettings.new(htf="72", max_memory=3, htfint=72)
var Candle[] candlesadd72                  = array.new<Candle>(0)
var BOSdata bosdataadd72                   = BOSdata.new()
htfadd72.settings                 := SettingsHTFadd72
htfadd72.candles                  := candlesadd72
htfadd72.bosdata                  := bosdataadd72
var CandleSet htfadd73                     = CandleSet.new()
var CandleSettings SettingsHTFadd73        = CandleSettings.new(htf="73", max_memory=3, htfint=73)
var Candle[] candlesadd73                  = array.new<Candle>(0)
var BOSdata bosdataadd73                   = BOSdata.new()
htfadd73.settings                 := SettingsHTFadd73
htfadd73.candles                  := candlesadd73
htfadd73.bosdata                  := bosdataadd73
var CandleSet htfadd74                     = CandleSet.new()
var CandleSettings SettingsHTFadd74        = CandleSettings.new(htf="74", max_memory=3, htfint=74)
var Candle[] candlesadd74                  = array.new<Candle>(0)
var BOSdata bosdataadd74                   = BOSdata.new()
htfadd74.settings                 := SettingsHTFadd74
htfadd74.candles                  := candlesadd74
htfadd74.bosdata                  := bosdataadd74
var CandleSet htfadd75                     = CandleSet.new()
var CandleSettings SettingsHTFadd75        = CandleSettings.new(htf="75", max_memory=3, htfint=75)
var Candle[] candlesadd75                  = array.new<Candle>(0)
var BOSdata bosdataadd75                   = BOSdata.new()
htfadd75.settings                 := SettingsHTFadd75
htfadd75.candles                  := candlesadd75
htfadd75.bosdata                  := bosdataadd75
var CandleSet htfadd76                     = CandleSet.new()
var CandleSettings SettingsHTFadd76        = CandleSettings.new(htf="76", max_memory=3, htfint=76)
var Candle[] candlesadd76                  = array.new<Candle>(0)
var BOSdata bosdataadd76                   = BOSdata.new()
htfadd76.settings                 := SettingsHTFadd76
htfadd76.candles                  := candlesadd76
htfadd76.bosdata                  := bosdataadd76
var CandleSet htfadd77                     = CandleSet.new()
var CandleSettings SettingsHTFadd77        = CandleSettings.new(htf="77", max_memory=3, htfint=77)
var Candle[] candlesadd77                  = array.new<Candle>(0)
var BOSdata bosdataadd77                   = BOSdata.new()
htfadd77.settings                 := SettingsHTFadd77
htfadd77.candles                  := candlesadd77
htfadd77.bosdata                  := bosdataadd77
var CandleSet htfadd78                     = CandleSet.new()
var CandleSettings SettingsHTFadd78        = CandleSettings.new(htf="78", max_memory=3, htfint=78)
var Candle[] candlesadd78                  = array.new<Candle>(0)
var BOSdata bosdataadd78                   = BOSdata.new()
htfadd78.settings                 := SettingsHTFadd78
htfadd78.candles                  := candlesadd78
htfadd78.bosdata                  := bosdataadd78
var CandleSet htfadd79                     = CandleSet.new()
var CandleSettings SettingsHTFadd79        = CandleSettings.new(htf="79", max_memory=3, htfint=79)
var Candle[] candlesadd79                  = array.new<Candle>(0)
var BOSdata bosdataadd79                   = BOSdata.new()
htfadd79.settings                 := SettingsHTFadd79
htfadd79.candles                  := candlesadd79
htfadd79.bosdata                  := bosdataadd79
var CandleSet htfadd80                     = CandleSet.new()
var CandleSettings SettingsHTFadd80        = CandleSettings.new(htf="80", max_memory=3, htfint=80)
var Candle[] candlesadd80                  = array.new<Candle>(0)
var BOSdata bosdataadd80                   = BOSdata.new()
htfadd80.settings                 := SettingsHTFadd80
htfadd80.candles                  := candlesadd80
htfadd80.bosdata                  := bosdataadd80
var CandleSet htfadd81                     = CandleSet.new()
var CandleSettings SettingsHTFadd81        = CandleSettings.new(htf="81", max_memory=3, htfint=81)
var Candle[] candlesadd81                  = array.new<Candle>(0)
var BOSdata bosdataadd81                   = BOSdata.new()
htfadd81.settings                 := SettingsHTFadd81
htfadd81.candles                  := candlesadd81
htfadd81.bosdata                  := bosdataadd81
var CandleSet htfadd82                     = CandleSet.new()
var CandleSettings SettingsHTFadd82        = CandleSettings.new(htf="82", max_memory=3, htfint=82)
var Candle[] candlesadd82                  = array.new<Candle>(0)
var BOSdata bosdataadd82                   = BOSdata.new()
htfadd82.settings                 := SettingsHTFadd82
htfadd82.candles                  := candlesadd82
htfadd82.bosdata                  := bosdataadd82
var CandleSet htfadd83                     = CandleSet.new()
var CandleSettings SettingsHTFadd83        = CandleSettings.new(htf="83", max_memory=3, htfint=83)
var Candle[] candlesadd83                  = array.new<Candle>(0)
var BOSdata bosdataadd83                   = BOSdata.new()
htfadd83.settings                 := SettingsHTFadd83
htfadd83.candles                  := candlesadd83
htfadd83.bosdata                  := bosdataadd83
var CandleSet htfadd84                     = CandleSet.new()
var CandleSettings SettingsHTFadd84        = CandleSettings.new(htf="84", max_memory=3, htfint=84)
var Candle[] candlesadd84                  = array.new<Candle>(0)
var BOSdata bosdataadd84                   = BOSdata.new()
htfadd84.settings                 := SettingsHTFadd84
htfadd84.candles                  := candlesadd84
htfadd84.bosdata                  := bosdataadd84
var CandleSet htfadd85                     = CandleSet.new()
var CandleSettings SettingsHTFadd85        = CandleSettings.new(htf="85", max_memory=3, htfint=85)
var Candle[] candlesadd85                  = array.new<Candle>(0)
var BOSdata bosdataadd85                   = BOSdata.new()
htfadd85.settings                 := SettingsHTFadd85
htfadd85.candles                  := candlesadd85
htfadd85.bosdata                  := bosdataadd85
var CandleSet htfadd86                     = CandleSet.new()
var CandleSettings SettingsHTFadd86        = CandleSettings.new(htf="86", max_memory=3, htfint=86)
var Candle[] candlesadd86                  = array.new<Candle>(0)
var BOSdata bosdataadd86                   = BOSdata.new()
htfadd86.settings                 := SettingsHTFadd86
htfadd86.candles                  := candlesadd86
htfadd86.bosdata                  := bosdataadd86
var CandleSet htfadd87                     = CandleSet.new()
var CandleSettings SettingsHTFadd87        = CandleSettings.new(htf="87", max_memory=3, htfint=87)
var Candle[] candlesadd87                  = array.new<Candle>(0)
var BOSdata bosdataadd87                   = BOSdata.new()
htfadd87.settings                 := SettingsHTFadd87
htfadd87.candles                  := candlesadd87
htfadd87.bosdata                  := bosdataadd87
var CandleSet htfadd88                     = CandleSet.new()
var CandleSettings SettingsHTFadd88        = CandleSettings.new(htf="88", max_memory=3, htfint=88)
var Candle[] candlesadd88                  = array.new<Candle>(0)
var BOSdata bosdataadd88                   = BOSdata.new()
htfadd88.settings                 := SettingsHTFadd88
htfadd88.candles                  := candlesadd88
htfadd88.bosdata                  := bosdataadd88
var CandleSet htfadd89                     = CandleSet.new()
var CandleSettings SettingsHTFadd89        = CandleSettings.new(htf="89", max_memory=3, htfint=89)
var Candle[] candlesadd89                  = array.new<Candle>(0)
var BOSdata bosdataadd89                   = BOSdata.new()
htfadd89.settings                 := SettingsHTFadd89
htfadd89.candles                  := candlesadd89
htfadd89.bosdata                  := bosdataadd89
var CandleSet htfadd90                     = CandleSet.new()
var CandleSettings SettingsHTFadd90        = CandleSettings.new(htf="90", max_memory=3, htfint=90)
var Candle[] candlesadd90                  = array.new<Candle>(0)
var BOSdata bosdataadd90                   = BOSdata.new()
htfadd90.settings                 := SettingsHTFadd90
htfadd90.candles                  := candlesadd90
htfadd90.bosdata                  := bosdataadd90


htfadd1.HTFAddValidCheck().Monitor().BOSJudge()
htfadd2.HTFAddValidCheck().Monitor().BOSJudge()
htfadd3.HTFAddValidCheck().Monitor().BOSJudge()
htfadd4.HTFAddValidCheck().Monitor().BOSJudge()
htfadd5.HTFAddValidCheck().Monitor().BOSJudge()
htfadd6.HTFAddValidCheck().Monitor().BOSJudge()
htfadd7.HTFAddValidCheck().Monitor().BOSJudge()
htfadd8.HTFAddValidCheck().Monitor().BOSJudge()
htfadd9.HTFAddValidCheck().Monitor().BOSJudge()
htfadd10.HTFAddValidCheck().Monitor().BOSJudge()
htfadd11.HTFAddValidCheck().Monitor().BOSJudge()
htfadd12.HTFAddValidCheck().Monitor().BOSJudge()
htfadd13.HTFAddValidCheck().Monitor().BOSJudge()
htfadd14.HTFAddValidCheck().Monitor().BOSJudge()
htfadd15.HTFAddValidCheck().Monitor().BOSJudge()
htfadd16.HTFAddValidCheck().Monitor().BOSJudge()
htfadd17.HTFAddValidCheck().Monitor().BOSJudge()
htfadd18.HTFAddValidCheck().Monitor().BOSJudge()
htfadd19.HTFAddValidCheck().Monitor().BOSJudge()
htfadd20.HTFAddValidCheck().Monitor().BOSJudge()
htfadd21.HTFAddValidCheck().Monitor().BOSJudge()
htfadd22.HTFAddValidCheck().Monitor().BOSJudge()
htfadd23.HTFAddValidCheck().Monitor().BOSJudge()
htfadd24.HTFAddValidCheck().Monitor().BOSJudge()
htfadd25.HTFAddValidCheck().Monitor().BOSJudge()
htfadd26.HTFAddValidCheck().Monitor().BOSJudge()
htfadd27.HTFAddValidCheck().Monitor().BOSJudge()
htfadd28.HTFAddValidCheck().Monitor().BOSJudge()
htfadd29.HTFAddValidCheck().Monitor().BOSJudge()
htfadd30.HTFAddValidCheck().Monitor().BOSJudge()
htfadd31.HTFAddValidCheck().Monitor().BOSJudge()
htfadd32.HTFAddValidCheck().Monitor().BOSJudge()
htfadd33.HTFAddValidCheck().Monitor().BOSJudge()
htfadd34.HTFAddValidCheck().Monitor().BOSJudge()
htfadd35.HTFAddValidCheck().Monitor().BOSJudge()
htfadd36.HTFAddValidCheck().Monitor().BOSJudge()
htfadd37.HTFAddValidCheck().Monitor().BOSJudge()
htfadd38.HTFAddValidCheck().Monitor().BOSJudge()
htfadd39.HTFAddValidCheck().Monitor().BOSJudge()
htfadd40.HTFAddValidCheck().Monitor().BOSJudge()
htfadd41.HTFAddValidCheck().Monitor().BOSJudge()
htfadd42.HTFAddValidCheck().Monitor().BOSJudge()
htfadd43.HTFAddValidCheck().Monitor().BOSJudge()
htfadd44.HTFAddValidCheck().Monitor().BOSJudge()
htfadd45.HTFAddValidCheck().Monitor().BOSJudge()
htfadd46.HTFAddValidCheck().Monitor().BOSJudge()
htfadd47.HTFAddValidCheck().Monitor().BOSJudge()
htfadd48.HTFAddValidCheck().Monitor().BOSJudge()
htfadd49.HTFAddValidCheck().Monitor().BOSJudge()
htfadd50.HTFAddValidCheck().Monitor().BOSJudge()
htfadd51.HTFAddValidCheck().Monitor().BOSJudge()
htfadd52.HTFAddValidCheck().Monitor().BOSJudge()
htfadd53.HTFAddValidCheck().Monitor().BOSJudge()
htfadd54.HTFAddValidCheck().Monitor().BOSJudge()
htfadd55.HTFAddValidCheck().Monitor().BOSJudge()
htfadd56.HTFAddValidCheck().Monitor().BOSJudge()
htfadd57.HTFAddValidCheck().Monitor().BOSJudge()
htfadd58.HTFAddValidCheck().Monitor().BOSJudge()
htfadd59.HTFAddValidCheck().Monitor().BOSJudge()
htfadd60.HTFAddValidCheck().Monitor().BOSJudge()
htfadd61.HTFAddValidCheck().Monitor().BOSJudge()
htfadd62.HTFAddValidCheck().Monitor().BOSJudge()
htfadd63.HTFAddValidCheck().Monitor().BOSJudge()
htfadd64.HTFAddValidCheck().Monitor().BOSJudge()
htfadd65.HTFAddValidCheck().Monitor().BOSJudge()
htfadd66.HTFAddValidCheck().Monitor().BOSJudge()
htfadd67.HTFAddValidCheck().Monitor().BOSJudge()
htfadd68.HTFAddValidCheck().Monitor().BOSJudge()
htfadd69.HTFAddValidCheck().Monitor().BOSJudge()
htfadd70.HTFAddValidCheck().Monitor().BOSJudge()
htfadd71.HTFAddValidCheck().Monitor().BOSJudge()
htfadd72.HTFAddValidCheck().Monitor().BOSJudge()
htfadd73.HTFAddValidCheck().Monitor().BOSJudge()
htfadd74.HTFAddValidCheck().Monitor().BOSJudge()
htfadd75.HTFAddValidCheck().Monitor().BOSJudge()
htfadd76.HTFAddValidCheck().Monitor().BOSJudge()
htfadd77.HTFAddValidCheck().Monitor().BOSJudge()
htfadd78.HTFAddValidCheck().Monitor().BOSJudge()
htfadd79.HTFAddValidCheck().Monitor().BOSJudge()
htfadd80.HTFAddValidCheck().Monitor().BOSJudge()
htfadd81.HTFAddValidCheck().Monitor().BOSJudge()
htfadd82.HTFAddValidCheck().Monitor().BOSJudge()
htfadd83.HTFAddValidCheck().Monitor().BOSJudge()
htfadd84.HTFAddValidCheck().Monitor().BOSJudge()
htfadd85.HTFAddValidCheck().Monitor().BOSJudge()
htfadd86.HTFAddValidCheck().Monitor().BOSJudge()
htfadd87.HTFAddValidCheck().Monitor().BOSJudge()
htfadd88.HTFAddValidCheck().Monitor().BOSJudge()
htfadd89.HTFAddValidCheck().Monitor().BOSJudge()
htfadd90.HTFAddValidCheck().Monitor().BOSJudge()


if bar_index == last_bar_index - 1
    HighestsbdSet(highestsbd, htfadd1)
    LowestsbuSet(lowestsbu, htfadd1) 
    HighestsbdSet(highestsbd, htfadd2)
    LowestsbuSet(lowestsbu, htfadd2) 
    HighestsbdSet(highestsbd, htfadd3)
    LowestsbuSet(lowestsbu, htfadd3) 
    HighestsbdSet(highestsbd, htfadd4)
    LowestsbuSet(lowestsbu, htfadd4) 
    HighestsbdSet(highestsbd, htfadd5)
    LowestsbuSet(lowestsbu, htfadd5) 
    HighestsbdSet(highestsbd, htfadd6)
    LowestsbuSet(lowestsbu, htfadd6) 
    HighestsbdSet(highestsbd, htfadd7)
    LowestsbuSet(lowestsbu, htfadd7) 
    HighestsbdSet(highestsbd, htfadd8)
    LowestsbuSet(lowestsbu, htfadd8) 
    HighestsbdSet(highestsbd, htfadd9)
    LowestsbuSet(lowestsbu, htfadd9) 
    HighestsbdSet(highestsbd, htfadd10)
    LowestsbuSet(lowestsbu, htfadd10) 
    HighestsbdSet(highestsbd, htfadd11)
    LowestsbuSet(lowestsbu, htfadd11) 
    HighestsbdSet(highestsbd, htfadd12)
    LowestsbuSet(lowestsbu, htfadd12) 
    HighestsbdSet(highestsbd, htfadd13)
    LowestsbuSet(lowestsbu, htfadd13) 
    HighestsbdSet(highestsbd, htfadd14)
    LowestsbuSet(lowestsbu, htfadd14) 
    HighestsbdSet(highestsbd, htfadd15)
    LowestsbuSet(lowestsbu, htfadd15) 
    HighestsbdSet(highestsbd, htfadd16)
    LowestsbuSet(lowestsbu, htfadd16) 
    HighestsbdSet(highestsbd, htfadd17)
    LowestsbuSet(lowestsbu, htfadd17) 
    HighestsbdSet(highestsbd, htfadd18)
    LowestsbuSet(lowestsbu, htfadd18) 
    HighestsbdSet(highestsbd, htfadd19)
    LowestsbuSet(lowestsbu, htfadd19) 
    HighestsbdSet(highestsbd, htfadd20)
    LowestsbuSet(lowestsbu, htfadd20) 
    HighestsbdSet(highestsbd, htfadd21)
    LowestsbuSet(lowestsbu, htfadd21) 
    HighestsbdSet(highestsbd, htfadd22)
    LowestsbuSet(lowestsbu, htfadd22) 
    HighestsbdSet(highestsbd, htfadd23)
    LowestsbuSet(lowestsbu, htfadd23) 
    HighestsbdSet(highestsbd, htfadd24)
    LowestsbuSet(lowestsbu, htfadd24) 
    HighestsbdSet(highestsbd, htfadd25)
    LowestsbuSet(lowestsbu, htfadd25) 
    HighestsbdSet(highestsbd, htfadd26)
    LowestsbuSet(lowestsbu, htfadd26) 
    HighestsbdSet(highestsbd, htfadd27)
    LowestsbuSet(lowestsbu, htfadd27) 
    HighestsbdSet(highestsbd, htfadd28)
    LowestsbuSet(lowestsbu, htfadd28) 
    HighestsbdSet(highestsbd, htfadd29)
    LowestsbuSet(lowestsbu, htfadd29) 
    HighestsbdSet(highestsbd, htfadd30)
    LowestsbuSet(lowestsbu, htfadd30) 
    HighestsbdSet(highestsbd, htfadd31)
    LowestsbuSet(lowestsbu, htfadd31) 
    HighestsbdSet(highestsbd, htfadd32)
    LowestsbuSet(lowestsbu, htfadd32) 
    HighestsbdSet(highestsbd, htfadd33)
    LowestsbuSet(lowestsbu, htfadd33) 
    HighestsbdSet(highestsbd, htfadd34)
    LowestsbuSet(lowestsbu, htfadd34) 
    HighestsbdSet(highestsbd, htfadd35)
    LowestsbuSet(lowestsbu, htfadd35) 
    HighestsbdSet(highestsbd, htfadd36)
    LowestsbuSet(lowestsbu, htfadd36) 
    HighestsbdSet(highestsbd, htfadd37)
    LowestsbuSet(lowestsbu, htfadd37) 
    HighestsbdSet(highestsbd, htfadd38)
    LowestsbuSet(lowestsbu, htfadd38) 
    HighestsbdSet(highestsbd, htfadd39)
    LowestsbuSet(lowestsbu, htfadd39) 
    HighestsbdSet(highestsbd, htfadd40)
    LowestsbuSet(lowestsbu, htfadd40) 
    HighestsbdSet(highestsbd, htfadd41)
    LowestsbuSet(lowestsbu, htfadd41) 
    HighestsbdSet(highestsbd, htfadd42)
    LowestsbuSet(lowestsbu, htfadd42) 
    HighestsbdSet(highestsbd, htfadd43)
    LowestsbuSet(lowestsbu, htfadd43) 
    HighestsbdSet(highestsbd, htfadd44)
    LowestsbuSet(lowestsbu, htfadd44) 
    HighestsbdSet(highestsbd, htfadd45)
    LowestsbuSet(lowestsbu, htfadd45) 
    HighestsbdSet(highestsbd, htfadd46)
    LowestsbuSet(lowestsbu, htfadd46) 
    HighestsbdSet(highestsbd, htfadd47)
    LowestsbuSet(lowestsbu, htfadd47) 
    HighestsbdSet(highestsbd, htfadd48)
    LowestsbuSet(lowestsbu, htfadd48) 
    HighestsbdSet(highestsbd, htfadd49)
    LowestsbuSet(lowestsbu, htfadd49) 
    HighestsbdSet(highestsbd, htfadd50)
    LowestsbuSet(lowestsbu, htfadd50) 
    HighestsbdSet(highestsbd, htfadd51)
    LowestsbuSet(lowestsbu, htfadd51) 
    HighestsbdSet(highestsbd, htfadd52)
    LowestsbuSet(lowestsbu, htfadd52) 
    HighestsbdSet(highestsbd, htfadd53)
    LowestsbuSet(lowestsbu, htfadd53) 
    HighestsbdSet(highestsbd, htfadd54)
    LowestsbuSet(lowestsbu, htfadd54) 
    HighestsbdSet(highestsbd, htfadd55)
    LowestsbuSet(lowestsbu, htfadd55) 
    HighestsbdSet(highestsbd, htfadd56)
    LowestsbuSet(lowestsbu, htfadd56) 
    HighestsbdSet(highestsbd, htfadd57)
    LowestsbuSet(lowestsbu, htfadd57) 
    HighestsbdSet(highestsbd, htfadd58)
    LowestsbuSet(lowestsbu, htfadd58) 
    HighestsbdSet(highestsbd, htfadd59)
    LowestsbuSet(lowestsbu, htfadd59) 
    HighestsbdSet(highestsbd, htfadd60)
    LowestsbuSet(lowestsbu, htfadd60) 
    HighestsbdSet(highestsbd, htfadd61)
    LowestsbuSet(lowestsbu, htfadd61) 
    HighestsbdSet(highestsbd, htfadd62)
    LowestsbuSet(lowestsbu, htfadd62) 
    HighestsbdSet(highestsbd, htfadd63)
    LowestsbuSet(lowestsbu, htfadd63) 
    HighestsbdSet(highestsbd, htfadd64)
    LowestsbuSet(lowestsbu, htfadd64) 
    HighestsbdSet(highestsbd, htfadd65)
    LowestsbuSet(lowestsbu, htfadd65) 
    HighestsbdSet(highestsbd, htfadd66)
    LowestsbuSet(lowestsbu, htfadd66) 
    HighestsbdSet(highestsbd, htfadd67)
    LowestsbuSet(lowestsbu, htfadd67) 
    HighestsbdSet(highestsbd, htfadd68)
    LowestsbuSet(lowestsbu, htfadd68) 
    HighestsbdSet(highestsbd, htfadd69)
    LowestsbuSet(lowestsbu, htfadd69) 
    HighestsbdSet(highestsbd, htfadd70)
    LowestsbuSet(lowestsbu, htfadd70) 
    HighestsbdSet(highestsbd, htfadd71)
    LowestsbuSet(lowestsbu, htfadd71) 
    HighestsbdSet(highestsbd, htfadd72)
    LowestsbuSet(lowestsbu, htfadd72) 
    HighestsbdSet(highestsbd, htfadd73)
    LowestsbuSet(lowestsbu, htfadd73) 
    HighestsbdSet(highestsbd, htfadd74)
    LowestsbuSet(lowestsbu, htfadd74) 
    HighestsbdSet(highestsbd, htfadd75)
    LowestsbuSet(lowestsbu, htfadd75) 
    HighestsbdSet(highestsbd, htfadd76)
    LowestsbuSet(lowestsbu, htfadd76) 
    HighestsbdSet(highestsbd, htfadd77)
    LowestsbuSet(lowestsbu, htfadd77) 
    HighestsbdSet(highestsbd, htfadd78)
    LowestsbuSet(lowestsbu, htfadd78) 
    HighestsbdSet(highestsbd, htfadd79)
    LowestsbuSet(lowestsbu, htfadd79) 
    HighestsbdSet(highestsbd, htfadd80)
    LowestsbuSet(lowestsbu, htfadd80) 
    HighestsbdSet(highestsbd, htfadd81)
    LowestsbuSet(lowestsbu, htfadd81) 
    HighestsbdSet(highestsbd, htfadd82)
    LowestsbuSet(lowestsbu, htfadd82) 
    HighestsbdSet(highestsbd, htfadd83)
    LowestsbuSet(lowestsbu, htfadd83) 
    HighestsbdSet(highestsbd, htfadd84)
    LowestsbuSet(lowestsbu, htfadd84) 
    HighestsbdSet(highestsbd, htfadd85)
    LowestsbuSet(lowestsbu, htfadd85) 
    HighestsbdSet(highestsbd, htfadd86)
    LowestsbuSet(lowestsbu, htfadd86) 
    HighestsbdSet(highestsbd, htfadd87)
    LowestsbuSet(lowestsbu, htfadd87) 
    HighestsbdSet(highestsbd, htfadd88)
    LowestsbuSet(lowestsbu, htfadd88) 
    HighestsbdSet(highestsbd, htfadd89)
    LowestsbuSet(lowestsbu, htfadd89) 
    HighestsbdSet(highestsbd, htfadd90)
    LowestsbuSet(lowestsbu, htfadd90) 

if barstate.islast or barstate.isrealtime
    HighestsbdSet(highestsbd, htfadd1)
    LowestsbuSet(lowestsbu, htfadd1) 
    HighestsbdSet(highestsbd, htfadd2)
    LowestsbuSet(lowestsbu, htfadd2) 
    HighestsbdSet(highestsbd, htfadd3)
    LowestsbuSet(lowestsbu, htfadd3) 
    HighestsbdSet(highestsbd, htfadd4)
    LowestsbuSet(lowestsbu, htfadd4) 
    HighestsbdSet(highestsbd, htfadd5)
    LowestsbuSet(lowestsbu, htfadd5) 
    HighestsbdSet(highestsbd, htfadd6)
    LowestsbuSet(lowestsbu, htfadd6) 
    HighestsbdSet(highestsbd, htfadd7)
    LowestsbuSet(lowestsbu, htfadd7) 
    HighestsbdSet(highestsbd, htfadd8)
    LowestsbuSet(lowestsbu, htfadd8) 
    HighestsbdSet(highestsbd, htfadd9)
    LowestsbuSet(lowestsbu, htfadd9) 
    HighestsbdSet(highestsbd, htfadd10)
    LowestsbuSet(lowestsbu, htfadd10) 
    HighestsbdSet(highestsbd, htfadd11)
    LowestsbuSet(lowestsbu, htfadd11) 
    HighestsbdSet(highestsbd, htfadd12)
    LowestsbuSet(lowestsbu, htfadd12) 
    HighestsbdSet(highestsbd, htfadd13)
    LowestsbuSet(lowestsbu, htfadd13) 
    HighestsbdSet(highestsbd, htfadd14)
    LowestsbuSet(lowestsbu, htfadd14) 
    HighestsbdSet(highestsbd, htfadd15)
    LowestsbuSet(lowestsbu, htfadd15) 
    HighestsbdSet(highestsbd, htfadd16)
    LowestsbuSet(lowestsbu, htfadd16) 
    HighestsbdSet(highestsbd, htfadd17)
    LowestsbuSet(lowestsbu, htfadd17) 
    HighestsbdSet(highestsbd, htfadd18)
    LowestsbuSet(lowestsbu, htfadd18) 
    HighestsbdSet(highestsbd, htfadd19)
    LowestsbuSet(lowestsbu, htfadd19) 
    HighestsbdSet(highestsbd, htfadd20)
    LowestsbuSet(lowestsbu, htfadd20) 
    HighestsbdSet(highestsbd, htfadd21)
    LowestsbuSet(lowestsbu, htfadd21) 
    HighestsbdSet(highestsbd, htfadd22)
    LowestsbuSet(lowestsbu, htfadd22) 
    HighestsbdSet(highestsbd, htfadd23)
    LowestsbuSet(lowestsbu, htfadd23) 
    HighestsbdSet(highestsbd, htfadd24)
    LowestsbuSet(lowestsbu, htfadd24) 
    HighestsbdSet(highestsbd, htfadd25)
    LowestsbuSet(lowestsbu, htfadd25) 
    HighestsbdSet(highestsbd, htfadd26)
    LowestsbuSet(lowestsbu, htfadd26) 
    HighestsbdSet(highestsbd, htfadd27)
    LowestsbuSet(lowestsbu, htfadd27) 
    HighestsbdSet(highestsbd, htfadd28)
    LowestsbuSet(lowestsbu, htfadd28) 
    HighestsbdSet(highestsbd, htfadd29)
    LowestsbuSet(lowestsbu, htfadd29) 
    HighestsbdSet(highestsbd, htfadd30)
    LowestsbuSet(lowestsbu, htfadd30) 
    HighestsbdSet(highestsbd, htfadd31)
    LowestsbuSet(lowestsbu, htfadd31) 
    HighestsbdSet(highestsbd, htfadd32)
    LowestsbuSet(lowestsbu, htfadd32) 
    HighestsbdSet(highestsbd, htfadd33)
    LowestsbuSet(lowestsbu, htfadd33) 
    HighestsbdSet(highestsbd, htfadd34)
    LowestsbuSet(lowestsbu, htfadd34) 
    HighestsbdSet(highestsbd, htfadd35)
    LowestsbuSet(lowestsbu, htfadd35) 
    HighestsbdSet(highestsbd, htfadd36)
    LowestsbuSet(lowestsbu, htfadd36) 
    HighestsbdSet(highestsbd, htfadd37)
    LowestsbuSet(lowestsbu, htfadd37) 
    HighestsbdSet(highestsbd, htfadd38)
    LowestsbuSet(lowestsbu, htfadd38) 
    HighestsbdSet(highestsbd, htfadd39)
    LowestsbuSet(lowestsbu, htfadd39) 
    HighestsbdSet(highestsbd, htfadd40)
    LowestsbuSet(lowestsbu, htfadd40) 
    HighestsbdSet(highestsbd, htfadd41)
    LowestsbuSet(lowestsbu, htfadd41) 
    HighestsbdSet(highestsbd, htfadd42)
    LowestsbuSet(lowestsbu, htfadd42) 
    HighestsbdSet(highestsbd, htfadd43)
    LowestsbuSet(lowestsbu, htfadd43) 
    HighestsbdSet(highestsbd, htfadd44)
    LowestsbuSet(lowestsbu, htfadd44) 
    HighestsbdSet(highestsbd, htfadd45)
    LowestsbuSet(lowestsbu, htfadd45) 
    HighestsbdSet(highestsbd, htfadd46)
    LowestsbuSet(lowestsbu, htfadd46) 
    HighestsbdSet(highestsbd, htfadd47)
    LowestsbuSet(lowestsbu, htfadd47) 
    HighestsbdSet(highestsbd, htfadd48)
    LowestsbuSet(lowestsbu, htfadd48) 
    HighestsbdSet(highestsbd, htfadd49)
    LowestsbuSet(lowestsbu, htfadd49) 
    HighestsbdSet(highestsbd, htfadd50)
    LowestsbuSet(lowestsbu, htfadd50) 
    HighestsbdSet(highestsbd, htfadd51)
    LowestsbuSet(lowestsbu, htfadd51) 
    HighestsbdSet(highestsbd, htfadd52)
    LowestsbuSet(lowestsbu, htfadd52) 
    HighestsbdSet(highestsbd, htfadd53)
    LowestsbuSet(lowestsbu, htfadd53) 
    HighestsbdSet(highestsbd, htfadd54)
    LowestsbuSet(lowestsbu, htfadd54) 
    HighestsbdSet(highestsbd, htfadd55)
    LowestsbuSet(lowestsbu, htfadd55) 
    HighestsbdSet(highestsbd, htfadd56)
    LowestsbuSet(lowestsbu, htfadd56) 
    HighestsbdSet(highestsbd, htfadd57)
    LowestsbuSet(lowestsbu, htfadd57) 
    HighestsbdSet(highestsbd, htfadd58)
    LowestsbuSet(lowestsbu, htfadd58) 
    HighestsbdSet(highestsbd, htfadd59)
    LowestsbuSet(lowestsbu, htfadd59) 
    HighestsbdSet(highestsbd, htfadd60)
    LowestsbuSet(lowestsbu, htfadd60) 
    HighestsbdSet(highestsbd, htfadd61)
    LowestsbuSet(lowestsbu, htfadd61) 
    HighestsbdSet(highestsbd, htfadd62)
    LowestsbuSet(lowestsbu, htfadd62) 
    HighestsbdSet(highestsbd, htfadd63)
    LowestsbuSet(lowestsbu, htfadd63) 
    HighestsbdSet(highestsbd, htfadd64)
    LowestsbuSet(lowestsbu, htfadd64) 
    HighestsbdSet(highestsbd, htfadd65)
    LowestsbuSet(lowestsbu, htfadd65) 
    HighestsbdSet(highestsbd, htfadd66)
    LowestsbuSet(lowestsbu, htfadd66) 
    HighestsbdSet(highestsbd, htfadd67)
    LowestsbuSet(lowestsbu, htfadd67) 
    HighestsbdSet(highestsbd, htfadd68)
    LowestsbuSet(lowestsbu, htfadd68) 
    HighestsbdSet(highestsbd, htfadd69)
    LowestsbuSet(lowestsbu, htfadd69) 
    HighestsbdSet(highestsbd, htfadd70)
    LowestsbuSet(lowestsbu, htfadd70) 
    HighestsbdSet(highestsbd, htfadd71)
    LowestsbuSet(lowestsbu, htfadd71) 
    HighestsbdSet(highestsbd, htfadd72)
    LowestsbuSet(lowestsbu, htfadd72) 
    HighestsbdSet(highestsbd, htfadd73)
    LowestsbuSet(lowestsbu, htfadd73) 
    HighestsbdSet(highestsbd, htfadd74)
    LowestsbuSet(lowestsbu, htfadd74) 
    HighestsbdSet(highestsbd, htfadd75)
    LowestsbuSet(lowestsbu, htfadd75) 
    HighestsbdSet(highestsbd, htfadd76)
    LowestsbuSet(lowestsbu, htfadd76) 
    HighestsbdSet(highestsbd, htfadd77)
    LowestsbuSet(lowestsbu, htfadd77) 
    HighestsbdSet(highestsbd, htfadd78)
    LowestsbuSet(lowestsbu, htfadd78) 
    HighestsbdSet(highestsbd, htfadd79)
    LowestsbuSet(lowestsbu, htfadd79) 
    HighestsbdSet(highestsbd, htfadd80)
    LowestsbuSet(lowestsbu, htfadd80) 
    HighestsbdSet(highestsbd, htfadd81)
    LowestsbuSet(lowestsbu, htfadd81) 
    HighestsbdSet(highestsbd, htfadd82)
    LowestsbuSet(lowestsbu, htfadd82) 
    HighestsbdSet(highestsbd, htfadd83)
    LowestsbuSet(lowestsbu, htfadd83) 
    HighestsbdSet(highestsbd, htfadd84)
    LowestsbuSet(lowestsbu, htfadd84) 
    HighestsbdSet(highestsbd, htfadd85)
    LowestsbuSet(lowestsbu, htfadd85) 
    HighestsbdSet(highestsbd, htfadd86)
    LowestsbuSet(lowestsbu, htfadd86) 
    HighestsbdSet(highestsbd, htfadd87)
    LowestsbuSet(lowestsbu, htfadd87) 
    HighestsbdSet(highestsbd, htfadd88)
    LowestsbuSet(lowestsbu, htfadd88) 
    HighestsbdSet(highestsbd, htfadd89)
    LowestsbuSet(lowestsbu, htfadd89) 
    HighestsbdSet(highestsbd, htfadd90)
    LowestsbuSet(lowestsbu, htfadd90) 
    
    Predictor(htfadd1, estminsbu)
    Predictor(htfadd1, estmaxsbd)  
    Predictor(htfadd2, estminsbu)
    Predictor(htfadd2, estmaxsbd)  
    Predictor(htfadd3, estminsbu)
    Predictor(htfadd3, estmaxsbd)  
    Predictor(htfadd4, estminsbu)
    Predictor(htfadd4, estmaxsbd)  
    Predictor(htfadd5, estminsbu)
    Predictor(htfadd5, estmaxsbd)  
    Predictor(htfadd6, estminsbu)
    Predictor(htfadd6, estmaxsbd)  
    Predictor(htfadd7, estminsbu)
    Predictor(htfadd7, estmaxsbd)  
    Predictor(htfadd8, estminsbu)
    Predictor(htfadd8, estmaxsbd)  
    Predictor(htfadd9, estminsbu)
    Predictor(htfadd9, estmaxsbd)  
    Predictor(htfadd10, estminsbu)
    Predictor(htfadd10, estmaxsbd)  
    Predictor(htfadd11, estminsbu)
    Predictor(htfadd11, estmaxsbd)  
    Predictor(htfadd12, estminsbu)
    Predictor(htfadd12, estmaxsbd)  
    Predictor(htfadd13, estminsbu)
    Predictor(htfadd13, estmaxsbd)  
    Predictor(htfadd14, estminsbu)
    Predictor(htfadd14, estmaxsbd)  
    Predictor(htfadd15, estminsbu)
    Predictor(htfadd15, estmaxsbd)  
    Predictor(htfadd16, estminsbu)
    Predictor(htfadd16, estmaxsbd)  
    Predictor(htfadd17, estminsbu)
    Predictor(htfadd17, estmaxsbd)  
    Predictor(htfadd18, estminsbu)
    Predictor(htfadd18, estmaxsbd)  
    Predictor(htfadd19, estminsbu)
    Predictor(htfadd19, estmaxsbd)  
    Predictor(htfadd20, estminsbu)
    Predictor(htfadd20, estmaxsbd)  
    Predictor(htfadd21, estminsbu)
    Predictor(htfadd21, estmaxsbd)  
    Predictor(htfadd22, estminsbu)
    Predictor(htfadd22, estmaxsbd)  
    Predictor(htfadd23, estminsbu)
    Predictor(htfadd23, estmaxsbd)  
    Predictor(htfadd24, estminsbu)
    Predictor(htfadd24, estmaxsbd)  
    Predictor(htfadd25, estminsbu)
    Predictor(htfadd25, estmaxsbd)  
    Predictor(htfadd26, estminsbu)
    Predictor(htfadd26, estmaxsbd)  
    Predictor(htfadd27, estminsbu)
    Predictor(htfadd27, estmaxsbd)  
    Predictor(htfadd28, estminsbu)
    Predictor(htfadd28, estmaxsbd)  
    Predictor(htfadd29, estminsbu)
    Predictor(htfadd29, estmaxsbd)  
    Predictor(htfadd30, estminsbu)
    Predictor(htfadd30, estmaxsbd)  
    Predictor(htfadd31, estminsbu)
    Predictor(htfadd31, estmaxsbd)  
    Predictor(htfadd32, estminsbu)
    Predictor(htfadd32, estmaxsbd)  
    Predictor(htfadd33, estminsbu)
    Predictor(htfadd33, estmaxsbd)  
    Predictor(htfadd34, estminsbu)
    Predictor(htfadd34, estmaxsbd)  
    Predictor(htfadd35, estminsbu)
    Predictor(htfadd35, estmaxsbd)  
    Predictor(htfadd36, estminsbu)
    Predictor(htfadd36, estmaxsbd)  
    Predictor(htfadd37, estminsbu)
    Predictor(htfadd37, estmaxsbd)  
    Predictor(htfadd38, estminsbu)
    Predictor(htfadd38, estmaxsbd)  
    Predictor(htfadd39, estminsbu)
    Predictor(htfadd39, estmaxsbd)  
    Predictor(htfadd40, estminsbu)
    Predictor(htfadd40, estmaxsbd)  
    Predictor(htfadd41, estminsbu)
    Predictor(htfadd41, estmaxsbd)  
    Predictor(htfadd42, estminsbu)
    Predictor(htfadd42, estmaxsbd)  
    Predictor(htfadd43, estminsbu)
    Predictor(htfadd43, estmaxsbd)  
    Predictor(htfadd44, estminsbu)
    Predictor(htfadd44, estmaxsbd)  
    Predictor(htfadd45, estminsbu)
    Predictor(htfadd45, estmaxsbd)  
    Predictor(htfadd46, estminsbu)
    Predictor(htfadd46, estmaxsbd)  
    Predictor(htfadd47, estminsbu)
    Predictor(htfadd47, estmaxsbd)  
    Predictor(htfadd48, estminsbu)
    Predictor(htfadd48, estmaxsbd)  
    Predictor(htfadd49, estminsbu)
    Predictor(htfadd49, estmaxsbd)  
    Predictor(htfadd50, estminsbu)
    Predictor(htfadd50, estmaxsbd)  
    Predictor(htfadd51, estminsbu)
    Predictor(htfadd51, estmaxsbd)  
    Predictor(htfadd52, estminsbu)
    Predictor(htfadd52, estmaxsbd)  
    Predictor(htfadd53, estminsbu)
    Predictor(htfadd53, estmaxsbd)  
    Predictor(htfadd54, estminsbu)
    Predictor(htfadd54, estmaxsbd)  
    Predictor(htfadd55, estminsbu)
    Predictor(htfadd55, estmaxsbd)  
    Predictor(htfadd56, estminsbu)
    Predictor(htfadd56, estmaxsbd)  
    Predictor(htfadd57, estminsbu)
    Predictor(htfadd57, estmaxsbd)  
    Predictor(htfadd58, estminsbu)
    Predictor(htfadd58, estmaxsbd)  
    Predictor(htfadd59, estminsbu)
    Predictor(htfadd59, estmaxsbd)  
    Predictor(htfadd60, estminsbu)
    Predictor(htfadd60, estmaxsbd)  
    Predictor(htfadd61, estminsbu)
    Predictor(htfadd61, estmaxsbd)  
    Predictor(htfadd62, estminsbu)
    Predictor(htfadd62, estmaxsbd)  
    Predictor(htfadd63, estminsbu)
    Predictor(htfadd63, estmaxsbd)  
    Predictor(htfadd64, estminsbu)
    Predictor(htfadd64, estmaxsbd)  
    Predictor(htfadd65, estminsbu)
    Predictor(htfadd65, estmaxsbd)  
    Predictor(htfadd66, estminsbu)
    Predictor(htfadd66, estmaxsbd)  
    Predictor(htfadd67, estminsbu)
    Predictor(htfadd67, estmaxsbd)  
    Predictor(htfadd68, estminsbu)
    Predictor(htfadd68, estmaxsbd)  
    Predictor(htfadd69, estminsbu)
    Predictor(htfadd69, estmaxsbd)  
    Predictor(htfadd70, estminsbu)
    Predictor(htfadd70, estmaxsbd)  
    Predictor(htfadd71, estminsbu)
    Predictor(htfadd71, estmaxsbd)  
    Predictor(htfadd72, estminsbu)
    Predictor(htfadd72, estmaxsbd)  
    Predictor(htfadd73, estminsbu)
    Predictor(htfadd73, estmaxsbd)  
    Predictor(htfadd74, estminsbu)
    Predictor(htfadd74, estmaxsbd)  
    Predictor(htfadd75, estminsbu)
    Predictor(htfadd75, estmaxsbd)  
    Predictor(htfadd76, estminsbu)
    Predictor(htfadd76, estmaxsbd)  
    Predictor(htfadd77, estminsbu)
    Predictor(htfadd77, estmaxsbd)  
    Predictor(htfadd78, estminsbu)
    Predictor(htfadd78, estmaxsbd)  
    Predictor(htfadd79, estminsbu)
    Predictor(htfadd79, estmaxsbd)  
    Predictor(htfadd80, estminsbu)
    Predictor(htfadd80, estmaxsbd)  
    Predictor(htfadd81, estminsbu)
    Predictor(htfadd81, estmaxsbd)  
    Predictor(htfadd82, estminsbu)
    Predictor(htfadd82, estmaxsbd)  
    Predictor(htfadd83, estminsbu)
    Predictor(htfadd83, estmaxsbd)  
    Predictor(htfadd84, estminsbu)
    Predictor(htfadd84, estmaxsbd)  
    Predictor(htfadd85, estminsbu)
    Predictor(htfadd85, estmaxsbd)  
    Predictor(htfadd86, estminsbu)
    Predictor(htfadd86, estmaxsbd)  
    Predictor(htfadd87, estminsbu)
    Predictor(htfadd87, estmaxsbd)  
    Predictor(htfadd88, estminsbu)
    Predictor(htfadd88, estmaxsbd)  
    Predictor(htfadd89, estminsbu)
    Predictor(htfadd89, estmaxsbd)  
    Predictor(htfadd90, estminsbu)
    Predictor(htfadd90, estmaxsbd)  
       

//+---------------add var end------------------+//
if settings.add_show and barstate.isrealtime
    highestsbd.addplot(offset)
    lowestsbu.addplot(offset)
    estminsbu.addplot(offset)
    estmaxsbd.addplot(offset)

    var line nowcloseline = na
    if not na(nowcloseline)
        line.set_xy1(nowcloseline, bar_index, close)
        line.set_xy2(nowcloseline, bar_index+2, close)
    else
        nowcloseline := line.new(bar_index, close, bar_index, close, xloc= xloc.bar_index, color = color.new(color.gray, 10), style = line.style_dotted , width = 4)       
//if barstate.islast
//    label.new(bar_index,close, str.tostring(htfadd15.bosdata.sbu) + "\n" + str.tostring(htfadd15.bosdata.sbd) + "\n" + "hello")
//+---------------ADD END------------------+//

index += 1

