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
   parser.add_argument('--fraudsters', type=int, help="Percentage of fraudolent intemidiaraies, estimated fraudsters providers" )
   parser.add_argument('--frauds', type=int, help="Percentage of fraud calls. " )
   parser.add_argument('--pcoop', type=int, help="Percentage of cooperation provider " )
   parser.add_argument('--icoop', type=int, help="Percentage of cooperation intermidiaries. " )

   parser.add_argument('--scenario', help="Name of the simulation directory" )
   args = parser.parse_args()


   #simulation_directory = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
   simulation_directory = args.scenario 
   home = expanduser('~')
   #sim_path = home + '/Documents/tesi/mysimulator2/FraudDetectorSimulator/traces/' + simulation_directory
   sim_path = 'traces/' + simulation_directory

   if not os.path.exists(sim_path):
      print ("create dir: traces/"+simulation_directory+"/")
      os.makedirs(sim_path)

   #create an istance of TraceGenerator with the params from cli
   scenario =  Scenario(n_providers=int(args.providers), 
      n_intermidiaries=int(args.intermidiaries), 
      n_calls=int(args.calls), 
      l_chain = int(args.hops),
      fraudsters_percentage=int(args.fraudsters), 
      frauds_percentage=int(args.frauds),
      provider_participation = int(args.pcoop),
      intermidiaries_participation = int(args.icoop))

   traceGen = TraceGenerator(scenario=scenario)

   traceGen.createCsv(sim_path+"/traces.csv")

   if os.path.isfile(sim_path+'/INFO.csv'):
      os.remove(sim_path+'/INFO.csv')

   with open(sim_path+'/INFO.csv', mode='w') as info:
      employee_writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      employee_writer.writerow(["providers", "intermidiaries","fraudsterspercentage", "l_chain","calls","fraudspercentage", "n_coop_providers", "n_coop_intermidiaries"])
      employee_writer.writerow([scenario.n_providers, scenario.n_intermidiaries, scenario.fraudsters_percentage, TraceConfig.providers_per_call, scenario.n_calls, scenario.frauds_percentage, scenario.provider_participation, scenario.intermidiaries_participation
         ])
      

if __name__ == '__main__':
   main()