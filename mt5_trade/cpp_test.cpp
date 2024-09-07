string line = "1.1 2.2 3.3";  // 示例输入字符串
string separators = " ";       // 分隔符（空格）
string parts[];                // 存储拆分后的部分

int columns = StringSplit(line, separators, parts);  // 按分隔符拆分字符串

// 输出拆分结果
for(int i = 0; i < columns; i++)
{
    if(StringLen(parts[i]) > 0)  // 检查是否为空
    {
        PrintFormat("parts[%d] = '%s'", i, parts[i]);
    }
    else
    {
        PrintFormat("parts[%d] 是空的", i);
    }
}
