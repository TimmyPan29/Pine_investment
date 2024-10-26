import torch

# Check if CUDA is available; if not, fall back to CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Example close prices (replace with your actual data)
close_prices = [1.2, 1.3, 1.4, 1.5]

# Print the first close price
print(f"{close_prices[0]}")

# Convert close prices to a PyTorch tensor and move to the chosen device (GPU or CPU)
close_prices_tensor = torch.tensor(close_prices, dtype=torch.float32, device=device)

# Example tensors for computation on the chosen device
a = torch.randn(10000, 10000, device=device)
b = torch.randn(10000, 10000, device=device)

# Perform matrix multiplication on the chosen device
c = torch.matmul(a, b)

# Transfer the result back to CPU and convert to a list
result = c.cpu().numpy().tolist()

# Example: Print the first row of the result
print(f"{result[0]}")

# Optionally, you can work with the result in MT5 here