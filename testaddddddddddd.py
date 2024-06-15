//+-----filter the multiline after the timing and show that on figure -----+//
// © T.PanShuai29
//@version=5
indicator("linex30_configurable", overlay=true, max_boxes_count = 500, max_lines_count = 500, max_bars_back = 5000)

type Candle //for fourline candle
    float           c
    int             c_idx

type BOSdata
    float           sbu         = 0
    float           sbd         = 0
    int             sbu_idx     = 0
    int             sbd_idx     = 0
    float           slope1      = 0
    float           slope2      = 0
    int             state       = 1 //ini
    float           reg1key     = 0
    int             reg1key_idx = 0
    float           reg2key     = 0
    int             reg2key_idx = 0
    float           regclose1   = 0
    float           regclose2   = 0
    float           regclose3   = 0
    label           sbu_l
    label           sbu_date
    string          s_dateu
    label           sbu_price
    line            sbu_line
    label           sbd_l
    label           sbd_date
    string          s_dated
    label           sbd_price
    line            sbd_line       
    float           temp        = 0
    string          strtemp1
    string          strtemp2
    int             dateinnumber = 0

type CandleSettings
    bool            show
    string          htf
    int             max_memory

type Settings
    int             offset
    int             text_buffer
    int             max_sets
    string          sbu_label_size 
    color           sbu_label_color
    bool            sbu_label_show
    string          sbd_label_size 
    color           sbd_label_color
    bool            sbd_label_show

    string          htf_timer_size
    color           htf_timer_color
    string          htf_label_size 
    color           htf_label_color
    string          date_label_size
    color           date_label_color
    string          price_label_size
    color           price_label_color

type Trace
    int             trace_c_size 
    color           trace_c_color 
    string          trace_c_style 

type CandleSet
    Candle[]        candles
    CandleSettings  settings
    BOSdata         bosdata
    Trace           trace
    label           tfName
    label           tfTimer        

type Helper
    string name             = "Helper"

Settings settings = Settings.new()
//+-----four line-----+//
var CandleSettings SettingsHTF1 = CandleSettings.new()
var CandleSettings SettingsHTF2 = CandleSettings.new()
var CandleSettings SettingsHTF3 = CandleSettings.new()
var CandleSettings SettingsHTF4 = CandleSettings.new()
var CandleSettings SettingsHTF5 = CandleSettings.new()
var CandleSettings SettingsHTF6 = CandleSettings.new()
var CandleSettings SettingsHTF7 = CandleSettings.new()
var CandleSettings SettingsHTF8 = CandleSettings.new()
var CandleSettings SettingsHTF9 = CandleSettings.new()
var CandleSettings SettingsHTF10 = CandleSettings.new()
var CandleSettings SettingsHTF11 = CandleSettings.new()
var CandleSettings SettingsHTF12 = CandleSettings.new()
var CandleSettings SettingsHTF13 = CandleSettings.new()
var CandleSettings SettingsHTF14 = CandleSettings.new()
var CandleSettings SettingsHTF15 = CandleSettings.new()
var CandleSettings SettingsHTF16 = CandleSettings.new()
var CandleSettings SettingsHTF17 = CandleSettings.new()
var CandleSettings SettingsHTF18 = CandleSettings.new()
var CandleSettings SettingsHTF19 = CandleSettings.new()
var CandleSettings SettingsHTF20 = CandleSettings.new()
var CandleSettings SettingsHTF21 = CandleSettings.new()
var CandleSettings SettingsHTF22 = CandleSettings.new()
var CandleSettings SettingsHTF23 = CandleSettings.new()
var CandleSettings SettingsHTF24 = CandleSettings.new()
var CandleSettings SettingsHTF25 = CandleSettings.new()
var CandleSettings SettingsHTF26 = CandleSettings.new()
var CandleSettings SettingsHTF27 = CandleSettings.new()
var CandleSettings SettingsHTF28 = CandleSettings.new()
var CandleSettings SettingsHTF29 = CandleSettings.new()
var CandleSettings SettingsHTF30 = CandleSettings.new()
var Candle[] candles_1       = array.new<Candle>(0)
var Candle[] candles_2       = array.new<Candle>(0)
var Candle[] candles_3       = array.new<Candle>(0)
var Candle[] candles_4       = array.new<Candle>(0)
var Candle[] candles_5       = array.new<Candle>(0)
var Candle[] candles_6       = array.new<Candle>(0)
var Candle[] candles_7       = array.new<Candle>(0)
var Candle[] candles_8       = array.new<Candle>(0)
var Candle[] candles_9       = array.new<Candle>(0)
var Candle[] candles_10       = array.new<Candle>(0)
var Candle[] candles_11       = array.new<Candle>(0)
var Candle[] candles_12       = array.new<Candle>(0)
var Candle[] candles_13       = array.new<Candle>(0)
var Candle[] candles_14       = array.new<Candle>(0)
var Candle[] candles_15       = array.new<Candle>(0)
var Candle[] candles_16       = array.new<Candle>(0)
var Candle[] candles_17       = array.new<Candle>(0)
var Candle[] candles_18       = array.new<Candle>(0)
var Candle[] candles_19       = array.new<Candle>(0)
var Candle[] candles_20       = array.new<Candle>(0)
var Candle[] candles_21       = array.new<Candle>(0)
var Candle[] candles_22       = array.new<Candle>(0)
var Candle[] candles_23       = array.new<Candle>(0)
var Candle[] candles_24       = array.new<Candle>(0)
var Candle[] candles_25       = array.new<Candle>(0)
var Candle[] candles_26       = array.new<Candle>(0)
var Candle[] candles_27       = array.new<Candle>(0)
var Candle[] candles_28       = array.new<Candle>(0)
var Candle[] candles_29       = array.new<Candle>(0)
var Candle[] candles_30       = array.new<Candle>(0)
var BOSdata bosdata_1       = BOSdata.new()
var BOSdata bosdata_2       = BOSdata.new()
var BOSdata bosdata_3       = BOSdata.new()
var BOSdata bosdata_4       = BOSdata.new()
var BOSdata bosdata_5       = BOSdata.new()
var BOSdata bosdata_6       = BOSdata.new()
var BOSdata bosdata_7       = BOSdata.new()
var BOSdata bosdata_8       = BOSdata.new()
var BOSdata bosdata_9       = BOSdata.new()
var BOSdata bosdata_10       = BOSdata.new()
var BOSdata bosdata_11       = BOSdata.new()
var BOSdata bosdata_12       = BOSdata.new()
var BOSdata bosdata_13       = BOSdata.new()
var BOSdata bosdata_14       = BOSdata.new()
var BOSdata bosdata_15       = BOSdata.new()
var BOSdata bosdata_16       = BOSdata.new()
var BOSdata bosdata_17       = BOSdata.new()
var BOSdata bosdata_18       = BOSdata.new()
var BOSdata bosdata_19       = BOSdata.new()
var BOSdata bosdata_20       = BOSdata.new()
var BOSdata bosdata_21       = BOSdata.new()
var BOSdata bosdata_22       = BOSdata.new()
var BOSdata bosdata_23       = BOSdata.new()
var BOSdata bosdata_24       = BOSdata.new()
var BOSdata bosdata_25       = BOSdata.new()
var BOSdata bosdata_26       = BOSdata.new()
var BOSdata bosdata_27       = BOSdata.new()
var BOSdata bosdata_28       = BOSdata.new()
var BOSdata bosdata_29       = BOSdata.new()
var BOSdata bosdata_30       = BOSdata.new()
var Trace   trace_1         = Trace.new()
var Trace   trace_2         = Trace.new()
var Trace   trace_3         = Trace.new()
var Trace   trace_4         = Trace.new()
var Trace   trace_5         = Trace.new()
var Trace   trace_6         = Trace.new()
var Trace   trace_7         = Trace.new()
var Trace   trace_8         = Trace.new()
var Trace   trace_9         = Trace.new()
var Trace   trace_10         = Trace.new()
var Trace   trace_11         = Trace.new()
var Trace   trace_12         = Trace.new()
var Trace   trace_13         = Trace.new()
var Trace   trace_14         = Trace.new()
var Trace   trace_15         = Trace.new()
var Trace   trace_16         = Trace.new()
var Trace   trace_17         = Trace.new()
var Trace   trace_18         = Trace.new()
var Trace   trace_19         = Trace.new()
var Trace   trace_20         = Trace.new()
var Trace   trace_21         = Trace.new()
var Trace   trace_22         = Trace.new()
var Trace   trace_23         = Trace.new()
var Trace   trace_24         = Trace.new()
var Trace   trace_25         = Trace.new()
var Trace   trace_26         = Trace.new()
var Trace   trace_27         = Trace.new()
var Trace   trace_28         = Trace.new()
var Trace   trace_29         = Trace.new()
var Trace   trace_30         = Trace.new()

var CandleSet htf1          = CandleSet.new()
htf1 .settings               := SettingsHTF1
htf1 .candles                := candles_1 
htf1 .bosdata                := bosdata_1 
htf1 .trace                  := trace_1 
var CandleSet htf2          = CandleSet.new()
htf2 .settings               := SettingsHTF2
htf2 .candles                := candles_2 
htf2 .bosdata                := bosdata_2 
htf2 .trace                  := trace_2 
var CandleSet htf3          = CandleSet.new()
htf3 .settings               := SettingsHTF3
htf3 .candles                := candles_3 
htf3 .bosdata                := bosdata_3 
htf3 .trace                  := trace_3 
var CandleSet htf4          = CandleSet.new()
htf4 .settings               := SettingsHTF4
htf4 .candles                := candles_4 
htf4 .bosdata                := bosdata_4 
htf4 .trace                  := trace_4 
var CandleSet htf5          = CandleSet.new()
htf5 .settings               := SettingsHTF5
htf5 .candles                := candles_5 
htf5 .bosdata                := bosdata_5 
htf5 .trace                  := trace_5 
var CandleSet htf6          = CandleSet.new()
htf6 .settings               := SettingsHTF6
htf6 .candles                := candles_6 
htf6 .bosdata                := bosdata_6 
htf6 .trace                  := trace_6 
var CandleSet htf7          = CandleSet.new()
htf7 .settings               := SettingsHTF7
htf7 .candles                := candles_7 
htf7 .bosdata                := bosdata_7 
htf7 .trace                  := trace_7 
var CandleSet htf8          = CandleSet.new()
htf8 .settings               := SettingsHTF8
htf8 .candles                := candles_8 
htf8 .bosdata                := bosdata_8 
htf8 .trace                  := trace_8 
var CandleSet htf9          = CandleSet.new()
htf9 .settings               := SettingsHTF9
htf9 .candles                := candles_9 
htf9 .bosdata                := bosdata_9 
htf9 .trace                  := trace_9 
var CandleSet htf10          = CandleSet.new()
htf10 .settings               := SettingsHTF10
htf10 .candles                := candles_10 
htf10 .bosdata                := bosdata_10 
htf10 .trace                  := trace_10 
var CandleSet htf11          = CandleSet.new()
htf11 .settings               := SettingsHTF11
htf11 .candles                := candles_11 
htf11 .bosdata                := bosdata_11 
htf11 .trace                  := trace_11 
var CandleSet htf12          = CandleSet.new()
htf12 .settings               := SettingsHTF12
htf12 .candles                := candles_12 
htf12 .bosdata                := bosdata_12 
htf12 .trace                  := trace_12 
var CandleSet htf13          = CandleSet.new()
htf13 .settings               := SettingsHTF13
htf13 .candles                := candles_13 
htf13 .bosdata                := bosdata_13 
htf13 .trace                  := trace_13 
var CandleSet htf14          = CandleSet.new()
htf14 .settings               := SettingsHTF14
htf14 .candles                := candles_14 
htf14 .bosdata                := bosdata_14 
htf14 .trace                  := trace_14 
var CandleSet htf15          = CandleSet.new()
htf15 .settings               := SettingsHTF15
htf15 .candles                := candles_15 
htf15 .bosdata                := bosdata_15 
htf15 .trace                  := trace_15 
var CandleSet htf16          = CandleSet.new()
htf16 .settings               := SettingsHTF16
htf16 .candles                := candles_16 
htf16 .bosdata                := bosdata_16 
htf16 .trace                  := trace_16 
var CandleSet htf17          = CandleSet.new()
htf17 .settings               := SettingsHTF17
htf17 .candles                := candles_17 
htf17 .bosdata                := bosdata_17 
htf17 .trace                  := trace_17 
var CandleSet htf18          = CandleSet.new()
htf18 .settings               := SettingsHTF18
htf18 .candles                := candles_18 
htf18 .bosdata                := bosdata_18 
htf18 .trace                  := trace_18 
var CandleSet htf19          = CandleSet.new()
htf19 .settings               := SettingsHTF19
htf19 .candles                := candles_19 
htf19 .bosdata                := bosdata_19 
htf19 .trace                  := trace_19 
var CandleSet htf20          = CandleSet.new()
htf20 .settings               := SettingsHTF20
htf20 .candles                := candles_20 
htf20 .bosdata                := bosdata_20 
htf20 .trace                  := trace_20 
var CandleSet htf21          = CandleSet.new()
htf21 .settings               := SettingsHTF21
htf21 .candles                := candles_21 
htf21 .bosdata                := bosdata_21 
htf21 .trace                  := trace_21 
var CandleSet htf22          = CandleSet.new()
htf22 .settings               := SettingsHTF22
htf22 .candles                := candles_22 
htf22 .bosdata                := bosdata_22 
htf22 .trace                  := trace_22 
var CandleSet htf23          = CandleSet.new()
htf23 .settings               := SettingsHTF23
htf23 .candles                := candles_23 
htf23 .bosdata                := bosdata_23 
htf23 .trace                  := trace_23 
var CandleSet htf24          = CandleSet.new()
htf24 .settings               := SettingsHTF24
htf24 .candles                := candles_24 
htf24 .bosdata                := bosdata_24 
htf24 .trace                  := trace_24 
var CandleSet htf25          = CandleSet.new()
htf25 .settings               := SettingsHTF25
htf25 .candles                := candles_25 
htf25 .bosdata                := bosdata_25 
htf25 .trace                  := trace_25 
var CandleSet htf26          = CandleSet.new()
htf26 .settings               := SettingsHTF26
htf26 .candles                := candles_26 
htf26 .bosdata                := bosdata_26 
htf26 .trace                  := trace_26 
var CandleSet htf27          = CandleSet.new()
htf27 .settings               := SettingsHTF27
htf27 .candles                := candles_27 
htf27 .bosdata                := bosdata_27 
htf27 .trace                  := trace_27 
var CandleSet htf28          = CandleSet.new()
htf28 .settings               := SettingsHTF28
htf28 .candles                := candles_28 
htf28 .bosdata                := bosdata_28 
htf28 .trace                  := trace_28 
var CandleSet htf29          = CandleSet.new()
htf29 .settings               := SettingsHTF29
htf29 .candles                := candles_29 
htf29 .bosdata                := bosdata_29 
htf29 .trace                  := trace_29 
var CandleSet htf30          = CandleSet.new()
htf30 .settings               := SettingsHTF30
htf30 .candles                := candles_30 
htf30 .bosdata                := bosdata_30 
htf30 .trace                  := trace_30 
//+----------------------------------------+//
//+-settings    

//+----------------------------------------+//
htf1.settings.show         := input.bool(true, "HTF 1", inline="htf1")
htf_1                      = input.timeframe("1", "", inline="htf1")
htf1.settings.htf          := htf_1
htf1.settings.max_memory   := input.int(3, "", inline="htf1")
htf2.settings.show         := input.bool(true, "HTF 2", inline="htf2")
htf_2                      = input.timeframe("2", "", inline="htf2")
htf2.settings.htf          := htf_2
htf2.settings.max_memory   := input.int(3, "", inline="htf2")
htf3.settings.show         := input.bool(true, "HTF 3", inline="htf3")
htf_3                      = input.timeframe("3", "", inline="htf3")
htf3.settings.htf          := htf_3
htf3.settings.max_memory   := input.int(3, "", inline="htf3")
htf4.settings.show         := input.bool(true, "HTF 4", inline="htf4")
htf_4                      = input.timeframe("4", "", inline="htf4")
htf4.settings.htf          := htf_4
htf4.settings.max_memory   := input.int(3, "", inline="htf4")
htf5.settings.show         := input.bool(false, "HTF 5", inline="htf5")
htf_5                      = input.timeframe("5", "", inline="htf5")
htf5.settings.htf          := htf_5
htf5.settings.max_memory   := input.int(3, "", inline="htf5")
htf6.settings.show         := input.bool(false, "HTF 6", inline="htf6")
htf_6                      = input.timeframe("6", "", inline="htf6")
htf6.settings.htf          := htf_6
htf6.settings.max_memory   := input.int(3, "", inline="htf6")
htf7.settings.show         := input.bool(false, "HTF 7", inline="htf7")
htf_7                      = input.timeframe("7", "", inline="htf7")
htf7.settings.htf          := htf_7
htf7.settings.max_memory   := input.int(3, "", inline="htf7")
htf8.settings.show         := input.bool(false, "HTF 8", inline="htf8")
htf_8                      = input.timeframe("8", "", inline="htf8")
htf8.settings.htf          := htf_8
htf8.settings.max_memory   := input.int(3, "", inline="htf8")
htf9.settings.show         := input.bool(false, "HTF 9", inline="htf9")
htf_9                      = input.timeframe("9", "", inline="htf9")
htf9.settings.htf          := htf_9
htf9.settings.max_memory   := input.int(3, "", inline="htf9")
htf10.settings.show         := input.bool(false, "HTF 10", inline="htf10")
htf_10                      = input.timeframe("10", "", inline="htf10")
htf10.settings.htf          := htf_10
htf10.settings.max_memory   := input.int(3, "", inline="htf10")
htf11.settings.show         := input.bool(false, "HTF 11", inline="htf11")
htf_11                      = input.timeframe("11", "", inline="htf11")
htf11.settings.htf          := htf_11
htf11.settings.max_memory   := input.int(3, "", inline="htf11")
htf12.settings.show         := input.bool(false, "HTF 12", inline="htf12")
htf_12                      = input.timeframe("12", "", inline="htf12")
htf12.settings.htf          := htf_12
htf12.settings.max_memory   := input.int(3, "", inline="htf12")
htf13.settings.show         := input.bool(false, "HTF 13", inline="htf13")
htf_13                      = input.timeframe("13", "", inline="htf13")
htf13.settings.htf          := htf_13
htf13.settings.max_memory   := input.int(3, "", inline="htf13")
htf14.settings.show         := input.bool(false, "HTF 14", inline="htf14")
htf_14                      = input.timeframe("14", "", inline="htf14")
htf14.settings.htf          := htf_14
htf14.settings.max_memory   := input.int(3, "", inline="htf14")
htf15.settings.show         := input.bool(false, "HTF 15", inline="htf15")
htf_15                      = input.timeframe("15", "", inline="htf15")
htf15.settings.htf          := htf_15
htf15.settings.max_memory   := input.int(3, "", inline="htf15")
htf16.settings.show         := input.bool(false, "HTF 16", inline="htf16")
htf_16                      = input.timeframe("16", "", inline="htf16")
htf16.settings.htf          := htf_16
htf16.settings.max_memory   := input.int(3, "", inline="htf16")
htf17.settings.show         := input.bool(false, "HTF 17", inline="htf17")
htf_17                      = input.timeframe("17", "", inline="htf17")
htf17.settings.htf          := htf_17
htf17.settings.max_memory   := input.int(3, "", inline="htf17")
htf18.settings.show         := input.bool(false, "HTF 18", inline="htf18")
htf_18                      = input.timeframe("18", "", inline="htf18")
htf18.settings.htf          := htf_18
htf18.settings.max_memory   := input.int(3, "", inline="htf18")
htf19.settings.show         := input.bool(false, "HTF 19", inline="htf19")
htf_19                      = input.timeframe("19", "", inline="htf19")
htf19.settings.htf          := htf_19
htf19.settings.max_memory   := input.int(3, "", inline="htf19")
htf20.settings.show         := input.bool(false, "HTF 20", inline="htf20")
htf_20                      = input.timeframe("20", "", inline="htf20")
htf20.settings.htf          := htf_20
htf20.settings.max_memory   := input.int(3, "", inline="htf20")
htf21.settings.show         := input.bool(false, "HTF 21", inline="htf21")
htf_21                      = input.timeframe("21", "", inline="htf21")
htf21.settings.htf          := htf_21
htf21.settings.max_memory   := input.int(3, "", inline="htf21")
htf22.settings.show         := input.bool(false, "HTF 22", inline="htf22")
htf_22                      = input.timeframe("22", "", inline="htf22")
htf22.settings.htf          := htf_22
htf22.settings.max_memory   := input.int(3, "", inline="htf22")
htf23.settings.show         := input.bool(false, "HTF 23", inline="htf23")
htf_23                      = input.timeframe("23", "", inline="htf23")
htf23.settings.htf          := htf_23
htf23.settings.max_memory   := input.int(3, "", inline="htf23")
htf24.settings.show         := input.bool(false, "HTF 24", inline="htf24")
htf_24                      = input.timeframe("24", "", inline="htf24")
htf24.settings.htf          := htf_24
htf24.settings.max_memory   := input.int(3, "", inline="htf24")
htf25.settings.show         := input.bool(false, "HTF 25", inline="htf25")
htf_25                      = input.timeframe("25", "", inline="htf25")
htf25.settings.htf          := htf_25
htf25.settings.max_memory   := input.int(3, "", inline="htf25")
htf26.settings.show         := input.bool(false, "HTF 26", inline="htf26")
htf_26                      = input.timeframe("26", "", inline="htf26")
htf26.settings.htf          := htf_26
htf26.settings.max_memory   := input.int(3, "", inline="htf26")
htf27.settings.show         := input.bool(false, "HTF 27", inline="htf27")
htf_27                      = input.timeframe("27", "", inline="htf27")
htf27.settings.htf          := htf_27
htf27.settings.max_memory   := input.int(3, "", inline="htf27")
htf28.settings.show         := input.bool(false, "HTF 28", inline="htf28")
htf_28                      = input.timeframe("28", "", inline="htf28")
htf28.settings.htf          := htf_28
htf28.settings.max_memory   := input.int(3, "", inline="htf28")
htf29.settings.show         := input.bool(false, "HTF 29", inline="htf29")
htf_29                      = input.timeframe("29", "", inline="htf29")
htf29.settings.htf          := htf_29
htf29.settings.max_memory   := input.int(3, "", inline="htf29")
htf30.settings.show         := input.bool(false, "HTF 30", inline="htf30")
htf_30                      = input.timeframe("30", "", inline="htf30")
htf30.settings.htf          := htf_30
htf30.settings.max_memory   := input.int(3, "", inline="htf30")

settings.max_sets          := input.int(30, "Limit to next HTFs only", minval=1, maxval=30)

settings.offset            := input.int(10, "padding from current candles", minval = 1)
settings.text_buffer       := input.int(10, "space between text features", minval = 1, maxval = 10)
// sbu sbd, period, date happen, remain time, price, line color

settings.sbu_label_color   := input.color(color.new(color.black, 10), "sbu_label", inline='11')
settings.sbu_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.sbd_label_color   := input.color(color.new(color.black, 10), "sbd_label", inline='11')
settings.sbd_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="11")

settings.htf_label_color   := input.color(color.new(color.black, 10), "htf_label", inline='21')
settings.htf_label_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.date_label_color  := input.color(color.new(color.black, 10), "date_label", inline='21')
settings.date_label_size   := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="21")

settings.htf_timer_color   := input.color(color.new(color.black, 10), "htf_timer", inline='31')
settings.htf_timer_size    := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

settings.price_label_color := input.color(color.new(color.black, 10), "price_label", inline='31')
settings.price_label_size  := input.string(size.normal, "", [size.tiny, size.small, size.normal, size.large, size.huge], inline="31")

htf1.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF1    ", inline='htflevel1', group="trace")
htf1.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel1', group="trace")
htf1.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel1', group="trace")
htf2.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF2    ", inline='htflevel2', group="trace")
htf2.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel2', group="trace")
htf2.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel2', group="trace")
htf3.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF3    ", inline='htflevel3', group="trace")
htf3.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel3', group="trace")
htf3.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel3', group="trace")
htf4.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF4    ", inline='htflevel4', group="trace")
htf4.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel4', group="trace")
htf4.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel4', group="trace")
htf5.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF5    ", inline='htflevel5', group="trace")
htf5.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel5', group="trace")
htf5.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel5', group="trace")
htf6.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF6    ", inline='htflevel6', group="trace")
htf6.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel6', group="trace")
htf6.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel6', group="trace")
htf7.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF7    ", inline='htflevel7', group="trace")
htf7.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel7', group="trace")
htf7.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel7', group="trace")
htf8.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF8    ", inline='htflevel8', group="trace")
htf8.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel8', group="trace")
htf8.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel8', group="trace")
htf9.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF9    ", inline='htflevel9', group="trace")
htf9.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel9', group="trace")
htf9.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel9', group="trace")
htf10.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF10    ", inline='htflevel10', group="trace")
htf10.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel10', group="trace")
htf10.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel10', group="trace")
htf11.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF11    ", inline='htflevel11', group="trace")
htf11.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel11', group="trace")
htf11.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel11', group="trace")
htf12.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF12    ", inline='htflevel12', group="trace")
htf12.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel12', group="trace")
htf12.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel12', group="trace")
htf13.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF13    ", inline='htflevel13', group="trace")
htf13.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel13', group="trace")
htf13.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel13', group="trace")
htf14.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF14    ", inline='htflevel14', group="trace")
htf14.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel14', group="trace")
htf14.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel14', group="trace")
htf15.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF15    ", inline='htflevel15', group="trace")
htf15.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel15', group="trace")
htf15.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel15', group="trace")
htf16.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF16    ", inline='htflevel16', group="trace")
htf16.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel16', group="trace")
htf16.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel16', group="trace")
htf17.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF17    ", inline='htflevel17', group="trace")
htf17.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel17', group="trace")
htf17.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel17', group="trace")
htf18.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF18    ", inline='htflevel18', group="trace")
htf18.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel18', group="trace")
htf18.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel18', group="trace")
htf19.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF19    ", inline='htflevel19', group="trace")
htf19.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel19', group="trace")
htf19.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel19', group="trace")
htf20.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF20    ", inline='htflevel20', group="trace")
htf20.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel20', group="trace")
htf20.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel20', group="trace")
htf21.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF21    ", inline='htflevel21', group="trace")
htf21.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel21', group="trace")
htf21.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel21', group="trace")
htf22.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF22    ", inline='htflevel22', group="trace")
htf22.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel22', group="trace")
htf22.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel22', group="trace")
htf23.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF23    ", inline='htflevel23', group="trace")
htf23.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel23', group="trace")
htf23.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel23', group="trace")
htf24.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF24    ", inline='htflevel24', group="trace")
htf24.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel24', group="trace")
htf24.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel24', group="trace")
htf25.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF25    ", inline='htflevel25', group="trace")
htf25.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel25', group="trace")
htf25.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel25', group="trace")
htf26.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF26    ", inline='htflevel26', group="trace")
htf26.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel26', group="trace")
htf26.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel26', group="trace")
htf27.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF27    ", inline='htflevel27', group="trace")
htf27.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel27', group="trace")
htf27.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel27', group="trace")
htf28.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF28    ", inline='htflevel28', group="trace")
htf28.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel28', group="trace")
htf28.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel28', group="trace")
htf29.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF29    ", inline='htflevel29', group="trace")
htf29.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel29', group="trace")
htf29.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel29', group="trace")
htf30.trace.trace_c_color   := input.color(color.new(color.black, 50), "SkinHTF30    ", inline='htflevel30', group="trace")
htf30.trace.trace_c_style   := input.string('⎯⎯⎯', '', options = ['⎯⎯⎯', '----', '····'], inline='htflevel30', group="trace")
htf30.trace.trace_c_size    := input.int(2, '', options = [1,2,3,4], inline='htflevel30', group="trace")

//+----------------------------------------+//
//+- Variables   
//+----------------------------------------+//
Helper    helper        = Helper.new()

color color_transparent = #ffffff00
var index               = 0  //不要動

//+----------------------------------------+//
//+- Internal functions   

//+----------------------------------------+//


method LineStyle(Helper helper, string style) =>
    helper.name := style
    out = switch style
        '----' => line.style_dashed
        '····' => line.style_dotted
        => line.style_solid


method ValidTimeframe(Helper helper, string HTF) => //兩個部分 一個是檢查更高週期的是不是大於天，這個部分用轉成秒數的方式來判斷，第二個部分則是如果週期不是以天為單位，則一樣 使用秒的方式 判斷是不是整數倍 以及高週期的輸入要大於當前週期
    helper.name := HTF
    if timeframe.in_seconds(HTF) >= timeframe.in_seconds("D") and timeframe.in_seconds(HTF) > timeframe.in_seconds()
        true 
    else
        n1 = timeframe.in_seconds()
        n2 = timeframe.in_seconds(HTF)
        n3 = n2 % n1 //it is wrong, it should be n2%n1
        (n1 <= n2 and math.round(n2/n1) == n2/n1)

method RemainingTime(Helper helper, string HTF) =>
    helper.name     := HTF
    if barstate.isrealtime
        timeRemaining   = (time_close(HTF) - timenow)/1000
        days            = math.floor(timeRemaining / 86400)
        hours           = math.floor((timeRemaining - (days*86400)) / 3600)
        minutes         = math.floor((timeRemaining - (days*86400) - (hours*3600))/ 60)
        seconds         = math.floor(timeRemaining - (days*86400) - (hours*3600) - (minutes*60))

        r = str.tostring(seconds, "00")
        if minutes > 0 or hours > 0 or days > 0
            r := str.tostring(minutes, "00") + ":" + r
        if hours > 0 or days > 0
            r := str.tostring(hours, "00") + ":" + r
        if days > 0
            r := str.tostring(days) + "D " + r
        r
    else
        "n/a"

method formattedtime(Helper helper, int i_HTF) =>
    helper.name := "THE DATE OF BAR"
    r = str.format("{0,date,yyyy-MM-dd HH:mm}", i_HTF)
    r

    
method HTFName(Helper helper, string HTF) =>
    helper.name := "HTFName"
    formatted = HTF

    seconds = timeframe.in_seconds(HTF)
    if seconds < 60
        formatted := str.tostring(seconds) + "s"
    else if (seconds / 60) < 60
        formatted := str.tostring((seconds/60)) + "m"
    else if (seconds/60/60) < 24
        formatted := str.tostring((seconds/60/60)) + "H" 
    formatted

method HTFEnabled(Helper helper) =>
    helper.name := "HTFEnabled"
    int enabled =0
    enabled += htf1.settings.show ? 1 : 0
    enabled += htf2.settings.show ? 1 : 0
    enabled += htf3.settings.show ? 1 : 0
    enabled += htf4.settings.show ? 1 : 0
    enabled += htf5.settings.show ? 1 : 0
    enabled += htf6.settings.show ? 1 : 0
    enabled += htf7.settings.show ? 1 : 0
    enabled += htf8.settings.show ? 1 : 0
    enabled += htf9.settings.show ? 1 : 0
    enabled += htf10.settings.show ? 1 : 0
    enabled += htf11.settings.show ? 1 : 0
    enabled += htf12.settings.show ? 1 : 0
    enabled += htf13.settings.show ? 1 : 0
    enabled += htf14.settings.show ? 1 : 0
    enabled += htf15.settings.show ? 1 : 0
    enabled += htf16.settings.show ? 1 : 0
    enabled += htf17.settings.show ? 1 : 0
    enabled += htf18.settings.show ? 1 : 0
    enabled += htf19.settings.show ? 1 : 0
    enabled += htf20.settings.show ? 1 : 0
    enabled += htf21.settings.show ? 1 : 0
    enabled += htf22.settings.show ? 1 : 0
    enabled += htf23.settings.show ? 1 : 0
    enabled += htf24.settings.show ? 1 : 0
    enabled += htf25.settings.show ? 1 : 0
    enabled += htf26.settings.show ? 1 : 0
    enabled += htf27.settings.show ? 1 : 0
    enabled += htf28.settings.show ? 1 : 0
    enabled += htf29.settings.show ? 1 : 0
    enabled += htf30.settings.show ? 1 : 0
    int last = math.min(enabled, settings.max_sets)

    last

method Monitor(CandleSet candleSet) =>
    BOSdata bosdata = candleSet.bosdata
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    if isNewHTFCandle != 0 
        Candle candle    = Candle.new()
        candle.c        := bar_index==0 ? close : bosdata.temp
        candle.c_idx    := bar_index
        candleSet.candles.unshift(candle) //從這句話可以知道 index越靠近零 資料越新

        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)
    bosdata.temp := close //in fact "temp" is the lastest close price
    candleSet

method Monitor_Est(CandleSet candleSet) =>
    if barstate.isrealtime
        Candle candle    = Candle.new()
        candle.c        := close
        candle.c_idx    := bar_index
        candleSet.candles.unshift(candle)
        if candleSet.candles.size() > candleSet.settings.max_memory //清除舊candle
            Candle delCandle = array.pop(candleSet.candles)
    candleSet 
    
method BOSJudge(CandleSet candleSet) =>
    HTFBarTime = time(candleSet.settings.htf)
    isNewHTFCandle = ta.change(HTFBarTime)
    BOSdata bosdata = candleSet.bosdata
    int tf = time(timeframe.period)
    int tp = timeframe.in_seconds(timeframe.period)
    int tn = timeframe.in_seconds(candleSet.settings.htf)
    int k  = tn/tp
    if not barstate.isrealtime
        bosdata.dateinnumber := tf-tp*2000*k+tp*(k-1)*1000
    string strresult = helper.formattedtime(bosdata.dateinnumber)
    if candleSet.candles.size() > 0 and isNewHTFCandle != 0
        Candle candle = candleSet.candles.first()
        if(bosdata.state == 1)
            bosdata.regclose1 := bosdata.regclose2
            bosdata.regclose2 := bosdata.regclose3
            bosdata.regclose3 := candle.c
            bosdata.slope1 := bosdata.regclose2 - bosdata.regclose1>0? 1 : -1
            bosdata.slope2 := bosdata.regclose3 - bosdata.regclose2>0? 1 : -1
            if((not na(bosdata.sbd)) and (not na(bosdata.sbu)))
                bosdata.state := 2 
            else if(not na(bosdata.sbd) and na(bosdata.sbu))  //no sky
                bosdata.state := 3
            else if(na(bosdata.sbd) and (not na(bosdata.sbu)))
                bosdata.state := 4
            else
                label.new(bar_index,high,text="GG")

        if(bosdata.state == 2)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.reg1key := bosdata.regclose2
                bosdata.reg1key_idx := index==0? 0 : index - 1 - k
                bosdata.strtemp1    := strresult
            //else //Buff_key1維持原樣
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx := na
                bosdata.sbd := bosdata.reg1key
                bosdata.sbd_idx := bosdata.reg1key_idx
                bosdata.s_dated := bosdata.strtemp1
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd := na 
                bosdata.sbd_idx := na
                bosdata.sbu := bosdata.reg1key
                bosdata.sbu_idx := bosdata.reg1key_idx
                bosdata.s_dateu := bosdata.strtemp1
            bosdata.state := 1
            
        if(bosdata.state == 3)//no sky
            if(bosdata.slope1 != bosdata.slope2) // build sky
                bosdata.strtemp2    := strresult
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index - 1 - k
                bosdata.sbu := bosdata.reg2key
                bosdata.sbu_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
                bosdata.s_dateu := bosdata.strtemp2
                bosdata.strtemp1 := bosdata.strtemp2
            if(bosdata.regclose3<bosdata.sbd)
                bosdata.sbd    := na
                bosdata.sbd_idx:= na
            bosdata.state := 1
            
        if(bosdata.state == 4)
            if(bosdata.slope1 != bosdata.slope2)
                bosdata.strtemp2    := strresult
                bosdata.reg2key := bosdata.regclose2
                bosdata.reg2key_idx := index - 1 - k
                bosdata.sbd := bosdata.reg2key
                bosdata.sbd_idx:= bosdata.reg2key_idx
                bosdata.reg1key := bosdata.reg2key
                bosdata.reg1key_idx := bosdata.reg2key_idx
                bosdata.s_dated := bosdata.strtemp2
                bosdata.strtemp1 := bosdata.strtemp2
            if(bosdata.regclose3>bosdata.sbu)
                bosdata.sbu := na
                bosdata.sbu_idx:= na
            bosdata.state := 1
    candleSet

method plotdata(CandleSet candleSet, int offset, int delta) =>
    int pcnt = 0
    BOSdata bosdata = candleSet.bosdata
    Trace   trace   = candleSet.trace
    var label l = candleSet.tfName
    var label l2 = na
    var label l_sbu = bosdata.sbu_l
    var label l_sbd = bosdata.sbd_l
    var label l_datesbu = bosdata.sbu_date
    var label l_datesbd = bosdata.sbd_date
    var label lt = candleSet.tfTimer
    var label lt2 = na
    var label l_pricesbu = bosdata.sbu_price
    var label l_pricesbd = bosdata.sbd_price
    var line  li_sbu   = bosdata.sbu_line
    var line  li_sbd   = bosdata.sbd_line
    string lbn  = helper.HTFName(candleSet.settings.htf)
    if candleSet.settings.show
        if not na(l_pricesbu)
            label.set_xy(l_pricesbu, offset+pcnt*delta, bosdata.sbu)
            label.set_text(l_pricesbu, str.tostring(bosdata.sbu))
        else
            l_pricesbu := label.new(offset+pcnt*delta, bosdata.sbu, 'err', color = color_transparent, textcolor = settings.price_label_color, size = settings.price_label_size, textalign = text.align_center)
        if not na(l_pricesbd)
            label.set_xy(l_pricesbd, offset+pcnt*delta, bosdata.sbd)
            label.set_text(l_pricesbd, str.tostring(bosdata.sbd))
        else
            l_pricesbd := label.new(offset+pcnt*delta, bosdata.sbd, 'err', color = color_transparent, textcolor = settings.price_label_color, size = settings.price_label_size, textalign = text.align_center)
        
        pcnt += 1
        if not na(l)
            label.set_xy(l, offset+pcnt*delta,bosdata.sbu)
        else
            l := label.new(offset+pcnt*delta, bosdata.sbu, lbn, color = color_transparent, textcolor = settings.htf_label_color, size = settings.htf_label_size, textalign = text.align_center)
        if not na(l2)
            label.set_xy(l2, offset+pcnt*delta,bosdata.sbd)
        else
            l2 := label.new(offset+pcnt*delta, bosdata.sbd, lbn, color = color_transparent, textcolor = settings.htf_label_color, size = settings.htf_label_size, textalign = text.align_center)
        pcnt += 1
        if not na(l_datesbu)
            label.set_xy(l_datesbu, offset+pcnt*delta,bosdata.sbu)
            label.set_text(l_datesbu, bosdata.s_dateu)
        else
            l_datesbu := label.new(offset+pcnt*delta, bosdata.sbu, 'ini', color = color_transparent, textcolor = settings.date_label_color, size = settings.date_label_size, textalign = text.align_center)
        if not na(l_datesbd)
            label.set_xy(l_datesbd, offset+pcnt*delta,bosdata.sbd)
            label.set_text(l_datesbd, bosdata.s_dated)
        else
            l_datesbd := label.new(offset+pcnt*delta, bosdata.sbd, 'ini', color = color_transparent, textcolor = settings.date_label_color, size = settings.date_label_size, textalign = text.align_center)
        pcnt += 1
        if not na(lt)
            label.set_xy(lt, offset+pcnt*delta,bosdata.sbu)
            label.set_text(lt,helper.RemainingTime(candleSet.settings.htf))
        else
            lt := label.new(offset+pcnt*delta, bosdata.sbu, helper.RemainingTime(candleSet.settings.htf), color = color_transparent, textcolor = settings.htf_timer_color, size = settings.htf_timer_size, textalign = text.align_center)
        if not na(lt2)
            label.set_xy(lt2, offset+pcnt*delta,bosdata.sbd)
            label.set_text(lt2,helper.RemainingTime(candleSet.settings.htf))
        else
            lt2 := label.new(offset+pcnt*delta, bosdata.sbd, helper.RemainingTime(candleSet.settings.htf), color = color_transparent, textcolor = settings.htf_timer_color, size = settings.htf_timer_size, textalign = text.align_center)
        pcnt += 1
        if not na(l_sbu)
            label.set_xy(l_sbu, offset+pcnt*delta,bosdata.sbu)
        else
            l_sbu := label.new(offset+pcnt*delta, bosdata.sbu, "SBU", color = color_transparent, textcolor = settings.sbu_label_color, size = settings.sbu_label_size, textalign = text.align_center)
        if not na(l_sbd)
            label.set_xy(l_sbd, offset+pcnt*delta,bosdata.sbd)
        else
            l_sbd := label.new(offset+pcnt*delta, bosdata.sbd, "SBD", color = color_transparent, textcolor = settings.sbd_label_color, size = settings.sbd_label_size, textalign = text.align_center)
        pcnt += 1    
        if not na(li_sbu)
            line.set_xy1(li_sbu, bar_index, bosdata.sbu)
            line.set_xy2(li_sbu, offset, bosdata.sbu)
        else
            li_sbu := line.new(bar_index, bosdata.sbu, offset, bosdata.sbu, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
        if not na(li_sbd)
            line.set_xy1(li_sbd, bar_index, bosdata.sbd)
            line.set_xy2(li_sbd, offset, bosdata.sbd)
        else
            li_sbd := line.new(bar_index, bosdata.sbd, offset, bosdata.sbd, xloc= xloc.bar_index, color = trace.trace_c_color, style = helper.LineStyle(trace.trace_c_style) , width = trace.trace_c_size)
    candleSet

//+---------------Main------------------+//
int cnt    = 0
int last   = helper.HTFEnabled()
int delta  = settings.text_buffer
int offset = settings.offset + bar_index

if  htf1.settings.show and helper.ValidTimeframe(htf1.settings.htf) 
    htf1.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf1.Monitor_Est().BOSJudge()
        plotdata(htf1, offset, delta)
    cnt +=1
if  htf2.settings.show and helper.ValidTimeframe(htf2.settings.htf) 
    htf2.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf2.Monitor_Est().BOSJudge()
        plotdata(htf2, offset, delta)
    cnt +=1
if  htf3.settings.show and helper.ValidTimeframe(htf3.settings.htf) 
    htf3.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf3.Monitor_Est().BOSJudge()
        plotdata(htf3, offset, delta)
    cnt +=1
if  htf4.settings.show and helper.ValidTimeframe(htf4.settings.htf) 
    htf4.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf4.Monitor_Est().BOSJudge()
        plotdata(htf4, offset, delta)
    cnt +=1
if  htf5.settings.show and helper.ValidTimeframe(htf5.settings.htf) 
    htf5.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf5.Monitor_Est().BOSJudge()
        plotdata(htf5, offset, delta)
    cnt +=1
if  htf6.settings.show and helper.ValidTimeframe(htf6.settings.htf) 
    htf6.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf6.Monitor_Est().BOSJudge()
        plotdata(htf6, offset, delta)
    cnt +=1
if  htf7.settings.show and helper.ValidTimeframe(htf7.settings.htf) 
    htf7.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf7.Monitor_Est().BOSJudge()
        plotdata(htf7, offset, delta)
    cnt +=1
if  htf8.settings.show and helper.ValidTimeframe(htf8.settings.htf) 
    htf8.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf8.Monitor_Est().BOSJudge()
        plotdata(htf8, offset, delta)
    cnt +=1
if  htf9.settings.show and helper.ValidTimeframe(htf9.settings.htf) 
    htf9.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf9.Monitor_Est().BOSJudge()
        plotdata(htf9, offset, delta)
    cnt +=1
if  htf10.settings.show and helper.ValidTimeframe(htf10.settings.htf) 
    htf10.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf10.Monitor_Est().BOSJudge()
        plotdata(htf10, offset, delta)
    cnt +=1
if  htf11.settings.show and helper.ValidTimeframe(htf11.settings.htf) 
    htf11.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf11.Monitor_Est().BOSJudge()
        plotdata(htf11, offset, delta)
    cnt +=1
if  htf12.settings.show and helper.ValidTimeframe(htf12.settings.htf) 
    htf12.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf12.Monitor_Est().BOSJudge()
        plotdata(htf12, offset, delta)
    cnt +=1
if  htf13.settings.show and helper.ValidTimeframe(htf13.settings.htf) 
    htf13.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf13.Monitor_Est().BOSJudge()
        plotdata(htf13, offset, delta)
    cnt +=1
if  htf14.settings.show and helper.ValidTimeframe(htf14.settings.htf) 
    htf14.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf14.Monitor_Est().BOSJudge()
        plotdata(htf14, offset, delta)
    cnt +=1
if  htf15.settings.show and helper.ValidTimeframe(htf15.settings.htf) 
    htf15.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf15.Monitor_Est().BOSJudge()
        plotdata(htf15, offset, delta)
    cnt +=1
if  htf16.settings.show and helper.ValidTimeframe(htf16.settings.htf) 
    htf16.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf16.Monitor_Est().BOSJudge()
        plotdata(htf16, offset, delta)
    cnt +=1
if  htf17.settings.show and helper.ValidTimeframe(htf17.settings.htf) 
    htf17.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf17.Monitor_Est().BOSJudge()
        plotdata(htf17, offset, delta)
    cnt +=1
if  htf18.settings.show and helper.ValidTimeframe(htf18.settings.htf) 
    htf18.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf18.Monitor_Est().BOSJudge()
        plotdata(htf18, offset, delta)
    cnt +=1
if  htf19.settings.show and helper.ValidTimeframe(htf19.settings.htf) 
    htf19.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf19.Monitor_Est().BOSJudge()
        plotdata(htf19, offset, delta)
    cnt +=1
if  htf20.settings.show and helper.ValidTimeframe(htf20.settings.htf) 
    htf20.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf20.Monitor_Est().BOSJudge()
        plotdata(htf20, offset, delta)
    cnt +=1
if  htf21.settings.show and helper.ValidTimeframe(htf21.settings.htf) 
    htf21.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf21.Monitor_Est().BOSJudge()
        plotdata(htf21, offset, delta)
    cnt +=1
if  htf22.settings.show and helper.ValidTimeframe(htf22.settings.htf) 
    htf22.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf22.Monitor_Est().BOSJudge()
        plotdata(htf22, offset, delta)
    cnt +=1
if  htf23.settings.show and helper.ValidTimeframe(htf23.settings.htf) 
    htf23.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf23.Monitor_Est().BOSJudge()
        plotdata(htf23, offset, delta)
    cnt +=1
if  htf24.settings.show and helper.ValidTimeframe(htf24.settings.htf) 
    htf24.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf24.Monitor_Est().BOSJudge()
        plotdata(htf24, offset, delta)
    cnt +=1
if  htf25.settings.show and helper.ValidTimeframe(htf25.settings.htf) 
    htf25.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf25.Monitor_Est().BOSJudge()
        plotdata(htf25, offset, delta)
    cnt +=1
if  htf26.settings.show and helper.ValidTimeframe(htf26.settings.htf) 
    htf26.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf26.Monitor_Est().BOSJudge()
        plotdata(htf26, offset, delta)
    cnt +=1
if  htf27.settings.show and helper.ValidTimeframe(htf27.settings.htf) 
    htf27.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf27.Monitor_Est().BOSJudge()
        plotdata(htf27, offset, delta)
    cnt +=1
if  htf28.settings.show and helper.ValidTimeframe(htf28.settings.htf) 
    htf28.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf28.Monitor_Est().BOSJudge()
        plotdata(htf28, offset, delta)
    cnt +=1
if  htf29.settings.show and helper.ValidTimeframe(htf29.settings.htf) 
    htf29.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf29.Monitor_Est().BOSJudge()
        plotdata(htf29, offset, delta)
    cnt +=1
if  htf30.settings.show and helper.ValidTimeframe(htf30.settings.htf) 
    htf30.Monitor().BOSJudge()
    if barstate.isrealtime or barstate.islast
        htf30.Monitor_Est().BOSJudge()
        plotdata(htf30, offset, delta)
    cnt +=1

if cnt>last
    label.new(bar_index,high,"over the line count limit 30")

index += 1


