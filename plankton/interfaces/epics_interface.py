# -*- coding: utf-8 -*-
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

from plankton.core.interfaces import InterfaceBase
from plankton.core.utils import ForwardProperty
from plankton.adapters.epics import EpicsAdapter


class EpicsInterface(InterfaceBase):
    pvs = None

    def __init__(self, device):
        super(EpicsInterface, self).__init__(device)

        self._create_properties(self.pvs.values())

    def _create_properties(self, pvs):
        for pv in pvs:
            prop = pv.property

            if prop not in dir(self):
                if prop not in dir(self._device):
                    raise AttributeError('Can not find property \''
                                         + prop + '\' in device or interface.')
                setattr(type(self), prop, ForwardProperty('_device', prop, instance=self))

    @property
    def adapter(self):
        return EpicsAdapter

    @property
    def protocol(self):
        return 'epics'
