# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from unittest import mock

import snapcraft
from snapcraft import tests
from snapcraft.plugins import make


class MakePluginTestCase(tests.TestCase):

    def setUp(self):
        super().setUp()

        class Options:
            makefile = None
            make_parameters = []

        self.options = Options()
        self.project_options = snapcraft.ProjectOptions()

        patcher = mock.patch('snapcraft.repo.Ubuntu')
        self.ubuntu_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_schema(self):
        schema = make.MakePlugin.schema()

        properties = schema['properties']
        self.assertTrue('makefile' in properties,
                        'Expected "makefile" to be included in properties')
        self.assertTrue(
            'make-parameters' in properties,
            'Expected "make-parameters" to be included in properties')

        makefile = properties['makefile']
        self.assertTrue('type' in makefile,
                        'Expected "type" to be included in "makefile"')

        makefile_type = makefile['type']
        self.assertEqual(makefile_type, 'string',
                         'Expected "makefile" "type" to be "string", but it '
                         'was "{}"'.format(makefile_type))

        make_parameters = properties['make-parameters']
        self.assertTrue('type' in make_parameters,
                        'Expected "type" to be included in "make-parameters"')

        make_parameters_type = make_parameters['type']
        self.assertEqual(
            make_parameters_type, 'array',
            'Expected "make-parameters" "type" to be "array", but it '
            'was "{}"'.format(make_parameters_type))

        build_properties = schema['build-properties']
        self.assertEqual(2, len(build_properties))
        self.assertTrue('makefile' in build_properties)
        self.assertTrue('make-parameters' in build_properties)

    @mock.patch.object(make.MakePlugin, 'run')
    def test_build(self, run_mock):
        plugin = make.MakePlugin('test-part', self.options,
                                 self.project_options)
        os.makedirs(plugin.sourcedir)

        plugin.build()

        self.assertEqual(2, run_mock.call_count)
        run_mock.assert_has_calls([
            mock.call(['make', '-j2']),
            mock.call(['make', 'install',
                       'DESTDIR={}'.format(plugin.installdir)])
        ])

    @mock.patch.object(make.MakePlugin, 'run')
    def test_build_makefile(self, run_mock):
        self.options.makefile = 'makefile.linux'
        plugin = make.MakePlugin('test-part', self.options,
                                 self.project_options)
        os.makedirs(plugin.sourcedir)

        plugin.build()

        self.assertEqual(2, run_mock.call_count)
        run_mock.assert_has_calls([
            mock.call(['make', '-f', 'makefile.linux', '-j2']),
            mock.call(['make', '-f', 'makefile.linux', 'install',
                       'DESTDIR={}'.format(plugin.installdir)])
        ])
