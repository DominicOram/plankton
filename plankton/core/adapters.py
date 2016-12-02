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
This module defines a base class for adapters, called :class:`AdapterBase`.
"""


class AdapterBase(object):
    """
    Base class for adapters

    This class serves as a base class for concrete adapter implementations that expose a device via
    a certain communication protocol. It defines the minimal interface that an adapter must provide
    in order to fit seamlessly into other parts of the framework
    (most importantly :class:`~plankton.core.simulation.Simulation`).

    Sub-classes should re-define the ``protocol``-member to something appropriate. While it is
    explicitly supported to modify it in concrete device interface implementations, it is good
    to have a default (for example ``epics`` or ``stream``).

    An adapter should provide everything that is needed for the communication via the protocol it
    defines. This might involve constructing a server-object, configuring it and starting the
    service (this should happen in :meth:`start_server`). Due to the large differences between
    protocols it is very hard to provide general guidelines here. Please take a look at the
    implementations of existing adapters (:class:`~plankton.adapters.epics.EpicsAdapter`,
    :class:`~plankton.adapters.stream.StreamAdapter`),to get some examples.

    :param arguments: Command line arguments to the adapter, currently ignored.
    """

    interfaces = []

    def __init__(self, arguments=None):
        super(AdapterBase, self).__init__()

    def add_interface(self, new_interface):
        if new_interface.adapter == type(self):
            self.interfaces.append(new_interface)

    def start_server(self):
        """
        This method should be re-implemented to start the infrastructure required for the
        protocol in question. These startup operations are not supposed to be carried out on
        construction of the adapter in order to preserve control over when services are
        started during a run of a simulation.
        """
        pass

    def handle(self, cycle_delay=0.1):
        """
        This function is called on each cycle of a simulation. It should process requests that are
        made via the protocol that exposes the device. The time spent processing should be
        approximately ``cycle_delay`` seconds, during which the adapter may block the current
        process. It is desirable to stick to the provided time, but deviations are permissible if
        necessary due to the way the protocol works.

        :param cycle_delay: Approximate time spent processing requests.
        """
        pass


def is_adapter(obj):
    """
    Returns True if obj is an interface (derived from Adapter), but not defined in
    :mod:`plankton.adapters`.

    :param obj: Object to test.
    :return: True if obj is an interface type.
    """
    return isinstance(obj, type) and issubclass(
        obj, AdapterBase) and not obj.__module__.startswith(
        'plankton.adapters') and obj.__module__ != 'plankton.core.adapters'
