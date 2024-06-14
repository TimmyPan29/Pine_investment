//@version=5
indicator("hr,week sbd sbu", shorttitle="BOSoneline_ver2", overlay=true)
//
////**參數
//  *自定義參數
//  *//////////

var int Number_bar = na

////**變數
//  *注意刷新sbd sbu後各項變數要初始化
//  *//
type BOS_Type
    int index_key1 = 0
    int index_key2 = 0
    int index_SBU = 0
    int index_SBD = 0
    float close_SBU= 0
    float close_SBD= 0
    float Buff_close1 = 0
    float Buff_close2 = 0
    float Buff_close3 = 0
    float Buff_key1 = 0
    float Buff_key2 = 0    
    int slope1 = 0
    int slope2 = 0
//end type
var int x = na
var int state = 1
var int index = 0
var line myLine = na
var label mylabel  = na
var line myLinesbu = na
var line myLinesbd = na
var label mylabel2  = na
var label label_SBU = na
var label label_SBD = na
var label test = na

var float testfloat1 = na
var int testint = 0
var string teststr = na

var BOS_Type BOS = BOS_Type.new()

//*****custom option*****//
x := 0
//*****var initialization*****//
if bar_index <= last_bar_index
    if(state == 1) //從第一個close開始
        BOS.Buff_close1 := BOS.Buff_close2
        BOS.Buff_close2 := BOS.Buff_close3
        BOS.Buff_close3 := close
        BOS.slope1 := BOS.Buff_close2-BOS.Buff_close1>0? 1:-1
        BOS.slope2 := BOS.Buff_close3-BOS.Buff_close2>0? 1:-1   
        //test := label.new(bar_index,close,text= "hello world")
        if((not na(BOS.close_SBD)) and (not na(BOS.close_SBU)))
            state := 2
        else if(not na(BOS.close_SBD) and na(BOS.close_SBU))
            state := 3
        else if(na(BOS.close_SBD) and (not na(BOS.close_SBU)))
            state := 4
        else
            "GG"
    if(state==2)
        if(BOS.slope1 != BOS.slope2)
            BOS.Buff_key1 := BOS.Buff_close2
            BOS.index_key1 := bar_index==0? 0 : index - 1
        //else //Buff_key1維持原樣
        if(BOS.Buff_close3>BOS.close_SBU)
            BOS.close_SBU := na
            BOS.index_SBU := na
            BOS.close_SBD := BOS.Buff_key1
            BOS.index_SBD := BOS.index_key1
        if(BOS.Buff_close3<BOS.close_SBD)
            BOS.close_SBD := na 
            BOS.index_SBD := na
            BOS.close_SBU := BOS.Buff_key1
            BOS.index_SBU := BOS.index_key1
        state := 1
        
    if(state==3)
        if(BOS.slope1 != BOS.slope2)
            BOS.Buff_key2 := BOS.Buff_close2
            BOS.index_key2 := index-1
            BOS.close_SBU := BOS.Buff_key2
            BOS.index_SBU := BOS.index_key2
            BOS.Buff_key1 := BOS.Buff_key2
            BOS.index_key1 := BOS.index_key2
        if(BOS.Buff_close3<BOS.close_SBD)
            BOS.close_SBD := na
            BOS.index_SBD := na
        state := 1
        
    if(state==4)
        if(BOS.slope1 != BOS.slope2)
            BOS.Buff_key2 := BOS.Buff_close2
            BOS.index_key2 := index-1
            BOS.close_SBD := BOS.Buff_key2
            BOS.index_SBD := BOS.index_key2
            BOS.Buff_key1 := BOS.Buff_key2
            BOS.index_key1 := BOS.index_key2
        if(BOS.Buff_close3>BOS.close_SBU)
            BOS.close_SBU := na
            BOS.index_SBU := na
        state := 1
    
//    if((not na(close_SBU)) and na(close_SBD)) // ⎻⎻📉
//    if((not na(close_SBD)) and na(close_SBU)) // __📈
    if barstate.isrealtime
        if(not na(mylabel))
            label.set_xy(mylabel, bar_index, low)
        else
            mylabel := label.new(x=bar_index, y=low, text="now k bar: " + str.   tostring(index+1)+"\n tickerid: " + str.tostring(syminfo.tickerid)+"\n typeis: " + str.tostring(syminfo.type),   xloc=xloc.bar_index,yloc = yloc.belowbar, color=color.black,style = label. style_arrowup)
        if (not na(myLine))
            line.set_xy1(myLine, bar_index, low)
            line.set_xy2(myLine, bar_index, high)
        else
            myLine := line.new(x1=bar_index, y1=low, x2=bar_index, y2=high, width=1, color=color.black, style=line.style_solid)
        
        if(not na(myLinesbu))
            line.set_xy1(myLinesbu,BOS.index_SBU,BOS.close_SBU)
            line.set_xy2(myLinesbu,BOS.index_SBU+100,BOS.close_SBU)
        else
            myLinesbu := line.new(x1=BOS.index_SBU, y1=BOS.close_SBU, x2=BOS.index_SBU+100, y2=BOS.close_SBU, width=2, color=color.black)
        if(not na(myLinesbd))
            line.set_xy1(myLinesbd,BOS.index_SBD,BOS.close_SBD)
            line.set_xy2(myLinesbd,BOS.index_SBD+100,BOS.close_SBD)
        else
            myLinesbd := line.new(x1=BOS.index_SBD, y1=BOS.close_SBD, x2=BOS.index_SBD+100, y2=BOS.close_SBD, width=2, color=color.black)
        
        if(na(label_SBU)==false)
            label.delete(label_SBU)
        label_SBU := label.new(x=BOS.index_SBU, y=BOS.close_SBU, text="SBU: " + str.tostring(BOS.close_SBU), xloc = xloc.bar_index,yloc=yloc.price,color=color.blue) 
        if(na(label_SBD)==false)
            label.delete(label_SBD)
        label_SBD := label.new(x=BOS.index_SBD, y=BOS.close_SBD, text="SBD: " + str.tostring(BOS.close_SBD), xloc = xloc.bar_index,yloc=yloc.price,color=color.blue,style = label.style_label_up) 
index += 1

