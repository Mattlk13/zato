# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import Secret_Shadow
from zato.common.const import SECRETS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.simpleio import SIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

def resolve_value(key, value, decrypt_func=None, _default=object(), _secrets=SECRETS):
    """ Resolves final value of a given variable by looking it up in environment if applicable.
    """
    # Skip non-resolvable items
    if not isinstance(value, str):
        return value

    if not value:
        return value

    value = value.decode('utf8') if isinstance(value, bytes) else value

    # It may be an environment variable ..
    if value.startswith('$'):

        # .. but not if it's $$ which is a signal to skip this value ..
        if value.startswith('$$'):
            return value

        # .. a genuine pointer to an environment variable.
        else:
            env_key = value[1:].strip().upper()
            value = os.environ.get(env_key, _default)

            # Use a placeholder if the actual environment key is missing
            if value is _default:
                value = 'Env_Key_Missing_{}'.format(env_key)

    # It may be an encrypted value
    elif key in _secrets.PARAMS and value.startswith(_secrets.PREFIX):
        value = decrypt_func(value)

    # Pre-processed, we can assign this pair to output
    return value

# ################################################################################################################################

def resolve_env_variables(data):
    """ Given a Bunch instance on input, iterates over all items and resolves all keys/values to ones extracted
    from environment variables.
    """
    out = Bunch()
    for key, value in data.items():
        out[key] = resolve_value(None, value)

    return out

# ################################################################################################################################

def replace_query_string_items(sio_config:'SIOServerConfig', data:'str') -> 'str':
    # server.sio_config.
    return data

# ################################################################################################################################
