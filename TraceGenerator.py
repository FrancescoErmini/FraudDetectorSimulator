from config import *
import random

class TraceGenerator:
  
   def __init__(self, scenario):
      super(TraceGenerator, self).__init__()
      self.scenario = scenario
     

   def createCsv(self, file):
      f = open(file,'w')

      for i in range(0, self.scenario.n_calls):
         Tools.printProgress( i, self.scenario.n_calls)

         durationA = TraceConfig.average_call_duration #random.randint(TraceConfig.duration_min,TraceConfig.duration_max)#minuti
         durationB = durationA
         rateA = TraceConfig.tariff_international #euro local termination tarif iva inclusa
         rateB = rateA
         fraud = 0 #FALSE

         if not self.isFraud(i):    
            endPoints = self.generateEndPoints(fraud=False)
            #popolo il vettore degli intermediari
            nodes = self.generateNodesChain(fraud=False)
         else: #tracce con frode
            endPoints = self.generateEndPoints(fraud=True)
            nodes = self.generateNodesChain(fraud=True)

            fraud = 1
            if TraceConfig.fas_fraud:
               durationA = durationA + (1/60.0)*TraceConfig.fas_duration
            if TraceConfig.bypass_fraud:
               rateB = TraceConfig.tariff_local
            if TraceConfig.lrn_fraud:
               rateA = TraceConfig.tariff_local  #.uniform(TraceConfig.rate_inter_min , TraceConfig.rate_inter_max)
         
         """
         Note: element order shold match above values in config.py
         class Csv:
            ID = 0
            FRAUD = 1
            ORIGIN = 2
            TERMIN = 3
            TRANSIT = 4+i
         """

         trace = str(i)
         trace += ',' + str(fraud)
         trace += ',' + str(endPoints[0])
         trace += ',' + str(endPoints[1])
         for node in nodes:
            trace = trace + ',' + str(node)

         #punto1 - evito di scrivere le tracce con frodatore in blacklist
         if fraud==1 and not self.scenario.isFraudster(nodes[len(nodes)-1]):
            #print("-")
            pass
         else:
            f.write(trace+'\n')
      #endfor
      f.close()


   '''
   def analyseTrace(self, infile):
      with open(infile, 'r') as src:
         reader = csv.reader(src)
         traces = list(reader)

      print("\nAnalysing traces....")

      for trace in traces:
         pass
   '''





   def isFraud(self, index):
      chunk = TraceConfig.n_chunk
      limit = int(chunk-self.scenario.frauds_percentage*chunk/100)
      if index%chunk < limit:
         return False
      else:
         return True

   def generateEndPoints(self, fraud):
      if fraud==False:
         origin = random.randint(0,self.scenario.n_providers)
         termin = random.randint(0,self.scenario.n_providers)
         while(termin == origin):
            termin = random.randint(0,self.scenario.n_providers)
      else:
         #i frodatori operano unidirezionalmente su una rotta
         origin = random.randint(0,self.scenario.n_providers / 2)
         termin = random.randint(self.scenario.n_providers/2, self.scenario.n_providers)

      endPoints = [origin, termin]
      return endPoints



   def generateNodesChain(self, fraud):
      l_chain = self.scenario.l_chain
      #if TraceConfig.fraudsters_response_strategy != 3 and fraud==True:
      #   l_chain = 2

      firstnode = 0
      nodes = []
      lastnode = 0

      #sia nodi onesti che nodi fraudolenti instradano chiamate oneste
      if fraud==False and TrustConfig.fraudsters_camouflage == True: 
         #first node
         firstnode=random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries -1)
         nodes.append(firstnode)
         count = 1
         #l_chain-1 nodes
         while count < (l_chain-1):
            node = random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries -1)
            if not self.isBlackListed(node):
               nodes.append(node)
               count = count +1
         lastnode = random.randint(self.scenario.n_providers, self.scenario.n_providers+self.scenario.n_intermidiaries-1)
         nodes.append(lastnode)

      #solo nodi onesti instradano chiamate oneste
      if fraud==False and TrustConfig.fraudsters_camouflage == False: 
         firstnode=random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries - self.scenario.n_fraudsters -1)
         nodes.append(firstnode)
         count = 1
         #l_chain-1 nodes
         while count < (l_chain-1):
            node = random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries - self.scenario.n_fraudsters -1)
            if not self.isBlackListed(node):
               nodes.append(node)
               count = count +1
         lastnode = random.randint(self.scenario.n_providers, self.scenario.n_providers+self.scenario.n_intermidiaries- self.scenario.n_fraudsters-1)
         nodes.append(lastnode)

      #L'ultimo nodo deve essere fraudolento, gli altri onesti, sia nel disguised sia nel pure
      if fraud==True:
         firstnode=random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries - self.scenario.n_fraudsters -1)
         nodes.append(firstnode)
         count = 1
         #l_chain-1 nodes
         while count < (l_chain-1):
            node = random.randint(self.scenario.n_providers, self.scenario.n_providers + self.scenario.n_intermidiaries - self.scenario.n_fraudsters -1)
            if not self.isBlackListed(node):
               nodes.append(node)
               count = count +1

         lastnode = random.randint(self.scenario.n_providers+self.scenario.n_intermidiaries - self.scenario.n_fraudsters, self.scenario.n_providers + self.scenario.n_intermidiaries -1)
         if not self.isBlackListed(lastnode):
            nodes.append(lastnode)
            #attenzione, controsenso la traccia è con frode, senza frodatore: risolta alla cazzo vedi punto1
      return nodes

   def isBlackListed(self, node):
      if not TrustConfig.use_tmp_blacklist:
         return False
      else:
         if node in self.scenario.blacklist:
            #print("Exclude from trace node: " + str(node))
            return True
         return False





      """
      if TrustConfig.clustering_strategy == False:
         return False
      found = False
      for n in nodes:
         #n = nodes[i]
         if (n/TraceConfig.n_cluster_size) == (node/TraceConfig.n_cluster_size):
            found = True
      return found
      """

