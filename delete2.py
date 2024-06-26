# Python script to generate the Pine Script code
output = ""
for i in range(1, 61):
    output += f"""var CandleSet htfitv{i}                     = CandleSet.new()
var CandleSettings Settingshtfitv{i}        = CandleSettings.new(htf=str_itv{i},htfint=int_itv{i},max_memory=3,htfintdivD=int_itv{i}/1440)
var Candle[] candlesitv{i}                  = array.new<Candle>(0)
var BOSdata bosdataitv{i}                   = BOSdata.new()
htfitv{i}.settings                         := Settingshtfitv{i}
htfitv{i}.candles                          := candlesitv{i}
htfitv{i}.bosdata                          := bosdataitv{i}
"""
print(f"{output}")