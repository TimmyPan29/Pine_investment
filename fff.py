//@version=5
indicator("`request.security_lower_tf()` Example", overlay = true)

// If the current chart timeframe is set to 120 minutes, then the `arrayClose` array will contain two 'close' values from the 60 minute timeframe for each bar.
arrClose = request.security_lower_tf(syminfo.tickerid, "60", close)

if bar_index == last_bar_index - 1
    label.new(last_bar_index-1, high, str.tostring(arrClose))
    firstPrice = array.get(arrClose, 1)
    label.new(last_bar_index-1, high-500, str.tostring(firstPrice),style=label.style_triangledown,color = color.green)
