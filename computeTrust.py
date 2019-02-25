import argparse
import os
import csv


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--scenario', help="Trace file source directory for the simulation")
	args = parser.parse_args()

	scenario_directory = 'traces/'+args.scenario
	log_file = scenario_directory + '/INFO.csv'
	trace_file = scenario_directory + '/traces.csv'

	with open(log_file, 'r') as f:
		reader = csv.reader(f)
		log = list(reader)[0]

	n_providers=log[0]
	n_intermidiaries=log[1]
	fraudsters_percentage=log[2]
	l_chain = log[3]
	n_calls=0
	frauds_percentage=0

	manager = TrustMan(n_providers,n_intermidiaries,fraudsters_percentage,l_chain,calls,frauds_percentage)

	manager.updateMatrix(trace_file)




#print args.file.readlines()
if __name__ == '__main__':
   main()