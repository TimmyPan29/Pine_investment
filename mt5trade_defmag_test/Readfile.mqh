#ifndef __READFILE_MQH__
#define __READFILE_MQH__
#include "MyTrade.mqh"
#define __MAXSTRLEN 500
//+-----
//+流程 讀BOSMONITOR 和 GOLD 分別進去兩個矩陣A B 這兩個矩陣來自GOLD CLASS
//+馬上做單 條件是必須要有大級別支撐壓力 有的話把做的單子的資訊填入C矩陣, C矩陣存 單子編號 P ITV PRICE SL TP 
//+C矩陣一直去監控B矩陣中和自己相同的period和ITV是否還存在 不存在的話 取消掛單並且初始化那一列週期的所有資訊
//+做的單子 TP和SL要差20個pip以上 而且買單的pending-SL>0  賣單的pending-SL<0
//+
//+-----
//商品名稱(第一列) code 基本週期 itv 空單還是多單  FVG型態 上 下界價錢 在區間內的最低的紅色FVG價格 在區間內的最高的綠色FVG價格  [(突破sbd時最初sbu的價錢(空單停損用應該要引線) 時間點)]or[(突破sbu時最初sbd的價錢(多單停損用應該要引線) 時間點)]
//P bosd H L T T T i2bsbd H L T bosu H L T T T i2bsbu H L T  sbd_ted  sbu_ted
//0 1    2 3 4 5 6 7      8 9 10 11  121314151617     181920 21       22
string EX1 = "Eightcap Pty Ltd" ;
string EX2 = "OANDA Corporation";

void RSfileEX1(const string& symbolname, const string& sectorname, Golder& G){
	ResetLastError();
	string filename  = StringFormat("%s"+"\\%s"+"\\Gold"+"\\Gold_%s.txt", EX1, sectorname, symbolname);
    int filehandle=FileOpen(filename, FILE_READ|FILE_TXT|FILE_COMMON);
    string sep=" ";                // A separator as a character 
    ushort u_sep;                  // The code of the separator character 
    u_sep=StringGetCharacter(sep,0); 
	if(filehandle!=INVALID_HANDLE){
		//PrintFormat("File path: %s\\Files\\", TerminalInfoString(TERMINAL_DATA_PATH));
		string line ;
		int rows= 0;
		bool isfirstline = true ;
		int  ptemp ;
		while (!FileIsEnding(filehandle)){
        	line = FileReadString(filehandle);
        	StringTrimRight(line);
        	//Print(line);
        	if(isfirstline){
        		G.symbol = line ;
        		isfirstline = false ;
        		continue;
        	}
        	if ((StringLen(line) > 0) && (StringLen(line)<__MAXSTRLEN)){// if not void
            	string parts[];
            	int columes = StringSplit(line, u_sep, parts);
            	//printf("parts[0]= %.1f, colume= %d", StringToDouble(parts[0]), columes) ;
            	// transform string parts[] into real double value
            	for (int i = 0; i<columes && rows<PERIODX4; ++i){
            		ptemp = StringToDouble(parts[1])-1;
                	G.GD[ptemp][i] = StringToDouble(parts[i]);
            	}
            	//printf("p= %.0f", StringToDouble(parts[1])) ;
            	++rows;
        	}
    	}
		FileClose(filehandle);
        //printf("FilereadGD %s OK, ", symbolname);
	}
	else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
	string filename2 = StringFormat("%s"+"\\%s"+"\\BosSort"+"\\TradeBOS_%s.txt", EX1, sectorname, symbolname);
    filehandle=FileOpen(filename2, FILE_READ|FILE_TXT|FILE_COMMON);
	if(filehandle!=INVALID_HANDLE){
		//PrintFormat("File path: %s\\Files\\", TerminalInfoString(TERMINAL_DATA_PATH));
		string line ;
		int rows= 0;
		while (!FileIsEnding(filehandle)){
        	line = FileReadString(filehandle);
        	StringTrimRight(line);
        	if ((StringLen(line) > 0) && (StringLen(line)<__MAXSTRLEN)){// if not void
            	string parts[];
            	int columes = StringSplit(line, u_sep, parts);
            	// transform string parts[] into real double value
            	for (int i = 0; i<columes && rows<PERIODX4; ++i){
                	G.GDbos[rows][i] = StringToDouble(parts[i]);
            	}
            	++rows;
        	}
    	}
    	FileClose(filehandle);
        //printf("FilereadGD %s OK, ", symbolname);
	}
	else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
void RSfileEX2(const string& symbolname, const string& sectorname, Golder& G){
	ResetLastError();
	string symbolnameforcheck = symbolname ;
	//+-----check oanda's name for matching eightcap
	if(CheckNameForMatch(symbolname, symbolnameforcheck) ) printf("name change successfully") ;
	else printf("not need to modify the name ") ;
	//+-----end
	string filename  = StringFormat("%s"+"\\%s"+"\\Gold"+"\\Gold_%s.txt", EX2, sectorname, symbolnameforcheck);
    int filehandle=FileOpen(filename, FILE_READ|FILE_TXT|FILE_COMMON);
    string sep=" ";                // A separator as a character 
    ushort u_sep;                  // The code of the separator character 
    u_sep=StringGetCharacter(sep,0); 
	if(filehandle!=INVALID_HANDLE){
		//PrintFormat("File path: %s\\Files\\", TerminalInfoString(TERMINAL_DATA_PATH));
		string line ;
		int rows= 0;
		bool isfirstline = true ;
		int  ptemp ;
		while (!FileIsEnding(filehandle)){
        	line = FileReadString(filehandle);
        	StringTrimRight(line);
        	//Print(line);
        	if(isfirstline){
        		G.symbol = line ;
        		isfirstline = false ;
        		continue;
        	}
        	if ((StringLen(line) > 0) && (StringLen(line)<__MAXSTRLEN)){// if not void
            	string parts[];
            	int columes = StringSplit(line, u_sep, parts);
            	//printf("parts[0]= %.1f, colume= %d", StringToDouble(parts[0]), columes) ;
            	// transform string parts[] into real double value
            	for (int i = 0; i<columes && rows<PERIODX4; ++i){
            		ptemp = StringToDouble(parts[1])-1;
                	G.GD2[ptemp][i] = StringToDouble(parts[i]);
            	}
            	//printf("p= %.0f", StringToDouble(parts[1])) ;
            	++rows;
        	}
    	}
		FileClose(filehandle);
        //printf("FilereadGD %s OK, ", symbolname);
	}
	else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
	string filename2 = StringFormat("%s"+"\\%s"+"\\BosSort"+"\\TradeBOS_%s.txt", EX2, sectorname, symbolnameforcheck);
    filehandle=FileOpen(filename2, FILE_READ|FILE_TXT|FILE_COMMON);
	if(filehandle!=INVALID_HANDLE){
		//PrintFormat("File path: %s\\Files\\", TerminalInfoString(TERMINAL_DATA_PATH));
		string line ;
		int rows= 0;
		while (!FileIsEnding(filehandle)){
        	line = FileReadString(filehandle);
        	StringTrimRight(line);
        	if ((StringLen(line) > 0) && (StringLen(line)<__MAXSTRLEN)){// if not void
            	string parts[];
            	int columes = StringSplit(line, u_sep, parts);
            	// transform string parts[] into real double value
            	for (int i = 0; i<columes && rows<PERIODX4; ++i){
                	G.GDbos2[rows][i] = StringToDouble(parts[i]);
            	}
            	++rows;
        	}
    	}
    	FileClose(filehandle);
        //printf("FilereadGD %s OK, ", symbolname);
	}
	else Print("Operation FileOpen failed, error ",GetLastError());
    ResetLastError();
}
bool CheckNameForMatch(const string& symbolname, string& symbolnameforcheck){
	if(symbolname == "EURGBP")      symbolnameforcheck = "EURGBP.sml" ;
	else if(symbolname == "EURUSD") symbolnameforcheck = "EURUSD.sml" ;
	else if(symbolname == "AUDUSD") symbolnameforcheck = "AUDUSD.sml" ;
	else if(symbolname == "GBPJPY") symbolnameforcheck = "GBPJPY.sml" ;
	else if(symbolname == "USDJPY") symbolnameforcheck = "USDJPY.sml" ;
	else if(symbolname == "GBPUSD") symbolnameforcheck = "GBPUSD.sml" ;
	else symbolnameforcheck = symbolname;
	if(symbolnameforcheck == symbolname) return false;
	else return true;
}
#endif


//+------------------------------***HARDBONE CO.,LTD***----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+//
