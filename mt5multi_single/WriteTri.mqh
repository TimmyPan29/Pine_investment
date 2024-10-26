#ifndef __WRITETRI_MQH__
#define __WRITETRI_MQH__

void TriWrite(string symbolname, const BOS& Bos[], const Triset& Tri[], string sectorname){
    string filename =StringFormat("%s"+"\\%s"+"\\SingleLevel"+"\\single_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    bool anycode = false;
    bool anycodereg = false;
    bool bkflag;
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            bkflag = Tri[i].broken ;
            if(!bkflag) continue ;
            anycodereg   = true;
            string line  = "";
            line += StringFormat("Period %d ", i+1);
            line += StringFormat("SBD= %.5f SBU= %.5f FVGtype= %01X NearGreenFvg= %.5f NearRedFvg= %.5f", Bos[i].sbd, Bos[i].sbu, Tri[i].fvgtype, Tri[i].gFvgnear, Tri[i].rFvgnear);
            FileWrite(filehandle, line);
        }//i for end
    if(anycodereg) FileWrite(filehandle, "//+------------------------------***HARDBONE CO.,LTD***----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+//"); 
    FileClose(filehandle);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
#endif

