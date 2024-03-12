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
  *開3分鐘周期 OANDA會從5:03 or 6:03出來 取決夏令時間 夏令時間是三月第二個禮拜天開始
  *開2,1分鐘周期 OANDA會從5:04 or 6:04出來 
  *開4分鐘周期 OANDA會從5:04 or 6:04出來
  *開30s周期 OANDA會從5:04:30 or 6:04:30出來 
  *開5分鐘周期 OANDA會從5:00 or 6:00出來,跟其他週期有明顯差異
  **//
  
//**限制四倍週期之四條重疊線演算法
  *用case
  *用array
  *用state
  *看五點的第一根kbar 的分鐘 進而推算buff的array要多少 如果因為不能用動態矩陣的話 那麼一開始可以預設buff長度20，應該是不會有一開始的時間出現在20分鐘的
  *一件奇怪的事情 OANDA交易所在我3/13 夏令時間看 切換到交易所時區 開盤都是17:00 我在想是不是夏令時間一到 會自動把以前到現在的歷史數據的時間全部-1 變成相對時間 絕對時間還是18:00 但是看的話會變成17:00 
  *general 從8分鐘期開始到1440 , 4分週期要額外補5:00的值 用插值就好
  *以OANDA: saox Eightcap外匯 為例 且切換為台北時間
    夏令時間  禮拜一5:04開盤到隔天5:00 所以是24小時 禮拜日休息 所以一個禮拜的kbar，時間會走到禮拜六的5:00(就是4:59-5:00那根) 後來發現不一定從04分開始 也有從12分開始的
    非夏令時間 禮拜一6:04開盤到隔天6:00 所以是24小時 禮拜日休息 所以一個禮拜的kbar，時間會走到禮拜六的6:00(就是5:59-6:00那根)
  *以OANDA:加密貨幣比特幣美元為例 開4分鐘周期
    夏令時間  5:04開盤到隔天5:00 所以是24小時 禮拜日休息 所以一個禮拜的kbar，時間會走到禮拜六5:00(就是4:59-5:00那根)
    非夏令時間 6:04開盤到隔天6:00 所以是24小時 禮拜日休息 所以一個禮拜的kbar，時間會走到禮拜六6:00(就是5:59-6:00那根)
  *eightcap指數 在monday的開盤時間跟其他日子的開盤時間不一樣  指數的商品不一樣 就算交易平台相同 開盤收盤時間也會不同 禮拜一甚至會和禮拜二的開盤時間不一樣
    以台灣時間為例
    US Dollar index cash夏令時間是從禮拜一6:00開始到隔天的5點 23個小時 而禮拜二開始是8:00開始到隔天5點 只有21小時
    US Dollar index cash非夏令是從禮拜一7:00開始 到隔天6:00 所以是23個小時 而禮拜二開始是9:00到隔天6點
  *eightcap指數 日經225指數 ４分鐘線
    夏令時間是從禮拜一6:00開始到隔天的5:00, 23個小時 而禮拜二開始也是6:00開始到隔天5:00 
    非夏令是從禮拜一7:00開始 到隔天6:00 所以是23個小時 而禮拜二開始也是7:00到隔天6點
  *要大家從一個時間點開始我的時間計時器
  *k bar依據不同的商品，追溯到第一根kbar的日期有點不同 應該是因為每個商品的開盤收盤時間不盡相同 但是總kbar數應該是差不多的
    4分鐘的外匯k bar 以運作23小時來說 可以追溯到約三個月前
  *
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

//這樣寫可以隨時更新最新動態
//@version=5
indicator("array", overlay=true)
array<float> a = na
var int count = 0
var float b = na
var label testlabel = na
var int barcount = 0
barcount := barcount + 1
a := array.new<float>(2, 0)
array.push(a, 1)
if(barcount==last_bar_index-count+1)
    if(not na(testlabel))
        label.delete(testlabel)
    testlabel := label.new(x=last_bar_index-count, y=low, text="now k bar: " + str.tostring(last_bar_index-count+1)+"\n,,testint: "+ str.tostring(minute(time))+"\n,,teststr: "+str.tostring(dayofmonth(time))+"\n,,testbool: "+str.tostring(hour(time)),xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label.style_arrowup) 
//

//可以刷新所有矩陣裡面的元素值
//@version=5
indicator("array.fill example")
a = array.new_float(size,value)
array.fill(a, 0)
