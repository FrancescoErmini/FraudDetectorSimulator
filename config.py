
class TraceConfig:


	n_chunk = 1000

	#retail_providers =  2300 #30 #deve essere pari
	#wholesale_providers = 4000 #1000 #somma di provider e intermediari deve essere multiplo di cluster size
	#providers_per_call = 4
	
	terminating_traffic = 180000000
	min_per_day = 60*24
	average_call_duration = 6 #Average call duration
	n_calls_per_min = 694

	#fraudsters_providers_percentage = 1 #5%degli intermediari
	#fraud_traffic_percentage = 
	

	#da rimuovere: solo 3 è concessa.
	#fraudsters_response_strategy = 3 # 1=not_responding 2=hijack_suspects 3=honesty_spoof

	bypass_fraud = True
	fas_fraud = False
	lrn_fraud = False
	tariff_local = 0.02	
	tariff_international = 0.2
	bypass_revenue = 0.1 #guadagno al minuti stimato per bypass fraud
	lrn_revenue = 0.05
	fas_duration = 10 #secondi

	n_cluster_size = 1




	def cycles2days(call_per_cycle):
		return call_per_cycle*TraceConfig.n_calls_per_min/(24*60)


	

class TrustConfig:

	fraudsters_camouflage = False
	pretrust_strategy = False
	simmetry_strategy = True
	l_cascade_agreements = 1 # minore di l_chain 1,2,3
	#clustering_strategy = 1

class TNSLAsettings:
	trustee_score = 0.8
	cycle_deep_max = 10
	pos_forgetting_factor = 0.1
	neg_forgetting_factor = 1.0
	pretrust_agreements = 4
	use_pretrust = True



class Csv:
	ID = 0
	FRAUD = 1
	ORIGIN = 2
	TERMIN = 3
	TRANSIT = 4



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
		

		