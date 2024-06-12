# Python script to generate the Pine Script code
output = ""

for i in range(1, 31):
    output += f"""if  htf{i}.settings.show and helper.ValidTimeframe(htf{i}.settings.htf) 
    htf{i}.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf{i}.Monitor_Est().BOSJudge()
        plotdata(htf{i}, offset, delta)
    cnt +=1
"""
print(output)



