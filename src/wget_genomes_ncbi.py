#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import sys
import codecs
import os
import time

###########################################################################################################
#	A little python script to get all E. coli genomes from NCBI ftp
#	Tested with Python 3.4.5
#	paulineauffret88@gmail.com
#	last update November, 22th 2017
###########################################################################################################
#Input and output files (required)
fileIn=sys.argv[1]		#text file, list of url to download output from wget ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/Escherichia_coli/assembly_summary.txt

#command line : python3 /home1/scratch/pauffret/analyse_eutT_ecoli/wget_genomes_ncbi.py /home1/scratch/pauffret/analyse_eutT_ecoli/assembly_summary.txt 

#Set date
TIMESTAMP=time.strftime("%A %d %B %Y %H:%M:%S")

#Open files
fin = codecs.open(fileIn, "r")

#Download genomes
i=0
line=fin.readline()
while line :
	if not line.startswith("#") :
		url=line.split("\t")[19]
		directory=url.split("/")[-1]
		url=url+"/"+directory+"_genomic.fna.gz"
		i=i+1
		print(url)
		os.system("wget -q \""+url+"\"")
	line=fin.readline()
print(str(i)+" genomes downloaded "+str(TIMESTAMP))



