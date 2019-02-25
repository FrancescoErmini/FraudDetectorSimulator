import sys
import argparse
from config import *
from Scenario import *
import os, csv
from os.path import expanduser
import time, datetime


def main():


   parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
   parser.add_argument('--providers', metavar='N', type=int, help="N - total number of local telco providers" )
   parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
   parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
   parser.add_argument('--scenario', help="Name of the simulation directory" )
   args = parser.parse_args()


   #simulation_directory = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
   simulation_directory = args.scenario 
   home = expanduser('~')
   dl_path = home + '/Documents/tesi/mysimulator2/FraudDetectorSimulator/traces/' + simulation_directory

   if not os.path.exists(dl_path):
      print ("create dir: traces/"+simulation_directory+"/")
      os.makedirs(dl_path)

   #create an istance of TraceGenerator with the params from cli
   scenario =  Scenario(providers=args.providers, 
      intermidiaries=args.intermidiaries[0], 
      fraudsters_percentage=args.intermidiaries[1], 
      calls=args.calls[0], 
      frauds_percentage=args.calls[1])

   scenario.createCsv(dl_path+"/traces.csv")

   with open(dl_path+'/INFO.csv', mode='w') as info:
      employee_writer = csv.writer(info, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      employee_writer.writerow(["providers", "intermidiaries","fraudsterspercentage", "l_chain","calls","fraudspercentage"])
      employee_writer.writerow([scenario.n_providers, scenario.n_intermidiaries, scenario.fraudsters_percentage, TraceConfig.providers_per_call, scenario.n_calls, scenario.frauds_percentage])
      

if __name__ == '__main__':
   main()