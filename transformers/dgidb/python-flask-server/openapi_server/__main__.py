#!/usr/bin/env python3

import connexion

from openapi_server import encoder

# Create the application instance using Connexion rather than Flask
# (Internally, the Flask app is still created but it now has additional
# functionality included)
# The parameter "specification_dir" informs Connexion in what directory to 
# find its configuration file, in this case it is /openapi.
app = connexion.App(__name__, specification_dir='./openapi/')

app.app.json_encoder = encoder.JSONEncoder

# Reads the openapi.yaml file from the specification directory
# to configure the endpoints
app.add_api('openapi.yaml',
            arguments={'title': 'Transformer API for DGIdb'},
            pythonic_params=True)

def main():
    app.run(port=8330,debug=True)

# If we are running in standalone mode, run the application
if __name__ == '__main__':
    main()
