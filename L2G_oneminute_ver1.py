type Count_Type
  int x
  int y
  int z
  float count
  float fiff
  float barcount
  
type Flag_Type
  bool ct_start
  bool ct_end
type CurrentTime_Type
  float currentperiod
  float currentperiod_div4
  int currentYear 
  int currentMon
  int currentDay
  int currentHr
  int currentMin
  int HrMin2Min
  float starttime
  int HrMin2Min2
  float lasttime
//**
//+----local parameter and constant----+//
var const int RESET = 1
var const int ARRAYGEN = 2
var const int PLOT = 3
var const int SURRD = 4
var const int NOSKY = 5
var const int NOGRD = 6
var const int DAY2MINUTE = 1440
var const int EIGHTCAP_CRYPTO = 0
var const int EIGHTCAP_FOREX = 0
var const int EIGHTCAP_CFD = 60
var const int SAXO_CRYPTO = 1020
var const int SAXO_FOREX = 1020
var const int SAXO_CFD = 1080
var const int OANDA_CRYPTO = 1020
var const int OANDA_FOREX = 1020
var const int OANDA_CFD= 1020

//+----common variable----+//
var int numbershift = na
var int state = na
var int nextstate = na
var float Quotient = na
var float Remainder = na
var float diff = na
var int buffyear = na
var int buffmonth = na
var int buffday = na
var int buffhour = na
var int buffmin = na
var int arraysize = na
var float Remainder2Bar = na
var float fourminus_Remainger2Bar = na
var int index = 0
var string str_timeframe = na
var float flt_timeframe = na 
var string TICKERID = syminfo.tickerid
var string ITSTYPE = syminfo.type
var arrayclose = array.new<float>(0)
var int BASETIME = 0
var string EXCHANGE = na
var float ttlbar = na

   