#!/usr/bin/env python
# -*- coding: utf-8 -*-

import crudalchemy
import unittest


class File(object):
    pass


class TestsBase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_usage(self):
        config = None
        proxy = crudalchemy.Proxy(File)
        config.include(proxy.includeme)
