# Python script to generate the Pine Script code
output = ""
for i in range(2, 61):
    output += f"htfshadow.Shadowing(htfitv{i}).Monitor_Est().BOSJudge()\n"
    output += f"Predictor(htfshadow, estminsbu)\n"
    output += f"Predictor(htfshadow, estmaxsbd)\n"
print(output)
