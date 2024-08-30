#ifndef __WRITETRI_MQH__
#define __WRITETRI_MQH__

void TriWrite(string symbolname, const Triset& Tri[], string sectorname){
   string filename  =StringFormat("%s"+"\\%s"+"\\Tricode"+"\\Tri_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else if (((i+1)/10)<1000) line2= "            ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if (((j+1)/10)<1) line2 += StringFormat("Itv %d      ", j+1);
                else if (((j+1)/10)<10) line2 += StringFormat("Itv %d     ", j+1);
                else if (((j+1)/10)<100) line2 += StringFormat("Itv %d    ", j+1);
                else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d   ", j+1);
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
//+------------------------------// 
    string filename2 =StringFormat("%s"+"\\%s"+"\\Tricode0F"+"\\Tri0F_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle2=FileOpen(filename2,FILE_WRITE|FILE_TXT);
    if(filehandle2!=INVALID_HANDLE){
        FileWrite(filehandle2, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            if(Tri[i].wide2itv0X==-1 && Tri[i].wide2itvXF==-1) continue ;
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else if (((i+1)/10)<1000) line2= "            ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if(Tri[i].comparecode0F[j]==0) continue ;
                else{
                    if (((j+1)/10)<1) line2 += StringFormat("Itv %d       ", j+1);
                    else if (((j+1)/10)<10) line2 += StringFormat("Itv %d      ", j+1);
                    else if (((j+1)/10)<100) line2 += StringFormat("Itv %d     ", j+1);
                    else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d    ", j+1);
                    else line2 += StringFormat("Itv %d       ", j+1);
                    //if(Tri[i].comparecode0F[j]==0) line  += "            ";
                    //else line  += StringFormat("0x%08X%01X ", Tri[i].comparecode0F[j], Tri[i].fvgtype0F[j]);
                    line  += StringFormat("0x%08X%01X ", Tri[i].comparecode0F[j], Tri[i].fvgtype0F[j]);
                }
            }
            line2 += "widespace";
            line += StringFormat("%d %d", Tri[i].wide2itv0X+1,Tri[i].wide2itvXF+1);
            FileWrite(filehandle2, line2);
            FileWrite(filehandle2, line);
        }
    FileClose(filehandle2);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
//+------------------------------// 
    string filename3 =StringFormat("%s"+"\\%s"+"\\TricodeOut"+"\\TriOut_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int fIlehandle3=FileOpen(filename3,FILE_WRITE|FILE_TXT);
    if(fIlehandle3!=INVALID_HANDLE){
        FileWrite(fIlehandle3, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            if(!Tri[i].comparecodeOut[0]) continue ;
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else if (((i+1)/10)<1000) line2= "            ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if(i!=j) continue ;
                else{
                    if (((j+1)/10)<1) line2 += StringFormat("Itv %d       ", j+1);
                    else if (((j+1)/10)<10) line2 += StringFormat("Itv %d      ", j+1);
                    else if (((j+1)/10)<100) line2 += StringFormat("Itv %d     ", j+1);
                    else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d    ", j+1);
                    else line2 += StringFormat("Itv %d       ", j+1);
                    //if(Tri[i].comparecode0F[j]==0) line  += "            ";
                    //else line  += StringFormat("0x%08X%01X ", Tri[i].comparecode0F[j], Tri[i].fvgtype0F[j]);
                    line  += StringFormat("0x%08X ", Tri[i].comparecodeOut[0]);
                }
            }
            FileWrite(fIlehandle3, line2);
            FileWrite(fIlehandle3, line);
        }
    FileClose(fIlehandle3);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
//+------------------------------//
//+------------------------------//
    string filename4 =StringFormat("%s"+"\\%s"+"\\Tribool"+"\\Tri_flt%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int fIlehandle4=FileOpen(filename4,FILE_WRITE|FILE_TXT);
    if(fIlehandle4!=INVALID_HANDLE){
        FileWrite(fIlehandle4, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else if (((i+1)/10)<1000) line2= "            ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            for(int j=0; j<=i; ++j){
                if(Tri[i].u_inside[j] || Tri[i].d_inside[j]){
                    if (((j+1)/10)<1) line2 += StringFormat("Itv %d      ", j+1);
                    else if (((j+1)/10)<10) line2 += StringFormat("Itv %d     ", j+1);
                    else if (((j+1)/10)<100) line2 += StringFormat("Itv %d    ", j+1);
                    else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d   ", j+1);
                    else line2 += StringFormat("Itv %d      ", j+1);
                    line  += StringFormat("%d %d        ", Tri[i].d_inside[j],Tri[i].u_inside[j]);
                }
                // else if(Tri[i].u_inside[j] && Tri[i].d_inside[j]){
                //     if (((j+1)/10)<1) line2 += StringFormat("Itv %d      ", j+1);
                //     else if (((j+1)/10)<10) line2 += StringFormat("Itv %d     ", j+1);
                //     else if (((j+1)/10)<100) line2 += StringFormat("Itv %d    ", j+1);
                //     else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d   ", j+1);
                //     else line2 += StringFormat("Itv %d      ", j+1);
                //     line  += StringFormat("%d%01X%d        ", Tri[i].d_inside[j],Tri[i].fvgtype0F[j],Tri[i].u_inside[j]);
                // }
            }
            line2 += "widespace";
            line += StringFormat("%d %d", Tri[i].wide2itv_d+1,Tri[i].wide2itv_u+1);
            FileWrite(fIlehandle4, line2);
            FileWrite(fIlehandle4, line);
        }
    FileClose(fIlehandle4);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
} 
void FvgWrite(string symbolname, const FVG& fvg[], string sectorname){
    string filename  =StringFormat("%s"+"\\%s"+"\\FVGproperty"+"\\FVG_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        string line  = "" ;
        string line2 = "" ;
        for(int k=0; k<PERIODX4; ++k){
            line2 = StringFormat("Period %d: ", k+1);
            FileWrite(filehandle, line2);
            for (int i=0; fvg[k].Property[i]!=-1; i++){
                line= StringFormat("idx%d %d %d %d LT%.5f RB%.5f", i, fvg[k].Property[i], fvg[k].effkbar[i], fvg[k].effkbarend[i], fvg[k].LTprice[i], fvg[k].RBprice[i]);
                FileWrite(filehandle, line);
            }
        }
        FileClose(filehandle);
        Print("FileOpenlast OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
#endif

// void OnStart()
//   {
// //--- incorrect file opening method
//    string terminal_data_path=TerminalInfoString(TERMINAL_DATA_PATH);
//    string filename=terminal_data_path+"\\MQL5\\Files\\"+"fractals.txt";
//    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
//    if(filehandle<0)
//      {
//       Print("Failed to open the file by the absolute path ");
//       Print("Error code ",GetLastError());
//      }
 
// //--- correct way of working in the "file sandbox"
//    ResetLastError();
//    filehandle=FileOpen("Tri.txt",FILE_WRITE|FILE_TXT);
//    if(filehandle!=INVALID_HANDLE)
//      {
//       FileWrite(filehandle,"miaomiao",TimeCurrent(),Symbol(), EnumToString(_Period),"狗狗","\n ddd");
//       FileClose(filehandle);
//       Print("FileOpen OK");
//      }
//    else Print("Operation FileOpen failed, error ",GetLastError());
//    ResetLastError();
// //--- another example with the creation of an enclosed directory in MQL5\Files\
//    string subfolder="Research";
//    filehandle=FileOpen(subfolder+"\\fractals.txt",FILE_WRITE|FILE_TXT);
//       if(filehandle!=INVALID_HANDLE)
//      {
//       FileWrite(filehandle,TimeCurrent(),Symbol(), EnumToString(_Period));
//       FileClose(filehandle);
//       Print("The file must be created in the folder "+terminal_data_path+"\\"+subfolder);
//      }
//    else Print("File open failed, error ",GetLastError());
//   }