#ifndef __PLOTPACK_MQH__
#define __PLOTPACK_MQH__
//+--------------------------------------------------------------------------------//
//+when declaring the struct, 
//-note that set the initial value : label la1 = {"fill name u want"}
//+--------------------------------------------------------------------------------//
struct label{
    string name;
    label(string n){name = n;}
    void Create(string name="templb", datetime x=0, double y=0, string text="somethinghappen", color textColor = clrBlack, int fontSize = 12, ENUM_ALIGN_MODE textAlign = ALIGN_CENTER, string fontType="Arial", bool bgshow=false, color bgColor = clrGray) {
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
        ObjectSetInteger(0, name, OBJPROP_HALIGNMENT, textAlign); 
        ObjectSetString(0, name, OBJPROP_TEXT, text);
        ObjectSetInteger(0, name, OBJPROP_FONT, "Arial"); 
        ObjectSetInteger(0, name, OBJPROP_BACK, bgshow); 
        ObjectSetInteger(0, name, OBJPROP_BACKGROUND_COLOR, bgColor); 
        ChartRedraw();
    }
    void set_xy(string name="templa", datetime x=0, double y=0){
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); 
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
    }
    void set_text(string name="templa", string text="you forgot to input text", color textColor = clrBlack, int fontSize = 12){
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
        ObjectSetString(0, name, OBJPROP_TEXT, text);
    }
};
struct line{
    string name;
    void Create(string name="templ", datetime time1=0, double price1=0, datetime time2=0, double price2=0, color clr=clrBlack) {
        if(ObjectFind(0, name) != -1) {
            ObjectDelete(0, name); // 删除同名对象
        }
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
        ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
        ChartRedraw();
    }
    void set_x1y1x2y2(string name="templ", datetime time1=0, double price1=0, datetime time2=0, double price2=0){
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
    }
    void set_color(string name="templ", color textColor = clrBlack){
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
    }
};








#endif