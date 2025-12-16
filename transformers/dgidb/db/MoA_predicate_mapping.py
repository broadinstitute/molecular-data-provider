import pandas as pd
import json


def moa_to_json(moa_df):
    dgidb_MoA_Map = {}                                  # Start a new JSON
    for index, row in moa_df.iterrows():                # Get each row data for JSON
        if( not pd.isna(row['value']) ):                # e.g.,"Prostanoid EP2 receptor agonist"
            if row['Specific Action of the Ligand']:
                dgidb_MoA_Map[row['value']] = row['Specific Action of the Ligand']     # Add new mapping to JSON
    with open('../python-flask-server/config/DGIdb_moa_map.json', 'w') as outfile:
        json.dump(dgidb_MoA_Map, outfile, indent=4, sort_keys=True)


########################################################
# Create mapping between DGIdb's MoAs in the interaction_attributes
# table and the MolePro config file, predicateMap.txt. 
#
def qualifiers_to_json( predicate_qualifier_df):
    dgidb_qualifiers_map = {}                           # Start a new JSON for export into a file
    for index, row in predicate_qualifier_df.iterrows(): # Get each row data for JSON
        key = row['Specific Action of the Ligand']       # e.g.,"Prostanoid EP2 receptor agonist"
        action = {}                                     # Start a new action mapping 
        action['predicate'] = row['biolinkPredicate']   
        action['inv_predicate'] = row['inversePredicate'] 
        if not pd.isna(row['qualifiedPredicate']):
            action['qualified_predicate'] = row['qualifiedPredicate']
            action['inv_qualified_predicate'] = row['inverseQualifiedPredicate']
        qualifier_list = []
        for i in range(1,4):                            # Scan all four of the qualifier columns
            qualifier = {}
            if not pd.isna(row['qualifier_' + str(i)]):
                qualifier['qualifier_type_id'] = row['qualifier_' + str(i)].split(':')[0] 
                qualifier['qualifier_value'] = row['qualifier_' + str(i)].split(':')[1]  
                qualifier_list.append(qualifier)
            action['qualifiers'] = qualifier_list
        dgidb_qualifiers_map[key] = action


#   Save as a JSON file
    with open('../python-flask-server/config/DGIdb_qualifiers.json', 'w') as outfile:
        json.dump(dgidb_qualifiers_map, outfile, indent=4, sort_keys=True) 


def main():
    # Two spreadsheets will be merged into one JSON
    moa_df = pd.read_csv('moa_action.csv', sep=",", encoding='utf-8-sig')
    moa_to_json(moa_df)
    predicate_qualifier_df = pd.read_csv('predicate and qualifier mapping.csv', encoding='utf-8-sig')
    qualifiers_to_json( predicate_qualifier_df)


if __name__ == '__main__':
    main()