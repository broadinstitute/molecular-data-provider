def dispatch_MolePro_services(node_start,node_end):
    
    node_start_class = node_start["element_class"]
    node_end_class = node_end["element_class"]
    
    score_threshold = '95'
    maximum_number = 0
    
    dispatcher = {
        "compound->disease": "transform_compound_to_disease(node_start)",
        "compound->diseasepheno": "transform_compound_to_DiseaseOrPhenotypicFeature(node_start)",
        "compound->gene": "transform_compound_to_gene(node_start, score_threshold, maximum_number)",
        "compound->protein": "transform_compound_to_protein(node_start, score_threshold, limit)",
        "gene->compound": "transform_gene_to_compound(node_start, score_threshold, maximum_number)"
    }
    
    collection = list()
    if (node_start_class == 'compound'):
        if (node_end_class == 'disease'):
            eval('collection = ' + dispatcher['compound->disease'])
        elif(node_end_class == 'DiseaseOrPhenotypicFeature'):
            eval('collection = ' + dispatcher['compound->disease_pheno'])
        elif(node_end_class == 'gene'):
            eval('collection = ' + dispatcher['compound->gene'])
        elif(node_end_class == 'protein'):
            eval('collection = ' + dispatcher['compound->protein'])
        else:
            print('no services provided')
    if (node_start_class == 'gene'):
        eval('collection = ' + dispatcher['gene->compound'])
    else:
        print('no services provided')
        
    return collection


#def propagate(node_start, node_end):
 #   
 #   while()  
    