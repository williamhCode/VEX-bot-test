import matplotlib.pyplot as plt
import numpy as np

with open("positions.txt") as file_in:
    y = []
    for line in file_in:
        y.append(float(line.rstrip('\n')))

x = []
t = 0
for i in range(len(y)):
    x.append(t)
    t += 1/60

plt.plot(x, y)
plt.show()
