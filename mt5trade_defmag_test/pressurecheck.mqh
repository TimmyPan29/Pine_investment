//+-----check pressure or support-----+//
//+-----the goal of this function is for check pressure or support before build s order-----+//
//+I need these argument as following+//
//+if it's a sell ticket, I need the sbu whose price are in the range of the goal sbu's high and the occured time must be advanced of the goal sbu's time, the last is the compared period gotta be higher than goal period. 
//+so that arguments to be compared are goal sbd, goal sbd occured time or goal sbd's high time(gotta discuzz),  
//+step one: check the period
//+step two: check the time
//+step three: check the value.

set a additional limit before sending a pending ticket.
bool CheckPressureOrsupport(Golder& G){
	bool couldpending;
	double ticketsbd;
	double ticketsbu;
	datetime ticketsbdtime;
	datetime ticketsbutime;
	int type;
	for (int i = 0; i < PERIODX4 && G.GD[i][0]!=0; i++) {
		type = G.GD[i][typeidx];
		if(type == 0){
			ticketsbu  = G.GD[i][sbuidx];
			ticketsbut = G.GD[i][sbutimeidx];
			tickethigh = G.GD[i][sbuhighidx];	
			for (int l=i; l < PERIODX4; l++) {
				if(G.GDbos[l][sbutimeidx]<ticketsbutime && (G.GDbos[l][sbuidx]>=ticketsbu && G.GDbos[l][sbuidx]<=tickethigh)){
					couldpending = true ;
				}                        
				else couldpending = false ;				
			}
		}
		else{
			ticketsbd  = G.GD[i][sbdidx];
			ticketsbdt = G.GD[i][sbdtimeidx];
			ticketlow  = G.GD[i][sbdlowidx];	
			for (int l=i; l < PERIODX4; l++) {
				if(G.GDbos[l][sbdtimeidx]<ticketsbdtime && (G.GDbos[l][sbdidx]<=ticketsbd && G.GDbos[l][sbdidx]>=ticketlow)){
					couldpending = true ;
				}                        
				else couldpending = false ;				
			}
		}
	}
	return couldpending ;
}



//+-----modify and monitor the price after building a sell or buy position-----+//
//+take sell position as a example, monitor whether the higer level sbd's price is higher than the goal tp or not and those higher sbd's time must be later than the time of builded postion time. 
//+@ positino time, @tp price @level sbd period, @level sbd price @level sbd time 
add new ticketing indictor: GD.ticketmod
void MonitorAndModifyPos(Golder& G){
	bool ismodified;
	for(int i=0; i<PERIODX4; ++i){
		if(G.GD.ticketing[i] != 2) continue;
		else{
			datetime tpos = PositionGetInteger(G.GD.ticketpos[i], POSITION_TIME);
			double   tp   = PositionGetDouble(G.GD.ticketpos[i], POSITION_TP);
			for(int l=i; i<PERIODX4; ++l){
				if(G.GDbos[l][sbdidx]>tp && G.GDbos[l][sbdtimeidxterm]>tpos){
					trade.modifypos(oldtp <- newtp=G.GDbos[l][sbdidxterm]);
					GD.ticketmod[l] = true ;
					printf("the tp is modified");
				}
			}
		}
	}
}

//+-----我還要多加一個矩陣來讀OANDA的資料 或者我可以先省略這步驟 讓他們兩個交易所分別跑 比對他們做單的signal是否一樣 一樣的話再來進一步分析-----+