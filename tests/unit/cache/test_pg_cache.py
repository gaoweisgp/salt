# -*- coding: utf-8 -*-
'''
tests.unit.cache.test_pg_cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for the Postgres Cache interface
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
import salt.cache.pg_cache as pg_cache
import salt.exceptions

import psycopg2

log = logging.getLogger(__name__)

@skipIf(NO_MOCK, NO_MOCK_REASON)
class PgCacheTestCase(TestCase, LoaderModuleMockMixin):

    def setup_loader_modules(self):
        return {pg_cache: {} }

    def test_fetch_empty(self):
        db_mock = MagicMock()
        with patch.object(pg_cache, '_exec_pg',  db_mock):
            db_mock.return_value.__enter__.return_value.fetchone.return_value = []
            self.assertEqual(pg_cache.fetch('x','y'), {})

    def test_fetch_value(self):
        db_mock = MagicMock()
        with patch.object(pg_cache, '_exec_pg',  db_mock):
            db_mock.return_value.__enter__.return_value.fetchone.return_value = ['somedata']
            self.assertEqual(pg_cache.fetch('x','y'), 'somedata')

    def test_contains_true(self):
        db_mock = MagicMock()
        with patch.object(pg_cache, '_exec_pg',  db_mock):
            db_mock.return_value.__enter__.return_value.fetchone.return_value = [1]
            self.assertEqual(pg_cache.contains('x','y'), True)

    def test_contains_false(self):
        db_mock = MagicMock()
        with patch.object(pg_cache, '_exec_pg',  db_mock):
            db_mock.return_value.__enter__.return_value.fetchone.return_value = []
            self.assertEqual(pg_cache.contains('x','y'), False)

    @patch('psycopg2.connect')
    def test_exec_pg_raise_op_error(self, mock_connect):
        mock_connect.side_effect = MagicMock(side_effect=psycopg2.OperationalError)
        with self.assertRaises(salt.exceptions.SaltMasterError):
            with pg_cache._exec_pg() as cur:
                pass

    @patch('psycopg2.connect')
    def test_exec_pg_rollback(self, mock_connect):
        mock_cur = mock_connect.return_value
        mock_cur.execute.side_effect = MagicMock(side_effect=psycopg2.DatabaseError)
        with pg_cache._exec_pg() as x:
            x.execute("failme")
            x.called_with("ROLLBACK")

    @patch('psycopg2.connect')
    def test_exec_pg_commit(self, mock_connect):
        mock_cur = mock_connect.return_value
        mock_cur.execute.return_value = None
        with pg_cache._exec_pg(commit=True) as x:
            x.execute("an insert statement")
            x.called_with("COMMIT")
