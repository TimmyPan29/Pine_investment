SL轉乘TP
SELL_limit改成SEll_stop
//以上沒什麼用
會一開場馬上到SL點的原因是 abs(tp-sl)的值太小 導致買進或賣出倉位的當下 價格就已經很靠近sl了 ，舉例：當買入時 我們交易的價格通常會比我們想要的價格還要來的高，這導致會很容易碰到sl

要修正的有 增加兩個變量 sbd成立時間 與 sbu成立時間  <<我在monitorbos新增了 接下來請mytrade檔案的read要讀這些時間 << OK
P bos H L O T T T T i2bbos H L T  P bos H L O T T T T i2bbos H L T sbd_ted sbu_ted
0 1   2 3 4 5 6 7 8 9     10 11 1213 14 15161718192021 22    222425 26     27 
需要取得 進場的SL 進場的SL需要設定在前sbd的引線上面 << OK
限價單掛單需要隨時監控支撐壓力的有無 如果沒有 則取消，支撐壓力只要在level1sb low or high 和 縮在最裡面之sb中出現 且成立時間比levelsb還要早即可  << ok
開倉後 TP要動態浮動 一開始先0.5 後來測看看非波那契

已買單為例 運行中倉位的tp動態移動，必須要有G.GDBOS的資料 每個tick都要去監控是否有成立時間比level1sbu還要晚 且週期比level1還要大的sbu出現，前提是level1 sbu要先出現 為tp開始移動的關鍵<< OK

//+----- -----+//
