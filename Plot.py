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
		plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.1), shadow=True, fancybox=True,ncol=4, borderaxespad=0.)

		#plt.legend(loc=2, bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
		# Add titles
		#plt.title("Trust transitivity cases", loc='left', fontsize=12, fontweight=0, color='black')
		plt.xlabel("cycles")
		plt.ylabel("trust score")
		plt.show()	

	def statistics(self, result):
		"""
		self.fraudsters_detection = 0
		self.fraudsters_detection_suspect = 0
		self.fraudsters_detection_error = 0
		self.fraudsters_detection_missing = 0

		self.honests_detection = 0
		self.honests_detection_suspect = 0
		self.honests_detection_error  = 0
		self.honests_detection_missing = 0
		"""

		# Data to plot
		plt.figure(1)
		plt.title("fraudsters detection statistics")
		plt.text(-1, -1.2, 'fraud behaviour: '+str(result.getFraudBehaviour()), fontsize=12)
		
		labels = 'detected', 'suspected', 'errors', 'missed'
		sizes = [result.fraudsters_detection, result.fraudsters_detection_suspect, result.fraudsters_detection_error, result.fraudsters_detection_missing]
		colors = ['yellowgreen', 'gold', 'lightcoral', 'lightskyblue']
		patches, texts = plt.pie(sizes, colors=colors, shadow=False, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()

		plt.figure(2)
		plt.title("honests detection statistics")
		plt.text(-1, -1.2, 'fraud behaviour: '+str(result.getFraudBehaviour()), fontsize=12)

		sizes = [result.honests_detection, result.honests_detection_suspect, result.honests_detection_error, result.honests_detection_missing]
		colors = ['yellowgreen', 'gold', 'lightcoral', 'lightskyblue']
		patches, texts = plt.pie(sizes, colors=colors, shadow=False, startangle=90)
		plt.legend(patches, labels, loc="best")
		plt.axis('equal')
		plt.tight_layout()


		plt.show()

	def trustScore(self, honests_score_avg, fraudsters_score_avg,fraudBehaviour):
		N = len(honests_score_avg)
		ind = np.arange(N)  # the x locations for the groups
		width = 0.9   # the width of the bars
		fig, ax = plt.subplots()
		rects1 = ax.bar(ind-width/2, honests_score_avg, width, color='green')
		rects2 = ax.bar(ind+width/2, fraudsters_score_avg, width, color='red')
		#rects4 = ax.bar(ind+2*width, pFalsenegative, width, color='tomato', yerr=2)
		#rects5 = ax.bar(ind+3*width, fraudRevenuePercentage, width, color='r', yerr=3)
		ax.set_ylabel('reputation score')
		ax.set_xlabel('cycles')
		#ax.set_title('global repution')
		ax.legend((rects1[0], rects2[0]), ('honests', 'fraudsters'), bbox_to_anchor=(1.0,1.0))
		plt.plot([-width, N-1+width], [0.5, 0.5], "k--")
		plt.plot([-width, N-1+width], [TNSLAsettings.trustee_score, TNSLAsettings.trustee_score], "k--")
		plt.text(0, 1.1, 'fraud behaviour: '+str(fraudBehaviour), fontsize=12)
		plt.tight_layout()
		plt.show()

	def plotPie(self, result):

		detect = result.fraudsters * 100.0 / result.fraudsters_tot
		suspect = result.suspected_fraudsters * 100.0 / result.fraudsters_tot
		miss = result.unknown_fraudsters * 100.0 / result.fraudsters_tot
		fn = result.falsenegative * 100.0 / result.fraudsters_tot
		fp = result.falsepositive * 100.0 / result.honests_tot

		plt.figure(1)
		plt.title("Detection Stat")
		plt.text(-0.7,-1.2,str(result.scenario.provider_participation)+"% providers, "+str(result.scenario.intermidiaries_participation)+"% intermidiaries",fontsize=11)

		#plt.text(-1, -1.2, 'fraud behaviour: '+str(result.getFraudBehaviour()), fontsize=12)

		labels = 'detect','suspect', 'fn','fp', 'miss'
		sizes = [detect, suspect, fn, fp, miss]
		colors = ['yellowgreen', 'gold', 'lightcoral','crimson','lightskyblue']
		#patches, texts = plt.pie(sizes, colors=colors, shadow=False, startangle=90)
		#plt.legend(patches, labels, loc="best")
		# Plot
		labelspp = ['{0} - {1:1.2f} %'.format(i,j) for i,j in zip(labels, sizes)]

		patches, texts = plt.pie(sizes, colors=colors, pctdistance=1.1, shadow=False, startangle=90)
		plt.legend(patches, labelspp, loc="upper right", bbox_to_anchor=(1., 1.),fontsize=10)
		#plt.text(0, 1.1, 'fraud behaviour: '+str(fraudBehaviour), fontsize=12)
		plt.axis('equal')
		plt.tight_layout()
		plt.show()

	def plotBars(self, revenues):

		N = self.scenario.cycles
		ind = np.arange(N)  # the x locations for the groups
		width = 0.3   # the width of the bars
		fig, ax = plt.subplots()
		rects1 = ax.bar(ind+width*0, revenues[0], width, color='yellowgreen', yerr=0)
		rects2 = ax.bar(ind+width*1, revenues[1], width, color='lightskyblue', yerr=1)
		rects3 = ax.bar(ind+2*width, revenues[2], width, color='lightcoral', yerr=2)
		#rects5 = ax.bar(ind+3*width, fraudRevenuePercentage, width, color='r', yerr=3)
		ax.set_ylabel('profits')
		ax.set_xlabel('cycles')
		#ax.set_title('global repution')
		ax.legend((rects1[0], rects2[0], rects3[0]), ('termin', 'transit','fraudsters'), bbox_to_anchor=(1.0,1.0))
		#plt.plot([-width, N-1+width], [0.5, 0.5], "k--")
		#plt.plot([-width, N-1+width], [TNSLAsettings.trustee_score, TNSLAsettings.trustee_score], "k--")
		#plt.text(0, 1.1, 'fraud behaviour: '+str(fraudBehaviour), fontsize=12)
		plt.tight_layout()
		plt.show()

	def plotBars2(self, revenues):
		x = [i for i in range(self.scenario.cycles)]

		df=pd.DataFrame({'x': x, 'Termin': revenues[0,:], 'Transit': revenues[1,:], 'Fraud': revenues[2,:]})
		# style
		#plt.style.use('seaborn')#-darkgrid
		# create a color palette
		palette = plt.get_cmap('Set1')
		# multiple line plot
		num=0
		for column in df.drop('x', axis=1):
			
			plt.plot(df['x'], df[column], marker='', color=self.getColor(num), linewidth=2, alpha=0.9, label=column)
			num+=1

		plt.legend(loc='bottom center',ncol=3, borderaxespad=0.)
		#plt.legend(loc=2, bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
		# Add titles
		#plt.title("Trust transitivity cases", loc='left', fontsize=12, fontweight=0, color='black')
		plt.xlabel("cycles")
		plt.ylabel("absolute revenues")
		#plt.tight_layout()
		plt.show()

	def getColor(self, num):
		#colors = ['yellowgreen', 'gold', 'lightcoral', 'lightskyblue']
		
		if num == 0:
			return 'green' #termin
		
		if num == 1:
			return 'blue' #transit

		if num == 2:
			return 'red' #fraudster




