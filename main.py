//@version=5
indicator("`request.security_lower_tf()` Example", overlay = true)
var int buff1=na
buff1 := last_bar_index-2442
var float count = na
currentperiod = str.tonumber(timeframe.period)
currentperiod_div4 = currentperiod/4
currentperiod_div4_str = str.tostring(currentperiod_div4)
currentYear = year(time)
currentMon= month(time)
currentHour = hour(time)
currentMin = minute(time)
var float lasttime = na
var int HrMin2Min = na
var int HrMin2Min2 = na
var bool SizeFlag = na
var int Number_bar = na
var int sizearray = na
var bool GOFlag = false
var int buffyear = na
var int buffmonth = na
var int buffday = na
var int buffhour = na
var int buffmin = na
var int state = na
var int state2 = na
var float diff = na
var float barloop = na
var float Quotient = na
var float Remainder = na
var float RemainKbar = na
var float testint = na
var float testint2 = na
var float teststr = na
var float testbool = na
var float starttime = na
var const int hello = 1 
var const int FOREX_OANDATIME = 1020
var const int DAY2MINUTE = 1440
// If the current chart timeframe is set to 120 minutes, then the `arrayClose` array will contain two 'close' values from the 60 minute timeframe for each bar.
Quotient := math.floor(float(DAY2MINUTE)/currentperiod)
Remainder := DAY2MINUTE%currentperiod
arrClose = request.security_lower_tf(syminfo.tickerid, currentperiod_div4_str, close)
sizearray := array.size(arrClose)
SizeFlag := array.size(arrClose)==4? true : false
HrMin2Min := currentHour*60+currentMin
if(HrMin2Min<FOREX_OANDATIME and HrMin2Min>=0)
    HrMin2Min2 := HrMin2Min+DAY2MINUTE
else
    HrMin2Min2 := HrMin2Min
if(HrMin2Min2==FOREX_OANDATIME and GOFlag==false) //find the start point
    count := 0
    starttime := HrMin2Min2
    lasttime := FOREX_OANDATIME
    GOFlag := true
if(GOFlag)
    if(count==0 and HrMin2Min2!=FOREX_OANDATIME)
        state :=1
        count := 1+(HrMin2Min2-FOREX_OANDATIME)/currentperiod      
        diff := (HrMin2Min2-FOREX_OANDATIME)/currentperiod
        starttime := FOREX_OANDATIME + (count-1)*currentperiod
    else if(count==0 and HrMin2Min2==FOREX_OANDATIME)
        state := 2
        count := 1
        diff := 0
        starttime := HrMin2Min2
    else           
        //starttime := starttime + currentperiod
        if(starttime+currentperiod==HrMin2Min2)
            state := 3
            diff := 1         
            count := count+diff
            
            lasttime := starttime
            starttime := starttime+currentperiod
        else
            state := 4
            lasttime := starttime
            diff := (HrMin2Min2-lasttime)/currentperiod
            if(diff<0)
                RemainKbar := (FOREX_OANDATIME+currentperiod*Quotient-lasttime)/currentperiod
                testbool := lasttime
                GOFlag := false
                diff := na
                teststr := RemainKbar
            else
                count := count+diff
                lasttime := HrMin2Min2                        
                starttime := FOREX_OANDATIME+(count-1)*currentperiod       
    
    testint := count
    testint2 := diff
if(starttime == (FOREX_OANDATIME+currentperiod*Quotient))
    lasttime := FOREX_OANDATIME
    count := 0

if bar_index == last_bar_index - buff1
    //label.new(last_bar_index-buff1, high, str.tostring(arrClose),color = color.orange,size = size.normal)
    firstPrice = array.get(arrClose, 1)
    buffyear := year(time)
    buffmonth := month(time)
    buffday := dayofmonth(time) 
    buffhour := hour(time)
    buffmin := minute(time)
    label.new(last_bar_index-buff1, low, str.tostring(GOFlag)+"\n state: "+str.tostring(state)+"\n state2: "+str.tostring(state2)+"\n testint: "+str.tostring(testint)+"\n testint2: "+str.tostring(testint2)+"\n teststr : "+str.tostring(teststr)+"\n testbool : "+str.tostring(testbool),style=label.style_triangledown,color = color.green)
if bar_index == last_bar_index 
    label.new(last_bar_index, low, "\n label bufftime at : "+ str.tostring(buffyear)+ "\t" +str.tostring(buffmonth) +"\t" + str.tostring(buffday)+"\t" + str.tostring(buffhour)+"\t" + str.tostring(buffmin)+"\n\t testint=" + str.tostring(str.contains(syminfo.tickerid,"OANDA")),style=label.style_triangledown,color = color.green)
