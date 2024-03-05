//@version=5
indicator("`request.security_lower_tf()` Example", overlay = true)
var int buff1=na
buff1 := 11
currentperiod = timeframe.period
currentperiod_div4 = str.tostring(str.tonumber(currentperiod)/4)
currentYear = year(time)
currentMon= month(time)
var bool SizeFlag = na
var int Number_bar = 7

// If the current chart timeframe is set to 120 minutes, then the `arrayClose` array will contain two 'close' values from the 60 minute timeframe for each bar.
arrClose = request.security_lower_tf(syminfo.tickerid, currentperiod_div4, close)
SizeFlag := array.size(arrClose)==4? true : false
if bar_index == last_bar_index - buff1
    label.new(last_bar_index-buff1, high, str.tostring(arrClose))
    firstPrice = array.get(arrClose, 1)
   // label.new(last_bar_index-buff1, low, str.tostring(SizeFlag),style=label.style_triangledown,color = color.green)