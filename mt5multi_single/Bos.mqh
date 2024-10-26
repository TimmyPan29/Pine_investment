#ifndef __BOS_MQH__
#define __BOS_MQH__
#include "Plotpack.mqh"
#include "GETDATA.mqh"
#include "Helper.mqh"
#define FVGarraysize 3000
#define MAXSBU       9999999
struct BOS{
    double          htfint      ;//=i
    string          htfname     ;//IntegerToString(i)
    double          sbu         ;
    double          sbd         ;
    datetime        sbu_t       ;
    datetime        sbd_t       ;
    datetime        sbubrk_t    ;
    datetime        sbdbrk_t    ;
    double          i2bsbu      ;
    datetime        i2bsbu_t    ;
    double          i2bsbd      ;
    datetime        i2bsbd_t    ;
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

    BOS():sbu_lb(""),sbu_ln(""),sbd_lb(""),sbd_ln(""){
        htfint      = 0;
        htfname     = "";
        sbu         = 0.0;
        sbd         = 0.0;
        sbu_t       = 0;
        sbd_t       = 0;
        i2bsbu      = 0;
        i2bsbu_t    = 0;
        i2bsbd      = 0;
        i2bsbd_t    = 0;
        slope1      = 0.0;
        slope2      = 0.0;
        state       = 1;
        regclose1   = 0.0;
        regclose2   = 0.0;
        regclose3   = 0.0;
        regclose1_t = 0.0;
        regclose2_t = 0.0;
        regclose3_t = 0.0;
    }

    // 带参数的构造函数
    BOS(int i):sbu_lb("sbu_lb" + IntegerToString(i)),sbu_ln("sbu_line" + IntegerToString(i)),sbd_lb("sbd_lb" + IntegerToString(i)),sbd_ln("sbd_line" + IntegerToString(i)) {
        htfint      = i;
        htfname     = IntegerToString(i);
        sbu         = 0;
        sbd         = 0;
        sbu_t       = 0;
        sbu_t       = 0;
        i2bsbu      = 0;
        i2bsbu_t    = 0;
        i2bsbd      = 0;
        i2bsbd_t    = 0;
        slope1      = 0;
        slope2      = 0;
        state       = 1;
        regclose1   = 0;
        regclose2   = 0;
        regclose3   = 0;
        regclose1_t = 0;
        regclose2_t = 0;
        regclose3_t = 0;
    }
};
struct FVG{
    int namei                 ;
    int Property[]            ; //property= 2 green , =1 red, =0 no existence
    int leadblockfg[]         ; // if true, lead from certain bar blocked the fvg no matter which is red or green fvg. 0 is not blocked, 1 is partly blocked, and  2 is fully blocked
    double leadblockbound[]   ; // if leadbolckfg is true, I must know exactly the value of bound blocked .
    int kbar[]                ; // index : 0 ~ datasize-2 are targets
    double kbarclose[]        ;
    double kbarhigh[]         ;
    double kbarlow[]          ;
    double kbaropen[]         ;
    datetime kbartime[]       ;
    double LTprice[]          ;
    double RBprice[]          ;
    datetime Boxtime[]         ;
    int effkbar[]             ;
    int effkbarend[]          ;
    int fvgsyndrone[]    ;
    FVG(){}
    FVG(int i){
        namei = i ;
        ArrayResize(kbar,FVGarraysize,FVGarraysize)     ;
        ArrayResize(kbarclose,FVGarraysize,FVGarraysize);
        ArrayResize(kbarhigh,FVGarraysize,FVGarraysize) ;
        ArrayResize(kbarlow,FVGarraysize,FVGarraysize)  ;
        ArrayResize(kbaropen,FVGarraysize,FVGarraysize) ;
        ArrayResize(kbartime,FVGarraysize,FVGarraysize) ;
        ArrayResize(Property,300,300)                   ;
        ArrayResize(leadblockfg,300,300)                ;
        ArrayResize(leadblockbound,300,300)             ;
        ArrayResize(LTprice,300,300)                    ;
        ArrayResize(RBprice,300,300)                    ;
        ArrayResize(Boxtime,300,300)                    ;
        ArrayResize(effkbar,300,300)                    ;
        ArrayResize(effkbarend,300,300)                 ;
        ArrayResize(fvgsyndrone,300,300)                ;
        ArrayInitialize(kbar,-1)                        ;
        ArrayInitialize(kbarclose,-1)                   ;
        ArrayInitialize(kbarhigh,-1)                    ;
        ArrayInitialize(kbarlow,-1)                     ;
        ArrayInitialize(kbaropen,-1)                    ;
        ArrayInitialize(kbartime,0)                     ;
        ArrayInitialize(Property,-1)                    ;
        ArrayInitialize(leadblockfg,-1)                 ;
        ArrayInitialize(leadblockbound,-1)              ;
        ArrayInitialize(LTprice,-1)                     ;
        ArrayInitialize(RBprice,-1)                     ;
        ArrayInitialize(Boxtime,0)                      ;
        ArrayInitialize(effkbar,-1)                     ;
        ArrayInitialize(effkbarend,-1)                  ;
        ArrayInitialize(fvgsyndrone,-1)                 ;
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
        // for(int l=0; l<FVGarraysize && kbarclose[l]!=-1; l++){
        //     string str = TimeToString(kbartime[l], TIME_DATE|TIME_MINUTES);
        //     if(namei==23)printf("namei= %.0f value= %.5f time=%s", namei, kbarclose[l], str);
        // }    
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
    double Findmaxhighaftk(int idx, int kbarsize, int& kbarend, BOS& bos1){//for lead line block fvg check, maxhigh lead will block green fvg no matter it is up bar or down bar .
        int i = idx;
        double temphigh;
        double temp ;
        datetime ktime    ;
        datetime temptime ;
        int cnt = 0;
        int i_3 = i+3 ;
        int offset = bos1.htfint*60 ;
        if (i_3==kbarsize){
            temp = kbarhigh[kbarsize-1] ; 
            ktime= kbartime[kbarsize-1] ;
        }
        else{
            temp = kbarhigh[i_3] ; 
            ktime= kbartime[i_3] ;
        }
        if(((bos1.sbd>0)&&(bos1.sbu<0))||((bos1.sbu>0)&&(bos1.sbd<0))){
            temptime = bos1.sbd<0? bos1.sbdbrk_t : bos1.sbubrk_t ;
            while(((i_3+cnt)<kbarsize)&&(ktime<temptime)){
                temphigh = kbarhigh[i_3+cnt];
                if(temphigh>temp){
                    temp = temphigh;
                    kbarend = i_3+cnt ;//kbarend=highest high end after k
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        else{
            temptime = bos1.sbd_t<bos1.sbu_t?  bos1.sbu_t :  bos1.sbd_t ;
            while( ((i_3+cnt)<kbarsize) && (ktime<temptime) ){
                temphigh = kbarhigh[i_3+cnt];
                if(temphigh>temp){
                    temp = temphigh;
                    kbarend = i_3+cnt ;
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        return temp ;
    }
    double Findminlowaftk(int idx, int kbarsize, int& kbarend, BOS& bos1){//for lead line block fvg check, maxhigh lead will block green fvg no matter it is up bar or down bar .
        int i = idx;
        double templow;
        double temp ;
        datetime ktime ;
        string teststr ;
        datetime temptime ;
        int cnt = 0;
        int i_3 = i+3 ;
        int offset = bos1.htfint*60 ;
        if (i_3==kbarsize){
            temp = kbarlow[kbarsize-1] ; 
            ktime= kbartime[kbarsize-1] ;
        }
        else{
            temp = kbarlow[i_3] ; 
            ktime= kbartime[i_3] ;
        }
         
        if(((bos1.sbd>0)&&(bos1.sbu<0))||((bos1.sbu>0)&&(bos1.sbd<0))){
            temptime = bos1.sbd<0? bos1.sbdbrk_t : bos1.sbubrk_t ;
            while( ((i_3+cnt)<kbarsize)&&(ktime<temptime) ){
                templow = kbarlow[i_3+cnt];
                if(templow<temp){
                    temp = templow;
                    kbarend = i_3+cnt ; //kbarend=lowest low end after k
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        else{
            temptime = bos1.sbd_t<bos1.sbu_t?  bos1.sbu_t :  bos1.sbd_t ;
            while( ((i_3+cnt)<kbarsize) && (ktime<temptime) ){
                templow = kbarlow[i_3+cnt];
                if(templow<temp){
                    temp = templow;
                    kbarend = i_3+cnt ;
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        // if(bos1.htfint==100){
        //     teststr = TimeToString(ktime, TIME_DATE | TIME_MINUTES);
        //     printf("%.5f, %s, sbd= %.5f ,sbu= %.5f", templow, teststr, bos1.sbd, bos1.sbu);
        // } 
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
    void Putefffvg(BOS& bos1){
        int kbarsize = Getfvgkbarsize() ;
        double maxpt;
        double minpt;
        double lhigh; //l for lead line. 
        double llow ;
        double boxLT; // LT for left top. 
        double boxRB;
        datetime boxtime;
        int kbarmaxend ;
        int kbarminend ;
        int kbarhighend;
        int kbarlowend ;
        int fvgcolor   ;
        int    cnt = 0;
        datetime dt  = bos1.sbd_t;
        datetime ut  = bos1.sbu_t;
        datetime dbt = bos1.sbdbrk_t;
        datetime ubt = bos1.sbubrk_t;
        for(int putidx=0; putidx<kbarsize-2; ++putidx){
            kbarmaxend = 0;
            kbarminend = 0;
            kbarhighend= 0;
            kbarlowend = 0;
            maxpt = Findmaxcloseaftk(putidx, kbarsize, kbarmaxend);
            minpt = Findmincloseaftk(putidx, kbarsize, kbarminend);
            lhigh = Findmaxhighaftk(putidx, kbarsize, kbarhighend, bos1);
            llow  = Findminlowaftk(putidx, kbarsize, kbarlowend, bos1)  ;
            fvgcolor = FVGupdown(putidx, kbarsize) ;
            //-----set property and judge whether the box was blocked or not-----//
            if(fvgcolor == 2){ //green
                boxLT    = kbarhigh[putidx];
                boxRB    = kbarlow[putidx+2] ;
                boxtime  = kbartime[putidx+1];
                if (minpt>boxRB) Property[cnt]    = 2 ; //fvg exist
                else if (minpt<=boxLT){//fvg not exist
                    continue;
                } 
                else Property[cnt]    = 4 ; //fvg exist but is shorten
                if(Property[cnt]>0){
                    if(llow>boxRB) leadblockfg[cnt] = 0;//leadblockbound[cnt] = -1 ; when original initialization, it's set -1
                    else if (llow <= boxLT){
                        leadblockfg[cnt] = 2;
                        //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
                        //fvg not exist anymore 
                    }
                    else{
                        leadblockfg[cnt] = 1;
                    }
                }
            }
            else if(fvgcolor == 1){ //red
                boxLT    = kbarlow[putidx];
                boxRB    = kbarhigh[putidx+2] ;
                boxtime  = kbartime[putidx+1];
                if (maxpt<boxRB) Property[cnt]    = 1 ; //fvg exist
                else if (maxpt>=boxLT){//fvg not exist
                    continue;
                } 
                else Property[cnt]    = 3 ;//fvg exist but is shorten
                if(Property[cnt]>0){   
                    if(lhigh<boxRB) leadblockfg[cnt] = 0;//leadblockbound[cnt] = -1 ; when original initialization, it's set -1
                    else if(lhigh >= boxLT) leadblockfg[cnt] = 2;        
                        //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
                        //fvg not exist anymore 
                    else leadblockfg[cnt] = 1;
                }
            }
            else{
                if(FVGupdown(putidx, kbarsize) == -1) printf("overpass the size");
                continue;
            }
            //-----set fvgsyndrone aligning with property-----//
            if(Property[cnt]>0){
                if((bos1.sbd>0) && (bos1.sbu<0)){//break
                    if(boxtime<ubt) fvgsyndrone[cnt] = 7 ; 
                    else fvgsyndrone[cnt] = 9 ; 
                }  
                else if((bos1.sbd<0) && (bos1.sbu>0)){//break
                    if(boxtime<dbt) fvgsyndrone[cnt] = 8 ; 
                    else fvgsyndrone[cnt] = 10 ; 
                }  
                else{//cover
                    if(ut>dt){
                        if(boxtime<=dt) fvgsyndrone[cnt] = 2 ; //before cover
                        else if(boxtime>ut) fvgsyndrone[cnt] = 6;//after cover
                        else fvgsyndrone[cnt] =4 ; //in the middle of cover
                    } 
                    else{
                        if(boxtime<=ut) fvgsyndrone[cnt] = 1 ; //before cover
                        else if(boxtime>dt) fvgsyndrone[cnt] = 5; //after cover
                        else fvgsyndrone[cnt] =3 ; //in the middle of cover
                    } 
                }  
            }
            //printf("fvgsyndrone[cnt]= %d", fvgsyndrone[cnt]);
            //-----set real box value with fvgsyndrone, the variables following are all under >0 property situation -----//
            int syn   = fvgsyndrone[cnt] ;
            int pro   = Property[cnt]    ;
            int ldblk = leadblockfg[cnt] ;
            if(syn==4 || syn==6 || syn==3 || syn==5 || syn==9 || syn==10){
                if(ldblk==0){
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = boxRB ;
                    Boxtime[cnt]     = boxtime;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[putidx+2];
                }
                else{
                    if(pro%2==0){//even
                        LTprice[cnt]     = boxLT ;
                        RBprice[cnt]     = minpt<boxLT? boxLT : minpt<boxRB? minpt : boxRB ;
                        Boxtime[cnt]     = boxtime;
                        effkbar[cnt]     = kbar[putidx];
                        effkbarend[cnt]  = kbar[kbarminend];
                    }
                    else{//odd
                        LTprice[cnt]     = boxLT ;
                        RBprice[cnt]     = maxpt>boxLT? boxLT : maxpt>boxRB? maxpt : boxRB ;
                        Boxtime[cnt]     = boxtime;
                        effkbar[cnt]     = kbar[putidx];
                        effkbarend[cnt]  = kbar[kbarmaxend];
                    }
                }
            }
            else if(syn==1 || syn==2 || syn==7 || syn==8){
                if(pro%2==0){//even
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = llow<boxLT? boxLT : llow<boxRB? llow : boxRB ;
                    Boxtime[cnt]     = boxtime;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[kbarminend];
                }
                else{//odd
                    LTprice[cnt]     = boxLT ;
                    RBprice[cnt]     = lhigh>boxLT? boxLT : lhigh>boxRB? lhigh : boxRB ;
                    Boxtime[cnt]     = boxtime;
                    effkbar[cnt]     = kbar[putidx];
                    effkbarend[cnt]  = kbar[kbarmaxend];
                }
            }
            else{
                printf("wrong fvgsyndrone entrance, syn= %d", syn);
                break;
            }
            if(Property[cnt]>0) cnt++ ;
        }//for end
        //printf("cnt= %d, namei= %d", cnt, namei);
    }//fun end
};
struct Triset{
    double  gFvgnear             ;
    double  rFvgnear             ;
    int     fvgtype              ;
    bool    broken               ;
    bool    gfvgfg               ; //signal for lead line touch green fvg
    bool    rfvgfg               ; //signal for lead line touch red fvg 
    Triset():gFvgnear(-1),rFvgnear(-1),fvgtype(-1),broken(false),gfvgfg(false),rfvgfg(false){}
    void SearchNearbox(FVG& fvg, const BOS& bos1);
    void TouchfvgDetect(const BOS& bos1, const string& symbolname);
    void TriInit();
};
void Triset::SearchNearbox(FVG& fvg, const BOS& bos1){
    bool ub = bos1.sbu==-2 ; //ub is for broken sbu
    bool db = bos1.sbd==-1 ; //db is for broken sbd
    double gfvgextreme = 0 ;
    double rfvgextreme = MAXSBU;
    fvgtype      = 0        ;
    int  reg     = fvgtype  ;
    double u;
    double d;
    bool s1fg ;
    bool flag ;
    int effkbarsize  = fvg.Getfvgeffkbarsize();
    if(ub){
        u = MAXSBU;
        d = bos1.sbd ;
        broken = true ;
    }
    else if(db){
        u = bos1.sbu ;
        d = 0 ;
        broken = true ;
    }
    else{
        u = bos1.sbu;
        d = bos1.sbd;
        broken = false ;
    }
    for (int i=0; i<effkbarsize; ++i){
        s1fg = (fvg.LTprice[i]<u && fvg.LTprice[i]>d) || (fvg.RBprice[i]<u && fvg.RBprice[i]>d);
        if((fvg.leadblockfg[i]!=2)&&(fvg.leadblockfg[i]!=-1)){
            flag = (s1fg && broken) ;
            if(flag){
                if((fvg.Property[i]%2)==0) gfvgextreme = fvg.RBprice[i]>gfvgextreme? fvg.RBprice[i] : gfvgextreme ;
                else rfvgextreme = fvg.RBprice[i]<rfvgextreme? fvg.RBprice[i] : rfvgextreme ;
                if((fvg.Property[i]%2)==0){
                    if(fvg.leadblockfg[i]==1) gFvgnear = gfvgextreme ;
                    else gFvgnear = gfvgextreme ;
                }
                else{
                    if(fvg.leadblockfg[i]==1) rFvgnear = rfvgextreme ;
                    else rFvgnear = rfvgextreme ;
                }
            }
            if(fvgtype!=0xF){
                if(flag){
                    reg          = fvgtype ;
                    if(reg==0){
                        fvgtype = (fvg.Property[i]%2==0)? 0x2 : 0x1 ;
                    }
                    else if(reg==2){
                        fvgtype = (fvg.Property[i]%2==0)? 0x2 : 0xF ;
                    }
                    else{
                        fvgtype = (fvg.Property[i]%2==1)? 0x1 : 0xF ;
                    }
                    //if((fvg.namei==159) && (j==158)) printf("fvg%.0f= j=%.0f, 0x%.0f", fvg.namei, j, fvg.Property[i]);
                }

            }
            else continue ;
        }
    } 
}
void Triset::TouchfvgDetect(const BOS& bos1, const string& symbolname){
    bool ub = bos1.sbu==-2 ; //ub is for broken sbu
    bool db = bos1.sbd==-1 ; //db is for broken sbd
    if(broken){
        if(db){ //broken sbd
            for(int k=0; k<datasize; k++){
                datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                if((iLow(symbolname,PERIOD_M1,k)<=gFvgnear) && (temptime>=bos1.sbdbrk_t)){
                    gfvgfg = true ; 
                    break; 
                } 
                else{
                    if(temptime<bos1.sbdbrk_t){
                        gfvgfg = false ;
                        break ; 
                    }
                } 
            }
        }
        else{ //broken sbu
            for(int k=0; k<datasize; k++){
                datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                if((iHigh(symbolname,PERIOD_M1,k)>=rFvgnear) && (temptime>=bos1.sbubrk_t)){
                    rfvgfg = true ; 
                    break;    
                } 
                else{
                    if(temptime<bos1.sbubrk_t){
                        rfvgfg = false ;
                        break ; 
                    }
                }
            }
        }
    }
}
void Triset::TriInit(){
    gFvgnear   = -1     ;
    rFvgnear   = -1     ;
    fvgtype    = -1     ;
    broken     = false  ;
    gfvgfg     = 0      ;
    rfvgfg     = 0      ;
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

void BOSJudge(BOS& bosdata, const int size, const RawCandles& rd, const int starti, Helper& helper, FVG& fvgarr, const int& i){
    int k                         ;                 
    int qidxnow                   ;
    int qidxpt                    ;
    double tempprice              ;
    datetime temptime             ;
    int cnt                       ;
    int tempmin                   ;
    int tempminm1                 ;
    int tempminreg=-1             ;
    int htfint =i+1               ;
    k   = starti+1                ;
    cnt = 0                       ;
    while(k < size){//last one can not be considered cuz it's not closed
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
                fvgarr.kbar[cnt]     = k-1 ;
            }
            else{
                tempprice         = rd.mat_rates[3][k] ;
                temptime          = rd.mat_rates[4][k] ;
                if(tempprice == bosdata.regclose3){
                    ++k;
                    continue;
                }
                fvgarr.kbar[cnt]     = k ;
            }
            ++cnt;
            //if(bosdata.htfint==4)printf("k= %d \t tempprice@k-1= %.5f \t date@k-1= %s\n htfint= %.1f", k, tempprice,TimeToString(temptime,TIME_DATE|TIME_MINUTES),bosdata.htfint);
            if(bosdata.state == 1){
                bosdata.regclose1 = bosdata.regclose2;
                bosdata.regclose2 = bosdata.regclose3;
                bosdata.regclose3 = tempprice;
                bosdata.regclose1_t = bosdata.regclose2_t;
                bosdata.regclose2_t = bosdata.regclose3_t;
                bosdata.regclose3_t = temptime;
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
                }
                //else //Buff_key1維持原樣
                if(bosdata.sbu>0 && bosdata.sbd>0){
                    bosdata.i2bsbu  = bosdata.sbu  ;
                    bosdata.i2bsbu_t= bosdata.sbu_t;
                    bosdata.i2bsbd  = bosdata.sbd  ;
                    bosdata.i2bsbd_t= bosdata.sbd_t;
                }
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu     = -2;
                    bosdata.sbu_t   = 0;
                    bosdata.i2bsbu  = -2;
                    bosdata.i2bsbu_t= 0 ;
                    bosdata.sbubrk_t= bosdata.regclose3_t;  
                    bosdata.sbd     = bosdata.reg1key;
                    bosdata.sbd_t   = bosdata.reg1key_t;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd     = -1 ;
                    bosdata.sbd_t   = 0 ;
                    bosdata.i2bsbd  = -1 ;
                    bosdata.i2bsbd_t= 0  ;
                    bosdata.sbdbrk_t= bosdata.regclose3_t;  
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
                    bosdata.sbubrk_t    = 0;
                    bosdata.sbdbrk_t    = 0;
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                    bosdata.i2bsbu      = bosdata.sbu  ;
                    bosdata.i2bsbu_t    = bosdata.sbu_t;
                    bosdata.i2bsbd      = bosdata.sbd  ;
                    bosdata.i2bsbd_t    = bosdata.sbd_t;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd         = -1;
                    bosdata.sbd_t       = 0 ;
                    bosdata.i2bsbd      = -1;
                    bosdata.i2bsbd_t    = 0 ;
                    bosdata.sbdbrk_t    = bosdata.regclose3_t;  
                }
                bosdata.state = 1;
            }
            if(bosdata.state == 4){
                if(bosdata.slope1 != bosdata.slope2){
                    bosdata.reg2key     = bosdata.regclose2;
                    bosdata.reg2key_t   = bosdata.regclose2_t;
                    bosdata.sbd         = bosdata.reg2key;
                    bosdata.sbd_t       = bosdata.reg2key_t;
                    bosdata.sbubrk_t    = 0;
                    bosdata.sbdbrk_t    = 0;
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                    bosdata.i2bsbu      = bosdata.sbu  ;
                    bosdata.i2bsbu_t    = bosdata.sbu_t;
                    bosdata.i2bsbd      = bosdata.sbd  ;
                    bosdata.i2bsbd_t    = bosdata.sbd_t;
                }
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu         = -2;
                    bosdata.sbu_t       = 0 ;
                    bosdata.i2bsbu      = -2;
                    bosdata.i2bsbu_t    = 0 ;
                    bosdata.sbubrk_t    = bosdata.regclose3_t;  
                }
                bosdata.state = 1;
            }
        }
        ++k; 
    }//while end
    //if(bosdata.htfint==393) printf("bosdata.htfint= %d, sbd= %.5f sbu= %.5f", bosdata.htfint, bosdata.sbd, bosdata.sbu);
    // string str1 = TimeToString(bosdata.sbd_t,TIME_DATE|TIME_MINUTES);
    // string str2 = TimeToString(bosdata.sbu_t,TIME_DATE|TIME_MINUTES);
    // printf("bosdata.htfint= %.0f, sbd= %.5f sbu= %.5f", bosdata.htfint, bosdata.sbd, bosdata.sbu);
    // printf("bosdata.htfint= %.0f, %s ,%s", bosdata.htfint, str1, str2);
}//func end

#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful