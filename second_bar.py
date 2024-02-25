//@version=5
indicator("Second Bar Close", shorttitle="SBC", overlay=true)

// 設置一個條形計數器
var int barCount = 0

// 在腳本的每次運行時更新條形計數器
barCount := barCount + 1

// 檢查是否為第二個條形，並捕獲其收盤價
var float secondClose = na
if (barCount == 2)
    secondClose := close

// 當secondClose有值時，在圖表上顯示標籤
if (not na(secondClose))
    label.new(bar_index, secondClose, text="Second Close: " + str.tostring(secondClose), style=label.style_label_down, color=color.red, size=size.normal)

