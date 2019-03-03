import json
import random
from config import *
import sys
#import cPickle
#import hashlib
#import getopt

#def bytes(jsonObj):
#	JSON_as_string = cPickle.dumps(jsonObj)
#	return sys.getsizeof(JSON_as_string)


class TraceGeneretor:
	n_providers=0
	n_intermidiaries=0
	n_fraudsters=0
	n_calls=0
	n_calls_fraud=0
	frauds_percentage=0

	def __init__(self, providers, intermidiaries, fraudsters_percentage, calls, frauds_percentage):
		super(TraceGeneretor, self).__init__()
		self.n_providers = providers
		self.n_intermidiaries = intermidiaries 
		self.n_fraudsters = intermidiaries * fraudsters_percentage // 100
		self.n_calls = calls
		self.n_calls_fraud = calls * frauds_percentage // 100
		self.frauds_percentage = frauds_percentage
		


	
	'''
	n_call sono le chiamate totali
	fraud percentage e la percentuale di fraudolente rispetto alle totali ( 50 vuol dire 50)
	Nota: assicurarsi che le chiamate fraudolente risultino essere un intero, altrimenti l'approssimazione va a zero.
	n_chunk serve a spezzare l'inserimento delle chiamate nel file. Ad esempio se voglio inserie un milione di chiamate
	posso definire n chunck = 1000 cosi che python calcola una traccia di n_chunck chiamate e la aggiunge al file generale 
	ogni in modo incrementale.

	terminating_traffic (minutes)

	time_period (minutes)

	'''

	def generateCalls(self):
		
		variable_call_frauds = _size * self.frauds_percentage // 100

		#random.seed(9001)

		traces = [] 
		
		for i in range( variable_call):

			trace = {
				"cid": 0,
				"origin": 0,
				"termin": 0,
				"fraud":0,
				"transit": [],
				"durationA": 0,
				"durationB": 0,
				"rateA": 0,
				"rateB": 0
			}

			durationA = TraceConfig.average_call_duration #random.randint(TraceConfig.duration_min,TraceConfig.duration_max)#minuti
			durationB = durationA
			#rateA = random.uniform(TraceConfig.average_call_duration.rate_local_min,TraceConfig.rate_local_max)#euro local termination tarif iva inclusa
			rateA = TraceConfig.tariff_local #euro local termination tarif iva inclusa
			rateB = rateA

			cid = i + offset
			intermidiaries = []			
			#honest call, symmetry. all intermediaries are honest
			if i in range(variable_call-variable_call_frauds):#.n_call_fraud):
				fraud = 0
				endPoints = self.generateEndPoints(fraud=False)
				#popolo il vettore degli intermediari
				intermidiaries = self.generateNodesChain(fraud=False)
			else: #tracce con frode
				fraud = 1
				endPoints = self.generateEndPoints(fraud=True)
				intermidiaries = self.generateNodesChain(fraud=True)

				if TraceConfig.fas_fraud:
					duration_fas = (1/60.0)*TraceConfig.fas_duration
					durationA = durationA + duration_fas
				if TraceConfig.bypass_fraud:
					rateA = rateA + TraceConfig.bypass_revenue
				if TraceConfig.lrn_fraud:
					rateA = TraceConfig.rate_international #.uniform(TraceConfig.rate_inter_min , TraceConfig.rate_inter_max)
					rateB = rateA
					rateA = rateA / float(TraceConfig.lrn_price_rapport)

			tmp = []
			for intermidiary in intermidiaries:
				tmp.append({"id":intermidiary})

			trace["cid"] = cid
			trace["origin"] = endPoints[0]
			trace["termin"] = endPoints[1]
			trace["fraud"] =  fraud
			trace["transit"] = tmp
			trace["durationA"] = durationA
			trace["durationB"] = durationB
			trace["rateA"] = rateA
			trace["rateB"]= rateB


			#print(trace)
			traces.append(trace)

		#calltraces = { "traces" : traces }

		return traces

		#with open(.file_path, 'w') as outfile:
		#	json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
		

def generateCallDetail(self):

		#random.seed(9001)

		call = [] 
		
		
			trace = {
				"cid": 0,
				"origin": 0,
				"termin": 0,
				"fraud":0,
				"transit": [],
				"durationA": 0,
				"durationB": 0,
				"rateA": 0,
				"rateB": 0
			}

			durationA = TraceConfig.average_call_duration #random.randint(TraceConfig.duration_min,TraceConfig.duration_max)#minuti
			durationB = durationA
			#rateA = random.uniform(TraceConfig.average_call_duration.rate_local_min,TraceConfig.rate_local_max)#euro local termination tarif iva inclusa
			rateA = TraceConfig.tariff_local #euro local termination tarif iva inclusa
			rateB = rateA

			cid = i + offset
			intermidiaries = []			
			#honest call, symmetry. all intermediaries are honest
			if i in range(variable_call-variable_call_frauds):#.n_call_fraud):
				fraud = 0
				endPoints = self.generateEndPoints(fraud=False)
				#popolo il vettore degli intermediari
				intermidiaries = self.generateNodesChain(fraud=False)
			else: #tracce con frode
				fraud = 1
				endPoints = self.generateEndPoints(fraud=True)
				intermidiaries = self.generateNodesChain(fraud=True)

				if TraceConfig.fas_fraud:
					duration_fas = (1/60.0)*TraceConfig.fas_duration
					durationA = durationA + duration_fas
				if TraceConfig.bypass_fraud:
					rateA = rateA + TraceConfig.bypass_revenue
				if TraceConfig.lrn_fraud:
					rateA = TraceConfig.rate_international #.uniform(TraceConfig.rate_inter_min , TraceConfig.rate_inter_max)
					rateB = rateA
					rateA = rateA / float(TraceConfig.lrn_price_rapport)

			tmp = []
			for intermidiary in intermidiaries:
				tmp.append({"id":intermidiary})

			trace["cid"] = cid
			trace["origin"] = endPoints[0]
			trace["termin"] = endPoints[1]
			trace["fraud"] =  fraud
			trace["transit"] = tmp
			trace["durationA"] = durationA
			trace["durationB"] = durationB
			trace["rateA"] = rateA
			trace["rateB"]= rateB


			#print(trace)
			traces.append(trace)

		#calltraces = { "traces" : traces }

		return traces
	def generateEndPoints(self, fraud):
		if fraud==False:
			origin = random.randint(0,self.n_providers)
			termin = random.randint(0,self.n_providers)
			while(termin == origin):
				termin = random.randint(0,self.n_providers)
		else:
			#i frodatori operano unidirezionalmente su una rotta
			origin = random.randint(0,self.n_providers / 2)
			termin = random.randint(self.n_providers/2, self.n_providers)

		endPoints = [origin, termin]
		return endPoints


	
	def generateNodesChain(self, fraud):
		l_chain = TraceConfig.providers_per_call
		if TraceConfig.fraudsters_response_strategy != 3 and fraud==True:
			l_chain = 2

		firstnode = 0
		nodes = []
		lastnode = 0

		#sia nodi onesti che nodi fraudolenti instradano chiamate oneste
		if fraud==False and TraceConfig.fraudsters_camouflage == True: 
			#first node
			firstnode=random.randint(self.n_providers, self.n_providers + self.n_intermidiaries -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(self.n_providers, self.n_providers + self.n_intermidiaries -1)
				if not self.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(self.n_providers, self.n_providers+self.n_intermidiaries-1)
			nodes.append(lastnode)

		#solo nodi onesti instradano chiamate oneste
		if fraud==False and TraceConfig.fraudsters_camouflage == False: 
			firstnode=random.randint(self.n_providers, self.n_providers + self.n_intermidiaries - self.n_fraudsters -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(self.n_providers, self.n_providers + self.n_intermidiaries - self.n_fraudsters -1)
				if not self.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(self.n_providers, self.n_providers+self.n_intermidiaries- self.n_fraudsters-1)
			nodes.append(lastnode)

		#L'ultimo nodo deve essere fraudolento, gli altri onesti, sia nel disguised sia nel pure
		if fraud==True:
			firstnode=random.randint(self.n_providers, self.n_providers + self.n_intermidiaries - self.n_fraudsters -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(self.n_providers, self.n_providers + self.n_intermidiaries - self.n_fraudsters -1)
				if not self.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(self.n_providers+self.n_intermidiaries - self.n_fraudsters, self.n_providers + self.n_intermidiaries -1)
			nodes.append(lastnode)

		return nodes

	def duplicateNodeInGroup(self, nodes, node):
		if TrustConfig.clustering_strategy == False:
			return False
		found = False
		for n in nodes:
			#n = nodes[i]
			if (n/TraceConfig.n_cluster_size) == (node/TraceConfig.n_cluster_size):
				found = True
		return found


		#print(traces)

#with open('data.json', 'w') as outfile:
#    json.dump(data, outfile)





			