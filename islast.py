islast
//@version=5
indicator("Last Bar Close", shorttitle="LBC", overlay=true)

// 在數據集的最後一筆數據上標記收盤價
if (barstate.islast)
    label.new(bar_index, close, text="Last Close: " + str.tostring(close), style=label.style_cross, color=color.blue, yloc=yloc.belowbar)


//@version=5
indicator("Last Bar Close Line", shorttitle="LBC", overlay=true)

// 当处理最后一根K线时
if barstate.islast
    // 绘制一条水平线表示收盘价
    line.new(x1=bar_index,text="Last Close: " + str.tostring(close),y1=close, x2=bar_index, y2=close, width=1, color=color.blue, style=line.style_solid)
