class ProviderConfig:
	n_providers =  20 #30 #deve essere pari
	n_intermidiaries = 1000 #1000 #somma di provider e intermediari deve essere multiplo di cluster size
	n_fraudsters = 50 #5%degli intermediari
	n_cluster_size = 1
	
	provider_participation = 100 #%di partecipazione dei nodi di terminazione
	intermidiaries_participation = 100


class TarifConfig:
	duration_min = 1
	duration_max = 8
	rate_local_min = 0.02
	rate_local_max = 0.07
	rate_inter_min = 0.2
	rate_inter_max = 1.0
	
class TraceConfig:
	n_call = 41666
	n_call_fraud = 2820 
	l_chain = 4
	n_call_per_minute = 5000 #gloabli 9512 locali=168
	file_path = "calltraces.json"


class TrustConfig:
	symmetry_strategy = True
	pretrust_strategy = True
	clustering_strategy = False
	revenue_strategy = True
	ref = False
	l_cascade_agreements = 2 #minore di l_chain - 1 #da controllare se nex_ho_strategy = 1|2
	std_dev = 1 #99%=2,58 95%=1.96
'''
1 - not_responding
2 - hijack_suspects
3 - honesty_spoof
'''

class FraudStrategy:
	next_hop_strategy = 1
	sybil=False
	disguised_malicious = False

class FraudType:
	bypass_fraud = True
	fas_fraud =False
	lrn_fraud = False
	bypass_revenue = 0.1 #guadagno al minuti stimato per bypass fraud
	fas_duration = 10 #secondi
	lrn_price_rapport = 2 #quante volte di pi (moltiplicazione) costa la chiamata rurale


class Result:
	graph1 = False
	graph2 = False
	graph3 = False
	graph4 = False
	graphA = False
	graphB = False
	graphC = False

		