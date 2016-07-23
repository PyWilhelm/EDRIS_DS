'''
Extrapolation methods
'''
import numpy as np
import matplotlib.pyplot as plt
from ndtable import NDTable

x = np.array([0, 1, 2, 3])
y = np.array([-1.5, -0.5, 0.5, 1.5])

table = NDTable(y, (x,))

xi = np.linspace(-4, 7, 1000)

figure = plt.figure()
figure.canvas.set_window_title('Extrapolation Methods')

for i, method in enumerate(['hold', 'linear']):
    yi = table.evaluate((xi,), interp='linear', extrap=method)
    ax = figure.add_subplot(2,1,i+1)
    ax.set_title(method)
    ax.plot(xi, yi, 'b')
    ax.plot(x, y, 'or')
    ax.set_xlim([-4,7])
    ax.set_ylim([-5,5])

figure.tight_layout()

plt.show()
