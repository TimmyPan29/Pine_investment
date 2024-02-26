//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)
var int barCount = 0
var int slope = na
var int isbreakSBU =na
var int isbreakSBD =na
var float close_SBU=na
var float close_SBD=na
float Buff_close1 =na
float Buff_close2 =na
barCount := barCount+1
if (barCount == 1)
    close_SBU := close
    Buff_close1 := close
    
if (barCount == 2)
    close_SBD := close
    Buff_close2 := close
    slope:=(Buff_close2-Buff_close1)>0? 1:-1
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
    label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
    label.new(bar_index[0], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)
if((not barstate.islast) and (barCount!=1) and barCount!=2)
    if (close>close_SBU)
        