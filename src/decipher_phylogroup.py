#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import sys
import codecs
import os
import time

#################################################################################################################
#	A little python script to determine the phylogroup of an E. coli strain according to Clermont et al. 2013
#	https://www.ncbi.nlm.nih.gov/pubmed/?term=The+Clermont+Escherichia+coli+phylo-typing+method+revisited%3A+improvement+of+specificity+and+detection+of+new+phylo-groups
#	Tested with Python 3.4.5
#	paulineauffret88@gmail.com
#	last update November, 22th 2017
#################################################################################################################
#Input and output files (required)
fileIn=sys.argv[1]		#text file, output from primerseach program
fileIn2=sys.argv[2]		#text file with primers name and their length (chuA.1b_[chuA]	288) one per line
fileIn3=sys.argv[3]		#Phylogroup file with correpondance between amplimer profile and phylogroup according to Clermont et al. 2013 (1011111	B2)
fileOut=sys.argv[4]		#output file

#Set date
TIMESTAMP=time.strftime("%A %d %B %Y %H:%M:%S")

#Open input and output files
fin = codecs.open(fileIn, "r")
fin2= codecs.open(fileIn2, "r")
fin3 = codecs.open(fileIn3, "r")
fout = codecs.open(fileOut, "a")

#Read primers length file and save info into PL dictionary 
#PL[amplimer_name]=amplimer expected length
PL=dict()
line=fin2.readline()
while line :
	if line != "\n" :
		name=line.replace("\n","").split("\t")[0]
		length=line.replace("\n","").split("\t")[1]
		PL[name]=str(length)
	line=fin2.readline()

#Read phylogroup file and save info into PG dictionary
#PG[amplimer_profile]=phylogroup
PG=dict()
line=fin3.readline()
while line :
        if line != "\n" :
                code=line.replace("\n","").split("\t")[0]
                phyl=line.replace("\n","").split("\t")[1]
                PG[code]=str(phyl)
        line=fin3.readline()

#Read primersearch result file and save info into PT dictionary
PT=dict()
i=0
FIND=0
line=fin.readline()
while line :
	if line.startswith("Primer") and i == 0 :
		i=i+1
		primer=line.replace("\n","").split(" ")[2]
		#set bornes for amplimer length (here 10 bp) 
		bornInf=int(PL[primer])-10
		bornSup=int(PL[primer])+10
	elif line.startswith("Primer") and i !=0 :
		i=i+1
		if FIND == 1 :
			PT[primer]=1
		else :
			PT[primer]=0
		FIND=0
		primer=line.replace("\n","").split(" ")[2]
		bornInf=int(PL[primer])-10
		bornSup=int(PL[primer])+10
	elif line.startswith("\tAmplimer length") :
		length=line.split(" ")[2]
		if  int(length) < bornSup and int(length) >  bornInf :
			FIND=1	
	line=fin.readline()
if FIND == 1 :
	PT[primer]=1
elif FIND ==0 :
	PT[primer]=0

#If amplimer control not found, returns "UNDET" for undetermined phylogroup
ctrl=PT["trpBA.f_[trpA]"]
if ctrl == 0 :
	phylogroup="UNDET"
#else returns phylogropp
else :
	code_phylogroup=str(PT["trpBA.f_[trpA]"])+str(PT["AceK.f_[arpA]"])+str(PT["chuA.1b_[chuA]"])+str(PT["yjaA.1b_[yjaA]"])+str(PT["TspE4C2.1b_[TspE4.C2]"])+str(PT["trpAgpC.1_[trpA]"])+str(PT["ArpAgpE.f_[arpA]"])
	phylogroup=PG[code_phylogroup]

#Write results into output file
fout.write(phylogroup)
fout.write("\n")













