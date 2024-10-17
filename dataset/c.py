import sympy as sp

# Define the given number
given_number = 350

# Find the smallest integer n such that 350 + n is a perfect square
n = 1
while True:
    candidate = given_number + n
    if sp.is_square(candidate):
        break
    n += 1

# Print the result
print(n)