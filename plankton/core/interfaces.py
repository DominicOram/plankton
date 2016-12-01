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

"""
The interface module contains :class:`InterfaceBase`, which is a common base class for all
device interfaces. The term "interface" should not be confused with the identical term from the
context of object oriented programming. In this context it describes the set of available commands
that are available for interacting with a hardware device.
"""


class InterfaceBase(object):
    @property
    def adapter(self):
        raise NotImplementedError(
            'The adapter property must be re-implemented in each interface class.')

    @property
    def protocol(self):
        raise NotImplementedError(
            'The protocol property must be re-implemented in each interface class.')

