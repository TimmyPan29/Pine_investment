barstate.islast
barstate.isfirst

 label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
    label.new(bar_index[2], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)

注意！ 每個Ｋ圖代表執行腳本一次 用var的用意是在每個Ｋ圖產生時（從左至右）會保持原來的值
