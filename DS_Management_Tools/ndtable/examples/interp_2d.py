'''
2d interpolation example
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import NonUniformImage
from ndtable import NDTable

def peaks(x=np.linspace(-3, 3, 49),  y=np.linspace(-3, 3, 49)):
    X, Y = np.meshgrid(x, y)
    Z =  3*(1-X)**2 * np.e**(-(X**2) - (Y+1)**2) - 10*(X/5 - X**3 - Y**5) * np.e**(-X**2-Y**2) - 1/3 * np.e**(-(X+1)**2 - Y**2)
    return X, Y, Z

x = y = np.linspace(-3, 3, 20)
_, _, Z = peaks(x, y)  
table = NDTable(Z, (x, y))

xi = yi = np.linspace(-10, 10, 100)
XI, YI = np.meshgrid(xi, yi)

figure = plt.figure(figsize=(10, 5))
figure.canvas.set_window_title('Extrapolation Methods')

for i, method in enumerate(['hold', 'linear']):
    ZI = table.evaluate((XI, YI), interp='linear', extrap=method)
    ax = figure.add_subplot(1,2,i+1)
    ax.set_title(method)
    im = NonUniformImage(ax)
    im.set_data(xi, yi, ZI)
    im.set_extent((-10, 10, -10, 10))
    ax.images.append(im)

plt.show()
