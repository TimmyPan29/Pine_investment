#ifndef __BOS_MQH__
#define __BOS_MQH__
#ifndef __GETDATA_MQH__
#define __GETDATA_MQH__
struct BOS{
    int             htfint      ;//=i
    int             baraday     ;//= MathCeil(__DAYMIN/htfint);
    int             baradayrm   ;// __DAYMIN;
    string          htfname     ;//inttostring
    double          sbu      = 0;
    double          sbd      = 0;
    datetime        sbu_t       ;
    datetime        sbd_t       ;
    int             slope1   = 0;
    int             slope2   = 0;
    int             state    = 1; //ini 
    int             reg1key  = 0;
    datetime        reg1key_t   ;
    int             reg2key  = 0;
    datetime        reg2key_t   ;
    double          regclose1= 0;
    double          regclose2= 0;
    double          regclose3= 0;
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
        


        k += (count == bosdata.baraday+1)? bosdata.htfint : bosdata.baradayrm;
        ++count;
    }


}

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful