//@version=5
indicator("hr,week sbd sbu", shorttitle="SB", overlay=true)
var int slope = na
var int isbreakSBU =na
var int isbreakSBD =na
var float close_SBU=na
var float close_SBD=na
float Buff_close_when_turn_occur=na
for var i=0 to 1 
if (barCount == 0)
    close_SBU := close
    
if (barCount == 1)
    close_SBD := close
    close_SBU := close_SBU>close_SBD? close_SBU:close_SBD
    close_SBD := close_SBU>close_SBD? close_SBD:close_SBU
    label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
    label.new(bar_index[0], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)


