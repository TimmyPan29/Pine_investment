//@version=5
indicator("input.time", overlay=true)
i_date = input.time(timestamp("20 Jul 2021 00:00 +0000"))
l = label.new(bar_index, high, text=str.tostring(i_date)+"\n"+str.format("{0,date,yyyy-MM-dd HH:mm}", i_date))

