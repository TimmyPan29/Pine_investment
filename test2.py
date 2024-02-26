//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)
var int barCount = 0
var int slope1 = 0
var int slope2 = 0
var int turn_count =0
var bool isbreakSBU =na
var bool isbreakSBD =na
var float close_SBU=na
var float close_SBD=na
var float Buff_close1 =na
var float Buff_close2 =na
var float Buff_close3 =na
barCount := barCount+1
if (barCount == 1)
    close_SBU := close
    Buff_close1 := close //Buff_close1 is generated first
    
if (barCount == 2)
    close_SBD := close
    Buff_close2 := close
    slope1:=(Buff_close2-Buff_close1)>0? 1:-1
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
    label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
    label.new(bar_index[0], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)
if((not barstate.islast) and (barCount!=1) and barCount!=2)
    Buff_close1 := Buff_close2
    Buff_close2 := close
    slope2 := (Buff_close2-Buff_close1>0? 1:-1
    if(slope1!=slope2)
        turn_count := turn_count+1
    if (close>close_SBU)
        isbreakSBU := true
    else 
        if(close<close_SBD)
            isbreakSBD := true
        else //do nothing

