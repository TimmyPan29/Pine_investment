# Python script to generate the Pine Script code
output = ""

for i in range(60, 91):
    output += f"""var CandleSet htfadd{i}                     = CandleSet.new()
var CandleSettings SettingsHTFadd{i}        = CandleSettings.new()
var Candle[] candlesadd{i}                  = array.new<Candle>(0)
var BOSdata bosdataadd{i}                   = BOSdata.new()

htfadd{i}.settings                 := SettingsHTFadd{i}
htfadd{i}.candles                  := candlesadd{i}
htfadd{i}.bosdata                  := bosdataadd{i}
htfadd{i}.settings.htf             := '{i}'
htfadd{i}.settings.max_memory      := 10
htfadd{i}.Monitor().BOSJudge()
if barstate.islast or barstate.isrealtime
    HighestsbdSet(highestsbd, htfadd{i})
    LowestsbuSet(lowestsbu, htfadd{i}) 
    MaxNormalSet(maxnormal, htfadd{i})
    MinNormalSet(minnormal, htfadd{i})
"""
print(output)



