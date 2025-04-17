import numpy as np
import matplotlib.pyplot as plt

bbr_point = np.array([10.60, 50.14])
scream_point = np.array([10.37, 50.13])
copa_point = np.array([10.84, 50.14])

y_values = [bbr_point[0], scream_point[0], copa_point[0]]  
x_values = [bbr_point[1], scream_point[1], copa_point[1]]  

plt.scatter(x_values, y_values, color='blue', label='Protocols', s=100)

plt.annotate('BBR', (bbr_point[1], bbr_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')
plt.annotate('SCReAM', (scream_point[1], scream_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')
plt.annotate('COPA', (copa_point[1], copa_point[0]), textcoords="offset points", xytext=(0, 10), ha='center')

plt.xlabel('RTT (ms)')
plt.ylabel('Throughput (Mbps)')
plt.title('Congestion Control Protocol Comparison')

plt.xlim(50.125, 50.145)  
plt.ylim(10.3, 11.0)      

plt.legend()
plt.show()
