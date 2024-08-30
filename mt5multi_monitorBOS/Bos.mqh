#ifndef __BOS_MQH__
#define __BOS_MQH__
#include "Plotpack.mqh"
#include "GETDATA.mqh"
#include "Helper.mqh"
#define FVGarraysize 3000
struct BOS{
    double          htfint      ;//=i
    string          htfname     ;//IntegerToString(i)
    double          sbu         ;
    double          sbd         ;
    datetime        sbu_t       ;
    datetime        sbd_t       ;
    int             slope1      ;
    int             slope2      ;
    int             bar1idx     ;
    int             bar2idx     ;
    int             bar3idx     ;
    int             barkey1     ;
    int             barkey2     ;
    int             cnt1idx     ;
    int             cnt2idx     ;
    int             cnt3idx     ;
    int             cntkey1     ;
    int             cntkey2     ;
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

    BOS():sbu_lb(""),sbu_ln(""),sbd_lb(""),sbd_ln(""){
        htfint = 0;
        htfname = "";
        sbu = 0;
        sbd = 0;
        sbu_t = 0;
        sbd_t = 0;
        slope1 = 0;
        slope2 = 0;
        state = 1;
        regclose1 = 0;
        regclose2 = 0;
        regclose3 = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
        bar1idx     = 0  ;
        bar2idx     = 0  ;
        bar3idx     = 0  ;
        cnt1idx     = 0  ;
        cnt2idx     = 0  ;
        cnt3idx     = 0  ;
    }

    // 带参数的构造函数
    BOS(int i):sbu_lb("sbu_lb" + IntegerToString(i)),sbu_ln("sbu_line" + IntegerToString(i)),sbd_lb("sbd_lb" + IntegerToString(i)),sbd_ln("sbd_line" + IntegerToString(i)) {
        htfint = i;
        htfname = IntegerToString(i);
        sbu = 0;
        sbd = 0;
        sbu_t = 0;
        sbd_t = 0;
        slope1 = 0;
        slope2 = 0;
        state = 1;
        regclose1 = 0;
        regclose2 = 0;
        regclose3 = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
        bar1idx     = 0  ;
        bar2idx     = 0  ;
        bar3idx     = 0  ;
        cnt1idx     = 0  ;
        cnt2idx     = 0  ;
        cnt3idx     = 0  ;
    }
};
struct FVG{
    int namei                 ;
    int kbarbosd              ;
    int kbarbosu              ;
    int cntbosd               ;
    int cntbosu               ;
    double sbd                ;
    double sbu                ;
    datetime sbd_t            ;
    datetime sbu_t            ;
    int kbar[]                ; // index : 0 ~ datasize-2 are targets //kbar[cnt]= k-1 in BOSjudge function
    double kbarclose[]        ;
    double kbarhigh[]         ;
    double kbarlow[]          ;
    double kbaropen[]         ;
    datetime kbartime[]       ;
    FVG(){}
    FVG(int i){
        namei    = i  ;
        sbd      = 0 ;
        sbu      = 0 ;
        sbd_t    = 0 ;
        sbu_t    = 0 ;
        kbarbosd = -1 ;
        kbarbosu = -1 ;
        cntbosd  = -1 ;
        cntbosu  = -1 ;
        ArrayResize(kbar,FVGarraysize,FVGarraysize)     ;
        ArrayResize(kbarclose,FVGarraysize,FVGarraysize);
        ArrayResize(kbarhigh,FVGarraysize,FVGarraysize) ;
        ArrayResize(kbarlow,FVGarraysize,FVGarraysize)  ;
        ArrayResize(kbaropen,FVGarraysize,FVGarraysize) ;
        ArrayResize(kbartime,FVGarraysize,FVGarraysize) ;
        ArrayInitialize(kbar,-1)                        ;
        ArrayInitialize(kbarclose,-1)                   ;
        ArrayInitialize(kbarhigh,-1)                    ;
        ArrayInitialize(kbarlow,-1)                     ;
        ArrayInitialize(kbaropen,-1)                    ;
        ArrayInitialize(kbartime,0)                     ;
    }
    bool FVGkbarBull(int k){
        bool b;
        b = (kbarclose[k] - kbaropen[k] > 0)? true : false ;
        if (kbarclose[k] - kbaropen[k] == 0 && k!=0) b = FVGkbarBull(k-1);
        return b ;
    }
    void Putfvg_chlo(const matrix& Mat, int& cnt , int htfint){ //OHLCT
        int kbaridx   = kbar[cnt]             ;
        int kbaridxm1 = cnt>0? kbar[cnt-1] : 0;
        if(cnt==0){
            kbarclose[cnt]  = Mat[3][kbaridx]      ;
            kbarhigh[cnt]   = Mat[1][kbaridx]      ;
            kbarlow[cnt]    = Mat[2][kbaridx]      ;
            kbaropen[cnt]   = Mat[0][kbaridx]      ;
            kbartime[cnt]   = Mat[4][kbaridx]      ;
        }
        else{
            if(htfint == 1){
                kbarclose[cnt]  = Mat[3][kbaridx]      ;
                kbarhigh[cnt]   = Mat[1][kbaridx]      ;
                kbarlow[cnt]    = Mat[2][kbaridx]      ;
                kbaropen[cnt]   = Mat[0][kbaridx]      ;
                kbartime[cnt]   = Mat[4][kbaridx]      ;
            }
            else{
                int start       = kbaridxm1+1          ;
                int end         = kbaridx              ;
                kbarclose[cnt]  = Mat[3][kbaridx]      ;
                kbartime[cnt]   = Mat[4][kbaridx]      ;
                kbaropen[cnt]   = Mat[0][start]        ;
                kbarhigh[cnt]   = Mat[1][start]        ;
                kbarlow[cnt]    = Mat[2][start]        ;
                while (start < end){
                    kbarhigh[cnt] = kbarhigh[cnt]>Mat[1][start+1]? kbarhigh[cnt] : Mat[1][start+1]     ;
                    kbarlow[cnt]  = kbarlow[cnt]<Mat[2][start+1]?  kbarlow[cnt]  : Mat[2][start+1]     ;
                    ++start ;
                }
            }
        }     
    }
    
    int Getfvgkbarsize(){
        int i=0 ;
        while(kbar[i]!=-1){
            ++i ;
        }
        return i ;
    }
    // int Getfvgeffkbarsize(){
    //     int i=0 ;
    //     while(effkbar[i]!=-1){
    //         ++i ;
    //     }
    //     return i ;
    // }
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
// void Insertalg(double& arr[], int& index[]){
//     for (int i = 1; i < 8; ++i) {
//         double key = arr[i];
//         int keyIndex = index[i];
//         int j = i - 1; // 
//         while (j >= 0 && arr[j] > key) {//從左比到現在的key 有種n階梯比較的概念 //
//             arr[j + 1] = arr[j];
//             index[j + 1] = index[j];
//             j = j - 1;
//         }
//         arr[j + 1] = key; //swap
//         index[j + 1] = keyIndex;
//     }
// }
void BOSInsertalg(matrix& Mat){
    int rsize = Mat.Rows() ;
    for (int i = 1; i < rsize; ++i) {
        double key      = Mat[i][2];
        int htf         = Mat[i][0];
        int keycnt      = Mat[i][1];
        datetime time   = Mat[i][6];
        int j = i - 1; // 
        while (j >= 0 && Mat[j][2] > key) {//從左比到現在的key 有種n階梯比較的概念 //
            Mat[j+1][2] = Mat[j][2];
            Mat[j+1][0] = Mat[j][0];
            Mat[j+1][1] = Mat[j][1];
            Mat[j+1][6] = Mat[j][6];
            j = j - 1;
        }
        Mat[j+1][2] = key; //swap
        Mat[j+1][0] = htf;
        Mat[j+1][1] = keycnt;
        Mat[j+1][6] = time;
    }
}
void BOSJudge(BOS& bosdata, const int size, const RawCandles& rd, const int starti, Helper& helper, FVG& fvg, const int& i){
    int k                         ;                 
    int qidxnow                   ;
    int qidxpt                    ;
    double tempprice              ;
    datetime temptime             ;
    int tempcnt                   ;
    int tempkbar                  ;
    int cnt                       ;
    int tempmin                   ;
    int tempminm1                 ;
    int tempminreg=-1             ;
    datetime testt                ;
    int htfint=i+1                ;
    k   = starti+1                ;
    cnt = 0                       ;
    while(k < size){//last one can not be considered cuz it's not closed
        //我在這裡應該有整整兩個月錯 我20240820 21:29才發現並改正(原本是(rd.mat_rates[4][k])==0? 1439 : ...改成下面那樣) 我的媽鴨= = 解決後全都對了 我還一直以為是barsize取的不夠多 一直調整 想不到這裡才是關鍵，今天只吃午餐(光明陽春麵)而已。 好開心，這代表我的rawdata全部都對了 可以有信心做更深入的分析與輸出。今天是胖小咘剛考完微控制器 跑去看倒吊地鐵，再3個禮拜就飛德國
        if(i<PERIODX4){
            tempmin   = helper.TurnMin(rd.mat_rates[4][k])   ;
            tempminm1 = helper.TurnMin(rd.mat_rates[4][k-1]) ;
        }
        else if(i<PERIODX8){
            tempmin   = helper.TurnMinX2(rd.mat_rates[4][k])   ;
            tempminm1 = helper.TurnMinX2(rd.mat_rates[4][k-1]) ;
        }
        else if(i<PERIODX12){
            tempmin   = helper.TurnMinX3(rd.mat_rates[4][k])   ;
            tempminm1 = helper.TurnMinX3(rd.mat_rates[4][k-1]) ;
        }
        else{
            tempmin   = helper.TurnMinX4(rd.mat_rates[4][k])   ;
            tempminm1 = helper.TurnMinX4(rd.mat_rates[4][k-1]) ;
        }
        //不管哪個週期遇到23:59 都要把這個bar收進來rawdata裡面{
        if(tempminreg==-1) tempminreg=tempminm1-1;
        qidxnow   = tempmin-tempminm1<0? 0 : tempmin;
        qidxpt    = tempminm1-tempminreg<0? 0 : tempminm1;
        tempminreg= qidxpt ;
        if(qidxnow!=0 && ((qidxnow+1)%htfint!=0)){
            ++k ;
            continue;
        }
        if(rd.dataQuo[qidxnow] != rd.dataQuo[qidxpt]){
            if(qidxnow==0 ){
                tempprice         = rd.mat_rates[3][k-1] ;
                temptime          = rd.mat_rates[4][k-1] ;
                if(tempprice == bosdata.regclose3){
                    ++k;
                    continue;
                }
                fvg.kbar[cnt]     = k-1 ;
            }
            else{
                tempprice         = rd.mat_rates[3][k] ;
                temptime          = rd.mat_rates[4][k] ;
                if(tempprice == bosdata.regclose3) {
                    ++k;
                    continue;
                }
                fvg.kbar[cnt]     = k ;
            }
            tempcnt = cnt ;
            tempkbar= fvg.kbar[cnt] ;
            ++cnt;
            //if(bosdata.htfint==4)printf("k= %d \t tempprice@k-1= %.5f \t date@k-1= %s\n htfint= %.1f", k, tempprice,TimeToString(temptime,TIME_DATE|TIME_MINUTES),bosdata.htfint);
            if(bosdata.state == 1){
                bosdata.cnt1idx     = bosdata.cnt2idx  ;
                bosdata.cnt2idx     = bosdata.cnt3idx  ;
                bosdata.cnt3idx     = tempcnt          ;
                bosdata.bar1idx     = bosdata.bar2idx  ;
                bosdata.bar2idx     = bosdata.bar3idx  ;
                bosdata.bar3idx     = tempkbar         ;
                bosdata.regclose1   = bosdata.regclose2;
                bosdata.regclose2   = bosdata.regclose3;
                bosdata.regclose3   = tempprice;
                bosdata.regclose1_t = bosdata.regclose2_t;
                bosdata.regclose2_t = bosdata.regclose3_t;
                bosdata.regclose3_t = temptime;
                testt      = temptime;
                if(cnt<3){
                    ++k;
                    continue;
                }      
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
                    bosdata.barkey1     = bosdata.bar2idx ;
                    bosdata.cntkey1     = bosdata.cnt2idx ;
                }
                //else //Buff_key1維持原樣
                if(bosdata.regclose3>bosdata.sbu){                    
                    bosdata.sbu     = -2;
                    bosdata.sbu_t   = -2;
                    bosdata.sbd     = bosdata.reg1key;
                    bosdata.sbd_t   = bosdata.reg1key_t;
                    fvg.sbu         = -2 ;
                    fvg.sbd         = bosdata.reg1key;
                    fvg.sbu_t       =  0 ;
                    fvg.sbd_t       = bosdata.reg1key_t;
                    fvg.kbarbosd    = bosdata.barkey1;
                    fvg.kbarbosu    = -1 ;
                    fvg.cntbosd     = bosdata.cntkey1;
                    fvg.cntbosu     = -1 ; 
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd     = -1 ;
                    bosdata.sbd_t   = -1 ;
                    bosdata.sbu     = bosdata.reg1key;
                    bosdata.sbu_t   = bosdata.reg1key_t;
                    fvg.sbd         = -1 ;
                    fvg.sbu         = bosdata.reg1key;
                    fvg.sbd_t       =  0 ;
                    fvg.sbu_t       = bosdata.reg1key_t;
                    fvg.kbarbosd    = -1 ;
                    fvg.kbarbosu    = bosdata.barkey1;
                    fvg.cntbosd     = -1 ;
                    fvg.cntbosu     = bosdata.cntkey1;
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
                    fvg.sbu             = bosdata.reg2key;
                    fvg.sbu_t           = bosdata.reg2key_t;
                    fvg.kbarbosu        = bosdata.barkey2;
                    fvg.cntbosu         = bosdata.cntkey2;
                    bosdata.barkey1     = bosdata.barkey2;
                    bosdata.cntkey1     = bosdata.cntkey2;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd         = -1;
                    bosdata.sbd_t       = -1;
                    fvg.sbd             = -1;
                    fvg.sbd_t           =  0;
                    fvg.kbarbosd        = -1;
                    fvg.cntbosd         = -1;
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
                    fvg.sbd             = bosdata.reg2key;
                    fvg.sbd_t           = bosdata.reg2key_t;
                    fvg.kbarbosd        = bosdata.barkey2 ;
                    fvg.cntbosd         = bosdata.cntkey2;
                    bosdata.barkey1     = bosdata.barkey2;
                    bosdata.cntkey1     = bosdata.cntkey2;
                }
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu         = -2;
                    bosdata.sbu_t       = -2;
                    fvg.sbu             = -2;
                    fvg.sbu_t           =  0;
                    fvg.kbarbosu        = -1;
                    fvg.cntbosu         = -1;
                }
                bosdata.state = 1;
            }
            // if(fvg.namei==30){
            //     string str = TimeToString(testt, TIME_DATE | TIME_MINUTES);
            //     printf("fvg%d.sbd= %.5f", fvg.namei, fvg.sbd);
            //     printf("bosdata.state= %d bosdata.slope1= %.1f bosdata.slope2= %.1f bosdata.sbd= %.5f bosdata.sbu= %.5f bosdata.reg1key= %.5f bosdata.reg2key= %.5f bosdata.regclose1= %.5f bosdata.regclose2= %.5f bosdata.regclose3= %.5f time= %s",bosdata.state, bosdata.slope1, bosdata.slope2, bosdata.sbd, bosdata.sbu, bosdata.reg1key, bosdata.reg2key, bosdata.regclose1, bosdata.regclose2, bosdata.regclose3, str);
            // } 
        }
        ++k; 
    }//while end
    //printf("cnt= %d\tk= %d", cnt,k);
}//func end
void BosPut(const FVG& fvg, matrix& M_sbd, matrix& M_sbu, matrix& M_sbdo, matrix& M_sbuo, const int& i){ //P cnt bos H L O T Kbar
    M_sbd[i][0] = fvg.namei ;
    M_sbd[i][1] = fvg.cntbosd ;
    M_sbd[i][2] = fvg.sbd;
    M_sbd[i][6] = fvg.sbd_t;
    //if(fvg.sbd==0) printf("dddd");
    M_sbu[i][0] = fvg.namei ;
    M_sbu[i][1] = fvg.cntbosu ;
    M_sbu[i][2] = fvg.sbu;
    M_sbu[i][6] = fvg.sbu_t;
    //if(fvg.sbu=0) printf("uuuu");
    //-----original data, non sorted-----//

    // int size = fvg.Getfvgkbarsize();
    // if(i<50&&i>29) printf("size= %d", size);
    // for(int j=0; j<size&&i<50&&i>29; ++j){
    //     printf("fvg%d.kbar[%d]= %d",i, j, fvg.kbar[j]);
    // }
    M_sbdo[i][0] = fvg.namei ;
    M_sbdo[i][1] = fvg.cntbosd ;
    M_sbdo[i][2] = fvg.sbd;
    M_sbdo[i][6] = fvg.sbd_t ;
    
    M_sbuo[i][0] = fvg.namei ;
    M_sbuo[i][1] = fvg.cntbosu ;
    M_sbuo[i][2] = fvg.sbu;
    M_sbuo[i][6] = fvg.sbu_t ;
    

    
    //-----original data, non sorted-----//
}
void BosSortAndFill(const FVG& fvg, const FVG& fvgd, const FVG& fvgu, matrix& M_sbd, matrix& M_sbu, matrix& M_sbdo, matrix& M_sbuo, const int& i){ //in this, i is reordered, so we need find the order from less to greater period i is not 1 2 3 4 ... 1440 anymore. fvg[reoreder idx] will be correct. 
    int didx  = M_sbd[i][1]  ;
    int uidx  = M_sbu[i][1]  ;
    int didxo = M_sbdo[i][1] ;
    int uidxo = M_sbuo[i][1] ;
    if(didx>=0){
        M_sbd[i][3] = fvgd.kbarhigh[didx] ;
        M_sbd[i][4] = fvgd.kbarlow [didx] ;
        M_sbd[i][5] = fvgd.kbaropen[didx] ;
        M_sbd[i][7] = fvgd.kbar    [didx] ;
    }
    else{
        M_sbd[i][3] = -1 ;
        M_sbd[i][4] = -1 ;
        M_sbd[i][5] = -1 ;
        M_sbd[i][7] = -1 ;
    }
    if(uidx>=0){
        M_sbu[i][3] = fvgu.kbarhigh[uidx] ;
        M_sbu[i][4] = fvgu.kbarlow [uidx] ;
        M_sbu[i][5] = fvgu.kbaropen[uidx] ;
        M_sbu[i][7] = fvgu.kbar    [uidx] ;
    }
    else{
        M_sbu[i][3] = -1 ;
        M_sbu[i][4] = -1 ;
        M_sbu[i][5] = -1 ;
        M_sbu[i][7] = -1 ;
    }
    if(didxo>=0){
        M_sbdo[i][3] = fvg.kbarhigh[didxo] ;
        M_sbdo[i][4] = fvg.kbarlow [didxo] ;
        M_sbdo[i][5] = fvg.kbaropen[didxo] ;       
        M_sbdo[i][7] = fvg.kbar    [didxo] ;
    }
    else{
        M_sbdo[i][3] = -1 ;
        M_sbdo[i][4] = -1 ;
        M_sbdo[i][5] = -1 ;
        M_sbdo[i][7] = -1 ;
    }
    if(uidxo>=0){
        M_sbdo[i][3] = fvg.kbarhigh[uidxo] ;
        M_sbdo[i][4] = fvg.kbarlow [uidxo] ;
        M_sbdo[i][5] = fvg.kbaropen[uidxo] ;
        M_sbdo[i][7] = fvg.kbar    [uidxo] ;
    } 
    else{
        M_sbuo[i][3] = -1 ;
        M_sbuo[i][4] = -1 ;
        M_sbuo[i][5] = -1 ;
        M_sbuo[i][7] = -1 ;
    }
}

//-----filter-----//
void CheckClosePosPeriod(matrix& Md, matrix& Mu, const matrix& RMd, const matrix& RMu, const int& Pd, const int& Pu){
    int      period;
    double   tempp;
    datetime tempt;
    int      cnt=0 ;

    period   = Pd-1;
    tempp    = RMd[period][2];
    tempt    = RMd[period][6];
    for(int i=0; i<PERIODX4; ++i){
        if((RMd[i][0]>Pd) && (RMd[i][2]>tempp) && (RMd[i][6]>tempt)){
            Md[cnt][0] = RMd[i][0];
            Md[cnt][1] = RMd[i][2];
            Md[cnt][2] = RMd[i][6];
            ++cnt;
        }
        else continue;
    }
    period   = Pu-1;
    tempp    = RMu[period][2];
    tempt    = RMu[period][6];
    for(int i=0; i<PERIODX4; ++i){
        if((RMu[i][0]>Pu) && (RMu[i][2]<tempp) && (RMu[i][6]>tempt)){
            Mu[cnt][0] = RMu[i][0];
            Mu[cnt][1] = RMu[i][2];
            Mu[cnt][2] = RMu[i][6];
            ++cnt;
        }
        else continue;
    }

}

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful