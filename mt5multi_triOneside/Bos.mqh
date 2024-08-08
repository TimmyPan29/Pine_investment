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
struct FVG{
    int namei                 ;
    int Property[]            ; //property= 2 green , =1 red, =0 no existence
    int kbar[]                ; // index : 0 ~ datasize-2 are targets
    double kbarclose[]        ;
    double kbarhigh[]         ;
    double kbarlow[]          ;
    double kbaropen[]         ;
    double LTprice[]          ;
    double RBprice[]          ;
    int effkbar[];
    int effkbarend[];
    FVG(){}
    FVG(int i){
        namei = i ;
        ArrayResize(kbar,FVGarraysize,FVGarraysize)     ;
        ArrayResize(kbarclose,FVGarraysize,FVGarraysize);
        ArrayResize(kbarhigh,FVGarraysize,FVGarraysize) ;
        ArrayResize(kbarlow,FVGarraysize,FVGarraysize)  ;
        ArrayResize(kbaropen,FVGarraysize,FVGarraysize) ;
        ArrayResize(Property,300,300)   ;
        ArrayResize(LTprice,300,300)    ;
        ArrayResize(RBprice,300,300)    ;
        ArrayResize(effkbar,300,300)    ;
        ArrayResize(effkbarend,300,300) ;
        ArrayInitialize(kbar,-1)        ;
        ArrayInitialize(kbarclose,-1)   ;
        ArrayInitialize(kbarhigh,-1)    ;
        ArrayInitialize(kbarlow,-1)     ;
        ArrayInitialize(kbaropen,-1)    ;
        ArrayInitialize(Property,-1)    ;
        ArrayInitialize(LTprice,-1)     ;
        ArrayInitialize(RBprice,-1)     ;
        ArrayInitialize(effkbar,-1)     ;
    }
    
    bool FVGkbarBull(int k){
        bool b;
        b = (kbarclose[k] - kbaropen[k] > 0)? true : false ;
        if (kbarclose[k] - kbaropen[k] == 0 && k!=0) b = FVGkbarBull(k-1);
        return b ;
    }
    void Putfvg_chlo(const RawCandles& rc, int& cnt , int htfint){ 
        if(cnt==0){
            kbarclose[cnt]  = rc.rawprices[kbar[cnt]];
            kbarhigh[cnt]   = rc.rawhigh[kbar[cnt]] ;
            kbarlow[cnt]    = rc.rawlow[kbar[cnt]]  ;
            kbaropen[cnt]   = rc.rawopen[kbar[cnt]] ;
        }
        else{
            if(htfint == 1){
                kbarclose[cnt]  = rc.rawprices[kbar[cnt]];
                kbarhigh[cnt]   = rc.rawhigh[kbar[cnt]] ;
                kbarlow[cnt]    = rc.rawlow[kbar[cnt]]  ;
                kbaropen[cnt]   = rc.rawopen[kbar[cnt]] ;
            }
            else{
                int start       = kbar[cnt-1]+1   ;
                int end         = kbar[cnt]  ;
                kbarclose[cnt]  = rc.rawprices[kbar[cnt]] ;
                kbaropen[cnt]   = rc.rawopen[start] ;
                kbarhigh[cnt]   = rc.rawhigh[start] ;
                kbarlow[cnt]    = rc.rawlow[start] ;
                while (start < end){
                    kbarhigh[cnt] = kbarhigh[cnt]>rc.rawhigh[start+1]? kbarhigh[cnt] : rc.rawhigh[start+1] ;
                    kbarlow[cnt]  = kbarlow[cnt]<rc.rawlow[start+1]? kbarlow[cnt] : rc.rawlow[start+1] ;
                    ++start ;
                }
            }
        }     
    }
    int FVGupdown(int idx, int kbarsize){
        if (idx > kbarsize - 3) return -1 ;
        if(FVGkbarBull(idx+1)){
            if(kbarlow[idx+2] - kbarhigh[idx] > 0){
                return 2 ;
            } 
            else{
                return 0 ;
            } 
        }
        else{
            if(kbarhigh[idx+2] - kbarlow[idx] < 0){
                return 1 ;
            } 
            else{
                return 0 ;
            }
        }
    }
    double Findmaxcloseaftk(int idx, int kbarsize, int& kbarend){//find max in bull candle //idx+3 cuz +0~+2is box position
        int i = idx;
        double tempclose;
        double temp ;
        if (i+3==kbarsize) temp = kbarclose[kbarsize-1]; 
        else temp = kbarclose[i+3]; 
        while(i+3<kbarsize){
            if(FVGkbarBull(i+3)){
                tempclose = kbarclose[i+3];
                if(tempclose>temp){
                    temp = tempclose;
                    kbarend = i+3 ;
                }
            }
            ++i ;
        }
        //printf("i= %d, kbarsize= %d", i, kbarsize);
        return temp ;
    }
    double Findmincloseaftk(int idx, int kbarsize, int& kbarend){//find min in bear candle //idx+3 cuz +0~+2is box position
        int i = idx;
        double tempclose;
        double temp ;
        if (i+3==kbarsize) temp = kbarclose[kbarsize-1]; 
        else temp = kbarclose[i+3]; 
        while(i+3<kbarsize){
            if(!FVGkbarBull(i+3)){
                tempclose = kbarclose[i+3];
                if(tempclose<temp){
                    temp = tempclose;
                    kbarend = i+3 ;
                } 
            }
            ++i ;
        }
        return temp ;
    }
    int Getfvgkbarsize(){
        int i=0 ;
        while(kbar[i]!=-1){
            ++i ;
        }
        return i ;
    }
    int Getfvgeffkbarsize(){
        int i=0 ;
        while(effkbar[i]!=-1){
            ++i ;
        }
        return i ;
    }

    void Putefffvg(){
        int kbarsize = Getfvgkbarsize() ;
        double maxpt;
        double minpt;
        double boxLT;
        double boxRB;
        int kbarmaxend ;
        int kbarminend ;
        int    cnt =0;
        for(int putidx=0; putidx<kbarsize-2; ++putidx){
            kbarmaxend = 0;
            kbarminend = 0;
            maxpt = Findmaxcloseaftk(putidx, kbarsize, kbarmaxend);
            minpt = Findmincloseaftk(putidx, kbarsize, kbarminend);
            if(FVGupdown(putidx, kbarsize) == 2){ //green
                boxLT = kbarhigh[putidx];
                boxRB = kbarlow[putidx+2] ;
                if (minpt>boxRB){ //fvg exist
                    Property[cnt]    = 2 ;
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = boxRB ;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[putidx+2];
                    ++cnt;
                }
                else if (minpt<=boxLT){//fvg not exist
                    
                } 
                else{ //fvg exist but is shorten
                    Property[cnt]    = 4 ;
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = minpt ;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[kbarminend];

                    ++cnt;
                }
            }
            else if(FVGupdown(putidx, kbarsize) == 1){ //red
                boxLT = kbarlow[putidx];
                boxRB = kbarhigh[putidx+2] ;
                if (maxpt<boxRB){ //fvg exist
                    Property[cnt]    = 1 ;
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = boxRB ;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[putidx+2];
                    ++cnt;
                }
                else if (maxpt>=boxLT){//fvg not exist
                    
                } 
                else{ //fvg exist but is shorten
                    Property[cnt]    = 3 ;
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = maxpt ;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[kbarmaxend];
                    ++cnt;
                }
            }

            else{
                if(FVGupdown(putidx, kbarsize) == -1) printf("overpass the size");
            }
        }//for end
        //printf("cnt= %d, namei= %d", cnt, namei);
    }//fun end
};
struct Triset{
    uint    comparecode[]   ;
    uint    comparecode0F[] ;
    bool    u_inside[]      ;
    bool    d_inside[]      ;
    int     wide2itv_d      ;
    int     wide2itv_u      ;
    int     wide2itv0X      ;
    int     wide2itvXF      ;
    int     fvgtype0F[]     ;
    Triset():wide2itv_d(-1),wide2itv_u(-1),wide2itv0X(-1),wide2itvXF(-1){}
    double maxbos(const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4);
    double minbos(const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4);
    double TriItvCompare_d (const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& tempd, const int& j);
    double TriItvCompare_u (const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& tempu, const int& j);
    double TriItvCompare0X (FVG& fvg, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& delta0X, const int& j, const int& count3);
    double TriItvCompareXF (FVG& fvg, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& deltaXF, const int& j, const int& count3);
    void   TriFVGcheck0F   (FVG& fvg, const double& u, const double& d, const int& j);
};
double Triset::maxbos(const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4){
    double temp ;
    temp = (bos2.sbd>bos3.sbd)? bos2.sbd : bos3.sbd ;
    temp = (temp>bos4.sbd)? temp : bos4.sbd ;
    if(temp<0) temp = bos1.sbd ;
    return temp ;
}
double Triset::minbos(const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4){
    double temp ;
    temp = (bos2.sbu<bos3.sbu)? bos2.sbu : bos3.sbu ;
    if(bos2.sbu== -2) temp = bos3.sbu ;
    temp = (temp<bos4.sbu)? temp : bos4.sbu ;
    if(bos3.sbu== -2) temp = bos4.sbu ;
    if(temp<0) temp = bos1.sbu ;
    return temp ;
}
double Triset::TriItvCompare_d (const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& tempd, const int& j){
    double temp = tempd ;
    if(d_inside[j]!=0){
        if(wide2itv_d==-1){
            wide2itv_d = j ;
            temp = maxbos(bos1,bos2,bos3,bos4);
        }
        else{
            if(maxbos(bos1,bos2,bos3,bos4)<=temp){
                wide2itv_d = j ;
                temp = maxbos(bos1,bos2,bos3,bos4);
            }
        }
        return temp ;
    }
    else return tempd ;
}
double Triset::TriItvCompare_u (const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& tempu, const int& j){
    double temp = tempu ;
    if(u_inside[j]!=0){
        if(wide2itv_u==-1){
            wide2itv_u = j ;
            temp = minbos(bos1,bos2,bos3,bos4);
        }
        else{
            if(minbos(bos1,bos2,bos3,bos4)>=temp){
                wide2itv_u = j ;
                temp = minbos(bos1,bos2,bos3,bos4);
            }
        }
        return temp ;
    }
    else return tempu ;
}
double Triset::TriItvCompare0X (FVG& fvg, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& delta0X, const int& j, const int& count3){//7 belong case 0xXXX0XXXX, 11 belong 0xXXXXFXXX
    double deltatemp = delta0X ;
    double minsbu ; //for TriFVGcheck0F
    double tempmin; //for TriFVGcheck0F
    if(count3==7){
        delta0X     = MathMax(bos2.sbd, bos3.sbd);
        delta0X     = MathMax(delta0X, bos4.sbd);
        minsbu      = MathMin(bos1.sbu, bos2.sbu);
        tempmin     = MathMin(bos3.sbu, bos4.sbu);
        minsbu      = MathMin(minsbu, tempmin);
        TriFVGcheck0F(fvg, bos1.sbu, delta0X, j); //fix bos1.sbu from minsbu
        //delta0X = temp1 - temp2 ;//其實不用差來算也可以 把0當成基準來比較就好
        if(wide2itv0X==-1){
            wide2itv0X = j ;
            deltatemp = delta0X ;
        }
        else{
            if(deltatemp >= delta0X){
                wide2itv0X = j ;
                deltatemp = delta0X ;
            }
        }
        return deltatemp ;
    }
    else return delta0X ;
}
double Triset::TriItvCompareXF (FVG& fvg, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& deltaXF, const int& j, const int& count3){//7 belong case 0xXXX0XXXX, 11 belong 0xXXXXFXXX
    double deltatemp = deltaXF ;
    double maxsbd ; //for TriFVGcheck0F
    double tempmax; //for TriFVGcheck0F
    if(count3==11){
        deltaXF     = MathMin(bos2.sbu, bos3.sbu);
        deltaXF     = MathMin(deltaXF , bos4.sbu);
        maxsbd      = MathMax(bos1.sbd, bos2.sbd);
        tempmax     = MathMax(bos3.sbd, bos4.sbd);
        maxsbd      = MathMax(maxsbd, tempmax); 
        TriFVGcheck0F(fvg, deltaXF, bos1.sbd, j); //fix bos1.sbd from maxsbd
        if(wide2itvXF==-1){
            wide2itvXF = j ;
            deltatemp = deltaXF ;
        }
        else{
            if(deltatemp <= deltaXF){
                wide2itvXF = j ;
                deltatemp = deltaXF ;
            }
        }
        return deltatemp ;
    }
    else return deltaXF ;
}
void Triset::TriFVGcheck0F(FVG& fvg, const double& u, const double& d, const int& j){
    int effkbarsize = fvg.Getfvgeffkbarsize();
    bool flag ;
    fvgtype0F[j] = 0 ;
    int  reg     = fvgtype0F[j]  ;
    for (int i=0; i<effkbarsize; ++i){
        flag = ((fvg.LTprice[i]<u && fvg.LTprice[i]>d) || (fvg.RBprice[i]<u && fvg.RBprice[i]>d))? true : false ;
        if(fvgtype0F[j]!=0xF){
            if(flag){
                reg          = fvgtype0F[j] ;
                fvgtype0F[j] = (fvg.Property[i]%2==0)? 2 : 1 ;
            }
            if(reg+fvgtype0F[j]==3){
                fvgtype0F[j] = 0xF ;
            }
        }
        else break ;
    } 
}
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
void Boolcheck(const double& arr[], int& signsbd, int& signsbu){
    if(arr[3] == arr[2]) signsbd = 2 ;
    else if(arr[3] == arr[1]) signsbd = 3 ;
    else if(arr[3] == arr[0]) signsbd = 4 ;
    else if((arr[3] == arr[2]) && (arr[3] == arr[1])) signsbd = 5 ; 
    else if((arr[3] == arr[2]) && (arr[3] == arr[0])) signsbd = 6 ; 
    else if((arr[3] == arr[1]) && (arr[3] == arr[0])) signsbd = 7 ;
    else if((arr[3] == arr[2]) && (arr[3] == arr[1]) && (arr[3] == arr[0])) signsbd = 9 ;  
    else signsbd = 0 ;
    if(arr[4] == arr[5]) signsbu = 2 ;
    else if(arr[4] == arr[6]) signsbu = 3 ;
    else if(arr[4] == arr[7]) signsbu = 4 ;
    else if((arr[4] == arr[5]) && (arr[4] == arr[6])) signsbu = 5 ; 
    else if((arr[4] == arr[5]) && (arr[4] == arr[7])) signsbu = 6 ; 
    else if((arr[4] == arr[6]) && (arr[4] == arr[7])) signsbu = 7 ;
    else if((arr[4] == arr[5]) && (arr[4] == arr[6]) && (arr[4] == arr[7])) signsbu = 9 ;  
    else signsbu = 0 ;
}

void BOSJudge(BOS& bosdata, const int size, RawCandles& rd, const int starti, Helper& helper, FVG& fvgarr, const int& i){
    int k                         ;                     
    int qidxnow                   ;
    int qidxpt                    ;
    double tempprice              ;
    datetime temptime             ;
    int cnt                       ;
    k   = starti+1                ;
    cnt = 0                       ;
    while(k < size){//last one can not be considered cuz it's not closed
        if(i<PERIODX4){
            qidxnow = helper.TurnMin(rd.datadate[k])==0? 1439 : helper.TurnMin(rd.datadate[k])-1;
            qidxpt  = helper.TurnMin(rd.datadate[k-1])==0? 1439 : helper.TurnMin(rd.datadate[k-1])-1 ;   
        }
        else if(i<PERIODX8){
            qidxnow = helper.TurnMinX2(rd.datadate[k])==0? 2879 : helper.TurnMinX2(rd.datadate[k])-1;
            qidxpt  = helper.TurnMinX2(rd.datadate[k-1])==0? 2879 : helper.TurnMinX2(rd.datadate[k-1])-1 ;  
        }
        else if(i<PERIODX12){
            qidxnow = helper.TurnMinX3(rd.datadate[k])==0? 4319 : helper.TurnMinX3(rd.datadate[k])-1;
            qidxpt  = helper.TurnMinX3(rd.datadate[k-1])==0? 4319 : helper.TurnMinX3(rd.datadate[k-1])-1 ;  
        }
        else{
            qidxnow = helper.TurnMinX4(rd.datadate[k])==0? 5759 : helper.TurnMinX4(rd.datadate[k])-1;
            qidxpt  = helper.TurnMinX4(rd.datadate[k-1])==0? 5759 : helper.TurnMinX4(rd.datadate[k-1])-1 ;  
        }

        if(rd.dataQuo[qidxnow] != rd.dataQuo[qidxpt]){
            //Print("qidxnow= ", qidxnow, "qidxpt", qidxpt, "bosdata.htfint", bosdata.htfint);
            tempprice         = rd.rawprices[k-1] ;
            temptime          = rd.datadate[k-1]  ;
            fvgarr.kbar[cnt]  = k-1 ;
              //as period 2 for a example, we need to take one forward bar consider for calculating high and low price.
            // int i =past k ; i<nowk ; ++i //plz use circular buff
            ++cnt;
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
    //printf("cnt= %d\tk= %d", cnt,k);
}//func end

Triset TriCode(FVG& fvg, Triset& ts, BOS& bos1, BOS& bos2, BOS& bos3, BOS& bos4, int j, double& tempd, double& tempu, double& delta0X, double& deltaXF){
    //-1 == no sbd, -2 == no sbu
    uint code       = 0 ;
    int count1      = 0 ;
    int count2      = 0 ;
    int count3      = 0 ;
    double arr[8]   = {bos4.sbd, bos3.sbd, bos2.sbd, bos1.sbd, bos1.sbu, bos2.sbu, bos3.sbu, bos4.sbu};
    int    index[8] ={28, 24, 20, 16, 12, 8, 4, 0}; //according to the index[i], I can know that which bos is represnented. And. i is comparison result.
    int    signsbd ;
    int    signsbu ;
    Boolcheck(arr, signsbd, signsbu);
    Insertalg(arr, index);
    for (int i = 0; i < 8; ++i) {
        code = (arr[i] == -1) ? (code & (LeftRotate(__7f10fMASK, index[i]))) : (arr[i] == -2) ? (code | (LeftRotate(__701ffMASK, index[i]))) :(code | ((i + 1) << index[i]));
    }
//code non filtered
    if((code & __LEVEL1SBDMASK)<<4  > (code & __LEVEL2SBDMASK)) ++count1 ;
    if((code & __LEVEL1SBDMASK)<<8  > (code & __LEVEL3SBDMASK)) ++count1 ;
    if((code & __LEVEL1SBDMASK)<<12 > (code & __LEVEL4SBDMASK)) ++count1 ;
    if((code & __LEVEL1SBUMASK)>>4  < (code & __LEVEL2SBUMASK)) ++count2 ;
    if((code & __LEVEL1SBUMASK)>>8  < (code & __LEVEL3SBUMASK)) ++count2 ;
    if((code & __LEVEL1SBUMASK)>>12 < (code & __LEVEL4SBUMASK)) ++count2 ;
   
//code filtered
    if(( code & __LEVEL2SBDMASK  ) == 0) ++count3 ;
    if(( code & __LEVEL3SBDMASK  ) == 0) ++count3 ;
    if(( code & __LEVEL4SBDMASK  ) == 0) ++count3 ;
    if(( code & __LEVEL1SBDMASK  ) == 0) ++count3 ;
    if(( code & __LEVEL2SBUMASK  ) == (__LEVEL2SBUMASK)) count3=count3+5 ;
    if(( code & __LEVEL3SBUMASK  ) == (__LEVEL3SBUMASK)) count3=count3+5 ;
    if(( code & __LEVEL4SBUMASK  ) == (__LEVEL4SBUMASK)) count3=count3+5 ;
    if(( code & __LEVEL1SBUMASK  ) == (__LEVEL1SBUMASK)) count3=count3+5 ;

    if(count3==4 || count3==20) ts.comparecode0F[j] = code; //4 belong case 0x0000XXXX, 20 belong 0xXXXXFFFF
    else ts.comparecode0F[j] = 0;
    ts.comparecode[j]   = code ;
    ts.d_inside[j]      = (count1==3 && signsbd==0)? true : false ;
    ts.u_inside[j]      = (count2==3 && signsbu==0)? true : false ;

    tempd   = ts.TriItvCompare_d(bos1, bos2, bos3, bos4, tempd, j);
    tempu   = ts.TriItvCompare_u(bos1, bos2, bos3, bos4, tempu, j);
    delta0X = ts.TriItvCompare0X(fvg, bos1, bos2, bos3, bos4, delta0X, j, count3);
    deltaXF = ts.TriItvCompareXF(fvg, bos1, bos2, bos3, bos4, deltaXF, j, count3);

    //Print("bos1.htfint: ", bos1.htfint);
    return ts;
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful