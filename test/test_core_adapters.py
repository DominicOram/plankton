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
import unittest

from plankton.adapters.stream import StreamAdapter
from plankton.core.adapters import is_adapter, AdapterBase
from plankton.core.utils import FromOptionalDependency


class TestIsAdapter(unittest.TestCase):
    def test_not_a_type_returns_false(self):
        self.assertFalse(is_adapter(0.0))
        self.assertFalse(is_adapter(None))

    def test_arbitrary_types_fail(self):
        self.assertFalse(is_adapter(type(3.0)))
        self.assertFalse(is_adapter(FromOptionalDependency))

    def test_adapter_base_is_ignored(self):
        self.assertFalse(is_adapter(AdapterBase))
        self.assertFalse(is_adapter(StreamAdapter))

    def test_adapter_types_work(self):
        class DummyAdapter(AdapterBase):
            pass

        self.assertTrue(is_adapter(DummyAdapter))
