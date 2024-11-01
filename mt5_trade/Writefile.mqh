#ifndef __WRITEFILE_MQH__
#define __WRITEFILE_MQH__
struct DealGolder{
	ulong    dealmagic ;
	ulong    dealorder ;
	ulong    dealposticket;
    ulong    dealposid ;
    double   dealopen  ;
    double   dealtp    ;
    double   dealsl    ;
    ulong    dealticket;
	string   dealsymbol;
	int      dealcode  ;
	int      dealprd   ;
	int      dealitv   ;
	datetime dealsbd_t ;
	datetime dealsbu_t ;
	double   dealvolume;
	double   dealprofit;

	DealGolder():dealmagic(0), dealorder(0), dealposticket(0), dealposid(0), dealopen(0), dealtp(0), dealsl(0), dealticket(0), dealsymbol(""), dealcode(0), dealprd(0), dealitv(0), dealsbd_t(0), dealsbu_t(0), dealvolume(0), dealprofit(0){}
	void DealWriteOut(const string& sectorname);
};
void DealGolder::DealWriteOut(const string& sectorname){
	string filename  = "DealLog.txt" ;
	int file_handle ;
	string file_content = "";
	string timesbd;
	string timesbu;
	string line = "" ;
	file_handle = FileOpen(filename, FILE_READ | FILE_COMMON  );
	
	if(file_handle != INVALID_HANDLE){
        while(!FileIsEnding(file_handle)){
            file_content += FileReadString(file_handle) + "\n";
        }
        FileClose(file_handle); 
    }
    else{
    	Print("Can't open file");
    	PrintFormat("can not open file %s, errorcode: %d", filename, GetLastError());
    }
    file_handle = FileOpen(filename, FILE_WRITE | FILE_COMMON  );
    if (file_handle != INVALID_HANDLE){
    	if(StringLen(file_content) > 0){
    		FileWrite(file_handle, file_content);
    	}
    	timesbd = TimeToString(dealsbd_t, TIME_DATE|TIME_MINUTES);
    	timesbu = TimeToString(dealsbu_t, TIME_DATE|TIME_MINUTES);
    	line = StringFormat("Exchange: %s,Magic: %ld,OrderTicket: %d,PosTicket: %d,PosID: %d,Openprice: %.5f,TP: %.5f,SL: %.5f,DealTicket: %d,Symbol: %s,Code: 0x%08X,Prd: %d,Itv: %d,Sbd_t: %s,Sbu_t: %s,Volume: %.2f, Profit: %.2f", AccountInfoString(ACCOUNT_COMPANY), dealmagic, dealorder, dealposticket, dealposid, dealopen, dealtp, dealsl, dealticket, dealsymbol, dealcode, dealprd, dealitv, timesbd, timesbu, dealvolume, dealprofit);
    	FileWrite(file_handle, line);
    	FileClose(file_handle);
        Print("Write into DealLog.csv successfully!");
    }
    else{
    	Print("Can't open file");
    	PrintFormat("can not open file %s, errorcode: %d", filename, GetLastError());
    }
}


#endif