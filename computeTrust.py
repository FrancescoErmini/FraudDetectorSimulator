import argparse
import os
import csv
import random

from TrustMan import *
from TraceGenerator import *
from config import *
from EigenTrust import *
from Scenario import Scenario
from TNSLA import *
from Result import *
from Dataset import Dataset
from Plot import *

def main():

	

	parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
	#abs params
	parser.add_argument('--providers',  type=int, help="Number of local telco providers" )
	#parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
	#parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
	parser.add_argument('--intermidiaries', type=int, help="Number of intermidiary providers" )
	parser.add_argument('--calls', type=int, help="Number of calls" )
	parser.add_argument('--hops', type=int, help="Numer of hops per call" )

	#percentage params
	parser.add_argument('--fraudsters', type=float, help="Percentage of fraudolent intemidiaraies" )
	parser.add_argument('--frauds', type=float, help="Percentage of fraud calls. " )
	parser.add_argument('--pcoop', type=float, help="Percentage of cooperation provider " )
	parser.add_argument('--icoop', type=float, help="Percentage of cooperation intermidiaries. " )
	parser.add_argument('--cycles', type=int, help="Number of traces to simulate" )

	parser.add_argument('--scenario', help="Name of the simulation directory" )
	parser.add_argument('--useblacklist', dest='blacklist', action='store_true')
	parser.add_argument('--no-useblacklist', dest='blacklist', action='store_false')
	parser.set_defaults(blacklist=True)
	
	args = parser.parse_args()


	

		#create an istance of TraceGenerator with the params from cli
	scenario =  Scenario(n_providers=int(args.providers), 
					n_intermidiaries=int(args.intermidiaries), 
					n_calls=int(args.calls), 
					l_chain = int(args.hops),
					fraudsters_percentage=float(args.fraudsters), 
					frauds_percentage=float(args.frauds),
					provider_participation = int(args.pcoop),
					intermidiaries_participation = int(args.icoop),
					cycles = int(args.cycles),
					blacklist=args.blacklist)

	The idea of ​​accusing a priori honest nodes has been proven to be valid.


	#for simul in range(1):

	print('\n\nstart simulation: ' + args.scenario +'\n')



	#scenario.revenue_termin = 0
	#scenario.revenue_transit = 0
	#scenario.revenue_fraudster = 0 

	#if simul==0:
		#print("no blacklist")
		#scenario.use_blacklist = False
		

	#if simul==1:
		#print("yes blacklist")
		#scenario.use_blacklist = True
		

	

	N = scenario.n_providers + scenario.n_intermidiaries
	cycles = int(args.cycles)
	sources = [x for x in range(0,scenario.n_providers,10)]
	#targets = [(random.randint(200,599)) for x in range(20)]
	step = 1
	targets = [(x+scenario.n_providers) for x in range(0,scenario.n_intermidiaries,step)] #80 targets
	for f in range(scenario.n_fraudsters):
		targets[scenario.n_intermidiaries//step-f-1] = N-f-1
	
	results = np.zeros((cycles,len(targets))) #tmp, cambia col source attenzione!
	revenues = np.zeros((3,cycles))
	days=0


	blacklist_history = []


	for c in range(cycles):

		if scenario.use_blacklist:
			print("it works")



		scenario_directory = 'simulation/' + args.scenario

		trace_file  =  scenario_directory + '/' + str(c) + '/traces.csv'
		#dataset_file = scenario_directory + '/' + str(c) + '/dataset.hdf5'
		result_file = scenario_directory  + '/results/result.txt'

		

		dataset = Dataset(N, scenario_directory, c)
		dataset.destroy()
		dataset.create()



		if (c)%4 == 0 and scenario.use_blacklist:
			#if c > 4: #simulo l'ingresso ritardato
			
			scenario.reset_blacklist()


		
		#print("deeeebuggg")
		#print(blacklist_history)


		traceGenerator = TraceGenerator(scenario=scenario)
		traceGenerator.createCsv(file=trace_file)

		
		
		



		manager = TrustMan(scenario=scenario, dataset=dataset)

		manager.createFeedbackMatrix(infile=trace_file)
		#print("tot calls managed by fraudsters: good:" + str(manager.disguised_behaviour) + " and bad:" + str(manager.malicious_behaviour))
		#print("PREEEEE")
		#results.printFeedback()
		manager.updateFeedbackMatrix(scenario_directory=scenario_directory, cycle=c)

		#trust = EigenTrust(scenario=scenario)

		result = Result(scenario=scenario,dataset=dataset, manager=manager)
		days+=result.calcDelay()
		print("\n\nPERIOD: "+str(days))
		print("Blacklisted operators are:")
		blacklist_history.append(scenario.blacklist[:])
		print(scenario.blacklist)

		#result.printFeedback(targets)

		trust = TNSLA(scenario=scenario, dataset=dataset)
		#trust.initialize()

		
		
		for i in range(len(targets)):
			Tools.printProgress( i, len(targets))
			"""
			if general:

				results[c][i] = trust.computeTrust(targets[i])
			else:
			"""
			for j in range(len(sources)):
				if scenario.isCoopProvider(sources[j]):
					results[c][i] = trust.computeTrust2(sources[j], targets[i])

					#print("\nTrust from "+str(sources[j])+" to "+str(targets[i])+" at period "+str(c)+"th is "+str(results[c][i]))
					res = result.fraudsterClassifier2(targets[i], results[c][i])
					if res and scenario.use_blacklist: #is Fraudster
						scenario.push_in_blacklist(targets[i])
					'''
					if not res and scenario.use_blacklist and scenario.is_blacklisted(targets[i]):
						scenario.pull_from_blacklist(targets[i])
					'''






						
			
		'''
		else:
			for i in range(len(targets)):
				Tools.printProgress( i, len(targets))
				results[c][i] = trust.computeTrust(targets[i])
				result.fraudsterClassifier2(targets[i], results[c][i])

			r = result.printTrustAvg(targets, results[c])
			honests_score_avg[c] = r[0]
			fraudsters_score_avg[c] = r[1]
		'''

				
			
		result.printRes()
		scenario.revenue_termin += manager.revenue_termin
		scenario.revenue_transit += manager.revenue_transit
		scenario.revenue_fraudster += manager.revenue_fraudster

		revenues[0][c]=scenario.revenue_termin #/scenario.n_providers
		revenues[1][c]=scenario.revenue_transit #/scenario.n_honests
		revenues[2][c]=scenario.revenue_fraudster #/scenario.n_fraudsters

			


		print("REVENUES")
		print("termin"+str(revenues[0][c]))
		print("transit"+str(revenues[1][c]))
		print("fraudster"+str(revenues[2][c]))

	plot = Plot(scenario=scenario)


	#plot.plotDetectResult(blacklist_history, result.getFraudBehaviour())

	#if not general:
	plot.plotPie(result)
	#threshold = result.calcThreshold(days)
	
	#plot.plotBars2(revenues, case=simul)
	#plot.plotBars3(revenues, threshold=threshold,days=days,case=simul)
	#else:
		#plot.statistics(result=result)
		#plot.trustScore(honests_score_avg,fraudsters_score_avg, result.getFraudBehaviour())
#plot.plotEnd(days)
'''
def saveSetting(self, sim_root):
if os.path.isfile(sim_root+'/info/sim_params.csv'):
	os.remove(sim_root+'/info/sim_params.csv')

with open(sim_root+'/info/sim_params.csv', mode='w') as info:
	writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["providers", "intermidiaries","fraudsterspercentage", "l_chain","calls","fraudspercentage", "n_coop_providers", "n_coop_intermidiaries", "fraudster_camuflage", "simmetry_strategy", "pretrust_strategy"])
	writer.writerow([scenario.n_providers, scenario.n_intermidiaries, scenario.fraudsters_percentage, scenario.l_chain, scenario.n_calls, scenario.frauds_percentage, scenario.provider_participation, scenario.intermidiaries_participation, TrustConfig.fraudsters_camouflage, TrustConfig.simmetry_strategy, TrustConfig.pretrust_strategy])
'''


#print args.file.readlines()
if __name__ == '__main__':
   main()