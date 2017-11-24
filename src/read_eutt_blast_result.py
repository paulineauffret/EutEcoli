#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import sys
import codecs
import os
import time

#################################################################################################################
#	A little python script to read blastn file results from eutT research and interpret it
#	Tested with Python 3.4.5
#	paulineauffret88@gmail.com
#	last update November, 23th 2017
#################################################################################################################
#Input and output files (required)
fileIn=sys.argv[1]		#text file, output from blastn, outfmt "6 qseqid qlen sseqid slen qcovs pident length mismatch gapopen qstart qend sstart send evalue bitscore"
fileOut=sys.argv[2]		#output file

#Set date
TIMESTAMP=time.strftime("%A %d %B %Y %H:%M:%S")

#Open input and output files
fin = codecs.open(fileIn, "r")
fout = codecs.open(fileOut, "a")

#Read blastn results file  
pident=0
cov=0
nbSeq=0
allength=0
line=fin.readline()
while line :
	if line == "" :
		eut="NOEUTT"
	elif line != "\n" or nbSeq > 2 :
		nbSeq=nbSeq+1
		line=line.replace("\n","").split("\t")
		seqname=line[0]
		seqID=seqname.split("__")[0]
		qlength=line[1]
		pident=(float(pident)+float(line[5]))/float(nbSeq)
		allength=int(allength)+int(line[6])
		cov=float(allength)/float(line[3])*100
	else :
		eut="AMBIGUOUS"
	line=fin.readline()
print(allength)
print(pident)
print(cov)

if pident < 70 or cov <70 :
	eut="AMBIGUOUS"
else :
	eut=str(allength)


#Write results into output file
fout.write(seqID+"\t"+eut+"\n")














