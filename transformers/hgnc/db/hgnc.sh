# Download and build the HGNC database
# Usage: ./hgnc.sh YYYY-MM-DD

if ($#argv != 1) then
    echo "Usage: $0 YYYY-MM-DD"
    exit 1
endif

if (-d "data/$1") then
    echo "Directory data/$1 already exists."
    exit 1
endif
mkdir -p data/$1

curl https://storage.googleapis.com/public-download-files/hgnc/archive/archive/monthly/tsv/hgnc_complete_set_$1.txt -o data/$1/hgnc_complete_set_$1.txt

grep NoSuchKey data/$1/hgnc_complete_set_$1.txt
if ($status == 0) then
    echo "Failed to download the file."
    exit 1
endif

python build_hgnc_db.py $1
if ($status != 0) then
    echo "Failed to build the database."
    exit 1
endif
