class ProviderConfig:
	n_providers = 100 #deve essere pari
	n_intermidiaries = 1000 #somma di provider e intermediari deve essere multiplo di cluster size
	n_fraudsters = 200 # un cluster
	n_cluster_size = 10

class TarifConfig:
	duration_min = 1
	duration_max = 8
	rate_local_min = 0.02
	rate_local_max = 0.07
	rate_inter_min = 0.2
	rate_inter_max = 1.0
	
class TraceConfig:
	n_call = 300000
	n_call_fraud = 3000
	l_chain = 5
	n_call_per_minute = 5000 #gloabli 9512 locali=168
	file_path = "calltraces.json"


class TrustConfig:
	symmetry_strategy = True
	pretrust_strategy = True
	clustering_strategy = True
	revenue_strategy = True
	l_cascade_agreements = 2 #minore di l_chain - 1 #da controllare se nex_ho_strategy = 1|2

'''
1 - not_responding
2 - hijack_suspects
3 - honesty_spoof
'''

class FraudStrategy:
	next_hop_strategy = 3
	sybil=False
	disguised_malicious = True

class FraudType:
	bypass_fraud = True
	fas_fraud = True
	lrn_fraud = False
	bypass_revenue = 0.15 #guadagno al minuti stimato per bypass fraud
	fas_duration = 10 #secondi
	lrn_price_rapport = 2 #quante volte di pi (moltiplicazione) costa la chiamata rurale


class Result:
	graph1 = False
	graph2 = False
	graph3 = False
	graph4 = False

		