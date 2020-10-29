import os


AZURE_APP_INSIGHTS_CONN_STRING = os.environ.get(
    'AZURE_APP_INSIGHTS_CONN_STRING')


# -- Project -----------------------------------------------------------------

PROJECT_NAME = 'FakeEloverblik'
SECRET = 'secret!'
# SECRET = os.environ['SECRET']


# -- Directories/paths -------------------------------------------------------

__current_file = os.path.abspath(__file__)
__current_folder = os.path.split(__current_file)[0]

SOURCE_DIR = os.path.abspath(os.path.join(__current_folder, '..'))
MIGRATIONS_DIR = os.path.join(SOURCE_DIR, 'migrations')
# ALEMBIC_CONFIG_PATH = os.path.join(MIGRATIONS_DIR, 'alembic.ini')
TEMPLATES_DIR = os.path.join(SOURCE_DIR, 'templates')
# STATIC_DIR = os.path.join(SOURCE_DIR, 'static')


# -- Database ----------------------------------------------------------------

SQL_ALCHEMY_SETTINGS = {
    'echo': False,
    'pool_pre_ping': True,
    'pool_size': 1,
}

DATABASE_URI = os.environ['DATABASE_URI']


# -- Misc --------------------------------------------------------------------

ENERGY_TYPE_SERVICE_URL = os.environ['ENERGY_TYPE_SERVICE_URL']

TECHNOLOGIES = {
    # Technology : (TechnologyCode, FuelCode)

    'Coal': ('T050000', 'F02010100'),
    'Wind': ('T020000', 'F01050100'),
    'Biogas': ('T050000', 'F01030000'),
    'Waste': ('T050000', 'F02010400'),
    'Oil': ('T050000', 'F02020000'),
    'Hydro': ('T030000', 'F01050200'),
    'Naturalgas': ('T050000', 'F02030100'),
    'Solar': ('T010000', 'F01040100'),
    'Marine': ('T040000', 'F01050200'),
    'Biomass': ('T050000', 'F01010000'),
    'Nuclear': ('T060000', 'F03010100'),
}
