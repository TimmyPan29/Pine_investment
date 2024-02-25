islast
//@version=5
indicator("Last Bar Close", shorttitle="LBC", overlay=true)

// 在數據集的最後一筆數據上標記收盤價
if (barstate.islast)
    label.new(bar_index, close, text="Last Close: " + str.tostring(close), style=label.style_cross, color=color.blue, yloc=yloc.belowbar)
