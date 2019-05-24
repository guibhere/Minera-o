# -*- coding: cp1252 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
from sklearn.cluster import KMeans
import math
from scipy.cluster.hierarchy import single, fcluster
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import dendrogram, linkage

#Lendo do Banco de DADOS-----------------------------------------------
reader = csv.reader(open('matrix.csv', 'rb'),delimiter=':')
lista = list(reader)
base = np.array(lista)
#-----------------------------------------------------------------------



Dist=[]
for i in range(6):
    D = []
    if(i!=0):
        for j in range(6):
            d=0
            if(j!=0):
                for k in range(5):
                    if(k!=0):
                        d =  d+ (math.pow((float(base[k][j]) - float(base[k][i])),2))

                        
                D.append(round(math.sqrt(d),2))
        Dist.append(D)


Z = linkage(pdist(Dist), method='single')
fig = plt.figure(figsize=(25, 10))
dn = dendrogram(Z)
plt.show("Clustering")
