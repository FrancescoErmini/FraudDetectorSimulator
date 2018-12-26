import json
import random
from config import ProviderConfig, TraceConfig, TrustConfig


class TraceGeneretor:

	def __init__(self):
		pass

	@staticmethod	
	def generateCalls():
		

		traces = []  # [trace] * self.n_call
		
		for i in range( TraceConfig.n_call):

			trace = {
				"cid": 0,
				"origin": 0,
				"termin": 0,
				"fraud":0,
				"transit": []
			}
			cid = i
			intermidiaries = []			
			#honest call, symmetry. all intermediaries are honest
			if i in range(TraceConfig.n_call-TraceConfig.n_call_fraud):
				origin = random.randint(0,ProviderConfig.n_providers)
				termin = random.randint(0,ProviderConfig.n_providers)
				while(termin == origin):
					termin = random.randint(0,ProviderConfig.n_providers)
				fraud = 0
				#popolo il vettore degli intermediari
				for t in range(TraceConfig.l_chain):
					intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters-1))
			
			else:
				origin = random.randint(0,ProviderConfig.n_providers / 2)
				termin = random.randint(ProviderConfig.n_providers/2, ProviderConfig.n_providers)
				fraud = 1
				for t in range(TraceConfig.l_chain-1):
					intermidiaries.append(random.randint(ProviderConfig.n_providers, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters -1))
				
				if ProviderConfig.n_fraudsters == 1:
					fraudster = ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters
				else:
					fraudster = random.randint(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries -1)
				intermidiaries.append(fraudster)
				

			tmp = []
			for intermidiary in intermidiaries:
				tmp.append({"id":intermidiary})

			trace["cid"] = cid
			trace["origin"] = origin
			trace["termin"] = termin
			trace["fraud"] =  fraud
			trace["transit"] = tmp

			#print(trace)
			traces.append(trace)

		calltraces = { "traces" : traces }

		

		with open(TraceConfig.file_path, 'w') as outfile:
			json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
		
		#print(traces)

#with open('data.json', 'w') as outfile:
#    json.dump(data, outfile)





			