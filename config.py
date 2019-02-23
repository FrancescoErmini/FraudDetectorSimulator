
class TraceConfig:

	retail_providers =  2300 #30 #deve essere pari
	wholesale_providers = 4000 #1000 #somma di provider e intermediari deve essere multiplo di cluster size
	providers_per_call = 4
	
	terminating_traffic = 180000000
	timespan = 60*24
	average_call_duration = 6 #Average call duration

	fraudsters_providers_percentage = 5 #5%degli intermediari
	fraud_traffic_percentage = 5
	fraudsters_camouflage = False

	#da rimuovere: solo 3 è concessa.
	fraudsters_response_strategy = 3 # 1=not_responding 2=hijack_suspects 3=honesty_spoof

	bypass_fraud = True
	fas_fraud =False
	lrn_fraud = False

	tariff_local = 0.02	
	tariff_interational = 0.2
	bypass_revenue = 0.1 #guadagno al minuti stimato per bypass fraud
	
	fas_duration = 10 #secondi
	lrn_price_rapport = 2 #quante volte di pi (moltiplicazione) costa la chiamata rurale

	n_cluster_size = 1

class TrustConfig:

	detection_delay = 60*24 # less then time_span
	cooperating_retail_percentage = 1 #%di partecipazione dei nodi di terminazione
	cooperating_wholesale_percentage = 1

	pretrust_strategy = True
	simmetry_strategy = True

	l_pretrust = 3 # minore di l_chain
	clustering_strategy = 1


class Result:
	graph1 = False
	graph2 = False
	graph3 = False
	graph4 = False
	graphA = False
	graphB = False
	graphC = False

		