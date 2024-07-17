def adjust_H_NLMS(cnt_initial, H_initial, desired_output=1000, mu=0.01, max_iterations=1435, tolerance=0.01):
    cnt = cnt_initial
    H = H_initial
    i = 0

    for iteration in range(max_iterations):
        cnt = (cnt * (i + 1)) * H
        error = desired_output - cnt
        normalization_factor = (cnt * (i + 1)) ** 2
        
        if normalization_factor != 0:
            H = H + (mu * error) / normalization_factor
        
        print(f"Iteration {iteration + 1}: error {error}, cnt: {cnt}, H: {H}")
        
        if abs(error) < tolerance:
            break
        
        i += 1  # Increment i for each iteration
    
    return H, cnt

# Example usage
H_initial = 1  # initial constant H
cnt_initial = 998  # initial cnt value

H_adjusted, final_cnt = adjust_H_NLMS(cnt_initial, H_initial)

print(f"Adjusted H: {H_adjusted}")
print(f"Final cnt: {final_cnt}")
