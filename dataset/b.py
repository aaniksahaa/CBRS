a1 = 1
a2 = 2
sequence = [a1, a2]

# Generate terms up to the 999th term
for n in range(2, 998):
    an = sequence[n-1] * sequence[n-2] - sequence[n-2]
    sequence.append(an)

# The 999th term
a999 = sequence[998]

print(a999)
