# Python script to generate the Pine Script code
output = ""
for i in range(0, 60):
    output += f"""{i},"""
print(f"[{output}]")