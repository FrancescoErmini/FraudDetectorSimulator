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
from Plot import *

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
						intermidiaries_participation = int(args.icoop),
						cycles = int(args.cycles))

	scenario.printDetails()

	N = scenario.n_providers + scenario.n_intermidiaries
	cycles = int(args.cycles)

	source = 2
	targets = [320,201,597,598]

	#matrix cycles x targets 
	results = np.zeros((cycles,len(targets)))

	for c in range(cycles):

		scenario_directory = 'simulation/' + args.scenario

		trace_file  =  scenario_directory + '/' + str(c) + '/traces.csv'
		#dataset_file = scenario_directory + '/' + str(c) + '/dataset.hdf5'
		result_file = scenario_directory  + '/results/result.txt'

		dataset = Dataset(N, scenario_directory, c)
		dataset.destroy()
		dataset.create()

		traceGenerator = TraceGenerator(scenario=scenario)
		traceGenerator.createCsv(file=trace_file)


		manager = TrustMan(scenario=scenario, dataset=dataset)

		manager.createFeedbackMatrix(infile=trace_file)
		#print("PREEEEE")
		#results.printFeedback()
		manager.updateFeedbackMatrix(scenario_directory=scenario_directory, cycle=c)

		#trust = EigenTrust(scenario=scenario)

		result = Result(scenario=scenario,dataset=dataset, manager=manager)
		result.printFeedback(targets)

		trust = TNSLA(scenario=scenario, dataset=dataset)
		trust.initialize()

		
		for i in range(len(targets)):
			results[c][i] = trust.computeTrust2(source, targets[i])
			print("\nTrust from "+str(source)+" to "+str(targets[i])+" at period "+str(c)+"th is "+str(results[c][i]))

	plot = Plot(scenario=scenario)
	plot.transitivity(targets=targets,results=results)

	#for i in range(len(targets)):
	#	print("reputation of "+str(targets[i]))
	#	for j in range(cycles):
	#		print(str(j)+": "+str(results[j][i]))






#print args.file.readlines()
if __name__ == '__main__':
   main()