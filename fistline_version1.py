//@version=5
indicator("hr,week sbd sbu", shorttitle="BOSoneline", overlay=true)

////**參數
//  *自定義參數
//  *//

var int Number_bar = na

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
var int x = na
var int testint = 0
var string teststr = na

barCount := barCount+1

////**初始條件
//  *先處理前三個點,初始化SBD SBU
//  *// 

//*****custom option*****//
x := 1
//*****var initialization*****//

if (barCount == 1)
    Buff_close1 := close //Buff_close1 is generated first
    index_key1 := barCount-1
    Buff_key1 := Buff_close1
if (barCount == 2)
    Buff_close2 := close
    index_key2 := barCount-1
    close_SBU := Buff_close2>Buff_close1? Buff_close2:Buff_close1
    close_SBD := Buff_close2<Buff_close1? Buff_close2:Buff_close1
    if(Buff_close2 - Buff_close1 >0)
        index_SBD := index_key1
        index_SBU := barCount-1
    else
        index_SBU := index_key1
        index_SBD := barCount-1
    state := 1

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
    isbreakSBU := na(close_SBU)? na : close>close_SBU? true : false
    isbreakSBD := na(close_SBD)? na : close<close_SBD? true : false
    if(not na(Buff_close3))
        Buff_close1 := Buff_close2
        Buff_close2 := Buff_close3
    else
        Buff_close1 := Buff_close1
        Buff_close2 := Buff_close2
    Buff_close3 := close
    slope1 := Buff_close2-Buff_close1>0? 1:-1
    slope2 := Buff_close3-Buff_close2>0? 1:-1  
    //test := label.new(bar_index,close,text= "hello world")
    if((not na(close_SBD)) and (not na(close_SBU)))
        state := 3
    if(isbreakSBU or isbreakSBD)
        state := 2
    if(na(close_SBU) or na(close_SBD))
        state := 4

if(state==2)
    
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
        index_key1 := barCount-2
    //else //Buff_key1維持原樣
    if(isbreakSBU)

        close_SBU := na
        isbreakSBU := na
        close_SBD := Buff_key1
        index_SBD := index_key1
    if(isbreakSBD)

        close_SBD := na
        isbreakSBD := na
        close_SBU := Buff_key1
        index_SBU := index_key1
    state := 1
    if(bar_index==last_bar_index-x)                               
        state := 5

if(state==3)
    
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
        index_key1 := barCount-2
    else
        Buff_key1 := Buff_key1
    state := 1
    if(bar_index==last_bar_index-x)                                
        state := 5

if(state==4)

    if(slope1!=slope2)
        Buff_key2 := Buff_close2
        index_key2 := barCount-2
        if(na(isbreakSBU))
            close_SBU := Buff_key2
            index_SBU := index_key2
            isbreakSBU := false
        if(na(isbreakSBD))
            close_SBD := Buff_key2
            index_SBD := index_key2
            isbreakSBD := false
        Buff_key1 := Buff_key2
        index_key1 := index_key2
    //else //沒事發生 繼續沒界
    if(close>close_SBU)
        close_SBU := na
        isbreakSBU := na
    if(close<close_SBD)
        close_SBD := na
        isbreakSBD := na
    state := 1
    if(bar_index==last_bar_index-x)                                
        state := 5

if(state==5)
    if((not na(close_SBU)) and na(close_SBD)) // ⎻⎻📉
        index_SBU := index_key1
        index_SBD := na
    if((not na(close_SBD)) and na(close_SBU)) // __📈
        index_SBD := index_key1
        index_SBU := na

    if(na(mylabel)==false)
        label.delete(mylabel)
    mylabel := label.new(x=bar_index, y=low, text="now k bar: " + str.tostring(bar_index+1)+"\n tickertype: " + str.tostring(syminfo.type),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
    if (na(myLine) == false)
        line.delete(myLine)
    myLine := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    line.new(x1=index_SBU, y1=close_SBU, x2=index_SBU +100, y2=close_SBU, width=2, color=color.black)
    line.new(x1=index_SBD, y1=close_SBD, x2=index_SBD +100, y2=close_SBD, width=2, color=color.black)
    //line.new(x1=bar_index-1, y1=Buff_close2, x2=bar_index, y2=Buff_close2, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3, x2=1 + 100, y2=Buff_close3, width=2, color=color.black)

    if(na(label_SBU)==false)
        label.delete(label_SBU)
    label_SBU := label.new(x=index_SBU, y=close_SBU, text="SBU: " + str.tostring(close_SBU), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    if(na(label_SBD)==false)
        label.delete(label_SBD)
    label_SBD := label.new(x=index_SBD, y=close_SBD, text="SBD: " + str.tostring(close_SBD), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state := na

