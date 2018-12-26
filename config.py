class ProviderConfig:
	n_providers = 4 #deve essere pari
	n_intermidiaries = 32 #multiplo di cluster size
	n_fraudsters = 4 # un cluster
	n_cluster_size = 4
	
	

class TraceConfig:
	n_call = 400
	n_call_fraud = 200 #minore di n_call
	l_chain = 4
	l_cascade_agreements = 3 #minore di l_chain - 1
	file_path = "calltraces.json"


class TrustConfig:
	symmetry_strategy = True
	pretrust_strategy = True
	clustering_strategy = True




		