//@version=5
indicator("Second Bar Close", shorttitle="SBC", overlay=true)

// 設置一個條形計數器
var int barCount = 0

// 在腳本的每次運行時更新條形計數器
barCount := barCount + 1

// 檢查是否為第二個條形，並捕獲其收盤價
var float secondClose = na
if (barCount == 500)
    secondClose := close
    label.new(bar_index, secondClose, text="Second Close: " + str.tostring(secondClose), style=label.style_cross, color=color.blue, size=size.normal)



