import pandas as pd
import json

########################################################
#  
# Convert the DGIdb prefix Dataframe to JSON
#
def convert_df_2_json(dataframe):

    # print(dataframe.head(2))
    # with open('file.json', 'w') as f:
    #     f.write(dataframe.to_json(orient='records', lines=True))


    dgidbMap = {}                                       # Start a new JSON
    for index, row in dataframe.iterrows():             # Find row data for JSON
        if( not pd.isna(row['DGIdb_prefix']) ):         # e.g.,PUBCHEM.COMPOUND
            prefix = {}                                 # Start a new prefix mapping 
            mapping = {}                                                       
            mapping['field_name'] = row['field_name']
            mapping['molepro_prefix'] = row['molepro_prefix']
            prefix[row['DGIdb_prefix']] = mapping

            dgidbMap[row['DGIdb_prefix']]= mapping                    # Add new mapping to JSON

#                
    for key in dgidbMap:
        print('key:', key)

#   Save as a JSON file
    with open('../python-flask-server/config/DGIdb_prefixes.json', 'w') as outfile:
        json.dump(dgidbMap, outfile, indent=4, sort_keys=False) 


def main():
    dataframe = pd.read_csv('DGIdb_prefixes.csv', sep=",", encoding='utf-8-sig')
    convert_df_2_json(dataframe)

if __name__ == '__main__':
    main()