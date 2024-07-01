#ifndef __PLOTPACK_MQH__
#define __PLOTPACK_MQH__
//+--------------------------------------------------------------------------------//
//+when declaring the struct, 
//-note that set the initial value : label la1 = {"fill name u want"}
//+--------------------------------------------------------------------------------//
struct label{
    string name;
    int ObjectSetFont(string fontType) {
        if(fontType == "Arial") return OBJPROP_FONT_ARIAL;
        if(fontType == "Times New Roman") return OBJPROP_FONT_TIMES_NEW_ROMAN;
        if(fontType == "Courier New") return OBJPROP_FONT_COURIER_NEW;
        // Add more fonts if needed
        return OBJPROP_FONT_ARIAL; // Default font
    }
    void new(string name="templa", datetime x, double y, string text, color textColor = clrBlack, int fontSize = 12, ENUM_ALIGN_MODE textAlign = ALIGN_CENTER, string fontType, bool bgshow, color bgColor = clrGray) {
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
        ObjectSetInteger(0, name, OBJPROP_FONT, ObjectSetFont(fontType)); 
        ObjectSetInteger(0, name, OBJPROP_BACK, bgshow); 
        ObjectSetInteger(0, name, OBJPROP_BACKGROUND_COLOR, bgColor); 
        ChartRedraw();
    }
    void set_xy(string name="templa", datetime x, double y){
        ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); 
        ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y); 
    void set_text(string name="templa", string text="you forgot to input text", color textColor = clrBlack, int fontSize = 12){
        ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize); 
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
        ObjectSetString(0, name, OBJPROP_TEXT, text);
    }
};
struct line{
    string name;
    void new(string name="templ", datetime time1, double price1, datetime time2, double price2, color clr) {
        if(ObjectFind(0, name) != -1) {
            ObjectDelete(0, name); // 删除同名对象
        }
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
        ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
        ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
        ChartRedraw();
    }
    void set_x1y1x2y2(0, name="templ", datetime time1, double price1, datetime time2, double price2){
        ObjectCreate(0, name, OBJ_TREND, 0, time1, price1, time2, price2);
    }
    void set_color(0, name="templ", color textColor = clrBlack){
        ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
    }
};








#endif