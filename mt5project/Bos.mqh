#ifndef __BOS_MQH__
#define __BOS_MQH__
#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
#ifndef __PLOTPACK_MQH__
#define __PLOTPACK_MQH__
struct BOS{
    int             htfint             ;//=i
    int             baraday            ;//= MathCeil(__DAYMIN/htfint);
    int             baradayrm          ;// __DAYMIN;
    string          htfname            ;//inttostring
    double          sbu             = 0;
    double          sbd             = 0;
    datetime        sbu_t              ;
    datetime        sbd_t              ;
    int             slope1          = 0;
    int             slope2          = 0;
    int             state           = 1; //ini 
    int             reg1key         = 0;
    datetime        reg1key_t          ;
    int             reg2key         = 0;
    datetime        reg2key_t          ;
    double          regclose1_t     = 0;
    double          regclose2_t     = 0;
    double          regclose3_t     = 0;
    datetime        regclose1_t     = 0;
    datetime        regclose2_t     = 0;
    datetime        regclose3_t     = 0;
    label           sbu_l       ;
    label           sbu_price   ;
    line            sbu_line    ;
    string          s_udate     ;
    label           sbd_l       ;
    label           sbd_price   ;
    line            sbd_line    ;
    string          s_ddate     ;
    datetime        t_temp1     ;
    datetime        t_temp2     ;
};

void BOSJudge(BOS& bosdata, const int size, const Rawdatagroup& rd, const int& starti, int tint){
    int k         = starti      ;                     
    int count     = 1           ;
    while(k < size){
        if(bosdata.state == 1){
            bosdata.regclose1 = bosdata.regclose2;
            bosdata.regclose2 = bosdata.regclose3;
            bosdata.regclose3 = rd.rawprices[k];
            bosdata.regclose1_t = bosdata.regclose2_t;
            bosdata.regclose2_t = bosdata.regclose3_t;
            bosdata.regclose3_t = rd.datadate[k];
            bosdata.slope1 = bosdata.regclose2 - bosdata.regclose1>0? 1 : -1;
            bosdata.slope2 = bosdata.regclose3 - bosdata.regclose2>0? 1 : -1;
            if((not na(bosdata.sbd)) and (not na(bosdata.sbu))){
                bosdata.state = 2 ;
            }
            else if(not na(bosdata.sbd) and na(bosdata.sbu)){
                bosdata.state = 3 ;
            }
            else if(na(bosdata.sbd) and (not na(bosdata.sbu))){
                bosdata.state = 4 ;
            }
            else{
                label lb;
                lb.Create();
            }
        }
        if(bosdata.state == 2){
            if(bosdata.slope1 != bosdata.slope2){
                bosdata.reg1key     = bosdata.regclose2;
                bosdata.reg1key_t   = bosdata.regclose2_t ;
            }
            //else //Buff_key1維持原樣
            if(bosdata.regclose3>bosdata.sbu){
                bosdata.sbu     = 0;
                bosdata.sbu_t   = 0;
                bosdata.sbd     = bosdata.reg1key;
                bosdata.sbd_t   = bosdata.reg1key_t;
            }
            if(bosdata.regclose3<bosdata.sbd){
                bosdata.sbd     = 0 ;
                bosdata.sbd_t   = 0 ;
                bosdata.sbu     = bosdata.reg1key;
                bosdata.sbu_t   = bosdata.reg1key_t;
            }
            bosdata.state = 1;
        }
        if(bosdata.state == 3){//no sky
            if(bosdata.slope1 != bosdata.slope2){ // build sky
                bosdata.reg2key     = bosdata.regclose2;
                bosdata.reg2key_t   = bosdata.regclose2_t;
                bosdata.sbu         = bosdata.reg2key;
                bosdata.sbu_t       = bosdata.reg2key_t;
                bosdata.reg1key     = bosdata.reg2key;
                bosdata.reg1key_t    = bosdata.reg2key_t;
            }
            if(bosdata.regclose3<bosdata.sbd){
                bosdata.sbd         = 0;
                bosdata.sbd_t       = 0;
            }
            bosdata.state = 1;
        }
        if(bosdata.state == 4){
            if(bosdata.slope1 != bosdata.slope2){
                bosdata.reg2key     = bosdata.regclose2;
                bosdata.reg2key_t   = bosdata.regclose2_t;
                bosdata.sbd         = bosdata.reg2key;
                bosdata.sbd_t       = bosdata.reg2key_t;
                bosdata.reg1key     = bosdata.reg2key;
                bosdata.reg1key_t   = bosdata.reg2key_t;
            }
            if(bosdata.regclose3>bosdata.sbu){
                bosdata.sbu         = 0;
                bosdata.sbu_t       = 0;
            }
            bosdata.state = 1;
        }
        if (count == bosdata.baraday){
            k     += bosdata.baradayrm;
            count  = 1; 

        }
        else{
            k += bosdata.htfint;
            ++count ;
        }

    }//while end


}//func end

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful