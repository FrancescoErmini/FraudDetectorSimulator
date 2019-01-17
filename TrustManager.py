#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
#import pandas as pd
#import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
#matplotlib.style.use('ggplot')
#from pandas import DataFrame
from config import ProviderConfig, TraceConfig, TrustConfig, FraudStrategy, FraudType, Result

class TrustManager:


    @staticmethod
    def computeTrust():
        ''' referenze without false-positive cases '''
        if TrustConfig.ref:
            Ref = [[ 0 for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
            Tref = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        
        n_groups = (ProviderConfig.n_providers+ProviderConfig.n_intermidiaries) / ProviderConfig.n_cluster_size
        if FraudStrategy.sybil:
            Tinit = [1 for g in range(n_groups)]

        if TrustConfig.clustering_strategy:
            Trow = [[0 for k in range(2)] for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]



        fraudsters_behaviour = [[0 for k in range(2)] for i in range(ProviderConfig.n_fraudsters)]
        Revenue = [0 for g in range(ProviderConfig.n_intermidiaries+ProviderConfig.n_providers)]
        M = [[[0 for k in range(2)] for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        Tscore = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]

        provider_participation = (ProviderConfig.n_providers*ProviderConfig.provider_participation)/100
        intermidiaries_participation = (ProviderConfig.n_intermidiaries*ProviderConfig.intermidiaries_participation)/100

        fraudsters = 0
        temporary_fraudsters =0
        falsepositive = 0
        falsenegative = 0
        nullfalsepositive = 0
        undetected = 0
        fraudRevenue = 0
        fraudSaved = 0
        temporary_fraudsters = 0
        reports_counter_ref=0
        reports_counter=0
        count = 0



        pHonesty = 0
        fraudBehaviour = 0



        fraudAverageRevenue=0
        pDetect=0
        pFalsepositive=0
        pFalsenegative=0
        fraudRevenuePercentage=0
       
        with open(TraceConfig.file_path) as f:
            data = json.load(f)
        traces = data["traces"]

        frauds_counter = 0
        reports_counter = 0

        good = 0
        bad = 0

        variable_call = len(traces)

        for trace in traces:

            if count == variable_call/100*10:
                print("10%")
            if count == variable_call/100*20:
                print("20%")
            if count == variable_call/100*30:
                print("30%")
            if count == variable_call/100*40:
                print("40%")
            if count == variable_call/100*50:
                print("50%")
            if count == variable_call/100*60:
                print("60%")
            if count == variable_call/100*70:
                print("70%")
            if count == variable_call/100*80:
                print("80%")
            if count == variable_call/100*90:
                print("90%")
            if count == variable_call-1:
                print("100%")
            count = count + 1

            if FraudStrategy.disguised_malicious:
                for i in range(len(trace["transit"])):
                    if trace["transit"][i]["id"] in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                        if trace["fraud"]==0:
                            good = good + 1 #le transazioni buone fatte da un frodatre nel campione
                        else:
                            bad = bad + 1 #le transazioni maligne fatte da un frodatre nel campione
            else:
                bad = 100

            if trace["fraud"]==0 and trace["termin"] in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                #print("+")
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][0] = M[origin][nextop][0] + 1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    if source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                        M[source][target][0] = M[source][target][0] + 1
                        if TrustConfig.ref:
                            Ref[source][target] = Ref[source][target] +1

            if trace["fraud"]==1 and trace["termin"] in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                frauds_counter = frauds_counter + 1
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][1] = M[origin][nextop][1] + 1
                if TrustConfig.pretrust_strategy and TrustConfig.l_cascade_agreements > 0 and nextop not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[origin][nextop][1]>0:
                        M[origin][nextop][1] = M[origin][nextop][1] - 1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    reports_counter_ref = reports_counter_ref + 1
                    if source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                        reports_counter = reports_counter + 1
                        M[source][target][1] = M[source][target][1] + 1
                        Revenue[target] = Revenue[target] +  TrustManager.calcRevenue(trace)
                        if TrustConfig.ref:
                            Ref[source][target] = Ref[source][target] +1
                        if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[source][target][1]>0:  
                                    M[source][target][1] = M[source][target][1] -  1.0 / (i+2)

                    
                    '''
                    if  FraudStrategy.sybil and target in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                        pos = 0
                        neg = 0
                        for k in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                            pos = pos + M[k][target][0]
                            neg = neg + M[k][target][1]

                        reputation = (float)((pos +1.0)/(neg+pos+2.0))
                        if reputation < 0.5 and trace["cid"]%111==0:
                            print("\nSybil: Fraudster id " + str(target) + " has change identity " + " with r= " + str(reputation)) 
                            for k in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                                M[k][target][0] = 0
                                M[k][target][1] = 0
                                Tinit[n_groups-1] = 0.1 #TODO aggiusta
                    '''




                    #if target in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters):
      

        '''
        
        Reputation before false positive reduction

        '''
        if TrustConfig.ref:

            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters):
                pos = 0
                for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                    pos = pos + Ref[i][j]
                Tref[j] = (1.0+pos)/(2.0+pos) #neg = 0
            #da togliere, ridurre il vettore!!
            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                Tref[j] = 0
           
            Tworstcase = TrustManager.printRes(M)
            #print ("\nWorst case:")
            #print(Tworstcase)

        '''

        preTrust nota bene: vaanno aggiunte funizionalità del bebbo

        ''' 
        '''
        if TrustConfig.pretrust_strategy:
            for trace in traces:
                if trace["fraud"] == 1 and trace["termin"] in range(ProviderConfig.n_providers/2-provider_participation/2, ProviderConfig.n_providers/2 + provider_participation/2):
                    origin = trace["origin"]
                    nextop = trace["transit"][0]["id"]
                    if TrustConfig.l_cascade_agreements > 0 and nextop not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[origin][nextop][1]>0:
                        M[origin][nextop][1] = M[origin][nextop][1] - 1
                    for i in range(len(trace["transit"])-1):
                            source = trace["transit"][i]["id"]
                            target = trace["transit"][i+1]["id"]
                            discount = 0
                            if source in range(ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2-intermidiaries_participation/2,ProviderConfig.n_providers+(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)/2+intermidiaries_participation/2):
                                if TrustConfig.pretrust_strategy and i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[source][target][1]>0:  
                                    M[source][target][1] = M[source][target][1] -  1.0 / (i+2)
                                #Revenue[target] =  Revenue[target] - TrustManager.calcRevenue(trace)*(1.0/(2.0+i))
            
            Tpretrust = TrustManager.printRes(M)
            #print ("\nPre trust:")
            #print(Tpretrust)


        '''

        ''' 

        simmetry 

        '''

        if TrustConfig.symmetry_strategy:
            print("start simmetry")
            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                for i in range(j+1):
                    discount = min(M[i][j][1],M[j][i][1])
                    M[i][j][1] = M[i][j][1] - discount
                    M[j][i][1] = M[j][i][1] - discount

            
            Tsimmetry = TrustManager.printRes(M)
            #print ("\nSimmetry:")
            #print(Tsimmetry)


        ''' 

        cluster strategy

        '''


        if TrustConfig.clustering_strategy:

            Tscore = TrustManager.printRes(M)

            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = 0
                neg = 0
                for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                    pos = pos + M[i][j][0]
                    neg = neg + M[i][j][1]
                Trow[j][0]=pos
                Trow[j][1]=neg
            
            #l_groups = ProviderConfig.n_intermidiaries / ProviderConfig.n_cluster_size
            Tgroup = [0 for g in range(n_groups)]
            #Tgroup = [0 for g in range(l_groups)]
            for group in range( n_groups ):
                pos = 0
                neg = 0
                for interm in range( group*ProviderConfig.n_cluster_size , ((group+1)*ProviderConfig.n_cluster_size)):
                    pos = pos + Trow[interm][0]
                    neg = neg + Trow[interm][1]
                Tgroup[group] = (1.0+pos)/(2.0+pos+neg) * Tinit[group]

                for peer in range( group*ProviderConfig.n_cluster_size , (group+1)*ProviderConfig.n_cluster_size ):
                    Tscore[peer] = (Tscore[peer] * Tgroup[group]) / ((Tscore[peer] * Tgroup[group]) + ((1-Tscore[peer])*(1-Tgroup[group])))
            #print ("\nClustering:")
            #print (Tscore)




        '''


        RESULT



        '''
        Tscore = TrustManager.printRes(M)



        numeratore = 0
        denominatore = 0
        for  i in range(ProviderConfig.n_intermidiaries):
            numeratore = numeratore + Tscore[i+ProviderConfig.n_providers] #*weights[i]
        denominatore =  ProviderConfig.n_intermidiaries #denominatore + weights[i]
        average = numeratore / denominatore
        x=0
        cnt = 0
        for  i in range(ProviderConfig.n_intermidiaries):
            #if Tscore[i+ProviderConfig.n_providers] > 0.5:
            cnt = cnt + 1
            x = x+(Tscore[i+ProviderConfig.n_providers] - average)**2
        x = x / cnt
        standarddev = math.sqrt(x)
        threshold = average - TrustConfig.std_dev*standarddev #99%=2,58 95%=1.96
        if threshold < 0.5:
            threshold = 0.5

        

        
        for i in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            print("compare threshold")
            if i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                if Tscore[i] < 0.5:
                    print("fraudster is: " + str(i) + " with score values: " +  str(Tscore[i]) +"<"+str(threshold))
                    fraudsters = fraudsters +1
            
                if Tscore[i] < threshold and Tscore[i] > 0.5:
                    temporary_fraudsters = temporary_fraudsters +1
                
                if Tscore[i] > threshold:
                    falsenegative = falsenegative +1
                
                if Tscore[i] == 0.5:
                    undetected = undetected +1
           
            else:                

                if Tscore[i] < threshold:
                    falsepositive = falsepositive +1

            if i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                fraudRevenue = fraudRevenue + Revenue[i]
                if Tscore[i] < threshold:
                    fraudSaved = fraudSaved + Revenue[i]

                #if Tscore[i] == 0.5:
                #    nullfalsepositive = nullfalsepositive+1
        '''
        for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
            fraudRevenue = fraudRevenue + Revenue[i]
            if Tscore[i] < threshold:
                fraudSaved = fraudSaved + Revenue[i]
        '''
        #fraudAverageRevenue = (fraudRevenue-fraudSaved)/(ProviderConfig.n_fraudsters/ProviderConfig.n_cluster_size)
        #if fraudsters == 0:
        #    pass
        #else:
        fraudAverageRevenue = float(fraudRevenue)/ fraudsters


        fraudBehaviour = 100*(bad/(bad+good)) #tasso di transazioni positive per nodo frodatore
        reportRate = (100*reports_counter)/reports_counter_ref #tasso di risposta per nodi transizione nel campione

        fraudRate=  (100*frauds_counter)/TraceConfig.n_call_fraud #tasso di frodi conosciute (rilevate) nel campione

        pDetect = (fraudsters*100) / ProviderConfig.n_fraudsters
        pFalsepositive = (100*(falsepositive))/(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)
        pFalsenegative = (100*(falsenegative))/ProviderConfig.n_fraudsters
        

        revenue_before_detect = TraceConfig.n_call_fraud*FraudType.bypass_revenue*6
        pDetect2 = float(fraudsters) / ProviderConfig.n_fraudsters
        revenue_after_detect = revenue_before_detect - revenue_before_detect*pDetect2 
        revenue_per_minute_after_detect = revenue_after_detect / (TraceConfig.n_call_fraud*6)
        


        print("fraud analyzed: " + str(fraudRate))
        print("fraud behaviour: " + str(fraudBehaviour))

        print("fraud revenue, before: " + str(revenue_before_detect) + " after: " + str(revenue_after_detect))
        print("revenue per minute after detect: "+str(revenue_per_minute_after_detect))

        
        #print("fraudsters detection max probability: " + str(reportRate))

        print("fraudsters: " +str(fraudsters)+ "/" + str(ProviderConfig.n_fraudsters)+ " suspicious: " + str(temporary_fraudsters)+ "/" + str(ProviderConfig.n_fraudsters) +" undetected: " +  str(undetected) + "/" + str(ProviderConfig.n_fraudsters)+" percentage: "+ str(pDetect))
        print("false negative: " + str(falsenegative) + "/" + str(ProviderConfig.n_fraudsters) + " percentage: "+str(pFalsenegative))
        print("false positive: " + str(falsepositive) + "/" + str(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters) + " percentage: " +str(pFalsepositive))




        #df=pd.DataFrame({'data1':data1, 'data2':data2, 'data3':data3})
        #df.plot(kind='bar', stacked=True)
        '''
        if Result.graph2:
            N = ProviderConfig.n_intermidiaries;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            std = [0 for s in range(N)]

            fig, ax = plt.subplots()
            #rects1 = ax.bar(ind, fp_ref, width, color='black', yerr=std)
            rects2 = ax.bar(ind+0*width, fp_worstcase, width, color='darkred', yerr=std)
            rects3 = ax.bar(ind+1*width, fp_pretrust, width, color='firebrick', yerr=std)
            rects4 = ax.bar(ind+2*width, fp_simmetry, width, color='tomato', yerr=std)
            rects5 = ax.bar(ind+3*width, fp_cluster, width, color='r', yerr=std)

            # add some text for labels, title and axes ticks

            ax.set_ylabel('false-positive [%]')
            ax.set_xlabel('nodes')
            ax.set_title('false-positive reduction in percentage')
            #ax.set_xticks(ind+width/4)
            #ax.set_xticklabels(('G1', 'G2'))

            ax.legend((rects2[0], rects3[0], rects4[0],rects5[0] ), ('worst-case', 'pre-trust','symmetry','clustering'))
        '''
        if Result.graph1:
            reputations =  [0 for s in range(ProviderConfig.n_intermidiaries)]
            for i in range(ProviderConfig.n_intermidiaries):
                reputations[i] = Tscore[i+ProviderConfig.n_providers]
            N = ProviderConfig.n_intermidiaries;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            std = [0 for s in range(N)]
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind, reputations, width, color='b', yerr=std)
            # add some text for labels, title and axes ticks
            ax.set_ylabel('reputation [0-100]')
            #ax.set_xlabel('nodes')
            ax.set_title('Global reputation')
            #ax.set_xticks(ind + width / 2)
            #ax.set_xticklabels(('N1', 'N2', 'N3', 'N4', 'N5','N6', 'N7', 'F' ))
            ax.plot([0., N], [threshold, threshold], "k--")
            plt.text(6.3, threshold+0.01, 'honest threshold', fontsize=12)
            plt.show()


        if Result.graph3:
            N = ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            std = [0 for s in range(N)]
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind, Revenue, width, color='r', yerr=std)
            ax.set_ylabel('fraud revenues in Euro')
            ax.set_title('False-positive and fraudster revenue compared')
            plt.show()


        if Result.graph4:
            N = 4;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            fig, ax = plt.subplots()
            rects2 = ax.bar(ind+0*width, pDetect, width, color='darkred', yerr=0)
            rects3 = ax.bar(ind+1*width, pFalsepositive, width, color='firebrick', yerr=1)
            rects4 = ax.bar(ind+2*width, pFalsenegative, width, color='tomato', yerr=2)
            rects5 = ax.bar(ind+3*width, fraudRevenuePercentage, width, color='r', yerr=3)
            ax.set_ylabel('false-positive [%]')
            ax.set_xlabel('nodes')
            ax.set_title('false-positive reduction in percentage')
            ax.legend((rects2[0], rects3[0], rects4[0],rects5[0] ), ('worst-case', 'pre-trust','symmetry','clustering'))
            plt.show()


        def autolabel(rects):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        '%d' % int(height),
                        ha='center', va='bottom')


        v = [fraudBehaviour, pDetect, pFalsepositive, pFalsenegative, fraudAverageRevenue, fraudsters]
        return v


    @staticmethod
    def printRes(matrix):
        ''' T score '''
        Ts = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        #Trow = [[0 for k in range(2)] for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            pos = 0
            neg = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + matrix[i][j][0]
                neg = neg + matrix[i][j][1]
            #Trow[j][0] = pos
            #Trow[j][1] = neg
            Ts[j] = (1.0+pos)/(2.0+pos+neg)
        return Ts

    @staticmethod
    def calcRevenue(trace):
        r_bypass = (trace["rateA"]-trace["rateB"])*trace["durationA"]
        #r_bypass = FraudType.bypass_revenue * trace["durationA"]
        r_fas = (trace["durationA"] - trace["durationB"])*trace["rateA"]
        r_lrn = (trace["rateB"]-trace["rateA"])*trace["durationA"]
        r = 0

        if FraudType.fas_fraud:
            r = r_fas
        if FraudType.bypass_fraud:
            r = r_bypass
        if FraudType.bypass_fraud and FraudType.fas_fraud:
            r = r_bypass + r_fas
        if FraudType.lrn_fraud:
            r = r_lrn

        return r
