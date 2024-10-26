#ifndef __WRITETRI_MQH__
#define __WRITETRI_MQH__

void TriWrite(string symbolname, const Triset& Tri[], string sectorname, matrix& mg){
    string filename  = StringFormat("%s"+"\\%s"+"\\Tricode"+"\\Tri_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_COMMON);
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
    string filename2 =StringFormat("%s"+"\\%s"+"\\Tricode0F_ex"+"\\Tri0F_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle2=FileOpen(filename2,FILE_WRITE|FILE_TXT|FILE_COMMON);
    bool anycode = false;
    bool anycodereg = false;

    if(filehandle2!=INVALID_HANDLE){
        FileWrite(filehandle2, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        for(int i=0; i<PERIOD; ++i){
            if(Tri[i].wide2itv0X==-1 && Tri[i].wide2itvXF==-1) continue ;
            int  temp1=-1;
            int  temp2=999999;
            int  idxd  =-1;
            int  idxu  =-1;
            string line2 = "";
            string line  = "";
            if (((i+1)/10)<1) line2= "         ";
            else if (((i+1)/10)<10) line2= "          ";
            else if (((i+1)/10)<100) line2= "           ";
            else if (((i+1)/10)<1000) line2= "            ";
            else line2= "         ";
            line += StringFormat("Period %d ", i+1);
            bool highfg = false ;
            bool lowfg  = false ;
            bool rfvgfg = false ;
            bool gfvgfg = false ;
            for(int j=0; j<=i; ++j){
                if(Tri[i].fvgtype0F[j]==0) continue ;
                if(Tri[i].comparecode0F[j]==0) continue ;
                if(((Tri[i].comparecode0F[j]&__LEVEL1SBUMASK)==__LEVEL1SBUMASK) && ((Tri[i].fvgtype0F[j]==0x1) || (Tri[i].fvgtype0F[j]==0x3) || (Tri[i].fvgtype0F[j]==0xA) || (Tri[i].fvgtype0F[j]==0xC))) continue;
                if(((Tri[i].comparecode0F[j]&__LEVEL1SBDMASK)==0) && ((Tri[i].fvgtype0F[j]==0x2) || (Tri[i].fvgtype0F[j]==0x4) || (Tri[i].fvgtype0F[j]==0xB) || (Tri[i].fvgtype0F[j]==0xD))) continue;
                if(((Tri[i].comparecode0F[j]&__LEVEL1SBUMASK)==__LEVEL1SBUMASK) && (Tri[i].highfg[j] || Tri[i].rfvgfg[j])  )continue ;
                else if(((Tri[i].comparecode0F[j]&__LEVEL1SBDMASK)==0) && (Tri[i].lowfg[j] || Tri[i].gfvgfg[j])  ) continue ;
                else{
                    if (((j+1)/10)<1) line2 += StringFormat("Itv %d       ", j+1);
                    else if (((j+1)/10)<10) line2 += StringFormat("Itv %d      ", j+1);
                    else if (((j+1)/10)<100) line2 += StringFormat("Itv %d     ", j+1);
                    else if (((j+1)/10)<1000) line2 += StringFormat("Itv %d    ", j+1);
                    else line2 += StringFormat("Itv %d       ", j+1);
                    anycode   = true;
                    anycodereg= true;
                    if((Tri[i].comparecode0F[j]&__LEVEL1SBUMASK)==__LEVEL1SBUMASK){
                        if(Tri[i].localminu[j] > temp1){ //find maximun localminu in localminu group
                            temp1 = Tri[i].localminu[j] ;
                            idxu  = j ;
                        }
                        else{
                            temp1 = -1 ;
                            idxu  = idxu;
                        }
                    }
                    if((Tri[i].comparecode0F[j]&__LEVEL1SBDMASK)==0){
                        if(Tri[i].localmaxd[j] < temp2){ //find minimun localmaxd in localminu group
                            temp2 = Tri[i].localmaxd[j] ;
                            idxd  = j ;
                        }
                        else{
                            temp2 = 999999 ;
                            idxd  = idxd;
                        }
                    }

                    line  += StringFormat("0x%08X%01X ", Tri[i].comparecode0F[j], Tri[i].fvgtype0F[j]);
                }
            }//j for end
            if(anycode){//商品名稱(第一列) code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用) 時間點)]
                line2 += "widespace";
                line += StringFormat("%d %d", idxd+1,idxu+1);
                FileWrite(filehandle2, line2);
                FileWrite(filehandle2, line); 
                anycode = false ;
                if(idxu+1==0){
                    mg[i][0]  = Tri[i].comparecode0F[idxd] ;
                    mg[i][1]  = i+1 ;
                    mg[i][2]  = idxd+1 ;
                    mg[i][3]  = 0 ;
                    mg[i][4]  = Tri[i].fvgtype0F[idxd] ;
                    mg[i][5]  = Bosarr[i].sbu ;
                    mg[i][6]  = Tri[i].localmaxd[idxd] ;
                    mg[i][7]  = Tri[i].code0FrFvgExtreme[idxd] ;
                    mg[i][8]  = Tri[i].code0FgFvgExtreme[idxd] ;
                    mg[i][9]  = Bosarr[i].i2bsbu  ;
                    mg[i][10] = Bosarr[i].i2bsbu_t;
                }
                else if(idxd+1==0){
                    mg[i][0]  = Tri[i].comparecode0F[idxu] ;
                    mg[i][1]  = i+1 ;
                    mg[i][2]  = idxu+1 ;
                    mg[i][3]  = 0xF ;
                    mg[i][4]  = Tri[i].fvgtype0F[idxu] ;
                    mg[i][5]  = Tri[i].localminu[idxu] ;
                    mg[i][6]  = Bosarr[i].sbd ;
                    mg[i][7]  = Tri[i].code0FrFvgExtreme[idxu];
                    mg[i][8]  = Tri[i].code0FgFvgExtreme[idxu];
                    mg[i][9]  = Bosarr[i].i2bsbd  ;
                    mg[i][10] = Bosarr[i].i2bsbd_t;
                }
            }
        }//i for end
    if(anycodereg) FileWrite(filehandle2, "//+------------------------------***HARDBONE CO.,LTD***----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+//"); 
    FileClose(filehandle2);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    //int temp = 20 ;
    //printf("Tri[%.0f].fvgtype0F[%.0f]= %01X", temp, temp, Tri[temp].fvgtype0F[temp]);
    ResetLastError();
}
void FvgWrite(string symbolname, const FVG& fvg[], string sectorname){
    string filename  =StringFormat("%s"+"\\%s"+"\\FVGproperty"+"\\FVG_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);

    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_COMMON);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        string line  = "" ;
        string line2 = "" ;
        for(int k=0; k<PERIODX4; ++k){
            line2 = StringFormat("Period %d: ", k+1);
            FileWrite(filehandle, line2);
            for (int i=0; fvg[k].Property[i]!=-1; i++){
                string str= TimeToString(fvg[k].Boxtime[i] , TIME_DATE|TIME_MINUTES) ;
                if(fvg[k].leadblockbound[i]<0)line= StringFormat("idx%d p%d l%d lv%.5f o%d %d %d LT%.5f RB%.5f BT%s" , i, fvg[k].Property[i], fvg[k].leadblockfg[i], fvg[k].leadblockbound[i], fvg[k].fvgsyndrone[i], fvg[k].effkbar[i], fvg[k].effkbarend[i], fvg[k].LTprice[i], fvg[k].RBprice[i], str);
                else line= StringFormat("idx%d p%d l%d lv %.5f o%d %d %d LT%.5f RB%.5f BT%s", i, fvg[k].Property[i], fvg[k].leadblockfg[i], fvg[k].leadblockbound[i], fvg[k].fvgsyndrone[i], fvg[k].effkbar[i], fvg[k].effkbarend[i], fvg[k].LTprice[i], fvg[k].RBprice[i], str);
                FileWrite(filehandle, line);
            }
        }
        FileClose(filehandle);
        Print("FileOpenlast OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
void GoldWrite(string symbolname, const matrix& mg, string sectorname){//商品名稱(第一列) code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  
    string filename  =StringFormat("%s"+"\\%s"+"\\Gold"+"\\Gold_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_COMMON);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, symbolname);
        string line  = "" ;
        bool anycode=false;
        for(int i=0; i<PERIODX4; ++i){
            if(mg[i][0]==0) continue ;
            line = StringFormat("%.0f %.0f %.0f %.0f %.0f %.5f %.5f %.5f %.5f %.5f %.0f", mg[i][0], mg[i][1], mg[i][2], mg[i][3], mg[i][4], mg[i][5], mg[i][6], mg[i][7], mg[i][8], mg[i][9], mg[i][10]);
            FileWrite(filehandle, line);
            anycode = true ;
        }
        if(anycode) FileWrite(filehandle, "//+------------------------------***HARDBONE CO.,LTD***----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+//") ;
        FileClose(filehandle);
        Print("FileOpenlast OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
#endif

