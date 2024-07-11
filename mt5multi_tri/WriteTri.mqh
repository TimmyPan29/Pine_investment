#ifndef __WRITETRI_MQH__
#define __WRITETRI_MQH__

void TriWrite(string symbolname, const Triset& Tri[], string sectorname){
   string filename  =StringFormat("%s"+"\\%s"+"\\Tricode"+"\\Tri_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<period; ++i){
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if (((j+1)/10)<1) line2 += StringFormat("Itv %d      ", j+1);
                else if (((j+1)/10)<10) line2 += StringFormat("Itv %d     ", j+1);
                else if (((j+1)/10)<100) line2 += StringFormat("Itv %d    ", j+1);
                else line2 += StringFormat("Itv %d      ", j+1);
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
    
    string filename2 =StringFormat("%s"+"\\%s"+"\\Tribool"+"\\Tri_flt%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle2=FileOpen(filename2,FILE_WRITE|FILE_TXT);
    if(filehandle2!=INVALID_HANDLE){
        FileWrite(filehandle2, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<period; ++i){
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if(Tri[i].u_inside[j] || Tri[i].d_inside[j]){
                    if (((j+1)/10)<1) line2 += StringFormat("Itv %d      ", j+1);
                    else if (((j+1)/10)<10) line2 += StringFormat("Itv %d     ", j+1);
                    else if (((j+1)/10)<100) line2 += StringFormat("Itv %d    ", j+1);
                    else line2 += StringFormat("Itv %d      ", j+1);
                    line  += StringFormat("%d %d        ", Tri[i].d_inside[j],Tri[i].u_inside[j]);
                }
            }
            FileWrite(filehandle2, line2);
            FileWrite(filehandle2, line);
        }
    FileClose(filehandle2);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();

} 

#endif