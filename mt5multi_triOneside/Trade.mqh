#ifndef __TRADE_MQH__
#define __TRADE_MQH__

struct Trademark{
	double Entry ;
	double Exit  ;
	double SL    ;
	double TP    ;
	double Lot   ;
	int    OrderType ;
	double MaxDrawdown ;
	int    MaxDuration ;
	int    TradeType   ;
	string Asset       ;
	string Direction   ;
};
struct Tradeset
{
	bool PreFlag ;
	bool TradeFlag;
	int  Algor;
	Trademark Tk  ;
};

class TradeClass{
private:
    Tradeset Tradesets;
public:
	TradeClass();
};
TradeClass::TradeClass:PreFlag(0),TradeFlag(0),Algor(0){}

// Entry Price (Buy Price): The price at which the system will execute a buy order.
// Exit Price (Sell Price): The price at which the system will execute a sell order.
// Stop Loss (SL): A predefined price level at which the system will exit a losing trade to prevent further losses.
// Take Profit (TP): A predefined price level at which the system will exit a winning trade to secure profits.
// Order Size (Lot Size): The volume or quantity of the asset to be traded in each transaction.
// Order Type: The type of order to be executed, such as market order, limit order, stop order, etc.
// Maximum Drawdown: The maximum allowable loss from the peak to a trough of a portfolio, before a new peak is attained.
// Maximum Trade Duration: The maximum time a trade can remain open.
// Trailing Stop: A stop order that moves with the price to lock in profits while minimizing losses.
// Risk Management Parameters: These can include the percentage of the account balance to risk per trade, maximum number of open trades, etc.
// Trade Timing: Specific times or conditions under which trades should be executed.
// Currency Pair or Asset: The specific financial instrument to be traded.
// Trade Direction: Whether the trade is a buy (long) or sell (short)