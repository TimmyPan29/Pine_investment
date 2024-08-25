#ifndef __WRITEBOS_MQH__
#define __WRITEBOS_MQH__

void BosWrite(string symbolname, const matrix& Mat_d, const matrix& Mat_u, const matrix& Mat_do, const matrix& Mat_uo, const matrix& Mat_dCP, const matrix& Mat_uCP, const int& Pd, const int& Pu, string sectorname){
    string filename  =StringFormat("%s"+"\\%s"+"\\BosSort"+"\\BOS_%s.txt", AccountInfoString(ACCOUNT_COMPANY), sectorname, symbolname);
    int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
    if(filehandle!=INVALID_HANDLE){
        FileWrite(filehandle, AccountInfoString(ACCOUNT_COMPANY)+", ", AccountInfoString(ACCOUNT_CURRENCY)+", ", AccountInfoString(ACCOUNT_NAME)+", ", AccountInfoString(ACCOUNT_SERVER)+", ", symbolname);
        string line  = "";
        string line2 = "";
        string line3 = "";
        string line4 = "";
        string str   = "";
        int    idx   = 0 ;
        str  = TimeToString(Mat_do[Pd-1][6], TIME_DATE | TIME_MINUTES);
        line = StringFormat("Those Period whose sbd is more than P%d %.5f %s: ",Pd, Mat_do[Pd-1][2], str);
        FileWrite(filehandle, line);
        while(Mat_dCP[idx][0]!=0){
            str  = TimeToString(Mat_dCP[idx][2], TIME_DATE | TIME_MINUTES);
            line = StringFormat("%.0f\t%.5f\t%s", Mat_dCP[idx][0], Mat_dCP[idx][1], str);
            FileWrite(filehandle, line);
            ++idx;
        }
        idx  = 0;
        str  = TimeToString(Mat_uo[Pd-1][6], TIME_DATE | TIME_MINUTES);
        line = StringFormat("Those Period whose sbu is less than P%d %.5f %s: ",Pu, Mat_uo[Pu-1][2], str);
        FileWrite(filehandle, line);
        while(Mat_uCP[idx][0]!=0){
            str  = TimeToString(Mat_uCP[idx][2], TIME_DATE | TIME_MINUTES);
            line = StringFormat("%.0f\t%.5f\t%s", Mat_uCP[idx][0], Mat_uCP[idx][1], str);
            FileWrite(filehandle, line);
            ++idx;
        }
        idx   = 0;
        line  = "";
        FileWrite(filehandle, "//-----***-----//");
        FileWrite(filehandle, "Period\tSBD&U\tH\tL\tO\tT");
        for(int i=0; i<PERIODX4; ++i){
            //+----------sbd---------+//
            line  += StringFormat("P%.0f \t\t" , Mat_d[i][0]); //P
            //line  += StringFormat("%.0f " , Mat_d[i][1]); //cnt
            line  += StringFormat("%.5f " , Mat_d[i][2]); //BOS
            //line  += StringFormat("%.5f " , Mat_d[i][3]); //H
            //line  += StringFormat("%.5f " , Mat_d[i][4]); //L
            //line  += StringFormat("%.5f " , Mat_d[i][5]); //O
            str    = TimeToString(Mat_d[i][6], TIME_DATE | TIME_MINUTES);
            line  += StringFormat("%s " , str); //T
            //line  += StringFormat("%.0f " , Mat_d[i][7]); //kbar
            line  += "\t\t|\t\t";            
            //+----------sbu---------+//
            line2  += StringFormat("P%.0f \t\t" , Mat_u[i][0]); //P
            //line  += StringFormat("%.0f " , Mat_u[i][1]); //cnt
            line2  += StringFormat("%.5f " , Mat_u[i][2]); //BOS
            //line2  += StringFormat("%.5f " , Mat_u[i][3]); //H
            //line2  += StringFormat("%.5f " , Mat_u[i][4]); //L
            //line2  += StringFormat("%.5f " , Mat_u[i][5]); //O
            str    = TimeToString(Mat_u[i][6], TIME_DATE | TIME_MINUTES);
            line2  += StringFormat("%s " , str); //T
            //line  += StringFormat("%.0f  " , Mat_u[i][7]); //kbar
            line2  += "\t\t\t\t|\t\t\t\t";
            //+----------sbd_o---------+//
            line3  += StringFormat("P%.0f \t\t" , Mat_do[i][0]); //P
            //line  += StringFormat("%.0f " , Mat_do[i][1]); //cnt
            line3  += StringFormat("%.5f " , Mat_do[i][2]); //BOS
            //line3  += StringFormat("%.5f " , Mat_do[i][3]); //H
            //line3  += StringFormat("%.5f " , Mat_do[i][4]); //L
            //line3  += StringFormat("%.5f " , Mat_do[i][5]); //O
            str    = TimeToString(Mat_do[i][6], TIME_DATE | TIME_MINUTES);
            line3  += StringFormat("%s " , str); //T
            //line  += StringFormat("%.0f  " , Mat_do[i][7]); //kbar
            line3  += "\t\t\t\t|\t\t\t\t";
            //+----------sbu_o---------+//
            line4  += StringFormat("P%.0f \t\t" , Mat_uo[i][0]); //P
            //line  += StringFormat("%.0f " , Mat_uo[i][1]); //cnt
            line4  += StringFormat("%.5f " , Mat_uo[i][2]); //BOS
            //line4  += StringFormat("%.5f " , Mat_uo[i][3]); //H
            //line4  += StringFormat("%.5f " , Mat_uo[i][4]); //L
            //line4  += StringFormat("%.5f " , Mat_uo[i][5]); //O
            str    = TimeToString(Mat_uo[i][6], TIME_DATE | TIME_MINUTES);
            line4  += StringFormat("%s " , str); //T
            //line  += StringFormat("%.0f  " , Mat_uo[i][7]); //kbar
            line4  += "\t\t|\t\t";
            FileWrite(filehandle, line+line2+line3+line4);
            line  = "";
            line2 = "";
            line3 = "";
            line4 = "";
        }
    FileClose(filehandle);
    Print("FileOpen OK");
    }
    else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
#endif 