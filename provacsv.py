import csv
import pandas as pd
import numpy as np

def main():

	trace_file = 'traces/esperimento4/traces.csv'

	chunks = pd.read_csv(trace_file,chunksize=1000, sep=',', index_col=False, header=None)
	for chunk in chunks:
		#data = pd.concat(chunk)
		data = chunk.values
		#print(data)
		for trace in data:
			print(trace[7])



#print args.file.readlines()
if __name__ == '__main__':
   main()