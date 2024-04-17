type Delta_Type
    float x_U1o4 = 0
    float x_U2o4 = 0
    float x_U3o4 = 0
    float x_U4o4 = 0
    float x_D1o4 = 0    
    float x_D2o4 = 0    
    float x_D3o4 = 0    
    float x_D4o4 = 0    
//**
method BOScal_level1(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = na
    j := 0
    while f.bosFlag 
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
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_1over4 := b.Buff_close2_1over4
                        b.index_key1_1over4 := index-1
                    if(b.Buff_close3_1over4>b.close_SBU_1over4)
                        b.close_SBU_1over4 := na
                        b.close_SBD_1over4 := b.Buff_key1_1over4
                        b.index_SBD_1over4 := b.index_key1_1over4
                    else if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.close_SBD_1over4 := na
                        b.close_SBU_1over4 := b.Buff_key1_1over4
                        b.index_SBU_1over4 := b.index_key1_1over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index-1
                        b.close_SBU_1over4 := b.Buff_key2_1over4
                        b.index_SBU_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                        b.index_key1_1over4 := b.index_key2_1over4
                    if(b.Buff_close3_1over4<b.close_SBD_1over4)
                        b.close_SBD_1over4 := na
                        b.index_SBD_1over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_1over4 := b.Buff_close2_1over4
                        b.index_key2_1over4 := index-1
                        b.close_SBD_1over4 := b.Buff_key2_1over4
                        b.index_SBD_1over4 := b.index_key2_1over4
                        b.Buff_key1_1over4 := b.Buff_key2_1over4
                        b.index_key1_1over4 := b.index_key2_1over4
                    if(b.Buff_close3_1over4>b.close_SBU_1over4)
                        b.close_SBU_1over4 := na
                        b.index_SBU_1over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 1
            break
        //end while
        if(j>=4)
            break
//        count := j%4==0? count+1 : count
//        if(count==c.Barcount) //it means diff<0, jump over the day or today is at the end. 
//            break
    //end while
//end method   
method BOScal_level2(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = 1
    while f.bosFlag 
        if((not na(b.close_SBU_2over4)) and (not na(b.close_SBD_2over4)) )//有天地 留在SURRD 依此類推
            b.state_2over4 := SURRD
        else if ((na(b.close_SBU_2over4)) and (not na(b.close_SBD_2over4)) )
            b.state_2over4 := NOSKY
        else
            b.state_2over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_2over4 := b.Buff_close2_2over4
            b.Buff_close2_2over4 := b.Buff_close3_2over4 
            b.Buff_close3_2over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_2over4 - b.Buff_close1_2over4>0? 1 : -1
            b.slope2 := b.Buff_close3_2over4 - b.Buff_close2_2over4>0? 1 : -1
            switch b.state_2over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_2over4 := b.Buff_close2_2over4
                        b.index_key1_2over4 := index-1
                    if(b.Buff_close3_2over4>b.close_SBU_2over4)
                        b.close_SBU_2over4 := na
                        b.close_SBD_2over4 := b.Buff_key1_2over4
                        b.index_SBD_2over4 := b.index_key1_2over4
                    else if(b.Buff_close3_2over4<b.close_SBD_2over4)
                        b.close_SBD_2over4 := na
                        b.close_SBU_2over4 := b.Buff_key1_2over4
                        b.index_SBU_2over4 := b.index_key1_2over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_2over4 := b.Buff_close2_2over4
                        b.index_key2_2over4 := index-1
                        b.close_SBU_2over4 := b.Buff_key2_2over4
                        b.index_SBU_2over4 := b.index_key2_2over4
                        b.Buff_key1_2over4 := b.Buff_key2_2over4
                        b.index_key1_2over4 := b.index_key2_2over4
                    if(b.Buff_close3_2over4<b.close_SBD_2over4)
                        b.close_SBD_2over4 := na
                        b.index_SBD_2over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_2over4 := b.Buff_close2_2over4
                        b.index_key2_2over4 := index-1
                        b.close_SBD_2over4 := b.Buff_key2_2over4
                        b.index_SBD_2over4 := b.index_key2_2over4
                        b.Buff_key1_2over4 := b.Buff_key2_2over4
                        b.index_key1_2over4 := b.index_key2_2over4
                    if(b.Buff_close3_2over4>b.close_SBU_2over4)
                        b.close_SBU_2over4 := na
                        b.index_SBU_2over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 2
            break
        //end while
        if(j>=4)
            break
//        count := j%4==0? count+1 : count
//        if((count == c.Barcount and f.diffFlag) or (count == Quotient+1 and not(f.diffFlag))) //it means diff<0, jump over the day or today is at the end. 
//            break //fix if j==4 break
    //end while
//end method  
method BOScal_level3(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = na
    if(NowBar>52)
        NowBar := NowBar-52
    j := NowBar%3==1? 2 : NowBar%3==2? 1 : 0
    while f.bosFlag 
        if((not na(b.close_SBU_3over4)) and (not na(b.close_SBD_3over4)) )//有天地 留在SURRD 依此類推
            b.state_3over4 := SURRD
        else if ((na(b.close_SBU_3over4)) and (not na(b.close_SBD_3over4)) )
            b.state_3over4 := NOSKY
        else
            b.state_3over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_3over4 := b.Buff_close2_3over4
            b.Buff_close2_3over4 := b.Buff_close3_3over4 
            b.Buff_close3_3over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_3over4 - b.Buff_close1_3over4>0? 1 : -1
            b.slope2 := b.Buff_close3_3over4 - b.Buff_close2_3over4>0? 1 : -1
            switch b.state_3over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_3over4 := b.Buff_close2_3over4
                        b.index_key1_3over4 := index-1
                    if(b.Buff_close3_3over4>b.close_SBU_3over4)
                        b.close_SBU_3over4 := na
                        b.close_SBD_3over4 := b.Buff_key1_3over4
                        b.index_SBD_3over4 := b.index_key1_3over4
                    else if(b.Buff_close3_3over4<b.close_SBD_3over4)
                        b.close_SBD_3over4 := na
                        b.close_SBU_3over4 := b.Buff_key1_3over4
                        b.index_SBU_3over4 := b.index_key1_3over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_3over4 := b.Buff_close2_3over4
                        b.index_key2_3over4 := index-1
                        b.close_SBU_3over4 := b.Buff_key2_3over4
                        b.index_SBU_3over4 := b.index_key2_3over4
                        b.Buff_key1_3over4 := b.Buff_key2_3over4
                        b.index_key1_3over4 := b.index_key2_3over4
                    if(b.Buff_close3_3over4<b.close_SBD_3over4)
                        b.close_SBD_3over4 := na
                        b.index_SBD_3over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_3over4 := b.Buff_close2_3over4
                        b.index_key2_3over4 := index-1
                        b.close_SBD_3over4 := b.Buff_key2_3over4
                        b.index_SBD_3over4 := b.index_key2_3over4
                        b.Buff_key1_3over4 := b.Buff_key2_3over4
                        b.index_key1_3over4 := b.index_key2_3over4
                    if(b.Buff_close3_3over4>b.close_SBU_3over4)
                        b.close_SBU_3over4 := na
                        b.index_SBU_3over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 3
            break
        //end while
        if(j>=4)
            break
//        count := j%4==0? count+1 : count
//        if((count == c.Barcount and f.diffFlag) or (count == Quotient+1 and not(f.diffFlag))) //it means diff<0, jump over the day or today is at the end. 
//            break
    //end while
//end method   
method BOScal_level4(BOS_Type b, Count_Type c, Flag_Type f, array<float> arr, float Quotient, int index) => 
    float count = c.boscount //if count == Barcount? if crossover day ?
    float NowBar = count + 1
    int j = 3
    while f.bosFlag 
        if((not na(b.close_SBU_4over4)) and (not na(b.close_SBD_4over4)) )//有天地 留在SURRD 依此類推
            b.state_4over4 := SURRD
        else if ((na(b.close_SBU_4over4)) and (not na(b.close_SBD_4over4)) )
            b.state_4over4 := NOSKY
        else
            b.state_4over4 := NOGRD
        while j<array.size(arr)
            b.Buff_close1_4over4 := b.Buff_close2_4over4
            b.Buff_close2_4over4 := b.Buff_close3_4over4 
            b.Buff_close3_4over4 := array.get(arr,j)
            b.slope1 := b.Buff_close2_4over4 - b.Buff_close1_4over4>0? 1 : -1
            b.slope2 := b.Buff_close3_4over4 - b.Buff_close2_4over4>0? 1 : -1
            switch b.state_4over4
                SURRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key1_4over4 := b.Buff_close2_4over4
                        b.index_key1_4over4 := index-1
                    if(b.Buff_close3_4over4>b.close_SBU_4over4)
                        b.close_SBU_4over4 := na
                        b.close_SBD_4over4 := b.Buff_key1_4over4
                        b.index_SBD_4over4 := b.index_key1_4over4
                    else if(b.Buff_close3_4over4<b.close_SBD_4over4)
                        b.close_SBD_4over4 := na
                        b.close_SBU_4over4 := b.Buff_key1_4over4
                        b.index_SBU_4over4 := b.index_key1_4over4
//                    else //maintain SURRD still in bounded box
                NOSKY =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_4over4 := b.Buff_close2_4over4
                        b.index_key2_4over4 := index-1
                        b.close_SBU_4over4 := b.Buff_key2_4over4
                        b.index_SBU_4over4 := b.index_key2_4over4
                        b.Buff_key1_4over4 := b.Buff_key2_4over4
                        b.index_key1_4over4 := b.index_key2_4over4
                    if(b.Buff_close3_4over4<b.close_SBD_4over4)
                        b.close_SBD_4over4 := na
                        b.index_SBD_4over4 := na
                NOGRD =>
                    if(b.slope1 != b.slope2)
                        b.Buff_key2_4over4 := b.Buff_close2_4over4
                        b.index_key2_4over4 := index-1
                        b.close_SBD_4over4 := b.Buff_key2_4over4
                        b.index_SBD_4over4 := b.index_key2_4over4
                        b.Buff_key1_4over4 := b.Buff_key2_4over4
                        b.index_key1_4over4 := b.index_key2_4over4
                    if(b.Buff_close3_4over4>b.close_SBU_4over4)
                        b.close_SBU_4over4 := na
                        b.index_SBU_4over4 := na          
                =>
                    label.new(bar_index,low,"something wrong")
            //end switch
            j += 4
            break
        //end while
        if(j>=4)
            break
//        count := j%4==0? count+1 : count
//        if((count == c.Barcount and f.diffFlag) or (count == Quotient+1 and not(f.diffFlag))) //it means diff<0, jump over the day or today is at the end. 
//            break
    //end while
//end method  
method reorderSBlabel(BOS_Type b, Delta_Type d, close) =>
    int x = na
    float base = 0.05
    arrU = array.from(b.close_SBU_1over4, b.close_SBU_2over4, b.close_SBU_3over4, b.close_SBU_4over4)
    arrD = array.from(b.close_SBD_1over4, b.close_SBD_2over4, b.close_SBD_3over4, b.close_SBD_4over4)
    Uindices = array.sort_indices(arrU,ascending)
    Dindices = array.sort_indices(arrD,descending)
    if(close>=10000)
        x := 1000
    else if(close>=1000 and close<10000)
        x := 100
    else if(close>=100 and close<1000)
        x := 10
    else
        x := 1
    d.x_U1o4 := base*array.get()


//end method