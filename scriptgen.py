# Python script to generate the Pine Script code
output = ""

for i in range(1, 121):
    output += f"""Predictor(htfadd{i}, estminsbu)
Predictor(htfadd{i}, estmaxsbd)
"""
print(output)


