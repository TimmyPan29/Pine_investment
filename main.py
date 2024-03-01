//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)

////**參數
//  *自定義參數
//  *//

var int Number_bar = 9
var string currenperiod = timeframe.period
var string DcurrentPeriod = "1D"
var string HcurrentPeriod = "60" 
var string OneMincurrentPeriod = "1" 
if(DcurrentPeriod==currenperiod)
    DcurrentPeriod := timeframe.period
if(HcurrentPeriod==currenperiod)
    HcurrentPeriod := timeframe.period
if(OneMincurrentPeriod==currenperiod)
    OneMincurrentPeriod := timeframe.period

////**變數
//  *注意刷新sbd sbu後各項變數要初始化
//  *//
var int barCount = 0
var int slope1 = 0
var int slope2 = 0
var int state = na
var bool isbreakSBU = na
var bool isbreakSBD = na
var bool isbreak = na
var float close_SBU= na
var float close_SBD= na
var float Buff_close1 = na
var float Buff_close2 = na
var float Buff_close3 = na
var float Buff_key1 = na
var float Buff_key2 = na
var line OneMinLine1 = na
var line OneMinLine2 = na
var line OneMinLine3 = na
var line HLine1 = na
var line HLine2 = na
var line HLine3 = na

var label OneMinLabel1  = na
var label HLabel1  = na

var label OneMinlabel_SBU = na
var label OneMinlabel_SBD = na
var label Hlabel_SBU = na
var label Hlabel_SBD = na

barCount := barCount+1

////**初始條件
//  *先處理前三個點,初始化SBD SBU
//  *// 

if (barCount == 1)
    close_SBU := close
    Buff_close1 := close //Buff_close1 is generated first
if (barCount == 2)
    close_SBD := close
    Buff_close2 := close
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
if (barCount == 3)
    state :=1 
    Buff_close3 := close
    slope1 := Buff_close2-Buff_close1>0? 1:-1
    slope2 := Buff_close3-Buff_close2>0? 1:-1
    if(Buff_close3>close_SBU)
        isbreakSBU := true
        if(slope1!=slope2)
            Buff_key1:=Buff_close2 //第一次轉折點出現
        else
            Buff_key1:=Buff_close1
    if(Buff_close3<close_SBD)
        isbreakSBD := true
        if(slope1!=slope2)
            Buff_key1:=Buff_close2 //第一次轉折點出現
        else
            Buff_key1:=Buff_close1
    else//包在裡面
        if(slope1!=slope2)
            Buff_key1:=Buff_close2 //第一次轉折點出現

////**向上突破 向下突破 待在空間中 三種情況
//  *三種情況來寫判別式，且從第四根bar開始算，先滿足破，再滿足是否轉折點
//  *state2 : Buff_close2有突破且isbreak有跳起來
//  *state3 : state2的反
//  *state4 : end並畫圖
//  *破的轉點一律叫key2，缺少突破的控制訊號
//  *支撐被破之後 SBU要馬上跟上，而在嚴格遞減的情況下，此時的SBD不可以長出來 
//  *//   

if(state==1 and barCount>3) //從第四點開始
    isbreakSBU := close>close_SBU? true : false
    isbreakSBD := close<close_SBD? true : false
    if(isbreakSBU or isbreakSBD)
        isbreak := true
    Buff_close1 := Buff_close2
    Buff_close2 := Buff_close3
    Buff_close3 := close
    slope1 := slope2
    slope2 := Buff_close3-Buff_close2>0? 1:-1
    if(isbreak)
        state := 2
    else
        state := 3

if(state==2)
    if(slope1!=slope2) 
        Buff_key2 := Buff_close2
        if(Buff_key2>Buff_key1) //代表上破
            close_SBU := Buff_key2
            close_SBD := Buff_key1
            isbreakSBU := na
        else //下破
            close_SBD := Buff_key2
            close_SBU := Buff_key1
            isbreakSBD := na
        Buff_key1 := Buff_key2
        Buff_key2 := na
        isbreak := na
    else
        if(isbreakSBU)
            close_SBD := Buff_key1
            close_SBU := na
        if(isbreakSBD)
            close_SBU := Buff_key1
            close_SBD := na
        Buff_key2 := na
    state := 1
    if(barstate.islast)                               
        state := 4

if(state==3)
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
    else
        Buff_key1 := Buff_key1
    state := 1
    if(barstate.islast)                                
        state := 4

if(state==4 and OneMincurrentPeriod==currenperiod) //1min

    OneMinLabel1 := label.new(x=bar_index, y=low, text="k bar: " + str.tostring(bar_index+1),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 

    OneMinLine1 := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    OneMinLine2 := line.new(x1=bar_index-1, y1=close_SBU, x2=bar_index +100, y2=close_SBU, width=2, color=color.black)
    OneMinLine3 := line.new(x1=bar_index-1, y1=close_SBD, x2=bar_index +100, y2=close_SBD, width=2, color=color.black)

    OneMinlabel_SBU := label.new(x=bar_index, y=close_SBU, text=currenperiod+"SBU: " + str.tostring(close_SBU), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    OneMinlabel_SBD := label.new(x=bar_index, y=close_SBD, text="SBD: " + str.tostring(close_SBD), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state := na
    

if(state==4 and HcurrentPeriod==currenperiod) //1H

    HLabel1 := label.new(x=bar_index, y=low, text="k bar: " + str.tostring(bar_index+1),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 

 
    HLine1 := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    HLine2 := line.new(x1=bar_index-1, y1=close_SBU, x2=bar_index +100, y2=close_SBU, width=2, color=color.black)
    HLine3 := line.new(x1=bar_index-1, y1=close_SBD, x2=bar_index +100, y2=close_SBD, width=2, color=color.black)
  
 
    Hlabel_SBU := label.new(x=bar_index, y=close_SBU, text=currenperiod+"SBU: " + str.tostring(close_SBU), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

  
    Hlabel_SBD := label.new(x=bar_index, y=close_SBD, text="SBD: " + str.tostring(close_SBD), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state := na

