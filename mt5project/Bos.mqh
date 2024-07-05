#ifndef __BOS_MQH__
#define __BOS_MQH__
#include "Plotpack.mqh"
#include "GETDATA.mqh"
#include "Helper.mqh"
struct BOS{
    int             htfint      ;//=i
    int             baraday     ;//= MathCeil(__DAYMIN/htfint);
    int             baradayrm   ;// __DAYMIN%i;
    string          htfname     ;//IntegerToString(i)
    double          sbu         ;
    double          sbd         ;
    datetime        sbu_t       ;
    datetime        sbd_t       ;
    int             slope1      ;
    int             slope2      ;
    int             state       ; //ini 
    int             reg1key     ;
    datetime        reg1key_t   ;
    int             reg2key     ;
    datetime        reg2key_t   ;
    double          regclose1   ;
    double          regclose2   ;
    double          regclose3   ;
    datetime        regclose1_t ;
    datetime        regclose2_t ;
    datetime        regclose3_t ;
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

    BOS(int i,string ulb, string up, string ul, string dlb, string dp, string dl):sbu_l(ulb), sbu_price(up), sbu_line(ul),sbd_l(dlb), sbd_price(dp), sbd_line(dl){
        htfint      = i ;
        baraday     = MathCeil(__DAYMIN/htfint);
        baradayrm   = __DAYMIN%i ;
        htfname     = IntegerToString(i);
        sbu         = -2;
        sbd         = -1;
        slope1      = 0;
        slope2      = 0;
        state       = 1;
        regclose1   = -1;
        regclose2   = -1;
        regclose3   = -1;
        regclose1_t = -1;
        regclose2_t = -1;
        regclose3_t = -1;
    }
};

struct Triset{
    uint    comparecode ;
    int     base        ;
    int     itv         ;
    bool    u_inside    ;
    bool    d_inside    ;
    Triset(){
        comparecode = 0;
        u_inside    = false;
        d_inside    = false;
    }
};
uint LeftRotate(uint value, int shift) {
    int bits = 32; // 假设是32位无符号整数
    shift = shift % bits; // 处理移位大于位数的情况
    return (value << shift) | (value >> (bits - shift));
}
uint RightRotate(uint value, int shift) {
    int bits = 32; // 假设是32位无符号整数
    shift = shift % bits; // 处理移位大于位数的情况
    return (value >> shift) | (value << (bits - shift));
}
void Insertalg(double& arr[], int& index[]){
    for (int i = 1; i < 8; ++i) {
        double key = arr[i];
        int keyIndex = index[i];
        int j = i - 1; // 
        while (j >= 0 && arr[j] > key) {//從左比到現在的key 有種n階梯比較的概念 //
            arr[j + 1] = arr[j];
            index[j + 1] = index[j];
            j = j - 1;
        }
        arr[j + 1] = key; //swap
        index[j + 1] = keyIndex;
    }

}
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
            if(bosdata.sbd != -1 && bosdata.sbu != -2){
                bosdata.state = 2 ;
            }
            else if(bosdata.sbd !=-1 && bosdata.sbu==-2){
                bosdata.state = 3 ;
            }
            else if(bosdata.sbd ==-1 && bosdata.sbu != -2){
                bosdata.state = 4 ;
            }
            else{
                label lb("templb");
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
                bosdata.sbu     = -2;
                bosdata.sbu_t   = -2;
                bosdata.sbd     = bosdata.reg1key;
                bosdata.sbd_t   = bosdata.reg1key_t;
            }
            if(bosdata.regclose3<bosdata.sbd){
                bosdata.sbd     = -1 ;
                bosdata.sbd_t   = -1 ;
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
                bosdata.sbd         = -1;
                bosdata.sbd_t       = -1;
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
                bosdata.sbu         = -2;
                bosdata.sbu_t       = -2;
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

Triset TriCode(Triset& ts, BOS& bos1, BOS& bos2, BOS& bos3, BOS& bos4){
    //-1 == no sbd, -2 == no sbu
    uint  code      = ts.comparecode ;
    code            = 0 ;
    int count1      = 0 ;
    int count2      = 0 ;
    ts.base         = bos1.htfint    ;
    ts.itv          = bos2.htfint-bos1.htfint;
    double arr[8]   ={bos4.sbu, bos3.sbu, bos2.sbu, bos1.sbu, bos1.sbd, bos2.sbd, bos3.sbd, bos4.sbd};
    int    index[8] ={28, 24, 20, 16, 12, 8, 4, 0}; //according to the index[i], I can know that which bos is represnented. And. i is comparison result.
    Insertalg(arr, index);
    for (int i = 0; i < 8; ++i) {
        code = (arr[i] == -1) ? (code & (LeftRotate(__7f10fMASK, index[i]))) : (arr[i] == -2) ? (code | (LeftRotate(__701ffMASK, index[i]))) :(code | ((i + 1) << index[i]));
    }
    if((code & __LEVEL1SBDMASK)>>4 > (code & __LEVEL2SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBDMASK)>>8 > (code & __LEVEL3SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBDMASK)>>12 > (code & __LEVEL4SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBUMASK)<<4  < (code & __LEVEL2SBUMASK)){
        ++count2 ;
    }
    if((code & __LEVEL1SBUMASK)<<8  < (code & __LEVEL3SBUMASK)){
        ++count2 ;
    }
    if((code & __LEVEL1SBUMASK)<<12 < (code & __LEVEL4SBUMASK)){
        ++count2 ;
    }
    
    ts.u_inside = count1==3? true : false ;
    ts.d_inside = count2==3? true : false ; 
    return ts;
}

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful