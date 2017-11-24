#!/bin/bash
TIMESTAMP=$(date +%Y-%m-%d_%Hh%Mm%Ss)
WORKING_DIRECTORY=/home1/scratch/pauffret/analyse_eutT_ecoli
FINAL=${WORKING_DIRECTORY}/finalresults
SRC=${WORKING_DIRECTORY}/src
SCRIPT_WGET=${SRC}/wget_genomes_ncbi.py
SCRIPT_DECIPHER=${SRC}/decipher_phylogroup.py
SCRIPT_READ_BLAST=${SRC}/read_eutt_blast_result.py
SCRIPT_COMPILE_RESULTS=${SRC}/compile_results.py
PRIMERS_FILE=${SRC}/phylotyping_primers_clermont.txt
PRIMERS_LENGTH_FILE=${SRC}/primers_length.txt
PHYLOGROUPS_FILE=${SRC}/phylogroups.txt
GENOME_SUMMARY_URL=ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/Escherichia_coli/assembly_summary.txt
GENOME_DIR=${WORKING_DIRECTORY}/genomes
GENOME_ARCHIVE=${GENOME_DIR}/archives
PHYLOGROUPING_DIR=${WORKING_DIRECTORY}/phylogrouping
BLAST_DIR=${WORKING_DIRECTORY}/blast
BLAST_SRC=${WORKING_DIRECTORY}/blast/scripts
BLAST_RES=${WORKING_DIRECTORY}/blast/results_${TIMESTAMP}
SUMMARY_FILE=${GENOME_DIR}/assembly_summary.txt
CURDIR=${PHYLOGROUPING_DIR}/${TIMESTAMP}
RESULT=${CURDIR}/results.txt
FINAL_RESULT=${FINAL}/final_${TIMESTAMP}
LOG=${WORKING_DIRECTORY}/log
MISMATCH_RATE_PRIMERS=20
PYTHON=python3
EUTT=${SRC}/eutT_BG1.fa
HEADER_BLAST=${SRC}/header_blast.txt

mkdir -p ${WORKING_DIRECTORY}

mkdir -p ${FINAL}

mkdir -p ${LOG}

mkdir -p ${GENOME_DIR}

mkdir -p ${GENOME_ARCHIVE}

mkdir -p ${PHYLOGROUPING_DIR}

mkdir -p ${BLAST_DIR}

mkdir -p ${BLAST_SRC}

mkdir -p ${BLAST_RES}

mkdir -p ${CURDIR} 

touch ${RESULT}

cd ${GENOME_DIR}

#echo "Downloading summary file."
wget -O ${SUMMARY_FILE} ${GENOME_SUMMARY_URL}

#head -60 ${SUMMARY_FILE} | tail -10 > ${WORKING_DIRECTORY}/genomes/TEST.txt

#echo "Downloading genomes."
#${PYTHON} ${SCRIPT_WGET} ${WORKING_DIRECTORY}/genomes/TEST.txt > ${LOG}/${SCRIPT_WGET##*/}_${TIMESTAMP}.log

echo "Downloading genomes."
${PYTHON} ${SCRIPT_WGET} ${SUMMARY_FILE} > ${LOG}/${SCRIPT_WGET##*/}_${TIMESTAMP}.log

#Load primerserach (emboss) environment
. /appli/bioinfo/emboss/latest/env.sh

cd  ${GENOME_DIR}

#List all downloaded genomes
for file in $(ls *.fna*) ;
do
	cp ${file} ${GENOME_ARCHIVE}/
	#if file is .gz, unzip it
	suffix=${file##*.} ;
	if [ "$suffix" = "gz" ] ;
	then 
		gunzip -f ${file} ;
		file=${file%.*} ;
	fi ;
	
	echo ".o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o..o°O°o."
	echo "File ${file}."
	#print file info in result file
	head -1 $file >> ${RESULT} ;
	echo ${file} >> ${RESULT} ;
	#phylotyping with primersearch
	echo "In silico PCR with primersearch." ;
	primersearch -seqall ${file} -infile ${PRIMERS_FILE} -mismatchpercent ${MISMATCH_RATE_PRIMERS} -outfile ${CURDIR}/${file%.*}_phylogrouping_${TIMESTAMP}.txt ;
	#decipher phylotype profile
	echo "Searching phylogrouping correspondance." ;
	${PYTHON} ${SCRIPT_DECIPHER} ${CURDIR}/${file%.*}_phylogrouping_${TIMESTAMP}.txt ${PRIMERS_LENGTH_FILE} ${PHYLOGROUPS_FILE} ${RESULT} ;
	#blastn to find eutT gene in genome
	echo "Blastn eutT." ;
	sed -i "s/ /_/g" ${file} ;
	sed -i "s/>/>${file##*/}__/g" ${file} ;
	#create script for pbs
	cp $HEADER_BLAST ${BLAST_SRC}/blastn_${file%.*}.pbs ;
	echo "formatdb -i ${GENOME_DIR}/${file} -p F" >>  ${BLAST_SRC}/blastn_${file%.*}.pbs ;
	echo "cat ${GENOME_DIR}/${file} | parallel -j 8 -k --block 10k --recstart '>' --pipe blastn -subject ${EUTT} -query - -outfmt \\\"6 qseqid qlen sseqid slen qcovs pident length mismatch gapopen qstart qend sstart send evalue bitscore\\\" -evalue 1e-5 -max_target_seqs 1 > ${BLAST_RES}/${file##*/}_${EUTT##*/}_${TIMESTAMP}.nt.txt " >> ${BLAST_SRC}/blastn_${file%.*}.pbs ;
	echo "rm ${GENOME_DIR}/${file}" >> ${BLAST_SRC}/blastn_${file%.*}.pbs ;
	#submit blastn job
	qsub ${BLAST_SRC}/blastn_${file%.*}.pbs ;
done ;

echo "There are " ;
grep -c "UNDET" ${RESULT} ;
echo "undetermined phylogroups." ;

#Pause script until jobs are finished
echo "Pause."
qstat -u "pauffret" > ${BLAST_RES}/qstat ;
current_jobs=$(wc -l ${BLAST_RES}/qstat | cut -f1 -d " ") ;
echo $current_jobs
while [ "$current_jobs" != "0" ] ; 
do
	echo "sleep" ;
	sleep 30s ;
	qstat -u "pauffret" > ${BLAST_RES}/qstat ;
	current_jobs=$(wc -l ${BLAST_RES}/qstat | cut -f1 -d " ") ;
done
	
touch ${BLAST_RES}/all_blast_results.txt

#Compile blastn results
echo "Compile blast results."
cd ${BLAST_RES}
for file in $(ls *.nt.txt)
do
	${PYTHON} ${SCRIPT_READ_BLAST} ${file} ${BLAST_RES}/all_blast_results.txt ;
done 

#Compile blast and phylotype results
echo "Write final results file."
${PYTHON} ${SCRIPT_COMPILE} ${RESULT} ${BLAST_RES}/all_blast_results.txt ${FINAL_RESULT} ;

echo "Done."
