# Steps to onboard STRING DB:
1) Follow this link and download (for homo sapiens): 9606.protein.info.v11.5.txt.gz, 9606.protein.links.full.v11.5.txt.gz, and 9606.protein.aliases.v11.5.txt.gz
https://string-db.org/cgi/download?species_text=Homo+sapiens
2) Unzip the files in (1) in the `db/data` folder
3) Run the file fom the command line:
`python build_links_db.py`

The run can take more than an hour and is appending a protein to gene mapping from the EnsEMBL annotation that provides complete coverage of the proteins in the STRING DB. 
