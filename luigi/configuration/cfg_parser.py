# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
luigi.configuration provides some convenience wrappers around Python's
ConfigParser to get configuration options from config files.

The default location for configuration files is luigi.cfg (or client.cfg) in the current
working directory, then /etc/luigi/client.cfg.

Configuration has largely been superseded by parameters since they can
do essentially everything configuration can do, plus a tighter integration
with the rest of Luigi.

See :doc:`/configuration` for more info.
"""

import os
import warnings

try:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from configparser import ConfigParser, NoOptionError, NoSectionError

from .base_parser import BaseParser


class LuigiConfigParser(BaseParser, ConfigParser):
    NO_DEFAULT = object()
    enabled = True
    _instance = None
    _config_paths = [
        '/etc/luigi/client.cfg',  # Deprecated old-style global luigi config
        '/etc/luigi/luigi.cfg',
        'client.cfg',  # Deprecated old-style local luigi config
        'luigi.cfg',
    ]

    @classmethod
    def reload(cls):
        # Warn about deprecated old-style config paths.
        deprecated_paths = [p for p in cls._config_paths if os.path.basename(p) == 'client.cfg' and os.path.exists(p)]
        if deprecated_paths:
            warnings.warn("Luigi configuration files named 'client.cfg' are deprecated if favor of 'luigi.cfg'. " +
                          "Found: {paths!r}".format(paths=deprecated_paths),
                          DeprecationWarning)

        return cls.instance().read(cls._config_paths)

    def _get_with_default(self, method, section, option, default, expected_type=None, **kwargs):
        """
        Gets the value of the section/option using method.

        Returns default if value is not found.

        Raises an exception if the default value is not None and doesn't match the expected_type.
        """
        try:
            return method(self, section, option, **kwargs)
        except (NoOptionError, NoSectionError):
            if default is LuigiConfigParser.NO_DEFAULT:
                raise
            if expected_type is not None and default is not None and \
               not isinstance(default, expected_type):
                raise
            return default

    def get(self, section, option, default=NO_DEFAULT, **kwargs):
        return self._get_with_default(ConfigParser.get, section, option, default, **kwargs)

    def getboolean(self, section, option, default=NO_DEFAULT):
        return self._get_with_default(ConfigParser.getboolean, section, option, default, bool)

    def getint(self, section, option, default=NO_DEFAULT):
        return self._get_with_default(ConfigParser.getint, section, option, default, int)

    def getfloat(self, section, option, default=NO_DEFAULT):
        return self._get_with_default(ConfigParser.getfloat, section, option, default, float)

    def getintdict(self, section):
        try:
            # Exclude keys from [DEFAULT] section because in general they do not hold int values
            return dict((key, int(value)) for key, value in self.items(section)
                        if key not in {k for k, _ in self.items('DEFAULT')})
        except NoSectionError:
            return {}

    def set(self, section, option, value=None):
        if not ConfigParser.has_section(self, section) and section != self.default_section:
            ConfigParser.add_section(self, section)

        return ConfigParser.set(self, section, option, value)
