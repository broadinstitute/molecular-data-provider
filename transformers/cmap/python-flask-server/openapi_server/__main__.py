#!/usr/bin/env python3

import connexion

from openapi_server import encoder

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml', arguments={'title': 'API for CMAP gene-list and compound-list expander'},pythonic_params=True)

def main():
    app.run(port=8210, debug=True)


if __name__ == '__main__':
    main()
