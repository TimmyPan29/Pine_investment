barstate.islast
barstate.isfirst

 label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
    label.new(bar_index[2], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)

注意！ 每個Ｋ圖代表執行腳本一次 用var的用意是在每個Ｋ圖產生時（從左至右）會保持原來的值

line.new(x1=1-100, y1=close_SBU, x2=1 + 100, y2=close_SBU, width=2, color=color.purple)
    line.new(x1=1-100, y1=close_SBD, x2=1 + 100, y2=close_SBD, width=2, color=color.purple)
    line.new(x1=1-100, y1=Buff_close2, x2=1 + 100, y2=Buff_close2, width=2, color=color.yellow)
    line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    
ine.new(x1=barCount-100, y1=close_SBU, x2=barCount + 100, y2=close_SBU, width=2, color=color.purple)
    line.new(x1=barCount-100, y1=close_SBD, x2=barCount + 100, y2=close_SBD, width=2, color=color.purple)
    line.new(x1=barCount-100, y1=Buff_close2, x2=barCount + 100, y2=Buff_close2, width=2, color=color.yellow)
    line.new(x1=barCount-100, y1=Buff_key1, x2=barCount + 100, y2=Buff_key1, width=2, color=color.orange)