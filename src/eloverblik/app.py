import random
import logging
from datetime import datetime, timedelta
from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_wtf.csrf import CSRFProtect
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import AlwaysOnSampler

from eloverblik.models import MeteringPoint, MeteringPointType
from eloverblik.db import atomic, inject_session
from eloverblik.settings import (
    SECRET,
    PROJECT_NAME,
    TEMPLATES_DIR,
    TECHNOLOGIES,
    AZURE_APP_INSIGHTS_CONN_STRING,
)


app_kwargs = dict(
    import_name=PROJECT_NAME,
    template_folder=TEMPLATES_DIR,
)

app = Flask(**app_kwargs)
app.logger.setLevel(logging.DEBUG)
app.config['SECRET_KEY'] = SECRET
csrf = CSRFProtect(app)


# Setup logging using OpenCensus / Azure
if AZURE_APP_INSIGHTS_CONN_STRING:
    print('Exporting logs to Azure Application Insight', flush=True)

    def __telemetry_processor(envelope):
        envelope.data.baseData.cloud_roleName = PROJECT_NAME
        envelope.tags['ai.cloud.role'] = PROJECT_NAME

    handler = AzureLogHandler(
        connection_string=AZURE_APP_INSIGHTS_CONN_STRING,
        export_interval=5.0,
    )
    handler.add_telemetry_processor(__telemetry_processor)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    exporter = AzureExporter(connection_string=AZURE_APP_INSIGHTS_CONN_STRING)
    exporter.add_telemetry_processor(__telemetry_processor)

    FlaskMiddleware(
        app=app,
        sampler=AlwaysOnSampler(),
        exporter=exporter,
    )


# -- Onboarding endpoints ----------------------------------------------------


@app.route('/test', methods=['GET'])
def start_onboarding_test():
    return redirect('/onboarding?fromDate=2020-01-01&toDate=2020-12-31&customerKey=1234&returnUrl=https://eloverblik.dk')


@app.route('/onboarding', methods=['GET', 'POST'])
def start_onboarding():
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')
    subject = request.args.get('customerKey')
    return_url = request.args.get('returnUrl')

    if request.form.get('submitted'):
        create_meteringpoints_from_form(subject)
        return redirect(return_url)

    env = {
        'form': None,
        'from_date': from_date,
        'to_date': to_date,
        'subject': subject,
        'return_url': return_url,
        'technologies': sorted(TECHNOLOGIES.keys()),
    }

    return render_template('index.html', **env)


@atomic
def create_meteringpoints_from_form(subject, session):
    for technology in TECHNOLOGIES.keys():
        tech_code, fuel_code = TECHNOLOGIES[technology]

        for type in list(MeteringPointType):
            amount = int(request.form['%s_%s' % (technology, type.value)])

            for i in range(amount):
                session.add(MeteringPoint(
                    subject=subject,
                    gsrn=random_gsrn(),
                    type=type,
                    technology_code=tech_code,
                    fuel_code=fuel_code,
                    street_name='Testpunkt',
                    building_number=str(random.randint(1, 999999)),
                    city_name='Aarhus C.',
                    postcode='8000',
                ))


def random_gsrn():
    s = []
    for i in range(15):
        s.append(str(random.randint(0, 9)))
    return ''.join(s)


# -- API endpoints -----------------------------------------------------------


@app.route('/api/Token', methods=['GET'])
def get_token():
    return 'mock-token'


@app.route('/api/Authorization/Authorization/MeteringPoints/customerKey/<subject>', methods=['GET'])
@inject_session
def get_meteringpoints(subject, session):
    meteringpints = session.query(MeteringPoint) \
        .filter_by(subject=subject) \
        .all()

    results = []

    for meteringpint in meteringpints:
        results.append({
            'meteringPointId': meteringpint.gsrn,
            'typeOfMP': meteringpint.type.value,
            'streetCode': meteringpint.street_code,
            'streetName': meteringpint.street_name,
            'buildingNumber': meteringpint.building_number,
            'cityName': meteringpint.city_name,
            'postcode': meteringpint.postcode,
            'municipalityCode': meteringpint.municipality_code,
        })

    return jsonify({'result': results})


@app.route('/api/MeterData/GetTimeSeries/<date_from>/<date_to>/Hour', methods=['GET'])
def get_time_series(date_from, date_to):
    begin = datetime.strptime(date_from, '%Y-%m-%d')
    end = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23)
    current = begin

    points = []
    position = 0

    while current < end:
        points.append({
            'position': position,
            'quantity': random.randint(1, 10),
        })
        current += timedelta(hours=1)
        position += 1

    return {
        'result': [
            {
                'MyEnergyData_MarketDocument': {
                    'TimeSeries': [
                        {
                            'mrid': 'GSRN',
                            'measurement_Unit.name': 'KWH',
                            'Period': [
                                {
                                    'point': points,
                                    'timeInterval': {
                                        'start': str(begin),
                                        'end': str(end),
                                    },
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }


if __name__ == '__main__':
    app.run(port=8766)
