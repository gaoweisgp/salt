# -*- coding: utf-8 -*-
'''

'''

from __future__ import absolute_import, print_function, unicode_literals

import os
import logging
import hashlib

import salt.cache

from salt.ext import six

log = logging.getLogger(__name__)

__virtualname__ = 'cache'

def mk_token(opts, tdata):
    '''
    Mint a new token using the config option hash_type and store tdata with 
    'token' attribute set to the token.

    This module uses the hash of random 512 bytes as a token.

    :param opts: Salt master config options
    :param tdata: token data
    :returns: Token data with new token
    '''

    # TODO
    #   This should be moved to a util that allows more
    #   hash type control and centrally managed.
    hash_type = getattr(hashlib, opts.get('hash_type', 'md5'))
    new_token = six.text_type(hash_type(os.urandom(512)).hexdigest())
    tdata['token'] = new_token
   
    driver = opts.get('eauth_cache_driver', 'localfs')
    log.debug("mk_token using %s storing %s", driver, new_token)
    try:
        cache = salt.cache.Cache(__opts__, driver=driver)
        cache.store('tokens', new_token, tdata)
    except Exception as err:
        log.warning(
            'Cannot mk_token from cache using %s: %s',
            driver, err
        )
        return None

    return tdata

def get_token(opts, token):
    '''
    Fetch the token data from the store.

    :param opts: Salt master config options
    :param token: Token value
    :returns: Token data if successful. Empty dict if failed.
    '''
    driver = opts.get('eauth_cache_driver', 'localfs')
    try:
        cache = salt.cache.Cache(__opts__, driver=driver)
        token = cache.fetch('tokens', token)
    except Exception as err:
        log.warning(
            'Cannot get token %s from cache using %s: %s',
            token, driver, err
        )
        return None

    log.debug("get_token using %s returned %s", driver, token)
    return token

def rm_token(opts, token):
    '''
    Remove token from the store.

    :param opts: Salt master config options
    :param token: Token to remove
    '''
    driver = opts.get('eauth_cache_driver', 'localfs')
    log.debug("rm_token flushing using %s token %s",driver, token)
    try:
        cache = salt.cache.Cache(__opts__, driver=driver)
        cache.flush('tokens', token)
    except Exception as err:
        log.warning(
            'Cannot rm token %s from cache using %s: %s',
            token, driver, err
        )
        return None

def list_tokens(opts):
    '''
    List all tokens in the store.

    :param opts: Salt master config options
    :returns: List of dicts (token_data)
    '''
    driver = opts.get('eauth_cache_driver', 'localfs')
    try:
        cache = salt.cache.Cache(__opts__, driver=driver)
        tokens = cache.list('tokens')
    except Exception as err:
        log.warning(
            'Cannot list tokens from cache using %s: %s',
            driver, err
        )
        return []

    log.debug("list_tokens using %s returned %s", driver, tokens)
    return tokens
