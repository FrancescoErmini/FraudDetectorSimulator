import sys
import argparse
import json
from TraceGeneretor import *

def main():

   parser = argparse.ArgumentParser(prog='TRACES GENERATOR')
   parser.add_argument('--providers', metavar='N', type=int, help="N - total number of local telco providers" )
   parser.add_argument('--intermidiaries', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of intermidiary providers. F - number of estimated fraudsters providers" )
   parser.add_argument('--calls', nargs=2, metavar=('N', 'F'), type=int,help="N - total number of calls. F - number of estimated fraud calls" )
   parser.add_argument('--outputfile', type=argparse.FileType('w'), default=sys.stdout, help="Name of the call traces file" )
   args = parser.parse_args()


   #create an istance of TraceGenerator with the params from cli
   trace = TraceGeneretor(providers=args.providers, 
      intermidiaries=args.intermidiaries[0], 
      fraudsters_percentage=args.intermidiaries[1], 
      calls=args.calls[0], 
      frauds_percentage=args.calls[1])

   #write the trace details on the header of the output file
   args.outputfile.write(
      '{' +
      ' "providers" : ' + str(args.providers)+','+
      ' "intermidiaries" : ' + str(args.intermidiaries[0])+','+
      ' "fraudsters" : ' + str(args.intermidiaries[1])+','+
      ' "calls" : ' + str(args.calls[0])+','+
      ' "frauds" : ' + str(args.calls[1])+
      '},\n')

   args.outputfile.write('{ "traces" : \n')
   index=0
   chunk=1000
   done=True
   while done:   
      if index + chunk > trace.n_calls:
         chunk = trace.n_calls - index
         done = False
      traces=trace.generateCalls(_size=chunk, offset=index)
      printProgress(index,trace.n_calls)
      index += chunk
      print(traces, file=args.outputfile)
      #json.dump(traces, args.outputfile, sort_keys=True, indent=4, separators=(',', ': '))
      
   args.outputfile.write('\n}')
   


def printProgress(i, n):
   if i < n//100*10:
      print("10%")
      return
   elif i < n//100*20:
      print("20%")
      return
   elif i < n//100*30:
      print("30%")
      return
   elif i < n//100*40:
      print("40%")
      return
   elif i < n//100*50:
      print("50%")
      return
   elif i < n//100*60:
      print("60%")
      return
   elif i < n//100*70:
      print("70%")
      return
   elif i < n//100*80:
      print("80%")
      return
   elif i < n//100*90:
      print("90%")
      return
   elif i < n:
      print("100%")
      return

if __name__ == '__main__':
   main()


   '''
   ####def generateTraceFile(terminating_traffic, collect_period, fraud_percentage, retail_providers, wholesale_providers):
      n_calls = terminating_traffic // 

      file_json = ["trace1.json","trace2.json","trace3.json","trace4.json","trace5.json","trace6.json","trace7.json"]
      
      for i in range(7):
         traces = TraceGeneretor.generateCalls( 694*60*24,  34*60*24, i*(694*60*24))
         calltraces = { "traces" : traces }
         with open(file_json[i], 'w') as outfile:
            json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))

      traces = []    
      
      iterations = n_call / n_chunk

      for i in range(iterations):
         if 0 == 0:
            calltraces = { "traces" : traces }
            with open(TraceConfig.file_path, 'w') as outfile:
               json.dump(calltraces, outfile, sort_keys=True, indent=4, separators=(',', ': '))
         else:
            TraceGeneretor.append_to_json(TraceConfig.file_path, traces)
      '''
   '''
   @staticmethod
   def printProgress(i, n_call):
      if i == n_call/100*10:
            print("10%")
      if i == n_call/100*20:
         print("20%")
      if i == n_call/100*30:
         print("30%")
      if i == n_call/100*40:
         print("40%")
      if i == n_call/100*50:
         print("50%")
      if i == n_call/100*60:
         print("60%")
      if i == n_call/100*70:
         print("70%")
      if i == n_call/100*80:
         print("80%")
      if i == n_call/100*90:
         print("90%")
      if i == n_call-1:
         print("100%")


   @staticmethod
   def append_to_json(filepath, data):
      # construct JSON fragment as new file ending
       new_ending = "},\n" + json.dumps(data,sort_keys=True, indent=4, separators=(',', ': '))[1:-1] + "\n]\n}"

       # edit the file in situ - first open it in read/write mode
       with open(filepath, 'r+') as f:

           f.seek(0, 2)        # move to end of file
           index = f.tell()    # find index of last byte
           index -= 1         # skip last } closing
 
           # walking back from the end of file, find the index 
           # of the original JSON's closing '}'
           while not f.read().startswith('}'):
               index -= 1
               if index == 0:
                   raise ValueError("can't find JSON object in {!r}".format(filepath))
               f.seek(index)

           # starting at the original ending } position, write out
           # the new ending
           f.seek(index)
           f.write(new_ending) 


   '''


   '''

   n_providers=TraceConfig.retail_providers #-p 100000
   n_intermidiaries=TraceConfig.TraceConfig.wholesale_providers # -i 1000000
   l_chain=TraceConfig.transit_providers_per_call # -l 4
   n_fraudsters = TraceConfig.fraudsters_providers_percentage*n_intermidiaries//100

   n_calls=TraceConfig.terminating_traffic // TraceConfig.average_call_duration
   n_calls_fraud = TraceConfig.fraud_traffic_percentage*n_calls//100

   TraceConfig.timespan # -d # -t 
   
  

    # -x
   TraceConfig.fraud_traffic_percentage # -f
   TraceConfig.fraudsters_camouflage # -c
   '''
'''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg 
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

if __name__ == "__main__":
   main(sys.argv[1:])
'''