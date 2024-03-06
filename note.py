barstate.islast
barstate.isfirst

 label.new(bar_index[1], close_SBU, text="SBU: " + str.tostring(close_SBU), style=label.style_cross, color=color.green, size=size.normal)
label.new(bar_index[2], close_SBD, text="SBD: " + str.tostring(close_SBD), style=label.style_cross, color=color.red, size=size.normal)

注意！ 每個Ｋ圖代表執行腳本一次 用var的用意是在每個Ｋ圖產生時（從左至右）會保持原來的值

line.new(x1=1-100, y1=close_SBU, x2=1 + 100, y2=close_SBU, width=2, color=color.purple)
    line.new(x1=1-100, y1=close_SBD, x2=1 + 100, y2=close_SBD, width=2, color=color.purple)
    line.new(x1=1-100, y1=Buff_close2, x2=1 + 100, y2=Buff_close2, width=2, color=color.yellow)
    line.new(x1=1-100, y1=Buff_key1, x2=1 + 100, y2=Buff_key1, width=2, color=color.orange)
    
line.new(x1=barCount-100, y1=close_SBU, x2=barCount + 100, y2=close_SBU, width=2, color=color.purple)
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
  *大週期切小週期來分析 最後匯入小週期的ｋ線 
  *L388 L391需要註釋
  *舉例一分鐘周期線 3:20跑完1分鐘後到3:21,此時3:20的k bar才會長出來
  *trading view如果以折線圖且收盤價來看 Kbar鉛直線對下來的叫做起跑線
  *也許我可以用一根Kbar長出來的時間當作計數器來做判斷式的依據
  *必須想一個辦法來做元素1,2,3的算法
  **//

close_1over4 = array.get(Reqclose, 0)
close_2over4 = array.get(Reqclose, 1)
close_3over4 = array.get(Reqclose, 2)

//@version=5
indicator("`request.security_lower_tf()` Example", overlay = true)

// If the current chart timeframe is set to 120 minutes, then the `arrayClose` array will contain two 'close' values from the 60 minute timeframe for each bar.
arrClose = request.security_lower_tf(syminfo.tickerid, "60", close)

if bar_index == last_bar_index - 1
    label.new(last_bar_index-1, high, str.tostring(arrClose))
    firstPrice = array.get(arrClose, 1)
    label.new(last_bar_index-1, high-500, str.tostring(firstPrice),style=label.style_triangledown,color = color.green)
    
//@version=5
indicator("My Kbar Example", overlay=true)

// 请求特定周期的开、高、低、收价格
timeframe = "D" // 例如，使用日周期
openPrice = request.security(syminfo.tickerid, timeframe, open)
highPrice = request.security(syminfo.tickerid, timeframe, high)
lowPrice = request.security(syminfo.tickerid, timeframe, low)
closePrice = request.security(syminfo.tickerid, timeframe, close)

// 绘制K线图
plotcandle(openPrice, highPrice, lowPrice, closePrice, title="K-Bar")

//getyear
currentYear = year(time)

//tonumber
currentperiod = timeframe.period
currentperiod_div4 = str.tostring(str.tonumber(currentperiod)/4)