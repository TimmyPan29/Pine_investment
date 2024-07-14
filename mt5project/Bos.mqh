#ifndef __BOS_MQH__
#define __BOS_MQH__
#include "Plotpack.mqh"
#include "GETDATA.mqh"
#include "Helper.mqh"
struct BOS{
    double          htfint      ;//=i
    string          htfname     ;//IntegerToString(i)
    double          sbu         ;
    double          sbd         ;
    datetime        sbu_t       ;
    datetime        sbd_t       ;
    int             slope1      ;
    int             slope2      ;
    int             state       ; //ini 
    double          reg1key     ;
    datetime        reg1key_t   ;
    double          reg2key     ;
    datetime        reg2key_t   ;
    double          regclose1   ;
    double          regclose2   ;
    double          regclose3   ;
    datetime        regclose1_t ;
    datetime        regclose2_t ;
    datetime        regclose3_t ;
    label           sbu_lb      ;
    line            sbu_ln      ;
    string          s_udate     ;
    label           sbd_lb      ;
    line            sbd_ln      ;
    string          s_ddate     ;
    datetime        t_temp1     ;
    datetime        t_temp2     ;

    BOS():sbu_lb(""),sbu_ln(""),sbd_lb(""),sbd_ln(""){
        htfint = 0;
        htfname = "";
        sbu = 0.0;
        sbd = 0.0;
        sbu_t = 0;
        sbd_t = 0;
        slope1 = 0.0;
        slope2 = 0.0;
        state = 1;
        regclose1 = 0.0;
        regclose2 = 0.0;
        regclose3 = 0.0;
        regclose1_t = 0.0;
        regclose2_t = 0.0;
        regclose3_t = 0.0;
    }

    // 带参数的构造函数
    BOS(int i):sbu_lb("sbu_lb" + IntegerToString(i)),sbu_ln("sbu_line" + IntegerToString(i)),sbd_lb("sbd_lb" + IntegerToString(i)),sbd_ln("sbd_line" + IntegerToString(i)) {
        htfint = i;
        htfname = IntegerToString(i);
        sbu = 0;
        sbd = 0;
        sbu_t = 0;
        sbu_t = 0;
        slope1 = 0;
        slope2 = 0;
        state = 1;
        regclose1 = 0;
        regclose2 = 0;
        regclose3 = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
    }
};

struct Triset{
    uint    comparecode[] ;
    bool    u_inside[]   ;
    bool    d_inside[]    ;
   
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
void BOSJudge(BOS& bosdata, const int size, Rawdatagroup& rd, const int starti, Helper& helper){
    int k                         ;                     
    int qidxnow                   ;
    int qidxpt                    ;
    double tempprice              ;
    datetime temptime             ;
    k               = starti+1    ;
    while(k < size){//last one can not be considered cuz it's not closed
        qidxnow = helper.TurnMin(rd.datadate[k])==0? 1439 : helper.TurnMin(rd.datadate[k])-1;
        qidxpt  = helper.TurnMin(rd.datadate[k-1])==0? 1439 : helper.TurnMin(rd.datadate[k-1])-1 ;        
        if(rd.dataQuo[qidxnow] != rd.dataQuo[qidxpt]){
            //Print("qidxnow= ", qidxnow, "qidxpt", qidxpt, "bosdata.htfint", bosdata.htfint);
            tempprice = rd.rawprices[k-1] ;
            temptime  = rd.datadate[k-1]  ;
            //if(bosdata.htfint==4)printf("k= %d \t tempprice@k-1= %.5f \t date@k-1= %s\n htfint= %.1f", k, tempprice,TimeToString(temptime,TIME_DATE|TIME_MINUTES),bosdata.htfint);
            if(bosdata.state == 1){
                bosdata.regclose1 = bosdata.regclose2;
                bosdata.regclose2 = bosdata.regclose3;
                bosdata.regclose3 = tempprice;
                bosdata.regclose1_t = bosdata.regclose2_t;
                bosdata.regclose2_t = bosdata.regclose3_t;
                bosdata.regclose3_t = temptime;
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
                    lb.Create(lb.name1);
                }
            }
            //Print("k: ", k, " state: ", bosdata.state, " bosdata.htfint: ", bosdata.htfint, "tempprice", tempprice);
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
                    bosdata.reg1key_t   = bosdata.reg2key_t;
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
        }
        ++k; 
    }//while end
}//func end

Triset TriCode(Triset& ts, BOS& bos1, BOS& bos2, BOS& bos3, BOS& bos4, int j){
    //-1 == no sbd, -2 == no sbu
    uint  code      = ts.comparecode[j] ;
    code = 0 ;
    int count1      = 0 ;
    int count2      = 0 ;
    double arr[8]   = {bos4.sbd, bos3.sbd, bos2.sbd, bos1.sbd, bos1.sbu, bos2.sbu, bos3.sbu, bos4.sbu};
    int    index[8] ={28, 24, 20, 16, 12, 8, 4, 0}; //according to the index[i], I can know that which bos is represnented. And. i is comparison result.
    Insertalg(arr, index);
    for (int i = 0; i < 8; ++i) {
        code = (arr[i] == -1) ? (code & (LeftRotate(__7f10fMASK, index[i]))) : (arr[i] == -2) ? (code | (LeftRotate(__701ffMASK, index[i]))) :(code | ((i + 1) << index[i]));
    }
    if((code & __LEVEL1SBDMASK)<<4 > (code & __LEVEL2SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBDMASK)<<8 > (code & __LEVEL3SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBDMASK)<<12 > (code & __LEVEL4SBDMASK)){
        ++count1 ;
    }
    if((code & __LEVEL1SBUMASK)>>4  < (code & __LEVEL2SBUMASK)){
        ++count2 ;
    }
    if((code & __LEVEL1SBUMASK)>>8  < (code & __LEVEL3SBUMASK)){
        ++count2 ;
    }
    if((code & __LEVEL1SBUMASK)>>12 < (code & __LEVEL4SBUMASK)){
        ++count2 ;
    }
    ts.comparecode[j]= code ;
    ts.d_inside[j]   = count1==3? true : false ;
    ts.u_inside[j]   = count2==3? true : false ;
    //Print("bos1.htfint: ", bos1.htfint);
    return ts;
}

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful

//         if (count == bosdata.baraday && bosdata.baradayrm!=0){
//             k     -= bosdata.baradayrm;
//             count  = 1; 

//         }
//         else{
//             if((k == starti || k == starti - __DAYMIN * r)&& bosdata.htfint != 1){
//                 k -= (bosdata.htfint-1);
//             }
//             else{
//                 k -= bosdata.htfint;
//             }
//             ++count ;  
//         }