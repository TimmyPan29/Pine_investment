#ifndef __PLOTPACK_MQH__
#define __PLOTPACK_MQH__
//+--------------------------------------------------------------------------------//
//+when declaring the struct, 
//-note that set the initial value : label la1 = {"fill name u want"}
//+--------------------------------------------------------------------------------//
struct label{
    string name1;
    label(string n){name1 = n;}
    void Create(string name ="templb", datetime x=0, double y=0, string text="somethinghappen", color textColor = clrBlack, int fontSize = 12, ENUM_ALIGN_MODE textAlign = ALIGN_CENTER, string fontType="Arial", bool bgshow=false, color bgColor = clrGray) {
        if(ObjectFind(0, name) != -1) {
            ObjectDelete(0, name); // 删除同名对象
        }
        // 创建标签对象
        ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
        ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_RIGHT_UPPER); 
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); 
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y); 
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor); 
        ObjectSetInteger(0, name, OBJPROP_ALIGN, textAlign); 
        ObjectSetString (0, name, OBJPROP_TEXT, text);
        ObjectSetString (0, name, OBJPROP_FONT, fontType); 
        ObjectSetInteger(0, name, OBJPROP_BACK, bgshow); 
        ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor); 
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
    void set_text(string name="templa", string text="you forgot to input text", color textColor = clrBlack, int fontSize = 12){
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
        ObjectSetString(0, name, OBJPROP_TEXT, text);
        ChartRedraw();
    }
    void set_color(string name="templa", color textColor = clrBlack){
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
        ChartRedraw();
    }
    
};
struct line{
    string name1;
    line(string n){name1 = n;}
    void Create(string name="templ", datetime time1=0, double price1=0, datetime time2=0, double price2=0, color clr=clrBlack) {
        if(ObjectFind(0, name) != -1) {
            ObjectDelete(0, name); // 删除同名对象
        }
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
        ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
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
    void set_color(string name="templ", color textColor = clrBlack){
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
    }
};


#endif

