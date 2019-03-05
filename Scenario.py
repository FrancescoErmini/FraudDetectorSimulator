
class Scenario:
   n_providers=0
   n_intermidiaries=0
   n_fraudsters=0
   fraudsters_percentage = 0
   n_calls=0
   n_calls_fraud=0
   frauds_percentage=0
   l_chain = 0
   provider_participation = 0
   intermidiaries_participation = 0

   n_coop_providers = 0
   n_coop_intermidiaries = 0
   n_honests = 0


   def __init__(self, n_providers, n_intermidiaries, n_calls,  l_chain, fraudsters_percentage,  frauds_percentage, provider_participation, intermidiaries_participation, dataset):
      super(Scenario, self).__init__()
      self.n_providers = n_providers
      self.n_intermidiaries = n_intermidiaries 
      self.fraudsters_percentage= fraudsters_percentage
      self.n_calls = n_calls
      self.frauds_percentage = frauds_percentage
      self.l_chain=l_chain
      self.provider_participation = provider_participation
      self.intermidiaries_participation = intermidiaries_participation

      self.n_fraudsters = n_intermidiaries * fraudsters_percentage // 100
      self.n_calls_fraud = n_calls * frauds_percentage // 100
      self.n_coop_providers = provider_participation*n_providers//100
      self.n_coop_intermidiaries = intermidiaries_participation*(n_intermidiaries-self.n_fraudsters)//100
      self.n_honests = self.n_intermidiaries - self.n_fraudsters
      self.N = n_providers + n_intermidiaries
      self.dataset = dataset




   def isFraudster(self, index):

      ind = int(index)
      low = self.n_providers+self.n_intermidiaries-self.n_fraudsters
      up =  self.n_providers+self.n_intermidiaries

      if ind in range(low,up):
         return True 
      else:
         return False

   def isFraud(self, value):

      val = int(value)

      if val == 1:
         return True
      else:
         return False

   def isCoopProvider(self, index):

      ind = int(index)
      low = int(self.n_providers/2) - int(self.n_coop_providers/2)
      up =  int(self.n_providers/2) + int(self.n_coop_providers/2)
      
      if ind in range(low,up+1):
         return True
      else:
         return False

   def isCoopIntermidiary(self, index):

      ind = int(index)
      low = self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)-int(self.n_coop_intermidiaries/2)
      up =  self.n_providers+int((self.n_intermidiaries-self.n_fraudsters)/2)+int(self.n_coop_intermidiaries/2)

      if ind in range(low,up+1):
         return True
      else:
         return False