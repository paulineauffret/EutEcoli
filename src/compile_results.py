#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import sys
import codecs
import os
import time

#################################################################################################################
#	A little python script to compile results from blastn et phylotyping
#	Tested with Python 3.4.5
#	paulineauffret88@gmail.com
#	last update November, 22th 2017
#################################################################################################################
#Input and output files (required)
fileIn=sys.argv[1]		#text file, output from analyse of all blastn results, 2 columns : sequence ID	euT_gene_length
fileIn2=sys.argv[2]		#text file, output from phylotyping of all strains, 3 lines per sequence : 1st line = sequence ID ; 2nd line = file name ; 3rd line = phylogroup
fileOut=sys.argv[3]		#output file

#Set date
TIMESTAMP=time.strftime("%A %d %B %Y %H:%M:%S")

#Open input and output files
fin = codecs.open(fileIn, "r")
fin2= codecs.open(fileIn2, "r")
fout = codecs.open(fileOut, "w")

#Read blast file file and save info into BL dictionary 
#BL[file name]=eutT gene length
BL=dict()
line=fin.readline()
while line :
	if line != "\n" :
		filename=line.replace("\n","").split("\t")[0]
		eutlen=line.replace("\n","").split("\t")[1]
		BL[filename]=str(eutlen)
	line=fin.readline()
BL[filename]=str(eutlen)

#Read phylogroup file and write info
fout.write("File_name\tStrain_info\tPhylogroup\teutT_gene_length(bp)\n")
line=fin2.readline()
while line :
	if line != "\n" and line.startswith(">") :
		seqinfo=line.replace("\n","").split("__")[1]
		line=fin2.readline()
		filename=line.replace("\n","")
		line=fin2.readline()
		phylogroup=line.replace("\n","")  
		result=filename+"\t"+seqinfo+"\t"+phylogroup+"\t"+str(BL[filename])+"\n"
		fout.write(str(result))
	line=fin2.readline()


