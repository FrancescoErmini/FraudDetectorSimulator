import argparse
import os
import csv
from TrustMan import *
from TraceGenerator import *
from config import Tools
from EigenTrust import *
from Scenario import Scenario
from TNSLA import *
from Result import *
from Dataset import Dataset

def main():

	

	parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
	#abs params
	parser.add_argument('--providers', metavar='N', type=int, help="N - total number of local telco providers" )
	#parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
	#parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
	parser.add_argument('--intermidiaries',type=int, help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
	parser.add_argument('--calls', type=int, help="N - total number of calls. F - number of estimated fraud calls" )
	parser.add_argument('--hops', type=int, help="Average hops per call" )

	#percentage params
	parser.add_argument('--fraudsters', type=float, help="Percentage of fraudolent intemidiaraies, estimated fraudsters providers" )
	parser.add_argument('--frauds', type=float, help="Percentage of fraud calls. " )
	parser.add_argument('--pcoop', type=float, help="Percentage of cooperation provider " )
	parser.add_argument('--icoop', type=float, help="Percentage of cooperation intermidiaries. " )

	parser.add_argument('--scenario', help="Name of the simulation directory" )
	parser.add_argument('--cycles', type=int, help="Number of different traces" )

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
						intermidiaries_participation = int(args.icoop))
	scenario.printDetails()


	N = scenario.n_providers + scenario.n_intermidiaries
	cycles = int(args.cycles)
	for c in range(cycles):

		scenario_directory = 'simulation/' + args.scenario

		trace_file  =  scenario_directory + '/' + str(c) + '/traces.csv'
		#dataset_file = scenario_directory + '/' + str(c) + '/dataset.hdf5'
		result_file = scenario_directory  + '/' + str(c) +  '/result.txt'

		dataset = Dataset(N, scenario_directory, c)
		dataset.destroy()
		dataset.create()

		traceGenerator = TraceGenerator(scenario=scenario)
		traceGenerator.createCsv(file=trace_file)


		manager = TrustMan(scenario=scenario, dataset=dataset)

		results = Result(scenario=scenario, dataset=dataset, manager=manager)
		manager.createFeedbackMatrix(infile=trace_file)
		print("PREEEEE")
		results.printFeedback()
		manager.updateFeedbackMatrix(scenario_directory=scenario_directory, cycle=c)
		print("POST")
		results.printFeedback()

		#trust = EigenTrust(scenario=scenario)
	
		trust = TNSLA(scenario=scenario, dataset=dataset)
		trust.initialize()

		t=trust.computeTrust2(1, 598)#206

		print("trust AB: "  + str(t))

		#manager.fraudsterClassifier(data_in='trust_score', outfile=result_file)


		#
		#results.store2Csv(scenario_directory+'trust_score.csv')
		#results.printTrustScores('trust_score')
		#results.printFeedback()
		#results.printRes()
		#results.storeRes(result_file)





#print args.file.readlines()
if __name__ == '__main__':
   main()