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
    
if(state==4)
    if(na(mylabel)==false)
        label.delete(mylabel)
    mylabel := label.new(bar_index, high, text="k bar: " + str.tostring(bar_index+1), color=color.green) 
    if (na(myLine) == false)
        line.delete(myLine)
    myLine := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.red, style=line.style_solid)

    if(na(mylabel2)==false)
        label.delete(mylabel2)
    mylabel2 := label.new(bar_index-1, high, text="因為系統判定下一根還沒收盤\n所以判斷的地方落在這點 k bar" + str.tostring(bar_index), color=color.green) 
    if (na(myLine2) == false)
        line.delete(myLine2)
    myLine2 := line.new(x1=bar_index-1, y1=low, x2=bar_index-1, y2=high, width=1, color=color.red, style=line.style_solid)
    line.new(x1=1-100, y1=close_SBU, x2=1 + 100, y2=close_SBU, width=2, color=color.purple)
    line.new(x1=1-100, y1=close_SBD, x2=1 + 100, y2=close_SBD, width=2, color=color.purple)
    //line.new(x1=1-100, y1=Buff_close2, x2=1 + 100, y2=Buff_close2, width=2, color=color.yellow)
    //line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    //line.new(x1=1-100, y1=Buff_close3, x2=1 + 100, y2=Buff_close3, width=2, color=color.black)
    state := na

//**待增加事項
  *新增 Multi-Timeframe 
  *自通判斷當前時區
  *把他能多功一次畫很多級別
  *一小時做單 1 2 3 4為一個單位
  *二小時做單 2 4 6 8為一個單位
  *2D -> 2D 4D 6D 8D
  *21m -> 21 42 63 84
  *小時最多做到6小 6 12 18 24
  *FVG 有破才有用 
  *費波納氣
  *週期大的壓力比週期小的壓力強
  *週期大的支撐比週期小的支撐強
  *找到4H的bound的之後 找4H+1min or +2min 的基礎
  **//
    