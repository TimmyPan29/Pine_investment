# Python script to generate the Pine Script code
output = ""

for i in range(60, 91):
    output += f"""HighestsbdSet(highestsbd, htfadd{i})
LowestsbuSet(lowestsbu, htfadd{i}) 
MaxNormalSet(maxnormal, htfadd{i})
MinNormalSet(minnormal, htfadd{i})
"""
print(output)



