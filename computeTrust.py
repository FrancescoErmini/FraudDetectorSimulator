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

	args = parser.parse_args()

	print('\n\nstart simulation: ' + args.scenario +'\n')
	#create an istance of TraceGenerator with the params from cli
	scenario =  Scenario(n_providers=int(args.providers), 
						n_intermidiaries=int(args.intermidiaries), 
						n_calls=int(args.calls), 
						l_chain = int(args.hops),
						fraudsters_percentage=float(args.fraudsters), 
						frauds_percentage=float(args.frauds),
						provider_participation = int(args.pcoop),
						intermidiaries_participation = int(args.icoop),
						cycles = int(args.cycles))

	scenario.printDetails()

	general = False

	N = scenario.n_providers + scenario.n_intermidiaries
	cycles = int(args.cycles)

	sources = [x for x in range(0,scenario.n_providers,10)]
	#targets = [(random.randint(200,599)) for x in range(20)]
	step = 1
	targets = [(x+scenario.n_providers) for x in range(0,scenario.n_intermidiaries,step)] #80 targets
	for f in range(scenario.n_fraudsters):
		targets[scenario.n_intermidiaries//step-f-1] = N-f-1
	

	"""
	
	if general:
		targets = [(x+scenario.n_providers) for x in range(scenario.n_intermidiaries)]
	"""
		

	#matrix cycles x targets 
	results = np.zeros((cycles,len(targets))) #tmp, cambia col source attenzione!
	



	honests_score_avg = np.zeros(cycles)
	fraudsters_score_avg = np.zeros(cycles)

	revenues = np.zeros((3,cycles))

	#àscenario.fullfill_blacklist()


	for c in range(cycles):


		scenario_directory = 'simulation/' + args.scenario

		trace_file  =  scenario_directory + '/' + str(c) + '/traces.csv'
		#dataset_file = scenario_directory + '/' + str(c) + '/dataset.hdf5'
		result_file = scenario_directory  + '/results/result.txt'

		dataset = Dataset(N, scenario_directory, c)
		dataset.destroy()
		dataset.create()



		if c%2 == 0 and TrustConfig.use_tmp_blacklist:
			#if c > 4: #simulo l'ingresso ritardato
			scenario.reset_blacklist()

		print("Blacklisted operators are:")
		print(scenario.blacklist)

		traceGenerator = TraceGenerator(scenario=scenario)
		traceGenerator.createCsv(file=trace_file)

		
		
		



		manager = TrustMan(scenario=scenario, dataset=dataset)

		manager.createFeedbackMatrix(infile=trace_file)
		print("tot calls managed by fraudsters: good:" + str(manager.disguised_behaviour) + " and bad:" + str(manager.malicious_behaviour))
		#print("PREEEEE")
		#results.printFeedback()
		manager.updateFeedbackMatrix(scenario_directory=scenario_directory, cycle=c)

		#trust = EigenTrust(scenario=scenario)

		result = Result(scenario=scenario,dataset=dataset, manager=manager)

		#result.printFeedback(targets)

		trust = TNSLA(scenario=scenario, dataset=dataset)
		#trust.initialize()

		
		if not general:
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
						if res and TrustConfig.use_tmp_blacklist: #is Fraudster
							scenario.push_in_blacklist(targets[i])



						
			

		else:
			for i in range(len(targets)):
				Tools.printProgress( i, len(targets))
				results[c][i] = trust.computeTrust(targets[i])
				result.fraudsterClassifier2(targets[i], results[c][i])

			r = result.printTrustAvg(targets, results[c])
			honests_score_avg[c] = r[0]
			fraudsters_score_avg[c] = r[1]

				
			
		result.printRes()
		revenues[0][c]=scenario.revenue_termin//(scenario.n_providers//2)
		revenues[1][c]=scenario.revenue_transit//scenario.n_intermidiaries
		revenues[2][c]=scenario.revenue_fraudster//scenario.n_fraudsters

			


		print("REVENUES")
		print("termin"+str(revenues[0][c]))
		print("transit"+str(revenues[1][c]))
		print("fraudster"+str(revenues[2][c]))

	plot = Plot(scenario=scenario)

	if not general:
		#plot.plotPie(result)
		plot.plotBars2(revenues)
	else:
		#plot.statistics(result=result)
		plot.trustScore(honests_score_avg,fraudsters_score_avg, result.getFraudBehaviour())

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