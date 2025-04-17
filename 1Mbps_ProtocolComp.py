import numpy as np
import matplotlib.pyplot as plt

bbr_point = np.array([200.79, 1.0])
scream_point = np.array([200.59, 1.0])
copa_point = np.array([202.30, 1.0])

y_values = [bbr_point[0], scream_point[0], copa_point[0]]  
x_values = [bbr_point[1], scream_point[1], copa_point[1]] 

# Create the scatter plot
plt.scatter(x_values, y_values, color='blue', label='Protocols', s=100)

plt.annotate('BBR', (bbr_point[1], bbr_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')
plt.annotate('SCReAM', (scream_point[1], scream_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')
plt.annotate('COPA', (copa_point[1], copa_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')

plt.xlabel('RTT (ms)')
plt.ylabel('Throughput (Mbps)')
plt.title('Congestion Control Protocol Comparison')

plt.xlim(0.8, 1.2)  
plt.ylim(199, 203)      

plt.legend()
plt.show()
