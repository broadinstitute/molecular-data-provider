import pandas as pd
import json

######################################################################################################
# Scan the dataframe for data to populate a JSON config file.
# GtoPdb Relations JSON - JSON.tsv is just a spreadsheet that must have the following columns:
# type
# biolinkPredicate
# inversePredicate
# attributeName
# attributes
# qualifiedPredicate
# qualifier_1
# qualifier_2
# qualifier_3
# qualifier_4

        
###########################################################################################################
#  Add the collection of qualifiers to the list
# 
def add_qualifer(qualifier, row, qualifier_list):
        qualifier_dict = {}
        if not pd.isna(row[qualifier]) and ':' in row[qualifier]: # if the cell does have qualifier type:value
            splits = row[qualifier].split(':',1)
            qualifier_dict['qualifier_type_id'] = splits[0]
            qualifier_dict['qualifier_value'] = splits[1]
            qualifier_list.append(qualifier_dict)
            
            
    
###########################################################################################################
# Convert the GtoPdb Dataframe to JSON
#
def convert_df_2_json(dataframe):
    relationsMap = {}                                  # Start a new JSON
    type_action  = ''
    for index, row in dataframe.iterrows():            # Get a row of data from spreadsheet
        if( not pd.isna(row['action_type'])):
            relation = {}
            qualifier_list = []                        # Start a new relation

            type_key = row['action_type']
            
            relation["predicate"] = row['biolinkPredicate']
            relation['inv_predicate'] = row['inversePredicate']
            if (not pd.isna(row['qualifiedPredicate'])):
                #relation['qualified_predicate'] = row['qualifiedPredicate']
                if not pd.isna(row['qualifiedPredicate']):
                    qualifier_dict = {}
                    qualifier_dict['qualifier_type_id'] = 'qualified_predicate'
                    qualifier_dict['qualifier_value'] = row['qualifiedPredicate']
                    qualifier_list.append(qualifier_dict)
            relation['qualifiers'] = qualifier_list

            for qualifier_idx in range(1, 5):          # loop from qualifier 1 to qualifier 4
                if(not type(row['qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx)]) is float):
                    add_qualifer('qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx), row, qualifier_list)
            
            relationsMap[type_key]= relation

#   Save as a JSON file
    with open('data/chembl_qualifiers.json', 'w') as outfile:
        json.dump(relationsMap, outfile, indent=4, sort_keys=True) 

def scan_df():    
    gtopdb_dataframe = pd.read_table("data/ChEMBL_qualifiers.tsv", encoding='utf-8-sig')  
    convert_df_2_json(gtopdb_dataframe)


def main():
  # Scan the dataframe for data to populate JSON file
    scan_df()

if __name__ == '__main__':
    main()