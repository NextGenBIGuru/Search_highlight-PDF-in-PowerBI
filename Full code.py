import fitz
import pandas as pd #make sure to install the library using "pip3 install pandas"
import re
from bs4 import BeautifulSoup #make sure to install the library using "pip3 install bs4"
import os
import base64
import csv
from csv import DictWriter
from PyPDF2 import PdfWriter, PdfReader #make sure to install the library using "pip3 install PyPDF2"
import os
from os import path
import shutil

def ProcessPDF(WDir,source,FN):
    PDF_Dir=WDir + "PDFs\\" + source + "\\"
    CSV_Dir=WDir + "CSVs\\" + source + "\\"
    Arc_Dir=WDir + "PDFs\\" + source + "\\Archive\\"

    with open(PDF_Dir + FN + '.pdf', "rb") as pdf: #Open the PDF file
        inputpdf=PdfReader(pdf)

        Data_={} #Creating a dictionary for the CSV headers
        field_names=['ID','Merged','Source','Group','Title']
        [field_names.append('B' + str(i)) for i in range(50)]

        if not path.exists(CSV_Dir): os.mkdir(CSV_Dir) #Create the CSV file and add the headers
        with open(CSV_Dir + FN + '.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            f.close()

        for i in range(len(inputpdf.pages)):#iterat through the PDF pages and create a seperate tem PDF file for each page
            output = PdfWriter()
            output.add_page(inputpdf.pages[i])
            with open(FN + '_'+  str(i) + '.pdf', "wb") as outputStream:
                output.write(outputStream)
            with fitz.open(FN + '_' + str(i) + '.pdf') as doc:#Get the text contents from the temp files
                contents=doc[0].get_text("XHTML")
                soup = BeautifulSoup(contents,"html.parser")
                Prghs = soup.findAll('p')#find all paragraphs in the extracted text
                n=0
            for Prgh in Prghs:#iterate through all paragraphs and highlight the contents in sepearate new PDF files
                if not '<p><img' in str(Prgh) and not len(Prgh.get_text())<4:#ignore images and paraghraphs with <4 charachters
                    n+=1
                    with fitz.open(FN + '_' + str(i) + '.pdf') as doc:
                        for page in doc:
                            text_instances = page.search_for(Prgh.get_text())
                            for inst in text_instances:
                                highlight = page.add_highlight_annot(inst).update()#highlight the text 
                    
                        doc.save(FN + '_'+  str(i) + '_' + str(n) +  '.pdf', garbage=4, deflate=True, clean=True)
            os.remove(FN + '_' + str(i) + '.pdf') #Remove tem files
            n=0
            for Prgh in Prghs: #iterate through the highlited temp files and extract the contents in base64 format
                if not '<p><img' in str(Prgh) and not len(Prgh.get_text())<4:
                    n+=1
                    with open(FN + '_'+  str(i) + '_' + str(n) +  '.pdf', "rb") as Tempfile:
                        my_string=base64.b64encode(Tempfile.read())
                        my_string=my_string.decode('ascii')

                    with open(CSV_Dir + FN + '.csv', 'a',encoding="utf-8") as f:#add the PDF base64 code into the CSV file
                        NRow = DictWriter(f, fieldnames=field_names, lineterminator = '\n')
                        IID='Ref' + str(i) + '_' + str(n)
                        TT=source + " - " + FN + " - " + 'Page:' + str(i)
                        Data_={'ID':IID,'Merged':IID + " - " + Prgh.get_text(),'Group':source,'Source':FN,'Title': TT}
                        for j in range(int(len(my_string)/32000)+1):#break the base64 code into portions of 32000 charachters before saving them into the CSV file to avoid the characters length limitation
                            Data_['B' + str(j)]=my_string[j*32000:(j+1)*32000]
                        NRow.writerow(Data_)
                        Data_.clear()
                    os.remove(FN + '_'+  str(i) + '_' + str(n) +  '.pdf')
    if not path.exists(Arc_Dir): os.mkdir(Arc_Dir)       
    shutil.move(PDF_Dir + FN + ".pdf", Arc_Dir + FN + "_Processed.pdf")

WDir="C:\\Users\\hamze\\Desktop\\NG BI Guru\\Video contents\\PDF Videos\\Video 3 PDF search\\"#Make sure to replace \ with \\ for python to treat the text as a directory (Path)

for source in os.listdir(WDir + "PDFs"): #iterate through the PDF files in the directory and extract the contents to the CSV files
    if not os.path.isfile(source):
        FDir=WDir + "PDFs\\" + source + "\\"
      
        for file in os.listdir(WDir + "PDFs\\" + source):
            if os.path.isfile(os.path.join(WDir + "PDFs\\" + source, file)) and file.lower().endswith(".pdf"):              
                FN=file.rsplit( ".", 1 )[ 0 ]
                ProcessPDF(WDir,source,FN)

