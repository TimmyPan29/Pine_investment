//@version=5

//**變數
  *注意初始化
  *//

indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)
var int barCount = 0
var int slope1 = 0
var int slope2 = 0
var bool key2occur = na
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
  *三個點可造成轉折，所以三個點為判斷轉折的一個單位
  *// 

if (barCount == 1)
    close_SBU := close
    Buff_close1 := close //Buff_close1 is generated first
if (barCount == 2)
    close_SBD := close
    Buff_close2 := close
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
if (barcount == 3)

    Buff_close3 := close
    slope1 :=(Buff_close2-Buff_close1)>0? 1:-1
    slope2 := (Buff_close3-Buff_close2>0? 1:-1
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
        else //不會有此情況

//**向上突破 向下突破 待在空間中 三種情況
  *三種情況來寫判別式，且從第四根bar開始算，先滿足破，再滿足是否轉折點
  *//   

if((not barstate.islast) and (barCount!=1) and (barCount!=2) and (barCount!=3)) //從第四點開始
    isbreakSBU := close>close_SBU? true : false
    isbreakSBD := close<close_SBD? true : false
    Buff_close1 := Buff_close2
    Buff_close2 := Buff_close3
    Buff_close3 := close
    slope1 := slope2
    slope2 := Buff_close3-Buff_close2>0? 1:-1
    if(slope1 != slope2)
        

     
        turn_count := turn_count+1
        Buff_key1 := Buff_close2
    if(isbreakSBU && turn_count>1)
        if(slope1!=slope2) 
            Buff_key2 := Buff_close2
            close_SBU := Buff_key1>Buff_key2? Buff_key1:Buff_key2
            close_SBD := Buff_key1<Buff_key2? Buff_key1:Buff_key2
            Buff_key1 := Buff_key2
            Buff_key2 := na
            turn_count := 0
            isbreakSBU := false
            isbreakSBD := false
    if(isbreakSBD && turn_count>1)
        if(slope1!=slope2) 
            Buff_key2 := Buff_close2
            close_SBU := Buff_key1>Buff_key2? Buff_key1:Buff_key2
            close_SBD := Buff_key1<Buff_key2? Buff_key1:Buff_key2
            Buff_key1 := Buff_key2
            Buff_key2 := na
            turn_count := 0
            isbreakSBU := false
            isbreakSBD := false
    if(close_SBU>close>close_SBD) 
        if(slope1!=slope2)
            Buff_key1:=Buff_close2
        else //do nothing
    




        turn_count := turn_count+1
        Buff_key1 := Buff_close2
        slope1 := slope2
        slope2 := (close-Buff_close3)>0? 1:-1
    else
        slope1 := slope2
        slope2 := (close-Buff_close3)>0? 1:-1
    if (close>close_SBU)
        isbreakSBU := true
    else 
        if(close<close_SBD)
            isbreakSBD := true
        else //do nothing

