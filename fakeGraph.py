
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def main():

frauds_detection = []
fraudsters_detection = []
fraudsters_detection_error = []
fraudsters_detection_missing = []

N = 4
ind = np.arange(N)  # the x locations for the groups
width = 0.2    # the width of the bars
std = [0 for s in range(N)]



fig, ax = plt.subplots()
#rects1 = ax.bar(ind, fp_ref, width, color='black', yerr=std)
rects2 = ax.bar(ind+0*width, frauds_detection, width, color='darkred', yerr=std)
rects3 = ax.bar(ind+1*width, fraudsters_detection, width, color='firebrick', yerr=std)
rects4 = ax.bar(ind+2*width, fraudsters_detection_error, width, color='tomato', yerr=std)
rects5 = ax.bar(ind+3*width, fraudsters_detection_missing, width, color='r', yerr=std)

# add some text for labels, title and axes ticks

ax.set_ylabel('outcomes [%]')
ax.set_xlabel('providers partial cooperation')
ax.set_title('Fraudsters detection by varing frauds detection')
#ax.set_xticks(ind+width/4)
#ax.set_xticklabels(('G1', 'G2'))

ax.legend((rects2[0], rects3[0], rects4[0],rects5[0] ), ('frauds det.', 'fraudsters det.','error det.','missing det.'))
'''



if __name__ == '__main__':
	main()