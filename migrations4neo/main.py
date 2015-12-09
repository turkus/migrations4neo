import binascii
import ConfigParser
import os
import argparse

from slugify import Slugify

from . import package_dir
from . import template
from . import utils


PARSER_INIT = 'init'
PARSER_REVISION = 'revision'
PARSER_UPGRADE = 'upgrade'

PARSER_NAMES = [PARSER_INIT, PARSER_REVISION, PARSER_UPGRADE]

MIG4NEO_DIR = 'mig4neo'

MIG4NEO_PATH = os.path.join(package_dir, MIG4NEO_DIR)
REVISIONS_PATH = os.path.join(MIG4NEO_PATH, 'revisions')

FOLDER_PATHS = [MIG4NEO_PATH, REVISIONS_PATH]

INI_PATH = os.path.join(package_dir, MIG4NEO_DIR, 'mig4neo.ini')
INI_SECTION = 'mig4neo'
INI_DB_KEY = 'neo4j.db_uri'


def init():
    for dir_path in FOLDER_PATHS:
        if os.path.exists(dir_path):
            msg = 'Creating directory {}...already exists'.format(dir_path)
            utils.message(msg)
        else:
            os.makedirs(dir_path)
            msg = 'Creating directory {}...created'.format(dir_path)
            utils.message(msg)

    if os.path.exists(INI_PATH):
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


def upgrade(revisions):
    config = ConfigParser.RawConfigParser()
    config.read(INI_PATH)
    db_uri = config.get(INI_SECTION, INI_DB_KEY)
    os.environ['NEO4J_REST_URL'] = db_uri

    filenames = os.listdir(REVISIONS_PATH)
    filename_numbers = {}
    for filename in filenames:
        key = filename.split('-')[0]
        filename_numbers[key] = filename
    revision_numbers = revisions.split(',')
    #TODO: handle upgrade/downgrade
    if True:
        msg = 'Cannot find revisions: {}'.format(missing)
        utils.message(msg)
    else:
        msg = '{} upgraded'.format(revisions)
        utils.message(msg)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    for parser_name in PARSER_NAMES:
        _parser = subparsers.add_parser(parser_name)
        _parser.set_defaults(which=parser_name)

    subparsers.choices.get(PARSER_REVISION).add_argument(
        '-m', '--message', type=str, dest='message',
        help='Create new revision with message',
        default=None
    )
    subparsers.choices.get(PARSER_UPGRADE).add_argument(
        '-r', '--revisions', dest='revisions',
        help='Upgrades with provided revisions',
        default=None
    )

    parsed_args = parser.parse_args()
    if parsed_args.which == PARSER_INIT:
        init()
    elif parsed_args.which == PARSER_REVISION:
        revision(parsed_args.message)
    elif parsed_args.which == PARSER_UPGRADE:
        upgrade(parsed_args.revisions)
    else:
        msg = 'Please tell me what to do :)'
        utils.message(msg)


if __name__ == '__main__':
    main()
