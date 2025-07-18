# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import boolnone, dataclass, intnone, strnone

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConnectorConfig:
    id: int
    name: str
    port: intnone
    address: strnone
    is_active: boolnone
    pool_size: intnone
    def_name: strnone
    old_name: strnone
    password: strnone
    service_name: strnone

# ################################################################################################################################
# ################################################################################################################################
