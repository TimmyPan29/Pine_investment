# Python script to generate the Pine Script code
output = ""

for i in range(1, 31):
    output += f"""htf{i}.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF{i}    ", inline='htflevel{i}', group="trace")
htf{i}.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel{i}', group="trace")
htf{i}.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel{i}', group="trace")
"""
print(output)



