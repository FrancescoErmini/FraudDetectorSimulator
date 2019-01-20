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
	'''
	n_call sono le chiamate totali
	fraud percentage e la percentuale di fraudolente rispetto alle totali ( 50 vuol dire 50)
	Nota: assicurarsi che le chiamate fraudolente risultino essere un intero, altrimenti l'approssimazione va a zero.
	n_chunk serve a spezzare l'inserimento delle chiamate nel file. Ad esempio se voglio inserie un milione di chiamate
	posso definire n chunck = 1000 cosi che python calcola una traccia di n_chunck chiamate e la aggiunge al file generale 
	ogni in modo incrementale.
	'''

	@staticmethod	
	def generateTraceFile(n_call, fraud_percentage, n_chunk):

		traces = []		
		
		iterations = n_call / n_chunk

		for i in range(iterations):
			traces = TraceGeneretor.generateCalls( n_chunk,  (n_chunk * fraud_percentage)/100, i*n_chunk)
			if i == 0:
				calltraces = { "traces" : traces }
				with open(TraceConfig.file_path, 'w') as outfile:
					json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
			else:
				TraceGeneretor.append_to_json(TraceConfig.file_path, traces)

	@staticmethod
	def printProgress(i, n_call):
		if i == n_call/100*10:
				print("10%")
		if i == n_call/100*20:
			print("20%")
		if i == n_call/100*30:
			print("30%")
		if i == n_call/100*40:
			print("40%")
		if i == n_call/100*50:
			print("50%")
		if i == n_call/100*60:
			print("60%")
		if i == n_call/100*70:
			print("70%")
		if i == n_call/100*80:
			print("80%")
		if i == n_call/100*90:
			print("90%")
		if i == n_call-1:
			print("100%")


	@staticmethod
	def append_to_json(filepath, data):
		# construct JSON fragment as new file ending
	    new_ending = "},\n" + json.dumps(data,sort_keys=True, indent=4, separators=(',', ': '))[1:-1] + "\n]\n}"

	    # edit the file in situ - first open it in read/write mode
	    with open(filepath, 'r+') as f:

	        f.seek(0, 2)        # move to end of file
	        index = f.tell()    # find index of last byte
	        index -= 1			# skip last } closing
 
	        # walking back from the end of file, find the index 
	        # of the original JSON's closing '}'
	        while not f.read().startswith('}'):
	            index -= 1
	            if index == 0:
	                raise ValueError("can't find JSON object in {!r}".format(filepath))
	            f.seek(index)

	        # starting at the original ending } position, write out
	        # the new ending
	        f.seek(index)
	        f.write(new_ending) 



	@staticmethod	
	def generateCalls(variable_call, variable_call_frauds, offset):

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

			durationA = 6 #random.randint(TarifConfig.duration_min,TarifConfig.duration_max)#minuti
			durationB = durationA
			rateA = random.uniform(TarifConfig.rate_local_min,TarifConfig.rate_local_max)#euro local termination tarif iva inclusa
			rateB = rateA

			cid = i + offset
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

		#calltraces = { "traces" : traces }

		return traces

		#with open(TraceConfig.file_path, 'w') as outfile:
		#	json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
		


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





			