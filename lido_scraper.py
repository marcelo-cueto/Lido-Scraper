#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from requests import Session

from bs4 import BeautifulSoup as bs

import os

from datetime import datetime, date, time, timedelta

from selenium import webdriver

from selenium.webdriver.support.ui import Select

import shutil

import re

import pandas as pd

import numpy as np

from time import sleep

from PyPDF2 import PdfFileReader, PdfFileWriter

from pikepdf import Pdf, Page

from os import remove

from datetime import date

import pdfplumber ##libreria para trabajar con pdf


# In[ ]:


base='https://viewer.flightsupport.com'

url="https://viewer.flightsupport.com/frames/login.html"


# Configuro Profile para descargar

# In[ ]:


direccionActual=os.path.abspath(os.getcwd())


# In[ ]:


chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("no-sandbox")
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--headless")
#driver = os.path.join("/opt/odoo/procedimientos/","chromedriver")
chrome_options.add_experimental_option('prefs',{
"download.default_directory": direccionActual,
"download.prompt_for_download": False, # Para que el navegador no pregunte al descargar
"plugins.always_open_pdf_externally": True})


# In[ ]:


## crea una instancia para firefox e indica el pah donde se encuentra geckodriver ademas de implementar Profile !!!!FIREFOX!!!!
##driver = webdriver.Firefox(executable_path='/home/marce/Documents/lido/geckodriver',firefox_profile=fp)


# In[ ]:


driver = webdriver.Chrome(executable_path='chromedriver',options=chrome_options)


# ### Ingresando a la pagina!!

# In[ ]:


##conecta con la pagina
driver.get (url)
sleep(2)


# In[ ]:


driver.find_element_by_name("username").send_keys("AerolineasArgentinas") ## busco elemento por name y agrego valor de usuario

driver.find_element_by_name ("password").send_keys("")  ## busco elemento por name y agrego valor de password

element=driver.find_element_by_name("login")## busco elemento name login

element.submit()##le doy submit// existe click() pero solo toma si forma parte de un form ( este esta en js)
sleep(2)


# In[ ]:


driver.get("https://viewer.flightsupport.com/frames/configuration.jsp")##ingreso a la pagina de configuracion
bsObj = bs(driver.page_source, 'html.parser')## para ver mejor el html


# In[53]:


select = Select(driver.find_element_by_id("aircraft"))## busco select por id

select.select_by_value('OFFICE')## selecciono el valor


# In[54]:


select_fr = Select(driver.find_element_by_id("airline")) ## chequear en nva revision, hacer que elija automaticamente la fecha mas nva
driver.find_element_by_id("airline").text


# In[55]:


ahora = datetime.now() 

mes=str(ahora.month) ##hago string el numero del mes actual


# In[56]:



month = Select(driver.find_element_by_id("month")) ## busco select de mes por id

month.select_by_value(mes)## selecciono la opcion del mes actual


# In[57]:


cont=driver.find_element_by_name("continue")## busco el boton y doy a continuar

cont.submit()


# In[58]:


driver.get("https://viewer.flightsupport.com/frames/manuals.jsp")##busco la siguiente pagina

bsObj = bs(driver.page_source, 'html.parser')##la ordeno


# In[124]:


linkList=driver.find_elements_by_class_name('table')## hago lista buscando por clases los a de la tabla


# In[125]:


lpe=linkList.pop(0)##extraigo en una variable las LEP

rl=linkList.pop(0)##extraigo en una variable el Revision Letter


# In[126]:


li=[]
for i in linkList:
    li.append(i.get_attribute('href'))##extraigo el link


# In[127]:


u=rl.get_attribute("href") ##extraigo url de Revision Letter
print(u)
driver.get(u) ##ingreso a la pagina

bsObj = bs(driver.page_source, 'html.parser')##emprolijo


# In[128]:


link=driver.find_element_by_class_name('table')##busco el a por clase


# In[129]:


d=link.get_attribute('href')##extraigo el link


# ### Bajo el Revision letter

# In[130]:


driver.find_element_by_xpath("//a[@class='table']").click()## ingreso y descargo
sleep(10)


# In[ ]:


lp=[]


# In[ ]:


#with pdfplumber.open("ls/2039-24-Sep-20/2039-24-Sep-20.pdf") as pdf:
with pdfplumber.open("ChartAccessServlet2151.pdf") as pdf:
    for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea
        a=p.extract_text()
        lp.append(a.split('\n'))
                  
    


# ### Cambio de nombre y Guadado en carpeta de la rev

# In[ ]:


lrn=lp[0][0]## obtengo primera fila 
rn=lrn[-4:]## me quedo con los ultimos 4 digitos para obtener el nro de revision


# In[ ]:


lrd=lp[0][1]## obtengo fecha de la revision


# In[ ]:


an=rn+'-'+lrd+'.pdf'


# In[ ]:


os.mkdir('ls/'+rn+'-'+lrd)##creo carpeta de revision
os.mkdir('ls/'+rn+'-'+lrd+"/America")
os.mkdir('ls/'+rn+'-'+lrd+"/Europa")
os.mkdir('ls/'+rn+'-'+lrd+"/Alt Ruta")
os.mkdir('ls/'+rn+'-'+lrd+"/Manual de Rutas")
os.mkdir('ls/'+rn+'-'+lrd+"/Manual de Rutas Int")
os.mkdir('ls/'+rn+'-'+lrd+"/China")


# In[ ]:


os.rename(direccionActual+'/ChartAccessServlet2151.pdf', an)## renombro el archivo


# In[ ]:


shutil.move(direccionActual+'/'+an , direccionActual + '/ls/'+rn+'-'+lrd+'/')


# ### Extraccion de info importante

# In[ ]:


cartas=[]

for i in lp:
       
    for x in i:
        
        a=re.search('\W\d\W\d{2,3}', x) ##busco coincidencia de REGEX en cada renglon, me quedo solo con las que cumplen la condicion
        
        if a != None :

            cartas.append(x)


# In[ ]:


df=pd.DataFrame()

amberso=[]

reverso=[]


# In[ ]:


for s in cartas:

    first=s.index('[') #obtenemos la posición del primer carácter

    second= s.index(']')#obtenemos la posición del carácter final

    hojas=s[first+1:second] 

    if re.search('\d\W\d{2,3}/\d\W\d{2,3}',hojas)==None:

        amberso.append(hojas)

        reverso.append('BLK')

    else:

        div=hojas.split('/')

        amberso.append(div[0])

        reverso.append(div[1])


# In[ ]:


amb=pd.Series(amberso)

rev=pd.Series(reverso)

df=pd.concat([df,amb])


# In[ ]:


df.rename(columns={0:'amberso'}, inplace=True)


# In[ ]:


df=pd.concat([df,rev], axis=1)

df.rename(columns={0:'reverso'}, inplace=True)


# In[ ]:


ciudades=[]

for s in cartas:
    
    m=s.split(']')
    
    match=re.search('[A-Z]{3,}?|dAdO',m[1]) ### variable a modificable

    

    e = match.start()

    ciudades.append(m[1][0:e])


# In[ ]:


ciu=pd.Series(ciudades)

df=pd.concat([df,ciu], axis=1)

df.rename(columns={0:'ciudades'}, inplace=True)


# In[ ]:




status=[]

fecha=[]

for i in cartas:
    
    
    
    
    match=re.search('Add|dd| d |Destroy|=',i)
    if match!=None:
        
        fo=i[match.start():match.end()]

        status.append(fo)

        fecha.append(date.today())
    else:
        algo=i.split('] ')
        
        match1=re.search('([A-Z]{2,})',algo[1])
        
        if match1 != None:
        
            fo=algo[1][match1.start():match1.end()+4]
            
            fo=re.sub('([A-Z])','', fo)
            
            
            if fo == 'dd':
                
                status.append("Add")

                fecha.append(date.today())
           
            elif fo == 'd':
                
                status.append("Add")

                fecha.append(date.today())
            elif fo == 'es':
                
                status.append("Destroy")

                fecha.append(date.today())
            elif fo == 's':
                
                status.append("Destroy")

                fecha.append(date.today())


# In[ ]:


sta=pd.Series(status)

df=pd.concat([df,sta], axis=1)

df.rename(columns={0:'status'}, inplace=True)


# In[ ]:


fca=pd.Series(fecha)

df=pd.concat([df,fca], axis=1)

df.rename(columns={0:'fecha'}, inplace=True)


# In[ ]:


df['oaci']=''


# In[ ]:


indexNames = df[ df['status'] == 'Destroy' ].index
df.drop(indexNames , inplace=True)
indexNames = df[( df['status'] == 'd')  |( df['status'] == 'dd')].index
df.drop(indexNames , inplace=True)


# In[ ]:


ciudades=df['ciudades'].unique()


# In[ ]:


oaci=[]
for c in ciudades:
   
    for i in lp:
        for x in i:
            p=c+'\W\s[A-Z]{3}'
            
            a=re.search('[A-Z][a-z]{1,20}\s\W\s[A-Z]|\W[A-Z][a-z]{1,20}\W\s\W\s[A-Z]', x)
            
            if a != None:
                
                f=x.split('|')
                
                cs=c.strip(' ')
                fp=f[0].strip(' ')
                if cs==fp:
                        df.loc[df['ciudades'] == c, 'oaci'] = f[1].replace(" ","")
                


# In[ ]:


indexNames = df[ df['oaci'] == '' ].index
df.drop(indexNames , inplace=True)


# In[ ]:


america=pd.read_excel("america.xlsx")


# In[ ]:


dfam= pd.merge(america, df, how='inner', on="oaci")


# In[ ]:


oaciList=dfam['oaci'].unique()


# In[ ]:


oaciList1=[]
for i in oaciList:
    if i != '':
        oaciList1.append(i.replace(" ",""))


# In[ ]:


def algo(df):
    charts.append(df['amberso'])
    charts.append(df['reverso'])


# In[84]:


for i in oaciList1:
    
        ua='https://viewer.flightsupport.com/frames/aerodrome.jsp?aerodrome='+i+'&routeManualId=AR-Airports'
        print(ua)
        charts=[]

        b=df.loc[(df['oaci']==i)]

        nm=i

        b.apply(algo, axis=1)

        driver.get(ua)

        checkList=driver.find_elements_by_name('order')## hago lista buscando por name los a de la tabla    
        
        fechasas=driver.find_elements_by_xpath("//tr/td[@class='TDwhiteBottomAndLeftLineGrey']")

       

        cont=0
        asas=[]
        for fec in fechasas:
           
            ec=re.search("[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}", fec.text)
            if ec != None:
                asas.append(fec)
                
        asas.pop(0)
        asas.pop(0)
        count=0
        for g in asas:
            
            count+=1
            if datetime.strptime(g.text, '%d.%m.%Y')>= datetime.strptime(lrd, '%d-%b-%y'):
                
                checkList[count].click()
                
        driver.find_element_by_id("idPrint").click()

        sleep(15)

        al='ls/'+rn+'-'+nm+'.pdf'

        os.rename('PrintServlet.pdf', al)

        shutil.move(al, 'ls/'+rn+'-'+lrd+'/America/'+rn+'-'+nm+'.pdf')
       


# In[86]:


i5=Pdf.open('Intencionalmente en Blanco A5.pdf')
i4=Pdf.open('Intencionalmente en Blanco A4.pdf')


# In[87]:


a4=Pdf.new()
a5=Pdf.new()


# In[ ]:





# In[85]:


probending=df['amberso'].str.rsplit("-", expand=True)   
df['order 1']=probending[0]
df['order 2']=probending[1]


# In[88]:


for i in oaciList1:
    
   
        print(i)
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'.pdf', allow_overwriting_input=True)

        porto=df.loc[(df['oaci']==i)]
        porto['order 1']=porto['order 1'].astype(int)
        porto['order 2']=porto['order 2'].astype(int)
        porto=porto.sort_values([ 'order 1','order 2'])
        charts=[]

        porto.apply(algo, axis=1)
        print(charts)
        count=-1
        
        newpdf=Pdf.new()
        for c in charts:

            count+=1
            
            if c =='BLK':
                
                print(count)
                
                w=pdf.pages[count-1]['/MediaBox']
              
                if float(w[2]) ==439.37009:
                    
                    pdf.pages.insert(count, i5.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
                elif float(w[2]) ==841.88977:

                    pdf.pages.insert(count, i4.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
            else:
                pdf.save('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf')
             


# In[89]:


for i in oaciList1:
    
    
        
        order=[]
        
        with pdfplumber.open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf') as pdf:

            for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea
                
                if float(p.height) == 841.890:

                    order.append(p.page_number)

        ppf=PdfFileReader(open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intW.pdf', 'rb'))

        pdf_writer = PdfFileWriter()

        for d in order:



            ppf.getPage(d-1).rotateCounterClockwise(90)



        for page in range(ppf.getNumPages()):

                    # Add each page to the writer object

                    pdf_writer.addPage(ppf.getPage(page))

        with open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intWOK.pdf', 'wb') as out:

                pdf_writer.write(out)


# In[90]:


for i in oaciList1:
    
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/America/'+rn+'-'+i+'intWOK.pdf')

        nh=range(0,len(pdf.pages))

        for t1 in nh:

                q=pdf.pages[t1]

                t=pdf.pages[t1].MediaBox

                if float(t[2]) ==439.37009 or float(t[2])== 419.52:

                    a5.pages.append(q)

                elif float(t[2]) ==841.88977 or float(t[2])== 841.92:

                    a4.pages.append(q)

        


# In[91]:


a5.save('ls/'+rn+'-'+lrd+'/America/'+rn+'-America-a5.pdf')
a4.save('ls/'+rn+'-'+lrd+'/America/'+rn+'-America-a4.pdf')


# ### Europa

# In[110]:



europa=pd.read_excel("europa.xlsx")

dfeu= pd.merge(europa, df, how='inner', on="oaci")


# In[111]:


oaciList1=dfeu['oaci'].unique()


# In[113]:



np.append(oaciList1,[ 'LFPO','LFPB'], axis=None)


# In[94]:


for i in oaciList1:
    
        ua='https://viewer.flightsupport.com/frames/aerodrome.jsp?aerodrome='+i+'&routeManualId=AR-Airports'
        print(ua)
        charts=[]
        porto['order 1']=porto['order 1'].astype(int)
        porto['order 2']=porto['order 2'].astype(int)
        porto=porto.sort_values([ 'order 1','order 2'])
        b=df.loc[(df['oaci']==i)]

        nm=i

        b.apply(algo, axis=1)

        driver.get(ua)

        checkList=driver.find_elements_by_name('order')## hago lista buscando por name los a de la tabla    
        
        fechasas=driver.find_elements_by_xpath("//tr/td[@class='TDwhiteBottomAndLeftLineGrey']")

        

        cont=0
        asas=[]
        for fec in fechasas:
            ec=re.search("[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}", fec.text)
            if ec != None:
                asas.append(fec)
                
        asas.pop(0)
        asas.pop(0)
        count=0
        for g in asas:
            
            count+=1
            if datetime.strptime(g.text, '%d.%m.%Y')>= datetime.strptime(lrd, '%d-%b-%y'):
                
                checkList[count].click()
                
        driver.find_element_by_id("idPrint").click()

        sleep(15)

        al='ls/'+rn+'-'+nm+'.pdf'

        os.rename('PrintServlet.pdf', al)

        shutil.move(al, 'ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+nm+'.pdf')


# In[117]:


a4=Pdf.new()
a5=Pdf.new()


# In[96]:


for i in oaciList1:
   
   
       
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'.pdf', allow_overwriting_input=True)

        porto=df.loc[(df['oaci']==i)]

        charts=[]

        porto.apply(algo, axis=1)
        
        count=-1
        
        newpdf=Pdf.new()
        for c in charts:

            count+=1

            if c =='BLK':
                
                w=pdf.pages[count-1]['/MediaBox']
              
                if float(w[2]) ==439.37009:
                    
                    pdf.pages.insert(count, i5.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
                elif float(w[2]) ==841.88977:

                    pdf.pages.insert(count, i4.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
            else:
                pdf.save('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf')


# In[97]:


for i in oaciList1:
    
    
        
        order=[]
        
        with pdfplumber.open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf') as pdf:

            for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea

                if float(p.height) == 841.890:

                    order.append(p.page_number)

        ppf=PdfFileReader(open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intW.pdf', 'rb'))

        pdf_writer = PdfFileWriter()

        for d in order:



            ppf.getPage(d-1).rotateCounterClockwise(90)



        for page in range(ppf.getNumPages()):

                    # Add each page to the writer object

                    pdf_writer.addPage(ppf.getPage(page))

        with open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intWOK.pdf', 'wb') as out:

                pdf_writer.write(out)


# In[118]:


for i in oaciList1:
        
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-'+i+'intWOK.pdf')

        nh=range(len(pdf.pages))

        for t1 in nh:

                q=pdf.pages[t1]

                t=pdf.pages[t1].MediaBox
                
                if float(t[2]) <=439.37009:

                    a5.pages.append(q)

                elif float(t[2]) >=841.88977 :

                    a4.pages.append(q)


# In[116]:


a5.save('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-Europa-a5.pdf')
a4.save('ls/'+rn+'-'+lrd+'/Europa/'+rn+'-Europa-a4.pdf')


# In[98]:





# ### China

# In[132]:


chin=pd.read_excel("china.xlsx")
chin=chin.drop_duplicates()
dfch= pd.merge(chin, df, how='inner', on="oaci")
oaciList1=dfch['oaci'].unique()


# In[137]:


oaciList1


# In[134]:


for i in oaciList1:
    if i != "LPPT":
        ua='https://viewer.flightsupport.com/frames/aerodrome.jsp?aerodrome='+i+'&routeManualId=AR-Airports'
        print(ua)
        charts=[]

        b=df.loc[(df['oaci']==i)]

        nm=i

        b.apply(algo, axis=1)

        driver.get(ua)

        checkList=driver.find_elements_by_name('order')## hago lista buscando por name los a de la tabla    
        
        fechasas=driver.find_elements_by_xpath("//tr/td[@class='TDwhiteBottomAndLeftLineGrey']")

        

        cont=0
        asas=[]
        for fec in fechasas:
            ec=re.search("[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}", fec.text)
            if ec != None:
                asas.append(fec)
                
        asas.pop(0)
        asas.pop(0)
        count=0
        for g in asas:
            
            count+=1
            if datetime.strptime(g.text, '%d.%m.%Y')>= datetime.strptime(lrd, '%d-%b-%y'):
                
                checkList[count].click()
                
        driver.find_element_by_id("idPrint").click()

        sleep(15)

        al='ls/'+rn+'-'+nm+'.pdf'

        os.rename('PrintServlet.pdf', al)

        shutil.move(al, 'ls/'+rn+'-'+lrd+'/China/'+rn+'-'+nm+'.pdf')


# In[135]:


a4=Pdf.new()
a5=Pdf.new()


# In[138]:


for i in oaciList1:
   
   
        
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'.pdf', allow_overwriting_input=True)

        porto=df.loc[(df['oaci']==i)]

        charts=[]

        porto.apply(algo, axis=1)
        
        count=-1
        
        newpdf=Pdf.new()
        for c in charts:

            count+=1

            if c =='BLK':
                
                w=pdf.pages[count-1]['/MediaBox']
              
                if float(w[2]) ==439.37009:
                    
                    pdf.pages.insert(count, i5.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
                elif float(w[2]) ==841.88977:

                    pdf.pages.insert(count, i4.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
            else:
                pdf.save('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf')


# In[140]:


for i in oaciList1:
    
    
        
        order=[]
        
        with pdfplumber.open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf') as pdf:

            for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea

                if float(p.height) == 841.890:

                    order.append(p.page_number)

        ppf=PdfFileReader(open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intW.pdf', 'rb'))

        pdf_writer = PdfFileWriter()

        for d in order:



            ppf.getPage(d-1).rotateCounterClockwise(90)



        for page in range(ppf.getNumPages()):

                    # Add each page to the writer object

                    pdf_writer.addPage(ppf.getPage(page))

        with open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intWOK.pdf', 'wb') as out:

                pdf_writer.write(out)


# In[142]:



for i in oaciList1:
        
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/China/'+rn+'-'+i+'intWOK.pdf')

        nh=range(len(pdf.pages))

        for t1 in nh:

                q=pdf.pages[t1]

                t=pdf.pages[t1].MediaBox
                
                if float(t[2]) <=439.37009:

                    a5.pages.append(q)

                elif float(t[2]) >=841.88977 :

                    a4.pages.append(q)


# In[143]:


a5.save('ls/'+rn+'-'+lrd+'/China/'+rn+'-China-a5.pdf')
a4.save('ls/'+rn+'-'+lrd+'/China/'+rn+'-China-a4.pdf')


# ### Alternativa en Ruta        

# In[100]:


altr=pd.read_excel("alternativa.xlsx")
dfal= pd.merge(altr, df, how='inner', on="oaci")
oaciList1=dfal['oaci'].unique()


# In[101]:


for i in oaciList1:
    if i != "LPPT":
        ua='https://viewer.flightsupport.com/frames/aerodrome.jsp?aerodrome='+i+'&routeManualId=AR-Airports'
        print(ua)
        charts=[]

        b=df.loc[(df['oaci']==i)]

        nm=i

        b.apply(algo, axis=1)

        driver.get(ua)

        checkList=driver.find_elements_by_name('order')## hago lista buscando por name los a de la tabla    
        
        fechasas=driver.find_elements_by_xpath("//tr/td[@class='TDwhiteBottomAndLeftLineGrey']")
        aiportList=driver.find_elements_by_class_name('table')## hago lista buscando por clases los a de la tabla

        aiportList.pop(0)
        aiportList.pop(0)
        aiportList.pop(0)
        aiportList.pop(0)
        

        cont=0
        asas=[]
        for fec in fechasas:
            ec=re.search("[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}", fec.text)
            if ec != None:
                asas.append(fec)
                
        asas.pop(0)
        asas.pop(0)
        count=0
        for g in asas:
            
            count+=1
            if datetime.strptime(g.text, '%d.%m.%Y')>= datetime.strptime(lrd, '%d-%b-%y'):
                
                cu=aiportList[count].get_attribute("href")

                for x in charts:
                    if x!="BLK":
                        prim=x.split("-")

                        if int(prim[0]) == 2 or int(prim[0])== 3:

                            x=x.replace('-','_')
                            
                            t=re.search(x, cu)

                            if t != None:

                                checkList[count].click()
                
        driver.find_element_by_id("idPrint").click()

        sleep(15)

        al='ls/'+rn+'-'+nm+'.pdf'
        if os.path.isfile('PrintServlet.pdf'):
            os.rename('PrintServlet.pdf', al)

            shutil.move(al, 'ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+nm+'.pdf')


# In[105]:


paginas=dfal["amberso"]
trtr=[]
for c in paginas:
    alu=c.split("-")
    trtr.append(int(alu[0]))
dfal["pim Num"]=trtr


# In[106]:


dfal=dfal.loc[(dfal["pim Num"]==2) |(dfal["pim Num"]==3)]


# In[107]:


a4=Pdf.new()
a5=Pdf.new()


# In[109]:



for i in oaciList1:
    if i != "LPPT":
   
        try:
            pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'.pdf', allow_overwriting_input=True)
        except:
            continue
        porto=dfal.loc[(dfal['oaci']==i)]

        charts=[]
        porto['order 1']=porto['order 1'].astype(int)
        porto['order 2']=porto['order 2'].astype(int)
        porto=porto.sort_values([ 'order 1','order 2'])
        porto.apply(algo, axis=1)
        
        print(charts)
        count=-1
        
        newpdf=Pdf.new()
        for c in charts:
            
            count+=1

            if c =='BLK':
             
                w=pdf.pages[count-1]['/MediaBox']
              
                if float(w[2]) ==439.37009:
                    
                    pdf.pages.insert(count, i5.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
                elif float(w[2]) ==841.88977:

                    pdf.pages.insert(count, i4.pages[0])
                    pdf.save('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf')
                    pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf',allow_overwriting_input=True)
            else:
                pdf.save('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf')


# In[213]:


for i in oaciList1:
    if i != "LPPT":
    
        
        order=[]
        
        with pdfplumber.open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf') as pdf:

            for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea

                if float(p.height) == 841.890:

                    order.append(p.page_number)

        ppf=PdfFileReader(open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intW.pdf', 'rb'))

        pdf_writer = PdfFileWriter()

        for d in order:



            ppf.getPage(d-1).rotateCounterClockwise(90)



        for page in range(ppf.getNumPages()):

                    # Add each page to the writer object

                    pdf_writer.addPage(ppf.getPage(page))

        with open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intWOK.pdf', 'wb') as out:

                pdf_writer.write(out)


# In[214]:


for i in oaciList1:
    if i != "LPPT":  
        pdf = Pdf.open('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-'+i+'intWOK.pdf')

        nh=range(len(pdf.pages))

        for t1 in nh:

                q=pdf.pages[t1]

                t=pdf.pages[t1].MediaBox
                
                if float(t[2]) <=439.37009:

                    a5.pages.append(q)

                elif float(t[2]) >=841.88977 :

                    a4.pages.append(q)


# In[215]:


a5.save('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-Alter-a5.pdf')
a4.save('ls/'+rn+'-'+lrd+'/Alt Ruta/'+rn+'-Alter-a4.pdf')


# In[ ]:





# In[47]:


order=[]
with pdfplumber.open("ls/a4.pdf") as pdf:
    
    for p in pdf.pages: ## divido por paginas, extraigo el texto y lo divido en los saltos de linea
        
        if float(p.height) == 841.890:
            
            order.append(p.page_number)


