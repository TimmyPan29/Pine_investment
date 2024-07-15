#include "Bos.mqh"
//+------------------------------------------------------------------+
//|                                                      MyScript.mq5|
//|                        Copyright 2024, MyName                    |
//|                                     www.mywebsite.com            |
//+------------------------------------------------------------------+
#property script_show_inputs

//+------------------------------------------------------------------+
//| input                                                     
//+------------------------------------------------------------------+
input int datasize = 1000 ;
int starti      = datasize-1;
int firstflag   = true ;
Fetcher fc ;
BOS bosdata ;

//+------------------------------------------------------------------+
//| initiation                                                       
//+------------------------------------------------------------------+
int OnInit() {
    EventSetTimer(5);
    bosdata = BOS(PeriodSeconds(_Period)/60);
    Print("EA has been initialized.");
    Print("PeriodSeconds(_Period)/60= ",PeriodSeconds(_Period)/60);
    Print("Info: ", AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", _Symbol);
    fc.Setarrsize(datasize);
    
    // Print("price@starti: ",fc.Getpriceinfo(starti)," date@starti: ",fc.Getdateinfo(starti));
    // Print("price@0: ",fc.Getpriceinfo(0)," date@0: ",fc.Getdateinfo(0));
    // Print("rd.rawprices[5]= ", rd.rawprices[5]);
    // printf("sbu= %.6f\t sbd= %.6f\n sbu_t= %s\t sbd_t= %s", bosdata.sbu, bosdata.sbd, TimeToString(bosdata.sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(bosdata.sbd_t,TIME_DATE|TIME_MINUTES) );
    // Print("bosdata.regclose3: ",bosdata.regclose3," bosdata.regclose3_t: ",bosdata.regclose3_t);
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//|main                                                         
//+------------------------------------------------------------------+
void OnTimer() {
    fc.Getprice(_Symbol, datasize);
    fc.Getdate(_Symbol, datasize); 
    Rawdatagroup rd = fc.GetRaw();
    BOSJudge(bosdata, datasize, rd, starti);
    if(firstflag){
        bosdata.sbu_lb.Create(0, bosdata.sbu_lb.name1, bosdata.sbu_t, bosdata.sbu, "sbu:"+DoubleToString(bosdata.sbu, 5), clrMagenta, 12, ANCHOR_RIGHT_LOWER, ALIGN_CENTER, "Arial", false, clrGray);
        bosdata.sbd_lb.Create(0, bosdata.sbd_lb.name1, bosdata.sbd_t, bosdata.sbd, "sbd:"+DoubleToString(bosdata.sbd, 5), clrMagenta, 12, ANCHOR_RIGHT_LOWER, ALIGN_CENTER, "Arial", false, clrGray);
        bosdata.sbu_ln.Create(0, bosdata.sbu_ln.name1, bosdata.sbu_t, bosdata.sbu, bosdata.sbu_t+(TimeCurrent()-bosdata.sbu_t), bosdata.sbu, clrMediumVioletRed);
        bosdata.sbd_ln.Create(0, bosdata.sbd_ln.name1, bosdata.sbd_t, bosdata.sbd, bosdata.sbd_t+(TimeCurrent()-bosdata.sbd_t), bosdata.sbd, clrMediumVioletRed);
        firstflag = false ;
    }
    else{
        if(ObjectFind(0, bosdata.sbu_lb.name1) == -1) firstflag = true ;
        if(ObjectFind(0, bosdata.sbd_lb.name1) == -1) firstflag = true ;
        if(ObjectFind(0, bosdata.sbu_ln.name1) == -1) firstflag = true ;
        if(ObjectFind(0, bosdata.sbd_ln.name1) == -1) firstflag = true ;
        bosdata.sbu_lb.set_xy(0, bosdata.sbu_lb.name1, 0, bosdata.sbu_t, bosdata.sbu);
        bosdata.sbd_lb.set_xy(0, bosdata.sbd_lb.name1, 0, bosdata.sbd_t, bosdata.sbd);
        bosdata.sbu_lb.set_text(0, bosdata.sbu_lb.name1, "sbu:"+DoubleToString(bosdata.sbu,5), clrMagenta, 12);
        bosdata.sbd_lb.set_text(0, bosdata.sbd_lb.name1, "sbd:"+DoubleToString(bosdata.sbd,5), clrMagenta, 12);
        bosdata.sbu_ln.set_xy(0, bosdata.sbu_ln.name1, 0, bosdata.sbu_t, bosdata.sbu);
        bosdata.sbu_ln.set_xy(0, bosdata.sbu_ln.name1, 1, bosdata.sbu_t+(TimeCurrent()-bosdata.sbu_t), bosdata.sbu);

        bosdata.sbd_ln.set_xy(0, bosdata.sbd_ln.name1, 0, bosdata.sbd_t, bosdata.sbd);
        bosdata.sbd_ln.set_xy(0, bosdata.sbd_ln.name1, 1, bosdata.sbd_t+(TimeCurrent()-bosdata.sbd_t), bosdata.sbd);
    }

    ChartRedraw();
    //printf("sbu= %.6f\t sbd= %.6f\n sbu_t= %s\t sbd_t= %s", bosdata.sbu, bosdata.sbd, TimeToString(bosdata.sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(bosdata.sbd_t,TIME_DATE|TIME_MINUTES) );
    //printf("rd.rawprices[%d]=  %.6f", starti, rd.rawprices[starti]);
    //printf("rd.datadate[%d]=  %s", starti, TimeToString(rd.datadate[starti],TIME_DATE|TIME_MINUTES));
    bosdata = BOS(PeriodSeconds(_Period)/60);
}
//+------------------------------------------------------------------+
//| deinit                                                         
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    Print("Script deinitialized with reason code: ", reason);
    ObjectDelete(0,  bosdata.sbu_lb.name1);
    ObjectDelete(0,  bosdata.sbd_lb.name1);
    ObjectDelete(0,  bosdata.sbu_ln.name1);
    ObjectDelete(0,  bosdata.sbd_ln.name1);
    ChartRedraw();
    EventKillTimer();
}
