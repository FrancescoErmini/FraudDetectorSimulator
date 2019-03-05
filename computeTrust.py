import argparse
import os
import csv
from TrustMan import *
from config import Tools
from EigenTrust import *
from Scenario import Scenario
from TNSLA import *
from Result import *

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--scenario', help="Trace file source directory for the simulation")
	#parser.add_argument('--trustalg', help="Name of trace algoritm EigenTrust or TNSLA")
	#parser.add_argument('--icoop', type=int, help="Intermidiaries cooperation within the trust framework")

	args = parser.parse_args()

	scenario_directory = 'traces/'+args.scenario
	dataset = scenario_directory + '/dataset.hdf5'
	trace_file = scenario_directory + '/traces.csv'



	log_file = scenario_directory + '/INFO.csv'
	#debug_file = scenario_directory+'/rawresult.log'
	#posneg_file = scenario_directory+'/rowfback.log'
	result_file = scenario_directory+'/result.txt'

	
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


	if os.path.isfile(dataset):
		os.remove(dataset)


	with h5py.File(dataset, "a") as f:
		f.create_dataset("fback_matrix", shape=(N,N,2), dtype='uint16')
		f.create_dataset("normal_matrix", shape=(N,N), dtype='uint16')
		f.create_dataset("opinion_matrix", shape=(N,N,4), dtype='uint16')
		f.create_dataset("trust_score", shape=(N,1))




	print('simulation: ' + args.scenario)
	#print('trust alg: ' + args.trustalg)
	print('scenario: ' + str(n_providers) + ' providers,  ' + str(n_intermidiaries) + ' intermidiaries,  ' + str(fraudsters_percentage) + '[%] fradusters')
	print('transactions: ' + str(n_calls) + ' calls,  ' + str(frauds_percentage) + '[%]  call frauds,  ' + str(l_chain) + ' chain length')
	print('cooperation: ' + str(provider_participation) + '[%] providers,  ' + str(intermidiaries_participation) + '[%] intermidiaries')




	 #create an istance of TraceGenerator with the params from cli
	scenario =  Scenario(n_providers=n_providers, 
		n_intermidiaries=n_intermidiaries, 
		fraudsters_percentage=fraudsters_percentage, 
		n_calls=n_calls, 
		frauds_percentage=frauds_percentage,
		l_chain =l_chain,
		provider_participation=provider_participation,
		intermidiaries_participation=intermidiaries_participation,
		dataset=dataset)


	manager = TrustMan(scenario=scenario)

	manager.updateMatrix(infile=trace_file, data_out='fback_matrix')
	

	#if args.trustalg == "EigenTrust":
	#	trust = EigenTrust(scenario=scenario)
	#else:
	trust = TNSLA(scenario=scenario)

	trust.computeTrust(data_in='fback_matrix', data_out='trust_score')

	manager.fraudsterClassifier(data_in='trust_score', outfile=result_file)


	results = Result(scenario=scenario, manager=manager)
	results.store2Csv(scenario_directory+'/trust_score.csv')
	results.printRes()





#print args.file.readlines()
if __name__ == '__main__':
   main()