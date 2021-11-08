#!/usr/bin/env python3

import connexion
import os

from openapi_server import encoder

# environment variables
MOLEPRO_PORT = os.environ.get('MOLEPRO_PORT')

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Molecular Data Provider for NCATS Biomedical Translator'},
            pythonic_params=True)

def main():
    app.run(port=MOLEPRO_PORT)


if __name__ == '__main__':
    main()
