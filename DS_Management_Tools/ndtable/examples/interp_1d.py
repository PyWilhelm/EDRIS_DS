'''
Interpolation Methods
'''
import numpy as np
import matplotlib.pyplot as plt
from ndtable import NDTable

x = np.linspace(0, 2 * np.pi, 6)
y = np.sin(x)
 
ndtable = NDTable(y, (x,))

xi = np.linspace(0, 2 * np.pi, 1000)
dxi = np.ones(1000)

figure = plt.figure()
figure.canvas.set_window_title('Interpolation Methods')

for i, method in enumerate(['nearest', 'linear', 'akima']):
    yi = ndtable.evaluate((xi,), interp=method)
    dyi = ndtable.evaluate_derivative((xi,), (dxi,), interp=method)
    ax = figure.add_subplot(3,1,i+1)
    ax.set_title(method)
    ax.plot(xi, yi, 'b')
    ax.plot(xi, dyi, 'r')
    ax.plot(x, y, 'or')
    ax.set_xlim([-1, 2*np.pi+1])
    ax.set_ylim([-1.5, 1.5])

figure.tight_layout()

plt.show()
