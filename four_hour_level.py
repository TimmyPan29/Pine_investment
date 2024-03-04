//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)

////**參數
//  *自定義參數
//  *//

var int Number_bar = 3

////**240變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *//

var int BarCount = 0
var int slope1_240 = 0
var int slope2_240 = 0
var int state_240 = na
var int index_key1_240 = 0
var int index_key2_240 = 0
var int index_SBU_240 = na
var int index_SBD_240 = na
var bool isbreakSBU_240 = na
var bool isbreakSBD_240 = na
var float close_SBU_240= na
var float close_SBD_240= na
var float Buff_close1_240 = na
var float Buff_close2_240 = na
var float Buff_close3_240 = na
var float Buff_key1_240 = na
var float Buff_key2_240 = na
var line Line_Bar_240 = na
var label Label_Bar_240  = na
var label Label_SBU_240 = na
var label Label_SBD_240 = na

////**120變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *
var int slope1_120 = 0
var int slope2_120 = 0
var int state_120 = na
var int index_key1_120 = 0
var int index_key2_120 = 0
var int index_SBU_120 = na
var int index_SBD_120 = na
var bool isbreakSBU_120 = na
var bool isbreakSBD_120 = na
var float close_SBU_120= na
var float close_SBD_120= na
var float Buff_close1_120 = na
var float Buff_close2_120 = na
var float Buff_close3_120 = na
var float Buff_key1_120 = na
var float Buff_key2_120 = na
var line Line_Bar_120 = na
var label Label_Bar_120  = na
var label Label_SBU_120 = na
var label Label_SBD_120 = na

////**測試變數區
//  *
//  *//

var label test = na
var int testint = 0
var string teststr = na

////**初始條件
//  *先處理前三個點,初始化SBD SBU
//  *// 
Reqclose = request.security_lower_tf(syminfo.tickerid, "60", close)
close_120 = array.get(Reqclose, 1)
BarCount := BarCount+1

if (BarCount == 1)
    Buff_close1_240 := close //Buff_close1_240 is generated first
    index_key1_240 := BarCount-1
    Buff_key1_240 := Buff_close1_240
    
    Buff_close1_120 := close_120 //Buff_close1_120 is generated first
    index_key1_120 := BarCount-1
    Buff_key1_120 := Buff_close1_120
    
if (BarCount == 2)
    Buff_close2_240 := close
    index_key2_240 := BarCount-1
    close_SBU_240 := Buff_close2_240>Buff_close1_240? Buff_close2_240:Buff_close1_240
    close_SBD_240 := Buff_close2_240<Buff_close1_240? Buff_close2_240:Buff_close1_240
    if(Buff_close2_240 - Buff_close1_240 >0)
        index_SBD_240 := index_key1_240
        index_SBU_240 := BarCount-1
    else
        index_SBU_240 := index_key1_240
        index_SBD_240 := BarCount-1
    state_240 := 1

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

if(state_240==1 and BarCount>2) //從第三點開始
    isbreakSBU_240 := na(close_SBU_240)? na : close>close_SBU_240? true : false
    isbreakSBD_240 := na(close_SBD_240)? na : close<close_SBD_240? true : false
    if(not na(Buff_close3_240))
        Buff_close1_240 := Buff_close2_240
        Buff_close2_240 := Buff_close3_240
    else
        Buff_close1_240 := Buff_close1_240
        Buff_close2_240 := Buff_close2_240
    Buff_close3_240 := close
    slope1_240 := Buff_close2_240-Buff_close1_240>0? 1:-1
    slope2_240 := Buff_close3_240-Buff_close2_240>0? 1:-1  
    //test := label.new(bar_index,close,text= "hello world")
    if((not na(close_SBD_240)) and (not na(close_SBU_240)))
        state_240 := 3
    if(isbreakSBU_240 or isbreakSBD_240)
        state_240 := 2
    if(na(close_SBU_240) or na(close_SBD_240))
        state_240 := 4

if(state_240==2)
    
    if(slope1_240!=slope2_240)
        teststr := "im hereerere"
        Buff_key1_240 := Buff_close2_240
        index_key1_240 := BarCount-2
    //else //Buff_key1維持原樣
    if(isbreakSBU_240)

        close_SBU_240 := na
        isbreakSBU_240 := na
        close_SBD_240 := Buff_key1_240
        index_SBD_240 := index_key1_240
    if(isbreakSBD_240)

        close_SBD_240 := na
        isbreakSBD_240 := na
        close_SBU_240 := Buff_key1_240
        index_SBU_240 := index_key1_240
    state_240 := 1
    if(BarCount==Number_bar)                               
        state_240 := 5

if(state_240==3)
    
    if(slope1_240!=slope2_240)
        Buff_key1_240 := Buff_close2_240
        index_key1_240 := BarCount-2
    else
        Buff_key1_240 := Buff_key1_240
    state_240 := 1
    if(BarCount==Number_bar)                                
        state_240 := 5

if(state_240==4)

    if(slope1_240!=slope2_240)
        Buff_key2_240 := Buff_close2_240
        index_key2_240 := BarCount-2
        if(na(isbreakSBU_240))
            close_SBU_240 := Buff_key2_240
            index_SBU_240 := index_key2_240
            isbreakSBU_240 := false
        if(na(isbreakSBD_240))
            close_SBD_240 := Buff_key2_240
            index_SBD_240 := index_key2_240
            isbreakSBD_240 := false
        Buff_key1_240 := Buff_key2_240
        index_key1_240 := index_key2_240
    //else //沒事發生 繼續沒界
    if(close>close_SBU_240)
        close_SBU_240 := na
        isbreakSBU_240 := na
    if(close<close_SBD_240)
        close_SBD_240 := na
        isbreakSBD_240 := na
    state_240 := 1
    if(BarCount==Number_bar)                                
        state_240 := 5

if(state_240==5)
    if((not na(close_SBU_240)) and na(close_SBD_240)) // ⎻⎻📉
        index_SBU_240 := index_key1_240
        index_SBD_240 := na
    if((not na(close_SBD_240)) and na(close_SBU_240)) // __📈
        index_SBD_240 := index_key1_240
        index_SBU_240 := na

    if(na(Label_Bar_240)==false)
        label.delete(Label_Bar_240)
    Label_Bar_240 := label.new(x=bar_index, y=low, text="now k bar: " + str.tostring(bar_index+1)+"\n,,testint: "+ str.tostring(Buff_key1_240)+",,teststr: "+str.tostring(teststr),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
    if (na(Line_Bar_240) == false)
        line.delete(Line_Bar_240)
    Line_Bar_240 := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    line.new(x1=index_SBU_240, y1=close_SBU_240, x2=index_SBU_240 +100, y2=close_SBU_240, width=2, color=color.black)
    line.new(x1=index_SBD_240, y1=close_SBD_240, x2=index_SBD_240 +100, y2=close_SBD_240, width=2, color=color.black)
    //line.new(x1=bar_index-1, y1=Buff_close2_240, x2=bar_index, y2=Buff_close2_240, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1_240, x2=1 + 100, y2=Buff_key1_240, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3_240, x2=1 + 100, y2=Buff_close3_240, width=2, color=color.black)

    if(na(Label_SBU_240)==false)
        label.delete(Label_SBU_240)
    Label_SBU_240 := label.new(x=index_SBU_240, y=close_SBU_240, text="SBU: " + str.tostring(close_SBU_240), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    if(na(Label_SBD_240)==false)
        label.delete(Label_SBD_240)
    Label_SBD_240 := label.new(x=index_SBD_240, y=close_SBD_240, text="SBD: " + str.tostring(close_SBD_240), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state_240 := na

