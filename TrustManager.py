import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
#import pandas as pd
#import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
#matplotlib.style.use('ggplot')
#from pandas import DataFrame
from config import ProviderConfig, TraceConfig, TrustConfig

class TrustManager:


    @staticmethod
    def computeTrust():
        ''' referenze without false-positive cases '''
        Ref = [[ 0 for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        Tref = [0 for m in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]

        frauds = 0
        M = [[[0 for k in range(2)] for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)] for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries)]
        with open(TraceConfig.file_path) as f:
            data = json.load(f)
        traces = data["traces"]
        for trace in traces:
            if trace["fraud"] == 0:
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    M[source][target][0] = M[source][target][0] + 1
                    Ref[source][target] = Ref[source][target] +1
            else:
                frauds = frauds +1
                for i in range(len(trace["transit"])-1):
                    source = trace["transit"][i]["id"]
                    target = trace["transit"][i+1]["id"]
                    M[source][target][1] = M[source][target][1] + 1
                    #if target in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters):
                    Ref[source][target] = Ref[source][target] +1

        for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
            pos = 0
            for i in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                pos = pos + Ref[i][j]
            Tref[j] = (1.0+pos)/(2.0+pos) #neg = 0
        print ("\nReference score:")
        print (Tref)


        print ("\nFirst trust score:")
        Treal = TrustManager.printRes(M)

        ''' preTrust ''' 
        if TrustConfig.pretrust_strategy:
            for trace in traces:
                if trace["fraud"] == 1:
                    for i in range(len(trace["transit"])-1):
                            source = trace["transit"][i]["id"]
                            target = trace["transit"][i+1]["id"]
                            discount = 0
                            if i < TraceConfig.l_cascade_agreements and target not in range(ProviderConfig.n_providers + ProviderConfig.n_intermidiaries - ProviderConfig.n_fraudsters, ProviderConfig.n_providers + ProviderConfig.n_intermidiaries-1):
                                discount = 1.0 / (i+1)
                            M[source][target][1] = M[source][target][1] - discount
            print ("\nPre trust:")
            Tpretrust = TrustManager.printRes(M)



        ''' simmetry '''
        if TrustConfig.symmetry_strategy:
            for j in range(ProviderConfig.n_providers+ProviderConfig.n_intermidiaries):
                for i in range(j+1):
                    discount = min(M[i][j][1],M[j][i][1])
                    M[i][j][1] = M[i][j][1] - discount
                    M[j][i][1] = M[j][i][1] - discount
            print ("\nSimmetry:")
            Tsimmetry = TrustManager.printRes(M)

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
            l_groups = ProviderConfig.n_intermidiaries / ProviderConfig.n_cluster_size
            Tgroup = [0 for g in range(l_groups)]
            for group in range( l_groups  ):
                pos = 0
                neg = 0
                for interm in range( group*ProviderConfig.n_cluster_size , (group+1)*ProviderConfig.n_cluster_size ):
                    pos = pos + Trow[interm][0]
                    neg = neg + Trow[interm][1]
                Tgroup[group] = (1.0+pos)/(2.0+pos+neg)
                for peer in range( group*ProviderConfig.n_cluster_size , (group+1)*ProviderConfig.n_cluster_size ):
                    Tscore[peer] = (Tscore[peer] * Tgroup[group]) / ((Tscore[peer] * Tgroup[group]) + ((1-Tscore[peer])*(1-Tgroup[group])))
            print ("\nClustering:")
            Tcluster = Tscore
            print (Tscore)
        #i falsi positivi li calcolo solo per gli onesti
        fp_ref =      [0 for m in range(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)]
        fp_pretrust = [0 for m in range(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)]
        fp_simmetry = [0 for m in range(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)]
        fp_cluster =  [0 for m in range(ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters)]
        for i in range(ProviderConfig.n_providers, ProviderConfig.n_providers+ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters):
            fp_ref[i-ProviderConfig.n_providers]      = (Tref[i] - Treal[i])*100
            fp_pretrust[i-ProviderConfig.n_providers] = (Tref[i] - Tpretrust[i])*100
            fp_simmetry[i-ProviderConfig.n_providers] = (Tref[i] - Tsimmetry[i])*100
            fp_cluster[i-ProviderConfig.n_providers]  = (Tref[i] - Tcluster[i])*100

        print ("\n\nFalse positive reference:")
        print (fp_ref)
        print ("\nFalse positive reduction with Pretrust:")
        print (fp_pretrust)
        print ("\nFalse positive reduction with Simmetry:")
        print (fp_simmetry)
        print ("\nFalse positive reduction with Cluster:")
        print (fp_cluster)


       

        #df=pd.DataFrame({'data1':data1, 'data2':data2, 'data3':data3})
        #df.plot(kind='bar', stacked=True)
        N = ProviderConfig.n_intermidiaries-ProviderConfig.n_fraudsters;
        ind = np.arange(N)  # the x locations for the groups
        width = 0.2    # the width of the bars
        std = [0 for s in range(N)]

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, fp_ref, width, color='m', yerr=std)
        rects2 = ax.bar(ind + width, fp_pretrust, width, color='b', yerr=std)
        rects3 = ax.bar(ind+2*width, fp_simmetry, width, color='g', yerr=std)
        rects4 = ax.bar(ind+3*width, fp_cluster, width, color='r', yerr=std)

        # add some text for labels, title and axes ticks
        ax.set_ylabel('false-positive reports %')
        ax.set_title('Honest intermidiaries')
        #ax.set_xticks(ind + width / 2)
       # ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))

        ax.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('worst-case', 'pre-trust','symmetry','clustering'))


        def autolabel(rects):
            """
            Attach a text label above each bar displaying its height
            """
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        '%d' % int(height),
                        ha='center', va='bottom')

        autolabel(rects1)
        autolabel(rects2)

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
        print (Ts)
        print (Trow)
        return Ts
