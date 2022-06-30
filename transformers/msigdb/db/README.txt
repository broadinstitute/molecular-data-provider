*** README ***
__________________________________________________________________________________________________________________
DEPENDENCIES:
libraries needed:
sqlite3
pandas
xml
numpy
csv
re
os
warnings
pathlib
__________________________________________________________________________________________________________________
LAUNCH PARSING AND SQLite CREATION: 
(1) download db folder from GitHub
(2) create a subfolder named 'data' within the 'db' subfolder
(3) download msigdb_v7.4 version available here (you must be registered to MSigDB) and place it in the db/data/ subfolder: 
http://www.gsea-msigdb.org/gsea/msigdb/download_file.jsp?filePath=/msigdb/release/7.4/msigdb_v7.4.xml
(4) using the editor console, navigate to the download db/ folder
(5) open and run MSigDBmain.py with your favorite code editor (this code has been generated with VSCode): 
!!!!!!!WARNING!!!!!!!   To run the code you need to have 615,015KB available on disk.
__________________________________________________________________________________________________________________
PARSING AND DATABASE CREATION VERIFICATION:
* The parsing will create chunks of the MSigDB file and parse them individually. Once the file partition is successfully parsed, the partition will be deleted. At the end of the parsing process, remaining partitions are partitions that could not be parsed. This step creates .csv files containing the data parsed that will be used for the SQLite creation.
* At the end of the database creation, an MSigDB.sqlite file. You can open to view the file with the SQLite database of your choice.  
__________________________________________________________________________________________________________________
DATABASE PARSING NOTES:
* MSigDB parsed from .xml file: msigdb_v7.4 version available here : http://www.gsea-msigdb.org/gsea/downloads.jsp
* Data was parsed to 4 .csv files : GENESET (containing attributes of gene sets), MEMBER (containing attributes of gene/protein IDs), GENESET_MAP (mapping the hierarchy between genesets to create the Hallmark genesets) and MEMBER_MAP (mapping between GENESET and MEMBER)
* .xml file was parsed using xml.sax python module resulting to a parsing by partitions of file (to circumvent memory issues), 45 "DESCRIPTION FULL" values were transformed to fix issues with non allowed characters: '\u' changed in 'u', ' " ' changed in ''. The MEMBER file headers were created from the gene name mapping triples from the original file and were names as MEMBER_MAPPING_1, MEMBER_MAPPING_2, MEMBER_MAPPING_3
* .csv files containing concatenation of IDs '|' separated in MEMBER table were cleaned : selecting the ENSEMBL transcript IDs when primarily available, if not the Linc IDs, if not what is remaining (TC IDs)
* .csv files were normalized to reduce redundancy of information leading to a reduction of 92.96% redundancy reduction of info for the MEMBER table



