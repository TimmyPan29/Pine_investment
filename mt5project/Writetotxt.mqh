void AppendToFile(string filename, string data) {
    int fileHandle;
    string fullPath = TerminalInfoString(TERMINAL_COMMONDATA_PATH) + "\\" + filename;

    // 以读写模式打开文件，如果文件不存在则创建文件
    fileHandle = FileOpen(fullPath, FILE_READ|FILE_WRITE|FILE_TXT);
    if(fileHandle != INVALID_HANDLE) {
        // 将文件指针移动到文件末尾
        FileSeek(fileHandle, 0, SEEK_END);
        // 写入数据
        FileWrite(fileHandle, data);
        // 关闭文件
        FileClose(fileHandle);
        Print("Data appended to file: ", fullPath);
    } else {
        Print("Failed to open file: ", fullPath);
    }
}

void OnStart() {
    string filename = "log.txt";
    string data = "This is another log entry.";

    // 追加数据到文件
    AppendToFile(filename, data);
}

