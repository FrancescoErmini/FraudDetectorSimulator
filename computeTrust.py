import argparse
import os
import csv
from TrustMan import *
from config import Tools
from EigenTrust import *

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--scenario', help="Trace file source directory for the simulation")
	parser.add_argument('--pcoop', type=int, help="Providers cooperation percentage within the trust framework")
	parser.add_argument('--icoop', type=int, help="Intermidiaries cooperation within the trust framework")

	args = parser.parse_args()

	scenario_directory = 'traces/'+args.scenario
	log_file = scenario_directory + '/INFO.csv'
	trace_file = scenario_directory + '/traces.csv'

	with open(log_file, 'r') as f:
		reader = csv.reader(f)
		log = list(reader)[1]


	n_providers=log[0]
	n_intermidiaries=log[1]
	fraudsters_percentage=log[2]
	l_chain = log[3]
	n_calls=log[4]
	frauds_percentage=log[5]

	provider_participation=args.pcoop
	intermidiaries_participation=args.icoop

	N=int(n_providers)+int(n_intermidiaries)


	print('simulation: ' + args.scenario)
	print('scenario: ' + str(n_providers) + ' providers,  ' + str(n_intermidiaries) + ' intermidiaries,  ' + str(fraudsters_percentage) + '[%] fradusters')
	print('transactions: ' + str(n_calls) + ' calls,  ' + str(frauds_percentage) + '[%]  call frauds,  ' + str(l_chain) + ' chain length')
	print('cooperation: ' + str(provider_participation) + '[%] providers,  ' + str(intermidiaries_participation) + '[%] intermidiaries')



	if os.path.isfile(scenario_directory+'/dataset.hdf5'):
		os.remove(scenario_directory+'/dataset.hdf5')

	manager = TrustMan(providers=n_providers, intermidiaries=n_intermidiaries, fraudsters_percentage=fraudsters_percentage, l_chain=l_chain,
		calls=n_calls, frauds_percentage=frauds_percentage, provider_participation=provider_participation, intermidiaries_participation=intermidiaries_participation)

	manager.updateMatrix(scenario_directory)

	trust = EigenTrust(int(n_providers), int(n_intermidiaries), int(provider_participation), int(intermidiaries_participation))
	
	trust.computeTrust(scenario_directory)





#print args.file.readlines()
if __name__ == '__main__':
   main()