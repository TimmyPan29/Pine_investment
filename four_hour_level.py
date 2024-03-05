//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)

////**參數
//  *自定義參數
//  *//
currentperiod = timeframe.period
currentperiod_div4 = str.tostring(str.tonumber(currentperiod)/4)
currentYear = year(time)
var int Number_bar = 3

////**4over4變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *//
var int slope1_4over4 = 0
var int slope2_4over4 = 0
var int state_4over4 = na
var int index_key1_4over4 = 0
var int index_key2_4over4 = 0
var int index_SBU_4over4 = na
var int index_SBD_4over4 = na
var bool isbreakSBU_4over4 = na
var bool isbreakSBD_4over4 = na
var float close_SBU_4over4= na
var float close_SBD_4over4= na
var float Buff_close1_4over4 = na
var float Buff_close2_4over4 = na
var float Buff_close3_4over4 = na
var float Buff_key1_4over4 = na
var float Buff_key2_4over4 = na
var line Line_Bar_4over4 = na
var label Label_Bar_4over4  = na
var label Label_SBU_4over4 = na
var label Label_SBD_4over4 = na

////**1over4變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *
var int slope1_1over4 = 0
var int slope2_1over4 = 0
var int state_1over4 = na
var int index_key1_1over4 = 0
var int index_key2_1over4 = 0
var int index_SBU_1over4 = na
var int index_SBD_1over4 = na
var bool isbreakSBU_1over4 = na
var bool isbreakSBD_1over4 = na
var float close_SBU_1over4= na
var float close_SBD_1over4= na
var float Buff_close1_1over4 = na
var float Buff_close2_1over4 = na
var float Buff_close3_1over4 = na
var float Buff_key1_1over4 = na
var float Buff_key2_1over4 = na
var line Line_Bar_1over4 = na
var label Label_Bar_1over4  = na
var label Label_SBU_1over4 = na
var label Label_SBD_1over4 = na

////**2over4變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *
var int slope1_2over4 = 0
var int slope2_2over4 = 0
var int state_2over4 = na
var int index_key1_2over4 = 0
var int index_key2_2over4 = 0
var int index_SBU_2over4 = na
var int index_SBD_2over4 = na
var bool isbreakSBU_2over4 = na
var bool isbreakSBD_2over4 = na
var float close_SBU_2over4= na
var float close_SBD_2over4= na
var float Buff_close1_2over4 = na
var float Buff_close2_2over4 = na
var float Buff_close3_2over4 = na
var float Buff_key1_2over4 = na
var float Buff_key2_2over4 = na
var line Line_Bar_2over4 = na
var label Label_Bar_2over4  = na
var label Label_SBU_2over4 = na
var label Label_SBD_2over4 = na

////**3over4變數區
//  *注意刷新sbd sbu後各項變數要初始化
//  *
var int slope1_3over4 = 0
var int slope2_3over4 = 0
var int state_3over4 = na
var int index_key1_3over4 = 0
var int index_key2_3over4 = 0
var int index_SBU_3over4 = na
var int index_SBD_3over4 = na
var bool isbreakSBU_3over4 = na
var bool isbreakSBD_3over4 = na
var float close_SBU_3over4= na
var float close_SBD_3over4= na
var float Buff_close1_3over4 = na
var float Buff_close2_3over4 = na
var float Buff_close3_3over4 = na
var float Buff_key1_3over4 = na
var float Buff_key2_3over4 = na
var line Line_Bar_3over4 = na
var label Label_Bar_3over4  = na
var label Label_SBU_3over4 = na
var label Label_SBD_3over4 = na
////**測試變數區
//  *
//  *//
var label test = na
var int testint = 0
var string teststr = na

////**共同變數區
//  *
//  *//
var int BarCountBuff = na
var bool BarCountFlag = na
var int BarCount = 0

////**初始條件
//  *先處理前三個點,初始化SBD SBU
//  *// 
ReqClose = request.security_lower_tf(syminfo.tickerid, currentperiod_div4, close)
close_1over4 = array.get(ReqClose,0)
close_2over4 = array.get(ReqClose,1)
close_3over4 = array.get(ReqClose,2)
close_4over4 = array.get(ReqClose,3)

BarCount := BarCount+1
if(currentYear==2010 and BarCountFlag==true)
    BarCountBuff := BarCount
    BarCountFlag := false
if(currentYear>2009)
if (BarCount == 1)
    Buff_close1_4over4 := close //Buff_close1_4over4 is generated first
    index_key1_4over4 := BarCount-1
    Buff_key1_4over4 := Buff_close1_4over4
    
    Buff_close1_2over4 := close_2over4 //Buff_close1_120 is generated first
    index_key1_2over4 := BarCount-1
    Buff_key1_2over4 := Buff_close1_2over4
    
if (BarCount == 2)
    Buff_close2_4over4 := close
    index_key2_4over4 := BarCount-1
    close_SBU_4over4 := Buff_close2_4over4>Buff_close1_4over4? Buff_close2_4over4:Buff_close1_4over4
    close_SBD_4over4 := Buff_close2_4over4<Buff_close1_4over4? Buff_close2_4over4:Buff_close1_4over4
    if(Buff_close2_4over4 - Buff_close1_4over4 >0)
        index_SBD_4over4 := index_key1_4over4
        index_SBU_4over4 := BarCount-1
    else
        index_SBU_4over4 := index_key1_4over4
        index_SBD_4over4 := BarCount-1
    state_4over4 := 1

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

if(state_4over4==1 and BarCount>2) //從第三點開始
    isbreakSBU_4over4 := na(close_SBU_4over4)? na : close>close_SBU_4over4? true : false
    isbreakSBD_4over4 := na(close_SBD_4over4)? na : close<close_SBD_4over4? true : false
    if(not na(Buff_close3_4over4))
        Buff_close1_4over4 := Buff_close2_4over4
        Buff_close2_4over4 := Buff_close3_4over4
    else
        Buff_close1_4over4 := Buff_close1_4over4
        Buff_close2_4over4 := Buff_close2_4over4
    Buff_close3_4over4 := close
    slope1_4over4 := Buff_close2_4over4-Buff_close1_4over4>0? 1:-1
    slope2_4over4 := Buff_close3_4over4-Buff_close2_4over4>0? 1:-1  
    //test := label.new(bar_index,close,text= "hello world")
    if((not na(close_SBD_4over4)) and (not na(close_SBU_4over4)))
        state_4over4 := 3
    if(isbreakSBU_4over4 or isbreakSBD_4over4)
        state_4over4 := 2
    if(na(close_SBU_4over4) or na(close_SBD_4over4))
        state_4over4 := 4

if(state_4over4==2)
    
    if(slope1_4over4!=slope2_4over4)
        teststr := "im hereerere"
        Buff_key1_4over4 := Buff_close2_4over4
        index_key1_4over4 := BarCount-2
    //else //Buff_key1維持原樣
    if(isbreakSBU_4over4)

        close_SBU_4over4 := na
        isbreakSBU_4over4 := na
        close_SBD_4over4 := Buff_key1_4over4
        index_SBD_4over4 := index_key1_4over4
    if(isbreakSBD_4over4)

        close_SBD_4over4 := na
        isbreakSBD_4over4 := na
        close_SBU_4over4 := Buff_key1_4over4
        index_SBU_4over4 := index_key1_4over4
    state_4over4 := 1
    if(BarCount==Number_bar)                               
        state_4over4 := 5

if(state_4over4==3)
    
    if(slope1_4over4!=slope2_4over4)
        Buff_key1_4over4 := Buff_close2_4over4
        index_key1_4over4 := BarCount-2
    else
        Buff_key1_4over4 := Buff_key1_4over4
    state_4over4 := 1
    if(BarCount==Number_bar)                                
        state_4over4 := 5

if(state_4over4==4)

    if(slope1_4over4!=slope2_4over4)
        Buff_key2_4over4 := Buff_close2_4over4
        index_key2_4over4 := BarCount-2
        if(na(isbreakSBU_4over4))
            close_SBU_4over4 := Buff_key2_4over4
            index_SBU_4over4 := index_key2_4over4
            isbreakSBU_4over4 := false
        if(na(isbreakSBD_4over4))
            close_SBD_4over4 := Buff_key2_4over4
            index_SBD_4over4 := index_key2_4over4
            isbreakSBD_4over4 := false
        Buff_key1_4over4 := Buff_key2_4over4
        index_key1_4over4 := index_key2_4over4
    //else //沒事發生 繼續沒界
    if(close>close_SBU_4over4)
        close_SBU_4over4 := na
        isbreakSBU_4over4 := na
    if(close<close_SBD_4over4)
        close_SBD_4over4 := na
        isbreakSBD_4over4 := na
    state_4over4 := 1
    if(BarCount==Number_bar)                                
        state_4over4 := 5

if(state_4over4==5)
    if((not na(close_SBU_4over4)) and na(close_SBD_4over4)) // ⎻⎻📉
        index_SBU_4over4 := index_key1_4over4
        index_SBD_4over4 := na
    if((not na(close_SBD_4over4)) and na(close_SBU_4over4)) // __📈
        index_SBD_4over4 := index_key1_4over4
        index_SBU_4over4 := na

    if(na(Label_Bar_4over4)==false)
        label.delete(Label_Bar_4over4)
    Label_Bar_4over4 := label.new(x=bar_index, y=low, text="now k bar: " + str.tostring(bar_index+1)+"\n,,testint: "+ str.tostring(close_2over4)+",,teststr: "+str.tostring(teststr),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
    if (na(Line_Bar_4over4) == false)
        line.delete(Line_Bar_4over4)
    Line_Bar_4over4 := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    line.new(x1=index_SBU_4over4, y1=close_SBU_4over4, x2=index_SBU_4over4 +100, y2=close_SBU_4over4, width=2, color=color.black)
    line.new(x1=index_SBD_4over4, y1=close_SBD_4over4, x2=index_SBD_4over4 +100, y2=close_SBD_4over4, width=2, color=color.black)
    //line.new(x1=bar_index-1, y1=Buff_close2_4over4, x2=bar_index, y2=Buff_close2_4over4, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1_4over4, x2=1 + 100, y2=Buff_key1_4over4, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3_4over4, x2=1 + 100, y2=Buff_close3_4over4, width=2, color=color.black)

    if(na(Label_SBU_4over4)==false)
        label.delete(Label_SBU_4over4)
    Label_SBU_4over4 := label.new(x=index_SBU_4over4, y=close_SBU_4over4, text="SBU: " + str.tostring(close_SBU_4over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    if(na(Label_SBD_4over4)==false)
        label.delete(Label_SBD_4over4)
    Label_SBD_4over4 := label.new(x=index_SBD_4over4, y=close_SBD_4over4, text="SBD: " + str.tostring(close_SBD_4over4), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state_4over4 := na

