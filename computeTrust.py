import argparse
import os
import csv
from TrustMan import *
from config import Tools
from EigenTrust import *
from Scenario import Scenario
from TNSLA import *

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--scenario', help="Trace file source directory for the simulation")
	#parser.add_argument('--pcoop', type=int, help="Providers cooperation percentage within the trust framework")
	#parser.add_argument('--icoop', type=int, help="Intermidiaries cooperation within the trust framework")

	args = parser.parse_args()

	scenario_directory = 'traces/'+args.scenario
	log_file = scenario_directory + '/INFO.csv'
	trace_file = scenario_directory + '/traces.csv'
	matrix_file = scenario_directory + '/dataset.hdf5'
	debug_file = scenario_directory+'/rawresult.log'
	posneg_file = scenario_directory+'/rowfback.log'
	results_file = scenario_directory+'/results.csv'

	
	with open(log_file, 'r') as f:
		reader = csv.reader(f)
		log = list(reader)[1]



	n_providers=int(log[0])
	n_intermidiaries=int(log[1])
	fraudsters_percentage=int(log[2])
	l_chain = int(log[3])
	n_calls= int(log[4])
	frauds_percentage= int(log[5])

	provider_participation= int(log[6])
	intermidiaries_participation= int(log[7])

	N=n_providers+n_intermidiaries


	print('simulation: ' + args.scenario)
	print('scenario: ' + str(n_providers) + ' providers,  ' + str(n_intermidiaries) + ' intermidiaries,  ' + str(fraudsters_percentage) + '[%] fradusters')
	print('transactions: ' + str(n_calls) + ' calls,  ' + str(frauds_percentage) + '[%]  call frauds,  ' + str(l_chain) + ' chain length')
	print('cooperation: ' + str(provider_participation) + '[%] providers,  ' + str(intermidiaries_participation) + '[%] intermidiaries')


	if os.path.isfile(matrix_file):
		os.remove(matrix_file)



	 #create an istance of TraceGenerator with the params from cli
	scenario =  Scenario(n_providers=n_providers, 
		n_intermidiaries=n_intermidiaries, 
		fraudsters_percentage=fraudsters_percentage, 
		n_calls=n_calls, 
		frauds_percentage=frauds_percentage,
		l_chain =l_chain,
		provider_participation=provider_participation,
		intermidiaries_participation=intermidiaries_participation)


	manager = TrustMan(scenario=scenario)

	manager.updateMatrix(infile=trace_file, outfile=matrix_file, logfile=posneg_file)

	#trust = EigenTrust(scenario=scenario)
	trust = TNSLA(scenario=scenario)
	trust.computeTrust(infile=matrix_file, outfile=results_file)





#print args.file.readlines()
if __name__ == '__main__':
   main()