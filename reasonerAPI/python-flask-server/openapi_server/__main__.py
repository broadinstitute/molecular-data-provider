#!/usr/bin/env python3

import connexion
import os
from openapi_server.controllers.utils import get_logger

from openapi_server import encoder

# environment variables
MOLEPRO_PORT = os.environ.get('MOLEPRO_PORT')

# get logger 
logger = get_logger(__name__)

# open telemetry section
# check to make sure dev flag is not on (open telemetry not loaded if on)
IS_DEV = False
OTEL_ENABLED = False
ENV_IS_DEV = os.environ.get('IS_DEV')
if ENV_IS_DEV:
    IS_DEV = True
logger.info('Molepro environment IS_DEV flag set to {}'.format(IS_DEV))

# if not DEV environment, then load open telemetry
if not IS_DEV:
    # import open telemetry
    try:
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME as telemetery_service_name_key, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        # from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
        OTEL_ENABLED = True
        logger.info("OPENTELEMETRY imported; OTEL_ENABLED set to: {}".format(OTEL_ENABLED))
    except ImportError:
        OTEL_ENABLED = False
        logger.info("OPENTELEMETRY import FAILED; OTEL_ENABLED set to: {}".format(OTEL_ENABLED))

# methods
def load_otel(molepro_app, otel_enabled=False):
    if otel_enabled:
        logger.info('About to instrument app for OTEL')

        # set the service name for our trace provider
        otel_service_name = 'molepro'
        tp = TracerProvider(
                resource=Resource.create({telemetery_service_name_key: otel_service_name})
            )
        # create an exporter to jaeger
        jaeger_host = 'jaeger-otel-agent.sri'
        jaeger_port = 6831
        jaeger_exporter = JaegerExporter(
                    agent_host_name=jaeger_host,
                    agent_port=jaeger_port,
                )
        # here we use the exporter to export each span in a trace
        tp.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        trace.set_tracer_provider(
            tp
        )
        # otel_excluded_urls = 'api/dev/.*'
        otel_excluded_urls = 'ui/.*'
        FlaskInstrumentor().instrument_app(molepro_app.app, excluded_urls=otel_excluded_urls)
        RequestsInstrumentor().instrument()
        logger.info('Finished instrumenting app for OTEL')
    else:
        logger.info('OTEL is set to {}, so not instrumenting app for OTEL'.format(otel_enabled))



app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'MolePro'},
            pythonic_params=True)

# if not DEV enviroment and open telemetry libraries loaded properly, enable tracing on the application
# start open telemetry
if not IS_DEV:
    logger.info("Molepro DEV set to: {}, initializing opentelemetry with OTEL_ENABLED set to: {}".format(IS_DEV, OTEL_ENABLED))
    load_otel(molepro_app=app, otel_enabled=OTEL_ENABLED)


def main():
    app.run(port=MOLEPRO_PORT)


if __name__ == '__main__':
    main()
