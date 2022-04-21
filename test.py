import numpy as np

import matplotlib.pyplot as plot
import math
 

# Get x values of the cosine wave

time    = np.arange(0, 2, 0.1);

 

# Amplitude of the cosine wave is cosine of a variable like time

amplitude   = np.cos(time)
amplitude1 = 1 - (time/math.pi)

 

# Plot a cosine wave using time and amplitude obtained for the cosine wave

plot.plot(time, amplitude)
plot.plot(time, amplitude1)

 

# Give a title for the cosine wave plot

plot.title('Cosine estimate')

 

# Give x axis label for the cosine wave plot

plot.xlabel('Angle (Radians)')

 

# Give y axis label for the cosine wave plot

plot.ylabel('Amplitude')

 

# Draw the grid for the graph

plot.grid(True, which='both')

 

plot.axhline(y=0, color='b')

 
plot.legend(["cos(\u03B8)", "1-\u03B8/\u03C0"])
# Display the cosine wave plot

plot.show()