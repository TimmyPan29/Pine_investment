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
    int             cntbosd     ;
    int             cntbosu     ;
    int             slope1      ;
    int             slope2      ;
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
        cntbosu=0;
        cntbosd=0;
        slope1 = 0;
        slope2 = 0;
        state = 1;
        regclose1 = 0;
        regclose2 = 0;
        regclose3 = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
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
        cntbosu=0;
        cntbosd=0;
        slope1 = 0;
        slope2 = 0;
        state = 1;
        regclose1 = 0;
        regclose2 = 0;
        regclose3 = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
        cnt1idx     = 0  ;
        cnt2idx     = 0  ;
        cnt3idx     = 0  ;
    }
};
struct FVG{
    int namei                 ;
    int kbar[]                ; // index : 0 ~ datasize-2 are targets //kbar[cnt]= k-1 in BOSjudge function
    double kbarclose[]        ;
    double kbarhigh[]         ;
    int    kbarhighidx[]      ;
    datetime kbarhight[]      ;
    double kbarlow[]          ;
    int    kbarlowidx[]       ;
    datetime kbarlowt[]       ;
    double kbaropen[]         ;
    datetime kbartime[]       ;
    FVG(){}
    FVG(int i){
        namei    = i  ;
        ArrayResize(kbar,FVGarraysize,FVGarraysize)         ;
        ArrayResize(kbarclose,FVGarraysize,FVGarraysize)    ;
        ArrayResize(kbarhigh,FVGarraysize,FVGarraysize)     ;
        ArrayResize(kbarhighidx, FVGarraysize, FVGarraysize);
        ArrayResize(kbarhight, FVGarraysize, FVGarraysize)  ;
        ArrayResize(kbarlow, FVGarraysize,FVGarraysize)     ;
        ArrayResize(kbarlowidx, FVGarraysize,FVGarraysize)  ;
        ArrayResize(kbarlowt, FVGarraysize,FVGarraysize)    ;
        ArrayResize(kbaropen, FVGarraysize,FVGarraysize)    ;
        ArrayResize(kbartime, FVGarraysize,FVGarraysize)    ;
        ArrayInitialize(kbar,-1)                            ;
        ArrayInitialize(kbarclose,-1)                       ;
        ArrayInitialize(kbarhigh,-1)                        ;
        ArrayInitialize(kbarhighidx,-1)                     ;
        ArrayInitialize(kbarhight,0)                        ;
        ArrayInitialize(kbarlow,-1)                         ;
        ArrayInitialize(kbarlowidx,-1)                      ;
        ArrayInitialize(kbarlowt,0)                         ;
        ArrayInitialize(kbaropen,-1)                        ;
        ArrayInitialize(kbartime,0)                         ;
    }
    bool FVGkbarBull(int k){
        bool b;
        b = (kbarclose[k] - kbaropen[k] > 0)? true : false ;
        if (kbarclose[k] - kbaropen[k] == 0 && k!=0) b = FVGkbarBull(k-1);
        return b ;
    }
    void Putfvg_chlo(const matrix& Mat, int& cnt , int htfint){ //OHLCT
        int kbaridx   = kbar[cnt]                  ;
        int kbaridxm1 = cnt>0? kbar[cnt-1] : 0     ;
        if(cnt==0){
            kbarclose[cnt]  = Mat[3][kbaridx]      ;
            kbarhigh[cnt]   = Mat[1][kbaridx]      ;
            kbarhighidx[cnt]= kbaridx              ;
            kbarhight[cnt]  = Mat[4][kbaridx]      ;
            kbarlow[cnt]    = Mat[2][kbaridx]      ;
            kbarlowidx[cnt] = kbaridx              ;
            kbarlowt[cnt]   = Mat[4][kbaridx]      ;
            kbaropen[cnt]   = Mat[0][kbaridx]      ;
            kbartime[cnt]   = Mat[4][kbaridx]      ;
        }
        else{
            if(htfint == 1){
                kbarclose[cnt]  = Mat[3][kbaridx]      ;
                kbarhigh[cnt]   = Mat[1][kbaridx]      ;
                kbarhighidx[cnt]= kbaridx              ;
                kbarhight[cnt]  = Mat[4][kbaridx]      ;
                kbarlow[cnt]    = Mat[2][kbaridx]      ;
                kbarlowidx[cnt] = kbaridx              ;
                kbarlowt[cnt]   = Mat[4][kbaridx]      ;
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
                kbarhighidx[cnt]= start                ;
                kbarhight[cnt]  = Mat[4][kbaridx]      ;
                kbarlow[cnt]    = Mat[2][start]        ;
                kbarlowidx[cnt] = start                ;
                kbarlowt[cnt]   = Mat[4][kbaridx]      ;
                
                while (start < end){
                    if(kbarhigh[cnt]>Mat[1][start+1]){
                        kbarhigh[cnt]    = kbarhigh[cnt] ;
                        kbarhighidx[cnt] = kbarhighidx[cnt] ;
                        kbarhight[cnt]   = kbarhight[cnt] ;
                    }
                    else{
                        kbarhigh[cnt]    = Mat[1][start+1] ;
                        kbarhighidx[cnt] = start+1 ;
                        kbarhight[cnt]   = Mat[4][start+1] ;
                    }
                    if(kbarlow[cnt]<Mat[2][start+1]){
                        kbarlow[cnt]     = kbarlow[cnt] ;
                        kbarlowidx[cnt]  = kbarlowidx[cnt] ;
                        kbarlowt[cnt]    = kbarlowt[cnt] ;
                    }
                    else{
                        kbarlow[cnt]     = Mat[2][start+1] ;
                        kbarlowidx[cnt]  = start+1 ;
                        kbarlowt[cnt]    = Mat[4][start+1] ;
                    }
                    ++start ;
                }
            }
        }     
    }
    void bos_hlt(const matrix& Mat, matrix& Matd, matrix& Matu, const BOS& bos, const int& i){ //cal the high low argument with bosdata and Rawdata from Mat //P bos H L O BT HT LT OT  , //Mat OHLCT
        Matd[i][0] = namei;
        Matu[i][0] = namei;
        if(bos.sbd>0){
            int didx   = kbar[bos.cntbosd]             ;
            int didxm1 = bos.cntbosd>0? kbar[bos.cntbosd-1] : 0        ;  
            // if(namei==593){
            //     for(int l=0; kbar[l]!=-1; ++l){
            //         string strtest= TimeToString(kbartime[l], TIME_DATE|TIME_MINUTES);
            //         printf("namei%d %d, kbar=%d, sbd%.5f, bosd=%.5f, bosu=%.5f kbartime%s, ", namei, l, kbar[l], kbarclose[l], bos.sbd, bos.sbu, strtest);
            //     }
            // }
            if(namei==1){
                Matd[i][1] = Mat[3][didx];
                Matd[i][4] = Mat[0][didx];
                Matd[i][5] = Mat[4][didx];
                Matd[i][8] = Mat[4][didx];
                Matd[i][6] = Mat[4][didx];
                Matd[i][7] = Mat[4][didx];
                Matd[i][2] = Mat[1][didx];
                Matd[i][3] = Mat[2][didx];
            }
            else{
                int start       = didxm1+1          ;
                int end         = didx              ;
                int temph       = didxm1+1          ;
                int templ       = didxm1+1          ;
                Matd[i][1] = Mat[3][didx];
                Matd[i][4] = Mat[0][start];
                Matd[i][5] = Mat[4][didx];
                Matd[i][8] = Mat[4][start];
                Matd[i][6] = Mat[4][start];
                Matd[i][7] = Mat[4][start];
                Matd[i][2] = Mat[1][didx];
                Matd[i][3] = Mat[2][didx];
                while(start<end){
                    Matd[i][2] = Matd[i][2]>Mat[1][start+1]? Matd[i][2] : Mat[1][start+1];
                    temph      = Matd[i][2]>Mat[1][start+1]? temph      : start+1;
                    Matd[i][3] = Matd[i][3]<Mat[2][start+1]? Matd[i][3] : Mat[2][start+1];
                    templ      = Matd[i][3]<Mat[2][start+1]? templ      : start+1;
                    ++start;
                }
                Matd[i][6] = Mat[4][temph];
                Matd[i][7] = Mat[4][templ];
            }
        }
        else{ //P bos H L O BT HT LT OT
            Matd[i][1] = -1;
            Matd[i][4] = 0;
            Matd[i][5] = 0;
            Matd[i][8] = 0;
            Matd[i][6] = 0;
            Matd[i][7] = 0;
            Matd[i][2] = 0;
            Matd[i][3] = 0;
        }
        if(bos.sbu>0){
            int uidx   = kbar[bos.cntbosu]             ;
            int uidxm1 = bos.cntbosu>0? kbar[bos.cntbosu-1] : 0        ;
            if(namei==1){
                Matu[i][1] = Mat[3][uidx];
                Matu[i][4] = Mat[0][uidx];
                Matu[i][5] = Mat[4][uidx];
                Matu[i][8] = Mat[4][uidx];
                Matu[i][6] = Mat[4][uidx];
                Matu[i][7] = Mat[4][uidx];
                Matu[i][2] = Mat[1][uidx];
                Matu[i][3] = Mat[2][uidx];
            }
            else{
                int start       = uidxm1+1          ;
                int end         = uidx              ;
                int temph       = uidxm1+1          ;
                int templ       = uidxm1+1          ;
                Matu[i][1] = Mat[3][uidx];
                Matu[i][4] = Mat[0][start];
                Matu[i][5] = Mat[4][uidx];
                Matu[i][8] = Mat[4][start];
                Matu[i][6] = Mat[4][start];
                Matu[i][7] = Mat[4][start];
                Matu[i][2] = Mat[1][uidx];
                Matu[i][3] = Mat[2][uidx];
                while(start<end){
                    Matu[i][2] = Matu[i][2]>Mat[1][start+1]? Matu[i][2] : Mat[1][start+1];
                    temph      = Matu[i][2]>Mat[1][start+1]? temph      : start+1;
                    Matu[i][3] = Matu[i][3]<Mat[2][start+1]? Matu[i][3] : Mat[2][start+1];
                    templ      = Matu[i][3]<Mat[2][start+1]? templ      : start+1;
                    ++start;
                }
                Matu[i][6] = Mat[4][temph];
                Matu[i][7] = Mat[4][templ];
            }
        }
        else{ //P bos H L O BT HT LT OT
            Matu[i][1] = -2;
            Matu[i][4] = 0;
            Matu[i][5] = 0;
            Matu[i][8] = 0;
            Matu[i][6] = 0;
            Matu[i][7] = 0;
            Matu[i][2] = 0;
            Matu[i][3] = 0;
        }
    }
    int Getfvgkbarsize(){
        int i=0 ;
        while(kbar[i]!=-1){
            ++i ;
        }
        return i ;
    }
};

//-----------------------------------***bos.h global fuction***------------------------------------//
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
void BOSInsertalg(matrix& Mattobesort){ //P bos H L O T T T T
    int rsize = Mattobesort.Rows() ;
    for (int i = 1; i < rsize; ++i) {
        double key         = Mattobesort[i][1];
        int htf            = Mattobesort[i][0];
        double   H         = Mattobesort[i][2];
        double   L         = Mattobesort[i][3];
        double   O         = Mattobesort[i][4];
        datetime Btime     = Mattobesort[i][5];
        datetime Htime     = Mattobesort[i][6];
        datetime Ltime     = Mattobesort[i][7];
        datetime Otime     = Mattobesort[i][8];
        int j = i - 1; // 
        while (j >= 0 && Mattobesort[j][2] > key) {//從左比到現在的key 有種n階梯比較的概念 //
            Mattobesort[j+1][1] = Mattobesort[j][1];
            Mattobesort[j+1][0] = Mattobesort[j][0];
            Mattobesort[j+1][2] = Mattobesort[j][2];
            Mattobesort[j+1][3] = Mattobesort[j][3];
            Mattobesort[j+1][4] = Mattobesort[j][4];
            Mattobesort[j+1][5] = Mattobesort[j][5];
            Mattobesort[j+1][6] = Mattobesort[j][6];
            Mattobesort[j+1][7] = Mattobesort[j][7];
            Mattobesort[j+1][8] = Mattobesort[j][8];
            j = j - 1;
        }
        Mattobesort[j+1][1] = key; //swap
        Mattobesort[j+1][0] = htf;
        Mattobesort[j+1][2] = H;
        Mattobesort[j+1][3] = L;
        Mattobesort[j+1][4] = O;
        Mattobesort[j+1][5] = Btime;
        Mattobesort[j+1][6] = Htime;
        Mattobesort[j+1][7] = Ltime;
        Mattobesort[j+1][8] = Otime;
    }
}
void BOSJudge(BOS& bosdata, const int size, const RawCandles& rd, const int starti, Helper& helper, FVG& fvg, const int& i){
    int k                         ;                 
    int qidxnow                   ;
    int qidxpt                    ;
    double tempprice              ;
    datetime temptime             ;
    int tempcnt                   ;
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
            if(qidxnow==0){
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
            ++cnt;
            //if(bosdata.htfint==4)printf("k= %d \t tempprice@k-1= %.5f \t date@k-1= %s\n htfint= %.1f", k, tempprice,TimeToString(temptime,TIME_DATE|TIME_MINUTES),bosdata.htfint);
            if(bosdata.state == 1){
                bosdata.cnt1idx     = bosdata.cnt2idx  ;
                bosdata.cnt2idx     = bosdata.cnt3idx  ;
                bosdata.cnt3idx     = tempcnt          ;
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
                    bosdata.cntkey1     = bosdata.cnt2idx ;
                }
                //else //Buff_key1維持原樣
                if(bosdata.regclose3>bosdata.sbu){                    
                    bosdata.sbu     = -2;
                    bosdata.sbu_t   = -2;
                    bosdata.sbd     = bosdata.reg1key;
                    bosdata.sbd_t   = bosdata.reg1key_t;
                    bosdata.cntbosd = bosdata.cntkey1;
                    bosdata.cntbosu = -1 ; 
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd     = -1 ;
                    bosdata.sbd_t   = -1 ;
                    bosdata.sbu     = bosdata.reg1key;
                    bosdata.sbu_t   = bosdata.reg1key_t;
                    bosdata.cntbosd = -1 ;
                    bosdata.cntbosu = bosdata.cntkey1;
                }
                bosdata.state = 1;
            }
            if(bosdata.state == 3){//no sky
                if(bosdata.slope1 != bosdata.slope2){ // build sky
                    bosdata.reg2key     = bosdata.regclose2;
                    bosdata.reg2key_t   = bosdata.regclose2_t;
                    bosdata.cntkey2     = bosdata.cnt2idx ;
                    bosdata.sbu         = bosdata.reg2key;
                    bosdata.sbu_t       = bosdata.reg2key_t;
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                    bosdata.cntbosu     = bosdata.cntkey2;
                    bosdata.cntkey1     = bosdata.cntkey2;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd         = -1;
                    bosdata.sbd_t       = -1;
                    bosdata.cntbosd     = -1;
                }
                bosdata.state = 1;
            }
            if(bosdata.state == 4){
                if(bosdata.slope1 != bosdata.slope2){
                    bosdata.reg2key     = bosdata.regclose2;
                    bosdata.reg2key_t   = bosdata.regclose2_t;
                    bosdata.cntkey2     = bosdata.cnt2idx ;
                    bosdata.sbd         = bosdata.reg2key;
                    bosdata.sbd_t       = bosdata.reg2key_t;
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                    bosdata.cntbosd     = bosdata.cntkey2;
                    bosdata.cntkey1     = bosdata.cntkey2;
                }
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu         = -2;
                    bosdata.sbu_t       = -2;
                    bosdata.cntbosu     = -1;
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

//P bos H L O T T T T

void Boscopy(const matrix& M_sbd, const matrix& M_sbu, matrix& M_sbdo, matrix& M_sbuo, const int& i){ //in this, i is reordered, so we need find the order from less to greater period i is not 1 2 3 4 ... 1440 anymore. fvg[reoreder idx] will be correct. 
    for(int j=0; j<9; ++j){
        M_sbdo[i][j] = M_sbd[i][j] ;
    }
    for(int j=0; j<9; ++j){
        M_sbuo[i][j] = M_sbu[i][j] ;
    }
}

//-----filter-----//
//RMd: P bos H L O BT HT LT OT , Rmd is M_sbdordered
//Md:  P bos H L BT ,  Md is M_sbdCP
void CheckClosePosPeriod(matrix& Md, matrix& Mu, const matrix& RMd, const matrix& RMu, const int& Pd, const int& Pu){//R is raw
    int      period;
    double   tempp;
    datetime tempt;
    int      cnt=0 ;

    period   = Pd-1;
    tempp    = RMd[period][1];
    tempt    = RMd[period][5];
    for(int i=0; i<PERIODX4; ++i){
        if((RMd[i][0]>Pd) && (RMd[i][1]>tempp) && (RMd[i][5]>tempt)){
            Md[cnt][0] = RMd[i][0];
            Md[cnt][1] = RMd[i][1];
            Md[cnt][2] = RMd[i][2];
            Md[cnt][3] = RMd[i][3];
            Md[cnt][4] = RMd[i][5];
            ++cnt;
        }
        else continue;
    }
    period   = Pu-1;
    tempp    = RMu[period][1];
    tempt    = RMu[period][5];
    for(int i=0; i<PERIODX4; ++i){
        if((RMu[i][0]>Pu) && (RMu[i][1]<tempp) && (RMu[i][5]>tempt)){
            Mu[cnt][0] = RMu[i][0];
            Mu[cnt][1] = RMu[i][2];
            Mu[cnt][2] = RMu[i][2];
            Mu[cnt][3] = RMu[i][3];
            Mu[cnt][4] = RMu[i][5];
            ++cnt;
        }
        else continue;
    }

}
void MatBosinit(matrix& mat, const int& rows, const int& columes){
    for(int i=0; i<rows; ++i){
        for(int j=0; j<columes; ++j){
            mat[i][j]=0 ;
        }
    }
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful