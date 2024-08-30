#ifndef __PLOTPACK_MQH__
#define __PLOTPACK_MQH__
//+--------------------------------------------------------------------------------//
//+when declaring the struct, 
//-note that set the initial value : label la1 = {"fill name u want"}
//+--------------------------------------------------------------------------------//
struct label{
    string name1;
    label(string n){name1 = n;}
    void Create(const long chart_ID=0, string name ="templb", datetime x=0, double y=0, string text="somethinghappen", color textColor = clrMagenta, int fontSize = 12, int textAnckor = ANCHOR_RIGHT_LOWER, int textAlign= ALIGN_CENTER, string fontType="Arial", bool bgshow=false, color bgColor = clrGray) {
        if(ObjectFind(chart_ID, name) != -1) {
            ObjectDelete(chart_ID, name); // 删除同名对象
        }
        // 创建标签对象
        ObjectCreate(chart_ID, name, OBJ_TEXT, 0, x, y);
        ObjectSetInteger(chart_ID, name, OBJPROP_XDISTANCE, x); 
        ObjectSetInteger(chart_ID, name, OBJPROP_YDISTANCE, y); 
        ObjectSetInteger(chart_ID, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(chart_ID, name, OBJPROP_COLOR, textColor); 
        ObjectSetInteger(chart_ID, name, OBJPROP_ALIGN, textAlign); 
        ObjectSetString (chart_ID, name, OBJPROP_TEXT, text);
        ObjectSetString (chart_ID, name, OBJPROP_FONT, fontType); 
        ObjectSetInteger(chart_ID, name, OBJPROP_BACK, bgshow); 
        ObjectSetInteger(chart_ID, name, OBJPROP_BGCOLOR, bgColor);
        ObjectSetInteger(chart_ID, name, OBJPROP_ANCHOR, textAnckor);
        ChartRedraw();
    }
    bool set_xy(const long chart_ID=0, string name="templa", const int point_index=0, datetime x=0, double y=0){
        if(!x) x=TimeCurrent();  
        if(!y) y=SymbolInfoDouble(Symbol(),SYMBOL_BID); 
//--- 重置错误的值 
        ResetLastError(); 
//--- 移动趋势线定位点   
        if(!ObjectMove(chart_ID,name,point_index,x,y)){ 
            Print(__FUNCTION__, ": failed to move the anchor point! Error code = ",GetLastError()); 
            return(false); 
        } 
//--- 成功执行 
        return(true); 
    }  
    void set_text(const long chart_ID=0, string name="templa", string text="you forgot to input text", color textColor = clrMagenta, int fontSize = 12){
        ObjectSetInteger(chart_ID, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(chart_ID, name, OBJPROP_COLOR, textColor);
        ObjectSetString(chart_ID, name, OBJPROP_TEXT, text);
        ChartRedraw();
    }
    void set_color(const long chart_ID=0, string name="templa", color textColor = clrBlack){
        ObjectSetInteger(chart_ID, name, OBJPROP_COLOR, textColor);
        ChartRedraw();
    }
    
};
struct line{
    string name1;
    line(string n){name1 = n;}
    void Create(const long chart_ID=0, string name="templ", datetime time1=0, double price1=0, datetime time2=0, double price2=0, color clr=clrBlack) {
        if(ObjectFind(chart_ID, name) != -1) {
            ObjectDelete(chart_ID, name); // 删除同名对象
        }
        ObjectCreate(chart_ID, name, OBJ_TREND, 0, time1, price1, time2, price2);
        ObjectSetInteger(chart_ID, name, OBJPROP_COLOR, clr);
        ObjectSetInteger(chart_ID, name, OBJPROP_WIDTH, 2);
        ChartRedraw();
    }
    bool set_xy(const long chart_ID=0, string name="templa", const int point_index=0, datetime x=0, double y=0){
        if(!x) x=TimeCurrent(); 
        if(!y) y=SymbolInfoDouble(Symbol(),SYMBOL_BID); 
        ResetLastError(); 
        if(!ObjectMove(chart_ID,name,point_index,x,y)){ 
            Print(__FUNCTION__, ": failed to move the anchor point! Error code = ",GetLastError()); 
            return(false); 
        } 
        return(true); 
    }  
    void set_color(const long chart_ID=0, string name="templ", color textColor = clrBlack){
        ObjectSetInteger(chart_ID, name, OBJPROP_COLOR, textColor);
    }
};


#endif

