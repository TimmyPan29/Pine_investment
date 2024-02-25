//@version=5
indicator("Last Bar Close Line", shorttitle="LBC", overlay=true)

// 当处理最后一根K线时
if barstate.islast
    // 绘制一条水平线表示收盘价
    line.new(x1=bar_index, y1=close, x2=bar_index[3000], y2=close, width=3, color=color.blue, style=line.style_solid)