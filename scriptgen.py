# Python script to generate the Pine Script code
output = ""

for i in range(1350, 1441):
    output += f"""var CandleSet htfadd{i}                     = CandleSet.new()
var CandleSettings SettingsHTFadd{i}        = CandleSettings.new(htf='{i}',htfint={i},max_memory=3)
var Candle[] candlesadd{i}                  = array.new<Candle>(0)
var BOSdata bosdataadd{i}                   = BOSdata.new()
htfadd{i}.settings                 := SettingsHTFadd{i}
htfadd{i}.candles                  := candlesadd{i}
htfadd{i}.bosdata                  := bosdataadd{i}
"""
print(output)

output = ""
for i in range(1350, 1441):
    output += f"""htfadd{i}.Monitor().BOSJudge()
"""
print(f"{output}")

output = ""
for i in range(1350, 1441):
    output += f"""    HighestsbdSet(highestsbd, htfadd{i})
    LowestsbuSet(lowestsbu, htfadd{i})
"""
print(f"if bar_index == last_bar_index\n{output}")

output = ""
for i in range(1350, 1441):
    output += f"""    htfshadow.Shadowing(htfadd{i}).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
"""
print(f"{output}")

output = "fggetnowclose := false"
print(f"\t{output}")
