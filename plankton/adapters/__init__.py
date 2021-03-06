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
This module defines a base class for adapters and some supporting infrastructure.
"""

import importlib
import inspect
from ..core.exceptions import PlanktonException


class Adapter(object):
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

    :param device: Device that is supposed to be exposed. Available as ``_device``.
    :param arguments: Command line arguments to the adapter, currently ignored.
    """
    protocol = None

    def __init__(self, device, arguments=None):
        super(Adapter, self).__init__()
        self._device = device

    @property
    def documentation(self):
        """
        This property can be overridden in a sub-class to provide protocol documentation to users
        at runtime. By default it returns the indentation cleaned-up docstring of the class.
        """
        return inspect.getdoc(self) or ''

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
    try:
        return issubclass(obj, Adapter) and not obj.__module__.startswith('plankton.adapters')
    except TypeError:
        return False


def get_available_adapters(device_name, device_package):
    """
    This helper function returns a dictionary with name/type pairs. It imports the module
    ``device_package.device_name.adapters`` and puts those members of the module that inherit
    from :class:`Adapter` into the dictionary.

    :param device_name: Device name for which to get the adapters.
    :param device_package: Name of the package where devices are defined.
    :return: Dictionary of name/type pairs for available adapters for that device.
    """
    adapters = dict()

    try:
        adapter_module = importlib.import_module(
            '{}.{}.{}'.format(device_package, device_name, 'interfaces'))
        module_members = {name: getattr(adapter_module, name) for name in dir(adapter_module)}

        for name, member in module_members.items():
            if is_adapter(member):
                adapters[name] = member
    except ImportError:
        pass

    device_module = importlib.import_module('{}.{}'.format(device_package, device_name))

    for member in dir(device_module):
        member_object = getattr(device_module, member)

        if is_adapter(member_object):
            adapters[member] = member_object

    return adapters


def import_adapter(device_name, protocol_name, device_package='devices'):
    """
    This function tries to import an adapter for the given device that implements
    the requested protocol. If no adapter for that protocol exists, an exception
    is raised. If protocol name is None, the function returns an
    unspecified adapter. If no adapters are found at all, an error is raised.

    :param device_name: Name of device for which an adapter is requested.
    :param protocol_name: Requested protocol implemented by adapter.
    :param device_package: Name of the package where devices are defined.
    :return: Adapter class that implements requested protocol for the specified device.
    """
    available_adapters = get_available_adapters(device_name, device_package)

    if not available_adapters:
        raise PlanktonException(
            'Could not find any communication interfaces for device \'{}\'.'.format(device_name))

    if not protocol_name:
        return list(available_adapters.values())[0]

    for adapter in available_adapters.values():
        if adapter.protocol == protocol_name:
            return adapter

    raise PlanktonException(
        'No interface for device \'{}\' implementing protocol \'{}\' '
        'could be found.\nPlease check the spelling and the '
        '-k and -a flags of the run script.'.format(device_name, protocol_name))


class ForwardProperty(object):
    """
    This is a small helper class that can be used to act as
    a forwarding property to relay property setting/getting
    to a member of the class it's installed on.

    This is a small helper class that can be used to act as
    a forwarding property to relay property setting/getting
    to a member of the class it's installed on.

    Typical use would be:

    .. sourcecode:: Python

        a = Foo()
        a._b = Bar() # Bar has property baz

        type(a).forward = ForwardProperty('_b', 'baz')

        a.forward = 10 # equivalent to a._b.baz = 10

    Note that this modifies the type ``Foo``. Usage must thus be
    limited to cases where this type modification is
    acceptable.

    :param target_member: Target member to forward to.
    :param property_name: Property of target to access.
    :param instance: Object from which to obtain target_member for the purpose of extracting
                     the docstring of the property identified by property_name. If it doesn't
                     exist on the type, of target_member, the docstring is not copied.

    .. seealso:: See :class:`ForwardMethod` to forward method calls to another object.
    """
    def __init__(self, target_member, property_name, instance=None):
        self._target_member = target_member
        self._prop = property_name

        # Extract docstring from the property that's being forwarded.
        # The property exists in the type of the specified target_member of instance,
        # so getattr must be called on the type, not object, otherwise the
        # docstring of the returned value would be stored.
        self.__doc__ = getattr(type(getattr(instance, self._target_member)),
                               self._prop, None).__doc__

    def __get__(self, instance, type=None):
        """
        This method forwards property read access on instance
        to the member of instance that was selected in __init__.

        :param instance: Instance of type.
        :param type: Type.
        :return: Attribute value of member property.
        """
        if instance is not None:
            return getattr(getattr(instance, self._target_member), self._prop)

        return self

    def __set__(self, instance, value):
        """
        This method forwards property write access on instance
        to the member of instance that was selected in __init__.

        :param instance: Instance of type.
        :param value: Value of property.
        """

        setattr(getattr(instance, self._target_member), self._prop, value)


class ForwardMethod(object):
    """
    Small helper to forward calls to another target.

    It can be used like this:

    .. sourcecode:: Python

        a = Foo()
        b = Bar()  # Bar has method baz(parameter)

        a.forward = ForwardProperty(b, 'baz')
        a.forward(10)  # Calls b.baz(10)

    .. seealso:: See :class:`ForwardProperty` for forwarding properties.
    """
    def __init__(self, target, method):
        self._target = target
        self._method = method

        self.__doc__ = getattr(self._target, self._method).__doc__

    def __call__(self, *args, **kwargs):
        return getattr(self._target, self._method)(*args, **kwargs)
