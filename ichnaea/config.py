"""
Contains helper functionality for reading and parsing configuration files
and parsing of environment variables.
"""

import os
import os.path

from backports.configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
)
import pkg_resources
import simplejson
from six import PY2, string_types

HERE = os.path.dirname(__file__)

RELEASE = None
TESTING = 'TESTING' in os.environ
VERSION = pkg_resources.get_distribution('ichnaea').version
VERSION_FILE = os.path.join(HERE, 'version.json')
VERSION_INFO = {
    'build': None,
    'commit': 'HEAD',
    'source': 'https://github.com/mozilla/ichnaea',
    'tag': 'master',
    'version': VERSION,
}

DB_RW_URI = os.environ.get('DB_RW_URI')
DB_RO_URI = os.environ.get('DB_RO_URI')
GEOIP_PATH = os.environ.get('GEOIP_PATH')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = os.environ.get('REDIS_URI')
if 'REDIS_HOST' in os.environ or 'REDIS_PORT' in os.environ:
    os.environ['REDIS_URI'] = REDIS_URI = \
        'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)

if os.path.isfile(VERSION_FILE):
    with open(VERSION_FILE, 'r') as fd:
        data = simplejson.load(fd)
    VERSION_INFO['build'] = data.get('build', None)
    VERSION_INFO['commit'] = data.get('commit', None)
    VERSION_INFO['tag'] = RELEASE = data.get('tag', None)


class Config(ConfigParser):
    """
    A :class:`configparser.ConfigParser` subclass with added
    functionality.

    :param filename: The path to a configuration file.
    """

    def __init__(self, filename, **kw):
        super(Config, self).__init__(**kw)
        # let's read the file
        if isinstance(filename, string_types):
            self.filename = filename
            self.read(filename)
        else:  # pragma: no cover
            self.filename = None
            self.read_file(filename)

    def get(self, section, option, default=None, **kw):
        """
        A get method which returns the default argument when the option
        cannot be found instead of raising an exception.
        """
        try:
            value = super(Config, self).get(section, option, **kw)
        except (NoOptionError, NoSectionError):  # pragma: no cover
            value = default
        return value

    def get_map(self, section, default=None):
        """
        Return a config section as a dictionary.
        """
        try:
            value = dict(self.items(section))
        except (NoOptionError, NoSectionError):  # pragma: no cover
            value = default
        return value

    def optionxform(self, option):
        """
        Disable automatic lowercasing of option names.
        """
        return option

    def asdict(self):  # pragma: no cover
        """
        Return the entire config as a dict of dicts.
        """
        result = {}
        for section in self.sections():
            result[section] = self.get_map(section)
        return result


class DummyConfig(object):
    """
    A stub implementation of :class:`ichnaea.config.Config` used in tests.

    :param settings: A dict of dicts representing the parsed config
                     settings.
    """

    def __init__(self, settings):
        self.settings = settings

    def get(self, section, option, default=None):  # pragma: no cover
        section_values = self.get_map(section, {})
        return section_values.get(option, default)

    def get_map(self, section, default=None):
        return self.settings.get(section, default)

    def sections(self):
        return list(self.settings.keys())

    def asdict(self):
        result = {}
        for section in self.sections():
            result[section] = self.get_map(section)
        return result


def read_config(filename=None, envvar='ICHNAEA_CFG'):
    """
    Read a configuration file from one of two possible locations:

    1. from the passed in filename,
    2. from the environment variable passed as `envvar`.

    :rtype: :class:`ichnaea.config.Config`
    """
    if filename is None:
        filename = os.environ.get(envvar, '')
        if PY2:  # pragma: no cover
            filename = filename.decode('utf-8')

    return Config(filename)
