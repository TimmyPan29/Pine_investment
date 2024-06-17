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
var totaladdPeriod      = 60 //總共想要做幾條等差的週期?  預設60條 也可以1440條 但和間隔乘積不可以超過1440分鐘, 所以1440條的話 間隔要設定成1
var Interval            = 1  //間隔 也就是等差

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
    cs.settings.show := (cs.settings.htfint-InitialPeriod)%Interval==0? true : false
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
var CandleSet htfadd91                     = CandleSet.new()
var CandleSettings SettingsHTFadd91        = CandleSettings.new(htf="91", max_memory=3, htfint=91)
var Candle[] candlesadd91                  = array.new<Candle>(0)
var BOSdata bosdataadd91                   = BOSdata.new()
htfadd91.settings                 := SettingsHTFadd91
htfadd91.candles                  := candlesadd91
htfadd91.bosdata                  := bosdataadd91
var CandleSet htfadd92                     = CandleSet.new()
var CandleSettings SettingsHTFadd92        = CandleSettings.new(htf="92", max_memory=3, htfint=92)
var Candle[] candlesadd92                  = array.new<Candle>(0)
var BOSdata bosdataadd92                   = BOSdata.new()
htfadd92.settings                 := SettingsHTFadd92
htfadd92.candles                  := candlesadd92
htfadd92.bosdata                  := bosdataadd92
var CandleSet htfadd93                     = CandleSet.new()
var CandleSettings SettingsHTFadd93        = CandleSettings.new(htf="93", max_memory=3, htfint=93)
var Candle[] candlesadd93                  = array.new<Candle>(0)
var BOSdata bosdataadd93                   = BOSdata.new()
htfadd93.settings                 := SettingsHTFadd93
htfadd93.candles                  := candlesadd93
htfadd93.bosdata                  := bosdataadd93
var CandleSet htfadd94                     = CandleSet.new()
var CandleSettings SettingsHTFadd94        = CandleSettings.new(htf="94", max_memory=3, htfint=94)
var Candle[] candlesadd94                  = array.new<Candle>(0)
var BOSdata bosdataadd94                   = BOSdata.new()
htfadd94.settings                 := SettingsHTFadd94
htfadd94.candles                  := candlesadd94
htfadd94.bosdata                  := bosdataadd94
var CandleSet htfadd95                     = CandleSet.new()
var CandleSettings SettingsHTFadd95        = CandleSettings.new(htf="95", max_memory=3, htfint=95)
var Candle[] candlesadd95                  = array.new<Candle>(0)
var BOSdata bosdataadd95                   = BOSdata.new()
htfadd95.settings                 := SettingsHTFadd95
htfadd95.candles                  := candlesadd95
htfadd95.bosdata                  := bosdataadd95
var CandleSet htfadd96                     = CandleSet.new()
var CandleSettings SettingsHTFadd96        = CandleSettings.new(htf="96", max_memory=3, htfint=96)
var Candle[] candlesadd96                  = array.new<Candle>(0)
var BOSdata bosdataadd96                   = BOSdata.new()
htfadd96.settings                 := SettingsHTFadd96
htfadd96.candles                  := candlesadd96
htfadd96.bosdata                  := bosdataadd96
var CandleSet htfadd97                     = CandleSet.new()
var CandleSettings SettingsHTFadd97        = CandleSettings.new(htf="97", max_memory=3, htfint=97)
var Candle[] candlesadd97                  = array.new<Candle>(0)
var BOSdata bosdataadd97                   = BOSdata.new()
htfadd97.settings                 := SettingsHTFadd97
htfadd97.candles                  := candlesadd97
htfadd97.bosdata                  := bosdataadd97
var CandleSet htfadd98                     = CandleSet.new()
var CandleSettings SettingsHTFadd98        = CandleSettings.new(htf="98", max_memory=3, htfint=98)
var Candle[] candlesadd98                  = array.new<Candle>(0)
var BOSdata bosdataadd98                   = BOSdata.new()
htfadd98.settings                 := SettingsHTFadd98
htfadd98.candles                  := candlesadd98
htfadd98.bosdata                  := bosdataadd98
var CandleSet htfadd99                     = CandleSet.new()
var CandleSettings SettingsHTFadd99        = CandleSettings.new(htf="99", max_memory=3, htfint=99)
var Candle[] candlesadd99                  = array.new<Candle>(0)
var BOSdata bosdataadd99                   = BOSdata.new()
htfadd99.settings                 := SettingsHTFadd99
htfadd99.candles                  := candlesadd99
htfadd99.bosdata                  := bosdataadd99
var CandleSet htfadd100                     = CandleSet.new()
var CandleSettings SettingsHTFadd100        = CandleSettings.new(htf="100", max_memory=3, htfint=100)
var Candle[] candlesadd100                  = array.new<Candle>(0)
var BOSdata bosdataadd100                   = BOSdata.new()
htfadd100.settings                 := SettingsHTFadd100
htfadd100.candles                  := candlesadd100
htfadd100.bosdata                  := bosdataadd100
var CandleSet htfadd101                     = CandleSet.new()
var CandleSettings SettingsHTFadd101        = CandleSettings.new(htf="101", max_memory=3, htfint=101)
var Candle[] candlesadd101                  = array.new<Candle>(0)
var BOSdata bosdataadd101                   = BOSdata.new()
htfadd101.settings                 := SettingsHTFadd101
htfadd101.candles                  := candlesadd101
htfadd101.bosdata                  := bosdataadd101
var CandleSet htfadd102                     = CandleSet.new()
var CandleSettings SettingsHTFadd102        = CandleSettings.new(htf="102", max_memory=3, htfint=102)
var Candle[] candlesadd102                  = array.new<Candle>(0)
var BOSdata bosdataadd102                   = BOSdata.new()
htfadd102.settings                 := SettingsHTFadd102
htfadd102.candles                  := candlesadd102
htfadd102.bosdata                  := bosdataadd102
var CandleSet htfadd103                     = CandleSet.new()
var CandleSettings SettingsHTFadd103        = CandleSettings.new(htf="103", max_memory=3, htfint=103)
var Candle[] candlesadd103                  = array.new<Candle>(0)
var BOSdata bosdataadd103                   = BOSdata.new()
htfadd103.settings                 := SettingsHTFadd103
htfadd103.candles                  := candlesadd103
htfadd103.bosdata                  := bosdataadd103
var CandleSet htfadd104                     = CandleSet.new()
var CandleSettings SettingsHTFadd104        = CandleSettings.new(htf="104", max_memory=3, htfint=104)
var Candle[] candlesadd104                  = array.new<Candle>(0)
var BOSdata bosdataadd104                   = BOSdata.new()
htfadd104.settings                 := SettingsHTFadd104
htfadd104.candles                  := candlesadd104
htfadd104.bosdata                  := bosdataadd104
var CandleSet htfadd105                     = CandleSet.new()
var CandleSettings SettingsHTFadd105        = CandleSettings.new(htf="105", max_memory=3, htfint=105)
var Candle[] candlesadd105                  = array.new<Candle>(0)
var BOSdata bosdataadd105                   = BOSdata.new()
htfadd105.settings                 := SettingsHTFadd105
htfadd105.candles                  := candlesadd105
htfadd105.bosdata                  := bosdataadd105
var CandleSet htfadd106                     = CandleSet.new()
var CandleSettings SettingsHTFadd106        = CandleSettings.new(htf="106", max_memory=3, htfint=106)
var Candle[] candlesadd106                  = array.new<Candle>(0)
var BOSdata bosdataadd106                   = BOSdata.new()
htfadd106.settings                 := SettingsHTFadd106
htfadd106.candles                  := candlesadd106
htfadd106.bosdata                  := bosdataadd106
var CandleSet htfadd107                     = CandleSet.new()
var CandleSettings SettingsHTFadd107        = CandleSettings.new(htf="107", max_memory=3, htfint=107)
var Candle[] candlesadd107                  = array.new<Candle>(0)
var BOSdata bosdataadd107                   = BOSdata.new()
htfadd107.settings                 := SettingsHTFadd107
htfadd107.candles                  := candlesadd107
htfadd107.bosdata                  := bosdataadd107
var CandleSet htfadd108                     = CandleSet.new()
var CandleSettings SettingsHTFadd108        = CandleSettings.new(htf="108", max_memory=3, htfint=108)
var Candle[] candlesadd108                  = array.new<Candle>(0)
var BOSdata bosdataadd108                   = BOSdata.new()
htfadd108.settings                 := SettingsHTFadd108
htfadd108.candles                  := candlesadd108
htfadd108.bosdata                  := bosdataadd108
var CandleSet htfadd109                     = CandleSet.new()
var CandleSettings SettingsHTFadd109        = CandleSettings.new(htf="109", max_memory=3, htfint=109)
var Candle[] candlesadd109                  = array.new<Candle>(0)
var BOSdata bosdataadd109                   = BOSdata.new()
htfadd109.settings                 := SettingsHTFadd109
htfadd109.candles                  := candlesadd109
htfadd109.bosdata                  := bosdataadd109
var CandleSet htfadd110                     = CandleSet.new()
var CandleSettings SettingsHTFadd110        = CandleSettings.new(htf="110", max_memory=3, htfint=110)
var Candle[] candlesadd110                  = array.new<Candle>(0)
var BOSdata bosdataadd110                   = BOSdata.new()
htfadd110.settings                 := SettingsHTFadd110
htfadd110.candles                  := candlesadd110
htfadd110.bosdata                  := bosdataadd110
var CandleSet htfadd111                     = CandleSet.new()
var CandleSettings SettingsHTFadd111        = CandleSettings.new(htf="111", max_memory=3, htfint=111)
var Candle[] candlesadd111                  = array.new<Candle>(0)
var BOSdata bosdataadd111                   = BOSdata.new()
htfadd111.settings                 := SettingsHTFadd111
htfadd111.candles                  := candlesadd111
htfadd111.bosdata                  := bosdataadd111
var CandleSet htfadd112                     = CandleSet.new()
var CandleSettings SettingsHTFadd112        = CandleSettings.new(htf="112", max_memory=3, htfint=112)
var Candle[] candlesadd112                  = array.new<Candle>(0)
var BOSdata bosdataadd112                   = BOSdata.new()
htfadd112.settings                 := SettingsHTFadd112
htfadd112.candles                  := candlesadd112
htfadd112.bosdata                  := bosdataadd112
var CandleSet htfadd113                     = CandleSet.new()
var CandleSettings SettingsHTFadd113        = CandleSettings.new(htf="113", max_memory=3, htfint=113)
var Candle[] candlesadd113                  = array.new<Candle>(0)
var BOSdata bosdataadd113                   = BOSdata.new()
htfadd113.settings                 := SettingsHTFadd113
htfadd113.candles                  := candlesadd113
htfadd113.bosdata                  := bosdataadd113
var CandleSet htfadd114                     = CandleSet.new()
var CandleSettings SettingsHTFadd114        = CandleSettings.new(htf="114", max_memory=3, htfint=114)
var Candle[] candlesadd114                  = array.new<Candle>(0)
var BOSdata bosdataadd114                   = BOSdata.new()
htfadd114.settings                 := SettingsHTFadd114
htfadd114.candles                  := candlesadd114
htfadd114.bosdata                  := bosdataadd114
var CandleSet htfadd115                     = CandleSet.new()
var CandleSettings SettingsHTFadd115        = CandleSettings.new(htf="115", max_memory=3, htfint=115)
var Candle[] candlesadd115                  = array.new<Candle>(0)
var BOSdata bosdataadd115                   = BOSdata.new()
htfadd115.settings                 := SettingsHTFadd115
htfadd115.candles                  := candlesadd115
htfadd115.bosdata                  := bosdataadd115
var CandleSet htfadd116                     = CandleSet.new()
var CandleSettings SettingsHTFadd116        = CandleSettings.new(htf="116", max_memory=3, htfint=116)
var Candle[] candlesadd116                  = array.new<Candle>(0)
var BOSdata bosdataadd116                   = BOSdata.new()
htfadd116.settings                 := SettingsHTFadd116
htfadd116.candles                  := candlesadd116
htfadd116.bosdata                  := bosdataadd116
var CandleSet htfadd117                     = CandleSet.new()
var CandleSettings SettingsHTFadd117        = CandleSettings.new(htf="117", max_memory=3, htfint=117)
var Candle[] candlesadd117                  = array.new<Candle>(0)
var BOSdata bosdataadd117                   = BOSdata.new()
htfadd117.settings                 := SettingsHTFadd117
htfadd117.candles                  := candlesadd117
htfadd117.bosdata                  := bosdataadd117
var CandleSet htfadd118                     = CandleSet.new()
var CandleSettings SettingsHTFadd118        = CandleSettings.new(htf="118", max_memory=3, htfint=118)
var Candle[] candlesadd118                  = array.new<Candle>(0)
var BOSdata bosdataadd118                   = BOSdata.new()
htfadd118.settings                 := SettingsHTFadd118
htfadd118.candles                  := candlesadd118
htfadd118.bosdata                  := bosdataadd118
var CandleSet htfadd119                     = CandleSet.new()
var CandleSettings SettingsHTFadd119        = CandleSettings.new(htf="119", max_memory=3, htfint=119)
var Candle[] candlesadd119                  = array.new<Candle>(0)
var BOSdata bosdataadd119                   = BOSdata.new()
htfadd119.settings                 := SettingsHTFadd119
htfadd119.candles                  := candlesadd119
htfadd119.bosdata                  := bosdataadd119
var CandleSet htfadd120                     = CandleSet.new()
var CandleSettings SettingsHTFadd120        = CandleSettings.new(htf="120", max_memory=3, htfint=120)
var Candle[] candlesadd120                  = array.new<Candle>(0)
var BOSdata bosdataadd120                   = BOSdata.new()
htfadd120.settings                 := SettingsHTFadd120
htfadd120.candles                  := candlesadd120
htfadd120.bosdata                  := bosdataadd120
var CandleSet htfadd121                     = CandleSet.new()
var CandleSettings SettingsHTFadd121        = CandleSettings.new(htf="121", max_memory=3, htfint=121)
var Candle[] candlesadd121                  = array.new<Candle>(0)
var BOSdata bosdataadd121                   = BOSdata.new()
htfadd121.settings                 := SettingsHTFadd121
htfadd121.candles                  := candlesadd121
htfadd121.bosdata                  := bosdataadd121
var CandleSet htfadd122                     = CandleSet.new()
var CandleSettings SettingsHTFadd122        = CandleSettings.new(htf="122", max_memory=3, htfint=122)
var Candle[] candlesadd122                  = array.new<Candle>(0)
var BOSdata bosdataadd122                   = BOSdata.new()
htfadd122.settings                 := SettingsHTFadd122
htfadd122.candles                  := candlesadd122
htfadd122.bosdata                  := bosdataadd122
var CandleSet htfadd123                     = CandleSet.new()
var CandleSettings SettingsHTFadd123        = CandleSettings.new(htf="123", max_memory=3, htfint=123)
var Candle[] candlesadd123                  = array.new<Candle>(0)
var BOSdata bosdataadd123                   = BOSdata.new()
htfadd123.settings                 := SettingsHTFadd123
htfadd123.candles                  := candlesadd123
htfadd123.bosdata                  := bosdataadd123
var CandleSet htfadd124                     = CandleSet.new()
var CandleSettings SettingsHTFadd124        = CandleSettings.new(htf="124", max_memory=3, htfint=124)
var Candle[] candlesadd124                  = array.new<Candle>(0)
var BOSdata bosdataadd124                   = BOSdata.new()
htfadd124.settings                 := SettingsHTFadd124
htfadd124.candles                  := candlesadd124
htfadd124.bosdata                  := bosdataadd124
var CandleSet htfadd125                     = CandleSet.new()
var CandleSettings SettingsHTFadd125        = CandleSettings.new(htf="125", max_memory=3, htfint=125)
var Candle[] candlesadd125                  = array.new<Candle>(0)
var BOSdata bosdataadd125                   = BOSdata.new()
htfadd125.settings                 := SettingsHTFadd125
htfadd125.candles                  := candlesadd125
htfadd125.bosdata                  := bosdataadd125
var CandleSet htfadd126                     = CandleSet.new()
var CandleSettings SettingsHTFadd126        = CandleSettings.new(htf="126", max_memory=3, htfint=126)
var Candle[] candlesadd126                  = array.new<Candle>(0)
var BOSdata bosdataadd126                   = BOSdata.new()
htfadd126.settings                 := SettingsHTFadd126
htfadd126.candles                  := candlesadd126
htfadd126.bosdata                  := bosdataadd126
var CandleSet htfadd127                     = CandleSet.new()
var CandleSettings SettingsHTFadd127        = CandleSettings.new(htf="127", max_memory=3, htfint=127)
var Candle[] candlesadd127                  = array.new<Candle>(0)
var BOSdata bosdataadd127                   = BOSdata.new()
htfadd127.settings                 := SettingsHTFadd127
htfadd127.candles                  := candlesadd127
htfadd127.bosdata                  := bosdataadd127
var CandleSet htfadd128                     = CandleSet.new()
var CandleSettings SettingsHTFadd128        = CandleSettings.new(htf="128", max_memory=3, htfint=128)
var Candle[] candlesadd128                  = array.new<Candle>(0)
var BOSdata bosdataadd128                   = BOSdata.new()
htfadd128.settings                 := SettingsHTFadd128
htfadd128.candles                  := candlesadd128
htfadd128.bosdata                  := bosdataadd128
var CandleSet htfadd129                     = CandleSet.new()
var CandleSettings SettingsHTFadd129        = CandleSettings.new(htf="129", max_memory=3, htfint=129)
var Candle[] candlesadd129                  = array.new<Candle>(0)
var BOSdata bosdataadd129                   = BOSdata.new()
htfadd129.settings                 := SettingsHTFadd129
htfadd129.candles                  := candlesadd129
htfadd129.bosdata                  := bosdataadd129
var CandleSet htfadd130                     = CandleSet.new()
var CandleSettings SettingsHTFadd130        = CandleSettings.new(htf="130", max_memory=3, htfint=130)
var Candle[] candlesadd130                  = array.new<Candle>(0)
var BOSdata bosdataadd130                   = BOSdata.new()
htfadd130.settings                 := SettingsHTFadd130
htfadd130.candles                  := candlesadd130
htfadd130.bosdata                  := bosdataadd130
var CandleSet htfadd131                     = CandleSet.new()
var CandleSettings SettingsHTFadd131        = CandleSettings.new(htf="131", max_memory=3, htfint=131)
var Candle[] candlesadd131                  = array.new<Candle>(0)
var BOSdata bosdataadd131                   = BOSdata.new()
htfadd131.settings                 := SettingsHTFadd131
htfadd131.candles                  := candlesadd131
htfadd131.bosdata                  := bosdataadd131
var CandleSet htfadd132                     = CandleSet.new()
var CandleSettings SettingsHTFadd132        = CandleSettings.new(htf="132", max_memory=3, htfint=132)
var Candle[] candlesadd132                  = array.new<Candle>(0)
var BOSdata bosdataadd132                   = BOSdata.new()
htfadd132.settings                 := SettingsHTFadd132
htfadd132.candles                  := candlesadd132
htfadd132.bosdata                  := bosdataadd132
var CandleSet htfadd133                     = CandleSet.new()
var CandleSettings SettingsHTFadd133        = CandleSettings.new(htf="133", max_memory=3, htfint=133)
var Candle[] candlesadd133                  = array.new<Candle>(0)
var BOSdata bosdataadd133                   = BOSdata.new()
htfadd133.settings                 := SettingsHTFadd133
htfadd133.candles                  := candlesadd133
htfadd133.bosdata                  := bosdataadd133
var CandleSet htfadd134                     = CandleSet.new()
var CandleSettings SettingsHTFadd134        = CandleSettings.new(htf="134", max_memory=3, htfint=134)
var Candle[] candlesadd134                  = array.new<Candle>(0)
var BOSdata bosdataadd134                   = BOSdata.new()
htfadd134.settings                 := SettingsHTFadd134
htfadd134.candles                  := candlesadd134
htfadd134.bosdata                  := bosdataadd134
var CandleSet htfadd135                     = CandleSet.new()
var CandleSettings SettingsHTFadd135        = CandleSettings.new(htf="135", max_memory=3, htfint=135)
var Candle[] candlesadd135                  = array.new<Candle>(0)
var BOSdata bosdataadd135                   = BOSdata.new()
htfadd135.settings                 := SettingsHTFadd135
htfadd135.candles                  := candlesadd135
htfadd135.bosdata                  := bosdataadd135
var CandleSet htfadd136                     = CandleSet.new()
var CandleSettings SettingsHTFadd136        = CandleSettings.new(htf="136", max_memory=3, htfint=136)
var Candle[] candlesadd136                  = array.new<Candle>(0)
var BOSdata bosdataadd136                   = BOSdata.new()
htfadd136.settings                 := SettingsHTFadd136
htfadd136.candles                  := candlesadd136
htfadd136.bosdata                  := bosdataadd136
var CandleSet htfadd137                     = CandleSet.new()
var CandleSettings SettingsHTFadd137        = CandleSettings.new(htf="137", max_memory=3, htfint=137)
var Candle[] candlesadd137                  = array.new<Candle>(0)
var BOSdata bosdataadd137                   = BOSdata.new()
htfadd137.settings                 := SettingsHTFadd137
htfadd137.candles                  := candlesadd137
htfadd137.bosdata                  := bosdataadd137
var CandleSet htfadd138                     = CandleSet.new()
var CandleSettings SettingsHTFadd138        = CandleSettings.new(htf="138", max_memory=3, htfint=138)
var Candle[] candlesadd138                  = array.new<Candle>(0)
var BOSdata bosdataadd138                   = BOSdata.new()
htfadd138.settings                 := SettingsHTFadd138
htfadd138.candles                  := candlesadd138
htfadd138.bosdata                  := bosdataadd138
var CandleSet htfadd139                     = CandleSet.new()
var CandleSettings SettingsHTFadd139        = CandleSettings.new(htf="139", max_memory=3, htfint=139)
var Candle[] candlesadd139                  = array.new<Candle>(0)
var BOSdata bosdataadd139                   = BOSdata.new()
htfadd139.settings                 := SettingsHTFadd139
htfadd139.candles                  := candlesadd139
htfadd139.bosdata                  := bosdataadd139
var CandleSet htfadd140                     = CandleSet.new()
var CandleSettings SettingsHTFadd140        = CandleSettings.new(htf="140", max_memory=3, htfint=140)
var Candle[] candlesadd140                  = array.new<Candle>(0)
var BOSdata bosdataadd140                   = BOSdata.new()
htfadd140.settings                 := SettingsHTFadd140
htfadd140.candles                  := candlesadd140
htfadd140.bosdata                  := bosdataadd140
var CandleSet htfadd141                     = CandleSet.new()
var CandleSettings SettingsHTFadd141        = CandleSettings.new(htf="141", max_memory=3, htfint=141)
var Candle[] candlesadd141                  = array.new<Candle>(0)
var BOSdata bosdataadd141                   = BOSdata.new()
htfadd141.settings                 := SettingsHTFadd141
htfadd141.candles                  := candlesadd141
htfadd141.bosdata                  := bosdataadd141
var CandleSet htfadd142                     = CandleSet.new()
var CandleSettings SettingsHTFadd142        = CandleSettings.new(htf="142", max_memory=3, htfint=142)
var Candle[] candlesadd142                  = array.new<Candle>(0)
var BOSdata bosdataadd142                   = BOSdata.new()
htfadd142.settings                 := SettingsHTFadd142
htfadd142.candles                  := candlesadd142
htfadd142.bosdata                  := bosdataadd142
var CandleSet htfadd143                     = CandleSet.new()
var CandleSettings SettingsHTFadd143        = CandleSettings.new(htf="143", max_memory=3, htfint=143)
var Candle[] candlesadd143                  = array.new<Candle>(0)
var BOSdata bosdataadd143                   = BOSdata.new()
htfadd143.settings                 := SettingsHTFadd143
htfadd143.candles                  := candlesadd143
htfadd143.bosdata                  := bosdataadd143
var CandleSet htfadd144                     = CandleSet.new()
var CandleSettings SettingsHTFadd144        = CandleSettings.new(htf="144", max_memory=3, htfint=144)
var Candle[] candlesadd144                  = array.new<Candle>(0)
var BOSdata bosdataadd144                   = BOSdata.new()
htfadd144.settings                 := SettingsHTFadd144
htfadd144.candles                  := candlesadd144
htfadd144.bosdata                  := bosdataadd144
var CandleSet htfadd145                     = CandleSet.new()
var CandleSettings SettingsHTFadd145        = CandleSettings.new(htf="145", max_memory=3, htfint=145)
var Candle[] candlesadd145                  = array.new<Candle>(0)
var BOSdata bosdataadd145                   = BOSdata.new()
htfadd145.settings                 := SettingsHTFadd145
htfadd145.candles                  := candlesadd145
htfadd145.bosdata                  := bosdataadd145
var CandleSet htfadd146                     = CandleSet.new()
var CandleSettings SettingsHTFadd146        = CandleSettings.new(htf="146", max_memory=3, htfint=146)
var Candle[] candlesadd146                  = array.new<Candle>(0)
var BOSdata bosdataadd146                   = BOSdata.new()
htfadd146.settings                 := SettingsHTFadd146
htfadd146.candles                  := candlesadd146
htfadd146.bosdata                  := bosdataadd146
var CandleSet htfadd147                     = CandleSet.new()
var CandleSettings SettingsHTFadd147        = CandleSettings.new(htf="147", max_memory=3, htfint=147)
var Candle[] candlesadd147                  = array.new<Candle>(0)
var BOSdata bosdataadd147                   = BOSdata.new()
htfadd147.settings                 := SettingsHTFadd147
htfadd147.candles                  := candlesadd147
htfadd147.bosdata                  := bosdataadd147
var CandleSet htfadd148                     = CandleSet.new()
var CandleSettings SettingsHTFadd148        = CandleSettings.new(htf="148", max_memory=3, htfint=148)
var Candle[] candlesadd148                  = array.new<Candle>(0)
var BOSdata bosdataadd148                   = BOSdata.new()
htfadd148.settings                 := SettingsHTFadd148
htfadd148.candles                  := candlesadd148
htfadd148.bosdata                  := bosdataadd148
var CandleSet htfadd149                     = CandleSet.new()
var CandleSettings SettingsHTFadd149        = CandleSettings.new(htf="149", max_memory=3, htfint=149)
var Candle[] candlesadd149                  = array.new<Candle>(0)
var BOSdata bosdataadd149                   = BOSdata.new()
htfadd149.settings                 := SettingsHTFadd149
htfadd149.candles                  := candlesadd149
htfadd149.bosdata                  := bosdataadd149
var CandleSet htfadd150                     = CandleSet.new()
var CandleSettings SettingsHTFadd150        = CandleSettings.new(htf="150", max_memory=3, htfint=150)
var Candle[] candlesadd150                  = array.new<Candle>(0)
var BOSdata bosdataadd150                   = BOSdata.new()
htfadd150.settings                 := SettingsHTFadd150
htfadd150.candles                  := candlesadd150
htfadd150.bosdata                  := bosdataadd150
var CandleSet htfadd151                     = CandleSet.new()
var CandleSettings SettingsHTFadd151        = CandleSettings.new(htf="151", max_memory=3, htfint=151)
var Candle[] candlesadd151                  = array.new<Candle>(0)
var BOSdata bosdataadd151                   = BOSdata.new()
htfadd151.settings                 := SettingsHTFadd151
htfadd151.candles                  := candlesadd151
htfadd151.bosdata                  := bosdataadd151
var CandleSet htfadd152                     = CandleSet.new()
var CandleSettings SettingsHTFadd152        = CandleSettings.new(htf="152", max_memory=3, htfint=152)
var Candle[] candlesadd152                  = array.new<Candle>(0)
var BOSdata bosdataadd152                   = BOSdata.new()
htfadd152.settings                 := SettingsHTFadd152
htfadd152.candles                  := candlesadd152
htfadd152.bosdata                  := bosdataadd152
var CandleSet htfadd153                     = CandleSet.new()
var CandleSettings SettingsHTFadd153        = CandleSettings.new(htf="153", max_memory=3, htfint=153)
var Candle[] candlesadd153                  = array.new<Candle>(0)
var BOSdata bosdataadd153                   = BOSdata.new()
htfadd153.settings                 := SettingsHTFadd153
htfadd153.candles                  := candlesadd153
htfadd153.bosdata                  := bosdataadd153
var CandleSet htfadd154                     = CandleSet.new()
var CandleSettings SettingsHTFadd154        = CandleSettings.new(htf="154", max_memory=3, htfint=154)
var Candle[] candlesadd154                  = array.new<Candle>(0)
var BOSdata bosdataadd154                   = BOSdata.new()
htfadd154.settings                 := SettingsHTFadd154
htfadd154.candles                  := candlesadd154
htfadd154.bosdata                  := bosdataadd154
var CandleSet htfadd155                     = CandleSet.new()
var CandleSettings SettingsHTFadd155        = CandleSettings.new(htf="155", max_memory=3, htfint=155)
var Candle[] candlesadd155                  = array.new<Candle>(0)
var BOSdata bosdataadd155                   = BOSdata.new()
htfadd155.settings                 := SettingsHTFadd155
htfadd155.candles                  := candlesadd155
htfadd155.bosdata                  := bosdataadd155
var CandleSet htfadd156                     = CandleSet.new()
var CandleSettings SettingsHTFadd156        = CandleSettings.new(htf="156", max_memory=3, htfint=156)
var Candle[] candlesadd156                  = array.new<Candle>(0)
var BOSdata bosdataadd156                   = BOSdata.new()
htfadd156.settings                 := SettingsHTFadd156
htfadd156.candles                  := candlesadd156
htfadd156.bosdata                  := bosdataadd156
var CandleSet htfadd157                     = CandleSet.new()
var CandleSettings SettingsHTFadd157        = CandleSettings.new(htf="157", max_memory=3, htfint=157)
var Candle[] candlesadd157                  = array.new<Candle>(0)
var BOSdata bosdataadd157                   = BOSdata.new()
htfadd157.settings                 := SettingsHTFadd157
htfadd157.candles                  := candlesadd157
htfadd157.bosdata                  := bosdataadd157
var CandleSet htfadd158                     = CandleSet.new()
var CandleSettings SettingsHTFadd158        = CandleSettings.new(htf="158", max_memory=3, htfint=158)
var Candle[] candlesadd158                  = array.new<Candle>(0)
var BOSdata bosdataadd158                   = BOSdata.new()
htfadd158.settings                 := SettingsHTFadd158
htfadd158.candles                  := candlesadd158
htfadd158.bosdata                  := bosdataadd158
var CandleSet htfadd159                     = CandleSet.new()
var CandleSettings SettingsHTFadd159        = CandleSettings.new(htf="159", max_memory=3, htfint=159)
var Candle[] candlesadd159                  = array.new<Candle>(0)
var BOSdata bosdataadd159                   = BOSdata.new()
htfadd159.settings                 := SettingsHTFadd159
htfadd159.candles                  := candlesadd159
htfadd159.bosdata                  := bosdataadd159
var CandleSet htfadd160                     = CandleSet.new()
var CandleSettings SettingsHTFadd160        = CandleSettings.new(htf="160", max_memory=3, htfint=160)
var Candle[] candlesadd160                  = array.new<Candle>(0)
var BOSdata bosdataadd160                   = BOSdata.new()
htfadd160.settings                 := SettingsHTFadd160
htfadd160.candles                  := candlesadd160
htfadd160.bosdata                  := bosdataadd160
var CandleSet htfadd161                     = CandleSet.new()
var CandleSettings SettingsHTFadd161        = CandleSettings.new(htf="161", max_memory=3, htfint=161)
var Candle[] candlesadd161                  = array.new<Candle>(0)
var BOSdata bosdataadd161                   = BOSdata.new()
htfadd161.settings                 := SettingsHTFadd161
htfadd161.candles                  := candlesadd161
htfadd161.bosdata                  := bosdataadd161
var CandleSet htfadd162                     = CandleSet.new()
var CandleSettings SettingsHTFadd162        = CandleSettings.new(htf="162", max_memory=3, htfint=162)
var Candle[] candlesadd162                  = array.new<Candle>(0)
var BOSdata bosdataadd162                   = BOSdata.new()
htfadd162.settings                 := SettingsHTFadd162
htfadd162.candles                  := candlesadd162
htfadd162.bosdata                  := bosdataadd162
var CandleSet htfadd163                     = CandleSet.new()
var CandleSettings SettingsHTFadd163        = CandleSettings.new(htf="163", max_memory=3, htfint=163)
var Candle[] candlesadd163                  = array.new<Candle>(0)
var BOSdata bosdataadd163                   = BOSdata.new()
htfadd163.settings                 := SettingsHTFadd163
htfadd163.candles                  := candlesadd163
htfadd163.bosdata                  := bosdataadd163
var CandleSet htfadd164                     = CandleSet.new()
var CandleSettings SettingsHTFadd164        = CandleSettings.new(htf="164", max_memory=3, htfint=164)
var Candle[] candlesadd164                  = array.new<Candle>(0)
var BOSdata bosdataadd164                   = BOSdata.new()
htfadd164.settings                 := SettingsHTFadd164
htfadd164.candles                  := candlesadd164
htfadd164.bosdata                  := bosdataadd164
var CandleSet htfadd165                     = CandleSet.new()
var CandleSettings SettingsHTFadd165        = CandleSettings.new(htf="165", max_memory=3, htfint=165)
var Candle[] candlesadd165                  = array.new<Candle>(0)
var BOSdata bosdataadd165                   = BOSdata.new()
htfadd165.settings                 := SettingsHTFadd165
htfadd165.candles                  := candlesadd165
htfadd165.bosdata                  := bosdataadd165
var CandleSet htfadd166                     = CandleSet.new()
var CandleSettings SettingsHTFadd166        = CandleSettings.new(htf="166", max_memory=3, htfint=166)
var Candle[] candlesadd166                  = array.new<Candle>(0)
var BOSdata bosdataadd166                   = BOSdata.new()
htfadd166.settings                 := SettingsHTFadd166
htfadd166.candles                  := candlesadd166
htfadd166.bosdata                  := bosdataadd166
var CandleSet htfadd167                     = CandleSet.new()
var CandleSettings SettingsHTFadd167        = CandleSettings.new(htf="167", max_memory=3, htfint=167)
var Candle[] candlesadd167                  = array.new<Candle>(0)
var BOSdata bosdataadd167                   = BOSdata.new()
htfadd167.settings                 := SettingsHTFadd167
htfadd167.candles                  := candlesadd167
htfadd167.bosdata                  := bosdataadd167
var CandleSet htfadd168                     = CandleSet.new()
var CandleSettings SettingsHTFadd168        = CandleSettings.new(htf="168", max_memory=3, htfint=168)
var Candle[] candlesadd168                  = array.new<Candle>(0)
var BOSdata bosdataadd168                   = BOSdata.new()
htfadd168.settings                 := SettingsHTFadd168
htfadd168.candles                  := candlesadd168
htfadd168.bosdata                  := bosdataadd168
var CandleSet htfadd169                     = CandleSet.new()
var CandleSettings SettingsHTFadd169        = CandleSettings.new(htf="169", max_memory=3, htfint=169)
var Candle[] candlesadd169                  = array.new<Candle>(0)
var BOSdata bosdataadd169                   = BOSdata.new()
htfadd169.settings                 := SettingsHTFadd169
htfadd169.candles                  := candlesadd169
htfadd169.bosdata                  := bosdataadd169
var CandleSet htfadd170                     = CandleSet.new()
var CandleSettings SettingsHTFadd170        = CandleSettings.new(htf="170", max_memory=3, htfint=170)
var Candle[] candlesadd170                  = array.new<Candle>(0)
var BOSdata bosdataadd170                   = BOSdata.new()
htfadd170.settings                 := SettingsHTFadd170
htfadd170.candles                  := candlesadd170
htfadd170.bosdata                  := bosdataadd170
var CandleSet htfadd171                     = CandleSet.new()
var CandleSettings SettingsHTFadd171        = CandleSettings.new(htf="171", max_memory=3, htfint=171)
var Candle[] candlesadd171                  = array.new<Candle>(0)
var BOSdata bosdataadd171                   = BOSdata.new()
htfadd171.settings                 := SettingsHTFadd171
htfadd171.candles                  := candlesadd171
htfadd171.bosdata                  := bosdataadd171
var CandleSet htfadd172                     = CandleSet.new()
var CandleSettings SettingsHTFadd172        = CandleSettings.new(htf="172", max_memory=3, htfint=172)
var Candle[] candlesadd172                  = array.new<Candle>(0)
var BOSdata bosdataadd172                   = BOSdata.new()
htfadd172.settings                 := SettingsHTFadd172
htfadd172.candles                  := candlesadd172
htfadd172.bosdata                  := bosdataadd172
var CandleSet htfadd173                     = CandleSet.new()
var CandleSettings SettingsHTFadd173        = CandleSettings.new(htf="173", max_memory=3, htfint=173)
var Candle[] candlesadd173                  = array.new<Candle>(0)
var BOSdata bosdataadd173                   = BOSdata.new()
htfadd173.settings                 := SettingsHTFadd173
htfadd173.candles                  := candlesadd173
htfadd173.bosdata                  := bosdataadd173
var CandleSet htfadd174                     = CandleSet.new()
var CandleSettings SettingsHTFadd174        = CandleSettings.new(htf="174", max_memory=3, htfint=174)
var Candle[] candlesadd174                  = array.new<Candle>(0)
var BOSdata bosdataadd174                   = BOSdata.new()
htfadd174.settings                 := SettingsHTFadd174
htfadd174.candles                  := candlesadd174
htfadd174.bosdata                  := bosdataadd174
var CandleSet htfadd175                     = CandleSet.new()
var CandleSettings SettingsHTFadd175        = CandleSettings.new(htf="175", max_memory=3, htfint=175)
var Candle[] candlesadd175                  = array.new<Candle>(0)
var BOSdata bosdataadd175                   = BOSdata.new()
htfadd175.settings                 := SettingsHTFadd175
htfadd175.candles                  := candlesadd175
htfadd175.bosdata                  := bosdataadd175
var CandleSet htfadd176                     = CandleSet.new()
var CandleSettings SettingsHTFadd176        = CandleSettings.new(htf="176", max_memory=3, htfint=176)
var Candle[] candlesadd176                  = array.new<Candle>(0)
var BOSdata bosdataadd176                   = BOSdata.new()
htfadd176.settings                 := SettingsHTFadd176
htfadd176.candles                  := candlesadd176
htfadd176.bosdata                  := bosdataadd176
var CandleSet htfadd177                     = CandleSet.new()
var CandleSettings SettingsHTFadd177        = CandleSettings.new(htf="177", max_memory=3, htfint=177)
var Candle[] candlesadd177                  = array.new<Candle>(0)
var BOSdata bosdataadd177                   = BOSdata.new()
htfadd177.settings                 := SettingsHTFadd177
htfadd177.candles                  := candlesadd177
htfadd177.bosdata                  := bosdataadd177
var CandleSet htfadd178                     = CandleSet.new()
var CandleSettings SettingsHTFadd178        = CandleSettings.new(htf="178", max_memory=3, htfint=178)
var Candle[] candlesadd178                  = array.new<Candle>(0)
var BOSdata bosdataadd178                   = BOSdata.new()
htfadd178.settings                 := SettingsHTFadd178
htfadd178.candles                  := candlesadd178
htfadd178.bosdata                  := bosdataadd178
var CandleSet htfadd179                     = CandleSet.new()
var CandleSettings SettingsHTFadd179        = CandleSettings.new(htf="179", max_memory=3, htfint=179)
var Candle[] candlesadd179                  = array.new<Candle>(0)
var BOSdata bosdataadd179                   = BOSdata.new()
htfadd179.settings                 := SettingsHTFadd179
htfadd179.candles                  := candlesadd179
htfadd179.bosdata                  := bosdataadd179
var CandleSet htfadd180                     = CandleSet.new()
var CandleSettings SettingsHTFadd180        = CandleSettings.new(htf="180", max_memory=3, htfint=180)
var Candle[] candlesadd180                  = array.new<Candle>(0)
var BOSdata bosdataadd180                   = BOSdata.new()
htfadd180.settings                 := SettingsHTFadd180
htfadd180.candles                  := candlesadd180
htfadd180.bosdata                  := bosdataadd180
var CandleSet htfadd181                     = CandleSet.new()
var CandleSettings SettingsHTFadd181        = CandleSettings.new(htf="181", max_memory=3, htfint=181)
var Candle[] candlesadd181                  = array.new<Candle>(0)
var BOSdata bosdataadd181                   = BOSdata.new()
htfadd181.settings                 := SettingsHTFadd181
htfadd181.candles                  := candlesadd181
htfadd181.bosdata                  := bosdataadd181
var CandleSet htfadd182                     = CandleSet.new()
var CandleSettings SettingsHTFadd182        = CandleSettings.new(htf="182", max_memory=3, htfint=182)
var Candle[] candlesadd182                  = array.new<Candle>(0)
var BOSdata bosdataadd182                   = BOSdata.new()
htfadd182.settings                 := SettingsHTFadd182
htfadd182.candles                  := candlesadd182
htfadd182.bosdata                  := bosdataadd182
var CandleSet htfadd183                     = CandleSet.new()
var CandleSettings SettingsHTFadd183        = CandleSettings.new(htf="183", max_memory=3, htfint=183)
var Candle[] candlesadd183                  = array.new<Candle>(0)
var BOSdata bosdataadd183                   = BOSdata.new()
htfadd183.settings                 := SettingsHTFadd183
htfadd183.candles                  := candlesadd183
htfadd183.bosdata                  := bosdataadd183
var CandleSet htfadd184                     = CandleSet.new()
var CandleSettings SettingsHTFadd184        = CandleSettings.new(htf="184", max_memory=3, htfint=184)
var Candle[] candlesadd184                  = array.new<Candle>(0)
var BOSdata bosdataadd184                   = BOSdata.new()
htfadd184.settings                 := SettingsHTFadd184
htfadd184.candles                  := candlesadd184
htfadd184.bosdata                  := bosdataadd184
var CandleSet htfadd185                     = CandleSet.new()
var CandleSettings SettingsHTFadd185        = CandleSettings.new(htf="185", max_memory=3, htfint=185)
var Candle[] candlesadd185                  = array.new<Candle>(0)
var BOSdata bosdataadd185                   = BOSdata.new()
htfadd185.settings                 := SettingsHTFadd185
htfadd185.candles                  := candlesadd185
htfadd185.bosdata                  := bosdataadd185
var CandleSet htfadd186                     = CandleSet.new()
var CandleSettings SettingsHTFadd186        = CandleSettings.new(htf="186", max_memory=3, htfint=186)
var Candle[] candlesadd186                  = array.new<Candle>(0)
var BOSdata bosdataadd186                   = BOSdata.new()
htfadd186.settings                 := SettingsHTFadd186
htfadd186.candles                  := candlesadd186
htfadd186.bosdata                  := bosdataadd186
var CandleSet htfadd187                     = CandleSet.new()
var CandleSettings SettingsHTFadd187        = CandleSettings.new(htf="187", max_memory=3, htfint=187)
var Candle[] candlesadd187                  = array.new<Candle>(0)
var BOSdata bosdataadd187                   = BOSdata.new()
htfadd187.settings                 := SettingsHTFadd187
htfadd187.candles                  := candlesadd187
htfadd187.bosdata                  := bosdataadd187
var CandleSet htfadd188                     = CandleSet.new()
var CandleSettings SettingsHTFadd188        = CandleSettings.new(htf="188", max_memory=3, htfint=188)
var Candle[] candlesadd188                  = array.new<Candle>(0)
var BOSdata bosdataadd188                   = BOSdata.new()
htfadd188.settings                 := SettingsHTFadd188
htfadd188.candles                  := candlesadd188
htfadd188.bosdata                  := bosdataadd188
var CandleSet htfadd189                     = CandleSet.new()
var CandleSettings SettingsHTFadd189        = CandleSettings.new(htf="189", max_memory=3, htfint=189)
var Candle[] candlesadd189                  = array.new<Candle>(0)
var BOSdata bosdataadd189                   = BOSdata.new()
htfadd189.settings                 := SettingsHTFadd189
htfadd189.candles                  := candlesadd189
htfadd189.bosdata                  := bosdataadd189
var CandleSet htfadd190                     = CandleSet.new()
var CandleSettings SettingsHTFadd190        = CandleSettings.new(htf="190", max_memory=3, htfint=190)
var Candle[] candlesadd190                  = array.new<Candle>(0)
var BOSdata bosdataadd190                   = BOSdata.new()
htfadd190.settings                 := SettingsHTFadd190
htfadd190.candles                  := candlesadd190
htfadd190.bosdata                  := bosdataadd190
var CandleSet htfadd191                     = CandleSet.new()
var CandleSettings SettingsHTFadd191        = CandleSettings.new(htf="191", max_memory=3, htfint=191)
var Candle[] candlesadd191                  = array.new<Candle>(0)
var BOSdata bosdataadd191                   = BOSdata.new()
htfadd191.settings                 := SettingsHTFadd191
htfadd191.candles                  := candlesadd191
htfadd191.bosdata                  := bosdataadd191
var CandleSet htfadd192                     = CandleSet.new()
var CandleSettings SettingsHTFadd192        = CandleSettings.new(htf="192", max_memory=3, htfint=192)
var Candle[] candlesadd192                  = array.new<Candle>(0)
var BOSdata bosdataadd192                   = BOSdata.new()
htfadd192.settings                 := SettingsHTFadd192
htfadd192.candles                  := candlesadd192
htfadd192.bosdata                  := bosdataadd192
var CandleSet htfadd193                     = CandleSet.new()
var CandleSettings SettingsHTFadd193        = CandleSettings.new(htf="193", max_memory=3, htfint=193)
var Candle[] candlesadd193                  = array.new<Candle>(0)
var BOSdata bosdataadd193                   = BOSdata.new()
htfadd193.settings                 := SettingsHTFadd193
htfadd193.candles                  := candlesadd193
htfadd193.bosdata                  := bosdataadd193
var CandleSet htfadd194                     = CandleSet.new()
var CandleSettings SettingsHTFadd194        = CandleSettings.new(htf="194", max_memory=3, htfint=194)
var Candle[] candlesadd194                  = array.new<Candle>(0)
var BOSdata bosdataadd194                   = BOSdata.new()
htfadd194.settings                 := SettingsHTFadd194
htfadd194.candles                  := candlesadd194
htfadd194.bosdata                  := bosdataadd194
var CandleSet htfadd195                     = CandleSet.new()
var CandleSettings SettingsHTFadd195        = CandleSettings.new(htf="195", max_memory=3, htfint=195)
var Candle[] candlesadd195                  = array.new<Candle>(0)
var BOSdata bosdataadd195                   = BOSdata.new()
htfadd195.settings                 := SettingsHTFadd195
htfadd195.candles                  := candlesadd195
htfadd195.bosdata                  := bosdataadd195
var CandleSet htfadd196                     = CandleSet.new()
var CandleSettings SettingsHTFadd196        = CandleSettings.new(htf="196", max_memory=3, htfint=196)
var Candle[] candlesadd196                  = array.new<Candle>(0)
var BOSdata bosdataadd196                   = BOSdata.new()
htfadd196.settings                 := SettingsHTFadd196
htfadd196.candles                  := candlesadd196
htfadd196.bosdata                  := bosdataadd196
var CandleSet htfadd197                     = CandleSet.new()
var CandleSettings SettingsHTFadd197        = CandleSettings.new(htf="197", max_memory=3, htfint=197)
var Candle[] candlesadd197                  = array.new<Candle>(0)
var BOSdata bosdataadd197                   = BOSdata.new()
htfadd197.settings                 := SettingsHTFadd197
htfadd197.candles                  := candlesadd197
htfadd197.bosdata                  := bosdataadd197
var CandleSet htfadd198                     = CandleSet.new()
var CandleSettings SettingsHTFadd198        = CandleSettings.new(htf="198", max_memory=3, htfint=198)
var Candle[] candlesadd198                  = array.new<Candle>(0)
var BOSdata bosdataadd198                   = BOSdata.new()
htfadd198.settings                 := SettingsHTFadd198
htfadd198.candles                  := candlesadd198
htfadd198.bosdata                  := bosdataadd198
var CandleSet htfadd199                     = CandleSet.new()
var CandleSettings SettingsHTFadd199        = CandleSettings.new(htf="199", max_memory=3, htfint=199)
var Candle[] candlesadd199                  = array.new<Candle>(0)
var BOSdata bosdataadd199                   = BOSdata.new()
htfadd199.settings                 := SettingsHTFadd199
htfadd199.candles                  := candlesadd199
htfadd199.bosdata                  := bosdataadd199
var CandleSet htfadd200                     = CandleSet.new()
var CandleSettings SettingsHTFadd200        = CandleSettings.new(htf="200", max_memory=3, htfint=200)
var Candle[] candlesadd200                  = array.new<Candle>(0)
var BOSdata bosdataadd200                   = BOSdata.new()
htfadd200.settings                 := SettingsHTFadd200
htfadd200.candles                  := candlesadd200
htfadd200.bosdata                  := bosdataadd200
var CandleSet htfadd201                     = CandleSet.new()
var CandleSettings SettingsHTFadd201        = CandleSettings.new(htf="201", max_memory=3, htfint=201)
var Candle[] candlesadd201                  = array.new<Candle>(0)
var BOSdata bosdataadd201                   = BOSdata.new()
htfadd201.settings                 := SettingsHTFadd201
htfadd201.candles                  := candlesadd201
htfadd201.bosdata                  := bosdataadd201
var CandleSet htfadd202                     = CandleSet.new()
var CandleSettings SettingsHTFadd202        = CandleSettings.new(htf="202", max_memory=3, htfint=202)
var Candle[] candlesadd202                  = array.new<Candle>(0)
var BOSdata bosdataadd202                   = BOSdata.new()
htfadd202.settings                 := SettingsHTFadd202
htfadd202.candles                  := candlesadd202
htfadd202.bosdata                  := bosdataadd202
var CandleSet htfadd203                     = CandleSet.new()
var CandleSettings SettingsHTFadd203        = CandleSettings.new(htf="203", max_memory=3, htfint=203)
var Candle[] candlesadd203                  = array.new<Candle>(0)
var BOSdata bosdataadd203                   = BOSdata.new()
htfadd203.settings                 := SettingsHTFadd203
htfadd203.candles                  := candlesadd203
htfadd203.bosdata                  := bosdataadd203
var CandleSet htfadd204                     = CandleSet.new()
var CandleSettings SettingsHTFadd204        = CandleSettings.new(htf="204", max_memory=3, htfint=204)
var Candle[] candlesadd204                  = array.new<Candle>(0)
var BOSdata bosdataadd204                   = BOSdata.new()
htfadd204.settings                 := SettingsHTFadd204
htfadd204.candles                  := candlesadd204
htfadd204.bosdata                  := bosdataadd204
var CandleSet htfadd205                     = CandleSet.new()
var CandleSettings SettingsHTFadd205        = CandleSettings.new(htf="205", max_memory=3, htfint=205)
var Candle[] candlesadd205                  = array.new<Candle>(0)
var BOSdata bosdataadd205                   = BOSdata.new()
htfadd205.settings                 := SettingsHTFadd205
htfadd205.candles                  := candlesadd205
htfadd205.bosdata                  := bosdataadd205
var CandleSet htfadd206                     = CandleSet.new()
var CandleSettings SettingsHTFadd206        = CandleSettings.new(htf="206", max_memory=3, htfint=206)
var Candle[] candlesadd206                  = array.new<Candle>(0)
var BOSdata bosdataadd206                   = BOSdata.new()
htfadd206.settings                 := SettingsHTFadd206
htfadd206.candles                  := candlesadd206
htfadd206.bosdata                  := bosdataadd206
var CandleSet htfadd207                     = CandleSet.new()
var CandleSettings SettingsHTFadd207        = CandleSettings.new(htf="207", max_memory=3, htfint=207)
var Candle[] candlesadd207                  = array.new<Candle>(0)
var BOSdata bosdataadd207                   = BOSdata.new()
htfadd207.settings                 := SettingsHTFadd207
htfadd207.candles                  := candlesadd207
htfadd207.bosdata                  := bosdataadd207
var CandleSet htfadd208                     = CandleSet.new()
var CandleSettings SettingsHTFadd208        = CandleSettings.new(htf="208", max_memory=3, htfint=208)
var Candle[] candlesadd208                  = array.new<Candle>(0)
var BOSdata bosdataadd208                   = BOSdata.new()
htfadd208.settings                 := SettingsHTFadd208
htfadd208.candles                  := candlesadd208
htfadd208.bosdata                  := bosdataadd208
var CandleSet htfadd209                     = CandleSet.new()
var CandleSettings SettingsHTFadd209        = CandleSettings.new(htf="209", max_memory=3, htfint=209)
var Candle[] candlesadd209                  = array.new<Candle>(0)
var BOSdata bosdataadd209                   = BOSdata.new()
htfadd209.settings                 := SettingsHTFadd209
htfadd209.candles                  := candlesadd209
htfadd209.bosdata                  := bosdataadd209
var CandleSet htfadd210                     = CandleSet.new()
var CandleSettings SettingsHTFadd210        = CandleSettings.new(htf="210", max_memory=3, htfint=210)
var Candle[] candlesadd210                  = array.new<Candle>(0)
var BOSdata bosdataadd210                   = BOSdata.new()
htfadd210.settings                 := SettingsHTFadd210
htfadd210.candles                  := candlesadd210
htfadd210.bosdata                  := bosdataadd210
var CandleSet htfadd211                     = CandleSet.new()
var CandleSettings SettingsHTFadd211        = CandleSettings.new(htf="211", max_memory=3, htfint=211)
var Candle[] candlesadd211                  = array.new<Candle>(0)
var BOSdata bosdataadd211                   = BOSdata.new()
htfadd211.settings                 := SettingsHTFadd211
htfadd211.candles                  := candlesadd211
htfadd211.bosdata                  := bosdataadd211
var CandleSet htfadd212                     = CandleSet.new()
var CandleSettings SettingsHTFadd212        = CandleSettings.new(htf="212", max_memory=3, htfint=212)
var Candle[] candlesadd212                  = array.new<Candle>(0)
var BOSdata bosdataadd212                   = BOSdata.new()
htfadd212.settings                 := SettingsHTFadd212
htfadd212.candles                  := candlesadd212
htfadd212.bosdata                  := bosdataadd212
var CandleSet htfadd213                     = CandleSet.new()
var CandleSettings SettingsHTFadd213        = CandleSettings.new(htf="213", max_memory=3, htfint=213)
var Candle[] candlesadd213                  = array.new<Candle>(0)
var BOSdata bosdataadd213                   = BOSdata.new()
htfadd213.settings                 := SettingsHTFadd213
htfadd213.candles                  := candlesadd213
htfadd213.bosdata                  := bosdataadd213
var CandleSet htfadd214                     = CandleSet.new()
var CandleSettings SettingsHTFadd214        = CandleSettings.new(htf="214", max_memory=3, htfint=214)
var Candle[] candlesadd214                  = array.new<Candle>(0)
var BOSdata bosdataadd214                   = BOSdata.new()
htfadd214.settings                 := SettingsHTFadd214
htfadd214.candles                  := candlesadd214
htfadd214.bosdata                  := bosdataadd214
var CandleSet htfadd215                     = CandleSet.new()
var CandleSettings SettingsHTFadd215        = CandleSettings.new(htf="215", max_memory=3, htfint=215)
var Candle[] candlesadd215                  = array.new<Candle>(0)
var BOSdata bosdataadd215                   = BOSdata.new()
htfadd215.settings                 := SettingsHTFadd215
htfadd215.candles                  := candlesadd215
htfadd215.bosdata                  := bosdataadd215
var CandleSet htfadd216                     = CandleSet.new()
var CandleSettings SettingsHTFadd216        = CandleSettings.new(htf="216", max_memory=3, htfint=216)
var Candle[] candlesadd216                  = array.new<Candle>(0)
var BOSdata bosdataadd216                   = BOSdata.new()
htfadd216.settings                 := SettingsHTFadd216
htfadd216.candles                  := candlesadd216
htfadd216.bosdata                  := bosdataadd216
var CandleSet htfadd217                     = CandleSet.new()
var CandleSettings SettingsHTFadd217        = CandleSettings.new(htf="217", max_memory=3, htfint=217)
var Candle[] candlesadd217                  = array.new<Candle>(0)
var BOSdata bosdataadd217                   = BOSdata.new()
htfadd217.settings                 := SettingsHTFadd217
htfadd217.candles                  := candlesadd217
htfadd217.bosdata                  := bosdataadd217
var CandleSet htfadd218                     = CandleSet.new()
var CandleSettings SettingsHTFadd218        = CandleSettings.new(htf="218", max_memory=3, htfint=218)
var Candle[] candlesadd218                  = array.new<Candle>(0)
var BOSdata bosdataadd218                   = BOSdata.new()
htfadd218.settings                 := SettingsHTFadd218
htfadd218.candles                  := candlesadd218
htfadd218.bosdata                  := bosdataadd218
var CandleSet htfadd219                     = CandleSet.new()
var CandleSettings SettingsHTFadd219        = CandleSettings.new(htf="219", max_memory=3, htfint=219)
var Candle[] candlesadd219                  = array.new<Candle>(0)
var BOSdata bosdataadd219                   = BOSdata.new()
htfadd219.settings                 := SettingsHTFadd219
htfadd219.candles                  := candlesadd219
htfadd219.bosdata                  := bosdataadd219
var CandleSet htfadd220                     = CandleSet.new()
var CandleSettings SettingsHTFadd220        = CandleSettings.new(htf="220", max_memory=3, htfint=220)
var Candle[] candlesadd220                  = array.new<Candle>(0)
var BOSdata bosdataadd220                   = BOSdata.new()
htfadd220.settings                 := SettingsHTFadd220
htfadd220.candles                  := candlesadd220
htfadd220.bosdata                  := bosdataadd220
var CandleSet htfadd221                     = CandleSet.new()
var CandleSettings SettingsHTFadd221        = CandleSettings.new(htf="221", max_memory=3, htfint=221)
var Candle[] candlesadd221                  = array.new<Candle>(0)
var BOSdata bosdataadd221                   = BOSdata.new()
htfadd221.settings                 := SettingsHTFadd221
htfadd221.candles                  := candlesadd221
htfadd221.bosdata                  := bosdataadd221
var CandleSet htfadd222                     = CandleSet.new()
var CandleSettings SettingsHTFadd222        = CandleSettings.new(htf="222", max_memory=3, htfint=222)
var Candle[] candlesadd222                  = array.new<Candle>(0)
var BOSdata bosdataadd222                   = BOSdata.new()
htfadd222.settings                 := SettingsHTFadd222
htfadd222.candles                  := candlesadd222
htfadd222.bosdata                  := bosdataadd222
var CandleSet htfadd223                     = CandleSet.new()
var CandleSettings SettingsHTFadd223        = CandleSettings.new(htf="223", max_memory=3, htfint=223)
var Candle[] candlesadd223                  = array.new<Candle>(0)
var BOSdata bosdataadd223                   = BOSdata.new()
htfadd223.settings                 := SettingsHTFadd223
htfadd223.candles                  := candlesadd223
htfadd223.bosdata                  := bosdataadd223
var CandleSet htfadd224                     = CandleSet.new()
var CandleSettings SettingsHTFadd224        = CandleSettings.new(htf="224", max_memory=3, htfint=224)
var Candle[] candlesadd224                  = array.new<Candle>(0)
var BOSdata bosdataadd224                   = BOSdata.new()
htfadd224.settings                 := SettingsHTFadd224
htfadd224.candles                  := candlesadd224
htfadd224.bosdata                  := bosdataadd224
var CandleSet htfadd225                     = CandleSet.new()
var CandleSettings SettingsHTFadd225        = CandleSettings.new(htf="225", max_memory=3, htfint=225)
var Candle[] candlesadd225                  = array.new<Candle>(0)
var BOSdata bosdataadd225                   = BOSdata.new()
htfadd225.settings                 := SettingsHTFadd225
htfadd225.candles                  := candlesadd225
htfadd225.bosdata                  := bosdataadd225
var CandleSet htfadd226                     = CandleSet.new()
var CandleSettings SettingsHTFadd226        = CandleSettings.new(htf="226", max_memory=3, htfint=226)
var Candle[] candlesadd226                  = array.new<Candle>(0)
var BOSdata bosdataadd226                   = BOSdata.new()
htfadd226.settings                 := SettingsHTFadd226
htfadd226.candles                  := candlesadd226
htfadd226.bosdata                  := bosdataadd226
var CandleSet htfadd227                     = CandleSet.new()
var CandleSettings SettingsHTFadd227        = CandleSettings.new(htf="227", max_memory=3, htfint=227)
var Candle[] candlesadd227                  = array.new<Candle>(0)
var BOSdata bosdataadd227                   = BOSdata.new()
htfadd227.settings                 := SettingsHTFadd227
htfadd227.candles                  := candlesadd227
htfadd227.bosdata                  := bosdataadd227
var CandleSet htfadd228                     = CandleSet.new()
var CandleSettings SettingsHTFadd228        = CandleSettings.new(htf="228", max_memory=3, htfint=228)
var Candle[] candlesadd228                  = array.new<Candle>(0)
var BOSdata bosdataadd228                   = BOSdata.new()
htfadd228.settings                 := SettingsHTFadd228
htfadd228.candles                  := candlesadd228
htfadd228.bosdata                  := bosdataadd228
var CandleSet htfadd229                     = CandleSet.new()
var CandleSettings SettingsHTFadd229        = CandleSettings.new(htf="229", max_memory=3, htfint=229)
var Candle[] candlesadd229                  = array.new<Candle>(0)
var BOSdata bosdataadd229                   = BOSdata.new()
htfadd229.settings                 := SettingsHTFadd229
htfadd229.candles                  := candlesadd229
htfadd229.bosdata                  := bosdataadd229
var CandleSet htfadd230                     = CandleSet.new()
var CandleSettings SettingsHTFadd230        = CandleSettings.new(htf="230", max_memory=3, htfint=230)
var Candle[] candlesadd230                  = array.new<Candle>(0)
var BOSdata bosdataadd230                   = BOSdata.new()
htfadd230.settings                 := SettingsHTFadd230
htfadd230.candles                  := candlesadd230
htfadd230.bosdata                  := bosdataadd230
var CandleSet htfadd231                     = CandleSet.new()
var CandleSettings SettingsHTFadd231        = CandleSettings.new(htf="231", max_memory=3, htfint=231)
var Candle[] candlesadd231                  = array.new<Candle>(0)
var BOSdata bosdataadd231                   = BOSdata.new()
htfadd231.settings                 := SettingsHTFadd231
htfadd231.candles                  := candlesadd231
htfadd231.bosdata                  := bosdataadd231
var CandleSet htfadd232                     = CandleSet.new()
var CandleSettings SettingsHTFadd232        = CandleSettings.new(htf="232", max_memory=3, htfint=232)
var Candle[] candlesadd232                  = array.new<Candle>(0)
var BOSdata bosdataadd232                   = BOSdata.new()
htfadd232.settings                 := SettingsHTFadd232
htfadd232.candles                  := candlesadd232
htfadd232.bosdata                  := bosdataadd232
var CandleSet htfadd233                     = CandleSet.new()
var CandleSettings SettingsHTFadd233        = CandleSettings.new(htf="233", max_memory=3, htfint=233)
var Candle[] candlesadd233                  = array.new<Candle>(0)
var BOSdata bosdataadd233                   = BOSdata.new()
htfadd233.settings                 := SettingsHTFadd233
htfadd233.candles                  := candlesadd233
htfadd233.bosdata                  := bosdataadd233
var CandleSet htfadd234                     = CandleSet.new()
var CandleSettings SettingsHTFadd234        = CandleSettings.new(htf="234", max_memory=3, htfint=234)
var Candle[] candlesadd234                  = array.new<Candle>(0)
var BOSdata bosdataadd234                   = BOSdata.new()
htfadd234.settings                 := SettingsHTFadd234
htfadd234.candles                  := candlesadd234
htfadd234.bosdata                  := bosdataadd234
var CandleSet htfadd235                     = CandleSet.new()
var CandleSettings SettingsHTFadd235        = CandleSettings.new(htf="235", max_memory=3, htfint=235)
var Candle[] candlesadd235                  = array.new<Candle>(0)
var BOSdata bosdataadd235                   = BOSdata.new()
htfadd235.settings                 := SettingsHTFadd235
htfadd235.candles                  := candlesadd235
htfadd235.bosdata                  := bosdataadd235
var CandleSet htfadd236                     = CandleSet.new()
var CandleSettings SettingsHTFadd236        = CandleSettings.new(htf="236", max_memory=3, htfint=236)
var Candle[] candlesadd236                  = array.new<Candle>(0)
var BOSdata bosdataadd236                   = BOSdata.new()
htfadd236.settings                 := SettingsHTFadd236
htfadd236.candles                  := candlesadd236
htfadd236.bosdata                  := bosdataadd236
var CandleSet htfadd237                     = CandleSet.new()
var CandleSettings SettingsHTFadd237        = CandleSettings.new(htf="237", max_memory=3, htfint=237)
var Candle[] candlesadd237                  = array.new<Candle>(0)
var BOSdata bosdataadd237                   = BOSdata.new()
htfadd237.settings                 := SettingsHTFadd237
htfadd237.candles                  := candlesadd237
htfadd237.bosdata                  := bosdataadd237
var CandleSet htfadd238                     = CandleSet.new()
var CandleSettings SettingsHTFadd238        = CandleSettings.new(htf="238", max_memory=3, htfint=238)
var Candle[] candlesadd238                  = array.new<Candle>(0)
var BOSdata bosdataadd238                   = BOSdata.new()
htfadd238.settings                 := SettingsHTFadd238
htfadd238.candles                  := candlesadd238
htfadd238.bosdata                  := bosdataadd238
var CandleSet htfadd239                     = CandleSet.new()
var CandleSettings SettingsHTFadd239        = CandleSettings.new(htf="239", max_memory=3, htfint=239)
var Candle[] candlesadd239                  = array.new<Candle>(0)
var BOSdata bosdataadd239                   = BOSdata.new()
htfadd239.settings                 := SettingsHTFadd239
htfadd239.candles                  := candlesadd239
htfadd239.bosdata                  := bosdataadd239
var CandleSet htfadd240                     = CandleSet.new()
var CandleSettings SettingsHTFadd240        = CandleSettings.new(htf="240", max_memory=3, htfint=240)
var Candle[] candlesadd240                  = array.new<Candle>(0)
var BOSdata bosdataadd240                   = BOSdata.new()
htfadd240.settings                 := SettingsHTFadd240
htfadd240.candles                  := candlesadd240
htfadd240.bosdata                  := bosdataadd240
var CandleSet htfadd241                     = CandleSet.new()
var CandleSettings SettingsHTFadd241        = CandleSettings.new(htf="241", max_memory=3, htfint=241)
var Candle[] candlesadd241                  = array.new<Candle>(0)
var BOSdata bosdataadd241                   = BOSdata.new()
htfadd241.settings                 := SettingsHTFadd241
htfadd241.candles                  := candlesadd241
htfadd241.bosdata                  := bosdataadd241
var CandleSet htfadd242                     = CandleSet.new()
var CandleSettings SettingsHTFadd242        = CandleSettings.new(htf="242", max_memory=3, htfint=242)
var Candle[] candlesadd242                  = array.new<Candle>(0)
var BOSdata bosdataadd242                   = BOSdata.new()
htfadd242.settings                 := SettingsHTFadd242
htfadd242.candles                  := candlesadd242
htfadd242.bosdata                  := bosdataadd242
var CandleSet htfadd243                     = CandleSet.new()
var CandleSettings SettingsHTFadd243        = CandleSettings.new(htf="243", max_memory=3, htfint=243)
var Candle[] candlesadd243                  = array.new<Candle>(0)
var BOSdata bosdataadd243                   = BOSdata.new()
htfadd243.settings                 := SettingsHTFadd243
htfadd243.candles                  := candlesadd243
htfadd243.bosdata                  := bosdataadd243
var CandleSet htfadd244                     = CandleSet.new()
var CandleSettings SettingsHTFadd244        = CandleSettings.new(htf="244", max_memory=3, htfint=244)
var Candle[] candlesadd244                  = array.new<Candle>(0)
var BOSdata bosdataadd244                   = BOSdata.new()
htfadd244.settings                 := SettingsHTFadd244
htfadd244.candles                  := candlesadd244
htfadd244.bosdata                  := bosdataadd244
var CandleSet htfadd245                     = CandleSet.new()
var CandleSettings SettingsHTFadd245        = CandleSettings.new(htf="245", max_memory=3, htfint=245)
var Candle[] candlesadd245                  = array.new<Candle>(0)
var BOSdata bosdataadd245                   = BOSdata.new()
htfadd245.settings                 := SettingsHTFadd245
htfadd245.candles                  := candlesadd245
htfadd245.bosdata                  := bosdataadd245
var CandleSet htfadd246                     = CandleSet.new()
var CandleSettings SettingsHTFadd246        = CandleSettings.new(htf="246", max_memory=3, htfint=246)
var Candle[] candlesadd246                  = array.new<Candle>(0)
var BOSdata bosdataadd246                   = BOSdata.new()
htfadd246.settings                 := SettingsHTFadd246
htfadd246.candles                  := candlesadd246
htfadd246.bosdata                  := bosdataadd246
var CandleSet htfadd247                     = CandleSet.new()
var CandleSettings SettingsHTFadd247        = CandleSettings.new(htf="247", max_memory=3, htfint=247)
var Candle[] candlesadd247                  = array.new<Candle>(0)
var BOSdata bosdataadd247                   = BOSdata.new()
htfadd247.settings                 := SettingsHTFadd247
htfadd247.candles                  := candlesadd247
htfadd247.bosdata                  := bosdataadd247
var CandleSet htfadd248                     = CandleSet.new()
var CandleSettings SettingsHTFadd248        = CandleSettings.new(htf="248", max_memory=3, htfint=248)
var Candle[] candlesadd248                  = array.new<Candle>(0)
var BOSdata bosdataadd248                   = BOSdata.new()
htfadd248.settings                 := SettingsHTFadd248
htfadd248.candles                  := candlesadd248
htfadd248.bosdata                  := bosdataadd248
var CandleSet htfadd249                     = CandleSet.new()
var CandleSettings SettingsHTFadd249        = CandleSettings.new(htf="249", max_memory=3, htfint=249)
var Candle[] candlesadd249                  = array.new<Candle>(0)
var BOSdata bosdataadd249                   = BOSdata.new()
htfadd249.settings                 := SettingsHTFadd249
htfadd249.candles                  := candlesadd249
htfadd249.bosdata                  := bosdataadd249
var CandleSet htfadd250                     = CandleSet.new()
var CandleSettings SettingsHTFadd250        = CandleSettings.new(htf="250", max_memory=3, htfint=250)
var Candle[] candlesadd250                  = array.new<Candle>(0)
var BOSdata bosdataadd250                   = BOSdata.new()
htfadd250.settings                 := SettingsHTFadd250
htfadd250.candles                  := candlesadd250
htfadd250.bosdata                  := bosdataadd250
var CandleSet htfadd251                     = CandleSet.new()
var CandleSettings SettingsHTFadd251        = CandleSettings.new(htf="251", max_memory=3, htfint=251)
var Candle[] candlesadd251                  = array.new<Candle>(0)
var BOSdata bosdataadd251                   = BOSdata.new()
htfadd251.settings                 := SettingsHTFadd251
htfadd251.candles                  := candlesadd251
htfadd251.bosdata                  := bosdataadd251
var CandleSet htfadd252                     = CandleSet.new()
var CandleSettings SettingsHTFadd252        = CandleSettings.new(htf="252", max_memory=3, htfint=252)
var Candle[] candlesadd252                  = array.new<Candle>(0)
var BOSdata bosdataadd252                   = BOSdata.new()
htfadd252.settings                 := SettingsHTFadd252
htfadd252.candles                  := candlesadd252
htfadd252.bosdata                  := bosdataadd252
var CandleSet htfadd253                     = CandleSet.new()
var CandleSettings SettingsHTFadd253        = CandleSettings.new(htf="253", max_memory=3, htfint=253)
var Candle[] candlesadd253                  = array.new<Candle>(0)
var BOSdata bosdataadd253                   = BOSdata.new()
htfadd253.settings                 := SettingsHTFadd253
htfadd253.candles                  := candlesadd253
htfadd253.bosdata                  := bosdataadd253
var CandleSet htfadd254                     = CandleSet.new()
var CandleSettings SettingsHTFadd254        = CandleSettings.new(htf="254", max_memory=3, htfint=254)
var Candle[] candlesadd254                  = array.new<Candle>(0)
var BOSdata bosdataadd254                   = BOSdata.new()
htfadd254.settings                 := SettingsHTFadd254
htfadd254.candles                  := candlesadd254
htfadd254.bosdata                  := bosdataadd254
var CandleSet htfadd255                     = CandleSet.new()
var CandleSettings SettingsHTFadd255        = CandleSettings.new(htf="255", max_memory=3, htfint=255)
var Candle[] candlesadd255                  = array.new<Candle>(0)
var BOSdata bosdataadd255                   = BOSdata.new()
htfadd255.settings                 := SettingsHTFadd255
htfadd255.candles                  := candlesadd255
htfadd255.bosdata                  := bosdataadd255
var CandleSet htfadd256                     = CandleSet.new()
var CandleSettings SettingsHTFadd256        = CandleSettings.new(htf="256", max_memory=3, htfint=256)
var Candle[] candlesadd256                  = array.new<Candle>(0)
var BOSdata bosdataadd256                   = BOSdata.new()
htfadd256.settings                 := SettingsHTFadd256
htfadd256.candles                  := candlesadd256
htfadd256.bosdata                  := bosdataadd256
var CandleSet htfadd257                     = CandleSet.new()
var CandleSettings SettingsHTFadd257        = CandleSettings.new(htf="257", max_memory=3, htfint=257)
var Candle[] candlesadd257                  = array.new<Candle>(0)
var BOSdata bosdataadd257                   = BOSdata.new()
htfadd257.settings                 := SettingsHTFadd257
htfadd257.candles                  := candlesadd257
htfadd257.bosdata                  := bosdataadd257
var CandleSet htfadd258                     = CandleSet.new()
var CandleSettings SettingsHTFadd258        = CandleSettings.new(htf="258", max_memory=3, htfint=258)
var Candle[] candlesadd258                  = array.new<Candle>(0)
var BOSdata bosdataadd258                   = BOSdata.new()
htfadd258.settings                 := SettingsHTFadd258
htfadd258.candles                  := candlesadd258
htfadd258.bosdata                  := bosdataadd258
var CandleSet htfadd259                     = CandleSet.new()
var CandleSettings SettingsHTFadd259        = CandleSettings.new(htf="259", max_memory=3, htfint=259)
var Candle[] candlesadd259                  = array.new<Candle>(0)
var BOSdata bosdataadd259                   = BOSdata.new()
htfadd259.settings                 := SettingsHTFadd259
htfadd259.candles                  := candlesadd259
htfadd259.bosdata                  := bosdataadd259
var CandleSet htfadd260                     = CandleSet.new()
var CandleSettings SettingsHTFadd260        = CandleSettings.new(htf="260", max_memory=3, htfint=260)
var Candle[] candlesadd260                  = array.new<Candle>(0)
var BOSdata bosdataadd260                   = BOSdata.new()
htfadd260.settings                 := SettingsHTFadd260
htfadd260.candles                  := candlesadd260
htfadd260.bosdata                  := bosdataadd260
var CandleSet htfadd261                     = CandleSet.new()
var CandleSettings SettingsHTFadd261        = CandleSettings.new(htf="261", max_memory=3, htfint=261)
var Candle[] candlesadd261                  = array.new<Candle>(0)
var BOSdata bosdataadd261                   = BOSdata.new()
htfadd261.settings                 := SettingsHTFadd261
htfadd261.candles                  := candlesadd261
htfadd261.bosdata                  := bosdataadd261
var CandleSet htfadd262                     = CandleSet.new()
var CandleSettings SettingsHTFadd262        = CandleSettings.new(htf="262", max_memory=3, htfint=262)
var Candle[] candlesadd262                  = array.new<Candle>(0)
var BOSdata bosdataadd262                   = BOSdata.new()
htfadd262.settings                 := SettingsHTFadd262
htfadd262.candles                  := candlesadd262
htfadd262.bosdata                  := bosdataadd262
var CandleSet htfadd263                     = CandleSet.new()
var CandleSettings SettingsHTFadd263        = CandleSettings.new(htf="263", max_memory=3, htfint=263)
var Candle[] candlesadd263                  = array.new<Candle>(0)
var BOSdata bosdataadd263                   = BOSdata.new()
htfadd263.settings                 := SettingsHTFadd263
htfadd263.candles                  := candlesadd263
htfadd263.bosdata                  := bosdataadd263
var CandleSet htfadd264                     = CandleSet.new()
var CandleSettings SettingsHTFadd264        = CandleSettings.new(htf="264", max_memory=3, htfint=264)
var Candle[] candlesadd264                  = array.new<Candle>(0)
var BOSdata bosdataadd264                   = BOSdata.new()
htfadd264.settings                 := SettingsHTFadd264
htfadd264.candles                  := candlesadd264
htfadd264.bosdata                  := bosdataadd264
var CandleSet htfadd265                     = CandleSet.new()
var CandleSettings SettingsHTFadd265        = CandleSettings.new(htf="265", max_memory=3, htfint=265)
var Candle[] candlesadd265                  = array.new<Candle>(0)
var BOSdata bosdataadd265                   = BOSdata.new()
htfadd265.settings                 := SettingsHTFadd265
htfadd265.candles                  := candlesadd265
htfadd265.bosdata                  := bosdataadd265
var CandleSet htfadd266                     = CandleSet.new()
var CandleSettings SettingsHTFadd266        = CandleSettings.new(htf="266", max_memory=3, htfint=266)
var Candle[] candlesadd266                  = array.new<Candle>(0)
var BOSdata bosdataadd266                   = BOSdata.new()
htfadd266.settings                 := SettingsHTFadd266
htfadd266.candles                  := candlesadd266
htfadd266.bosdata                  := bosdataadd266
var CandleSet htfadd267                     = CandleSet.new()
var CandleSettings SettingsHTFadd267        = CandleSettings.new(htf="267", max_memory=3, htfint=267)
var Candle[] candlesadd267                  = array.new<Candle>(0)
var BOSdata bosdataadd267                   = BOSdata.new()
htfadd267.settings                 := SettingsHTFadd267
htfadd267.candles                  := candlesadd267
htfadd267.bosdata                  := bosdataadd267
var CandleSet htfadd268                     = CandleSet.new()
var CandleSettings SettingsHTFadd268        = CandleSettings.new(htf="268", max_memory=3, htfint=268)
var Candle[] candlesadd268                  = array.new<Candle>(0)
var BOSdata bosdataadd268                   = BOSdata.new()
htfadd268.settings                 := SettingsHTFadd268
htfadd268.candles                  := candlesadd268
htfadd268.bosdata                  := bosdataadd268
var CandleSet htfadd269                     = CandleSet.new()
var CandleSettings SettingsHTFadd269        = CandleSettings.new(htf="269", max_memory=3, htfint=269)
var Candle[] candlesadd269                  = array.new<Candle>(0)
var BOSdata bosdataadd269                   = BOSdata.new()
htfadd269.settings                 := SettingsHTFadd269
htfadd269.candles                  := candlesadd269
htfadd269.bosdata                  := bosdataadd269
var CandleSet htfadd270                     = CandleSet.new()
var CandleSettings SettingsHTFadd270        = CandleSettings.new(htf="270", max_memory=3, htfint=270)
var Candle[] candlesadd270                  = array.new<Candle>(0)
var BOSdata bosdataadd270                   = BOSdata.new()
htfadd270.settings                 := SettingsHTFadd270
htfadd270.candles                  := candlesadd270
htfadd270.bosdata                  := bosdataadd270
var CandleSet htfadd271                     = CandleSet.new()
var CandleSettings SettingsHTFadd271        = CandleSettings.new(htf="271", max_memory=3, htfint=271)
var Candle[] candlesadd271                  = array.new<Candle>(0)
var BOSdata bosdataadd271                   = BOSdata.new()
htfadd271.settings                 := SettingsHTFadd271
htfadd271.candles                  := candlesadd271
htfadd271.bosdata                  := bosdataadd271
var CandleSet htfadd272                     = CandleSet.new()
var CandleSettings SettingsHTFadd272        = CandleSettings.new(htf="272", max_memory=3, htfint=272)
var Candle[] candlesadd272                  = array.new<Candle>(0)
var BOSdata bosdataadd272                   = BOSdata.new()
htfadd272.settings                 := SettingsHTFadd272
htfadd272.candles                  := candlesadd272
htfadd272.bosdata                  := bosdataadd272
var CandleSet htfadd273                     = CandleSet.new()
var CandleSettings SettingsHTFadd273        = CandleSettings.new(htf="273", max_memory=3, htfint=273)
var Candle[] candlesadd273                  = array.new<Candle>(0)
var BOSdata bosdataadd273                   = BOSdata.new()
htfadd273.settings                 := SettingsHTFadd273
htfadd273.candles                  := candlesadd273
htfadd273.bosdata                  := bosdataadd273
var CandleSet htfadd274                     = CandleSet.new()
var CandleSettings SettingsHTFadd274        = CandleSettings.new(htf="274", max_memory=3, htfint=274)
var Candle[] candlesadd274                  = array.new<Candle>(0)
var BOSdata bosdataadd274                   = BOSdata.new()
htfadd274.settings                 := SettingsHTFadd274
htfadd274.candles                  := candlesadd274
htfadd274.bosdata                  := bosdataadd274
var CandleSet htfadd275                     = CandleSet.new()
var CandleSettings SettingsHTFadd275        = CandleSettings.new(htf="275", max_memory=3, htfint=275)
var Candle[] candlesadd275                  = array.new<Candle>(0)
var BOSdata bosdataadd275                   = BOSdata.new()
htfadd275.settings                 := SettingsHTFadd275
htfadd275.candles                  := candlesadd275
htfadd275.bosdata                  := bosdataadd275
var CandleSet htfadd276                     = CandleSet.new()
var CandleSettings SettingsHTFadd276        = CandleSettings.new(htf="276", max_memory=3, htfint=276)
var Candle[] candlesadd276                  = array.new<Candle>(0)
var BOSdata bosdataadd276                   = BOSdata.new()
htfadd276.settings                 := SettingsHTFadd276
htfadd276.candles                  := candlesadd276
htfadd276.bosdata                  := bosdataadd276
var CandleSet htfadd277                     = CandleSet.new()
var CandleSettings SettingsHTFadd277        = CandleSettings.new(htf="277", max_memory=3, htfint=277)
var Candle[] candlesadd277                  = array.new<Candle>(0)
var BOSdata bosdataadd277                   = BOSdata.new()
htfadd277.settings                 := SettingsHTFadd277
htfadd277.candles                  := candlesadd277
htfadd277.bosdata                  := bosdataadd277
var CandleSet htfadd278                     = CandleSet.new()
var CandleSettings SettingsHTFadd278        = CandleSettings.new(htf="278", max_memory=3, htfint=278)
var Candle[] candlesadd278                  = array.new<Candle>(0)
var BOSdata bosdataadd278                   = BOSdata.new()
htfadd278.settings                 := SettingsHTFadd278
htfadd278.candles                  := candlesadd278
htfadd278.bosdata                  := bosdataadd278
var CandleSet htfadd279                     = CandleSet.new()
var CandleSettings SettingsHTFadd279        = CandleSettings.new(htf="279", max_memory=3, htfint=279)
var Candle[] candlesadd279                  = array.new<Candle>(0)
var BOSdata bosdataadd279                   = BOSdata.new()
htfadd279.settings                 := SettingsHTFadd279
htfadd279.candles                  := candlesadd279
htfadd279.bosdata                  := bosdataadd279
var CandleSet htfadd280                     = CandleSet.new()
var CandleSettings SettingsHTFadd280        = CandleSettings.new(htf="280", max_memory=3, htfint=280)
var Candle[] candlesadd280                  = array.new<Candle>(0)
var BOSdata bosdataadd280                   = BOSdata.new()
htfadd280.settings                 := SettingsHTFadd280
htfadd280.candles                  := candlesadd280
htfadd280.bosdata                  := bosdataadd280
var CandleSet htfadd281                     = CandleSet.new()
var CandleSettings SettingsHTFadd281        = CandleSettings.new(htf="281", max_memory=3, htfint=281)
var Candle[] candlesadd281                  = array.new<Candle>(0)
var BOSdata bosdataadd281                   = BOSdata.new()
htfadd281.settings                 := SettingsHTFadd281
htfadd281.candles                  := candlesadd281
htfadd281.bosdata                  := bosdataadd281
var CandleSet htfadd282                     = CandleSet.new()
var CandleSettings SettingsHTFadd282        = CandleSettings.new(htf="282", max_memory=3, htfint=282)
var Candle[] candlesadd282                  = array.new<Candle>(0)
var BOSdata bosdataadd282                   = BOSdata.new()
htfadd282.settings                 := SettingsHTFadd282
htfadd282.candles                  := candlesadd282
htfadd282.bosdata                  := bosdataadd282
var CandleSet htfadd283                     = CandleSet.new()
var CandleSettings SettingsHTFadd283        = CandleSettings.new(htf="283", max_memory=3, htfint=283)
var Candle[] candlesadd283                  = array.new<Candle>(0)
var BOSdata bosdataadd283                   = BOSdata.new()
htfadd283.settings                 := SettingsHTFadd283
htfadd283.candles                  := candlesadd283
htfadd283.bosdata                  := bosdataadd283
var CandleSet htfadd284                     = CandleSet.new()
var CandleSettings SettingsHTFadd284        = CandleSettings.new(htf="284", max_memory=3, htfint=284)
var Candle[] candlesadd284                  = array.new<Candle>(0)
var BOSdata bosdataadd284                   = BOSdata.new()
htfadd284.settings                 := SettingsHTFadd284
htfadd284.candles                  := candlesadd284
htfadd284.bosdata                  := bosdataadd284
var CandleSet htfadd285                     = CandleSet.new()
var CandleSettings SettingsHTFadd285        = CandleSettings.new(htf="285", max_memory=3, htfint=285)
var Candle[] candlesadd285                  = array.new<Candle>(0)
var BOSdata bosdataadd285                   = BOSdata.new()
htfadd285.settings                 := SettingsHTFadd285
htfadd285.candles                  := candlesadd285
htfadd285.bosdata                  := bosdataadd285
var CandleSet htfadd286                     = CandleSet.new()
var CandleSettings SettingsHTFadd286        = CandleSettings.new(htf="286", max_memory=3, htfint=286)
var Candle[] candlesadd286                  = array.new<Candle>(0)
var BOSdata bosdataadd286                   = BOSdata.new()
htfadd286.settings                 := SettingsHTFadd286
htfadd286.candles                  := candlesadd286
htfadd286.bosdata                  := bosdataadd286
var CandleSet htfadd287                     = CandleSet.new()
var CandleSettings SettingsHTFadd287        = CandleSettings.new(htf="287", max_memory=3, htfint=287)
var Candle[] candlesadd287                  = array.new<Candle>(0)
var BOSdata bosdataadd287                   = BOSdata.new()
htfadd287.settings                 := SettingsHTFadd287
htfadd287.candles                  := candlesadd287
htfadd287.bosdata                  := bosdataadd287
var CandleSet htfadd288                     = CandleSet.new()
var CandleSettings SettingsHTFadd288        = CandleSettings.new(htf="288", max_memory=3, htfint=288)
var Candle[] candlesadd288                  = array.new<Candle>(0)
var BOSdata bosdataadd288                   = BOSdata.new()
htfadd288.settings                 := SettingsHTFadd288
htfadd288.candles                  := candlesadd288
htfadd288.bosdata                  := bosdataadd288
var CandleSet htfadd289                     = CandleSet.new()
var CandleSettings SettingsHTFadd289        = CandleSettings.new(htf="289", max_memory=3, htfint=289)
var Candle[] candlesadd289                  = array.new<Candle>(0)
var BOSdata bosdataadd289                   = BOSdata.new()
htfadd289.settings                 := SettingsHTFadd289
htfadd289.candles                  := candlesadd289
htfadd289.bosdata                  := bosdataadd289
var CandleSet htfadd290                     = CandleSet.new()
var CandleSettings SettingsHTFadd290        = CandleSettings.new(htf="290", max_memory=3, htfint=290)
var Candle[] candlesadd290                  = array.new<Candle>(0)
var BOSdata bosdataadd290                   = BOSdata.new()
htfadd290.settings                 := SettingsHTFadd290
htfadd290.candles                  := candlesadd290
htfadd290.bosdata                  := bosdataadd290
var CandleSet htfadd291                     = CandleSet.new()
var CandleSettings SettingsHTFadd291        = CandleSettings.new(htf="291", max_memory=3, htfint=291)
var Candle[] candlesadd291                  = array.new<Candle>(0)
var BOSdata bosdataadd291                   = BOSdata.new()
htfadd291.settings                 := SettingsHTFadd291
htfadd291.candles                  := candlesadd291
htfadd291.bosdata                  := bosdataadd291
var CandleSet htfadd292                     = CandleSet.new()
var CandleSettings SettingsHTFadd292        = CandleSettings.new(htf="292", max_memory=3, htfint=292)
var Candle[] candlesadd292                  = array.new<Candle>(0)
var BOSdata bosdataadd292                   = BOSdata.new()
htfadd292.settings                 := SettingsHTFadd292
htfadd292.candles                  := candlesadd292
htfadd292.bosdata                  := bosdataadd292
var CandleSet htfadd293                     = CandleSet.new()
var CandleSettings SettingsHTFadd293        = CandleSettings.new(htf="293", max_memory=3, htfint=293)
var Candle[] candlesadd293                  = array.new<Candle>(0)
var BOSdata bosdataadd293                   = BOSdata.new()
htfadd293.settings                 := SettingsHTFadd293
htfadd293.candles                  := candlesadd293
htfadd293.bosdata                  := bosdataadd293
var CandleSet htfadd294                     = CandleSet.new()
var CandleSettings SettingsHTFadd294        = CandleSettings.new(htf="294", max_memory=3, htfint=294)
var Candle[] candlesadd294                  = array.new<Candle>(0)
var BOSdata bosdataadd294                   = BOSdata.new()
htfadd294.settings                 := SettingsHTFadd294
htfadd294.candles                  := candlesadd294
htfadd294.bosdata                  := bosdataadd294
var CandleSet htfadd295                     = CandleSet.new()
var CandleSettings SettingsHTFadd295        = CandleSettings.new(htf="295", max_memory=3, htfint=295)
var Candle[] candlesadd295                  = array.new<Candle>(0)
var BOSdata bosdataadd295                   = BOSdata.new()
htfadd295.settings                 := SettingsHTFadd295
htfadd295.candles                  := candlesadd295
htfadd295.bosdata                  := bosdataadd295
var CandleSet htfadd296                     = CandleSet.new()
var CandleSettings SettingsHTFadd296        = CandleSettings.new(htf="296", max_memory=3, htfint=296)
var Candle[] candlesadd296                  = array.new<Candle>(0)
var BOSdata bosdataadd296                   = BOSdata.new()
htfadd296.settings                 := SettingsHTFadd296
htfadd296.candles                  := candlesadd296
htfadd296.bosdata                  := bosdataadd296
var CandleSet htfadd297                     = CandleSet.new()
var CandleSettings SettingsHTFadd297        = CandleSettings.new(htf="297", max_memory=3, htfint=297)
var Candle[] candlesadd297                  = array.new<Candle>(0)
var BOSdata bosdataadd297                   = BOSdata.new()
htfadd297.settings                 := SettingsHTFadd297
htfadd297.candles                  := candlesadd297
htfadd297.bosdata                  := bosdataadd297
var CandleSet htfadd298                     = CandleSet.new()
var CandleSettings SettingsHTFadd298        = CandleSettings.new(htf="298", max_memory=3, htfint=298)
var Candle[] candlesadd298                  = array.new<Candle>(0)
var BOSdata bosdataadd298                   = BOSdata.new()
htfadd298.settings                 := SettingsHTFadd298
htfadd298.candles                  := candlesadd298
htfadd298.bosdata                  := bosdataadd298
var CandleSet htfadd299                     = CandleSet.new()
var CandleSettings SettingsHTFadd299        = CandleSettings.new(htf="299", max_memory=3, htfint=299)
var Candle[] candlesadd299                  = array.new<Candle>(0)
var BOSdata bosdataadd299                   = BOSdata.new()
htfadd299.settings                 := SettingsHTFadd299
htfadd299.candles                  := candlesadd299
htfadd299.bosdata                  := bosdataadd299
var CandleSet htfadd300                     = CandleSet.new()
var CandleSettings SettingsHTFadd300        = CandleSettings.new(htf="300", max_memory=3, htfint=300)
var Candle[] candlesadd300                  = array.new<Candle>(0)
var BOSdata bosdataadd300                   = BOSdata.new()
htfadd300.settings                 := SettingsHTFadd300
htfadd300.candles                  := candlesadd300
htfadd300.bosdata                  := bosdataadd300
var CandleSet htfadd301                     = CandleSet.new()
var CandleSettings SettingsHTFadd301        = CandleSettings.new(htf="301", max_memory=3, htfint=301)
var Candle[] candlesadd301                  = array.new<Candle>(0)
var BOSdata bosdataadd301                   = BOSdata.new()
htfadd301.settings                 := SettingsHTFadd301
htfadd301.candles                  := candlesadd301
htfadd301.bosdata                  := bosdataadd301
var CandleSet htfadd302                     = CandleSet.new()
var CandleSettings SettingsHTFadd302        = CandleSettings.new(htf="302", max_memory=3, htfint=302)
var Candle[] candlesadd302                  = array.new<Candle>(0)
var BOSdata bosdataadd302                   = BOSdata.new()
htfadd302.settings                 := SettingsHTFadd302
htfadd302.candles                  := candlesadd302
htfadd302.bosdata                  := bosdataadd302
var CandleSet htfadd303                     = CandleSet.new()
var CandleSettings SettingsHTFadd303        = CandleSettings.new(htf="303", max_memory=3, htfint=303)
var Candle[] candlesadd303                  = array.new<Candle>(0)
var BOSdata bosdataadd303                   = BOSdata.new()
htfadd303.settings                 := SettingsHTFadd303
htfadd303.candles                  := candlesadd303
htfadd303.bosdata                  := bosdataadd303
var CandleSet htfadd304                     = CandleSet.new()
var CandleSettings SettingsHTFadd304        = CandleSettings.new(htf="304", max_memory=3, htfint=304)
var Candle[] candlesadd304                  = array.new<Candle>(0)
var BOSdata bosdataadd304                   = BOSdata.new()
htfadd304.settings                 := SettingsHTFadd304
htfadd304.candles                  := candlesadd304
htfadd304.bosdata                  := bosdataadd304
var CandleSet htfadd305                     = CandleSet.new()
var CandleSettings SettingsHTFadd305        = CandleSettings.new(htf="305", max_memory=3, htfint=305)
var Candle[] candlesadd305                  = array.new<Candle>(0)
var BOSdata bosdataadd305                   = BOSdata.new()
htfadd305.settings                 := SettingsHTFadd305
htfadd305.candles                  := candlesadd305
htfadd305.bosdata                  := bosdataadd305
var CandleSet htfadd306                     = CandleSet.new()
var CandleSettings SettingsHTFadd306        = CandleSettings.new(htf="306", max_memory=3, htfint=306)
var Candle[] candlesadd306                  = array.new<Candle>(0)
var BOSdata bosdataadd306                   = BOSdata.new()
htfadd306.settings                 := SettingsHTFadd306
htfadd306.candles                  := candlesadd306
htfadd306.bosdata                  := bosdataadd306
var CandleSet htfadd307                     = CandleSet.new()
var CandleSettings SettingsHTFadd307        = CandleSettings.new(htf="307", max_memory=3, htfint=307)
var Candle[] candlesadd307                  = array.new<Candle>(0)
var BOSdata bosdataadd307                   = BOSdata.new()
htfadd307.settings                 := SettingsHTFadd307
htfadd307.candles                  := candlesadd307
htfadd307.bosdata                  := bosdataadd307
var CandleSet htfadd308                     = CandleSet.new()
var CandleSettings SettingsHTFadd308        = CandleSettings.new(htf="308", max_memory=3, htfint=308)
var Candle[] candlesadd308                  = array.new<Candle>(0)
var BOSdata bosdataadd308                   = BOSdata.new()
htfadd308.settings                 := SettingsHTFadd308
htfadd308.candles                  := candlesadd308
htfadd308.bosdata                  := bosdataadd308
var CandleSet htfadd309                     = CandleSet.new()
var CandleSettings SettingsHTFadd309        = CandleSettings.new(htf="309", max_memory=3, htfint=309)
var Candle[] candlesadd309                  = array.new<Candle>(0)
var BOSdata bosdataadd309                   = BOSdata.new()
htfadd309.settings                 := SettingsHTFadd309
htfadd309.candles                  := candlesadd309
htfadd309.bosdata                  := bosdataadd309
var CandleSet htfadd310                     = CandleSet.new()
var CandleSettings SettingsHTFadd310        = CandleSettings.new(htf="310", max_memory=3, htfint=310)
var Candle[] candlesadd310                  = array.new<Candle>(0)
var BOSdata bosdataadd310                   = BOSdata.new()
htfadd310.settings                 := SettingsHTFadd310
htfadd310.candles                  := candlesadd310
htfadd310.bosdata                  := bosdataadd310
var CandleSet htfadd311                     = CandleSet.new()
var CandleSettings SettingsHTFadd311        = CandleSettings.new(htf="311", max_memory=3, htfint=311)
var Candle[] candlesadd311                  = array.new<Candle>(0)
var BOSdata bosdataadd311                   = BOSdata.new()
htfadd311.settings                 := SettingsHTFadd311
htfadd311.candles                  := candlesadd311
htfadd311.bosdata                  := bosdataadd311
var CandleSet htfadd312                     = CandleSet.new()
var CandleSettings SettingsHTFadd312        = CandleSettings.new(htf="312", max_memory=3, htfint=312)
var Candle[] candlesadd312                  = array.new<Candle>(0)
var BOSdata bosdataadd312                   = BOSdata.new()
htfadd312.settings                 := SettingsHTFadd312
htfadd312.candles                  := candlesadd312
htfadd312.bosdata                  := bosdataadd312
var CandleSet htfadd313                     = CandleSet.new()
var CandleSettings SettingsHTFadd313        = CandleSettings.new(htf="313", max_memory=3, htfint=313)
var Candle[] candlesadd313                  = array.new<Candle>(0)
var BOSdata bosdataadd313                   = BOSdata.new()
htfadd313.settings                 := SettingsHTFadd313
htfadd313.candles                  := candlesadd313
htfadd313.bosdata                  := bosdataadd313
var CandleSet htfadd314                     = CandleSet.new()
var CandleSettings SettingsHTFadd314        = CandleSettings.new(htf="314", max_memory=3, htfint=314)
var Candle[] candlesadd314                  = array.new<Candle>(0)
var BOSdata bosdataadd314                   = BOSdata.new()
htfadd314.settings                 := SettingsHTFadd314
htfadd314.candles                  := candlesadd314
htfadd314.bosdata                  := bosdataadd314
var CandleSet htfadd315                     = CandleSet.new()
var CandleSettings SettingsHTFadd315        = CandleSettings.new(htf="315", max_memory=3, htfint=315)
var Candle[] candlesadd315                  = array.new<Candle>(0)
var BOSdata bosdataadd315                   = BOSdata.new()
htfadd315.settings                 := SettingsHTFadd315
htfadd315.candles                  := candlesadd315
htfadd315.bosdata                  := bosdataadd315
var CandleSet htfadd316                     = CandleSet.new()
var CandleSettings SettingsHTFadd316        = CandleSettings.new(htf="316", max_memory=3, htfint=316)
var Candle[] candlesadd316                  = array.new<Candle>(0)
var BOSdata bosdataadd316                   = BOSdata.new()
htfadd316.settings                 := SettingsHTFadd316
htfadd316.candles                  := candlesadd316
htfadd316.bosdata                  := bosdataadd316
var CandleSet htfadd317                     = CandleSet.new()
var CandleSettings SettingsHTFadd317        = CandleSettings.new(htf="317", max_memory=3, htfint=317)
var Candle[] candlesadd317                  = array.new<Candle>(0)
var BOSdata bosdataadd317                   = BOSdata.new()
htfadd317.settings                 := SettingsHTFadd317
htfadd317.candles                  := candlesadd317
htfadd317.bosdata                  := bosdataadd317
var CandleSet htfadd318                     = CandleSet.new()
var CandleSettings SettingsHTFadd318        = CandleSettings.new(htf="318", max_memory=3, htfint=318)
var Candle[] candlesadd318                  = array.new<Candle>(0)
var BOSdata bosdataadd318                   = BOSdata.new()
htfadd318.settings                 := SettingsHTFadd318
htfadd318.candles                  := candlesadd318
htfadd318.bosdata                  := bosdataadd318
var CandleSet htfadd319                     = CandleSet.new()
var CandleSettings SettingsHTFadd319        = CandleSettings.new(htf="319", max_memory=3, htfint=319)
var Candle[] candlesadd319                  = array.new<Candle>(0)
var BOSdata bosdataadd319                   = BOSdata.new()
htfadd319.settings                 := SettingsHTFadd319
htfadd319.candles                  := candlesadd319
htfadd319.bosdata                  := bosdataadd319
var CandleSet htfadd320                     = CandleSet.new()
var CandleSettings SettingsHTFadd320        = CandleSettings.new(htf="320", max_memory=3, htfint=320)
var Candle[] candlesadd320                  = array.new<Candle>(0)
var BOSdata bosdataadd320                   = BOSdata.new()
htfadd320.settings                 := SettingsHTFadd320
htfadd320.candles                  := candlesadd320
htfadd320.bosdata                  := bosdataadd320
var CandleSet htfadd321                     = CandleSet.new()
var CandleSettings SettingsHTFadd321        = CandleSettings.new(htf="321", max_memory=3, htfint=321)
var Candle[] candlesadd321                  = array.new<Candle>(0)
var BOSdata bosdataadd321                   = BOSdata.new()
htfadd321.settings                 := SettingsHTFadd321
htfadd321.candles                  := candlesadd321
htfadd321.bosdata                  := bosdataadd321
var CandleSet htfadd322                     = CandleSet.new()
var CandleSettings SettingsHTFadd322        = CandleSettings.new(htf="322", max_memory=3, htfint=322)
var Candle[] candlesadd322                  = array.new<Candle>(0)
var BOSdata bosdataadd322                   = BOSdata.new()
htfadd322.settings                 := SettingsHTFadd322
htfadd322.candles                  := candlesadd322
htfadd322.bosdata                  := bosdataadd322
var CandleSet htfadd323                     = CandleSet.new()
var CandleSettings SettingsHTFadd323        = CandleSettings.new(htf="323", max_memory=3, htfint=323)
var Candle[] candlesadd323                  = array.new<Candle>(0)
var BOSdata bosdataadd323                   = BOSdata.new()
htfadd323.settings                 := SettingsHTFadd323
htfadd323.candles                  := candlesadd323
htfadd323.bosdata                  := bosdataadd323
var CandleSet htfadd324                     = CandleSet.new()
var CandleSettings SettingsHTFadd324        = CandleSettings.new(htf="324", max_memory=3, htfint=324)
var Candle[] candlesadd324                  = array.new<Candle>(0)
var BOSdata bosdataadd324                   = BOSdata.new()
htfadd324.settings                 := SettingsHTFadd324
htfadd324.candles                  := candlesadd324
htfadd324.bosdata                  := bosdataadd324
var CandleSet htfadd325                     = CandleSet.new()
var CandleSettings SettingsHTFadd325        = CandleSettings.new(htf="325", max_memory=3, htfint=325)
var Candle[] candlesadd325                  = array.new<Candle>(0)
var BOSdata bosdataadd325                   = BOSdata.new()
htfadd325.settings                 := SettingsHTFadd325
htfadd325.candles                  := candlesadd325
htfadd325.bosdata                  := bosdataadd325
var CandleSet htfadd326                     = CandleSet.new()
var CandleSettings SettingsHTFadd326        = CandleSettings.new(htf="326", max_memory=3, htfint=326)
var Candle[] candlesadd326                  = array.new<Candle>(0)
var BOSdata bosdataadd326                   = BOSdata.new()
htfadd326.settings                 := SettingsHTFadd326
htfadd326.candles                  := candlesadd326
htfadd326.bosdata                  := bosdataadd326
var CandleSet htfadd327                     = CandleSet.new()
var CandleSettings SettingsHTFadd327        = CandleSettings.new(htf="327", max_memory=3, htfint=327)
var Candle[] candlesadd327                  = array.new<Candle>(0)
var BOSdata bosdataadd327                   = BOSdata.new()
htfadd327.settings                 := SettingsHTFadd327
htfadd327.candles                  := candlesadd327
htfadd327.bosdata                  := bosdataadd327
var CandleSet htfadd328                     = CandleSet.new()
var CandleSettings SettingsHTFadd328        = CandleSettings.new(htf="328", max_memory=3, htfint=328)
var Candle[] candlesadd328                  = array.new<Candle>(0)
var BOSdata bosdataadd328                   = BOSdata.new()
htfadd328.settings                 := SettingsHTFadd328
htfadd328.candles                  := candlesadd328
htfadd328.bosdata                  := bosdataadd328
var CandleSet htfadd329                     = CandleSet.new()
var CandleSettings SettingsHTFadd329        = CandleSettings.new(htf="329", max_memory=3, htfint=329)
var Candle[] candlesadd329                  = array.new<Candle>(0)
var BOSdata bosdataadd329                   = BOSdata.new()
htfadd329.settings                 := SettingsHTFadd329
htfadd329.candles                  := candlesadd329
htfadd329.bosdata                  := bosdataadd329
var CandleSet htfadd330                     = CandleSet.new()
var CandleSettings SettingsHTFadd330        = CandleSettings.new(htf="330", max_memory=3, htfint=330)
var Candle[] candlesadd330                  = array.new<Candle>(0)
var BOSdata bosdataadd330                   = BOSdata.new()
htfadd330.settings                 := SettingsHTFadd330
htfadd330.candles                  := candlesadd330
htfadd330.bosdata                  := bosdataadd330
var CandleSet htfadd331                     = CandleSet.new()
var CandleSettings SettingsHTFadd331        = CandleSettings.new(htf="331", max_memory=3, htfint=331)
var Candle[] candlesadd331                  = array.new<Candle>(0)
var BOSdata bosdataadd331                   = BOSdata.new()
htfadd331.settings                 := SettingsHTFadd331
htfadd331.candles                  := candlesadd331
htfadd331.bosdata                  := bosdataadd331
var CandleSet htfadd332                     = CandleSet.new()
var CandleSettings SettingsHTFadd332        = CandleSettings.new(htf="332", max_memory=3, htfint=332)
var Candle[] candlesadd332                  = array.new<Candle>(0)
var BOSdata bosdataadd332                   = BOSdata.new()
htfadd332.settings                 := SettingsHTFadd332
htfadd332.candles                  := candlesadd332
htfadd332.bosdata                  := bosdataadd332
var CandleSet htfadd333                     = CandleSet.new()
var CandleSettings SettingsHTFadd333        = CandleSettings.new(htf="333", max_memory=3, htfint=333)
var Candle[] candlesadd333                  = array.new<Candle>(0)
var BOSdata bosdataadd333                   = BOSdata.new()
htfadd333.settings                 := SettingsHTFadd333
htfadd333.candles                  := candlesadd333
htfadd333.bosdata                  := bosdataadd333
var CandleSet htfadd334                     = CandleSet.new()
var CandleSettings SettingsHTFadd334        = CandleSettings.new(htf="334", max_memory=3, htfint=334)
var Candle[] candlesadd334                  = array.new<Candle>(0)
var BOSdata bosdataadd334                   = BOSdata.new()
htfadd334.settings                 := SettingsHTFadd334
htfadd334.candles                  := candlesadd334
htfadd334.bosdata                  := bosdataadd334
var CandleSet htfadd335                     = CandleSet.new()
var CandleSettings SettingsHTFadd335        = CandleSettings.new(htf="335", max_memory=3, htfint=335)
var Candle[] candlesadd335                  = array.new<Candle>(0)
var BOSdata bosdataadd335                   = BOSdata.new()
htfadd335.settings                 := SettingsHTFadd335
htfadd335.candles                  := candlesadd335
htfadd335.bosdata                  := bosdataadd335
var CandleSet htfadd336                     = CandleSet.new()
var CandleSettings SettingsHTFadd336        = CandleSettings.new(htf="336", max_memory=3, htfint=336)
var Candle[] candlesadd336                  = array.new<Candle>(0)
var BOSdata bosdataadd336                   = BOSdata.new()
htfadd336.settings                 := SettingsHTFadd336
htfadd336.candles                  := candlesadd336
htfadd336.bosdata                  := bosdataadd336
var CandleSet htfadd337                     = CandleSet.new()
var CandleSettings SettingsHTFadd337        = CandleSettings.new(htf="337", max_memory=3, htfint=337)
var Candle[] candlesadd337                  = array.new<Candle>(0)
var BOSdata bosdataadd337                   = BOSdata.new()
htfadd337.settings                 := SettingsHTFadd337
htfadd337.candles                  := candlesadd337
htfadd337.bosdata                  := bosdataadd337
var CandleSet htfadd338                     = CandleSet.new()
var CandleSettings SettingsHTFadd338        = CandleSettings.new(htf="338", max_memory=3, htfint=338)
var Candle[] candlesadd338                  = array.new<Candle>(0)
var BOSdata bosdataadd338                   = BOSdata.new()
htfadd338.settings                 := SettingsHTFadd338
htfadd338.candles                  := candlesadd338
htfadd338.bosdata                  := bosdataadd338
var CandleSet htfadd339                     = CandleSet.new()
var CandleSettings SettingsHTFadd339        = CandleSettings.new(htf="339", max_memory=3, htfint=339)
var Candle[] candlesadd339                  = array.new<Candle>(0)
var BOSdata bosdataadd339                   = BOSdata.new()
htfadd339.settings                 := SettingsHTFadd339
htfadd339.candles                  := candlesadd339
htfadd339.bosdata                  := bosdataadd339
var CandleSet htfadd340                     = CandleSet.new()
var CandleSettings SettingsHTFadd340        = CandleSettings.new(htf="340", max_memory=3, htfint=340)
var Candle[] candlesadd340                  = array.new<Candle>(0)
var BOSdata bosdataadd340                   = BOSdata.new()
htfadd340.settings                 := SettingsHTFadd340
htfadd340.candles                  := candlesadd340
htfadd340.bosdata                  := bosdataadd340
var CandleSet htfadd341                     = CandleSet.new()
var CandleSettings SettingsHTFadd341        = CandleSettings.new(htf="341", max_memory=3, htfint=341)
var Candle[] candlesadd341                  = array.new<Candle>(0)
var BOSdata bosdataadd341                   = BOSdata.new()
htfadd341.settings                 := SettingsHTFadd341
htfadd341.candles                  := candlesadd341
htfadd341.bosdata                  := bosdataadd341
var CandleSet htfadd342                     = CandleSet.new()
var CandleSettings SettingsHTFadd342        = CandleSettings.new(htf="342", max_memory=3, htfint=342)
var Candle[] candlesadd342                  = array.new<Candle>(0)
var BOSdata bosdataadd342                   = BOSdata.new()
htfadd342.settings                 := SettingsHTFadd342
htfadd342.candles                  := candlesadd342
htfadd342.bosdata                  := bosdataadd342
var CandleSet htfadd343                     = CandleSet.new()
var CandleSettings SettingsHTFadd343        = CandleSettings.new(htf="343", max_memory=3, htfint=343)
var Candle[] candlesadd343                  = array.new<Candle>(0)
var BOSdata bosdataadd343                   = BOSdata.new()
htfadd343.settings                 := SettingsHTFadd343
htfadd343.candles                  := candlesadd343
htfadd343.bosdata                  := bosdataadd343
var CandleSet htfadd344                     = CandleSet.new()
var CandleSettings SettingsHTFadd344        = CandleSettings.new(htf="344", max_memory=3, htfint=344)
var Candle[] candlesadd344                  = array.new<Candle>(0)
var BOSdata bosdataadd344                   = BOSdata.new()
htfadd344.settings                 := SettingsHTFadd344
htfadd344.candles                  := candlesadd344
htfadd344.bosdata                  := bosdataadd344
var CandleSet htfadd345                     = CandleSet.new()
var CandleSettings SettingsHTFadd345        = CandleSettings.new(htf="345", max_memory=3, htfint=345)
var Candle[] candlesadd345                  = array.new<Candle>(0)
var BOSdata bosdataadd345                   = BOSdata.new()
htfadd345.settings                 := SettingsHTFadd345
htfadd345.candles                  := candlesadd345
htfadd345.bosdata                  := bosdataadd345
var CandleSet htfadd346                     = CandleSet.new()
var CandleSettings SettingsHTFadd346        = CandleSettings.new(htf="346", max_memory=3, htfint=346)
var Candle[] candlesadd346                  = array.new<Candle>(0)
var BOSdata bosdataadd346                   = BOSdata.new()
htfadd346.settings                 := SettingsHTFadd346
htfadd346.candles                  := candlesadd346
htfadd346.bosdata                  := bosdataadd346
var CandleSet htfadd347                     = CandleSet.new()
var CandleSettings SettingsHTFadd347        = CandleSettings.new(htf="347", max_memory=3, htfint=347)
var Candle[] candlesadd347                  = array.new<Candle>(0)
var BOSdata bosdataadd347                   = BOSdata.new()
htfadd347.settings                 := SettingsHTFadd347
htfadd347.candles                  := candlesadd347
htfadd347.bosdata                  := bosdataadd347
var CandleSet htfadd348                     = CandleSet.new()
var CandleSettings SettingsHTFadd348        = CandleSettings.new(htf="348", max_memory=3, htfint=348)
var Candle[] candlesadd348                  = array.new<Candle>(0)
var BOSdata bosdataadd348                   = BOSdata.new()
htfadd348.settings                 := SettingsHTFadd348
htfadd348.candles                  := candlesadd348
htfadd348.bosdata                  := bosdataadd348
var CandleSet htfadd349                     = CandleSet.new()
var CandleSettings SettingsHTFadd349        = CandleSettings.new(htf="349", max_memory=3, htfint=349)
var Candle[] candlesadd349                  = array.new<Candle>(0)
var BOSdata bosdataadd349                   = BOSdata.new()
htfadd349.settings                 := SettingsHTFadd349
htfadd349.candles                  := candlesadd349
htfadd349.bosdata                  := bosdataadd349
var CandleSet htfadd350                     = CandleSet.new()
var CandleSettings SettingsHTFadd350        = CandleSettings.new(htf="350", max_memory=3, htfint=350)
var Candle[] candlesadd350                  = array.new<Candle>(0)
var BOSdata bosdataadd350                   = BOSdata.new()
htfadd350.settings                 := SettingsHTFadd350
htfadd350.candles                  := candlesadd350
htfadd350.bosdata                  := bosdataadd350
var CandleSet htfadd351                     = CandleSet.new()
var CandleSettings SettingsHTFadd351        = CandleSettings.new(htf="351", max_memory=3, htfint=351)
var Candle[] candlesadd351                  = array.new<Candle>(0)
var BOSdata bosdataadd351                   = BOSdata.new()
htfadd351.settings                 := SettingsHTFadd351
htfadd351.candles                  := candlesadd351
htfadd351.bosdata                  := bosdataadd351
var CandleSet htfadd352                     = CandleSet.new()
var CandleSettings SettingsHTFadd352        = CandleSettings.new(htf="352", max_memory=3, htfint=352)
var Candle[] candlesadd352                  = array.new<Candle>(0)
var BOSdata bosdataadd352                   = BOSdata.new()
htfadd352.settings                 := SettingsHTFadd352
htfadd352.candles                  := candlesadd352
htfadd352.bosdata                  := bosdataadd352
var CandleSet htfadd353                     = CandleSet.new()
var CandleSettings SettingsHTFadd353        = CandleSettings.new(htf="353", max_memory=3, htfint=353)
var Candle[] candlesadd353                  = array.new<Candle>(0)
var BOSdata bosdataadd353                   = BOSdata.new()
htfadd353.settings                 := SettingsHTFadd353
htfadd353.candles                  := candlesadd353
htfadd353.bosdata                  := bosdataadd353
var CandleSet htfadd354                     = CandleSet.new()
var CandleSettings SettingsHTFadd354        = CandleSettings.new(htf="354", max_memory=3, htfint=354)
var Candle[] candlesadd354                  = array.new<Candle>(0)
var BOSdata bosdataadd354                   = BOSdata.new()
htfadd354.settings                 := SettingsHTFadd354
htfadd354.candles                  := candlesadd354
htfadd354.bosdata                  := bosdataadd354
var CandleSet htfadd355                     = CandleSet.new()
var CandleSettings SettingsHTFadd355        = CandleSettings.new(htf="355", max_memory=3, htfint=355)
var Candle[] candlesadd355                  = array.new<Candle>(0)
var BOSdata bosdataadd355                   = BOSdata.new()
htfadd355.settings                 := SettingsHTFadd355
htfadd355.candles                  := candlesadd355
htfadd355.bosdata                  := bosdataadd355
var CandleSet htfadd356                     = CandleSet.new()
var CandleSettings SettingsHTFadd356        = CandleSettings.new(htf="356", max_memory=3, htfint=356)
var Candle[] candlesadd356                  = array.new<Candle>(0)
var BOSdata bosdataadd356                   = BOSdata.new()
htfadd356.settings                 := SettingsHTFadd356
htfadd356.candles                  := candlesadd356
htfadd356.bosdata                  := bosdataadd356
var CandleSet htfadd357                     = CandleSet.new()
var CandleSettings SettingsHTFadd357        = CandleSettings.new(htf="357", max_memory=3, htfint=357)
var Candle[] candlesadd357                  = array.new<Candle>(0)
var BOSdata bosdataadd357                   = BOSdata.new()
htfadd357.settings                 := SettingsHTFadd357
htfadd357.candles                  := candlesadd357
htfadd357.bosdata                  := bosdataadd357
var CandleSet htfadd358                     = CandleSet.new()
var CandleSettings SettingsHTFadd358        = CandleSettings.new(htf="358", max_memory=3, htfint=358)
var Candle[] candlesadd358                  = array.new<Candle>(0)
var BOSdata bosdataadd358                   = BOSdata.new()
htfadd358.settings                 := SettingsHTFadd358
htfadd358.candles                  := candlesadd358
htfadd358.bosdata                  := bosdataadd358
var CandleSet htfadd359                     = CandleSet.new()
var CandleSettings SettingsHTFadd359        = CandleSettings.new(htf="359", max_memory=3, htfint=359)
var Candle[] candlesadd359                  = array.new<Candle>(0)
var BOSdata bosdataadd359                   = BOSdata.new()
htfadd359.settings                 := SettingsHTFadd359
htfadd359.candles                  := candlesadd359
htfadd359.bosdata                  := bosdataadd359
var CandleSet htfadd360                     = CandleSet.new()
var CandleSettings SettingsHTFadd360        = CandleSettings.new(htf="360", max_memory=3, htfint=360)
var Candle[] candlesadd360                  = array.new<Candle>(0)
var BOSdata bosdataadd360                   = BOSdata.new()
htfadd360.settings                 := SettingsHTFadd360
htfadd360.candles                  := candlesadd360
htfadd360.bosdata                  := bosdataadd360
var CandleSet htfadd361                     = CandleSet.new()
var CandleSettings SettingsHTFadd361        = CandleSettings.new(htf="361", max_memory=3, htfint=361)
var Candle[] candlesadd361                  = array.new<Candle>(0)
var BOSdata bosdataadd361                   = BOSdata.new()
htfadd361.settings                 := SettingsHTFadd361
htfadd361.candles                  := candlesadd361
htfadd361.bosdata                  := bosdataadd361
var CandleSet htfadd362                     = CandleSet.new()
var CandleSettings SettingsHTFadd362        = CandleSettings.new(htf="362", max_memory=3, htfint=362)
var Candle[] candlesadd362                  = array.new<Candle>(0)
var BOSdata bosdataadd362                   = BOSdata.new()
htfadd362.settings                 := SettingsHTFadd362
htfadd362.candles                  := candlesadd362
htfadd362.bosdata                  := bosdataadd362
var CandleSet htfadd363                     = CandleSet.new()
var CandleSettings SettingsHTFadd363        = CandleSettings.new(htf="363", max_memory=3, htfint=363)
var Candle[] candlesadd363                  = array.new<Candle>(0)
var BOSdata bosdataadd363                   = BOSdata.new()
htfadd363.settings                 := SettingsHTFadd363
htfadd363.candles                  := candlesadd363
htfadd363.bosdata                  := bosdataadd363
var CandleSet htfadd364                     = CandleSet.new()
var CandleSettings SettingsHTFadd364        = CandleSettings.new(htf="364", max_memory=3, htfint=364)
var Candle[] candlesadd364                  = array.new<Candle>(0)
var BOSdata bosdataadd364                   = BOSdata.new()
htfadd364.settings                 := SettingsHTFadd364
htfadd364.candles                  := candlesadd364
htfadd364.bosdata                  := bosdataadd364
var CandleSet htfadd365                     = CandleSet.new()
var CandleSettings SettingsHTFadd365        = CandleSettings.new(htf="365", max_memory=3, htfint=365)
var Candle[] candlesadd365                  = array.new<Candle>(0)
var BOSdata bosdataadd365                   = BOSdata.new()
htfadd365.settings                 := SettingsHTFadd365
htfadd365.candles                  := candlesadd365
htfadd365.bosdata                  := bosdataadd365
var CandleSet htfadd366                     = CandleSet.new()
var CandleSettings SettingsHTFadd366        = CandleSettings.new(htf="366", max_memory=3, htfint=366)
var Candle[] candlesadd366                  = array.new<Candle>(0)
var BOSdata bosdataadd366                   = BOSdata.new()
htfadd366.settings                 := SettingsHTFadd366
htfadd366.candles                  := candlesadd366
htfadd366.bosdata                  := bosdataadd366
var CandleSet htfadd367                     = CandleSet.new()
var CandleSettings SettingsHTFadd367        = CandleSettings.new(htf="367", max_memory=3, htfint=367)
var Candle[] candlesadd367                  = array.new<Candle>(0)
var BOSdata bosdataadd367                   = BOSdata.new()
htfadd367.settings                 := SettingsHTFadd367
htfadd367.candles                  := candlesadd367
htfadd367.bosdata                  := bosdataadd367
var CandleSet htfadd368                     = CandleSet.new()
var CandleSettings SettingsHTFadd368        = CandleSettings.new(htf="368", max_memory=3, htfint=368)
var Candle[] candlesadd368                  = array.new<Candle>(0)
var BOSdata bosdataadd368                   = BOSdata.new()
htfadd368.settings                 := SettingsHTFadd368
htfadd368.candles                  := candlesadd368
htfadd368.bosdata                  := bosdataadd368
var CandleSet htfadd369                     = CandleSet.new()
var CandleSettings SettingsHTFadd369        = CandleSettings.new(htf="369", max_memory=3, htfint=369)
var Candle[] candlesadd369                  = array.new<Candle>(0)
var BOSdata bosdataadd369                   = BOSdata.new()
htfadd369.settings                 := SettingsHTFadd369
htfadd369.candles                  := candlesadd369
htfadd369.bosdata                  := bosdataadd369
var CandleSet htfadd370                     = CandleSet.new()
var CandleSettings SettingsHTFadd370        = CandleSettings.new(htf="370", max_memory=3, htfint=370)
var Candle[] candlesadd370                  = array.new<Candle>(0)
var BOSdata bosdataadd370                   = BOSdata.new()
htfadd370.settings                 := SettingsHTFadd370
htfadd370.candles                  := candlesadd370
htfadd370.bosdata                  := bosdataadd370
var CandleSet htfadd371                     = CandleSet.new()
var CandleSettings SettingsHTFadd371        = CandleSettings.new(htf="371", max_memory=3, htfint=371)
var Candle[] candlesadd371                  = array.new<Candle>(0)
var BOSdata bosdataadd371                   = BOSdata.new()
htfadd371.settings                 := SettingsHTFadd371
htfadd371.candles                  := candlesadd371
htfadd371.bosdata                  := bosdataadd371
var CandleSet htfadd372                     = CandleSet.new()
var CandleSettings SettingsHTFadd372        = CandleSettings.new(htf="372", max_memory=3, htfint=372)
var Candle[] candlesadd372                  = array.new<Candle>(0)
var BOSdata bosdataadd372                   = BOSdata.new()
htfadd372.settings                 := SettingsHTFadd372
htfadd372.candles                  := candlesadd372
htfadd372.bosdata                  := bosdataadd372
var CandleSet htfadd373                     = CandleSet.new()
var CandleSettings SettingsHTFadd373        = CandleSettings.new(htf="373", max_memory=3, htfint=373)
var Candle[] candlesadd373                  = array.new<Candle>(0)
var BOSdata bosdataadd373                   = BOSdata.new()
htfadd373.settings                 := SettingsHTFadd373
htfadd373.candles                  := candlesadd373
htfadd373.bosdata                  := bosdataadd373
var CandleSet htfadd374                     = CandleSet.new()
var CandleSettings SettingsHTFadd374        = CandleSettings.new(htf="374", max_memory=3, htfint=374)
var Candle[] candlesadd374                  = array.new<Candle>(0)
var BOSdata bosdataadd374                   = BOSdata.new()
htfadd374.settings                 := SettingsHTFadd374
htfadd374.candles                  := candlesadd374
htfadd374.bosdata                  := bosdataadd374
var CandleSet htfadd375                     = CandleSet.new()
var CandleSettings SettingsHTFadd375        = CandleSettings.new(htf="375", max_memory=3, htfint=375)
var Candle[] candlesadd375                  = array.new<Candle>(0)
var BOSdata bosdataadd375                   = BOSdata.new()
htfadd375.settings                 := SettingsHTFadd375
htfadd375.candles                  := candlesadd375
htfadd375.bosdata                  := bosdataadd375
var CandleSet htfadd376                     = CandleSet.new()
var CandleSettings SettingsHTFadd376        = CandleSettings.new(htf="376", max_memory=3, htfint=376)
var Candle[] candlesadd376                  = array.new<Candle>(0)
var BOSdata bosdataadd376                   = BOSdata.new()
htfadd376.settings                 := SettingsHTFadd376
htfadd376.candles                  := candlesadd376
htfadd376.bosdata                  := bosdataadd376
var CandleSet htfadd377                     = CandleSet.new()
var CandleSettings SettingsHTFadd377        = CandleSettings.new(htf="377", max_memory=3, htfint=377)
var Candle[] candlesadd377                  = array.new<Candle>(0)
var BOSdata bosdataadd377                   = BOSdata.new()
htfadd377.settings                 := SettingsHTFadd377
htfadd377.candles                  := candlesadd377
htfadd377.bosdata                  := bosdataadd377
var CandleSet htfadd378                     = CandleSet.new()
var CandleSettings SettingsHTFadd378        = CandleSettings.new(htf="378", max_memory=3, htfint=378)
var Candle[] candlesadd378                  = array.new<Candle>(0)
var BOSdata bosdataadd378                   = BOSdata.new()
htfadd378.settings                 := SettingsHTFadd378
htfadd378.candles                  := candlesadd378
htfadd378.bosdata                  := bosdataadd378
var CandleSet htfadd379                     = CandleSet.new()
var CandleSettings SettingsHTFadd379        = CandleSettings.new(htf="379", max_memory=3, htfint=379)
var Candle[] candlesadd379                  = array.new<Candle>(0)
var BOSdata bosdataadd379                   = BOSdata.new()
htfadd379.settings                 := SettingsHTFadd379
htfadd379.candles                  := candlesadd379
htfadd379.bosdata                  := bosdataadd379
var CandleSet htfadd380                     = CandleSet.new()
var CandleSettings SettingsHTFadd380        = CandleSettings.new(htf="380", max_memory=3, htfint=380)
var Candle[] candlesadd380                  = array.new<Candle>(0)
var BOSdata bosdataadd380                   = BOSdata.new()
htfadd380.settings                 := SettingsHTFadd380
htfadd380.candles                  := candlesadd380
htfadd380.bosdata                  := bosdataadd380
var CandleSet htfadd381                     = CandleSet.new()
var CandleSettings SettingsHTFadd381        = CandleSettings.new(htf="381", max_memory=3, htfint=381)
var Candle[] candlesadd381                  = array.new<Candle>(0)
var BOSdata bosdataadd381                   = BOSdata.new()
htfadd381.settings                 := SettingsHTFadd381
htfadd381.candles                  := candlesadd381
htfadd381.bosdata                  := bosdataadd381
var CandleSet htfadd382                     = CandleSet.new()
var CandleSettings SettingsHTFadd382        = CandleSettings.new(htf="382", max_memory=3, htfint=382)
var Candle[] candlesadd382                  = array.new<Candle>(0)
var BOSdata bosdataadd382                   = BOSdata.new()
htfadd382.settings                 := SettingsHTFadd382
htfadd382.candles                  := candlesadd382
htfadd382.bosdata                  := bosdataadd382
var CandleSet htfadd383                     = CandleSet.new()
var CandleSettings SettingsHTFadd383        = CandleSettings.new(htf="383", max_memory=3, htfint=383)
var Candle[] candlesadd383                  = array.new<Candle>(0)
var BOSdata bosdataadd383                   = BOSdata.new()
htfadd383.settings                 := SettingsHTFadd383
htfadd383.candles                  := candlesadd383
htfadd383.bosdata                  := bosdataadd383
var CandleSet htfadd384                     = CandleSet.new()
var CandleSettings SettingsHTFadd384        = CandleSettings.new(htf="384", max_memory=3, htfint=384)
var Candle[] candlesadd384                  = array.new<Candle>(0)
var BOSdata bosdataadd384                   = BOSdata.new()
htfadd384.settings                 := SettingsHTFadd384
htfadd384.candles                  := candlesadd384
htfadd384.bosdata                  := bosdataadd384
var CandleSet htfadd385                     = CandleSet.new()
var CandleSettings SettingsHTFadd385        = CandleSettings.new(htf="385", max_memory=3, htfint=385)
var Candle[] candlesadd385                  = array.new<Candle>(0)
var BOSdata bosdataadd385                   = BOSdata.new()
htfadd385.settings                 := SettingsHTFadd385
htfadd385.candles                  := candlesadd385
htfadd385.bosdata                  := bosdataadd385
var CandleSet htfadd386                     = CandleSet.new()
var CandleSettings SettingsHTFadd386        = CandleSettings.new(htf="386", max_memory=3, htfint=386)
var Candle[] candlesadd386                  = array.new<Candle>(0)
var BOSdata bosdataadd386                   = BOSdata.new()
htfadd386.settings                 := SettingsHTFadd386
htfadd386.candles                  := candlesadd386
htfadd386.bosdata                  := bosdataadd386
var CandleSet htfadd387                     = CandleSet.new()
var CandleSettings SettingsHTFadd387        = CandleSettings.new(htf="387", max_memory=3, htfint=387)
var Candle[] candlesadd387                  = array.new<Candle>(0)
var BOSdata bosdataadd387                   = BOSdata.new()
htfadd387.settings                 := SettingsHTFadd387
htfadd387.candles                  := candlesadd387
htfadd387.bosdata                  := bosdataadd387
var CandleSet htfadd388                     = CandleSet.new()
var CandleSettings SettingsHTFadd388        = CandleSettings.new(htf="388", max_memory=3, htfint=388)
var Candle[] candlesadd388                  = array.new<Candle>(0)
var BOSdata bosdataadd388                   = BOSdata.new()
htfadd388.settings                 := SettingsHTFadd388
htfadd388.candles                  := candlesadd388
htfadd388.bosdata                  := bosdataadd388
var CandleSet htfadd389                     = CandleSet.new()
var CandleSettings SettingsHTFadd389        = CandleSettings.new(htf="389", max_memory=3, htfint=389)
var Candle[] candlesadd389                  = array.new<Candle>(0)
var BOSdata bosdataadd389                   = BOSdata.new()
htfadd389.settings                 := SettingsHTFadd389
htfadd389.candles                  := candlesadd389
htfadd389.bosdata                  := bosdataadd389
var CandleSet htfadd390                     = CandleSet.new()
var CandleSettings SettingsHTFadd390        = CandleSettings.new(htf="390", max_memory=3, htfint=390)
var Candle[] candlesadd390                  = array.new<Candle>(0)
var BOSdata bosdataadd390                   = BOSdata.new()
htfadd390.settings                 := SettingsHTFadd390
htfadd390.candles                  := candlesadd390
htfadd390.bosdata                  := bosdataadd390
var CandleSet htfadd391                     = CandleSet.new()
var CandleSettings SettingsHTFadd391        = CandleSettings.new(htf="391", max_memory=3, htfint=391)
var Candle[] candlesadd391                  = array.new<Candle>(0)
var BOSdata bosdataadd391                   = BOSdata.new()
htfadd391.settings                 := SettingsHTFadd391
htfadd391.candles                  := candlesadd391
htfadd391.bosdata                  := bosdataadd391
var CandleSet htfadd392                     = CandleSet.new()
var CandleSettings SettingsHTFadd392        = CandleSettings.new(htf="392", max_memory=3, htfint=392)
var Candle[] candlesadd392                  = array.new<Candle>(0)
var BOSdata bosdataadd392                   = BOSdata.new()
htfadd392.settings                 := SettingsHTFadd392
htfadd392.candles                  := candlesadd392
htfadd392.bosdata                  := bosdataadd392
var CandleSet htfadd393                     = CandleSet.new()
var CandleSettings SettingsHTFadd393        = CandleSettings.new(htf="393", max_memory=3, htfint=393)
var Candle[] candlesadd393                  = array.new<Candle>(0)
var BOSdata bosdataadd393                   = BOSdata.new()
htfadd393.settings                 := SettingsHTFadd393
htfadd393.candles                  := candlesadd393
htfadd393.bosdata                  := bosdataadd393
var CandleSet htfadd394                     = CandleSet.new()
var CandleSettings SettingsHTFadd394        = CandleSettings.new(htf="394", max_memory=3, htfint=394)
var Candle[] candlesadd394                  = array.new<Candle>(0)
var BOSdata bosdataadd394                   = BOSdata.new()
htfadd394.settings                 := SettingsHTFadd394
htfadd394.candles                  := candlesadd394
htfadd394.bosdata                  := bosdataadd394
var CandleSet htfadd395                     = CandleSet.new()
var CandleSettings SettingsHTFadd395        = CandleSettings.new(htf="395", max_memory=3, htfint=395)
var Candle[] candlesadd395                  = array.new<Candle>(0)
var BOSdata bosdataadd395                   = BOSdata.new()
htfadd395.settings                 := SettingsHTFadd395
htfadd395.candles                  := candlesadd395
htfadd395.bosdata                  := bosdataadd395
var CandleSet htfadd396                     = CandleSet.new()
var CandleSettings SettingsHTFadd396        = CandleSettings.new(htf="396", max_memory=3, htfint=396)
var Candle[] candlesadd396                  = array.new<Candle>(0)
var BOSdata bosdataadd396                   = BOSdata.new()
htfadd396.settings                 := SettingsHTFadd396
htfadd396.candles                  := candlesadd396
htfadd396.bosdata                  := bosdataadd396
var CandleSet htfadd397                     = CandleSet.new()
var CandleSettings SettingsHTFadd397        = CandleSettings.new(htf="397", max_memory=3, htfint=397)
var Candle[] candlesadd397                  = array.new<Candle>(0)
var BOSdata bosdataadd397                   = BOSdata.new()
htfadd397.settings                 := SettingsHTFadd397
htfadd397.candles                  := candlesadd397
htfadd397.bosdata                  := bosdataadd397
var CandleSet htfadd398                     = CandleSet.new()
var CandleSettings SettingsHTFadd398        = CandleSettings.new(htf="398", max_memory=3, htfint=398)
var Candle[] candlesadd398                  = array.new<Candle>(0)
var BOSdata bosdataadd398                   = BOSdata.new()
htfadd398.settings                 := SettingsHTFadd398
htfadd398.candles                  := candlesadd398
htfadd398.bosdata                  := bosdataadd398
var CandleSet htfadd399                     = CandleSet.new()
var CandleSettings SettingsHTFadd399        = CandleSettings.new(htf="399", max_memory=3, htfint=399)
var Candle[] candlesadd399                  = array.new<Candle>(0)
var BOSdata bosdataadd399                   = BOSdata.new()
htfadd399.settings                 := SettingsHTFadd399
htfadd399.candles                  := candlesadd399
htfadd399.bosdata                  := bosdataadd399
var CandleSet htfadd400                     = CandleSet.new()
var CandleSettings SettingsHTFadd400        = CandleSettings.new(htf="400", max_memory=3, htfint=400)
var Candle[] candlesadd400                  = array.new<Candle>(0)
var BOSdata bosdataadd400                   = BOSdata.new()
htfadd400.settings                 := SettingsHTFadd400
htfadd400.candles                  := candlesadd400
htfadd400.bosdata                  := bosdataadd400
var CandleSet htfadd401                     = CandleSet.new()
var CandleSettings SettingsHTFadd401        = CandleSettings.new(htf="401", max_memory=3, htfint=401)
var Candle[] candlesadd401                  = array.new<Candle>(0)
var BOSdata bosdataadd401                   = BOSdata.new()
htfadd401.settings                 := SettingsHTFadd401
htfadd401.candles                  := candlesadd401
htfadd401.bosdata                  := bosdataadd401
var CandleSet htfadd402                     = CandleSet.new()
var CandleSettings SettingsHTFadd402        = CandleSettings.new(htf="402", max_memory=3, htfint=402)
var Candle[] candlesadd402                  = array.new<Candle>(0)
var BOSdata bosdataadd402                   = BOSdata.new()
htfadd402.settings                 := SettingsHTFadd402
htfadd402.candles                  := candlesadd402
htfadd402.bosdata                  := bosdataadd402
var CandleSet htfadd403                     = CandleSet.new()
var CandleSettings SettingsHTFadd403        = CandleSettings.new(htf="403", max_memory=3, htfint=403)
var Candle[] candlesadd403                  = array.new<Candle>(0)
var BOSdata bosdataadd403                   = BOSdata.new()
htfadd403.settings                 := SettingsHTFadd403
htfadd403.candles                  := candlesadd403
htfadd403.bosdata                  := bosdataadd403
var CandleSet htfadd404                     = CandleSet.new()
var CandleSettings SettingsHTFadd404        = CandleSettings.new(htf="404", max_memory=3, htfint=404)
var Candle[] candlesadd404                  = array.new<Candle>(0)
var BOSdata bosdataadd404                   = BOSdata.new()
htfadd404.settings                 := SettingsHTFadd404
htfadd404.candles                  := candlesadd404
htfadd404.bosdata                  := bosdataadd404
var CandleSet htfadd405                     = CandleSet.new()
var CandleSettings SettingsHTFadd405        = CandleSettings.new(htf="405", max_memory=3, htfint=405)
var Candle[] candlesadd405                  = array.new<Candle>(0)
var BOSdata bosdataadd405                   = BOSdata.new()
htfadd405.settings                 := SettingsHTFadd405
htfadd405.candles                  := candlesadd405
htfadd405.bosdata                  := bosdataadd405
var CandleSet htfadd406                     = CandleSet.new()
var CandleSettings SettingsHTFadd406        = CandleSettings.new(htf="406", max_memory=3, htfint=406)
var Candle[] candlesadd406                  = array.new<Candle>(0)
var BOSdata bosdataadd406                   = BOSdata.new()
htfadd406.settings                 := SettingsHTFadd406
htfadd406.candles                  := candlesadd406
htfadd406.bosdata                  := bosdataadd406
var CandleSet htfadd407                     = CandleSet.new()
var CandleSettings SettingsHTFadd407        = CandleSettings.new(htf="407", max_memory=3, htfint=407)
var Candle[] candlesadd407                  = array.new<Candle>(0)
var BOSdata bosdataadd407                   = BOSdata.new()
htfadd407.settings                 := SettingsHTFadd407
htfadd407.candles                  := candlesadd407
htfadd407.bosdata                  := bosdataadd407
var CandleSet htfadd408                     = CandleSet.new()
var CandleSettings SettingsHTFadd408        = CandleSettings.new(htf="408", max_memory=3, htfint=408)
var Candle[] candlesadd408                  = array.new<Candle>(0)
var BOSdata bosdataadd408                   = BOSdata.new()
htfadd408.settings                 := SettingsHTFadd408
htfadd408.candles                  := candlesadd408
htfadd408.bosdata                  := bosdataadd408
var CandleSet htfadd409                     = CandleSet.new()
var CandleSettings SettingsHTFadd409        = CandleSettings.new(htf="409", max_memory=3, htfint=409)
var Candle[] candlesadd409                  = array.new<Candle>(0)
var BOSdata bosdataadd409                   = BOSdata.new()
htfadd409.settings                 := SettingsHTFadd409
htfadd409.candles                  := candlesadd409
htfadd409.bosdata                  := bosdataadd409
var CandleSet htfadd410                     = CandleSet.new()
var CandleSettings SettingsHTFadd410        = CandleSettings.new(htf="410", max_memory=3, htfint=410)
var Candle[] candlesadd410                  = array.new<Candle>(0)
var BOSdata bosdataadd410                   = BOSdata.new()
htfadd410.settings                 := SettingsHTFadd410
htfadd410.candles                  := candlesadd410
htfadd410.bosdata                  := bosdataadd410
var CandleSet htfadd411                     = CandleSet.new()
var CandleSettings SettingsHTFadd411        = CandleSettings.new(htf="411", max_memory=3, htfint=411)
var Candle[] candlesadd411                  = array.new<Candle>(0)
var BOSdata bosdataadd411                   = BOSdata.new()
htfadd411.settings                 := SettingsHTFadd411
htfadd411.candles                  := candlesadd411
htfadd411.bosdata                  := bosdataadd411
var CandleSet htfadd412                     = CandleSet.new()
var CandleSettings SettingsHTFadd412        = CandleSettings.new(htf="412", max_memory=3, htfint=412)
var Candle[] candlesadd412                  = array.new<Candle>(0)
var BOSdata bosdataadd412                   = BOSdata.new()
htfadd412.settings                 := SettingsHTFadd412
htfadd412.candles                  := candlesadd412
htfadd412.bosdata                  := bosdataadd412
var CandleSet htfadd413                     = CandleSet.new()
var CandleSettings SettingsHTFadd413        = CandleSettings.new(htf="413", max_memory=3, htfint=413)
var Candle[] candlesadd413                  = array.new<Candle>(0)
var BOSdata bosdataadd413                   = BOSdata.new()
htfadd413.settings                 := SettingsHTFadd413
htfadd413.candles                  := candlesadd413
htfadd413.bosdata                  := bosdataadd413
var CandleSet htfadd414                     = CandleSet.new()
var CandleSettings SettingsHTFadd414        = CandleSettings.new(htf="414", max_memory=3, htfint=414)
var Candle[] candlesadd414                  = array.new<Candle>(0)
var BOSdata bosdataadd414                   = BOSdata.new()
htfadd414.settings                 := SettingsHTFadd414
htfadd414.candles                  := candlesadd414
htfadd414.bosdata                  := bosdataadd414
var CandleSet htfadd415                     = CandleSet.new()
var CandleSettings SettingsHTFadd415        = CandleSettings.new(htf="415", max_memory=3, htfint=415)
var Candle[] candlesadd415                  = array.new<Candle>(0)
var BOSdata bosdataadd415                   = BOSdata.new()
htfadd415.settings                 := SettingsHTFadd415
htfadd415.candles                  := candlesadd415
htfadd415.bosdata                  := bosdataadd415
var CandleSet htfadd416                     = CandleSet.new()
var CandleSettings SettingsHTFadd416        = CandleSettings.new(htf="416", max_memory=3, htfint=416)
var Candle[] candlesadd416                  = array.new<Candle>(0)
var BOSdata bosdataadd416                   = BOSdata.new()
htfadd416.settings                 := SettingsHTFadd416
htfadd416.candles                  := candlesadd416
htfadd416.bosdata                  := bosdataadd416
var CandleSet htfadd417                     = CandleSet.new()
var CandleSettings SettingsHTFadd417        = CandleSettings.new(htf="417", max_memory=3, htfint=417)
var Candle[] candlesadd417                  = array.new<Candle>(0)
var BOSdata bosdataadd417                   = BOSdata.new()
htfadd417.settings                 := SettingsHTFadd417
htfadd417.candles                  := candlesadd417
htfadd417.bosdata                  := bosdataadd417
var CandleSet htfadd418                     = CandleSet.new()
var CandleSettings SettingsHTFadd418        = CandleSettings.new(htf="418", max_memory=3, htfint=418)
var Candle[] candlesadd418                  = array.new<Candle>(0)
var BOSdata bosdataadd418                   = BOSdata.new()
htfadd418.settings                 := SettingsHTFadd418
htfadd418.candles                  := candlesadd418
htfadd418.bosdata                  := bosdataadd418
var CandleSet htfadd419                     = CandleSet.new()
var CandleSettings SettingsHTFadd419        = CandleSettings.new(htf="419", max_memory=3, htfint=419)
var Candle[] candlesadd419                  = array.new<Candle>(0)
var BOSdata bosdataadd419                   = BOSdata.new()
htfadd419.settings                 := SettingsHTFadd419
htfadd419.candles                  := candlesadd419
htfadd419.bosdata                  := bosdataadd419
var CandleSet htfadd420                     = CandleSet.new()
var CandleSettings SettingsHTFadd420        = CandleSettings.new(htf="420", max_memory=3, htfint=420)
var Candle[] candlesadd420                  = array.new<Candle>(0)
var BOSdata bosdataadd420                   = BOSdata.new()
htfadd420.settings                 := SettingsHTFadd420
htfadd420.candles                  := candlesadd420
htfadd420.bosdata                  := bosdataadd420
var CandleSet htfadd421                     = CandleSet.new()
var CandleSettings SettingsHTFadd421        = CandleSettings.new(htf="421", max_memory=3, htfint=421)
var Candle[] candlesadd421                  = array.new<Candle>(0)
var BOSdata bosdataadd421                   = BOSdata.new()
htfadd421.settings                 := SettingsHTFadd421
htfadd421.candles                  := candlesadd421
htfadd421.bosdata                  := bosdataadd421
var CandleSet htfadd422                     = CandleSet.new()
var CandleSettings SettingsHTFadd422        = CandleSettings.new(htf="422", max_memory=3, htfint=422)
var Candle[] candlesadd422                  = array.new<Candle>(0)
var BOSdata bosdataadd422                   = BOSdata.new()
htfadd422.settings                 := SettingsHTFadd422
htfadd422.candles                  := candlesadd422
htfadd422.bosdata                  := bosdataadd422
var CandleSet htfadd423                     = CandleSet.new()
var CandleSettings SettingsHTFadd423        = CandleSettings.new(htf="423", max_memory=3, htfint=423)
var Candle[] candlesadd423                  = array.new<Candle>(0)
var BOSdata bosdataadd423                   = BOSdata.new()
htfadd423.settings                 := SettingsHTFadd423
htfadd423.candles                  := candlesadd423
htfadd423.bosdata                  := bosdataadd423
var CandleSet htfadd424                     = CandleSet.new()
var CandleSettings SettingsHTFadd424        = CandleSettings.new(htf="424", max_memory=3, htfint=424)
var Candle[] candlesadd424                  = array.new<Candle>(0)
var BOSdata bosdataadd424                   = BOSdata.new()
htfadd424.settings                 := SettingsHTFadd424
htfadd424.candles                  := candlesadd424
htfadd424.bosdata                  := bosdataadd424
var CandleSet htfadd425                     = CandleSet.new()
var CandleSettings SettingsHTFadd425        = CandleSettings.new(htf="425", max_memory=3, htfint=425)
var Candle[] candlesadd425                  = array.new<Candle>(0)
var BOSdata bosdataadd425                   = BOSdata.new()
htfadd425.settings                 := SettingsHTFadd425
htfadd425.candles                  := candlesadd425
htfadd425.bosdata                  := bosdataadd425
var CandleSet htfadd426                     = CandleSet.new()
var CandleSettings SettingsHTFadd426        = CandleSettings.new(htf="426", max_memory=3, htfint=426)
var Candle[] candlesadd426                  = array.new<Candle>(0)
var BOSdata bosdataadd426                   = BOSdata.new()
htfadd426.settings                 := SettingsHTFadd426
htfadd426.candles                  := candlesadd426
htfadd426.bosdata                  := bosdataadd426
var CandleSet htfadd427                     = CandleSet.new()
var CandleSettings SettingsHTFadd427        = CandleSettings.new(htf="427", max_memory=3, htfint=427)
var Candle[] candlesadd427                  = array.new<Candle>(0)
var BOSdata bosdataadd427                   = BOSdata.new()
htfadd427.settings                 := SettingsHTFadd427
htfadd427.candles                  := candlesadd427
htfadd427.bosdata                  := bosdataadd427
var CandleSet htfadd428                     = CandleSet.new()
var CandleSettings SettingsHTFadd428        = CandleSettings.new(htf="428", max_memory=3, htfint=428)
var Candle[] candlesadd428                  = array.new<Candle>(0)
var BOSdata bosdataadd428                   = BOSdata.new()
htfadd428.settings                 := SettingsHTFadd428
htfadd428.candles                  := candlesadd428
htfadd428.bosdata                  := bosdataadd428
var CandleSet htfadd429                     = CandleSet.new()
var CandleSettings SettingsHTFadd429        = CandleSettings.new(htf="429", max_memory=3, htfint=429)
var Candle[] candlesadd429                  = array.new<Candle>(0)
var BOSdata bosdataadd429                   = BOSdata.new()
htfadd429.settings                 := SettingsHTFadd429
htfadd429.candles                  := candlesadd429
htfadd429.bosdata                  := bosdataadd429
var CandleSet htfadd430                     = CandleSet.new()
var CandleSettings SettingsHTFadd430        = CandleSettings.new(htf="430", max_memory=3, htfint=430)
var Candle[] candlesadd430                  = array.new<Candle>(0)
var BOSdata bosdataadd430                   = BOSdata.new()
htfadd430.settings                 := SettingsHTFadd430
htfadd430.candles                  := candlesadd430
htfadd430.bosdata                  := bosdataadd430
var CandleSet htfadd431                     = CandleSet.new()
var CandleSettings SettingsHTFadd431        = CandleSettings.new(htf="431", max_memory=3, htfint=431)
var Candle[] candlesadd431                  = array.new<Candle>(0)
var BOSdata bosdataadd431                   = BOSdata.new()
htfadd431.settings                 := SettingsHTFadd431
htfadd431.candles                  := candlesadd431
htfadd431.bosdata                  := bosdataadd431
var CandleSet htfadd432                     = CandleSet.new()
var CandleSettings SettingsHTFadd432        = CandleSettings.new(htf="432", max_memory=3, htfint=432)
var Candle[] candlesadd432                  = array.new<Candle>(0)
var BOSdata bosdataadd432                   = BOSdata.new()
htfadd432.settings                 := SettingsHTFadd432
htfadd432.candles                  := candlesadd432
htfadd432.bosdata                  := bosdataadd432
var CandleSet htfadd433                     = CandleSet.new()
var CandleSettings SettingsHTFadd433        = CandleSettings.new(htf="433", max_memory=3, htfint=433)
var Candle[] candlesadd433                  = array.new<Candle>(0)
var BOSdata bosdataadd433                   = BOSdata.new()
htfadd433.settings                 := SettingsHTFadd433
htfadd433.candles                  := candlesadd433
htfadd433.bosdata                  := bosdataadd433
var CandleSet htfadd434                     = CandleSet.new()
var CandleSettings SettingsHTFadd434        = CandleSettings.new(htf="434", max_memory=3, htfint=434)
var Candle[] candlesadd434                  = array.new<Candle>(0)
var BOSdata bosdataadd434                   = BOSdata.new()
htfadd434.settings                 := SettingsHTFadd434
htfadd434.candles                  := candlesadd434
htfadd434.bosdata                  := bosdataadd434
var CandleSet htfadd435                     = CandleSet.new()
var CandleSettings SettingsHTFadd435        = CandleSettings.new(htf="435", max_memory=3, htfint=435)
var Candle[] candlesadd435                  = array.new<Candle>(0)
var BOSdata bosdataadd435                   = BOSdata.new()
htfadd435.settings                 := SettingsHTFadd435
htfadd435.candles                  := candlesadd435
htfadd435.bosdata                  := bosdataadd435
var CandleSet htfadd436                     = CandleSet.new()
var CandleSettings SettingsHTFadd436        = CandleSettings.new(htf="436", max_memory=3, htfint=436)
var Candle[] candlesadd436                  = array.new<Candle>(0)
var BOSdata bosdataadd436                   = BOSdata.new()
htfadd436.settings                 := SettingsHTFadd436
htfadd436.candles                  := candlesadd436
htfadd436.bosdata                  := bosdataadd436
var CandleSet htfadd437                     = CandleSet.new()
var CandleSettings SettingsHTFadd437        = CandleSettings.new(htf="437", max_memory=3, htfint=437)
var Candle[] candlesadd437                  = array.new<Candle>(0)
var BOSdata bosdataadd437                   = BOSdata.new()
htfadd437.settings                 := SettingsHTFadd437
htfadd437.candles                  := candlesadd437
htfadd437.bosdata                  := bosdataadd437
var CandleSet htfadd438                     = CandleSet.new()
var CandleSettings SettingsHTFadd438        = CandleSettings.new(htf="438", max_memory=3, htfint=438)
var Candle[] candlesadd438                  = array.new<Candle>(0)
var BOSdata bosdataadd438                   = BOSdata.new()
htfadd438.settings                 := SettingsHTFadd438
htfadd438.candles                  := candlesadd438
htfadd438.bosdata                  := bosdataadd438
var CandleSet htfadd439                     = CandleSet.new()
var CandleSettings SettingsHTFadd439        = CandleSettings.new(htf="439", max_memory=3, htfint=439)
var Candle[] candlesadd439                  = array.new<Candle>(0)
var BOSdata bosdataadd439                   = BOSdata.new()
htfadd439.settings                 := SettingsHTFadd439
htfadd439.candles                  := candlesadd439
htfadd439.bosdata                  := bosdataadd439
var CandleSet htfadd440                     = CandleSet.new()
var CandleSettings SettingsHTFadd440        = CandleSettings.new(htf="440", max_memory=3, htfint=440)
var Candle[] candlesadd440                  = array.new<Candle>(0)
var BOSdata bosdataadd440                   = BOSdata.new()
htfadd440.settings                 := SettingsHTFadd440
htfadd440.candles                  := candlesadd440
htfadd440.bosdata                  := bosdataadd440
var CandleSet htfadd441                     = CandleSet.new()
var CandleSettings SettingsHTFadd441        = CandleSettings.new(htf="441", max_memory=3, htfint=441)
var Candle[] candlesadd441                  = array.new<Candle>(0)
var BOSdata bosdataadd441                   = BOSdata.new()
htfadd441.settings                 := SettingsHTFadd441
htfadd441.candles                  := candlesadd441
htfadd441.bosdata                  := bosdataadd441
var CandleSet htfadd442                     = CandleSet.new()
var CandleSettings SettingsHTFadd442        = CandleSettings.new(htf="442", max_memory=3, htfint=442)
var Candle[] candlesadd442                  = array.new<Candle>(0)
var BOSdata bosdataadd442                   = BOSdata.new()
htfadd442.settings                 := SettingsHTFadd442
htfadd442.candles                  := candlesadd442
htfadd442.bosdata                  := bosdataadd442
var CandleSet htfadd443                     = CandleSet.new()
var CandleSettings SettingsHTFadd443        = CandleSettings.new(htf="443", max_memory=3, htfint=443)
var Candle[] candlesadd443                  = array.new<Candle>(0)
var BOSdata bosdataadd443                   = BOSdata.new()
htfadd443.settings                 := SettingsHTFadd443
htfadd443.candles                  := candlesadd443
htfadd443.bosdata                  := bosdataadd443
var CandleSet htfadd444                     = CandleSet.new()
var CandleSettings SettingsHTFadd444        = CandleSettings.new(htf="444", max_memory=3, htfint=444)
var Candle[] candlesadd444                  = array.new<Candle>(0)
var BOSdata bosdataadd444                   = BOSdata.new()
htfadd444.settings                 := SettingsHTFadd444
htfadd444.candles                  := candlesadd444
htfadd444.bosdata                  := bosdataadd444
var CandleSet htfadd445                     = CandleSet.new()
var CandleSettings SettingsHTFadd445        = CandleSettings.new(htf="445", max_memory=3, htfint=445)
var Candle[] candlesadd445                  = array.new<Candle>(0)
var BOSdata bosdataadd445                   = BOSdata.new()
htfadd445.settings                 := SettingsHTFadd445
htfadd445.candles                  := candlesadd445
htfadd445.bosdata                  := bosdataadd445
var CandleSet htfadd446                     = CandleSet.new()
var CandleSettings SettingsHTFadd446        = CandleSettings.new(htf="446", max_memory=3, htfint=446)
var Candle[] candlesadd446                  = array.new<Candle>(0)
var BOSdata bosdataadd446                   = BOSdata.new()
htfadd446.settings                 := SettingsHTFadd446
htfadd446.candles                  := candlesadd446
htfadd446.bosdata                  := bosdataadd446
var CandleSet htfadd447                     = CandleSet.new()
var CandleSettings SettingsHTFadd447        = CandleSettings.new(htf="447", max_memory=3, htfint=447)
var Candle[] candlesadd447                  = array.new<Candle>(0)
var BOSdata bosdataadd447                   = BOSdata.new()
htfadd447.settings                 := SettingsHTFadd447
htfadd447.candles                  := candlesadd447
htfadd447.bosdata                  := bosdataadd447
var CandleSet htfadd448                     = CandleSet.new()
var CandleSettings SettingsHTFadd448        = CandleSettings.new(htf="448", max_memory=3, htfint=448)
var Candle[] candlesadd448                  = array.new<Candle>(0)
var BOSdata bosdataadd448                   = BOSdata.new()
htfadd448.settings                 := SettingsHTFadd448
htfadd448.candles                  := candlesadd448
htfadd448.bosdata                  := bosdataadd448
var CandleSet htfadd449                     = CandleSet.new()
var CandleSettings SettingsHTFadd449        = CandleSettings.new(htf="449", max_memory=3, htfint=449)
var Candle[] candlesadd449                  = array.new<Candle>(0)
var BOSdata bosdataadd449                   = BOSdata.new()
htfadd449.settings                 := SettingsHTFadd449
htfadd449.candles                  := candlesadd449
htfadd449.bosdata                  := bosdataadd449
var CandleSet htfadd450                     = CandleSet.new()
var CandleSettings SettingsHTFadd450        = CandleSettings.new(htf="450", max_memory=3, htfint=450)
var Candle[] candlesadd450                  = array.new<Candle>(0)
var BOSdata bosdataadd450                   = BOSdata.new()
htfadd450.settings                 := SettingsHTFadd450
htfadd450.candles                  := candlesadd450
htfadd450.bosdata                  := bosdataadd450
var CandleSet htfadd451                     = CandleSet.new()
var CandleSettings SettingsHTFadd451        = CandleSettings.new(htf="451", max_memory=3, htfint=451)
var Candle[] candlesadd451                  = array.new<Candle>(0)
var BOSdata bosdataadd451                   = BOSdata.new()
htfadd451.settings                 := SettingsHTFadd451
htfadd451.candles                  := candlesadd451
htfadd451.bosdata                  := bosdataadd451
var CandleSet htfadd452                     = CandleSet.new()
var CandleSettings SettingsHTFadd452        = CandleSettings.new(htf="452", max_memory=3, htfint=452)
var Candle[] candlesadd452                  = array.new<Candle>(0)
var BOSdata bosdataadd452                   = BOSdata.new()
htfadd452.settings                 := SettingsHTFadd452
htfadd452.candles                  := candlesadd452
htfadd452.bosdata                  := bosdataadd452
var CandleSet htfadd453                     = CandleSet.new()
var CandleSettings SettingsHTFadd453        = CandleSettings.new(htf="453", max_memory=3, htfint=453)
var Candle[] candlesadd453                  = array.new<Candle>(0)
var BOSdata bosdataadd453                   = BOSdata.new()
htfadd453.settings                 := SettingsHTFadd453
htfadd453.candles                  := candlesadd453
htfadd453.bosdata                  := bosdataadd453
var CandleSet htfadd454                     = CandleSet.new()
var CandleSettings SettingsHTFadd454        = CandleSettings.new(htf="454", max_memory=3, htfint=454)
var Candle[] candlesadd454                  = array.new<Candle>(0)
var BOSdata bosdataadd454                   = BOSdata.new()
htfadd454.settings                 := SettingsHTFadd454
htfadd454.candles                  := candlesadd454
htfadd454.bosdata                  := bosdataadd454
var CandleSet htfadd455                     = CandleSet.new()
var CandleSettings SettingsHTFadd455        = CandleSettings.new(htf="455", max_memory=3, htfint=455)
var Candle[] candlesadd455                  = array.new<Candle>(0)
var BOSdata bosdataadd455                   = BOSdata.new()
htfadd455.settings                 := SettingsHTFadd455
htfadd455.candles                  := candlesadd455
htfadd455.bosdata                  := bosdataadd455
var CandleSet htfadd456                     = CandleSet.new()
var CandleSettings SettingsHTFadd456        = CandleSettings.new(htf="456", max_memory=3, htfint=456)
var Candle[] candlesadd456                  = array.new<Candle>(0)
var BOSdata bosdataadd456                   = BOSdata.new()
htfadd456.settings                 := SettingsHTFadd456
htfadd456.candles                  := candlesadd456
htfadd456.bosdata                  := bosdataadd456
var CandleSet htfadd457                     = CandleSet.new()
var CandleSettings SettingsHTFadd457        = CandleSettings.new(htf="457", max_memory=3, htfint=457)
var Candle[] candlesadd457                  = array.new<Candle>(0)
var BOSdata bosdataadd457                   = BOSdata.new()
htfadd457.settings                 := SettingsHTFadd457
htfadd457.candles                  := candlesadd457
htfadd457.bosdata                  := bosdataadd457
var CandleSet htfadd458                     = CandleSet.new()
var CandleSettings SettingsHTFadd458        = CandleSettings.new(htf="458", max_memory=3, htfint=458)
var Candle[] candlesadd458                  = array.new<Candle>(0)
var BOSdata bosdataadd458                   = BOSdata.new()
htfadd458.settings                 := SettingsHTFadd458
htfadd458.candles                  := candlesadd458
htfadd458.bosdata                  := bosdataadd458
var CandleSet htfadd459                     = CandleSet.new()
var CandleSettings SettingsHTFadd459        = CandleSettings.new(htf="459", max_memory=3, htfint=459)
var Candle[] candlesadd459                  = array.new<Candle>(0)
var BOSdata bosdataadd459                   = BOSdata.new()
htfadd459.settings                 := SettingsHTFadd459
htfadd459.candles                  := candlesadd459
htfadd459.bosdata                  := bosdataadd459
var CandleSet htfadd460                     = CandleSet.new()
var CandleSettings SettingsHTFadd460        = CandleSettings.new(htf="460", max_memory=3, htfint=460)
var Candle[] candlesadd460                  = array.new<Candle>(0)
var BOSdata bosdataadd460                   = BOSdata.new()
htfadd460.settings                 := SettingsHTFadd460
htfadd460.candles                  := candlesadd460
htfadd460.bosdata                  := bosdataadd460
var CandleSet htfadd461                     = CandleSet.new()
var CandleSettings SettingsHTFadd461        = CandleSettings.new(htf="461", max_memory=3, htfint=461)
var Candle[] candlesadd461                  = array.new<Candle>(0)
var BOSdata bosdataadd461                   = BOSdata.new()
htfadd461.settings                 := SettingsHTFadd461
htfadd461.candles                  := candlesadd461
htfadd461.bosdata                  := bosdataadd461
var CandleSet htfadd462                     = CandleSet.new()
var CandleSettings SettingsHTFadd462        = CandleSettings.new(htf="462", max_memory=3, htfint=462)
var Candle[] candlesadd462                  = array.new<Candle>(0)
var BOSdata bosdataadd462                   = BOSdata.new()
htfadd462.settings                 := SettingsHTFadd462
htfadd462.candles                  := candlesadd462
htfadd462.bosdata                  := bosdataadd462
var CandleSet htfadd463                     = CandleSet.new()
var CandleSettings SettingsHTFadd463        = CandleSettings.new(htf="463", max_memory=3, htfint=463)
var Candle[] candlesadd463                  = array.new<Candle>(0)
var BOSdata bosdataadd463                   = BOSdata.new()
htfadd463.settings                 := SettingsHTFadd463
htfadd463.candles                  := candlesadd463
htfadd463.bosdata                  := bosdataadd463
var CandleSet htfadd464                     = CandleSet.new()
var CandleSettings SettingsHTFadd464        = CandleSettings.new(htf="464", max_memory=3, htfint=464)
var Candle[] candlesadd464                  = array.new<Candle>(0)
var BOSdata bosdataadd464                   = BOSdata.new()
htfadd464.settings                 := SettingsHTFadd464
htfadd464.candles                  := candlesadd464
htfadd464.bosdata                  := bosdataadd464
var CandleSet htfadd465                     = CandleSet.new()
var CandleSettings SettingsHTFadd465        = CandleSettings.new(htf="465", max_memory=3, htfint=465)
var Candle[] candlesadd465                  = array.new<Candle>(0)
var BOSdata bosdataadd465                   = BOSdata.new()
htfadd465.settings                 := SettingsHTFadd465
htfadd465.candles                  := candlesadd465
htfadd465.bosdata                  := bosdataadd465
var CandleSet htfadd466                     = CandleSet.new()
var CandleSettings SettingsHTFadd466        = CandleSettings.new(htf="466", max_memory=3, htfint=466)
var Candle[] candlesadd466                  = array.new<Candle>(0)
var BOSdata bosdataadd466                   = BOSdata.new()
htfadd466.settings                 := SettingsHTFadd466
htfadd466.candles                  := candlesadd466
htfadd466.bosdata                  := bosdataadd466
var CandleSet htfadd467                     = CandleSet.new()
var CandleSettings SettingsHTFadd467        = CandleSettings.new(htf="467", max_memory=3, htfint=467)
var Candle[] candlesadd467                  = array.new<Candle>(0)
var BOSdata bosdataadd467                   = BOSdata.new()
htfadd467.settings                 := SettingsHTFadd467
htfadd467.candles                  := candlesadd467
htfadd467.bosdata                  := bosdataadd467
var CandleSet htfadd468                     = CandleSet.new()
var CandleSettings SettingsHTFadd468        = CandleSettings.new(htf="468", max_memory=3, htfint=468)
var Candle[] candlesadd468                  = array.new<Candle>(0)
var BOSdata bosdataadd468                   = BOSdata.new()
htfadd468.settings                 := SettingsHTFadd468
htfadd468.candles                  := candlesadd468
htfadd468.bosdata                  := bosdataadd468
var CandleSet htfadd469                     = CandleSet.new()
var CandleSettings SettingsHTFadd469        = CandleSettings.new(htf="469", max_memory=3, htfint=469)
var Candle[] candlesadd469                  = array.new<Candle>(0)
var BOSdata bosdataadd469                   = BOSdata.new()
htfadd469.settings                 := SettingsHTFadd469
htfadd469.candles                  := candlesadd469
htfadd469.bosdata                  := bosdataadd469
var CandleSet htfadd470                     = CandleSet.new()
var CandleSettings SettingsHTFadd470        = CandleSettings.new(htf="470", max_memory=3, htfint=470)
var Candle[] candlesadd470                  = array.new<Candle>(0)
var BOSdata bosdataadd470                   = BOSdata.new()
htfadd470.settings                 := SettingsHTFadd470
htfadd470.candles                  := candlesadd470
htfadd470.bosdata                  := bosdataadd470
var CandleSet htfadd471                     = CandleSet.new()
var CandleSettings SettingsHTFadd471        = CandleSettings.new(htf="471", max_memory=3, htfint=471)
var Candle[] candlesadd471                  = array.new<Candle>(0)
var BOSdata bosdataadd471                   = BOSdata.new()
htfadd471.settings                 := SettingsHTFadd471
htfadd471.candles                  := candlesadd471
htfadd471.bosdata                  := bosdataadd471
var CandleSet htfadd472                     = CandleSet.new()
var CandleSettings SettingsHTFadd472        = CandleSettings.new(htf="472", max_memory=3, htfint=472)
var Candle[] candlesadd472                  = array.new<Candle>(0)
var BOSdata bosdataadd472                   = BOSdata.new()
htfadd472.settings                 := SettingsHTFadd472
htfadd472.candles                  := candlesadd472
htfadd472.bosdata                  := bosdataadd472
var CandleSet htfadd473                     = CandleSet.new()
var CandleSettings SettingsHTFadd473        = CandleSettings.new(htf="473", max_memory=3, htfint=473)
var Candle[] candlesadd473                  = array.new<Candle>(0)
var BOSdata bosdataadd473                   = BOSdata.new()
htfadd473.settings                 := SettingsHTFadd473
htfadd473.candles                  := candlesadd473
htfadd473.bosdata                  := bosdataadd473
var CandleSet htfadd474                     = CandleSet.new()
var CandleSettings SettingsHTFadd474        = CandleSettings.new(htf="474", max_memory=3, htfint=474)
var Candle[] candlesadd474                  = array.new<Candle>(0)
var BOSdata bosdataadd474                   = BOSdata.new()
htfadd474.settings                 := SettingsHTFadd474
htfadd474.candles                  := candlesadd474
htfadd474.bosdata                  := bosdataadd474
var CandleSet htfadd475                     = CandleSet.new()
var CandleSettings SettingsHTFadd475        = CandleSettings.new(htf="475", max_memory=3, htfint=475)
var Candle[] candlesadd475                  = array.new<Candle>(0)
var BOSdata bosdataadd475                   = BOSdata.new()
htfadd475.settings                 := SettingsHTFadd475
htfadd475.candles                  := candlesadd475
htfadd475.bosdata                  := bosdataadd475
var CandleSet htfadd476                     = CandleSet.new()
var CandleSettings SettingsHTFadd476        = CandleSettings.new(htf="476", max_memory=3, htfint=476)
var Candle[] candlesadd476                  = array.new<Candle>(0)
var BOSdata bosdataadd476                   = BOSdata.new()
htfadd476.settings                 := SettingsHTFadd476
htfadd476.candles                  := candlesadd476
htfadd476.bosdata                  := bosdataadd476
var CandleSet htfadd477                     = CandleSet.new()
var CandleSettings SettingsHTFadd477        = CandleSettings.new(htf="477", max_memory=3, htfint=477)
var Candle[] candlesadd477                  = array.new<Candle>(0)
var BOSdata bosdataadd477                   = BOSdata.new()
htfadd477.settings                 := SettingsHTFadd477
htfadd477.candles                  := candlesadd477
htfadd477.bosdata                  := bosdataadd477
var CandleSet htfadd478                     = CandleSet.new()
var CandleSettings SettingsHTFadd478        = CandleSettings.new(htf="478", max_memory=3, htfint=478)
var Candle[] candlesadd478                  = array.new<Candle>(0)
var BOSdata bosdataadd478                   = BOSdata.new()
htfadd478.settings                 := SettingsHTFadd478
htfadd478.candles                  := candlesadd478
htfadd478.bosdata                  := bosdataadd478
var CandleSet htfadd479                     = CandleSet.new()
var CandleSettings SettingsHTFadd479        = CandleSettings.new(htf="479", max_memory=3, htfint=479)
var Candle[] candlesadd479                  = array.new<Candle>(0)
var BOSdata bosdataadd479                   = BOSdata.new()
htfadd479.settings                 := SettingsHTFadd479
htfadd479.candles                  := candlesadd479
htfadd479.bosdata                  := bosdataadd479
var CandleSet htfadd480                     = CandleSet.new()
var CandleSettings SettingsHTFadd480        = CandleSettings.new(htf="480", max_memory=3, htfint=480)
var Candle[] candlesadd480                  = array.new<Candle>(0)
var BOSdata bosdataadd480                   = BOSdata.new()
htfadd480.settings                 := SettingsHTFadd480
htfadd480.candles                  := candlesadd480
htfadd480.bosdata                  := bosdataadd480
var CandleSet htfadd481                     = CandleSet.new()
var CandleSettings SettingsHTFadd481        = CandleSettings.new(htf="481", max_memory=3, htfint=481)
var Candle[] candlesadd481                  = array.new<Candle>(0)
var BOSdata bosdataadd481                   = BOSdata.new()
htfadd481.settings                 := SettingsHTFadd481
htfadd481.candles                  := candlesadd481
htfadd481.bosdata                  := bosdataadd481
var CandleSet htfadd482                     = CandleSet.new()
var CandleSettings SettingsHTFadd482        = CandleSettings.new(htf="482", max_memory=3, htfint=482)
var Candle[] candlesadd482                  = array.new<Candle>(0)
var BOSdata bosdataadd482                   = BOSdata.new()
htfadd482.settings                 := SettingsHTFadd482
htfadd482.candles                  := candlesadd482
htfadd482.bosdata                  := bosdataadd482
var CandleSet htfadd483                     = CandleSet.new()
var CandleSettings SettingsHTFadd483        = CandleSettings.new(htf="483", max_memory=3, htfint=483)
var Candle[] candlesadd483                  = array.new<Candle>(0)
var BOSdata bosdataadd483                   = BOSdata.new()
htfadd483.settings                 := SettingsHTFadd483
htfadd483.candles                  := candlesadd483
htfadd483.bosdata                  := bosdataadd483
var CandleSet htfadd484                     = CandleSet.new()
var CandleSettings SettingsHTFadd484        = CandleSettings.new(htf="484", max_memory=3, htfint=484)
var Candle[] candlesadd484                  = array.new<Candle>(0)
var BOSdata bosdataadd484                   = BOSdata.new()
htfadd484.settings                 := SettingsHTFadd484
htfadd484.candles                  := candlesadd484
htfadd484.bosdata                  := bosdataadd484
var CandleSet htfadd485                     = CandleSet.new()
var CandleSettings SettingsHTFadd485        = CandleSettings.new(htf="485", max_memory=3, htfint=485)
var Candle[] candlesadd485                  = array.new<Candle>(0)
var BOSdata bosdataadd485                   = BOSdata.new()
htfadd485.settings                 := SettingsHTFadd485
htfadd485.candles                  := candlesadd485
htfadd485.bosdata                  := bosdataadd485
var CandleSet htfadd486                     = CandleSet.new()
var CandleSettings SettingsHTFadd486        = CandleSettings.new(htf="486", max_memory=3, htfint=486)
var Candle[] candlesadd486                  = array.new<Candle>(0)
var BOSdata bosdataadd486                   = BOSdata.new()
htfadd486.settings                 := SettingsHTFadd486
htfadd486.candles                  := candlesadd486
htfadd486.bosdata                  := bosdataadd486
var CandleSet htfadd487                     = CandleSet.new()
var CandleSettings SettingsHTFadd487        = CandleSettings.new(htf="487", max_memory=3, htfint=487)
var Candle[] candlesadd487                  = array.new<Candle>(0)
var BOSdata bosdataadd487                   = BOSdata.new()
htfadd487.settings                 := SettingsHTFadd487
htfadd487.candles                  := candlesadd487
htfadd487.bosdata                  := bosdataadd487
var CandleSet htfadd488                     = CandleSet.new()
var CandleSettings SettingsHTFadd488        = CandleSettings.new(htf="488", max_memory=3, htfint=488)
var Candle[] candlesadd488                  = array.new<Candle>(0)
var BOSdata bosdataadd488                   = BOSdata.new()
htfadd488.settings                 := SettingsHTFadd488
htfadd488.candles                  := candlesadd488
htfadd488.bosdata                  := bosdataadd488
var CandleSet htfadd489                     = CandleSet.new()
var CandleSettings SettingsHTFadd489        = CandleSettings.new(htf="489", max_memory=3, htfint=489)
var Candle[] candlesadd489                  = array.new<Candle>(0)
var BOSdata bosdataadd489                   = BOSdata.new()
htfadd489.settings                 := SettingsHTFadd489
htfadd489.candles                  := candlesadd489
htfadd489.bosdata                  := bosdataadd489
var CandleSet htfadd490                     = CandleSet.new()
var CandleSettings SettingsHTFadd490        = CandleSettings.new(htf="490", max_memory=3, htfint=490)
var Candle[] candlesadd490                  = array.new<Candle>(0)
var BOSdata bosdataadd490                   = BOSdata.new()
htfadd490.settings                 := SettingsHTFadd490
htfadd490.candles                  := candlesadd490
htfadd490.bosdata                  := bosdataadd490
var CandleSet htfadd491                     = CandleSet.new()
var CandleSettings SettingsHTFadd491        = CandleSettings.new(htf="491", max_memory=3, htfint=491)
var Candle[] candlesadd491                  = array.new<Candle>(0)
var BOSdata bosdataadd491                   = BOSdata.new()
htfadd491.settings                 := SettingsHTFadd491
htfadd491.candles                  := candlesadd491
htfadd491.bosdata                  := bosdataadd491
var CandleSet htfadd492                     = CandleSet.new()
var CandleSettings SettingsHTFadd492        = CandleSettings.new(htf="492", max_memory=3, htfint=492)
var Candle[] candlesadd492                  = array.new<Candle>(0)
var BOSdata bosdataadd492                   = BOSdata.new()
htfadd492.settings                 := SettingsHTFadd492
htfadd492.candles                  := candlesadd492
htfadd492.bosdata                  := bosdataadd492
var CandleSet htfadd493                     = CandleSet.new()
var CandleSettings SettingsHTFadd493        = CandleSettings.new(htf="493", max_memory=3, htfint=493)
var Candle[] candlesadd493                  = array.new<Candle>(0)
var BOSdata bosdataadd493                   = BOSdata.new()
htfadd493.settings                 := SettingsHTFadd493
htfadd493.candles                  := candlesadd493
htfadd493.bosdata                  := bosdataadd493
var CandleSet htfadd494                     = CandleSet.new()
var CandleSettings SettingsHTFadd494        = CandleSettings.new(htf="494", max_memory=3, htfint=494)
var Candle[] candlesadd494                  = array.new<Candle>(0)
var BOSdata bosdataadd494                   = BOSdata.new()
htfadd494.settings                 := SettingsHTFadd494
htfadd494.candles                  := candlesadd494
htfadd494.bosdata                  := bosdataadd494
var CandleSet htfadd495                     = CandleSet.new()
var CandleSettings SettingsHTFadd495        = CandleSettings.new(htf="495", max_memory=3, htfint=495)
var Candle[] candlesadd495                  = array.new<Candle>(0)
var BOSdata bosdataadd495                   = BOSdata.new()
htfadd495.settings                 := SettingsHTFadd495
htfadd495.candles                  := candlesadd495
htfadd495.bosdata                  := bosdataadd495
var CandleSet htfadd496                     = CandleSet.new()
var CandleSettings SettingsHTFadd496        = CandleSettings.new(htf="496", max_memory=3, htfint=496)
var Candle[] candlesadd496                  = array.new<Candle>(0)
var BOSdata bosdataadd496                   = BOSdata.new()
htfadd496.settings                 := SettingsHTFadd496
htfadd496.candles                  := candlesadd496
htfadd496.bosdata                  := bosdataadd496
var CandleSet htfadd497                     = CandleSet.new()
var CandleSettings SettingsHTFadd497        = CandleSettings.new(htf="497", max_memory=3, htfint=497)
var Candle[] candlesadd497                  = array.new<Candle>(0)
var BOSdata bosdataadd497                   = BOSdata.new()
htfadd497.settings                 := SettingsHTFadd497
htfadd497.candles                  := candlesadd497
htfadd497.bosdata                  := bosdataadd497
var CandleSet htfadd498                     = CandleSet.new()
var CandleSettings SettingsHTFadd498        = CandleSettings.new(htf="498", max_memory=3, htfint=498)
var Candle[] candlesadd498                  = array.new<Candle>(0)
var BOSdata bosdataadd498                   = BOSdata.new()
htfadd498.settings                 := SettingsHTFadd498
htfadd498.candles                  := candlesadd498
htfadd498.bosdata                  := bosdataadd498
var CandleSet htfadd499                     = CandleSet.new()
var CandleSettings SettingsHTFadd499        = CandleSettings.new(htf="499", max_memory=3, htfint=499)
var Candle[] candlesadd499                  = array.new<Candle>(0)
var BOSdata bosdataadd499                   = BOSdata.new()
htfadd499.settings                 := SettingsHTFadd499
htfadd499.candles                  := candlesadd499
htfadd499.bosdata                  := bosdataadd499
var CandleSet htfadd500                     = CandleSet.new()
var CandleSettings SettingsHTFadd500        = CandleSettings.new(htf="500", max_memory=3, htfint=500)
var Candle[] candlesadd500                  = array.new<Candle>(0)
var BOSdata bosdataadd500                   = BOSdata.new()
htfadd500.settings                 := SettingsHTFadd500
htfadd500.candles                  := candlesadd500
htfadd500.bosdata                  := bosdataadd500
var CandleSet htfadd501                     = CandleSet.new()
var CandleSettings SettingsHTFadd501        = CandleSettings.new(htf="501", max_memory=3, htfint=501)
var Candle[] candlesadd501                  = array.new<Candle>(0)
var BOSdata bosdataadd501                   = BOSdata.new()
htfadd501.settings                 := SettingsHTFadd501
htfadd501.candles                  := candlesadd501
htfadd501.bosdata                  := bosdataadd501
var CandleSet htfadd502                     = CandleSet.new()
var CandleSettings SettingsHTFadd502        = CandleSettings.new(htf="502", max_memory=3, htfint=502)
var Candle[] candlesadd502                  = array.new<Candle>(0)
var BOSdata bosdataadd502                   = BOSdata.new()
htfadd502.settings                 := SettingsHTFadd502
htfadd502.candles                  := candlesadd502
htfadd502.bosdata                  := bosdataadd502
var CandleSet htfadd503                     = CandleSet.new()
var CandleSettings SettingsHTFadd503        = CandleSettings.new(htf="503", max_memory=3, htfint=503)
var Candle[] candlesadd503                  = array.new<Candle>(0)
var BOSdata bosdataadd503                   = BOSdata.new()
htfadd503.settings                 := SettingsHTFadd503
htfadd503.candles                  := candlesadd503
htfadd503.bosdata                  := bosdataadd503
var CandleSet htfadd504                     = CandleSet.new()
var CandleSettings SettingsHTFadd504        = CandleSettings.new(htf="504", max_memory=3, htfint=504)
var Candle[] candlesadd504                  = array.new<Candle>(0)
var BOSdata bosdataadd504                   = BOSdata.new()
htfadd504.settings                 := SettingsHTFadd504
htfadd504.candles                  := candlesadd504
htfadd504.bosdata                  := bosdataadd504
var CandleSet htfadd505                     = CandleSet.new()
var CandleSettings SettingsHTFadd505        = CandleSettings.new(htf="505", max_memory=3, htfint=505)
var Candle[] candlesadd505                  = array.new<Candle>(0)
var BOSdata bosdataadd505                   = BOSdata.new()
htfadd505.settings                 := SettingsHTFadd505
htfadd505.candles                  := candlesadd505
htfadd505.bosdata                  := bosdataadd505
var CandleSet htfadd506                     = CandleSet.new()
var CandleSettings SettingsHTFadd506        = CandleSettings.new(htf="506", max_memory=3, htfint=506)
var Candle[] candlesadd506                  = array.new<Candle>(0)
var BOSdata bosdataadd506                   = BOSdata.new()
htfadd506.settings                 := SettingsHTFadd506
htfadd506.candles                  := candlesadd506
htfadd506.bosdata                  := bosdataadd506
var CandleSet htfadd507                     = CandleSet.new()
var CandleSettings SettingsHTFadd507        = CandleSettings.new(htf="507", max_memory=3, htfint=507)
var Candle[] candlesadd507                  = array.new<Candle>(0)
var BOSdata bosdataadd507                   = BOSdata.new()
htfadd507.settings                 := SettingsHTFadd507
htfadd507.candles                  := candlesadd507
htfadd507.bosdata                  := bosdataadd507
var CandleSet htfadd508                     = CandleSet.new()
var CandleSettings SettingsHTFadd508        = CandleSettings.new(htf="508", max_memory=3, htfint=508)
var Candle[] candlesadd508                  = array.new<Candle>(0)
var BOSdata bosdataadd508                   = BOSdata.new()
htfadd508.settings                 := SettingsHTFadd508
htfadd508.candles                  := candlesadd508
htfadd508.bosdata                  := bosdataadd508
var CandleSet htfadd509                     = CandleSet.new()
var CandleSettings SettingsHTFadd509        = CandleSettings.new(htf="509", max_memory=3, htfint=509)
var Candle[] candlesadd509                  = array.new<Candle>(0)
var BOSdata bosdataadd509                   = BOSdata.new()
htfadd509.settings                 := SettingsHTFadd509
htfadd509.candles                  := candlesadd509
htfadd509.bosdata                  := bosdataadd509
var CandleSet htfadd510                     = CandleSet.new()
var CandleSettings SettingsHTFadd510        = CandleSettings.new(htf="510", max_memory=3, htfint=510)
var Candle[] candlesadd510                  = array.new<Candle>(0)
var BOSdata bosdataadd510                   = BOSdata.new()
htfadd510.settings                 := SettingsHTFadd510
htfadd510.candles                  := candlesadd510
htfadd510.bosdata                  := bosdataadd510
var CandleSet htfadd511                     = CandleSet.new()
var CandleSettings SettingsHTFadd511        = CandleSettings.new(htf="511", max_memory=3, htfint=511)
var Candle[] candlesadd511                  = array.new<Candle>(0)
var BOSdata bosdataadd511                   = BOSdata.new()
htfadd511.settings                 := SettingsHTFadd511
htfadd511.candles                  := candlesadd511
htfadd511.bosdata                  := bosdataadd511
var CandleSet htfadd512                     = CandleSet.new()
var CandleSettings SettingsHTFadd512        = CandleSettings.new(htf="512", max_memory=3, htfint=512)
var Candle[] candlesadd512                  = array.new<Candle>(0)
var BOSdata bosdataadd512                   = BOSdata.new()
htfadd512.settings                 := SettingsHTFadd512
htfadd512.candles                  := candlesadd512
htfadd512.bosdata                  := bosdataadd512
var CandleSet htfadd513                     = CandleSet.new()
var CandleSettings SettingsHTFadd513        = CandleSettings.new(htf="513", max_memory=3, htfint=513)
var Candle[] candlesadd513                  = array.new<Candle>(0)
var BOSdata bosdataadd513                   = BOSdata.new()
htfadd513.settings                 := SettingsHTFadd513
htfadd513.candles                  := candlesadd513
htfadd513.bosdata                  := bosdataadd513
var CandleSet htfadd514                     = CandleSet.new()
var CandleSettings SettingsHTFadd514        = CandleSettings.new(htf="514", max_memory=3, htfint=514)
var Candle[] candlesadd514                  = array.new<Candle>(0)
var BOSdata bosdataadd514                   = BOSdata.new()
htfadd514.settings                 := SettingsHTFadd514
htfadd514.candles                  := candlesadd514
htfadd514.bosdata                  := bosdataadd514
var CandleSet htfadd515                     = CandleSet.new()
var CandleSettings SettingsHTFadd515        = CandleSettings.new(htf="515", max_memory=3, htfint=515)
var Candle[] candlesadd515                  = array.new<Candle>(0)
var BOSdata bosdataadd515                   = BOSdata.new()
htfadd515.settings                 := SettingsHTFadd515
htfadd515.candles                  := candlesadd515
htfadd515.bosdata                  := bosdataadd515
var CandleSet htfadd516                     = CandleSet.new()
var CandleSettings SettingsHTFadd516        = CandleSettings.new(htf="516", max_memory=3, htfint=516)
var Candle[] candlesadd516                  = array.new<Candle>(0)
var BOSdata bosdataadd516                   = BOSdata.new()
htfadd516.settings                 := SettingsHTFadd516
htfadd516.candles                  := candlesadd516
htfadd516.bosdata                  := bosdataadd516
var CandleSet htfadd517                     = CandleSet.new()
var CandleSettings SettingsHTFadd517        = CandleSettings.new(htf="517", max_memory=3, htfint=517)
var Candle[] candlesadd517                  = array.new<Candle>(0)
var BOSdata bosdataadd517                   = BOSdata.new()
htfadd517.settings                 := SettingsHTFadd517
htfadd517.candles                  := candlesadd517
htfadd517.bosdata                  := bosdataadd517
var CandleSet htfadd518                     = CandleSet.new()
var CandleSettings SettingsHTFadd518        = CandleSettings.new(htf="518", max_memory=3, htfint=518)
var Candle[] candlesadd518                  = array.new<Candle>(0)
var BOSdata bosdataadd518                   = BOSdata.new()
htfadd518.settings                 := SettingsHTFadd518
htfadd518.candles                  := candlesadd518
htfadd518.bosdata                  := bosdataadd518
var CandleSet htfadd519                     = CandleSet.new()
var CandleSettings SettingsHTFadd519        = CandleSettings.new(htf="519", max_memory=3, htfint=519)
var Candle[] candlesadd519                  = array.new<Candle>(0)
var BOSdata bosdataadd519                   = BOSdata.new()
htfadd519.settings                 := SettingsHTFadd519
htfadd519.candles                  := candlesadd519
htfadd519.bosdata                  := bosdataadd519
var CandleSet htfadd520                     = CandleSet.new()
var CandleSettings SettingsHTFadd520        = CandleSettings.new(htf="520", max_memory=3, htfint=520)
var Candle[] candlesadd520                  = array.new<Candle>(0)
var BOSdata bosdataadd520                   = BOSdata.new()
htfadd520.settings                 := SettingsHTFadd520
htfadd520.candles                  := candlesadd520
htfadd520.bosdata                  := bosdataadd520
var CandleSet htfadd521                     = CandleSet.new()
var CandleSettings SettingsHTFadd521        = CandleSettings.new(htf="521", max_memory=3, htfint=521)
var Candle[] candlesadd521                  = array.new<Candle>(0)
var BOSdata bosdataadd521                   = BOSdata.new()
htfadd521.settings                 := SettingsHTFadd521
htfadd521.candles                  := candlesadd521
htfadd521.bosdata                  := bosdataadd521
var CandleSet htfadd522                     = CandleSet.new()
var CandleSettings SettingsHTFadd522        = CandleSettings.new(htf="522", max_memory=3, htfint=522)
var Candle[] candlesadd522                  = array.new<Candle>(0)
var BOSdata bosdataadd522                   = BOSdata.new()
htfadd522.settings                 := SettingsHTFadd522
htfadd522.candles                  := candlesadd522
htfadd522.bosdata                  := bosdataadd522
var CandleSet htfadd523                     = CandleSet.new()
var CandleSettings SettingsHTFadd523        = CandleSettings.new(htf="523", max_memory=3, htfint=523)
var Candle[] candlesadd523                  = array.new<Candle>(0)
var BOSdata bosdataadd523                   = BOSdata.new()
htfadd523.settings                 := SettingsHTFadd523
htfadd523.candles                  := candlesadd523
htfadd523.bosdata                  := bosdataadd523
var CandleSet htfadd524                     = CandleSet.new()
var CandleSettings SettingsHTFadd524        = CandleSettings.new(htf="524", max_memory=3, htfint=524)
var Candle[] candlesadd524                  = array.new<Candle>(0)
var BOSdata bosdataadd524                   = BOSdata.new()
htfadd524.settings                 := SettingsHTFadd524
htfadd524.candles                  := candlesadd524
htfadd524.bosdata                  := bosdataadd524
var CandleSet htfadd525                     = CandleSet.new()
var CandleSettings SettingsHTFadd525        = CandleSettings.new(htf="525", max_memory=3, htfint=525)
var Candle[] candlesadd525                  = array.new<Candle>(0)
var BOSdata bosdataadd525                   = BOSdata.new()
htfadd525.settings                 := SettingsHTFadd525
htfadd525.candles                  := candlesadd525
htfadd525.bosdata                  := bosdataadd525
var CandleSet htfadd526                     = CandleSet.new()
var CandleSettings SettingsHTFadd526        = CandleSettings.new(htf="526", max_memory=3, htfint=526)
var Candle[] candlesadd526                  = array.new<Candle>(0)
var BOSdata bosdataadd526                   = BOSdata.new()
htfadd526.settings                 := SettingsHTFadd526
htfadd526.candles                  := candlesadd526
htfadd526.bosdata                  := bosdataadd526
var CandleSet htfadd527                     = CandleSet.new()
var CandleSettings SettingsHTFadd527        = CandleSettings.new(htf="527", max_memory=3, htfint=527)
var Candle[] candlesadd527                  = array.new<Candle>(0)
var BOSdata bosdataadd527                   = BOSdata.new()
htfadd527.settings                 := SettingsHTFadd527
htfadd527.candles                  := candlesadd527
htfadd527.bosdata                  := bosdataadd527
var CandleSet htfadd528                     = CandleSet.new()
var CandleSettings SettingsHTFadd528        = CandleSettings.new(htf="528", max_memory=3, htfint=528)
var Candle[] candlesadd528                  = array.new<Candle>(0)
var BOSdata bosdataadd528                   = BOSdata.new()
htfadd528.settings                 := SettingsHTFadd528
htfadd528.candles                  := candlesadd528
htfadd528.bosdata                  := bosdataadd528
var CandleSet htfadd529                     = CandleSet.new()
var CandleSettings SettingsHTFadd529        = CandleSettings.new(htf="529", max_memory=3, htfint=529)
var Candle[] candlesadd529                  = array.new<Candle>(0)
var BOSdata bosdataadd529                   = BOSdata.new()
htfadd529.settings                 := SettingsHTFadd529
htfadd529.candles                  := candlesadd529
htfadd529.bosdata                  := bosdataadd529
var CandleSet htfadd530                     = CandleSet.new()
var CandleSettings SettingsHTFadd530        = CandleSettings.new(htf="530", max_memory=3, htfint=530)
var Candle[] candlesadd530                  = array.new<Candle>(0)
var BOSdata bosdataadd530                   = BOSdata.new()
htfadd530.settings                 := SettingsHTFadd530
htfadd530.candles                  := candlesadd530
htfadd530.bosdata                  := bosdataadd530
var CandleSet htfadd531                     = CandleSet.new()
var CandleSettings SettingsHTFadd531        = CandleSettings.new(htf="531", max_memory=3, htfint=531)
var Candle[] candlesadd531                  = array.new<Candle>(0)
var BOSdata bosdataadd531                   = BOSdata.new()
htfadd531.settings                 := SettingsHTFadd531
htfadd531.candles                  := candlesadd531
htfadd531.bosdata                  := bosdataadd531
var CandleSet htfadd532                     = CandleSet.new()
var CandleSettings SettingsHTFadd532        = CandleSettings.new(htf="532", max_memory=3, htfint=532)
var Candle[] candlesadd532                  = array.new<Candle>(0)
var BOSdata bosdataadd532                   = BOSdata.new()
htfadd532.settings                 := SettingsHTFadd532
htfadd532.candles                  := candlesadd532
htfadd532.bosdata                  := bosdataadd532
var CandleSet htfadd533                     = CandleSet.new()
var CandleSettings SettingsHTFadd533        = CandleSettings.new(htf="533", max_memory=3, htfint=533)
var Candle[] candlesadd533                  = array.new<Candle>(0)
var BOSdata bosdataadd533                   = BOSdata.new()
htfadd533.settings                 := SettingsHTFadd533
htfadd533.candles                  := candlesadd533
htfadd533.bosdata                  := bosdataadd533
var CandleSet htfadd534                     = CandleSet.new()
var CandleSettings SettingsHTFadd534        = CandleSettings.new(htf="534", max_memory=3, htfint=534)
var Candle[] candlesadd534                  = array.new<Candle>(0)
var BOSdata bosdataadd534                   = BOSdata.new()
htfadd534.settings                 := SettingsHTFadd534
htfadd534.candles                  := candlesadd534
htfadd534.bosdata                  := bosdataadd534
var CandleSet htfadd535                     = CandleSet.new()
var CandleSettings SettingsHTFadd535        = CandleSettings.new(htf="535", max_memory=3, htfint=535)
var Candle[] candlesadd535                  = array.new<Candle>(0)
var BOSdata bosdataadd535                   = BOSdata.new()
htfadd535.settings                 := SettingsHTFadd535
htfadd535.candles                  := candlesadd535
htfadd535.bosdata                  := bosdataadd535
var CandleSet htfadd536                     = CandleSet.new()
var CandleSettings SettingsHTFadd536        = CandleSettings.new(htf="536", max_memory=3, htfint=536)
var Candle[] candlesadd536                  = array.new<Candle>(0)
var BOSdata bosdataadd536                   = BOSdata.new()
htfadd536.settings                 := SettingsHTFadd536
htfadd536.candles                  := candlesadd536
htfadd536.bosdata                  := bosdataadd536
var CandleSet htfadd537                     = CandleSet.new()
var CandleSettings SettingsHTFadd537        = CandleSettings.new(htf="537", max_memory=3, htfint=537)
var Candle[] candlesadd537                  = array.new<Candle>(0)
var BOSdata bosdataadd537                   = BOSdata.new()
htfadd537.settings                 := SettingsHTFadd537
htfadd537.candles                  := candlesadd537
htfadd537.bosdata                  := bosdataadd537
var CandleSet htfadd538                     = CandleSet.new()
var CandleSettings SettingsHTFadd538        = CandleSettings.new(htf="538", max_memory=3, htfint=538)
var Candle[] candlesadd538                  = array.new<Candle>(0)
var BOSdata bosdataadd538                   = BOSdata.new()
htfadd538.settings                 := SettingsHTFadd538
htfadd538.candles                  := candlesadd538
htfadd538.bosdata                  := bosdataadd538
var CandleSet htfadd539                     = CandleSet.new()
var CandleSettings SettingsHTFadd539        = CandleSettings.new(htf="539", max_memory=3, htfint=539)
var Candle[] candlesadd539                  = array.new<Candle>(0)
var BOSdata bosdataadd539                   = BOSdata.new()
htfadd539.settings                 := SettingsHTFadd539
htfadd539.candles                  := candlesadd539
htfadd539.bosdata                  := bosdataadd539
var CandleSet htfadd540                     = CandleSet.new()
var CandleSettings SettingsHTFadd540        = CandleSettings.new(htf="540", max_memory=3, htfint=540)
var Candle[] candlesadd540                  = array.new<Candle>(0)
var BOSdata bosdataadd540                   = BOSdata.new()
htfadd540.settings                 := SettingsHTFadd540
htfadd540.candles                  := candlesadd540
htfadd540.bosdata                  := bosdataadd540
var CandleSet htfadd541                     = CandleSet.new()
var CandleSettings SettingsHTFadd541        = CandleSettings.new(htf="541", max_memory=3, htfint=541)
var Candle[] candlesadd541                  = array.new<Candle>(0)
var BOSdata bosdataadd541                   = BOSdata.new()
htfadd541.settings                 := SettingsHTFadd541
htfadd541.candles                  := candlesadd541
htfadd541.bosdata                  := bosdataadd541
var CandleSet htfadd542                     = CandleSet.new()
var CandleSettings SettingsHTFadd542        = CandleSettings.new(htf="542", max_memory=3, htfint=542)
var Candle[] candlesadd542                  = array.new<Candle>(0)
var BOSdata bosdataadd542                   = BOSdata.new()
htfadd542.settings                 := SettingsHTFadd542
htfadd542.candles                  := candlesadd542
htfadd542.bosdata                  := bosdataadd542
var CandleSet htfadd543                     = CandleSet.new()
var CandleSettings SettingsHTFadd543        = CandleSettings.new(htf="543", max_memory=3, htfint=543)
var Candle[] candlesadd543                  = array.new<Candle>(0)
var BOSdata bosdataadd543                   = BOSdata.new()
htfadd543.settings                 := SettingsHTFadd543
htfadd543.candles                  := candlesadd543
htfadd543.bosdata                  := bosdataadd543
var CandleSet htfadd544                     = CandleSet.new()
var CandleSettings SettingsHTFadd544        = CandleSettings.new(htf="544", max_memory=3, htfint=544)
var Candle[] candlesadd544                  = array.new<Candle>(0)
var BOSdata bosdataadd544                   = BOSdata.new()
htfadd544.settings                 := SettingsHTFadd544
htfadd544.candles                  := candlesadd544
htfadd544.bosdata                  := bosdataadd544
var CandleSet htfadd545                     = CandleSet.new()
var CandleSettings SettingsHTFadd545        = CandleSettings.new(htf="545", max_memory=3, htfint=545)
var Candle[] candlesadd545                  = array.new<Candle>(0)
var BOSdata bosdataadd545                   = BOSdata.new()
htfadd545.settings                 := SettingsHTFadd545
htfadd545.candles                  := candlesadd545
htfadd545.bosdata                  := bosdataadd545
var CandleSet htfadd546                     = CandleSet.new()
var CandleSettings SettingsHTFadd546        = CandleSettings.new(htf="546", max_memory=3, htfint=546)
var Candle[] candlesadd546                  = array.new<Candle>(0)
var BOSdata bosdataadd546                   = BOSdata.new()
htfadd546.settings                 := SettingsHTFadd546
htfadd546.candles                  := candlesadd546
htfadd546.bosdata                  := bosdataadd546
var CandleSet htfadd547                     = CandleSet.new()
var CandleSettings SettingsHTFadd547        = CandleSettings.new(htf="547", max_memory=3, htfint=547)
var Candle[] candlesadd547                  = array.new<Candle>(0)
var BOSdata bosdataadd547                   = BOSdata.new()
htfadd547.settings                 := SettingsHTFadd547
htfadd547.candles                  := candlesadd547
htfadd547.bosdata                  := bosdataadd547
var CandleSet htfadd548                     = CandleSet.new()
var CandleSettings SettingsHTFadd548        = CandleSettings.new(htf="548", max_memory=3, htfint=548)
var Candle[] candlesadd548                  = array.new<Candle>(0)
var BOSdata bosdataadd548                   = BOSdata.new()
htfadd548.settings                 := SettingsHTFadd548
htfadd548.candles                  := candlesadd548
htfadd548.bosdata                  := bosdataadd548
var CandleSet htfadd549                     = CandleSet.new()
var CandleSettings SettingsHTFadd549        = CandleSettings.new(htf="549", max_memory=3, htfint=549)
var Candle[] candlesadd549                  = array.new<Candle>(0)
var BOSdata bosdataadd549                   = BOSdata.new()
htfadd549.settings                 := SettingsHTFadd549
htfadd549.candles                  := candlesadd549
htfadd549.bosdata                  := bosdataadd549
var CandleSet htfadd550                     = CandleSet.new()
var CandleSettings SettingsHTFadd550        = CandleSettings.new(htf="550", max_memory=3, htfint=550)
var Candle[] candlesadd550                  = array.new<Candle>(0)
var BOSdata bosdataadd550                   = BOSdata.new()
htfadd550.settings                 := SettingsHTFadd550
htfadd550.candles                  := candlesadd550
htfadd550.bosdata                  := bosdataadd550
var CandleSet htfadd551                     = CandleSet.new()
var CandleSettings SettingsHTFadd551        = CandleSettings.new(htf="551", max_memory=3, htfint=551)
var Candle[] candlesadd551                  = array.new<Candle>(0)
var BOSdata bosdataadd551                   = BOSdata.new()
htfadd551.settings                 := SettingsHTFadd551
htfadd551.candles                  := candlesadd551
htfadd551.bosdata                  := bosdataadd551
var CandleSet htfadd552                     = CandleSet.new()
var CandleSettings SettingsHTFadd552        = CandleSettings.new(htf="552", max_memory=3, htfint=552)
var Candle[] candlesadd552                  = array.new<Candle>(0)
var BOSdata bosdataadd552                   = BOSdata.new()
htfadd552.settings                 := SettingsHTFadd552
htfadd552.candles                  := candlesadd552
htfadd552.bosdata                  := bosdataadd552
var CandleSet htfadd553                     = CandleSet.new()
var CandleSettings SettingsHTFadd553        = CandleSettings.new(htf="553", max_memory=3, htfint=553)
var Candle[] candlesadd553                  = array.new<Candle>(0)
var BOSdata bosdataadd553                   = BOSdata.new()
htfadd553.settings                 := SettingsHTFadd553
htfadd553.candles                  := candlesadd553
htfadd553.bosdata                  := bosdataadd553
var CandleSet htfadd554                     = CandleSet.new()
var CandleSettings SettingsHTFadd554        = CandleSettings.new(htf="554", max_memory=3, htfint=554)
var Candle[] candlesadd554                  = array.new<Candle>(0)
var BOSdata bosdataadd554                   = BOSdata.new()
htfadd554.settings                 := SettingsHTFadd554
htfadd554.candles                  := candlesadd554
htfadd554.bosdata                  := bosdataadd554
var CandleSet htfadd555                     = CandleSet.new()
var CandleSettings SettingsHTFadd555        = CandleSettings.new(htf="555", max_memory=3, htfint=555)
var Candle[] candlesadd555                  = array.new<Candle>(0)
var BOSdata bosdataadd555                   = BOSdata.new()
htfadd555.settings                 := SettingsHTFadd555
htfadd555.candles                  := candlesadd555
htfadd555.bosdata                  := bosdataadd555
var CandleSet htfadd556                     = CandleSet.new()
var CandleSettings SettingsHTFadd556        = CandleSettings.new(htf="556", max_memory=3, htfint=556)
var Candle[] candlesadd556                  = array.new<Candle>(0)
var BOSdata bosdataadd556                   = BOSdata.new()
htfadd556.settings                 := SettingsHTFadd556
htfadd556.candles                  := candlesadd556
htfadd556.bosdata                  := bosdataadd556
var CandleSet htfadd557                     = CandleSet.new()
var CandleSettings SettingsHTFadd557        = CandleSettings.new(htf="557", max_memory=3, htfint=557)
var Candle[] candlesadd557                  = array.new<Candle>(0)
var BOSdata bosdataadd557                   = BOSdata.new()
htfadd557.settings                 := SettingsHTFadd557
htfadd557.candles                  := candlesadd557
htfadd557.bosdata                  := bosdataadd557
var CandleSet htfadd558                     = CandleSet.new()
var CandleSettings SettingsHTFadd558        = CandleSettings.new(htf="558", max_memory=3, htfint=558)
var Candle[] candlesadd558                  = array.new<Candle>(0)
var BOSdata bosdataadd558                   = BOSdata.new()
htfadd558.settings                 := SettingsHTFadd558
htfadd558.candles                  := candlesadd558
htfadd558.bosdata                  := bosdataadd558
var CandleSet htfadd559                     = CandleSet.new()
var CandleSettings SettingsHTFadd559        = CandleSettings.new(htf="559", max_memory=3, htfint=559)
var Candle[] candlesadd559                  = array.new<Candle>(0)
var BOSdata bosdataadd559                   = BOSdata.new()
htfadd559.settings                 := SettingsHTFadd559
htfadd559.candles                  := candlesadd559
htfadd559.bosdata                  := bosdataadd559
var CandleSet htfadd560                     = CandleSet.new()
var CandleSettings SettingsHTFadd560        = CandleSettings.new(htf="560", max_memory=3, htfint=560)
var Candle[] candlesadd560                  = array.new<Candle>(0)
var BOSdata bosdataadd560                   = BOSdata.new()
htfadd560.settings                 := SettingsHTFadd560
htfadd560.candles                  := candlesadd560
htfadd560.bosdata                  := bosdataadd560
var CandleSet htfadd561                     = CandleSet.new()
var CandleSettings SettingsHTFadd561        = CandleSettings.new(htf="561", max_memory=3, htfint=561)
var Candle[] candlesadd561                  = array.new<Candle>(0)
var BOSdata bosdataadd561                   = BOSdata.new()
htfadd561.settings                 := SettingsHTFadd561
htfadd561.candles                  := candlesadd561
htfadd561.bosdata                  := bosdataadd561
var CandleSet htfadd562                     = CandleSet.new()
var CandleSettings SettingsHTFadd562        = CandleSettings.new(htf="562", max_memory=3, htfint=562)
var Candle[] candlesadd562                  = array.new<Candle>(0)
var BOSdata bosdataadd562                   = BOSdata.new()
htfadd562.settings                 := SettingsHTFadd562
htfadd562.candles                  := candlesadd562
htfadd562.bosdata                  := bosdataadd562
var CandleSet htfadd563                     = CandleSet.new()
var CandleSettings SettingsHTFadd563        = CandleSettings.new(htf="563", max_memory=3, htfint=563)
var Candle[] candlesadd563                  = array.new<Candle>(0)
var BOSdata bosdataadd563                   = BOSdata.new()
htfadd563.settings                 := SettingsHTFadd563
htfadd563.candles                  := candlesadd563
htfadd563.bosdata                  := bosdataadd563
var CandleSet htfadd564                     = CandleSet.new()
var CandleSettings SettingsHTFadd564        = CandleSettings.new(htf="564", max_memory=3, htfint=564)
var Candle[] candlesadd564                  = array.new<Candle>(0)
var BOSdata bosdataadd564                   = BOSdata.new()
htfadd564.settings                 := SettingsHTFadd564
htfadd564.candles                  := candlesadd564
htfadd564.bosdata                  := bosdataadd564
var CandleSet htfadd565                     = CandleSet.new()
var CandleSettings SettingsHTFadd565        = CandleSettings.new(htf="565", max_memory=3, htfint=565)
var Candle[] candlesadd565                  = array.new<Candle>(0)
var BOSdata bosdataadd565                   = BOSdata.new()
htfadd565.settings                 := SettingsHTFadd565
htfadd565.candles                  := candlesadd565
htfadd565.bosdata                  := bosdataadd565
var CandleSet htfadd566                     = CandleSet.new()
var CandleSettings SettingsHTFadd566        = CandleSettings.new(htf="566", max_memory=3, htfint=566)
var Candle[] candlesadd566                  = array.new<Candle>(0)
var BOSdata bosdataadd566                   = BOSdata.new()
htfadd566.settings                 := SettingsHTFadd566
htfadd566.candles                  := candlesadd566
htfadd566.bosdata                  := bosdataadd566
var CandleSet htfadd567                     = CandleSet.new()
var CandleSettings SettingsHTFadd567        = CandleSettings.new(htf="567", max_memory=3, htfint=567)
var Candle[] candlesadd567                  = array.new<Candle>(0)
var BOSdata bosdataadd567                   = BOSdata.new()
htfadd567.settings                 := SettingsHTFadd567
htfadd567.candles                  := candlesadd567
htfadd567.bosdata                  := bosdataadd567
var CandleSet htfadd568                     = CandleSet.new()
var CandleSettings SettingsHTFadd568        = CandleSettings.new(htf="568", max_memory=3, htfint=568)
var Candle[] candlesadd568                  = array.new<Candle>(0)
var BOSdata bosdataadd568                   = BOSdata.new()
htfadd568.settings                 := SettingsHTFadd568
htfadd568.candles                  := candlesadd568
htfadd568.bosdata                  := bosdataadd568
var CandleSet htfadd569                     = CandleSet.new()
var CandleSettings SettingsHTFadd569        = CandleSettings.new(htf="569", max_memory=3, htfint=569)
var Candle[] candlesadd569                  = array.new<Candle>(0)
var BOSdata bosdataadd569                   = BOSdata.new()
htfadd569.settings                 := SettingsHTFadd569
htfadd569.candles                  := candlesadd569
htfadd569.bosdata                  := bosdataadd569
var CandleSet htfadd570                     = CandleSet.new()
var CandleSettings SettingsHTFadd570        = CandleSettings.new(htf="570", max_memory=3, htfint=570)
var Candle[] candlesadd570                  = array.new<Candle>(0)
var BOSdata bosdataadd570                   = BOSdata.new()
htfadd570.settings                 := SettingsHTFadd570
htfadd570.candles                  := candlesadd570
htfadd570.bosdata                  := bosdataadd570
var CandleSet htfadd571                     = CandleSet.new()
var CandleSettings SettingsHTFadd571        = CandleSettings.new(htf="571", max_memory=3, htfint=571)
var Candle[] candlesadd571                  = array.new<Candle>(0)
var BOSdata bosdataadd571                   = BOSdata.new()
htfadd571.settings                 := SettingsHTFadd571
htfadd571.candles                  := candlesadd571
htfadd571.bosdata                  := bosdataadd571
var CandleSet htfadd572                     = CandleSet.new()
var CandleSettings SettingsHTFadd572        = CandleSettings.new(htf="572", max_memory=3, htfint=572)
var Candle[] candlesadd572                  = array.new<Candle>(0)
var BOSdata bosdataadd572                   = BOSdata.new()
htfadd572.settings                 := SettingsHTFadd572
htfadd572.candles                  := candlesadd572
htfadd572.bosdata                  := bosdataadd572
var CandleSet htfadd573                     = CandleSet.new()
var CandleSettings SettingsHTFadd573        = CandleSettings.new(htf="573", max_memory=3, htfint=573)
var Candle[] candlesadd573                  = array.new<Candle>(0)
var BOSdata bosdataadd573                   = BOSdata.new()
htfadd573.settings                 := SettingsHTFadd573
htfadd573.candles                  := candlesadd573
htfadd573.bosdata                  := bosdataadd573
var CandleSet htfadd574                     = CandleSet.new()
var CandleSettings SettingsHTFadd574        = CandleSettings.new(htf="574", max_memory=3, htfint=574)
var Candle[] candlesadd574                  = array.new<Candle>(0)
var BOSdata bosdataadd574                   = BOSdata.new()
htfadd574.settings                 := SettingsHTFadd574
htfadd574.candles                  := candlesadd574
htfadd574.bosdata                  := bosdataadd574
var CandleSet htfadd575                     = CandleSet.new()
var CandleSettings SettingsHTFadd575        = CandleSettings.new(htf="575", max_memory=3, htfint=575)
var Candle[] candlesadd575                  = array.new<Candle>(0)
var BOSdata bosdataadd575                   = BOSdata.new()
htfadd575.settings                 := SettingsHTFadd575
htfadd575.candles                  := candlesadd575
htfadd575.bosdata                  := bosdataadd575
var CandleSet htfadd576                     = CandleSet.new()
var CandleSettings SettingsHTFadd576        = CandleSettings.new(htf="576", max_memory=3, htfint=576)
var Candle[] candlesadd576                  = array.new<Candle>(0)
var BOSdata bosdataadd576                   = BOSdata.new()
htfadd576.settings                 := SettingsHTFadd576
htfadd576.candles                  := candlesadd576
htfadd576.bosdata                  := bosdataadd576
var CandleSet htfadd577                     = CandleSet.new()
var CandleSettings SettingsHTFadd577        = CandleSettings.new(htf="577", max_memory=3, htfint=577)
var Candle[] candlesadd577                  = array.new<Candle>(0)
var BOSdata bosdataadd577                   = BOSdata.new()
htfadd577.settings                 := SettingsHTFadd577
htfadd577.candles                  := candlesadd577
htfadd577.bosdata                  := bosdataadd577
var CandleSet htfadd578                     = CandleSet.new()
var CandleSettings SettingsHTFadd578        = CandleSettings.new(htf="578", max_memory=3, htfint=578)
var Candle[] candlesadd578                  = array.new<Candle>(0)
var BOSdata bosdataadd578                   = BOSdata.new()
htfadd578.settings                 := SettingsHTFadd578
htfadd578.candles                  := candlesadd578
htfadd578.bosdata                  := bosdataadd578
var CandleSet htfadd579                     = CandleSet.new()
var CandleSettings SettingsHTFadd579        = CandleSettings.new(htf="579", max_memory=3, htfint=579)
var Candle[] candlesadd579                  = array.new<Candle>(0)
var BOSdata bosdataadd579                   = BOSdata.new()
htfadd579.settings                 := SettingsHTFadd579
htfadd579.candles                  := candlesadd579
htfadd579.bosdata                  := bosdataadd579
var CandleSet htfadd580                     = CandleSet.new()
var CandleSettings SettingsHTFadd580        = CandleSettings.new(htf="580", max_memory=3, htfint=580)
var Candle[] candlesadd580                  = array.new<Candle>(0)
var BOSdata bosdataadd580                   = BOSdata.new()
htfadd580.settings                 := SettingsHTFadd580
htfadd580.candles                  := candlesadd580
htfadd580.bosdata                  := bosdataadd580
var CandleSet htfadd581                     = CandleSet.new()
var CandleSettings SettingsHTFadd581        = CandleSettings.new(htf="581", max_memory=3, htfint=581)
var Candle[] candlesadd581                  = array.new<Candle>(0)
var BOSdata bosdataadd581                   = BOSdata.new()
htfadd581.settings                 := SettingsHTFadd581
htfadd581.candles                  := candlesadd581
htfadd581.bosdata                  := bosdataadd581
var CandleSet htfadd582                     = CandleSet.new()
var CandleSettings SettingsHTFadd582        = CandleSettings.new(htf="582", max_memory=3, htfint=582)
var Candle[] candlesadd582                  = array.new<Candle>(0)
var BOSdata bosdataadd582                   = BOSdata.new()
htfadd582.settings                 := SettingsHTFadd582
htfadd582.candles                  := candlesadd582
htfadd582.bosdata                  := bosdataadd582
var CandleSet htfadd583                     = CandleSet.new()
var CandleSettings SettingsHTFadd583        = CandleSettings.new(htf="583", max_memory=3, htfint=583)
var Candle[] candlesadd583                  = array.new<Candle>(0)
var BOSdata bosdataadd583                   = BOSdata.new()
htfadd583.settings                 := SettingsHTFadd583
htfadd583.candles                  := candlesadd583
htfadd583.bosdata                  := bosdataadd583
var CandleSet htfadd584                     = CandleSet.new()
var CandleSettings SettingsHTFadd584        = CandleSettings.new(htf="584", max_memory=3, htfint=584)
var Candle[] candlesadd584                  = array.new<Candle>(0)
var BOSdata bosdataadd584                   = BOSdata.new()
htfadd584.settings                 := SettingsHTFadd584
htfadd584.candles                  := candlesadd584
htfadd584.bosdata                  := bosdataadd584
var CandleSet htfadd585                     = CandleSet.new()
var CandleSettings SettingsHTFadd585        = CandleSettings.new(htf="585", max_memory=3, htfint=585)
var Candle[] candlesadd585                  = array.new<Candle>(0)
var BOSdata bosdataadd585                   = BOSdata.new()
htfadd585.settings                 := SettingsHTFadd585
htfadd585.candles                  := candlesadd585
htfadd585.bosdata                  := bosdataadd585
var CandleSet htfadd586                     = CandleSet.new()
var CandleSettings SettingsHTFadd586        = CandleSettings.new(htf="586", max_memory=3, htfint=586)
var Candle[] candlesadd586                  = array.new<Candle>(0)
var BOSdata bosdataadd586                   = BOSdata.new()
htfadd586.settings                 := SettingsHTFadd586
htfadd586.candles                  := candlesadd586
htfadd586.bosdata                  := bosdataadd586
var CandleSet htfadd587                     = CandleSet.new()
var CandleSettings SettingsHTFadd587        = CandleSettings.new(htf="587", max_memory=3, htfint=587)
var Candle[] candlesadd587                  = array.new<Candle>(0)
var BOSdata bosdataadd587                   = BOSdata.new()
htfadd587.settings                 := SettingsHTFadd587
htfadd587.candles                  := candlesadd587
htfadd587.bosdata                  := bosdataadd587
var CandleSet htfadd588                     = CandleSet.new()
var CandleSettings SettingsHTFadd588        = CandleSettings.new(htf="588", max_memory=3, htfint=588)
var Candle[] candlesadd588                  = array.new<Candle>(0)
var BOSdata bosdataadd588                   = BOSdata.new()
htfadd588.settings                 := SettingsHTFadd588
htfadd588.candles                  := candlesadd588
htfadd588.bosdata                  := bosdataadd588
var CandleSet htfadd589                     = CandleSet.new()
var CandleSettings SettingsHTFadd589        = CandleSettings.new(htf="589", max_memory=3, htfint=589)
var Candle[] candlesadd589                  = array.new<Candle>(0)
var BOSdata bosdataadd589                   = BOSdata.new()
htfadd589.settings                 := SettingsHTFadd589
htfadd589.candles                  := candlesadd589
htfadd589.bosdata                  := bosdataadd589
var CandleSet htfadd590                     = CandleSet.new()
var CandleSettings SettingsHTFadd590        = CandleSettings.new(htf="590", max_memory=3, htfint=590)
var Candle[] candlesadd590                  = array.new<Candle>(0)
var BOSdata bosdataadd590                   = BOSdata.new()
htfadd590.settings                 := SettingsHTFadd590
htfadd590.candles                  := candlesadd590
htfadd590.bosdata                  := bosdataadd590
var CandleSet htfadd591                     = CandleSet.new()
var CandleSettings SettingsHTFadd591        = CandleSettings.new(htf="591", max_memory=3, htfint=591)
var Candle[] candlesadd591                  = array.new<Candle>(0)
var BOSdata bosdataadd591                   = BOSdata.new()
htfadd591.settings                 := SettingsHTFadd591
htfadd591.candles                  := candlesadd591
htfadd591.bosdata                  := bosdataadd591
var CandleSet htfadd592                     = CandleSet.new()
var CandleSettings SettingsHTFadd592        = CandleSettings.new(htf="592", max_memory=3, htfint=592)
var Candle[] candlesadd592                  = array.new<Candle>(0)
var BOSdata bosdataadd592                   = BOSdata.new()
htfadd592.settings                 := SettingsHTFadd592
htfadd592.candles                  := candlesadd592
htfadd592.bosdata                  := bosdataadd592
var CandleSet htfadd593                     = CandleSet.new()
var CandleSettings SettingsHTFadd593        = CandleSettings.new(htf="593", max_memory=3, htfint=593)
var Candle[] candlesadd593                  = array.new<Candle>(0)
var BOSdata bosdataadd593                   = BOSdata.new()
htfadd593.settings                 := SettingsHTFadd593
htfadd593.candles                  := candlesadd593
htfadd593.bosdata                  := bosdataadd593
var CandleSet htfadd594                     = CandleSet.new()
var CandleSettings SettingsHTFadd594        = CandleSettings.new(htf="594", max_memory=3, htfint=594)
var Candle[] candlesadd594                  = array.new<Candle>(0)
var BOSdata bosdataadd594                   = BOSdata.new()
htfadd594.settings                 := SettingsHTFadd594
htfadd594.candles                  := candlesadd594
htfadd594.bosdata                  := bosdataadd594
var CandleSet htfadd595                     = CandleSet.new()
var CandleSettings SettingsHTFadd595        = CandleSettings.new(htf="595", max_memory=3, htfint=595)
var Candle[] candlesadd595                  = array.new<Candle>(0)
var BOSdata bosdataadd595                   = BOSdata.new()
htfadd595.settings                 := SettingsHTFadd595
htfadd595.candles                  := candlesadd595
htfadd595.bosdata                  := bosdataadd595
var CandleSet htfadd596                     = CandleSet.new()
var CandleSettings SettingsHTFadd596        = CandleSettings.new(htf="596", max_memory=3, htfint=596)
var Candle[] candlesadd596                  = array.new<Candle>(0)
var BOSdata bosdataadd596                   = BOSdata.new()
htfadd596.settings                 := SettingsHTFadd596
htfadd596.candles                  := candlesadd596
htfadd596.bosdata                  := bosdataadd596
var CandleSet htfadd597                     = CandleSet.new()
var CandleSettings SettingsHTFadd597        = CandleSettings.new(htf="597", max_memory=3, htfint=597)
var Candle[] candlesadd597                  = array.new<Candle>(0)
var BOSdata bosdataadd597                   = BOSdata.new()
htfadd597.settings                 := SettingsHTFadd597
htfadd597.candles                  := candlesadd597
htfadd597.bosdata                  := bosdataadd597
var CandleSet htfadd598                     = CandleSet.new()
var CandleSettings SettingsHTFadd598        = CandleSettings.new(htf="598", max_memory=3, htfint=598)
var Candle[] candlesadd598                  = array.new<Candle>(0)
var BOSdata bosdataadd598                   = BOSdata.new()
htfadd598.settings                 := SettingsHTFadd598
htfadd598.candles                  := candlesadd598
htfadd598.bosdata                  := bosdataadd598
var CandleSet htfadd599                     = CandleSet.new()
var CandleSettings SettingsHTFadd599        = CandleSettings.new(htf="599", max_memory=3, htfint=599)
var Candle[] candlesadd599                  = array.new<Candle>(0)
var BOSdata bosdataadd599                   = BOSdata.new()
htfadd599.settings                 := SettingsHTFadd599
htfadd599.candles                  := candlesadd599
htfadd599.bosdata                  := bosdataadd599
var CandleSet htfadd600                     = CandleSet.new()
var CandleSettings SettingsHTFadd600        = CandleSettings.new(htf="600", max_memory=3, htfint=600)
var Candle[] candlesadd600                  = array.new<Candle>(0)
var BOSdata bosdataadd600                   = BOSdata.new()
htfadd600.settings                 := SettingsHTFadd600
htfadd600.candles                  := candlesadd600
htfadd600.bosdata                  := bosdataadd600
var CandleSet htfadd601                     = CandleSet.new()
var CandleSettings SettingsHTFadd601        = CandleSettings.new(htf="601", max_memory=3, htfint=601)
var Candle[] candlesadd601                  = array.new<Candle>(0)
var BOSdata bosdataadd601                   = BOSdata.new()
htfadd601.settings                 := SettingsHTFadd601
htfadd601.candles                  := candlesadd601
htfadd601.bosdata                  := bosdataadd601
var CandleSet htfadd602                     = CandleSet.new()
var CandleSettings SettingsHTFadd602        = CandleSettings.new(htf="602", max_memory=3, htfint=602)
var Candle[] candlesadd602                  = array.new<Candle>(0)
var BOSdata bosdataadd602                   = BOSdata.new()
htfadd602.settings                 := SettingsHTFadd602
htfadd602.candles                  := candlesadd602
htfadd602.bosdata                  := bosdataadd602
var CandleSet htfadd603                     = CandleSet.new()
var CandleSettings SettingsHTFadd603        = CandleSettings.new(htf="603", max_memory=3, htfint=603)
var Candle[] candlesadd603                  = array.new<Candle>(0)
var BOSdata bosdataadd603                   = BOSdata.new()
htfadd603.settings                 := SettingsHTFadd603
htfadd603.candles                  := candlesadd603
htfadd603.bosdata                  := bosdataadd603
var CandleSet htfadd604                     = CandleSet.new()
var CandleSettings SettingsHTFadd604        = CandleSettings.new(htf="604", max_memory=3, htfint=604)
var Candle[] candlesadd604                  = array.new<Candle>(0)
var BOSdata bosdataadd604                   = BOSdata.new()
htfadd604.settings                 := SettingsHTFadd604
htfadd604.candles                  := candlesadd604
htfadd604.bosdata                  := bosdataadd604
var CandleSet htfadd605                     = CandleSet.new()
var CandleSettings SettingsHTFadd605        = CandleSettings.new(htf="605", max_memory=3, htfint=605)
var Candle[] candlesadd605                  = array.new<Candle>(0)
var BOSdata bosdataadd605                   = BOSdata.new()
htfadd605.settings                 := SettingsHTFadd605
htfadd605.candles                  := candlesadd605
htfadd605.bosdata                  := bosdataadd605
var CandleSet htfadd606                     = CandleSet.new()
var CandleSettings SettingsHTFadd606        = CandleSettings.new(htf="606", max_memory=3, htfint=606)
var Candle[] candlesadd606                  = array.new<Candle>(0)
var BOSdata bosdataadd606                   = BOSdata.new()
htfadd606.settings                 := SettingsHTFadd606
htfadd606.candles                  := candlesadd606
htfadd606.bosdata                  := bosdataadd606
var CandleSet htfadd607                     = CandleSet.new()
var CandleSettings SettingsHTFadd607        = CandleSettings.new(htf="607", max_memory=3, htfint=607)
var Candle[] candlesadd607                  = array.new<Candle>(0)
var BOSdata bosdataadd607                   = BOSdata.new()
htfadd607.settings                 := SettingsHTFadd607
htfadd607.candles                  := candlesadd607
htfadd607.bosdata                  := bosdataadd607
var CandleSet htfadd608                     = CandleSet.new()
var CandleSettings SettingsHTFadd608        = CandleSettings.new(htf="608", max_memory=3, htfint=608)
var Candle[] candlesadd608                  = array.new<Candle>(0)
var BOSdata bosdataadd608                   = BOSdata.new()
htfadd608.settings                 := SettingsHTFadd608
htfadd608.candles                  := candlesadd608
htfadd608.bosdata                  := bosdataadd608
var CandleSet htfadd609                     = CandleSet.new()
var CandleSettings SettingsHTFadd609        = CandleSettings.new(htf="609", max_memory=3, htfint=609)
var Candle[] candlesadd609                  = array.new<Candle>(0)
var BOSdata bosdataadd609                   = BOSdata.new()
htfadd609.settings                 := SettingsHTFadd609
htfadd609.candles                  := candlesadd609
htfadd609.bosdata                  := bosdataadd609
var CandleSet htfadd610                     = CandleSet.new()
var CandleSettings SettingsHTFadd610        = CandleSettings.new(htf="610", max_memory=3, htfint=610)
var Candle[] candlesadd610                  = array.new<Candle>(0)
var BOSdata bosdataadd610                   = BOSdata.new()
htfadd610.settings                 := SettingsHTFadd610
htfadd610.candles                  := candlesadd610
htfadd610.bosdata                  := bosdataadd610
var CandleSet htfadd611                     = CandleSet.new()
var CandleSettings SettingsHTFadd611        = CandleSettings.new(htf="611", max_memory=3, htfint=611)
var Candle[] candlesadd611                  = array.new<Candle>(0)
var BOSdata bosdataadd611                   = BOSdata.new()
htfadd611.settings                 := SettingsHTFadd611
htfadd611.candles                  := candlesadd611
htfadd611.bosdata                  := bosdataadd611
var CandleSet htfadd612                     = CandleSet.new()
var CandleSettings SettingsHTFadd612        = CandleSettings.new(htf="612", max_memory=3, htfint=612)
var Candle[] candlesadd612                  = array.new<Candle>(0)
var BOSdata bosdataadd612                   = BOSdata.new()
htfadd612.settings                 := SettingsHTFadd612
htfadd612.candles                  := candlesadd612
htfadd612.bosdata                  := bosdataadd612
var CandleSet htfadd613                     = CandleSet.new()
var CandleSettings SettingsHTFadd613        = CandleSettings.new(htf="613", max_memory=3, htfint=613)
var Candle[] candlesadd613                  = array.new<Candle>(0)
var BOSdata bosdataadd613                   = BOSdata.new()
htfadd613.settings                 := SettingsHTFadd613
htfadd613.candles                  := candlesadd613
htfadd613.bosdata                  := bosdataadd613
var CandleSet htfadd614                     = CandleSet.new()
var CandleSettings SettingsHTFadd614        = CandleSettings.new(htf="614", max_memory=3, htfint=614)
var Candle[] candlesadd614                  = array.new<Candle>(0)
var BOSdata bosdataadd614                   = BOSdata.new()
htfadd614.settings                 := SettingsHTFadd614
htfadd614.candles                  := candlesadd614
htfadd614.bosdata                  := bosdataadd614
var CandleSet htfadd615                     = CandleSet.new()
var CandleSettings SettingsHTFadd615        = CandleSettings.new(htf="615", max_memory=3, htfint=615)
var Candle[] candlesadd615                  = array.new<Candle>(0)
var BOSdata bosdataadd615                   = BOSdata.new()
htfadd615.settings                 := SettingsHTFadd615
htfadd615.candles                  := candlesadd615
htfadd615.bosdata                  := bosdataadd615
var CandleSet htfadd616                     = CandleSet.new()
var CandleSettings SettingsHTFadd616        = CandleSettings.new(htf="616", max_memory=3, htfint=616)
var Candle[] candlesadd616                  = array.new<Candle>(0)
var BOSdata bosdataadd616                   = BOSdata.new()
htfadd616.settings                 := SettingsHTFadd616
htfadd616.candles                  := candlesadd616
htfadd616.bosdata                  := bosdataadd616
var CandleSet htfadd617                     = CandleSet.new()
var CandleSettings SettingsHTFadd617        = CandleSettings.new(htf="617", max_memory=3, htfint=617)
var Candle[] candlesadd617                  = array.new<Candle>(0)
var BOSdata bosdataadd617                   = BOSdata.new()
htfadd617.settings                 := SettingsHTFadd617
htfadd617.candles                  := candlesadd617
htfadd617.bosdata                  := bosdataadd617
var CandleSet htfadd618                     = CandleSet.new()
var CandleSettings SettingsHTFadd618        = CandleSettings.new(htf="618", max_memory=3, htfint=618)
var Candle[] candlesadd618                  = array.new<Candle>(0)
var BOSdata bosdataadd618                   = BOSdata.new()
htfadd618.settings                 := SettingsHTFadd618
htfadd618.candles                  := candlesadd618
htfadd618.bosdata                  := bosdataadd618
var CandleSet htfadd619                     = CandleSet.new()
var CandleSettings SettingsHTFadd619        = CandleSettings.new(htf="619", max_memory=3, htfint=619)
var Candle[] candlesadd619                  = array.new<Candle>(0)
var BOSdata bosdataadd619                   = BOSdata.new()
htfadd619.settings                 := SettingsHTFadd619
htfadd619.candles                  := candlesadd619
htfadd619.bosdata                  := bosdataadd619
var CandleSet htfadd620                     = CandleSet.new()
var CandleSettings SettingsHTFadd620        = CandleSettings.new(htf="620", max_memory=3, htfint=620)
var Candle[] candlesadd620                  = array.new<Candle>(0)
var BOSdata bosdataadd620                   = BOSdata.new()
htfadd620.settings                 := SettingsHTFadd620
htfadd620.candles                  := candlesadd620
htfadd620.bosdata                  := bosdataadd620
var CandleSet htfadd621                     = CandleSet.new()
var CandleSettings SettingsHTFadd621        = CandleSettings.new(htf="621", max_memory=3, htfint=621)
var Candle[] candlesadd621                  = array.new<Candle>(0)
var BOSdata bosdataadd621                   = BOSdata.new()
htfadd621.settings                 := SettingsHTFadd621
htfadd621.candles                  := candlesadd621
htfadd621.bosdata                  := bosdataadd621
var CandleSet htfadd622                     = CandleSet.new()
var CandleSettings SettingsHTFadd622        = CandleSettings.new(htf="622", max_memory=3, htfint=622)
var Candle[] candlesadd622                  = array.new<Candle>(0)
var BOSdata bosdataadd622                   = BOSdata.new()
htfadd622.settings                 := SettingsHTFadd622
htfadd622.candles                  := candlesadd622
htfadd622.bosdata                  := bosdataadd622
var CandleSet htfadd623                     = CandleSet.new()
var CandleSettings SettingsHTFadd623        = CandleSettings.new(htf="623", max_memory=3, htfint=623)
var Candle[] candlesadd623                  = array.new<Candle>(0)
var BOSdata bosdataadd623                   = BOSdata.new()
htfadd623.settings                 := SettingsHTFadd623
htfadd623.candles                  := candlesadd623
htfadd623.bosdata                  := bosdataadd623
var CandleSet htfadd624                     = CandleSet.new()
var CandleSettings SettingsHTFadd624        = CandleSettings.new(htf="624", max_memory=3, htfint=624)
var Candle[] candlesadd624                  = array.new<Candle>(0)
var BOSdata bosdataadd624                   = BOSdata.new()
htfadd624.settings                 := SettingsHTFadd624
htfadd624.candles                  := candlesadd624
htfadd624.bosdata                  := bosdataadd624
var CandleSet htfadd625                     = CandleSet.new()
var CandleSettings SettingsHTFadd625        = CandleSettings.new(htf="625", max_memory=3, htfint=625)
var Candle[] candlesadd625                  = array.new<Candle>(0)
var BOSdata bosdataadd625                   = BOSdata.new()
htfadd625.settings                 := SettingsHTFadd625
htfadd625.candles                  := candlesadd625
htfadd625.bosdata                  := bosdataadd625
var CandleSet htfadd626                     = CandleSet.new()
var CandleSettings SettingsHTFadd626        = CandleSettings.new(htf="626", max_memory=3, htfint=626)
var Candle[] candlesadd626                  = array.new<Candle>(0)
var BOSdata bosdataadd626                   = BOSdata.new()
htfadd626.settings                 := SettingsHTFadd626
htfadd626.candles                  := candlesadd626
htfadd626.bosdata                  := bosdataadd626
var CandleSet htfadd627                     = CandleSet.new()
var CandleSettings SettingsHTFadd627        = CandleSettings.new(htf="627", max_memory=3, htfint=627)
var Candle[] candlesadd627                  = array.new<Candle>(0)
var BOSdata bosdataadd627                   = BOSdata.new()
htfadd627.settings                 := SettingsHTFadd627
htfadd627.candles                  := candlesadd627
htfadd627.bosdata                  := bosdataadd627
var CandleSet htfadd628                     = CandleSet.new()
var CandleSettings SettingsHTFadd628        = CandleSettings.new(htf="628", max_memory=3, htfint=628)
var Candle[] candlesadd628                  = array.new<Candle>(0)
var BOSdata bosdataadd628                   = BOSdata.new()
htfadd628.settings                 := SettingsHTFadd628
htfadd628.candles                  := candlesadd628
htfadd628.bosdata                  := bosdataadd628
var CandleSet htfadd629                     = CandleSet.new()
var CandleSettings SettingsHTFadd629        = CandleSettings.new(htf="629", max_memory=3, htfint=629)
var Candle[] candlesadd629                  = array.new<Candle>(0)
var BOSdata bosdataadd629                   = BOSdata.new()
htfadd629.settings                 := SettingsHTFadd629
htfadd629.candles                  := candlesadd629
htfadd629.bosdata                  := bosdataadd629
var CandleSet htfadd630                     = CandleSet.new()
var CandleSettings SettingsHTFadd630        = CandleSettings.new(htf="630", max_memory=3, htfint=630)
var Candle[] candlesadd630                  = array.new<Candle>(0)
var BOSdata bosdataadd630                   = BOSdata.new()
htfadd630.settings                 := SettingsHTFadd630
htfadd630.candles                  := candlesadd630
htfadd630.bosdata                  := bosdataadd630
var CandleSet htfadd631                     = CandleSet.new()
var CandleSettings SettingsHTFadd631        = CandleSettings.new(htf="631", max_memory=3, htfint=631)
var Candle[] candlesadd631                  = array.new<Candle>(0)
var BOSdata bosdataadd631                   = BOSdata.new()
htfadd631.settings                 := SettingsHTFadd631
htfadd631.candles                  := candlesadd631
htfadd631.bosdata                  := bosdataadd631
var CandleSet htfadd632                     = CandleSet.new()
var CandleSettings SettingsHTFadd632        = CandleSettings.new(htf="632", max_memory=3, htfint=632)
var Candle[] candlesadd632                  = array.new<Candle>(0)
var BOSdata bosdataadd632                   = BOSdata.new()
htfadd632.settings                 := SettingsHTFadd632
htfadd632.candles                  := candlesadd632
htfadd632.bosdata                  := bosdataadd632
var CandleSet htfadd633                     = CandleSet.new()
var CandleSettings SettingsHTFadd633        = CandleSettings.new(htf="633", max_memory=3, htfint=633)
var Candle[] candlesadd633                  = array.new<Candle>(0)
var BOSdata bosdataadd633                   = BOSdata.new()
htfadd633.settings                 := SettingsHTFadd633
htfadd633.candles                  := candlesadd633
htfadd633.bosdata                  := bosdataadd633
var CandleSet htfadd634                     = CandleSet.new()
var CandleSettings SettingsHTFadd634        = CandleSettings.new(htf="634", max_memory=3, htfint=634)
var Candle[] candlesadd634                  = array.new<Candle>(0)
var BOSdata bosdataadd634                   = BOSdata.new()
htfadd634.settings                 := SettingsHTFadd634
htfadd634.candles                  := candlesadd634
htfadd634.bosdata                  := bosdataadd634
var CandleSet htfadd635                     = CandleSet.new()
var CandleSettings SettingsHTFadd635        = CandleSettings.new(htf="635", max_memory=3, htfint=635)
var Candle[] candlesadd635                  = array.new<Candle>(0)
var BOSdata bosdataadd635                   = BOSdata.new()
htfadd635.settings                 := SettingsHTFadd635
htfadd635.candles                  := candlesadd635
htfadd635.bosdata                  := bosdataadd635
var CandleSet htfadd636                     = CandleSet.new()
var CandleSettings SettingsHTFadd636        = CandleSettings.new(htf="636", max_memory=3, htfint=636)
var Candle[] candlesadd636                  = array.new<Candle>(0)
var BOSdata bosdataadd636                   = BOSdata.new()
htfadd636.settings                 := SettingsHTFadd636
htfadd636.candles                  := candlesadd636
htfadd636.bosdata                  := bosdataadd636
var CandleSet htfadd637                     = CandleSet.new()
var CandleSettings SettingsHTFadd637        = CandleSettings.new(htf="637", max_memory=3, htfint=637)
var Candle[] candlesadd637                  = array.new<Candle>(0)
var BOSdata bosdataadd637                   = BOSdata.new()
htfadd637.settings                 := SettingsHTFadd637
htfadd637.candles                  := candlesadd637
htfadd637.bosdata                  := bosdataadd637
var CandleSet htfadd638                     = CandleSet.new()
var CandleSettings SettingsHTFadd638        = CandleSettings.new(htf="638", max_memory=3, htfint=638)
var Candle[] candlesadd638                  = array.new<Candle>(0)
var BOSdata bosdataadd638                   = BOSdata.new()
htfadd638.settings                 := SettingsHTFadd638
htfadd638.candles                  := candlesadd638
htfadd638.bosdata                  := bosdataadd638
var CandleSet htfadd639                     = CandleSet.new()
var CandleSettings SettingsHTFadd639        = CandleSettings.new(htf="639", max_memory=3, htfint=639)
var Candle[] candlesadd639                  = array.new<Candle>(0)
var BOSdata bosdataadd639                   = BOSdata.new()
htfadd639.settings                 := SettingsHTFadd639
htfadd639.candles                  := candlesadd639
htfadd639.bosdata                  := bosdataadd639
var CandleSet htfadd640                     = CandleSet.new()
var CandleSettings SettingsHTFadd640        = CandleSettings.new(htf="640", max_memory=3, htfint=640)
var Candle[] candlesadd640                  = array.new<Candle>(0)
var BOSdata bosdataadd640                   = BOSdata.new()
htfadd640.settings                 := SettingsHTFadd640
htfadd640.candles                  := candlesadd640
htfadd640.bosdata                  := bosdataadd640
var CandleSet htfadd641                     = CandleSet.new()
var CandleSettings SettingsHTFadd641        = CandleSettings.new(htf="641", max_memory=3, htfint=641)
var Candle[] candlesadd641                  = array.new<Candle>(0)
var BOSdata bosdataadd641                   = BOSdata.new()
htfadd641.settings                 := SettingsHTFadd641
htfadd641.candles                  := candlesadd641
htfadd641.bosdata                  := bosdataadd641
var CandleSet htfadd642                     = CandleSet.new()
var CandleSettings SettingsHTFadd642        = CandleSettings.new(htf="642", max_memory=3, htfint=642)
var Candle[] candlesadd642                  = array.new<Candle>(0)
var BOSdata bosdataadd642                   = BOSdata.new()
htfadd642.settings                 := SettingsHTFadd642
htfadd642.candles                  := candlesadd642
htfadd642.bosdata                  := bosdataadd642
var CandleSet htfadd643                     = CandleSet.new()
var CandleSettings SettingsHTFadd643        = CandleSettings.new(htf="643", max_memory=3, htfint=643)
var Candle[] candlesadd643                  = array.new<Candle>(0)
var BOSdata bosdataadd643                   = BOSdata.new()
htfadd643.settings                 := SettingsHTFadd643
htfadd643.candles                  := candlesadd643
htfadd643.bosdata                  := bosdataadd643
var CandleSet htfadd644                     = CandleSet.new()
var CandleSettings SettingsHTFadd644        = CandleSettings.new(htf="644", max_memory=3, htfint=644)
var Candle[] candlesadd644                  = array.new<Candle>(0)
var BOSdata bosdataadd644                   = BOSdata.new()
htfadd644.settings                 := SettingsHTFadd644
htfadd644.candles                  := candlesadd644
htfadd644.bosdata                  := bosdataadd644
var CandleSet htfadd645                     = CandleSet.new()
var CandleSettings SettingsHTFadd645        = CandleSettings.new(htf="645", max_memory=3, htfint=645)
var Candle[] candlesadd645                  = array.new<Candle>(0)
var BOSdata bosdataadd645                   = BOSdata.new()
htfadd645.settings                 := SettingsHTFadd645
htfadd645.candles                  := candlesadd645
htfadd645.bosdata                  := bosdataadd645
var CandleSet htfadd646                     = CandleSet.new()
var CandleSettings SettingsHTFadd646        = CandleSettings.new(htf="646", max_memory=3, htfint=646)
var Candle[] candlesadd646                  = array.new<Candle>(0)
var BOSdata bosdataadd646                   = BOSdata.new()
htfadd646.settings                 := SettingsHTFadd646
htfadd646.candles                  := candlesadd646
htfadd646.bosdata                  := bosdataadd646
var CandleSet htfadd647                     = CandleSet.new()
var CandleSettings SettingsHTFadd647        = CandleSettings.new(htf="647", max_memory=3, htfint=647)
var Candle[] candlesadd647                  = array.new<Candle>(0)
var BOSdata bosdataadd647                   = BOSdata.new()
htfadd647.settings                 := SettingsHTFadd647
htfadd647.candles                  := candlesadd647
htfadd647.bosdata                  := bosdataadd647
var CandleSet htfadd648                     = CandleSet.new()
var CandleSettings SettingsHTFadd648        = CandleSettings.new(htf="648", max_memory=3, htfint=648)
var Candle[] candlesadd648                  = array.new<Candle>(0)
var BOSdata bosdataadd648                   = BOSdata.new()
htfadd648.settings                 := SettingsHTFadd648
htfadd648.candles                  := candlesadd648
htfadd648.bosdata                  := bosdataadd648
var CandleSet htfadd649                     = CandleSet.new()
var CandleSettings SettingsHTFadd649        = CandleSettings.new(htf="649", max_memory=3, htfint=649)
var Candle[] candlesadd649                  = array.new<Candle>(0)
var BOSdata bosdataadd649                   = BOSdata.new()
htfadd649.settings                 := SettingsHTFadd649
htfadd649.candles                  := candlesadd649
htfadd649.bosdata                  := bosdataadd649
var CandleSet htfadd650                     = CandleSet.new()
var CandleSettings SettingsHTFadd650        = CandleSettings.new(htf="650", max_memory=3, htfint=650)
var Candle[] candlesadd650                  = array.new<Candle>(0)
var BOSdata bosdataadd650                   = BOSdata.new()
htfadd650.settings                 := SettingsHTFadd650
htfadd650.candles                  := candlesadd650
htfadd650.bosdata                  := bosdataadd650
var CandleSet htfadd651                     = CandleSet.new()
var CandleSettings SettingsHTFadd651        = CandleSettings.new(htf="651", max_memory=3, htfint=651)
var Candle[] candlesadd651                  = array.new<Candle>(0)
var BOSdata bosdataadd651                   = BOSdata.new()
htfadd651.settings                 := SettingsHTFadd651
htfadd651.candles                  := candlesadd651
htfadd651.bosdata                  := bosdataadd651
var CandleSet htfadd652                     = CandleSet.new()
var CandleSettings SettingsHTFadd652        = CandleSettings.new(htf="652", max_memory=3, htfint=652)
var Candle[] candlesadd652                  = array.new<Candle>(0)
var BOSdata bosdataadd652                   = BOSdata.new()
htfadd652.settings                 := SettingsHTFadd652
htfadd652.candles                  := candlesadd652
htfadd652.bosdata                  := bosdataadd652
var CandleSet htfadd653                     = CandleSet.new()
var CandleSettings SettingsHTFadd653        = CandleSettings.new(htf="653", max_memory=3, htfint=653)
var Candle[] candlesadd653                  = array.new<Candle>(0)
var BOSdata bosdataadd653                   = BOSdata.new()
htfadd653.settings                 := SettingsHTFadd653
htfadd653.candles                  := candlesadd653
htfadd653.bosdata                  := bosdataadd653
var CandleSet htfadd654                     = CandleSet.new()
var CandleSettings SettingsHTFadd654        = CandleSettings.new(htf="654", max_memory=3, htfint=654)
var Candle[] candlesadd654                  = array.new<Candle>(0)
var BOSdata bosdataadd654                   = BOSdata.new()
htfadd654.settings                 := SettingsHTFadd654
htfadd654.candles                  := candlesadd654
htfadd654.bosdata                  := bosdataadd654
var CandleSet htfadd655                     = CandleSet.new()
var CandleSettings SettingsHTFadd655        = CandleSettings.new(htf="655", max_memory=3, htfint=655)
var Candle[] candlesadd655                  = array.new<Candle>(0)
var BOSdata bosdataadd655                   = BOSdata.new()
htfadd655.settings                 := SettingsHTFadd655
htfadd655.candles                  := candlesadd655
htfadd655.bosdata                  := bosdataadd655
var CandleSet htfadd656                     = CandleSet.new()
var CandleSettings SettingsHTFadd656        = CandleSettings.new(htf="656", max_memory=3, htfint=656)
var Candle[] candlesadd656                  = array.new<Candle>(0)
var BOSdata bosdataadd656                   = BOSdata.new()
htfadd656.settings                 := SettingsHTFadd656
htfadd656.candles                  := candlesadd656
htfadd656.bosdata                  := bosdataadd656
var CandleSet htfadd657                     = CandleSet.new()
var CandleSettings SettingsHTFadd657        = CandleSettings.new(htf="657", max_memory=3, htfint=657)
var Candle[] candlesadd657                  = array.new<Candle>(0)
var BOSdata bosdataadd657                   = BOSdata.new()
htfadd657.settings                 := SettingsHTFadd657
htfadd657.candles                  := candlesadd657
htfadd657.bosdata                  := bosdataadd657
var CandleSet htfadd658                     = CandleSet.new()
var CandleSettings SettingsHTFadd658        = CandleSettings.new(htf="658", max_memory=3, htfint=658)
var Candle[] candlesadd658                  = array.new<Candle>(0)
var BOSdata bosdataadd658                   = BOSdata.new()
htfadd658.settings                 := SettingsHTFadd658
htfadd658.candles                  := candlesadd658
htfadd658.bosdata                  := bosdataadd658
var CandleSet htfadd659                     = CandleSet.new()
var CandleSettings SettingsHTFadd659        = CandleSettings.new(htf="659", max_memory=3, htfint=659)
var Candle[] candlesadd659                  = array.new<Candle>(0)
var BOSdata bosdataadd659                   = BOSdata.new()
htfadd659.settings                 := SettingsHTFadd659
htfadd659.candles                  := candlesadd659
htfadd659.bosdata                  := bosdataadd659
var CandleSet htfadd660                     = CandleSet.new()
var CandleSettings SettingsHTFadd660        = CandleSettings.new(htf="660", max_memory=3, htfint=660)
var Candle[] candlesadd660                  = array.new<Candle>(0)
var BOSdata bosdataadd660                   = BOSdata.new()
htfadd660.settings                 := SettingsHTFadd660
htfadd660.candles                  := candlesadd660
htfadd660.bosdata                  := bosdataadd660
var CandleSet htfadd661                     = CandleSet.new()
var CandleSettings SettingsHTFadd661        = CandleSettings.new(htf="661", max_memory=3, htfint=661)
var Candle[] candlesadd661                  = array.new<Candle>(0)
var BOSdata bosdataadd661                   = BOSdata.new()
htfadd661.settings                 := SettingsHTFadd661
htfadd661.candles                  := candlesadd661
htfadd661.bosdata                  := bosdataadd661
var CandleSet htfadd662                     = CandleSet.new()
var CandleSettings SettingsHTFadd662        = CandleSettings.new(htf="662", max_memory=3, htfint=662)
var Candle[] candlesadd662                  = array.new<Candle>(0)
var BOSdata bosdataadd662                   = BOSdata.new()
htfadd662.settings                 := SettingsHTFadd662
htfadd662.candles                  := candlesadd662
htfadd662.bosdata                  := bosdataadd662
var CandleSet htfadd663                     = CandleSet.new()
var CandleSettings SettingsHTFadd663        = CandleSettings.new(htf="663", max_memory=3, htfint=663)
var Candle[] candlesadd663                  = array.new<Candle>(0)
var BOSdata bosdataadd663                   = BOSdata.new()
htfadd663.settings                 := SettingsHTFadd663
htfadd663.candles                  := candlesadd663
htfadd663.bosdata                  := bosdataadd663
var CandleSet htfadd664                     = CandleSet.new()
var CandleSettings SettingsHTFadd664        = CandleSettings.new(htf="664", max_memory=3, htfint=664)
var Candle[] candlesadd664                  = array.new<Candle>(0)
var BOSdata bosdataadd664                   = BOSdata.new()
htfadd664.settings                 := SettingsHTFadd664
htfadd664.candles                  := candlesadd664
htfadd664.bosdata                  := bosdataadd664
var CandleSet htfadd665                     = CandleSet.new()
var CandleSettings SettingsHTFadd665        = CandleSettings.new(htf="665", max_memory=3, htfint=665)
var Candle[] candlesadd665                  = array.new<Candle>(0)
var BOSdata bosdataadd665                   = BOSdata.new()
htfadd665.settings                 := SettingsHTFadd665
htfadd665.candles                  := candlesadd665
htfadd665.bosdata                  := bosdataadd665
var CandleSet htfadd666                     = CandleSet.new()
var CandleSettings SettingsHTFadd666        = CandleSettings.new(htf="666", max_memory=3, htfint=666)
var Candle[] candlesadd666                  = array.new<Candle>(0)
var BOSdata bosdataadd666                   = BOSdata.new()
htfadd666.settings                 := SettingsHTFadd666
htfadd666.candles                  := candlesadd666
htfadd666.bosdata                  := bosdataadd666
var CandleSet htfadd667                     = CandleSet.new()
var CandleSettings SettingsHTFadd667        = CandleSettings.new(htf="667", max_memory=3, htfint=667)
var Candle[] candlesadd667                  = array.new<Candle>(0)
var BOSdata bosdataadd667                   = BOSdata.new()
htfadd667.settings                 := SettingsHTFadd667
htfadd667.candles                  := candlesadd667
htfadd667.bosdata                  := bosdataadd667
var CandleSet htfadd668                     = CandleSet.new()
var CandleSettings SettingsHTFadd668        = CandleSettings.new(htf="668", max_memory=3, htfint=668)
var Candle[] candlesadd668                  = array.new<Candle>(0)
var BOSdata bosdataadd668                   = BOSdata.new()
htfadd668.settings                 := SettingsHTFadd668
htfadd668.candles                  := candlesadd668
htfadd668.bosdata                  := bosdataadd668
var CandleSet htfadd669                     = CandleSet.new()
var CandleSettings SettingsHTFadd669        = CandleSettings.new(htf="669", max_memory=3, htfint=669)
var Candle[] candlesadd669                  = array.new<Candle>(0)
var BOSdata bosdataadd669                   = BOSdata.new()
htfadd669.settings                 := SettingsHTFadd669
htfadd669.candles                  := candlesadd669
htfadd669.bosdata                  := bosdataadd669
var CandleSet htfadd670                     = CandleSet.new()
var CandleSettings SettingsHTFadd670        = CandleSettings.new(htf="670", max_memory=3, htfint=670)
var Candle[] candlesadd670                  = array.new<Candle>(0)
var BOSdata bosdataadd670                   = BOSdata.new()
htfadd670.settings                 := SettingsHTFadd670
htfadd670.candles                  := candlesadd670
htfadd670.bosdata                  := bosdataadd670
var CandleSet htfadd671                     = CandleSet.new()
var CandleSettings SettingsHTFadd671        = CandleSettings.new(htf="671", max_memory=3, htfint=671)
var Candle[] candlesadd671                  = array.new<Candle>(0)
var BOSdata bosdataadd671                   = BOSdata.new()
htfadd671.settings                 := SettingsHTFadd671
htfadd671.candles                  := candlesadd671
htfadd671.bosdata                  := bosdataadd671
var CandleSet htfadd672                     = CandleSet.new()
var CandleSettings SettingsHTFadd672        = CandleSettings.new(htf="672", max_memory=3, htfint=672)
var Candle[] candlesadd672                  = array.new<Candle>(0)
var BOSdata bosdataadd672                   = BOSdata.new()
htfadd672.settings                 := SettingsHTFadd672
htfadd672.candles                  := candlesadd672
htfadd672.bosdata                  := bosdataadd672
var CandleSet htfadd673                     = CandleSet.new()
var CandleSettings SettingsHTFadd673        = CandleSettings.new(htf="673", max_memory=3, htfint=673)
var Candle[] candlesadd673                  = array.new<Candle>(0)
var BOSdata bosdataadd673                   = BOSdata.new()
htfadd673.settings                 := SettingsHTFadd673
htfadd673.candles                  := candlesadd673
htfadd673.bosdata                  := bosdataadd673
var CandleSet htfadd674                     = CandleSet.new()
var CandleSettings SettingsHTFadd674        = CandleSettings.new(htf="674", max_memory=3, htfint=674)
var Candle[] candlesadd674                  = array.new<Candle>(0)
var BOSdata bosdataadd674                   = BOSdata.new()
htfadd674.settings                 := SettingsHTFadd674
htfadd674.candles                  := candlesadd674
htfadd674.bosdata                  := bosdataadd674
var CandleSet htfadd675                     = CandleSet.new()
var CandleSettings SettingsHTFadd675        = CandleSettings.new(htf="675", max_memory=3, htfint=675)
var Candle[] candlesadd675                  = array.new<Candle>(0)
var BOSdata bosdataadd675                   = BOSdata.new()
htfadd675.settings                 := SettingsHTFadd675
htfadd675.candles                  := candlesadd675
htfadd675.bosdata                  := bosdataadd675
var CandleSet htfadd676                     = CandleSet.new()
var CandleSettings SettingsHTFadd676        = CandleSettings.new(htf="676", max_memory=3, htfint=676)
var Candle[] candlesadd676                  = array.new<Candle>(0)
var BOSdata bosdataadd676                   = BOSdata.new()
htfadd676.settings                 := SettingsHTFadd676
htfadd676.candles                  := candlesadd676
htfadd676.bosdata                  := bosdataadd676
var CandleSet htfadd677                     = CandleSet.new()
var CandleSettings SettingsHTFadd677        = CandleSettings.new(htf="677", max_memory=3, htfint=677)
var Candle[] candlesadd677                  = array.new<Candle>(0)
var BOSdata bosdataadd677                   = BOSdata.new()
htfadd677.settings                 := SettingsHTFadd677
htfadd677.candles                  := candlesadd677
htfadd677.bosdata                  := bosdataadd677
var CandleSet htfadd678                     = CandleSet.new()
var CandleSettings SettingsHTFadd678        = CandleSettings.new(htf="678", max_memory=3, htfint=678)
var Candle[] candlesadd678                  = array.new<Candle>(0)
var BOSdata bosdataadd678                   = BOSdata.new()
htfadd678.settings                 := SettingsHTFadd678
htfadd678.candles                  := candlesadd678
htfadd678.bosdata                  := bosdataadd678
var CandleSet htfadd679                     = CandleSet.new()
var CandleSettings SettingsHTFadd679        = CandleSettings.new(htf="679", max_memory=3, htfint=679)
var Candle[] candlesadd679                  = array.new<Candle>(0)
var BOSdata bosdataadd679                   = BOSdata.new()
htfadd679.settings                 := SettingsHTFadd679
htfadd679.candles                  := candlesadd679
htfadd679.bosdata                  := bosdataadd679
var CandleSet htfadd680                     = CandleSet.new()
var CandleSettings SettingsHTFadd680        = CandleSettings.new(htf="680", max_memory=3, htfint=680)
var Candle[] candlesadd680                  = array.new<Candle>(0)
var BOSdata bosdataadd680                   = BOSdata.new()
htfadd680.settings                 := SettingsHTFadd680
htfadd680.candles                  := candlesadd680
htfadd680.bosdata                  := bosdataadd680
var CandleSet htfadd681                     = CandleSet.new()
var CandleSettings SettingsHTFadd681        = CandleSettings.new(htf="681", max_memory=3, htfint=681)
var Candle[] candlesadd681                  = array.new<Candle>(0)
var BOSdata bosdataadd681                   = BOSdata.new()
htfadd681.settings                 := SettingsHTFadd681
htfadd681.candles                  := candlesadd681
htfadd681.bosdata                  := bosdataadd681
var CandleSet htfadd682                     = CandleSet.new()
var CandleSettings SettingsHTFadd682        = CandleSettings.new(htf="682", max_memory=3, htfint=682)
var Candle[] candlesadd682                  = array.new<Candle>(0)
var BOSdata bosdataadd682                   = BOSdata.new()
htfadd682.settings                 := SettingsHTFadd682
htfadd682.candles                  := candlesadd682
htfadd682.bosdata                  := bosdataadd682
var CandleSet htfadd683                     = CandleSet.new()
var CandleSettings SettingsHTFadd683        = CandleSettings.new(htf="683", max_memory=3, htfint=683)
var Candle[] candlesadd683                  = array.new<Candle>(0)
var BOSdata bosdataadd683                   = BOSdata.new()
htfadd683.settings                 := SettingsHTFadd683
htfadd683.candles                  := candlesadd683
htfadd683.bosdata                  := bosdataadd683
var CandleSet htfadd684                     = CandleSet.new()
var CandleSettings SettingsHTFadd684        = CandleSettings.new(htf="684", max_memory=3, htfint=684)
var Candle[] candlesadd684                  = array.new<Candle>(0)
var BOSdata bosdataadd684                   = BOSdata.new()
htfadd684.settings                 := SettingsHTFadd684
htfadd684.candles                  := candlesadd684
htfadd684.bosdata                  := bosdataadd684
var CandleSet htfadd685                     = CandleSet.new()
var CandleSettings SettingsHTFadd685        = CandleSettings.new(htf="685", max_memory=3, htfint=685)
var Candle[] candlesadd685                  = array.new<Candle>(0)
var BOSdata bosdataadd685                   = BOSdata.new()
htfadd685.settings                 := SettingsHTFadd685
htfadd685.candles                  := candlesadd685
htfadd685.bosdata                  := bosdataadd685
var CandleSet htfadd686                     = CandleSet.new()
var CandleSettings SettingsHTFadd686        = CandleSettings.new(htf="686", max_memory=3, htfint=686)
var Candle[] candlesadd686                  = array.new<Candle>(0)
var BOSdata bosdataadd686                   = BOSdata.new()
htfadd686.settings                 := SettingsHTFadd686
htfadd686.candles                  := candlesadd686
htfadd686.bosdata                  := bosdataadd686
var CandleSet htfadd687                     = CandleSet.new()
var CandleSettings SettingsHTFadd687        = CandleSettings.new(htf="687", max_memory=3, htfint=687)
var Candle[] candlesadd687                  = array.new<Candle>(0)
var BOSdata bosdataadd687                   = BOSdata.new()
htfadd687.settings                 := SettingsHTFadd687
htfadd687.candles                  := candlesadd687
htfadd687.bosdata                  := bosdataadd687
var CandleSet htfadd688                     = CandleSet.new()
var CandleSettings SettingsHTFadd688        = CandleSettings.new(htf="688", max_memory=3, htfint=688)
var Candle[] candlesadd688                  = array.new<Candle>(0)
var BOSdata bosdataadd688                   = BOSdata.new()
htfadd688.settings                 := SettingsHTFadd688
htfadd688.candles                  := candlesadd688
htfadd688.bosdata                  := bosdataadd688
var CandleSet htfadd689                     = CandleSet.new()
var CandleSettings SettingsHTFadd689        = CandleSettings.new(htf="689", max_memory=3, htfint=689)
var Candle[] candlesadd689                  = array.new<Candle>(0)
var BOSdata bosdataadd689                   = BOSdata.new()
htfadd689.settings                 := SettingsHTFadd689
htfadd689.candles                  := candlesadd689
htfadd689.bosdata                  := bosdataadd689
var CandleSet htfadd690                     = CandleSet.new()
var CandleSettings SettingsHTFadd690        = CandleSettings.new(htf="690", max_memory=3, htfint=690)
var Candle[] candlesadd690                  = array.new<Candle>(0)
var BOSdata bosdataadd690                   = BOSdata.new()
htfadd690.settings                 := SettingsHTFadd690
htfadd690.candles                  := candlesadd690
htfadd690.bosdata                  := bosdataadd690
var CandleSet htfadd691                     = CandleSet.new()
var CandleSettings SettingsHTFadd691        = CandleSettings.new(htf="691", max_memory=3, htfint=691)
var Candle[] candlesadd691                  = array.new<Candle>(0)
var BOSdata bosdataadd691                   = BOSdata.new()
htfadd691.settings                 := SettingsHTFadd691
htfadd691.candles                  := candlesadd691
htfadd691.bosdata                  := bosdataadd691
var CandleSet htfadd692                     = CandleSet.new()
var CandleSettings SettingsHTFadd692        = CandleSettings.new(htf="692", max_memory=3, htfint=692)
var Candle[] candlesadd692                  = array.new<Candle>(0)
var BOSdata bosdataadd692                   = BOSdata.new()
htfadd692.settings                 := SettingsHTFadd692
htfadd692.candles                  := candlesadd692
htfadd692.bosdata                  := bosdataadd692
var CandleSet htfadd693                     = CandleSet.new()
var CandleSettings SettingsHTFadd693        = CandleSettings.new(htf="693", max_memory=3, htfint=693)
var Candle[] candlesadd693                  = array.new<Candle>(0)
var BOSdata bosdataadd693                   = BOSdata.new()
htfadd693.settings                 := SettingsHTFadd693
htfadd693.candles                  := candlesadd693
htfadd693.bosdata                  := bosdataadd693
var CandleSet htfadd694                     = CandleSet.new()
var CandleSettings SettingsHTFadd694        = CandleSettings.new(htf="694", max_memory=3, htfint=694)
var Candle[] candlesadd694                  = array.new<Candle>(0)
var BOSdata bosdataadd694                   = BOSdata.new()
htfadd694.settings                 := SettingsHTFadd694
htfadd694.candles                  := candlesadd694
htfadd694.bosdata                  := bosdataadd694
var CandleSet htfadd695                     = CandleSet.new()
var CandleSettings SettingsHTFadd695        = CandleSettings.new(htf="695", max_memory=3, htfint=695)
var Candle[] candlesadd695                  = array.new<Candle>(0)
var BOSdata bosdataadd695                   = BOSdata.new()
htfadd695.settings                 := SettingsHTFadd695
htfadd695.candles                  := candlesadd695
htfadd695.bosdata                  := bosdataadd695
var CandleSet htfadd696                     = CandleSet.new()
var CandleSettings SettingsHTFadd696        = CandleSettings.new(htf="696", max_memory=3, htfint=696)
var Candle[] candlesadd696                  = array.new<Candle>(0)
var BOSdata bosdataadd696                   = BOSdata.new()
htfadd696.settings                 := SettingsHTFadd696
htfadd696.candles                  := candlesadd696
htfadd696.bosdata                  := bosdataadd696
var CandleSet htfadd697                     = CandleSet.new()
var CandleSettings SettingsHTFadd697        = CandleSettings.new(htf="697", max_memory=3, htfint=697)
var Candle[] candlesadd697                  = array.new<Candle>(0)
var BOSdata bosdataadd697                   = BOSdata.new()
htfadd697.settings                 := SettingsHTFadd697
htfadd697.candles                  := candlesadd697
htfadd697.bosdata                  := bosdataadd697
var CandleSet htfadd698                     = CandleSet.new()
var CandleSettings SettingsHTFadd698        = CandleSettings.new(htf="698", max_memory=3, htfint=698)
var Candle[] candlesadd698                  = array.new<Candle>(0)
var BOSdata bosdataadd698                   = BOSdata.new()
htfadd698.settings                 := SettingsHTFadd698
htfadd698.candles                  := candlesadd698
htfadd698.bosdata                  := bosdataadd698
var CandleSet htfadd699                     = CandleSet.new()
var CandleSettings SettingsHTFadd699        = CandleSettings.new(htf="699", max_memory=3, htfint=699)
var Candle[] candlesadd699                  = array.new<Candle>(0)
var BOSdata bosdataadd699                   = BOSdata.new()
htfadd699.settings                 := SettingsHTFadd699
htfadd699.candles                  := candlesadd699
htfadd699.bosdata                  := bosdataadd699
var CandleSet htfadd700                     = CandleSet.new()
var CandleSettings SettingsHTFadd700        = CandleSettings.new(htf="700", max_memory=3, htfint=700)
var Candle[] candlesadd700                  = array.new<Candle>(0)
var BOSdata bosdataadd700                   = BOSdata.new()
htfadd700.settings                 := SettingsHTFadd700
htfadd700.candles                  := candlesadd700
htfadd700.bosdata                  := bosdataadd700
var CandleSet htfadd701                     = CandleSet.new()
var CandleSettings SettingsHTFadd701        = CandleSettings.new(htf="701", max_memory=3, htfint=701)
var Candle[] candlesadd701                  = array.new<Candle>(0)
var BOSdata bosdataadd701                   = BOSdata.new()
htfadd701.settings                 := SettingsHTFadd701
htfadd701.candles                  := candlesadd701
htfadd701.bosdata                  := bosdataadd701
var CandleSet htfadd702                     = CandleSet.new()
var CandleSettings SettingsHTFadd702        = CandleSettings.new(htf="702", max_memory=3, htfint=702)
var Candle[] candlesadd702                  = array.new<Candle>(0)
var BOSdata bosdataadd702                   = BOSdata.new()
htfadd702.settings                 := SettingsHTFadd702
htfadd702.candles                  := candlesadd702
htfadd702.bosdata                  := bosdataadd702
var CandleSet htfadd703                     = CandleSet.new()
var CandleSettings SettingsHTFadd703        = CandleSettings.new(htf="703", max_memory=3, htfint=703)
var Candle[] candlesadd703                  = array.new<Candle>(0)
var BOSdata bosdataadd703                   = BOSdata.new()
htfadd703.settings                 := SettingsHTFadd703
htfadd703.candles                  := candlesadd703
htfadd703.bosdata                  := bosdataadd703
var CandleSet htfadd704                     = CandleSet.new()
var CandleSettings SettingsHTFadd704        = CandleSettings.new(htf="704", max_memory=3, htfint=704)
var Candle[] candlesadd704                  = array.new<Candle>(0)
var BOSdata bosdataadd704                   = BOSdata.new()
htfadd704.settings                 := SettingsHTFadd704
htfadd704.candles                  := candlesadd704
htfadd704.bosdata                  := bosdataadd704
var CandleSet htfadd705                     = CandleSet.new()
var CandleSettings SettingsHTFadd705        = CandleSettings.new(htf="705", max_memory=3, htfint=705)
var Candle[] candlesadd705                  = array.new<Candle>(0)
var BOSdata bosdataadd705                   = BOSdata.new()
htfadd705.settings                 := SettingsHTFadd705
htfadd705.candles                  := candlesadd705
htfadd705.bosdata                  := bosdataadd705
var CandleSet htfadd706                     = CandleSet.new()
var CandleSettings SettingsHTFadd706        = CandleSettings.new(htf="706", max_memory=3, htfint=706)
var Candle[] candlesadd706                  = array.new<Candle>(0)
var BOSdata bosdataadd706                   = BOSdata.new()
htfadd706.settings                 := SettingsHTFadd706
htfadd706.candles                  := candlesadd706
htfadd706.bosdata                  := bosdataadd706
var CandleSet htfadd707                     = CandleSet.new()
var CandleSettings SettingsHTFadd707        = CandleSettings.new(htf="707", max_memory=3, htfint=707)
var Candle[] candlesadd707                  = array.new<Candle>(0)
var BOSdata bosdataadd707                   = BOSdata.new()
htfadd707.settings                 := SettingsHTFadd707
htfadd707.candles                  := candlesadd707
htfadd707.bosdata                  := bosdataadd707
var CandleSet htfadd708                     = CandleSet.new()
var CandleSettings SettingsHTFadd708        = CandleSettings.new(htf="708", max_memory=3, htfint=708)
var Candle[] candlesadd708                  = array.new<Candle>(0)
var BOSdata bosdataadd708                   = BOSdata.new()
htfadd708.settings                 := SettingsHTFadd708
htfadd708.candles                  := candlesadd708
htfadd708.bosdata                  := bosdataadd708
var CandleSet htfadd709                     = CandleSet.new()
var CandleSettings SettingsHTFadd709        = CandleSettings.new(htf="709", max_memory=3, htfint=709)
var Candle[] candlesadd709                  = array.new<Candle>(0)
var BOSdata bosdataadd709                   = BOSdata.new()
htfadd709.settings                 := SettingsHTFadd709
htfadd709.candles                  := candlesadd709
htfadd709.bosdata                  := bosdataadd709
var CandleSet htfadd710                     = CandleSet.new()
var CandleSettings SettingsHTFadd710        = CandleSettings.new(htf="710", max_memory=3, htfint=710)
var Candle[] candlesadd710                  = array.new<Candle>(0)
var BOSdata bosdataadd710                   = BOSdata.new()
htfadd710.settings                 := SettingsHTFadd710
htfadd710.candles                  := candlesadd710
htfadd710.bosdata                  := bosdataadd710
var CandleSet htfadd711                     = CandleSet.new()
var CandleSettings SettingsHTFadd711        = CandleSettings.new(htf="711", max_memory=3, htfint=711)
var Candle[] candlesadd711                  = array.new<Candle>(0)
var BOSdata bosdataadd711                   = BOSdata.new()
htfadd711.settings                 := SettingsHTFadd711
htfadd711.candles                  := candlesadd711
htfadd711.bosdata                  := bosdataadd711
var CandleSet htfadd712                     = CandleSet.new()
var CandleSettings SettingsHTFadd712        = CandleSettings.new(htf="712", max_memory=3, htfint=712)
var Candle[] candlesadd712                  = array.new<Candle>(0)
var BOSdata bosdataadd712                   = BOSdata.new()
htfadd712.settings                 := SettingsHTFadd712
htfadd712.candles                  := candlesadd712
htfadd712.bosdata                  := bosdataadd712
var CandleSet htfadd713                     = CandleSet.new()
var CandleSettings SettingsHTFadd713        = CandleSettings.new(htf="713", max_memory=3, htfint=713)
var Candle[] candlesadd713                  = array.new<Candle>(0)
var BOSdata bosdataadd713                   = BOSdata.new()
htfadd713.settings                 := SettingsHTFadd713
htfadd713.candles                  := candlesadd713
htfadd713.bosdata                  := bosdataadd713
var CandleSet htfadd714                     = CandleSet.new()
var CandleSettings SettingsHTFadd714        = CandleSettings.new(htf="714", max_memory=3, htfint=714)
var Candle[] candlesadd714                  = array.new<Candle>(0)
var BOSdata bosdataadd714                   = BOSdata.new()
htfadd714.settings                 := SettingsHTFadd714
htfadd714.candles                  := candlesadd714
htfadd714.bosdata                  := bosdataadd714
var CandleSet htfadd715                     = CandleSet.new()
var CandleSettings SettingsHTFadd715        = CandleSettings.new(htf="715", max_memory=3, htfint=715)
var Candle[] candlesadd715                  = array.new<Candle>(0)
var BOSdata bosdataadd715                   = BOSdata.new()
htfadd715.settings                 := SettingsHTFadd715
htfadd715.candles                  := candlesadd715
htfadd715.bosdata                  := bosdataadd715
var CandleSet htfadd716                     = CandleSet.new()
var CandleSettings SettingsHTFadd716        = CandleSettings.new(htf="716", max_memory=3, htfint=716)
var Candle[] candlesadd716                  = array.new<Candle>(0)
var BOSdata bosdataadd716                   = BOSdata.new()
htfadd716.settings                 := SettingsHTFadd716
htfadd716.candles                  := candlesadd716
htfadd716.bosdata                  := bosdataadd716
var CandleSet htfadd717                     = CandleSet.new()
var CandleSettings SettingsHTFadd717        = CandleSettings.new(htf="717", max_memory=3, htfint=717)
var Candle[] candlesadd717                  = array.new<Candle>(0)
var BOSdata bosdataadd717                   = BOSdata.new()
htfadd717.settings                 := SettingsHTFadd717
htfadd717.candles                  := candlesadd717
htfadd717.bosdata                  := bosdataadd717
var CandleSet htfadd718                     = CandleSet.new()
var CandleSettings SettingsHTFadd718        = CandleSettings.new(htf="718", max_memory=3, htfint=718)
var Candle[] candlesadd718                  = array.new<Candle>(0)
var BOSdata bosdataadd718                   = BOSdata.new()
htfadd718.settings                 := SettingsHTFadd718
htfadd718.candles                  := candlesadd718
htfadd718.bosdata                  := bosdataadd718
var CandleSet htfadd719                     = CandleSet.new()
var CandleSettings SettingsHTFadd719        = CandleSettings.new(htf="719", max_memory=3, htfint=719)
var Candle[] candlesadd719                  = array.new<Candle>(0)
var BOSdata bosdataadd719                   = BOSdata.new()
htfadd719.settings                 := SettingsHTFadd719
htfadd719.candles                  := candlesadd719
htfadd719.bosdata                  := bosdataadd719
var CandleSet htfadd720                     = CandleSet.new()
var CandleSettings SettingsHTFadd720        = CandleSettings.new(htf="720", max_memory=3, htfint=720)
var Candle[] candlesadd720                  = array.new<Candle>(0)
var BOSdata bosdataadd720                   = BOSdata.new()
htfadd720.settings                 := SettingsHTFadd720
htfadd720.candles                  := candlesadd720
htfadd720.bosdata                  := bosdataadd720
var CandleSet htfadd721                     = CandleSet.new()
var CandleSettings SettingsHTFadd721        = CandleSettings.new(htf="721", max_memory=3, htfint=721)
var Candle[] candlesadd721                  = array.new<Candle>(0)
var BOSdata bosdataadd721                   = BOSdata.new()
htfadd721.settings                 := SettingsHTFadd721
htfadd721.candles                  := candlesadd721
htfadd721.bosdata                  := bosdataadd721
var CandleSet htfadd722                     = CandleSet.new()
var CandleSettings SettingsHTFadd722        = CandleSettings.new(htf="722", max_memory=3, htfint=722)
var Candle[] candlesadd722                  = array.new<Candle>(0)
var BOSdata bosdataadd722                   = BOSdata.new()
htfadd722.settings                 := SettingsHTFadd722
htfadd722.candles                  := candlesadd722
htfadd722.bosdata                  := bosdataadd722
var CandleSet htfadd723                     = CandleSet.new()
var CandleSettings SettingsHTFadd723        = CandleSettings.new(htf="723", max_memory=3, htfint=723)
var Candle[] candlesadd723                  = array.new<Candle>(0)
var BOSdata bosdataadd723                   = BOSdata.new()
htfadd723.settings                 := SettingsHTFadd723
htfadd723.candles                  := candlesadd723
htfadd723.bosdata                  := bosdataadd723
var CandleSet htfadd724                     = CandleSet.new()
var CandleSettings SettingsHTFadd724        = CandleSettings.new(htf="724", max_memory=3, htfint=724)
var Candle[] candlesadd724                  = array.new<Candle>(0)
var BOSdata bosdataadd724                   = BOSdata.new()
htfadd724.settings                 := SettingsHTFadd724
htfadd724.candles                  := candlesadd724
htfadd724.bosdata                  := bosdataadd724
var CandleSet htfadd725                     = CandleSet.new()
var CandleSettings SettingsHTFadd725        = CandleSettings.new(htf="725", max_memory=3, htfint=725)
var Candle[] candlesadd725                  = array.new<Candle>(0)
var BOSdata bosdataadd725                   = BOSdata.new()
htfadd725.settings                 := SettingsHTFadd725
htfadd725.candles                  := candlesadd725
htfadd725.bosdata                  := bosdataadd725
var CandleSet htfadd726                     = CandleSet.new()
var CandleSettings SettingsHTFadd726        = CandleSettings.new(htf="726", max_memory=3, htfint=726)
var Candle[] candlesadd726                  = array.new<Candle>(0)
var BOSdata bosdataadd726                   = BOSdata.new()
htfadd726.settings                 := SettingsHTFadd726
htfadd726.candles                  := candlesadd726
htfadd726.bosdata                  := bosdataadd726
var CandleSet htfadd727                     = CandleSet.new()
var CandleSettings SettingsHTFadd727        = CandleSettings.new(htf="727", max_memory=3, htfint=727)
var Candle[] candlesadd727                  = array.new<Candle>(0)
var BOSdata bosdataadd727                   = BOSdata.new()
htfadd727.settings                 := SettingsHTFadd727
htfadd727.candles                  := candlesadd727
htfadd727.bosdata                  := bosdataadd727
var CandleSet htfadd728                     = CandleSet.new()
var CandleSettings SettingsHTFadd728        = CandleSettings.new(htf="728", max_memory=3, htfint=728)
var Candle[] candlesadd728                  = array.new<Candle>(0)
var BOSdata bosdataadd728                   = BOSdata.new()
htfadd728.settings                 := SettingsHTFadd728
htfadd728.candles                  := candlesadd728
htfadd728.bosdata                  := bosdataadd728
var CandleSet htfadd729                     = CandleSet.new()
var CandleSettings SettingsHTFadd729        = CandleSettings.new(htf="729", max_memory=3, htfint=729)
var Candle[] candlesadd729                  = array.new<Candle>(0)
var BOSdata bosdataadd729                   = BOSdata.new()
htfadd729.settings                 := SettingsHTFadd729
htfadd729.candles                  := candlesadd729
htfadd729.bosdata                  := bosdataadd729
var CandleSet htfadd730                     = CandleSet.new()
var CandleSettings SettingsHTFadd730        = CandleSettings.new(htf="730", max_memory=3, htfint=730)
var Candle[] candlesadd730                  = array.new<Candle>(0)
var BOSdata bosdataadd730                   = BOSdata.new()
htfadd730.settings                 := SettingsHTFadd730
htfadd730.candles                  := candlesadd730
htfadd730.bosdata                  := bosdataadd730
var CandleSet htfadd731                     = CandleSet.new()
var CandleSettings SettingsHTFadd731        = CandleSettings.new(htf="731", max_memory=3, htfint=731)
var Candle[] candlesadd731                  = array.new<Candle>(0)
var BOSdata bosdataadd731                   = BOSdata.new()
htfadd731.settings                 := SettingsHTFadd731
htfadd731.candles                  := candlesadd731
htfadd731.bosdata                  := bosdataadd731
var CandleSet htfadd732                     = CandleSet.new()
var CandleSettings SettingsHTFadd732        = CandleSettings.new(htf="732", max_memory=3, htfint=732)
var Candle[] candlesadd732                  = array.new<Candle>(0)
var BOSdata bosdataadd732                   = BOSdata.new()
htfadd732.settings                 := SettingsHTFadd732
htfadd732.candles                  := candlesadd732
htfadd732.bosdata                  := bosdataadd732
var CandleSet htfadd733                     = CandleSet.new()
var CandleSettings SettingsHTFadd733        = CandleSettings.new(htf="733", max_memory=3, htfint=733)
var Candle[] candlesadd733                  = array.new<Candle>(0)
var BOSdata bosdataadd733                   = BOSdata.new()
htfadd733.settings                 := SettingsHTFadd733
htfadd733.candles                  := candlesadd733
htfadd733.bosdata                  := bosdataadd733
var CandleSet htfadd734                     = CandleSet.new()
var CandleSettings SettingsHTFadd734        = CandleSettings.new(htf="734", max_memory=3, htfint=734)
var Candle[] candlesadd734                  = array.new<Candle>(0)
var BOSdata bosdataadd734                   = BOSdata.new()
htfadd734.settings                 := SettingsHTFadd734
htfadd734.candles                  := candlesadd734
htfadd734.bosdata                  := bosdataadd734
var CandleSet htfadd735                     = CandleSet.new()
var CandleSettings SettingsHTFadd735        = CandleSettings.new(htf="735", max_memory=3, htfint=735)
var Candle[] candlesadd735                  = array.new<Candle>(0)
var BOSdata bosdataadd735                   = BOSdata.new()
htfadd735.settings                 := SettingsHTFadd735
htfadd735.candles                  := candlesadd735
htfadd735.bosdata                  := bosdataadd735
var CandleSet htfadd736                     = CandleSet.new()
var CandleSettings SettingsHTFadd736        = CandleSettings.new(htf="736", max_memory=3, htfint=736)
var Candle[] candlesadd736                  = array.new<Candle>(0)
var BOSdata bosdataadd736                   = BOSdata.new()
htfadd736.settings                 := SettingsHTFadd736
htfadd736.candles                  := candlesadd736
htfadd736.bosdata                  := bosdataadd736
var CandleSet htfadd737                     = CandleSet.new()
var CandleSettings SettingsHTFadd737        = CandleSettings.new(htf="737", max_memory=3, htfint=737)
var Candle[] candlesadd737                  = array.new<Candle>(0)
var BOSdata bosdataadd737                   = BOSdata.new()
htfadd737.settings                 := SettingsHTFadd737
htfadd737.candles                  := candlesadd737
htfadd737.bosdata                  := bosdataadd737
var CandleSet htfadd738                     = CandleSet.new()
var CandleSettings SettingsHTFadd738        = CandleSettings.new(htf="738", max_memory=3, htfint=738)
var Candle[] candlesadd738                  = array.new<Candle>(0)
var BOSdata bosdataadd738                   = BOSdata.new()
htfadd738.settings                 := SettingsHTFadd738
htfadd738.candles                  := candlesadd738
htfadd738.bosdata                  := bosdataadd738
var CandleSet htfadd739                     = CandleSet.new()
var CandleSettings SettingsHTFadd739        = CandleSettings.new(htf="739", max_memory=3, htfint=739)
var Candle[] candlesadd739                  = array.new<Candle>(0)
var BOSdata bosdataadd739                   = BOSdata.new()
htfadd739.settings                 := SettingsHTFadd739
htfadd739.candles                  := candlesadd739
htfadd739.bosdata                  := bosdataadd739
var CandleSet htfadd740                     = CandleSet.new()
var CandleSettings SettingsHTFadd740        = CandleSettings.new(htf="740", max_memory=3, htfint=740)
var Candle[] candlesadd740                  = array.new<Candle>(0)
var BOSdata bosdataadd740                   = BOSdata.new()
htfadd740.settings                 := SettingsHTFadd740
htfadd740.candles                  := candlesadd740
htfadd740.bosdata                  := bosdataadd740
var CandleSet htfadd741                     = CandleSet.new()
var CandleSettings SettingsHTFadd741        = CandleSettings.new(htf="741", max_memory=3, htfint=741)
var Candle[] candlesadd741                  = array.new<Candle>(0)
var BOSdata bosdataadd741                   = BOSdata.new()
htfadd741.settings                 := SettingsHTFadd741
htfadd741.candles                  := candlesadd741
htfadd741.bosdata                  := bosdataadd741
var CandleSet htfadd742                     = CandleSet.new()
var CandleSettings SettingsHTFadd742        = CandleSettings.new(htf="742", max_memory=3, htfint=742)
var Candle[] candlesadd742                  = array.new<Candle>(0)
var BOSdata bosdataadd742                   = BOSdata.new()
htfadd742.settings                 := SettingsHTFadd742
htfadd742.candles                  := candlesadd742
htfadd742.bosdata                  := bosdataadd742
var CandleSet htfadd743                     = CandleSet.new()
var CandleSettings SettingsHTFadd743        = CandleSettings.new(htf="743", max_memory=3, htfint=743)
var Candle[] candlesadd743                  = array.new<Candle>(0)
var BOSdata bosdataadd743                   = BOSdata.new()
htfadd743.settings                 := SettingsHTFadd743
htfadd743.candles                  := candlesadd743
htfadd743.bosdata                  := bosdataadd743
var CandleSet htfadd744                     = CandleSet.new()
var CandleSettings SettingsHTFadd744        = CandleSettings.new(htf="744", max_memory=3, htfint=744)
var Candle[] candlesadd744                  = array.new<Candle>(0)
var BOSdata bosdataadd744                   = BOSdata.new()
htfadd744.settings                 := SettingsHTFadd744
htfadd744.candles                  := candlesadd744
htfadd744.bosdata                  := bosdataadd744
var CandleSet htfadd745                     = CandleSet.new()
var CandleSettings SettingsHTFadd745        = CandleSettings.new(htf="745", max_memory=3, htfint=745)
var Candle[] candlesadd745                  = array.new<Candle>(0)
var BOSdata bosdataadd745                   = BOSdata.new()
htfadd745.settings                 := SettingsHTFadd745
htfadd745.candles                  := candlesadd745
htfadd745.bosdata                  := bosdataadd745
var CandleSet htfadd746                     = CandleSet.new()
var CandleSettings SettingsHTFadd746        = CandleSettings.new(htf="746", max_memory=3, htfint=746)
var Candle[] candlesadd746                  = array.new<Candle>(0)
var BOSdata bosdataadd746                   = BOSdata.new()
htfadd746.settings                 := SettingsHTFadd746
htfadd746.candles                  := candlesadd746
htfadd746.bosdata                  := bosdataadd746
var CandleSet htfadd747                     = CandleSet.new()
var CandleSettings SettingsHTFadd747        = CandleSettings.new(htf="747", max_memory=3, htfint=747)
var Candle[] candlesadd747                  = array.new<Candle>(0)
var BOSdata bosdataadd747                   = BOSdata.new()
htfadd747.settings                 := SettingsHTFadd747
htfadd747.candles                  := candlesadd747
htfadd747.bosdata                  := bosdataadd747
var CandleSet htfadd748                     = CandleSet.new()
var CandleSettings SettingsHTFadd748        = CandleSettings.new(htf="748", max_memory=3, htfint=748)
var Candle[] candlesadd748                  = array.new<Candle>(0)
var BOSdata bosdataadd748                   = BOSdata.new()
htfadd748.settings                 := SettingsHTFadd748
htfadd748.candles                  := candlesadd748
htfadd748.bosdata                  := bosdataadd748
var CandleSet htfadd749                     = CandleSet.new()
var CandleSettings SettingsHTFadd749        = CandleSettings.new(htf="749", max_memory=3, htfint=749)
var Candle[] candlesadd749                  = array.new<Candle>(0)
var BOSdata bosdataadd749                   = BOSdata.new()
htfadd749.settings                 := SettingsHTFadd749
htfadd749.candles                  := candlesadd749
htfadd749.bosdata                  := bosdataadd749
var CandleSet htfadd750                     = CandleSet.new()
var CandleSettings SettingsHTFadd750        = CandleSettings.new(htf="750", max_memory=3, htfint=750)
var Candle[] candlesadd750                  = array.new<Candle>(0)
var BOSdata bosdataadd750                   = BOSdata.new()
htfadd750.settings                 := SettingsHTFadd750
htfadd750.candles                  := candlesadd750
htfadd750.bosdata                  := bosdataadd750
var CandleSet htfadd751                     = CandleSet.new()
var CandleSettings SettingsHTFadd751        = CandleSettings.new(htf="751", max_memory=3, htfint=751)
var Candle[] candlesadd751                  = array.new<Candle>(0)
var BOSdata bosdataadd751                   = BOSdata.new()
htfadd751.settings                 := SettingsHTFadd751
htfadd751.candles                  := candlesadd751
htfadd751.bosdata                  := bosdataadd751
var CandleSet htfadd752                     = CandleSet.new()
var CandleSettings SettingsHTFadd752        = CandleSettings.new(htf="752", max_memory=3, htfint=752)
var Candle[] candlesadd752                  = array.new<Candle>(0)
var BOSdata bosdataadd752                   = BOSdata.new()
htfadd752.settings                 := SettingsHTFadd752
htfadd752.candles                  := candlesadd752
htfadd752.bosdata                  := bosdataadd752
var CandleSet htfadd753                     = CandleSet.new()
var CandleSettings SettingsHTFadd753        = CandleSettings.new(htf="753", max_memory=3, htfint=753)
var Candle[] candlesadd753                  = array.new<Candle>(0)
var BOSdata bosdataadd753                   = BOSdata.new()
htfadd753.settings                 := SettingsHTFadd753
htfadd753.candles                  := candlesadd753
htfadd753.bosdata                  := bosdataadd753
var CandleSet htfadd754                     = CandleSet.new()
var CandleSettings SettingsHTFadd754        = CandleSettings.new(htf="754", max_memory=3, htfint=754)
var Candle[] candlesadd754                  = array.new<Candle>(0)
var BOSdata bosdataadd754                   = BOSdata.new()
htfadd754.settings                 := SettingsHTFadd754
htfadd754.candles                  := candlesadd754
htfadd754.bosdata                  := bosdataadd754
var CandleSet htfadd755                     = CandleSet.new()
var CandleSettings SettingsHTFadd755        = CandleSettings.new(htf="755", max_memory=3, htfint=755)
var Candle[] candlesadd755                  = array.new<Candle>(0)
var BOSdata bosdataadd755                   = BOSdata.new()
htfadd755.settings                 := SettingsHTFadd755
htfadd755.candles                  := candlesadd755
htfadd755.bosdata                  := bosdataadd755
var CandleSet htfadd756                     = CandleSet.new()
var CandleSettings SettingsHTFadd756        = CandleSettings.new(htf="756", max_memory=3, htfint=756)
var Candle[] candlesadd756                  = array.new<Candle>(0)
var BOSdata bosdataadd756                   = BOSdata.new()
htfadd756.settings                 := SettingsHTFadd756
htfadd756.candles                  := candlesadd756
htfadd756.bosdata                  := bosdataadd756
var CandleSet htfadd757                     = CandleSet.new()
var CandleSettings SettingsHTFadd757        = CandleSettings.new(htf="757", max_memory=3, htfint=757)
var Candle[] candlesadd757                  = array.new<Candle>(0)
var BOSdata bosdataadd757                   = BOSdata.new()
htfadd757.settings                 := SettingsHTFadd757
htfadd757.candles                  := candlesadd757
htfadd757.bosdata                  := bosdataadd757
var CandleSet htfadd758                     = CandleSet.new()
var CandleSettings SettingsHTFadd758        = CandleSettings.new(htf="758", max_memory=3, htfint=758)
var Candle[] candlesadd758                  = array.new<Candle>(0)
var BOSdata bosdataadd758                   = BOSdata.new()
htfadd758.settings                 := SettingsHTFadd758
htfadd758.candles                  := candlesadd758
htfadd758.bosdata                  := bosdataadd758
var CandleSet htfadd759                     = CandleSet.new()
var CandleSettings SettingsHTFadd759        = CandleSettings.new(htf="759", max_memory=3, htfint=759)
var Candle[] candlesadd759                  = array.new<Candle>(0)
var BOSdata bosdataadd759                   = BOSdata.new()
htfadd759.settings                 := SettingsHTFadd759
htfadd759.candles                  := candlesadd759
htfadd759.bosdata                  := bosdataadd759
var CandleSet htfadd760                     = CandleSet.new()
var CandleSettings SettingsHTFadd760        = CandleSettings.new(htf="760", max_memory=3, htfint=760)
var Candle[] candlesadd760                  = array.new<Candle>(0)
var BOSdata bosdataadd760                   = BOSdata.new()
htfadd760.settings                 := SettingsHTFadd760
htfadd760.candles                  := candlesadd760
htfadd760.bosdata                  := bosdataadd760
var CandleSet htfadd761                     = CandleSet.new()
var CandleSettings SettingsHTFadd761        = CandleSettings.new(htf="761", max_memory=3, htfint=761)
var Candle[] candlesadd761                  = array.new<Candle>(0)
var BOSdata bosdataadd761                   = BOSdata.new()
htfadd761.settings                 := SettingsHTFadd761
htfadd761.candles                  := candlesadd761
htfadd761.bosdata                  := bosdataadd761
var CandleSet htfadd762                     = CandleSet.new()
var CandleSettings SettingsHTFadd762        = CandleSettings.new(htf="762", max_memory=3, htfint=762)
var Candle[] candlesadd762                  = array.new<Candle>(0)
var BOSdata bosdataadd762                   = BOSdata.new()
htfadd762.settings                 := SettingsHTFadd762
htfadd762.candles                  := candlesadd762
htfadd762.bosdata                  := bosdataadd762
var CandleSet htfadd763                     = CandleSet.new()
var CandleSettings SettingsHTFadd763        = CandleSettings.new(htf="763", max_memory=3, htfint=763)
var Candle[] candlesadd763                  = array.new<Candle>(0)
var BOSdata bosdataadd763                   = BOSdata.new()
htfadd763.settings                 := SettingsHTFadd763
htfadd763.candles                  := candlesadd763
htfadd763.bosdata                  := bosdataadd763
var CandleSet htfadd764                     = CandleSet.new()
var CandleSettings SettingsHTFadd764        = CandleSettings.new(htf="764", max_memory=3, htfint=764)
var Candle[] candlesadd764                  = array.new<Candle>(0)
var BOSdata bosdataadd764                   = BOSdata.new()
htfadd764.settings                 := SettingsHTFadd764
htfadd764.candles                  := candlesadd764
htfadd764.bosdata                  := bosdataadd764
var CandleSet htfadd765                     = CandleSet.new()
var CandleSettings SettingsHTFadd765        = CandleSettings.new(htf="765", max_memory=3, htfint=765)
var Candle[] candlesadd765                  = array.new<Candle>(0)
var BOSdata bosdataadd765                   = BOSdata.new()
htfadd765.settings                 := SettingsHTFadd765
htfadd765.candles                  := candlesadd765
htfadd765.bosdata                  := bosdataadd765
var CandleSet htfadd766                     = CandleSet.new()
var CandleSettings SettingsHTFadd766        = CandleSettings.new(htf="766", max_memory=3, htfint=766)
var Candle[] candlesadd766                  = array.new<Candle>(0)
var BOSdata bosdataadd766                   = BOSdata.new()
htfadd766.settings                 := SettingsHTFadd766
htfadd766.candles                  := candlesadd766
htfadd766.bosdata                  := bosdataadd766
var CandleSet htfadd767                     = CandleSet.new()
var CandleSettings SettingsHTFadd767        = CandleSettings.new(htf="767", max_memory=3, htfint=767)
var Candle[] candlesadd767                  = array.new<Candle>(0)
var BOSdata bosdataadd767                   = BOSdata.new()
htfadd767.settings                 := SettingsHTFadd767
htfadd767.candles                  := candlesadd767
htfadd767.bosdata                  := bosdataadd767
var CandleSet htfadd768                     = CandleSet.new()
var CandleSettings SettingsHTFadd768        = CandleSettings.new(htf="768", max_memory=3, htfint=768)
var Candle[] candlesadd768                  = array.new<Candle>(0)
var BOSdata bosdataadd768                   = BOSdata.new()
htfadd768.settings                 := SettingsHTFadd768
htfadd768.candles                  := candlesadd768
htfadd768.bosdata                  := bosdataadd768
var CandleSet htfadd769                     = CandleSet.new()
var CandleSettings SettingsHTFadd769        = CandleSettings.new(htf="769", max_memory=3, htfint=769)
var Candle[] candlesadd769                  = array.new<Candle>(0)
var BOSdata bosdataadd769                   = BOSdata.new()
htfadd769.settings                 := SettingsHTFadd769
htfadd769.candles                  := candlesadd769
htfadd769.bosdata                  := bosdataadd769
var CandleSet htfadd770                     = CandleSet.new()
var CandleSettings SettingsHTFadd770        = CandleSettings.new(htf="770", max_memory=3, htfint=770)
var Candle[] candlesadd770                  = array.new<Candle>(0)
var BOSdata bosdataadd770                   = BOSdata.new()
htfadd770.settings                 := SettingsHTFadd770
htfadd770.candles                  := candlesadd770
htfadd770.bosdata                  := bosdataadd770
var CandleSet htfadd771                     = CandleSet.new()
var CandleSettings SettingsHTFadd771        = CandleSettings.new(htf="771", max_memory=3, htfint=771)
var Candle[] candlesadd771                  = array.new<Candle>(0)
var BOSdata bosdataadd771                   = BOSdata.new()
htfadd771.settings                 := SettingsHTFadd771
htfadd771.candles                  := candlesadd771
htfadd771.bosdata                  := bosdataadd771
var CandleSet htfadd772                     = CandleSet.new()
var CandleSettings SettingsHTFadd772        = CandleSettings.new(htf="772", max_memory=3, htfint=772)
var Candle[] candlesadd772                  = array.new<Candle>(0)
var BOSdata bosdataadd772                   = BOSdata.new()
htfadd772.settings                 := SettingsHTFadd772
htfadd772.candles                  := candlesadd772
htfadd772.bosdata                  := bosdataadd772
var CandleSet htfadd773                     = CandleSet.new()
var CandleSettings SettingsHTFadd773        = CandleSettings.new(htf="773", max_memory=3, htfint=773)
var Candle[] candlesadd773                  = array.new<Candle>(0)
var BOSdata bosdataadd773                   = BOSdata.new()
htfadd773.settings                 := SettingsHTFadd773
htfadd773.candles                  := candlesadd773
htfadd773.bosdata                  := bosdataadd773
var CandleSet htfadd774                     = CandleSet.new()
var CandleSettings SettingsHTFadd774        = CandleSettings.new(htf="774", max_memory=3, htfint=774)
var Candle[] candlesadd774                  = array.new<Candle>(0)
var BOSdata bosdataadd774                   = BOSdata.new()
htfadd774.settings                 := SettingsHTFadd774
htfadd774.candles                  := candlesadd774
htfadd774.bosdata                  := bosdataadd774
var CandleSet htfadd775                     = CandleSet.new()
var CandleSettings SettingsHTFadd775        = CandleSettings.new(htf="775", max_memory=3, htfint=775)
var Candle[] candlesadd775                  = array.new<Candle>(0)
var BOSdata bosdataadd775                   = BOSdata.new()
htfadd775.settings                 := SettingsHTFadd775
htfadd775.candles                  := candlesadd775
htfadd775.bosdata                  := bosdataadd775
var CandleSet htfadd776                     = CandleSet.new()
var CandleSettings SettingsHTFadd776        = CandleSettings.new(htf="776", max_memory=3, htfint=776)
var Candle[] candlesadd776                  = array.new<Candle>(0)
var BOSdata bosdataadd776                   = BOSdata.new()
htfadd776.settings                 := SettingsHTFadd776
htfadd776.candles                  := candlesadd776
htfadd776.bosdata                  := bosdataadd776
var CandleSet htfadd777                     = CandleSet.new()
var CandleSettings SettingsHTFadd777        = CandleSettings.new(htf="777", max_memory=3, htfint=777)
var Candle[] candlesadd777                  = array.new<Candle>(0)
var BOSdata bosdataadd777                   = BOSdata.new()
htfadd777.settings                 := SettingsHTFadd777
htfadd777.candles                  := candlesadd777
htfadd777.bosdata                  := bosdataadd777
var CandleSet htfadd778                     = CandleSet.new()
var CandleSettings SettingsHTFadd778        = CandleSettings.new(htf="778", max_memory=3, htfint=778)
var Candle[] candlesadd778                  = array.new<Candle>(0)
var BOSdata bosdataadd778                   = BOSdata.new()
htfadd778.settings                 := SettingsHTFadd778
htfadd778.candles                  := candlesadd778
htfadd778.bosdata                  := bosdataadd778
var CandleSet htfadd779                     = CandleSet.new()
var CandleSettings SettingsHTFadd779        = CandleSettings.new(htf="779", max_memory=3, htfint=779)
var Candle[] candlesadd779                  = array.new<Candle>(0)
var BOSdata bosdataadd779                   = BOSdata.new()
htfadd779.settings                 := SettingsHTFadd779
htfadd779.candles                  := candlesadd779
htfadd779.bosdata                  := bosdataadd779
var CandleSet htfadd780                     = CandleSet.new()
var CandleSettings SettingsHTFadd780        = CandleSettings.new(htf="780", max_memory=3, htfint=780)
var Candle[] candlesadd780                  = array.new<Candle>(0)
var BOSdata bosdataadd780                   = BOSdata.new()
htfadd780.settings                 := SettingsHTFadd780
htfadd780.candles                  := candlesadd780
htfadd780.bosdata                  := bosdataadd780
var CandleSet htfadd781                     = CandleSet.new()
var CandleSettings SettingsHTFadd781        = CandleSettings.new(htf="781", max_memory=3, htfint=781)
var Candle[] candlesadd781                  = array.new<Candle>(0)
var BOSdata bosdataadd781                   = BOSdata.new()
htfadd781.settings                 := SettingsHTFadd781
htfadd781.candles                  := candlesadd781
htfadd781.bosdata                  := bosdataadd781
var CandleSet htfadd782                     = CandleSet.new()
var CandleSettings SettingsHTFadd782        = CandleSettings.new(htf="782", max_memory=3, htfint=782)
var Candle[] candlesadd782                  = array.new<Candle>(0)
var BOSdata bosdataadd782                   = BOSdata.new()
htfadd782.settings                 := SettingsHTFadd782
htfadd782.candles                  := candlesadd782
htfadd782.bosdata                  := bosdataadd782
var CandleSet htfadd783                     = CandleSet.new()
var CandleSettings SettingsHTFadd783        = CandleSettings.new(htf="783", max_memory=3, htfint=783)
var Candle[] candlesadd783                  = array.new<Candle>(0)
var BOSdata bosdataadd783                   = BOSdata.new()
htfadd783.settings                 := SettingsHTFadd783
htfadd783.candles                  := candlesadd783
htfadd783.bosdata                  := bosdataadd783
var CandleSet htfadd784                     = CandleSet.new()
var CandleSettings SettingsHTFadd784        = CandleSettings.new(htf="784", max_memory=3, htfint=784)
var Candle[] candlesadd784                  = array.new<Candle>(0)
var BOSdata bosdataadd784                   = BOSdata.new()
htfadd784.settings                 := SettingsHTFadd784
htfadd784.candles                  := candlesadd784
htfadd784.bosdata                  := bosdataadd784
var CandleSet htfadd785                     = CandleSet.new()
var CandleSettings SettingsHTFadd785        = CandleSettings.new(htf="785", max_memory=3, htfint=785)
var Candle[] candlesadd785                  = array.new<Candle>(0)
var BOSdata bosdataadd785                   = BOSdata.new()
htfadd785.settings                 := SettingsHTFadd785
htfadd785.candles                  := candlesadd785
htfadd785.bosdata                  := bosdataadd785
var CandleSet htfadd786                     = CandleSet.new()
var CandleSettings SettingsHTFadd786        = CandleSettings.new(htf="786", max_memory=3, htfint=786)
var Candle[] candlesadd786                  = array.new<Candle>(0)
var BOSdata bosdataadd786                   = BOSdata.new()
htfadd786.settings                 := SettingsHTFadd786
htfadd786.candles                  := candlesadd786
htfadd786.bosdata                  := bosdataadd786
var CandleSet htfadd787                     = CandleSet.new()
var CandleSettings SettingsHTFadd787        = CandleSettings.new(htf="787", max_memory=3, htfint=787)
var Candle[] candlesadd787                  = array.new<Candle>(0)
var BOSdata bosdataadd787                   = BOSdata.new()
htfadd787.settings                 := SettingsHTFadd787
htfadd787.candles                  := candlesadd787
htfadd787.bosdata                  := bosdataadd787
var CandleSet htfadd788                     = CandleSet.new()
var CandleSettings SettingsHTFadd788        = CandleSettings.new(htf="788", max_memory=3, htfint=788)
var Candle[] candlesadd788                  = array.new<Candle>(0)
var BOSdata bosdataadd788                   = BOSdata.new()
htfadd788.settings                 := SettingsHTFadd788
htfadd788.candles                  := candlesadd788
htfadd788.bosdata                  := bosdataadd788
var CandleSet htfadd789                     = CandleSet.new()
var CandleSettings SettingsHTFadd789        = CandleSettings.new(htf="789", max_memory=3, htfint=789)
var Candle[] candlesadd789                  = array.new<Candle>(0)
var BOSdata bosdataadd789                   = BOSdata.new()
htfadd789.settings                 := SettingsHTFadd789
htfadd789.candles                  := candlesadd789
htfadd789.bosdata                  := bosdataadd789
var CandleSet htfadd790                     = CandleSet.new()
var CandleSettings SettingsHTFadd790        = CandleSettings.new(htf="790", max_memory=3, htfint=790)
var Candle[] candlesadd790                  = array.new<Candle>(0)
var BOSdata bosdataadd790                   = BOSdata.new()
htfadd790.settings                 := SettingsHTFadd790
htfadd790.candles                  := candlesadd790
htfadd790.bosdata                  := bosdataadd790
var CandleSet htfadd791                     = CandleSet.new()
var CandleSettings SettingsHTFadd791        = CandleSettings.new(htf="791", max_memory=3, htfint=791)
var Candle[] candlesadd791                  = array.new<Candle>(0)
var BOSdata bosdataadd791                   = BOSdata.new()
htfadd791.settings                 := SettingsHTFadd791
htfadd791.candles                  := candlesadd791
htfadd791.bosdata                  := bosdataadd791
var CandleSet htfadd792                     = CandleSet.new()
var CandleSettings SettingsHTFadd792        = CandleSettings.new(htf="792", max_memory=3, htfint=792)
var Candle[] candlesadd792                  = array.new<Candle>(0)
var BOSdata bosdataadd792                   = BOSdata.new()
htfadd792.settings                 := SettingsHTFadd792
htfadd792.candles                  := candlesadd792
htfadd792.bosdata                  := bosdataadd792
var CandleSet htfadd793                     = CandleSet.new()
var CandleSettings SettingsHTFadd793        = CandleSettings.new(htf="793", max_memory=3, htfint=793)
var Candle[] candlesadd793                  = array.new<Candle>(0)
var BOSdata bosdataadd793                   = BOSdata.new()
htfadd793.settings                 := SettingsHTFadd793
htfadd793.candles                  := candlesadd793
htfadd793.bosdata                  := bosdataadd793
var CandleSet htfadd794                     = CandleSet.new()
var CandleSettings SettingsHTFadd794        = CandleSettings.new(htf="794", max_memory=3, htfint=794)
var Candle[] candlesadd794                  = array.new<Candle>(0)
var BOSdata bosdataadd794                   = BOSdata.new()
htfadd794.settings                 := SettingsHTFadd794
htfadd794.candles                  := candlesadd794
htfadd794.bosdata                  := bosdataadd794
var CandleSet htfadd795                     = CandleSet.new()
var CandleSettings SettingsHTFadd795        = CandleSettings.new(htf="795", max_memory=3, htfint=795)
var Candle[] candlesadd795                  = array.new<Candle>(0)
var BOSdata bosdataadd795                   = BOSdata.new()
htfadd795.settings                 := SettingsHTFadd795
htfadd795.candles                  := candlesadd795
htfadd795.bosdata                  := bosdataadd795
var CandleSet htfadd796                     = CandleSet.new()
var CandleSettings SettingsHTFadd796        = CandleSettings.new(htf="796", max_memory=3, htfint=796)
var Candle[] candlesadd796                  = array.new<Candle>(0)
var BOSdata bosdataadd796                   = BOSdata.new()
htfadd796.settings                 := SettingsHTFadd796
htfadd796.candles                  := candlesadd796
htfadd796.bosdata                  := bosdataadd796
var CandleSet htfadd797                     = CandleSet.new()
var CandleSettings SettingsHTFadd797        = CandleSettings.new(htf="797", max_memory=3, htfint=797)
var Candle[] candlesadd797                  = array.new<Candle>(0)
var BOSdata bosdataadd797                   = BOSdata.new()
htfadd797.settings                 := SettingsHTFadd797
htfadd797.candles                  := candlesadd797
htfadd797.bosdata                  := bosdataadd797
var CandleSet htfadd798                     = CandleSet.new()
var CandleSettings SettingsHTFadd798        = CandleSettings.new(htf="798", max_memory=3, htfint=798)
var Candle[] candlesadd798                  = array.new<Candle>(0)
var BOSdata bosdataadd798                   = BOSdata.new()
htfadd798.settings                 := SettingsHTFadd798
htfadd798.candles                  := candlesadd798
htfadd798.bosdata                  := bosdataadd798
var CandleSet htfadd799                     = CandleSet.new()
var CandleSettings SettingsHTFadd799        = CandleSettings.new(htf="799", max_memory=3, htfint=799)
var Candle[] candlesadd799                  = array.new<Candle>(0)
var BOSdata bosdataadd799                   = BOSdata.new()
htfadd799.settings                 := SettingsHTFadd799
htfadd799.candles                  := candlesadd799
htfadd799.bosdata                  := bosdataadd799
var CandleSet htfadd800                     = CandleSet.new()
var CandleSettings SettingsHTFadd800        = CandleSettings.new(htf="800", max_memory=3, htfint=800)
var Candle[] candlesadd800                  = array.new<Candle>(0)
var BOSdata bosdataadd800                   = BOSdata.new()
htfadd800.settings                 := SettingsHTFadd800
htfadd800.candles                  := candlesadd800
htfadd800.bosdata                  := bosdataadd800
var CandleSet htfadd801                     = CandleSet.new()
var CandleSettings SettingsHTFadd801        = CandleSettings.new(htf="801", max_memory=3, htfint=801)
var Candle[] candlesadd801                  = array.new<Candle>(0)
var BOSdata bosdataadd801                   = BOSdata.new()
htfadd801.settings                 := SettingsHTFadd801
htfadd801.candles                  := candlesadd801
htfadd801.bosdata                  := bosdataadd801
var CandleSet htfadd802                     = CandleSet.new()
var CandleSettings SettingsHTFadd802        = CandleSettings.new(htf="802", max_memory=3, htfint=802)
var Candle[] candlesadd802                  = array.new<Candle>(0)
var BOSdata bosdataadd802                   = BOSdata.new()
htfadd802.settings                 := SettingsHTFadd802
htfadd802.candles                  := candlesadd802
htfadd802.bosdata                  := bosdataadd802
var CandleSet htfadd803                     = CandleSet.new()
var CandleSettings SettingsHTFadd803        = CandleSettings.new(htf="803", max_memory=3, htfint=803)
var Candle[] candlesadd803                  = array.new<Candle>(0)
var BOSdata bosdataadd803                   = BOSdata.new()
htfadd803.settings                 := SettingsHTFadd803
htfadd803.candles                  := candlesadd803
htfadd803.bosdata                  := bosdataadd803
var CandleSet htfadd804                     = CandleSet.new()
var CandleSettings SettingsHTFadd804        = CandleSettings.new(htf="804", max_memory=3, htfint=804)
var Candle[] candlesadd804                  = array.new<Candle>(0)
var BOSdata bosdataadd804                   = BOSdata.new()
htfadd804.settings                 := SettingsHTFadd804
htfadd804.candles                  := candlesadd804
htfadd804.bosdata                  := bosdataadd804
var CandleSet htfadd805                     = CandleSet.new()
var CandleSettings SettingsHTFadd805        = CandleSettings.new(htf="805", max_memory=3, htfint=805)
var Candle[] candlesadd805                  = array.new<Candle>(0)
var BOSdata bosdataadd805                   = BOSdata.new()
htfadd805.settings                 := SettingsHTFadd805
htfadd805.candles                  := candlesadd805
htfadd805.bosdata                  := bosdataadd805
var CandleSet htfadd806                     = CandleSet.new()
var CandleSettings SettingsHTFadd806        = CandleSettings.new(htf="806", max_memory=3, htfint=806)
var Candle[] candlesadd806                  = array.new<Candle>(0)
var BOSdata bosdataadd806                   = BOSdata.new()
htfadd806.settings                 := SettingsHTFadd806
htfadd806.candles                  := candlesadd806
htfadd806.bosdata                  := bosdataadd806
var CandleSet htfadd807                     = CandleSet.new()
var CandleSettings SettingsHTFadd807        = CandleSettings.new(htf="807", max_memory=3, htfint=807)
var Candle[] candlesadd807                  = array.new<Candle>(0)
var BOSdata bosdataadd807                   = BOSdata.new()
htfadd807.settings                 := SettingsHTFadd807
htfadd807.candles                  := candlesadd807
htfadd807.bosdata                  := bosdataadd807
var CandleSet htfadd808                     = CandleSet.new()
var CandleSettings SettingsHTFadd808        = CandleSettings.new(htf="808", max_memory=3, htfint=808)
var Candle[] candlesadd808                  = array.new<Candle>(0)
var BOSdata bosdataadd808                   = BOSdata.new()
htfadd808.settings                 := SettingsHTFadd808
htfadd808.candles                  := candlesadd808
htfadd808.bosdata                  := bosdataadd808
var CandleSet htfadd809                     = CandleSet.new()
var CandleSettings SettingsHTFadd809        = CandleSettings.new(htf="809", max_memory=3, htfint=809)
var Candle[] candlesadd809                  = array.new<Candle>(0)
var BOSdata bosdataadd809                   = BOSdata.new()
htfadd809.settings                 := SettingsHTFadd809
htfadd809.candles                  := candlesadd809
htfadd809.bosdata                  := bosdataadd809
var CandleSet htfadd810                     = CandleSet.new()
var CandleSettings SettingsHTFadd810        = CandleSettings.new(htf="810", max_memory=3, htfint=810)
var Candle[] candlesadd810                  = array.new<Candle>(0)
var BOSdata bosdataadd810                   = BOSdata.new()
htfadd810.settings                 := SettingsHTFadd810
htfadd810.candles                  := candlesadd810
htfadd810.bosdata                  := bosdataadd810
var CandleSet htfadd811                     = CandleSet.new()
var CandleSettings SettingsHTFadd811        = CandleSettings.new(htf="811", max_memory=3, htfint=811)
var Candle[] candlesadd811                  = array.new<Candle>(0)
var BOSdata bosdataadd811                   = BOSdata.new()
htfadd811.settings                 := SettingsHTFadd811
htfadd811.candles                  := candlesadd811
htfadd811.bosdata                  := bosdataadd811
var CandleSet htfadd812                     = CandleSet.new()
var CandleSettings SettingsHTFadd812        = CandleSettings.new(htf="812", max_memory=3, htfint=812)
var Candle[] candlesadd812                  = array.new<Candle>(0)
var BOSdata bosdataadd812                   = BOSdata.new()
htfadd812.settings                 := SettingsHTFadd812
htfadd812.candles                  := candlesadd812
htfadd812.bosdata                  := bosdataadd812
var CandleSet htfadd813                     = CandleSet.new()
var CandleSettings SettingsHTFadd813        = CandleSettings.new(htf="813", max_memory=3, htfint=813)
var Candle[] candlesadd813                  = array.new<Candle>(0)
var BOSdata bosdataadd813                   = BOSdata.new()
htfadd813.settings                 := SettingsHTFadd813
htfadd813.candles                  := candlesadd813
htfadd813.bosdata                  := bosdataadd813
var CandleSet htfadd814                     = CandleSet.new()
var CandleSettings SettingsHTFadd814        = CandleSettings.new(htf="814", max_memory=3, htfint=814)
var Candle[] candlesadd814                  = array.new<Candle>(0)
var BOSdata bosdataadd814                   = BOSdata.new()
htfadd814.settings                 := SettingsHTFadd814
htfadd814.candles                  := candlesadd814
htfadd814.bosdata                  := bosdataadd814
var CandleSet htfadd815                     = CandleSet.new()
var CandleSettings SettingsHTFadd815        = CandleSettings.new(htf="815", max_memory=3, htfint=815)
var Candle[] candlesadd815                  = array.new<Candle>(0)
var BOSdata bosdataadd815                   = BOSdata.new()
htfadd815.settings                 := SettingsHTFadd815
htfadd815.candles                  := candlesadd815
htfadd815.bosdata                  := bosdataadd815
var CandleSet htfadd816                     = CandleSet.new()
var CandleSettings SettingsHTFadd816        = CandleSettings.new(htf="816", max_memory=3, htfint=816)
var Candle[] candlesadd816                  = array.new<Candle>(0)
var BOSdata bosdataadd816                   = BOSdata.new()
htfadd816.settings                 := SettingsHTFadd816
htfadd816.candles                  := candlesadd816
htfadd816.bosdata                  := bosdataadd816
var CandleSet htfadd817                     = CandleSet.new()
var CandleSettings SettingsHTFadd817        = CandleSettings.new(htf="817", max_memory=3, htfint=817)
var Candle[] candlesadd817                  = array.new<Candle>(0)
var BOSdata bosdataadd817                   = BOSdata.new()
htfadd817.settings                 := SettingsHTFadd817
htfadd817.candles                  := candlesadd817
htfadd817.bosdata                  := bosdataadd817
var CandleSet htfadd818                     = CandleSet.new()
var CandleSettings SettingsHTFadd818        = CandleSettings.new(htf="818", max_memory=3, htfint=818)
var Candle[] candlesadd818                  = array.new<Candle>(0)
var BOSdata bosdataadd818                   = BOSdata.new()
htfadd818.settings                 := SettingsHTFadd818
htfadd818.candles                  := candlesadd818
htfadd818.bosdata                  := bosdataadd818
var CandleSet htfadd819                     = CandleSet.new()
var CandleSettings SettingsHTFadd819        = CandleSettings.new(htf="819", max_memory=3, htfint=819)
var Candle[] candlesadd819                  = array.new<Candle>(0)
var BOSdata bosdataadd819                   = BOSdata.new()
htfadd819.settings                 := SettingsHTFadd819
htfadd819.candles                  := candlesadd819
htfadd819.bosdata                  := bosdataadd819
var CandleSet htfadd820                     = CandleSet.new()
var CandleSettings SettingsHTFadd820        = CandleSettings.new(htf="820", max_memory=3, htfint=820)
var Candle[] candlesadd820                  = array.new<Candle>(0)
var BOSdata bosdataadd820                   = BOSdata.new()
htfadd820.settings                 := SettingsHTFadd820
htfadd820.candles                  := candlesadd820
htfadd820.bosdata                  := bosdataadd820
var CandleSet htfadd821                     = CandleSet.new()
var CandleSettings SettingsHTFadd821        = CandleSettings.new(htf="821", max_memory=3, htfint=821)
var Candle[] candlesadd821                  = array.new<Candle>(0)
var BOSdata bosdataadd821                   = BOSdata.new()
htfadd821.settings                 := SettingsHTFadd821
htfadd821.candles                  := candlesadd821
htfadd821.bosdata                  := bosdataadd821
var CandleSet htfadd822                     = CandleSet.new()
var CandleSettings SettingsHTFadd822        = CandleSettings.new(htf="822", max_memory=3, htfint=822)
var Candle[] candlesadd822                  = array.new<Candle>(0)
var BOSdata bosdataadd822                   = BOSdata.new()
htfadd822.settings                 := SettingsHTFadd822
htfadd822.candles                  := candlesadd822
htfadd822.bosdata                  := bosdataadd822
var CandleSet htfadd823                     = CandleSet.new()
var CandleSettings SettingsHTFadd823        = CandleSettings.new(htf="823", max_memory=3, htfint=823)
var Candle[] candlesadd823                  = array.new<Candle>(0)
var BOSdata bosdataadd823                   = BOSdata.new()
htfadd823.settings                 := SettingsHTFadd823
htfadd823.candles                  := candlesadd823
htfadd823.bosdata                  := bosdataadd823
var CandleSet htfadd824                     = CandleSet.new()
var CandleSettings SettingsHTFadd824        = CandleSettings.new(htf="824", max_memory=3, htfint=824)
var Candle[] candlesadd824                  = array.new<Candle>(0)
var BOSdata bosdataadd824                   = BOSdata.new()
htfadd824.settings                 := SettingsHTFadd824
htfadd824.candles                  := candlesadd824
htfadd824.bosdata                  := bosdataadd824
var CandleSet htfadd825                     = CandleSet.new()
var CandleSettings SettingsHTFadd825        = CandleSettings.new(htf="825", max_memory=3, htfint=825)
var Candle[] candlesadd825                  = array.new<Candle>(0)
var BOSdata bosdataadd825                   = BOSdata.new()
htfadd825.settings                 := SettingsHTFadd825
htfadd825.candles                  := candlesadd825
htfadd825.bosdata                  := bosdataadd825
var CandleSet htfadd826                     = CandleSet.new()
var CandleSettings SettingsHTFadd826        = CandleSettings.new(htf="826", max_memory=3, htfint=826)
var Candle[] candlesadd826                  = array.new<Candle>(0)
var BOSdata bosdataadd826                   = BOSdata.new()
htfadd826.settings                 := SettingsHTFadd826
htfadd826.candles                  := candlesadd826
htfadd826.bosdata                  := bosdataadd826
var CandleSet htfadd827                     = CandleSet.new()
var CandleSettings SettingsHTFadd827        = CandleSettings.new(htf="827", max_memory=3, htfint=827)
var Candle[] candlesadd827                  = array.new<Candle>(0)
var BOSdata bosdataadd827                   = BOSdata.new()
htfadd827.settings                 := SettingsHTFadd827
htfadd827.candles                  := candlesadd827
htfadd827.bosdata                  := bosdataadd827
var CandleSet htfadd828                     = CandleSet.new()
var CandleSettings SettingsHTFadd828        = CandleSettings.new(htf="828", max_memory=3, htfint=828)
var Candle[] candlesadd828                  = array.new<Candle>(0)
var BOSdata bosdataadd828                   = BOSdata.new()
htfadd828.settings                 := SettingsHTFadd828
htfadd828.candles                  := candlesadd828
htfadd828.bosdata                  := bosdataadd828
var CandleSet htfadd829                     = CandleSet.new()
var CandleSettings SettingsHTFadd829        = CandleSettings.new(htf="829", max_memory=3, htfint=829)
var Candle[] candlesadd829                  = array.new<Candle>(0)
var BOSdata bosdataadd829                   = BOSdata.new()
htfadd829.settings                 := SettingsHTFadd829
htfadd829.candles                  := candlesadd829
htfadd829.bosdata                  := bosdataadd829
var CandleSet htfadd830                     = CandleSet.new()
var CandleSettings SettingsHTFadd830        = CandleSettings.new(htf="830", max_memory=3, htfint=830)
var Candle[] candlesadd830                  = array.new<Candle>(0)
var BOSdata bosdataadd830                   = BOSdata.new()
htfadd830.settings                 := SettingsHTFadd830
htfadd830.candles                  := candlesadd830
htfadd830.bosdata                  := bosdataadd830
var CandleSet htfadd831                     = CandleSet.new()
var CandleSettings SettingsHTFadd831        = CandleSettings.new(htf="831", max_memory=3, htfint=831)
var Candle[] candlesadd831                  = array.new<Candle>(0)
var BOSdata bosdataadd831                   = BOSdata.new()
htfadd831.settings                 := SettingsHTFadd831
htfadd831.candles                  := candlesadd831
htfadd831.bosdata                  := bosdataadd831
var CandleSet htfadd832                     = CandleSet.new()
var CandleSettings SettingsHTFadd832        = CandleSettings.new(htf="832", max_memory=3, htfint=832)
var Candle[] candlesadd832                  = array.new<Candle>(0)
var BOSdata bosdataadd832                   = BOSdata.new()
htfadd832.settings                 := SettingsHTFadd832
htfadd832.candles                  := candlesadd832
htfadd832.bosdata                  := bosdataadd832
var CandleSet htfadd833                     = CandleSet.new()
var CandleSettings SettingsHTFadd833        = CandleSettings.new(htf="833", max_memory=3, htfint=833)
var Candle[] candlesadd833                  = array.new<Candle>(0)
var BOSdata bosdataadd833                   = BOSdata.new()
htfadd833.settings                 := SettingsHTFadd833
htfadd833.candles                  := candlesadd833
htfadd833.bosdata                  := bosdataadd833
var CandleSet htfadd834                     = CandleSet.new()
var CandleSettings SettingsHTFadd834        = CandleSettings.new(htf="834", max_memory=3, htfint=834)
var Candle[] candlesadd834                  = array.new<Candle>(0)
var BOSdata bosdataadd834                   = BOSdata.new()
htfadd834.settings                 := SettingsHTFadd834
htfadd834.candles                  := candlesadd834
htfadd834.bosdata                  := bosdataadd834
var CandleSet htfadd835                     = CandleSet.new()
var CandleSettings SettingsHTFadd835        = CandleSettings.new(htf="835", max_memory=3, htfint=835)
var Candle[] candlesadd835                  = array.new<Candle>(0)
var BOSdata bosdataadd835                   = BOSdata.new()
htfadd835.settings                 := SettingsHTFadd835
htfadd835.candles                  := candlesadd835
htfadd835.bosdata                  := bosdataadd835
var CandleSet htfadd836                     = CandleSet.new()
var CandleSettings SettingsHTFadd836        = CandleSettings.new(htf="836", max_memory=3, htfint=836)
var Candle[] candlesadd836                  = array.new<Candle>(0)
var BOSdata bosdataadd836                   = BOSdata.new()
htfadd836.settings                 := SettingsHTFadd836
htfadd836.candles                  := candlesadd836
htfadd836.bosdata                  := bosdataadd836
var CandleSet htfadd837                     = CandleSet.new()
var CandleSettings SettingsHTFadd837        = CandleSettings.new(htf="837", max_memory=3, htfint=837)
var Candle[] candlesadd837                  = array.new<Candle>(0)
var BOSdata bosdataadd837                   = BOSdata.new()
htfadd837.settings                 := SettingsHTFadd837
htfadd837.candles                  := candlesadd837
htfadd837.bosdata                  := bosdataadd837
var CandleSet htfadd838                     = CandleSet.new()
var CandleSettings SettingsHTFadd838        = CandleSettings.new(htf="838", max_memory=3, htfint=838)
var Candle[] candlesadd838                  = array.new<Candle>(0)
var BOSdata bosdataadd838                   = BOSdata.new()
htfadd838.settings                 := SettingsHTFadd838
htfadd838.candles                  := candlesadd838
htfadd838.bosdata                  := bosdataadd838
var CandleSet htfadd839                     = CandleSet.new()
var CandleSettings SettingsHTFadd839        = CandleSettings.new(htf="839", max_memory=3, htfint=839)
var Candle[] candlesadd839                  = array.new<Candle>(0)
var BOSdata bosdataadd839                   = BOSdata.new()
htfadd839.settings                 := SettingsHTFadd839
htfadd839.candles                  := candlesadd839
htfadd839.bosdata                  := bosdataadd839
var CandleSet htfadd840                     = CandleSet.new()
var CandleSettings SettingsHTFadd840        = CandleSettings.new(htf="840", max_memory=3, htfint=840)
var Candle[] candlesadd840                  = array.new<Candle>(0)
var BOSdata bosdataadd840                   = BOSdata.new()
htfadd840.settings                 := SettingsHTFadd840
htfadd840.candles                  := candlesadd840
htfadd840.bosdata                  := bosdataadd840
var CandleSet htfadd841                     = CandleSet.new()
var CandleSettings SettingsHTFadd841        = CandleSettings.new(htf="841", max_memory=3, htfint=841)
var Candle[] candlesadd841                  = array.new<Candle>(0)
var BOSdata bosdataadd841                   = BOSdata.new()
htfadd841.settings                 := SettingsHTFadd841
htfadd841.candles                  := candlesadd841
htfadd841.bosdata                  := bosdataadd841
var CandleSet htfadd842                     = CandleSet.new()
var CandleSettings SettingsHTFadd842        = CandleSettings.new(htf="842", max_memory=3, htfint=842)
var Candle[] candlesadd842                  = array.new<Candle>(0)
var BOSdata bosdataadd842                   = BOSdata.new()
htfadd842.settings                 := SettingsHTFadd842
htfadd842.candles                  := candlesadd842
htfadd842.bosdata                  := bosdataadd842
var CandleSet htfadd843                     = CandleSet.new()
var CandleSettings SettingsHTFadd843        = CandleSettings.new(htf="843", max_memory=3, htfint=843)
var Candle[] candlesadd843                  = array.new<Candle>(0)
var BOSdata bosdataadd843                   = BOSdata.new()
htfadd843.settings                 := SettingsHTFadd843
htfadd843.candles                  := candlesadd843
htfadd843.bosdata                  := bosdataadd843
var CandleSet htfadd844                     = CandleSet.new()
var CandleSettings SettingsHTFadd844        = CandleSettings.new(htf="844", max_memory=3, htfint=844)
var Candle[] candlesadd844                  = array.new<Candle>(0)
var BOSdata bosdataadd844                   = BOSdata.new()
htfadd844.settings                 := SettingsHTFadd844
htfadd844.candles                  := candlesadd844
htfadd844.bosdata                  := bosdataadd844
var CandleSet htfadd845                     = CandleSet.new()
var CandleSettings SettingsHTFadd845        = CandleSettings.new(htf="845", max_memory=3, htfint=845)
var Candle[] candlesadd845                  = array.new<Candle>(0)
var BOSdata bosdataadd845                   = BOSdata.new()
htfadd845.settings                 := SettingsHTFadd845
htfadd845.candles                  := candlesadd845
htfadd845.bosdata                  := bosdataadd845
var CandleSet htfadd846                     = CandleSet.new()
var CandleSettings SettingsHTFadd846        = CandleSettings.new(htf="846", max_memory=3, htfint=846)
var Candle[] candlesadd846                  = array.new<Candle>(0)
var BOSdata bosdataadd846                   = BOSdata.new()
htfadd846.settings                 := SettingsHTFadd846
htfadd846.candles                  := candlesadd846
htfadd846.bosdata                  := bosdataadd846
var CandleSet htfadd847                     = CandleSet.new()
var CandleSettings SettingsHTFadd847        = CandleSettings.new(htf="847", max_memory=3, htfint=847)
var Candle[] candlesadd847                  = array.new<Candle>(0)
var BOSdata bosdataadd847                   = BOSdata.new()
htfadd847.settings                 := SettingsHTFadd847
htfadd847.candles                  := candlesadd847
htfadd847.bosdata                  := bosdataadd847
var CandleSet htfadd848                     = CandleSet.new()
var CandleSettings SettingsHTFadd848        = CandleSettings.new(htf="848", max_memory=3, htfint=848)
var Candle[] candlesadd848                  = array.new<Candle>(0)
var BOSdata bosdataadd848                   = BOSdata.new()
htfadd848.settings                 := SettingsHTFadd848
htfadd848.candles                  := candlesadd848
htfadd848.bosdata                  := bosdataadd848
var CandleSet htfadd849                     = CandleSet.new()
var CandleSettings SettingsHTFadd849        = CandleSettings.new(htf="849", max_memory=3, htfint=849)
var Candle[] candlesadd849                  = array.new<Candle>(0)
var BOSdata bosdataadd849                   = BOSdata.new()
htfadd849.settings                 := SettingsHTFadd849
htfadd849.candles                  := candlesadd849
htfadd849.bosdata                  := bosdataadd849
var CandleSet htfadd850                     = CandleSet.new()
var CandleSettings SettingsHTFadd850        = CandleSettings.new(htf="850", max_memory=3, htfint=850)
var Candle[] candlesadd850                  = array.new<Candle>(0)
var BOSdata bosdataadd850                   = BOSdata.new()
htfadd850.settings                 := SettingsHTFadd850
htfadd850.candles                  := candlesadd850
htfadd850.bosdata                  := bosdataadd850
var CandleSet htfadd851                     = CandleSet.new()
var CandleSettings SettingsHTFadd851        = CandleSettings.new(htf="851", max_memory=3, htfint=851)
var Candle[] candlesadd851                  = array.new<Candle>(0)
var BOSdata bosdataadd851                   = BOSdata.new()
htfadd851.settings                 := SettingsHTFadd851
htfadd851.candles                  := candlesadd851
htfadd851.bosdata                  := bosdataadd851
var CandleSet htfadd852                     = CandleSet.new()
var CandleSettings SettingsHTFadd852        = CandleSettings.new(htf="852", max_memory=3, htfint=852)
var Candle[] candlesadd852                  = array.new<Candle>(0)
var BOSdata bosdataadd852                   = BOSdata.new()
htfadd852.settings                 := SettingsHTFadd852
htfadd852.candles                  := candlesadd852
htfadd852.bosdata                  := bosdataadd852
var CandleSet htfadd853                     = CandleSet.new()
var CandleSettings SettingsHTFadd853        = CandleSettings.new(htf="853", max_memory=3, htfint=853)
var Candle[] candlesadd853                  = array.new<Candle>(0)
var BOSdata bosdataadd853                   = BOSdata.new()
htfadd853.settings                 := SettingsHTFadd853
htfadd853.candles                  := candlesadd853
htfadd853.bosdata                  := bosdataadd853
var CandleSet htfadd854                     = CandleSet.new()
var CandleSettings SettingsHTFadd854        = CandleSettings.new(htf="854", max_memory=3, htfint=854)
var Candle[] candlesadd854                  = array.new<Candle>(0)
var BOSdata bosdataadd854                   = BOSdata.new()
htfadd854.settings                 := SettingsHTFadd854
htfadd854.candles                  := candlesadd854
htfadd854.bosdata                  := bosdataadd854
var CandleSet htfadd855                     = CandleSet.new()
var CandleSettings SettingsHTFadd855        = CandleSettings.new(htf="855", max_memory=3, htfint=855)
var Candle[] candlesadd855                  = array.new<Candle>(0)
var BOSdata bosdataadd855                   = BOSdata.new()
htfadd855.settings                 := SettingsHTFadd855
htfadd855.candles                  := candlesadd855
htfadd855.bosdata                  := bosdataadd855
var CandleSet htfadd856                     = CandleSet.new()
var CandleSettings SettingsHTFadd856        = CandleSettings.new(htf="856", max_memory=3, htfint=856)
var Candle[] candlesadd856                  = array.new<Candle>(0)
var BOSdata bosdataadd856                   = BOSdata.new()
htfadd856.settings                 := SettingsHTFadd856
htfadd856.candles                  := candlesadd856
htfadd856.bosdata                  := bosdataadd856
var CandleSet htfadd857                     = CandleSet.new()
var CandleSettings SettingsHTFadd857        = CandleSettings.new(htf="857", max_memory=3, htfint=857)
var Candle[] candlesadd857                  = array.new<Candle>(0)
var BOSdata bosdataadd857                   = BOSdata.new()
htfadd857.settings                 := SettingsHTFadd857
htfadd857.candles                  := candlesadd857
htfadd857.bosdata                  := bosdataadd857
var CandleSet htfadd858                     = CandleSet.new()
var CandleSettings SettingsHTFadd858        = CandleSettings.new(htf="858", max_memory=3, htfint=858)
var Candle[] candlesadd858                  = array.new<Candle>(0)
var BOSdata bosdataadd858                   = BOSdata.new()
htfadd858.settings                 := SettingsHTFadd858
htfadd858.candles                  := candlesadd858
htfadd858.bosdata                  := bosdataadd858
var CandleSet htfadd859                     = CandleSet.new()
var CandleSettings SettingsHTFadd859        = CandleSettings.new(htf="859", max_memory=3, htfint=859)
var Candle[] candlesadd859                  = array.new<Candle>(0)
var BOSdata bosdataadd859                   = BOSdata.new()
htfadd859.settings                 := SettingsHTFadd859
htfadd859.candles                  := candlesadd859
htfadd859.bosdata                  := bosdataadd859
var CandleSet htfadd860                     = CandleSet.new()
var CandleSettings SettingsHTFadd860        = CandleSettings.new(htf="860", max_memory=3, htfint=860)
var Candle[] candlesadd860                  = array.new<Candle>(0)
var BOSdata bosdataadd860                   = BOSdata.new()
htfadd860.settings                 := SettingsHTFadd860
htfadd860.candles                  := candlesadd860
htfadd860.bosdata                  := bosdataadd860
var CandleSet htfadd861                     = CandleSet.new()
var CandleSettings SettingsHTFadd861        = CandleSettings.new(htf="861", max_memory=3, htfint=861)
var Candle[] candlesadd861                  = array.new<Candle>(0)
var BOSdata bosdataadd861                   = BOSdata.new()
htfadd861.settings                 := SettingsHTFadd861
htfadd861.candles                  := candlesadd861
htfadd861.bosdata                  := bosdataadd861
var CandleSet htfadd862                     = CandleSet.new()
var CandleSettings SettingsHTFadd862        = CandleSettings.new(htf="862", max_memory=3, htfint=862)
var Candle[] candlesadd862                  = array.new<Candle>(0)
var BOSdata bosdataadd862                   = BOSdata.new()
htfadd862.settings                 := SettingsHTFadd862
htfadd862.candles                  := candlesadd862
htfadd862.bosdata                  := bosdataadd862
var CandleSet htfadd863                     = CandleSet.new()
var CandleSettings SettingsHTFadd863        = CandleSettings.new(htf="863", max_memory=3, htfint=863)
var Candle[] candlesadd863                  = array.new<Candle>(0)
var BOSdata bosdataadd863                   = BOSdata.new()
htfadd863.settings                 := SettingsHTFadd863
htfadd863.candles                  := candlesadd863
htfadd863.bosdata                  := bosdataadd863
var CandleSet htfadd864                     = CandleSet.new()
var CandleSettings SettingsHTFadd864        = CandleSettings.new(htf="864", max_memory=3, htfint=864)
var Candle[] candlesadd864                  = array.new<Candle>(0)
var BOSdata bosdataadd864                   = BOSdata.new()
htfadd864.settings                 := SettingsHTFadd864
htfadd864.candles                  := candlesadd864
htfadd864.bosdata                  := bosdataadd864
var CandleSet htfadd865                     = CandleSet.new()
var CandleSettings SettingsHTFadd865        = CandleSettings.new(htf="865", max_memory=3, htfint=865)
var Candle[] candlesadd865                  = array.new<Candle>(0)
var BOSdata bosdataadd865                   = BOSdata.new()
htfadd865.settings                 := SettingsHTFadd865
htfadd865.candles                  := candlesadd865
htfadd865.bosdata                  := bosdataadd865
var CandleSet htfadd866                     = CandleSet.new()
var CandleSettings SettingsHTFadd866        = CandleSettings.new(htf="866", max_memory=3, htfint=866)
var Candle[] candlesadd866                  = array.new<Candle>(0)
var BOSdata bosdataadd866                   = BOSdata.new()
htfadd866.settings                 := SettingsHTFadd866
htfadd866.candles                  := candlesadd866
htfadd866.bosdata                  := bosdataadd866
var CandleSet htfadd867                     = CandleSet.new()
var CandleSettings SettingsHTFadd867        = CandleSettings.new(htf="867", max_memory=3, htfint=867)
var Candle[] candlesadd867                  = array.new<Candle>(0)
var BOSdata bosdataadd867                   = BOSdata.new()
htfadd867.settings                 := SettingsHTFadd867
htfadd867.candles                  := candlesadd867
htfadd867.bosdata                  := bosdataadd867
var CandleSet htfadd868                     = CandleSet.new()
var CandleSettings SettingsHTFadd868        = CandleSettings.new(htf="868", max_memory=3, htfint=868)
var Candle[] candlesadd868                  = array.new<Candle>(0)
var BOSdata bosdataadd868                   = BOSdata.new()
htfadd868.settings                 := SettingsHTFadd868
htfadd868.candles                  := candlesadd868
htfadd868.bosdata                  := bosdataadd868
var CandleSet htfadd869                     = CandleSet.new()
var CandleSettings SettingsHTFadd869        = CandleSettings.new(htf="869", max_memory=3, htfint=869)
var Candle[] candlesadd869                  = array.new<Candle>(0)
var BOSdata bosdataadd869                   = BOSdata.new()
htfadd869.settings                 := SettingsHTFadd869
htfadd869.candles                  := candlesadd869
htfadd869.bosdata                  := bosdataadd869
var CandleSet htfadd870                     = CandleSet.new()
var CandleSettings SettingsHTFadd870        = CandleSettings.new(htf="870", max_memory=3, htfint=870)
var Candle[] candlesadd870                  = array.new<Candle>(0)
var BOSdata bosdataadd870                   = BOSdata.new()
htfadd870.settings                 := SettingsHTFadd870
htfadd870.candles                  := candlesadd870
htfadd870.bosdata                  := bosdataadd870
var CandleSet htfadd871                     = CandleSet.new()
var CandleSettings SettingsHTFadd871        = CandleSettings.new(htf="871", max_memory=3, htfint=871)
var Candle[] candlesadd871                  = array.new<Candle>(0)
var BOSdata bosdataadd871                   = BOSdata.new()
htfadd871.settings                 := SettingsHTFadd871
htfadd871.candles                  := candlesadd871
htfadd871.bosdata                  := bosdataadd871
var CandleSet htfadd872                     = CandleSet.new()
var CandleSettings SettingsHTFadd872        = CandleSettings.new(htf="872", max_memory=3, htfint=872)
var Candle[] candlesadd872                  = array.new<Candle>(0)
var BOSdata bosdataadd872                   = BOSdata.new()
htfadd872.settings                 := SettingsHTFadd872
htfadd872.candles                  := candlesadd872
htfadd872.bosdata                  := bosdataadd872
var CandleSet htfadd873                     = CandleSet.new()
var CandleSettings SettingsHTFadd873        = CandleSettings.new(htf="873", max_memory=3, htfint=873)
var Candle[] candlesadd873                  = array.new<Candle>(0)
var BOSdata bosdataadd873                   = BOSdata.new()
htfadd873.settings                 := SettingsHTFadd873
htfadd873.candles                  := candlesadd873
htfadd873.bosdata                  := bosdataadd873
var CandleSet htfadd874                     = CandleSet.new()
var CandleSettings SettingsHTFadd874        = CandleSettings.new(htf="874", max_memory=3, htfint=874)
var Candle[] candlesadd874                  = array.new<Candle>(0)
var BOSdata bosdataadd874                   = BOSdata.new()
htfadd874.settings                 := SettingsHTFadd874
htfadd874.candles                  := candlesadd874
htfadd874.bosdata                  := bosdataadd874
var CandleSet htfadd875                     = CandleSet.new()
var CandleSettings SettingsHTFadd875        = CandleSettings.new(htf="875", max_memory=3, htfint=875)
var Candle[] candlesadd875                  = array.new<Candle>(0)
var BOSdata bosdataadd875                   = BOSdata.new()
htfadd875.settings                 := SettingsHTFadd875
htfadd875.candles                  := candlesadd875
htfadd875.bosdata                  := bosdataadd875
var CandleSet htfadd876                     = CandleSet.new()
var CandleSettings SettingsHTFadd876        = CandleSettings.new(htf="876", max_memory=3, htfint=876)
var Candle[] candlesadd876                  = array.new<Candle>(0)
var BOSdata bosdataadd876                   = BOSdata.new()
htfadd876.settings                 := SettingsHTFadd876
htfadd876.candles                  := candlesadd876
htfadd876.bosdata                  := bosdataadd876
var CandleSet htfadd877                     = CandleSet.new()
var CandleSettings SettingsHTFadd877        = CandleSettings.new(htf="877", max_memory=3, htfint=877)
var Candle[] candlesadd877                  = array.new<Candle>(0)
var BOSdata bosdataadd877                   = BOSdata.new()
htfadd877.settings                 := SettingsHTFadd877
htfadd877.candles                  := candlesadd877
htfadd877.bosdata                  := bosdataadd877
var CandleSet htfadd878                     = CandleSet.new()
var CandleSettings SettingsHTFadd878        = CandleSettings.new(htf="878", max_memory=3, htfint=878)
var Candle[] candlesadd878                  = array.new<Candle>(0)
var BOSdata bosdataadd878                   = BOSdata.new()
htfadd878.settings                 := SettingsHTFadd878
htfadd878.candles                  := candlesadd878
htfadd878.bosdata                  := bosdataadd878
var CandleSet htfadd879                     = CandleSet.new()
var CandleSettings SettingsHTFadd879        = CandleSettings.new(htf="879", max_memory=3, htfint=879)
var Candle[] candlesadd879                  = array.new<Candle>(0)
var BOSdata bosdataadd879                   = BOSdata.new()
htfadd879.settings                 := SettingsHTFadd879
htfadd879.candles                  := candlesadd879
htfadd879.bosdata                  := bosdataadd879
var CandleSet htfadd880                     = CandleSet.new()
var CandleSettings SettingsHTFadd880        = CandleSettings.new(htf="880", max_memory=3, htfint=880)
var Candle[] candlesadd880                  = array.new<Candle>(0)
var BOSdata bosdataadd880                   = BOSdata.new()
htfadd880.settings                 := SettingsHTFadd880
htfadd880.candles                  := candlesadd880
htfadd880.bosdata                  := bosdataadd880
var CandleSet htfadd881                     = CandleSet.new()
var CandleSettings SettingsHTFadd881        = CandleSettings.new(htf="881", max_memory=3, htfint=881)
var Candle[] candlesadd881                  = array.new<Candle>(0)
var BOSdata bosdataadd881                   = BOSdata.new()
htfadd881.settings                 := SettingsHTFadd881
htfadd881.candles                  := candlesadd881
htfadd881.bosdata                  := bosdataadd881
var CandleSet htfadd882                     = CandleSet.new()
var CandleSettings SettingsHTFadd882        = CandleSettings.new(htf="882", max_memory=3, htfint=882)
var Candle[] candlesadd882                  = array.new<Candle>(0)
var BOSdata bosdataadd882                   = BOSdata.new()
htfadd882.settings                 := SettingsHTFadd882
htfadd882.candles                  := candlesadd882
htfadd882.bosdata                  := bosdataadd882
var CandleSet htfadd883                     = CandleSet.new()
var CandleSettings SettingsHTFadd883        = CandleSettings.new(htf="883", max_memory=3, htfint=883)
var Candle[] candlesadd883                  = array.new<Candle>(0)
var BOSdata bosdataadd883                   = BOSdata.new()
htfadd883.settings                 := SettingsHTFadd883
htfadd883.candles                  := candlesadd883
htfadd883.bosdata                  := bosdataadd883
var CandleSet htfadd884                     = CandleSet.new()
var CandleSettings SettingsHTFadd884        = CandleSettings.new(htf="884", max_memory=3, htfint=884)
var Candle[] candlesadd884                  = array.new<Candle>(0)
var BOSdata bosdataadd884                   = BOSdata.new()
htfadd884.settings                 := SettingsHTFadd884
htfadd884.candles                  := candlesadd884
htfadd884.bosdata                  := bosdataadd884
var CandleSet htfadd885                     = CandleSet.new()
var CandleSettings SettingsHTFadd885        = CandleSettings.new(htf="885", max_memory=3, htfint=885)
var Candle[] candlesadd885                  = array.new<Candle>(0)
var BOSdata bosdataadd885                   = BOSdata.new()
htfadd885.settings                 := SettingsHTFadd885
htfadd885.candles                  := candlesadd885
htfadd885.bosdata                  := bosdataadd885
var CandleSet htfadd886                     = CandleSet.new()
var CandleSettings SettingsHTFadd886        = CandleSettings.new(htf="886", max_memory=3, htfint=886)
var Candle[] candlesadd886                  = array.new<Candle>(0)
var BOSdata bosdataadd886                   = BOSdata.new()
htfadd886.settings                 := SettingsHTFadd886
htfadd886.candles                  := candlesadd886
htfadd886.bosdata                  := bosdataadd886
var CandleSet htfadd887                     = CandleSet.new()
var CandleSettings SettingsHTFadd887        = CandleSettings.new(htf="887", max_memory=3, htfint=887)
var Candle[] candlesadd887                  = array.new<Candle>(0)
var BOSdata bosdataadd887                   = BOSdata.new()
htfadd887.settings                 := SettingsHTFadd887
htfadd887.candles                  := candlesadd887
htfadd887.bosdata                  := bosdataadd887
var CandleSet htfadd888                     = CandleSet.new()
var CandleSettings SettingsHTFadd888        = CandleSettings.new(htf="888", max_memory=3, htfint=888)
var Candle[] candlesadd888                  = array.new<Candle>(0)
var BOSdata bosdataadd888                   = BOSdata.new()
htfadd888.settings                 := SettingsHTFadd888
htfadd888.candles                  := candlesadd888
htfadd888.bosdata                  := bosdataadd888
var CandleSet htfadd889                     = CandleSet.new()
var CandleSettings SettingsHTFadd889        = CandleSettings.new(htf="889", max_memory=3, htfint=889)
var Candle[] candlesadd889                  = array.new<Candle>(0)
var BOSdata bosdataadd889                   = BOSdata.new()
htfadd889.settings                 := SettingsHTFadd889
htfadd889.candles                  := candlesadd889
htfadd889.bosdata                  := bosdataadd889
var CandleSet htfadd890                     = CandleSet.new()
var CandleSettings SettingsHTFadd890        = CandleSettings.new(htf="890", max_memory=3, htfint=890)
var Candle[] candlesadd890                  = array.new<Candle>(0)
var BOSdata bosdataadd890                   = BOSdata.new()
htfadd890.settings                 := SettingsHTFadd890
htfadd890.candles                  := candlesadd890
htfadd890.bosdata                  := bosdataadd890
var CandleSet htfadd891                     = CandleSet.new()
var CandleSettings SettingsHTFadd891        = CandleSettings.new(htf="891", max_memory=3, htfint=891)
var Candle[] candlesadd891                  = array.new<Candle>(0)
var BOSdata bosdataadd891                   = BOSdata.new()
htfadd891.settings                 := SettingsHTFadd891
htfadd891.candles                  := candlesadd891
htfadd891.bosdata                  := bosdataadd891
var CandleSet htfadd892                     = CandleSet.new()
var CandleSettings SettingsHTFadd892        = CandleSettings.new(htf="892", max_memory=3, htfint=892)
var Candle[] candlesadd892                  = array.new<Candle>(0)
var BOSdata bosdataadd892                   = BOSdata.new()
htfadd892.settings                 := SettingsHTFadd892
htfadd892.candles                  := candlesadd892
htfadd892.bosdata                  := bosdataadd892
var CandleSet htfadd893                     = CandleSet.new()
var CandleSettings SettingsHTFadd893        = CandleSettings.new(htf="893", max_memory=3, htfint=893)
var Candle[] candlesadd893                  = array.new<Candle>(0)
var BOSdata bosdataadd893                   = BOSdata.new()
htfadd893.settings                 := SettingsHTFadd893
htfadd893.candles                  := candlesadd893
htfadd893.bosdata                  := bosdataadd893
var CandleSet htfadd894                     = CandleSet.new()
var CandleSettings SettingsHTFadd894        = CandleSettings.new(htf="894", max_memory=3, htfint=894)
var Candle[] candlesadd894                  = array.new<Candle>(0)
var BOSdata bosdataadd894                   = BOSdata.new()
htfadd894.settings                 := SettingsHTFadd894
htfadd894.candles                  := candlesadd894
htfadd894.bosdata                  := bosdataadd894
var CandleSet htfadd895                     = CandleSet.new()
var CandleSettings SettingsHTFadd895        = CandleSettings.new(htf="895", max_memory=3, htfint=895)
var Candle[] candlesadd895                  = array.new<Candle>(0)
var BOSdata bosdataadd895                   = BOSdata.new()
htfadd895.settings                 := SettingsHTFadd895
htfadd895.candles                  := candlesadd895
htfadd895.bosdata                  := bosdataadd895
var CandleSet htfadd896                     = CandleSet.new()
var CandleSettings SettingsHTFadd896        = CandleSettings.new(htf="896", max_memory=3, htfint=896)
var Candle[] candlesadd896                  = array.new<Candle>(0)
var BOSdata bosdataadd896                   = BOSdata.new()
htfadd896.settings                 := SettingsHTFadd896
htfadd896.candles                  := candlesadd896
htfadd896.bosdata                  := bosdataadd896
var CandleSet htfadd897                     = CandleSet.new()
var CandleSettings SettingsHTFadd897        = CandleSettings.new(htf="897", max_memory=3, htfint=897)
var Candle[] candlesadd897                  = array.new<Candle>(0)
var BOSdata bosdataadd897                   = BOSdata.new()
htfadd897.settings                 := SettingsHTFadd897
htfadd897.candles                  := candlesadd897
htfadd897.bosdata                  := bosdataadd897
var CandleSet htfadd898                     = CandleSet.new()
var CandleSettings SettingsHTFadd898        = CandleSettings.new(htf="898", max_memory=3, htfint=898)
var Candle[] candlesadd898                  = array.new<Candle>(0)
var BOSdata bosdataadd898                   = BOSdata.new()
htfadd898.settings                 := SettingsHTFadd898
htfadd898.candles                  := candlesadd898
htfadd898.bosdata                  := bosdataadd898
var CandleSet htfadd899                     = CandleSet.new()
var CandleSettings SettingsHTFadd899        = CandleSettings.new(htf="899", max_memory=3, htfint=899)
var Candle[] candlesadd899                  = array.new<Candle>(0)
var BOSdata bosdataadd899                   = BOSdata.new()
htfadd899.settings                 := SettingsHTFadd899
htfadd899.candles                  := candlesadd899
htfadd899.bosdata                  := bosdataadd899
var CandleSet htfadd900                     = CandleSet.new()
var CandleSettings SettingsHTFadd900        = CandleSettings.new(htf="900", max_memory=3, htfint=900)
var Candle[] candlesadd900                  = array.new<Candle>(0)
var BOSdata bosdataadd900                   = BOSdata.new()
htfadd900.settings                 := SettingsHTFadd900
htfadd900.candles                  := candlesadd900
htfadd900.bosdata                  := bosdataadd900
var CandleSet htfadd901                     = CandleSet.new()
var CandleSettings SettingsHTFadd901        = CandleSettings.new(htf="901", max_memory=3, htfint=901)
var Candle[] candlesadd901                  = array.new<Candle>(0)
var BOSdata bosdataadd901                   = BOSdata.new()
htfadd901.settings                 := SettingsHTFadd901
htfadd901.candles                  := candlesadd901
htfadd901.bosdata                  := bosdataadd901
var CandleSet htfadd902                     = CandleSet.new()
var CandleSettings SettingsHTFadd902        = CandleSettings.new(htf="902", max_memory=3, htfint=902)
var Candle[] candlesadd902                  = array.new<Candle>(0)
var BOSdata bosdataadd902                   = BOSdata.new()
htfadd902.settings                 := SettingsHTFadd902
htfadd902.candles                  := candlesadd902
htfadd902.bosdata                  := bosdataadd902
var CandleSet htfadd903                     = CandleSet.new()
var CandleSettings SettingsHTFadd903        = CandleSettings.new(htf="903", max_memory=3, htfint=903)
var Candle[] candlesadd903                  = array.new<Candle>(0)
var BOSdata bosdataadd903                   = BOSdata.new()
htfadd903.settings                 := SettingsHTFadd903
htfadd903.candles                  := candlesadd903
htfadd903.bosdata                  := bosdataadd903
var CandleSet htfadd904                     = CandleSet.new()
var CandleSettings SettingsHTFadd904        = CandleSettings.new(htf="904", max_memory=3, htfint=904)
var Candle[] candlesadd904                  = array.new<Candle>(0)
var BOSdata bosdataadd904                   = BOSdata.new()
htfadd904.settings                 := SettingsHTFadd904
htfadd904.candles                  := candlesadd904
htfadd904.bosdata                  := bosdataadd904
var CandleSet htfadd905                     = CandleSet.new()
var CandleSettings SettingsHTFadd905        = CandleSettings.new(htf="905", max_memory=3, htfint=905)
var Candle[] candlesadd905                  = array.new<Candle>(0)
var BOSdata bosdataadd905                   = BOSdata.new()
htfadd905.settings                 := SettingsHTFadd905
htfadd905.candles                  := candlesadd905
htfadd905.bosdata                  := bosdataadd905
var CandleSet htfadd906                     = CandleSet.new()
var CandleSettings SettingsHTFadd906        = CandleSettings.new(htf="906", max_memory=3, htfint=906)
var Candle[] candlesadd906                  = array.new<Candle>(0)
var BOSdata bosdataadd906                   = BOSdata.new()
htfadd906.settings                 := SettingsHTFadd906
htfadd906.candles                  := candlesadd906
htfadd906.bosdata                  := bosdataadd906
var CandleSet htfadd907                     = CandleSet.new()
var CandleSettings SettingsHTFadd907        = CandleSettings.new(htf="907", max_memory=3, htfint=907)
var Candle[] candlesadd907                  = array.new<Candle>(0)
var BOSdata bosdataadd907                   = BOSdata.new()
htfadd907.settings                 := SettingsHTFadd907
htfadd907.candles                  := candlesadd907
htfadd907.bosdata                  := bosdataadd907
var CandleSet htfadd908                     = CandleSet.new()
var CandleSettings SettingsHTFadd908        = CandleSettings.new(htf="908", max_memory=3, htfint=908)
var Candle[] candlesadd908                  = array.new<Candle>(0)
var BOSdata bosdataadd908                   = BOSdata.new()
htfadd908.settings                 := SettingsHTFadd908
htfadd908.candles                  := candlesadd908
htfadd908.bosdata                  := bosdataadd908
var CandleSet htfadd909                     = CandleSet.new()
var CandleSettings SettingsHTFadd909        = CandleSettings.new(htf="909", max_memory=3, htfint=909)
var Candle[] candlesadd909                  = array.new<Candle>(0)
var BOSdata bosdataadd909                   = BOSdata.new()
htfadd909.settings                 := SettingsHTFadd909
htfadd909.candles                  := candlesadd909
htfadd909.bosdata                  := bosdataadd909
var CandleSet htfadd910                     = CandleSet.new()
var CandleSettings SettingsHTFadd910        = CandleSettings.new(htf="910", max_memory=3, htfint=910)
var Candle[] candlesadd910                  = array.new<Candle>(0)
var BOSdata bosdataadd910                   = BOSdata.new()
htfadd910.settings                 := SettingsHTFadd910
htfadd910.candles                  := candlesadd910
htfadd910.bosdata                  := bosdataadd910
var CandleSet htfadd911                     = CandleSet.new()
var CandleSettings SettingsHTFadd911        = CandleSettings.new(htf="911", max_memory=3, htfint=911)
var Candle[] candlesadd911                  = array.new<Candle>(0)
var BOSdata bosdataadd911                   = BOSdata.new()
htfadd911.settings                 := SettingsHTFadd911
htfadd911.candles                  := candlesadd911
htfadd911.bosdata                  := bosdataadd911
var CandleSet htfadd912                     = CandleSet.new()
var CandleSettings SettingsHTFadd912        = CandleSettings.new(htf="912", max_memory=3, htfint=912)
var Candle[] candlesadd912                  = array.new<Candle>(0)
var BOSdata bosdataadd912                   = BOSdata.new()
htfadd912.settings                 := SettingsHTFadd912
htfadd912.candles                  := candlesadd912
htfadd912.bosdata                  := bosdataadd912
var CandleSet htfadd913                     = CandleSet.new()
var CandleSettings SettingsHTFadd913        = CandleSettings.new(htf="913", max_memory=3, htfint=913)
var Candle[] candlesadd913                  = array.new<Candle>(0)
var BOSdata bosdataadd913                   = BOSdata.new()
htfadd913.settings                 := SettingsHTFadd913
htfadd913.candles                  := candlesadd913
htfadd913.bosdata                  := bosdataadd913
var CandleSet htfadd914                     = CandleSet.new()
var CandleSettings SettingsHTFadd914        = CandleSettings.new(htf="914", max_memory=3, htfint=914)
var Candle[] candlesadd914                  = array.new<Candle>(0)
var BOSdata bosdataadd914                   = BOSdata.new()
htfadd914.settings                 := SettingsHTFadd914
htfadd914.candles                  := candlesadd914
htfadd914.bosdata                  := bosdataadd914
var CandleSet htfadd915                     = CandleSet.new()
var CandleSettings SettingsHTFadd915        = CandleSettings.new(htf="915", max_memory=3, htfint=915)
var Candle[] candlesadd915                  = array.new<Candle>(0)
var BOSdata bosdataadd915                   = BOSdata.new()
htfadd915.settings                 := SettingsHTFadd915
htfadd915.candles                  := candlesadd915
htfadd915.bosdata                  := bosdataadd915
var CandleSet htfadd916                     = CandleSet.new()
var CandleSettings SettingsHTFadd916        = CandleSettings.new(htf="916", max_memory=3, htfint=916)
var Candle[] candlesadd916                  = array.new<Candle>(0)
var BOSdata bosdataadd916                   = BOSdata.new()
htfadd916.settings                 := SettingsHTFadd916
htfadd916.candles                  := candlesadd916
htfadd916.bosdata                  := bosdataadd916
var CandleSet htfadd917                     = CandleSet.new()
var CandleSettings SettingsHTFadd917        = CandleSettings.new(htf="917", max_memory=3, htfint=917)
var Candle[] candlesadd917                  = array.new<Candle>(0)
var BOSdata bosdataadd917                   = BOSdata.new()
htfadd917.settings                 := SettingsHTFadd917
htfadd917.candles                  := candlesadd917
htfadd917.bosdata                  := bosdataadd917
var CandleSet htfadd918                     = CandleSet.new()
var CandleSettings SettingsHTFadd918        = CandleSettings.new(htf="918", max_memory=3, htfint=918)
var Candle[] candlesadd918                  = array.new<Candle>(0)
var BOSdata bosdataadd918                   = BOSdata.new()
htfadd918.settings                 := SettingsHTFadd918
htfadd918.candles                  := candlesadd918
htfadd918.bosdata                  := bosdataadd918
var CandleSet htfadd919                     = CandleSet.new()
var CandleSettings SettingsHTFadd919        = CandleSettings.new(htf="919", max_memory=3, htfint=919)
var Candle[] candlesadd919                  = array.new<Candle>(0)
var BOSdata bosdataadd919                   = BOSdata.new()
htfadd919.settings                 := SettingsHTFadd919
htfadd919.candles                  := candlesadd919
htfadd919.bosdata                  := bosdataadd919
var CandleSet htfadd920                     = CandleSet.new()
var CandleSettings SettingsHTFadd920        = CandleSettings.new(htf="920", max_memory=3, htfint=920)
var Candle[] candlesadd920                  = array.new<Candle>(0)
var BOSdata bosdataadd920                   = BOSdata.new()
htfadd920.settings                 := SettingsHTFadd920
htfadd920.candles                  := candlesadd920
htfadd920.bosdata                  := bosdataadd920
var CandleSet htfadd921                     = CandleSet.new()
var CandleSettings SettingsHTFadd921        = CandleSettings.new(htf="921", max_memory=3, htfint=921)
var Candle[] candlesadd921                  = array.new<Candle>(0)
var BOSdata bosdataadd921                   = BOSdata.new()
htfadd921.settings                 := SettingsHTFadd921
htfadd921.candles                  := candlesadd921
htfadd921.bosdata                  := bosdataadd921
var CandleSet htfadd922                     = CandleSet.new()
var CandleSettings SettingsHTFadd922        = CandleSettings.new(htf="922", max_memory=3, htfint=922)
var Candle[] candlesadd922                  = array.new<Candle>(0)
var BOSdata bosdataadd922                   = BOSdata.new()
htfadd922.settings                 := SettingsHTFadd922
htfadd922.candles                  := candlesadd922
htfadd922.bosdata                  := bosdataadd922
var CandleSet htfadd923                     = CandleSet.new()
var CandleSettings SettingsHTFadd923        = CandleSettings.new(htf="923", max_memory=3, htfint=923)
var Candle[] candlesadd923                  = array.new<Candle>(0)
var BOSdata bosdataadd923                   = BOSdata.new()
htfadd923.settings                 := SettingsHTFadd923
htfadd923.candles                  := candlesadd923
htfadd923.bosdata                  := bosdataadd923
var CandleSet htfadd924                     = CandleSet.new()
var CandleSettings SettingsHTFadd924        = CandleSettings.new(htf="924", max_memory=3, htfint=924)
var Candle[] candlesadd924                  = array.new<Candle>(0)
var BOSdata bosdataadd924                   = BOSdata.new()
htfadd924.settings                 := SettingsHTFadd924
htfadd924.candles                  := candlesadd924
htfadd924.bosdata                  := bosdataadd924
var CandleSet htfadd925                     = CandleSet.new()
var CandleSettings SettingsHTFadd925        = CandleSettings.new(htf="925", max_memory=3, htfint=925)
var Candle[] candlesadd925                  = array.new<Candle>(0)
var BOSdata bosdataadd925                   = BOSdata.new()
htfadd925.settings                 := SettingsHTFadd925
htfadd925.candles                  := candlesadd925
htfadd925.bosdata                  := bosdataadd925
var CandleSet htfadd926                     = CandleSet.new()
var CandleSettings SettingsHTFadd926        = CandleSettings.new(htf="926", max_memory=3, htfint=926)
var Candle[] candlesadd926                  = array.new<Candle>(0)
var BOSdata bosdataadd926                   = BOSdata.new()
htfadd926.settings                 := SettingsHTFadd926
htfadd926.candles                  := candlesadd926
htfadd926.bosdata                  := bosdataadd926
var CandleSet htfadd927                     = CandleSet.new()
var CandleSettings SettingsHTFadd927        = CandleSettings.new(htf="927", max_memory=3, htfint=927)
var Candle[] candlesadd927                  = array.new<Candle>(0)
var BOSdata bosdataadd927                   = BOSdata.new()
htfadd927.settings                 := SettingsHTFadd927
htfadd927.candles                  := candlesadd927
htfadd927.bosdata                  := bosdataadd927
var CandleSet htfadd928                     = CandleSet.new()
var CandleSettings SettingsHTFadd928        = CandleSettings.new(htf="928", max_memory=3, htfint=928)
var Candle[] candlesadd928                  = array.new<Candle>(0)
var BOSdata bosdataadd928                   = BOSdata.new()
htfadd928.settings                 := SettingsHTFadd928
htfadd928.candles                  := candlesadd928
htfadd928.bosdata                  := bosdataadd928
var CandleSet htfadd929                     = CandleSet.new()
var CandleSettings SettingsHTFadd929        = CandleSettings.new(htf="929", max_memory=3, htfint=929)
var Candle[] candlesadd929                  = array.new<Candle>(0)
var BOSdata bosdataadd929                   = BOSdata.new()
htfadd929.settings                 := SettingsHTFadd929
htfadd929.candles                  := candlesadd929
htfadd929.bosdata                  := bosdataadd929
var CandleSet htfadd930                     = CandleSet.new()
var CandleSettings SettingsHTFadd930        = CandleSettings.new(htf="930", max_memory=3, htfint=930)
var Candle[] candlesadd930                  = array.new<Candle>(0)
var BOSdata bosdataadd930                   = BOSdata.new()
htfadd930.settings                 := SettingsHTFadd930
htfadd930.candles                  := candlesadd930
htfadd930.bosdata                  := bosdataadd930
var CandleSet htfadd931                     = CandleSet.new()
var CandleSettings SettingsHTFadd931        = CandleSettings.new(htf="931", max_memory=3, htfint=931)
var Candle[] candlesadd931                  = array.new<Candle>(0)
var BOSdata bosdataadd931                   = BOSdata.new()
htfadd931.settings                 := SettingsHTFadd931
htfadd931.candles                  := candlesadd931
htfadd931.bosdata                  := bosdataadd931
var CandleSet htfadd932                     = CandleSet.new()
var CandleSettings SettingsHTFadd932        = CandleSettings.new(htf="932", max_memory=3, htfint=932)
var Candle[] candlesadd932                  = array.new<Candle>(0)
var BOSdata bosdataadd932                   = BOSdata.new()
htfadd932.settings                 := SettingsHTFadd932
htfadd932.candles                  := candlesadd932
htfadd932.bosdata                  := bosdataadd932
var CandleSet htfadd933                     = CandleSet.new()
var CandleSettings SettingsHTFadd933        = CandleSettings.new(htf="933", max_memory=3, htfint=933)
var Candle[] candlesadd933                  = array.new<Candle>(0)
var BOSdata bosdataadd933                   = BOSdata.new()
htfadd933.settings                 := SettingsHTFadd933
htfadd933.candles                  := candlesadd933
htfadd933.bosdata                  := bosdataadd933
var CandleSet htfadd934                     = CandleSet.new()
var CandleSettings SettingsHTFadd934        = CandleSettings.new(htf="934", max_memory=3, htfint=934)
var Candle[] candlesadd934                  = array.new<Candle>(0)
var BOSdata bosdataadd934                   = BOSdata.new()
htfadd934.settings                 := SettingsHTFadd934
htfadd934.candles                  := candlesadd934
htfadd934.bosdata                  := bosdataadd934
var CandleSet htfadd935                     = CandleSet.new()
var CandleSettings SettingsHTFadd935        = CandleSettings.new(htf="935", max_memory=3, htfint=935)
var Candle[] candlesadd935                  = array.new<Candle>(0)
var BOSdata bosdataadd935                   = BOSdata.new()
htfadd935.settings                 := SettingsHTFadd935
htfadd935.candles                  := candlesadd935
htfadd935.bosdata                  := bosdataadd935
var CandleSet htfadd936                     = CandleSet.new()
var CandleSettings SettingsHTFadd936        = CandleSettings.new(htf="936", max_memory=3, htfint=936)
var Candle[] candlesadd936                  = array.new<Candle>(0)
var BOSdata bosdataadd936                   = BOSdata.new()
htfadd936.settings                 := SettingsHTFadd936
htfadd936.candles                  := candlesadd936
htfadd936.bosdata                  := bosdataadd936
var CandleSet htfadd937                     = CandleSet.new()
var CandleSettings SettingsHTFadd937        = CandleSettings.new(htf="937", max_memory=3, htfint=937)
var Candle[] candlesadd937                  = array.new<Candle>(0)
var BOSdata bosdataadd937                   = BOSdata.new()
htfadd937.settings                 := SettingsHTFadd937
htfadd937.candles                  := candlesadd937
htfadd937.bosdata                  := bosdataadd937
var CandleSet htfadd938                     = CandleSet.new()
var CandleSettings SettingsHTFadd938        = CandleSettings.new(htf="938", max_memory=3, htfint=938)
var Candle[] candlesadd938                  = array.new<Candle>(0)
var BOSdata bosdataadd938                   = BOSdata.new()
htfadd938.settings                 := SettingsHTFadd938
htfadd938.candles                  := candlesadd938
htfadd938.bosdata                  := bosdataadd938
var CandleSet htfadd939                     = CandleSet.new()
var CandleSettings SettingsHTFadd939        = CandleSettings.new(htf="939", max_memory=3, htfint=939)
var Candle[] candlesadd939                  = array.new<Candle>(0)
var BOSdata bosdataadd939                   = BOSdata.new()
htfadd939.settings                 := SettingsHTFadd939
htfadd939.candles                  := candlesadd939
htfadd939.bosdata                  := bosdataadd939
var CandleSet htfadd940                     = CandleSet.new()
var CandleSettings SettingsHTFadd940        = CandleSettings.new(htf="940", max_memory=3, htfint=940)
var Candle[] candlesadd940                  = array.new<Candle>(0)
var BOSdata bosdataadd940                   = BOSdata.new()
htfadd940.settings                 := SettingsHTFadd940
htfadd940.candles                  := candlesadd940
htfadd940.bosdata                  := bosdataadd940
var CandleSet htfadd941                     = CandleSet.new()
var CandleSettings SettingsHTFadd941        = CandleSettings.new(htf="941", max_memory=3, htfint=941)
var Candle[] candlesadd941                  = array.new<Candle>(0)
var BOSdata bosdataadd941                   = BOSdata.new()
htfadd941.settings                 := SettingsHTFadd941
htfadd941.candles                  := candlesadd941
htfadd941.bosdata                  := bosdataadd941
var CandleSet htfadd942                     = CandleSet.new()
var CandleSettings SettingsHTFadd942        = CandleSettings.new(htf="942", max_memory=3, htfint=942)
var Candle[] candlesadd942                  = array.new<Candle>(0)
var BOSdata bosdataadd942                   = BOSdata.new()
htfadd942.settings                 := SettingsHTFadd942
htfadd942.candles                  := candlesadd942
htfadd942.bosdata                  := bosdataadd942
var CandleSet htfadd943                     = CandleSet.new()
var CandleSettings SettingsHTFadd943        = CandleSettings.new(htf="943", max_memory=3, htfint=943)
var Candle[] candlesadd943                  = array.new<Candle>(0)
var BOSdata bosdataadd943                   = BOSdata.new()
htfadd943.settings                 := SettingsHTFadd943
htfadd943.candles                  := candlesadd943
htfadd943.bosdata                  := bosdataadd943
var CandleSet htfadd944                     = CandleSet.new()
var CandleSettings SettingsHTFadd944        = CandleSettings.new(htf="944", max_memory=3, htfint=944)
var Candle[] candlesadd944                  = array.new<Candle>(0)
var BOSdata bosdataadd944                   = BOSdata.new()
htfadd944.settings                 := SettingsHTFadd944
htfadd944.candles                  := candlesadd944
htfadd944.bosdata                  := bosdataadd944
var CandleSet htfadd945                     = CandleSet.new()
var CandleSettings SettingsHTFadd945        = CandleSettings.new(htf="945", max_memory=3, htfint=945)
var Candle[] candlesadd945                  = array.new<Candle>(0)
var BOSdata bosdataadd945                   = BOSdata.new()
htfadd945.settings                 := SettingsHTFadd945
htfadd945.candles                  := candlesadd945
htfadd945.bosdata                  := bosdataadd945
var CandleSet htfadd946                     = CandleSet.new()
var CandleSettings SettingsHTFadd946        = CandleSettings.new(htf="946", max_memory=3, htfint=946)
var Candle[] candlesadd946                  = array.new<Candle>(0)
var BOSdata bosdataadd946                   = BOSdata.new()
htfadd946.settings                 := SettingsHTFadd946
htfadd946.candles                  := candlesadd946
htfadd946.bosdata                  := bosdataadd946
var CandleSet htfadd947                     = CandleSet.new()
var CandleSettings SettingsHTFadd947        = CandleSettings.new(htf="947", max_memory=3, htfint=947)
var Candle[] candlesadd947                  = array.new<Candle>(0)
var BOSdata bosdataadd947                   = BOSdata.new()
htfadd947.settings                 := SettingsHTFadd947
htfadd947.candles                  := candlesadd947
htfadd947.bosdata                  := bosdataadd947
var CandleSet htfadd948                     = CandleSet.new()
var CandleSettings SettingsHTFadd948        = CandleSettings.new(htf="948", max_memory=3, htfint=948)
var Candle[] candlesadd948                  = array.new<Candle>(0)
var BOSdata bosdataadd948                   = BOSdata.new()
htfadd948.settings                 := SettingsHTFadd948
htfadd948.candles                  := candlesadd948
htfadd948.bosdata                  := bosdataadd948
var CandleSet htfadd949                     = CandleSet.new()
var CandleSettings SettingsHTFadd949        = CandleSettings.new(htf="949", max_memory=3, htfint=949)
var Candle[] candlesadd949                  = array.new<Candle>(0)
var BOSdata bosdataadd949                   = BOSdata.new()
htfadd949.settings                 := SettingsHTFadd949
htfadd949.candles                  := candlesadd949
htfadd949.bosdata                  := bosdataadd949
var CandleSet htfadd950                     = CandleSet.new()
var CandleSettings SettingsHTFadd950        = CandleSettings.new(htf="950", max_memory=3, htfint=950)
var Candle[] candlesadd950                  = array.new<Candle>(0)
var BOSdata bosdataadd950                   = BOSdata.new()
htfadd950.settings                 := SettingsHTFadd950
htfadd950.candles                  := candlesadd950
htfadd950.bosdata                  := bosdataadd950
var CandleSet htfadd951                     = CandleSet.new()
var CandleSettings SettingsHTFadd951        = CandleSettings.new(htf="951", max_memory=3, htfint=951)
var Candle[] candlesadd951                  = array.new<Candle>(0)
var BOSdata bosdataadd951                   = BOSdata.new()
htfadd951.settings                 := SettingsHTFadd951
htfadd951.candles                  := candlesadd951
htfadd951.bosdata                  := bosdataadd951
var CandleSet htfadd952                     = CandleSet.new()
var CandleSettings SettingsHTFadd952        = CandleSettings.new(htf="952", max_memory=3, htfint=952)
var Candle[] candlesadd952                  = array.new<Candle>(0)
var BOSdata bosdataadd952                   = BOSdata.new()
htfadd952.settings                 := SettingsHTFadd952
htfadd952.candles                  := candlesadd952
htfadd952.bosdata                  := bosdataadd952
var CandleSet htfadd953                     = CandleSet.new()
var CandleSettings SettingsHTFadd953        = CandleSettings.new(htf="953", max_memory=3, htfint=953)
var Candle[] candlesadd953                  = array.new<Candle>(0)
var BOSdata bosdataadd953                   = BOSdata.new()
htfadd953.settings                 := SettingsHTFadd953
htfadd953.candles                  := candlesadd953
htfadd953.bosdata                  := bosdataadd953
var CandleSet htfadd954                     = CandleSet.new()
var CandleSettings SettingsHTFadd954        = CandleSettings.new(htf="954", max_memory=3, htfint=954)
var Candle[] candlesadd954                  = array.new<Candle>(0)
var BOSdata bosdataadd954                   = BOSdata.new()
htfadd954.settings                 := SettingsHTFadd954
htfadd954.candles                  := candlesadd954
htfadd954.bosdata                  := bosdataadd954
var CandleSet htfadd955                     = CandleSet.new()
var CandleSettings SettingsHTFadd955        = CandleSettings.new(htf="955", max_memory=3, htfint=955)
var Candle[] candlesadd955                  = array.new<Candle>(0)
var BOSdata bosdataadd955                   = BOSdata.new()
htfadd955.settings                 := SettingsHTFadd955
htfadd955.candles                  := candlesadd955
htfadd955.bosdata                  := bosdataadd955
var CandleSet htfadd956                     = CandleSet.new()
var CandleSettings SettingsHTFadd956        = CandleSettings.new(htf="956", max_memory=3, htfint=956)
var Candle[] candlesadd956                  = array.new<Candle>(0)
var BOSdata bosdataadd956                   = BOSdata.new()
htfadd956.settings                 := SettingsHTFadd956
htfadd956.candles                  := candlesadd956
htfadd956.bosdata                  := bosdataadd956
var CandleSet htfadd957                     = CandleSet.new()
var CandleSettings SettingsHTFadd957        = CandleSettings.new(htf="957", max_memory=3, htfint=957)
var Candle[] candlesadd957                  = array.new<Candle>(0)
var BOSdata bosdataadd957                   = BOSdata.new()
htfadd957.settings                 := SettingsHTFadd957
htfadd957.candles                  := candlesadd957
htfadd957.bosdata                  := bosdataadd957
var CandleSet htfadd958                     = CandleSet.new()
var CandleSettings SettingsHTFadd958        = CandleSettings.new(htf="958", max_memory=3, htfint=958)
var Candle[] candlesadd958                  = array.new<Candle>(0)
var BOSdata bosdataadd958                   = BOSdata.new()
htfadd958.settings                 := SettingsHTFadd958
htfadd958.candles                  := candlesadd958
htfadd958.bosdata                  := bosdataadd958
var CandleSet htfadd959                     = CandleSet.new()
var CandleSettings SettingsHTFadd959        = CandleSettings.new(htf="959", max_memory=3, htfint=959)
var Candle[] candlesadd959                  = array.new<Candle>(0)
var BOSdata bosdataadd959                   = BOSdata.new()
htfadd959.settings                 := SettingsHTFadd959
htfadd959.candles                  := candlesadd959
htfadd959.bosdata                  := bosdataadd959
var CandleSet htfadd960                     = CandleSet.new()
var CandleSettings SettingsHTFadd960        = CandleSettings.new(htf="960", max_memory=3, htfint=960)
var Candle[] candlesadd960                  = array.new<Candle>(0)
var BOSdata bosdataadd960                   = BOSdata.new()
htfadd960.settings                 := SettingsHTFadd960
htfadd960.candles                  := candlesadd960
htfadd960.bosdata                  := bosdataadd960
var CandleSet htfadd961                     = CandleSet.new()
var CandleSettings SettingsHTFadd961        = CandleSettings.new(htf="961", max_memory=3, htfint=961)
var Candle[] candlesadd961                  = array.new<Candle>(0)
var BOSdata bosdataadd961                   = BOSdata.new()
htfadd961.settings                 := SettingsHTFadd961
htfadd961.candles                  := candlesadd961
htfadd961.bosdata                  := bosdataadd961
var CandleSet htfadd962                     = CandleSet.new()
var CandleSettings SettingsHTFadd962        = CandleSettings.new(htf="962", max_memory=3, htfint=962)
var Candle[] candlesadd962                  = array.new<Candle>(0)
var BOSdata bosdataadd962                   = BOSdata.new()
htfadd962.settings                 := SettingsHTFadd962
htfadd962.candles                  := candlesadd962
htfadd962.bosdata                  := bosdataadd962
var CandleSet htfadd963                     = CandleSet.new()
var CandleSettings SettingsHTFadd963        = CandleSettings.new(htf="963", max_memory=3, htfint=963)
var Candle[] candlesadd963                  = array.new<Candle>(0)
var BOSdata bosdataadd963                   = BOSdata.new()
htfadd963.settings                 := SettingsHTFadd963
htfadd963.candles                  := candlesadd963
htfadd963.bosdata                  := bosdataadd963
var CandleSet htfadd964                     = CandleSet.new()
var CandleSettings SettingsHTFadd964        = CandleSettings.new(htf="964", max_memory=3, htfint=964)
var Candle[] candlesadd964                  = array.new<Candle>(0)
var BOSdata bosdataadd964                   = BOSdata.new()
htfadd964.settings                 := SettingsHTFadd964
htfadd964.candles                  := candlesadd964
htfadd964.bosdata                  := bosdataadd964
var CandleSet htfadd965                     = CandleSet.new()
var CandleSettings SettingsHTFadd965        = CandleSettings.new(htf="965", max_memory=3, htfint=965)
var Candle[] candlesadd965                  = array.new<Candle>(0)
var BOSdata bosdataadd965                   = BOSdata.new()
htfadd965.settings                 := SettingsHTFadd965
htfadd965.candles                  := candlesadd965
htfadd965.bosdata                  := bosdataadd965
var CandleSet htfadd966                     = CandleSet.new()
var CandleSettings SettingsHTFadd966        = CandleSettings.new(htf="966", max_memory=3, htfint=966)
var Candle[] candlesadd966                  = array.new<Candle>(0)
var BOSdata bosdataadd966                   = BOSdata.new()
htfadd966.settings                 := SettingsHTFadd966
htfadd966.candles                  := candlesadd966
htfadd966.bosdata                  := bosdataadd966
var CandleSet htfadd967                     = CandleSet.new()
var CandleSettings SettingsHTFadd967        = CandleSettings.new(htf="967", max_memory=3, htfint=967)
var Candle[] candlesadd967                  = array.new<Candle>(0)
var BOSdata bosdataadd967                   = BOSdata.new()
htfadd967.settings                 := SettingsHTFadd967
htfadd967.candles                  := candlesadd967
htfadd967.bosdata                  := bosdataadd967
var CandleSet htfadd968                     = CandleSet.new()
var CandleSettings SettingsHTFadd968        = CandleSettings.new(htf="968", max_memory=3, htfint=968)
var Candle[] candlesadd968                  = array.new<Candle>(0)
var BOSdata bosdataadd968                   = BOSdata.new()
htfadd968.settings                 := SettingsHTFadd968
htfadd968.candles                  := candlesadd968
htfadd968.bosdata                  := bosdataadd968
var CandleSet htfadd969                     = CandleSet.new()
var CandleSettings SettingsHTFadd969        = CandleSettings.new(htf="969", max_memory=3, htfint=969)
var Candle[] candlesadd969                  = array.new<Candle>(0)
var BOSdata bosdataadd969                   = BOSdata.new()
htfadd969.settings                 := SettingsHTFadd969
htfadd969.candles                  := candlesadd969
htfadd969.bosdata                  := bosdataadd969
var CandleSet htfadd970                     = CandleSet.new()
var CandleSettings SettingsHTFadd970        = CandleSettings.new(htf="970", max_memory=3, htfint=970)
var Candle[] candlesadd970                  = array.new<Candle>(0)
var BOSdata bosdataadd970                   = BOSdata.new()
htfadd970.settings                 := SettingsHTFadd970
htfadd970.candles                  := candlesadd970
htfadd970.bosdata                  := bosdataadd970
var CandleSet htfadd971                     = CandleSet.new()
var CandleSettings SettingsHTFadd971        = CandleSettings.new(htf="971", max_memory=3, htfint=971)
var Candle[] candlesadd971                  = array.new<Candle>(0)
var BOSdata bosdataadd971                   = BOSdata.new()
htfadd971.settings                 := SettingsHTFadd971
htfadd971.candles                  := candlesadd971
htfadd971.bosdata                  := bosdataadd971
var CandleSet htfadd972                     = CandleSet.new()
var CandleSettings SettingsHTFadd972        = CandleSettings.new(htf="972", max_memory=3, htfint=972)
var Candle[] candlesadd972                  = array.new<Candle>(0)
var BOSdata bosdataadd972                   = BOSdata.new()
htfadd972.settings                 := SettingsHTFadd972
htfadd972.candles                  := candlesadd972
htfadd972.bosdata                  := bosdataadd972
var CandleSet htfadd973                     = CandleSet.new()
var CandleSettings SettingsHTFadd973        = CandleSettings.new(htf="973", max_memory=3, htfint=973)
var Candle[] candlesadd973                  = array.new<Candle>(0)
var BOSdata bosdataadd973                   = BOSdata.new()
htfadd973.settings                 := SettingsHTFadd973
htfadd973.candles                  := candlesadd973
htfadd973.bosdata                  := bosdataadd973
var CandleSet htfadd974                     = CandleSet.new()
var CandleSettings SettingsHTFadd974        = CandleSettings.new(htf="974", max_memory=3, htfint=974)
var Candle[] candlesadd974                  = array.new<Candle>(0)
var BOSdata bosdataadd974                   = BOSdata.new()
htfadd974.settings                 := SettingsHTFadd974
htfadd974.candles                  := candlesadd974
htfadd974.bosdata                  := bosdataadd974
var CandleSet htfadd975                     = CandleSet.new()
var CandleSettings SettingsHTFadd975        = CandleSettings.new(htf="975", max_memory=3, htfint=975)
var Candle[] candlesadd975                  = array.new<Candle>(0)
var BOSdata bosdataadd975                   = BOSdata.new()
htfadd975.settings                 := SettingsHTFadd975
htfadd975.candles                  := candlesadd975
htfadd975.bosdata                  := bosdataadd975
var CandleSet htfadd976                     = CandleSet.new()
var CandleSettings SettingsHTFadd976        = CandleSettings.new(htf="976", max_memory=3, htfint=976)
var Candle[] candlesadd976                  = array.new<Candle>(0)
var BOSdata bosdataadd976                   = BOSdata.new()
htfadd976.settings                 := SettingsHTFadd976
htfadd976.candles                  := candlesadd976
htfadd976.bosdata                  := bosdataadd976
var CandleSet htfadd977                     = CandleSet.new()
var CandleSettings SettingsHTFadd977        = CandleSettings.new(htf="977", max_memory=3, htfint=977)
var Candle[] candlesadd977                  = array.new<Candle>(0)
var BOSdata bosdataadd977                   = BOSdata.new()
htfadd977.settings                 := SettingsHTFadd977
htfadd977.candles                  := candlesadd977
htfadd977.bosdata                  := bosdataadd977
var CandleSet htfadd978                     = CandleSet.new()
var CandleSettings SettingsHTFadd978        = CandleSettings.new(htf="978", max_memory=3, htfint=978)
var Candle[] candlesadd978                  = array.new<Candle>(0)
var BOSdata bosdataadd978                   = BOSdata.new()
htfadd978.settings                 := SettingsHTFadd978
htfadd978.candles                  := candlesadd978
htfadd978.bosdata                  := bosdataadd978
var CandleSet htfadd979                     = CandleSet.new()
var CandleSettings SettingsHTFadd979        = CandleSettings.new(htf="979", max_memory=3, htfint=979)
var Candle[] candlesadd979                  = array.new<Candle>(0)
var BOSdata bosdataadd979                   = BOSdata.new()
htfadd979.settings                 := SettingsHTFadd979
htfadd979.candles                  := candlesadd979
htfadd979.bosdata                  := bosdataadd979
var CandleSet htfadd980                     = CandleSet.new()
var CandleSettings SettingsHTFadd980        = CandleSettings.new(htf="980", max_memory=3, htfint=980)
var Candle[] candlesadd980                  = array.new<Candle>(0)
var BOSdata bosdataadd980                   = BOSdata.new()
htfadd980.settings                 := SettingsHTFadd980
htfadd980.candles                  := candlesadd980
htfadd980.bosdata                  := bosdataadd980
var CandleSet htfadd981                     = CandleSet.new()
var CandleSettings SettingsHTFadd981        = CandleSettings.new(htf="981", max_memory=3, htfint=981)
var Candle[] candlesadd981                  = array.new<Candle>(0)
var BOSdata bosdataadd981                   = BOSdata.new()
htfadd981.settings                 := SettingsHTFadd981
htfadd981.candles                  := candlesadd981
htfadd981.bosdata                  := bosdataadd981
var CandleSet htfadd982                     = CandleSet.new()
var CandleSettings SettingsHTFadd982        = CandleSettings.new(htf="982", max_memory=3, htfint=982)
var Candle[] candlesadd982                  = array.new<Candle>(0)
var BOSdata bosdataadd982                   = BOSdata.new()
htfadd982.settings                 := SettingsHTFadd982
htfadd982.candles                  := candlesadd982
htfadd982.bosdata                  := bosdataadd982
var CandleSet htfadd983                     = CandleSet.new()
var CandleSettings SettingsHTFadd983        = CandleSettings.new(htf="983", max_memory=3, htfint=983)
var Candle[] candlesadd983                  = array.new<Candle>(0)
var BOSdata bosdataadd983                   = BOSdata.new()
htfadd983.settings                 := SettingsHTFadd983
htfadd983.candles                  := candlesadd983
htfadd983.bosdata                  := bosdataadd983
var CandleSet htfadd984                     = CandleSet.new()
var CandleSettings SettingsHTFadd984        = CandleSettings.new(htf="984", max_memory=3, htfint=984)
var Candle[] candlesadd984                  = array.new<Candle>(0)
var BOSdata bosdataadd984                   = BOSdata.new()
htfadd984.settings                 := SettingsHTFadd984
htfadd984.candles                  := candlesadd984
htfadd984.bosdata                  := bosdataadd984
var CandleSet htfadd985                     = CandleSet.new()
var CandleSettings SettingsHTFadd985        = CandleSettings.new(htf="985", max_memory=3, htfint=985)
var Candle[] candlesadd985                  = array.new<Candle>(0)
var BOSdata bosdataadd985                   = BOSdata.new()
htfadd985.settings                 := SettingsHTFadd985
htfadd985.candles                  := candlesadd985
htfadd985.bosdata                  := bosdataadd985
var CandleSet htfadd986                     = CandleSet.new()
var CandleSettings SettingsHTFadd986        = CandleSettings.new(htf="986", max_memory=3, htfint=986)
var Candle[] candlesadd986                  = array.new<Candle>(0)
var BOSdata bosdataadd986                   = BOSdata.new()
htfadd986.settings                 := SettingsHTFadd986
htfadd986.candles                  := candlesadd986
htfadd986.bosdata                  := bosdataadd986
var CandleSet htfadd987                     = CandleSet.new()
var CandleSettings SettingsHTFadd987        = CandleSettings.new(htf="987", max_memory=3, htfint=987)
var Candle[] candlesadd987                  = array.new<Candle>(0)
var BOSdata bosdataadd987                   = BOSdata.new()
htfadd987.settings                 := SettingsHTFadd987
htfadd987.candles                  := candlesadd987
htfadd987.bosdata                  := bosdataadd987
var CandleSet htfadd988                     = CandleSet.new()
var CandleSettings SettingsHTFadd988        = CandleSettings.new(htf="988", max_memory=3, htfint=988)
var Candle[] candlesadd988                  = array.new<Candle>(0)
var BOSdata bosdataadd988                   = BOSdata.new()
htfadd988.settings                 := SettingsHTFadd988
htfadd988.candles                  := candlesadd988
htfadd988.bosdata                  := bosdataadd988
var CandleSet htfadd989                     = CandleSet.new()
var CandleSettings SettingsHTFadd989        = CandleSettings.new(htf="989", max_memory=3, htfint=989)
var Candle[] candlesadd989                  = array.new<Candle>(0)
var BOSdata bosdataadd989                   = BOSdata.new()
htfadd989.settings                 := SettingsHTFadd989
htfadd989.candles                  := candlesadd989
htfadd989.bosdata                  := bosdataadd989
var CandleSet htfadd990                     = CandleSet.new()
var CandleSettings SettingsHTFadd990        = CandleSettings.new(htf="990", max_memory=3, htfint=990)
var Candle[] candlesadd990                  = array.new<Candle>(0)
var BOSdata bosdataadd990                   = BOSdata.new()
htfadd990.settings                 := SettingsHTFadd990
htfadd990.candles                  := candlesadd990
htfadd990.bosdata                  := bosdataadd990
var CandleSet htfadd991                     = CandleSet.new()
var CandleSettings SettingsHTFadd991        = CandleSettings.new(htf="991", max_memory=3, htfint=991)
var Candle[] candlesadd991                  = array.new<Candle>(0)
var BOSdata bosdataadd991                   = BOSdata.new()
htfadd991.settings                 := SettingsHTFadd991
htfadd991.candles                  := candlesadd991
htfadd991.bosdata                  := bosdataadd991
var CandleSet htfadd992                     = CandleSet.new()
var CandleSettings SettingsHTFadd992        = CandleSettings.new(htf="992", max_memory=3, htfint=992)
var Candle[] candlesadd992                  = array.new<Candle>(0)
var BOSdata bosdataadd992                   = BOSdata.new()
htfadd992.settings                 := SettingsHTFadd992
htfadd992.candles                  := candlesadd992
htfadd992.bosdata                  := bosdataadd992
var CandleSet htfadd993                     = CandleSet.new()
var CandleSettings SettingsHTFadd993        = CandleSettings.new(htf="993", max_memory=3, htfint=993)
var Candle[] candlesadd993                  = array.new<Candle>(0)
var BOSdata bosdataadd993                   = BOSdata.new()
htfadd993.settings                 := SettingsHTFadd993
htfadd993.candles                  := candlesadd993
htfadd993.bosdata                  := bosdataadd993
var CandleSet htfadd994                     = CandleSet.new()
var CandleSettings SettingsHTFadd994        = CandleSettings.new(htf="994", max_memory=3, htfint=994)
var Candle[] candlesadd994                  = array.new<Candle>(0)
var BOSdata bosdataadd994                   = BOSdata.new()
htfadd994.settings                 := SettingsHTFadd994
htfadd994.candles                  := candlesadd994
htfadd994.bosdata                  := bosdataadd994
var CandleSet htfadd995                     = CandleSet.new()
var CandleSettings SettingsHTFadd995        = CandleSettings.new(htf="995", max_memory=3, htfint=995)
var Candle[] candlesadd995                  = array.new<Candle>(0)
var BOSdata bosdataadd995                   = BOSdata.new()
htfadd995.settings                 := SettingsHTFadd995
htfadd995.candles                  := candlesadd995
htfadd995.bosdata                  := bosdataadd995
var CandleSet htfadd996                     = CandleSet.new()
var CandleSettings SettingsHTFadd996        = CandleSettings.new(htf="996", max_memory=3, htfint=996)
var Candle[] candlesadd996                  = array.new<Candle>(0)
var BOSdata bosdataadd996                   = BOSdata.new()
htfadd996.settings                 := SettingsHTFadd996
htfadd996.candles                  := candlesadd996
htfadd996.bosdata                  := bosdataadd996
var CandleSet htfadd997                     = CandleSet.new()
var CandleSettings SettingsHTFadd997        = CandleSettings.new(htf="997", max_memory=3, htfint=997)
var Candle[] candlesadd997                  = array.new<Candle>(0)
var BOSdata bosdataadd997                   = BOSdata.new()
htfadd997.settings                 := SettingsHTFadd997
htfadd997.candles                  := candlesadd997
htfadd997.bosdata                  := bosdataadd997
var CandleSet htfadd998                     = CandleSet.new()
var CandleSettings SettingsHTFadd998        = CandleSettings.new(htf="998", max_memory=3, htfint=998)
var Candle[] candlesadd998                  = array.new<Candle>(0)
var BOSdata bosdataadd998                   = BOSdata.new()
htfadd998.settings                 := SettingsHTFadd998
htfadd998.candles                  := candlesadd998
htfadd998.bosdata                  := bosdataadd998
var CandleSet htfadd999                     = CandleSet.new()
var CandleSettings SettingsHTFadd999        = CandleSettings.new(htf="999", max_memory=3, htfint=999)
var Candle[] candlesadd999                  = array.new<Candle>(0)
var BOSdata bosdataadd999                   = BOSdata.new()
htfadd999.settings                 := SettingsHTFadd999
htfadd999.candles                  := candlesadd999
htfadd999.bosdata                  := bosdataadd999
var CandleSet htfadd1000                     = CandleSet.new()
var CandleSettings SettingsHTFadd1000        = CandleSettings.new(htf="1000", max_memory=3, htfint=1000)
var Candle[] candlesadd1000                  = array.new<Candle>(0)
var BOSdata bosdataadd1000                   = BOSdata.new()
htfadd1000.settings                 := SettingsHTFadd1000
htfadd1000.candles                  := candlesadd1000
htfadd1000.bosdata                  := bosdataadd1000
var CandleSet htfadd1001                     = CandleSet.new()
var CandleSettings SettingsHTFadd1001        = CandleSettings.new(htf="1001", max_memory=3, htfint=1001)
var Candle[] candlesadd1001                  = array.new<Candle>(0)
var BOSdata bosdataadd1001                   = BOSdata.new()
htfadd1001.settings                 := SettingsHTFadd1001
htfadd1001.candles                  := candlesadd1001
htfadd1001.bosdata                  := bosdataadd1001
var CandleSet htfadd1002                     = CandleSet.new()
var CandleSettings SettingsHTFadd1002        = CandleSettings.new(htf="1002", max_memory=3, htfint=1002)
var Candle[] candlesadd1002                  = array.new<Candle>(0)
var BOSdata bosdataadd1002                   = BOSdata.new()
htfadd1002.settings                 := SettingsHTFadd1002
htfadd1002.candles                  := candlesadd1002
htfadd1002.bosdata                  := bosdataadd1002
var CandleSet htfadd1003                     = CandleSet.new()
var CandleSettings SettingsHTFadd1003        = CandleSettings.new(htf="1003", max_memory=3, htfint=1003)
var Candle[] candlesadd1003                  = array.new<Candle>(0)
var BOSdata bosdataadd1003                   = BOSdata.new()
htfadd1003.settings                 := SettingsHTFadd1003
htfadd1003.candles                  := candlesadd1003
htfadd1003.bosdata                  := bosdataadd1003
var CandleSet htfadd1004                     = CandleSet.new()
var CandleSettings SettingsHTFadd1004        = CandleSettings.new(htf="1004", max_memory=3, htfint=1004)
var Candle[] candlesadd1004                  = array.new<Candle>(0)
var BOSdata bosdataadd1004                   = BOSdata.new()
htfadd1004.settings                 := SettingsHTFadd1004
htfadd1004.candles                  := candlesadd1004
htfadd1004.bosdata                  := bosdataadd1004
var CandleSet htfadd1005                     = CandleSet.new()
var CandleSettings SettingsHTFadd1005        = CandleSettings.new(htf="1005", max_memory=3, htfint=1005)
var Candle[] candlesadd1005                  = array.new<Candle>(0)
var BOSdata bosdataadd1005                   = BOSdata.new()
htfadd1005.settings                 := SettingsHTFadd1005
htfadd1005.candles                  := candlesadd1005
htfadd1005.bosdata                  := bosdataadd1005
var CandleSet htfadd1006                     = CandleSet.new()
var CandleSettings SettingsHTFadd1006        = CandleSettings.new(htf="1006", max_memory=3, htfint=1006)
var Candle[] candlesadd1006                  = array.new<Candle>(0)
var BOSdata bosdataadd1006                   = BOSdata.new()
htfadd1006.settings                 := SettingsHTFadd1006
htfadd1006.candles                  := candlesadd1006
htfadd1006.bosdata                  := bosdataadd1006
var CandleSet htfadd1007                     = CandleSet.new()
var CandleSettings SettingsHTFadd1007        = CandleSettings.new(htf="1007", max_memory=3, htfint=1007)
var Candle[] candlesadd1007                  = array.new<Candle>(0)
var BOSdata bosdataadd1007                   = BOSdata.new()
htfadd1007.settings                 := SettingsHTFadd1007
htfadd1007.candles                  := candlesadd1007
htfadd1007.bosdata                  := bosdataadd1007
var CandleSet htfadd1008                     = CandleSet.new()
var CandleSettings SettingsHTFadd1008        = CandleSettings.new(htf="1008", max_memory=3, htfint=1008)
var Candle[] candlesadd1008                  = array.new<Candle>(0)
var BOSdata bosdataadd1008                   = BOSdata.new()
htfadd1008.settings                 := SettingsHTFadd1008
htfadd1008.candles                  := candlesadd1008
htfadd1008.bosdata                  := bosdataadd1008
var CandleSet htfadd1009                     = CandleSet.new()
var CandleSettings SettingsHTFadd1009        = CandleSettings.new(htf="1009", max_memory=3, htfint=1009)
var Candle[] candlesadd1009                  = array.new<Candle>(0)
var BOSdata bosdataadd1009                   = BOSdata.new()
htfadd1009.settings                 := SettingsHTFadd1009
htfadd1009.candles                  := candlesadd1009
htfadd1009.bosdata                  := bosdataadd1009
var CandleSet htfadd1010                     = CandleSet.new()
var CandleSettings SettingsHTFadd1010        = CandleSettings.new(htf="1010", max_memory=3, htfint=1010)
var Candle[] candlesadd1010                  = array.new<Candle>(0)
var BOSdata bosdataadd1010                   = BOSdata.new()
htfadd1010.settings                 := SettingsHTFadd1010
htfadd1010.candles                  := candlesadd1010
htfadd1010.bosdata                  := bosdataadd1010
var CandleSet htfadd1011                     = CandleSet.new()
var CandleSettings SettingsHTFadd1011        = CandleSettings.new(htf="1011", max_memory=3, htfint=1011)
var Candle[] candlesadd1011                  = array.new<Candle>(0)
var BOSdata bosdataadd1011                   = BOSdata.new()
htfadd1011.settings                 := SettingsHTFadd1011
htfadd1011.candles                  := candlesadd1011
htfadd1011.bosdata                  := bosdataadd1011
var CandleSet htfadd1012                     = CandleSet.new()
var CandleSettings SettingsHTFadd1012        = CandleSettings.new(htf="1012", max_memory=3, htfint=1012)
var Candle[] candlesadd1012                  = array.new<Candle>(0)
var BOSdata bosdataadd1012                   = BOSdata.new()
htfadd1012.settings                 := SettingsHTFadd1012
htfadd1012.candles                  := candlesadd1012
htfadd1012.bosdata                  := bosdataadd1012
var CandleSet htfadd1013                     = CandleSet.new()
var CandleSettings SettingsHTFadd1013        = CandleSettings.new(htf="1013", max_memory=3, htfint=1013)
var Candle[] candlesadd1013                  = array.new<Candle>(0)
var BOSdata bosdataadd1013                   = BOSdata.new()
htfadd1013.settings                 := SettingsHTFadd1013
htfadd1013.candles                  := candlesadd1013
htfadd1013.bosdata                  := bosdataadd1013
var CandleSet htfadd1014                     = CandleSet.new()
var CandleSettings SettingsHTFadd1014        = CandleSettings.new(htf="1014", max_memory=3, htfint=1014)
var Candle[] candlesadd1014                  = array.new<Candle>(0)
var BOSdata bosdataadd1014                   = BOSdata.new()
htfadd1014.settings                 := SettingsHTFadd1014
htfadd1014.candles                  := candlesadd1014
htfadd1014.bosdata                  := bosdataadd1014
var CandleSet htfadd1015                     = CandleSet.new()
var CandleSettings SettingsHTFadd1015        = CandleSettings.new(htf="1015", max_memory=3, htfint=1015)
var Candle[] candlesadd1015                  = array.new<Candle>(0)
var BOSdata bosdataadd1015                   = BOSdata.new()
htfadd1015.settings                 := SettingsHTFadd1015
htfadd1015.candles                  := candlesadd1015
htfadd1015.bosdata                  := bosdataadd1015
var CandleSet htfadd1016                     = CandleSet.new()
var CandleSettings SettingsHTFadd1016        = CandleSettings.new(htf="1016", max_memory=3, htfint=1016)
var Candle[] candlesadd1016                  = array.new<Candle>(0)
var BOSdata bosdataadd1016                   = BOSdata.new()
htfadd1016.settings                 := SettingsHTFadd1016
htfadd1016.candles                  := candlesadd1016
htfadd1016.bosdata                  := bosdataadd1016
var CandleSet htfadd1017                     = CandleSet.new()
var CandleSettings SettingsHTFadd1017        = CandleSettings.new(htf="1017", max_memory=3, htfint=1017)
var Candle[] candlesadd1017                  = array.new<Candle>(0)
var BOSdata bosdataadd1017                   = BOSdata.new()
htfadd1017.settings                 := SettingsHTFadd1017
htfadd1017.candles                  := candlesadd1017
htfadd1017.bosdata                  := bosdataadd1017
var CandleSet htfadd1018                     = CandleSet.new()
var CandleSettings SettingsHTFadd1018        = CandleSettings.new(htf="1018", max_memory=3, htfint=1018)
var Candle[] candlesadd1018                  = array.new<Candle>(0)
var BOSdata bosdataadd1018                   = BOSdata.new()
htfadd1018.settings                 := SettingsHTFadd1018
htfadd1018.candles                  := candlesadd1018
htfadd1018.bosdata                  := bosdataadd1018
var CandleSet htfadd1019                     = CandleSet.new()
var CandleSettings SettingsHTFadd1019        = CandleSettings.new(htf="1019", max_memory=3, htfint=1019)
var Candle[] candlesadd1019                  = array.new<Candle>(0)
var BOSdata bosdataadd1019                   = BOSdata.new()
htfadd1019.settings                 := SettingsHTFadd1019
htfadd1019.candles                  := candlesadd1019
htfadd1019.bosdata                  := bosdataadd1019
var CandleSet htfadd1020                     = CandleSet.new()
var CandleSettings SettingsHTFadd1020        = CandleSettings.new(htf="1020", max_memory=3, htfint=1020)
var Candle[] candlesadd1020                  = array.new<Candle>(0)
var BOSdata bosdataadd1020                   = BOSdata.new()
htfadd1020.settings                 := SettingsHTFadd1020
htfadd1020.candles                  := candlesadd1020
htfadd1020.bosdata                  := bosdataadd1020
var CandleSet htfadd1021                     = CandleSet.new()
var CandleSettings SettingsHTFadd1021        = CandleSettings.new(htf="1021", max_memory=3, htfint=1021)
var Candle[] candlesadd1021                  = array.new<Candle>(0)
var BOSdata bosdataadd1021                   = BOSdata.new()
htfadd1021.settings                 := SettingsHTFadd1021
htfadd1021.candles                  := candlesadd1021
htfadd1021.bosdata                  := bosdataadd1021
var CandleSet htfadd1022                     = CandleSet.new()
var CandleSettings SettingsHTFadd1022        = CandleSettings.new(htf="1022", max_memory=3, htfint=1022)
var Candle[] candlesadd1022                  = array.new<Candle>(0)
var BOSdata bosdataadd1022                   = BOSdata.new()
htfadd1022.settings                 := SettingsHTFadd1022
htfadd1022.candles                  := candlesadd1022
htfadd1022.bosdata                  := bosdataadd1022
var CandleSet htfadd1023                     = CandleSet.new()
var CandleSettings SettingsHTFadd1023        = CandleSettings.new(htf="1023", max_memory=3, htfint=1023)
var Candle[] candlesadd1023                  = array.new<Candle>(0)
var BOSdata bosdataadd1023                   = BOSdata.new()
htfadd1023.settings                 := SettingsHTFadd1023
htfadd1023.candles                  := candlesadd1023
htfadd1023.bosdata                  := bosdataadd1023
var CandleSet htfadd1024                     = CandleSet.new()
var CandleSettings SettingsHTFadd1024        = CandleSettings.new(htf="1024", max_memory=3, htfint=1024)
var Candle[] candlesadd1024                  = array.new<Candle>(0)
var BOSdata bosdataadd1024                   = BOSdata.new()
htfadd1024.settings                 := SettingsHTFadd1024
htfadd1024.candles                  := candlesadd1024
htfadd1024.bosdata                  := bosdataadd1024
var CandleSet htfadd1025                     = CandleSet.new()
var CandleSettings SettingsHTFadd1025        = CandleSettings.new(htf="1025", max_memory=3, htfint=1025)
var Candle[] candlesadd1025                  = array.new<Candle>(0)
var BOSdata bosdataadd1025                   = BOSdata.new()
htfadd1025.settings                 := SettingsHTFadd1025
htfadd1025.candles                  := candlesadd1025
htfadd1025.bosdata                  := bosdataadd1025
var CandleSet htfadd1026                     = CandleSet.new()
var CandleSettings SettingsHTFadd1026        = CandleSettings.new(htf="1026", max_memory=3, htfint=1026)
var Candle[] candlesadd1026                  = array.new<Candle>(0)
var BOSdata bosdataadd1026                   = BOSdata.new()
htfadd1026.settings                 := SettingsHTFadd1026
htfadd1026.candles                  := candlesadd1026
htfadd1026.bosdata                  := bosdataadd1026
var CandleSet htfadd1027                     = CandleSet.new()
var CandleSettings SettingsHTFadd1027        = CandleSettings.new(htf="1027", max_memory=3, htfint=1027)
var Candle[] candlesadd1027                  = array.new<Candle>(0)
var BOSdata bosdataadd1027                   = BOSdata.new()
htfadd1027.settings                 := SettingsHTFadd1027
htfadd1027.candles                  := candlesadd1027
htfadd1027.bosdata                  := bosdataadd1027
var CandleSet htfadd1028                     = CandleSet.new()
var CandleSettings SettingsHTFadd1028        = CandleSettings.new(htf="1028", max_memory=3, htfint=1028)
var Candle[] candlesadd1028                  = array.new<Candle>(0)
var BOSdata bosdataadd1028                   = BOSdata.new()
htfadd1028.settings                 := SettingsHTFadd1028
htfadd1028.candles                  := candlesadd1028
htfadd1028.bosdata                  := bosdataadd1028
var CandleSet htfadd1029                     = CandleSet.new()
var CandleSettings SettingsHTFadd1029        = CandleSettings.new(htf="1029", max_memory=3, htfint=1029)
var Candle[] candlesadd1029                  = array.new<Candle>(0)
var BOSdata bosdataadd1029                   = BOSdata.new()
htfadd1029.settings                 := SettingsHTFadd1029
htfadd1029.candles                  := candlesadd1029
htfadd1029.bosdata                  := bosdataadd1029
var CandleSet htfadd1030                     = CandleSet.new()
var CandleSettings SettingsHTFadd1030        = CandleSettings.new(htf="1030", max_memory=3, htfint=1030)
var Candle[] candlesadd1030                  = array.new<Candle>(0)
var BOSdata bosdataadd1030                   = BOSdata.new()
htfadd1030.settings                 := SettingsHTFadd1030
htfadd1030.candles                  := candlesadd1030
htfadd1030.bosdata                  := bosdataadd1030
var CandleSet htfadd1031                     = CandleSet.new()
var CandleSettings SettingsHTFadd1031        = CandleSettings.new(htf="1031", max_memory=3, htfint=1031)
var Candle[] candlesadd1031                  = array.new<Candle>(0)
var BOSdata bosdataadd1031                   = BOSdata.new()
htfadd1031.settings                 := SettingsHTFadd1031
htfadd1031.candles                  := candlesadd1031
htfadd1031.bosdata                  := bosdataadd1031
var CandleSet htfadd1032                     = CandleSet.new()
var CandleSettings SettingsHTFadd1032        = CandleSettings.new(htf="1032", max_memory=3, htfint=1032)
var Candle[] candlesadd1032                  = array.new<Candle>(0)
var BOSdata bosdataadd1032                   = BOSdata.new()
htfadd1032.settings                 := SettingsHTFadd1032
htfadd1032.candles                  := candlesadd1032
htfadd1032.bosdata                  := bosdataadd1032
var CandleSet htfadd1033                     = CandleSet.new()
var CandleSettings SettingsHTFadd1033        = CandleSettings.new(htf="1033", max_memory=3, htfint=1033)
var Candle[] candlesadd1033                  = array.new<Candle>(0)
var BOSdata bosdataadd1033                   = BOSdata.new()
htfadd1033.settings                 := SettingsHTFadd1033
htfadd1033.candles                  := candlesadd1033
htfadd1033.bosdata                  := bosdataadd1033
var CandleSet htfadd1034                     = CandleSet.new()
var CandleSettings SettingsHTFadd1034        = CandleSettings.new(htf="1034", max_memory=3, htfint=1034)
var Candle[] candlesadd1034                  = array.new<Candle>(0)
var BOSdata bosdataadd1034                   = BOSdata.new()
htfadd1034.settings                 := SettingsHTFadd1034
htfadd1034.candles                  := candlesadd1034
htfadd1034.bosdata                  := bosdataadd1034
var CandleSet htfadd1035                     = CandleSet.new()
var CandleSettings SettingsHTFadd1035        = CandleSettings.new(htf="1035", max_memory=3, htfint=1035)
var Candle[] candlesadd1035                  = array.new<Candle>(0)
var BOSdata bosdataadd1035                   = BOSdata.new()
htfadd1035.settings                 := SettingsHTFadd1035
htfadd1035.candles                  := candlesadd1035
htfadd1035.bosdata                  := bosdataadd1035
var CandleSet htfadd1036                     = CandleSet.new()
var CandleSettings SettingsHTFadd1036        = CandleSettings.new(htf="1036", max_memory=3, htfint=1036)
var Candle[] candlesadd1036                  = array.new<Candle>(0)
var BOSdata bosdataadd1036                   = BOSdata.new()
htfadd1036.settings                 := SettingsHTFadd1036
htfadd1036.candles                  := candlesadd1036
htfadd1036.bosdata                  := bosdataadd1036
var CandleSet htfadd1037                     = CandleSet.new()
var CandleSettings SettingsHTFadd1037        = CandleSettings.new(htf="1037", max_memory=3, htfint=1037)
var Candle[] candlesadd1037                  = array.new<Candle>(0)
var BOSdata bosdataadd1037                   = BOSdata.new()
htfadd1037.settings                 := SettingsHTFadd1037
htfadd1037.candles                  := candlesadd1037
htfadd1037.bosdata                  := bosdataadd1037
var CandleSet htfadd1038                     = CandleSet.new()
var CandleSettings SettingsHTFadd1038        = CandleSettings.new(htf="1038", max_memory=3, htfint=1038)
var Candle[] candlesadd1038                  = array.new<Candle>(0)
var BOSdata bosdataadd1038                   = BOSdata.new()
htfadd1038.settings                 := SettingsHTFadd1038
htfadd1038.candles                  := candlesadd1038
htfadd1038.bosdata                  := bosdataadd1038
var CandleSet htfadd1039                     = CandleSet.new()
var CandleSettings SettingsHTFadd1039        = CandleSettings.new(htf="1039", max_memory=3, htfint=1039)
var Candle[] candlesadd1039                  = array.new<Candle>(0)
var BOSdata bosdataadd1039                   = BOSdata.new()
htfadd1039.settings                 := SettingsHTFadd1039
htfadd1039.candles                  := candlesadd1039
htfadd1039.bosdata                  := bosdataadd1039
var CandleSet htfadd1040                     = CandleSet.new()
var CandleSettings SettingsHTFadd1040        = CandleSettings.new(htf="1040", max_memory=3, htfint=1040)
var Candle[] candlesadd1040                  = array.new<Candle>(0)
var BOSdata bosdataadd1040                   = BOSdata.new()
htfadd1040.settings                 := SettingsHTFadd1040
htfadd1040.candles                  := candlesadd1040
htfadd1040.bosdata                  := bosdataadd1040
var CandleSet htfadd1041                     = CandleSet.new()
var CandleSettings SettingsHTFadd1041        = CandleSettings.new(htf="1041", max_memory=3, htfint=1041)
var Candle[] candlesadd1041                  = array.new<Candle>(0)
var BOSdata bosdataadd1041                   = BOSdata.new()
htfadd1041.settings                 := SettingsHTFadd1041
htfadd1041.candles                  := candlesadd1041
htfadd1041.bosdata                  := bosdataadd1041
var CandleSet htfadd1042                     = CandleSet.new()
var CandleSettings SettingsHTFadd1042        = CandleSettings.new(htf="1042", max_memory=3, htfint=1042)
var Candle[] candlesadd1042                  = array.new<Candle>(0)
var BOSdata bosdataadd1042                   = BOSdata.new()
htfadd1042.settings                 := SettingsHTFadd1042
htfadd1042.candles                  := candlesadd1042
htfadd1042.bosdata                  := bosdataadd1042
var CandleSet htfadd1043                     = CandleSet.new()
var CandleSettings SettingsHTFadd1043        = CandleSettings.new(htf="1043", max_memory=3, htfint=1043)
var Candle[] candlesadd1043                  = array.new<Candle>(0)
var BOSdata bosdataadd1043                   = BOSdata.new()
htfadd1043.settings                 := SettingsHTFadd1043
htfadd1043.candles                  := candlesadd1043
htfadd1043.bosdata                  := bosdataadd1043
var CandleSet htfadd1044                     = CandleSet.new()
var CandleSettings SettingsHTFadd1044        = CandleSettings.new(htf="1044", max_memory=3, htfint=1044)
var Candle[] candlesadd1044                  = array.new<Candle>(0)
var BOSdata bosdataadd1044                   = BOSdata.new()
htfadd1044.settings                 := SettingsHTFadd1044
htfadd1044.candles                  := candlesadd1044
htfadd1044.bosdata                  := bosdataadd1044
var CandleSet htfadd1045                     = CandleSet.new()
var CandleSettings SettingsHTFadd1045        = CandleSettings.new(htf="1045", max_memory=3, htfint=1045)
var Candle[] candlesadd1045                  = array.new<Candle>(0)
var BOSdata bosdataadd1045                   = BOSdata.new()
htfadd1045.settings                 := SettingsHTFadd1045
htfadd1045.candles                  := candlesadd1045
htfadd1045.bosdata                  := bosdataadd1045
var CandleSet htfadd1046                     = CandleSet.new()
var CandleSettings SettingsHTFadd1046        = CandleSettings.new(htf="1046", max_memory=3, htfint=1046)
var Candle[] candlesadd1046                  = array.new<Candle>(0)
var BOSdata bosdataadd1046                   = BOSdata.new()
htfadd1046.settings                 := SettingsHTFadd1046
htfadd1046.candles                  := candlesadd1046
htfadd1046.bosdata                  := bosdataadd1046
var CandleSet htfadd1047                     = CandleSet.new()
var CandleSettings SettingsHTFadd1047        = CandleSettings.new(htf="1047", max_memory=3, htfint=1047)
var Candle[] candlesadd1047                  = array.new<Candle>(0)
var BOSdata bosdataadd1047                   = BOSdata.new()
htfadd1047.settings                 := SettingsHTFadd1047
htfadd1047.candles                  := candlesadd1047
htfadd1047.bosdata                  := bosdataadd1047
var CandleSet htfadd1048                     = CandleSet.new()
var CandleSettings SettingsHTFadd1048        = CandleSettings.new(htf="1048", max_memory=3, htfint=1048)
var Candle[] candlesadd1048                  = array.new<Candle>(0)
var BOSdata bosdataadd1048                   = BOSdata.new()
htfadd1048.settings                 := SettingsHTFadd1048
htfadd1048.candles                  := candlesadd1048
htfadd1048.bosdata                  := bosdataadd1048
var CandleSet htfadd1049                     = CandleSet.new()
var CandleSettings SettingsHTFadd1049        = CandleSettings.new(htf="1049", max_memory=3, htfint=1049)
var Candle[] candlesadd1049                  = array.new<Candle>(0)
var BOSdata bosdataadd1049                   = BOSdata.new()
htfadd1049.settings                 := SettingsHTFadd1049
htfadd1049.candles                  := candlesadd1049
htfadd1049.bosdata                  := bosdataadd1049
var CandleSet htfadd1050                     = CandleSet.new()
var CandleSettings SettingsHTFadd1050        = CandleSettings.new(htf="1050", max_memory=3, htfint=1050)
var Candle[] candlesadd1050                  = array.new<Candle>(0)
var BOSdata bosdataadd1050                   = BOSdata.new()
htfadd1050.settings                 := SettingsHTFadd1050
htfadd1050.candles                  := candlesadd1050
htfadd1050.bosdata                  := bosdataadd1050
var CandleSet htfadd1051                     = CandleSet.new()
var CandleSettings SettingsHTFadd1051        = CandleSettings.new(htf="1051", max_memory=3, htfint=1051)
var Candle[] candlesadd1051                  = array.new<Candle>(0)
var BOSdata bosdataadd1051                   = BOSdata.new()
htfadd1051.settings                 := SettingsHTFadd1051
htfadd1051.candles                  := candlesadd1051
htfadd1051.bosdata                  := bosdataadd1051
var CandleSet htfadd1052                     = CandleSet.new()
var CandleSettings SettingsHTFadd1052        = CandleSettings.new(htf="1052", max_memory=3, htfint=1052)
var Candle[] candlesadd1052                  = array.new<Candle>(0)
var BOSdata bosdataadd1052                   = BOSdata.new()
htfadd1052.settings                 := SettingsHTFadd1052
htfadd1052.candles                  := candlesadd1052
htfadd1052.bosdata                  := bosdataadd1052
var CandleSet htfadd1053                     = CandleSet.new()
var CandleSettings SettingsHTFadd1053        = CandleSettings.new(htf="1053", max_memory=3, htfint=1053)
var Candle[] candlesadd1053                  = array.new<Candle>(0)
var BOSdata bosdataadd1053                   = BOSdata.new()
htfadd1053.settings                 := SettingsHTFadd1053
htfadd1053.candles                  := candlesadd1053
htfadd1053.bosdata                  := bosdataadd1053
var CandleSet htfadd1054                     = CandleSet.new()
var CandleSettings SettingsHTFadd1054        = CandleSettings.new(htf="1054", max_memory=3, htfint=1054)
var Candle[] candlesadd1054                  = array.new<Candle>(0)
var BOSdata bosdataadd1054                   = BOSdata.new()
htfadd1054.settings                 := SettingsHTFadd1054
htfadd1054.candles                  := candlesadd1054
htfadd1054.bosdata                  := bosdataadd1054
var CandleSet htfadd1055                     = CandleSet.new()
var CandleSettings SettingsHTFadd1055        = CandleSettings.new(htf="1055", max_memory=3, htfint=1055)
var Candle[] candlesadd1055                  = array.new<Candle>(0)
var BOSdata bosdataadd1055                   = BOSdata.new()
htfadd1055.settings                 := SettingsHTFadd1055
htfadd1055.candles                  := candlesadd1055
htfadd1055.bosdata                  := bosdataadd1055
var CandleSet htfadd1056                     = CandleSet.new()
var CandleSettings SettingsHTFadd1056        = CandleSettings.new(htf="1056", max_memory=3, htfint=1056)
var Candle[] candlesadd1056                  = array.new<Candle>(0)
var BOSdata bosdataadd1056                   = BOSdata.new()
htfadd1056.settings                 := SettingsHTFadd1056
htfadd1056.candles                  := candlesadd1056
htfadd1056.bosdata                  := bosdataadd1056
var CandleSet htfadd1057                     = CandleSet.new()
var CandleSettings SettingsHTFadd1057        = CandleSettings.new(htf="1057", max_memory=3, htfint=1057)
var Candle[] candlesadd1057                  = array.new<Candle>(0)
var BOSdata bosdataadd1057                   = BOSdata.new()
htfadd1057.settings                 := SettingsHTFadd1057
htfadd1057.candles                  := candlesadd1057
htfadd1057.bosdata                  := bosdataadd1057
var CandleSet htfadd1058                     = CandleSet.new()
var CandleSettings SettingsHTFadd1058        = CandleSettings.new(htf="1058", max_memory=3, htfint=1058)
var Candle[] candlesadd1058                  = array.new<Candle>(0)
var BOSdata bosdataadd1058                   = BOSdata.new()
htfadd1058.settings                 := SettingsHTFadd1058
htfadd1058.candles                  := candlesadd1058
htfadd1058.bosdata                  := bosdataadd1058
var CandleSet htfadd1059                     = CandleSet.new()
var CandleSettings SettingsHTFadd1059        = CandleSettings.new(htf="1059", max_memory=3, htfint=1059)
var Candle[] candlesadd1059                  = array.new<Candle>(0)
var BOSdata bosdataadd1059                   = BOSdata.new()
htfadd1059.settings                 := SettingsHTFadd1059
htfadd1059.candles                  := candlesadd1059
htfadd1059.bosdata                  := bosdataadd1059
var CandleSet htfadd1060                     = CandleSet.new()
var CandleSettings SettingsHTFadd1060        = CandleSettings.new(htf="1060", max_memory=3, htfint=1060)
var Candle[] candlesadd1060                  = array.new<Candle>(0)
var BOSdata bosdataadd1060                   = BOSdata.new()
htfadd1060.settings                 := SettingsHTFadd1060
htfadd1060.candles                  := candlesadd1060
htfadd1060.bosdata                  := bosdataadd1060
var CandleSet htfadd1061                     = CandleSet.new()
var CandleSettings SettingsHTFadd1061        = CandleSettings.new(htf="1061", max_memory=3, htfint=1061)
var Candle[] candlesadd1061                  = array.new<Candle>(0)
var BOSdata bosdataadd1061                   = BOSdata.new()
htfadd1061.settings                 := SettingsHTFadd1061
htfadd1061.candles                  := candlesadd1061
htfadd1061.bosdata                  := bosdataadd1061
var CandleSet htfadd1062                     = CandleSet.new()
var CandleSettings SettingsHTFadd1062        = CandleSettings.new(htf="1062", max_memory=3, htfint=1062)
var Candle[] candlesadd1062                  = array.new<Candle>(0)
var BOSdata bosdataadd1062                   = BOSdata.new()
htfadd1062.settings                 := SettingsHTFadd1062
htfadd1062.candles                  := candlesadd1062
htfadd1062.bosdata                  := bosdataadd1062
var CandleSet htfadd1063                     = CandleSet.new()
var CandleSettings SettingsHTFadd1063        = CandleSettings.new(htf="1063", max_memory=3, htfint=1063)
var Candle[] candlesadd1063                  = array.new<Candle>(0)
var BOSdata bosdataadd1063                   = BOSdata.new()
htfadd1063.settings                 := SettingsHTFadd1063
htfadd1063.candles                  := candlesadd1063
htfadd1063.bosdata                  := bosdataadd1063
var CandleSet htfadd1064                     = CandleSet.new()
var CandleSettings SettingsHTFadd1064        = CandleSettings.new(htf="1064", max_memory=3, htfint=1064)
var Candle[] candlesadd1064                  = array.new<Candle>(0)
var BOSdata bosdataadd1064                   = BOSdata.new()
htfadd1064.settings                 := SettingsHTFadd1064
htfadd1064.candles                  := candlesadd1064
htfadd1064.bosdata                  := bosdataadd1064
var CandleSet htfadd1065                     = CandleSet.new()
var CandleSettings SettingsHTFadd1065        = CandleSettings.new(htf="1065", max_memory=3, htfint=1065)
var Candle[] candlesadd1065                  = array.new<Candle>(0)
var BOSdata bosdataadd1065                   = BOSdata.new()
htfadd1065.settings                 := SettingsHTFadd1065
htfadd1065.candles                  := candlesadd1065
htfadd1065.bosdata                  := bosdataadd1065
var CandleSet htfadd1066                     = CandleSet.new()
var CandleSettings SettingsHTFadd1066        = CandleSettings.new(htf="1066", max_memory=3, htfint=1066)
var Candle[] candlesadd1066                  = array.new<Candle>(0)
var BOSdata bosdataadd1066                   = BOSdata.new()
htfadd1066.settings                 := SettingsHTFadd1066
htfadd1066.candles                  := candlesadd1066
htfadd1066.bosdata                  := bosdataadd1066
var CandleSet htfadd1067                     = CandleSet.new()
var CandleSettings SettingsHTFadd1067        = CandleSettings.new(htf="1067", max_memory=3, htfint=1067)
var Candle[] candlesadd1067                  = array.new<Candle>(0)
var BOSdata bosdataadd1067                   = BOSdata.new()
htfadd1067.settings                 := SettingsHTFadd1067
htfadd1067.candles                  := candlesadd1067
htfadd1067.bosdata                  := bosdataadd1067
var CandleSet htfadd1068                     = CandleSet.new()
var CandleSettings SettingsHTFadd1068        = CandleSettings.new(htf="1068", max_memory=3, htfint=1068)
var Candle[] candlesadd1068                  = array.new<Candle>(0)
var BOSdata bosdataadd1068                   = BOSdata.new()
htfadd1068.settings                 := SettingsHTFadd1068
htfadd1068.candles                  := candlesadd1068
htfadd1068.bosdata                  := bosdataadd1068
var CandleSet htfadd1069                     = CandleSet.new()
var CandleSettings SettingsHTFadd1069        = CandleSettings.new(htf="1069", max_memory=3, htfint=1069)
var Candle[] candlesadd1069                  = array.new<Candle>(0)
var BOSdata bosdataadd1069                   = BOSdata.new()
htfadd1069.settings                 := SettingsHTFadd1069
htfadd1069.candles                  := candlesadd1069
htfadd1069.bosdata                  := bosdataadd1069
var CandleSet htfadd1070                     = CandleSet.new()
var CandleSettings SettingsHTFadd1070        = CandleSettings.new(htf="1070", max_memory=3, htfint=1070)
var Candle[] candlesadd1070                  = array.new<Candle>(0)
var BOSdata bosdataadd1070                   = BOSdata.new()
htfadd1070.settings                 := SettingsHTFadd1070
htfadd1070.candles                  := candlesadd1070
htfadd1070.bosdata                  := bosdataadd1070
var CandleSet htfadd1071                     = CandleSet.new()
var CandleSettings SettingsHTFadd1071        = CandleSettings.new(htf="1071", max_memory=3, htfint=1071)
var Candle[] candlesadd1071                  = array.new<Candle>(0)
var BOSdata bosdataadd1071                   = BOSdata.new()
htfadd1071.settings                 := SettingsHTFadd1071
htfadd1071.candles                  := candlesadd1071
htfadd1071.bosdata                  := bosdataadd1071
var CandleSet htfadd1072                     = CandleSet.new()
var CandleSettings SettingsHTFadd1072        = CandleSettings.new(htf="1072", max_memory=3, htfint=1072)
var Candle[] candlesadd1072                  = array.new<Candle>(0)
var BOSdata bosdataadd1072                   = BOSdata.new()
htfadd1072.settings                 := SettingsHTFadd1072
htfadd1072.candles                  := candlesadd1072
htfadd1072.bosdata                  := bosdataadd1072
var CandleSet htfadd1073                     = CandleSet.new()
var CandleSettings SettingsHTFadd1073        = CandleSettings.new(htf="1073", max_memory=3, htfint=1073)
var Candle[] candlesadd1073                  = array.new<Candle>(0)
var BOSdata bosdataadd1073                   = BOSdata.new()
htfadd1073.settings                 := SettingsHTFadd1073
htfadd1073.candles                  := candlesadd1073
htfadd1073.bosdata                  := bosdataadd1073
var CandleSet htfadd1074                     = CandleSet.new()
var CandleSettings SettingsHTFadd1074        = CandleSettings.new(htf="1074", max_memory=3, htfint=1074)
var Candle[] candlesadd1074                  = array.new<Candle>(0)
var BOSdata bosdataadd1074                   = BOSdata.new()
htfadd1074.settings                 := SettingsHTFadd1074
htfadd1074.candles                  := candlesadd1074
htfadd1074.bosdata                  := bosdataadd1074
var CandleSet htfadd1075                     = CandleSet.new()
var CandleSettings SettingsHTFadd1075        = CandleSettings.new(htf="1075", max_memory=3, htfint=1075)
var Candle[] candlesadd1075                  = array.new<Candle>(0)
var BOSdata bosdataadd1075                   = BOSdata.new()
htfadd1075.settings                 := SettingsHTFadd1075
htfadd1075.candles                  := candlesadd1075
htfadd1075.bosdata                  := bosdataadd1075
var CandleSet htfadd1076                     = CandleSet.new()
var CandleSettings SettingsHTFadd1076        = CandleSettings.new(htf="1076", max_memory=3, htfint=1076)
var Candle[] candlesadd1076                  = array.new<Candle>(0)
var BOSdata bosdataadd1076                   = BOSdata.new()
htfadd1076.settings                 := SettingsHTFadd1076
htfadd1076.candles                  := candlesadd1076
htfadd1076.bosdata                  := bosdataadd1076
var CandleSet htfadd1077                     = CandleSet.new()
var CandleSettings SettingsHTFadd1077        = CandleSettings.new(htf="1077", max_memory=3, htfint=1077)
var Candle[] candlesadd1077                  = array.new<Candle>(0)
var BOSdata bosdataadd1077                   = BOSdata.new()
htfadd1077.settings                 := SettingsHTFadd1077
htfadd1077.candles                  := candlesadd1077
htfadd1077.bosdata                  := bosdataadd1077
var CandleSet htfadd1078                     = CandleSet.new()
var CandleSettings SettingsHTFadd1078        = CandleSettings.new(htf="1078", max_memory=3, htfint=1078)
var Candle[] candlesadd1078                  = array.new<Candle>(0)
var BOSdata bosdataadd1078                   = BOSdata.new()
htfadd1078.settings                 := SettingsHTFadd1078
htfadd1078.candles                  := candlesadd1078
htfadd1078.bosdata                  := bosdataadd1078
var CandleSet htfadd1079                     = CandleSet.new()
var CandleSettings SettingsHTFadd1079        = CandleSettings.new(htf="1079", max_memory=3, htfint=1079)
var Candle[] candlesadd1079                  = array.new<Candle>(0)
var BOSdata bosdataadd1079                   = BOSdata.new()
htfadd1079.settings                 := SettingsHTFadd1079
htfadd1079.candles                  := candlesadd1079
htfadd1079.bosdata                  := bosdataadd1079
var CandleSet htfadd1080                     = CandleSet.new()
var CandleSettings SettingsHTFadd1080        = CandleSettings.new(htf="1080", max_memory=3, htfint=1080)
var Candle[] candlesadd1080                  = array.new<Candle>(0)
var BOSdata bosdataadd1080                   = BOSdata.new()
htfadd1080.settings                 := SettingsHTFadd1080
htfadd1080.candles                  := candlesadd1080
htfadd1080.bosdata                  := bosdataadd1080
var CandleSet htfadd1081                     = CandleSet.new()
var CandleSettings SettingsHTFadd1081        = CandleSettings.new(htf="1081", max_memory=3, htfint=1081)
var Candle[] candlesadd1081                  = array.new<Candle>(0)
var BOSdata bosdataadd1081                   = BOSdata.new()
htfadd1081.settings                 := SettingsHTFadd1081
htfadd1081.candles                  := candlesadd1081
htfadd1081.bosdata                  := bosdataadd1081
var CandleSet htfadd1082                     = CandleSet.new()
var CandleSettings SettingsHTFadd1082        = CandleSettings.new(htf="1082", max_memory=3, htfint=1082)
var Candle[] candlesadd1082                  = array.new<Candle>(0)
var BOSdata bosdataadd1082                   = BOSdata.new()
htfadd1082.settings                 := SettingsHTFadd1082
htfadd1082.candles                  := candlesadd1082
htfadd1082.bosdata                  := bosdataadd1082
var CandleSet htfadd1083                     = CandleSet.new()
var CandleSettings SettingsHTFadd1083        = CandleSettings.new(htf="1083", max_memory=3, htfint=1083)
var Candle[] candlesadd1083                  = array.new<Candle>(0)
var BOSdata bosdataadd1083                   = BOSdata.new()
htfadd1083.settings                 := SettingsHTFadd1083
htfadd1083.candles                  := candlesadd1083
htfadd1083.bosdata                  := bosdataadd1083
var CandleSet htfadd1084                     = CandleSet.new()
var CandleSettings SettingsHTFadd1084        = CandleSettings.new(htf="1084", max_memory=3, htfint=1084)
var Candle[] candlesadd1084                  = array.new<Candle>(0)
var BOSdata bosdataadd1084                   = BOSdata.new()
htfadd1084.settings                 := SettingsHTFadd1084
htfadd1084.candles                  := candlesadd1084
htfadd1084.bosdata                  := bosdataadd1084
var CandleSet htfadd1085                     = CandleSet.new()
var CandleSettings SettingsHTFadd1085        = CandleSettings.new(htf="1085", max_memory=3, htfint=1085)
var Candle[] candlesadd1085                  = array.new<Candle>(0)
var BOSdata bosdataadd1085                   = BOSdata.new()
htfadd1085.settings                 := SettingsHTFadd1085
htfadd1085.candles                  := candlesadd1085
htfadd1085.bosdata                  := bosdataadd1085
var CandleSet htfadd1086                     = CandleSet.new()
var CandleSettings SettingsHTFadd1086        = CandleSettings.new(htf="1086", max_memory=3, htfint=1086)
var Candle[] candlesadd1086                  = array.new<Candle>(0)
var BOSdata bosdataadd1086                   = BOSdata.new()
htfadd1086.settings                 := SettingsHTFadd1086
htfadd1086.candles                  := candlesadd1086
htfadd1086.bosdata                  := bosdataadd1086
var CandleSet htfadd1087                     = CandleSet.new()
var CandleSettings SettingsHTFadd1087        = CandleSettings.new(htf="1087", max_memory=3, htfint=1087)
var Candle[] candlesadd1087                  = array.new<Candle>(0)
var BOSdata bosdataadd1087                   = BOSdata.new()
htfadd1087.settings                 := SettingsHTFadd1087
htfadd1087.candles                  := candlesadd1087
htfadd1087.bosdata                  := bosdataadd1087
var CandleSet htfadd1088                     = CandleSet.new()
var CandleSettings SettingsHTFadd1088        = CandleSettings.new(htf="1088", max_memory=3, htfint=1088)
var Candle[] candlesadd1088                  = array.new<Candle>(0)
var BOSdata bosdataadd1088                   = BOSdata.new()
htfadd1088.settings                 := SettingsHTFadd1088
htfadd1088.candles                  := candlesadd1088
htfadd1088.bosdata                  := bosdataadd1088
var CandleSet htfadd1089                     = CandleSet.new()
var CandleSettings SettingsHTFadd1089        = CandleSettings.new(htf="1089", max_memory=3, htfint=1089)
var Candle[] candlesadd1089                  = array.new<Candle>(0)
var BOSdata bosdataadd1089                   = BOSdata.new()
htfadd1089.settings                 := SettingsHTFadd1089
htfadd1089.candles                  := candlesadd1089
htfadd1089.bosdata                  := bosdataadd1089
var CandleSet htfadd1090                     = CandleSet.new()
var CandleSettings SettingsHTFadd1090        = CandleSettings.new(htf="1090", max_memory=3, htfint=1090)
var Candle[] candlesadd1090                  = array.new<Candle>(0)
var BOSdata bosdataadd1090                   = BOSdata.new()
htfadd1090.settings                 := SettingsHTFadd1090
htfadd1090.candles                  := candlesadd1090
htfadd1090.bosdata                  := bosdataadd1090
var CandleSet htfadd1091                     = CandleSet.new()
var CandleSettings SettingsHTFadd1091        = CandleSettings.new(htf="1091", max_memory=3, htfint=1091)
var Candle[] candlesadd1091                  = array.new<Candle>(0)
var BOSdata bosdataadd1091                   = BOSdata.new()
htfadd1091.settings                 := SettingsHTFadd1091
htfadd1091.candles                  := candlesadd1091
htfadd1091.bosdata                  := bosdataadd1091
var CandleSet htfadd1092                     = CandleSet.new()
var CandleSettings SettingsHTFadd1092        = CandleSettings.new(htf="1092", max_memory=3, htfint=1092)
var Candle[] candlesadd1092                  = array.new<Candle>(0)
var BOSdata bosdataadd1092                   = BOSdata.new()
htfadd1092.settings                 := SettingsHTFadd1092
htfadd1092.candles                  := candlesadd1092
htfadd1092.bosdata                  := bosdataadd1092
var CandleSet htfadd1093                     = CandleSet.new()
var CandleSettings SettingsHTFadd1093        = CandleSettings.new(htf="1093", max_memory=3, htfint=1093)
var Candle[] candlesadd1093                  = array.new<Candle>(0)
var BOSdata bosdataadd1093                   = BOSdata.new()
htfadd1093.settings                 := SettingsHTFadd1093
htfadd1093.candles                  := candlesadd1093
htfadd1093.bosdata                  := bosdataadd1093
var CandleSet htfadd1094                     = CandleSet.new()
var CandleSettings SettingsHTFadd1094        = CandleSettings.new(htf="1094", max_memory=3, htfint=1094)
var Candle[] candlesadd1094                  = array.new<Candle>(0)
var BOSdata bosdataadd1094                   = BOSdata.new()
htfadd1094.settings                 := SettingsHTFadd1094
htfadd1094.candles                  := candlesadd1094
htfadd1094.bosdata                  := bosdataadd1094
var CandleSet htfadd1095                     = CandleSet.new()
var CandleSettings SettingsHTFadd1095        = CandleSettings.new(htf="1095", max_memory=3, htfint=1095)
var Candle[] candlesadd1095                  = array.new<Candle>(0)
var BOSdata bosdataadd1095                   = BOSdata.new()
htfadd1095.settings                 := SettingsHTFadd1095
htfadd1095.candles                  := candlesadd1095
htfadd1095.bosdata                  := bosdataadd1095
var CandleSet htfadd1096                     = CandleSet.new()
var CandleSettings SettingsHTFadd1096        = CandleSettings.new(htf="1096", max_memory=3, htfint=1096)
var Candle[] candlesadd1096                  = array.new<Candle>(0)
var BOSdata bosdataadd1096                   = BOSdata.new()
htfadd1096.settings                 := SettingsHTFadd1096
htfadd1096.candles                  := candlesadd1096
htfadd1096.bosdata                  := bosdataadd1096
var CandleSet htfadd1097                     = CandleSet.new()
var CandleSettings SettingsHTFadd1097        = CandleSettings.new(htf="1097", max_memory=3, htfint=1097)
var Candle[] candlesadd1097                  = array.new<Candle>(0)
var BOSdata bosdataadd1097                   = BOSdata.new()
htfadd1097.settings                 := SettingsHTFadd1097
htfadd1097.candles                  := candlesadd1097
htfadd1097.bosdata                  := bosdataadd1097
var CandleSet htfadd1098                     = CandleSet.new()
var CandleSettings SettingsHTFadd1098        = CandleSettings.new(htf="1098", max_memory=3, htfint=1098)
var Candle[] candlesadd1098                  = array.new<Candle>(0)
var BOSdata bosdataadd1098                   = BOSdata.new()
htfadd1098.settings                 := SettingsHTFadd1098
htfadd1098.candles                  := candlesadd1098
htfadd1098.bosdata                  := bosdataadd1098
var CandleSet htfadd1099                     = CandleSet.new()
var CandleSettings SettingsHTFadd1099        = CandleSettings.new(htf="1099", max_memory=3, htfint=1099)
var Candle[] candlesadd1099                  = array.new<Candle>(0)
var BOSdata bosdataadd1099                   = BOSdata.new()
htfadd1099.settings                 := SettingsHTFadd1099
htfadd1099.candles                  := candlesadd1099
htfadd1099.bosdata                  := bosdataadd1099
var CandleSet htfadd1100                     = CandleSet.new()
var CandleSettings SettingsHTFadd1100        = CandleSettings.new(htf="1100", max_memory=3, htfint=1100)
var Candle[] candlesadd1100                  = array.new<Candle>(0)
var BOSdata bosdataadd1100                   = BOSdata.new()
htfadd1100.settings                 := SettingsHTFadd1100
htfadd1100.candles                  := candlesadd1100
htfadd1100.bosdata                  := bosdataadd1100
var CandleSet htfadd1101                     = CandleSet.new()
var CandleSettings SettingsHTFadd1101        = CandleSettings.new(htf="1101", max_memory=3, htfint=1101)
var Candle[] candlesadd1101                  = array.new<Candle>(0)
var BOSdata bosdataadd1101                   = BOSdata.new()
htfadd1101.settings                 := SettingsHTFadd1101
htfadd1101.candles                  := candlesadd1101
htfadd1101.bosdata                  := bosdataadd1101
var CandleSet htfadd1102                     = CandleSet.new()
var CandleSettings SettingsHTFadd1102        = CandleSettings.new(htf="1102", max_memory=3, htfint=1102)
var Candle[] candlesadd1102                  = array.new<Candle>(0)
var BOSdata bosdataadd1102                   = BOSdata.new()
htfadd1102.settings                 := SettingsHTFadd1102
htfadd1102.candles                  := candlesadd1102
htfadd1102.bosdata                  := bosdataadd1102
var CandleSet htfadd1103                     = CandleSet.new()
var CandleSettings SettingsHTFadd1103        = CandleSettings.new(htf="1103", max_memory=3, htfint=1103)
var Candle[] candlesadd1103                  = array.new<Candle>(0)
var BOSdata bosdataadd1103                   = BOSdata.new()
htfadd1103.settings                 := SettingsHTFadd1103
htfadd1103.candles                  := candlesadd1103
htfadd1103.bosdata                  := bosdataadd1103
var CandleSet htfadd1104                     = CandleSet.new()
var CandleSettings SettingsHTFadd1104        = CandleSettings.new(htf="1104", max_memory=3, htfint=1104)
var Candle[] candlesadd1104                  = array.new<Candle>(0)
var BOSdata bosdataadd1104                   = BOSdata.new()
htfadd1104.settings                 := SettingsHTFadd1104
htfadd1104.candles                  := candlesadd1104
htfadd1104.bosdata                  := bosdataadd1104
var CandleSet htfadd1105                     = CandleSet.new()
var CandleSettings SettingsHTFadd1105        = CandleSettings.new(htf="1105", max_memory=3, htfint=1105)
var Candle[] candlesadd1105                  = array.new<Candle>(0)
var BOSdata bosdataadd1105                   = BOSdata.new()
htfadd1105.settings                 := SettingsHTFadd1105
htfadd1105.candles                  := candlesadd1105
htfadd1105.bosdata                  := bosdataadd1105
var CandleSet htfadd1106                     = CandleSet.new()
var CandleSettings SettingsHTFadd1106        = CandleSettings.new(htf="1106", max_memory=3, htfint=1106)
var Candle[] candlesadd1106                  = array.new<Candle>(0)
var BOSdata bosdataadd1106                   = BOSdata.new()
htfadd1106.settings                 := SettingsHTFadd1106
htfadd1106.candles                  := candlesadd1106
htfadd1106.bosdata                  := bosdataadd1106
var CandleSet htfadd1107                     = CandleSet.new()
var CandleSettings SettingsHTFadd1107        = CandleSettings.new(htf="1107", max_memory=3, htfint=1107)
var Candle[] candlesadd1107                  = array.new<Candle>(0)
var BOSdata bosdataadd1107                   = BOSdata.new()
htfadd1107.settings                 := SettingsHTFadd1107
htfadd1107.candles                  := candlesadd1107
htfadd1107.bosdata                  := bosdataadd1107
var CandleSet htfadd1108                     = CandleSet.new()
var CandleSettings SettingsHTFadd1108        = CandleSettings.new(htf="1108", max_memory=3, htfint=1108)
var Candle[] candlesadd1108                  = array.new<Candle>(0)
var BOSdata bosdataadd1108                   = BOSdata.new()
htfadd1108.settings                 := SettingsHTFadd1108
htfadd1108.candles                  := candlesadd1108
htfadd1108.bosdata                  := bosdataadd1108
var CandleSet htfadd1109                     = CandleSet.new()
var CandleSettings SettingsHTFadd1109        = CandleSettings.new(htf="1109", max_memory=3, htfint=1109)
var Candle[] candlesadd1109                  = array.new<Candle>(0)
var BOSdata bosdataadd1109                   = BOSdata.new()
htfadd1109.settings                 := SettingsHTFadd1109
htfadd1109.candles                  := candlesadd1109
htfadd1109.bosdata                  := bosdataadd1109
var CandleSet htfadd1110                     = CandleSet.new()
var CandleSettings SettingsHTFadd1110        = CandleSettings.new(htf="1110", max_memory=3, htfint=1110)
var Candle[] candlesadd1110                  = array.new<Candle>(0)
var BOSdata bosdataadd1110                   = BOSdata.new()
htfadd1110.settings                 := SettingsHTFadd1110
htfadd1110.candles                  := candlesadd1110
htfadd1110.bosdata                  := bosdataadd1110
var CandleSet htfadd1111                     = CandleSet.new()
var CandleSettings SettingsHTFadd1111        = CandleSettings.new(htf="1111", max_memory=3, htfint=1111)
var Candle[] candlesadd1111                  = array.new<Candle>(0)
var BOSdata bosdataadd1111                   = BOSdata.new()
htfadd1111.settings                 := SettingsHTFadd1111
htfadd1111.candles                  := candlesadd1111
htfadd1111.bosdata                  := bosdataadd1111
var CandleSet htfadd1112                     = CandleSet.new()
var CandleSettings SettingsHTFadd1112        = CandleSettings.new(htf="1112", max_memory=3, htfint=1112)
var Candle[] candlesadd1112                  = array.new<Candle>(0)
var BOSdata bosdataadd1112                   = BOSdata.new()
htfadd1112.settings                 := SettingsHTFadd1112
htfadd1112.candles                  := candlesadd1112
htfadd1112.bosdata                  := bosdataadd1112
var CandleSet htfadd1113                     = CandleSet.new()
var CandleSettings SettingsHTFadd1113        = CandleSettings.new(htf="1113", max_memory=3, htfint=1113)
var Candle[] candlesadd1113                  = array.new<Candle>(0)
var BOSdata bosdataadd1113                   = BOSdata.new()
htfadd1113.settings                 := SettingsHTFadd1113
htfadd1113.candles                  := candlesadd1113
htfadd1113.bosdata                  := bosdataadd1113
var CandleSet htfadd1114                     = CandleSet.new()
var CandleSettings SettingsHTFadd1114        = CandleSettings.new(htf="1114", max_memory=3, htfint=1114)
var Candle[] candlesadd1114                  = array.new<Candle>(0)
var BOSdata bosdataadd1114                   = BOSdata.new()
htfadd1114.settings                 := SettingsHTFadd1114
htfadd1114.candles                  := candlesadd1114
htfadd1114.bosdata                  := bosdataadd1114
var CandleSet htfadd1115                     = CandleSet.new()
var CandleSettings SettingsHTFadd1115        = CandleSettings.new(htf="1115", max_memory=3, htfint=1115)
var Candle[] candlesadd1115                  = array.new<Candle>(0)
var BOSdata bosdataadd1115                   = BOSdata.new()
htfadd1115.settings                 := SettingsHTFadd1115
htfadd1115.candles                  := candlesadd1115
htfadd1115.bosdata                  := bosdataadd1115
var CandleSet htfadd1116                     = CandleSet.new()
var CandleSettings SettingsHTFadd1116        = CandleSettings.new(htf="1116", max_memory=3, htfint=1116)
var Candle[] candlesadd1116                  = array.new<Candle>(0)
var BOSdata bosdataadd1116                   = BOSdata.new()
htfadd1116.settings                 := SettingsHTFadd1116
htfadd1116.candles                  := candlesadd1116
htfadd1116.bosdata                  := bosdataadd1116
var CandleSet htfadd1117                     = CandleSet.new()
var CandleSettings SettingsHTFadd1117        = CandleSettings.new(htf="1117", max_memory=3, htfint=1117)
var Candle[] candlesadd1117                  = array.new<Candle>(0)
var BOSdata bosdataadd1117                   = BOSdata.new()
htfadd1117.settings                 := SettingsHTFadd1117
htfadd1117.candles                  := candlesadd1117
htfadd1117.bosdata                  := bosdataadd1117
var CandleSet htfadd1118                     = CandleSet.new()
var CandleSettings SettingsHTFadd1118        = CandleSettings.new(htf="1118", max_memory=3, htfint=1118)
var Candle[] candlesadd1118                  = array.new<Candle>(0)
var BOSdata bosdataadd1118                   = BOSdata.new()
htfadd1118.settings                 := SettingsHTFadd1118
htfadd1118.candles                  := candlesadd1118
htfadd1118.bosdata                  := bosdataadd1118
var CandleSet htfadd1119                     = CandleSet.new()
var CandleSettings SettingsHTFadd1119        = CandleSettings.new(htf="1119", max_memory=3, htfint=1119)
var Candle[] candlesadd1119                  = array.new<Candle>(0)
var BOSdata bosdataadd1119                   = BOSdata.new()
htfadd1119.settings                 := SettingsHTFadd1119
htfadd1119.candles                  := candlesadd1119
htfadd1119.bosdata                  := bosdataadd1119
var CandleSet htfadd1120                     = CandleSet.new()
var CandleSettings SettingsHTFadd1120        = CandleSettings.new(htf="1120", max_memory=3, htfint=1120)
var Candle[] candlesadd1120                  = array.new<Candle>(0)
var BOSdata bosdataadd1120                   = BOSdata.new()
htfadd1120.settings                 := SettingsHTFadd1120
htfadd1120.candles                  := candlesadd1120
htfadd1120.bosdata                  := bosdataadd1120
var CandleSet htfadd1121                     = CandleSet.new()
var CandleSettings SettingsHTFadd1121        = CandleSettings.new(htf="1121", max_memory=3, htfint=1121)
var Candle[] candlesadd1121                  = array.new<Candle>(0)
var BOSdata bosdataadd1121                   = BOSdata.new()
htfadd1121.settings                 := SettingsHTFadd1121
htfadd1121.candles                  := candlesadd1121
htfadd1121.bosdata                  := bosdataadd1121
var CandleSet htfadd1122                     = CandleSet.new()
var CandleSettings SettingsHTFadd1122        = CandleSettings.new(htf="1122", max_memory=3, htfint=1122)
var Candle[] candlesadd1122                  = array.new<Candle>(0)
var BOSdata bosdataadd1122                   = BOSdata.new()
htfadd1122.settings                 := SettingsHTFadd1122
htfadd1122.candles                  := candlesadd1122
htfadd1122.bosdata                  := bosdataadd1122
var CandleSet htfadd1123                     = CandleSet.new()
var CandleSettings SettingsHTFadd1123        = CandleSettings.new(htf="1123", max_memory=3, htfint=1123)
var Candle[] candlesadd1123                  = array.new<Candle>(0)
var BOSdata bosdataadd1123                   = BOSdata.new()
htfadd1123.settings                 := SettingsHTFadd1123
htfadd1123.candles                  := candlesadd1123
htfadd1123.bosdata                  := bosdataadd1123
var CandleSet htfadd1124                     = CandleSet.new()
var CandleSettings SettingsHTFadd1124        = CandleSettings.new(htf="1124", max_memory=3, htfint=1124)
var Candle[] candlesadd1124                  = array.new<Candle>(0)
var BOSdata bosdataadd1124                   = BOSdata.new()
htfadd1124.settings                 := SettingsHTFadd1124
htfadd1124.candles                  := candlesadd1124
htfadd1124.bosdata                  := bosdataadd1124
var CandleSet htfadd1125                     = CandleSet.new()
var CandleSettings SettingsHTFadd1125        = CandleSettings.new(htf="1125", max_memory=3, htfint=1125)
var Candle[] candlesadd1125                  = array.new<Candle>(0)
var BOSdata bosdataadd1125                   = BOSdata.new()
htfadd1125.settings                 := SettingsHTFadd1125
htfadd1125.candles                  := candlesadd1125
htfadd1125.bosdata                  := bosdataadd1125
var CandleSet htfadd1126                     = CandleSet.new()
var CandleSettings SettingsHTFadd1126        = CandleSettings.new(htf="1126", max_memory=3, htfint=1126)
var Candle[] candlesadd1126                  = array.new<Candle>(0)
var BOSdata bosdataadd1126                   = BOSdata.new()
htfadd1126.settings                 := SettingsHTFadd1126
htfadd1126.candles                  := candlesadd1126
htfadd1126.bosdata                  := bosdataadd1126
var CandleSet htfadd1127                     = CandleSet.new()
var CandleSettings SettingsHTFadd1127        = CandleSettings.new(htf="1127", max_memory=3, htfint=1127)
var Candle[] candlesadd1127                  = array.new<Candle>(0)
var BOSdata bosdataadd1127                   = BOSdata.new()
htfadd1127.settings                 := SettingsHTFadd1127
htfadd1127.candles                  := candlesadd1127
htfadd1127.bosdata                  := bosdataadd1127
var CandleSet htfadd1128                     = CandleSet.new()
var CandleSettings SettingsHTFadd1128        = CandleSettings.new(htf="1128", max_memory=3, htfint=1128)
var Candle[] candlesadd1128                  = array.new<Candle>(0)
var BOSdata bosdataadd1128                   = BOSdata.new()
htfadd1128.settings                 := SettingsHTFadd1128
htfadd1128.candles                  := candlesadd1128
htfadd1128.bosdata                  := bosdataadd1128
var CandleSet htfadd1129                     = CandleSet.new()
var CandleSettings SettingsHTFadd1129        = CandleSettings.new(htf="1129", max_memory=3, htfint=1129)
var Candle[] candlesadd1129                  = array.new<Candle>(0)
var BOSdata bosdataadd1129                   = BOSdata.new()
htfadd1129.settings                 := SettingsHTFadd1129
htfadd1129.candles                  := candlesadd1129
htfadd1129.bosdata                  := bosdataadd1129
var CandleSet htfadd1130                     = CandleSet.new()
var CandleSettings SettingsHTFadd1130        = CandleSettings.new(htf="1130", max_memory=3, htfint=1130)
var Candle[] candlesadd1130                  = array.new<Candle>(0)
var BOSdata bosdataadd1130                   = BOSdata.new()
htfadd1130.settings                 := SettingsHTFadd1130
htfadd1130.candles                  := candlesadd1130
htfadd1130.bosdata                  := bosdataadd1130
var CandleSet htfadd1131                     = CandleSet.new()
var CandleSettings SettingsHTFadd1131        = CandleSettings.new(htf="1131", max_memory=3, htfint=1131)
var Candle[] candlesadd1131                  = array.new<Candle>(0)
var BOSdata bosdataadd1131                   = BOSdata.new()
htfadd1131.settings                 := SettingsHTFadd1131
htfadd1131.candles                  := candlesadd1131
htfadd1131.bosdata                  := bosdataadd1131
var CandleSet htfadd1132                     = CandleSet.new()
var CandleSettings SettingsHTFadd1132        = CandleSettings.new(htf="1132", max_memory=3, htfint=1132)
var Candle[] candlesadd1132                  = array.new<Candle>(0)
var BOSdata bosdataadd1132                   = BOSdata.new()
htfadd1132.settings                 := SettingsHTFadd1132
htfadd1132.candles                  := candlesadd1132
htfadd1132.bosdata                  := bosdataadd1132
var CandleSet htfadd1133                     = CandleSet.new()
var CandleSettings SettingsHTFadd1133        = CandleSettings.new(htf="1133", max_memory=3, htfint=1133)
var Candle[] candlesadd1133                  = array.new<Candle>(0)
var BOSdata bosdataadd1133                   = BOSdata.new()
htfadd1133.settings                 := SettingsHTFadd1133
htfadd1133.candles                  := candlesadd1133
htfadd1133.bosdata                  := bosdataadd1133
var CandleSet htfadd1134                     = CandleSet.new()
var CandleSettings SettingsHTFadd1134        = CandleSettings.new(htf="1134", max_memory=3, htfint=1134)
var Candle[] candlesadd1134                  = array.new<Candle>(0)
var BOSdata bosdataadd1134                   = BOSdata.new()
htfadd1134.settings                 := SettingsHTFadd1134
htfadd1134.candles                  := candlesadd1134
htfadd1134.bosdata                  := bosdataadd1134
var CandleSet htfadd1135                     = CandleSet.new()
var CandleSettings SettingsHTFadd1135        = CandleSettings.new(htf="1135", max_memory=3, htfint=1135)
var Candle[] candlesadd1135                  = array.new<Candle>(0)
var BOSdata bosdataadd1135                   = BOSdata.new()
htfadd1135.settings                 := SettingsHTFadd1135
htfadd1135.candles                  := candlesadd1135
htfadd1135.bosdata                  := bosdataadd1135
var CandleSet htfadd1136                     = CandleSet.new()
var CandleSettings SettingsHTFadd1136        = CandleSettings.new(htf="1136", max_memory=3, htfint=1136)
var Candle[] candlesadd1136                  = array.new<Candle>(0)
var BOSdata bosdataadd1136                   = BOSdata.new()
htfadd1136.settings                 := SettingsHTFadd1136
htfadd1136.candles                  := candlesadd1136
htfadd1136.bosdata                  := bosdataadd1136
var CandleSet htfadd1137                     = CandleSet.new()
var CandleSettings SettingsHTFadd1137        = CandleSettings.new(htf="1137", max_memory=3, htfint=1137)
var Candle[] candlesadd1137                  = array.new<Candle>(0)
var BOSdata bosdataadd1137                   = BOSdata.new()
htfadd1137.settings                 := SettingsHTFadd1137
htfadd1137.candles                  := candlesadd1137
htfadd1137.bosdata                  := bosdataadd1137
var CandleSet htfadd1138                     = CandleSet.new()
var CandleSettings SettingsHTFadd1138        = CandleSettings.new(htf="1138", max_memory=3, htfint=1138)
var Candle[] candlesadd1138                  = array.new<Candle>(0)
var BOSdata bosdataadd1138                   = BOSdata.new()
htfadd1138.settings                 := SettingsHTFadd1138
htfadd1138.candles                  := candlesadd1138
htfadd1138.bosdata                  := bosdataadd1138
var CandleSet htfadd1139                     = CandleSet.new()
var CandleSettings SettingsHTFadd1139        = CandleSettings.new(htf="1139", max_memory=3, htfint=1139)
var Candle[] candlesadd1139                  = array.new<Candle>(0)
var BOSdata bosdataadd1139                   = BOSdata.new()
htfadd1139.settings                 := SettingsHTFadd1139
htfadd1139.candles                  := candlesadd1139
htfadd1139.bosdata                  := bosdataadd1139
var CandleSet htfadd1140                     = CandleSet.new()
var CandleSettings SettingsHTFadd1140        = CandleSettings.new(htf="1140", max_memory=3, htfint=1140)
var Candle[] candlesadd1140                  = array.new<Candle>(0)
var BOSdata bosdataadd1140                   = BOSdata.new()
htfadd1140.settings                 := SettingsHTFadd1140
htfadd1140.candles                  := candlesadd1140
htfadd1140.bosdata                  := bosdataadd1140
var CandleSet htfadd1141                     = CandleSet.new()
var CandleSettings SettingsHTFadd1141        = CandleSettings.new(htf="1141", max_memory=3, htfint=1141)
var Candle[] candlesadd1141                  = array.new<Candle>(0)
var BOSdata bosdataadd1141                   = BOSdata.new()
htfadd1141.settings                 := SettingsHTFadd1141
htfadd1141.candles                  := candlesadd1141
htfadd1141.bosdata                  := bosdataadd1141
var CandleSet htfadd1142                     = CandleSet.new()
var CandleSettings SettingsHTFadd1142        = CandleSettings.new(htf="1142", max_memory=3, htfint=1142)
var Candle[] candlesadd1142                  = array.new<Candle>(0)
var BOSdata bosdataadd1142                   = BOSdata.new()
htfadd1142.settings                 := SettingsHTFadd1142
htfadd1142.candles                  := candlesadd1142
htfadd1142.bosdata                  := bosdataadd1142
var CandleSet htfadd1143                     = CandleSet.new()
var CandleSettings SettingsHTFadd1143        = CandleSettings.new(htf="1143", max_memory=3, htfint=1143)
var Candle[] candlesadd1143                  = array.new<Candle>(0)
var BOSdata bosdataadd1143                   = BOSdata.new()
htfadd1143.settings                 := SettingsHTFadd1143
htfadd1143.candles                  := candlesadd1143
htfadd1143.bosdata                  := bosdataadd1143
var CandleSet htfadd1144                     = CandleSet.new()
var CandleSettings SettingsHTFadd1144        = CandleSettings.new(htf="1144", max_memory=3, htfint=1144)
var Candle[] candlesadd1144                  = array.new<Candle>(0)
var BOSdata bosdataadd1144                   = BOSdata.new()
htfadd1144.settings                 := SettingsHTFadd1144
htfadd1144.candles                  := candlesadd1144
htfadd1144.bosdata                  := bosdataadd1144
var CandleSet htfadd1145                     = CandleSet.new()
var CandleSettings SettingsHTFadd1145        = CandleSettings.new(htf="1145", max_memory=3, htfint=1145)
var Candle[] candlesadd1145                  = array.new<Candle>(0)
var BOSdata bosdataadd1145                   = BOSdata.new()
htfadd1145.settings                 := SettingsHTFadd1145
htfadd1145.candles                  := candlesadd1145
htfadd1145.bosdata                  := bosdataadd1145
var CandleSet htfadd1146                     = CandleSet.new()
var CandleSettings SettingsHTFadd1146        = CandleSettings.new(htf="1146", max_memory=3, htfint=1146)
var Candle[] candlesadd1146                  = array.new<Candle>(0)
var BOSdata bosdataadd1146                   = BOSdata.new()
htfadd1146.settings                 := SettingsHTFadd1146
htfadd1146.candles                  := candlesadd1146
htfadd1146.bosdata                  := bosdataadd1146
var CandleSet htfadd1147                     = CandleSet.new()
var CandleSettings SettingsHTFadd1147        = CandleSettings.new(htf="1147", max_memory=3, htfint=1147)
var Candle[] candlesadd1147                  = array.new<Candle>(0)
var BOSdata bosdataadd1147                   = BOSdata.new()
htfadd1147.settings                 := SettingsHTFadd1147
htfadd1147.candles                  := candlesadd1147
htfadd1147.bosdata                  := bosdataadd1147
var CandleSet htfadd1148                     = CandleSet.new()
var CandleSettings SettingsHTFadd1148        = CandleSettings.new(htf="1148", max_memory=3, htfint=1148)
var Candle[] candlesadd1148                  = array.new<Candle>(0)
var BOSdata bosdataadd1148                   = BOSdata.new()
htfadd1148.settings                 := SettingsHTFadd1148
htfadd1148.candles                  := candlesadd1148
htfadd1148.bosdata                  := bosdataadd1148
var CandleSet htfadd1149                     = CandleSet.new()
var CandleSettings SettingsHTFadd1149        = CandleSettings.new(htf="1149", max_memory=3, htfint=1149)
var Candle[] candlesadd1149                  = array.new<Candle>(0)
var BOSdata bosdataadd1149                   = BOSdata.new()
htfadd1149.settings                 := SettingsHTFadd1149
htfadd1149.candles                  := candlesadd1149
htfadd1149.bosdata                  := bosdataadd1149
var CandleSet htfadd1150                     = CandleSet.new()
var CandleSettings SettingsHTFadd1150        = CandleSettings.new(htf="1150", max_memory=3, htfint=1150)
var Candle[] candlesadd1150                  = array.new<Candle>(0)
var BOSdata bosdataadd1150                   = BOSdata.new()
htfadd1150.settings                 := SettingsHTFadd1150
htfadd1150.candles                  := candlesadd1150
htfadd1150.bosdata                  := bosdataadd1150
var CandleSet htfadd1151                     = CandleSet.new()
var CandleSettings SettingsHTFadd1151        = CandleSettings.new(htf="1151", max_memory=3, htfint=1151)
var Candle[] candlesadd1151                  = array.new<Candle>(0)
var BOSdata bosdataadd1151                   = BOSdata.new()
htfadd1151.settings                 := SettingsHTFadd1151
htfadd1151.candles                  := candlesadd1151
htfadd1151.bosdata                  := bosdataadd1151
var CandleSet htfadd1152                     = CandleSet.new()
var CandleSettings SettingsHTFadd1152        = CandleSettings.new(htf="1152", max_memory=3, htfint=1152)
var Candle[] candlesadd1152                  = array.new<Candle>(0)
var BOSdata bosdataadd1152                   = BOSdata.new()
htfadd1152.settings                 := SettingsHTFadd1152
htfadd1152.candles                  := candlesadd1152
htfadd1152.bosdata                  := bosdataadd1152
var CandleSet htfadd1153                     = CandleSet.new()
var CandleSettings SettingsHTFadd1153        = CandleSettings.new(htf="1153", max_memory=3, htfint=1153)
var Candle[] candlesadd1153                  = array.new<Candle>(0)
var BOSdata bosdataadd1153                   = BOSdata.new()
htfadd1153.settings                 := SettingsHTFadd1153
htfadd1153.candles                  := candlesadd1153
htfadd1153.bosdata                  := bosdataadd1153
var CandleSet htfadd1154                     = CandleSet.new()
var CandleSettings SettingsHTFadd1154        = CandleSettings.new(htf="1154", max_memory=3, htfint=1154)
var Candle[] candlesadd1154                  = array.new<Candle>(0)
var BOSdata bosdataadd1154                   = BOSdata.new()
htfadd1154.settings                 := SettingsHTFadd1154
htfadd1154.candles                  := candlesadd1154
htfadd1154.bosdata                  := bosdataadd1154
var CandleSet htfadd1155                     = CandleSet.new()
var CandleSettings SettingsHTFadd1155        = CandleSettings.new(htf="1155", max_memory=3, htfint=1155)
var Candle[] candlesadd1155                  = array.new<Candle>(0)
var BOSdata bosdataadd1155                   = BOSdata.new()
htfadd1155.settings                 := SettingsHTFadd1155
htfadd1155.candles                  := candlesadd1155
htfadd1155.bosdata                  := bosdataadd1155
var CandleSet htfadd1156                     = CandleSet.new()
var CandleSettings SettingsHTFadd1156        = CandleSettings.new(htf="1156", max_memory=3, htfint=1156)
var Candle[] candlesadd1156                  = array.new<Candle>(0)
var BOSdata bosdataadd1156                   = BOSdata.new()
htfadd1156.settings                 := SettingsHTFadd1156
htfadd1156.candles                  := candlesadd1156
htfadd1156.bosdata                  := bosdataadd1156
var CandleSet htfadd1157                     = CandleSet.new()
var CandleSettings SettingsHTFadd1157        = CandleSettings.new(htf="1157", max_memory=3, htfint=1157)
var Candle[] candlesadd1157                  = array.new<Candle>(0)
var BOSdata bosdataadd1157                   = BOSdata.new()
htfadd1157.settings                 := SettingsHTFadd1157
htfadd1157.candles                  := candlesadd1157
htfadd1157.bosdata                  := bosdataadd1157
var CandleSet htfadd1158                     = CandleSet.new()
var CandleSettings SettingsHTFadd1158        = CandleSettings.new(htf="1158", max_memory=3, htfint=1158)
var Candle[] candlesadd1158                  = array.new<Candle>(0)
var BOSdata bosdataadd1158                   = BOSdata.new()
htfadd1158.settings                 := SettingsHTFadd1158
htfadd1158.candles                  := candlesadd1158
htfadd1158.bosdata                  := bosdataadd1158
var CandleSet htfadd1159                     = CandleSet.new()
var CandleSettings SettingsHTFadd1159        = CandleSettings.new(htf="1159", max_memory=3, htfint=1159)
var Candle[] candlesadd1159                  = array.new<Candle>(0)
var BOSdata bosdataadd1159                   = BOSdata.new()
htfadd1159.settings                 := SettingsHTFadd1159
htfadd1159.candles                  := candlesadd1159
htfadd1159.bosdata                  := bosdataadd1159
var CandleSet htfadd1160                     = CandleSet.new()
var CandleSettings SettingsHTFadd1160        = CandleSettings.new(htf="1160", max_memory=3, htfint=1160)
var Candle[] candlesadd1160                  = array.new<Candle>(0)
var BOSdata bosdataadd1160                   = BOSdata.new()
htfadd1160.settings                 := SettingsHTFadd1160
htfadd1160.candles                  := candlesadd1160
htfadd1160.bosdata                  := bosdataadd1160
var CandleSet htfadd1161                     = CandleSet.new()
var CandleSettings SettingsHTFadd1161        = CandleSettings.new(htf="1161", max_memory=3, htfint=1161)
var Candle[] candlesadd1161                  = array.new<Candle>(0)
var BOSdata bosdataadd1161                   = BOSdata.new()
htfadd1161.settings                 := SettingsHTFadd1161
htfadd1161.candles                  := candlesadd1161
htfadd1161.bosdata                  := bosdataadd1161
var CandleSet htfadd1162                     = CandleSet.new()
var CandleSettings SettingsHTFadd1162        = CandleSettings.new(htf="1162", max_memory=3, htfint=1162)
var Candle[] candlesadd1162                  = array.new<Candle>(0)
var BOSdata bosdataadd1162                   = BOSdata.new()
htfadd1162.settings                 := SettingsHTFadd1162
htfadd1162.candles                  := candlesadd1162
htfadd1162.bosdata                  := bosdataadd1162
var CandleSet htfadd1163                     = CandleSet.new()
var CandleSettings SettingsHTFadd1163        = CandleSettings.new(htf="1163", max_memory=3, htfint=1163)
var Candle[] candlesadd1163                  = array.new<Candle>(0)
var BOSdata bosdataadd1163                   = BOSdata.new()
htfadd1163.settings                 := SettingsHTFadd1163
htfadd1163.candles                  := candlesadd1163
htfadd1163.bosdata                  := bosdataadd1163
var CandleSet htfadd1164                     = CandleSet.new()
var CandleSettings SettingsHTFadd1164        = CandleSettings.new(htf="1164", max_memory=3, htfint=1164)
var Candle[] candlesadd1164                  = array.new<Candle>(0)
var BOSdata bosdataadd1164                   = BOSdata.new()
htfadd1164.settings                 := SettingsHTFadd1164
htfadd1164.candles                  := candlesadd1164
htfadd1164.bosdata                  := bosdataadd1164
var CandleSet htfadd1165                     = CandleSet.new()
var CandleSettings SettingsHTFadd1165        = CandleSettings.new(htf="1165", max_memory=3, htfint=1165)
var Candle[] candlesadd1165                  = array.new<Candle>(0)
var BOSdata bosdataadd1165                   = BOSdata.new()
htfadd1165.settings                 := SettingsHTFadd1165
htfadd1165.candles                  := candlesadd1165
htfadd1165.bosdata                  := bosdataadd1165
var CandleSet htfadd1166                     = CandleSet.new()
var CandleSettings SettingsHTFadd1166        = CandleSettings.new(htf="1166", max_memory=3, htfint=1166)
var Candle[] candlesadd1166                  = array.new<Candle>(0)
var BOSdata bosdataadd1166                   = BOSdata.new()
htfadd1166.settings                 := SettingsHTFadd1166
htfadd1166.candles                  := candlesadd1166
htfadd1166.bosdata                  := bosdataadd1166
var CandleSet htfadd1167                     = CandleSet.new()
var CandleSettings SettingsHTFadd1167        = CandleSettings.new(htf="1167", max_memory=3, htfint=1167)
var Candle[] candlesadd1167                  = array.new<Candle>(0)
var BOSdata bosdataadd1167                   = BOSdata.new()
htfadd1167.settings                 := SettingsHTFadd1167
htfadd1167.candles                  := candlesadd1167
htfadd1167.bosdata                  := bosdataadd1167
var CandleSet htfadd1168                     = CandleSet.new()
var CandleSettings SettingsHTFadd1168        = CandleSettings.new(htf="1168", max_memory=3, htfint=1168)
var Candle[] candlesadd1168                  = array.new<Candle>(0)
var BOSdata bosdataadd1168                   = BOSdata.new()
htfadd1168.settings                 := SettingsHTFadd1168
htfadd1168.candles                  := candlesadd1168
htfadd1168.bosdata                  := bosdataadd1168
var CandleSet htfadd1169                     = CandleSet.new()
var CandleSettings SettingsHTFadd1169        = CandleSettings.new(htf="1169", max_memory=3, htfint=1169)
var Candle[] candlesadd1169                  = array.new<Candle>(0)
var BOSdata bosdataadd1169                   = BOSdata.new()
htfadd1169.settings                 := SettingsHTFadd1169
htfadd1169.candles                  := candlesadd1169
htfadd1169.bosdata                  := bosdataadd1169
var CandleSet htfadd1170                     = CandleSet.new()
var CandleSettings SettingsHTFadd1170        = CandleSettings.new(htf="1170", max_memory=3, htfint=1170)
var Candle[] candlesadd1170                  = array.new<Candle>(0)
var BOSdata bosdataadd1170                   = BOSdata.new()
htfadd1170.settings                 := SettingsHTFadd1170
htfadd1170.candles                  := candlesadd1170
htfadd1170.bosdata                  := bosdataadd1170
var CandleSet htfadd1171                     = CandleSet.new()
var CandleSettings SettingsHTFadd1171        = CandleSettings.new(htf="1171", max_memory=3, htfint=1171)
var Candle[] candlesadd1171                  = array.new<Candle>(0)
var BOSdata bosdataadd1171                   = BOSdata.new()
htfadd1171.settings                 := SettingsHTFadd1171
htfadd1171.candles                  := candlesadd1171
htfadd1171.bosdata                  := bosdataadd1171
var CandleSet htfadd1172                     = CandleSet.new()
var CandleSettings SettingsHTFadd1172        = CandleSettings.new(htf="1172", max_memory=3, htfint=1172)
var Candle[] candlesadd1172                  = array.new<Candle>(0)
var BOSdata bosdataadd1172                   = BOSdata.new()
htfadd1172.settings                 := SettingsHTFadd1172
htfadd1172.candles                  := candlesadd1172
htfadd1172.bosdata                  := bosdataadd1172
var CandleSet htfadd1173                     = CandleSet.new()
var CandleSettings SettingsHTFadd1173        = CandleSettings.new(htf="1173", max_memory=3, htfint=1173)
var Candle[] candlesadd1173                  = array.new<Candle>(0)
var BOSdata bosdataadd1173                   = BOSdata.new()
htfadd1173.settings                 := SettingsHTFadd1173
htfadd1173.candles                  := candlesadd1173
htfadd1173.bosdata                  := bosdataadd1173
var CandleSet htfadd1174                     = CandleSet.new()
var CandleSettings SettingsHTFadd1174        = CandleSettings.new(htf="1174", max_memory=3, htfint=1174)
var Candle[] candlesadd1174                  = array.new<Candle>(0)
var BOSdata bosdataadd1174                   = BOSdata.new()
htfadd1174.settings                 := SettingsHTFadd1174
htfadd1174.candles                  := candlesadd1174
htfadd1174.bosdata                  := bosdataadd1174
var CandleSet htfadd1175                     = CandleSet.new()
var CandleSettings SettingsHTFadd1175        = CandleSettings.new(htf="1175", max_memory=3, htfint=1175)
var Candle[] candlesadd1175                  = array.new<Candle>(0)
var BOSdata bosdataadd1175                   = BOSdata.new()
htfadd1175.settings                 := SettingsHTFadd1175
htfadd1175.candles                  := candlesadd1175
htfadd1175.bosdata                  := bosdataadd1175
var CandleSet htfadd1176                     = CandleSet.new()
var CandleSettings SettingsHTFadd1176        = CandleSettings.new(htf="1176", max_memory=3, htfint=1176)
var Candle[] candlesadd1176                  = array.new<Candle>(0)
var BOSdata bosdataadd1176                   = BOSdata.new()
htfadd1176.settings                 := SettingsHTFadd1176
htfadd1176.candles                  := candlesadd1176
htfadd1176.bosdata                  := bosdataadd1176
var CandleSet htfadd1177                     = CandleSet.new()
var CandleSettings SettingsHTFadd1177        = CandleSettings.new(htf="1177", max_memory=3, htfint=1177)
var Candle[] candlesadd1177                  = array.new<Candle>(0)
var BOSdata bosdataadd1177                   = BOSdata.new()
htfadd1177.settings                 := SettingsHTFadd1177
htfadd1177.candles                  := candlesadd1177
htfadd1177.bosdata                  := bosdataadd1177
var CandleSet htfadd1178                     = CandleSet.new()
var CandleSettings SettingsHTFadd1178        = CandleSettings.new(htf="1178", max_memory=3, htfint=1178)
var Candle[] candlesadd1178                  = array.new<Candle>(0)
var BOSdata bosdataadd1178                   = BOSdata.new()
htfadd1178.settings                 := SettingsHTFadd1178
htfadd1178.candles                  := candlesadd1178
htfadd1178.bosdata                  := bosdataadd1178
var CandleSet htfadd1179                     = CandleSet.new()
var CandleSettings SettingsHTFadd1179        = CandleSettings.new(htf="1179", max_memory=3, htfint=1179)
var Candle[] candlesadd1179                  = array.new<Candle>(0)
var BOSdata bosdataadd1179                   = BOSdata.new()
htfadd1179.settings                 := SettingsHTFadd1179
htfadd1179.candles                  := candlesadd1179
htfadd1179.bosdata                  := bosdataadd1179
var CandleSet htfadd1180                     = CandleSet.new()
var CandleSettings SettingsHTFadd1180        = CandleSettings.new(htf="1180", max_memory=3, htfint=1180)
var Candle[] candlesadd1180                  = array.new<Candle>(0)
var BOSdata bosdataadd1180                   = BOSdata.new()
htfadd1180.settings                 := SettingsHTFadd1180
htfadd1180.candles                  := candlesadd1180
htfadd1180.bosdata                  := bosdataadd1180
var CandleSet htfadd1181                     = CandleSet.new()
var CandleSettings SettingsHTFadd1181        = CandleSettings.new(htf="1181", max_memory=3, htfint=1181)
var Candle[] candlesadd1181                  = array.new<Candle>(0)
var BOSdata bosdataadd1181                   = BOSdata.new()
htfadd1181.settings                 := SettingsHTFadd1181
htfadd1181.candles                  := candlesadd1181
htfadd1181.bosdata                  := bosdataadd1181
var CandleSet htfadd1182                     = CandleSet.new()
var CandleSettings SettingsHTFadd1182        = CandleSettings.new(htf="1182", max_memory=3, htfint=1182)
var Candle[] candlesadd1182                  = array.new<Candle>(0)
var BOSdata bosdataadd1182                   = BOSdata.new()
htfadd1182.settings                 := SettingsHTFadd1182
htfadd1182.candles                  := candlesadd1182
htfadd1182.bosdata                  := bosdataadd1182
var CandleSet htfadd1183                     = CandleSet.new()
var CandleSettings SettingsHTFadd1183        = CandleSettings.new(htf="1183", max_memory=3, htfint=1183)
var Candle[] candlesadd1183                  = array.new<Candle>(0)
var BOSdata bosdataadd1183                   = BOSdata.new()
htfadd1183.settings                 := SettingsHTFadd1183
htfadd1183.candles                  := candlesadd1183
htfadd1183.bosdata                  := bosdataadd1183
var CandleSet htfadd1184                     = CandleSet.new()
var CandleSettings SettingsHTFadd1184        = CandleSettings.new(htf="1184", max_memory=3, htfint=1184)
var Candle[] candlesadd1184                  = array.new<Candle>(0)
var BOSdata bosdataadd1184                   = BOSdata.new()
htfadd1184.settings                 := SettingsHTFadd1184
htfadd1184.candles                  := candlesadd1184
htfadd1184.bosdata                  := bosdataadd1184
var CandleSet htfadd1185                     = CandleSet.new()
var CandleSettings SettingsHTFadd1185        = CandleSettings.new(htf="1185", max_memory=3, htfint=1185)
var Candle[] candlesadd1185                  = array.new<Candle>(0)
var BOSdata bosdataadd1185                   = BOSdata.new()
htfadd1185.settings                 := SettingsHTFadd1185
htfadd1185.candles                  := candlesadd1185
htfadd1185.bosdata                  := bosdataadd1185
var CandleSet htfadd1186                     = CandleSet.new()
var CandleSettings SettingsHTFadd1186        = CandleSettings.new(htf="1186", max_memory=3, htfint=1186)
var Candle[] candlesadd1186                  = array.new<Candle>(0)
var BOSdata bosdataadd1186                   = BOSdata.new()
htfadd1186.settings                 := SettingsHTFadd1186
htfadd1186.candles                  := candlesadd1186
htfadd1186.bosdata                  := bosdataadd1186
var CandleSet htfadd1187                     = CandleSet.new()
var CandleSettings SettingsHTFadd1187        = CandleSettings.new(htf="1187", max_memory=3, htfint=1187)
var Candle[] candlesadd1187                  = array.new<Candle>(0)
var BOSdata bosdataadd1187                   = BOSdata.new()
htfadd1187.settings                 := SettingsHTFadd1187
htfadd1187.candles                  := candlesadd1187
htfadd1187.bosdata                  := bosdataadd1187
var CandleSet htfadd1188                     = CandleSet.new()
var CandleSettings SettingsHTFadd1188        = CandleSettings.new(htf="1188", max_memory=3, htfint=1188)
var Candle[] candlesadd1188                  = array.new<Candle>(0)
var BOSdata bosdataadd1188                   = BOSdata.new()
htfadd1188.settings                 := SettingsHTFadd1188
htfadd1188.candles                  := candlesadd1188
htfadd1188.bosdata                  := bosdataadd1188
var CandleSet htfadd1189                     = CandleSet.new()
var CandleSettings SettingsHTFadd1189        = CandleSettings.new(htf="1189", max_memory=3, htfint=1189)
var Candle[] candlesadd1189                  = array.new<Candle>(0)
var BOSdata bosdataadd1189                   = BOSdata.new()
htfadd1189.settings                 := SettingsHTFadd1189
htfadd1189.candles                  := candlesadd1189
htfadd1189.bosdata                  := bosdataadd1189
var CandleSet htfadd1190                     = CandleSet.new()
var CandleSettings SettingsHTFadd1190        = CandleSettings.new(htf="1190", max_memory=3, htfint=1190)
var Candle[] candlesadd1190                  = array.new<Candle>(0)
var BOSdata bosdataadd1190                   = BOSdata.new()
htfadd1190.settings                 := SettingsHTFadd1190
htfadd1190.candles                  := candlesadd1190
htfadd1190.bosdata                  := bosdataadd1190
var CandleSet htfadd1191                     = CandleSet.new()
var CandleSettings SettingsHTFadd1191        = CandleSettings.new(htf="1191", max_memory=3, htfint=1191)
var Candle[] candlesadd1191                  = array.new<Candle>(0)
var BOSdata bosdataadd1191                   = BOSdata.new()
htfadd1191.settings                 := SettingsHTFadd1191
htfadd1191.candles                  := candlesadd1191
htfadd1191.bosdata                  := bosdataadd1191
var CandleSet htfadd1192                     = CandleSet.new()
var CandleSettings SettingsHTFadd1192        = CandleSettings.new(htf="1192", max_memory=3, htfint=1192)
var Candle[] candlesadd1192                  = array.new<Candle>(0)
var BOSdata bosdataadd1192                   = BOSdata.new()
htfadd1192.settings                 := SettingsHTFadd1192
htfadd1192.candles                  := candlesadd1192
htfadd1192.bosdata                  := bosdataadd1192
var CandleSet htfadd1193                     = CandleSet.new()
var CandleSettings SettingsHTFadd1193        = CandleSettings.new(htf="1193", max_memory=3, htfint=1193)
var Candle[] candlesadd1193                  = array.new<Candle>(0)
var BOSdata bosdataadd1193                   = BOSdata.new()
htfadd1193.settings                 := SettingsHTFadd1193
htfadd1193.candles                  := candlesadd1193
htfadd1193.bosdata                  := bosdataadd1193
var CandleSet htfadd1194                     = CandleSet.new()
var CandleSettings SettingsHTFadd1194        = CandleSettings.new(htf="1194", max_memory=3, htfint=1194)
var Candle[] candlesadd1194                  = array.new<Candle>(0)
var BOSdata bosdataadd1194                   = BOSdata.new()
htfadd1194.settings                 := SettingsHTFadd1194
htfadd1194.candles                  := candlesadd1194
htfadd1194.bosdata                  := bosdataadd1194
var CandleSet htfadd1195                     = CandleSet.new()
var CandleSettings SettingsHTFadd1195        = CandleSettings.new(htf="1195", max_memory=3, htfint=1195)
var Candle[] candlesadd1195                  = array.new<Candle>(0)
var BOSdata bosdataadd1195                   = BOSdata.new()
htfadd1195.settings                 := SettingsHTFadd1195
htfadd1195.candles                  := candlesadd1195
htfadd1195.bosdata                  := bosdataadd1195
var CandleSet htfadd1196                     = CandleSet.new()
var CandleSettings SettingsHTFadd1196        = CandleSettings.new(htf="1196", max_memory=3, htfint=1196)
var Candle[] candlesadd1196                  = array.new<Candle>(0)
var BOSdata bosdataadd1196                   = BOSdata.new()
htfadd1196.settings                 := SettingsHTFadd1196
htfadd1196.candles                  := candlesadd1196
htfadd1196.bosdata                  := bosdataadd1196
var CandleSet htfadd1197                     = CandleSet.new()
var CandleSettings SettingsHTFadd1197        = CandleSettings.new(htf="1197", max_memory=3, htfint=1197)
var Candle[] candlesadd1197                  = array.new<Candle>(0)
var BOSdata bosdataadd1197                   = BOSdata.new()
htfadd1197.settings                 := SettingsHTFadd1197
htfadd1197.candles                  := candlesadd1197
htfadd1197.bosdata                  := bosdataadd1197
var CandleSet htfadd1198                     = CandleSet.new()
var CandleSettings SettingsHTFadd1198        = CandleSettings.new(htf="1198", max_memory=3, htfint=1198)
var Candle[] candlesadd1198                  = array.new<Candle>(0)
var BOSdata bosdataadd1198                   = BOSdata.new()
htfadd1198.settings                 := SettingsHTFadd1198
htfadd1198.candles                  := candlesadd1198
htfadd1198.bosdata                  := bosdataadd1198
var CandleSet htfadd1199                     = CandleSet.new()
var CandleSettings SettingsHTFadd1199        = CandleSettings.new(htf="1199", max_memory=3, htfint=1199)
var Candle[] candlesadd1199                  = array.new<Candle>(0)
var BOSdata bosdataadd1199                   = BOSdata.new()
htfadd1199.settings                 := SettingsHTFadd1199
htfadd1199.candles                  := candlesadd1199
htfadd1199.bosdata                  := bosdataadd1199
var CandleSet htfadd1200                     = CandleSet.new()
var CandleSettings SettingsHTFadd1200        = CandleSettings.new(htf="1200", max_memory=3, htfint=1200)
var Candle[] candlesadd1200                  = array.new<Candle>(0)
var BOSdata bosdataadd1200                   = BOSdata.new()
htfadd1200.settings                 := SettingsHTFadd1200
htfadd1200.candles                  := candlesadd1200
htfadd1200.bosdata                  := bosdataadd1200
var CandleSet htfadd1201                     = CandleSet.new()
var CandleSettings SettingsHTFadd1201        = CandleSettings.new(htf="1201", max_memory=3, htfint=1201)
var Candle[] candlesadd1201                  = array.new<Candle>(0)
var BOSdata bosdataadd1201                   = BOSdata.new()
htfadd1201.settings                 := SettingsHTFadd1201
htfadd1201.candles                  := candlesadd1201
htfadd1201.bosdata                  := bosdataadd1201
var CandleSet htfadd1202                     = CandleSet.new()
var CandleSettings SettingsHTFadd1202        = CandleSettings.new(htf="1202", max_memory=3, htfint=1202)
var Candle[] candlesadd1202                  = array.new<Candle>(0)
var BOSdata bosdataadd1202                   = BOSdata.new()
htfadd1202.settings                 := SettingsHTFadd1202
htfadd1202.candles                  := candlesadd1202
htfadd1202.bosdata                  := bosdataadd1202
var CandleSet htfadd1203                     = CandleSet.new()
var CandleSettings SettingsHTFadd1203        = CandleSettings.new(htf="1203", max_memory=3, htfint=1203)
var Candle[] candlesadd1203                  = array.new<Candle>(0)
var BOSdata bosdataadd1203                   = BOSdata.new()
htfadd1203.settings                 := SettingsHTFadd1203
htfadd1203.candles                  := candlesadd1203
htfadd1203.bosdata                  := bosdataadd1203
var CandleSet htfadd1204                     = CandleSet.new()
var CandleSettings SettingsHTFadd1204        = CandleSettings.new(htf="1204", max_memory=3, htfint=1204)
var Candle[] candlesadd1204                  = array.new<Candle>(0)
var BOSdata bosdataadd1204                   = BOSdata.new()
htfadd1204.settings                 := SettingsHTFadd1204
htfadd1204.candles                  := candlesadd1204
htfadd1204.bosdata                  := bosdataadd1204
var CandleSet htfadd1205                     = CandleSet.new()
var CandleSettings SettingsHTFadd1205        = CandleSettings.new(htf="1205", max_memory=3, htfint=1205)
var Candle[] candlesadd1205                  = array.new<Candle>(0)
var BOSdata bosdataadd1205                   = BOSdata.new()
htfadd1205.settings                 := SettingsHTFadd1205
htfadd1205.candles                  := candlesadd1205
htfadd1205.bosdata                  := bosdataadd1205
var CandleSet htfadd1206                     = CandleSet.new()
var CandleSettings SettingsHTFadd1206        = CandleSettings.new(htf="1206", max_memory=3, htfint=1206)
var Candle[] candlesadd1206                  = array.new<Candle>(0)
var BOSdata bosdataadd1206                   = BOSdata.new()
htfadd1206.settings                 := SettingsHTFadd1206
htfadd1206.candles                  := candlesadd1206
htfadd1206.bosdata                  := bosdataadd1206
var CandleSet htfadd1207                     = CandleSet.new()
var CandleSettings SettingsHTFadd1207        = CandleSettings.new(htf="1207", max_memory=3, htfint=1207)
var Candle[] candlesadd1207                  = array.new<Candle>(0)
var BOSdata bosdataadd1207                   = BOSdata.new()
htfadd1207.settings                 := SettingsHTFadd1207
htfadd1207.candles                  := candlesadd1207
htfadd1207.bosdata                  := bosdataadd1207
var CandleSet htfadd1208                     = CandleSet.new()
var CandleSettings SettingsHTFadd1208        = CandleSettings.new(htf="1208", max_memory=3, htfint=1208)
var Candle[] candlesadd1208                  = array.new<Candle>(0)
var BOSdata bosdataadd1208                   = BOSdata.new()
htfadd1208.settings                 := SettingsHTFadd1208
htfadd1208.candles                  := candlesadd1208
htfadd1208.bosdata                  := bosdataadd1208
var CandleSet htfadd1209                     = CandleSet.new()
var CandleSettings SettingsHTFadd1209        = CandleSettings.new(htf="1209", max_memory=3, htfint=1209)
var Candle[] candlesadd1209                  = array.new<Candle>(0)
var BOSdata bosdataadd1209                   = BOSdata.new()
htfadd1209.settings                 := SettingsHTFadd1209
htfadd1209.candles                  := candlesadd1209
htfadd1209.bosdata                  := bosdataadd1209
var CandleSet htfadd1210                     = CandleSet.new()
var CandleSettings SettingsHTFadd1210        = CandleSettings.new(htf="1210", max_memory=3, htfint=1210)
var Candle[] candlesadd1210                  = array.new<Candle>(0)
var BOSdata bosdataadd1210                   = BOSdata.new()
htfadd1210.settings                 := SettingsHTFadd1210
htfadd1210.candles                  := candlesadd1210
htfadd1210.bosdata                  := bosdataadd1210
var CandleSet htfadd1211                     = CandleSet.new()
var CandleSettings SettingsHTFadd1211        = CandleSettings.new(htf="1211", max_memory=3, htfint=1211)
var Candle[] candlesadd1211                  = array.new<Candle>(0)
var BOSdata bosdataadd1211                   = BOSdata.new()
htfadd1211.settings                 := SettingsHTFadd1211
htfadd1211.candles                  := candlesadd1211
htfadd1211.bosdata                  := bosdataadd1211
var CandleSet htfadd1212                     = CandleSet.new()
var CandleSettings SettingsHTFadd1212        = CandleSettings.new(htf="1212", max_memory=3, htfint=1212)
var Candle[] candlesadd1212                  = array.new<Candle>(0)
var BOSdata bosdataadd1212                   = BOSdata.new()
htfadd1212.settings                 := SettingsHTFadd1212
htfadd1212.candles                  := candlesadd1212
htfadd1212.bosdata                  := bosdataadd1212
var CandleSet htfadd1213                     = CandleSet.new()
var CandleSettings SettingsHTFadd1213        = CandleSettings.new(htf="1213", max_memory=3, htfint=1213)
var Candle[] candlesadd1213                  = array.new<Candle>(0)
var BOSdata bosdataadd1213                   = BOSdata.new()
htfadd1213.settings                 := SettingsHTFadd1213
htfadd1213.candles                  := candlesadd1213
htfadd1213.bosdata                  := bosdataadd1213
var CandleSet htfadd1214                     = CandleSet.new()
var CandleSettings SettingsHTFadd1214        = CandleSettings.new(htf="1214", max_memory=3, htfint=1214)
var Candle[] candlesadd1214                  = array.new<Candle>(0)
var BOSdata bosdataadd1214                   = BOSdata.new()
htfadd1214.settings                 := SettingsHTFadd1214
htfadd1214.candles                  := candlesadd1214
htfadd1214.bosdata                  := bosdataadd1214
var CandleSet htfadd1215                     = CandleSet.new()
var CandleSettings SettingsHTFadd1215        = CandleSettings.new(htf="1215", max_memory=3, htfint=1215)
var Candle[] candlesadd1215                  = array.new<Candle>(0)
var BOSdata bosdataadd1215                   = BOSdata.new()
htfadd1215.settings                 := SettingsHTFadd1215
htfadd1215.candles                  := candlesadd1215
htfadd1215.bosdata                  := bosdataadd1215
var CandleSet htfadd1216                     = CandleSet.new()
var CandleSettings SettingsHTFadd1216        = CandleSettings.new(htf="1216", max_memory=3, htfint=1216)
var Candle[] candlesadd1216                  = array.new<Candle>(0)
var BOSdata bosdataadd1216                   = BOSdata.new()
htfadd1216.settings                 := SettingsHTFadd1216
htfadd1216.candles                  := candlesadd1216
htfadd1216.bosdata                  := bosdataadd1216
var CandleSet htfadd1217                     = CandleSet.new()
var CandleSettings SettingsHTFadd1217        = CandleSettings.new(htf="1217", max_memory=3, htfint=1217)
var Candle[] candlesadd1217                  = array.new<Candle>(0)
var BOSdata bosdataadd1217                   = BOSdata.new()
htfadd1217.settings                 := SettingsHTFadd1217
htfadd1217.candles                  := candlesadd1217
htfadd1217.bosdata                  := bosdataadd1217
var CandleSet htfadd1218                     = CandleSet.new()
var CandleSettings SettingsHTFadd1218        = CandleSettings.new(htf="1218", max_memory=3, htfint=1218)
var Candle[] candlesadd1218                  = array.new<Candle>(0)
var BOSdata bosdataadd1218                   = BOSdata.new()
htfadd1218.settings                 := SettingsHTFadd1218
htfadd1218.candles                  := candlesadd1218
htfadd1218.bosdata                  := bosdataadd1218
var CandleSet htfadd1219                     = CandleSet.new()
var CandleSettings SettingsHTFadd1219        = CandleSettings.new(htf="1219", max_memory=3, htfint=1219)
var Candle[] candlesadd1219                  = array.new<Candle>(0)
var BOSdata bosdataadd1219                   = BOSdata.new()
htfadd1219.settings                 := SettingsHTFadd1219
htfadd1219.candles                  := candlesadd1219
htfadd1219.bosdata                  := bosdataadd1219
var CandleSet htfadd1220                     = CandleSet.new()
var CandleSettings SettingsHTFadd1220        = CandleSettings.new(htf="1220", max_memory=3, htfint=1220)
var Candle[] candlesadd1220                  = array.new<Candle>(0)
var BOSdata bosdataadd1220                   = BOSdata.new()
htfadd1220.settings                 := SettingsHTFadd1220
htfadd1220.candles                  := candlesadd1220
htfadd1220.bosdata                  := bosdataadd1220
var CandleSet htfadd1221                     = CandleSet.new()
var CandleSettings SettingsHTFadd1221        = CandleSettings.new(htf="1221", max_memory=3, htfint=1221)
var Candle[] candlesadd1221                  = array.new<Candle>(0)
var BOSdata bosdataadd1221                   = BOSdata.new()
htfadd1221.settings                 := SettingsHTFadd1221
htfadd1221.candles                  := candlesadd1221
htfadd1221.bosdata                  := bosdataadd1221
var CandleSet htfadd1222                     = CandleSet.new()
var CandleSettings SettingsHTFadd1222        = CandleSettings.new(htf="1222", max_memory=3, htfint=1222)
var Candle[] candlesadd1222                  = array.new<Candle>(0)
var BOSdata bosdataadd1222                   = BOSdata.new()
htfadd1222.settings                 := SettingsHTFadd1222
htfadd1222.candles                  := candlesadd1222
htfadd1222.bosdata                  := bosdataadd1222
var CandleSet htfadd1223                     = CandleSet.new()
var CandleSettings SettingsHTFadd1223        = CandleSettings.new(htf="1223", max_memory=3, htfint=1223)
var Candle[] candlesadd1223                  = array.new<Candle>(0)
var BOSdata bosdataadd1223                   = BOSdata.new()
htfadd1223.settings                 := SettingsHTFadd1223
htfadd1223.candles                  := candlesadd1223
htfadd1223.bosdata                  := bosdataadd1223
var CandleSet htfadd1224                     = CandleSet.new()
var CandleSettings SettingsHTFadd1224        = CandleSettings.new(htf="1224", max_memory=3, htfint=1224)
var Candle[] candlesadd1224                  = array.new<Candle>(0)
var BOSdata bosdataadd1224                   = BOSdata.new()
htfadd1224.settings                 := SettingsHTFadd1224
htfadd1224.candles                  := candlesadd1224
htfadd1224.bosdata                  := bosdataadd1224
var CandleSet htfadd1225                     = CandleSet.new()
var CandleSettings SettingsHTFadd1225        = CandleSettings.new(htf="1225", max_memory=3, htfint=1225)
var Candle[] candlesadd1225                  = array.new<Candle>(0)
var BOSdata bosdataadd1225                   = BOSdata.new()
htfadd1225.settings                 := SettingsHTFadd1225
htfadd1225.candles                  := candlesadd1225
htfadd1225.bosdata                  := bosdataadd1225
var CandleSet htfadd1226                     = CandleSet.new()
var CandleSettings SettingsHTFadd1226        = CandleSettings.new(htf="1226", max_memory=3, htfint=1226)
var Candle[] candlesadd1226                  = array.new<Candle>(0)
var BOSdata bosdataadd1226                   = BOSdata.new()
htfadd1226.settings                 := SettingsHTFadd1226
htfadd1226.candles                  := candlesadd1226
htfadd1226.bosdata                  := bosdataadd1226
var CandleSet htfadd1227                     = CandleSet.new()
var CandleSettings SettingsHTFadd1227        = CandleSettings.new(htf="1227", max_memory=3, htfint=1227)
var Candle[] candlesadd1227                  = array.new<Candle>(0)
var BOSdata bosdataadd1227                   = BOSdata.new()
htfadd1227.settings                 := SettingsHTFadd1227
htfadd1227.candles                  := candlesadd1227
htfadd1227.bosdata                  := bosdataadd1227
var CandleSet htfadd1228                     = CandleSet.new()
var CandleSettings SettingsHTFadd1228        = CandleSettings.new(htf="1228", max_memory=3, htfint=1228)
var Candle[] candlesadd1228                  = array.new<Candle>(0)
var BOSdata bosdataadd1228                   = BOSdata.new()
htfadd1228.settings                 := SettingsHTFadd1228
htfadd1228.candles                  := candlesadd1228
htfadd1228.bosdata                  := bosdataadd1228
var CandleSet htfadd1229                     = CandleSet.new()
var CandleSettings SettingsHTFadd1229        = CandleSettings.new(htf="1229", max_memory=3, htfint=1229)
var Candle[] candlesadd1229                  = array.new<Candle>(0)
var BOSdata bosdataadd1229                   = BOSdata.new()
htfadd1229.settings                 := SettingsHTFadd1229
htfadd1229.candles                  := candlesadd1229
htfadd1229.bosdata                  := bosdataadd1229
var CandleSet htfadd1230                     = CandleSet.new()
var CandleSettings SettingsHTFadd1230        = CandleSettings.new(htf="1230", max_memory=3, htfint=1230)
var Candle[] candlesadd1230                  = array.new<Candle>(0)
var BOSdata bosdataadd1230                   = BOSdata.new()
htfadd1230.settings                 := SettingsHTFadd1230
htfadd1230.candles                  := candlesadd1230
htfadd1230.bosdata                  := bosdataadd1230
var CandleSet htfadd1231                     = CandleSet.new()
var CandleSettings SettingsHTFadd1231        = CandleSettings.new(htf="1231", max_memory=3, htfint=1231)
var Candle[] candlesadd1231                  = array.new<Candle>(0)
var BOSdata bosdataadd1231                   = BOSdata.new()
htfadd1231.settings                 := SettingsHTFadd1231
htfadd1231.candles                  := candlesadd1231
htfadd1231.bosdata                  := bosdataadd1231
var CandleSet htfadd1232                     = CandleSet.new()
var CandleSettings SettingsHTFadd1232        = CandleSettings.new(htf="1232", max_memory=3, htfint=1232)
var Candle[] candlesadd1232                  = array.new<Candle>(0)
var BOSdata bosdataadd1232                   = BOSdata.new()
htfadd1232.settings                 := SettingsHTFadd1232
htfadd1232.candles                  := candlesadd1232
htfadd1232.bosdata                  := bosdataadd1232
var CandleSet htfadd1233                     = CandleSet.new()
var CandleSettings SettingsHTFadd1233        = CandleSettings.new(htf="1233", max_memory=3, htfint=1233)
var Candle[] candlesadd1233                  = array.new<Candle>(0)
var BOSdata bosdataadd1233                   = BOSdata.new()
htfadd1233.settings                 := SettingsHTFadd1233
htfadd1233.candles                  := candlesadd1233
htfadd1233.bosdata                  := bosdataadd1233
var CandleSet htfadd1234                     = CandleSet.new()
var CandleSettings SettingsHTFadd1234        = CandleSettings.new(htf="1234", max_memory=3, htfint=1234)
var Candle[] candlesadd1234                  = array.new<Candle>(0)
var BOSdata bosdataadd1234                   = BOSdata.new()
htfadd1234.settings                 := SettingsHTFadd1234
htfadd1234.candles                  := candlesadd1234
htfadd1234.bosdata                  := bosdataadd1234
var CandleSet htfadd1235                     = CandleSet.new()
var CandleSettings SettingsHTFadd1235        = CandleSettings.new(htf="1235", max_memory=3, htfint=1235)
var Candle[] candlesadd1235                  = array.new<Candle>(0)
var BOSdata bosdataadd1235                   = BOSdata.new()
htfadd1235.settings                 := SettingsHTFadd1235
htfadd1235.candles                  := candlesadd1235
htfadd1235.bosdata                  := bosdataadd1235
var CandleSet htfadd1236                     = CandleSet.new()
var CandleSettings SettingsHTFadd1236        = CandleSettings.new(htf="1236", max_memory=3, htfint=1236)
var Candle[] candlesadd1236                  = array.new<Candle>(0)
var BOSdata bosdataadd1236                   = BOSdata.new()
htfadd1236.settings                 := SettingsHTFadd1236
htfadd1236.candles                  := candlesadd1236
htfadd1236.bosdata                  := bosdataadd1236
var CandleSet htfadd1237                     = CandleSet.new()
var CandleSettings SettingsHTFadd1237        = CandleSettings.new(htf="1237", max_memory=3, htfint=1237)
var Candle[] candlesadd1237                  = array.new<Candle>(0)
var BOSdata bosdataadd1237                   = BOSdata.new()
htfadd1237.settings                 := SettingsHTFadd1237
htfadd1237.candles                  := candlesadd1237
htfadd1237.bosdata                  := bosdataadd1237
var CandleSet htfadd1238                     = CandleSet.new()
var CandleSettings SettingsHTFadd1238        = CandleSettings.new(htf="1238", max_memory=3, htfint=1238)
var Candle[] candlesadd1238                  = array.new<Candle>(0)
var BOSdata bosdataadd1238                   = BOSdata.new()
htfadd1238.settings                 := SettingsHTFadd1238
htfadd1238.candles                  := candlesadd1238
htfadd1238.bosdata                  := bosdataadd1238
var CandleSet htfadd1239                     = CandleSet.new()
var CandleSettings SettingsHTFadd1239        = CandleSettings.new(htf="1239", max_memory=3, htfint=1239)
var Candle[] candlesadd1239                  = array.new<Candle>(0)
var BOSdata bosdataadd1239                   = BOSdata.new()
htfadd1239.settings                 := SettingsHTFadd1239
htfadd1239.candles                  := candlesadd1239
htfadd1239.bosdata                  := bosdataadd1239
var CandleSet htfadd1240                     = CandleSet.new()
var CandleSettings SettingsHTFadd1240        = CandleSettings.new(htf="1240", max_memory=3, htfint=1240)
var Candle[] candlesadd1240                  = array.new<Candle>(0)
var BOSdata bosdataadd1240                   = BOSdata.new()
htfadd1240.settings                 := SettingsHTFadd1240
htfadd1240.candles                  := candlesadd1240
htfadd1240.bosdata                  := bosdataadd1240
var CandleSet htfadd1241                     = CandleSet.new()
var CandleSettings SettingsHTFadd1241        = CandleSettings.new(htf="1241", max_memory=3, htfint=1241)
var Candle[] candlesadd1241                  = array.new<Candle>(0)
var BOSdata bosdataadd1241                   = BOSdata.new()
htfadd1241.settings                 := SettingsHTFadd1241
htfadd1241.candles                  := candlesadd1241
htfadd1241.bosdata                  := bosdataadd1241
var CandleSet htfadd1242                     = CandleSet.new()
var CandleSettings SettingsHTFadd1242        = CandleSettings.new(htf="1242", max_memory=3, htfint=1242)
var Candle[] candlesadd1242                  = array.new<Candle>(0)
var BOSdata bosdataadd1242                   = BOSdata.new()
htfadd1242.settings                 := SettingsHTFadd1242
htfadd1242.candles                  := candlesadd1242
htfadd1242.bosdata                  := bosdataadd1242
var CandleSet htfadd1243                     = CandleSet.new()
var CandleSettings SettingsHTFadd1243        = CandleSettings.new(htf="1243", max_memory=3, htfint=1243)
var Candle[] candlesadd1243                  = array.new<Candle>(0)
var BOSdata bosdataadd1243                   = BOSdata.new()
htfadd1243.settings                 := SettingsHTFadd1243
htfadd1243.candles                  := candlesadd1243
htfadd1243.bosdata                  := bosdataadd1243
var CandleSet htfadd1244                     = CandleSet.new()
var CandleSettings SettingsHTFadd1244        = CandleSettings.new(htf="1244", max_memory=3, htfint=1244)
var Candle[] candlesadd1244                  = array.new<Candle>(0)
var BOSdata bosdataadd1244                   = BOSdata.new()
htfadd1244.settings                 := SettingsHTFadd1244
htfadd1244.candles                  := candlesadd1244
htfadd1244.bosdata                  := bosdataadd1244
var CandleSet htfadd1245                     = CandleSet.new()
var CandleSettings SettingsHTFadd1245        = CandleSettings.new(htf="1245", max_memory=3, htfint=1245)
var Candle[] candlesadd1245                  = array.new<Candle>(0)
var BOSdata bosdataadd1245                   = BOSdata.new()
htfadd1245.settings                 := SettingsHTFadd1245
htfadd1245.candles                  := candlesadd1245
htfadd1245.bosdata                  := bosdataadd1245
var CandleSet htfadd1246                     = CandleSet.new()
var CandleSettings SettingsHTFadd1246        = CandleSettings.new(htf="1246", max_memory=3, htfint=1246)
var Candle[] candlesadd1246                  = array.new<Candle>(0)
var BOSdata bosdataadd1246                   = BOSdata.new()
htfadd1246.settings                 := SettingsHTFadd1246
htfadd1246.candles                  := candlesadd1246
htfadd1246.bosdata                  := bosdataadd1246
var CandleSet htfadd1247                     = CandleSet.new()
var CandleSettings SettingsHTFadd1247        = CandleSettings.new(htf="1247", max_memory=3, htfint=1247)
var Candle[] candlesadd1247                  = array.new<Candle>(0)
var BOSdata bosdataadd1247                   = BOSdata.new()
htfadd1247.settings                 := SettingsHTFadd1247
htfadd1247.candles                  := candlesadd1247
htfadd1247.bosdata                  := bosdataadd1247
var CandleSet htfadd1248                     = CandleSet.new()
var CandleSettings SettingsHTFadd1248        = CandleSettings.new(htf="1248", max_memory=3, htfint=1248)
var Candle[] candlesadd1248                  = array.new<Candle>(0)
var BOSdata bosdataadd1248                   = BOSdata.new()
htfadd1248.settings                 := SettingsHTFadd1248
htfadd1248.candles                  := candlesadd1248
htfadd1248.bosdata                  := bosdataadd1248
var CandleSet htfadd1249                     = CandleSet.new()
var CandleSettings SettingsHTFadd1249        = CandleSettings.new(htf="1249", max_memory=3, htfint=1249)
var Candle[] candlesadd1249                  = array.new<Candle>(0)
var BOSdata bosdataadd1249                   = BOSdata.new()
htfadd1249.settings                 := SettingsHTFadd1249
htfadd1249.candles                  := candlesadd1249
htfadd1249.bosdata                  := bosdataadd1249
var CandleSet htfadd1250                     = CandleSet.new()
var CandleSettings SettingsHTFadd1250        = CandleSettings.new(htf="1250", max_memory=3, htfint=1250)
var Candle[] candlesadd1250                  = array.new<Candle>(0)
var BOSdata bosdataadd1250                   = BOSdata.new()
htfadd1250.settings                 := SettingsHTFadd1250
htfadd1250.candles                  := candlesadd1250
htfadd1250.bosdata                  := bosdataadd1250
var CandleSet htfadd1251                     = CandleSet.new()
var CandleSettings SettingsHTFadd1251        = CandleSettings.new(htf="1251", max_memory=3, htfint=1251)
var Candle[] candlesadd1251                  = array.new<Candle>(0)
var BOSdata bosdataadd1251                   = BOSdata.new()
htfadd1251.settings                 := SettingsHTFadd1251
htfadd1251.candles                  := candlesadd1251
htfadd1251.bosdata                  := bosdataadd1251
var CandleSet htfadd1252                     = CandleSet.new()
var CandleSettings SettingsHTFadd1252        = CandleSettings.new(htf="1252", max_memory=3, htfint=1252)
var Candle[] candlesadd1252                  = array.new<Candle>(0)
var BOSdata bosdataadd1252                   = BOSdata.new()
htfadd1252.settings                 := SettingsHTFadd1252
htfadd1252.candles                  := candlesadd1252
htfadd1252.bosdata                  := bosdataadd1252
var CandleSet htfadd1253                     = CandleSet.new()
var CandleSettings SettingsHTFadd1253        = CandleSettings.new(htf="1253", max_memory=3, htfint=1253)
var Candle[] candlesadd1253                  = array.new<Candle>(0)
var BOSdata bosdataadd1253                   = BOSdata.new()
htfadd1253.settings                 := SettingsHTFadd1253
htfadd1253.candles                  := candlesadd1253
htfadd1253.bosdata                  := bosdataadd1253
var CandleSet htfadd1254                     = CandleSet.new()
var CandleSettings SettingsHTFadd1254        = CandleSettings.new(htf="1254", max_memory=3, htfint=1254)
var Candle[] candlesadd1254                  = array.new<Candle>(0)
var BOSdata bosdataadd1254                   = BOSdata.new()
htfadd1254.settings                 := SettingsHTFadd1254
htfadd1254.candles                  := candlesadd1254
htfadd1254.bosdata                  := bosdataadd1254
var CandleSet htfadd1255                     = CandleSet.new()
var CandleSettings SettingsHTFadd1255        = CandleSettings.new(htf="1255", max_memory=3, htfint=1255)
var Candle[] candlesadd1255                  = array.new<Candle>(0)
var BOSdata bosdataadd1255                   = BOSdata.new()
htfadd1255.settings                 := SettingsHTFadd1255
htfadd1255.candles                  := candlesadd1255
htfadd1255.bosdata                  := bosdataadd1255
var CandleSet htfadd1256                     = CandleSet.new()
var CandleSettings SettingsHTFadd1256        = CandleSettings.new(htf="1256", max_memory=3, htfint=1256)
var Candle[] candlesadd1256                  = array.new<Candle>(0)
var BOSdata bosdataadd1256                   = BOSdata.new()
htfadd1256.settings                 := SettingsHTFadd1256
htfadd1256.candles                  := candlesadd1256
htfadd1256.bosdata                  := bosdataadd1256
var CandleSet htfadd1257                     = CandleSet.new()
var CandleSettings SettingsHTFadd1257        = CandleSettings.new(htf="1257", max_memory=3, htfint=1257)
var Candle[] candlesadd1257                  = array.new<Candle>(0)
var BOSdata bosdataadd1257                   = BOSdata.new()
htfadd1257.settings                 := SettingsHTFadd1257
htfadd1257.candles                  := candlesadd1257
htfadd1257.bosdata                  := bosdataadd1257
var CandleSet htfadd1258                     = CandleSet.new()
var CandleSettings SettingsHTFadd1258        = CandleSettings.new(htf="1258", max_memory=3, htfint=1258)
var Candle[] candlesadd1258                  = array.new<Candle>(0)
var BOSdata bosdataadd1258                   = BOSdata.new()
htfadd1258.settings                 := SettingsHTFadd1258
htfadd1258.candles                  := candlesadd1258
htfadd1258.bosdata                  := bosdataadd1258
var CandleSet htfadd1259                     = CandleSet.new()
var CandleSettings SettingsHTFadd1259        = CandleSettings.new(htf="1259", max_memory=3, htfint=1259)
var Candle[] candlesadd1259                  = array.new<Candle>(0)
var BOSdata bosdataadd1259                   = BOSdata.new()
htfadd1259.settings                 := SettingsHTFadd1259
htfadd1259.candles                  := candlesadd1259
htfadd1259.bosdata                  := bosdataadd1259
var CandleSet htfadd1260                     = CandleSet.new()
var CandleSettings SettingsHTFadd1260        = CandleSettings.new(htf="1260", max_memory=3, htfint=1260)
var Candle[] candlesadd1260                  = array.new<Candle>(0)
var BOSdata bosdataadd1260                   = BOSdata.new()
htfadd1260.settings                 := SettingsHTFadd1260
htfadd1260.candles                  := candlesadd1260
htfadd1260.bosdata                  := bosdataadd1260
var CandleSet htfadd1261                     = CandleSet.new()
var CandleSettings SettingsHTFadd1261        = CandleSettings.new(htf="1261", max_memory=3, htfint=1261)
var Candle[] candlesadd1261                  = array.new<Candle>(0)
var BOSdata bosdataadd1261                   = BOSdata.new()
htfadd1261.settings                 := SettingsHTFadd1261
htfadd1261.candles                  := candlesadd1261
htfadd1261.bosdata                  := bosdataadd1261
var CandleSet htfadd1262                     = CandleSet.new()
var CandleSettings SettingsHTFadd1262        = CandleSettings.new(htf="1262", max_memory=3, htfint=1262)
var Candle[] candlesadd1262                  = array.new<Candle>(0)
var BOSdata bosdataadd1262                   = BOSdata.new()
htfadd1262.settings                 := SettingsHTFadd1262
htfadd1262.candles                  := candlesadd1262
htfadd1262.bosdata                  := bosdataadd1262
var CandleSet htfadd1263                     = CandleSet.new()
var CandleSettings SettingsHTFadd1263        = CandleSettings.new(htf="1263", max_memory=3, htfint=1263)
var Candle[] candlesadd1263                  = array.new<Candle>(0)
var BOSdata bosdataadd1263                   = BOSdata.new()
htfadd1263.settings                 := SettingsHTFadd1263
htfadd1263.candles                  := candlesadd1263
htfadd1263.bosdata                  := bosdataadd1263
var CandleSet htfadd1264                     = CandleSet.new()
var CandleSettings SettingsHTFadd1264        = CandleSettings.new(htf="1264", max_memory=3, htfint=1264)
var Candle[] candlesadd1264                  = array.new<Candle>(0)
var BOSdata bosdataadd1264                   = BOSdata.new()
htfadd1264.settings                 := SettingsHTFadd1264
htfadd1264.candles                  := candlesadd1264
htfadd1264.bosdata                  := bosdataadd1264
var CandleSet htfadd1265                     = CandleSet.new()
var CandleSettings SettingsHTFadd1265        = CandleSettings.new(htf="1265", max_memory=3, htfint=1265)
var Candle[] candlesadd1265                  = array.new<Candle>(0)
var BOSdata bosdataadd1265                   = BOSdata.new()
htfadd1265.settings                 := SettingsHTFadd1265
htfadd1265.candles                  := candlesadd1265
htfadd1265.bosdata                  := bosdataadd1265
var CandleSet htfadd1266                     = CandleSet.new()
var CandleSettings SettingsHTFadd1266        = CandleSettings.new(htf="1266", max_memory=3, htfint=1266)
var Candle[] candlesadd1266                  = array.new<Candle>(0)
var BOSdata bosdataadd1266                   = BOSdata.new()
htfadd1266.settings                 := SettingsHTFadd1266
htfadd1266.candles                  := candlesadd1266
htfadd1266.bosdata                  := bosdataadd1266
var CandleSet htfadd1267                     = CandleSet.new()
var CandleSettings SettingsHTFadd1267        = CandleSettings.new(htf="1267", max_memory=3, htfint=1267)
var Candle[] candlesadd1267                  = array.new<Candle>(0)
var BOSdata bosdataadd1267                   = BOSdata.new()
htfadd1267.settings                 := SettingsHTFadd1267
htfadd1267.candles                  := candlesadd1267
htfadd1267.bosdata                  := bosdataadd1267
var CandleSet htfadd1268                     = CandleSet.new()
var CandleSettings SettingsHTFadd1268        = CandleSettings.new(htf="1268", max_memory=3, htfint=1268)
var Candle[] candlesadd1268                  = array.new<Candle>(0)
var BOSdata bosdataadd1268                   = BOSdata.new()
htfadd1268.settings                 := SettingsHTFadd1268
htfadd1268.candles                  := candlesadd1268
htfadd1268.bosdata                  := bosdataadd1268
var CandleSet htfadd1269                     = CandleSet.new()
var CandleSettings SettingsHTFadd1269        = CandleSettings.new(htf="1269", max_memory=3, htfint=1269)
var Candle[] candlesadd1269                  = array.new<Candle>(0)
var BOSdata bosdataadd1269                   = BOSdata.new()
htfadd1269.settings                 := SettingsHTFadd1269
htfadd1269.candles                  := candlesadd1269
htfadd1269.bosdata                  := bosdataadd1269
var CandleSet htfadd1270                     = CandleSet.new()
var CandleSettings SettingsHTFadd1270        = CandleSettings.new(htf="1270", max_memory=3, htfint=1270)
var Candle[] candlesadd1270                  = array.new<Candle>(0)
var BOSdata bosdataadd1270                   = BOSdata.new()
htfadd1270.settings                 := SettingsHTFadd1270
htfadd1270.candles                  := candlesadd1270
htfadd1270.bosdata                  := bosdataadd1270
var CandleSet htfadd1271                     = CandleSet.new()
var CandleSettings SettingsHTFadd1271        = CandleSettings.new(htf="1271", max_memory=3, htfint=1271)
var Candle[] candlesadd1271                  = array.new<Candle>(0)
var BOSdata bosdataadd1271                   = BOSdata.new()
htfadd1271.settings                 := SettingsHTFadd1271
htfadd1271.candles                  := candlesadd1271
htfadd1271.bosdata                  := bosdataadd1271
var CandleSet htfadd1272                     = CandleSet.new()
var CandleSettings SettingsHTFadd1272        = CandleSettings.new(htf="1272", max_memory=3, htfint=1272)
var Candle[] candlesadd1272                  = array.new<Candle>(0)
var BOSdata bosdataadd1272                   = BOSdata.new()
htfadd1272.settings                 := SettingsHTFadd1272
htfadd1272.candles                  := candlesadd1272
htfadd1272.bosdata                  := bosdataadd1272
var CandleSet htfadd1273                     = CandleSet.new()
var CandleSettings SettingsHTFadd1273        = CandleSettings.new(htf="1273", max_memory=3, htfint=1273)
var Candle[] candlesadd1273                  = array.new<Candle>(0)
var BOSdata bosdataadd1273                   = BOSdata.new()
htfadd1273.settings                 := SettingsHTFadd1273
htfadd1273.candles                  := candlesadd1273
htfadd1273.bosdata                  := bosdataadd1273
var CandleSet htfadd1274                     = CandleSet.new()
var CandleSettings SettingsHTFadd1274        = CandleSettings.new(htf="1274", max_memory=3, htfint=1274)
var Candle[] candlesadd1274                  = array.new<Candle>(0)
var BOSdata bosdataadd1274                   = BOSdata.new()
htfadd1274.settings                 := SettingsHTFadd1274
htfadd1274.candles                  := candlesadd1274
htfadd1274.bosdata                  := bosdataadd1274
var CandleSet htfadd1275                     = CandleSet.new()
var CandleSettings SettingsHTFadd1275        = CandleSettings.new(htf="1275", max_memory=3, htfint=1275)
var Candle[] candlesadd1275                  = array.new<Candle>(0)
var BOSdata bosdataadd1275                   = BOSdata.new()
htfadd1275.settings                 := SettingsHTFadd1275
htfadd1275.candles                  := candlesadd1275
htfadd1275.bosdata                  := bosdataadd1275
var CandleSet htfadd1276                     = CandleSet.new()
var CandleSettings SettingsHTFadd1276        = CandleSettings.new(htf="1276", max_memory=3, htfint=1276)
var Candle[] candlesadd1276                  = array.new<Candle>(0)
var BOSdata bosdataadd1276                   = BOSdata.new()
htfadd1276.settings                 := SettingsHTFadd1276
htfadd1276.candles                  := candlesadd1276
htfadd1276.bosdata                  := bosdataadd1276
var CandleSet htfadd1277                     = CandleSet.new()
var CandleSettings SettingsHTFadd1277        = CandleSettings.new(htf="1277", max_memory=3, htfint=1277)
var Candle[] candlesadd1277                  = array.new<Candle>(0)
var BOSdata bosdataadd1277                   = BOSdata.new()
htfadd1277.settings                 := SettingsHTFadd1277
htfadd1277.candles                  := candlesadd1277
htfadd1277.bosdata                  := bosdataadd1277
var CandleSet htfadd1278                     = CandleSet.new()
var CandleSettings SettingsHTFadd1278        = CandleSettings.new(htf="1278", max_memory=3, htfint=1278)
var Candle[] candlesadd1278                  = array.new<Candle>(0)
var BOSdata bosdataadd1278                   = BOSdata.new()
htfadd1278.settings                 := SettingsHTFadd1278
htfadd1278.candles                  := candlesadd1278
htfadd1278.bosdata                  := bosdataadd1278
var CandleSet htfadd1279                     = CandleSet.new()
var CandleSettings SettingsHTFadd1279        = CandleSettings.new(htf="1279", max_memory=3, htfint=1279)
var Candle[] candlesadd1279                  = array.new<Candle>(0)
var BOSdata bosdataadd1279                   = BOSdata.new()
htfadd1279.settings                 := SettingsHTFadd1279
htfadd1279.candles                  := candlesadd1279
htfadd1279.bosdata                  := bosdataadd1279
var CandleSet htfadd1280                     = CandleSet.new()
var CandleSettings SettingsHTFadd1280        = CandleSettings.new(htf="1280", max_memory=3, htfint=1280)
var Candle[] candlesadd1280                  = array.new<Candle>(0)
var BOSdata bosdataadd1280                   = BOSdata.new()
htfadd1280.settings                 := SettingsHTFadd1280
htfadd1280.candles                  := candlesadd1280
htfadd1280.bosdata                  := bosdataadd1280
var CandleSet htfadd1281                     = CandleSet.new()
var CandleSettings SettingsHTFadd1281        = CandleSettings.new(htf="1281", max_memory=3, htfint=1281)
var Candle[] candlesadd1281                  = array.new<Candle>(0)
var BOSdata bosdataadd1281                   = BOSdata.new()
htfadd1281.settings                 := SettingsHTFadd1281
htfadd1281.candles                  := candlesadd1281
htfadd1281.bosdata                  := bosdataadd1281
var CandleSet htfadd1282                     = CandleSet.new()
var CandleSettings SettingsHTFadd1282        = CandleSettings.new(htf="1282", max_memory=3, htfint=1282)
var Candle[] candlesadd1282                  = array.new<Candle>(0)
var BOSdata bosdataadd1282                   = BOSdata.new()
htfadd1282.settings                 := SettingsHTFadd1282
htfadd1282.candles                  := candlesadd1282
htfadd1282.bosdata                  := bosdataadd1282
var CandleSet htfadd1283                     = CandleSet.new()
var CandleSettings SettingsHTFadd1283        = CandleSettings.new(htf="1283", max_memory=3, htfint=1283)
var Candle[] candlesadd1283                  = array.new<Candle>(0)
var BOSdata bosdataadd1283                   = BOSdata.new()
htfadd1283.settings                 := SettingsHTFadd1283
htfadd1283.candles                  := candlesadd1283
htfadd1283.bosdata                  := bosdataadd1283
var CandleSet htfadd1284                     = CandleSet.new()
var CandleSettings SettingsHTFadd1284        = CandleSettings.new(htf="1284", max_memory=3, htfint=1284)
var Candle[] candlesadd1284                  = array.new<Candle>(0)
var BOSdata bosdataadd1284                   = BOSdata.new()
htfadd1284.settings                 := SettingsHTFadd1284
htfadd1284.candles                  := candlesadd1284
htfadd1284.bosdata                  := bosdataadd1284
var CandleSet htfadd1285                     = CandleSet.new()
var CandleSettings SettingsHTFadd1285        = CandleSettings.new(htf="1285", max_memory=3, htfint=1285)
var Candle[] candlesadd1285                  = array.new<Candle>(0)
var BOSdata bosdataadd1285                   = BOSdata.new()
htfadd1285.settings                 := SettingsHTFadd1285
htfadd1285.candles                  := candlesadd1285
htfadd1285.bosdata                  := bosdataadd1285
var CandleSet htfadd1286                     = CandleSet.new()
var CandleSettings SettingsHTFadd1286        = CandleSettings.new(htf="1286", max_memory=3, htfint=1286)
var Candle[] candlesadd1286                  = array.new<Candle>(0)
var BOSdata bosdataadd1286                   = BOSdata.new()
htfadd1286.settings                 := SettingsHTFadd1286
htfadd1286.candles                  := candlesadd1286
htfadd1286.bosdata                  := bosdataadd1286
var CandleSet htfadd1287                     = CandleSet.new()
var CandleSettings SettingsHTFadd1287        = CandleSettings.new(htf="1287", max_memory=3, htfint=1287)
var Candle[] candlesadd1287                  = array.new<Candle>(0)
var BOSdata bosdataadd1287                   = BOSdata.new()
htfadd1287.settings                 := SettingsHTFadd1287
htfadd1287.candles                  := candlesadd1287
htfadd1287.bosdata                  := bosdataadd1287
var CandleSet htfadd1288                     = CandleSet.new()
var CandleSettings SettingsHTFadd1288        = CandleSettings.new(htf="1288", max_memory=3, htfint=1288)
var Candle[] candlesadd1288                  = array.new<Candle>(0)
var BOSdata bosdataadd1288                   = BOSdata.new()
htfadd1288.settings                 := SettingsHTFadd1288
htfadd1288.candles                  := candlesadd1288
htfadd1288.bosdata                  := bosdataadd1288
var CandleSet htfadd1289                     = CandleSet.new()
var CandleSettings SettingsHTFadd1289        = CandleSettings.new(htf="1289", max_memory=3, htfint=1289)
var Candle[] candlesadd1289                  = array.new<Candle>(0)
var BOSdata bosdataadd1289                   = BOSdata.new()
htfadd1289.settings                 := SettingsHTFadd1289
htfadd1289.candles                  := candlesadd1289
htfadd1289.bosdata                  := bosdataadd1289
var CandleSet htfadd1290                     = CandleSet.new()
var CandleSettings SettingsHTFadd1290        = CandleSettings.new(htf="1290", max_memory=3, htfint=1290)
var Candle[] candlesadd1290                  = array.new<Candle>(0)
var BOSdata bosdataadd1290                   = BOSdata.new()
htfadd1290.settings                 := SettingsHTFadd1290
htfadd1290.candles                  := candlesadd1290
htfadd1290.bosdata                  := bosdataadd1290
var CandleSet htfadd1291                     = CandleSet.new()
var CandleSettings SettingsHTFadd1291        = CandleSettings.new(htf="1291", max_memory=3, htfint=1291)
var Candle[] candlesadd1291                  = array.new<Candle>(0)
var BOSdata bosdataadd1291                   = BOSdata.new()
htfadd1291.settings                 := SettingsHTFadd1291
htfadd1291.candles                  := candlesadd1291
htfadd1291.bosdata                  := bosdataadd1291
var CandleSet htfadd1292                     = CandleSet.new()
var CandleSettings SettingsHTFadd1292        = CandleSettings.new(htf="1292", max_memory=3, htfint=1292)
var Candle[] candlesadd1292                  = array.new<Candle>(0)
var BOSdata bosdataadd1292                   = BOSdata.new()
htfadd1292.settings                 := SettingsHTFadd1292
htfadd1292.candles                  := candlesadd1292
htfadd1292.bosdata                  := bosdataadd1292
var CandleSet htfadd1293                     = CandleSet.new()
var CandleSettings SettingsHTFadd1293        = CandleSettings.new(htf="1293", max_memory=3, htfint=1293)
var Candle[] candlesadd1293                  = array.new<Candle>(0)
var BOSdata bosdataadd1293                   = BOSdata.new()
htfadd1293.settings                 := SettingsHTFadd1293
htfadd1293.candles                  := candlesadd1293
htfadd1293.bosdata                  := bosdataadd1293
var CandleSet htfadd1294                     = CandleSet.new()
var CandleSettings SettingsHTFadd1294        = CandleSettings.new(htf="1294", max_memory=3, htfint=1294)
var Candle[] candlesadd1294                  = array.new<Candle>(0)
var BOSdata bosdataadd1294                   = BOSdata.new()
htfadd1294.settings                 := SettingsHTFadd1294
htfadd1294.candles                  := candlesadd1294
htfadd1294.bosdata                  := bosdataadd1294
var CandleSet htfadd1295                     = CandleSet.new()
var CandleSettings SettingsHTFadd1295        = CandleSettings.new(htf="1295", max_memory=3, htfint=1295)
var Candle[] candlesadd1295                  = array.new<Candle>(0)
var BOSdata bosdataadd1295                   = BOSdata.new()
htfadd1295.settings                 := SettingsHTFadd1295
htfadd1295.candles                  := candlesadd1295
htfadd1295.bosdata                  := bosdataadd1295
var CandleSet htfadd1296                     = CandleSet.new()
var CandleSettings SettingsHTFadd1296        = CandleSettings.new(htf="1296", max_memory=3, htfint=1296)
var Candle[] candlesadd1296                  = array.new<Candle>(0)
var BOSdata bosdataadd1296                   = BOSdata.new()
htfadd1296.settings                 := SettingsHTFadd1296
htfadd1296.candles                  := candlesadd1296
htfadd1296.bosdata                  := bosdataadd1296
var CandleSet htfadd1297                     = CandleSet.new()
var CandleSettings SettingsHTFadd1297        = CandleSettings.new(htf="1297", max_memory=3, htfint=1297)
var Candle[] candlesadd1297                  = array.new<Candle>(0)
var BOSdata bosdataadd1297                   = BOSdata.new()
htfadd1297.settings                 := SettingsHTFadd1297
htfadd1297.candles                  := candlesadd1297
htfadd1297.bosdata                  := bosdataadd1297
var CandleSet htfadd1298                     = CandleSet.new()
var CandleSettings SettingsHTFadd1298        = CandleSettings.new(htf="1298", max_memory=3, htfint=1298)
var Candle[] candlesadd1298                  = array.new<Candle>(0)
var BOSdata bosdataadd1298                   = BOSdata.new()
htfadd1298.settings                 := SettingsHTFadd1298
htfadd1298.candles                  := candlesadd1298
htfadd1298.bosdata                  := bosdataadd1298
var CandleSet htfadd1299                     = CandleSet.new()
var CandleSettings SettingsHTFadd1299        = CandleSettings.new(htf="1299", max_memory=3, htfint=1299)
var Candle[] candlesadd1299                  = array.new<Candle>(0)
var BOSdata bosdataadd1299                   = BOSdata.new()
htfadd1299.settings                 := SettingsHTFadd1299
htfadd1299.candles                  := candlesadd1299
htfadd1299.bosdata                  := bosdataadd1299
var CandleSet htfadd1300                     = CandleSet.new()
var CandleSettings SettingsHTFadd1300        = CandleSettings.new(htf="1300", max_memory=3, htfint=1300)
var Candle[] candlesadd1300                  = array.new<Candle>(0)
var BOSdata bosdataadd1300                   = BOSdata.new()
htfadd1300.settings                 := SettingsHTFadd1300
htfadd1300.candles                  := candlesadd1300
htfadd1300.bosdata                  := bosdataadd1300
var CandleSet htfadd1301                     = CandleSet.new()
var CandleSettings SettingsHTFadd1301        = CandleSettings.new(htf="1301", max_memory=3, htfint=1301)
var Candle[] candlesadd1301                  = array.new<Candle>(0)
var BOSdata bosdataadd1301                   = BOSdata.new()
htfadd1301.settings                 := SettingsHTFadd1301
htfadd1301.candles                  := candlesadd1301
htfadd1301.bosdata                  := bosdataadd1301
var CandleSet htfadd1302                     = CandleSet.new()
var CandleSettings SettingsHTFadd1302        = CandleSettings.new(htf="1302", max_memory=3, htfint=1302)
var Candle[] candlesadd1302                  = array.new<Candle>(0)
var BOSdata bosdataadd1302                   = BOSdata.new()
htfadd1302.settings                 := SettingsHTFadd1302
htfadd1302.candles                  := candlesadd1302
htfadd1302.bosdata                  := bosdataadd1302
var CandleSet htfadd1303                     = CandleSet.new()
var CandleSettings SettingsHTFadd1303        = CandleSettings.new(htf="1303", max_memory=3, htfint=1303)
var Candle[] candlesadd1303                  = array.new<Candle>(0)
var BOSdata bosdataadd1303                   = BOSdata.new()
htfadd1303.settings                 := SettingsHTFadd1303
htfadd1303.candles                  := candlesadd1303
htfadd1303.bosdata                  := bosdataadd1303
var CandleSet htfadd1304                     = CandleSet.new()
var CandleSettings SettingsHTFadd1304        = CandleSettings.new(htf="1304", max_memory=3, htfint=1304)
var Candle[] candlesadd1304                  = array.new<Candle>(0)
var BOSdata bosdataadd1304                   = BOSdata.new()
htfadd1304.settings                 := SettingsHTFadd1304
htfadd1304.candles                  := candlesadd1304
htfadd1304.bosdata                  := bosdataadd1304
var CandleSet htfadd1305                     = CandleSet.new()
var CandleSettings SettingsHTFadd1305        = CandleSettings.new(htf="1305", max_memory=3, htfint=1305)
var Candle[] candlesadd1305                  = array.new<Candle>(0)
var BOSdata bosdataadd1305                   = BOSdata.new()
htfadd1305.settings                 := SettingsHTFadd1305
htfadd1305.candles                  := candlesadd1305
htfadd1305.bosdata                  := bosdataadd1305
var CandleSet htfadd1306                     = CandleSet.new()
var CandleSettings SettingsHTFadd1306        = CandleSettings.new(htf="1306", max_memory=3, htfint=1306)
var Candle[] candlesadd1306                  = array.new<Candle>(0)
var BOSdata bosdataadd1306                   = BOSdata.new()
htfadd1306.settings                 := SettingsHTFadd1306
htfadd1306.candles                  := candlesadd1306
htfadd1306.bosdata                  := bosdataadd1306
var CandleSet htfadd1307                     = CandleSet.new()
var CandleSettings SettingsHTFadd1307        = CandleSettings.new(htf="1307", max_memory=3, htfint=1307)
var Candle[] candlesadd1307                  = array.new<Candle>(0)
var BOSdata bosdataadd1307                   = BOSdata.new()
htfadd1307.settings                 := SettingsHTFadd1307
htfadd1307.candles                  := candlesadd1307
htfadd1307.bosdata                  := bosdataadd1307
var CandleSet htfadd1308                     = CandleSet.new()
var CandleSettings SettingsHTFadd1308        = CandleSettings.new(htf="1308", max_memory=3, htfint=1308)
var Candle[] candlesadd1308                  = array.new<Candle>(0)
var BOSdata bosdataadd1308                   = BOSdata.new()
htfadd1308.settings                 := SettingsHTFadd1308
htfadd1308.candles                  := candlesadd1308
htfadd1308.bosdata                  := bosdataadd1308
var CandleSet htfadd1309                     = CandleSet.new()
var CandleSettings SettingsHTFadd1309        = CandleSettings.new(htf="1309", max_memory=3, htfint=1309)
var Candle[] candlesadd1309                  = array.new<Candle>(0)
var BOSdata bosdataadd1309                   = BOSdata.new()
htfadd1309.settings                 := SettingsHTFadd1309
htfadd1309.candles                  := candlesadd1309
htfadd1309.bosdata                  := bosdataadd1309
var CandleSet htfadd1310                     = CandleSet.new()
var CandleSettings SettingsHTFadd1310        = CandleSettings.new(htf="1310", max_memory=3, htfint=1310)
var Candle[] candlesadd1310                  = array.new<Candle>(0)
var BOSdata bosdataadd1310                   = BOSdata.new()
htfadd1310.settings                 := SettingsHTFadd1310
htfadd1310.candles                  := candlesadd1310
htfadd1310.bosdata                  := bosdataadd1310
var CandleSet htfadd1311                     = CandleSet.new()
var CandleSettings SettingsHTFadd1311        = CandleSettings.new(htf="1311", max_memory=3, htfint=1311)
var Candle[] candlesadd1311                  = array.new<Candle>(0)
var BOSdata bosdataadd1311                   = BOSdata.new()
htfadd1311.settings                 := SettingsHTFadd1311
htfadd1311.candles                  := candlesadd1311
htfadd1311.bosdata                  := bosdataadd1311
var CandleSet htfadd1312                     = CandleSet.new()
var CandleSettings SettingsHTFadd1312        = CandleSettings.new(htf="1312", max_memory=3, htfint=1312)
var Candle[] candlesadd1312                  = array.new<Candle>(0)
var BOSdata bosdataadd1312                   = BOSdata.new()
htfadd1312.settings                 := SettingsHTFadd1312
htfadd1312.candles                  := candlesadd1312
htfadd1312.bosdata                  := bosdataadd1312
var CandleSet htfadd1313                     = CandleSet.new()
var CandleSettings SettingsHTFadd1313        = CandleSettings.new(htf="1313", max_memory=3, htfint=1313)
var Candle[] candlesadd1313                  = array.new<Candle>(0)
var BOSdata bosdataadd1313                   = BOSdata.new()
htfadd1313.settings                 := SettingsHTFadd1313
htfadd1313.candles                  := candlesadd1313
htfadd1313.bosdata                  := bosdataadd1313
var CandleSet htfadd1314                     = CandleSet.new()
var CandleSettings SettingsHTFadd1314        = CandleSettings.new(htf="1314", max_memory=3, htfint=1314)
var Candle[] candlesadd1314                  = array.new<Candle>(0)
var BOSdata bosdataadd1314                   = BOSdata.new()
htfadd1314.settings                 := SettingsHTFadd1314
htfadd1314.candles                  := candlesadd1314
htfadd1314.bosdata                  := bosdataadd1314
var CandleSet htfadd1315                     = CandleSet.new()
var CandleSettings SettingsHTFadd1315        = CandleSettings.new(htf="1315", max_memory=3, htfint=1315)
var Candle[] candlesadd1315                  = array.new<Candle>(0)
var BOSdata bosdataadd1315                   = BOSdata.new()
htfadd1315.settings                 := SettingsHTFadd1315
htfadd1315.candles                  := candlesadd1315
htfadd1315.bosdata                  := bosdataadd1315
var CandleSet htfadd1316                     = CandleSet.new()
var CandleSettings SettingsHTFadd1316        = CandleSettings.new(htf="1316", max_memory=3, htfint=1316)
var Candle[] candlesadd1316                  = array.new<Candle>(0)
var BOSdata bosdataadd1316                   = BOSdata.new()
htfadd1316.settings                 := SettingsHTFadd1316
htfadd1316.candles                  := candlesadd1316
htfadd1316.bosdata                  := bosdataadd1316
var CandleSet htfadd1317                     = CandleSet.new()
var CandleSettings SettingsHTFadd1317        = CandleSettings.new(htf="1317", max_memory=3, htfint=1317)
var Candle[] candlesadd1317                  = array.new<Candle>(0)
var BOSdata bosdataadd1317                   = BOSdata.new()
htfadd1317.settings                 := SettingsHTFadd1317
htfadd1317.candles                  := candlesadd1317
htfadd1317.bosdata                  := bosdataadd1317
var CandleSet htfadd1318                     = CandleSet.new()
var CandleSettings SettingsHTFadd1318        = CandleSettings.new(htf="1318", max_memory=3, htfint=1318)
var Candle[] candlesadd1318                  = array.new<Candle>(0)
var BOSdata bosdataadd1318                   = BOSdata.new()
htfadd1318.settings                 := SettingsHTFadd1318
htfadd1318.candles                  := candlesadd1318
htfadd1318.bosdata                  := bosdataadd1318
var CandleSet htfadd1319                     = CandleSet.new()
var CandleSettings SettingsHTFadd1319        = CandleSettings.new(htf="1319", max_memory=3, htfint=1319)
var Candle[] candlesadd1319                  = array.new<Candle>(0)
var BOSdata bosdataadd1319                   = BOSdata.new()
htfadd1319.settings                 := SettingsHTFadd1319
htfadd1319.candles                  := candlesadd1319
htfadd1319.bosdata                  := bosdataadd1319
var CandleSet htfadd1320                     = CandleSet.new()
var CandleSettings SettingsHTFadd1320        = CandleSettings.new(htf="1320", max_memory=3, htfint=1320)
var Candle[] candlesadd1320                  = array.new<Candle>(0)
var BOSdata bosdataadd1320                   = BOSdata.new()
htfadd1320.settings                 := SettingsHTFadd1320
htfadd1320.candles                  := candlesadd1320
htfadd1320.bosdata                  := bosdataadd1320
var CandleSet htfadd1321                     = CandleSet.new()
var CandleSettings SettingsHTFadd1321        = CandleSettings.new(htf="1321", max_memory=3, htfint=1321)
var Candle[] candlesadd1321                  = array.new<Candle>(0)
var BOSdata bosdataadd1321                   = BOSdata.new()
htfadd1321.settings                 := SettingsHTFadd1321
htfadd1321.candles                  := candlesadd1321
htfadd1321.bosdata                  := bosdataadd1321
var CandleSet htfadd1322                     = CandleSet.new()
var CandleSettings SettingsHTFadd1322        = CandleSettings.new(htf="1322", max_memory=3, htfint=1322)
var Candle[] candlesadd1322                  = array.new<Candle>(0)
var BOSdata bosdataadd1322                   = BOSdata.new()
htfadd1322.settings                 := SettingsHTFadd1322
htfadd1322.candles                  := candlesadd1322
htfadd1322.bosdata                  := bosdataadd1322
var CandleSet htfadd1323                     = CandleSet.new()
var CandleSettings SettingsHTFadd1323        = CandleSettings.new(htf="1323", max_memory=3, htfint=1323)
var Candle[] candlesadd1323                  = array.new<Candle>(0)
var BOSdata bosdataadd1323                   = BOSdata.new()
htfadd1323.settings                 := SettingsHTFadd1323
htfadd1323.candles                  := candlesadd1323
htfadd1323.bosdata                  := bosdataadd1323
var CandleSet htfadd1324                     = CandleSet.new()
var CandleSettings SettingsHTFadd1324        = CandleSettings.new(htf="1324", max_memory=3, htfint=1324)
var Candle[] candlesadd1324                  = array.new<Candle>(0)
var BOSdata bosdataadd1324                   = BOSdata.new()
htfadd1324.settings                 := SettingsHTFadd1324
htfadd1324.candles                  := candlesadd1324
htfadd1324.bosdata                  := bosdataadd1324
var CandleSet htfadd1325                     = CandleSet.new()
var CandleSettings SettingsHTFadd1325        = CandleSettings.new(htf="1325", max_memory=3, htfint=1325)
var Candle[] candlesadd1325                  = array.new<Candle>(0)
var BOSdata bosdataadd1325                   = BOSdata.new()
htfadd1325.settings                 := SettingsHTFadd1325
htfadd1325.candles                  := candlesadd1325
htfadd1325.bosdata                  := bosdataadd1325
var CandleSet htfadd1326                     = CandleSet.new()
var CandleSettings SettingsHTFadd1326        = CandleSettings.new(htf="1326", max_memory=3, htfint=1326)
var Candle[] candlesadd1326                  = array.new<Candle>(0)
var BOSdata bosdataadd1326                   = BOSdata.new()
htfadd1326.settings                 := SettingsHTFadd1326
htfadd1326.candles                  := candlesadd1326
htfadd1326.bosdata                  := bosdataadd1326
var CandleSet htfadd1327                     = CandleSet.new()
var CandleSettings SettingsHTFadd1327        = CandleSettings.new(htf="1327", max_memory=3, htfint=1327)
var Candle[] candlesadd1327                  = array.new<Candle>(0)
var BOSdata bosdataadd1327                   = BOSdata.new()
htfadd1327.settings                 := SettingsHTFadd1327
htfadd1327.candles                  := candlesadd1327
htfadd1327.bosdata                  := bosdataadd1327
var CandleSet htfadd1328                     = CandleSet.new()
var CandleSettings SettingsHTFadd1328        = CandleSettings.new(htf="1328", max_memory=3, htfint=1328)
var Candle[] candlesadd1328                  = array.new<Candle>(0)
var BOSdata bosdataadd1328                   = BOSdata.new()
htfadd1328.settings                 := SettingsHTFadd1328
htfadd1328.candles                  := candlesadd1328
htfadd1328.bosdata                  := bosdataadd1328
var CandleSet htfadd1329                     = CandleSet.new()
var CandleSettings SettingsHTFadd1329        = CandleSettings.new(htf="1329", max_memory=3, htfint=1329)
var Candle[] candlesadd1329                  = array.new<Candle>(0)
var BOSdata bosdataadd1329                   = BOSdata.new()
htfadd1329.settings                 := SettingsHTFadd1329
htfadd1329.candles                  := candlesadd1329
htfadd1329.bosdata                  := bosdataadd1329
var CandleSet htfadd1330                     = CandleSet.new()
var CandleSettings SettingsHTFadd1330        = CandleSettings.new(htf="1330", max_memory=3, htfint=1330)
var Candle[] candlesadd1330                  = array.new<Candle>(0)
var BOSdata bosdataadd1330                   = BOSdata.new()
htfadd1330.settings                 := SettingsHTFadd1330
htfadd1330.candles                  := candlesadd1330
htfadd1330.bosdata                  := bosdataadd1330
var CandleSet htfadd1331                     = CandleSet.new()
var CandleSettings SettingsHTFadd1331        = CandleSettings.new(htf="1331", max_memory=3, htfint=1331)
var Candle[] candlesadd1331                  = array.new<Candle>(0)
var BOSdata bosdataadd1331                   = BOSdata.new()
htfadd1331.settings                 := SettingsHTFadd1331
htfadd1331.candles                  := candlesadd1331
htfadd1331.bosdata                  := bosdataadd1331
var CandleSet htfadd1332                     = CandleSet.new()
var CandleSettings SettingsHTFadd1332        = CandleSettings.new(htf="1332", max_memory=3, htfint=1332)
var Candle[] candlesadd1332                  = array.new<Candle>(0)
var BOSdata bosdataadd1332                   = BOSdata.new()
htfadd1332.settings                 := SettingsHTFadd1332
htfadd1332.candles                  := candlesadd1332
htfadd1332.bosdata                  := bosdataadd1332
var CandleSet htfadd1333                     = CandleSet.new()
var CandleSettings SettingsHTFadd1333        = CandleSettings.new(htf="1333", max_memory=3, htfint=1333)
var Candle[] candlesadd1333                  = array.new<Candle>(0)
var BOSdata bosdataadd1333                   = BOSdata.new()
htfadd1333.settings                 := SettingsHTFadd1333
htfadd1333.candles                  := candlesadd1333
htfadd1333.bosdata                  := bosdataadd1333
var CandleSet htfadd1334                     = CandleSet.new()
var CandleSettings SettingsHTFadd1334        = CandleSettings.new(htf="1334", max_memory=3, htfint=1334)
var Candle[] candlesadd1334                  = array.new<Candle>(0)
var BOSdata bosdataadd1334                   = BOSdata.new()
htfadd1334.settings                 := SettingsHTFadd1334
htfadd1334.candles                  := candlesadd1334
htfadd1334.bosdata                  := bosdataadd1334
var CandleSet htfadd1335                     = CandleSet.new()
var CandleSettings SettingsHTFadd1335        = CandleSettings.new(htf="1335", max_memory=3, htfint=1335)
var Candle[] candlesadd1335                  = array.new<Candle>(0)
var BOSdata bosdataadd1335                   = BOSdata.new()
htfadd1335.settings                 := SettingsHTFadd1335
htfadd1335.candles                  := candlesadd1335
htfadd1335.bosdata                  := bosdataadd1335
var CandleSet htfadd1336                     = CandleSet.new()
var CandleSettings SettingsHTFadd1336        = CandleSettings.new(htf="1336", max_memory=3, htfint=1336)
var Candle[] candlesadd1336                  = array.new<Candle>(0)
var BOSdata bosdataadd1336                   = BOSdata.new()
htfadd1336.settings                 := SettingsHTFadd1336
htfadd1336.candles                  := candlesadd1336
htfadd1336.bosdata                  := bosdataadd1336
var CandleSet htfadd1337                     = CandleSet.new()
var CandleSettings SettingsHTFadd1337        = CandleSettings.new(htf="1337", max_memory=3, htfint=1337)
var Candle[] candlesadd1337                  = array.new<Candle>(0)
var BOSdata bosdataadd1337                   = BOSdata.new()
htfadd1337.settings                 := SettingsHTFadd1337
htfadd1337.candles                  := candlesadd1337
htfadd1337.bosdata                  := bosdataadd1337
var CandleSet htfadd1338                     = CandleSet.new()
var CandleSettings SettingsHTFadd1338        = CandleSettings.new(htf="1338", max_memory=3, htfint=1338)
var Candle[] candlesadd1338                  = array.new<Candle>(0)
var BOSdata bosdataadd1338                   = BOSdata.new()
htfadd1338.settings                 := SettingsHTFadd1338
htfadd1338.candles                  := candlesadd1338
htfadd1338.bosdata                  := bosdataadd1338
var CandleSet htfadd1339                     = CandleSet.new()
var CandleSettings SettingsHTFadd1339        = CandleSettings.new(htf="1339", max_memory=3, htfint=1339)
var Candle[] candlesadd1339                  = array.new<Candle>(0)
var BOSdata bosdataadd1339                   = BOSdata.new()
htfadd1339.settings                 := SettingsHTFadd1339
htfadd1339.candles                  := candlesadd1339
htfadd1339.bosdata                  := bosdataadd1339
var CandleSet htfadd1340                     = CandleSet.new()
var CandleSettings SettingsHTFadd1340        = CandleSettings.new(htf="1340", max_memory=3, htfint=1340)
var Candle[] candlesadd1340                  = array.new<Candle>(0)
var BOSdata bosdataadd1340                   = BOSdata.new()
htfadd1340.settings                 := SettingsHTFadd1340
htfadd1340.candles                  := candlesadd1340
htfadd1340.bosdata                  := bosdataadd1340
var CandleSet htfadd1341                     = CandleSet.new()
var CandleSettings SettingsHTFadd1341        = CandleSettings.new(htf="1341", max_memory=3, htfint=1341)
var Candle[] candlesadd1341                  = array.new<Candle>(0)
var BOSdata bosdataadd1341                   = BOSdata.new()
htfadd1341.settings                 := SettingsHTFadd1341
htfadd1341.candles                  := candlesadd1341
htfadd1341.bosdata                  := bosdataadd1341
var CandleSet htfadd1342                     = CandleSet.new()
var CandleSettings SettingsHTFadd1342        = CandleSettings.new(htf="1342", max_memory=3, htfint=1342)
var Candle[] candlesadd1342                  = array.new<Candle>(0)
var BOSdata bosdataadd1342                   = BOSdata.new()
htfadd1342.settings                 := SettingsHTFadd1342
htfadd1342.candles                  := candlesadd1342
htfadd1342.bosdata                  := bosdataadd1342
var CandleSet htfadd1343                     = CandleSet.new()
var CandleSettings SettingsHTFadd1343        = CandleSettings.new(htf="1343", max_memory=3, htfint=1343)
var Candle[] candlesadd1343                  = array.new<Candle>(0)
var BOSdata bosdataadd1343                   = BOSdata.new()
htfadd1343.settings                 := SettingsHTFadd1343
htfadd1343.candles                  := candlesadd1343
htfadd1343.bosdata                  := bosdataadd1343
var CandleSet htfadd1344                     = CandleSet.new()
var CandleSettings SettingsHTFadd1344        = CandleSettings.new(htf="1344", max_memory=3, htfint=1344)
var Candle[] candlesadd1344                  = array.new<Candle>(0)
var BOSdata bosdataadd1344                   = BOSdata.new()
htfadd1344.settings                 := SettingsHTFadd1344
htfadd1344.candles                  := candlesadd1344
htfadd1344.bosdata                  := bosdataadd1344
var CandleSet htfadd1345                     = CandleSet.new()
var CandleSettings SettingsHTFadd1345        = CandleSettings.new(htf="1345", max_memory=3, htfint=1345)
var Candle[] candlesadd1345                  = array.new<Candle>(0)
var BOSdata bosdataadd1345                   = BOSdata.new()
htfadd1345.settings                 := SettingsHTFadd1345
htfadd1345.candles                  := candlesadd1345
htfadd1345.bosdata                  := bosdataadd1345
var CandleSet htfadd1346                     = CandleSet.new()
var CandleSettings SettingsHTFadd1346        = CandleSettings.new(htf="1346", max_memory=3, htfint=1346)
var Candle[] candlesadd1346                  = array.new<Candle>(0)
var BOSdata bosdataadd1346                   = BOSdata.new()
htfadd1346.settings                 := SettingsHTFadd1346
htfadd1346.candles                  := candlesadd1346
htfadd1346.bosdata                  := bosdataadd1346
var CandleSet htfadd1347                     = CandleSet.new()
var CandleSettings SettingsHTFadd1347        = CandleSettings.new(htf="1347", max_memory=3, htfint=1347)
var Candle[] candlesadd1347                  = array.new<Candle>(0)
var BOSdata bosdataadd1347                   = BOSdata.new()
htfadd1347.settings                 := SettingsHTFadd1347
htfadd1347.candles                  := candlesadd1347
htfadd1347.bosdata                  := bosdataadd1347
var CandleSet htfadd1348                     = CandleSet.new()
var CandleSettings SettingsHTFadd1348        = CandleSettings.new(htf="1348", max_memory=3, htfint=1348)
var Candle[] candlesadd1348                  = array.new<Candle>(0)
var BOSdata bosdataadd1348                   = BOSdata.new()
htfadd1348.settings                 := SettingsHTFadd1348
htfadd1348.candles                  := candlesadd1348
htfadd1348.bosdata                  := bosdataadd1348
var CandleSet htfadd1349                     = CandleSet.new()
var CandleSettings SettingsHTFadd1349        = CandleSettings.new(htf="1349", max_memory=3, htfint=1349)
var Candle[] candlesadd1349                  = array.new<Candle>(0)
var BOSdata bosdataadd1349                   = BOSdata.new()
htfadd1349.settings                 := SettingsHTFadd1349
htfadd1349.candles                  := candlesadd1349
htfadd1349.bosdata                  := bosdataadd1349
var CandleSet htfadd1350                     = CandleSet.new()
var CandleSettings SettingsHTFadd1350        = CandleSettings.new(htf="1350", max_memory=3, htfint=1350)
var Candle[] candlesadd1350                  = array.new<Candle>(0)
var BOSdata bosdataadd1350                   = BOSdata.new()
htfadd1350.settings                 := SettingsHTFadd1350
htfadd1350.candles                  := candlesadd1350
htfadd1350.bosdata                  := bosdataadd1350
var CandleSet htfadd1351                     = CandleSet.new()
var CandleSettings SettingsHTFadd1351        = CandleSettings.new(htf="1351", max_memory=3, htfint=1351)
var Candle[] candlesadd1351                  = array.new<Candle>(0)
var BOSdata bosdataadd1351                   = BOSdata.new()
htfadd1351.settings                 := SettingsHTFadd1351
htfadd1351.candles                  := candlesadd1351
htfadd1351.bosdata                  := bosdataadd1351
var CandleSet htfadd1352                     = CandleSet.new()
var CandleSettings SettingsHTFadd1352        = CandleSettings.new(htf="1352", max_memory=3, htfint=1352)
var Candle[] candlesadd1352                  = array.new<Candle>(0)
var BOSdata bosdataadd1352                   = BOSdata.new()
htfadd1352.settings                 := SettingsHTFadd1352
htfadd1352.candles                  := candlesadd1352
htfadd1352.bosdata                  := bosdataadd1352
var CandleSet htfadd1353                     = CandleSet.new()
var CandleSettings SettingsHTFadd1353        = CandleSettings.new(htf="1353", max_memory=3, htfint=1353)
var Candle[] candlesadd1353                  = array.new<Candle>(0)
var BOSdata bosdataadd1353                   = BOSdata.new()
htfadd1353.settings                 := SettingsHTFadd1353
htfadd1353.candles                  := candlesadd1353
htfadd1353.bosdata                  := bosdataadd1353
var CandleSet htfadd1354                     = CandleSet.new()
var CandleSettings SettingsHTFadd1354        = CandleSettings.new(htf="1354", max_memory=3, htfint=1354)
var Candle[] candlesadd1354                  = array.new<Candle>(0)
var BOSdata bosdataadd1354                   = BOSdata.new()
htfadd1354.settings                 := SettingsHTFadd1354
htfadd1354.candles                  := candlesadd1354
htfadd1354.bosdata                  := bosdataadd1354
var CandleSet htfadd1355                     = CandleSet.new()
var CandleSettings SettingsHTFadd1355        = CandleSettings.new(htf="1355", max_memory=3, htfint=1355)
var Candle[] candlesadd1355                  = array.new<Candle>(0)
var BOSdata bosdataadd1355                   = BOSdata.new()
htfadd1355.settings                 := SettingsHTFadd1355
htfadd1355.candles                  := candlesadd1355
htfadd1355.bosdata                  := bosdataadd1355
var CandleSet htfadd1356                     = CandleSet.new()
var CandleSettings SettingsHTFadd1356        = CandleSettings.new(htf="1356", max_memory=3, htfint=1356)
var Candle[] candlesadd1356                  = array.new<Candle>(0)
var BOSdata bosdataadd1356                   = BOSdata.new()
htfadd1356.settings                 := SettingsHTFadd1356
htfadd1356.candles                  := candlesadd1356
htfadd1356.bosdata                  := bosdataadd1356
var CandleSet htfadd1357                     = CandleSet.new()
var CandleSettings SettingsHTFadd1357        = CandleSettings.new(htf="1357", max_memory=3, htfint=1357)
var Candle[] candlesadd1357                  = array.new<Candle>(0)
var BOSdata bosdataadd1357                   = BOSdata.new()
htfadd1357.settings                 := SettingsHTFadd1357
htfadd1357.candles                  := candlesadd1357
htfadd1357.bosdata                  := bosdataadd1357
var CandleSet htfadd1358                     = CandleSet.new()
var CandleSettings SettingsHTFadd1358        = CandleSettings.new(htf="1358", max_memory=3, htfint=1358)
var Candle[] candlesadd1358                  = array.new<Candle>(0)
var BOSdata bosdataadd1358                   = BOSdata.new()
htfadd1358.settings                 := SettingsHTFadd1358
htfadd1358.candles                  := candlesadd1358
htfadd1358.bosdata                  := bosdataadd1358
var CandleSet htfadd1359                     = CandleSet.new()
var CandleSettings SettingsHTFadd1359        = CandleSettings.new(htf="1359", max_memory=3, htfint=1359)
var Candle[] candlesadd1359                  = array.new<Candle>(0)
var BOSdata bosdataadd1359                   = BOSdata.new()
htfadd1359.settings                 := SettingsHTFadd1359
htfadd1359.candles                  := candlesadd1359
htfadd1359.bosdata                  := bosdataadd1359
var CandleSet htfadd1360                     = CandleSet.new()
var CandleSettings SettingsHTFadd1360        = CandleSettings.new(htf="1360", max_memory=3, htfint=1360)
var Candle[] candlesadd1360                  = array.new<Candle>(0)
var BOSdata bosdataadd1360                   = BOSdata.new()
htfadd1360.settings                 := SettingsHTFadd1360
htfadd1360.candles                  := candlesadd1360
htfadd1360.bosdata                  := bosdataadd1360
var CandleSet htfadd1361                     = CandleSet.new()
var CandleSettings SettingsHTFadd1361        = CandleSettings.new(htf="1361", max_memory=3, htfint=1361)
var Candle[] candlesadd1361                  = array.new<Candle>(0)
var BOSdata bosdataadd1361                   = BOSdata.new()
htfadd1361.settings                 := SettingsHTFadd1361
htfadd1361.candles                  := candlesadd1361
htfadd1361.bosdata                  := bosdataadd1361
var CandleSet htfadd1362                     = CandleSet.new()
var CandleSettings SettingsHTFadd1362        = CandleSettings.new(htf="1362", max_memory=3, htfint=1362)
var Candle[] candlesadd1362                  = array.new<Candle>(0)
var BOSdata bosdataadd1362                   = BOSdata.new()
htfadd1362.settings                 := SettingsHTFadd1362
htfadd1362.candles                  := candlesadd1362
htfadd1362.bosdata                  := bosdataadd1362
var CandleSet htfadd1363                     = CandleSet.new()
var CandleSettings SettingsHTFadd1363        = CandleSettings.new(htf="1363", max_memory=3, htfint=1363)
var Candle[] candlesadd1363                  = array.new<Candle>(0)
var BOSdata bosdataadd1363                   = BOSdata.new()
htfadd1363.settings                 := SettingsHTFadd1363
htfadd1363.candles                  := candlesadd1363
htfadd1363.bosdata                  := bosdataadd1363
var CandleSet htfadd1364                     = CandleSet.new()
var CandleSettings SettingsHTFadd1364        = CandleSettings.new(htf="1364", max_memory=3, htfint=1364)
var Candle[] candlesadd1364                  = array.new<Candle>(0)
var BOSdata bosdataadd1364                   = BOSdata.new()
htfadd1364.settings                 := SettingsHTFadd1364
htfadd1364.candles                  := candlesadd1364
htfadd1364.bosdata                  := bosdataadd1364
var CandleSet htfadd1365                     = CandleSet.new()
var CandleSettings SettingsHTFadd1365        = CandleSettings.new(htf="1365", max_memory=3, htfint=1365)
var Candle[] candlesadd1365                  = array.new<Candle>(0)
var BOSdata bosdataadd1365                   = BOSdata.new()
htfadd1365.settings                 := SettingsHTFadd1365
htfadd1365.candles                  := candlesadd1365
htfadd1365.bosdata                  := bosdataadd1365
var CandleSet htfadd1366                     = CandleSet.new()
var CandleSettings SettingsHTFadd1366        = CandleSettings.new(htf="1366", max_memory=3, htfint=1366)
var Candle[] candlesadd1366                  = array.new<Candle>(0)
var BOSdata bosdataadd1366                   = BOSdata.new()
htfadd1366.settings                 := SettingsHTFadd1366
htfadd1366.candles                  := candlesadd1366
htfadd1366.bosdata                  := bosdataadd1366
var CandleSet htfadd1367                     = CandleSet.new()
var CandleSettings SettingsHTFadd1367        = CandleSettings.new(htf="1367", max_memory=3, htfint=1367)
var Candle[] candlesadd1367                  = array.new<Candle>(0)
var BOSdata bosdataadd1367                   = BOSdata.new()
htfadd1367.settings                 := SettingsHTFadd1367
htfadd1367.candles                  := candlesadd1367
htfadd1367.bosdata                  := bosdataadd1367
var CandleSet htfadd1368                     = CandleSet.new()
var CandleSettings SettingsHTFadd1368        = CandleSettings.new(htf="1368", max_memory=3, htfint=1368)
var Candle[] candlesadd1368                  = array.new<Candle>(0)
var BOSdata bosdataadd1368                   = BOSdata.new()
htfadd1368.settings                 := SettingsHTFadd1368
htfadd1368.candles                  := candlesadd1368
htfadd1368.bosdata                  := bosdataadd1368
var CandleSet htfadd1369                     = CandleSet.new()
var CandleSettings SettingsHTFadd1369        = CandleSettings.new(htf="1369", max_memory=3, htfint=1369)
var Candle[] candlesadd1369                  = array.new<Candle>(0)
var BOSdata bosdataadd1369                   = BOSdata.new()
htfadd1369.settings                 := SettingsHTFadd1369
htfadd1369.candles                  := candlesadd1369
htfadd1369.bosdata                  := bosdataadd1369
var CandleSet htfadd1370                     = CandleSet.new()
var CandleSettings SettingsHTFadd1370        = CandleSettings.new(htf="1370", max_memory=3, htfint=1370)
var Candle[] candlesadd1370                  = array.new<Candle>(0)
var BOSdata bosdataadd1370                   = BOSdata.new()
htfadd1370.settings                 := SettingsHTFadd1370
htfadd1370.candles                  := candlesadd1370
htfadd1370.bosdata                  := bosdataadd1370
var CandleSet htfadd1371                     = CandleSet.new()
var CandleSettings SettingsHTFadd1371        = CandleSettings.new(htf="1371", max_memory=3, htfint=1371)
var Candle[] candlesadd1371                  = array.new<Candle>(0)
var BOSdata bosdataadd1371                   = BOSdata.new()
htfadd1371.settings                 := SettingsHTFadd1371
htfadd1371.candles                  := candlesadd1371
htfadd1371.bosdata                  := bosdataadd1371
var CandleSet htfadd1372                     = CandleSet.new()
var CandleSettings SettingsHTFadd1372        = CandleSettings.new(htf="1372", max_memory=3, htfint=1372)
var Candle[] candlesadd1372                  = array.new<Candle>(0)
var BOSdata bosdataadd1372                   = BOSdata.new()
htfadd1372.settings                 := SettingsHTFadd1372
htfadd1372.candles                  := candlesadd1372
htfadd1372.bosdata                  := bosdataadd1372
var CandleSet htfadd1373                     = CandleSet.new()
var CandleSettings SettingsHTFadd1373        = CandleSettings.new(htf="1373", max_memory=3, htfint=1373)
var Candle[] candlesadd1373                  = array.new<Candle>(0)
var BOSdata bosdataadd1373                   = BOSdata.new()
htfadd1373.settings                 := SettingsHTFadd1373
htfadd1373.candles                  := candlesadd1373
htfadd1373.bosdata                  := bosdataadd1373
var CandleSet htfadd1374                     = CandleSet.new()
var CandleSettings SettingsHTFadd1374        = CandleSettings.new(htf="1374", max_memory=3, htfint=1374)
var Candle[] candlesadd1374                  = array.new<Candle>(0)
var BOSdata bosdataadd1374                   = BOSdata.new()
htfadd1374.settings                 := SettingsHTFadd1374
htfadd1374.candles                  := candlesadd1374
htfadd1374.bosdata                  := bosdataadd1374
var CandleSet htfadd1375                     = CandleSet.new()
var CandleSettings SettingsHTFadd1375        = CandleSettings.new(htf="1375", max_memory=3, htfint=1375)
var Candle[] candlesadd1375                  = array.new<Candle>(0)
var BOSdata bosdataadd1375                   = BOSdata.new()
htfadd1375.settings                 := SettingsHTFadd1375
htfadd1375.candles                  := candlesadd1375
htfadd1375.bosdata                  := bosdataadd1375
var CandleSet htfadd1376                     = CandleSet.new()
var CandleSettings SettingsHTFadd1376        = CandleSettings.new(htf="1376", max_memory=3, htfint=1376)
var Candle[] candlesadd1376                  = array.new<Candle>(0)
var BOSdata bosdataadd1376                   = BOSdata.new()
htfadd1376.settings                 := SettingsHTFadd1376
htfadd1376.candles                  := candlesadd1376
htfadd1376.bosdata                  := bosdataadd1376
var CandleSet htfadd1377                     = CandleSet.new()
var CandleSettings SettingsHTFadd1377        = CandleSettings.new(htf="1377", max_memory=3, htfint=1377)
var Candle[] candlesadd1377                  = array.new<Candle>(0)
var BOSdata bosdataadd1377                   = BOSdata.new()
htfadd1377.settings                 := SettingsHTFadd1377
htfadd1377.candles                  := candlesadd1377
htfadd1377.bosdata                  := bosdataadd1377
var CandleSet htfadd1378                     = CandleSet.new()
var CandleSettings SettingsHTFadd1378        = CandleSettings.new(htf="1378", max_memory=3, htfint=1378)
var Candle[] candlesadd1378                  = array.new<Candle>(0)
var BOSdata bosdataadd1378                   = BOSdata.new()
htfadd1378.settings                 := SettingsHTFadd1378
htfadd1378.candles                  := candlesadd1378
htfadd1378.bosdata                  := bosdataadd1378
var CandleSet htfadd1379                     = CandleSet.new()
var CandleSettings SettingsHTFadd1379        = CandleSettings.new(htf="1379", max_memory=3, htfint=1379)
var Candle[] candlesadd1379                  = array.new<Candle>(0)
var BOSdata bosdataadd1379                   = BOSdata.new()
htfadd1379.settings                 := SettingsHTFadd1379
htfadd1379.candles                  := candlesadd1379
htfadd1379.bosdata                  := bosdataadd1379
var CandleSet htfadd1380                     = CandleSet.new()
var CandleSettings SettingsHTFadd1380        = CandleSettings.new(htf="1380", max_memory=3, htfint=1380)
var Candle[] candlesadd1380                  = array.new<Candle>(0)
var BOSdata bosdataadd1380                   = BOSdata.new()
htfadd1380.settings                 := SettingsHTFadd1380
htfadd1380.candles                  := candlesadd1380
htfadd1380.bosdata                  := bosdataadd1380
var CandleSet htfadd1381                     = CandleSet.new()
var CandleSettings SettingsHTFadd1381        = CandleSettings.new(htf="1381", max_memory=3, htfint=1381)
var Candle[] candlesadd1381                  = array.new<Candle>(0)
var BOSdata bosdataadd1381                   = BOSdata.new()
htfadd1381.settings                 := SettingsHTFadd1381
htfadd1381.candles                  := candlesadd1381
htfadd1381.bosdata                  := bosdataadd1381
var CandleSet htfadd1382                     = CandleSet.new()
var CandleSettings SettingsHTFadd1382        = CandleSettings.new(htf="1382", max_memory=3, htfint=1382)
var Candle[] candlesadd1382                  = array.new<Candle>(0)
var BOSdata bosdataadd1382                   = BOSdata.new()
htfadd1382.settings                 := SettingsHTFadd1382
htfadd1382.candles                  := candlesadd1382
htfadd1382.bosdata                  := bosdataadd1382
var CandleSet htfadd1383                     = CandleSet.new()
var CandleSettings SettingsHTFadd1383        = CandleSettings.new(htf="1383", max_memory=3, htfint=1383)
var Candle[] candlesadd1383                  = array.new<Candle>(0)
var BOSdata bosdataadd1383                   = BOSdata.new()
htfadd1383.settings                 := SettingsHTFadd1383
htfadd1383.candles                  := candlesadd1383
htfadd1383.bosdata                  := bosdataadd1383
var CandleSet htfadd1384                     = CandleSet.new()
var CandleSettings SettingsHTFadd1384        = CandleSettings.new(htf="1384", max_memory=3, htfint=1384)
var Candle[] candlesadd1384                  = array.new<Candle>(0)
var BOSdata bosdataadd1384                   = BOSdata.new()
htfadd1384.settings                 := SettingsHTFadd1384
htfadd1384.candles                  := candlesadd1384
htfadd1384.bosdata                  := bosdataadd1384
var CandleSet htfadd1385                     = CandleSet.new()
var CandleSettings SettingsHTFadd1385        = CandleSettings.new(htf="1385", max_memory=3, htfint=1385)
var Candle[] candlesadd1385                  = array.new<Candle>(0)
var BOSdata bosdataadd1385                   = BOSdata.new()
htfadd1385.settings                 := SettingsHTFadd1385
htfadd1385.candles                  := candlesadd1385
htfadd1385.bosdata                  := bosdataadd1385
var CandleSet htfadd1386                     = CandleSet.new()
var CandleSettings SettingsHTFadd1386        = CandleSettings.new(htf="1386", max_memory=3, htfint=1386)
var Candle[] candlesadd1386                  = array.new<Candle>(0)
var BOSdata bosdataadd1386                   = BOSdata.new()
htfadd1386.settings                 := SettingsHTFadd1386
htfadd1386.candles                  := candlesadd1386
htfadd1386.bosdata                  := bosdataadd1386
var CandleSet htfadd1387                     = CandleSet.new()
var CandleSettings SettingsHTFadd1387        = CandleSettings.new(htf="1387", max_memory=3, htfint=1387)
var Candle[] candlesadd1387                  = array.new<Candle>(0)
var BOSdata bosdataadd1387                   = BOSdata.new()
htfadd1387.settings                 := SettingsHTFadd1387
htfadd1387.candles                  := candlesadd1387
htfadd1387.bosdata                  := bosdataadd1387
var CandleSet htfadd1388                     = CandleSet.new()
var CandleSettings SettingsHTFadd1388        = CandleSettings.new(htf="1388", max_memory=3, htfint=1388)
var Candle[] candlesadd1388                  = array.new<Candle>(0)
var BOSdata bosdataadd1388                   = BOSdata.new()
htfadd1388.settings                 := SettingsHTFadd1388
htfadd1388.candles                  := candlesadd1388
htfadd1388.bosdata                  := bosdataadd1388
var CandleSet htfadd1389                     = CandleSet.new()
var CandleSettings SettingsHTFadd1389        = CandleSettings.new(htf="1389", max_memory=3, htfint=1389)
var Candle[] candlesadd1389                  = array.new<Candle>(0)
var BOSdata bosdataadd1389                   = BOSdata.new()
htfadd1389.settings                 := SettingsHTFadd1389
htfadd1389.candles                  := candlesadd1389
htfadd1389.bosdata                  := bosdataadd1389
var CandleSet htfadd1390                     = CandleSet.new()
var CandleSettings SettingsHTFadd1390        = CandleSettings.new(htf="1390", max_memory=3, htfint=1390)
var Candle[] candlesadd1390                  = array.new<Candle>(0)
var BOSdata bosdataadd1390                   = BOSdata.new()
htfadd1390.settings                 := SettingsHTFadd1390
htfadd1390.candles                  := candlesadd1390
htfadd1390.bosdata                  := bosdataadd1390
var CandleSet htfadd1391                     = CandleSet.new()
var CandleSettings SettingsHTFadd1391        = CandleSettings.new(htf="1391", max_memory=3, htfint=1391)
var Candle[] candlesadd1391                  = array.new<Candle>(0)
var BOSdata bosdataadd1391                   = BOSdata.new()
htfadd1391.settings                 := SettingsHTFadd1391
htfadd1391.candles                  := candlesadd1391
htfadd1391.bosdata                  := bosdataadd1391
var CandleSet htfadd1392                     = CandleSet.new()
var CandleSettings SettingsHTFadd1392        = CandleSettings.new(htf="1392", max_memory=3, htfint=1392)
var Candle[] candlesadd1392                  = array.new<Candle>(0)
var BOSdata bosdataadd1392                   = BOSdata.new()
htfadd1392.settings                 := SettingsHTFadd1392
htfadd1392.candles                  := candlesadd1392
htfadd1392.bosdata                  := bosdataadd1392
var CandleSet htfadd1393                     = CandleSet.new()
var CandleSettings SettingsHTFadd1393        = CandleSettings.new(htf="1393", max_memory=3, htfint=1393)
var Candle[] candlesadd1393                  = array.new<Candle>(0)
var BOSdata bosdataadd1393                   = BOSdata.new()
htfadd1393.settings                 := SettingsHTFadd1393
htfadd1393.candles                  := candlesadd1393
htfadd1393.bosdata                  := bosdataadd1393
var CandleSet htfadd1394                     = CandleSet.new()
var CandleSettings SettingsHTFadd1394        = CandleSettings.new(htf="1394", max_memory=3, htfint=1394)
var Candle[] candlesadd1394                  = array.new<Candle>(0)
var BOSdata bosdataadd1394                   = BOSdata.new()
htfadd1394.settings                 := SettingsHTFadd1394
htfadd1394.candles                  := candlesadd1394
htfadd1394.bosdata                  := bosdataadd1394
var CandleSet htfadd1395                     = CandleSet.new()
var CandleSettings SettingsHTFadd1395        = CandleSettings.new(htf="1395", max_memory=3, htfint=1395)
var Candle[] candlesadd1395                  = array.new<Candle>(0)
var BOSdata bosdataadd1395                   = BOSdata.new()
htfadd1395.settings                 := SettingsHTFadd1395
htfadd1395.candles                  := candlesadd1395
htfadd1395.bosdata                  := bosdataadd1395
var CandleSet htfadd1396                     = CandleSet.new()
var CandleSettings SettingsHTFadd1396        = CandleSettings.new(htf="1396", max_memory=3, htfint=1396)
var Candle[] candlesadd1396                  = array.new<Candle>(0)
var BOSdata bosdataadd1396                   = BOSdata.new()
htfadd1396.settings                 := SettingsHTFadd1396
htfadd1396.candles                  := candlesadd1396
htfadd1396.bosdata                  := bosdataadd1396
var CandleSet htfadd1397                     = CandleSet.new()
var CandleSettings SettingsHTFadd1397        = CandleSettings.new(htf="1397", max_memory=3, htfint=1397)
var Candle[] candlesadd1397                  = array.new<Candle>(0)
var BOSdata bosdataadd1397                   = BOSdata.new()
htfadd1397.settings                 := SettingsHTFadd1397
htfadd1397.candles                  := candlesadd1397
htfadd1397.bosdata                  := bosdataadd1397
var CandleSet htfadd1398                     = CandleSet.new()
var CandleSettings SettingsHTFadd1398        = CandleSettings.new(htf="1398", max_memory=3, htfint=1398)
var Candle[] candlesadd1398                  = array.new<Candle>(0)
var BOSdata bosdataadd1398                   = BOSdata.new()
htfadd1398.settings                 := SettingsHTFadd1398
htfadd1398.candles                  := candlesadd1398
htfadd1398.bosdata                  := bosdataadd1398
var CandleSet htfadd1399                     = CandleSet.new()
var CandleSettings SettingsHTFadd1399        = CandleSettings.new(htf="1399", max_memory=3, htfint=1399)
var Candle[] candlesadd1399                  = array.new<Candle>(0)
var BOSdata bosdataadd1399                   = BOSdata.new()
htfadd1399.settings                 := SettingsHTFadd1399
htfadd1399.candles                  := candlesadd1399
htfadd1399.bosdata                  := bosdataadd1399
var CandleSet htfadd1400                     = CandleSet.new()
var CandleSettings SettingsHTFadd1400        = CandleSettings.new(htf="1400", max_memory=3, htfint=1400)
var Candle[] candlesadd1400                  = array.new<Candle>(0)
var BOSdata bosdataadd1400                   = BOSdata.new()
htfadd1400.settings                 := SettingsHTFadd1400
htfadd1400.candles                  := candlesadd1400
htfadd1400.bosdata                  := bosdataadd1400
var CandleSet htfadd1401                     = CandleSet.new()
var CandleSettings SettingsHTFadd1401        = CandleSettings.new(htf="1401", max_memory=3, htfint=1401)
var Candle[] candlesadd1401                  = array.new<Candle>(0)
var BOSdata bosdataadd1401                   = BOSdata.new()
htfadd1401.settings                 := SettingsHTFadd1401
htfadd1401.candles                  := candlesadd1401
htfadd1401.bosdata                  := bosdataadd1401
var CandleSet htfadd1402                     = CandleSet.new()
var CandleSettings SettingsHTFadd1402        = CandleSettings.new(htf="1402", max_memory=3, htfint=1402)
var Candle[] candlesadd1402                  = array.new<Candle>(0)
var BOSdata bosdataadd1402                   = BOSdata.new()
htfadd1402.settings                 := SettingsHTFadd1402
htfadd1402.candles                  := candlesadd1402
htfadd1402.bosdata                  := bosdataadd1402
var CandleSet htfadd1403                     = CandleSet.new()
var CandleSettings SettingsHTFadd1403        = CandleSettings.new(htf="1403", max_memory=3, htfint=1403)
var Candle[] candlesadd1403                  = array.new<Candle>(0)
var BOSdata bosdataadd1403                   = BOSdata.new()
htfadd1403.settings                 := SettingsHTFadd1403
htfadd1403.candles                  := candlesadd1403
htfadd1403.bosdata                  := bosdataadd1403
var CandleSet htfadd1404                     = CandleSet.new()
var CandleSettings SettingsHTFadd1404        = CandleSettings.new(htf="1404", max_memory=3, htfint=1404)
var Candle[] candlesadd1404                  = array.new<Candle>(0)
var BOSdata bosdataadd1404                   = BOSdata.new()
htfadd1404.settings                 := SettingsHTFadd1404
htfadd1404.candles                  := candlesadd1404
htfadd1404.bosdata                  := bosdataadd1404
var CandleSet htfadd1405                     = CandleSet.new()
var CandleSettings SettingsHTFadd1405        = CandleSettings.new(htf="1405", max_memory=3, htfint=1405)
var Candle[] candlesadd1405                  = array.new<Candle>(0)
var BOSdata bosdataadd1405                   = BOSdata.new()
htfadd1405.settings                 := SettingsHTFadd1405
htfadd1405.candles                  := candlesadd1405
htfadd1405.bosdata                  := bosdataadd1405
var CandleSet htfadd1406                     = CandleSet.new()
var CandleSettings SettingsHTFadd1406        = CandleSettings.new(htf="1406", max_memory=3, htfint=1406)
var Candle[] candlesadd1406                  = array.new<Candle>(0)
var BOSdata bosdataadd1406                   = BOSdata.new()
htfadd1406.settings                 := SettingsHTFadd1406
htfadd1406.candles                  := candlesadd1406
htfadd1406.bosdata                  := bosdataadd1406
var CandleSet htfadd1407                     = CandleSet.new()
var CandleSettings SettingsHTFadd1407        = CandleSettings.new(htf="1407", max_memory=3, htfint=1407)
var Candle[] candlesadd1407                  = array.new<Candle>(0)
var BOSdata bosdataadd1407                   = BOSdata.new()
htfadd1407.settings                 := SettingsHTFadd1407
htfadd1407.candles                  := candlesadd1407
htfadd1407.bosdata                  := bosdataadd1407
var CandleSet htfadd1408                     = CandleSet.new()
var CandleSettings SettingsHTFadd1408        = CandleSettings.new(htf="1408", max_memory=3, htfint=1408)
var Candle[] candlesadd1408                  = array.new<Candle>(0)
var BOSdata bosdataadd1408                   = BOSdata.new()
htfadd1408.settings                 := SettingsHTFadd1408
htfadd1408.candles                  := candlesadd1408
htfadd1408.bosdata                  := bosdataadd1408
var CandleSet htfadd1409                     = CandleSet.new()
var CandleSettings SettingsHTFadd1409        = CandleSettings.new(htf="1409", max_memory=3, htfint=1409)
var Candle[] candlesadd1409                  = array.new<Candle>(0)
var BOSdata bosdataadd1409                   = BOSdata.new()
htfadd1409.settings                 := SettingsHTFadd1409
htfadd1409.candles                  := candlesadd1409
htfadd1409.bosdata                  := bosdataadd1409
var CandleSet htfadd1410                     = CandleSet.new()
var CandleSettings SettingsHTFadd1410        = CandleSettings.new(htf="1410", max_memory=3, htfint=1410)
var Candle[] candlesadd1410                  = array.new<Candle>(0)
var BOSdata bosdataadd1410                   = BOSdata.new()
htfadd1410.settings                 := SettingsHTFadd1410
htfadd1410.candles                  := candlesadd1410
htfadd1410.bosdata                  := bosdataadd1410
var CandleSet htfadd1411                     = CandleSet.new()
var CandleSettings SettingsHTFadd1411        = CandleSettings.new(htf="1411", max_memory=3, htfint=1411)
var Candle[] candlesadd1411                  = array.new<Candle>(0)
var BOSdata bosdataadd1411                   = BOSdata.new()
htfadd1411.settings                 := SettingsHTFadd1411
htfadd1411.candles                  := candlesadd1411
htfadd1411.bosdata                  := bosdataadd1411
var CandleSet htfadd1412                     = CandleSet.new()
var CandleSettings SettingsHTFadd1412        = CandleSettings.new(htf="1412", max_memory=3, htfint=1412)
var Candle[] candlesadd1412                  = array.new<Candle>(0)
var BOSdata bosdataadd1412                   = BOSdata.new()
htfadd1412.settings                 := SettingsHTFadd1412
htfadd1412.candles                  := candlesadd1412
htfadd1412.bosdata                  := bosdataadd1412
var CandleSet htfadd1413                     = CandleSet.new()
var CandleSettings SettingsHTFadd1413        = CandleSettings.new(htf="1413", max_memory=3, htfint=1413)
var Candle[] candlesadd1413                  = array.new<Candle>(0)
var BOSdata bosdataadd1413                   = BOSdata.new()
htfadd1413.settings                 := SettingsHTFadd1413
htfadd1413.candles                  := candlesadd1413
htfadd1413.bosdata                  := bosdataadd1413
var CandleSet htfadd1414                     = CandleSet.new()
var CandleSettings SettingsHTFadd1414        = CandleSettings.new(htf="1414", max_memory=3, htfint=1414)
var Candle[] candlesadd1414                  = array.new<Candle>(0)
var BOSdata bosdataadd1414                   = BOSdata.new()
htfadd1414.settings                 := SettingsHTFadd1414
htfadd1414.candles                  := candlesadd1414
htfadd1414.bosdata                  := bosdataadd1414
var CandleSet htfadd1415                     = CandleSet.new()
var CandleSettings SettingsHTFadd1415        = CandleSettings.new(htf="1415", max_memory=3, htfint=1415)
var Candle[] candlesadd1415                  = array.new<Candle>(0)
var BOSdata bosdataadd1415                   = BOSdata.new()
htfadd1415.settings                 := SettingsHTFadd1415
htfadd1415.candles                  := candlesadd1415
htfadd1415.bosdata                  := bosdataadd1415
var CandleSet htfadd1416                     = CandleSet.new()
var CandleSettings SettingsHTFadd1416        = CandleSettings.new(htf="1416", max_memory=3, htfint=1416)
var Candle[] candlesadd1416                  = array.new<Candle>(0)
var BOSdata bosdataadd1416                   = BOSdata.new()
htfadd1416.settings                 := SettingsHTFadd1416
htfadd1416.candles                  := candlesadd1416
htfadd1416.bosdata                  := bosdataadd1416
var CandleSet htfadd1417                     = CandleSet.new()
var CandleSettings SettingsHTFadd1417        = CandleSettings.new(htf="1417", max_memory=3, htfint=1417)
var Candle[] candlesadd1417                  = array.new<Candle>(0)
var BOSdata bosdataadd1417                   = BOSdata.new()
htfadd1417.settings                 := SettingsHTFadd1417
htfadd1417.candles                  := candlesadd1417
htfadd1417.bosdata                  := bosdataadd1417
var CandleSet htfadd1418                     = CandleSet.new()
var CandleSettings SettingsHTFadd1418        = CandleSettings.new(htf="1418", max_memory=3, htfint=1418)
var Candle[] candlesadd1418                  = array.new<Candle>(0)
var BOSdata bosdataadd1418                   = BOSdata.new()
htfadd1418.settings                 := SettingsHTFadd1418
htfadd1418.candles                  := candlesadd1418
htfadd1418.bosdata                  := bosdataadd1418
var CandleSet htfadd1419                     = CandleSet.new()
var CandleSettings SettingsHTFadd1419        = CandleSettings.new(htf="1419", max_memory=3, htfint=1419)
var Candle[] candlesadd1419                  = array.new<Candle>(0)
var BOSdata bosdataadd1419                   = BOSdata.new()
htfadd1419.settings                 := SettingsHTFadd1419
htfadd1419.candles                  := candlesadd1419
htfadd1419.bosdata                  := bosdataadd1419
var CandleSet htfadd1420                     = CandleSet.new()
var CandleSettings SettingsHTFadd1420        = CandleSettings.new(htf="1420", max_memory=3, htfint=1420)
var Candle[] candlesadd1420                  = array.new<Candle>(0)
var BOSdata bosdataadd1420                   = BOSdata.new()
htfadd1420.settings                 := SettingsHTFadd1420
htfadd1420.candles                  := candlesadd1420
htfadd1420.bosdata                  := bosdataadd1420
var CandleSet htfadd1421                     = CandleSet.new()
var CandleSettings SettingsHTFadd1421        = CandleSettings.new(htf="1421", max_memory=3, htfint=1421)
var Candle[] candlesadd1421                  = array.new<Candle>(0)
var BOSdata bosdataadd1421                   = BOSdata.new()
htfadd1421.settings                 := SettingsHTFadd1421
htfadd1421.candles                  := candlesadd1421
htfadd1421.bosdata                  := bosdataadd1421
var CandleSet htfadd1422                     = CandleSet.new()
var CandleSettings SettingsHTFadd1422        = CandleSettings.new(htf="1422", max_memory=3, htfint=1422)
var Candle[] candlesadd1422                  = array.new<Candle>(0)
var BOSdata bosdataadd1422                   = BOSdata.new()
htfadd1422.settings                 := SettingsHTFadd1422
htfadd1422.candles                  := candlesadd1422
htfadd1422.bosdata                  := bosdataadd1422
var CandleSet htfadd1423                     = CandleSet.new()
var CandleSettings SettingsHTFadd1423        = CandleSettings.new(htf="1423", max_memory=3, htfint=1423)
var Candle[] candlesadd1423                  = array.new<Candle>(0)
var BOSdata bosdataadd1423                   = BOSdata.new()
htfadd1423.settings                 := SettingsHTFadd1423
htfadd1423.candles                  := candlesadd1423
htfadd1423.bosdata                  := bosdataadd1423
var CandleSet htfadd1424                     = CandleSet.new()
var CandleSettings SettingsHTFadd1424        = CandleSettings.new(htf="1424", max_memory=3, htfint=1424)
var Candle[] candlesadd1424                  = array.new<Candle>(0)
var BOSdata bosdataadd1424                   = BOSdata.new()
htfadd1424.settings                 := SettingsHTFadd1424
htfadd1424.candles                  := candlesadd1424
htfadd1424.bosdata                  := bosdataadd1424
var CandleSet htfadd1425                     = CandleSet.new()
var CandleSettings SettingsHTFadd1425        = CandleSettings.new(htf="1425", max_memory=3, htfint=1425)
var Candle[] candlesadd1425                  = array.new<Candle>(0)
var BOSdata bosdataadd1425                   = BOSdata.new()
htfadd1425.settings                 := SettingsHTFadd1425
htfadd1425.candles                  := candlesadd1425
htfadd1425.bosdata                  := bosdataadd1425
var CandleSet htfadd1426                     = CandleSet.new()
var CandleSettings SettingsHTFadd1426        = CandleSettings.new(htf="1426", max_memory=3, htfint=1426)
var Candle[] candlesadd1426                  = array.new<Candle>(0)
var BOSdata bosdataadd1426                   = BOSdata.new()
htfadd1426.settings                 := SettingsHTFadd1426
htfadd1426.candles                  := candlesadd1426
htfadd1426.bosdata                  := bosdataadd1426
var CandleSet htfadd1427                     = CandleSet.new()
var CandleSettings SettingsHTFadd1427        = CandleSettings.new(htf="1427", max_memory=3, htfint=1427)
var Candle[] candlesadd1427                  = array.new<Candle>(0)
var BOSdata bosdataadd1427                   = BOSdata.new()
htfadd1427.settings                 := SettingsHTFadd1427
htfadd1427.candles                  := candlesadd1427
htfadd1427.bosdata                  := bosdataadd1427
var CandleSet htfadd1428                     = CandleSet.new()
var CandleSettings SettingsHTFadd1428        = CandleSettings.new(htf="1428", max_memory=3, htfint=1428)
var Candle[] candlesadd1428                  = array.new<Candle>(0)
var BOSdata bosdataadd1428                   = BOSdata.new()
htfadd1428.settings                 := SettingsHTFadd1428
htfadd1428.candles                  := candlesadd1428
htfadd1428.bosdata                  := bosdataadd1428
var CandleSet htfadd1429                     = CandleSet.new()
var CandleSettings SettingsHTFadd1429        = CandleSettings.new(htf="1429", max_memory=3, htfint=1429)
var Candle[] candlesadd1429                  = array.new<Candle>(0)
var BOSdata bosdataadd1429                   = BOSdata.new()
htfadd1429.settings                 := SettingsHTFadd1429
htfadd1429.candles                  := candlesadd1429
htfadd1429.bosdata                  := bosdataadd1429
var CandleSet htfadd1430                     = CandleSet.new()
var CandleSettings SettingsHTFadd1430        = CandleSettings.new(htf="1430", max_memory=3, htfint=1430)
var Candle[] candlesadd1430                  = array.new<Candle>(0)
var BOSdata bosdataadd1430                   = BOSdata.new()
htfadd1430.settings                 := SettingsHTFadd1430
htfadd1430.candles                  := candlesadd1430
htfadd1430.bosdata                  := bosdataadd1430
var CandleSet htfadd1431                     = CandleSet.new()
var CandleSettings SettingsHTFadd1431        = CandleSettings.new(htf="1431", max_memory=3, htfint=1431)
var Candle[] candlesadd1431                  = array.new<Candle>(0)
var BOSdata bosdataadd1431                   = BOSdata.new()
htfadd1431.settings                 := SettingsHTFadd1431
htfadd1431.candles                  := candlesadd1431
htfadd1431.bosdata                  := bosdataadd1431
var CandleSet htfadd1432                     = CandleSet.new()
var CandleSettings SettingsHTFadd1432        = CandleSettings.new(htf="1432", max_memory=3, htfint=1432)
var Candle[] candlesadd1432                  = array.new<Candle>(0)
var BOSdata bosdataadd1432                   = BOSdata.new()
htfadd1432.settings                 := SettingsHTFadd1432
htfadd1432.candles                  := candlesadd1432
htfadd1432.bosdata                  := bosdataadd1432
var CandleSet htfadd1433                     = CandleSet.new()
var CandleSettings SettingsHTFadd1433        = CandleSettings.new(htf="1433", max_memory=3, htfint=1433)
var Candle[] candlesadd1433                  = array.new<Candle>(0)
var BOSdata bosdataadd1433                   = BOSdata.new()
htfadd1433.settings                 := SettingsHTFadd1433
htfadd1433.candles                  := candlesadd1433
htfadd1433.bosdata                  := bosdataadd1433
var CandleSet htfadd1434                     = CandleSet.new()
var CandleSettings SettingsHTFadd1434        = CandleSettings.new(htf="1434", max_memory=3, htfint=1434)
var Candle[] candlesadd1434                  = array.new<Candle>(0)
var BOSdata bosdataadd1434                   = BOSdata.new()
htfadd1434.settings                 := SettingsHTFadd1434
htfadd1434.candles                  := candlesadd1434
htfadd1434.bosdata                  := bosdataadd1434
var CandleSet htfadd1435                     = CandleSet.new()
var CandleSettings SettingsHTFadd1435        = CandleSettings.new(htf="1435", max_memory=3, htfint=1435)
var Candle[] candlesadd1435                  = array.new<Candle>(0)
var BOSdata bosdataadd1435                   = BOSdata.new()
htfadd1435.settings                 := SettingsHTFadd1435
htfadd1435.candles                  := candlesadd1435
htfadd1435.bosdata                  := bosdataadd1435
var CandleSet htfadd1436                     = CandleSet.new()
var CandleSettings SettingsHTFadd1436        = CandleSettings.new(htf="1436", max_memory=3, htfint=1436)
var Candle[] candlesadd1436                  = array.new<Candle>(0)
var BOSdata bosdataadd1436                   = BOSdata.new()
htfadd1436.settings                 := SettingsHTFadd1436
htfadd1436.candles                  := candlesadd1436
htfadd1436.bosdata                  := bosdataadd1436
var CandleSet htfadd1437                     = CandleSet.new()
var CandleSettings SettingsHTFadd1437        = CandleSettings.new(htf="1437", max_memory=3, htfint=1437)
var Candle[] candlesadd1437                  = array.new<Candle>(0)
var BOSdata bosdataadd1437                   = BOSdata.new()
htfadd1437.settings                 := SettingsHTFadd1437
htfadd1437.candles                  := candlesadd1437
htfadd1437.bosdata                  := bosdataadd1437
var CandleSet htfadd1438                     = CandleSet.new()
var CandleSettings SettingsHTFadd1438        = CandleSettings.new(htf="1438", max_memory=3, htfint=1438)
var Candle[] candlesadd1438                  = array.new<Candle>(0)
var BOSdata bosdataadd1438                   = BOSdata.new()
htfadd1438.settings                 := SettingsHTFadd1438
htfadd1438.candles                  := candlesadd1438
htfadd1438.bosdata                  := bosdataadd1438
var CandleSet htfadd1439                     = CandleSet.new()
var CandleSettings SettingsHTFadd1439        = CandleSettings.new(htf="1439", max_memory=3, htfint=1439)
var Candle[] candlesadd1439                  = array.new<Candle>(0)
var BOSdata bosdataadd1439                   = BOSdata.new()
htfadd1439.settings                 := SettingsHTFadd1439
htfadd1439.candles                  := candlesadd1439
htfadd1439.bosdata                  := bosdataadd1439
var CandleSet htfadd1440                     = CandleSet.new()
var CandleSettings SettingsHTFadd1440        = CandleSettings.new(htf="1440", max_memory=3, htfint=1440)
var Candle[] candlesadd1440                  = array.new<Candle>(0)
var BOSdata bosdataadd1440                   = BOSdata.new()
htfadd1440.settings                 := SettingsHTFadd1440
htfadd1440.candles                  := candlesadd1440
htfadd1440.bosdata                  := bosdataadd1440

if true
    htfadd1.Monitor().BOSJudge()
    htfadd2.Monitor().BOSJudge()
    htfadd3.Monitor().BOSJudge()
    htfadd4.Monitor().BOSJudge()
    htfadd5.Monitor().BOSJudge()
    htfadd6.Monitor().BOSJudge()
    htfadd7.Monitor().BOSJudge()
    htfadd8.Monitor().BOSJudge()
    htfadd9.Monitor().BOSJudge()
    htfadd10.Monitor().BOSJudge()
    htfadd11.Monitor().BOSJudge()
    htfadd12.Monitor().BOSJudge()
    htfadd13.Monitor().BOSJudge()
    htfadd14.Monitor().BOSJudge()
    htfadd15.Monitor().BOSJudge()
    htfadd16.Monitor().BOSJudge()
    htfadd17.Monitor().BOSJudge()
    htfadd18.Monitor().BOSJudge()
    htfadd19.Monitor().BOSJudge()
    htfadd20.Monitor().BOSJudge()
    htfadd21.Monitor().BOSJudge()
    htfadd22.Monitor().BOSJudge()
    htfadd23.Monitor().BOSJudge()
    htfadd24.Monitor().BOSJudge()
    htfadd25.Monitor().BOSJudge()
    htfadd26.Monitor().BOSJudge()
    htfadd27.Monitor().BOSJudge()
    htfadd28.Monitor().BOSJudge()
    htfadd29.Monitor().BOSJudge()
    htfadd30.Monitor().BOSJudge()
    htfadd31.Monitor().BOSJudge()
    htfadd32.Monitor().BOSJudge()
    htfadd33.Monitor().BOSJudge()
    htfadd34.Monitor().BOSJudge()
    htfadd35.Monitor().BOSJudge()
    htfadd36.Monitor().BOSJudge()
    htfadd37.Monitor().BOSJudge()
    htfadd38.Monitor().BOSJudge()
    htfadd39.Monitor().BOSJudge()
    htfadd40.Monitor().BOSJudge()
    htfadd41.Monitor().BOSJudge()
    htfadd42.Monitor().BOSJudge()
    htfadd43.Monitor().BOSJudge()
    htfadd44.Monitor().BOSJudge()
    htfadd45.Monitor().BOSJudge()
    htfadd46.Monitor().BOSJudge()
    htfadd47.Monitor().BOSJudge()
    htfadd48.Monitor().BOSJudge()
    htfadd49.Monitor().BOSJudge()
    htfadd50.Monitor().BOSJudge()
    htfadd51.Monitor().BOSJudge()
    htfadd52.Monitor().BOSJudge()
    htfadd53.Monitor().BOSJudge()
    htfadd54.Monitor().BOSJudge()
    htfadd55.Monitor().BOSJudge()
    htfadd56.Monitor().BOSJudge()
    htfadd57.Monitor().BOSJudge()
    htfadd58.Monitor().BOSJudge()
    htfadd59.Monitor().BOSJudge()
    htfadd60.Monitor().BOSJudge()
    htfadd61.Monitor().BOSJudge()
    htfadd62.Monitor().BOSJudge()
    htfadd63.Monitor().BOSJudge()
    htfadd64.Monitor().BOSJudge()
    htfadd65.Monitor().BOSJudge()
    htfadd66.Monitor().BOSJudge()
    htfadd67.Monitor().BOSJudge()
    htfadd68.Monitor().BOSJudge()
    htfadd69.Monitor().BOSJudge()
    htfadd70.Monitor().BOSJudge()
    htfadd71.Monitor().BOSJudge()
    htfadd72.Monitor().BOSJudge()
    htfadd73.Monitor().BOSJudge()
    htfadd74.Monitor().BOSJudge()
    htfadd75.Monitor().BOSJudge()
    htfadd76.Monitor().BOSJudge()
    htfadd77.Monitor().BOSJudge()
    htfadd78.Monitor().BOSJudge()
    htfadd79.Monitor().BOSJudge()
    htfadd80.Monitor().BOSJudge()
    htfadd81.Monitor().BOSJudge()
    htfadd82.Monitor().BOSJudge()
    htfadd83.Monitor().BOSJudge()
    htfadd84.Monitor().BOSJudge()
    htfadd85.Monitor().BOSJudge()
    htfadd86.Monitor().BOSJudge()
    htfadd87.Monitor().BOSJudge()
    htfadd88.Monitor().BOSJudge()
    htfadd89.Monitor().BOSJudge()
    htfadd90.Monitor().BOSJudge()
    htfadd91.Monitor().BOSJudge()
    htfadd92.Monitor().BOSJudge()
    htfadd93.Monitor().BOSJudge()
    htfadd94.Monitor().BOSJudge()
    htfadd95.Monitor().BOSJudge()
    htfadd96.Monitor().BOSJudge()
    htfadd97.Monitor().BOSJudge()
    htfadd98.Monitor().BOSJudge()
    htfadd99.Monitor().BOSJudge()
    htfadd100.Monitor().BOSJudge()
    htfadd101.Monitor().BOSJudge()
    htfadd102.Monitor().BOSJudge()
    htfadd103.Monitor().BOSJudge()
    htfadd104.Monitor().BOSJudge()
    htfadd105.Monitor().BOSJudge()
    htfadd106.Monitor().BOSJudge()
    htfadd107.Monitor().BOSJudge()
    htfadd108.Monitor().BOSJudge()
    htfadd109.Monitor().BOSJudge()
    htfadd110.Monitor().BOSJudge()
    htfadd111.Monitor().BOSJudge()
    htfadd112.Monitor().BOSJudge()
    htfadd113.Monitor().BOSJudge()
    htfadd114.Monitor().BOSJudge()
    htfadd115.Monitor().BOSJudge()
    htfadd116.Monitor().BOSJudge()
    htfadd117.Monitor().BOSJudge()
    htfadd118.Monitor().BOSJudge()
    htfadd119.Monitor().BOSJudge()
    htfadd120.Monitor().BOSJudge()
    htfadd121.Monitor().BOSJudge()
    htfadd122.Monitor().BOSJudge()
    htfadd123.Monitor().BOSJudge()
    htfadd124.Monitor().BOSJudge()
    htfadd125.Monitor().BOSJudge()
    htfadd126.Monitor().BOSJudge()
    htfadd127.Monitor().BOSJudge()
    htfadd128.Monitor().BOSJudge()
    htfadd129.Monitor().BOSJudge()
    htfadd130.Monitor().BOSJudge()
    htfadd131.Monitor().BOSJudge()
    htfadd132.Monitor().BOSJudge()
    htfadd133.Monitor().BOSJudge()
    htfadd134.Monitor().BOSJudge()
    htfadd135.Monitor().BOSJudge()
    htfadd136.Monitor().BOSJudge()
    htfadd137.Monitor().BOSJudge()
    htfadd138.Monitor().BOSJudge()
    htfadd139.Monitor().BOSJudge()
    htfadd140.Monitor().BOSJudge()
    htfadd141.Monitor().BOSJudge()
    htfadd142.Monitor().BOSJudge()
    htfadd143.Monitor().BOSJudge()
    htfadd144.Monitor().BOSJudge()
    htfadd145.Monitor().BOSJudge()
    htfadd146.Monitor().BOSJudge()
    htfadd147.Monitor().BOSJudge()
    htfadd148.Monitor().BOSJudge()
    htfadd149.Monitor().BOSJudge()
    htfadd150.Monitor().BOSJudge()
    htfadd151.Monitor().BOSJudge()
    htfadd152.Monitor().BOSJudge()
    htfadd153.Monitor().BOSJudge()
    htfadd154.Monitor().BOSJudge()
    htfadd155.Monitor().BOSJudge()
    htfadd156.Monitor().BOSJudge()
    htfadd157.Monitor().BOSJudge()
    htfadd158.Monitor().BOSJudge()
    htfadd159.Monitor().BOSJudge()
    htfadd160.Monitor().BOSJudge()
    htfadd161.Monitor().BOSJudge()
    htfadd162.Monitor().BOSJudge()
    htfadd163.Monitor().BOSJudge()
    htfadd164.Monitor().BOSJudge()
    htfadd165.Monitor().BOSJudge()
    htfadd166.Monitor().BOSJudge()
    htfadd167.Monitor().BOSJudge()
    htfadd168.Monitor().BOSJudge()
    htfadd169.Monitor().BOSJudge()
    htfadd170.Monitor().BOSJudge()
    htfadd171.Monitor().BOSJudge()
    htfadd172.Monitor().BOSJudge()
    htfadd173.Monitor().BOSJudge()
    htfadd174.Monitor().BOSJudge()
    htfadd175.Monitor().BOSJudge()
    htfadd176.Monitor().BOSJudge()
    htfadd177.Monitor().BOSJudge()
    htfadd178.Monitor().BOSJudge()
    htfadd179.Monitor().BOSJudge()
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
    htfadd541.Monitor().BOSJudge()
    htfadd542.Monitor().BOSJudge()
    htfadd543.Monitor().BOSJudge()
    htfadd544.Monitor().BOSJudge()
    htfadd545.Monitor().BOSJudge()
    htfadd546.Monitor().BOSJudge()
    htfadd547.Monitor().BOSJudge()
    htfadd548.Monitor().BOSJudge()
    htfadd549.Monitor().BOSJudge()
    htfadd550.Monitor().BOSJudge()
    htfadd551.Monitor().BOSJudge()
    htfadd552.Monitor().BOSJudge()
    htfadd553.Monitor().BOSJudge()
    htfadd554.Monitor().BOSJudge()
    htfadd555.Monitor().BOSJudge()
    htfadd556.Monitor().BOSJudge()
    htfadd557.Monitor().BOSJudge()
    htfadd558.Monitor().BOSJudge()
    htfadd559.Monitor().BOSJudge()
    htfadd560.Monitor().BOSJudge()
    htfadd561.Monitor().BOSJudge()
    htfadd562.Monitor().BOSJudge()
    htfadd563.Monitor().BOSJudge()
    htfadd564.Monitor().BOSJudge()
    htfadd565.Monitor().BOSJudge()
    htfadd566.Monitor().BOSJudge()
    htfadd567.Monitor().BOSJudge()
    htfadd568.Monitor().BOSJudge()
    htfadd569.Monitor().BOSJudge()
    htfadd570.Monitor().BOSJudge()
    htfadd571.Monitor().BOSJudge()
    htfadd572.Monitor().BOSJudge()
    htfadd573.Monitor().BOSJudge()
    htfadd574.Monitor().BOSJudge()
    htfadd575.Monitor().BOSJudge()
    htfadd576.Monitor().BOSJudge()
    htfadd577.Monitor().BOSJudge()
    htfadd578.Monitor().BOSJudge()
    htfadd579.Monitor().BOSJudge()
    htfadd580.Monitor().BOSJudge()
    htfadd581.Monitor().BOSJudge()
    htfadd582.Monitor().BOSJudge()
    htfadd583.Monitor().BOSJudge()
    htfadd584.Monitor().BOSJudge()
    htfadd585.Monitor().BOSJudge()
    htfadd586.Monitor().BOSJudge()
    htfadd587.Monitor().BOSJudge()
    htfadd588.Monitor().BOSJudge()
    htfadd589.Monitor().BOSJudge()
    htfadd590.Monitor().BOSJudge()
    htfadd591.Monitor().BOSJudge()
    htfadd592.Monitor().BOSJudge()
    htfadd593.Monitor().BOSJudge()
    htfadd594.Monitor().BOSJudge()
    htfadd595.Monitor().BOSJudge()
    htfadd596.Monitor().BOSJudge()
    htfadd597.Monitor().BOSJudge()
    htfadd598.Monitor().BOSJudge()
    htfadd599.Monitor().BOSJudge()
    htfadd600.Monitor().BOSJudge()
    htfadd601.Monitor().BOSJudge()
    htfadd602.Monitor().BOSJudge()
    htfadd603.Monitor().BOSJudge()
    htfadd604.Monitor().BOSJudge()
    htfadd605.Monitor().BOSJudge()
    htfadd606.Monitor().BOSJudge()
    htfadd607.Monitor().BOSJudge()
    htfadd608.Monitor().BOSJudge()
    htfadd609.Monitor().BOSJudge()
    htfadd610.Monitor().BOSJudge()
    htfadd611.Monitor().BOSJudge()
    htfadd612.Monitor().BOSJudge()
    htfadd613.Monitor().BOSJudge()
    htfadd614.Monitor().BOSJudge()
    htfadd615.Monitor().BOSJudge()
    htfadd616.Monitor().BOSJudge()
    htfadd617.Monitor().BOSJudge()
    htfadd618.Monitor().BOSJudge()
    htfadd619.Monitor().BOSJudge()
    htfadd620.Monitor().BOSJudge()
    htfadd621.Monitor().BOSJudge()
    htfadd622.Monitor().BOSJudge()
    htfadd623.Monitor().BOSJudge()
    htfadd624.Monitor().BOSJudge()
    htfadd625.Monitor().BOSJudge()
    htfadd626.Monitor().BOSJudge()
    htfadd627.Monitor().BOSJudge()
    htfadd628.Monitor().BOSJudge()
    htfadd629.Monitor().BOSJudge()
    htfadd630.Monitor().BOSJudge()
    htfadd631.Monitor().BOSJudge()
    htfadd632.Monitor().BOSJudge()
    htfadd633.Monitor().BOSJudge()
    htfadd634.Monitor().BOSJudge()
    htfadd635.Monitor().BOSJudge()
    htfadd636.Monitor().BOSJudge()
    htfadd637.Monitor().BOSJudge()
    htfadd638.Monitor().BOSJudge()
    htfadd639.Monitor().BOSJudge()
    htfadd640.Monitor().BOSJudge()
    htfadd641.Monitor().BOSJudge()
    htfadd642.Monitor().BOSJudge()
    htfadd643.Monitor().BOSJudge()
    htfadd644.Monitor().BOSJudge()
    htfadd645.Monitor().BOSJudge()
    htfadd646.Monitor().BOSJudge()
    htfadd647.Monitor().BOSJudge()
    htfadd648.Monitor().BOSJudge()
    htfadd649.Monitor().BOSJudge()
    htfadd650.Monitor().BOSJudge()
    htfadd651.Monitor().BOSJudge()
    htfadd652.Monitor().BOSJudge()
    htfadd653.Monitor().BOSJudge()
    htfadd654.Monitor().BOSJudge()
    htfadd655.Monitor().BOSJudge()
    htfadd656.Monitor().BOSJudge()
    htfadd657.Monitor().BOSJudge()
    htfadd658.Monitor().BOSJudge()
    htfadd659.Monitor().BOSJudge()
    htfadd660.Monitor().BOSJudge()
    htfadd661.Monitor().BOSJudge()
    htfadd662.Monitor().BOSJudge()
    htfadd663.Monitor().BOSJudge()
    htfadd664.Monitor().BOSJudge()
    htfadd665.Monitor().BOSJudge()
    htfadd666.Monitor().BOSJudge()
    htfadd667.Monitor().BOSJudge()
    htfadd668.Monitor().BOSJudge()
    htfadd669.Monitor().BOSJudge()
    htfadd670.Monitor().BOSJudge()
    htfadd671.Monitor().BOSJudge()
    htfadd672.Monitor().BOSJudge()
    htfadd673.Monitor().BOSJudge()
    htfadd674.Monitor().BOSJudge()
    htfadd675.Monitor().BOSJudge()
    htfadd676.Monitor().BOSJudge()
    htfadd677.Monitor().BOSJudge()
    htfadd678.Monitor().BOSJudge()
    htfadd679.Monitor().BOSJudge()
    htfadd680.Monitor().BOSJudge()
    htfadd681.Monitor().BOSJudge()
    htfadd682.Monitor().BOSJudge()
    htfadd683.Monitor().BOSJudge()
    htfadd684.Monitor().BOSJudge()
    htfadd685.Monitor().BOSJudge()
    htfadd686.Monitor().BOSJudge()
    htfadd687.Monitor().BOSJudge()
    htfadd688.Monitor().BOSJudge()
    htfadd689.Monitor().BOSJudge()
    htfadd690.Monitor().BOSJudge()
    htfadd691.Monitor().BOSJudge()
    htfadd692.Monitor().BOSJudge()
    htfadd693.Monitor().BOSJudge()
    htfadd694.Monitor().BOSJudge()
    htfadd695.Monitor().BOSJudge()
    htfadd696.Monitor().BOSJudge()
    htfadd697.Monitor().BOSJudge()
    htfadd698.Monitor().BOSJudge()
    htfadd699.Monitor().BOSJudge()
    htfadd700.Monitor().BOSJudge()
    htfadd701.Monitor().BOSJudge()
    htfadd702.Monitor().BOSJudge()
    htfadd703.Monitor().BOSJudge()
    htfadd704.Monitor().BOSJudge()
    htfadd705.Monitor().BOSJudge()
    htfadd706.Monitor().BOSJudge()
    htfadd707.Monitor().BOSJudge()
    htfadd708.Monitor().BOSJudge()
    htfadd709.Monitor().BOSJudge()
    htfadd710.Monitor().BOSJudge()
    htfadd711.Monitor().BOSJudge()
    htfadd712.Monitor().BOSJudge()
    htfadd713.Monitor().BOSJudge()
    htfadd714.Monitor().BOSJudge()
    htfadd715.Monitor().BOSJudge()
    htfadd716.Monitor().BOSJudge()
    htfadd717.Monitor().BOSJudge()
    htfadd718.Monitor().BOSJudge()
    htfadd719.Monitor().BOSJudge()
    htfadd720.Monitor().BOSJudge()
    htfadd721.Monitor().BOSJudge()
    htfadd722.Monitor().BOSJudge()
    htfadd723.Monitor().BOSJudge()
    htfadd724.Monitor().BOSJudge()
    htfadd725.Monitor().BOSJudge()
    htfadd726.Monitor().BOSJudge()
    htfadd727.Monitor().BOSJudge()
    htfadd728.Monitor().BOSJudge()
    htfadd729.Monitor().BOSJudge()
    htfadd730.Monitor().BOSJudge()
    htfadd731.Monitor().BOSJudge()
    htfadd732.Monitor().BOSJudge()
    htfadd733.Monitor().BOSJudge()
    htfadd734.Monitor().BOSJudge()
    htfadd735.Monitor().BOSJudge()
    htfadd736.Monitor().BOSJudge()
    htfadd737.Monitor().BOSJudge()
    htfadd738.Monitor().BOSJudge()
    htfadd739.Monitor().BOSJudge()
    htfadd740.Monitor().BOSJudge()
    htfadd741.Monitor().BOSJudge()
    htfadd742.Monitor().BOSJudge()
    htfadd743.Monitor().BOSJudge()
    htfadd744.Monitor().BOSJudge()
    htfadd745.Monitor().BOSJudge()
    htfadd746.Monitor().BOSJudge()
    htfadd747.Monitor().BOSJudge()
    htfadd748.Monitor().BOSJudge()
    htfadd749.Monitor().BOSJudge()
    htfadd750.Monitor().BOSJudge()
    htfadd751.Monitor().BOSJudge()
    htfadd752.Monitor().BOSJudge()
    htfadd753.Monitor().BOSJudge()
    htfadd754.Monitor().BOSJudge()
    htfadd755.Monitor().BOSJudge()
    htfadd756.Monitor().BOSJudge()
    htfadd757.Monitor().BOSJudge()
    htfadd758.Monitor().BOSJudge()
    htfadd759.Monitor().BOSJudge()
    htfadd760.Monitor().BOSJudge()
    htfadd761.Monitor().BOSJudge()
    htfadd762.Monitor().BOSJudge()
    htfadd763.Monitor().BOSJudge()
    htfadd764.Monitor().BOSJudge()
    htfadd765.Monitor().BOSJudge()
    htfadd766.Monitor().BOSJudge()
    htfadd767.Monitor().BOSJudge()
    htfadd768.Monitor().BOSJudge()
    htfadd769.Monitor().BOSJudge()
    htfadd770.Monitor().BOSJudge()
    htfadd771.Monitor().BOSJudge()
    htfadd772.Monitor().BOSJudge()
    htfadd773.Monitor().BOSJudge()
    htfadd774.Monitor().BOSJudge()
    htfadd775.Monitor().BOSJudge()
    htfadd776.Monitor().BOSJudge()
    htfadd777.Monitor().BOSJudge()
    htfadd778.Monitor().BOSJudge()
    htfadd779.Monitor().BOSJudge()
    htfadd780.Monitor().BOSJudge()
    htfadd781.Monitor().BOSJudge()
    htfadd782.Monitor().BOSJudge()
    htfadd783.Monitor().BOSJudge()
    htfadd784.Monitor().BOSJudge()
    htfadd785.Monitor().BOSJudge()
    htfadd786.Monitor().BOSJudge()
    htfadd787.Monitor().BOSJudge()
    htfadd788.Monitor().BOSJudge()
    htfadd789.Monitor().BOSJudge()
    htfadd790.Monitor().BOSJudge()
    htfadd791.Monitor().BOSJudge()
    htfadd792.Monitor().BOSJudge()
    htfadd793.Monitor().BOSJudge()
    htfadd794.Monitor().BOSJudge()
    htfadd795.Monitor().BOSJudge()
    htfadd796.Monitor().BOSJudge()
    htfadd797.Monitor().BOSJudge()
    htfadd798.Monitor().BOSJudge()
    htfadd799.Monitor().BOSJudge()
    htfadd800.Monitor().BOSJudge()
    htfadd801.Monitor().BOSJudge()
    htfadd802.Monitor().BOSJudge()
    htfadd803.Monitor().BOSJudge()
    htfadd804.Monitor().BOSJudge()
    htfadd805.Monitor().BOSJudge()
    htfadd806.Monitor().BOSJudge()
    htfadd807.Monitor().BOSJudge()
    htfadd808.Monitor().BOSJudge()
    htfadd809.Monitor().BOSJudge()
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
    htfadd901.Monitor().BOSJudge()
    htfadd902.Monitor().BOSJudge()
    htfadd903.Monitor().BOSJudge()
    htfadd904.Monitor().BOSJudge()
    htfadd905.Monitor().BOSJudge()
    htfadd906.Monitor().BOSJudge()
    htfadd907.Monitor().BOSJudge()
    htfadd908.Monitor().BOSJudge()
    htfadd909.Monitor().BOSJudge()
    htfadd910.Monitor().BOSJudge()
    htfadd911.Monitor().BOSJudge()
    htfadd912.Monitor().BOSJudge()
    htfadd913.Monitor().BOSJudge()
    htfadd914.Monitor().BOSJudge()
    htfadd915.Monitor().BOSJudge()
    htfadd916.Monitor().BOSJudge()
    htfadd917.Monitor().BOSJudge()
    htfadd918.Monitor().BOSJudge()
    htfadd919.Monitor().BOSJudge()
    htfadd920.Monitor().BOSJudge()
    htfadd921.Monitor().BOSJudge()
    htfadd922.Monitor().BOSJudge()
    htfadd923.Monitor().BOSJudge()
    htfadd924.Monitor().BOSJudge()
    htfadd925.Monitor().BOSJudge()
    htfadd926.Monitor().BOSJudge()
    htfadd927.Monitor().BOSJudge()
    htfadd928.Monitor().BOSJudge()
    htfadd929.Monitor().BOSJudge()
    htfadd930.Monitor().BOSJudge()
    htfadd931.Monitor().BOSJudge()
    htfadd932.Monitor().BOSJudge()
    htfadd933.Monitor().BOSJudge()
    htfadd934.Monitor().BOSJudge()
    htfadd935.Monitor().BOSJudge()
    htfadd936.Monitor().BOSJudge()
    htfadd937.Monitor().BOSJudge()
    htfadd938.Monitor().BOSJudge()
    htfadd939.Monitor().BOSJudge()
    htfadd940.Monitor().BOSJudge()
    htfadd941.Monitor().BOSJudge()
    htfadd942.Monitor().BOSJudge()
    htfadd943.Monitor().BOSJudge()
    htfadd944.Monitor().BOSJudge()
    htfadd945.Monitor().BOSJudge()
    htfadd946.Monitor().BOSJudge()
    htfadd947.Monitor().BOSJudge()
    htfadd948.Monitor().BOSJudge()
    htfadd949.Monitor().BOSJudge()
    htfadd950.Monitor().BOSJudge()
    htfadd951.Monitor().BOSJudge()
    htfadd952.Monitor().BOSJudge()
    htfadd953.Monitor().BOSJudge()
    htfadd954.Monitor().BOSJudge()
    htfadd955.Monitor().BOSJudge()
    htfadd956.Monitor().BOSJudge()
    htfadd957.Monitor().BOSJudge()
    htfadd958.Monitor().BOSJudge()
    htfadd959.Monitor().BOSJudge()
    htfadd960.Monitor().BOSJudge()
    htfadd961.Monitor().BOSJudge()
    htfadd962.Monitor().BOSJudge()
    htfadd963.Monitor().BOSJudge()
    htfadd964.Monitor().BOSJudge()
    htfadd965.Monitor().BOSJudge()
    htfadd966.Monitor().BOSJudge()
    htfadd967.Monitor().BOSJudge()
    htfadd968.Monitor().BOSJudge()
    htfadd969.Monitor().BOSJudge()
    htfadd970.Monitor().BOSJudge()
    htfadd971.Monitor().BOSJudge()
    htfadd972.Monitor().BOSJudge()
    htfadd973.Monitor().BOSJudge()
    htfadd974.Monitor().BOSJudge()
    htfadd975.Monitor().BOSJudge()
    htfadd976.Monitor().BOSJudge()
    htfadd977.Monitor().BOSJudge()
    htfadd978.Monitor().BOSJudge()
    htfadd979.Monitor().BOSJudge()
    htfadd980.Monitor().BOSJudge()
    htfadd981.Monitor().BOSJudge()
    htfadd982.Monitor().BOSJudge()
    htfadd983.Monitor().BOSJudge()
    htfadd984.Monitor().BOSJudge()
    htfadd985.Monitor().BOSJudge()
    htfadd986.Monitor().BOSJudge()
    htfadd987.Monitor().BOSJudge()
    htfadd988.Monitor().BOSJudge()
    htfadd989.Monitor().BOSJudge()
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
    htfadd1081.Monitor().BOSJudge()
    htfadd1082.Monitor().BOSJudge()
    htfadd1083.Monitor().BOSJudge()
    htfadd1084.Monitor().BOSJudge()
    htfadd1085.Monitor().BOSJudge()
    htfadd1086.Monitor().BOSJudge()
    htfadd1087.Monitor().BOSJudge()
    htfadd1088.Monitor().BOSJudge()
    htfadd1089.Monitor().BOSJudge()
    htfadd1090.Monitor().BOSJudge()
    htfadd1091.Monitor().BOSJudge()
    htfadd1092.Monitor().BOSJudge()
    htfadd1093.Monitor().BOSJudge()
    htfadd1094.Monitor().BOSJudge()
    htfadd1095.Monitor().BOSJudge()
    htfadd1096.Monitor().BOSJudge()
    htfadd1097.Monitor().BOSJudge()
    htfadd1098.Monitor().BOSJudge()
    htfadd1099.Monitor().BOSJudge()
    htfadd1100.Monitor().BOSJudge()
    htfadd1101.Monitor().BOSJudge()
    htfadd1102.Monitor().BOSJudge()
    htfadd1103.Monitor().BOSJudge()
    htfadd1104.Monitor().BOSJudge()
    htfadd1105.Monitor().BOSJudge()
    htfadd1106.Monitor().BOSJudge()
    htfadd1107.Monitor().BOSJudge()
    htfadd1108.Monitor().BOSJudge()
    htfadd1109.Monitor().BOSJudge()
    htfadd1110.Monitor().BOSJudge()
    htfadd1111.Monitor().BOSJudge()
    htfadd1112.Monitor().BOSJudge()
    htfadd1113.Monitor().BOSJudge()
    htfadd1114.Monitor().BOSJudge()
    htfadd1115.Monitor().BOSJudge()
    htfadd1116.Monitor().BOSJudge()
    htfadd1117.Monitor().BOSJudge()
    htfadd1118.Monitor().BOSJudge()
    htfadd1119.Monitor().BOSJudge()
    htfadd1120.Monitor().BOSJudge()
    htfadd1121.Monitor().BOSJudge()
    htfadd1122.Monitor().BOSJudge()
    htfadd1123.Monitor().BOSJudge()
    htfadd1124.Monitor().BOSJudge()
    htfadd1125.Monitor().BOSJudge()
    htfadd1126.Monitor().BOSJudge()
    htfadd1127.Monitor().BOSJudge()
    htfadd1128.Monitor().BOSJudge()
    htfadd1129.Monitor().BOSJudge()
    htfadd1130.Monitor().BOSJudge()
    htfadd1131.Monitor().BOSJudge()
    htfadd1132.Monitor().BOSJudge()
    htfadd1133.Monitor().BOSJudge()
    htfadd1134.Monitor().BOSJudge()
    htfadd1135.Monitor().BOSJudge()
    htfadd1136.Monitor().BOSJudge()
    htfadd1137.Monitor().BOSJudge()
    htfadd1138.Monitor().BOSJudge()
    htfadd1139.Monitor().BOSJudge()
    htfadd1140.Monitor().BOSJudge()
    htfadd1141.Monitor().BOSJudge()
    htfadd1142.Monitor().BOSJudge()
    htfadd1143.Monitor().BOSJudge()
    htfadd1144.Monitor().BOSJudge()
    htfadd1145.Monitor().BOSJudge()
    htfadd1146.Monitor().BOSJudge()
    htfadd1147.Monitor().BOSJudge()
    htfadd1148.Monitor().BOSJudge()
    htfadd1149.Monitor().BOSJudge()
    htfadd1150.Monitor().BOSJudge()
    htfadd1151.Monitor().BOSJudge()
    htfadd1152.Monitor().BOSJudge()
    htfadd1153.Monitor().BOSJudge()
    htfadd1154.Monitor().BOSJudge()
    htfadd1155.Monitor().BOSJudge()
    htfadd1156.Monitor().BOSJudge()
    htfadd1157.Monitor().BOSJudge()
    htfadd1158.Monitor().BOSJudge()
    htfadd1159.Monitor().BOSJudge()
    htfadd1160.Monitor().BOSJudge()
    htfadd1161.Monitor().BOSJudge()
    htfadd1162.Monitor().BOSJudge()
    htfadd1163.Monitor().BOSJudge()
    htfadd1164.Monitor().BOSJudge()
    htfadd1165.Monitor().BOSJudge()
    htfadd1166.Monitor().BOSJudge()
    htfadd1167.Monitor().BOSJudge()
    htfadd1168.Monitor().BOSJudge()
    htfadd1169.Monitor().BOSJudge()
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

if bar_index == last_bar_index - 1
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
    HighestsbdSet(highestsbd, htfadd91)
    LowestsbuSet(lowestsbu, htfadd91) 
    HighestsbdSet(highestsbd, htfadd92)
    LowestsbuSet(lowestsbu, htfadd92) 
    HighestsbdSet(highestsbd, htfadd93)
    LowestsbuSet(lowestsbu, htfadd93) 
    HighestsbdSet(highestsbd, htfadd94)
    LowestsbuSet(lowestsbu, htfadd94) 
    HighestsbdSet(highestsbd, htfadd95)
    LowestsbuSet(lowestsbu, htfadd95) 
    HighestsbdSet(highestsbd, htfadd96)
    LowestsbuSet(lowestsbu, htfadd96) 
    HighestsbdSet(highestsbd, htfadd97)
    LowestsbuSet(lowestsbu, htfadd97) 
    HighestsbdSet(highestsbd, htfadd98)
    LowestsbuSet(lowestsbu, htfadd98) 
    HighestsbdSet(highestsbd, htfadd99)
    LowestsbuSet(lowestsbu, htfadd99) 
    HighestsbdSet(highestsbd, htfadd100)
    LowestsbuSet(lowestsbu, htfadd100) 
    HighestsbdSet(highestsbd, htfadd101)
    LowestsbuSet(lowestsbu, htfadd101) 
    HighestsbdSet(highestsbd, htfadd102)
    LowestsbuSet(lowestsbu, htfadd102) 
    HighestsbdSet(highestsbd, htfadd103)
    LowestsbuSet(lowestsbu, htfadd103) 
    HighestsbdSet(highestsbd, htfadd104)
    LowestsbuSet(lowestsbu, htfadd104) 
    HighestsbdSet(highestsbd, htfadd105)
    LowestsbuSet(lowestsbu, htfadd105) 
    HighestsbdSet(highestsbd, htfadd106)
    LowestsbuSet(lowestsbu, htfadd106) 
    HighestsbdSet(highestsbd, htfadd107)
    LowestsbuSet(lowestsbu, htfadd107) 
    HighestsbdSet(highestsbd, htfadd108)
    LowestsbuSet(lowestsbu, htfadd108) 
    HighestsbdSet(highestsbd, htfadd109)
    LowestsbuSet(lowestsbu, htfadd109) 
    HighestsbdSet(highestsbd, htfadd110)
    LowestsbuSet(lowestsbu, htfadd110) 
    HighestsbdSet(highestsbd, htfadd111)
    LowestsbuSet(lowestsbu, htfadd111) 
    HighestsbdSet(highestsbd, htfadd112)
    LowestsbuSet(lowestsbu, htfadd112) 
    HighestsbdSet(highestsbd, htfadd113)
    LowestsbuSet(lowestsbu, htfadd113) 
    HighestsbdSet(highestsbd, htfadd114)
    LowestsbuSet(lowestsbu, htfadd114) 
    HighestsbdSet(highestsbd, htfadd115)
    LowestsbuSet(lowestsbu, htfadd115) 
    HighestsbdSet(highestsbd, htfadd116)
    LowestsbuSet(lowestsbu, htfadd116) 
    HighestsbdSet(highestsbd, htfadd117)
    LowestsbuSet(lowestsbu, htfadd117) 
    HighestsbdSet(highestsbd, htfadd118)
    LowestsbuSet(lowestsbu, htfadd118) 
    HighestsbdSet(highestsbd, htfadd119)
    LowestsbuSet(lowestsbu, htfadd119) 
    HighestsbdSet(highestsbd, htfadd120)
    LowestsbuSet(lowestsbu, htfadd120) 
    HighestsbdSet(highestsbd, htfadd121)
    LowestsbuSet(lowestsbu, htfadd121) 
    HighestsbdSet(highestsbd, htfadd122)
    LowestsbuSet(lowestsbu, htfadd122) 
    HighestsbdSet(highestsbd, htfadd123)
    LowestsbuSet(lowestsbu, htfadd123) 
    HighestsbdSet(highestsbd, htfadd124)
    LowestsbuSet(lowestsbu, htfadd124) 
    HighestsbdSet(highestsbd, htfadd125)
    LowestsbuSet(lowestsbu, htfadd125) 
    HighestsbdSet(highestsbd, htfadd126)
    LowestsbuSet(lowestsbu, htfadd126) 
    HighestsbdSet(highestsbd, htfadd127)
    LowestsbuSet(lowestsbu, htfadd127) 
    HighestsbdSet(highestsbd, htfadd128)
    LowestsbuSet(lowestsbu, htfadd128) 
    HighestsbdSet(highestsbd, htfadd129)
    LowestsbuSet(lowestsbu, htfadd129) 
    HighestsbdSet(highestsbd, htfadd130)
    LowestsbuSet(lowestsbu, htfadd130) 
    HighestsbdSet(highestsbd, htfadd131)
    LowestsbuSet(lowestsbu, htfadd131) 
    HighestsbdSet(highestsbd, htfadd132)
    LowestsbuSet(lowestsbu, htfadd132) 
    HighestsbdSet(highestsbd, htfadd133)
    LowestsbuSet(lowestsbu, htfadd133) 
    HighestsbdSet(highestsbd, htfadd134)
    LowestsbuSet(lowestsbu, htfadd134) 
    HighestsbdSet(highestsbd, htfadd135)
    LowestsbuSet(lowestsbu, htfadd135) 
    HighestsbdSet(highestsbd, htfadd136)
    LowestsbuSet(lowestsbu, htfadd136) 
    HighestsbdSet(highestsbd, htfadd137)
    LowestsbuSet(lowestsbu, htfadd137) 
    HighestsbdSet(highestsbd, htfadd138)
    LowestsbuSet(lowestsbu, htfadd138) 
    HighestsbdSet(highestsbd, htfadd139)
    LowestsbuSet(lowestsbu, htfadd139) 
    HighestsbdSet(highestsbd, htfadd140)
    LowestsbuSet(lowestsbu, htfadd140) 
    HighestsbdSet(highestsbd, htfadd141)
    LowestsbuSet(lowestsbu, htfadd141) 
    HighestsbdSet(highestsbd, htfadd142)
    LowestsbuSet(lowestsbu, htfadd142) 
    HighestsbdSet(highestsbd, htfadd143)
    LowestsbuSet(lowestsbu, htfadd143) 
    HighestsbdSet(highestsbd, htfadd144)
    LowestsbuSet(lowestsbu, htfadd144) 
    HighestsbdSet(highestsbd, htfadd145)
    LowestsbuSet(lowestsbu, htfadd145) 
    HighestsbdSet(highestsbd, htfadd146)
    LowestsbuSet(lowestsbu, htfadd146) 
    HighestsbdSet(highestsbd, htfadd147)
    LowestsbuSet(lowestsbu, htfadd147) 
    HighestsbdSet(highestsbd, htfadd148)
    LowestsbuSet(lowestsbu, htfadd148) 
    HighestsbdSet(highestsbd, htfadd149)
    LowestsbuSet(lowestsbu, htfadd149) 
    HighestsbdSet(highestsbd, htfadd150)
    LowestsbuSet(lowestsbu, htfadd150) 
    HighestsbdSet(highestsbd, htfadd151)
    LowestsbuSet(lowestsbu, htfadd151) 
    HighestsbdSet(highestsbd, htfadd152)
    LowestsbuSet(lowestsbu, htfadd152) 
    HighestsbdSet(highestsbd, htfadd153)
    LowestsbuSet(lowestsbu, htfadd153) 
    HighestsbdSet(highestsbd, htfadd154)
    LowestsbuSet(lowestsbu, htfadd154) 
    HighestsbdSet(highestsbd, htfadd155)
    LowestsbuSet(lowestsbu, htfadd155) 
    HighestsbdSet(highestsbd, htfadd156)
    LowestsbuSet(lowestsbu, htfadd156) 
    HighestsbdSet(highestsbd, htfadd157)
    LowestsbuSet(lowestsbu, htfadd157) 
    HighestsbdSet(highestsbd, htfadd158)
    LowestsbuSet(lowestsbu, htfadd158) 
    HighestsbdSet(highestsbd, htfadd159)
    LowestsbuSet(lowestsbu, htfadd159) 
    HighestsbdSet(highestsbd, htfadd160)
    LowestsbuSet(lowestsbu, htfadd160) 
    HighestsbdSet(highestsbd, htfadd161)
    LowestsbuSet(lowestsbu, htfadd161) 
    HighestsbdSet(highestsbd, htfadd162)
    LowestsbuSet(lowestsbu, htfadd162) 
    HighestsbdSet(highestsbd, htfadd163)
    LowestsbuSet(lowestsbu, htfadd163) 
    HighestsbdSet(highestsbd, htfadd164)
    LowestsbuSet(lowestsbu, htfadd164) 
    HighestsbdSet(highestsbd, htfadd165)
    LowestsbuSet(lowestsbu, htfadd165) 
    HighestsbdSet(highestsbd, htfadd166)
    LowestsbuSet(lowestsbu, htfadd166) 
    HighestsbdSet(highestsbd, htfadd167)
    LowestsbuSet(lowestsbu, htfadd167) 
    HighestsbdSet(highestsbd, htfadd168)
    LowestsbuSet(lowestsbu, htfadd168) 
    HighestsbdSet(highestsbd, htfadd169)
    LowestsbuSet(lowestsbu, htfadd169) 
    HighestsbdSet(highestsbd, htfadd170)
    LowestsbuSet(lowestsbu, htfadd170) 
    HighestsbdSet(highestsbd, htfadd171)
    LowestsbuSet(lowestsbu, htfadd171) 
    HighestsbdSet(highestsbd, htfadd172)
    LowestsbuSet(lowestsbu, htfadd172) 
    HighestsbdSet(highestsbd, htfadd173)
    LowestsbuSet(lowestsbu, htfadd173) 
    HighestsbdSet(highestsbd, htfadd174)
    LowestsbuSet(lowestsbu, htfadd174) 
    HighestsbdSet(highestsbd, htfadd175)
    LowestsbuSet(lowestsbu, htfadd175) 
    HighestsbdSet(highestsbd, htfadd176)
    LowestsbuSet(lowestsbu, htfadd176) 
    HighestsbdSet(highestsbd, htfadd177)
    LowestsbuSet(lowestsbu, htfadd177) 
    HighestsbdSet(highestsbd, htfadd178)
    LowestsbuSet(lowestsbu, htfadd178) 
    HighestsbdSet(highestsbd, htfadd179)
    LowestsbuSet(lowestsbu, htfadd179) 
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
    HighestsbdSet(highestsbd, htfadd541)
    LowestsbuSet(lowestsbu, htfadd541) 
    HighestsbdSet(highestsbd, htfadd542)
    LowestsbuSet(lowestsbu, htfadd542) 
    HighestsbdSet(highestsbd, htfadd543)
    LowestsbuSet(lowestsbu, htfadd543) 
    HighestsbdSet(highestsbd, htfadd544)
    LowestsbuSet(lowestsbu, htfadd544) 
    HighestsbdSet(highestsbd, htfadd545)
    LowestsbuSet(lowestsbu, htfadd545) 
    HighestsbdSet(highestsbd, htfadd546)
    LowestsbuSet(lowestsbu, htfadd546) 
    HighestsbdSet(highestsbd, htfadd547)
    LowestsbuSet(lowestsbu, htfadd547) 
    HighestsbdSet(highestsbd, htfadd548)
    LowestsbuSet(lowestsbu, htfadd548) 
    HighestsbdSet(highestsbd, htfadd549)
    LowestsbuSet(lowestsbu, htfadd549) 
    HighestsbdSet(highestsbd, htfadd550)
    LowestsbuSet(lowestsbu, htfadd550) 
    HighestsbdSet(highestsbd, htfadd551)
    LowestsbuSet(lowestsbu, htfadd551) 
    HighestsbdSet(highestsbd, htfadd552)
    LowestsbuSet(lowestsbu, htfadd552) 
    HighestsbdSet(highestsbd, htfadd553)
    LowestsbuSet(lowestsbu, htfadd553) 
    HighestsbdSet(highestsbd, htfadd554)
    LowestsbuSet(lowestsbu, htfadd554) 
    HighestsbdSet(highestsbd, htfadd555)
    LowestsbuSet(lowestsbu, htfadd555) 
    HighestsbdSet(highestsbd, htfadd556)
    LowestsbuSet(lowestsbu, htfadd556) 
    HighestsbdSet(highestsbd, htfadd557)
    LowestsbuSet(lowestsbu, htfadd557) 
    HighestsbdSet(highestsbd, htfadd558)
    LowestsbuSet(lowestsbu, htfadd558) 
    HighestsbdSet(highestsbd, htfadd559)
    LowestsbuSet(lowestsbu, htfadd559) 
    HighestsbdSet(highestsbd, htfadd560)
    LowestsbuSet(lowestsbu, htfadd560) 
    HighestsbdSet(highestsbd, htfadd561)
    LowestsbuSet(lowestsbu, htfadd561) 
    HighestsbdSet(highestsbd, htfadd562)
    LowestsbuSet(lowestsbu, htfadd562) 
    HighestsbdSet(highestsbd, htfadd563)
    LowestsbuSet(lowestsbu, htfadd563) 
    HighestsbdSet(highestsbd, htfadd564)
    LowestsbuSet(lowestsbu, htfadd564) 
    HighestsbdSet(highestsbd, htfadd565)
    LowestsbuSet(lowestsbu, htfadd565) 
    HighestsbdSet(highestsbd, htfadd566)
    LowestsbuSet(lowestsbu, htfadd566) 
    HighestsbdSet(highestsbd, htfadd567)
    LowestsbuSet(lowestsbu, htfadd567) 
    HighestsbdSet(highestsbd, htfadd568)
    LowestsbuSet(lowestsbu, htfadd568) 
    HighestsbdSet(highestsbd, htfadd569)
    LowestsbuSet(lowestsbu, htfadd569) 
    HighestsbdSet(highestsbd, htfadd570)
    LowestsbuSet(lowestsbu, htfadd570) 
    HighestsbdSet(highestsbd, htfadd571)
    LowestsbuSet(lowestsbu, htfadd571) 
    HighestsbdSet(highestsbd, htfadd572)
    LowestsbuSet(lowestsbu, htfadd572) 
    HighestsbdSet(highestsbd, htfadd573)
    LowestsbuSet(lowestsbu, htfadd573) 
    HighestsbdSet(highestsbd, htfadd574)
    LowestsbuSet(lowestsbu, htfadd574) 
    HighestsbdSet(highestsbd, htfadd575)
    LowestsbuSet(lowestsbu, htfadd575) 
    HighestsbdSet(highestsbd, htfadd576)
    LowestsbuSet(lowestsbu, htfadd576) 
    HighestsbdSet(highestsbd, htfadd577)
    LowestsbuSet(lowestsbu, htfadd577) 
    HighestsbdSet(highestsbd, htfadd578)
    LowestsbuSet(lowestsbu, htfadd578) 
    HighestsbdSet(highestsbd, htfadd579)
    LowestsbuSet(lowestsbu, htfadd579) 
    HighestsbdSet(highestsbd, htfadd580)
    LowestsbuSet(lowestsbu, htfadd580) 
    HighestsbdSet(highestsbd, htfadd581)
    LowestsbuSet(lowestsbu, htfadd581) 
    HighestsbdSet(highestsbd, htfadd582)
    LowestsbuSet(lowestsbu, htfadd582) 
    HighestsbdSet(highestsbd, htfadd583)
    LowestsbuSet(lowestsbu, htfadd583) 
    HighestsbdSet(highestsbd, htfadd584)
    LowestsbuSet(lowestsbu, htfadd584) 
    HighestsbdSet(highestsbd, htfadd585)
    LowestsbuSet(lowestsbu, htfadd585) 
    HighestsbdSet(highestsbd, htfadd586)
    LowestsbuSet(lowestsbu, htfadd586) 
    HighestsbdSet(highestsbd, htfadd587)
    LowestsbuSet(lowestsbu, htfadd587) 
    HighestsbdSet(highestsbd, htfadd588)
    LowestsbuSet(lowestsbu, htfadd588) 
    HighestsbdSet(highestsbd, htfadd589)
    LowestsbuSet(lowestsbu, htfadd589) 
    HighestsbdSet(highestsbd, htfadd590)
    LowestsbuSet(lowestsbu, htfadd590) 
    HighestsbdSet(highestsbd, htfadd591)
    LowestsbuSet(lowestsbu, htfadd591) 
    HighestsbdSet(highestsbd, htfadd592)
    LowestsbuSet(lowestsbu, htfadd592) 
    HighestsbdSet(highestsbd, htfadd593)
    LowestsbuSet(lowestsbu, htfadd593) 
    HighestsbdSet(highestsbd, htfadd594)
    LowestsbuSet(lowestsbu, htfadd594) 
    HighestsbdSet(highestsbd, htfadd595)
    LowestsbuSet(lowestsbu, htfadd595) 
    HighestsbdSet(highestsbd, htfadd596)
    LowestsbuSet(lowestsbu, htfadd596) 
    HighestsbdSet(highestsbd, htfadd597)
    LowestsbuSet(lowestsbu, htfadd597) 
    HighestsbdSet(highestsbd, htfadd598)
    LowestsbuSet(lowestsbu, htfadd598) 
    HighestsbdSet(highestsbd, htfadd599)
    LowestsbuSet(lowestsbu, htfadd599) 
    HighestsbdSet(highestsbd, htfadd600)
    LowestsbuSet(lowestsbu, htfadd600) 
    HighestsbdSet(highestsbd, htfadd601)
    LowestsbuSet(lowestsbu, htfadd601) 
    HighestsbdSet(highestsbd, htfadd602)
    LowestsbuSet(lowestsbu, htfadd602) 
    HighestsbdSet(highestsbd, htfadd603)
    LowestsbuSet(lowestsbu, htfadd603) 
    HighestsbdSet(highestsbd, htfadd604)
    LowestsbuSet(lowestsbu, htfadd604) 
    HighestsbdSet(highestsbd, htfadd605)
    LowestsbuSet(lowestsbu, htfadd605) 
    HighestsbdSet(highestsbd, htfadd606)
    LowestsbuSet(lowestsbu, htfadd606) 
    HighestsbdSet(highestsbd, htfadd607)
    LowestsbuSet(lowestsbu, htfadd607) 
    HighestsbdSet(highestsbd, htfadd608)
    LowestsbuSet(lowestsbu, htfadd608) 
    HighestsbdSet(highestsbd, htfadd609)
    LowestsbuSet(lowestsbu, htfadd609) 
    HighestsbdSet(highestsbd, htfadd610)
    LowestsbuSet(lowestsbu, htfadd610) 
    HighestsbdSet(highestsbd, htfadd611)
    LowestsbuSet(lowestsbu, htfadd611) 
    HighestsbdSet(highestsbd, htfadd612)
    LowestsbuSet(lowestsbu, htfadd612) 
    HighestsbdSet(highestsbd, htfadd613)
    LowestsbuSet(lowestsbu, htfadd613) 
    HighestsbdSet(highestsbd, htfadd614)
    LowestsbuSet(lowestsbu, htfadd614) 
    HighestsbdSet(highestsbd, htfadd615)
    LowestsbuSet(lowestsbu, htfadd615) 
    HighestsbdSet(highestsbd, htfadd616)
    LowestsbuSet(lowestsbu, htfadd616) 
    HighestsbdSet(highestsbd, htfadd617)
    LowestsbuSet(lowestsbu, htfadd617) 
    HighestsbdSet(highestsbd, htfadd618)
    LowestsbuSet(lowestsbu, htfadd618) 
    HighestsbdSet(highestsbd, htfadd619)
    LowestsbuSet(lowestsbu, htfadd619) 
    HighestsbdSet(highestsbd, htfadd620)
    LowestsbuSet(lowestsbu, htfadd620) 
    HighestsbdSet(highestsbd, htfadd621)
    LowestsbuSet(lowestsbu, htfadd621) 
    HighestsbdSet(highestsbd, htfadd622)
    LowestsbuSet(lowestsbu, htfadd622) 
    HighestsbdSet(highestsbd, htfadd623)
    LowestsbuSet(lowestsbu, htfadd623) 
    HighestsbdSet(highestsbd, htfadd624)
    LowestsbuSet(lowestsbu, htfadd624) 
    HighestsbdSet(highestsbd, htfadd625)
    LowestsbuSet(lowestsbu, htfadd625) 
    HighestsbdSet(highestsbd, htfadd626)
    LowestsbuSet(lowestsbu, htfadd626) 
    HighestsbdSet(highestsbd, htfadd627)
    LowestsbuSet(lowestsbu, htfadd627) 
    HighestsbdSet(highestsbd, htfadd628)
    LowestsbuSet(lowestsbu, htfadd628) 
    HighestsbdSet(highestsbd, htfadd629)
    LowestsbuSet(lowestsbu, htfadd629) 
    HighestsbdSet(highestsbd, htfadd630)
    LowestsbuSet(lowestsbu, htfadd630) 
    HighestsbdSet(highestsbd, htfadd631)
    LowestsbuSet(lowestsbu, htfadd631) 
    HighestsbdSet(highestsbd, htfadd632)
    LowestsbuSet(lowestsbu, htfadd632) 
    HighestsbdSet(highestsbd, htfadd633)
    LowestsbuSet(lowestsbu, htfadd633) 
    HighestsbdSet(highestsbd, htfadd634)
    LowestsbuSet(lowestsbu, htfadd634) 
    HighestsbdSet(highestsbd, htfadd635)
    LowestsbuSet(lowestsbu, htfadd635) 
    HighestsbdSet(highestsbd, htfadd636)
    LowestsbuSet(lowestsbu, htfadd636) 
    HighestsbdSet(highestsbd, htfadd637)
    LowestsbuSet(lowestsbu, htfadd637) 
    HighestsbdSet(highestsbd, htfadd638)
    LowestsbuSet(lowestsbu, htfadd638) 
    HighestsbdSet(highestsbd, htfadd639)
    LowestsbuSet(lowestsbu, htfadd639) 
    HighestsbdSet(highestsbd, htfadd640)
    LowestsbuSet(lowestsbu, htfadd640) 
    HighestsbdSet(highestsbd, htfadd641)
    LowestsbuSet(lowestsbu, htfadd641) 
    HighestsbdSet(highestsbd, htfadd642)
    LowestsbuSet(lowestsbu, htfadd642) 
    HighestsbdSet(highestsbd, htfadd643)
    LowestsbuSet(lowestsbu, htfadd643) 
    HighestsbdSet(highestsbd, htfadd644)
    LowestsbuSet(lowestsbu, htfadd644) 
    HighestsbdSet(highestsbd, htfadd645)
    LowestsbuSet(lowestsbu, htfadd645) 
    HighestsbdSet(highestsbd, htfadd646)
    LowestsbuSet(lowestsbu, htfadd646) 
    HighestsbdSet(highestsbd, htfadd647)
    LowestsbuSet(lowestsbu, htfadd647) 
    HighestsbdSet(highestsbd, htfadd648)
    LowestsbuSet(lowestsbu, htfadd648) 
    HighestsbdSet(highestsbd, htfadd649)
    LowestsbuSet(lowestsbu, htfadd649) 
    HighestsbdSet(highestsbd, htfadd650)
    LowestsbuSet(lowestsbu, htfadd650) 
    HighestsbdSet(highestsbd, htfadd651)
    LowestsbuSet(lowestsbu, htfadd651) 
    HighestsbdSet(highestsbd, htfadd652)
    LowestsbuSet(lowestsbu, htfadd652) 
    HighestsbdSet(highestsbd, htfadd653)
    LowestsbuSet(lowestsbu, htfadd653) 
    HighestsbdSet(highestsbd, htfadd654)
    LowestsbuSet(lowestsbu, htfadd654) 
    HighestsbdSet(highestsbd, htfadd655)
    LowestsbuSet(lowestsbu, htfadd655) 
    HighestsbdSet(highestsbd, htfadd656)
    LowestsbuSet(lowestsbu, htfadd656) 
    HighestsbdSet(highestsbd, htfadd657)
    LowestsbuSet(lowestsbu, htfadd657) 
    HighestsbdSet(highestsbd, htfadd658)
    LowestsbuSet(lowestsbu, htfadd658) 
    HighestsbdSet(highestsbd, htfadd659)
    LowestsbuSet(lowestsbu, htfadd659) 
    HighestsbdSet(highestsbd, htfadd660)
    LowestsbuSet(lowestsbu, htfadd660) 
    HighestsbdSet(highestsbd, htfadd661)
    LowestsbuSet(lowestsbu, htfadd661) 
    HighestsbdSet(highestsbd, htfadd662)
    LowestsbuSet(lowestsbu, htfadd662) 
    HighestsbdSet(highestsbd, htfadd663)
    LowestsbuSet(lowestsbu, htfadd663) 
    HighestsbdSet(highestsbd, htfadd664)
    LowestsbuSet(lowestsbu, htfadd664) 
    HighestsbdSet(highestsbd, htfadd665)
    LowestsbuSet(lowestsbu, htfadd665) 
    HighestsbdSet(highestsbd, htfadd666)
    LowestsbuSet(lowestsbu, htfadd666) 
    HighestsbdSet(highestsbd, htfadd667)
    LowestsbuSet(lowestsbu, htfadd667) 
    HighestsbdSet(highestsbd, htfadd668)
    LowestsbuSet(lowestsbu, htfadd668) 
    HighestsbdSet(highestsbd, htfadd669)
    LowestsbuSet(lowestsbu, htfadd669) 
    HighestsbdSet(highestsbd, htfadd670)
    LowestsbuSet(lowestsbu, htfadd670) 
    HighestsbdSet(highestsbd, htfadd671)
    LowestsbuSet(lowestsbu, htfadd671) 
    HighestsbdSet(highestsbd, htfadd672)
    LowestsbuSet(lowestsbu, htfadd672) 
    HighestsbdSet(highestsbd, htfadd673)
    LowestsbuSet(lowestsbu, htfadd673) 
    HighestsbdSet(highestsbd, htfadd674)
    LowestsbuSet(lowestsbu, htfadd674) 
    HighestsbdSet(highestsbd, htfadd675)
    LowestsbuSet(lowestsbu, htfadd675) 
    HighestsbdSet(highestsbd, htfadd676)
    LowestsbuSet(lowestsbu, htfadd676) 
    HighestsbdSet(highestsbd, htfadd677)
    LowestsbuSet(lowestsbu, htfadd677) 
    HighestsbdSet(highestsbd, htfadd678)
    LowestsbuSet(lowestsbu, htfadd678) 
    HighestsbdSet(highestsbd, htfadd679)
    LowestsbuSet(lowestsbu, htfadd679) 
    HighestsbdSet(highestsbd, htfadd680)
    LowestsbuSet(lowestsbu, htfadd680) 
    HighestsbdSet(highestsbd, htfadd681)
    LowestsbuSet(lowestsbu, htfadd681) 
    HighestsbdSet(highestsbd, htfadd682)
    LowestsbuSet(lowestsbu, htfadd682) 
    HighestsbdSet(highestsbd, htfadd683)
    LowestsbuSet(lowestsbu, htfadd683) 
    HighestsbdSet(highestsbd, htfadd684)
    LowestsbuSet(lowestsbu, htfadd684) 
    HighestsbdSet(highestsbd, htfadd685)
    LowestsbuSet(lowestsbu, htfadd685) 
    HighestsbdSet(highestsbd, htfadd686)
    LowestsbuSet(lowestsbu, htfadd686) 
    HighestsbdSet(highestsbd, htfadd687)
    LowestsbuSet(lowestsbu, htfadd687) 
    HighestsbdSet(highestsbd, htfadd688)
    LowestsbuSet(lowestsbu, htfadd688) 
    HighestsbdSet(highestsbd, htfadd689)
    LowestsbuSet(lowestsbu, htfadd689) 
    HighestsbdSet(highestsbd, htfadd690)
    LowestsbuSet(lowestsbu, htfadd690) 
    HighestsbdSet(highestsbd, htfadd691)
    LowestsbuSet(lowestsbu, htfadd691) 
    HighestsbdSet(highestsbd, htfadd692)
    LowestsbuSet(lowestsbu, htfadd692) 
    HighestsbdSet(highestsbd, htfadd693)
    LowestsbuSet(lowestsbu, htfadd693) 
    HighestsbdSet(highestsbd, htfadd694)
    LowestsbuSet(lowestsbu, htfadd694) 
    HighestsbdSet(highestsbd, htfadd695)
    LowestsbuSet(lowestsbu, htfadd695) 
    HighestsbdSet(highestsbd, htfadd696)
    LowestsbuSet(lowestsbu, htfadd696) 
    HighestsbdSet(highestsbd, htfadd697)
    LowestsbuSet(lowestsbu, htfadd697) 
    HighestsbdSet(highestsbd, htfadd698)
    LowestsbuSet(lowestsbu, htfadd698) 
    HighestsbdSet(highestsbd, htfadd699)
    LowestsbuSet(lowestsbu, htfadd699) 
    HighestsbdSet(highestsbd, htfadd700)
    LowestsbuSet(lowestsbu, htfadd700) 
    HighestsbdSet(highestsbd, htfadd701)
    LowestsbuSet(lowestsbu, htfadd701) 
    HighestsbdSet(highestsbd, htfadd702)
    LowestsbuSet(lowestsbu, htfadd702) 
    HighestsbdSet(highestsbd, htfadd703)
    LowestsbuSet(lowestsbu, htfadd703) 
    HighestsbdSet(highestsbd, htfadd704)
    LowestsbuSet(lowestsbu, htfadd704) 
    HighestsbdSet(highestsbd, htfadd705)
    LowestsbuSet(lowestsbu, htfadd705) 
    HighestsbdSet(highestsbd, htfadd706)
    LowestsbuSet(lowestsbu, htfadd706) 
    HighestsbdSet(highestsbd, htfadd707)
    LowestsbuSet(lowestsbu, htfadd707) 
    HighestsbdSet(highestsbd, htfadd708)
    LowestsbuSet(lowestsbu, htfadd708) 
    HighestsbdSet(highestsbd, htfadd709)
    LowestsbuSet(lowestsbu, htfadd709) 
    HighestsbdSet(highestsbd, htfadd710)
    LowestsbuSet(lowestsbu, htfadd710) 
    HighestsbdSet(highestsbd, htfadd711)
    LowestsbuSet(lowestsbu, htfadd711) 
    HighestsbdSet(highestsbd, htfadd712)
    LowestsbuSet(lowestsbu, htfadd712) 
    HighestsbdSet(highestsbd, htfadd713)
    LowestsbuSet(lowestsbu, htfadd713) 
    HighestsbdSet(highestsbd, htfadd714)
    LowestsbuSet(lowestsbu, htfadd714) 
    HighestsbdSet(highestsbd, htfadd715)
    LowestsbuSet(lowestsbu, htfadd715) 
    HighestsbdSet(highestsbd, htfadd716)
    LowestsbuSet(lowestsbu, htfadd716) 
    HighestsbdSet(highestsbd, htfadd717)
    LowestsbuSet(lowestsbu, htfadd717) 
    HighestsbdSet(highestsbd, htfadd718)
    LowestsbuSet(lowestsbu, htfadd718) 
    HighestsbdSet(highestsbd, htfadd719)
    LowestsbuSet(lowestsbu, htfadd719) 
    HighestsbdSet(highestsbd, htfadd720)
    LowestsbuSet(lowestsbu, htfadd720) 
    HighestsbdSet(highestsbd, htfadd721)
    LowestsbuSet(lowestsbu, htfadd721) 
    HighestsbdSet(highestsbd, htfadd722)
    LowestsbuSet(lowestsbu, htfadd722) 
    HighestsbdSet(highestsbd, htfadd723)
    LowestsbuSet(lowestsbu, htfadd723) 
    HighestsbdSet(highestsbd, htfadd724)
    LowestsbuSet(lowestsbu, htfadd724) 
    HighestsbdSet(highestsbd, htfadd725)
    LowestsbuSet(lowestsbu, htfadd725) 
    HighestsbdSet(highestsbd, htfadd726)
    LowestsbuSet(lowestsbu, htfadd726) 
    HighestsbdSet(highestsbd, htfadd727)
    LowestsbuSet(lowestsbu, htfadd727) 
    HighestsbdSet(highestsbd, htfadd728)
    LowestsbuSet(lowestsbu, htfadd728) 
    HighestsbdSet(highestsbd, htfadd729)
    LowestsbuSet(lowestsbu, htfadd729) 
    HighestsbdSet(highestsbd, htfadd730)
    LowestsbuSet(lowestsbu, htfadd730) 
    HighestsbdSet(highestsbd, htfadd731)
    LowestsbuSet(lowestsbu, htfadd731) 
    HighestsbdSet(highestsbd, htfadd732)
    LowestsbuSet(lowestsbu, htfadd732) 
    HighestsbdSet(highestsbd, htfadd733)
    LowestsbuSet(lowestsbu, htfadd733) 
    HighestsbdSet(highestsbd, htfadd734)
    LowestsbuSet(lowestsbu, htfadd734) 
    HighestsbdSet(highestsbd, htfadd735)
    LowestsbuSet(lowestsbu, htfadd735) 
    HighestsbdSet(highestsbd, htfadd736)
    LowestsbuSet(lowestsbu, htfadd736) 
    HighestsbdSet(highestsbd, htfadd737)
    LowestsbuSet(lowestsbu, htfadd737) 
    HighestsbdSet(highestsbd, htfadd738)
    LowestsbuSet(lowestsbu, htfadd738) 
    HighestsbdSet(highestsbd, htfadd739)
    LowestsbuSet(lowestsbu, htfadd739) 
    HighestsbdSet(highestsbd, htfadd740)
    LowestsbuSet(lowestsbu, htfadd740) 
    HighestsbdSet(highestsbd, htfadd741)
    LowestsbuSet(lowestsbu, htfadd741) 
    HighestsbdSet(highestsbd, htfadd742)
    LowestsbuSet(lowestsbu, htfadd742) 
    HighestsbdSet(highestsbd, htfadd743)
    LowestsbuSet(lowestsbu, htfadd743) 
    HighestsbdSet(highestsbd, htfadd744)
    LowestsbuSet(lowestsbu, htfadd744) 
    HighestsbdSet(highestsbd, htfadd745)
    LowestsbuSet(lowestsbu, htfadd745) 
    HighestsbdSet(highestsbd, htfadd746)
    LowestsbuSet(lowestsbu, htfadd746) 
    HighestsbdSet(highestsbd, htfadd747)
    LowestsbuSet(lowestsbu, htfadd747) 
    HighestsbdSet(highestsbd, htfadd748)
    LowestsbuSet(lowestsbu, htfadd748) 
    HighestsbdSet(highestsbd, htfadd749)
    LowestsbuSet(lowestsbu, htfadd749) 
    HighestsbdSet(highestsbd, htfadd750)
    LowestsbuSet(lowestsbu, htfadd750) 
    HighestsbdSet(highestsbd, htfadd751)
    LowestsbuSet(lowestsbu, htfadd751) 
    HighestsbdSet(highestsbd, htfadd752)
    LowestsbuSet(lowestsbu, htfadd752) 
    HighestsbdSet(highestsbd, htfadd753)
    LowestsbuSet(lowestsbu, htfadd753) 
    HighestsbdSet(highestsbd, htfadd754)
    LowestsbuSet(lowestsbu, htfadd754) 
    HighestsbdSet(highestsbd, htfadd755)
    LowestsbuSet(lowestsbu, htfadd755) 
    HighestsbdSet(highestsbd, htfadd756)
    LowestsbuSet(lowestsbu, htfadd756) 
    HighestsbdSet(highestsbd, htfadd757)
    LowestsbuSet(lowestsbu, htfadd757) 
    HighestsbdSet(highestsbd, htfadd758)
    LowestsbuSet(lowestsbu, htfadd758) 
    HighestsbdSet(highestsbd, htfadd759)
    LowestsbuSet(lowestsbu, htfadd759) 
    HighestsbdSet(highestsbd, htfadd760)
    LowestsbuSet(lowestsbu, htfadd760) 
    HighestsbdSet(highestsbd, htfadd761)
    LowestsbuSet(lowestsbu, htfadd761) 
    HighestsbdSet(highestsbd, htfadd762)
    LowestsbuSet(lowestsbu, htfadd762) 
    HighestsbdSet(highestsbd, htfadd763)
    LowestsbuSet(lowestsbu, htfadd763) 
    HighestsbdSet(highestsbd, htfadd764)
    LowestsbuSet(lowestsbu, htfadd764) 
    HighestsbdSet(highestsbd, htfadd765)
    LowestsbuSet(lowestsbu, htfadd765) 
    HighestsbdSet(highestsbd, htfadd766)
    LowestsbuSet(lowestsbu, htfadd766) 
    HighestsbdSet(highestsbd, htfadd767)
    LowestsbuSet(lowestsbu, htfadd767) 
    HighestsbdSet(highestsbd, htfadd768)
    LowestsbuSet(lowestsbu, htfadd768) 
    HighestsbdSet(highestsbd, htfadd769)
    LowestsbuSet(lowestsbu, htfadd769) 
    HighestsbdSet(highestsbd, htfadd770)
    LowestsbuSet(lowestsbu, htfadd770) 
    HighestsbdSet(highestsbd, htfadd771)
    LowestsbuSet(lowestsbu, htfadd771) 
    HighestsbdSet(highestsbd, htfadd772)
    LowestsbuSet(lowestsbu, htfadd772) 
    HighestsbdSet(highestsbd, htfadd773)
    LowestsbuSet(lowestsbu, htfadd773) 
    HighestsbdSet(highestsbd, htfadd774)
    LowestsbuSet(lowestsbu, htfadd774) 
    HighestsbdSet(highestsbd, htfadd775)
    LowestsbuSet(lowestsbu, htfadd775) 
    HighestsbdSet(highestsbd, htfadd776)
    LowestsbuSet(lowestsbu, htfadd776) 
    HighestsbdSet(highestsbd, htfadd777)
    LowestsbuSet(lowestsbu, htfadd777) 
    HighestsbdSet(highestsbd, htfadd778)
    LowestsbuSet(lowestsbu, htfadd778) 
    HighestsbdSet(highestsbd, htfadd779)
    LowestsbuSet(lowestsbu, htfadd779) 
    HighestsbdSet(highestsbd, htfadd780)
    LowestsbuSet(lowestsbu, htfadd780) 
    HighestsbdSet(highestsbd, htfadd781)
    LowestsbuSet(lowestsbu, htfadd781) 
    HighestsbdSet(highestsbd, htfadd782)
    LowestsbuSet(lowestsbu, htfadd782) 
    HighestsbdSet(highestsbd, htfadd783)
    LowestsbuSet(lowestsbu, htfadd783) 
    HighestsbdSet(highestsbd, htfadd784)
    LowestsbuSet(lowestsbu, htfadd784) 
    HighestsbdSet(highestsbd, htfadd785)
    LowestsbuSet(lowestsbu, htfadd785) 
    HighestsbdSet(highestsbd, htfadd786)
    LowestsbuSet(lowestsbu, htfadd786) 
    HighestsbdSet(highestsbd, htfadd787)
    LowestsbuSet(lowestsbu, htfadd787) 
    HighestsbdSet(highestsbd, htfadd788)
    LowestsbuSet(lowestsbu, htfadd788) 
    HighestsbdSet(highestsbd, htfadd789)
    LowestsbuSet(lowestsbu, htfadd789) 
    HighestsbdSet(highestsbd, htfadd790)
    LowestsbuSet(lowestsbu, htfadd790) 
    HighestsbdSet(highestsbd, htfadd791)
    LowestsbuSet(lowestsbu, htfadd791) 
    HighestsbdSet(highestsbd, htfadd792)
    LowestsbuSet(lowestsbu, htfadd792) 
    HighestsbdSet(highestsbd, htfadd793)
    LowestsbuSet(lowestsbu, htfadd793) 
    HighestsbdSet(highestsbd, htfadd794)
    LowestsbuSet(lowestsbu, htfadd794) 
    HighestsbdSet(highestsbd, htfadd795)
    LowestsbuSet(lowestsbu, htfadd795) 
    HighestsbdSet(highestsbd, htfadd796)
    LowestsbuSet(lowestsbu, htfadd796) 
    HighestsbdSet(highestsbd, htfadd797)
    LowestsbuSet(lowestsbu, htfadd797) 
    HighestsbdSet(highestsbd, htfadd798)
    LowestsbuSet(lowestsbu, htfadd798) 
    HighestsbdSet(highestsbd, htfadd799)
    LowestsbuSet(lowestsbu, htfadd799) 
    HighestsbdSet(highestsbd, htfadd800)
    LowestsbuSet(lowestsbu, htfadd800) 
    HighestsbdSet(highestsbd, htfadd801)
    LowestsbuSet(lowestsbu, htfadd801) 
    HighestsbdSet(highestsbd, htfadd802)
    LowestsbuSet(lowestsbu, htfadd802) 
    HighestsbdSet(highestsbd, htfadd803)
    LowestsbuSet(lowestsbu, htfadd803) 
    HighestsbdSet(highestsbd, htfadd804)
    LowestsbuSet(lowestsbu, htfadd804) 
    HighestsbdSet(highestsbd, htfadd805)
    LowestsbuSet(lowestsbu, htfadd805) 
    HighestsbdSet(highestsbd, htfadd806)
    LowestsbuSet(lowestsbu, htfadd806) 
    HighestsbdSet(highestsbd, htfadd807)
    LowestsbuSet(lowestsbu, htfadd807) 
    HighestsbdSet(highestsbd, htfadd808)
    LowestsbuSet(lowestsbu, htfadd808) 
    HighestsbdSet(highestsbd, htfadd809)
    LowestsbuSet(lowestsbu, htfadd809) 
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
    HighestsbdSet(highestsbd, htfadd901)
    LowestsbuSet(lowestsbu, htfadd901) 
    HighestsbdSet(highestsbd, htfadd902)
    LowestsbuSet(lowestsbu, htfadd902) 
    HighestsbdSet(highestsbd, htfadd903)
    LowestsbuSet(lowestsbu, htfadd903) 
    HighestsbdSet(highestsbd, htfadd904)
    LowestsbuSet(lowestsbu, htfadd904) 
    HighestsbdSet(highestsbd, htfadd905)
    LowestsbuSet(lowestsbu, htfadd905) 
    HighestsbdSet(highestsbd, htfadd906)
    LowestsbuSet(lowestsbu, htfadd906) 
    HighestsbdSet(highestsbd, htfadd907)
    LowestsbuSet(lowestsbu, htfadd907) 
    HighestsbdSet(highestsbd, htfadd908)
    LowestsbuSet(lowestsbu, htfadd908) 
    HighestsbdSet(highestsbd, htfadd909)
    LowestsbuSet(lowestsbu, htfadd909) 
    HighestsbdSet(highestsbd, htfadd910)
    LowestsbuSet(lowestsbu, htfadd910) 
    HighestsbdSet(highestsbd, htfadd911)
    LowestsbuSet(lowestsbu, htfadd911) 
    HighestsbdSet(highestsbd, htfadd912)
    LowestsbuSet(lowestsbu, htfadd912) 
    HighestsbdSet(highestsbd, htfadd913)
    LowestsbuSet(lowestsbu, htfadd913) 
    HighestsbdSet(highestsbd, htfadd914)
    LowestsbuSet(lowestsbu, htfadd914) 
    HighestsbdSet(highestsbd, htfadd915)
    LowestsbuSet(lowestsbu, htfadd915) 
    HighestsbdSet(highestsbd, htfadd916)
    LowestsbuSet(lowestsbu, htfadd916) 
    HighestsbdSet(highestsbd, htfadd917)
    LowestsbuSet(lowestsbu, htfadd917) 
    HighestsbdSet(highestsbd, htfadd918)
    LowestsbuSet(lowestsbu, htfadd918) 
    HighestsbdSet(highestsbd, htfadd919)
    LowestsbuSet(lowestsbu, htfadd919) 
    HighestsbdSet(highestsbd, htfadd920)
    LowestsbuSet(lowestsbu, htfadd920) 
    HighestsbdSet(highestsbd, htfadd921)
    LowestsbuSet(lowestsbu, htfadd921) 
    HighestsbdSet(highestsbd, htfadd922)
    LowestsbuSet(lowestsbu, htfadd922) 
    HighestsbdSet(highestsbd, htfadd923)
    LowestsbuSet(lowestsbu, htfadd923) 
    HighestsbdSet(highestsbd, htfadd924)
    LowestsbuSet(lowestsbu, htfadd924) 
    HighestsbdSet(highestsbd, htfadd925)
    LowestsbuSet(lowestsbu, htfadd925) 
    HighestsbdSet(highestsbd, htfadd926)
    LowestsbuSet(lowestsbu, htfadd926) 
    HighestsbdSet(highestsbd, htfadd927)
    LowestsbuSet(lowestsbu, htfadd927) 
    HighestsbdSet(highestsbd, htfadd928)
    LowestsbuSet(lowestsbu, htfadd928) 
    HighestsbdSet(highestsbd, htfadd929)
    LowestsbuSet(lowestsbu, htfadd929) 
    HighestsbdSet(highestsbd, htfadd930)
    LowestsbuSet(lowestsbu, htfadd930) 
    HighestsbdSet(highestsbd, htfadd931)
    LowestsbuSet(lowestsbu, htfadd931) 
    HighestsbdSet(highestsbd, htfadd932)
    LowestsbuSet(lowestsbu, htfadd932) 
    HighestsbdSet(highestsbd, htfadd933)
    LowestsbuSet(lowestsbu, htfadd933) 
    HighestsbdSet(highestsbd, htfadd934)
    LowestsbuSet(lowestsbu, htfadd934) 
    HighestsbdSet(highestsbd, htfadd935)
    LowestsbuSet(lowestsbu, htfadd935) 
    HighestsbdSet(highestsbd, htfadd936)
    LowestsbuSet(lowestsbu, htfadd936) 
    HighestsbdSet(highestsbd, htfadd937)
    LowestsbuSet(lowestsbu, htfadd937) 
    HighestsbdSet(highestsbd, htfadd938)
    LowestsbuSet(lowestsbu, htfadd938) 
    HighestsbdSet(highestsbd, htfadd939)
    LowestsbuSet(lowestsbu, htfadd939) 
    HighestsbdSet(highestsbd, htfadd940)
    LowestsbuSet(lowestsbu, htfadd940) 
    HighestsbdSet(highestsbd, htfadd941)
    LowestsbuSet(lowestsbu, htfadd941) 
    HighestsbdSet(highestsbd, htfadd942)
    LowestsbuSet(lowestsbu, htfadd942) 
    HighestsbdSet(highestsbd, htfadd943)
    LowestsbuSet(lowestsbu, htfadd943) 
    HighestsbdSet(highestsbd, htfadd944)
    LowestsbuSet(lowestsbu, htfadd944) 
    HighestsbdSet(highestsbd, htfadd945)
    LowestsbuSet(lowestsbu, htfadd945) 
    HighestsbdSet(highestsbd, htfadd946)
    LowestsbuSet(lowestsbu, htfadd946) 
    HighestsbdSet(highestsbd, htfadd947)
    LowestsbuSet(lowestsbu, htfadd947) 
    HighestsbdSet(highestsbd, htfadd948)
    LowestsbuSet(lowestsbu, htfadd948) 
    HighestsbdSet(highestsbd, htfadd949)
    LowestsbuSet(lowestsbu, htfadd949) 
    HighestsbdSet(highestsbd, htfadd950)
    LowestsbuSet(lowestsbu, htfadd950) 
    HighestsbdSet(highestsbd, htfadd951)
    LowestsbuSet(lowestsbu, htfadd951) 
    HighestsbdSet(highestsbd, htfadd952)
    LowestsbuSet(lowestsbu, htfadd952) 
    HighestsbdSet(highestsbd, htfadd953)
    LowestsbuSet(lowestsbu, htfadd953) 
    HighestsbdSet(highestsbd, htfadd954)
    LowestsbuSet(lowestsbu, htfadd954) 
    HighestsbdSet(highestsbd, htfadd955)
    LowestsbuSet(lowestsbu, htfadd955) 
    HighestsbdSet(highestsbd, htfadd956)
    LowestsbuSet(lowestsbu, htfadd956) 
    HighestsbdSet(highestsbd, htfadd957)
    LowestsbuSet(lowestsbu, htfadd957) 
    HighestsbdSet(highestsbd, htfadd958)
    LowestsbuSet(lowestsbu, htfadd958) 
    HighestsbdSet(highestsbd, htfadd959)
    LowestsbuSet(lowestsbu, htfadd959) 
    HighestsbdSet(highestsbd, htfadd960)
    LowestsbuSet(lowestsbu, htfadd960) 
    HighestsbdSet(highestsbd, htfadd961)
    LowestsbuSet(lowestsbu, htfadd961) 
    HighestsbdSet(highestsbd, htfadd962)
    LowestsbuSet(lowestsbu, htfadd962) 
    HighestsbdSet(highestsbd, htfadd963)
    LowestsbuSet(lowestsbu, htfadd963) 
    HighestsbdSet(highestsbd, htfadd964)
    LowestsbuSet(lowestsbu, htfadd964) 
    HighestsbdSet(highestsbd, htfadd965)
    LowestsbuSet(lowestsbu, htfadd965) 
    HighestsbdSet(highestsbd, htfadd966)
    LowestsbuSet(lowestsbu, htfadd966) 
    HighestsbdSet(highestsbd, htfadd967)
    LowestsbuSet(lowestsbu, htfadd967) 
    HighestsbdSet(highestsbd, htfadd968)
    LowestsbuSet(lowestsbu, htfadd968) 
    HighestsbdSet(highestsbd, htfadd969)
    LowestsbuSet(lowestsbu, htfadd969) 
    HighestsbdSet(highestsbd, htfadd970)
    LowestsbuSet(lowestsbu, htfadd970) 
    HighestsbdSet(highestsbd, htfadd971)
    LowestsbuSet(lowestsbu, htfadd971) 
    HighestsbdSet(highestsbd, htfadd972)
    LowestsbuSet(lowestsbu, htfadd972) 
    HighestsbdSet(highestsbd, htfadd973)
    LowestsbuSet(lowestsbu, htfadd973) 
    HighestsbdSet(highestsbd, htfadd974)
    LowestsbuSet(lowestsbu, htfadd974) 
    HighestsbdSet(highestsbd, htfadd975)
    LowestsbuSet(lowestsbu, htfadd975) 
    HighestsbdSet(highestsbd, htfadd976)
    LowestsbuSet(lowestsbu, htfadd976) 
    HighestsbdSet(highestsbd, htfadd977)
    LowestsbuSet(lowestsbu, htfadd977) 
    HighestsbdSet(highestsbd, htfadd978)
    LowestsbuSet(lowestsbu, htfadd978) 
    HighestsbdSet(highestsbd, htfadd979)
    LowestsbuSet(lowestsbu, htfadd979) 
    HighestsbdSet(highestsbd, htfadd980)
    LowestsbuSet(lowestsbu, htfadd980) 
    HighestsbdSet(highestsbd, htfadd981)
    LowestsbuSet(lowestsbu, htfadd981) 
    HighestsbdSet(highestsbd, htfadd982)
    LowestsbuSet(lowestsbu, htfadd982) 
    HighestsbdSet(highestsbd, htfadd983)
    LowestsbuSet(lowestsbu, htfadd983) 
    HighestsbdSet(highestsbd, htfadd984)
    LowestsbuSet(lowestsbu, htfadd984) 
    HighestsbdSet(highestsbd, htfadd985)
    LowestsbuSet(lowestsbu, htfadd985) 
    HighestsbdSet(highestsbd, htfadd986)
    LowestsbuSet(lowestsbu, htfadd986) 
    HighestsbdSet(highestsbd, htfadd987)
    LowestsbuSet(lowestsbu, htfadd987) 
    HighestsbdSet(highestsbd, htfadd988)
    LowestsbuSet(lowestsbu, htfadd988) 
    HighestsbdSet(highestsbd, htfadd989)
    LowestsbuSet(lowestsbu, htfadd989) 
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
    HighestsbdSet(highestsbd, htfadd1081)
    LowestsbuSet(lowestsbu, htfadd1081) 
    HighestsbdSet(highestsbd, htfadd1082)
    LowestsbuSet(lowestsbu, htfadd1082) 
    HighestsbdSet(highestsbd, htfadd1083)
    LowestsbuSet(lowestsbu, htfadd1083) 
    HighestsbdSet(highestsbd, htfadd1084)
    LowestsbuSet(lowestsbu, htfadd1084) 
    HighestsbdSet(highestsbd, htfadd1085)
    LowestsbuSet(lowestsbu, htfadd1085) 
    HighestsbdSet(highestsbd, htfadd1086)
    LowestsbuSet(lowestsbu, htfadd1086) 
    HighestsbdSet(highestsbd, htfadd1087)
    LowestsbuSet(lowestsbu, htfadd1087) 
    HighestsbdSet(highestsbd, htfadd1088)
    LowestsbuSet(lowestsbu, htfadd1088) 
    HighestsbdSet(highestsbd, htfadd1089)
    LowestsbuSet(lowestsbu, htfadd1089) 
    HighestsbdSet(highestsbd, htfadd1090)
    LowestsbuSet(lowestsbu, htfadd1090) 
    HighestsbdSet(highestsbd, htfadd1091)
    LowestsbuSet(lowestsbu, htfadd1091) 
    HighestsbdSet(highestsbd, htfadd1092)
    LowestsbuSet(lowestsbu, htfadd1092) 
    HighestsbdSet(highestsbd, htfadd1093)
    LowestsbuSet(lowestsbu, htfadd1093) 
    HighestsbdSet(highestsbd, htfadd1094)
    LowestsbuSet(lowestsbu, htfadd1094) 
    HighestsbdSet(highestsbd, htfadd1095)
    LowestsbuSet(lowestsbu, htfadd1095) 
    HighestsbdSet(highestsbd, htfadd1096)
    LowestsbuSet(lowestsbu, htfadd1096) 
    HighestsbdSet(highestsbd, htfadd1097)
    LowestsbuSet(lowestsbu, htfadd1097) 
    HighestsbdSet(highestsbd, htfadd1098)
    LowestsbuSet(lowestsbu, htfadd1098) 
    HighestsbdSet(highestsbd, htfadd1099)
    LowestsbuSet(lowestsbu, htfadd1099) 
    HighestsbdSet(highestsbd, htfadd1100)
    LowestsbuSet(lowestsbu, htfadd1100) 
    HighestsbdSet(highestsbd, htfadd1101)
    LowestsbuSet(lowestsbu, htfadd1101) 
    HighestsbdSet(highestsbd, htfadd1102)
    LowestsbuSet(lowestsbu, htfadd1102) 
    HighestsbdSet(highestsbd, htfadd1103)
    LowestsbuSet(lowestsbu, htfadd1103) 
    HighestsbdSet(highestsbd, htfadd1104)
    LowestsbuSet(lowestsbu, htfadd1104) 
    HighestsbdSet(highestsbd, htfadd1105)
    LowestsbuSet(lowestsbu, htfadd1105) 
    HighestsbdSet(highestsbd, htfadd1106)
    LowestsbuSet(lowestsbu, htfadd1106) 
    HighestsbdSet(highestsbd, htfadd1107)
    LowestsbuSet(lowestsbu, htfadd1107) 
    HighestsbdSet(highestsbd, htfadd1108)
    LowestsbuSet(lowestsbu, htfadd1108) 
    HighestsbdSet(highestsbd, htfadd1109)
    LowestsbuSet(lowestsbu, htfadd1109) 
    HighestsbdSet(highestsbd, htfadd1110)
    LowestsbuSet(lowestsbu, htfadd1110) 
    HighestsbdSet(highestsbd, htfadd1111)
    LowestsbuSet(lowestsbu, htfadd1111) 
    HighestsbdSet(highestsbd, htfadd1112)
    LowestsbuSet(lowestsbu, htfadd1112) 
    HighestsbdSet(highestsbd, htfadd1113)
    LowestsbuSet(lowestsbu, htfadd1113) 
    HighestsbdSet(highestsbd, htfadd1114)
    LowestsbuSet(lowestsbu, htfadd1114) 
    HighestsbdSet(highestsbd, htfadd1115)
    LowestsbuSet(lowestsbu, htfadd1115) 
    HighestsbdSet(highestsbd, htfadd1116)
    LowestsbuSet(lowestsbu, htfadd1116) 
    HighestsbdSet(highestsbd, htfadd1117)
    LowestsbuSet(lowestsbu, htfadd1117) 
    HighestsbdSet(highestsbd, htfadd1118)
    LowestsbuSet(lowestsbu, htfadd1118) 
    HighestsbdSet(highestsbd, htfadd1119)
    LowestsbuSet(lowestsbu, htfadd1119) 
    HighestsbdSet(highestsbd, htfadd1120)
    LowestsbuSet(lowestsbu, htfadd1120) 
    HighestsbdSet(highestsbd, htfadd1121)
    LowestsbuSet(lowestsbu, htfadd1121) 
    HighestsbdSet(highestsbd, htfadd1122)
    LowestsbuSet(lowestsbu, htfadd1122) 
    HighestsbdSet(highestsbd, htfadd1123)
    LowestsbuSet(lowestsbu, htfadd1123) 
    HighestsbdSet(highestsbd, htfadd1124)
    LowestsbuSet(lowestsbu, htfadd1124) 
    HighestsbdSet(highestsbd, htfadd1125)
    LowestsbuSet(lowestsbu, htfadd1125) 
    HighestsbdSet(highestsbd, htfadd1126)
    LowestsbuSet(lowestsbu, htfadd1126) 
    HighestsbdSet(highestsbd, htfadd1127)
    LowestsbuSet(lowestsbu, htfadd1127) 
    HighestsbdSet(highestsbd, htfadd1128)
    LowestsbuSet(lowestsbu, htfadd1128) 
    HighestsbdSet(highestsbd, htfadd1129)
    LowestsbuSet(lowestsbu, htfadd1129) 
    HighestsbdSet(highestsbd, htfadd1130)
    LowestsbuSet(lowestsbu, htfadd1130) 
    HighestsbdSet(highestsbd, htfadd1131)
    LowestsbuSet(lowestsbu, htfadd1131) 
    HighestsbdSet(highestsbd, htfadd1132)
    LowestsbuSet(lowestsbu, htfadd1132) 
    HighestsbdSet(highestsbd, htfadd1133)
    LowestsbuSet(lowestsbu, htfadd1133) 
    HighestsbdSet(highestsbd, htfadd1134)
    LowestsbuSet(lowestsbu, htfadd1134) 
    HighestsbdSet(highestsbd, htfadd1135)
    LowestsbuSet(lowestsbu, htfadd1135) 
    HighestsbdSet(highestsbd, htfadd1136)
    LowestsbuSet(lowestsbu, htfadd1136) 
    HighestsbdSet(highestsbd, htfadd1137)
    LowestsbuSet(lowestsbu, htfadd1137) 
    HighestsbdSet(highestsbd, htfadd1138)
    LowestsbuSet(lowestsbu, htfadd1138) 
    HighestsbdSet(highestsbd, htfadd1139)
    LowestsbuSet(lowestsbu, htfadd1139) 
    HighestsbdSet(highestsbd, htfadd1140)
    LowestsbuSet(lowestsbu, htfadd1140) 
    HighestsbdSet(highestsbd, htfadd1141)
    LowestsbuSet(lowestsbu, htfadd1141) 
    HighestsbdSet(highestsbd, htfadd1142)
    LowestsbuSet(lowestsbu, htfadd1142) 
    HighestsbdSet(highestsbd, htfadd1143)
    LowestsbuSet(lowestsbu, htfadd1143) 
    HighestsbdSet(highestsbd, htfadd1144)
    LowestsbuSet(lowestsbu, htfadd1144) 
    HighestsbdSet(highestsbd, htfadd1145)
    LowestsbuSet(lowestsbu, htfadd1145) 
    HighestsbdSet(highestsbd, htfadd1146)
    LowestsbuSet(lowestsbu, htfadd1146) 
    HighestsbdSet(highestsbd, htfadd1147)
    LowestsbuSet(lowestsbu, htfadd1147) 
    HighestsbdSet(highestsbd, htfadd1148)
    LowestsbuSet(lowestsbu, htfadd1148) 
    HighestsbdSet(highestsbd, htfadd1149)
    LowestsbuSet(lowestsbu, htfadd1149) 
    HighestsbdSet(highestsbd, htfadd1150)
    LowestsbuSet(lowestsbu, htfadd1150) 
    HighestsbdSet(highestsbd, htfadd1151)
    LowestsbuSet(lowestsbu, htfadd1151) 
    HighestsbdSet(highestsbd, htfadd1152)
    LowestsbuSet(lowestsbu, htfadd1152) 
    HighestsbdSet(highestsbd, htfadd1153)
    LowestsbuSet(lowestsbu, htfadd1153) 
    HighestsbdSet(highestsbd, htfadd1154)
    LowestsbuSet(lowestsbu, htfadd1154) 
    HighestsbdSet(highestsbd, htfadd1155)
    LowestsbuSet(lowestsbu, htfadd1155) 
    HighestsbdSet(highestsbd, htfadd1156)
    LowestsbuSet(lowestsbu, htfadd1156) 
    HighestsbdSet(highestsbd, htfadd1157)
    LowestsbuSet(lowestsbu, htfadd1157) 
    HighestsbdSet(highestsbd, htfadd1158)
    LowestsbuSet(lowestsbu, htfadd1158) 
    HighestsbdSet(highestsbd, htfadd1159)
    LowestsbuSet(lowestsbu, htfadd1159) 
    HighestsbdSet(highestsbd, htfadd1160)
    LowestsbuSet(lowestsbu, htfadd1160) 
    HighestsbdSet(highestsbd, htfadd1161)
    LowestsbuSet(lowestsbu, htfadd1161) 
    HighestsbdSet(highestsbd, htfadd1162)
    LowestsbuSet(lowestsbu, htfadd1162) 
    HighestsbdSet(highestsbd, htfadd1163)
    LowestsbuSet(lowestsbu, htfadd1163) 
    HighestsbdSet(highestsbd, htfadd1164)
    LowestsbuSet(lowestsbu, htfadd1164) 
    HighestsbdSet(highestsbd, htfadd1165)
    LowestsbuSet(lowestsbu, htfadd1165) 
    HighestsbdSet(highestsbd, htfadd1166)
    LowestsbuSet(lowestsbu, htfadd1166) 
    HighestsbdSet(highestsbd, htfadd1167)
    LowestsbuSet(lowestsbu, htfadd1167) 
    HighestsbdSet(highestsbd, htfadd1168)
    LowestsbuSet(lowestsbu, htfadd1168) 
    HighestsbdSet(highestsbd, htfadd1169)
    LowestsbuSet(lowestsbu, htfadd1169) 
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
    Predictor(htfadd91, estminsbu)
    Predictor(htfadd91, estmaxsbd)  
    Predictor(htfadd92, estminsbu)
    Predictor(htfadd92, estmaxsbd)  
    Predictor(htfadd93, estminsbu)
    Predictor(htfadd93, estmaxsbd)  
    Predictor(htfadd94, estminsbu)
    Predictor(htfadd94, estmaxsbd)  
    Predictor(htfadd95, estminsbu)
    Predictor(htfadd95, estmaxsbd)  
    Predictor(htfadd96, estminsbu)
    Predictor(htfadd96, estmaxsbd)  
    Predictor(htfadd97, estminsbu)
    Predictor(htfadd97, estmaxsbd)  
    Predictor(htfadd98, estminsbu)
    Predictor(htfadd98, estmaxsbd)  
    Predictor(htfadd99, estminsbu)
    Predictor(htfadd99, estmaxsbd)  
    Predictor(htfadd100, estminsbu)
    Predictor(htfadd100, estmaxsbd)  
    Predictor(htfadd101, estminsbu)
    Predictor(htfadd101, estmaxsbd)  
    Predictor(htfadd102, estminsbu)
    Predictor(htfadd102, estmaxsbd)  
    Predictor(htfadd103, estminsbu)
    Predictor(htfadd103, estmaxsbd)  
    Predictor(htfadd104, estminsbu)
    Predictor(htfadd104, estmaxsbd)  
    Predictor(htfadd105, estminsbu)
    Predictor(htfadd105, estmaxsbd)  
    Predictor(htfadd106, estminsbu)
    Predictor(htfadd106, estmaxsbd)  
    Predictor(htfadd107, estminsbu)
    Predictor(htfadd107, estmaxsbd)  
    Predictor(htfadd108, estminsbu)
    Predictor(htfadd108, estmaxsbd)  
    Predictor(htfadd109, estminsbu)
    Predictor(htfadd109, estmaxsbd)  
    Predictor(htfadd110, estminsbu)
    Predictor(htfadd110, estmaxsbd)  
    Predictor(htfadd111, estminsbu)
    Predictor(htfadd111, estmaxsbd)  
    Predictor(htfadd112, estminsbu)
    Predictor(htfadd112, estmaxsbd)  
    Predictor(htfadd113, estminsbu)
    Predictor(htfadd113, estmaxsbd)  
    Predictor(htfadd114, estminsbu)
    Predictor(htfadd114, estmaxsbd)  
    Predictor(htfadd115, estminsbu)
    Predictor(htfadd115, estmaxsbd)  
    Predictor(htfadd116, estminsbu)
    Predictor(htfadd116, estmaxsbd)  
    Predictor(htfadd117, estminsbu)
    Predictor(htfadd117, estmaxsbd)  
    Predictor(htfadd118, estminsbu)
    Predictor(htfadd118, estmaxsbd)  
    Predictor(htfadd119, estminsbu)
    Predictor(htfadd119, estmaxsbd)  
    Predictor(htfadd120, estminsbu)
    Predictor(htfadd120, estmaxsbd)  
    Predictor(htfadd121, estminsbu)
    Predictor(htfadd121, estmaxsbd)  
    Predictor(htfadd122, estminsbu)
    Predictor(htfadd122, estmaxsbd)  
    Predictor(htfadd123, estminsbu)
    Predictor(htfadd123, estmaxsbd)  
    Predictor(htfadd124, estminsbu)
    Predictor(htfadd124, estmaxsbd)  
    Predictor(htfadd125, estminsbu)
    Predictor(htfadd125, estmaxsbd)  
    Predictor(htfadd126, estminsbu)
    Predictor(htfadd126, estmaxsbd)  
    Predictor(htfadd127, estminsbu)
    Predictor(htfadd127, estmaxsbd)  
    Predictor(htfadd128, estminsbu)
    Predictor(htfadd128, estmaxsbd)  
    Predictor(htfadd129, estminsbu)
    Predictor(htfadd129, estmaxsbd)  
    Predictor(htfadd130, estminsbu)
    Predictor(htfadd130, estmaxsbd)  
    Predictor(htfadd131, estminsbu)
    Predictor(htfadd131, estmaxsbd)  
    Predictor(htfadd132, estminsbu)
    Predictor(htfadd132, estmaxsbd)  
    Predictor(htfadd133, estminsbu)
    Predictor(htfadd133, estmaxsbd)  
    Predictor(htfadd134, estminsbu)
    Predictor(htfadd134, estmaxsbd)  
    Predictor(htfadd135, estminsbu)
    Predictor(htfadd135, estmaxsbd)  
    Predictor(htfadd136, estminsbu)
    Predictor(htfadd136, estmaxsbd)  
    Predictor(htfadd137, estminsbu)
    Predictor(htfadd137, estmaxsbd)  
    Predictor(htfadd138, estminsbu)
    Predictor(htfadd138, estmaxsbd)  
    Predictor(htfadd139, estminsbu)
    Predictor(htfadd139, estmaxsbd)  
    Predictor(htfadd140, estminsbu)
    Predictor(htfadd140, estmaxsbd)  
    Predictor(htfadd141, estminsbu)
    Predictor(htfadd141, estmaxsbd)  
    Predictor(htfadd142, estminsbu)
    Predictor(htfadd142, estmaxsbd)  
    Predictor(htfadd143, estminsbu)
    Predictor(htfadd143, estmaxsbd)  
    Predictor(htfadd144, estminsbu)
    Predictor(htfadd144, estmaxsbd)  
    Predictor(htfadd145, estminsbu)
    Predictor(htfadd145, estmaxsbd)  
    Predictor(htfadd146, estminsbu)
    Predictor(htfadd146, estmaxsbd)  
    Predictor(htfadd147, estminsbu)
    Predictor(htfadd147, estmaxsbd)  
    Predictor(htfadd148, estminsbu)
    Predictor(htfadd148, estmaxsbd)  
    Predictor(htfadd149, estminsbu)
    Predictor(htfadd149, estmaxsbd)  
    Predictor(htfadd150, estminsbu)
    Predictor(htfadd150, estmaxsbd)  
    Predictor(htfadd151, estminsbu)
    Predictor(htfadd151, estmaxsbd)  
    Predictor(htfadd152, estminsbu)
    Predictor(htfadd152, estmaxsbd)  
    Predictor(htfadd153, estminsbu)
    Predictor(htfadd153, estmaxsbd)  
    Predictor(htfadd154, estminsbu)
    Predictor(htfadd154, estmaxsbd)  
    Predictor(htfadd155, estminsbu)
    Predictor(htfadd155, estmaxsbd)  
    Predictor(htfadd156, estminsbu)
    Predictor(htfadd156, estmaxsbd)  
    Predictor(htfadd157, estminsbu)
    Predictor(htfadd157, estmaxsbd)  
    Predictor(htfadd158, estminsbu)
    Predictor(htfadd158, estmaxsbd)  
    Predictor(htfadd159, estminsbu)
    Predictor(htfadd159, estmaxsbd)  
    Predictor(htfadd160, estminsbu)
    Predictor(htfadd160, estmaxsbd)  
    Predictor(htfadd161, estminsbu)
    Predictor(htfadd161, estmaxsbd)  
    Predictor(htfadd162, estminsbu)
    Predictor(htfadd162, estmaxsbd)  
    Predictor(htfadd163, estminsbu)
    Predictor(htfadd163, estmaxsbd)  
    Predictor(htfadd164, estminsbu)
    Predictor(htfadd164, estmaxsbd)  
    Predictor(htfadd165, estminsbu)
    Predictor(htfadd165, estmaxsbd)  
    Predictor(htfadd166, estminsbu)
    Predictor(htfadd166, estmaxsbd)  
    Predictor(htfadd167, estminsbu)
    Predictor(htfadd167, estmaxsbd)  
    Predictor(htfadd168, estminsbu)
    Predictor(htfadd168, estmaxsbd)  
    Predictor(htfadd169, estminsbu)
    Predictor(htfadd169, estmaxsbd)  
    Predictor(htfadd170, estminsbu)
    Predictor(htfadd170, estmaxsbd)  
    Predictor(htfadd171, estminsbu)
    Predictor(htfadd171, estmaxsbd)  
    Predictor(htfadd172, estminsbu)
    Predictor(htfadd172, estmaxsbd)  
    Predictor(htfadd173, estminsbu)
    Predictor(htfadd173, estmaxsbd)  
    Predictor(htfadd174, estminsbu)
    Predictor(htfadd174, estmaxsbd)  
    Predictor(htfadd175, estminsbu)
    Predictor(htfadd175, estmaxsbd)  
    Predictor(htfadd176, estminsbu)
    Predictor(htfadd176, estmaxsbd)  
    Predictor(htfadd177, estminsbu)
    Predictor(htfadd177, estmaxsbd)  
    Predictor(htfadd178, estminsbu)
    Predictor(htfadd178, estmaxsbd)  
    Predictor(htfadd179, estminsbu)
    Predictor(htfadd179, estmaxsbd)  
    Predictor(htfadd180, estminsbu)
    Predictor(htfadd180, estmaxsbd)  
    Predictor(htfadd181, estminsbu)
    Predictor(htfadd181, estmaxsbd)  
    Predictor(htfadd182, estminsbu)
    Predictor(htfadd182, estmaxsbd)  
    Predictor(htfadd183, estminsbu)
    Predictor(htfadd183, estmaxsbd)  
    Predictor(htfadd184, estminsbu)
    Predictor(htfadd184, estmaxsbd)  
    Predictor(htfadd185, estminsbu)
    Predictor(htfadd185, estmaxsbd)  
    Predictor(htfadd186, estminsbu)
    Predictor(htfadd186, estmaxsbd)  
    Predictor(htfadd187, estminsbu)
    Predictor(htfadd187, estmaxsbd)  
    Predictor(htfadd188, estminsbu)
    Predictor(htfadd188, estmaxsbd)  
    Predictor(htfadd189, estminsbu)
    Predictor(htfadd189, estmaxsbd)  
    Predictor(htfadd190, estminsbu)
    Predictor(htfadd190, estmaxsbd)  
    Predictor(htfadd191, estminsbu)
    Predictor(htfadd191, estmaxsbd)  
    Predictor(htfadd192, estminsbu)
    Predictor(htfadd192, estmaxsbd)  
    Predictor(htfadd193, estminsbu)
    Predictor(htfadd193, estmaxsbd)  
    Predictor(htfadd194, estminsbu)
    Predictor(htfadd194, estmaxsbd)  
    Predictor(htfadd195, estminsbu)
    Predictor(htfadd195, estmaxsbd)  
    Predictor(htfadd196, estminsbu)
    Predictor(htfadd196, estmaxsbd)  
    Predictor(htfadd197, estminsbu)
    Predictor(htfadd197, estmaxsbd)  
    Predictor(htfadd198, estminsbu)
    Predictor(htfadd198, estmaxsbd)  
    Predictor(htfadd199, estminsbu)
    Predictor(htfadd199, estmaxsbd)  
    Predictor(htfadd200, estminsbu)
    Predictor(htfadd200, estmaxsbd)  
    Predictor(htfadd201, estminsbu)
    Predictor(htfadd201, estmaxsbd)  
    Predictor(htfadd202, estminsbu)
    Predictor(htfadd202, estmaxsbd)  
    Predictor(htfadd203, estminsbu)
    Predictor(htfadd203, estmaxsbd)  
    Predictor(htfadd204, estminsbu)
    Predictor(htfadd204, estmaxsbd)  
    Predictor(htfadd205, estminsbu)
    Predictor(htfadd205, estmaxsbd)  
    Predictor(htfadd206, estminsbu)
    Predictor(htfadd206, estmaxsbd)  
    Predictor(htfadd207, estminsbu)
    Predictor(htfadd207, estmaxsbd)  
    Predictor(htfadd208, estminsbu)
    Predictor(htfadd208, estmaxsbd)  
    Predictor(htfadd209, estminsbu)
    Predictor(htfadd209, estmaxsbd)  
    Predictor(htfadd210, estminsbu)
    Predictor(htfadd210, estmaxsbd)  
    Predictor(htfadd211, estminsbu)
    Predictor(htfadd211, estmaxsbd)  
    Predictor(htfadd212, estminsbu)
    Predictor(htfadd212, estmaxsbd)  
    Predictor(htfadd213, estminsbu)
    Predictor(htfadd213, estmaxsbd)  
    Predictor(htfadd214, estminsbu)
    Predictor(htfadd214, estmaxsbd)  
    Predictor(htfadd215, estminsbu)
    Predictor(htfadd215, estmaxsbd)  
    Predictor(htfadd216, estminsbu)
    Predictor(htfadd216, estmaxsbd)  
    Predictor(htfadd217, estminsbu)
    Predictor(htfadd217, estmaxsbd)  
    Predictor(htfadd218, estminsbu)
    Predictor(htfadd218, estmaxsbd)  
    Predictor(htfadd219, estminsbu)
    Predictor(htfadd219, estmaxsbd)  
    Predictor(htfadd220, estminsbu)
    Predictor(htfadd220, estmaxsbd)  
    Predictor(htfadd221, estminsbu)
    Predictor(htfadd221, estmaxsbd)  
    Predictor(htfadd222, estminsbu)
    Predictor(htfadd222, estmaxsbd)  
    Predictor(htfadd223, estminsbu)
    Predictor(htfadd223, estmaxsbd)  
    Predictor(htfadd224, estminsbu)
    Predictor(htfadd224, estmaxsbd)  
    Predictor(htfadd225, estminsbu)
    Predictor(htfadd225, estmaxsbd)  
    Predictor(htfadd226, estminsbu)
    Predictor(htfadd226, estmaxsbd)  
    Predictor(htfadd227, estminsbu)
    Predictor(htfadd227, estmaxsbd)  
    Predictor(htfadd228, estminsbu)
    Predictor(htfadd228, estmaxsbd)  
    Predictor(htfadd229, estminsbu)
    Predictor(htfadd229, estmaxsbd)  
    Predictor(htfadd230, estminsbu)
    Predictor(htfadd230, estmaxsbd)  
    Predictor(htfadd231, estminsbu)
    Predictor(htfadd231, estmaxsbd)  
    Predictor(htfadd232, estminsbu)
    Predictor(htfadd232, estmaxsbd)  
    Predictor(htfadd233, estminsbu)
    Predictor(htfadd233, estmaxsbd)  
    Predictor(htfadd234, estminsbu)
    Predictor(htfadd234, estmaxsbd)  
    Predictor(htfadd235, estminsbu)
    Predictor(htfadd235, estmaxsbd)  
    Predictor(htfadd236, estminsbu)
    Predictor(htfadd236, estmaxsbd)  
    Predictor(htfadd237, estminsbu)
    Predictor(htfadd237, estmaxsbd)  
    Predictor(htfadd238, estminsbu)
    Predictor(htfadd238, estmaxsbd)  
    Predictor(htfadd239, estminsbu)
    Predictor(htfadd239, estmaxsbd)  
    Predictor(htfadd240, estminsbu)
    Predictor(htfadd240, estmaxsbd)  
    Predictor(htfadd241, estminsbu)
    Predictor(htfadd241, estmaxsbd)  
    Predictor(htfadd242, estminsbu)
    Predictor(htfadd242, estmaxsbd)  
    Predictor(htfadd243, estminsbu)
    Predictor(htfadd243, estmaxsbd)  
    Predictor(htfadd244, estminsbu)
    Predictor(htfadd244, estmaxsbd)  
    Predictor(htfadd245, estminsbu)
    Predictor(htfadd245, estmaxsbd)  
    Predictor(htfadd246, estminsbu)
    Predictor(htfadd246, estmaxsbd)  
    Predictor(htfadd247, estminsbu)
    Predictor(htfadd247, estmaxsbd)  
    Predictor(htfadd248, estminsbu)
    Predictor(htfadd248, estmaxsbd)  
    Predictor(htfadd249, estminsbu)
    Predictor(htfadd249, estmaxsbd)  
    Predictor(htfadd250, estminsbu)
    Predictor(htfadd250, estmaxsbd)  
    Predictor(htfadd251, estminsbu)
    Predictor(htfadd251, estmaxsbd)  
    Predictor(htfadd252, estminsbu)
    Predictor(htfadd252, estmaxsbd)  
    Predictor(htfadd253, estminsbu)
    Predictor(htfadd253, estmaxsbd)  
    Predictor(htfadd254, estminsbu)
    Predictor(htfadd254, estmaxsbd)  
    Predictor(htfadd255, estminsbu)
    Predictor(htfadd255, estmaxsbd)  
    Predictor(htfadd256, estminsbu)
    Predictor(htfadd256, estmaxsbd)  
    Predictor(htfadd257, estminsbu)
    Predictor(htfadd257, estmaxsbd)  
    Predictor(htfadd258, estminsbu)
    Predictor(htfadd258, estmaxsbd)  
    Predictor(htfadd259, estminsbu)
    Predictor(htfadd259, estmaxsbd)  
    Predictor(htfadd260, estminsbu)
    Predictor(htfadd260, estmaxsbd)  
    Predictor(htfadd261, estminsbu)
    Predictor(htfadd261, estmaxsbd)  
    Predictor(htfadd262, estminsbu)
    Predictor(htfadd262, estmaxsbd)  
    Predictor(htfadd263, estminsbu)
    Predictor(htfadd263, estmaxsbd)  
    Predictor(htfadd264, estminsbu)
    Predictor(htfadd264, estmaxsbd)  
    Predictor(htfadd265, estminsbu)
    Predictor(htfadd265, estmaxsbd)  
    Predictor(htfadd266, estminsbu)
    Predictor(htfadd266, estmaxsbd)  
    Predictor(htfadd267, estminsbu)
    Predictor(htfadd267, estmaxsbd)  
    Predictor(htfadd268, estminsbu)
    Predictor(htfadd268, estmaxsbd)  
    Predictor(htfadd269, estminsbu)
    Predictor(htfadd269, estmaxsbd)  
    Predictor(htfadd270, estminsbu)
    Predictor(htfadd270, estmaxsbd)  
    Predictor(htfadd271, estminsbu)
    Predictor(htfadd271, estmaxsbd)  
    Predictor(htfadd272, estminsbu)
    Predictor(htfadd272, estmaxsbd)  
    Predictor(htfadd273, estminsbu)
    Predictor(htfadd273, estmaxsbd)  
    Predictor(htfadd274, estminsbu)
    Predictor(htfadd274, estmaxsbd)  
    Predictor(htfadd275, estminsbu)
    Predictor(htfadd275, estmaxsbd)  
    Predictor(htfadd276, estminsbu)
    Predictor(htfadd276, estmaxsbd)  
    Predictor(htfadd277, estminsbu)
    Predictor(htfadd277, estmaxsbd)  
    Predictor(htfadd278, estminsbu)
    Predictor(htfadd278, estmaxsbd)  
    Predictor(htfadd279, estminsbu)
    Predictor(htfadd279, estmaxsbd)  
    Predictor(htfadd280, estminsbu)
    Predictor(htfadd280, estmaxsbd)  
    Predictor(htfadd281, estminsbu)
    Predictor(htfadd281, estmaxsbd)  
    Predictor(htfadd282, estminsbu)
    Predictor(htfadd282, estmaxsbd)  
    Predictor(htfadd283, estminsbu)
    Predictor(htfadd283, estmaxsbd)  
    Predictor(htfadd284, estminsbu)
    Predictor(htfadd284, estmaxsbd)  
    Predictor(htfadd285, estminsbu)
    Predictor(htfadd285, estmaxsbd)  
    Predictor(htfadd286, estminsbu)
    Predictor(htfadd286, estmaxsbd)  
    Predictor(htfadd287, estminsbu)
    Predictor(htfadd287, estmaxsbd)  
    Predictor(htfadd288, estminsbu)
    Predictor(htfadd288, estmaxsbd)  
    Predictor(htfadd289, estminsbu)
    Predictor(htfadd289, estmaxsbd)  
    Predictor(htfadd290, estminsbu)
    Predictor(htfadd290, estmaxsbd)  
    Predictor(htfadd291, estminsbu)
    Predictor(htfadd291, estmaxsbd)  
    Predictor(htfadd292, estminsbu)
    Predictor(htfadd292, estmaxsbd)  
    Predictor(htfadd293, estminsbu)
    Predictor(htfadd293, estmaxsbd)  
    Predictor(htfadd294, estminsbu)
    Predictor(htfadd294, estmaxsbd)  
    Predictor(htfadd295, estminsbu)
    Predictor(htfadd295, estmaxsbd)  
    Predictor(htfadd296, estminsbu)
    Predictor(htfadd296, estmaxsbd)  
    Predictor(htfadd297, estminsbu)
    Predictor(htfadd297, estmaxsbd)  
    Predictor(htfadd298, estminsbu)
    Predictor(htfadd298, estmaxsbd)  
    Predictor(htfadd299, estminsbu)
    Predictor(htfadd299, estmaxsbd)  
    Predictor(htfadd300, estminsbu)
    Predictor(htfadd300, estmaxsbd)  
    Predictor(htfadd301, estminsbu)
    Predictor(htfadd301, estmaxsbd)  
    Predictor(htfadd302, estminsbu)
    Predictor(htfadd302, estmaxsbd)  
    Predictor(htfadd303, estminsbu)
    Predictor(htfadd303, estmaxsbd)  
    Predictor(htfadd304, estminsbu)
    Predictor(htfadd304, estmaxsbd)  
    Predictor(htfadd305, estminsbu)
    Predictor(htfadd305, estmaxsbd)  
    Predictor(htfadd306, estminsbu)
    Predictor(htfadd306, estmaxsbd)  
    Predictor(htfadd307, estminsbu)
    Predictor(htfadd307, estmaxsbd)  
    Predictor(htfadd308, estminsbu)
    Predictor(htfadd308, estmaxsbd)  
    Predictor(htfadd309, estminsbu)
    Predictor(htfadd309, estmaxsbd)  
    Predictor(htfadd310, estminsbu)
    Predictor(htfadd310, estmaxsbd)  
    Predictor(htfadd311, estminsbu)
    Predictor(htfadd311, estmaxsbd)  
    Predictor(htfadd312, estminsbu)
    Predictor(htfadd312, estmaxsbd)  
    Predictor(htfadd313, estminsbu)
    Predictor(htfadd313, estmaxsbd)  
    Predictor(htfadd314, estminsbu)
    Predictor(htfadd314, estmaxsbd)  
    Predictor(htfadd315, estminsbu)
    Predictor(htfadd315, estmaxsbd)  
    Predictor(htfadd316, estminsbu)
    Predictor(htfadd316, estmaxsbd)  
    Predictor(htfadd317, estminsbu)
    Predictor(htfadd317, estmaxsbd)  
    Predictor(htfadd318, estminsbu)
    Predictor(htfadd318, estmaxsbd)  
    Predictor(htfadd319, estminsbu)
    Predictor(htfadd319, estmaxsbd)  
    Predictor(htfadd320, estminsbu)
    Predictor(htfadd320, estmaxsbd)  
    Predictor(htfadd321, estminsbu)
    Predictor(htfadd321, estmaxsbd)  
    Predictor(htfadd322, estminsbu)
    Predictor(htfadd322, estmaxsbd)  
    Predictor(htfadd323, estminsbu)
    Predictor(htfadd323, estmaxsbd)  
    Predictor(htfadd324, estminsbu)
    Predictor(htfadd324, estmaxsbd)  
    Predictor(htfadd325, estminsbu)
    Predictor(htfadd325, estmaxsbd)  
    Predictor(htfadd326, estminsbu)
    Predictor(htfadd326, estmaxsbd)  
    Predictor(htfadd327, estminsbu)
    Predictor(htfadd327, estmaxsbd)  
    Predictor(htfadd328, estminsbu)
    Predictor(htfadd328, estmaxsbd)  
    Predictor(htfadd329, estminsbu)
    Predictor(htfadd329, estmaxsbd)  
    Predictor(htfadd330, estminsbu)
    Predictor(htfadd330, estmaxsbd)  
    Predictor(htfadd331, estminsbu)
    Predictor(htfadd331, estmaxsbd)  
    Predictor(htfadd332, estminsbu)
    Predictor(htfadd332, estmaxsbd)  
    Predictor(htfadd333, estminsbu)
    Predictor(htfadd333, estmaxsbd)  
    Predictor(htfadd334, estminsbu)
    Predictor(htfadd334, estmaxsbd)  
    Predictor(htfadd335, estminsbu)
    Predictor(htfadd335, estmaxsbd)  
    Predictor(htfadd336, estminsbu)
    Predictor(htfadd336, estmaxsbd)  
    Predictor(htfadd337, estminsbu)
    Predictor(htfadd337, estmaxsbd)  
    Predictor(htfadd338, estminsbu)
    Predictor(htfadd338, estmaxsbd)  
    Predictor(htfadd339, estminsbu)
    Predictor(htfadd339, estmaxsbd)  
    Predictor(htfadd340, estminsbu)
    Predictor(htfadd340, estmaxsbd)  
    Predictor(htfadd341, estminsbu)
    Predictor(htfadd341, estmaxsbd)  
    Predictor(htfadd342, estminsbu)
    Predictor(htfadd342, estmaxsbd)  
    Predictor(htfadd343, estminsbu)
    Predictor(htfadd343, estmaxsbd)  
    Predictor(htfadd344, estminsbu)
    Predictor(htfadd344, estmaxsbd)  
    Predictor(htfadd345, estminsbu)
    Predictor(htfadd345, estmaxsbd)  
    Predictor(htfadd346, estminsbu)
    Predictor(htfadd346, estmaxsbd)  
    Predictor(htfadd347, estminsbu)
    Predictor(htfadd347, estmaxsbd)  
    Predictor(htfadd348, estminsbu)
    Predictor(htfadd348, estmaxsbd)  
    Predictor(htfadd349, estminsbu)
    Predictor(htfadd349, estmaxsbd)  
    Predictor(htfadd350, estminsbu)
    Predictor(htfadd350, estmaxsbd)  
    Predictor(htfadd351, estminsbu)
    Predictor(htfadd351, estmaxsbd)  
    Predictor(htfadd352, estminsbu)
    Predictor(htfadd352, estmaxsbd)  
    Predictor(htfadd353, estminsbu)
    Predictor(htfadd353, estmaxsbd)  
    Predictor(htfadd354, estminsbu)
    Predictor(htfadd354, estmaxsbd)  
    Predictor(htfadd355, estminsbu)
    Predictor(htfadd355, estmaxsbd)  
    Predictor(htfadd356, estminsbu)
    Predictor(htfadd356, estmaxsbd)  
    Predictor(htfadd357, estminsbu)
    Predictor(htfadd357, estmaxsbd)  
    Predictor(htfadd358, estminsbu)
    Predictor(htfadd358, estmaxsbd)  
    Predictor(htfadd359, estminsbu)
    Predictor(htfadd359, estmaxsbd)  
    Predictor(htfadd360, estminsbu)
    Predictor(htfadd360, estmaxsbd)  
    Predictor(htfadd361, estminsbu)
    Predictor(htfadd361, estmaxsbd)  
    Predictor(htfadd362, estminsbu)
    Predictor(htfadd362, estmaxsbd)  
    Predictor(htfadd363, estminsbu)
    Predictor(htfadd363, estmaxsbd)  
    Predictor(htfadd364, estminsbu)
    Predictor(htfadd364, estmaxsbd)  
    Predictor(htfadd365, estminsbu)
    Predictor(htfadd365, estmaxsbd)  
    Predictor(htfadd366, estminsbu)
    Predictor(htfadd366, estmaxsbd)  
    Predictor(htfadd367, estminsbu)
    Predictor(htfadd367, estmaxsbd)  
    Predictor(htfadd368, estminsbu)
    Predictor(htfadd368, estmaxsbd)  
    Predictor(htfadd369, estminsbu)
    Predictor(htfadd369, estmaxsbd)  
    Predictor(htfadd370, estminsbu)
    Predictor(htfadd370, estmaxsbd)  
    Predictor(htfadd371, estminsbu)
    Predictor(htfadd371, estmaxsbd)  
    Predictor(htfadd372, estminsbu)
    Predictor(htfadd372, estmaxsbd)  
    Predictor(htfadd373, estminsbu)
    Predictor(htfadd373, estmaxsbd)  
    Predictor(htfadd374, estminsbu)
    Predictor(htfadd374, estmaxsbd)  
    Predictor(htfadd375, estminsbu)
    Predictor(htfadd375, estmaxsbd)  
    Predictor(htfadd376, estminsbu)
    Predictor(htfadd376, estmaxsbd)  
    Predictor(htfadd377, estminsbu)
    Predictor(htfadd377, estmaxsbd)  
    Predictor(htfadd378, estminsbu)
    Predictor(htfadd378, estmaxsbd)  
    Predictor(htfadd379, estminsbu)
    Predictor(htfadd379, estmaxsbd)  
    Predictor(htfadd380, estminsbu)
    Predictor(htfadd380, estmaxsbd)  
    Predictor(htfadd381, estminsbu)
    Predictor(htfadd381, estmaxsbd)  
    Predictor(htfadd382, estminsbu)
    Predictor(htfadd382, estmaxsbd)  
    Predictor(htfadd383, estminsbu)
    Predictor(htfadd383, estmaxsbd)  
    Predictor(htfadd384, estminsbu)
    Predictor(htfadd384, estmaxsbd)  
    Predictor(htfadd385, estminsbu)
    Predictor(htfadd385, estmaxsbd)  
    Predictor(htfadd386, estminsbu)
    Predictor(htfadd386, estmaxsbd)  
    Predictor(htfadd387, estminsbu)
    Predictor(htfadd387, estmaxsbd)  
    Predictor(htfadd388, estminsbu)
    Predictor(htfadd388, estmaxsbd)  
    Predictor(htfadd389, estminsbu)
    Predictor(htfadd389, estmaxsbd)  
    Predictor(htfadd390, estminsbu)
    Predictor(htfadd390, estmaxsbd)  
    Predictor(htfadd391, estminsbu)
    Predictor(htfadd391, estmaxsbd)  
    Predictor(htfadd392, estminsbu)
    Predictor(htfadd392, estmaxsbd)  
    Predictor(htfadd393, estminsbu)
    Predictor(htfadd393, estmaxsbd)  
    Predictor(htfadd394, estminsbu)
    Predictor(htfadd394, estmaxsbd)  
    Predictor(htfadd395, estminsbu)
    Predictor(htfadd395, estmaxsbd)  
    Predictor(htfadd396, estminsbu)
    Predictor(htfadd396, estmaxsbd)  
    Predictor(htfadd397, estminsbu)
    Predictor(htfadd397, estmaxsbd)  
    Predictor(htfadd398, estminsbu)
    Predictor(htfadd398, estmaxsbd)  
    Predictor(htfadd399, estminsbu)
    Predictor(htfadd399, estmaxsbd)  
    Predictor(htfadd400, estminsbu)
    Predictor(htfadd400, estmaxsbd)  
    Predictor(htfadd401, estminsbu)
    Predictor(htfadd401, estmaxsbd)  
    Predictor(htfadd402, estminsbu)
    Predictor(htfadd402, estmaxsbd)  
    Predictor(htfadd403, estminsbu)
    Predictor(htfadd403, estmaxsbd)  
    Predictor(htfadd404, estminsbu)
    Predictor(htfadd404, estmaxsbd)  
    Predictor(htfadd405, estminsbu)
    Predictor(htfadd405, estmaxsbd)  
    Predictor(htfadd406, estminsbu)
    Predictor(htfadd406, estmaxsbd)  
    Predictor(htfadd407, estminsbu)
    Predictor(htfadd407, estmaxsbd)  
    Predictor(htfadd408, estminsbu)
    Predictor(htfadd408, estmaxsbd)  
    Predictor(htfadd409, estminsbu)
    Predictor(htfadd409, estmaxsbd)  
    Predictor(htfadd410, estminsbu)
    Predictor(htfadd410, estmaxsbd)  
    Predictor(htfadd411, estminsbu)
    Predictor(htfadd411, estmaxsbd)  
    Predictor(htfadd412, estminsbu)
    Predictor(htfadd412, estmaxsbd)  
    Predictor(htfadd413, estminsbu)
    Predictor(htfadd413, estmaxsbd)  
    Predictor(htfadd414, estminsbu)
    Predictor(htfadd414, estmaxsbd)  
    Predictor(htfadd415, estminsbu)
    Predictor(htfadd415, estmaxsbd)  
    Predictor(htfadd416, estminsbu)
    Predictor(htfadd416, estmaxsbd)  
    Predictor(htfadd417, estminsbu)
    Predictor(htfadd417, estmaxsbd)  
    Predictor(htfadd418, estminsbu)
    Predictor(htfadd418, estmaxsbd)  
    Predictor(htfadd419, estminsbu)
    Predictor(htfadd419, estmaxsbd)  
    Predictor(htfadd420, estminsbu)
    Predictor(htfadd420, estmaxsbd)  
    Predictor(htfadd421, estminsbu)
    Predictor(htfadd421, estmaxsbd)  
    Predictor(htfadd422, estminsbu)
    Predictor(htfadd422, estmaxsbd)  
    Predictor(htfadd423, estminsbu)
    Predictor(htfadd423, estmaxsbd)  
    Predictor(htfadd424, estminsbu)
    Predictor(htfadd424, estmaxsbd)  
    Predictor(htfadd425, estminsbu)
    Predictor(htfadd425, estmaxsbd)  
    Predictor(htfadd426, estminsbu)
    Predictor(htfadd426, estmaxsbd)  
    Predictor(htfadd427, estminsbu)
    Predictor(htfadd427, estmaxsbd)  
    Predictor(htfadd428, estminsbu)
    Predictor(htfadd428, estmaxsbd)  
    Predictor(htfadd429, estminsbu)
    Predictor(htfadd429, estmaxsbd)  
    Predictor(htfadd430, estminsbu)
    Predictor(htfadd430, estmaxsbd)  
    Predictor(htfadd431, estminsbu)
    Predictor(htfadd431, estmaxsbd)  
    Predictor(htfadd432, estminsbu)
    Predictor(htfadd432, estmaxsbd)  
    Predictor(htfadd433, estminsbu)
    Predictor(htfadd433, estmaxsbd)  
    Predictor(htfadd434, estminsbu)
    Predictor(htfadd434, estmaxsbd)  
    Predictor(htfadd435, estminsbu)
    Predictor(htfadd435, estmaxsbd)  
    Predictor(htfadd436, estminsbu)
    Predictor(htfadd436, estmaxsbd)  
    Predictor(htfadd437, estminsbu)
    Predictor(htfadd437, estmaxsbd)  
    Predictor(htfadd438, estminsbu)
    Predictor(htfadd438, estmaxsbd)  
    Predictor(htfadd439, estminsbu)
    Predictor(htfadd439, estmaxsbd)  
    Predictor(htfadd440, estminsbu)
    Predictor(htfadd440, estmaxsbd)  
    Predictor(htfadd441, estminsbu)
    Predictor(htfadd441, estmaxsbd)  
    Predictor(htfadd442, estminsbu)
    Predictor(htfadd442, estmaxsbd)  
    Predictor(htfadd443, estminsbu)
    Predictor(htfadd443, estmaxsbd)  
    Predictor(htfadd444, estminsbu)
    Predictor(htfadd444, estmaxsbd)  
    Predictor(htfadd445, estminsbu)
    Predictor(htfadd445, estmaxsbd)  
    Predictor(htfadd446, estminsbu)
    Predictor(htfadd446, estmaxsbd)  
    Predictor(htfadd447, estminsbu)
    Predictor(htfadd447, estmaxsbd)  
    Predictor(htfadd448, estminsbu)
    Predictor(htfadd448, estmaxsbd)  
    Predictor(htfadd449, estminsbu)
    Predictor(htfadd449, estmaxsbd)  
    Predictor(htfadd450, estminsbu)
    Predictor(htfadd450, estmaxsbd)  
    Predictor(htfadd451, estminsbu)
    Predictor(htfadd451, estmaxsbd)  
    Predictor(htfadd452, estminsbu)
    Predictor(htfadd452, estmaxsbd)  
    Predictor(htfadd453, estminsbu)
    Predictor(htfadd453, estmaxsbd)  
    Predictor(htfadd454, estminsbu)
    Predictor(htfadd454, estmaxsbd)  
    Predictor(htfadd455, estminsbu)
    Predictor(htfadd455, estmaxsbd)  
    Predictor(htfadd456, estminsbu)
    Predictor(htfadd456, estmaxsbd)  
    Predictor(htfadd457, estminsbu)
    Predictor(htfadd457, estmaxsbd)  
    Predictor(htfadd458, estminsbu)
    Predictor(htfadd458, estmaxsbd)  
    Predictor(htfadd459, estminsbu)
    Predictor(htfadd459, estmaxsbd)  
    Predictor(htfadd460, estminsbu)
    Predictor(htfadd460, estmaxsbd)  
    Predictor(htfadd461, estminsbu)
    Predictor(htfadd461, estmaxsbd)  
    Predictor(htfadd462, estminsbu)
    Predictor(htfadd462, estmaxsbd)  
    Predictor(htfadd463, estminsbu)
    Predictor(htfadd463, estmaxsbd)  
    Predictor(htfadd464, estminsbu)
    Predictor(htfadd464, estmaxsbd)  
    Predictor(htfadd465, estminsbu)
    Predictor(htfadd465, estmaxsbd)  
    Predictor(htfadd466, estminsbu)
    Predictor(htfadd466, estmaxsbd)  
    Predictor(htfadd467, estminsbu)
    Predictor(htfadd467, estmaxsbd)  
    Predictor(htfadd468, estminsbu)
    Predictor(htfadd468, estmaxsbd)  
    Predictor(htfadd469, estminsbu)
    Predictor(htfadd469, estmaxsbd)  
    Predictor(htfadd470, estminsbu)
    Predictor(htfadd470, estmaxsbd)  
    Predictor(htfadd471, estminsbu)
    Predictor(htfadd471, estmaxsbd)  
    Predictor(htfadd472, estminsbu)
    Predictor(htfadd472, estmaxsbd)  
    Predictor(htfadd473, estminsbu)
    Predictor(htfadd473, estmaxsbd)  
    Predictor(htfadd474, estminsbu)
    Predictor(htfadd474, estmaxsbd)  
    Predictor(htfadd475, estminsbu)
    Predictor(htfadd475, estmaxsbd)  
    Predictor(htfadd476, estminsbu)
    Predictor(htfadd476, estmaxsbd)  
    Predictor(htfadd477, estminsbu)
    Predictor(htfadd477, estmaxsbd)  
    Predictor(htfadd478, estminsbu)
    Predictor(htfadd478, estmaxsbd)  
    Predictor(htfadd479, estminsbu)
    Predictor(htfadd479, estmaxsbd)  
    Predictor(htfadd480, estminsbu)
    Predictor(htfadd480, estmaxsbd)  
    Predictor(htfadd481, estminsbu)
    Predictor(htfadd481, estmaxsbd)  
    Predictor(htfadd482, estminsbu)
    Predictor(htfadd482, estmaxsbd)  
    Predictor(htfadd483, estminsbu)
    Predictor(htfadd483, estmaxsbd)  
    Predictor(htfadd484, estminsbu)
    Predictor(htfadd484, estmaxsbd)  
    Predictor(htfadd485, estminsbu)
    Predictor(htfadd485, estmaxsbd)  
    Predictor(htfadd486, estminsbu)
    Predictor(htfadd486, estmaxsbd)  
    Predictor(htfadd487, estminsbu)
    Predictor(htfadd487, estmaxsbd)  
    Predictor(htfadd488, estminsbu)
    Predictor(htfadd488, estmaxsbd)  
    Predictor(htfadd489, estminsbu)
    Predictor(htfadd489, estmaxsbd)  
    Predictor(htfadd490, estminsbu)
    Predictor(htfadd490, estmaxsbd)  
    Predictor(htfadd491, estminsbu)
    Predictor(htfadd491, estmaxsbd)  
    Predictor(htfadd492, estminsbu)
    Predictor(htfadd492, estmaxsbd)  
    Predictor(htfadd493, estminsbu)
    Predictor(htfadd493, estmaxsbd)  
    Predictor(htfadd494, estminsbu)
    Predictor(htfadd494, estmaxsbd)  
    Predictor(htfadd495, estminsbu)
    Predictor(htfadd495, estmaxsbd)  
    Predictor(htfadd496, estminsbu)
    Predictor(htfadd496, estmaxsbd)  
    Predictor(htfadd497, estminsbu)
    Predictor(htfadd497, estmaxsbd)  
    Predictor(htfadd498, estminsbu)
    Predictor(htfadd498, estmaxsbd)  
    Predictor(htfadd499, estminsbu)
    Predictor(htfadd499, estmaxsbd)  
    Predictor(htfadd500, estminsbu)
    Predictor(htfadd500, estmaxsbd)  
    Predictor(htfadd501, estminsbu)
    Predictor(htfadd501, estmaxsbd)  
    Predictor(htfadd502, estminsbu)
    Predictor(htfadd502, estmaxsbd)  
    Predictor(htfadd503, estminsbu)
    Predictor(htfadd503, estmaxsbd)  
    Predictor(htfadd504, estminsbu)
    Predictor(htfadd504, estmaxsbd)  
    Predictor(htfadd505, estminsbu)
    Predictor(htfadd505, estmaxsbd)  
    Predictor(htfadd506, estminsbu)
    Predictor(htfadd506, estmaxsbd)  
    Predictor(htfadd507, estminsbu)
    Predictor(htfadd507, estmaxsbd)  
    Predictor(htfadd508, estminsbu)
    Predictor(htfadd508, estmaxsbd)  
    Predictor(htfadd509, estminsbu)
    Predictor(htfadd509, estmaxsbd)  
    Predictor(htfadd510, estminsbu)
    Predictor(htfadd510, estmaxsbd)  
    Predictor(htfadd511, estminsbu)
    Predictor(htfadd511, estmaxsbd)  
    Predictor(htfadd512, estminsbu)
    Predictor(htfadd512, estmaxsbd)  
    Predictor(htfadd513, estminsbu)
    Predictor(htfadd513, estmaxsbd)  
    Predictor(htfadd514, estminsbu)
    Predictor(htfadd514, estmaxsbd)  
    Predictor(htfadd515, estminsbu)
    Predictor(htfadd515, estmaxsbd)  
    Predictor(htfadd516, estminsbu)
    Predictor(htfadd516, estmaxsbd)  
    Predictor(htfadd517, estminsbu)
    Predictor(htfadd517, estmaxsbd)  
    Predictor(htfadd518, estminsbu)
    Predictor(htfadd518, estmaxsbd)  
    Predictor(htfadd519, estminsbu)
    Predictor(htfadd519, estmaxsbd)  
    Predictor(htfadd520, estminsbu)
    Predictor(htfadd520, estmaxsbd)  
    Predictor(htfadd521, estminsbu)
    Predictor(htfadd521, estmaxsbd)  
    Predictor(htfadd522, estminsbu)
    Predictor(htfadd522, estmaxsbd)  
    Predictor(htfadd523, estminsbu)
    Predictor(htfadd523, estmaxsbd)  
    Predictor(htfadd524, estminsbu)
    Predictor(htfadd524, estmaxsbd)  
    Predictor(htfadd525, estminsbu)
    Predictor(htfadd525, estmaxsbd)  
    Predictor(htfadd526, estminsbu)
    Predictor(htfadd526, estmaxsbd)  
    Predictor(htfadd527, estminsbu)
    Predictor(htfadd527, estmaxsbd)  
    Predictor(htfadd528, estminsbu)
    Predictor(htfadd528, estmaxsbd)  
    Predictor(htfadd529, estminsbu)
    Predictor(htfadd529, estmaxsbd)  
    Predictor(htfadd530, estminsbu)
    Predictor(htfadd530, estmaxsbd)  
    Predictor(htfadd531, estminsbu)
    Predictor(htfadd531, estmaxsbd)  
    Predictor(htfadd532, estminsbu)
    Predictor(htfadd532, estmaxsbd)  
    Predictor(htfadd533, estminsbu)
    Predictor(htfadd533, estmaxsbd)  
    Predictor(htfadd534, estminsbu)
    Predictor(htfadd534, estmaxsbd)  
    Predictor(htfadd535, estminsbu)
    Predictor(htfadd535, estmaxsbd)  
    Predictor(htfadd536, estminsbu)
    Predictor(htfadd536, estmaxsbd)  
    Predictor(htfadd537, estminsbu)
    Predictor(htfadd537, estmaxsbd)  
    Predictor(htfadd538, estminsbu)
    Predictor(htfadd538, estmaxsbd)  
    Predictor(htfadd539, estminsbu)
    Predictor(htfadd539, estmaxsbd)  
    Predictor(htfadd540, estminsbu)
    Predictor(htfadd540, estmaxsbd)  
    Predictor(htfadd541, estminsbu)
    Predictor(htfadd541, estmaxsbd)  
    Predictor(htfadd542, estminsbu)
    Predictor(htfadd542, estmaxsbd)  
    Predictor(htfadd543, estminsbu)
    Predictor(htfadd543, estmaxsbd)  
    Predictor(htfadd544, estminsbu)
    Predictor(htfadd544, estmaxsbd)  
    Predictor(htfadd545, estminsbu)
    Predictor(htfadd545, estmaxsbd)  
    Predictor(htfadd546, estminsbu)
    Predictor(htfadd546, estmaxsbd)  
    Predictor(htfadd547, estminsbu)
    Predictor(htfadd547, estmaxsbd)  
    Predictor(htfadd548, estminsbu)
    Predictor(htfadd548, estmaxsbd)  
    Predictor(htfadd549, estminsbu)
    Predictor(htfadd549, estmaxsbd)  
    Predictor(htfadd550, estminsbu)
    Predictor(htfadd550, estmaxsbd)  
    Predictor(htfadd551, estminsbu)
    Predictor(htfadd551, estmaxsbd)  
    Predictor(htfadd552, estminsbu)
    Predictor(htfadd552, estmaxsbd)  
    Predictor(htfadd553, estminsbu)
    Predictor(htfadd553, estmaxsbd)  
    Predictor(htfadd554, estminsbu)
    Predictor(htfadd554, estmaxsbd)  
    Predictor(htfadd555, estminsbu)
    Predictor(htfadd555, estmaxsbd)  
    Predictor(htfadd556, estminsbu)
    Predictor(htfadd556, estmaxsbd)  
    Predictor(htfadd557, estminsbu)
    Predictor(htfadd557, estmaxsbd)  
    Predictor(htfadd558, estminsbu)
    Predictor(htfadd558, estmaxsbd)  
    Predictor(htfadd559, estminsbu)
    Predictor(htfadd559, estmaxsbd)  
    Predictor(htfadd560, estminsbu)
    Predictor(htfadd560, estmaxsbd)  
    Predictor(htfadd561, estminsbu)
    Predictor(htfadd561, estmaxsbd)  
    Predictor(htfadd562, estminsbu)
    Predictor(htfadd562, estmaxsbd)  
    Predictor(htfadd563, estminsbu)
    Predictor(htfadd563, estmaxsbd)  
    Predictor(htfadd564, estminsbu)
    Predictor(htfadd564, estmaxsbd)  
    Predictor(htfadd565, estminsbu)
    Predictor(htfadd565, estmaxsbd)  
    Predictor(htfadd566, estminsbu)
    Predictor(htfadd566, estmaxsbd)  
    Predictor(htfadd567, estminsbu)
    Predictor(htfadd567, estmaxsbd)  
    Predictor(htfadd568, estminsbu)
    Predictor(htfadd568, estmaxsbd)  
    Predictor(htfadd569, estminsbu)
    Predictor(htfadd569, estmaxsbd)  
    Predictor(htfadd570, estminsbu)
    Predictor(htfadd570, estmaxsbd)  
    Predictor(htfadd571, estminsbu)
    Predictor(htfadd571, estmaxsbd)  
    Predictor(htfadd572, estminsbu)
    Predictor(htfadd572, estmaxsbd)  
    Predictor(htfadd573, estminsbu)
    Predictor(htfadd573, estmaxsbd)  
    Predictor(htfadd574, estminsbu)
    Predictor(htfadd574, estmaxsbd)  
    Predictor(htfadd575, estminsbu)
    Predictor(htfadd575, estmaxsbd)  
    Predictor(htfadd576, estminsbu)
    Predictor(htfadd576, estmaxsbd)  
    Predictor(htfadd577, estminsbu)
    Predictor(htfadd577, estmaxsbd)  
    Predictor(htfadd578, estminsbu)
    Predictor(htfadd578, estmaxsbd)  
    Predictor(htfadd579, estminsbu)
    Predictor(htfadd579, estmaxsbd)  
    Predictor(htfadd580, estminsbu)
    Predictor(htfadd580, estmaxsbd)  
    Predictor(htfadd581, estminsbu)
    Predictor(htfadd581, estmaxsbd)  
    Predictor(htfadd582, estminsbu)
    Predictor(htfadd582, estmaxsbd)  
    Predictor(htfadd583, estminsbu)
    Predictor(htfadd583, estmaxsbd)  
    Predictor(htfadd584, estminsbu)
    Predictor(htfadd584, estmaxsbd)  
    Predictor(htfadd585, estminsbu)
    Predictor(htfadd585, estmaxsbd)  
    Predictor(htfadd586, estminsbu)
    Predictor(htfadd586, estmaxsbd)  
    Predictor(htfadd587, estminsbu)
    Predictor(htfadd587, estmaxsbd)  
    Predictor(htfadd588, estminsbu)
    Predictor(htfadd588, estmaxsbd)  
    Predictor(htfadd589, estminsbu)
    Predictor(htfadd589, estmaxsbd)  
    Predictor(htfadd590, estminsbu)
    Predictor(htfadd590, estmaxsbd)  
    Predictor(htfadd591, estminsbu)
    Predictor(htfadd591, estmaxsbd)  
    Predictor(htfadd592, estminsbu)
    Predictor(htfadd592, estmaxsbd)  
    Predictor(htfadd593, estminsbu)
    Predictor(htfadd593, estmaxsbd)  
    Predictor(htfadd594, estminsbu)
    Predictor(htfadd594, estmaxsbd)  
    Predictor(htfadd595, estminsbu)
    Predictor(htfadd595, estmaxsbd)  
    Predictor(htfadd596, estminsbu)
    Predictor(htfadd596, estmaxsbd)  
    Predictor(htfadd597, estminsbu)
    Predictor(htfadd597, estmaxsbd)  
    Predictor(htfadd598, estminsbu)
    Predictor(htfadd598, estmaxsbd)  
    Predictor(htfadd599, estminsbu)
    Predictor(htfadd599, estmaxsbd)  
    Predictor(htfadd600, estminsbu)
    Predictor(htfadd600, estmaxsbd)  
    Predictor(htfadd601, estminsbu)
    Predictor(htfadd601, estmaxsbd)  
    Predictor(htfadd602, estminsbu)
    Predictor(htfadd602, estmaxsbd)  
    Predictor(htfadd603, estminsbu)
    Predictor(htfadd603, estmaxsbd)  
    Predictor(htfadd604, estminsbu)
    Predictor(htfadd604, estmaxsbd)  
    Predictor(htfadd605, estminsbu)
    Predictor(htfadd605, estmaxsbd)  
    Predictor(htfadd606, estminsbu)
    Predictor(htfadd606, estmaxsbd)  
    Predictor(htfadd607, estminsbu)
    Predictor(htfadd607, estmaxsbd)  
    Predictor(htfadd608, estminsbu)
    Predictor(htfadd608, estmaxsbd)  
    Predictor(htfadd609, estminsbu)
    Predictor(htfadd609, estmaxsbd)  
    Predictor(htfadd610, estminsbu)
    Predictor(htfadd610, estmaxsbd)  
    Predictor(htfadd611, estminsbu)
    Predictor(htfadd611, estmaxsbd)  
    Predictor(htfadd612, estminsbu)
    Predictor(htfadd612, estmaxsbd)  
    Predictor(htfadd613, estminsbu)
    Predictor(htfadd613, estmaxsbd)  
    Predictor(htfadd614, estminsbu)
    Predictor(htfadd614, estmaxsbd)  
    Predictor(htfadd615, estminsbu)
    Predictor(htfadd615, estmaxsbd)  
    Predictor(htfadd616, estminsbu)
    Predictor(htfadd616, estmaxsbd)  
    Predictor(htfadd617, estminsbu)
    Predictor(htfadd617, estmaxsbd)  
    Predictor(htfadd618, estminsbu)
    Predictor(htfadd618, estmaxsbd)  
    Predictor(htfadd619, estminsbu)
    Predictor(htfadd619, estmaxsbd)  
    Predictor(htfadd620, estminsbu)
    Predictor(htfadd620, estmaxsbd)  
    Predictor(htfadd621, estminsbu)
    Predictor(htfadd621, estmaxsbd)  
    Predictor(htfadd622, estminsbu)
    Predictor(htfadd622, estmaxsbd)  
    Predictor(htfadd623, estminsbu)
    Predictor(htfadd623, estmaxsbd)  
    Predictor(htfadd624, estminsbu)
    Predictor(htfadd624, estmaxsbd)  
    Predictor(htfadd625, estminsbu)
    Predictor(htfadd625, estmaxsbd)  
    Predictor(htfadd626, estminsbu)
    Predictor(htfadd626, estmaxsbd)  
    Predictor(htfadd627, estminsbu)
    Predictor(htfadd627, estmaxsbd)  
    Predictor(htfadd628, estminsbu)
    Predictor(htfadd628, estmaxsbd)  
    Predictor(htfadd629, estminsbu)
    Predictor(htfadd629, estmaxsbd)  
    Predictor(htfadd630, estminsbu)
    Predictor(htfadd630, estmaxsbd)  
    Predictor(htfadd631, estminsbu)
    Predictor(htfadd631, estmaxsbd)  
    Predictor(htfadd632, estminsbu)
    Predictor(htfadd632, estmaxsbd)  
    Predictor(htfadd633, estminsbu)
    Predictor(htfadd633, estmaxsbd)  
    Predictor(htfadd634, estminsbu)
    Predictor(htfadd634, estmaxsbd)  
    Predictor(htfadd635, estminsbu)
    Predictor(htfadd635, estmaxsbd)  
    Predictor(htfadd636, estminsbu)
    Predictor(htfadd636, estmaxsbd)  
    Predictor(htfadd637, estminsbu)
    Predictor(htfadd637, estmaxsbd)  
    Predictor(htfadd638, estminsbu)
    Predictor(htfadd638, estmaxsbd)  
    Predictor(htfadd639, estminsbu)
    Predictor(htfadd639, estmaxsbd)  
    Predictor(htfadd640, estminsbu)
    Predictor(htfadd640, estmaxsbd)  
    Predictor(htfadd641, estminsbu)
    Predictor(htfadd641, estmaxsbd)  
    Predictor(htfadd642, estminsbu)
    Predictor(htfadd642, estmaxsbd)  
    Predictor(htfadd643, estminsbu)
    Predictor(htfadd643, estmaxsbd)  
    Predictor(htfadd644, estminsbu)
    Predictor(htfadd644, estmaxsbd)  
    Predictor(htfadd645, estminsbu)
    Predictor(htfadd645, estmaxsbd)  
    Predictor(htfadd646, estminsbu)
    Predictor(htfadd646, estmaxsbd)  
    Predictor(htfadd647, estminsbu)
    Predictor(htfadd647, estmaxsbd)  
    Predictor(htfadd648, estminsbu)
    Predictor(htfadd648, estmaxsbd)  
    Predictor(htfadd649, estminsbu)
    Predictor(htfadd649, estmaxsbd)  
    Predictor(htfadd650, estminsbu)
    Predictor(htfadd650, estmaxsbd)  
    Predictor(htfadd651, estminsbu)
    Predictor(htfadd651, estmaxsbd)  
    Predictor(htfadd652, estminsbu)
    Predictor(htfadd652, estmaxsbd)  
    Predictor(htfadd653, estminsbu)
    Predictor(htfadd653, estmaxsbd)  
    Predictor(htfadd654, estminsbu)
    Predictor(htfadd654, estmaxsbd)  
    Predictor(htfadd655, estminsbu)
    Predictor(htfadd655, estmaxsbd)  
    Predictor(htfadd656, estminsbu)
    Predictor(htfadd656, estmaxsbd)  
    Predictor(htfadd657, estminsbu)
    Predictor(htfadd657, estmaxsbd)  
    Predictor(htfadd658, estminsbu)
    Predictor(htfadd658, estmaxsbd)  
    Predictor(htfadd659, estminsbu)
    Predictor(htfadd659, estmaxsbd)  
    Predictor(htfadd660, estminsbu)
    Predictor(htfadd660, estmaxsbd)  
    Predictor(htfadd661, estminsbu)
    Predictor(htfadd661, estmaxsbd)  
    Predictor(htfadd662, estminsbu)
    Predictor(htfadd662, estmaxsbd)  
    Predictor(htfadd663, estminsbu)
    Predictor(htfadd663, estmaxsbd)  
    Predictor(htfadd664, estminsbu)
    Predictor(htfadd664, estmaxsbd)  
    Predictor(htfadd665, estminsbu)
    Predictor(htfadd665, estmaxsbd)  
    Predictor(htfadd666, estminsbu)
    Predictor(htfadd666, estmaxsbd)  
    Predictor(htfadd667, estminsbu)
    Predictor(htfadd667, estmaxsbd)  
    Predictor(htfadd668, estminsbu)
    Predictor(htfadd668, estmaxsbd)  
    Predictor(htfadd669, estminsbu)
    Predictor(htfadd669, estmaxsbd)  
    Predictor(htfadd670, estminsbu)
    Predictor(htfadd670, estmaxsbd)  
    Predictor(htfadd671, estminsbu)
    Predictor(htfadd671, estmaxsbd)  
    Predictor(htfadd672, estminsbu)
    Predictor(htfadd672, estmaxsbd)  
    Predictor(htfadd673, estminsbu)
    Predictor(htfadd673, estmaxsbd)  
    Predictor(htfadd674, estminsbu)
    Predictor(htfadd674, estmaxsbd)  
    Predictor(htfadd675, estminsbu)
    Predictor(htfadd675, estmaxsbd)  
    Predictor(htfadd676, estminsbu)
    Predictor(htfadd676, estmaxsbd)  
    Predictor(htfadd677, estminsbu)
    Predictor(htfadd677, estmaxsbd)  
    Predictor(htfadd678, estminsbu)
    Predictor(htfadd678, estmaxsbd)  
    Predictor(htfadd679, estminsbu)
    Predictor(htfadd679, estmaxsbd)  
    Predictor(htfadd680, estminsbu)
    Predictor(htfadd680, estmaxsbd)  
    Predictor(htfadd681, estminsbu)
    Predictor(htfadd681, estmaxsbd)  
    Predictor(htfadd682, estminsbu)
    Predictor(htfadd682, estmaxsbd)  
    Predictor(htfadd683, estminsbu)
    Predictor(htfadd683, estmaxsbd)  
    Predictor(htfadd684, estminsbu)
    Predictor(htfadd684, estmaxsbd)  
    Predictor(htfadd685, estminsbu)
    Predictor(htfadd685, estmaxsbd)  
    Predictor(htfadd686, estminsbu)
    Predictor(htfadd686, estmaxsbd)  
    Predictor(htfadd687, estminsbu)
    Predictor(htfadd687, estmaxsbd)  
    Predictor(htfadd688, estminsbu)
    Predictor(htfadd688, estmaxsbd)  
    Predictor(htfadd689, estminsbu)
    Predictor(htfadd689, estmaxsbd)  
    Predictor(htfadd690, estminsbu)
    Predictor(htfadd690, estmaxsbd)  
    Predictor(htfadd691, estminsbu)
    Predictor(htfadd691, estmaxsbd)  
    Predictor(htfadd692, estminsbu)
    Predictor(htfadd692, estmaxsbd)  
    Predictor(htfadd693, estminsbu)
    Predictor(htfadd693, estmaxsbd)  
    Predictor(htfadd694, estminsbu)
    Predictor(htfadd694, estmaxsbd)  
    Predictor(htfadd695, estminsbu)
    Predictor(htfadd695, estmaxsbd)  
    Predictor(htfadd696, estminsbu)
    Predictor(htfadd696, estmaxsbd)  
    Predictor(htfadd697, estminsbu)
    Predictor(htfadd697, estmaxsbd)  
    Predictor(htfadd698, estminsbu)
    Predictor(htfadd698, estmaxsbd)  
    Predictor(htfadd699, estminsbu)
    Predictor(htfadd699, estmaxsbd)  
    Predictor(htfadd700, estminsbu)
    Predictor(htfadd700, estmaxsbd)  
    Predictor(htfadd701, estminsbu)
    Predictor(htfadd701, estmaxsbd)  
    Predictor(htfadd702, estminsbu)
    Predictor(htfadd702, estmaxsbd)  
    Predictor(htfadd703, estminsbu)
    Predictor(htfadd703, estmaxsbd)  
    Predictor(htfadd704, estminsbu)
    Predictor(htfadd704, estmaxsbd)  
    Predictor(htfadd705, estminsbu)
    Predictor(htfadd705, estmaxsbd)  
    Predictor(htfadd706, estminsbu)
    Predictor(htfadd706, estmaxsbd)  
    Predictor(htfadd707, estminsbu)
    Predictor(htfadd707, estmaxsbd)  
    Predictor(htfadd708, estminsbu)
    Predictor(htfadd708, estmaxsbd)  
    Predictor(htfadd709, estminsbu)
    Predictor(htfadd709, estmaxsbd)  
    Predictor(htfadd710, estminsbu)
    Predictor(htfadd710, estmaxsbd)  
    Predictor(htfadd711, estminsbu)
    Predictor(htfadd711, estmaxsbd)  
    Predictor(htfadd712, estminsbu)
    Predictor(htfadd712, estmaxsbd)  
    Predictor(htfadd713, estminsbu)
    Predictor(htfadd713, estmaxsbd)  
    Predictor(htfadd714, estminsbu)
    Predictor(htfadd714, estmaxsbd)  
    Predictor(htfadd715, estminsbu)
    Predictor(htfadd715, estmaxsbd)  
    Predictor(htfadd716, estminsbu)
    Predictor(htfadd716, estmaxsbd)  
    Predictor(htfadd717, estminsbu)
    Predictor(htfadd717, estmaxsbd)  
    Predictor(htfadd718, estminsbu)
    Predictor(htfadd718, estmaxsbd)  
    Predictor(htfadd719, estminsbu)
    Predictor(htfadd719, estmaxsbd)  
    Predictor(htfadd720, estminsbu)
    Predictor(htfadd720, estmaxsbd)  
    Predictor(htfadd721, estminsbu)
    Predictor(htfadd721, estmaxsbd)  
    Predictor(htfadd722, estminsbu)
    Predictor(htfadd722, estmaxsbd)  
    Predictor(htfadd723, estminsbu)
    Predictor(htfadd723, estmaxsbd)  
    Predictor(htfadd724, estminsbu)
    Predictor(htfadd724, estmaxsbd)  
    Predictor(htfadd725, estminsbu)
    Predictor(htfadd725, estmaxsbd)  
    Predictor(htfadd726, estminsbu)
    Predictor(htfadd726, estmaxsbd)  
    Predictor(htfadd727, estminsbu)
    Predictor(htfadd727, estmaxsbd)  
    Predictor(htfadd728, estminsbu)
    Predictor(htfadd728, estmaxsbd)  
    Predictor(htfadd729, estminsbu)
    Predictor(htfadd729, estmaxsbd)  
    Predictor(htfadd730, estminsbu)
    Predictor(htfadd730, estmaxsbd)  
    Predictor(htfadd731, estminsbu)
    Predictor(htfadd731, estmaxsbd)  
    Predictor(htfadd732, estminsbu)
    Predictor(htfadd732, estmaxsbd)  
    Predictor(htfadd733, estminsbu)
    Predictor(htfadd733, estmaxsbd)  
    Predictor(htfadd734, estminsbu)
    Predictor(htfadd734, estmaxsbd)  
    Predictor(htfadd735, estminsbu)
    Predictor(htfadd735, estmaxsbd)  
    Predictor(htfadd736, estminsbu)
    Predictor(htfadd736, estmaxsbd)  
    Predictor(htfadd737, estminsbu)
    Predictor(htfadd737, estmaxsbd)  
    Predictor(htfadd738, estminsbu)
    Predictor(htfadd738, estmaxsbd)  
    Predictor(htfadd739, estminsbu)
    Predictor(htfadd739, estmaxsbd)  
    Predictor(htfadd740, estminsbu)
    Predictor(htfadd740, estmaxsbd)  
    Predictor(htfadd741, estminsbu)
    Predictor(htfadd741, estmaxsbd)  
    Predictor(htfadd742, estminsbu)
    Predictor(htfadd742, estmaxsbd)  
    Predictor(htfadd743, estminsbu)
    Predictor(htfadd743, estmaxsbd)  
    Predictor(htfadd744, estminsbu)
    Predictor(htfadd744, estmaxsbd)  
    Predictor(htfadd745, estminsbu)
    Predictor(htfadd745, estmaxsbd)  
    Predictor(htfadd746, estminsbu)
    Predictor(htfadd746, estmaxsbd)  
    Predictor(htfadd747, estminsbu)
    Predictor(htfadd747, estmaxsbd)  
    Predictor(htfadd748, estminsbu)
    Predictor(htfadd748, estmaxsbd)  
    Predictor(htfadd749, estminsbu)
    Predictor(htfadd749, estmaxsbd)  
    Predictor(htfadd750, estminsbu)
    Predictor(htfadd750, estmaxsbd)  
    Predictor(htfadd751, estminsbu)
    Predictor(htfadd751, estmaxsbd)  
    Predictor(htfadd752, estminsbu)
    Predictor(htfadd752, estmaxsbd)  
    Predictor(htfadd753, estminsbu)
    Predictor(htfadd753, estmaxsbd)  
    Predictor(htfadd754, estminsbu)
    Predictor(htfadd754, estmaxsbd)  
    Predictor(htfadd755, estminsbu)
    Predictor(htfadd755, estmaxsbd)  
    Predictor(htfadd756, estminsbu)
    Predictor(htfadd756, estmaxsbd)  
    Predictor(htfadd757, estminsbu)
    Predictor(htfadd757, estmaxsbd)  
    Predictor(htfadd758, estminsbu)
    Predictor(htfadd758, estmaxsbd)  
    Predictor(htfadd759, estminsbu)
    Predictor(htfadd759, estmaxsbd)  
    Predictor(htfadd760, estminsbu)
    Predictor(htfadd760, estmaxsbd)  
    Predictor(htfadd761, estminsbu)
    Predictor(htfadd761, estmaxsbd)  
    Predictor(htfadd762, estminsbu)
    Predictor(htfadd762, estmaxsbd)  
    Predictor(htfadd763, estminsbu)
    Predictor(htfadd763, estmaxsbd)  
    Predictor(htfadd764, estminsbu)
    Predictor(htfadd764, estmaxsbd)  
    Predictor(htfadd765, estminsbu)
    Predictor(htfadd765, estmaxsbd)  
    Predictor(htfadd766, estminsbu)
    Predictor(htfadd766, estmaxsbd)  
    Predictor(htfadd767, estminsbu)
    Predictor(htfadd767, estmaxsbd)  
    Predictor(htfadd768, estminsbu)
    Predictor(htfadd768, estmaxsbd)  
    Predictor(htfadd769, estminsbu)
    Predictor(htfadd769, estmaxsbd)  
    Predictor(htfadd770, estminsbu)
    Predictor(htfadd770, estmaxsbd)  
    Predictor(htfadd771, estminsbu)
    Predictor(htfadd771, estmaxsbd)  
    Predictor(htfadd772, estminsbu)
    Predictor(htfadd772, estmaxsbd)  
    Predictor(htfadd773, estminsbu)
    Predictor(htfadd773, estmaxsbd)  
    Predictor(htfadd774, estminsbu)
    Predictor(htfadd774, estmaxsbd)  
    Predictor(htfadd775, estminsbu)
    Predictor(htfadd775, estmaxsbd)  
    Predictor(htfadd776, estminsbu)
    Predictor(htfadd776, estmaxsbd)  
    Predictor(htfadd777, estminsbu)
    Predictor(htfadd777, estmaxsbd)  
    Predictor(htfadd778, estminsbu)
    Predictor(htfadd778, estmaxsbd)  
    Predictor(htfadd779, estminsbu)
    Predictor(htfadd779, estmaxsbd)  
    Predictor(htfadd780, estminsbu)
    Predictor(htfadd780, estmaxsbd)  
    Predictor(htfadd781, estminsbu)
    Predictor(htfadd781, estmaxsbd)  
    Predictor(htfadd782, estminsbu)
    Predictor(htfadd782, estmaxsbd)  
    Predictor(htfadd783, estminsbu)
    Predictor(htfadd783, estmaxsbd)  
    Predictor(htfadd784, estminsbu)
    Predictor(htfadd784, estmaxsbd)  
    Predictor(htfadd785, estminsbu)
    Predictor(htfadd785, estmaxsbd)  
    Predictor(htfadd786, estminsbu)
    Predictor(htfadd786, estmaxsbd)  
    Predictor(htfadd787, estminsbu)
    Predictor(htfadd787, estmaxsbd)  
    Predictor(htfadd788, estminsbu)
    Predictor(htfadd788, estmaxsbd)  
    Predictor(htfadd789, estminsbu)
    Predictor(htfadd789, estmaxsbd)  
    Predictor(htfadd790, estminsbu)
    Predictor(htfadd790, estmaxsbd)  
    Predictor(htfadd791, estminsbu)
    Predictor(htfadd791, estmaxsbd)  
    Predictor(htfadd792, estminsbu)
    Predictor(htfadd792, estmaxsbd)  
    Predictor(htfadd793, estminsbu)
    Predictor(htfadd793, estmaxsbd)  
    Predictor(htfadd794, estminsbu)
    Predictor(htfadd794, estmaxsbd)  
    Predictor(htfadd795, estminsbu)
    Predictor(htfadd795, estmaxsbd)  
    Predictor(htfadd796, estminsbu)
    Predictor(htfadd796, estmaxsbd)  
    Predictor(htfadd797, estminsbu)
    Predictor(htfadd797, estmaxsbd)  
    Predictor(htfadd798, estminsbu)
    Predictor(htfadd798, estmaxsbd)  
    Predictor(htfadd799, estminsbu)
    Predictor(htfadd799, estmaxsbd)  
    Predictor(htfadd800, estminsbu)
    Predictor(htfadd800, estmaxsbd)  
    Predictor(htfadd801, estminsbu)
    Predictor(htfadd801, estmaxsbd)  
    Predictor(htfadd802, estminsbu)
    Predictor(htfadd802, estmaxsbd)  
    Predictor(htfadd803, estminsbu)
    Predictor(htfadd803, estmaxsbd)  
    Predictor(htfadd804, estminsbu)
    Predictor(htfadd804, estmaxsbd)  
    Predictor(htfadd805, estminsbu)
    Predictor(htfadd805, estmaxsbd)  
    Predictor(htfadd806, estminsbu)
    Predictor(htfadd806, estmaxsbd)  
    Predictor(htfadd807, estminsbu)
    Predictor(htfadd807, estmaxsbd)  
    Predictor(htfadd808, estminsbu)
    Predictor(htfadd808, estmaxsbd)  
    Predictor(htfadd809, estminsbu)
    Predictor(htfadd809, estmaxsbd)  
    Predictor(htfadd810, estminsbu)
    Predictor(htfadd810, estmaxsbd)  
    Predictor(htfadd811, estminsbu)
    Predictor(htfadd811, estmaxsbd)  
    Predictor(htfadd812, estminsbu)
    Predictor(htfadd812, estmaxsbd)  
    Predictor(htfadd813, estminsbu)
    Predictor(htfadd813, estmaxsbd)  
    Predictor(htfadd814, estminsbu)
    Predictor(htfadd814, estmaxsbd)  
    Predictor(htfadd815, estminsbu)
    Predictor(htfadd815, estmaxsbd)  
    Predictor(htfadd816, estminsbu)
    Predictor(htfadd816, estmaxsbd)  
    Predictor(htfadd817, estminsbu)
    Predictor(htfadd817, estmaxsbd)  
    Predictor(htfadd818, estminsbu)
    Predictor(htfadd818, estmaxsbd)  
    Predictor(htfadd819, estminsbu)
    Predictor(htfadd819, estmaxsbd)  
    Predictor(htfadd820, estminsbu)
    Predictor(htfadd820, estmaxsbd)  
    Predictor(htfadd821, estminsbu)
    Predictor(htfadd821, estmaxsbd)  
    Predictor(htfadd822, estminsbu)
    Predictor(htfadd822, estmaxsbd)  
    Predictor(htfadd823, estminsbu)
    Predictor(htfadd823, estmaxsbd)  
    Predictor(htfadd824, estminsbu)
    Predictor(htfadd824, estmaxsbd)  
    Predictor(htfadd825, estminsbu)
    Predictor(htfadd825, estmaxsbd)  
    Predictor(htfadd826, estminsbu)
    Predictor(htfadd826, estmaxsbd)  
    Predictor(htfadd827, estminsbu)
    Predictor(htfadd827, estmaxsbd)  
    Predictor(htfadd828, estminsbu)
    Predictor(htfadd828, estmaxsbd)  
    Predictor(htfadd829, estminsbu)
    Predictor(htfadd829, estmaxsbd)  
    Predictor(htfadd830, estminsbu)
    Predictor(htfadd830, estmaxsbd)  
    Predictor(htfadd831, estminsbu)
    Predictor(htfadd831, estmaxsbd)  
    Predictor(htfadd832, estminsbu)
    Predictor(htfadd832, estmaxsbd)  
    Predictor(htfadd833, estminsbu)
    Predictor(htfadd833, estmaxsbd)  
    Predictor(htfadd834, estminsbu)
    Predictor(htfadd834, estmaxsbd)  
    Predictor(htfadd835, estminsbu)
    Predictor(htfadd835, estmaxsbd)  
    Predictor(htfadd836, estminsbu)
    Predictor(htfadd836, estmaxsbd)  
    Predictor(htfadd837, estminsbu)
    Predictor(htfadd837, estmaxsbd)  
    Predictor(htfadd838, estminsbu)
    Predictor(htfadd838, estmaxsbd)  
    Predictor(htfadd839, estminsbu)
    Predictor(htfadd839, estmaxsbd)  
    Predictor(htfadd840, estminsbu)
    Predictor(htfadd840, estmaxsbd)  
    Predictor(htfadd841, estminsbu)
    Predictor(htfadd841, estmaxsbd)  
    Predictor(htfadd842, estminsbu)
    Predictor(htfadd842, estmaxsbd)  
    Predictor(htfadd843, estminsbu)
    Predictor(htfadd843, estmaxsbd)  
    Predictor(htfadd844, estminsbu)
    Predictor(htfadd844, estmaxsbd)  
    Predictor(htfadd845, estminsbu)
    Predictor(htfadd845, estmaxsbd)  
    Predictor(htfadd846, estminsbu)
    Predictor(htfadd846, estmaxsbd)  
    Predictor(htfadd847, estminsbu)
    Predictor(htfadd847, estmaxsbd)  
    Predictor(htfadd848, estminsbu)
    Predictor(htfadd848, estmaxsbd)  
    Predictor(htfadd849, estminsbu)
    Predictor(htfadd849, estmaxsbd)  
    Predictor(htfadd850, estminsbu)
    Predictor(htfadd850, estmaxsbd)  
    Predictor(htfadd851, estminsbu)
    Predictor(htfadd851, estmaxsbd)  
    Predictor(htfadd852, estminsbu)
    Predictor(htfadd852, estmaxsbd)  
    Predictor(htfadd853, estminsbu)
    Predictor(htfadd853, estmaxsbd)  
    Predictor(htfadd854, estminsbu)
    Predictor(htfadd854, estmaxsbd)  
    Predictor(htfadd855, estminsbu)
    Predictor(htfadd855, estmaxsbd)  
    Predictor(htfadd856, estminsbu)
    Predictor(htfadd856, estmaxsbd)  
    Predictor(htfadd857, estminsbu)
    Predictor(htfadd857, estmaxsbd)  
    Predictor(htfadd858, estminsbu)
    Predictor(htfadd858, estmaxsbd)  
    Predictor(htfadd859, estminsbu)
    Predictor(htfadd859, estmaxsbd)  
    Predictor(htfadd860, estminsbu)
    Predictor(htfadd860, estmaxsbd)  
    Predictor(htfadd861, estminsbu)
    Predictor(htfadd861, estmaxsbd)  
    Predictor(htfadd862, estminsbu)
    Predictor(htfadd862, estmaxsbd)  
    Predictor(htfadd863, estminsbu)
    Predictor(htfadd863, estmaxsbd)  
    Predictor(htfadd864, estminsbu)
    Predictor(htfadd864, estmaxsbd)  
    Predictor(htfadd865, estminsbu)
    Predictor(htfadd865, estmaxsbd)  
    Predictor(htfadd866, estminsbu)
    Predictor(htfadd866, estmaxsbd)  
    Predictor(htfadd867, estminsbu)
    Predictor(htfadd867, estmaxsbd)  
    Predictor(htfadd868, estminsbu)
    Predictor(htfadd868, estmaxsbd)  
    Predictor(htfadd869, estminsbu)
    Predictor(htfadd869, estmaxsbd)  
    Predictor(htfadd870, estminsbu)
    Predictor(htfadd870, estmaxsbd)  
    Predictor(htfadd871, estminsbu)
    Predictor(htfadd871, estmaxsbd)  
    Predictor(htfadd872, estminsbu)
    Predictor(htfadd872, estmaxsbd)  
    Predictor(htfadd873, estminsbu)
    Predictor(htfadd873, estmaxsbd)  
    Predictor(htfadd874, estminsbu)
    Predictor(htfadd874, estmaxsbd)  
    Predictor(htfadd875, estminsbu)
    Predictor(htfadd875, estmaxsbd)  
    Predictor(htfadd876, estminsbu)
    Predictor(htfadd876, estmaxsbd)  
    Predictor(htfadd877, estminsbu)
    Predictor(htfadd877, estmaxsbd)  
    Predictor(htfadd878, estminsbu)
    Predictor(htfadd878, estmaxsbd)  
    Predictor(htfadd879, estminsbu)
    Predictor(htfadd879, estmaxsbd)  
    Predictor(htfadd880, estminsbu)
    Predictor(htfadd880, estmaxsbd)  
    Predictor(htfadd881, estminsbu)
    Predictor(htfadd881, estmaxsbd)  
    Predictor(htfadd882, estminsbu)
    Predictor(htfadd882, estmaxsbd)  
    Predictor(htfadd883, estminsbu)
    Predictor(htfadd883, estmaxsbd)  
    Predictor(htfadd884, estminsbu)
    Predictor(htfadd884, estmaxsbd)  
    Predictor(htfadd885, estminsbu)
    Predictor(htfadd885, estmaxsbd)  
    Predictor(htfadd886, estminsbu)
    Predictor(htfadd886, estmaxsbd)  
    Predictor(htfadd887, estminsbu)
    Predictor(htfadd887, estmaxsbd)  
    Predictor(htfadd888, estminsbu)
    Predictor(htfadd888, estmaxsbd)  
    Predictor(htfadd889, estminsbu)
    Predictor(htfadd889, estmaxsbd)  
    Predictor(htfadd890, estminsbu)
    Predictor(htfadd890, estmaxsbd)  
    Predictor(htfadd891, estminsbu)
    Predictor(htfadd891, estmaxsbd)  
    Predictor(htfadd892, estminsbu)
    Predictor(htfadd892, estmaxsbd)  
    Predictor(htfadd893, estminsbu)
    Predictor(htfadd893, estmaxsbd)  
    Predictor(htfadd894, estminsbu)
    Predictor(htfadd894, estmaxsbd)  
    Predictor(htfadd895, estminsbu)
    Predictor(htfadd895, estmaxsbd)  
    Predictor(htfadd896, estminsbu)
    Predictor(htfadd896, estmaxsbd)  
    Predictor(htfadd897, estminsbu)
    Predictor(htfadd897, estmaxsbd)  
    Predictor(htfadd898, estminsbu)
    Predictor(htfadd898, estmaxsbd)  
    Predictor(htfadd899, estminsbu)
    Predictor(htfadd899, estmaxsbd)  
    Predictor(htfadd900, estminsbu)
    Predictor(htfadd900, estmaxsbd)  
    Predictor(htfadd901, estminsbu)
    Predictor(htfadd901, estmaxsbd)  
    Predictor(htfadd902, estminsbu)
    Predictor(htfadd902, estmaxsbd)  
    Predictor(htfadd903, estminsbu)
    Predictor(htfadd903, estmaxsbd)  
    Predictor(htfadd904, estminsbu)
    Predictor(htfadd904, estmaxsbd)  
    Predictor(htfadd905, estminsbu)
    Predictor(htfadd905, estmaxsbd)  
    Predictor(htfadd906, estminsbu)
    Predictor(htfadd906, estmaxsbd)  
    Predictor(htfadd907, estminsbu)
    Predictor(htfadd907, estmaxsbd)  
    Predictor(htfadd908, estminsbu)
    Predictor(htfadd908, estmaxsbd)  
    Predictor(htfadd909, estminsbu)
    Predictor(htfadd909, estmaxsbd)  
    Predictor(htfadd910, estminsbu)
    Predictor(htfadd910, estmaxsbd)  
    Predictor(htfadd911, estminsbu)
    Predictor(htfadd911, estmaxsbd)  
    Predictor(htfadd912, estminsbu)
    Predictor(htfadd912, estmaxsbd)  
    Predictor(htfadd913, estminsbu)
    Predictor(htfadd913, estmaxsbd)  
    Predictor(htfadd914, estminsbu)
    Predictor(htfadd914, estmaxsbd)  
    Predictor(htfadd915, estminsbu)
    Predictor(htfadd915, estmaxsbd)  
    Predictor(htfadd916, estminsbu)
    Predictor(htfadd916, estmaxsbd)  
    Predictor(htfadd917, estminsbu)
    Predictor(htfadd917, estmaxsbd)  
    Predictor(htfadd918, estminsbu)
    Predictor(htfadd918, estmaxsbd)  
    Predictor(htfadd919, estminsbu)
    Predictor(htfadd919, estmaxsbd)  
    Predictor(htfadd920, estminsbu)
    Predictor(htfadd920, estmaxsbd)  
    Predictor(htfadd921, estminsbu)
    Predictor(htfadd921, estmaxsbd)  
    Predictor(htfadd922, estminsbu)
    Predictor(htfadd922, estmaxsbd)  
    Predictor(htfadd923, estminsbu)
    Predictor(htfadd923, estmaxsbd)  
    Predictor(htfadd924, estminsbu)
    Predictor(htfadd924, estmaxsbd)  
    Predictor(htfadd925, estminsbu)
    Predictor(htfadd925, estmaxsbd)  
    Predictor(htfadd926, estminsbu)
    Predictor(htfadd926, estmaxsbd)  
    Predictor(htfadd927, estminsbu)
    Predictor(htfadd927, estmaxsbd)  
    Predictor(htfadd928, estminsbu)
    Predictor(htfadd928, estmaxsbd)  
    Predictor(htfadd929, estminsbu)
    Predictor(htfadd929, estmaxsbd)  
    Predictor(htfadd930, estminsbu)
    Predictor(htfadd930, estmaxsbd)  
    Predictor(htfadd931, estminsbu)
    Predictor(htfadd931, estmaxsbd)  
    Predictor(htfadd932, estminsbu)
    Predictor(htfadd932, estmaxsbd)  
    Predictor(htfadd933, estminsbu)
    Predictor(htfadd933, estmaxsbd)  
    Predictor(htfadd934, estminsbu)
    Predictor(htfadd934, estmaxsbd)  
    Predictor(htfadd935, estminsbu)
    Predictor(htfadd935, estmaxsbd)  
    Predictor(htfadd936, estminsbu)
    Predictor(htfadd936, estmaxsbd)  
    Predictor(htfadd937, estminsbu)
    Predictor(htfadd937, estmaxsbd)  
    Predictor(htfadd938, estminsbu)
    Predictor(htfadd938, estmaxsbd)  
    Predictor(htfadd939, estminsbu)
    Predictor(htfadd939, estmaxsbd)  
    Predictor(htfadd940, estminsbu)
    Predictor(htfadd940, estmaxsbd)  
    Predictor(htfadd941, estminsbu)
    Predictor(htfadd941, estmaxsbd)  
    Predictor(htfadd942, estminsbu)
    Predictor(htfadd942, estmaxsbd)  
    Predictor(htfadd943, estminsbu)
    Predictor(htfadd943, estmaxsbd)  
    Predictor(htfadd944, estminsbu)
    Predictor(htfadd944, estmaxsbd)  
    Predictor(htfadd945, estminsbu)
    Predictor(htfadd945, estmaxsbd)  
    Predictor(htfadd946, estminsbu)
    Predictor(htfadd946, estmaxsbd)  
    Predictor(htfadd947, estminsbu)
    Predictor(htfadd947, estmaxsbd)  
    Predictor(htfadd948, estminsbu)
    Predictor(htfadd948, estmaxsbd)  
    Predictor(htfadd949, estminsbu)
    Predictor(htfadd949, estmaxsbd)  
    Predictor(htfadd950, estminsbu)
    Predictor(htfadd950, estmaxsbd)  
    Predictor(htfadd951, estminsbu)
    Predictor(htfadd951, estmaxsbd)  
    Predictor(htfadd952, estminsbu)
    Predictor(htfadd952, estmaxsbd)  
    Predictor(htfadd953, estminsbu)
    Predictor(htfadd953, estmaxsbd)  
    Predictor(htfadd954, estminsbu)
    Predictor(htfadd954, estmaxsbd)  
    Predictor(htfadd955, estminsbu)
    Predictor(htfadd955, estmaxsbd)  
    Predictor(htfadd956, estminsbu)
    Predictor(htfadd956, estmaxsbd)  
    Predictor(htfadd957, estminsbu)
    Predictor(htfadd957, estmaxsbd)  
    Predictor(htfadd958, estminsbu)
    Predictor(htfadd958, estmaxsbd)  
    Predictor(htfadd959, estminsbu)
    Predictor(htfadd959, estmaxsbd)  
    Predictor(htfadd960, estminsbu)
    Predictor(htfadd960, estmaxsbd)  
    Predictor(htfadd961, estminsbu)
    Predictor(htfadd961, estmaxsbd)  
    Predictor(htfadd962, estminsbu)
    Predictor(htfadd962, estmaxsbd)  
    Predictor(htfadd963, estminsbu)
    Predictor(htfadd963, estmaxsbd)  
    Predictor(htfadd964, estminsbu)
    Predictor(htfadd964, estmaxsbd)  
    Predictor(htfadd965, estminsbu)
    Predictor(htfadd965, estmaxsbd)  
    Predictor(htfadd966, estminsbu)
    Predictor(htfadd966, estmaxsbd)  
    Predictor(htfadd967, estminsbu)
    Predictor(htfadd967, estmaxsbd)  
    Predictor(htfadd968, estminsbu)
    Predictor(htfadd968, estmaxsbd)  
    Predictor(htfadd969, estminsbu)
    Predictor(htfadd969, estmaxsbd)  
    Predictor(htfadd970, estminsbu)
    Predictor(htfadd970, estmaxsbd)  
    Predictor(htfadd971, estminsbu)
    Predictor(htfadd971, estmaxsbd)  
    Predictor(htfadd972, estminsbu)
    Predictor(htfadd972, estmaxsbd)  
    Predictor(htfadd973, estminsbu)
    Predictor(htfadd973, estmaxsbd)  
    Predictor(htfadd974, estminsbu)
    Predictor(htfadd974, estmaxsbd)  
    Predictor(htfadd975, estminsbu)
    Predictor(htfadd975, estmaxsbd)  
    Predictor(htfadd976, estminsbu)
    Predictor(htfadd976, estmaxsbd)  
    Predictor(htfadd977, estminsbu)
    Predictor(htfadd977, estmaxsbd)  
    Predictor(htfadd978, estminsbu)
    Predictor(htfadd978, estmaxsbd)  
    Predictor(htfadd979, estminsbu)
    Predictor(htfadd979, estmaxsbd)  
    Predictor(htfadd980, estminsbu)
    Predictor(htfadd980, estmaxsbd)  
    Predictor(htfadd981, estminsbu)
    Predictor(htfadd981, estmaxsbd)  
    Predictor(htfadd982, estminsbu)
    Predictor(htfadd982, estmaxsbd)  
    Predictor(htfadd983, estminsbu)
    Predictor(htfadd983, estmaxsbd)  
    Predictor(htfadd984, estminsbu)
    Predictor(htfadd984, estmaxsbd)  
    Predictor(htfadd985, estminsbu)
    Predictor(htfadd985, estmaxsbd)  
    Predictor(htfadd986, estminsbu)
    Predictor(htfadd986, estmaxsbd)  
    Predictor(htfadd987, estminsbu)
    Predictor(htfadd987, estmaxsbd)  
    Predictor(htfadd988, estminsbu)
    Predictor(htfadd988, estmaxsbd)  
    Predictor(htfadd989, estminsbu)
    Predictor(htfadd989, estmaxsbd)  
    Predictor(htfadd990, estminsbu)
    Predictor(htfadd990, estmaxsbd)  
    Predictor(htfadd991, estminsbu)
    Predictor(htfadd991, estmaxsbd)  
    Predictor(htfadd992, estminsbu)
    Predictor(htfadd992, estmaxsbd)  
    Predictor(htfadd993, estminsbu)
    Predictor(htfadd993, estmaxsbd)  
    Predictor(htfadd994, estminsbu)
    Predictor(htfadd994, estmaxsbd)  
    Predictor(htfadd995, estminsbu)
    Predictor(htfadd995, estmaxsbd)  
    Predictor(htfadd996, estminsbu)
    Predictor(htfadd996, estmaxsbd)  
    Predictor(htfadd997, estminsbu)
    Predictor(htfadd997, estmaxsbd)  
    Predictor(htfadd998, estminsbu)
    Predictor(htfadd998, estmaxsbd)  
    Predictor(htfadd999, estminsbu)
    Predictor(htfadd999, estmaxsbd)  
    Predictor(htfadd1000, estminsbu)
    Predictor(htfadd1000, estmaxsbd)  
    Predictor(htfadd1001, estminsbu)
    Predictor(htfadd1001, estmaxsbd)  
    Predictor(htfadd1002, estminsbu)
    Predictor(htfadd1002, estmaxsbd)  
    Predictor(htfadd1003, estminsbu)
    Predictor(htfadd1003, estmaxsbd)  
    Predictor(htfadd1004, estminsbu)
    Predictor(htfadd1004, estmaxsbd)  
    Predictor(htfadd1005, estminsbu)
    Predictor(htfadd1005, estmaxsbd)  
    Predictor(htfadd1006, estminsbu)
    Predictor(htfadd1006, estmaxsbd)  
    Predictor(htfadd1007, estminsbu)
    Predictor(htfadd1007, estmaxsbd)  
    Predictor(htfadd1008, estminsbu)
    Predictor(htfadd1008, estmaxsbd)  
    Predictor(htfadd1009, estminsbu)
    Predictor(htfadd1009, estmaxsbd)  
    Predictor(htfadd1010, estminsbu)
    Predictor(htfadd1010, estmaxsbd)  
    Predictor(htfadd1011, estminsbu)
    Predictor(htfadd1011, estmaxsbd)  
    Predictor(htfadd1012, estminsbu)
    Predictor(htfadd1012, estmaxsbd)  
    Predictor(htfadd1013, estminsbu)
    Predictor(htfadd1013, estmaxsbd)  
    Predictor(htfadd1014, estminsbu)
    Predictor(htfadd1014, estmaxsbd)  
    Predictor(htfadd1015, estminsbu)
    Predictor(htfadd1015, estmaxsbd)  
    Predictor(htfadd1016, estminsbu)
    Predictor(htfadd1016, estmaxsbd)  
    Predictor(htfadd1017, estminsbu)
    Predictor(htfadd1017, estmaxsbd)  
    Predictor(htfadd1018, estminsbu)
    Predictor(htfadd1018, estmaxsbd)  
    Predictor(htfadd1019, estminsbu)
    Predictor(htfadd1019, estmaxsbd)  
    Predictor(htfadd1020, estminsbu)
    Predictor(htfadd1020, estmaxsbd)  
    Predictor(htfadd1021, estminsbu)
    Predictor(htfadd1021, estmaxsbd)  
    Predictor(htfadd1022, estminsbu)
    Predictor(htfadd1022, estmaxsbd)  
    Predictor(htfadd1023, estminsbu)
    Predictor(htfadd1023, estmaxsbd)  
    Predictor(htfadd1024, estminsbu)
    Predictor(htfadd1024, estmaxsbd)  
    Predictor(htfadd1025, estminsbu)
    Predictor(htfadd1025, estmaxsbd)  
    Predictor(htfadd1026, estminsbu)
    Predictor(htfadd1026, estmaxsbd)  
    Predictor(htfadd1027, estminsbu)
    Predictor(htfadd1027, estmaxsbd)  
    Predictor(htfadd1028, estminsbu)
    Predictor(htfadd1028, estmaxsbd)  
    Predictor(htfadd1029, estminsbu)
    Predictor(htfadd1029, estmaxsbd)  
    Predictor(htfadd1030, estminsbu)
    Predictor(htfadd1030, estmaxsbd)  
    Predictor(htfadd1031, estminsbu)
    Predictor(htfadd1031, estmaxsbd)  
    Predictor(htfadd1032, estminsbu)
    Predictor(htfadd1032, estmaxsbd)  
    Predictor(htfadd1033, estminsbu)
    Predictor(htfadd1033, estmaxsbd)  
    Predictor(htfadd1034, estminsbu)
    Predictor(htfadd1034, estmaxsbd)  
    Predictor(htfadd1035, estminsbu)
    Predictor(htfadd1035, estmaxsbd)  
    Predictor(htfadd1036, estminsbu)
    Predictor(htfadd1036, estmaxsbd)  
    Predictor(htfadd1037, estminsbu)
    Predictor(htfadd1037, estmaxsbd)  
    Predictor(htfadd1038, estminsbu)
    Predictor(htfadd1038, estmaxsbd)  
    Predictor(htfadd1039, estminsbu)
    Predictor(htfadd1039, estmaxsbd)  
    Predictor(htfadd1040, estminsbu)
    Predictor(htfadd1040, estmaxsbd)  
    Predictor(htfadd1041, estminsbu)
    Predictor(htfadd1041, estmaxsbd)  
    Predictor(htfadd1042, estminsbu)
    Predictor(htfadd1042, estmaxsbd)  
    Predictor(htfadd1043, estminsbu)
    Predictor(htfadd1043, estmaxsbd)  
    Predictor(htfadd1044, estminsbu)
    Predictor(htfadd1044, estmaxsbd)  
    Predictor(htfadd1045, estminsbu)
    Predictor(htfadd1045, estmaxsbd)  
    Predictor(htfadd1046, estminsbu)
    Predictor(htfadd1046, estmaxsbd)  
    Predictor(htfadd1047, estminsbu)
    Predictor(htfadd1047, estmaxsbd)  
    Predictor(htfadd1048, estminsbu)
    Predictor(htfadd1048, estmaxsbd)  
    Predictor(htfadd1049, estminsbu)
    Predictor(htfadd1049, estmaxsbd)  
    Predictor(htfadd1050, estminsbu)
    Predictor(htfadd1050, estmaxsbd)  
    Predictor(htfadd1051, estminsbu)
    Predictor(htfadd1051, estmaxsbd)  
    Predictor(htfadd1052, estminsbu)
    Predictor(htfadd1052, estmaxsbd)  
    Predictor(htfadd1053, estminsbu)
    Predictor(htfadd1053, estmaxsbd)  
    Predictor(htfadd1054, estminsbu)
    Predictor(htfadd1054, estmaxsbd)  
    Predictor(htfadd1055, estminsbu)
    Predictor(htfadd1055, estmaxsbd)  
    Predictor(htfadd1056, estminsbu)
    Predictor(htfadd1056, estmaxsbd)  
    Predictor(htfadd1057, estminsbu)
    Predictor(htfadd1057, estmaxsbd)  
    Predictor(htfadd1058, estminsbu)
    Predictor(htfadd1058, estmaxsbd)  
    Predictor(htfadd1059, estminsbu)
    Predictor(htfadd1059, estmaxsbd)  
    Predictor(htfadd1060, estminsbu)
    Predictor(htfadd1060, estmaxsbd)  
    Predictor(htfadd1061, estminsbu)
    Predictor(htfadd1061, estmaxsbd)  
    Predictor(htfadd1062, estminsbu)
    Predictor(htfadd1062, estmaxsbd)  
    Predictor(htfadd1063, estminsbu)
    Predictor(htfadd1063, estmaxsbd)  
    Predictor(htfadd1064, estminsbu)
    Predictor(htfadd1064, estmaxsbd)  
    Predictor(htfadd1065, estminsbu)
    Predictor(htfadd1065, estmaxsbd)  
    Predictor(htfadd1066, estminsbu)
    Predictor(htfadd1066, estmaxsbd)  
    Predictor(htfadd1067, estminsbu)
    Predictor(htfadd1067, estmaxsbd)  
    Predictor(htfadd1068, estminsbu)
    Predictor(htfadd1068, estmaxsbd)  
    Predictor(htfadd1069, estminsbu)
    Predictor(htfadd1069, estmaxsbd)  
    Predictor(htfadd1070, estminsbu)
    Predictor(htfadd1070, estmaxsbd)  
    Predictor(htfadd1071, estminsbu)
    Predictor(htfadd1071, estmaxsbd)  
    Predictor(htfadd1072, estminsbu)
    Predictor(htfadd1072, estmaxsbd)  
    Predictor(htfadd1073, estminsbu)
    Predictor(htfadd1073, estmaxsbd)  
    Predictor(htfadd1074, estminsbu)
    Predictor(htfadd1074, estmaxsbd)  
    Predictor(htfadd1075, estminsbu)
    Predictor(htfadd1075, estmaxsbd)  
    Predictor(htfadd1076, estminsbu)
    Predictor(htfadd1076, estmaxsbd)  
    Predictor(htfadd1077, estminsbu)
    Predictor(htfadd1077, estmaxsbd)  
    Predictor(htfadd1078, estminsbu)
    Predictor(htfadd1078, estmaxsbd)  
    Predictor(htfadd1079, estminsbu)
    Predictor(htfadd1079, estmaxsbd)  
    Predictor(htfadd1080, estminsbu)
    Predictor(htfadd1080, estmaxsbd)  
    Predictor(htfadd1081, estminsbu)
    Predictor(htfadd1081, estmaxsbd)  
    Predictor(htfadd1082, estminsbu)
    Predictor(htfadd1082, estmaxsbd)  
    Predictor(htfadd1083, estminsbu)
    Predictor(htfadd1083, estmaxsbd)  
    Predictor(htfadd1084, estminsbu)
    Predictor(htfadd1084, estmaxsbd)  
    Predictor(htfadd1085, estminsbu)
    Predictor(htfadd1085, estmaxsbd)  
    Predictor(htfadd1086, estminsbu)
    Predictor(htfadd1086, estmaxsbd)  
    Predictor(htfadd1087, estminsbu)
    Predictor(htfadd1087, estmaxsbd)  
    Predictor(htfadd1088, estminsbu)
    Predictor(htfadd1088, estmaxsbd)  
    Predictor(htfadd1089, estminsbu)
    Predictor(htfadd1089, estmaxsbd)  
    Predictor(htfadd1090, estminsbu)
    Predictor(htfadd1090, estmaxsbd)  
    Predictor(htfadd1091, estminsbu)
    Predictor(htfadd1091, estmaxsbd)  
    Predictor(htfadd1092, estminsbu)
    Predictor(htfadd1092, estmaxsbd)  
    Predictor(htfadd1093, estminsbu)
    Predictor(htfadd1093, estmaxsbd)  
    Predictor(htfadd1094, estminsbu)
    Predictor(htfadd1094, estmaxsbd)  
    Predictor(htfadd1095, estminsbu)
    Predictor(htfadd1095, estmaxsbd)  
    Predictor(htfadd1096, estminsbu)
    Predictor(htfadd1096, estmaxsbd)  
    Predictor(htfadd1097, estminsbu)
    Predictor(htfadd1097, estmaxsbd)  
    Predictor(htfadd1098, estminsbu)
    Predictor(htfadd1098, estmaxsbd)  
    Predictor(htfadd1099, estminsbu)
    Predictor(htfadd1099, estmaxsbd)  
    Predictor(htfadd1100, estminsbu)
    Predictor(htfadd1100, estmaxsbd)  
    Predictor(htfadd1101, estminsbu)
    Predictor(htfadd1101, estmaxsbd)  
    Predictor(htfadd1102, estminsbu)
    Predictor(htfadd1102, estmaxsbd)  
    Predictor(htfadd1103, estminsbu)
    Predictor(htfadd1103, estmaxsbd)  
    Predictor(htfadd1104, estminsbu)
    Predictor(htfadd1104, estmaxsbd)  
    Predictor(htfadd1105, estminsbu)
    Predictor(htfadd1105, estmaxsbd)  
    Predictor(htfadd1106, estminsbu)
    Predictor(htfadd1106, estmaxsbd)  
    Predictor(htfadd1107, estminsbu)
    Predictor(htfadd1107, estmaxsbd)  
    Predictor(htfadd1108, estminsbu)
    Predictor(htfadd1108, estmaxsbd)  
    Predictor(htfadd1109, estminsbu)
    Predictor(htfadd1109, estmaxsbd)  
    Predictor(htfadd1110, estminsbu)
    Predictor(htfadd1110, estmaxsbd)  
    Predictor(htfadd1111, estminsbu)
    Predictor(htfadd1111, estmaxsbd)  
    Predictor(htfadd1112, estminsbu)
    Predictor(htfadd1112, estmaxsbd)  
    Predictor(htfadd1113, estminsbu)
    Predictor(htfadd1113, estmaxsbd)  
    Predictor(htfadd1114, estminsbu)
    Predictor(htfadd1114, estmaxsbd)  
    Predictor(htfadd1115, estminsbu)
    Predictor(htfadd1115, estmaxsbd)  
    Predictor(htfadd1116, estminsbu)
    Predictor(htfadd1116, estmaxsbd)  
    Predictor(htfadd1117, estminsbu)
    Predictor(htfadd1117, estmaxsbd)  
    Predictor(htfadd1118, estminsbu)
    Predictor(htfadd1118, estmaxsbd)  
    Predictor(htfadd1119, estminsbu)
    Predictor(htfadd1119, estmaxsbd)  
    Predictor(htfadd1120, estminsbu)
    Predictor(htfadd1120, estmaxsbd)  
    Predictor(htfadd1121, estminsbu)
    Predictor(htfadd1121, estmaxsbd)  
    Predictor(htfadd1122, estminsbu)
    Predictor(htfadd1122, estmaxsbd)  
    Predictor(htfadd1123, estminsbu)
    Predictor(htfadd1123, estmaxsbd)  
    Predictor(htfadd1124, estminsbu)
    Predictor(htfadd1124, estmaxsbd)  
    Predictor(htfadd1125, estminsbu)
    Predictor(htfadd1125, estmaxsbd)  
    Predictor(htfadd1126, estminsbu)
    Predictor(htfadd1126, estmaxsbd)  
    Predictor(htfadd1127, estminsbu)
    Predictor(htfadd1127, estmaxsbd)  
    Predictor(htfadd1128, estminsbu)
    Predictor(htfadd1128, estmaxsbd)  
    Predictor(htfadd1129, estminsbu)
    Predictor(htfadd1129, estmaxsbd)  
    Predictor(htfadd1130, estminsbu)
    Predictor(htfadd1130, estmaxsbd)  
    Predictor(htfadd1131, estminsbu)
    Predictor(htfadd1131, estmaxsbd)  
    Predictor(htfadd1132, estminsbu)
    Predictor(htfadd1132, estmaxsbd)  
    Predictor(htfadd1133, estminsbu)
    Predictor(htfadd1133, estmaxsbd)  
    Predictor(htfadd1134, estminsbu)
    Predictor(htfadd1134, estmaxsbd)  
    Predictor(htfadd1135, estminsbu)
    Predictor(htfadd1135, estmaxsbd)  
    Predictor(htfadd1136, estminsbu)
    Predictor(htfadd1136, estmaxsbd)  
    Predictor(htfadd1137, estminsbu)
    Predictor(htfadd1137, estmaxsbd)  
    Predictor(htfadd1138, estminsbu)
    Predictor(htfadd1138, estmaxsbd)  
    Predictor(htfadd1139, estminsbu)
    Predictor(htfadd1139, estmaxsbd)  
    Predictor(htfadd1140, estminsbu)
    Predictor(htfadd1140, estmaxsbd)  
    Predictor(htfadd1141, estminsbu)
    Predictor(htfadd1141, estmaxsbd)  
    Predictor(htfadd1142, estminsbu)
    Predictor(htfadd1142, estmaxsbd)  
    Predictor(htfadd1143, estminsbu)
    Predictor(htfadd1143, estmaxsbd)  
    Predictor(htfadd1144, estminsbu)
    Predictor(htfadd1144, estmaxsbd)  
    Predictor(htfadd1145, estminsbu)
    Predictor(htfadd1145, estmaxsbd)  
    Predictor(htfadd1146, estminsbu)
    Predictor(htfadd1146, estmaxsbd)  
    Predictor(htfadd1147, estminsbu)
    Predictor(htfadd1147, estmaxsbd)  
    Predictor(htfadd1148, estminsbu)
    Predictor(htfadd1148, estmaxsbd)  
    Predictor(htfadd1149, estminsbu)
    Predictor(htfadd1149, estmaxsbd)  
    Predictor(htfadd1150, estminsbu)
    Predictor(htfadd1150, estmaxsbd)  
    Predictor(htfadd1151, estminsbu)
    Predictor(htfadd1151, estmaxsbd)  
    Predictor(htfadd1152, estminsbu)
    Predictor(htfadd1152, estmaxsbd)  
    Predictor(htfadd1153, estminsbu)
    Predictor(htfadd1153, estmaxsbd)  
    Predictor(htfadd1154, estminsbu)
    Predictor(htfadd1154, estmaxsbd)  
    Predictor(htfadd1155, estminsbu)
    Predictor(htfadd1155, estmaxsbd)  
    Predictor(htfadd1156, estminsbu)
    Predictor(htfadd1156, estmaxsbd)  
    Predictor(htfadd1157, estminsbu)
    Predictor(htfadd1157, estmaxsbd)  
    Predictor(htfadd1158, estminsbu)
    Predictor(htfadd1158, estmaxsbd)  
    Predictor(htfadd1159, estminsbu)
    Predictor(htfadd1159, estmaxsbd)  
    Predictor(htfadd1160, estminsbu)
    Predictor(htfadd1160, estmaxsbd)  
    Predictor(htfadd1161, estminsbu)
    Predictor(htfadd1161, estmaxsbd)  
    Predictor(htfadd1162, estminsbu)
    Predictor(htfadd1162, estmaxsbd)  
    Predictor(htfadd1163, estminsbu)
    Predictor(htfadd1163, estmaxsbd)  
    Predictor(htfadd1164, estminsbu)
    Predictor(htfadd1164, estmaxsbd)  
    Predictor(htfadd1165, estminsbu)
    Predictor(htfadd1165, estmaxsbd)  
    Predictor(htfadd1166, estminsbu)
    Predictor(htfadd1166, estmaxsbd)  
    Predictor(htfadd1167, estminsbu)
    Predictor(htfadd1167, estmaxsbd)  
    Predictor(htfadd1168, estminsbu)
    Predictor(htfadd1168, estmaxsbd)  
    Predictor(htfadd1169, estminsbu)
    Predictor(htfadd1169, estmaxsbd)  
    Predictor(htfadd1170, estminsbu)
    Predictor(htfadd1170, estmaxsbd)  
    Predictor(htfadd1171, estminsbu)
    Predictor(htfadd1171, estmaxsbd)  
    Predictor(htfadd1172, estminsbu)
    Predictor(htfadd1172, estmaxsbd)  
    Predictor(htfadd1173, estminsbu)
    Predictor(htfadd1173, estmaxsbd)  
    Predictor(htfadd1174, estminsbu)
    Predictor(htfadd1174, estmaxsbd)  
    Predictor(htfadd1175, estminsbu)
    Predictor(htfadd1175, estmaxsbd)  
    Predictor(htfadd1176, estminsbu)
    Predictor(htfadd1176, estmaxsbd)  
    Predictor(htfadd1177, estminsbu)
    Predictor(htfadd1177, estmaxsbd)  
    Predictor(htfadd1178, estminsbu)
    Predictor(htfadd1178, estmaxsbd)  
    Predictor(htfadd1179, estminsbu)
    Predictor(htfadd1179, estmaxsbd)  
    Predictor(htfadd1180, estminsbu)
    Predictor(htfadd1180, estmaxsbd)  
    Predictor(htfadd1181, estminsbu)
    Predictor(htfadd1181, estmaxsbd)  
    Predictor(htfadd1182, estminsbu)
    Predictor(htfadd1182, estmaxsbd)  
    Predictor(htfadd1183, estminsbu)
    Predictor(htfadd1183, estmaxsbd)  
    Predictor(htfadd1184, estminsbu)
    Predictor(htfadd1184, estmaxsbd)  
    Predictor(htfadd1185, estminsbu)
    Predictor(htfadd1185, estmaxsbd)  
    Predictor(htfadd1186, estminsbu)
    Predictor(htfadd1186, estmaxsbd)  
    Predictor(htfadd1187, estminsbu)
    Predictor(htfadd1187, estmaxsbd)  
    Predictor(htfadd1188, estminsbu)
    Predictor(htfadd1188, estmaxsbd)  
    Predictor(htfadd1189, estminsbu)
    Predictor(htfadd1189, estmaxsbd)  
    Predictor(htfadd1190, estminsbu)
    Predictor(htfadd1190, estmaxsbd)  
    Predictor(htfadd1191, estminsbu)
    Predictor(htfadd1191, estmaxsbd)  
    Predictor(htfadd1192, estminsbu)
    Predictor(htfadd1192, estmaxsbd)  
    Predictor(htfadd1193, estminsbu)
    Predictor(htfadd1193, estmaxsbd)  
    Predictor(htfadd1194, estminsbu)
    Predictor(htfadd1194, estmaxsbd)  
    Predictor(htfadd1195, estminsbu)
    Predictor(htfadd1195, estmaxsbd)  
    Predictor(htfadd1196, estminsbu)
    Predictor(htfadd1196, estmaxsbd)  
    Predictor(htfadd1197, estminsbu)
    Predictor(htfadd1197, estmaxsbd)  
    Predictor(htfadd1198, estminsbu)
    Predictor(htfadd1198, estmaxsbd)  
    Predictor(htfadd1199, estminsbu)
    Predictor(htfadd1199, estmaxsbd)  
    Predictor(htfadd1200, estminsbu)
    Predictor(htfadd1200, estmaxsbd)  
    Predictor(htfadd1201, estminsbu)
    Predictor(htfadd1201, estmaxsbd)  
    Predictor(htfadd1202, estminsbu)
    Predictor(htfadd1202, estmaxsbd)  
    Predictor(htfadd1203, estminsbu)
    Predictor(htfadd1203, estmaxsbd)  
    Predictor(htfadd1204, estminsbu)
    Predictor(htfadd1204, estmaxsbd)  
    Predictor(htfadd1205, estminsbu)
    Predictor(htfadd1205, estmaxsbd)  
    Predictor(htfadd1206, estminsbu)
    Predictor(htfadd1206, estmaxsbd)  
    Predictor(htfadd1207, estminsbu)
    Predictor(htfadd1207, estmaxsbd)  
    Predictor(htfadd1208, estminsbu)
    Predictor(htfadd1208, estmaxsbd)  
    Predictor(htfadd1209, estminsbu)
    Predictor(htfadd1209, estmaxsbd)  
    Predictor(htfadd1210, estminsbu)
    Predictor(htfadd1210, estmaxsbd)  
    Predictor(htfadd1211, estminsbu)
    Predictor(htfadd1211, estmaxsbd)  
    Predictor(htfadd1212, estminsbu)
    Predictor(htfadd1212, estmaxsbd)  
    Predictor(htfadd1213, estminsbu)
    Predictor(htfadd1213, estmaxsbd)  
    Predictor(htfadd1214, estminsbu)
    Predictor(htfadd1214, estmaxsbd)  
    Predictor(htfadd1215, estminsbu)
    Predictor(htfadd1215, estmaxsbd)  
    Predictor(htfadd1216, estminsbu)
    Predictor(htfadd1216, estmaxsbd)  
    Predictor(htfadd1217, estminsbu)
    Predictor(htfadd1217, estmaxsbd)  
    Predictor(htfadd1218, estminsbu)
    Predictor(htfadd1218, estmaxsbd)  
    Predictor(htfadd1219, estminsbu)
    Predictor(htfadd1219, estmaxsbd)  
    Predictor(htfadd1220, estminsbu)
    Predictor(htfadd1220, estmaxsbd)  
    Predictor(htfadd1221, estminsbu)
    Predictor(htfadd1221, estmaxsbd)  
    Predictor(htfadd1222, estminsbu)
    Predictor(htfadd1222, estmaxsbd)  
    Predictor(htfadd1223, estminsbu)
    Predictor(htfadd1223, estmaxsbd)  
    Predictor(htfadd1224, estminsbu)
    Predictor(htfadd1224, estmaxsbd)  
    Predictor(htfadd1225, estminsbu)
    Predictor(htfadd1225, estmaxsbd)  
    Predictor(htfadd1226, estminsbu)
    Predictor(htfadd1226, estmaxsbd)  
    Predictor(htfadd1227, estminsbu)
    Predictor(htfadd1227, estmaxsbd)  
    Predictor(htfadd1228, estminsbu)
    Predictor(htfadd1228, estmaxsbd)  
    Predictor(htfadd1229, estminsbu)
    Predictor(htfadd1229, estmaxsbd)  
    Predictor(htfadd1230, estminsbu)
    Predictor(htfadd1230, estmaxsbd)  
    Predictor(htfadd1231, estminsbu)
    Predictor(htfadd1231, estmaxsbd)  
    Predictor(htfadd1232, estminsbu)
    Predictor(htfadd1232, estmaxsbd)  
    Predictor(htfadd1233, estminsbu)
    Predictor(htfadd1233, estmaxsbd)  
    Predictor(htfadd1234, estminsbu)
    Predictor(htfadd1234, estmaxsbd)  
    Predictor(htfadd1235, estminsbu)
    Predictor(htfadd1235, estmaxsbd)  
    Predictor(htfadd1236, estminsbu)
    Predictor(htfadd1236, estmaxsbd)  
    Predictor(htfadd1237, estminsbu)
    Predictor(htfadd1237, estmaxsbd)  
    Predictor(htfadd1238, estminsbu)
    Predictor(htfadd1238, estmaxsbd)  
    Predictor(htfadd1239, estminsbu)
    Predictor(htfadd1239, estmaxsbd)  
    Predictor(htfadd1240, estminsbu)
    Predictor(htfadd1240, estmaxsbd)  
    Predictor(htfadd1241, estminsbu)
    Predictor(htfadd1241, estmaxsbd)  
    Predictor(htfadd1242, estminsbu)
    Predictor(htfadd1242, estmaxsbd)  
    Predictor(htfadd1243, estminsbu)
    Predictor(htfadd1243, estmaxsbd)  
    Predictor(htfadd1244, estminsbu)
    Predictor(htfadd1244, estmaxsbd)  
    Predictor(htfadd1245, estminsbu)
    Predictor(htfadd1245, estmaxsbd)  
    Predictor(htfadd1246, estminsbu)
    Predictor(htfadd1246, estmaxsbd)  
    Predictor(htfadd1247, estminsbu)
    Predictor(htfadd1247, estmaxsbd)  
    Predictor(htfadd1248, estminsbu)
    Predictor(htfadd1248, estmaxsbd)  
    Predictor(htfadd1249, estminsbu)
    Predictor(htfadd1249, estmaxsbd)  
    Predictor(htfadd1250, estminsbu)
    Predictor(htfadd1250, estmaxsbd)  
    Predictor(htfadd1251, estminsbu)
    Predictor(htfadd1251, estmaxsbd)  
    Predictor(htfadd1252, estminsbu)
    Predictor(htfadd1252, estmaxsbd)  
    Predictor(htfadd1253, estminsbu)
    Predictor(htfadd1253, estmaxsbd)  
    Predictor(htfadd1254, estminsbu)
    Predictor(htfadd1254, estmaxsbd)  
    Predictor(htfadd1255, estminsbu)
    Predictor(htfadd1255, estmaxsbd)  
    Predictor(htfadd1256, estminsbu)
    Predictor(htfadd1256, estmaxsbd)  
    Predictor(htfadd1257, estminsbu)
    Predictor(htfadd1257, estmaxsbd)  
    Predictor(htfadd1258, estminsbu)
    Predictor(htfadd1258, estmaxsbd)  
    Predictor(htfadd1259, estminsbu)
    Predictor(htfadd1259, estmaxsbd)  
    Predictor(htfadd1260, estminsbu)
    Predictor(htfadd1260, estmaxsbd)  
    Predictor(htfadd1261, estminsbu)
    Predictor(htfadd1261, estmaxsbd)  
    Predictor(htfadd1262, estminsbu)
    Predictor(htfadd1262, estmaxsbd)  
    Predictor(htfadd1263, estminsbu)
    Predictor(htfadd1263, estmaxsbd)  
    Predictor(htfadd1264, estminsbu)
    Predictor(htfadd1264, estmaxsbd)  
    Predictor(htfadd1265, estminsbu)
    Predictor(htfadd1265, estmaxsbd)  
    Predictor(htfadd1266, estminsbu)
    Predictor(htfadd1266, estmaxsbd)  
    Predictor(htfadd1267, estminsbu)
    Predictor(htfadd1267, estmaxsbd)  
    Predictor(htfadd1268, estminsbu)
    Predictor(htfadd1268, estmaxsbd)  
    Predictor(htfadd1269, estminsbu)
    Predictor(htfadd1269, estmaxsbd)  
    Predictor(htfadd1270, estminsbu)
    Predictor(htfadd1270, estmaxsbd)  
    Predictor(htfadd1271, estminsbu)
    Predictor(htfadd1271, estmaxsbd)  
    Predictor(htfadd1272, estminsbu)
    Predictor(htfadd1272, estmaxsbd)  
    Predictor(htfadd1273, estminsbu)
    Predictor(htfadd1273, estmaxsbd)  
    Predictor(htfadd1274, estminsbu)
    Predictor(htfadd1274, estmaxsbd)  
    Predictor(htfadd1275, estminsbu)
    Predictor(htfadd1275, estmaxsbd)  
    Predictor(htfadd1276, estminsbu)
    Predictor(htfadd1276, estmaxsbd)  
    Predictor(htfadd1277, estminsbu)
    Predictor(htfadd1277, estmaxsbd)  
    Predictor(htfadd1278, estminsbu)
    Predictor(htfadd1278, estmaxsbd)  
    Predictor(htfadd1279, estminsbu)
    Predictor(htfadd1279, estmaxsbd)  
    Predictor(htfadd1280, estminsbu)
    Predictor(htfadd1280, estmaxsbd)  
    Predictor(htfadd1281, estminsbu)
    Predictor(htfadd1281, estmaxsbd)  
    Predictor(htfadd1282, estminsbu)
    Predictor(htfadd1282, estmaxsbd)  
    Predictor(htfadd1283, estminsbu)
    Predictor(htfadd1283, estmaxsbd)  
    Predictor(htfadd1284, estminsbu)
    Predictor(htfadd1284, estmaxsbd)  
    Predictor(htfadd1285, estminsbu)
    Predictor(htfadd1285, estmaxsbd)  
    Predictor(htfadd1286, estminsbu)
    Predictor(htfadd1286, estmaxsbd)  
    Predictor(htfadd1287, estminsbu)
    Predictor(htfadd1287, estmaxsbd)  
    Predictor(htfadd1288, estminsbu)
    Predictor(htfadd1288, estmaxsbd)  
    Predictor(htfadd1289, estminsbu)
    Predictor(htfadd1289, estmaxsbd)  
    Predictor(htfadd1290, estminsbu)
    Predictor(htfadd1290, estmaxsbd)  
    Predictor(htfadd1291, estminsbu)
    Predictor(htfadd1291, estmaxsbd)  
    Predictor(htfadd1292, estminsbu)
    Predictor(htfadd1292, estmaxsbd)  
    Predictor(htfadd1293, estminsbu)
    Predictor(htfadd1293, estmaxsbd)  
    Predictor(htfadd1294, estminsbu)
    Predictor(htfadd1294, estmaxsbd)  
    Predictor(htfadd1295, estminsbu)
    Predictor(htfadd1295, estmaxsbd)  
    Predictor(htfadd1296, estminsbu)
    Predictor(htfadd1296, estmaxsbd)  
    Predictor(htfadd1297, estminsbu)
    Predictor(htfadd1297, estmaxsbd)  
    Predictor(htfadd1298, estminsbu)
    Predictor(htfadd1298, estmaxsbd)  
    Predictor(htfadd1299, estminsbu)
    Predictor(htfadd1299, estmaxsbd)  
    Predictor(htfadd1300, estminsbu)
    Predictor(htfadd1300, estmaxsbd)  
    Predictor(htfadd1301, estminsbu)
    Predictor(htfadd1301, estmaxsbd)  
    Predictor(htfadd1302, estminsbu)
    Predictor(htfadd1302, estmaxsbd)  
    Predictor(htfadd1303, estminsbu)
    Predictor(htfadd1303, estmaxsbd)  
    Predictor(htfadd1304, estminsbu)
    Predictor(htfadd1304, estmaxsbd)  
    Predictor(htfadd1305, estminsbu)
    Predictor(htfadd1305, estmaxsbd)  
    Predictor(htfadd1306, estminsbu)
    Predictor(htfadd1306, estmaxsbd)  
    Predictor(htfadd1307, estminsbu)
    Predictor(htfadd1307, estmaxsbd)  
    Predictor(htfadd1308, estminsbu)
    Predictor(htfadd1308, estmaxsbd)  
    Predictor(htfadd1309, estminsbu)
    Predictor(htfadd1309, estmaxsbd)  
    Predictor(htfadd1310, estminsbu)
    Predictor(htfadd1310, estmaxsbd)  
    Predictor(htfadd1311, estminsbu)
    Predictor(htfadd1311, estmaxsbd)  
    Predictor(htfadd1312, estminsbu)
    Predictor(htfadd1312, estmaxsbd)  
    Predictor(htfadd1313, estminsbu)
    Predictor(htfadd1313, estmaxsbd)  
    Predictor(htfadd1314, estminsbu)
    Predictor(htfadd1314, estmaxsbd)  
    Predictor(htfadd1315, estminsbu)
    Predictor(htfadd1315, estmaxsbd)  
    Predictor(htfadd1316, estminsbu)
    Predictor(htfadd1316, estmaxsbd)  
    Predictor(htfadd1317, estminsbu)
    Predictor(htfadd1317, estmaxsbd)  
    Predictor(htfadd1318, estminsbu)
    Predictor(htfadd1318, estmaxsbd)  
    Predictor(htfadd1319, estminsbu)
    Predictor(htfadd1319, estmaxsbd)  
    Predictor(htfadd1320, estminsbu)
    Predictor(htfadd1320, estmaxsbd)  
    Predictor(htfadd1321, estminsbu)
    Predictor(htfadd1321, estmaxsbd)  
    Predictor(htfadd1322, estminsbu)
    Predictor(htfadd1322, estmaxsbd)  
    Predictor(htfadd1323, estminsbu)
    Predictor(htfadd1323, estmaxsbd)  
    Predictor(htfadd1324, estminsbu)
    Predictor(htfadd1324, estmaxsbd)  
    Predictor(htfadd1325, estminsbu)
    Predictor(htfadd1325, estmaxsbd)  
    Predictor(htfadd1326, estminsbu)
    Predictor(htfadd1326, estmaxsbd)  
    Predictor(htfadd1327, estminsbu)
    Predictor(htfadd1327, estmaxsbd)  
    Predictor(htfadd1328, estminsbu)
    Predictor(htfadd1328, estmaxsbd)  
    Predictor(htfadd1329, estminsbu)
    Predictor(htfadd1329, estmaxsbd)  
    Predictor(htfadd1330, estminsbu)
    Predictor(htfadd1330, estmaxsbd)  
    Predictor(htfadd1331, estminsbu)
    Predictor(htfadd1331, estmaxsbd)  
    Predictor(htfadd1332, estminsbu)
    Predictor(htfadd1332, estmaxsbd)  
    Predictor(htfadd1333, estminsbu)
    Predictor(htfadd1333, estmaxsbd)  
    Predictor(htfadd1334, estminsbu)
    Predictor(htfadd1334, estmaxsbd)  
    Predictor(htfadd1335, estminsbu)
    Predictor(htfadd1335, estmaxsbd)  
    Predictor(htfadd1336, estminsbu)
    Predictor(htfadd1336, estmaxsbd)  
    Predictor(htfadd1337, estminsbu)
    Predictor(htfadd1337, estmaxsbd)  
    Predictor(htfadd1338, estminsbu)
    Predictor(htfadd1338, estmaxsbd)  
    Predictor(htfadd1339, estminsbu)
    Predictor(htfadd1339, estmaxsbd)  
    Predictor(htfadd1340, estminsbu)
    Predictor(htfadd1340, estmaxsbd)  
    Predictor(htfadd1341, estminsbu)
    Predictor(htfadd1341, estmaxsbd)  
    Predictor(htfadd1342, estminsbu)
    Predictor(htfadd1342, estmaxsbd)  
    Predictor(htfadd1343, estminsbu)
    Predictor(htfadd1343, estmaxsbd)  
    Predictor(htfadd1344, estminsbu)
    Predictor(htfadd1344, estmaxsbd)  
    Predictor(htfadd1345, estminsbu)
    Predictor(htfadd1345, estmaxsbd)  
    Predictor(htfadd1346, estminsbu)
    Predictor(htfadd1346, estmaxsbd)  
    Predictor(htfadd1347, estminsbu)
    Predictor(htfadd1347, estmaxsbd)  
    Predictor(htfadd1348, estminsbu)
    Predictor(htfadd1348, estmaxsbd)  
    Predictor(htfadd1349, estminsbu)
    Predictor(htfadd1349, estmaxsbd)  
    Predictor(htfadd1350, estminsbu)
    Predictor(htfadd1350, estmaxsbd)  
    Predictor(htfadd1351, estminsbu)
    Predictor(htfadd1351, estmaxsbd)  
    Predictor(htfadd1352, estminsbu)
    Predictor(htfadd1352, estmaxsbd)  
    Predictor(htfadd1353, estminsbu)
    Predictor(htfadd1353, estmaxsbd)  
    Predictor(htfadd1354, estminsbu)
    Predictor(htfadd1354, estmaxsbd)  
    Predictor(htfadd1355, estminsbu)
    Predictor(htfadd1355, estmaxsbd)  
    Predictor(htfadd1356, estminsbu)
    Predictor(htfadd1356, estmaxsbd)  
    Predictor(htfadd1357, estminsbu)
    Predictor(htfadd1357, estmaxsbd)  
    Predictor(htfadd1358, estminsbu)
    Predictor(htfadd1358, estmaxsbd)  
    Predictor(htfadd1359, estminsbu)
    Predictor(htfadd1359, estmaxsbd)  
    Predictor(htfadd1360, estminsbu)
    Predictor(htfadd1360, estmaxsbd)  
    Predictor(htfadd1361, estminsbu)
    Predictor(htfadd1361, estmaxsbd)  
    Predictor(htfadd1362, estminsbu)
    Predictor(htfadd1362, estmaxsbd)  
    Predictor(htfadd1363, estminsbu)
    Predictor(htfadd1363, estmaxsbd)  
    Predictor(htfadd1364, estminsbu)
    Predictor(htfadd1364, estmaxsbd)  
    Predictor(htfadd1365, estminsbu)
    Predictor(htfadd1365, estmaxsbd)  
    Predictor(htfadd1366, estminsbu)
    Predictor(htfadd1366, estmaxsbd)  
    Predictor(htfadd1367, estminsbu)
    Predictor(htfadd1367, estmaxsbd)  
    Predictor(htfadd1368, estminsbu)
    Predictor(htfadd1368, estmaxsbd)  
    Predictor(htfadd1369, estminsbu)
    Predictor(htfadd1369, estmaxsbd)  
    Predictor(htfadd1370, estminsbu)
    Predictor(htfadd1370, estmaxsbd)  
    Predictor(htfadd1371, estminsbu)
    Predictor(htfadd1371, estmaxsbd)  
    Predictor(htfadd1372, estminsbu)
    Predictor(htfadd1372, estmaxsbd)  
    Predictor(htfadd1373, estminsbu)
    Predictor(htfadd1373, estmaxsbd)  
    Predictor(htfadd1374, estminsbu)
    Predictor(htfadd1374, estmaxsbd)  
    Predictor(htfadd1375, estminsbu)
    Predictor(htfadd1375, estmaxsbd)  
    Predictor(htfadd1376, estminsbu)
    Predictor(htfadd1376, estmaxsbd)  
    Predictor(htfadd1377, estminsbu)
    Predictor(htfadd1377, estmaxsbd)  
    Predictor(htfadd1378, estminsbu)
    Predictor(htfadd1378, estmaxsbd)  
    Predictor(htfadd1379, estminsbu)
    Predictor(htfadd1379, estmaxsbd)  
    Predictor(htfadd1380, estminsbu)
    Predictor(htfadd1380, estmaxsbd)  
    Predictor(htfadd1381, estminsbu)
    Predictor(htfadd1381, estmaxsbd)  
    Predictor(htfadd1382, estminsbu)
    Predictor(htfadd1382, estmaxsbd)  
    Predictor(htfadd1383, estminsbu)
    Predictor(htfadd1383, estmaxsbd)  
    Predictor(htfadd1384, estminsbu)
    Predictor(htfadd1384, estmaxsbd)  
    Predictor(htfadd1385, estminsbu)
    Predictor(htfadd1385, estmaxsbd)  
    Predictor(htfadd1386, estminsbu)
    Predictor(htfadd1386, estmaxsbd)  
    Predictor(htfadd1387, estminsbu)
    Predictor(htfadd1387, estmaxsbd)  
    Predictor(htfadd1388, estminsbu)
    Predictor(htfadd1388, estmaxsbd)  
    Predictor(htfadd1389, estminsbu)
    Predictor(htfadd1389, estmaxsbd)  
    Predictor(htfadd1390, estminsbu)
    Predictor(htfadd1390, estmaxsbd)  
    Predictor(htfadd1391, estminsbu)
    Predictor(htfadd1391, estmaxsbd)  
    Predictor(htfadd1392, estminsbu)
    Predictor(htfadd1392, estmaxsbd)  
    Predictor(htfadd1393, estminsbu)
    Predictor(htfadd1393, estmaxsbd)  
    Predictor(htfadd1394, estminsbu)
    Predictor(htfadd1394, estmaxsbd)  
    Predictor(htfadd1395, estminsbu)
    Predictor(htfadd1395, estmaxsbd)  
    Predictor(htfadd1396, estminsbu)
    Predictor(htfadd1396, estmaxsbd)  
    Predictor(htfadd1397, estminsbu)
    Predictor(htfadd1397, estmaxsbd)  
    Predictor(htfadd1398, estminsbu)
    Predictor(htfadd1398, estmaxsbd)  
    Predictor(htfadd1399, estminsbu)
    Predictor(htfadd1399, estmaxsbd)  
    Predictor(htfadd1400, estminsbu)
    Predictor(htfadd1400, estmaxsbd)  
    Predictor(htfadd1401, estminsbu)
    Predictor(htfadd1401, estmaxsbd)  
    Predictor(htfadd1402, estminsbu)
    Predictor(htfadd1402, estmaxsbd)  
    Predictor(htfadd1403, estminsbu)
    Predictor(htfadd1403, estmaxsbd)  
    Predictor(htfadd1404, estminsbu)
    Predictor(htfadd1404, estmaxsbd)  
    Predictor(htfadd1405, estminsbu)
    Predictor(htfadd1405, estmaxsbd)  
    Predictor(htfadd1406, estminsbu)
    Predictor(htfadd1406, estmaxsbd)  
    Predictor(htfadd1407, estminsbu)
    Predictor(htfadd1407, estmaxsbd)  
    Predictor(htfadd1408, estminsbu)
    Predictor(htfadd1408, estmaxsbd)  
    Predictor(htfadd1409, estminsbu)
    Predictor(htfadd1409, estmaxsbd)  
    Predictor(htfadd1410, estminsbu)
    Predictor(htfadd1410, estmaxsbd)  
    Predictor(htfadd1411, estminsbu)
    Predictor(htfadd1411, estmaxsbd)  
    Predictor(htfadd1412, estminsbu)
    Predictor(htfadd1412, estmaxsbd)  
    Predictor(htfadd1413, estminsbu)
    Predictor(htfadd1413, estmaxsbd)  
    Predictor(htfadd1414, estminsbu)
    Predictor(htfadd1414, estmaxsbd)  
    Predictor(htfadd1415, estminsbu)
    Predictor(htfadd1415, estmaxsbd)  
    Predictor(htfadd1416, estminsbu)
    Predictor(htfadd1416, estmaxsbd)  
    Predictor(htfadd1417, estminsbu)
    Predictor(htfadd1417, estmaxsbd)  
    Predictor(htfadd1418, estminsbu)
    Predictor(htfadd1418, estmaxsbd)  
    Predictor(htfadd1419, estminsbu)
    Predictor(htfadd1419, estmaxsbd)  
    Predictor(htfadd1420, estminsbu)
    Predictor(htfadd1420, estmaxsbd)  
    Predictor(htfadd1421, estminsbu)
    Predictor(htfadd1421, estmaxsbd)  
    Predictor(htfadd1422, estminsbu)
    Predictor(htfadd1422, estmaxsbd)  
    Predictor(htfadd1423, estminsbu)
    Predictor(htfadd1423, estmaxsbd)  
    Predictor(htfadd1424, estminsbu)
    Predictor(htfadd1424, estmaxsbd)  
    Predictor(htfadd1425, estminsbu)
    Predictor(htfadd1425, estmaxsbd)  
    Predictor(htfadd1426, estminsbu)
    Predictor(htfadd1426, estmaxsbd)  
    Predictor(htfadd1427, estminsbu)
    Predictor(htfadd1427, estmaxsbd)  
    Predictor(htfadd1428, estminsbu)
    Predictor(htfadd1428, estmaxsbd)  
    Predictor(htfadd1429, estminsbu)
    Predictor(htfadd1429, estmaxsbd)  
    Predictor(htfadd1430, estminsbu)
    Predictor(htfadd1430, estmaxsbd)  
    Predictor(htfadd1431, estminsbu)
    Predictor(htfadd1431, estmaxsbd)  
    Predictor(htfadd1432, estminsbu)
    Predictor(htfadd1432, estmaxsbd)  
    Predictor(htfadd1433, estminsbu)
    Predictor(htfadd1433, estmaxsbd)  
    Predictor(htfadd1434, estminsbu)
    Predictor(htfadd1434, estmaxsbd)  
    Predictor(htfadd1435, estminsbu)
    Predictor(htfadd1435, estmaxsbd)  
    Predictor(htfadd1436, estminsbu)
    Predictor(htfadd1436, estmaxsbd)  
    Predictor(htfadd1437, estminsbu)
    Predictor(htfadd1437, estmaxsbd)  
    Predictor(htfadd1438, estminsbu)
    Predictor(htfadd1438, estmaxsbd)  
    Predictor(htfadd1439, estminsbu)
    Predictor(htfadd1439, estmaxsbd)  
    Predictor(htfadd1440, estminsbu)
    Predictor(htfadd1440, estmaxsbd)  

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

