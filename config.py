
class TraceConfig:

	retail_providers =  2300 #30 #deve essere pari
	wholesale_providers = 4000 #1000 #somma di provider e intermediari deve essere multiplo di cluster size
	providers_per_call = 4
	
	terminating_traffic = 180000000
	timespan = 60*24
	average_call_duration = 6 #Average call duration

	fraudsters_providers_percentage = 5 #5%degli intermediari
	fraud_traffic_percentage = 5
	fraudsters_camouflage = True

	#da rimuovere: solo 3 è concessa.
	fraudsters_response_strategy = 3 # 1=not_responding 2=hijack_suspects 3=honesty_spoof

	bypass_fraud = True
	fas_fraud =False
	lrn_fraud = False

	tariff_local = 0.02	
	tariff_international = 0.2
	bypass_revenue = 0.1 #guadagno al minuti stimato per bypass fraud
	lrn_revenue = 0.05
	fas_duration = 10 #secondi

	n_cluster_size = 1
	n_chunk = 10

class TrustConfig:

	detection_delay = 60*24 # less then time_span
	cooperating_retail_percentage = 1 #%di partecipazione dei nodi di terminazione
	cooperating_wholesale_percentage = 1

	pretrust_strategy = True
	simmetry_strategy = True

	l_cascade_agreements = 3 # minore di l_chain
	clustering_strategy = 1

class Csv:
	ID = 0
	FRAUD = 1
	ORIGIN = 2
	TERMIN = 3
	TRANSIT = 4


class m:
	FRAUD = 1
	HONEST = 0


class Tools:
	@staticmethod
	def printProgress(i,n):
		if i == n//100*10:
			print("10%")
		elif i == n//100*20:
			print("20%")
		elif i == n//100*30:
			print("30%")
		elif i == n//100*40:
			print("40%")
		elif i == n//100*50:
			print("50%")
		elif i == n//100*60:
			print("60%")
		elif i == n//100*70:
			print("70%")
		elif i == n//100*80:
			print("80%")
		elif i == n//100*90:
			print("90%")
		elif i == n-1:
			print("100%")
		return
		




		
class Result:
	graph1 = False
	graph2 = False
	graph3 = False
	graph4 = False
	graphA = False
	graphB = False
	graphC = False

		