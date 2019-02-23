import sys
import argparse
from config import *
from Scenario import *

def main():

   parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
   parser.add_argument('--providers', metavar='N', type=int, help="N - total number of local telco providers" )
   parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
   parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
   parser.add_argument('--outputfile', type=argparse.FileType('w'), default=sys.stdout, help="Name of the call traces file" )
   args = parser.parse_args()

   #create an istance of TraceGenerator with the params from cli
   scenario =  Scenario(providers=args.providers, 
      intermidiaries=args.intermidiaries[0], 
      fraudsters_percentage=args.intermidiaries[1], 
      calls=args.calls[0], 
      frauds_percentage=args.calls[1])

   scenario.createCsv("ciao.csv")
      

if __name__ == '__main__':
   main()