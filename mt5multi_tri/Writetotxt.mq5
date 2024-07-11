//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
  {
//--- incorrect file opening method
   string terminal_data_path=TerminalInfoString(TERMINAL_DATA_PATH);
   string filename=terminal_data_path+"\\MQL5\\Files\\"+"fractals.txt";
   int filehandle=FileOpen(filename,FILE_WRITE|FILE_TXT);
   if(filehandle<0)
     {
      Print("Failed to open the file by the absolute path ");
      Print("Error code ",GetLastError());
     }
 
//--- correct way of working in the "file sandbox"
   ResetLastError();
   filehandle=FileOpen("Tri.txt",FILE_WRITE|FILE_TXT);
   if(filehandle!=INVALID_HANDLE)
     {
      FileWrite(filehandle,"miaomiao",TimeCurrent(),Symbol(), EnumToString(_Period),"狗狗","\n ddd");
      FileClose(filehandle);
      Print("FileOpen OK");
     }
   else Print("Operation FileOpen failed, error ",GetLastError());
   ResetLastError();
//--- another example with the creation of an enclosed directory in MQL5\Files\
   string subfolder="Research";
   filehandle=FileOpen(subfolder+"\\fractals.txt",FILE_WRITE|FILE_TXT);
      if(filehandle!=INVALID_HANDLE)
     {
      FileWrite(filehandle,TimeCurrent(),Symbol(), EnumToString(_Period));
      FileClose(filehandle);
      Print("The file must be created in the folder "+terminal_data_path+"\\"+subfolder);
     }
   else Print("File open failed, error ",GetLastError());
  }







