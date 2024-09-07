// // 初始化函數
// int OnInit()
// {
//   // 設置EA初始化時的邏輯
//   Print("EA initialized.");
//   return INIT_SUCCEEDED;
// }

// // 去初始化函數
// void OnDeinit(const int reason)
// {
//   // 設置EA解除初始化時的邏輯
//   Print("EA deinitialized.");
// }

// // 每當價格變動時調用的主邏輯函數
// void OnTick()
// {
//   // 檢查是否有未平倉的買單
//   if(!HasOpenBuyOrders())
//   {
//     // 如果沒有未平倉買單，則下單買入
//     OpenBuyOrder();
//   }
// }

// // 檢查是否有未平倉的買單
// bool HasOpenBuyOrders()
// {
//   for(int i = PositionsTotal() - 1; i >= 0; i--)
//   {
//     if(PositionSelect(i))
//     {
//       if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY && PositionGetString(POSITION_SYMBOL) == Symbol())
//       {
//         return true;
//       }
//     }
//   }
//   return false;
// }

// // 開立買單
// void OpenBuyOrder()
// {
//   double price = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
//   double sl = price - stop_loss * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
//   double tp = price + take_profit * SymbolInfoDouble(Symbol(), SYMBOL_POINT);

//   int retries = 0;
//   while (retries < max_retries)
//   {
//     if(trade.Buy(lot_size, Symbol(), price, sl, tp, "SimpleEA Buy Order"))
//     {
//       Print("Buy order opened successfully.");
//       return;
//     }
//     else
//     {
//       int error_code = trade.ResultRetcode();
//       Print("Error opening order: ", error_code);
//       if (error_code == 10027) // Trade context is busy
//       {
//         retries++;
//         Sleep(1000); // 等待一秒鐘後重試
//       }
//       else
//       {
//         break; // 其他錯誤，不重試
//       }
//     }
//   }
// }
