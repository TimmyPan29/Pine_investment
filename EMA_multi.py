//@version=5
indicator(title="5Min period", overlay=true)

// 定義 EMA 的長度
emaLength = input(1, title="EMA Length")

// 獲取當前時間框架
current_tf = input("1", title="Current Timeframe")

// 計算新的時間框架（當前時間框架 + 5 分鐘）
new_tf_tx1 = na(timeframe.multiplier) ? 1 : timeframe.multiplier 
new_tf_tx2 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + timeframe.multiplier 
new_tf_tx3 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + timeframe.multiplier + timeframe.multiplier
new_tf_tx4 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + timeframe.multiplier + timeframe.multiplier + timeframe.multiplier
new_tf_25 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 25
new_tf_30 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 30
new_tf_35 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 35
new_tf_40 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 40
new_tf_45 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 45
new_tf_50 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 50
new_tf_55 = na(timeframe.multiplier) ? 1 : timeframe.multiplier + 55

// 獲取不同新時間框架下的 EMA 數據
ema_5 = request.security(syminfo.tickerid, str.tostring(new_tf_tx1), ta.ema(close, emaLength))
ema_10 = request.security(syminfo.tickerid, str.tostring(new_tf_tx2), ta.ema(close, emaLength))
ema_15 = request.security(syminfo.tickerid, str.tostring(new_tf_tx3), ta.ema(close, emaLength))
ema_20 = request.security(syminfo.tickerid, str.tostring(new_tf_tx4), ta.ema(close, emaLength))
ema_25 = request.security(syminfo.tickerid, str.tostring(new_tf_25), ta.ema(close, emaLength))
ema_30 = request.security(syminfo.tickerid, str.tostring(new_tf_30), ta.ema(close, emaLength))
ema_35 = request.security(syminfo.tickerid, str.tostring(new_tf_35), ta.ema(close, emaLength))
ema_40 = request.security(syminfo.tickerid, str.tostring(new_tf_40), ta.ema(close, emaLength))
ema_45 = request.security(syminfo.tickerid, str.tostring(new_tf_45), ta.ema(close, emaLength))
ema_50 = request.security(syminfo.tickerid, str.tostring(new_tf_50), ta.ema(close, emaLength))
ema_55 = request.security(syminfo.tickerid, str.tostring(new_tf_55), ta.ema(close, emaLength))


// 繪製不同新時間框架下的 EMA 線
plot(ema_5, color=color.blue, title="EMA MTF +t*1")
plot(ema_10, color=color.red, title="EMA MTF +t*2")
plot(ema_15, color=color.green, title="EMA MTF +t*3")
plot(ema_20, color=color.rgb(0, 255, 115), title="EMA MTF +t*4")
plot(ema_25, color=color.purple, title="EMA MTF +25")
plot(ema_30, color=color.blue, title="EMA MTF +30")
plot(ema_35, color=color.red, title="EMA MTF +35")
plot(ema_40, color=color.green, title="EMA MTF +40")
plot(ema_45, color=color.orange, title="EMA MTF +45")
plot(ema_50, color=color.purple, title="EMA MTF +50")
plot(ema_55, color=color.purple, title="EMA MTF +55")