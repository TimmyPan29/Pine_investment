20241018 將查詢功能的sbd or sbu 的時間 + 自身週期 再 +1 並且要以加完的時間來做比較 變成是A時間點生成的操作變因sbd 比控制變因sbd的加完的時間來的晚 並且價格高就符合trading view的出場看的方式就可以，


//不管哪個週期遇到23:59 都要把這個bar收進來rawdata裡面{
        if(tempminreg==-1) tempminreg=tempminm1-1; //全部都要以1分鐘去想其他週期  比如 3分鐘週期00:00這根的收盤 其實是1分鐘的00:02這根的收盤
        qidxnow   = tempmin-tempminm1<0? 0 : tempmin;
        qidxpt    = tempminm1-tempminreg<0? 0 : tempminm1;
        tempminreg= qidxpt ;