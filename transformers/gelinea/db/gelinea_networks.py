import sys


def filter_string(src_file, dest_file, threshold):
    print(dest_file, threshold)
    with open(src_file, 'r') as input:
        with open(dest_file, 'w') as output:
            header = input.readline().strip()
            if header != 'protein1 protein2 combined_score':
                print('WARN: bad file format', file=sys.stderr)
                sys.exit(1)
            print('protein1', 'protein2', 'combined_score', sep='\t', file=output)
            for line in input:
                row = line.split(' ')
                protein1 = row[0]
                if protein1.startswith('9606.'):
                    protein1 = protein1[5:]
                protein2 = row[1]
                if protein2.startswith('9606.'):
                    protein2 = protein2[5:]
                score = int(row[2])
                if len(row) == 3:
                    if score >= threshold:
                        print(protein1, protein2, score, sep='\t', file=output)
                else:
                    print('WARN: bad line format', file=sys.stderr)


def string_mapping(src_file, dest_file):
    string_map = {}
    print(dest_file)
    with open(src_file, 'r') as input:
        with open(dest_file, 'w') as output:
            header = input.readline().strip()
            if header != '#string_protein_id\talias\tsource':
                print('WARN: bad file format', file=sys.stderr)
                sys.exit(1)
            print('protein_id', 'GeneID', sep='\t', file=output)
            for line in input:
                row = line.strip().split('\t')
                if len(row) == 3:
                    protein_id = row[0]
                    source = row[2]
                    if source == 'Ensembl_HGNC_entrez_id':
                        gene_id = int(row[1])
                        if protein_id.startswith('9606.'):
                            protein_id = protein_id[5:]
                        string_map[gene_id] = protein_id
                        print(protein_id, gene_id, sep='\t', file=output)
                else:
                    print('WARN: bad line format', file=sys.stderr)
    return string_map


def map_msigdb(src_file, dest_file, string_map):
    print(dest_file)
    with open(src_file, 'r') as input:
        with open(dest_file, 'w') as output:
            for line in input:
                row = line.strip().split('\t')
                if len(row) > 3:
                    gene_set = []
                    ids = set()
                    gene_set.append(row[0])
                    gene_set.append(row[1])
                    for gene_id in row[2:]:
                        string_id = string_map.get(int(gene_id))
                        if string_id is not None and string_id not in ids:
                            gene_set.append(string_id)
                            ids.add(string_id)
                    print(*gene_set, sep='\t', file=output)
                else:
                    print('WARN: bad line format', file=sys.stderr)
 

def main():
    filter_string('data/download/string/protein.links.txt', 'data/transformer/human.links_700.txt', 700)
    filter_string('data/download/string/protein.links.txt', 'data/transformer/human.links_400.txt', 400)
    string_map = string_mapping('data/download/string/protein.aliases.txt','data/transformer/human_GeneID.txt')
    map_msigdb('data/download/msigdb/h.all.latest.Hs.entrez.gmt','data/transformer/h.all.current.STRING.gmt',string_map)
    map_msigdb('data/download/msigdb/c2.all.latest.Hs.entrez.gmt','data/transformer/c2.all.current.STRING.gmt',string_map)
    map_msigdb('data/download/msigdb/c5.all.latest.Hs.entrez.gmt','data/transformer/c5.all.current.STRING.gmt',string_map)


if __name__ == "__main__":
    main()
