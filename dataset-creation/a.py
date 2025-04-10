import time

# Record start time
start_time = time.perf_counter()

# Your code block here
for i in range(1000000):
    x = i * i

# Record end time
end_time = time.perf_counter()

# Calculate duration in seconds
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.4f} seconds")