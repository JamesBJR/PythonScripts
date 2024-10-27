import numpy as np
import matplotlib.pyplot as plt
from mpmath import mp, mpc

# Set arbitrary precision
mp.dps = 50  # Increase this value for more zoom depth

# Initial parameters
width, height = 800, 800
x_min, x_max = -2.0, 1.0
y_min, y_max = -1.5, 1.5
max_iter = 256
zoom_factor = 0.5  # Amount to zoom each time

def mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter):
    # Create complex grid
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    Z = np.zeros((width, height))

    # Mandelbrot iteration with high precision
    for i in range(width):
        for j in range(height):
            zx, zy = mp.mpf(x[i]), mp.mpf(y[j])
            c = mpc(zx, zy)
            z = c
            for k in range(max_iter):
                if abs(z) > 2.0:
                    Z[i, j] = k
                    break
                z = z * z + c
            else:
                Z[i, j] = max_iter

    return Z

def update_plot(Z):
    plt.imshow(Z.T, cmap='hot', extent=(x_min, x_max, y_min, y_max))
    plt.colorbar()
    plt.title(f"Mandelbrot Set - Zoom Level {1/zoom_factor:.2f}")
    plt.draw()

def onclick(event):
    global x_min, x_max, y_min, y_max, max_iter
    # Get click position in data coordinates
    x_center, y_center = event.xdata, event.ydata
    if x_center is None or y_center is None:
        return

    # Calculate new bounds with high precision
    x_range = (x_max - x_min) * zoom_factor
    y_range = (y_max - y_min) * zoom_factor
    x_min, x_max = mp.mpf(x_center - x_range / 2), mp.mpf(x_center + x_range / 2)
    y_min, y_max = mp.mpf(y_center - y_range / 2), mp.mpf(y_center + y_range / 2)

    # Increase iteration count for more detail as we zoom
    max_iter = int(max_iter * 1.1)

    # Generate and update plot
    Z = mandelbrot(float(x_min), float(x_max), float(y_min), float(y_max), width, height, max_iter)
    plt.clf()  # Clear previous plot
    update_plot(Z)

# Initial plot
plt.figure(figsize=(8, 8))
Z = mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter)
update_plot(Z)

# Set up event handler for mouse click
plt.gcf().canvas.mpl_connect('button_press_event', onclick)
plt.show()
