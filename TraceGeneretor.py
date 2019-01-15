import json
import random
from config import ProviderConfig, TraceConfig, TrustConfig, FraudStrategy, FraudType, TarifConfig
import sys
import cPickle
import hashlib

def bytes(jsonObj):
	JSON_as_string = cPickle.dumps(jsonObj)
	return sys.getsizeof(JSON_as_string)



class TraceGeneretor:

	def __init__(self):
		pass

	@staticmethod	
	def generateCalls(variable_call, variable_call_frauds):

		random.seed(9001)

		traces = []  # [trace] * self.n_call
		trace2 = {
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
		print("bytes for one trace sim: "+ str(bytes(trace2)))
		for i in range( variable_call):

			if i == variable_call/100*10:
				print("10%")
			if i == variable_call/100*20:
				print("20%")
			if i == variable_call/100*30:
				print("30%")
			if i == variable_call/100*40:
				print("40%")
			if i == variable_call/100*50:
				print("50%")
			if i == variable_call/100*60:
				print("60%")
			if i == variable_call/100*70:
				print("70%")
			if i == variable_call/100*80:
				print("80%")
			if i == variable_call/100*90:
				print("90%")
			if i == variable_call-1:
				print("100%")

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

			durationA = 6 #random.randint(TarifConfig.duration_min,TarifConfig.duration_max)#minuti
			durationB = durationA
			rateA = random.uniform(TarifConfig.rate_local_min,TarifConfig.rate_local_max)#euro local termination tarif iva inclusa
			rateB = rateA

			cid = i
			intermidiaries = []			
			#honest call, symmetry. all intermediaries are honest
			if i in range(variable_call-variable_call_frauds):#TraceConfig.n_call_fraud):
				fraud = 0
				endPoints = TraceGeneretor.generateEndPoints(False)
				#popolo il vettore degli intermediari
				intermidiaries = TraceGeneretor.generateNodesChain(False)
			else: #tracce con frode
				fraud = 1
				endPoints = TraceGeneretor.generateEndPoints(True)
				intermidiaries = TraceGeneretor.generateNodesChain(True)

				if FraudType.fas_fraud:
					duration_fas = (1/60.0)*FraudType.fas_duration
					durationA = durationA + duration_fas
				if FraudType.bypass_fraud:
					rateA = rateA + FraudType.bypass_revenue
				if FraudType.lrn_fraud:
					rateA = random.uniform(TarifConfig.rate_inter_min , TarifConfig.rate_inter_max)
					rateB = rateA
					rateA = rateA / float(FraudType.lrn_price_rapport)

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

		calltraces = { "traces" : traces }

		

		with open(TraceConfig.file_path, 'w') as outfile:
			json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
		

	'''
	@staticmethod
	def generateIntermidiaries(fraud):
		intermidiaries = []
		if fraud == False:
			for t in range(TraceConfig.l_chain):

					if FraudStrategy.disguised_malicious:
						intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1))
					else:
						intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters-1))
		else:
			intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1))
			if FraudStrategy.next_hop_strategy == 3: #gli onesti tutti sono sospettati ( selgo a caso l_chain -1 onesti )
				for t in range(TraceConfig.l_chain-2):
					intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1))
			#aggiungo il frodatore
			if ProviderConfig.n_fraudsters == 1:
				fraudster = ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters
			else:
				fraudster = random.randint(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
			intermidiaries.append(fraudster)
	'''

	@staticmethod
	def generateEndPoints(fraud):
		if fraud==False:
			origin = random.randint(0,ProviderConfig.n_providers)
			termin = random.randint(0,ProviderConfig.n_providers)
			while(termin == origin):
				termin = random.randint(0,ProviderConfig.n_providers)
		else:
			#i frodatori operano unidirezionalmente su una rotta
			origin = random.randint(0,ProviderConfig.n_providers / 2)
			termin = random.randint(ProviderConfig.n_providers/2, ProviderConfig.n_providers)

		endPoints = [origin, termin]
		return endPoints

	'''
	@staticmethod
	def generateNodesChain(fraud):
		l_chain = TraceConfig.l_chain
		if FraudStrategy.next_hop_strategy != 3 and fraud==True:
			l_chain = 2
		count = 1
		nodes = []
		#first node, choose between everyone or only honest depends on cases:
		#case of no frauds, every one is candidate.
		if TraceConfig.n_call_fraud == 0:
			nodes.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries-1))
		#in case of disguised malicious, even fraudsters can partecipates in honset call
		if fraud==False and FraudStrategy.disguised_malicious:
			nodes.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1))
		else:
			nodes.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1))
		while count < (l_chain-1):
			#aggiungo l_chain-1 nodi onesti evitando di inserire nodi di uno stesso gruppo. (ignorato se cluster startegy = flase)
			#node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters + ProviderConfig.n_honest_fraudsters  -1)
			node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
			if not TraceGeneretor.duplicateNodeInGroup(nodes,node):
				nodes.append(node)
				count = count +1
		
		if fraud:
			#aggiungo un nodo sicuramente fordatore
			lastNode = random.randint(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
		else:
			if FraudStrategy.disguised_malicious:
				#aggiungo un nodo, forse onesto forse no.
				lastNode = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-1)
			else:
				#aggiungo un noto sicuramente onesto
				lastNode = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
		
		nodes.append(lastNode)
		return nodes
	'''

	@staticmethod
	def generateNodesChain(fraud):
		l_chain = TraceConfig.l_chain
		if FraudStrategy.next_hop_strategy != 3 and fraud==True:
			l_chain = 2

		firstnode = 0
		nodes = []
		lastnode = 0

		#sia nodi onesti che nodi fraudolenti instradano chiamate oneste
		if fraud==False and FraudStrategy.disguised_malicious==True: 
			#first node
			firstnode=random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
				if not TraceGeneretor.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-1)
			nodes.append(lastnode)

		#solo nodi onesti instradano chiamate oneste
		if fraud==False and FraudStrategy.disguised_malicious==False: 
			firstnode=random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
				if not TraceGeneretor.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries- ProviderConfig.n_fraudsters-1)
			nodes.append(lastnode)

		#L'ultimo nodo deve essere fraudolento, gli altri onesti, sia nel disguised sia nel pure
		if fraud==True:
			firstnode=random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
			nodes.append(firstnode)
			count = 1
			#l_chain-1 nodes
			while count < (l_chain-1):
				node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
				if not TraceGeneretor.duplicateNodeInGroup(nodes,node):
					nodes.append(node)
					count = count +1
			lastnode = random.randint(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
			nodes.append(lastnode)

		return nodes

	@staticmethod
	def duplicateNodeInGroup(nodes, node):
		if TrustConfig.clustering_strategy == False:
			return False
		found = False
		for n in nodes:
			#n = nodes[i]
			if (n/ProviderConfig.n_cluster_size) == (node/ProviderConfig.n_cluster_size):
				found = True
		return found


		#print(traces)

#with open('data.json', 'w') as outfile:
#    json.dump(data, outfile)





			