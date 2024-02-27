//@version=5

//**變數
//  *注意刷新sbd sbu後各項變數要初始化
//  *//

indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)
var int barCount = 0
var int slope1 = 0
var int slope2 = 0
var int state = na
var bool isbreakSBU = na
var bool isbreakSBD = na
var float close_SBU= na
var float close_SBD= na
var float Buff_close1 = na
var float Buff_close2 = na
var float Buff_close3 = na
var float Buff_key1 = na
var float Buff_key2 = na
barCount := barCount+1


//**初始條件
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

//**向上突破 向下突破 待在空間中 三種情況
//  *三種情況來寫判別式，且從第四根bar開始算，先滿足破，再滿足是否轉折點
//  *state2 : Buff_close2有突破且isbreak有跳起來
//  *state3 : state2的反
//  *state4 : end並畫圖
//  *破的轉點一律叫key2，缺少突破的控制訊號<
//  *//   

if(state==1 and barCount>3) //從第四點開始
    isbreakSBU := close>close_SBU? true : false
    isbreakSBU := Buff_close2>close_SBU? true : false
    isbreakSBD := close<close_SBD? true : false
    isbreakSBD := Buff_close2<close_SBD? true : false
    Buff_close1 := Buff_close2
    Buff_close2 := Buff_close3
    Buff_close3 := close
    slope1 := slope2
    slope2 := Buff_close3-Buff_close2>0? 1:-1
    if((isbreakSBU and (Buff_close2>close_SBU)) or (isbreakSBD and (Buff_close2<close_SBD)))
        state := 2
    else
        state := 3
    if(barCount==6)
        state := 4
if(state==2)
    if(slope1!=slope2) 
        Buff_key2 := Buff_close2
        if(Buff_key2>Buff_key1) //代表上破
            close_SBU := Buff_key2
            close_SBD := Buff_key1
            isbreakSBU := false
        else //下破
            close_SBD := Buff_key2
            close_SBU := Buff_key1
            isbreakSBD := false
        Buff_key1 := Buff_key2
        Buff_key2 := na
    else
        Buff_key2 := na
    state := 1
if(state==3)
    if(slope1!=slope2)
        Buff_key1 := Buff_close2
    else
        Buff_key1 := Buff_key1
    state := 1
if(state==4)
    line.new(x1=1-100, y1=close_SBU, x2=1 + 100, y2=close_SBU, width=2, color=color.purple)
    line.new(x1=1-100, y1=close_SBD, x2=1 + 100, y2=close_SBD, width=2, color=color.purple)
    line.new(x1=1-100, y1=Buff_close2, x2=1 + 100, y2=Buff_close2, width=2, color=color.yellow)
    line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    line.new(x1=1-100, y1=Buff_key2, x2=1 + 100, y2=Buff_key2, width=2, color=color.black)
