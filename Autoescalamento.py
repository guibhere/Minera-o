# -*- coding: cp1252 -*-
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import math
import pandas as pd

#Lendo do Banco de DADOS-----------------------------------------------
reader = csv.reader(open('dados_chefes.csv', 'rb'),delimiter=',')
lista = list(reader)
base = np.array(lista)
dados  = pd.read_csv('dados_chefes.csv')
#-----------------------------------------------------------------------


z = []
z1 = []
z2 = [] 

desv = dados['Salario'].std()
med = dados['Salario'].mean()
desva = dados['carga_horaria'].std()
meda = dados['carga_horaria'].mean()
desvb = dados['lucratividade'].std()
medb = dados['lucratividade'].mean()

for i in range(len(lista)):
    if(i!=0):
        z.append((float(lista[i][2]) - med)/desv)
        z1.append((float(lista[i][4]) - meda)/desva)
        z2.append((float(lista[i][10]) - medb)/desvb)
        
dados['Salario'] = z
dados['carga_horaria'] = z1
dados['lucratividade'] = z2

print dados
dados.to_csv('Znormal.csv')


