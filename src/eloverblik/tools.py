import random
import requests

from eloverblik.settings import ENERGY_TYPE_SERVICE_URL


def random_gsrn():
    s = []
    for i in range(15):
        s.append(str(random.randint(0, 9)))
    return ''.join(s)


def register_energy_type(gsrn, tech, fuel):
    requests.post(
        url='%s/add-energy-type' % ENERGY_TYPE_SERVICE_URL,
        data={
            'gsrn': gsrn,
            'tech': tech,
            'fuel': fuel,
        }
    )

