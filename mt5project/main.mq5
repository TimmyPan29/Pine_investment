#include "Bos.mqh"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input Timebase tb           = __TIME00_00;
input Timebase tboffset     = __TIME00_00;
input Timebase tbtimeoffset = __TIME00_00;
input int      period   =359; 
input int      datasize =100000;


int OnInit() {
    EventSetTimer(300);
    //+----------initiation---------+//
    Helper helper;
    int      tint ;
    int      offset;
    int      starti ;
    int      timeoffset;
    tint                   = helper.Inputtimebase(tb); //
    offset                 = helper.Inputoffset(tboffset);
    timeoffset             = helper.Inputtimeoffset(tbtimeoffset); 
    Fetcher fc ;
    BOS Bosarr[1436] ;//設一天會卡死 base最多到359 超過360要再想辦法
    Triset Tri[359] ;
    
    //+----------initiation end---------+//
    //+----------Put Data---------+//
    
    fc.Setarrsize(datasize);
    // fc.Getprice(_Symbol, datasize);
    // fc.Getdate(_Symbol, datasize);
    fc.GetRawData(_Symbol, datasize, offset, timeoffset);
    Rawdatagroup rd = fc.GetRaw();
    starti          = fc.Searchdateidx(tint, datasize);
    Print("Exchange Time initiation: ",tint,"min","\nyou choose: ",helper.Inputtimetostring(tb));
    Print("EA has been initialized.");
    Print("Starti: ", starti);
    Print("price: ",fc.Getpriceinfo(starti)," date: ",fc.Getdateinfo(starti));
    fc.Printdata();
    //+----------Put Data end---------+//
    
    // u cannot write this way: ArrayResize(Bosarr,staticarraysize, staticarraysize);
    // cuz u s still have not initialize the BOS type;
    
    for (int i=0; i<(period<<2); ++i){
        Bosarr[i] = BOS(i+1);
        BOSJudge(Bosarr[i], datasize, rd, starti);
    }
 
    for (int i=0; i<(period); ++i){
        ArrayResize(Tri[i].comparecode,i+1,i+1);
        ArrayResize(Tri[i].u_inside,i+1,i+1);
        ArrayResize(Tri[i].d_inside,i+1,i+1);
        for(int j=0; j<=i; ++j){
            if(i==0 && j==0){
                Tri[0]=TriCode(Tri[0], Bosarr[0], Bosarr[1], Bosarr[2], Bosarr[3], j);
            }
            else if(i!=0 && j==0){
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+1], Bosarr[i+2], Bosarr[i+3], j);
            }
            else{
                Tri[i]=TriCode(Tri[i], Bosarr[i], Bosarr[i+(j+1)], Bosarr[i+((j+1)<<1)], Bosarr[i+(j+1)*3], j);
            }
        }
    }
    int z = 684 ;
    TimeToString(Bosarr[0].sbu_t,TIME_DATE|TIME_MINUTES); 
    string teststr   = TimeToString(rd.datadate[0],TIME_DATE|TIME_MINUTES); 
    string s_sbudate = TimeToString(Bosarr[z-1].sbu_t,TIME_DATE|TIME_MINUTES); 
    string s_sbddate = TimeToString(Bosarr[z-1].sbd_t,TIME_DATE|TIME_MINUTES); 
    Print("rd.datadate[0] ", teststr);
    //Print("BOS[1440].htfint= ", Bosarr[0].htfint);
    //Print("rd.rawprices[37]= ", rd.rawprices[37]);
    printf("Period 1.sbu= %.6f\t Period 1.sbd= %.6f\n Period 1.sbu_t= %s\t Period 1.sbd_t= %s", Bosarr[0].sbu, Bosarr[0].sbd, TimeToString(Bosarr[0].sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(Bosarr[0].sbd_t,TIME_DATE|TIME_MINUTES) );
    printf("Period 2.sbu= %.6f\t Period 2.sbd= %.6f\n Period 2.sbu_t= %s\t Period 2.sbd_t= %s", Bosarr[1].sbu, Bosarr[1].sbd, TimeToString(Bosarr[1].sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(Bosarr[1].sbd_t,TIME_DATE|TIME_MINUTES) );
    printf("Period 3.sbu= %.6f\t Period 3.sbd= %.6f\n Period 3.sbu_t= %s\t Period 3.sbd_t= %s", Bosarr[2].sbu, Bosarr[2].sbd, TimeToString(Bosarr[2].sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(Bosarr[2].sbd_t,TIME_DATE|TIME_MINUTES) );
    printf("Period 4.sbu= %.6f\t Period 4.sbd= %.6f\n Period 4.sbu_t= %s\t Period 4.sbd_t= %s", Bosarr[3].sbu, Bosarr[3].sbd, TimeToString(Bosarr[3].sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(Bosarr[3].sbd_t,TIME_DATE|TIME_MINUTES) );
    printf("Period 5.sbu= %.6f\t Period 5.sbd= %.6f\n Period 5.sbu_t= %s\t Period 5.sbd_t= %s", Bosarr[4].sbu, Bosarr[4].sbd, TimeToString(Bosarr[4].sbu_t,TIME_DATE|TIME_MINUTES) , TimeToString(Bosarr[4].sbd_t,TIME_DATE|TIME_MINUTES) );
    printf("Period %d.sbu= %.6f\t Period %d.sbd= %.6f", z, Bosarr[z-1].sbu, z, Bosarr[z-1].sbd);
    printf("Period %d.sbu_t= %s\t Period %d.sbd_t= %s", z, s_sbudate, z, s_sbddate);
    Print("diff zone  ", helper.Extime());
    PrintFormat("Period 1.comparecode= 0x%08X", Tri[0].comparecode[0]);

    string filename =StringFormat("Tri_%s_%s.txt", AccountInfoString(ACCOUNT_COMPANY), _Symbol);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", _Symbol);
        for(int i=0; i<period; ++i){
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                line2 += StringFormat("Itv %d      ", j+1);
                line  += StringFormat("0x%08X ", Tri[i].comparecode[j]);
            }
            FileWrite(filehandle, line2);
            FileWrite(filehandle, line);
        }
    FileClose(filehandle);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();

    return(INIT_SUCCEEDED);

}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    // Print a message to indicate the EA has been deinitialized
    Print("EA has been deinitialized.");
    EventKillTimer() ;
    // Add your deinitialization code here
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    // This function is called on every new tick
    // Add your tick processing code here
    
    // Example: Print the current Bid price
    //double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    //Print("Current Bid price: ", bid,TimeCurrent());
    
}
void OnTimer(){
    Print("Hi");

}
//+------------------------------------------------------------------+
//| Custom start function                                            |
//+------------------------------------------------------------------+

// Add your custom functions here