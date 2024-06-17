# Python script to generate the Pine Script code
output = ""
for i in range(2, 91):
    output += f"""    htfshadow.Shadowing(htfadd{i}).Monitor_Est().BOSJudge()
    Predictor(htfshadow, estminsbu)
    Predictor(htfshadow, estmaxsbd)
"""
print(output)