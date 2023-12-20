import pandas as pd
import json



###################################################
# Scan the dataframe for data to populate JSON file.
# Inxight_Drugs Chemical Relations.tsv is just a 
# spreadsheet with the relation column populated.
# The other columns are:
# relation	attributeName	attributeValue	biolinkPredicate	
# inversePredicate	qualifiedPredicate	qualifier_1	
# qualifier_2	qualifier_3	qualifier_4
def scan_df():
    inxight_dataframe = pd.read_table('Inxight_Drugs_Chemical_Relations.tsv', encoding='utf-8-sig')  
    for index, row in inxight_dataframe.iterrows():
        if( pd.isna(row['attributeName']) ):     # if the row has no attributeName value
            if('->' in row['relation']):         # then proceed to attempt populate
                splits = row['relation'].split('->',1)
                subject_role = splits[0].lower()
                object_role  = splits[1].lower()
            else:
                object_role = row['relation'].lower()
            print('object_role  ',object_role)
            find_in_predicate_map(object_role, index, row, inxight_dataframe)
    inxight_dataframe.to_csv('Inxight_Drugs_Chemical_Relations.tsv', sep="\t")
    convert_df_2_json(inxight_dataframe)


########################################################
# 
#   Create a dataframe and a TSV file of Mapping between
#   Inxight Drugs relations and Biolink predicates &
#   qualifiers
def find_in_predicate_map(object_role, index, row, inxight_dataframe):
    pred_dataframe = pd.read_table('predicateMap.txt')
    predicate_row = pred_dataframe.loc[ ((pred_dataframe['attributeValue'] == object_role) & (pred_dataframe['predicate'] == 'affects')) | (pred_dataframe['predicate'] == object_role.upper()) | (pred_dataframe['predicate'] == object_role) ]
    if (len(predicate_row['biolinkPredicate']) > 0):    # if found in the predicate map
        inxight_dataframe.loc[index,'attributeValue'] = predicate_row['attributeValue'].iloc[0]
        inxight_dataframe.loc[index,'attributeName'] = predicate_row['attributeName'].iloc[0]
        inxight_dataframe.loc[index,'biolinkPredicate'] = predicate_row['inversePredicate'].iloc[0]
        inxight_dataframe.loc[index,'inversePredicate'] = predicate_row['biolinkPredicate'].iloc[0]
        if (not pd.isna(predicate_row['qualifiedPredicate'].iloc[0])):
            inxight_dataframe.loc[index,'qualifiedPredicate'] = predicate_row['qualifiedPredicate'].iloc[0]
        for qualifier_idx in range(1, 5):              # loop from qualifier 1 to qualifier 4
            inxight_dataframe.loc[index,'qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx)] = predicate_row['qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx)].iloc[0]       
    else:                                              # alternatively just provide the default predicates
        inxight_dataframe.loc[index,'biolinkPredicate'] = 'related_to_at_instance_level' # superclass of affects, affected_by, etc
        inxight_dataframe.loc[index,'inversePredicate'] = 'related_to_at_instance_level' # superclass of affects, affected_by, etc   
        if (pd.isna(inxight_dataframe.loc[index,'attributeName'])):
            inxight_dataframe.loc[index,'attributeName'] = 'attribute name'    


########################################################
#  
# Convert the Inxight Drugs Dataframe to JSON
#
def convert_df_2_json(dataframe):
    relationsMap = {}                                   # Start a new JSON
    for index, row in dataframe.iterrows():             # Find row data for JSON
        if( not pd.isna(row['relation']) ):
            relation = {}
            qualifier_list = []                          # Start a new relation
            done = False
            subject = (row['relation'].split('->',1)[0]).lower()
            relation["predicate"] = row['biolinkPredicate']
            relation['inv_predicate'] = row['inversePredicate']
            if (not pd.isna(row['qualifiedPredicate'])):
                relation['qualifier_predicate'] = row['qualifiedPredicate']
            relation['qualifiers'] = qualifier_list
            if (not pd.isna(row['attributes'])):
                relation['attributes'] = row['attributes'].split('|')

            for qualifier_idx in range(1, 5):           # loop from qualifier 1 to qualifier 4
                if(not type(row['qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx)]) is float):
                    add_qualifer('qualifier_{qualifier_idx}'.format(qualifier_idx = qualifier_idx), row, qualifier_list)
            if not pd.isna(row['biolinkPredicate']) and not pd.isna(row['inversePredicate']):
                relationsMap[row['relation']]= relation     # Add new relation to JSON 
#   Save as a JSON file
    with open('config/relations.json', 'w') as outfile:
        json.dump(relationsMap, outfile, indent=4, sort_keys=True) 


########################################################
#  Add the collection of qualifiers to the list
# 
def add_qualifer(qualifier, row, qualifier_list):
        qualifier_dict = {}
        splits = row[qualifier].split(':',1)
        qualifier_dict['qualifier_type_id'] = splits[0]
        qualifier_dict['qualifier_value'] = splits[1]
        qualifier_list.append(qualifier_dict)


########################################################
# Create and add subject_role_qualifier to the list of
# qualifiers
def add_role_qualifer(subject, qualifier_list):
        qualifier_dict = {}
        qualifier_dict['qualifier_type_id'] = 'subject_role_qualifier'
        qualifier_dict['qualifier_value'] = subject
        qualifier_list.append(qualifier_dict)
        return True      



def exec():
  # Scan the dataframe for data to populate JSON file
    scan_df()


def main():
    dataframe = pd.read_table('data/Inxight_Drugs_Chemical_Relations.tsv', encoding='utf-8-sig')
    convert_df_2_json(dataframe)

if __name__ == '__main__':
    main()