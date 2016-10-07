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

from __future__ import print_function
from collections import OrderedDict

from core import StateMachine, CanProcessComposite, Context
from core.utils import dict_strict_update

from .states import *


class SimulatedLinkamT95(CanProcessComposite, object):
    def _initialize_data(self):
        """
        This method is called once on construction. After that, it may be
        manually called again to reset the device to its default state.

        After the first call during construction, the class is frozen.

        This means that attempting to define a new member variable will
        raise an exception. This is to prevent typos from inadvertently
        and silently adding new members instead of accessing existing ones.
        """
        self.serial_command_mode = False
        self.pump_overspeed = False

        self.start_commanded = False
        self.stop_commanded = False
        self.hold_commanded = False

        # Real device remembers values from last run, we use arbitrary defaults
        self.temperature_rate = 5.0  # Rate of change of temperature in C/min
        self.temperature_limit = 0.0  # Target temperature in C

        self.pump_speed = 0  # Pump speed in arbitrary unit, ranging 0 to 30
        self.temperature = 24.0  # Current temperature in C

        self.pump_manual_mode = False
        self.manual_target_speed = 0

    def __init__(self, override_states=None, override_transitions=None):
        super(SimulatedLinkamT95, self).__init__()

        # Create instance of device context. This is shared with all the states of this device.
        self._initialize_data()
        # Define all existing states of the device; the handlers live in states.py
        state_handlers = {
            'init': DefaultInitState(),
            'stopped': DefaultStoppedState(),
            'started': DefaultStartedState(),
            'heat': DefaultHeatState(),
            'hold': DefaultHoldState(),
            'cool': DefaultCoolState(),
        }

        # Allows setup to override state behaviour by passing it to this constructor
        if override_states is not None:
            dict_strict_update(state_handlers, override_states)

        # Define all transitions and the conditions under which they are executed.
        transition_handlers = OrderedDict([
            (('init', 'stopped'), lambda: self.serial_command_mode),

            (('stopped', 'started'), lambda: self.start_commanded),

            (('started', 'stopped'), lambda: self.stop_commanded),
            (('started', 'heat'), lambda: self.temperature < self.temperature_limit),
            (('started', 'hold'), lambda: self.temperature == self.temperature_limit),
            (('started', 'cool'), lambda: self.temperature > self.temperature_limit),

            (('heat', 'hold'),
             lambda: self.temperature == self.temperature_limit or self.hold_commanded),
            (('heat', 'cool'), lambda: self.temperature > self.temperature_limit),
            (('heat', 'stopped'), lambda: self.stop_commanded),

            (('hold', 'heat'),
             lambda: self.temperature < self.temperature_limit and not self.hold_commanded),
            (('hold', 'cool'),
             lambda: self.temperature > self.temperature_limit and not self.hold_commanded),
            (('hold', 'stopped'), lambda: self.stop_commanded),

            (('cool', 'heat'), lambda: self.temperature < self.temperature_limit),
            (('cool', 'hold'),
             lambda: self.temperature == self.temperature_limit or self.hold_commanded),
            (('cool', 'stopped'), lambda: self.stop_commanded),
        ])

        # Allows setup to override transition behaviour by passing it to this constructor
        if override_transitions is not None:
            dict_strict_update(transition_handlers, override_transitions)

        self._csm = StateMachine({
            'initial': 'init',
            'states': state_handlers,
            'transitions': transition_handlers,
        }, context=self)

        # Ensures the state machine object gets a 'process' heartbeat tick
        self.addProcessor(self._csm)
