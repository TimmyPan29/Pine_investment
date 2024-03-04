if (BarCount == 1)
    Buff_close1_120 := close //Buff_close1_120 is generated first
    index_key1_120 := BarCount-1
    Buff_key1_120 := Buff_close1_120
    
if (BarCount == 2)
    Buff_close2_120 := close
    index_key2_120 := BarCount-1
    close_SBU_120 := Buff_close2_120>Buff_close1_120? Buff_close2_120:Buff_close1_120
    close_SBD_120 := Buff_close2_120<Buff_close1_120? Buff_close2_120:Buff_close1_120
    if(Buff_close2_120 - Buff_close1_120 >0)
        index_SBD_120 := index_key1_120
        index_SBU_120 := BarCount-1
    else
        index_SBU_120 := index_key1_120
        index_SBD_120 := BarCount-1
    state_120 := 1

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

if(state_120==1 and BarCount>2) //從第三點開始
    isbreakSBU_120 := na(close_SBU_120)? na : close>close_SBU_120? true : false
    isbreakSBD_120 := na(close_SBD_120)? na : close<close_SBD_120? true : false
    if(not na(Buff_close3_120))
        Buff_close1_120 := Buff_close2_120
        Buff_close2_120 := Buff_close3_120
    else
        Buff_close1_120 := Buff_close1_120
        Buff_close2_120 := Buff_close2_120
    Buff_close3_120 := close
    slope1_120 := Buff_close2_120-Buff_close1_120>0? 1:-1
    slope2_120 := Buff_close3_120-Buff_close2_120>0? 1:-1  
    //test := label.new(bar_index,close,text= "hello world")
    if((not na(close_SBD_120)) and (not na(close_SBU_120)))
        state_120 := 3
    if(isbreakSBU_120 or isbreakSBD_120)
        state_120 := 2
    if(na(close_SBU_120) or na(close_SBD_120))
        state_120 := 4

if(state_120==2)
    
    if(slope1_120!=slope2_120)
        teststr := "im hereerere"
        Buff_key1_120 := Buff_close2_120
        index_key1_120 := BarCount-2
    //else //Buff_key1維持原樣
    if(isbreakSBU_120)

        close_SBU_120 := na
        isbreakSBU_120 := na
        close_SBD_120 := Buff_key1_120
        index_SBD_120 := index_key1_120
    if(isbreakSBD_120)

        close_SBD_120 := na
        isbreakSBD_120 := na
        close_SBU_120 := Buff_key1_120
        index_SBU_120 := index_key1_120
    state_120 := 1
    if(BarCount==Number_bar)                               
        state_120 := 5

if(state_120==3)
    
    if(slope1_120!=slope2_120)
        Buff_key1_120 := Buff_close2_120
        index_key1_120 := BarCount-2
    else
        Buff_key1_120 := Buff_key1_120
    state_120 := 1
    if(BarCount==Number_bar)                                
        state_120 := 5

if(state_120==4)

    if(slope1_120!=slope2_120)
        Buff_key2_120 := Buff_close2_120
        index_key2_120 := BarCount-2
        if(na(isbreakSBU_120))
            close_SBU_120 := Buff_key2_120
            index_SBU_120 := index_key2_120
            isbreakSBU_120 := false
        if(na(isbreakSBD_120))
            close_SBD_120 := Buff_key2_120
            index_SBD_120 := index_key2_120
            isbreakSBD_120 := false
        Buff_key1_120 := Buff_key2_120
        index_key1_120 := index_key2_120
    //else //沒事發生 繼續沒界
    if(close>close_SBU_120)
        close_SBU_120 := na
        isbreakSBU_120 := na
    if(close<close_SBD_120)
        close_SBD_120 := na
        isbreakSBD_120 := na
    state_120 := 1
    if(BarCount==Number_bar)                                
        state_120 := 5

if(state_120==5)
    if((not na(close_SBU_120)) and na(close_SBD_120)) // ⎻⎻📉
        index_SBU_120 := index_key1_120
        index_SBD_120 := na
    if((not na(close_SBD_120)) and na(close_SBU_120)) // __📈
        index_SBD_120 := index_key1_120
        index_SBU_120 := na

    if(na(Label_Bar_120)==false)
        label.delete(Label_Bar_120)
    Label_Bar_120 := label.new(x=bar_index, y=low, text="now k bar: " + str.tostring(bar_index+1)+"\n,,testint: "+ str.tostring(Buff_key1_120)+",,teststr: "+str.tostring(teststr),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
    if (na(Line_Bar_120) == false)
        line.delete(Line_Bar_120)
    Line_Bar_120 := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)

    line.new(x1=index_SBU_120, y1=close_SBU_120, x2=index_SBU_120 +100, y2=close_SBU_120, width=2, color=color.black)
    line.new(x1=index_SBD_120, y1=close_SBD_120, x2=index_SBD_120 +100, y2=close_SBD_120, width=2, color=color.black)
    //line.new(x1=bar_index-1, y1=Buff_close2_120, x2=bar_index, y2=Buff_close2_120, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1_120, x2=1 + 100, y2=Buff_key1_120, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3_120, x2=1 + 100, y2=Buff_close3_120, width=2, color=color.black)

    if(na(Label_SBU_120)==false)
        label.delete(Label_SBU_120)
    Label_SBU_120 := label.new(x=index_SBU_120, y=close_SBU_120, text="SBU: " + str.tostring(close_SBU_120), xloc = xloc.bar_index,yloc=yloc.price,color=color.red) 

    if(na(Label_SBD_120)==false)
        label.delete(Label_SBD_120)
    Label_SBD_120 := label.new(x=index_SBD_120, y=close_SBD_120, text="SBD: " + str.tostring(close_SBD_120), xloc = xloc.bar_index,yloc=yloc.price,color=color.red,style = label.style_label_up) 
    state_120 := na

