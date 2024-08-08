import MetaTrader5 as mt5
import torch
import torch_directml

# Initialize MT5
if not mt5.initialize():
    print("initialize() failed")
    mt5.shutdown()

# Get the closing prices of a specific symbol
symbol = "EURUSD"
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 500000)
close_prices = [rate[0] for rate in rates]
print(f"{close_prices[0]}")
# Check if GPU is available
# device = torch.device(torch_directml.device(0) if torch_directml.is_available() else "cpu")

# # Convert close prices to a PyTorch tensor and move to GPU
# close_prices_tensor = torch.tensor(close_prices, dtype=torch.float32, device=device)
# # Example tensors for computation
# a = torch.randn(10000, 10000, device=device)
# b = torch.randn(10000, 10000, device=device)

# # Perform computation on GPU
# c = torch.matmul(a, b)

# # Example: Transfer result back to CPU and convert to a list
# result = c.cpu().numpy().tolist()

# # Do something with the result in MT5
# # For example, print the first row of the result
# print(f"{result[0]},{a},{b}")
mt5.shutdown()
