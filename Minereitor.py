from Tkinter import *
import Tkinter as tk
import Tkinter, Tkconstants, tkFileDialog
import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import math
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import single, fcluster
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster import hierarchy as hc
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.width', None)



     
class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, bg='#3F6EBF',bd=0, highlightthickness=0, relief='solid', *args, **kwargs )
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill='#EAEAEA')
            i = self.textwidget.index("%s+1line" % i)


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) ||
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))


class Example(tk.Frame):

    """
         Parte central do código

        -----------------------------------------------

         Variáveis
         text = área de escrita do código
         response = área de exibição de erros
    """

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.filename = ''

        self.text = CustomText(self, bg='#152540', bd=0, padx=12, foreground='#EAEAEA',
                               highlightthickness=0, relief='ridge')
        self.vsb = tk.Scrollbar(
            orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.tag_configure("bigfont", font=("'Fira Code'", "30", "bold"))
        self.linenumbers = TextLineNumbers(self, width=27)
        self.linenumbers.attach(self.text)

        self.response = tk.Text(root, bg='#2A4980', bd=0, padx=9, pady=6, foreground='#EAEAEA',
                                highlightthickness=0, relief='ridge')
        self.response.config(state='disable')
        self.scroll = tk.Scrollbar(self.response,
                                   orient="vertical", command=self.response.yview)
        self.scroll.pack(side='right', fill='y')
        self.response.pack(side='bottom', fill="both", expand=True)

        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

        menu = tk.Menu(root)
        menu.option_add('*tearOff', False)
        root.config(menu=menu)
        itensSave = tk.Menu(menu)

        itensCod = tk.Menu(menu)

        itensSave.add_command(label='Abrir (ctrl+o)', command=self.abrirCodigo)
        itensSave.add_command(label='Salvar (ctrl+s)',
                              command=self.salvarCodigo)
        itensSave.add_command(
            label='Novo código (ctrl+n)', command=self.limpar)
        itensCod.add_command(label='Escalonador (F5)', command=self.run)
        itensCod.add_command(label='Correla��o (F6)', command=self.cor)
        itensCod.add_command(label='Dendograma (F7)', command=self.dend)

        menu.add_cascade(label='Arquivo', menu=itensSave)
        menu.add_cascade(label='Código', menu=itensCod)
        menu.add_cascade(label='Correla��o', menu=itensCod)

        self.text.bind("<KeyPress>", self.runKey)

    def _on_change(self, event):
        self.linenumbers.redraw()

    def abrirCodigo(self):
   

       # try:
                 self.filename = tkFileDialog.askopenfilename(
                 initialdir = "./",
                 title = "Select file"
                 ,filetypes = (("Arquivos de Texto","*.csv"),
                               ("all files","*.*")))



                 
                 global dados
                 dados = pd.read_csv(self.filename)
                 code = dados
                # file.close()
                 self.text.delete('0.0', 'end')
                 self.response.delete('0.0', 'end')
                 self.text.insert('0.0', code)

       # except:
         #   pass

    def limpar(self):
        """
            "Cria" um novo arquivo, apaga tudo do anterior e limpa a memória
        """

        self.text.delete('0.0', 'end')
        self.response.config(state='normal')
        self.response.delete('0.0', 'end')
        self.response.config(state='disable')
        self.filename = ''

    def salvarCodigo(self):
        global dados
        
        """
             Salva o código, try exception para evitar a escrita de erros
        """

        try:
             name = self.filename
             name = name[0:len(name)-4]
             
             name = name + "Z.csv"
             print name
             dados.to_csv(name)

        except:
            pass

    def run(self):
        """
            Realiza a compilação

        """
        # Salva o c�digo
        self.salvarCodigo()
        # Recebe o que está escrito no campo 'text'
        code = self.text.get('0.0', 'end')
        self.response.config(state='normal')

        # Limpa os erros anteriores
        self.response.delete('0.0', 'end')

        # Executa a análise e recebe o erro
        #escalonador(self.filename)
        
        
                   

        
            

        # code = string com os erros encontrados no código

        self.response.insert('end', zscore())
        self.response.config(state='disable')
    def cor(self):
         corr,frames = correl()
         corr = corr.round(2)
         
         self.response.config(state='disable')
         
         self.response.config(state='normal')


         self.response.delete('0.0', 'end')
         self.response.insert('end', "Matriz de Correla��o \n")
         self.response.insert('end', corr)
         self.response.config(state='disable')

         for f in(frames):
               x,y = list(f.columns.values)
               print x,y
               f.plot.scatter(x=x,y=y)
         plt.show()
    def dend(self):
          dendo()
          self.response.config(state='disable')
              
         

    def runKey(self, e):
        """
            Define qual ação realizar conforme as teclas apertadas
        """
        if (e.keycode == 116):
            self.run()
        elif(e.keycode == 117):
            self.cor()
        elif(e.keycode == 118):
            self.dend()    
            
        elif (e.char == '\x13'):
            self.salvarCodigo()
        elif (e.char == '\x0e'):
            self.limpar()
        elif (e.char == '\x0f'):
            self.abrirCodigo()

def zscore():
     global dados,dados_cor
     df = dados.select_dtypes(['number'])
     dados_cor = df
     try:
      df = df.drop("ID", axis=1)
     except:
      df = df
     df_zscore = (df - df.mean())/df.std()
     df_zscore = df_zscore.apply(lambda x: x.abs(), axis=1)
     df_zscore = df_zscore.round(2)
     #print df_zscore
     return df_zscore

def correl():
     global dados,corr
     df = zscore()
     corr = dados_cor.corr()

     
 

     listacolunas = list(corr.columns.values)
     yx  = len(listacolunas) -1
     y = listacolunas[yx]
    # print y 
     colunas = []
     cort = corr[[y]]
     #print cort

     colunas = (cort[y] >= 0.4)&(cort[y] != 1)
     dc = cort[colunas]
 
     select = list(dc.index)
     #select.append(y)
     #jesus = dados[select]
     #print jesus

     frames = []

     for c in (select):
          s = [c,y]
          frames.append(dados[s])
          


          
    
  
     return corr,frames


def dendo():

     df = zscore()
     corr = 1- dados_cor.corr()

     corr_condensed = hc.distance.squareform(corr) # convert to condensed
     z = hc.linkage(corr_condensed, method='average')
     dendrogram = hc.dendrogram(z, labels=corr.columns)
     plt.show()
     
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mineirator")
    Example(root).pack(side="top", fill="both", expand=True)

    root.mainloop()
