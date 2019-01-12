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
        #Revenue = [0 for g in range(n_groups)]
        fraudsters_behaviour = [[0 for k in range(2)] for i in range(ProviderConfig.n_fraudsters)]
        Revenue = [0 for g in range(ProviderConfig.n_intermidiaries+ProviderConfig.n_providers)]
        M = [[[0 for k in range(2)] for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        
       
        with open(TraceConfig.file_path) as f:
            data = json.load(f)
        traces = data["traces"]

        for trace in traces:
            #print("participating_providers"+str(participating_providers))
            if trace["fraud"]==0 and trace["termin"] in range(ProviderConfig.n_providers/2-ProviderConfig.provider_participation/2, ProviderConfig.n_providers/2 + ProviderConfig.provider_participation/2):
                #print("+")
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][0] = M[origin][nextop][0] + 1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    if source in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.intermidiaries_participation):
                        M[source][target][0] = M[source][target][0] + 1
                        Ref[source][target] = Ref[source][target] +1

            if trace["fraud"]==1 and trace["termin"] in range(ProviderConfig.n_providers/2-ProviderConfig.provider_participation/2, ProviderConfig.n_providers/2 + ProviderConfig.provider_participation/2):
                origin = trace["origin"]
                nextop = trace["transit"][0]["id"]
                M[origin][nextop][1] = M[origin][nextop][1] + 1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    if source in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries/2-ProviderConfig.intermidiaries_participation/2,ProviderConfig.n_providers+ProviderConfig.n_intermidiaries/2+ProviderConfig.intermidiaries_participation/2):
                        M[source][target][1] = M[source][target][1] + 1
                        Revenue[target] = Revenue[target] +  TrustManager.calcRevenue(trace)
                        #Revenue[target/ProviderConfig.n_cluster_size] = Revenue[target/ProviderConfig.n_cluster_size] + euros
                        #TODO: why ref here
                        Ref[source][target] = Ref[source][target] +1

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


                    #if target in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters):
        

        participating_intermidiaries = ((ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters) * 50)/100
        fraud_detection=0
        fraud_detection_ref = 0
        fraud_detection_percentage = 0
        fraudster_identification = 0
        fraudster_identification_ref = 0
        fraudster_identification_percentage = 0

        study_scenario=False
        if study_scenario:
            for trace in traces:
                if trace["fraud"]!=0: #c'è frode
                    fraud_detection_ref = fraud_detection_ref  + 1 
                    if trace["termin"] in range(0, participating_providers ):
                        fraud_detection = fraud_detection + 1 
                        for i in range(len(trace["transit"])-1):
                            fraudster_identification_ref = fraudster_identification_ref +1
                            if i in range(ProviderConfig.n_providers, ProviderConfig.n_providers + participating_intermidiaries):
                                fraudster_identification= fraudster_identification+1
            if fraudster_identification_ref != 0 and fraud_detection_ref!=0:
                fraud_detection_percentage = ((fraud_detection_ref - fraud_detection)/fraud_detection_ref)*100
                fraudster_identification_percentage = ((fraudster_identification_ref-fraudster_identification)/fraudster_identification_ref)*100
            #print("fraud dection percentage: " + str(fraud_detection_percentage))
            #print("fraudster identification pecentage: " + str(fraudster_identification_percentage))

        '''

        Fraud probability

        '''

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
                pass
            else:
                fraud_behaviour = fraud_behaviour+(100*f[0])/(f[0]+f[1])
            #la percentuale di chiamate oneste rispetto a quelle negative
        fraud_behaviour = fraud_behaviour / ProviderConfig.n_fraudsters
        print("fraudster honesty behaviour " + str(fraudsters_behaviour))


        '''
        
        Reputation before false positive reduction

        '''

        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters):
            pos = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + Ref[i][j]
            Tref[j] = (1.0+pos)/(2.0+pos) #neg = 0
        #da togliere, ridurre il vettore!!
        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            Tref[j] = 0
        #print ("\nReference score:")
        #print (Tref)


        
        Tworstcase = TrustManager.printRes(M)
        #print ("\nWorst case:")
        #print(Tworstcase)

        '''

        preTrust 

        ''' 

        if TrustConfig.pretrust_strategy:
            for trace in traces:
                if trace["fraud"] == 1:
                    ''' sconto da operatore di origine a primo intermediario '''
                    origin = trace["origin"]
                    nextop = trace["transit"][0]["id"]
                    if TrustConfig.l_cascade_agreements > 0 and nextop not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[origin][nextop][1]>0:
                        M[origin][nextop][1] = M[origin][nextop][1] - 1
                        Revenue[nextop] = Revenue[nextop] -  TrustManager.calcRevenue(trace)
                        #Revenue[nextop/ProviderConfig.n_cluster_size] = Revenue[nextop/ProviderConfig.n_cluster_size] -  TrustManager.calcRevenue(trace)
                    ''' sconto da intermmediario a intermediario successivo '''
                    for i in range(len(trace["transit"])-1):
                            source = trace["transit"][i]["id"]
                            target = trace["transit"][i+1]["id"]
                            discount = 0
                            if i < TrustConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries) and M[source][target][1]>0:
                                discount = 1.0 / (i+2)
                            M[source][target][1] = M[source][target][1] - discount
                            #Revenue[target/ProviderConfig.n_cluster_size] =  Revenue[target/ProviderConfig.n_cluster_size] -  TrustManager.calcRevenue(trace)*(1.0/(2.0+i))
                            Revenue[target] =  Revenue[target] - TrustManager.calcRevenue(trace)*(1.0/(1.0+i))
           


            Tpretrust = TrustManager.printRes(M)
            #print ("\nPre trust:")
            #print(Tpretrust)



        ''' 

        simmetry 

        '''

        if TrustConfig.symmetry_strategy:
            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                for i in range(j+1):
                    discount = min(M[i][j][1],M[j][i][1])
                    M[i][j][1] = M[i][j][1] - discount
                    M[j][i][1] = M[j][i][1] - discount

            
            Tsimmetry = TrustManager.printRes(M)
            #print ("\nSimmetry:")
            #print(Tsimmetry)

        ''' 

        Group reputation


        '''
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
            

        ''' 

        cluster strategy

        '''


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




        '''


        RESULT



        '''



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

        
        falsepositive = 0
        falsenegative = 0
        fraudsters = 0
        nullfalsepositive = 0
        nullfalsenegative = 0
        
        for i in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):

            if Tscore[i] < threshold and i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                print("fraudster is: " + str(i) + " with score values: " +  str(Tscore[i]) +"<"+str(threshold))
                fraudsters = fraudsters +1
            if Tscore[i] < threshold and i not in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                falsepositive = falsepositive +1 

            if Tscore[i] > threshold and i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                falsenegative = falsenegative +1

            if Tscore[i] == 0.5 and i not in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                nullfalsepositive = nullfalsepositive+1

            if Tscore[i] == 0.5 and i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                nullfalsenegative = nullfalsenegative +1

        
        '''
        for i in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            #fraudsters
            if i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                isFraud = False
                if Tscore[i] < 0.5:
                    isFraud = True
                if Tscore[i] < threshold:
                    isFraud = True
                if isFraud:
                    fraudsters = fraudsters + 1
                else:
                    falsenegative = falsenegative +1
            else:
                if Tscore[i] < threshold:
                    flasepositive=flasepositive+1
        '''

        
        print ("detected frauds raw data:"+str(fraudsters))
        print ("fp raw data:"+str(falsepositive) + " null fp " + str(nullfalsepositive))
        print ("fn raw data:"+str(falsenegative)+ " null fn " + str(nullfalsenegative))
        fraudstersPercentage = (fraudsters * 100) / ProviderConfig.n_fraudsters
        falsepositivePercentage = (falsepositive * 100)/ProviderConfig.n_intermidiaries
        falsenegativePercentage = (falsenegative * 100)/ProviderConfig.n_fraudsters


        '''
        if TrustConfig.revenue_strategy:
            AverageRevenue = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                AverageRevenue = AverageRevenue + Revenue[i]
            AverageRevenue = AverageRevenue / ProviderConfig.n_fraudsters
        '''

        fraudLosses = 0
        fraudSaved = 0
        if TrustConfig.revenue_strategy:
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters,ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries):
                fraudLosses = fraudLosses + Revenue[i]
                if Tscore[i] < threshold:
                    fraudSaved = fraudSaved + Revenue[i]

        fraudAverageRevenue = (fraudLosses-fraudSaved)/(ProviderConfig.n_fraudsters/ProviderConfig.n_cluster_size)

        if fraudLosses == 0:
            Loss = 0
        else:
            Loss = 100*(fraudLosses-fraudSaved)/fraudLosses

        RevenuePercentage = 100-Loss



        

        '''
        print("\nConfig:")
        #print("fraudsters: " + str(ProviderConfig.n_fraudsters*100/ProviderConfig.n_intermidiaries)+"%")
        #print("fraud calls: " + str(TraceConfig.n_call_fraud*100/TraceConfig.n_call)+"%")
        print("Fraudsters honesty behaviour: " + str(fraud_behaviour) +"%")
        print("Fraudsters revealed: "+ str(fraudstersPercentage)+"%")
        print("False positive: "+ str(falsepositivePercentage)+"%")
        print("False negative: "+ str(falsenegativePercentage)+"%")
        print("Fraud average revenue: " + str(RevenuePercentage))
        print("Economic Loss: " + str(Loss)+" %")
        '''



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
            N = ProviderConfig.n_providers+ ProviderConfig.n_intermidiaries;
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
        v = [fraud_behaviour, fraudstersPercentage, RevenuePercentage, Loss, falsepositivePercentage, falsenegativePercentage, fraudAverageRevenue]
        return v


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
