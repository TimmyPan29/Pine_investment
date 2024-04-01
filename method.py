type Count_Type
   int levelcount = 0
   float count1 = 0 
   int boscount = 0
   float Barcount = 0
   float RmnBarcount = 0
type BOS_Type
   int slope1 = na
   int slope2 = na
   int state_1over4 = SURRD
   int state_2over4 = SURRD
   int state_3over4 = SURRD
   int state_4over4 = SURRD
   int index_key1_1over4 = 0
   int index_key2_1over4 = na
   int index_key1_2over4 = na
   int index_key2_2over4 = na
   int index_key1_3over4 = na
   int index_key2_3over4 = na
   int index_key1_4over4 = na
   int index_key2_4over4 = na
   int index_SBU_1over4 = 0
   int index_SBD_1over4 = 0
   int index_SBU_2over4 = 0
   int index_SBD_2over4 = 0
   int index_SBU_3over4 = 0
   int index_SBD_3over4 = 0
   int index_SBU_4over4 = 0
   int index_SBD_4over4 = 0
   float close_SBU_1over4 = 0
   float close_SBD_1over4 = 0
   float close_SBU_2over4 = 0
   float close_SBD_2over4 = 0
   float close_SBU_3over4 = 0
   float close_SBD_3over4 = 0
   float close_SBU_4over4 = 0
   float close_SBD_4over4 = 0
   float Buff_key1_1over4 = 0
   float Buff_key2_1over4 = na
   float Buff_key1_2over4 = 0
   float Buff_key2_2over4 = na
   float Buff_key1_3over4 = 0
   float Buff_key2_3over4 = na
   float Buff_key1_4over4 = 0
   float Buff_key2_4over4 = na
   float Buff_close1_1over4 = 0
   float Buff_close2_1over4 = 0
   float Buff_close3_1over4 = 0
   float Buff_close1_2over4 = 0
   float Buff_close2_2over4 = 0
   float Buff_close3_2over4 = 0
   float Buff_close1_3over4 = 0
   float Buff_close2_3over4 = 0
   float Buff_close3_3over4 = 0
   float Buff_close1_4over4 = 0
   float Buff_close2_4over4 = 0
   float Buff_close3_4over4 = 0   
//**
type Flag_Type
    bool SizeFlag
    bool GoFlag
    bool resetFlag 
    bool plotFlag
    bool diffFlag
    bool bosFlag
    bool jumpFlag
//**
var const int RESET = 1
var const int ARRAYGEN = 2
var const int PLOT = 3
var const int SURRD = 4
var const int NOSKY = 5
var const int NOGRD = 6
var const int DAY2MINUTE = 1440
var const int FOREX_OANDATIME = 1020
var const int FOREX_OPENTIMEEIGHTCAP = 0
//the life cycle of this method live untill count == size()
method BOScal_level1(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
  int count = c.boscount //if count == Barcount? if crossover day ?
  int diff = c.Barcount - c.boscount
  int NowBar = count + 1
  int j = 0
  while f.bosflag 
    if((not na(b.close_SBU_1over4)) and (not na(b.close_SBD_1over4)) )//有天地 留在SURRD 依此類推
      b.state_1over4 := SURRD
    else if ((na(b.close_SBU_1over4)) and (not na(b.close_SBD_1over4)) )
      b.state_1over4 := NOSKY
    else
      b.state_1over4 := NOGRD
    while j<array.size(arr)
      b.Buff_close1_1over4 := b.Buff_close2_1over4
      b.Buff_close2_1over4 := b.Buff_close3_1over4 
      b.Buff_close3_1over4 := array.get(arr,j)
      b.slope1 := b.Buff_close2_1over4 - b.Buff_close1_1over4>0? 1 : -1
      b.slope2 := b.Buff_close3_1over4 - b.Buff_close2_1over4>0? 1 : -1
      switch b.state_1over4
        SURRD =>
          if(b.Buff_close3_1over4>b.close_SBU_1over4)
            b.close_SBU_1over4 := na
            b.close_SBD_1over4 := b.Buff_key1_1over4
            b.index_SBD_1over4 := index
          else if(b.Buff_close3_1over4<b.close_SBD_1over4)
            b.close_SBD_1over4 := na
            b.close_SBU_1over4 := b.Buff_key1_1over4
            b.index_SBU_1over4 := index
          else //maintain SURRD

              
          
        NOSKY =>

        NOGRD =>
        =>
          label.new(bar_index,low,"something wrong")
    //end switch
      j += 1
      break
  //end while
    count := ((j+1)%4)==0? count+1 : count
    if((count == c.Barcount and f.diffFlag) or ((count == Quotient+1) and not(f.diffFlag)) //it means diff<0, jump over the day or today is at the end. 
      break
//end while
    




