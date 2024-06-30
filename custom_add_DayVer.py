//+-----filter the multiline after the timing and show that on figure -----+//
// © T.PanShuai29
//@version=5
indicator("add_60Day_setBaseAndItv", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)
//+----------------------------------------+//
//+- Custom Variable
int Baseint  = input.int(1,"Base",inline='custom_setting',minval=1,maxval=365,tooltip="最大只能365")
int Interval = input.int(1,"Interval",inline='custom_setting',minval=1,maxval=364)
int CmprSet  = input.int(10,"Nunber of Compared Set",inline='custom_setting',minval=1,maxval=60,tooltip="總共要和幾組比 最少和1組比 最多60組比")
int Bound    = (Baseint + Interval*CmprSet)*1440
// there is four line a set, totally. 
string str_base  =  str.tostring(Baseint)+"D"
int    Base      =  (Baseint)*1440
int    int_itv1  =  (Baseint+1*Interval)*1440
int    int_itv2  =  (Baseint+2*Interval)*1440
int    int_itv3  =  (Baseint+3*Interval)*1440
int    int_itv4  =  (Baseint+4*Interval)*1440
int    int_itv5  =  (Baseint+5*Interval)*1440
int    int_itv6  =  (Baseint+6*Interval)*1440
int    int_itv7  =  (Baseint+7*Interval)*1440
int    int_itv8  =  (Baseint+8*Interval)*1440
int    int_itv9  =  (Baseint+9*Interval)*1440
int    int_itv10 =  (Baseint+10*Interval)*1440
int    int_itv11 =  (Baseint+11*Interval)*1440
int    int_itv12 =  (Baseint+12*Interval)*1440
int    int_itv13 =  (Baseint+13*Interval)*1440
int    int_itv14 =  (Baseint+14*Interval)*1440
int    int_itv15 =  (Baseint+15*Interval)*1440
int    int_itv16 =  (Baseint+16*Interval)*1440
int    int_itv17 =  (Baseint+17*Interval)*1440
int    int_itv18 =  (Baseint+18*Interval)*1440
int    int_itv19 =  (Baseint+19*Interval)*1440
int    int_itv20 =  (Baseint+20*Interval)*1440
int    int_itv21 =  (Baseint+21*Interval)*1440
int    int_itv22 =  (Baseint+22*Interval)*1440
int    int_itv23 =  (Baseint+23*Interval)*1440
int    int_itv24 =  (Baseint+24*Interval)*1440
int    int_itv25 =  (Baseint+25*Interval)*1440
int    int_itv26 =  (Baseint+26*Interval)*1440
int    int_itv27 =  (Baseint+27*Interval)*1440
int    int_itv28 =  (Baseint+28*Interval)*1440
int    int_itv29 =  (Baseint+29*Interval)*1440
int    int_itv30 =  (Baseint+30*Interval)*1440
int    int_itv31 =  (Baseint+31*Interval)*1440
int    int_itv32 =  (Baseint+32*Interval)*1440
int    int_itv33 =  (Baseint+33*Interval)*1440
int    int_itv34 =  (Baseint+34*Interval)*1440
int    int_itv35 =  (Baseint+35*Interval)*1440
int    int_itv36 =  (Baseint+36*Interval)*1440
int    int_itv37 =  (Baseint+37*Interval)*1440
int    int_itv38 =  (Baseint+38*Interval)*1440
int    int_itv39 =  (Baseint+39*Interval)*1440
int    int_itv40 =  (Baseint+40*Interval)*1440
int    int_itv41 =  (Baseint+41*Interval)*1440
int    int_itv42 =  (Baseint+42*Interval)*1440
int    int_itv43 =  (Baseint+43*Interval)*1440
int    int_itv44 =  (Baseint+44*Interval)*1440
int    int_itv45 =  (Baseint+45*Interval)*1440
int    int_itv46 =  (Baseint+46*Interval)*1440
int    int_itv47 =  (Baseint+47*Interval)*1440
int    int_itv48 =  (Baseint+48*Interval)*1440
int    int_itv49 =  (Baseint+49*Interval)*1440
int    int_itv50 =  (Baseint+50*Interval)*1440
int    int_itv51 =  (Baseint+51*Interval)*1440
int    int_itv52 =  (Baseint+52*Interval)*1440
int    int_itv53 =  (Baseint+53*Interval)*1440
int    int_itv54 =  (Baseint+54*Interval)*1440
int    int_itv55 =  (Baseint+55*Interval)*1440
int    int_itv56 =  (Baseint+56*Interval)*1440
int    int_itv57 =  (Baseint+57*Interval)*1440
int    int_itv58 =  (Baseint+58*Interval)*1440
int    int_itv59 =  (Baseint+59*Interval)*1440
int    int_itv60 =  (Baseint+60*Interval)*1440

string str_itv1   = str.tostring(int_itv1/1440)+"D"
string str_itv2   = str.tostring(int_itv2/1440)+"D"
string str_itv3   = str.tostring(int_itv3/1440)+"D"
string str_itv4   = str.tostring(int_itv4/1440)+"D"
string str_itv5   = str.tostring(int_itv5/1440)+"D"
string str_itv6   = str.tostring(int_itv6/1440)+"D"
string str_itv7   = str.tostring(int_itv7/1440)+"D"
string str_itv8   = str.tostring(int_itv8/1440)+"D"
string str_itv9   = str.tostring(int_itv9/1440)+"D"
string str_itv10  = str.tostring(int_itv10/1440)+"D"
string str_itv11  = str.tostring(int_itv11/1440)+"D"
string str_itv12  = str.tostring(int_itv12/1440)+"D"
string str_itv13  = str.tostring(int_itv13/1440)+"D"
string str_itv14  = str.tostring(int_itv14/1440)+"D"
string str_itv15  = str.tostring(int_itv15/1440)+"D"
string str_itv16  = str.tostring(int_itv16/1440)+"D"
string str_itv17  = str.tostring(int_itv17/1440)+"D"
string str_itv18  = str.tostring(int_itv18/1440)+"D"
string str_itv19  = str.tostring(int_itv19/1440)+"D"
string str_itv20  = str.tostring(int_itv20/1440)+"D"
string str_itv21  = str.tostring(int_itv21/1440)+"D"
string str_itv22  = str.tostring(int_itv22/1440)+"D"
string str_itv23  = str.tostring(int_itv23/1440)+"D"
string str_itv24  = str.tostring(int_itv24/1440)+"D"
string str_itv25  = str.tostring(int_itv25/1440)+"D"
string str_itv26  = str.tostring(int_itv26/1440)+"D"
string str_itv27  = str.tostring(int_itv27/1440)+"D"
string str_itv28  = str.tostring(int_itv28/1440)+"D"
string str_itv29  = str.tostring(int_itv29/1440)+"D"
string str_itv30  = str.tostring(int_itv30/1440)+"D"
string str_itv31  = str.tostring(int_itv31/1440)+"D"
string str_itv32  = str.tostring(int_itv32/1440)+"D"
string str_itv33  = str.tostring(int_itv33/1440)+"D"
string str_itv34  = str.tostring(int_itv34/1440)+"D"
string str_itv35  = str.tostring(int_itv35/1440)+"D"
string str_itv36  = str.tostring(int_itv36/1440)+"D"
string str_itv37  = str.tostring(int_itv37/1440)+"D"
string str_itv38  = str.tostring(int_itv38/1440)+"D"
string str_itv39  = str.tostring(int_itv39/1440)+"D"
string str_itv40  = str.tostring(int_itv40/1440)+"D"
string str_itv41  = str.tostring(int_itv41/1440)+"D"
string str_itv42  = str.tostring(int_itv42/1440)+"D"
string str_itv43  = str.tostring(int_itv43/1440)+"D"
string str_itv44  = str.tostring(int_itv44/1440)+"D"
string str_itv45  = str.tostring(int_itv45/1440)+"D"
string str_itv46  = str.tostring(int_itv46/1440)+"D"
string str_itv47  = str.tostring(int_itv47/1440)+"D"
string str_itv48  = str.tostring(int_itv48/1440)+"D"
string str_itv49  = str.tostring(int_itv49/1440)+"D"
string str_itv50  = str.tostring(int_itv50/1440)+"D"
string str_itv51  = str.tostring(int_itv51/1440)+"D"
string str_itv52  = str.tostring(int_itv52/1440)+"D"
string str_itv53  = str.tostring(int_itv53/1440)+"D"
string str_itv54  = str.tostring(int_itv54/1440)+"D"
string str_itv55  = str.tostring(int_itv55/1440)+"D"
string str_itv56  = str.tostring(int_itv56/1440)+"D"
string str_itv57  = str.tostring(int_itv57/1440)+"D"
string str_itv58  = str.tostring(int_itv58/1440)+"D"
string str_itv59  = str.tostring(int_itv59/1440)+"D"
string str_itv60  = str.tostring(int_itv60/1440)+"D"

//+----------------------------------------+//

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
    int             htfintdivD

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
var ValueDecisionReg highestsbd = ValueDecisionReg.new(value=0       ,vdecisionname = "HighestsbdSet", vtext = "highestsbd: ")
var ValueDecisionReg lowestsbu  = ValueDecisionReg.new(value=99999999,vdecisionname = "LowestsbuSet",  vtext = "lowestsbu: ")
var ValueDecisionReg estmaxsbd  = ValueDecisionReg.new(value=0       ,vdecisionname = "estmaxsbd",     vtext = "estmaxsbd: ")
var ValueDecisionReg estminsbu  = ValueDecisionReg.new(value=99999999,vdecisionname = "estminsbu",     vtext = "estminsbu: ")


//+---------------ValueDeicsionEND------------------+//

//+----------------------------------------+//
//+-settings    

//+----------------------------------------+//

settings.add_show          := input.bool(true, "add function enable?       ", inline="add enable")

settings.offset            := input.int(10, "padding from current candles", minval = 1)
settings.text_buffer       := input.int(10, "space between text features", minval = 1, maxval = 10)
// sbu sbd, period, date happen, remain time, price, line color


Helper    helper        = Helper.new()
var int index           = 0
color color_transparent = #ffffff00
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
    r = str.format("{0,date,yyyy-MM-dd}", i_HTF)
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
    if candleSet.settings.htfint <= Bound
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
    candleSet.bosdata.temp := close //in fact "temp" is the lastest close price
    candleSet


method Monitor_Est(CandleSet candleSet) =>
    if candleSet.settings.htfint <= Bound
        if barstate.isrealtime
            Candle candle    = Candle.new()
            candle.c        := close
            candle.c_idx    := bar_index
            candleSet.candles.unshift(candle)
            if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
                Candle delCandle = array.pop(candleSet.candles)
    candleSet
    

method BOSJudge(CandleSet candleSet) =>
    HTFBarTime      = time(candleSet.settings.htf)
    isNewHTFCandle  = ta.change(HTFBarTime)
    BOSdata bosdata = candleSet.bosdata
    bool fg     = true
    
    int tf = time(timeframe.period)
    int tp = timeframe.in_seconds(timeframe.period)
    int tn = timeframe.in_seconds(candleSet.settings.htf)
    int k  = tn/tp
    if fg
        bosdata.dateinnumber := tf-1000*tp*(k-1)
        fg                   := false
    string strresult = helper.formattedtime(bosdata.dateinnumber)
    if candleSet.settings.htfint <= Bound
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
    if candleSet.settings.htfint <= Bound
        ValueDecisionReg m1 = highestsbd
        CandleSet        cs = candleSet
        if cs.bosdata.sbd > m1.value
            m1.value := cs.bosdata.sbd
            m1.vidx  := cs.bosdata.sbd_idx
            m1.vname := cs.settings.htf
            m1.vdate := cs.bosdata.s_dated
    highestsbd

method LowestsbuSet (ValueDecisionReg lowestsbu, CandleSet candleSet) =>
    if candleSet.settings.htfint <= Bound
        ValueDecisionReg     m1 = lowestsbu
        CandleSet            cs = candleSet
        if cs.bosdata.sbu < m1.value
            m1.value := cs.bosdata.sbu
            m1.vidx  := cs.bosdata.sbu_idx
            m1.vname := cs.settings.htf
            m1.vdate := cs.bosdata.s_dateu
    lowestsbu

method Predictor (CandleSet candleSet, ValueDecisionReg predictor) =>
    if candleSet.settings.htfint <= Bound
        CandleSet              cs = candleSet
        var ValueDecisionReg   pt = predictor
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
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname  + "\n" + m1.vremntime)
        else
            m1.vlb := label.new( offset-5,m1.value,text= decision.vtext + str.tostring(m1.value)+ "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname  + "\n" + m1.vremntime,style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 99999999    
    if m1.vdecisionname == "HighestsbdSet"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset-2, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset-2,m1.value,text= decision.vtext + str.tostring(m1.value)+ "\n" + "@" + m1.vdate + "\n" + "HTF= " + m1.vname + "\n" + m1.vremntime,style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 0    
    if m1.vdecisionname == "estmaxsbd"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+3, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value) + "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname  + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset+3,m1.value,text= decision.vtext + str.tostring(m1.value)+ "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname  + "\n" + m1.vremntime, style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 0    
    if m1.vdecisionname == "estminsbu"
        if not na(m1.vlb)
            label.set_xy(m1.vlb, offset+3, m1.value)
            label.set_text(m1.vlb,decision.vtext + str.tostring(m1.value)  + "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname  + "\n" + m1.vremntime)
        else
            m1.vlb := label.new(offset+3,m1.value,text= decision.vtext + str.tostring(m1.value)+ "\n" + "@" + m1.vdate + "\n" +"HTF= " + m1.vname  + "\n" + m1.vremntime, style = label.style_label_up, color = color_transparent)
        if not na(m1.vln)
            line.set_xy1(m1.vln, bar_index, m1.value)
            line.set_xy2(m1.vln, offset, m1.value)
        else
            m1.vln := line.new(bar_index, m1.value, offset, m1.value, xloc= xloc.bar_index, color = color.new(color.black, 10), style = line.style_solid , width = 2)
        m1.value   := 99999999 
    decision

method Shadowing(CandleSet sh, CandleSet cd) =>
    if cd.settings.htfint <= Bound
        sh.settings.htfint      := cd.settings.htfint
        sh.settings.htf         := cd.settings.htf
        sh.bosdata.state        := cd.bosdata.state
        sh.bosdata.sbu          := cd.bosdata.sbu
        sh.bosdata.sbd          := cd.bosdata.sbd
        sh.bosdata.sbu_idx      := cd.bosdata.sbu_idx
        sh.bosdata.sbd_idx      := cd.bosdata.sbd_idx
        sh.bosdata.regclose3    := cd.bosdata.regclose3
        sh.bosdata.regclose2    := cd.bosdata.regclose2
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
var CandleSet htfbase                     = CandleSet.new()
var CandleSettings Settingshtfbase        = CandleSettings.new(htf=str_base,htfint=Base,max_memory=3,htfintdivD=Baseint)
var Candle[] candlesbase                  = array.new<Candle>(0)
var BOSdata bosdatabase                   = BOSdata.new()
htfbase.settings                 := Settingshtfbase
htfbase.candles                  := candlesbase
htfbase.bosdata                  := bosdatabase
var CandleSet htfitv1                     = CandleSet.new()
var CandleSettings Settingshtfitv1        = CandleSettings.new(htf=str_itv1,htfint=int_itv1,max_memory=3,htfintdivD=int_itv1/1440)
var Candle[] candlesitv1                  = array.new<Candle>(0)
var BOSdata bosdataitv1                   = BOSdata.new()
htfitv1.settings                         := Settingshtfitv1
htfitv1.candles                          := candlesitv1
htfitv1.bosdata                          := bosdataitv1
var CandleSet htfitv2                     = CandleSet.new()
var CandleSettings Settingshtfitv2        = CandleSettings.new(htf=str_itv2,htfint=int_itv2,max_memory=3,htfintdivD=int_itv2/1440)
var Candle[] candlesitv2                  = array.new<Candle>(0)
var BOSdata bosdataitv2                   = BOSdata.new()
htfitv2.settings                         := Settingshtfitv2
htfitv2.candles                          := candlesitv2
htfitv2.bosdata                          := bosdataitv2
var CandleSet htfitv3                     = CandleSet.new()
var CandleSettings Settingshtfitv3        = CandleSettings.new(htf=str_itv3,htfint=int_itv3,max_memory=3,htfintdivD=int_itv3/1440)
var Candle[] candlesitv3                  = array.new<Candle>(0)
var BOSdata bosdataitv3                   = BOSdata.new()
htfitv3.settings                         := Settingshtfitv3
htfitv3.candles                          := candlesitv3
htfitv3.bosdata                          := bosdataitv3
var CandleSet htfitv4                     = CandleSet.new()
var CandleSettings Settingshtfitv4        = CandleSettings.new(htf=str_itv4,htfint=int_itv4,max_memory=3,htfintdivD=int_itv4/1440)
var Candle[] candlesitv4                  = array.new<Candle>(0)
var BOSdata bosdataitv4                   = BOSdata.new()
htfitv4.settings                         := Settingshtfitv4
htfitv4.candles                          := candlesitv4
htfitv4.bosdata                          := bosdataitv4
var CandleSet htfitv5                     = CandleSet.new()
var CandleSettings Settingshtfitv5        = CandleSettings.new(htf=str_itv5,htfint=int_itv5,max_memory=3,htfintdivD=int_itv5/1440)
var Candle[] candlesitv5                  = array.new<Candle>(0)
var BOSdata bosdataitv5                   = BOSdata.new()
htfitv5.settings                         := Settingshtfitv5
htfitv5.candles                          := candlesitv5
htfitv5.bosdata                          := bosdataitv5
var CandleSet htfitv6                     = CandleSet.new()
var CandleSettings Settingshtfitv6        = CandleSettings.new(htf=str_itv6,htfint=int_itv6,max_memory=3,htfintdivD=int_itv6/1440)
var Candle[] candlesitv6                  = array.new<Candle>(0)
var BOSdata bosdataitv6                   = BOSdata.new()
htfitv6.settings                         := Settingshtfitv6
htfitv6.candles                          := candlesitv6
htfitv6.bosdata                          := bosdataitv6
var CandleSet htfitv7                     = CandleSet.new()
var CandleSettings Settingshtfitv7        = CandleSettings.new(htf=str_itv7,htfint=int_itv7,max_memory=3,htfintdivD=int_itv7/1440)
var Candle[] candlesitv7                  = array.new<Candle>(0)
var BOSdata bosdataitv7                   = BOSdata.new()
htfitv7.settings                         := Settingshtfitv7
htfitv7.candles                          := candlesitv7
htfitv7.bosdata                          := bosdataitv7
var CandleSet htfitv8                     = CandleSet.new()
var CandleSettings Settingshtfitv8        = CandleSettings.new(htf=str_itv8,htfint=int_itv8,max_memory=3,htfintdivD=int_itv8/1440)
var Candle[] candlesitv8                  = array.new<Candle>(0)
var BOSdata bosdataitv8                   = BOSdata.new()
htfitv8.settings                         := Settingshtfitv8
htfitv8.candles                          := candlesitv8
htfitv8.bosdata                          := bosdataitv8
var CandleSet htfitv9                     = CandleSet.new()
var CandleSettings Settingshtfitv9        = CandleSettings.new(htf=str_itv9,htfint=int_itv9,max_memory=3,htfintdivD=int_itv9/1440)
var Candle[] candlesitv9                  = array.new<Candle>(0)
var BOSdata bosdataitv9                   = BOSdata.new()
htfitv9.settings                         := Settingshtfitv9
htfitv9.candles                          := candlesitv9
htfitv9.bosdata                          := bosdataitv9
var CandleSet htfitv10                     = CandleSet.new()
var CandleSettings Settingshtfitv10        = CandleSettings.new(htf=str_itv10,htfint=int_itv10,max_memory=3,htfintdivD=int_itv10/1440)
var Candle[] candlesitv10                  = array.new<Candle>(0)
var BOSdata bosdataitv10                   = BOSdata.new()
htfitv10.settings                         := Settingshtfitv10
htfitv10.candles                          := candlesitv10
htfitv10.bosdata                          := bosdataitv10
var CandleSet htfitv11                     = CandleSet.new()
var CandleSettings Settingshtfitv11        = CandleSettings.new(htf=str_itv11,htfint=int_itv11,max_memory=3,htfintdivD=int_itv11/1440)
var Candle[] candlesitv11                  = array.new<Candle>(0)
var BOSdata bosdataitv11                   = BOSdata.new()
htfitv11.settings                         := Settingshtfitv11
htfitv11.candles                          := candlesitv11
htfitv11.bosdata                          := bosdataitv11
var CandleSet htfitv12                     = CandleSet.new()
var CandleSettings Settingshtfitv12        = CandleSettings.new(htf=str_itv12,htfint=int_itv12,max_memory=3,htfintdivD=int_itv12/1440)
var Candle[] candlesitv12                  = array.new<Candle>(0)
var BOSdata bosdataitv12                   = BOSdata.new()
htfitv12.settings                         := Settingshtfitv12
htfitv12.candles                          := candlesitv12
htfitv12.bosdata                          := bosdataitv12
var CandleSet htfitv13                     = CandleSet.new()
var CandleSettings Settingshtfitv13        = CandleSettings.new(htf=str_itv13,htfint=int_itv13,max_memory=3,htfintdivD=int_itv13/1440)
var Candle[] candlesitv13                  = array.new<Candle>(0)
var BOSdata bosdataitv13                   = BOSdata.new()
htfitv13.settings                         := Settingshtfitv13
htfitv13.candles                          := candlesitv13
htfitv13.bosdata                          := bosdataitv13
var CandleSet htfitv14                     = CandleSet.new()
var CandleSettings Settingshtfitv14        = CandleSettings.new(htf=str_itv14,htfint=int_itv14,max_memory=3,htfintdivD=int_itv14/1440)
var Candle[] candlesitv14                  = array.new<Candle>(0)
var BOSdata bosdataitv14                   = BOSdata.new()
htfitv14.settings                         := Settingshtfitv14
htfitv14.candles                          := candlesitv14
htfitv14.bosdata                          := bosdataitv14
var CandleSet htfitv15                     = CandleSet.new()
var CandleSettings Settingshtfitv15        = CandleSettings.new(htf=str_itv15,htfint=int_itv15,max_memory=3,htfintdivD=int_itv15/1440)
var Candle[] candlesitv15                  = array.new<Candle>(0)
var BOSdata bosdataitv15                   = BOSdata.new()
htfitv15.settings                         := Settingshtfitv15
htfitv15.candles                          := candlesitv15
htfitv15.bosdata                          := bosdataitv15
var CandleSet htfitv16                     = CandleSet.new()
var CandleSettings Settingshtfitv16        = CandleSettings.new(htf=str_itv16,htfint=int_itv16,max_memory=3,htfintdivD=int_itv16/1440)
var Candle[] candlesitv16                  = array.new<Candle>(0)
var BOSdata bosdataitv16                   = BOSdata.new()
htfitv16.settings                         := Settingshtfitv16
htfitv16.candles                          := candlesitv16
htfitv16.bosdata                          := bosdataitv16
var CandleSet htfitv17                     = CandleSet.new()
var CandleSettings Settingshtfitv17        = CandleSettings.new(htf=str_itv17,htfint=int_itv17,max_memory=3,htfintdivD=int_itv17/1440)
var Candle[] candlesitv17                  = array.new<Candle>(0)
var BOSdata bosdataitv17                   = BOSdata.new()
htfitv17.settings                         := Settingshtfitv17
htfitv17.candles                          := candlesitv17
htfitv17.bosdata                          := bosdataitv17
var CandleSet htfitv18                     = CandleSet.new()
var CandleSettings Settingshtfitv18        = CandleSettings.new(htf=str_itv18,htfint=int_itv18,max_memory=3,htfintdivD=int_itv18/1440)
var Candle[] candlesitv18                  = array.new<Candle>(0)
var BOSdata bosdataitv18                   = BOSdata.new()
htfitv18.settings                         := Settingshtfitv18
htfitv18.candles                          := candlesitv18
htfitv18.bosdata                          := bosdataitv18
var CandleSet htfitv19                     = CandleSet.new()
var CandleSettings Settingshtfitv19        = CandleSettings.new(htf=str_itv19,htfint=int_itv19,max_memory=3,htfintdivD=int_itv19/1440)
var Candle[] candlesitv19                  = array.new<Candle>(0)
var BOSdata bosdataitv19                   = BOSdata.new()
htfitv19.settings                         := Settingshtfitv19
htfitv19.candles                          := candlesitv19
htfitv19.bosdata                          := bosdataitv19
var CandleSet htfitv20                     = CandleSet.new()
var CandleSettings Settingshtfitv20        = CandleSettings.new(htf=str_itv20,htfint=int_itv20,max_memory=3,htfintdivD=int_itv20/1440)
var Candle[] candlesitv20                  = array.new<Candle>(0)
var BOSdata bosdataitv20                   = BOSdata.new()
htfitv20.settings                         := Settingshtfitv20
htfitv20.candles                          := candlesitv20
htfitv20.bosdata                          := bosdataitv20
var CandleSet htfitv21                     = CandleSet.new()
var CandleSettings Settingshtfitv21        = CandleSettings.new(htf=str_itv21,htfint=int_itv21,max_memory=3,htfintdivD=int_itv21/1440)
var Candle[] candlesitv21                  = array.new<Candle>(0)
var BOSdata bosdataitv21                   = BOSdata.new()
htfitv21.settings                         := Settingshtfitv21
htfitv21.candles                          := candlesitv21
htfitv21.bosdata                          := bosdataitv21
var CandleSet htfitv22                     = CandleSet.new()
var CandleSettings Settingshtfitv22        = CandleSettings.new(htf=str_itv22,htfint=int_itv22,max_memory=3,htfintdivD=int_itv22/1440)
var Candle[] candlesitv22                  = array.new<Candle>(0)
var BOSdata bosdataitv22                   = BOSdata.new()
htfitv22.settings                         := Settingshtfitv22
htfitv22.candles                          := candlesitv22
htfitv22.bosdata                          := bosdataitv22
var CandleSet htfitv23                     = CandleSet.new()
var CandleSettings Settingshtfitv23        = CandleSettings.new(htf=str_itv23,htfint=int_itv23,max_memory=3,htfintdivD=int_itv23/1440)
var Candle[] candlesitv23                  = array.new<Candle>(0)
var BOSdata bosdataitv23                   = BOSdata.new()
htfitv23.settings                         := Settingshtfitv23
htfitv23.candles                          := candlesitv23
htfitv23.bosdata                          := bosdataitv23
var CandleSet htfitv24                     = CandleSet.new()
var CandleSettings Settingshtfitv24        = CandleSettings.new(htf=str_itv24,htfint=int_itv24,max_memory=3,htfintdivD=int_itv24/1440)
var Candle[] candlesitv24                  = array.new<Candle>(0)
var BOSdata bosdataitv24                   = BOSdata.new()
htfitv24.settings                         := Settingshtfitv24
htfitv24.candles                          := candlesitv24
htfitv24.bosdata                          := bosdataitv24
var CandleSet htfitv25                     = CandleSet.new()
var CandleSettings Settingshtfitv25        = CandleSettings.new(htf=str_itv25,htfint=int_itv25,max_memory=3,htfintdivD=int_itv25/1440)
var Candle[] candlesitv25                  = array.new<Candle>(0)
var BOSdata bosdataitv25                   = BOSdata.new()
htfitv25.settings                         := Settingshtfitv25
htfitv25.candles                          := candlesitv25
htfitv25.bosdata                          := bosdataitv25
var CandleSet htfitv26                     = CandleSet.new()
var CandleSettings Settingshtfitv26        = CandleSettings.new(htf=str_itv26,htfint=int_itv26,max_memory=3,htfintdivD=int_itv26/1440)
var Candle[] candlesitv26                  = array.new<Candle>(0)
var BOSdata bosdataitv26                   = BOSdata.new()
htfitv26.settings                         := Settingshtfitv26
htfitv26.candles                          := candlesitv26
htfitv26.bosdata                          := bosdataitv26
var CandleSet htfitv27                     = CandleSet.new()
var CandleSettings Settingshtfitv27        = CandleSettings.new(htf=str_itv27,htfint=int_itv27,max_memory=3,htfintdivD=int_itv27/1440)
var Candle[] candlesitv27                  = array.new<Candle>(0)
var BOSdata bosdataitv27                   = BOSdata.new()
htfitv27.settings                         := Settingshtfitv27
htfitv27.candles                          := candlesitv27
htfitv27.bosdata                          := bosdataitv27
var CandleSet htfitv28                     = CandleSet.new()
var CandleSettings Settingshtfitv28        = CandleSettings.new(htf=str_itv28,htfint=int_itv28,max_memory=3,htfintdivD=int_itv28/1440)
var Candle[] candlesitv28                  = array.new<Candle>(0)
var BOSdata bosdataitv28                   = BOSdata.new()
htfitv28.settings                         := Settingshtfitv28
htfitv28.candles                          := candlesitv28
htfitv28.bosdata                          := bosdataitv28
var CandleSet htfitv29                     = CandleSet.new()
var CandleSettings Settingshtfitv29        = CandleSettings.new(htf=str_itv29,htfint=int_itv29,max_memory=3,htfintdivD=int_itv29/1440)
var Candle[] candlesitv29                  = array.new<Candle>(0)
var BOSdata bosdataitv29                   = BOSdata.new()
htfitv29.settings                         := Settingshtfitv29
htfitv29.candles                          := candlesitv29
htfitv29.bosdata                          := bosdataitv29
var CandleSet htfitv30                     = CandleSet.new()
var CandleSettings Settingshtfitv30        = CandleSettings.new(htf=str_itv30,htfint=int_itv30,max_memory=3,htfintdivD=int_itv30/1440)
var Candle[] candlesitv30                  = array.new<Candle>(0)
var BOSdata bosdataitv30                   = BOSdata.new()
htfitv30.settings                         := Settingshtfitv30
htfitv30.candles                          := candlesitv30
htfitv30.bosdata                          := bosdataitv30
var CandleSet htfitv31                     = CandleSet.new()
var CandleSettings Settingshtfitv31        = CandleSettings.new(htf=str_itv31,htfint=int_itv31,max_memory=3,htfintdivD=int_itv31/1440)
var Candle[] candlesitv31                  = array.new<Candle>(0)
var BOSdata bosdataitv31                   = BOSdata.new()
htfitv31.settings                         := Settingshtfitv31
htfitv31.candles                          := candlesitv31
htfitv31.bosdata                          := bosdataitv31
var CandleSet htfitv32                     = CandleSet.new()
var CandleSettings Settingshtfitv32        = CandleSettings.new(htf=str_itv32,htfint=int_itv32,max_memory=3,htfintdivD=int_itv32/1440)
var Candle[] candlesitv32                  = array.new<Candle>(0)
var BOSdata bosdataitv32                   = BOSdata.new()
htfitv32.settings                         := Settingshtfitv32
htfitv32.candles                          := candlesitv32
htfitv32.bosdata                          := bosdataitv32
var CandleSet htfitv33                     = CandleSet.new()
var CandleSettings Settingshtfitv33        = CandleSettings.new(htf=str_itv33,htfint=int_itv33,max_memory=3,htfintdivD=int_itv33/1440)
var Candle[] candlesitv33                  = array.new<Candle>(0)
var BOSdata bosdataitv33                   = BOSdata.new()
htfitv33.settings                         := Settingshtfitv33
htfitv33.candles                          := candlesitv33
htfitv33.bosdata                          := bosdataitv33
var CandleSet htfitv34                     = CandleSet.new()
var CandleSettings Settingshtfitv34        = CandleSettings.new(htf=str_itv34,htfint=int_itv34,max_memory=3,htfintdivD=int_itv34/1440)
var Candle[] candlesitv34                  = array.new<Candle>(0)
var BOSdata bosdataitv34                   = BOSdata.new()
htfitv34.settings                         := Settingshtfitv34
htfitv34.candles                          := candlesitv34
htfitv34.bosdata                          := bosdataitv34
var CandleSet htfitv35                     = CandleSet.new()
var CandleSettings Settingshtfitv35        = CandleSettings.new(htf=str_itv35,htfint=int_itv35,max_memory=3,htfintdivD=int_itv35/1440)
var Candle[] candlesitv35                  = array.new<Candle>(0)
var BOSdata bosdataitv35                   = BOSdata.new()
htfitv35.settings                         := Settingshtfitv35
htfitv35.candles                          := candlesitv35
htfitv35.bosdata                          := bosdataitv35
var CandleSet htfitv36                     = CandleSet.new()
var CandleSettings Settingshtfitv36        = CandleSettings.new(htf=str_itv36,htfint=int_itv36,max_memory=3,htfintdivD=int_itv36/1440)
var Candle[] candlesitv36                  = array.new<Candle>(0)
var BOSdata bosdataitv36                   = BOSdata.new()
htfitv36.settings                         := Settingshtfitv36
htfitv36.candles                          := candlesitv36
htfitv36.bosdata                          := bosdataitv36
var CandleSet htfitv37                     = CandleSet.new()
var CandleSettings Settingshtfitv37        = CandleSettings.new(htf=str_itv37,htfint=int_itv37,max_memory=3,htfintdivD=int_itv37/1440)
var Candle[] candlesitv37                  = array.new<Candle>(0)
var BOSdata bosdataitv37                   = BOSdata.new()
htfitv37.settings                         := Settingshtfitv37
htfitv37.candles                          := candlesitv37
htfitv37.bosdata                          := bosdataitv37
var CandleSet htfitv38                     = CandleSet.new()
var CandleSettings Settingshtfitv38        = CandleSettings.new(htf=str_itv38,htfint=int_itv38,max_memory=3,htfintdivD=int_itv38/1440)
var Candle[] candlesitv38                  = array.new<Candle>(0)
var BOSdata bosdataitv38                   = BOSdata.new()
htfitv38.settings                         := Settingshtfitv38
htfitv38.candles                          := candlesitv38
htfitv38.bosdata                          := bosdataitv38
var CandleSet htfitv39                     = CandleSet.new()
var CandleSettings Settingshtfitv39        = CandleSettings.new(htf=str_itv39,htfint=int_itv39,max_memory=3,htfintdivD=int_itv39/1440)
var Candle[] candlesitv39                  = array.new<Candle>(0)
var BOSdata bosdataitv39                   = BOSdata.new()
htfitv39.settings                         := Settingshtfitv39
htfitv39.candles                          := candlesitv39
htfitv39.bosdata                          := bosdataitv39
var CandleSet htfitv40                     = CandleSet.new()
var CandleSettings Settingshtfitv40        = CandleSettings.new(htf=str_itv40,htfint=int_itv40,max_memory=3,htfintdivD=int_itv40/1440)
var Candle[] candlesitv40                  = array.new<Candle>(0)
var BOSdata bosdataitv40                   = BOSdata.new()
htfitv40.settings                         := Settingshtfitv40
htfitv40.candles                          := candlesitv40
htfitv40.bosdata                          := bosdataitv40
var CandleSet htfitv41                     = CandleSet.new()
var CandleSettings Settingshtfitv41        = CandleSettings.new(htf=str_itv41,htfint=int_itv41,max_memory=3,htfintdivD=int_itv41/1440)
var Candle[] candlesitv41                  = array.new<Candle>(0)
var BOSdata bosdataitv41                   = BOSdata.new()
htfitv41.settings                         := Settingshtfitv41
htfitv41.candles                          := candlesitv41
htfitv41.bosdata                          := bosdataitv41
var CandleSet htfitv42                     = CandleSet.new()
var CandleSettings Settingshtfitv42        = CandleSettings.new(htf=str_itv42,htfint=int_itv42,max_memory=3,htfintdivD=int_itv42/1440)
var Candle[] candlesitv42                  = array.new<Candle>(0)
var BOSdata bosdataitv42                   = BOSdata.new()
htfitv42.settings                         := Settingshtfitv42
htfitv42.candles                          := candlesitv42
htfitv42.bosdata                          := bosdataitv42
var CandleSet htfitv43                     = CandleSet.new()
var CandleSettings Settingshtfitv43        = CandleSettings.new(htf=str_itv43,htfint=int_itv43,max_memory=3,htfintdivD=int_itv43/1440)
var Candle[] candlesitv43                  = array.new<Candle>(0)
var BOSdata bosdataitv43                   = BOSdata.new()
htfitv43.settings                         := Settingshtfitv43
htfitv43.candles                          := candlesitv43
htfitv43.bosdata                          := bosdataitv43
var CandleSet htfitv44                     = CandleSet.new()
var CandleSettings Settingshtfitv44        = CandleSettings.new(htf=str_itv44,htfint=int_itv44,max_memory=3,htfintdivD=int_itv44/1440)
var Candle[] candlesitv44                  = array.new<Candle>(0)
var BOSdata bosdataitv44                   = BOSdata.new()
htfitv44.settings                         := Settingshtfitv44
htfitv44.candles                          := candlesitv44
htfitv44.bosdata                          := bosdataitv44
var CandleSet htfitv45                     = CandleSet.new()
var CandleSettings Settingshtfitv45        = CandleSettings.new(htf=str_itv45,htfint=int_itv45,max_memory=3,htfintdivD=int_itv45/1440)
var Candle[] candlesitv45                  = array.new<Candle>(0)
var BOSdata bosdataitv45                   = BOSdata.new()
htfitv45.settings                         := Settingshtfitv45
htfitv45.candles                          := candlesitv45
htfitv45.bosdata                          := bosdataitv45
var CandleSet htfitv46                     = CandleSet.new()
var CandleSettings Settingshtfitv46        = CandleSettings.new(htf=str_itv46,htfint=int_itv46,max_memory=3,htfintdivD=int_itv46/1440)
var Candle[] candlesitv46                  = array.new<Candle>(0)
var BOSdata bosdataitv46                   = BOSdata.new()
htfitv46.settings                         := Settingshtfitv46
htfitv46.candles                          := candlesitv46
htfitv46.bosdata                          := bosdataitv46
var CandleSet htfitv47                     = CandleSet.new()
var CandleSettings Settingshtfitv47        = CandleSettings.new(htf=str_itv47,htfint=int_itv47,max_memory=3,htfintdivD=int_itv47/1440)
var Candle[] candlesitv47                  = array.new<Candle>(0)
var BOSdata bosdataitv47                   = BOSdata.new()
htfitv47.settings                         := Settingshtfitv47
htfitv47.candles                          := candlesitv47
htfitv47.bosdata                          := bosdataitv47
var CandleSet htfitv48                     = CandleSet.new()
var CandleSettings Settingshtfitv48        = CandleSettings.new(htf=str_itv48,htfint=int_itv48,max_memory=3,htfintdivD=int_itv48/1440)
var Candle[] candlesitv48                  = array.new<Candle>(0)
var BOSdata bosdataitv48                   = BOSdata.new()
htfitv48.settings                         := Settingshtfitv48
htfitv48.candles                          := candlesitv48
htfitv48.bosdata                          := bosdataitv48
var CandleSet htfitv49                     = CandleSet.new()
var CandleSettings Settingshtfitv49        = CandleSettings.new(htf=str_itv49,htfint=int_itv49,max_memory=3,htfintdivD=int_itv49/1440)
var Candle[] candlesitv49                  = array.new<Candle>(0)
var BOSdata bosdataitv49                   = BOSdata.new()
htfitv49.settings                         := Settingshtfitv49
htfitv49.candles                          := candlesitv49
htfitv49.bosdata                          := bosdataitv49
var CandleSet htfitv50                     = CandleSet.new()
var CandleSettings Settingshtfitv50        = CandleSettings.new(htf=str_itv50,htfint=int_itv50,max_memory=3,htfintdivD=int_itv50/1440)
var Candle[] candlesitv50                  = array.new<Candle>(0)
var BOSdata bosdataitv50                   = BOSdata.new()
htfitv50.settings                         := Settingshtfitv50
htfitv50.candles                          := candlesitv50
htfitv50.bosdata                          := bosdataitv50
var CandleSet htfitv51                     = CandleSet.new()
var CandleSettings Settingshtfitv51        = CandleSettings.new(htf=str_itv51,htfint=int_itv51,max_memory=3,htfintdivD=int_itv51/1440)
var Candle[] candlesitv51                  = array.new<Candle>(0)
var BOSdata bosdataitv51                   = BOSdata.new()
htfitv51.settings                         := Settingshtfitv51
htfitv51.candles                          := candlesitv51
htfitv51.bosdata                          := bosdataitv51
var CandleSet htfitv52                     = CandleSet.new()
var CandleSettings Settingshtfitv52        = CandleSettings.new(htf=str_itv52,htfint=int_itv52,max_memory=3,htfintdivD=int_itv52/1440)
var Candle[] candlesitv52                  = array.new<Candle>(0)
var BOSdata bosdataitv52                   = BOSdata.new()
htfitv52.settings                         := Settingshtfitv52
htfitv52.candles                          := candlesitv52
htfitv52.bosdata                          := bosdataitv52
var CandleSet htfitv53                     = CandleSet.new()
var CandleSettings Settingshtfitv53        = CandleSettings.new(htf=str_itv53,htfint=int_itv53,max_memory=3,htfintdivD=int_itv53/1440)
var Candle[] candlesitv53                  = array.new<Candle>(0)
var BOSdata bosdataitv53                   = BOSdata.new()
htfitv53.settings                         := Settingshtfitv53
htfitv53.candles                          := candlesitv53
htfitv53.bosdata                          := bosdataitv53
var CandleSet htfitv54                     = CandleSet.new()
var CandleSettings Settingshtfitv54        = CandleSettings.new(htf=str_itv54,htfint=int_itv54,max_memory=3,htfintdivD=int_itv54/1440)
var Candle[] candlesitv54                  = array.new<Candle>(0)
var BOSdata bosdataitv54                   = BOSdata.new()
htfitv54.settings                         := Settingshtfitv54
htfitv54.candles                          := candlesitv54
htfitv54.bosdata                          := bosdataitv54
var CandleSet htfitv55                     = CandleSet.new()
var CandleSettings Settingshtfitv55        = CandleSettings.new(htf=str_itv55,htfint=int_itv55,max_memory=3,htfintdivD=int_itv55/1440)
var Candle[] candlesitv55                  = array.new<Candle>(0)
var BOSdata bosdataitv55                   = BOSdata.new()
htfitv55.settings                         := Settingshtfitv55
htfitv55.candles                          := candlesitv55
htfitv55.bosdata                          := bosdataitv55
var CandleSet htfitv56                     = CandleSet.new()
var CandleSettings Settingshtfitv56        = CandleSettings.new(htf=str_itv56,htfint=int_itv56,max_memory=3,htfintdivD=int_itv56/1440)
var Candle[] candlesitv56                  = array.new<Candle>(0)
var BOSdata bosdataitv56                   = BOSdata.new()
htfitv56.settings                         := Settingshtfitv56
htfitv56.candles                          := candlesitv56
htfitv56.bosdata                          := bosdataitv56
var CandleSet htfitv57                     = CandleSet.new()
var CandleSettings Settingshtfitv57        = CandleSettings.new(htf=str_itv57,htfint=int_itv57,max_memory=3,htfintdivD=int_itv57/1440)
var Candle[] candlesitv57                  = array.new<Candle>(0)
var BOSdata bosdataitv57                   = BOSdata.new()
htfitv57.settings                         := Settingshtfitv57
htfitv57.candles                          := candlesitv57
htfitv57.bosdata                          := bosdataitv57
var CandleSet htfitv58                     = CandleSet.new()
var CandleSettings Settingshtfitv58        = CandleSettings.new(htf=str_itv58,htfint=int_itv58,max_memory=3,htfintdivD=int_itv58/1440)
var Candle[] candlesitv58                  = array.new<Candle>(0)
var BOSdata bosdataitv58                   = BOSdata.new()
htfitv58.settings                         := Settingshtfitv58
htfitv58.candles                          := candlesitv58
htfitv58.bosdata                          := bosdataitv58
var CandleSet htfitv59                     = CandleSet.new()
var CandleSettings Settingshtfitv59        = CandleSettings.new(htf=str_itv59,htfint=int_itv59,max_memory=3,htfintdivD=int_itv59/1440)
var Candle[] candlesitv59                  = array.new<Candle>(0)
var BOSdata bosdataitv59                   = BOSdata.new()
htfitv59.settings                         := Settingshtfitv59
htfitv59.candles                          := candlesitv59
htfitv59.bosdata                          := bosdataitv59
var CandleSet htfitv60                     = CandleSet.new()
var CandleSettings Settingshtfitv60        = CandleSettings.new(htf=str_itv60,htfint=int_itv60,max_memory=3,htfintdivD=int_itv60/1440)
var Candle[] candlesitv60                  = array.new<Candle>(0)
var BOSdata bosdataitv60                   = BOSdata.new()
htfitv60.settings                         := Settingshtfitv60
htfitv60.candles                          := candlesitv60
htfitv60.bosdata                          := bosdataitv60

htfbase.Monitor().BOSJudge()
htfitv1.Monitor().BOSJudge()
htfitv2.Monitor().BOSJudge()
htfitv3.Monitor().BOSJudge()
htfitv4.Monitor().BOSJudge()
htfitv5.Monitor().BOSJudge()
htfitv6.Monitor().BOSJudge()
htfitv7.Monitor().BOSJudge()
htfitv8.Monitor().BOSJudge()
htfitv9.Monitor().BOSJudge()
htfitv10.Monitor().BOSJudge()
htfitv11.Monitor().BOSJudge()
htfitv12.Monitor().BOSJudge()
htfitv13.Monitor().BOSJudge()
htfitv14.Monitor().BOSJudge()
htfitv15.Monitor().BOSJudge()
htfitv16.Monitor().BOSJudge()
htfitv17.Monitor().BOSJudge()
htfitv18.Monitor().BOSJudge()
htfitv19.Monitor().BOSJudge()
htfitv20.Monitor().BOSJudge()
htfitv21.Monitor().BOSJudge()
htfitv22.Monitor().BOSJudge()
htfitv23.Monitor().BOSJudge()
htfitv24.Monitor().BOSJudge()
htfitv25.Monitor().BOSJudge()
htfitv26.Monitor().BOSJudge()
htfitv27.Monitor().BOSJudge()
htfitv28.Monitor().BOSJudge()
htfitv29.Monitor().BOSJudge()
htfitv30.Monitor().BOSJudge()
htfitv31.Monitor().BOSJudge()
htfitv32.Monitor().BOSJudge()
htfitv33.Monitor().BOSJudge()
htfitv34.Monitor().BOSJudge()
htfitv35.Monitor().BOSJudge()
htfitv36.Monitor().BOSJudge()
htfitv37.Monitor().BOSJudge()
htfitv38.Monitor().BOSJudge()
htfitv39.Monitor().BOSJudge()
htfitv40.Monitor().BOSJudge()
htfitv41.Monitor().BOSJudge()
htfitv42.Monitor().BOSJudge()
htfitv43.Monitor().BOSJudge()
htfitv44.Monitor().BOSJudge()
htfitv45.Monitor().BOSJudge()
htfitv46.Monitor().BOSJudge()
htfitv47.Monitor().BOSJudge()
htfitv48.Monitor().BOSJudge()
htfitv49.Monitor().BOSJudge()
htfitv50.Monitor().BOSJudge()
htfitv51.Monitor().BOSJudge()
htfitv52.Monitor().BOSJudge()
htfitv53.Monitor().BOSJudge()
htfitv54.Monitor().BOSJudge()
htfitv55.Monitor().BOSJudge()
htfitv56.Monitor().BOSJudge()
htfitv57.Monitor().BOSJudge()
htfitv58.Monitor().BOSJudge()
htfitv59.Monitor().BOSJudge()
htfitv60.Monitor().BOSJudge()

if bar_index == last_bar_index
    HighestsbdSet(highestsbd, htfbase)
    LowestsbuSet(lowestsbu, htfbase)
    HighestsbdSet(highestsbd, htfitv1)
    LowestsbuSet(lowestsbu, htfitv1)
    HighestsbdSet(highestsbd, htfitv2)
    LowestsbuSet(lowestsbu, htfitv2)
    HighestsbdSet(highestsbd, htfitv3)
    LowestsbuSet(lowestsbu, htfitv3)
    HighestsbdSet(highestsbd, htfitv4)
    LowestsbuSet(lowestsbu, htfitv4)
    HighestsbdSet(highestsbd, htfitv5)
    LowestsbuSet(lowestsbu, htfitv5)
    HighestsbdSet(highestsbd, htfitv6)
    LowestsbuSet(lowestsbu, htfitv6)
    HighestsbdSet(highestsbd, htfitv7)
    LowestsbuSet(lowestsbu, htfitv7)
    HighestsbdSet(highestsbd, htfitv8)
    LowestsbuSet(lowestsbu, htfitv8)
    HighestsbdSet(highestsbd, htfitv9)
    LowestsbuSet(lowestsbu, htfitv9)
    HighestsbdSet(highestsbd, htfitv10)
    LowestsbuSet(lowestsbu, htfitv10)
    HighestsbdSet(highestsbd, htfitv11)
    LowestsbuSet(lowestsbu, htfitv11)
    HighestsbdSet(highestsbd, htfitv12)
    LowestsbuSet(lowestsbu, htfitv12)
    HighestsbdSet(highestsbd, htfitv13)
    LowestsbuSet(lowestsbu, htfitv13)
    HighestsbdSet(highestsbd, htfitv14)
    LowestsbuSet(lowestsbu, htfitv14)
    HighestsbdSet(highestsbd, htfitv15)
    LowestsbuSet(lowestsbu, htfitv15)
    HighestsbdSet(highestsbd, htfitv16)
    LowestsbuSet(lowestsbu, htfitv16)
    HighestsbdSet(highestsbd, htfitv17)
    LowestsbuSet(lowestsbu, htfitv17)
    HighestsbdSet(highestsbd, htfitv18)
    LowestsbuSet(lowestsbu, htfitv18)
    HighestsbdSet(highestsbd, htfitv19)
    LowestsbuSet(lowestsbu, htfitv19)
    HighestsbdSet(highestsbd, htfitv20)
    LowestsbuSet(lowestsbu, htfitv20)
    HighestsbdSet(highestsbd, htfitv21)
    LowestsbuSet(lowestsbu, htfitv21)
    HighestsbdSet(highestsbd, htfitv22)
    LowestsbuSet(lowestsbu, htfitv22)
    HighestsbdSet(highestsbd, htfitv23)
    LowestsbuSet(lowestsbu, htfitv23)
    HighestsbdSet(highestsbd, htfitv24)
    LowestsbuSet(lowestsbu, htfitv24)
    HighestsbdSet(highestsbd, htfitv25)
    LowestsbuSet(lowestsbu, htfitv25)
    HighestsbdSet(highestsbd, htfitv26)
    LowestsbuSet(lowestsbu, htfitv26)
    HighestsbdSet(highestsbd, htfitv27)
    LowestsbuSet(lowestsbu, htfitv27)
    HighestsbdSet(highestsbd, htfitv28)
    LowestsbuSet(lowestsbu, htfitv28)
    HighestsbdSet(highestsbd, htfitv29)
    LowestsbuSet(lowestsbu, htfitv29)
    HighestsbdSet(highestsbd, htfitv30)
    LowestsbuSet(lowestsbu, htfitv30)
    HighestsbdSet(highestsbd, htfitv31)
    LowestsbuSet(lowestsbu, htfitv31)
    HighestsbdSet(highestsbd, htfitv32)
    LowestsbuSet(lowestsbu, htfitv32)
    HighestsbdSet(highestsbd, htfitv33)
    LowestsbuSet(lowestsbu, htfitv33)
    HighestsbdSet(highestsbd, htfitv34)
    LowestsbuSet(lowestsbu, htfitv34)
    HighestsbdSet(highestsbd, htfitv35)
    LowestsbuSet(lowestsbu, htfitv35)
    HighestsbdSet(highestsbd, htfitv36)
    LowestsbuSet(lowestsbu, htfitv36)
    HighestsbdSet(highestsbd, htfitv37)
    LowestsbuSet(lowestsbu, htfitv37)
    HighestsbdSet(highestsbd, htfitv38)
    LowestsbuSet(lowestsbu, htfitv38)
    HighestsbdSet(highestsbd, htfitv39)
    LowestsbuSet(lowestsbu, htfitv39)
    HighestsbdSet(highestsbd, htfitv40)
    LowestsbuSet(lowestsbu, htfitv40)
    HighestsbdSet(highestsbd, htfitv41)
    LowestsbuSet(lowestsbu, htfitv41)
    HighestsbdSet(highestsbd, htfitv42)
    LowestsbuSet(lowestsbu, htfitv42)
    HighestsbdSet(highestsbd, htfitv43)
    LowestsbuSet(lowestsbu, htfitv43)
    HighestsbdSet(highestsbd, htfitv44)
    LowestsbuSet(lowestsbu, htfitv44)
    HighestsbdSet(highestsbd, htfitv45)
    LowestsbuSet(lowestsbu, htfitv45)
    HighestsbdSet(highestsbd, htfitv46)
    LowestsbuSet(lowestsbu, htfitv46)
    HighestsbdSet(highestsbd, htfitv47)
    LowestsbuSet(lowestsbu, htfitv47)
    HighestsbdSet(highestsbd, htfitv48)
    LowestsbuSet(lowestsbu, htfitv48)
    HighestsbdSet(highestsbd, htfitv49)
    LowestsbuSet(lowestsbu, htfitv49)
    HighestsbdSet(highestsbd, htfitv50)
    LowestsbuSet(lowestsbu, htfitv50)
    HighestsbdSet(highestsbd, htfitv51)
    LowestsbuSet(lowestsbu, htfitv51)
    HighestsbdSet(highestsbd, htfitv52)
    LowestsbuSet(lowestsbu, htfitv52)
    HighestsbdSet(highestsbd, htfitv53)
    LowestsbuSet(lowestsbu, htfitv53)
    HighestsbdSet(highestsbd, htfitv54)
    LowestsbuSet(lowestsbu, htfitv54)
    HighestsbdSet(highestsbd, htfitv55)
    LowestsbuSet(lowestsbu, htfitv55)
    HighestsbdSet(highestsbd, htfitv56)
    LowestsbuSet(lowestsbu, htfitv56)
    HighestsbdSet(highestsbd, htfitv57)
    LowestsbuSet(lowestsbu, htfitv57)
    HighestsbdSet(highestsbd, htfitv58)
    LowestsbuSet(lowestsbu, htfitv58)
    HighestsbdSet(highestsbd, htfitv59)
    LowestsbuSet(lowestsbu, htfitv59)
    HighestsbdSet(highestsbd, htfitv60)
    LowestsbuSet(lowestsbu, htfitv60)

    fggetnowclose := true
    htfshadow.Shadowing(htfbase).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv1).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv2).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv3).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv4).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv5).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv6).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv7).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv8).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv9).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv10).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv11).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv12).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv13).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv14).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv15).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv16).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv17).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv18).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv19).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv20).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv21).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv22).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv23).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv24).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv25).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv26).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv27).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv28).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv29).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv30).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv31).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv32).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv33).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv34).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv35).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv36).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv37).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv38).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv39).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv40).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv41).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv42).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv43).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv44).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv45).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv46).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv47).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv48).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv49).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv50).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv51).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv52).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv53).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv54).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv55).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv56).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv57).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv58).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv59).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
    htfshadow.Shadowing(htfitv60).Monitor_Est().BOSJudge()
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
    if timeframe.period !="D"
        label.new(bar_index,close,"please change period to 1 Day")
//    label.new(bar_index,close, str.tostring(htfshadow.bosdata.sbu) + "\n" + htfitv8.settings.htf + "\n" +htfitv1.bosdata.s_dated + "\n" + "hello")

index += 1


