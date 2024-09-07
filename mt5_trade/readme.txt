output所需資訊: 魔術號 單子號碼 商品  code 週期 間隔  sbd時間 sbu時間 change%數
無單 刪單 等單 進單 結單
在等單時 ticket設1 此時timer偵測如果原始檔的ITV已經消失  則刪單 變回無單ticket=0狀態
成功進單時  ticket設2 此時 timer中的monitor不會因為原始檔的ITV消失而關單 而那個周期也是禁止再等單的
結單時  進入ISR中output出我們要的資訊 並且把ticket設為0 如此一來可以再次等單

如果最新的交易出現 先檢查他是不是開倉位(因為有可能是等單) 接下來獲取他的symbol來和k0~k9的symbol比對
比對過了之後 進入迴圈1-1440把他的ticket所在位子的資訊全部寫出來