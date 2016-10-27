#  -*- coding: utf-8 -*-
# *********************************************************************
# plankton - a library for creating hardware device simulators
# Copyright (C) 2016 European Spallation Source ERIC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************

import unittest

from mock import Mock, call

from plankton.devices import StateMachineDevice
from . import assertRaisesNothing


class MockStateMachineDevice(StateMachineDevice):
    _get_state_handlers = Mock(return_value={'init': {}, 'test': {}})
    _get_initial_state = Mock(return_value='init')
    _get_transition_handlers = Mock(return_value={})
    _initialize_data = Mock()

    existing_member = 1.0


class TestStateMachineDevice(unittest.TestCase):
    def test_init_calls_appropriate_methods(self):
        smd = MockStateMachineDevice()

        smd._get_state_handlers.assert_has_calls([call()])
        smd._get_initial_state.assert_has_calls([call()])
        smd._get_transition_handlers.assert_has_calls([call()])
        smd._initialize_data.assert_has_calls([call()])

    def test_invalid_initial_override_fails(self):
        assertRaisesNothing(self, MockStateMachineDevice)
        assertRaisesNothing(self, MockStateMachineDevice, override_initial_state='init')
        assertRaisesNothing(self, MockStateMachineDevice, override_initial_state='test')

        self.assertRaises(RuntimeError, MockStateMachineDevice, override_initial_state='invalid')

    def test_overriding_undefined_data_fails(self):
        assertRaisesNothing(
            self, MockStateMachineDevice, override_initial_data={'existing_member': 2.0})

        smd = MockStateMachineDevice(override_initial_data={'existing_member': 2.0})
        self.assertEqual(smd.existing_member, 2.0)

        self.assertRaises(AttributeError, MockStateMachineDevice,
                          override_initial_data={'nonexisting_member': 1.0})
