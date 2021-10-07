#!/usr/bin/env python3

import connexion

from openapi_server import encoder

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Transformer API for the Repurposing Hub'},
            pythonic_params=True)

def main():
    app.run(port=8320, debug= True)


if __name__ == '__main__':
    main()
