import json
import random
from config import ProviderConfig, TraceConfig, TrustConfig, FraudStrategy, FraudType, TarifConfig


class TraceGeneretor:

	def __init__(self):
		pass

	@staticmethod	
	def generateCalls():
		random.seed(9001)

		traces = []  # [trace] * self.n_call
		
		for i in range( TraceConfig.n_call):

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

			durationA = random.randint(TarifConfig.duration_min,TarifConfig.duration_max)#minuti
			durationB = durationA
			rateA = random.uniform(TarifConfig.rate_local_min,TarifConfig.rate_local_max)#euro local termination tarif iva inclusa
			rateB = rateA

			cid = i
			intermidiaries = []			
			#honest call, symmetry. all intermediaries are honest
			if i in range(TraceConfig.n_call-TraceConfig.n_call_fraud):
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
					rateA = rateA + random.uniform(FraudType.bypass_revenue-0.02, FraudType.bypass_revenue+0.02)
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


	@staticmethod
	def generateNodesChain(fraud):
		l_chain = TraceConfig.l_chain
		if FraudStrategy.next_hop_strategy != 3 and fraud==True:
			l_chain = 2
		count = 1
		nodes = []
		nodes.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1))
		while count < (l_chain-1):
			#aggiungo l_chain-1 nodi onesti evitando di inserire nodi di uno stesso gruppo. (ignorato se cluster startegy = flase)
			node = random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1)
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





			