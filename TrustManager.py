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
        Ref = [[ 0 for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        Tref = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        n_groups = (ProviderConfig.n_providers+ProviderConfig.n_intermidiaries) / ProviderConfig.n_cluster_size
        Tinit = [1 for g in range(n_groups)]
        Revenue = [0 for g in range(n_groups)]
        fraudsters_behaviour = [[0 for k in range(2)] for i in range(ProviderConfig.n_fraudsters)]
        #Revenue = [0 for g in range(ProviderConfig.n_intermidiaries+ProviderConfig.n_providers)]
        frauds = 0
        M = [[[0 for k in range(2)] for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        with open(TraceConfig.file_path) as f:
            data = json.load(f)
        traces = data["traces"]



        for trace in traces:

            if trace["fraud"]==0:
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][0] = M[origin][nextop][0] + 1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    M[source][target][0] = M[source][target][0] + 1
                    Ref[source][target] = Ref[source][target] +1

            else:
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][1] = M[origin][nextop][1] + 1
                frauds = frauds +1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    M[source][target][1] = M[source][target][1] + 1 
                    #Revenue[target] = Revenue[target] +  TrustManager.calcRevenue(trace)
                    Revenue[target/ProviderConfig.n_cluster_size] = Revenue[target/ProviderConfig.n_cluster_size] + TrustManager.calcRevenue(trace)



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
                                Tinit[n_groups-1] = 0.1#TODO aggiusta


                    #if target in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters):
                    Ref[source][target] = Ref[source][target] +1


        for j in range(ProviderConfig.n_fraudsters):
            pos = 0
            neg = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + M[i][j+ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters][0]
                neg = neg + M[i][j+ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters][1]
            fraudsters_behaviour[j][0] = pos
            fraudsters_behaviour[j][1] = neg
        fraud_behaviour = 0
        for f in fraudsters_behaviour:
            if f[1] == 0 and f[0]==0:
                #previeni divisione zero, inserisvi v neutro
                v=50
            else:
                v=(100*f[0])/(f[0]+f[1])
            fraud_behaviour = fraud_behaviour+v #la percentuale di chiamate oneste rispetto a quelle negative
        fraud_behaviour = fraud_behaviour / ProviderConfig.n_fraudsters

        #print(fraudsters_behaviour)


        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters):
            pos = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + Ref[i][j]
            Tref[j] = (1.0+pos)/(2.0+pos) #neg = 0
        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            Tref[j] = 0
        #print ("\nReference score:")
        #print (Tref)


        
        Tworstcase = TrustManager.printRes(M)
        #print ("\nWorst case:")
        #print(Tworstcase)

        ''' preTrust ''' 
        if TrustConfig.pretrust_strategy:
            for trace in traces:
                if trace["fraud"] == 1:
                    ''' sconto da operatore di origine a primo intermediario '''
                    origin = trace["origin"]
                    nextop = trace["transit"][0]["id"]
                    if TrustConfig.l_cascade_agreements > 0 and nextop not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries):
                        M[origin][nextop][1] = M[origin][nextop][1] - 1
                        #Revenue[nextop] = Revenue[nextop] -  TrustManager.calcRevenue(trace)
                        Revenue[nextop/ProviderConfig.n_cluster_size] = Revenue[nextop/ProviderConfig.n_cluster_size] -  TrustManager.calcRevenue(trace)
                    ''' sconto da intermmediario a intermediario successivo '''
                    for i in range(len(trace["transit"])-1):
                            source = trace["transit"][i]["id"]
                            target = trace["transit"][i+1]["id"]
                            discount = 0
                            if i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries):
                                discount = 1.0 / (i+2)
                            M[source][target][1] = M[source][target][1] - discount
                            Revenue[target/ProviderConfig.n_cluster_size] =  Revenue[target/ProviderConfig.n_cluster_size] -  TrustManager.calcRevenue(trace)*(1.0/(2.0+i))
                            #Revenue[target] =  Revenue[target] -  TrustManager.calcRevenue(trace)*(1.0/(1.0+i))
           


            Tpretrust = TrustManager.printRes(M)
            #print ("\nPre trust:")
            #print(Tpretrust)



        ''' simmetry '''
        if TrustConfig.symmetry_strategy:
            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                for i in range(j+1):
                    discount = min(M[i][j][1],M[j][i][1])
                    M[i][j][1] = M[i][j][1] - discount
                    M[j][i][1] = M[j][i][1] - discount

            
            Tsimmetry = TrustManager.printRes(M)
            #print ("\nSimmetry:")
            #print(Tsimmetry)

        ''' aggregate by target '''
        Trow = [[0 for k in range(2)] for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        Tscore = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            pos = 0
            neg = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + M[i][j][0]
                neg = neg + M[i][j][1]
            Trow[j][0]=pos
            Trow[j][1]=neg
            Tscore[j] = (1.0+pos)/(2.0+pos+neg)
            

        ''' combine within cluster '''
        if TrustConfig.clustering_strategy:

            Tscore = TrustManager.printRes(M)
            
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


        if TrustConfig.symmetry_strategy  and TrustConfig.pretrust_strategy and TrustConfig.clustering_strategy:

            #i falsi positivi li calcolo solo per gli onesti
            fp_ref =      [0 for m in range(ProviderConfig.n_intermidiaries)]
            fp_worstcase =[0 for m in range(ProviderConfig.n_intermidiaries)]
            fp_pretrust = [0 for m in range(ProviderConfig.n_intermidiaries)]
            fp_simmetry = [0 for m in range(ProviderConfig.n_intermidiaries)]
            fp_cluster =  [0 for m in range(ProviderConfig.n_intermidiaries)]
            for i in range(ProviderConfig.n_intermidiaries):
                fp_worstcase[i]= (Tref[i+ProviderConfig.n_providers]-Tworstcase[i+ProviderConfig.n_providers])*100
                fp_pretrust[i] = (Tref[i+ProviderConfig.n_providers]-Tpretrust[i+ProviderConfig.n_providers])*100
                fp_simmetry[i] = (Tref[i+ProviderConfig.n_providers]-Tsimmetry[i+ProviderConfig.n_providers])*100
                fp_cluster[i]  = (Tref[i+ProviderConfig.n_providers]-Tscore[i+ProviderConfig.n_providers])*100
      

        #print ("\n\nFalse positive reference:")
        #print (fp_ref)
        #print ("\nFalse positive reduction with Pretrust:")
        #print (fp_pretrust)
        #print ("\nFalse positive reduction with Simmetry:")
        #print (fp_simmetry)
        #print ("\nFalse positive reduction with Cluster:")
        #print (fp_cluster)

        #print("revenue", Revenue)

        #print("\nSybil final score:" + str(Tscore[ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-1]))

        
        
        weights = [0 for s in range(ProviderConfig.n_intermidiaries)]
        for i in range(ProviderConfig.n_intermidiaries):
            if Tscore[i+ProviderConfig.n_providers] <= 0.5:
                weights[i] = 0
            else:
                weights[i] = Tscore[i+ProviderConfig.n_providers] - 0.5
        numeratore = 0
        denominatore = 0
        for  i in range(ProviderConfig.n_intermidiaries):
            numeratore = numeratore + Tscore[i+ProviderConfig.n_providers]*weights[i]
            denominatore = denominatore + weights[i]
        average = numeratore / denominatore
        x=0
        for  i in range(ProviderConfig.n_intermidiaries):
            if Tscore[i+ProviderConfig.n_providers] > 0.5:
                x = x+(Tscore[i+ProviderConfig.n_providers] - average)**2
        x = x / (ProviderConfig.n_intermidiaries)
        standarddev = math.sqrt(x)
        threshold = average - standarddev #- 0.003
        #print("\nthreshold: " + str(threshold))



        '''
        n_groups2 = ProviderConfig.n_intermidiaries / ProviderConfig.n_cluster_size
        revenue2 = [0 for i in range(n_groups2)]
        for i in range(n_groups2):
            revenue2[i] = Revenue[i+ProviderConfig.n_providers/ProviderConfig.n_cluster_size]

        print revenue2

       
        y_medium = 0
        for i in range(n_groups2):
            y_medium = y_medium + revenue2[i]
        y_medium = y_medium / n_groups2
        print("medio pre gradiente: " + str(y_medium))
        d = 0
        for i in range(n_groups2):
            d = d + (revenue2[i]-y_medium)**2

        go = True

        cmax = 50
        c = 0
        y_medium = y_medium - 5
        inc  = 1
        old = d
        while(c < cmax):
            c = c + 1
            new = 0
            for i in range(n_groups2):
                new = new + (revenue2[i]-(y_medium))**2
            

            if new < old:
                print("+"+str(new))
                y_medium = y_medium + 2

            if old < new:
                print("-"+str(old))
                y_medium = y_medium  -2
            if new == old:
                print("=")
                c = cmax
        '''      
                
                


        '''
        fraudsters_behaviour = [[0 0] for i in range(ProviderConfig.n_fraudsters)]
        for trace in traces:
            for peer in trace["transit"]:
                if peer["id"] in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                    if 
        '''




        
        flasepositive = 0
        falsenegative = 0
        fraudsters = 0
        for i in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            if Tscore[i] < threshold and i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                fraudsters = fraudsters +1
            if Tscore[i] < threshold and i not in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                flasepositive = flasepositive +1 

            if Tscore[i] >= threshold and i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                falsenegative = falsenegative +1

        fraudLosses = 0
        fraudSaved = 0

        fraudGroups = ProviderConfig.n_fraudsters / ProviderConfig.n_cluster_size

        if TrustConfig.clustering_strategy:
            for i in range(n_groups-fraudGroups-1, n_groups):
                fraudLosses = fraudLosses + Revenue[i]
                #print("group" + str(Tgroup[i]))
                if Tgroup[i] < threshold:
                    fraudSaved = fraudSaved + Revenue[i]
        Loss = 100*(fraudLosses-fraudSaved)/fraudLosses


        fraudstersPercentage = (fraudsters * 100) / ProviderConfig.n_fraudsters
        falsepositivePercentage = (flasepositive * 100)/ProviderConfig.n_intermidiaries
        falsenegativePercentage = (falsenegative * 100)/ProviderConfig.n_fraudsters
        


        print("\nConfig:")
        print("fraudsters: " + str(ProviderConfig.n_fraudsters*100/ProviderConfig.n_intermidiaries)+"%")
        print("fraud calls: " + str(TraceConfig.n_call_fraud*100/TraceConfig.n_call)+"%")
        print("Fraudsters honesty behaviour: " + str(fraud_behaviour) +"%")

        print("\nResults:")
        print("Fraudsters revealed: "+ str(fraudstersPercentage)+"%")
        print("False positive: "+ str(falsepositivePercentage)+"%")
        print("False negative: "+ str(falsenegativePercentage)+"%")
        print("Economic Loss: " + str(Loss)+" %")




        #df=pd.DataFrame({'data1':data1, 'data2':data2, 'data3':data3})
        #df.plot(kind='bar', stacked=True)

        if Result.graph2:
            N = ProviderConfig.n_intermidiaries;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            std = [0 for s in range(N)]

            fig, ax = plt.subplots()
            #rects1 = ax.bar(ind, fp_ref, width, color='black', yerr=std)
            '''
            rects2 = ax.bar(ind+0*width, fp_worstcase, width, color='lightgray', yerr=std)
            rects3 = ax.bar(ind+1*width, fp_pretrust, width, color='darkgray', yerr=std)
            rects4 = ax.bar(ind+2*width, fp_simmetry, width, color='dimgray', yerr=std)
            rects5 = ax.bar(ind+3*width, fp_cluster, width, color='gray', yerr=std)
            '''
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
            ax.set_xticks(ind + width / 2)
            ax.set_xticklabels(('N1', 'N2', 'N3', 'N4', 'N5','N6', 'N7', 'F' ))
            ax.plot([0., N], [threshold, threshold], "k--")
            plt.text(6.3, threshold+0.01, 'honest threshold', fontsize=12)

        if Result.graph3:
            #N = ProviderConfig.n_intermidiaries+ProviderConfig.n_providers
            N = n_groups;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            std = [0 for s in range(N)]
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind, Revenue, width, color='r', yerr=std)
            # add some text for labels, title and axes ticks
            ax.set_ylabel('fraud revenues in Euro')
            #ax.set_xlabel('nodes')
            ax.set_title('False-positive and fraudster revenue compared')
            #ax.set_xticks(ind + width / 2)
            #ax.set_xticklabels(('N1', 'N2', 'N3', 'N4', 'N5','N6', 'N7', 'F' ))
            #ax.plot(std, b0 , "k--")
            #plt.text(6.3, threshold+0.01, 'honest threshold', fontsize=12)

        if Result.graph4:
            N = 4;
            ind = np.arange(N)  # the x locations for the groups
            width = 0.2    # the width of the bars
            #std = [0 for s in range(N)]
            fig, ax = plt.subplots()
            rects2 = ax.bar(ind+0*width, fraudstersPercentage, width, color='darkred', yerr=0)
            rects3 = ax.bar(ind+1*width, falsepositivePercentage, width, color='firebrick', yerr=1)
            rects4 = ax.bar(ind+2*width, falsenegativePercentage, width, color='tomato', yerr=2)
            rects5 = ax.bar(ind+3*width, Loss, width, color='r', yerr=3)


            # add some text for labels, title and axes ticks

            ax.set_ylabel('false-positive [%]')
            ax.set_xlabel('nodes')
            ax.set_title('false-positive reduction in percentage')
            #ax.set_xticks(ind+width/4)
            #ax.set_xticklabels(('G1', 'G2'))

            ax.legend((rects2[0], rects3[0], rects4[0],rects5[0] ), ('worst-case', 'pre-trust','symmetry','clustering'))

        def autolabel(rects):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        '%d' % int(height),
                        ha='center', va='bottom')

        #autolabel(rects2)
        #autolabel(rects5)

        plt.show()


    @staticmethod
    def printRes(matrix):
        ''' T score '''
        Ts = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        Trow = [[0 for k in range(2)] for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            pos = 0
            neg = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + matrix[i][j][0]
                neg = neg + matrix[i][j][1]
            Trow[j][0] = pos
            Trow[j][1] = neg
            Ts[j] = (1.0+pos)/(2.0+pos+neg)
        return Ts

    @staticmethod
    def calcRevenue(trace):
        r_bypass = (trace["rateA"]-trace["rateB"])*trace["durationA"]
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
