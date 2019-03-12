import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from config import TraceConfig,TNSLAsettings
import random
#from matplotlib.colors import LinearSegmentedColormap

class Plot():

	def __init__(self, scenario):
		super(Plot, self).__init__()
		self.scenario = scenario

	def nodeColor(self, index):


		red_colors = ['red','orangered','crimson','firebrick','tomato','indianred','lightcoral']
		green_colors = ['green','forestgreen','limegreen','darkgreen','mediumseagreen','seagreen','springgreen','lime','limegreen']
		if self.scenario.isFraudster(index):
			return red_colors[random.randint(0,6)]
		else:
			return green_colors[random.randint(0,8)]

		

	def transitivity(self, targets, results):	

		
		# Make a data frame call_per_cycle, current_cycle, call_rate):
		#x = [i*TraceConfig.cycles2days(self.scenario.n_calls) for i in range(self.scenario.cycles)]
		x = [i for i in range(self.scenario.cycles)]

		df=pd.DataFrame({'x': x, 'n1': results[:,0], 'n2': results[:,1], 'n3': results[:,2], 'n4': results[:,3]})
		# style
		plt.style.use('seaborn')#-darkgrid
		# create a color palette
		palette = plt.get_cmap('Set1')
		# multiple line plot
		num=0
		for column in df.drop('x', axis=1):
			
			plt.plot(df['x'], df[column], marker='', color=self.nodeColor(targets[num]), linewidth=1, alpha=0.9, label=column)
			num+=1
		plt.plot([0., self.scenario.cycles], [0.5, 0.5], "k--")
		plt.text(self.scenario.cycles-2, 0.37, 'fraudster', fontsize=12)
		plt.plot([0., self.scenario.cycles], [TNSLAsettings.trustee_score, TNSLAsettings.trustee_score], "k--")
		plt.text(self.scenario.cycles-2, TNSLAsettings.trustee_score+0.01, 'honests', fontsize=12)
		# Add legend
		#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=4, ncol=4, mode="expand", borderaxespad=0.)
		plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, fancybox=True,ncol=4, borderaxespad=0.)

		#plt.legend(loc=2, bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
		# Add titles
		#plt.title("Trust transitivity cases", loc='left', fontsize=12, fontweight=0, color='black')
		plt.xlabel("cycles")
		plt.ylabel("trust score")
		plt.show()		