import sys
import argparse
from config import *
from Scenario import *
from TraceGenerator import *
import os, csv
from os.path import expanduser
import time, datetime


def main():


   parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
   #abs params
   parser.add_argument('--providers', metavar='N', type=int, help="N - total number of local telco providers" )
   #parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
   #parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
   parser.add_argument('--intermidiaries',type=int, help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
   parser.add_argument('--calls', type=int, help="N - total number of calls. F - number of estimated fraud calls" )
   parser.add_argument('--hops', type=int, help="Average hops per call" )

   #percentage params
   parser.add_argument('--fraudsters', type=float, help="Percentage of fraudolent intemidiaraies, estimated fraudsters providers" )
   parser.add_argument('--frauds', type=float, help="Percentage of fraud calls. " )
   parser.add_argument('--pcoop', type=float, help="Percentage of cooperation provider " )
   parser.add_argument('--icoop', type=float, help="Percentage of cooperation intermidiaries. " )

   parser.add_argument('--scenario', help="Name of the simulation directory" )
   parser.add_argument('--cycles', type=int, help="Number of different traces" )

   args = parser.parse_args()


   #simulation_directory = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
   #simulation_directory = args.scenario 
   #home = expanduser('~')
   #sim_path = home + '/Documents/tesi/mysimulator2/FraudDetectorSimulator/traces/' + simulation_directory
  

   cycles = int(args.cycles)
   for c in range(cycles):

      sim_root = 'simulation/traces/' + args.scenario + '/'+ str(c) +'/'
      # sim_root = 'simulation/' + args.scenario + '/'
      #dataset = sim_root + 'dataset.hdf5'

      if not os.path.exists(sim_root):
         print ("create dir: "+sim_root)
         os.makedirs(sim_root)

      #create an istance of TraceGenerator with the params from cli
      scenario =  Scenario(n_providers=int(args.providers), 
         n_intermidiaries=int(args.intermidiaries), 
         n_calls=int(args.calls), 
         l_chain = int(args.hops),
         fraudsters_percentage=float(args.fraudsters), 
         frauds_percentage=float(args.frauds),
         provider_participation = int(args.pcoop),
         intermidiaries_participation = int(args.icoop),
         dataset = dataset)

      traceGen = TraceGenerator(scenario=scenario)

      traceGen.createCsv(sim_root+"/traces.csv")


      if os.path.isfile(sim_root+'/INFO.csv'):
         os.remove(sim_root+'/INFO.csv')

      with open(sim_root+'/INFO.csv', mode='w') as info:
         writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
         writer.writerow(["providers", "intermidiaries","fraudsterspercentage", "l_chain","calls","fraudspercentage", "n_coop_providers", "n_coop_intermidiaries", "fraudster_camuflage", "simmetry_strategy", "pretrust_strategy"])
         writer.writerow([scenario.n_providers, scenario.n_intermidiaries, scenario.fraudsters_percentage, scenario.l_chain, scenario.n_calls, scenario.frauds_percentage, scenario.provider_participation, scenario.intermidiaries_participation, TrustConfig.fraudsters_camouflage, TrustConfig.simmetry_strategy, TrustConfig.pretrust_strategy
            ])
         

if __name__ == '__main__':
   main()