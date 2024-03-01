//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)

////**參數
//  *自定義參數
//  *//

var int Number_bar = 9

////**變數
//  *注意刷新sbd sbu後各項變數要初始化
//  *//
var int barCount = 0
var int slope1 = 0
var int slope2 = 0
var int state = na
var int index_key1 = 0
var int index_key2 = 0
var int index_SBU = na
var int index_SBD = na
var bool isbreakSBU = na
var bool isbreakSBD = na
var float close_SBU= na
var float close_SBD= na
var float Buff_close1 = na
var float Buff_close2 = na
var float Buff_close3 = na
var float Buff_key1 = na
var float Buff_key2 = na
var line myLine = na
var label mylabel  = na
var line myLine2 = na
var label mylabel2  = na
var label label_SBU = na
var label label_SBD = na
var label test = na

barCount := barCount+1

////**初始條件
//  *先處理前三個點,初始化SBD SBU
//  *// 

if (barCount == 1)
    close_SBU := close
    Buff_close1 := close //Buff_close1 is generated first
    Buff_key1 := Buff_close1
if (barCount == 2)
    close_SBD := close
    Buff_close2 := close
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
    state := 2

////**向上突破 向下突破 待在空間中 三種情況
//  *三種情況來寫判別式，且從第三根bar開始算，先滿足破，再滿足是否轉折點
//  *state1 : 狀態控制 以close 以及有無破
//  *state2 : 有界轉破變成沒界 
//  *state3 : 有界維持 包在裡面
//  *state4 : 沒界維持 或 沒界轉有界
//  *state5 : end並畫圖
//  *破的轉點一律叫key2，缺少突破的控制訊號
//  *支撐被破之後 SBU要馬上跟上，而在嚴格遞減的情況下，此時的SBD不可以長出來 
//  *//   

if(state==1 and barCount>2) //從第三點開始
    isbreakSBU := close>close_SBU? true : false
    isbreakSBD := close<close_SBD? true : false
    Buff_close1 := Buff_close2
    Buff_close2 := Buff_close3
    Buff_close3 := close
    slope1 := slope2
    slope2 := Buff_close3-Buff_close2>0? 1:-1  
    //test := label.new(bar_index,close,text= "hello world")
    if(isbreakSBU or isbreakSBD)
        state := 2
    else
        state := 3
    if(na(close_SBU) or na(close_SBD))
        state := 4

if(state==2)
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
        index_key1 := barCount-1
    //else //Buff_key1維持原樣
    if(isbreakSBU)
        close_SBU := na
        isbreakSBU := na
        close_SBD := Buff_key1
    if(isbreakSBD)
        close_SBD := na
        isbreakSBD := na
        close_SBU := Buff_key1
    state := 1
    if(barstate.islast)                               
        state := 5

if(state==3)
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
        index_key1 := barCount-1
    else
        Buff_key1 := Buff_key1
    state := 1
    if(barstate.islast)                                
        state := 5

if(state==4)
    if(slope1!=slope2)
        Buff_key2 := Buff_close2
        index_key2 := barCount-1
        if(na(isbreakSBU))
            close_SBU := Buff_key2
            index_SBU := index_key2
            isbreakSBU := false
        if(na(isbreakSBD))
            close_SBD := Buff_key2
            index_SBD := index_key2
            isbreakSBD := false
    //else //沒事發生 繼續沒界
    state := 1
    if(barstate.islast)                                
        state := 5

if(state==5)
    if(not na(close_SBU) and na(close_SBD)) // ⎻⎻📉
        index_SBU := index_key1
        index_SBD := na
    if(not na(close_SBD) and na(close_SBU)) // __📈
        index_SBD := index_key1
        index_SBU := na

    if(na(mylabel)==false)
        label.delete(mylabel)
    mylabel := label.new(x=bar_index, y=low, text="now k bar: " + str.tostring(bar_index+1),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
    if (na(myLine) == false)
        line.delete(myLine)
    myLine := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    line.new(x1=index_SBU-1, y1=close_SBU, x2=index_SBU +100, y2=close_SBU, width=2, color=color.black)
    line.new(x1=index_SBD-1, y1=close_SBD, x2=index_SBD +100, y2=close_SBD, width=2, color=color.black)
    //line.new(x1=1-100, y1=Buff_close2, x2=1 + 100, y2=Buff_close2, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3, x2=1 + 100, y2=Buff_close3, width=2, color=color.black)

    if(na(label_SBU)==false)
        label.delete(label_SBU)
    label_SBU := label.new(x=index_SBU-1, y=close_SBU, text="SBU: " + str.tostring(close_SBU), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    if(na(label_SBD)==false)
        label.delete(label_SBD)
    label_SBD := label.new(x=index_SBD-1, y=close_SBD, text="SBD: " + str.tostring(close_SBD), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state := na

