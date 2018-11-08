# -*- coding: utf-8 -*-
'''
tests.unit.tokens.test_cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for the tokens cache interface
'''

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
import logging

# Import Salt Testing libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    MagicMock,
    NO_MOCK,
    NO_MOCK_REASON,
    patch
)

# Import Salt libs
import salt.cache
import salt.tokens.cache as cache
import salt.exceptions

log = logging.getLogger(__name__)

@skipIf(NO_MOCK, NO_MOCK_REASON)
class CacheTokenTestCase(TestCase, LoaderModuleMockMixin):

    def setup_loader_modules(self):
        return {
            cache: {
                '__opts__': { }
            } 
        }

    @patch("salt.cache.Cache")
    def test_mk_token(self, mock_cache):
        inst = mock_cache.return_value
        inst.store.return_value = None 
        res = cache.mk_token({}, {})
        self.assertTrue('token' in res)

    @patch("salt.cache.Cache")
    def test_mk_token_none(self, mock_cache):
        inst = mock_cache.return_value
        inst.store.side_effect = MagicMock(side_effect=Exception)
        self.assertEqual(cache.mk_token({}, {}), None)
