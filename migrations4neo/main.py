import binascii
import ConfigParser
import imp
import os
import argparse

from slugify import Slugify

from . import package_dir
from . import template
from . import utils


PARSER_INIT = 'init'
PARSER_REVISION = 'revision'
PARSER_UPGRADE = 'upgrade'
PARSER_DOWNGRADE = 'downgrade'

MIGRATION_PARSERS = [PARSER_UPGRADE, PARSER_DOWNGRADE]
PARSER_NAMES = [PARSER_INIT, PARSER_REVISION] + MIGRATION_PARSERS

MIG4NEO_DIR = 'mig4neo'

MIG4NEO_PATH = os.path.join(package_dir, MIG4NEO_DIR)
REVISIONS_PATH = os.path.join(MIG4NEO_PATH, 'revisions')

FOLDER_PATHS = [MIG4NEO_PATH, REVISIONS_PATH]

INI_PATH = os.path.join(package_dir, MIG4NEO_DIR, 'mig4neo.ini')
INI_SECTION = 'mig4neo'
INI_DB_KEY = 'neo4j.db_uri'

CANNOT_FIND = """
!!!!!!!!!!!!!
ERROR: Cannot find revisions: {}'
!!!!!!!!!!!!!
"""

MIGRATION_INFO = """
#############
INFO: : {} {}'
#############
"""


def init(directory):
    mig4neo_path = os.path.abspath(directory)
    for dir_path in FOLDER_PATHS:
        dir_path = os.path.join(mig4neo_path, dir_path)
        if os.path.exists(dir_path):
            msg = 'Creating directory {}...already exists'.format(dir_path)
            utils.message(msg)
        else:
            os.makedirs(dir_path)
            msg = 'Creating directory {}...created'.format(dir_path)
            utils.message(msg)

    ini_path = os.path.join(mig4neo_path, ini_path)
    if os.path.exists(ini_path):
        msg = 'Generating ini file {}...already exists'.format(INI_PATH)
        utils.message(msg)
    else:
        db_uri = 'http://user:password@localhost:7474/db/data/'
        config = ConfigParser.RawConfigParser()
        config.add_section('mig4neo')
        config.set(INI_SECTION, INI_DB_KEY, db_uri)

        with open(INI_PATH, 'wb') as ini_file:
            config.write(ini_file)
        msg = 'Generating ini file {}...created'.format(INI_PATH)
        utils.message(msg)


def revision(message):
    mag_slugify = Slugify(to_lower=True)
    mag_slugify.separator = '_'
    message = mag_slugify(message)
    number = binascii.hexlify(os.urandom(5))
    revision_filename = '{}_{}.py'.format(number, message)
    revision_body = template.body.format(number)
    revision_path = os.path.join(REVISIONS_PATH, revision_filename)
    with open(revision_path, 'wb') as revision_file:
        revision_file.write(revision_body)
    msg = 'Generating revision file {}...created'.format(revision_path)
    utils.message(msg)


def run_migrations(revisions, action):
    config = ConfigParser.RawConfigParser()
    config.read(INI_PATH)
    db_uri = config.get(INI_SECTION, INI_DB_KEY)
    os.environ['NEO4J_REST_URL'] = db_uri

    filenames = os.listdir(REVISIONS_PATH)
    filename_numbers = {}
    for filename in filenames:
        key = filename.split('_')[0]
        filename_path = os.path.join(REVISIONS_PATH, filename)
        filename_numbers[key] = filename_path
    revision_numbers = revisions.split(',')

    missing = []
    for revision_number in revision_numbers:
        if revision_number not in filename_numbers:
            missing.append(revision_number)

    if missing:
        missing = ','.join(missing)
        msg = CANNOT_FIND.format(missing)
        utils.message(msg)
        return
    filename_paths = [filename_numbers[name] for name in revision_numbers]
    for filename_path, revision in zip(filename_paths, revisions):
        module = load_module(revision, filename_path)
        getattr(module, action)()
    

def load_module(revision, path):
    with open(path, 'rb') as f:
        return imp.load_source(revision, path, f)


def upgrade(revisions):
    run_migrations(revisions, 'up')
    msg = MIGRATION_INFO.format(revisions, 'upgraded')
    utils.message(msg)


def downgrade(revisions):
    run_migrations(revisions, 'down')
    msg = MIGRATION_INFO.format(revisions, 'downgraded')
    utils.message(msg)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for parser_name in PARSER_NAMES:
        _parser = subparsers.add_parser(parser_name)
        _parser.set_defaults(which=parser_name)

    subparsers.choices.get(PARSER_INIT).add_argument(
        'directory', help='Directory for migrations4neo',
        default=MIG4NEO_DIR
    )
    subparsers.choices.get(PARSER_REVISION).add_argument(
        '-m', '--message', type=str, dest='message',
        help='Create new revision with message',
        default=None
    )
    for migration_parser in MIGRATION_PARSERS:
        subparsers.choices.get(migration_parser).add_argument(
            '-r', '--revisions', dest='revisions',
            help='Upgrades with provided revisions',
            default=None
        )

    #TODO: prettify needed
    parsed_args = parser.parse_args()
    if parsed_args.which == PARSER_INIT:
        init(parsed_args.directory)
    elif parsed_args.which == PARSER_REVISION:
        revision(parsed_args.message)
    elif parsed_args.which == PARSER_UPGRADE:
        upgrade(parsed_args.revisions)
    elif parsed_args.which == PARSER_DOWNGRADE:
        downgrade(parsed_args.revisions)
    else:
        msg = 'Please tell me what to do :)'
        utils.message(msg)
