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
        ArrayResize(Boxtime,300,300)                     ;
        ArrayResize(effkbar,300,300)                    ;
        ArrayResize(effkbarend,300,300)                 ;
        ArrayResize(fvgsyndrone,300,300)            ;
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
                ktime = kbartime[i_3+cnt];
                if(temphigh>temp){
                    temp = temphigh;
                    kbarend = i_3+cnt ;//kbarend=highest high end after k
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        else{
            temptime = bos1.sbd_t<bos1.sbu_t?  bos1.sbd_t :  bos1.sbu_t ;
            while( ((i_3+cnt)<kbarsize) && (ktime<temptime) ){
                temphigh = kbarhigh[i_3+cnt];
                ktime = kbartime[i_3+cnt];
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
                ktime = kbartime[i_3+cnt];
                if(templow<temp){
                    temp = templow;
                    kbarend = i_3+cnt ; //kbarend=lowest low end after k
                } 
                ++cnt ;
                ktime = kbartime[i_3+cnt];
            }
        }
        else{
            temptime = bos1.sbd_t<bos1.sbu_t?  bos1.sbd_t :  bos1.sbu_t ;
            while( ((i_3+cnt)<kbarsize) && (ktime<temptime) ){
                templow = kbarlow[i_3+cnt];
                ktime = kbartime[i_3+cnt];
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
                        if(boxtime<=dt) fvgsyndrone[cnt] = 2 ;
                        else if(boxtime>ut) fvgsyndrone[cnt] = 6;
                        else fvgsyndrone[cnt] =4 ;
                    } 
                    else{
                        if(boxtime<=ut) fvgsyndrone[cnt] = 1 ;
                        else if(boxtime>dt) fvgsyndrone[cnt] = 5;
                        else fvgsyndrone[cnt] =3 ;
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

    // void Putefffvg(BOS& bos1){
    //     int kbarsize = Getfvgkbarsize() ;
    //     double maxpt;
    //     double minpt;
    //     double lhigh; //l for lead line. 
    //     double llow ;
    //     double boxLT; // LT for left top. 
    //     double boxRB;
    //     datetime boxtime;
    //     int kbarmaxend ;
    //     int kbarminend ;
    //     int kbarhighend;
    //     int kbarlowend ;
    //     int    cnt = 0;
    //     datetime dt  = bos1.sbd_t;
    //     datetime ut  = bos1.sbu_t;
    //     datetime dbt = bos1.sbdbrk_t;
    //     datetime ubt = bos1.sbubrk_t;
    //     for(int putidx=0; putidx<kbarsize-2; ++putidx){
    //         kbarmaxend = 0;
    //         kbarminend = 0;
    //         kbarhighend= 0;
    //         kbarlowend = 0;
    //         maxpt = Findmaxcloseaftk(putidx, kbarsize, kbarmaxend);
    //         minpt = Findmincloseaftk(putidx, kbarsize, kbarminend);
    //         lhigh = Findmaxhighaftk(putidx, kbarsize, kbarhighend, bos1);
    //         llow  = Findminlowaftk(putidx, kbarsize, kbarlowend, bos1)  ;
    //         if(FVGupdown(putidx, kbarsize) == 2){ //green
    //             boxLT  = kbarhigh[putidx];
    //             boxRB  = kbarlow[putidx+2];
    //             boxtime=kbartime[putidx+1];
    //             if (minpt>boxRB){ //fvg exist
    //                 Property[cnt]    = 2 ;
    //                 LTprice[cnt]     = boxLT ;
    //                 RBprice[cnt]     = boxRB ;
    //                 Boxtime[cnt]     = boxtime;
    //                 effkbar[cnt]     = kbar[putidx];
    //                 effkbarend[cnt]  = kbar[putidx+2];
    //                 if((bos1.sbd>0) && (bos1.sbu<0)){
    //                     if(boxtime<dbt) fvgsyndrone[cnt] = 7 ; 
    //                     else fvgsyndrone[cnt] = 9 ; 
    //                 }  
    //                 else if((bos1.sbd<0) && (bos1.sbu>0)){
    //                     if(boxtime<ubt) fvgsyndrone[cnt] = 8 ; 
    //                     else fvgsyndrone[cnt] = 10 ; 
    //                 }  
    //                 else{
    //                     if(ut>dt){
    //                         if(boxtime<=dt) fvgsyndrone[cnt] = 2 ;
    //                         else if(boxtime>ut) fvgsyndrone[cnt] = 6;
    //                         else fvgsyndrone[cnt] =4 ;
    //                     } 
    //                     else{
    //                         if(boxtime<=ut) fvgsyndrone[cnt] = 1 ;
    //                         else if(boxtime>dt) fvgsyndrone[cnt] = 5;
    //                         else fvgsyndrone[cnt] =3 ;
    //                     } 
    //                 }
    //                 if(llow>boxRB){
    //                     //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                     leadblockfg[cnt] = 0;   
    //                 } 
    //                 else if (llow <= boxLT){
    //                     //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                     leadblockfg[cnt] = 2;  // properry, leadblockfg{x 0}or{x 1} belong noblock or partly blocked respectively;//{x 2}is fully blocked
    //                     //fvg not exist anymore 
    //                 }
    //                 else{
    //                     leadblockfg[cnt] = 1;
    //                 }
    //                 if(fvgsyndrone[cnt]>2 && fvgsyndrone[cnt]<7){//after coverage

    //                 }
    //                 ++cnt;

    //             }
    //             else if (minpt<=boxLT){//fvg not exist
                    
    //             } 
    //             else{ //fvg exist but is shorten
    //                 Property[cnt]    = 4 ;
    //                 LTprice[cnt]     = boxLT ;
    //                 RBprice[cnt]     = minpt ;
    //                 Boxtime[cnt]     = boxtime;
    //                 effkbar[cnt]     = kbar[putidx];
    //                 effkbarend[cnt]  = kbar[kbarminend];
    //                 if((bos1.sbd>0) && (bos1.sbu<0)){//break
    //                     if(boxtime<dbt) fvgsyndrone[cnt] = 7 ; 
    //                     else fvgsyndrone[cnt] = 9 ; 
    //                 }  
    //                 else if((bos1.sbd<0) && (bos1.sbu>0)){//break
    //                     if(boxtime<ubt) fvgsyndrone[cnt] = 8 ; 
    //                     else fvgsyndrone[cnt] = 10 ; 
    //                 }  
    //                 else{//cover
    //                     if(ut>dt){
    //                         if(boxtime<=dt) fvgsyndrone[cnt] = 2 ;
    //                         else if(boxtime>ut) fvgsyndrone[cnt] = 6;
    //                         else fvgsyndrone[cnt] =4 ;
    //                     } 
    //                     else{
    //                         if(boxtime<=ut) fvgsyndrone[cnt] = 1 ;
    //                         else if(boxtime>dt) fvgsyndrone[cnt] = 5;
    //                         else fvgsyndrone[cnt] =3 ;
    //                     } 
    //                 }
    //                 if(llow>boxRB) leadblockfg[cnt] = 0;//leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                 else if (llow <= boxLT){
    //                     leadblockfg[cnt] = 2;
    //                     //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                     //fvg not exist anymore 
    //                 }
    //                 else{
    //                     RBprice[cnt]        = llow ;
    //                     leadblockbound[cnt] = llow ;
    //                     leadblockfg[cnt] = 1;
    //                 } 
    //                 ++cnt;
    //             }
    //         }
    //         else if(FVGupdown(putidx, kbarsize) == 1){ //red
    //             boxLT = kbarlow[putidx];
    //             boxRB = kbarhigh[putidx+2] ;
    //             boxtime=kbartime[putidx+1];
    //             if (maxpt<boxRB){ //fvg exist
    //                 Property[cnt]    = 1 ;
    //                 LTprice[cnt]     = boxLT ;
    //                 RBprice[cnt]     = boxRB ;
    //                 Boxtime[cnt]     = boxtime;
    //                 effkbar[cnt]     = kbar[putidx];
    //                 effkbarend[cnt]  = kbar[putidx+2];
    //                 if((bos1.sbd>0) && (bos1.sbu<0)){
    //                     if(boxtime<dbt) fvgsyndrone[cnt] = 7 ; 
    //                     else fvgsyndrone[cnt] = 9 ; 
    //                 }  
    //                 else if((bos1.sbd<0) && (bos1.sbu>0)){
    //                     if(boxtime<ubt) fvgsyndrone[cnt] = 8 ; 
    //                     else fvgsyndrone[cnt] = 10 ; 
    //                 }  
    //                 else{
    //                     if(ut>dt){
    //                         if(boxtime<=dt) fvgsyndrone[cnt] = 2 ;
    //                         else if(boxtime>ut) fvgsyndrone[cnt] = 6;
    //                         else fvgsyndrone[cnt] =4 ;
    //                     } 
    //                     else{
    //                         if(boxtime<=ut) fvgsyndrone[cnt] = 1 ;
    //                         else if(boxtime>dt) fvgsyndrone[cnt] = 5;
    //                         else fvgsyndrone[cnt] =3 ;
    //                     } 
    //                 }
    //                 if(lhigh<boxRB) leadblockfg[cnt] = 0;//leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                 else if(lhigh >= boxLT){
    //                     //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                     leadblockfg[cnt] = 2;
    //                     //fvg not exist anymore 
    //                 }
    //                 else{
    //                     RBprice[cnt]        = lhigh ;
    //                     leadblockbound[cnt] = lhigh ;
    //                     leadblockfg[cnt] = 1;
    //                 }
    //                 ++cnt;
    //             }
    //             else if (maxpt>=boxLT){//fvg not exist
                    
    //             } 
    //             else{ //fvg exist but is shorten
    //                 Property[cnt]    = 3 ;
    //                 LTprice[cnt]     = boxLT ;
    //                 RBprice[cnt]     = maxpt ;
    //                 Boxtime [cnt]    = boxtime;
    //                 effkbar[cnt]     = kbar[putidx];
    //                 effkbarend[cnt]  = kbar[kbarmaxend];
    //                 if((bos1.sbd>0) && (bos1.sbu<0)){
    //                     if(boxtime<dbt) fvgsyndrone[cnt] = 7 ; 
    //                     else fvgsyndrone[cnt] = 9 ; 
    //                 }  
    //                 else if((bos1.sbd<0) && (bos1.sbu>0)){
    //                     if(boxtime<ubt) fvgsyndrone[cnt] = 8 ; 
    //                     else fvgsyndrone[cnt] = 10 ; 
    //                 }  
    //                 else{
    //                     if(ut>dt){
    //                         if(boxtime<=dt) fvgsyndrone[cnt] = 2 ;
    //                         else if(boxtime>ut) fvgsyndrone[cnt] = 6;
    //                         else fvgsyndrone[cnt] =4 ;
    //                     } 
    //                     else{
    //                         if(boxtime<=ut) fvgsyndrone[cnt] = 1 ;
    //                         else if(boxtime>dt) fvgsyndrone[cnt] = 5;
    //                         else fvgsyndrone[cnt] =3 ;
    //                     } 
    //                 }
    //                 if(lhigh<boxRB) leadblockfg[cnt] = 0;//leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                 else if(lhigh >= boxLT){
    //                     leadblockfg[cnt] = 2;
    //                     //leadblockbound[cnt] = -1 ; when original initialization, it's set -1
    //                     //fvg not exist anymore 
    //                 }
    //                 else{
    //                     RBprice[cnt]        = lhigh ;
    //                     leadblockbound[cnt] = lhigh ;
    //                     leadblockfg[cnt] = 1;
    //                 }
    //                 ++cnt;
    //             }
    //         }
    //         else{
    //             if(FVGupdown(putidx, kbarsize) == -1) printf("overpass the size");
    //         }
    //     }//for end
    //     //printf("cnt= %d, namei= %d", cnt, namei);
    // }//fun end
};
struct Triset{
    uint    comparecode[]        ;
    uint    comparecode0F[]      ;
    double  code0FExtreme[]      ;
    double  code0FgFvgExtreme[]  ;
    double  code0FrFvgExtreme[]  ;
    bool    code0Ffvgblockcheck[];
    bool    highfg[]             ; //signal for touch high bound 
    bool    lowfg[]              ; //signal for touch low bound
    bool    gfvgfg[]             ; //signal for lead line touch green fvg
    bool    rfvgfg[]             ; //signal for lead line touch red fvg 
    int     wide2itv0X           ;
    int     wide2itvXF           ;
    int     fvgtype0F[]          ;
    Triset():wide2itv0X(-1),wide2itvXF(-1){}
    double TriItvCompare0X (FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& delta0X, const int& j, const int& count3);
    double TriItvCompareXF (FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& deltaXF, const int& j, const int& count3);
    void   TriFVGcheck0F   (FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const double& u, const double& d, const int& j);
};

double Triset::TriItvCompare0X (FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& delta0X, const int& j, const int& count3){//1 belong case 0xZZZ0ZZZZ,those Z beside 0 left can't be touch, otherwise rule will break, 5 belong 0xZZZZFZZZ, X non 0 and F
    double deltatemp = delta0X ;
    if(count3==1){
        delta0X     = MathMax(bos2.sbd, bos3.sbd);
        delta0X     = MathMax(delta0X, bos4.sbd);
        if(delta0X<0) delta0X=0 ;
        TriFVGcheck0F(fvg, fvg2, fvg3, fvg4, bos1.sbu, delta0X, j); //fix bos1.sbu from minsbu
        code0FExtreme[j] = delta0X ;
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
double Triset::TriItvCompareXF (FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, double& deltaXF, const int& j, const int& count3){//1 belong case 0xZZZ0ZZZZ,those Z beside 0 left can't be touch, otherwise rule will break, 5 belong 0xZZZZFZZZ, X non 0 and F
    double deltatemp = deltaXF ;
    if(count3==5){
        deltaXF     = MathMin(bos2.sbu, bos3.sbu);
        if(deltaXF<0) deltaXF= bos2.sbu>bos3.sbu? bos2.sbu : bos3.sbu ;
        deltaXF     = MathMin(deltaXF , bos4.sbu);
        if(deltaXF<0) deltaXF= deltaXF>bos4.sbu? deltaXF : bos4.sbu ;
        if(deltaXF<0) deltaXF= MAXSBU ;
        //if((fvg.namei==159) && (j==158)) printf("fvg%.0f j=%.0f,SBU= %.5f, SBD=%.5f", fvg.namei, j, deltaXF, bos1.sbd);
        TriFVGcheck0F(fvg, fvg2, fvg3, fvg4, deltaXF, bos1.sbd, j); //fix bos1.sbd from maxsbd
        code0FExtreme[j] = deltaXF ;
        if(wide2itvXF==-1){
            wide2itvXF = j ;
            deltatemp = deltaXF ; // I need to get min or max value, so that can deal with 0Ffile touch high level bos problem 
        }
        else{
            if((deltatemp <= deltaXF)&&(deltaXF!=MAXSBU)){
                wide2itvXF = j ;
                deltatemp = deltaXF ;
            }
        }
        return deltatemp ;
    }
    else return deltaXF ;
}
void Triset::TriFVGcheck0F(FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, const double& u, const double& d, const int& j){
    int effkbarsize  = fvg.Getfvgeffkbarsize();
    int effkbarsize2 = fvg2.Getfvgeffkbarsize();
    int effkbarsize3 = fvg3.Getfvgeffkbarsize();
    int effkbarsize4 = fvg4.Getfvgeffkbarsize();
    bool s1fg ;
    bool s2fg ;
    bool s3fg ;
    bool s4fg ;
    bool flag ;
    fvgtype0F[j] = 0 ;
    int  reg     = fvgtype0F[j]  ;
    double gfvgextreme = 0 ;
    double rfvgextreme = MAXSBU;
    string filename;
    int handle;
    string line;
    if(fvg.namei==ii && (j+1==jj)){
        filename =StringFormat("%s"+"\\fvg.txt", AccountInfoString(ACCOUNT_COMPANY));
        handle=FileOpen(filename,FILE_WRITE|FILE_TXT);
        line="";
    }
    for (int i=0; i<effkbarsize; ++i){
        s1fg = (fvg.LTprice[i]<u && fvg.LTprice[i]>d) || (fvg.RBprice[i]<u && fvg.RBprice[i]>d);
        if((fvg.leadblockfg[i]!=2)&&(fvg.leadblockfg[i]!=-1)){
            flag = (s1fg && fvg.fvgsyndrone[i]) ;
            if(fvg.namei==ii && fvg.namei==ii){
                line = StringFormat("l1=%.0f, l1=%.0f, fvg1.outs[%.0f]= %d,fvg1.p[%.0f]= %d, RB=%.5f, s1fg=%d ,flag=%d, u=%.5f, d=%.5f" ,fvg.namei, fvg.namei, i, fvg.fvgsyndrone[i], i, fvg.Property[i], fvg.RBprice[i], s1fg, flag, u, d);
                FileWrite(handle, line);
            }
            if(flag){
                if((fvg.Property[i]%2)==0) gfvgextreme = fvg.RBprice[i]>gfvgextreme? fvg.RBprice[i] : gfvgextreme ;
                else rfvgextreme = fvg.RBprice[i]<rfvgextreme? fvg.RBprice[i] : rfvgextreme ;
                if((fvg.Property[i]%2)==0){
                    if(fvg.leadblockfg[i]==1) code0FgFvgExtreme[j] = fvg.leadblockbound[i] ;
                    else code0FgFvgExtreme[j] = gfvgextreme ;
                }
                else{
                    if(fvg.leadblockfg[i]==1) code0FrFvgExtreme[j] = fvg.leadblockbound[i] ;
                    else code0FrFvgExtreme[j] = rfvgextreme ;
                }
                code0Ffvgblockcheck[j] = fvg.leadblockfg[i] ;
            }
            if(fvgtype0F[j]!=0xF){
                if(flag){
                    reg          = fvgtype0F[j] ;
                    if(reg==0){
                        fvgtype0F[j] = (fvg.Property[i]%2==0)? 0x2 : 0x1 ;
                    }
                    else if(reg==2){
                        fvgtype0F[j] = (fvg.Property[i]%2==0)? 0x2 : 0xF ;
                    }
                    else{
                        fvgtype0F[j] = (fvg.Property[i]%2==1)? 0x1 : 0xF ;
                    }
                    //if((fvg.namei==159) && (j==158)) printf("fvg%.0f= j=%.0f, 0x%.0f", fvg.namei, j, fvg.Property[i]);
                }

            }
            else continue ;
        }
    } 
    for (int i=0; i<effkbarsize2; ++i){
        s2fg = (fvg2.LTprice[i]<u && fvg2.LTprice[i]>d) || (fvg2.RBprice[i]<u && fvg2.RBprice[i]>d);
        if((fvg2.leadblockfg[i]!=2)&&(fvg2.leadblockfg[i]!=-1)){
            flag = (s2fg && fvg2.fvgsyndrone[i]) ;
            if(fvg.namei==ii && fvg2.namei==(ii+jj)){
                line = StringFormat("l1=%.0f, l2=%.0f, fvg2.outs[%.0f]= %d,fvg2.p[%.0f]= %d, RB=%.5f, s2fg=%d ,flag=%d, u=%.5f, d=%.5f" ,fvg.namei, fvg2.namei, i, fvg2.fvgsyndrone[i], i, fvg2.Property[i], fvg2.RBprice[i], s2fg, flag, u, d);
                FileWrite(handle, line);
            }
            if(flag){
                if((fvg2.Property[i]%2)==0) gfvgextreme = fvg2.RBprice[i]>gfvgextreme? fvg2.RBprice[i] : gfvgextreme ;
                else rfvgextreme = fvg2.RBprice[i]<rfvgextreme? fvg2.RBprice[i] : rfvgextreme ;
                if((fvg2.Property[i]%2)==0){
                    if(fvg2.leadblockfg[i]==1) code0FgFvgExtreme[j] = code0FgFvgExtreme[j]>fvg2.leadblockbound[i]? code0FgFvgExtreme[j] : fvg2.leadblockbound[i];
                    else code0FgFvgExtreme[j] = gfvgextreme ;
                }
                else{
                    if(fvg2.leadblockfg[i]==1) code0FrFvgExtreme[j] = code0FrFvgExtreme[j]<fvg2.leadblockbound[i]? code0FrFvgExtreme[j] : fvg2.leadblockbound[i];
                    else code0FrFvgExtreme[j] = rfvgextreme ;
                }
                code0Ffvgblockcheck[j] = fvg2.leadblockfg[i] ;
            }
            if((fvgtype0F[j]!=0xF) && (fvgtype0F[j]!=0xB) && (fvgtype0F[j]!=0xA) && (fvgtype0F[j]!=0xD) && (fvgtype0F[j]!=0xC)){
                if(flag){
                    reg          = fvgtype0F[j] ;
                    if(reg==0) continue ;
                    else if(reg==2){
                        fvgtype0F[j] = (fvg2.Property[i]%2==0)? 0x4 : 0xB ;
                    }
                    else if(reg==1){
                        fvgtype0F[j] = (fvg2.Property[i]%2==1)? 0x3 : 0xA ;
                    }
                    else if(reg==4){
                        fvgtype0F[j] = (fvg2.Property[i]%2==0)? 0x4 : 0xD ;
                    }
                    else{
                        fvgtype0F[j] = (fvg2.Property[i]%2==1)? 0x3 : 0xC ;
                    }
                }
            }
            else continue ;      
        }
        
    } 
    for (int i=0; i<effkbarsize3; ++i){
        s3fg = (fvg3.LTprice[i]<u && fvg3.LTprice[i]>d) || (fvg3.RBprice[i]<u && fvg3.RBprice[i]>d);
        if((fvg3.leadblockfg[i]!=2)&&(fvg3.leadblockfg[i]!=-1)){
            flag = (s3fg && fvg3.fvgsyndrone[i]) ;
            if(fvg.namei==ii && fvg3.namei==(ii+jj+jj)){
                line = StringFormat("l1=%.0f, l3=%.0f, fvg3.outs[%.0f]= %d,fvg3.p[%.0f]= %d, RB=%.5f, s3fg=%d ,flag=%d, u=%.5f, d=%.5f" ,fvg.namei, fvg3.namei, i, fvg3.fvgsyndrone[i], i, fvg3.Property[i], fvg3.RBprice[i], s3fg, flag, u, d);
                FileWrite(handle, line);
            }
            if(flag){
                if((fvg3.Property[i]%2)==0) gfvgextreme = fvg3.RBprice[i]>gfvgextreme? fvg3.RBprice[i] : gfvgextreme ;
                else rfvgextreme = fvg3.RBprice[i]<rfvgextreme? fvg3.RBprice[i] : rfvgextreme ;
                if((fvg3.Property[i]%2)==0){
                    if(fvg3.leadblockfg[i]==1) code0FgFvgExtreme[j] = code0FgFvgExtreme[j]>fvg3.leadblockbound[i]? code0FgFvgExtreme[j] : fvg3.leadblockbound[i];
                    else code0FgFvgExtreme[j] = gfvgextreme ;
                }
                else{
                    if(fvg3.leadblockfg[i]==1) code0FrFvgExtreme[j] = code0FrFvgExtreme[j]<fvg3.leadblockbound[i]? code0FrFvgExtreme[j] : fvg3.leadblockbound[i];
                    else code0FrFvgExtreme[j] = rfvgextreme ;
                }
                code0Ffvgblockcheck[j] = fvg3.leadblockfg[i] ;
            }
            if((fvgtype0F[j]!=0xF) && (fvgtype0F[j]!=0xB) && (fvgtype0F[j]!=0xA) && (fvgtype0F[j]!=0xD) && (fvgtype0F[j]!=0xC)){
                if(flag){
                    reg          = fvgtype0F[j] ;
                    if(reg==0) continue ;
                    else if(reg==2){
                        fvgtype0F[j] = (fvg3.Property[i]%2==0)? 0x4 : 0xB ;
                    }
                    else if(reg==1){
                        fvgtype0F[j] = (fvg3.Property[i]%2==1)? 0x3 : 0xA ;
                    }
                    else if(reg==4){
                        fvgtype0F[j] = (fvg3.Property[i]%2==0)? 0x4 : 0xD ;
                    }
                    else{
                        fvgtype0F[j] = (fvg3.Property[i]%2==1)? 0x3 : 0xC ;
                    }
                }
            }
            else continue ;    
        }
    } 
    for (int i=0; i<effkbarsize4; ++i){
        s4fg = (fvg4.LTprice[i]<u && fvg4.LTprice[i]>d) || (fvg4.RBprice[i]<u && fvg4.RBprice[i]>d);
        if((fvg4.leadblockfg[i]!=2)&&(fvg4.leadblockfg[i]!=-1)){
            flag = (s4fg && fvg4.fvgsyndrone[i]) ;
            if(fvg.namei==ii && fvg4.namei==(ii+jj+jj+jj)){
                line = StringFormat("l1=%.0f, l4=%.0f, fvg4.outs[%.0f]= %d,fvg4.p[%.0f]= %d, RB=%.5f, s4fg=%d ,flag=%d, u=%.5f, d=%.5f" ,fvg.namei, fvg4.namei, i, fvg4.fvgsyndrone[i], i, fvg4.Property[i], fvg4.RBprice[i], s4fg, flag, u, d);
                FileWrite(handle, line);              
            }
            if(flag){
                if((fvg4.Property[i]%2)==0) gfvgextreme = fvg4.RBprice[i]>gfvgextreme? fvg4.RBprice[i] : gfvgextreme ;
                else rfvgextreme = fvg4.RBprice[i]<rfvgextreme? fvg4.RBprice[i] : rfvgextreme ;
                if((fvg4.Property[i]%2)==0){
                    if(fvg4.leadblockfg[i]==1) code0FgFvgExtreme[j] = code0FgFvgExtreme[j]>fvg4.leadblockbound[i]? code0FgFvgExtreme[j] : fvg4.leadblockbound[i];
                    else code0FgFvgExtreme[j] = gfvgextreme ;
                }
                else{
                    if(fvg4.leadblockfg[i]==1) code0FrFvgExtreme[j] = code0FrFvgExtreme[j]<fvg4.leadblockbound[i]? code0FrFvgExtreme[j] : fvg4.leadblockbound[i];
                    else code0FrFvgExtreme[j] = rfvgextreme ;
                }
                code0Ffvgblockcheck[j] = fvg4.leadblockfg[i] ;
            }
            if((fvgtype0F[j]!=0xF) && (fvgtype0F[j]!=0xB) && (fvgtype0F[j]!=0xA) && (fvgtype0F[j]!=0xD) && (fvgtype0F[j]!=0xC)){
                if(flag){
                    reg          = fvgtype0F[j] ;
                    if(reg==0) continue ;
                    else if(reg==2){
                        fvgtype0F[j] = (fvg4.Property[i]%2==0)? 0x4 : 0xB ;
                    }
                    else if(reg==1){
                        fvgtype0F[j] = (fvg4.Property[i]%2==1)? 0x3 : 0xA ;
                    }
                    else if(reg==4){
                        fvgtype0F[j] = (fvg4.Property[i]%2==0)? 0x4 : 0xD ;
                    }
                    else{
                        fvgtype0F[j] = (fvg4.Property[i]%2==1)? 0x3 : 0xC ;
                    }
                }
            }
            else continue ;   
        }
    }
    if(fvg.namei==ii && (j+1==jj)) FileClose(handle);
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
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu     = -2;
                    bosdata.sbu_t   = -2;
                    bosdata.sbubrk_t= bosdata.regclose3_t;  
                    bosdata.sbd     = bosdata.reg1key;
                    bosdata.sbd_t   = bosdata.reg1key_t;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd     = -1 ;
                    bosdata.sbd_t   = -1 ;
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
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                }
                if(bosdata.regclose3<bosdata.sbd){
                    bosdata.sbd         = -1;
                    bosdata.sbd_t       = -1;
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
                    bosdata.sbdbrk_t    = 0;
                    bosdata.reg1key     = bosdata.reg2key;
                    bosdata.reg1key_t   = bosdata.reg2key_t;
                }
                if(bosdata.regclose3>bosdata.sbu){
                    bosdata.sbu         = -2;
                    bosdata.sbu_t       = -2;
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

Triset TriCode(FVG& fvg, FVG& fvg2, FVG& fvg3, FVG& fvg4, Triset& ts, const BOS& bos1, const BOS& bos2, const BOS& bos3, const BOS& bos4, int j, double& tempd, double& tempu, double& delta0X, double& deltaXF){
    //-1 == no sbd, -2 == no sbu
    uint code       = 0 ;
    int count3      = 0 ;
    int mask[8]     = {__LEVEL4SBDMASK, __LEVEL3SBDMASK, __LEVEL2SBDMASK, __LEVEL1SBUMASK, __LEVEL1SBUMASK, __LEVEL2SBUMASK, __LEVEL3SBUMASK, __LEVEL4SBUMASK};
    datetime sbt[8] = {bos4.sbdbrk_t, bos3.sbdbrk_t, bos2.sbdbrk_t, bos1.sbdbrk_t, bos1.sbubrk_t, bos2.sbubrk_t, bos3.sbubrk_t, bos4.sbubrk_t};
    string sbt_s[8] = {""} ;
    for(int i=0; i<8; ++i){
        sbt_s[i] = TimeToString(sbt[i], TIME_DATE|TIME_MINUTES);
    }
    double arr[8]   = {bos4.sbd, bos3.sbd, bos2.sbd, bos1.sbd, bos1.sbu, bos2.sbu, bos3.sbu, bos4.sbu};
    int    index[8] ={28, 24, 20, 16, 12, 8, 4, 0}; //according to the index[i], I can know that which bos is represnented. And. i is comparison result.
    int    signsbd ;
    int    signsbu ;
    Boolcheck(arr, signsbd, signsbu);
    Insertalg(arr, index);
    for (int i = 0; i < 8; ++i) {
        code = (arr[i] == -1) ? (code & (LeftRotate(__7f10fMASK, index[i]))) : (arr[i] == -2) ? (code | (LeftRotate(__701ffMASK, index[i]))) :(code | ((i + 1) << index[i]));
    }

//code filtered 0F
//1 belong case 0xZZZ0ZZZZ,those Z beside 0 left can't be touch, otherwise rule will break, 5 belong 0xZZZZFZZZ, X non 0 and F
    if(( code & __LEVEL1SBDMASK  ) == 0) ++count3 ;
    if(( code & __LEVEL1SBUMASK  ) == (__LEVEL1SBUMASK)) count3=count3+5 ;
//comparecode[j] is rawcode----------//  
    ts.comparecode[j]         = code ;
//comparecode0F[j] is code filtered by algorithm----------//
    if(count3==1){
        bool fg = true;
        for (int i = 0; i < 3; ++i) {
            if(((code&mask[i])>>index[i])==0){
                fg = fg&&(sbt[i]<sbt[3]) ;
            }
        }
        if(fg) ts.comparecode0F[j]  = code ; 
    }
    else if(count3==5){
        bool fg = true;
        for (int i = 5; i < 8; ++i) {
            if(((code&mask[i])>>index[i])==0xF){
                fg = fg&&(sbt[i]<sbt[4]) ;
            }
        }
        if(fg) ts.comparecode0F[j]  = code ; 
    }
    else ts.comparecode0F[j] = 0 ;
    
    delta0X = ts.TriItvCompare0X(fvg, fvg2, fvg3, fvg4, bos1, bos2, bos3, bos4, delta0X, j, count3);
    deltaXF = ts.TriItvCompareXF(fvg, fvg2, fvg3, fvg4, bos1, bos2, bos3, bos4, deltaXF, j, count3);
    if((fvg.namei==ii)&&(j+1==jj)){
        string filename =StringFormat("%s"+"\\testfile.txt", AccountInfoString(ACCOUNT_COMPANY));
        int handle=FileOpen(filename,FILE_WRITE|FILE_TXT);
        string line="";
        string dt;
        string ut;
        datetime t1;
        datetime t2;
        line = StringFormat("bos4=%.0f, bos3=%.0f, bos2=%.0f, bos1=%.0f, ii= %.0f, jj= %.0f, code=%08X%01X", bos4.htfint, bos3.htfint, bos2.htfint, bos1.htfint, ii, jj, code, ts.fvgtype0F[j]) ;
        FileWrite(handle, line);
        t1 = bos4.sbd_t<0? 0 : bos4.sbd_t;
        t2 = bos4.sbu_t<0? 0 : bos4.sbu_t;
        dt = TimeToString(t1, TIME_DATE|TIME_MINUTES);
        ut = TimeToString(t2, TIME_DATE|TIME_MINUTES);
        line = StringFormat("%.5f, %.5f, %s, %s" , bos4.sbd, bos4.sbu, dt, ut) ;
        FileWrite(handle, line);
        t1 = bos3.sbd_t<0? 0 : bos3.sbd_t;
        t2 = bos3.sbu_t<0? 0 : bos3.sbu_t;
        dt = TimeToString(t1, TIME_DATE|TIME_MINUTES);
        ut = TimeToString(t2, TIME_DATE|TIME_MINUTES);
        line = StringFormat("%.5f, %.5f, %s, %s" , bos3.sbd, bos3.sbu, dt, ut) ;
        FileWrite(handle, line);
        t1 = bos2.sbd_t<0? 0 : bos2.sbd_t;
        t2 = bos2.sbu_t<0? 0 : bos2.sbu_t;
        dt = TimeToString(t1, TIME_DATE|TIME_MINUTES);
        ut = TimeToString(t2, TIME_DATE|TIME_MINUTES);
        line = StringFormat("%.5f, %.5f, %s, %s" , bos2.sbd, bos2.sbu, dt, ut) ;
        FileWrite(handle, line);
        t1 = bos1.sbd_t<0? 0 : bos1.sbd_t;
        t2 = bos1.sbu_t<0? 0 : bos1.sbu_t;
        dt = TimeToString(t1, TIME_DATE|TIME_MINUTES);
        ut = TimeToString(t2, TIME_DATE|TIME_MINUTES);
        line = StringFormat("%.5f, %.5f, %s, %s" , bos1.sbd, bos1.sbu, dt, ut) ;
        FileWrite(handle, line);
        if(handle!=INVALID_HANDLE){
            for (int i = 0; i < 8; ++i){
                line = StringFormat("Break Time= %s", sbt_s[i]);
                FileWrite(handle, sbt_s[i]);
            }
        }
        FileClose(handle);
        //ArrayPrint(sbt_s);
    }
    //Print("bos1.htfint: ", bos1.htfint);
    return ts;
}
void BoundTouchCheck(Triset& ts, const BOS& bos1, const int& htfint, const string& symbolname, const int& datasize){
    for (int j=0; j<=htfint; ++j){
        uint code = ts.comparecode0F[j] ;
        double exe= ts.code0FExtreme[j] ;
        if(code!=0 && ((code & __LEVEL1SBUMASK)==__LEVEL1SBUMASK)){//0xZZZZFZZZ
            for(int k=0; k<datasize; k++){
                datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                if(exe==MAXSBU){
                    ts.highfg[j] = false ;
                    break;
                }
                if((iHigh(symbolname,PERIOD_M1,k)>exe) && (temptime>=bos1.sbd_t)){
                    ts.highfg[j] = true ; 
                    //if(i==198)printf("ts.code0FExtreme[%d]= %.4f", i,j,ts.code0FExtreme[j]) ;
                    //if(i==198)printf("iHigh(symbolname,PERIOD_M1,%d)= %.4f", k, iHigh(symbolname,PERIOD_M1,k)) ;
                    break; 
                } 
                else{
                    if(temptime<bos1.sbd_t){
                        ts.highfg[j] = false ;
                        break ; 
                    }
                }
            }
        }
        else if(code!=0 && ((code & __LEVEL1SBDMASK)== 0)){//0xZZZ0ZZZZ
            for(int k=0; k<datasize; k++){
                datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                if((iLow(symbolname,PERIOD_M1,k)<exe)&&(temptime>=bos1.sbu_t)){
                    ts.lowfg[j] = true ; 
                    break;    
                } 
                else{
                    if(temptime<bos1.sbu_t){
                        ts.lowfg[j] = false ;
                        break ; 
                    }
                } 
            }
        }
    }
}
void FvgTouchCheck(Triset& ts, const BOS& bos1, const int& htfint, const string& symbolname, const int& datasze){
    for (int j=0; j<=htfint; ++j){
        uint code = ts.comparecode0F[j] ;
        int  type = ts.fvgtype0F[j]     ;
        double gfvgexe = ts.code0FgFvgExtreme[j];
        double rfvgexe = ts.code0FrFvgExtreme[j];
        if(code!=0){
            if((type==0xF)||(type==0xA)||(type==0xB)||(type==0xC)||(type==0xD)){
                if((code & __LEVEL1SBDMASK) == 0){
                    for(int k=0; k<datasize; k++){
                        datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                        if((iLow(symbolname,PERIOD_M1,k)<=gfvgexe) && (temptime>=bos1.sbu_t)){
                            ts.gfvgfg[j] = true ; 
                            break; 
                        } 
                        else{
                            if(temptime<bos1.sbu_t){
                                ts.gfvgfg[j] = false ;
                                break ; 
                            }
                        } 
                    }
                }
                else{
                    for(int k=0; k<datasize; k++){
                        datetime temptime = iTime(symbolname, PERIOD_M1, k) ;
                        if((iHigh(symbolname,PERIOD_M1,k)>=rfvgexe) && (temptime>=bos1.sbd_t)){
                            ts.rfvgfg[j] = true ; 
                            break;    
                        } 
                        else{
                            if(temptime<bos1.sbd_t){
                                ts.rfvgfg[j] = false ;
                                break ; 
                            }
                        }
                    }
                }
            }
            else continue ;
        }
        
    }
}
#endif
//TimeToString(Vec_rawdata.datadate[i], TIME_MINUTES); useful