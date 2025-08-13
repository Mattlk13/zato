# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
from logging import getLogger

from traceback import format_exc



# Zato
from zato.common.typing_ import any_, dict_

# werkzeug
from werkzeug.routing import Map, Rule

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import PubSub
from zato.common.util.api import new_cid, utcnow
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.util import get_username_to_sec_name_mapping

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

# ################################################################################################################################
# ################################################################################################################################

class UnauthorizedException(Exception):
    def __init__(self, cid:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class BadRequestException(Exception):
    def __init__(self, cid:'str', message:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        self.message = message
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################



# ################################################################################################################################
# ################################################################################################################################

class BaseServer:

    def __init__(
        self,
        host:'str',
        port:'int',
        should_init_broker_client:'bool'=False,
    ) -> 'None':
        self.host = host
        self.port = port
        self.users = {}

        # Build our broker client
        self.broker_client = BrokerClient(consumer_drain_events_timeout=0.1)
        self.broker_client.ping_connection()

        # Initialize the backend
        self.backend = RESTBackend(self, self.broker_client)

        # Share references for backward compatibility and simpler access
        self.topics = self.backend.topics
        self.subs_by_topic = self.backend.subs_by_topic

        # Initialize broker client if requested (worker process only)
        if should_init_broker_client:
            self.init_broker_client()

        # URL routing configuration
        self.url_map = Map([

            #
            # Get messages for username
            #
            Rule('/pubsub/messages/get', endpoint='on_messages_get', methods=['POST']),

            #
            # Publish to topic
            #
            Rule('/pubsub/topic/<topic_name>', endpoint='on_publish', methods=['POST']),

            #
            # Subscribe
            #
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='on_subscribe', methods=['POST']),

            #
            # Unsubscribe
            #
            Rule('/pubsub/unsubscribe/topic/<topic_name>', endpoint='on_unsubscribe', methods=['POST']),

            #
            # Ping endpoint
            #
            Rule('/pubsub/health', endpoint='on_health_check', methods=['GET']),

            #
            # Internal details
            #
            Rule('/pubsub/admin/diagnostics', endpoint='on_admin_diagnostics', methods=['GET']),
        ])

# ################################################################################################################################

    def init_broker_client(self):

        # Delete the queue to remove any message we don't want to read since they were published when we were not running,
        # and then create it all again so we have a fresh start ..
        self.broker_client.delete_queue('pubsub')
        self.broker_client.create_internal_queue('pubsub')

        # .. and now, start our subscriber.
        self.backend.start_internal_pubusb_subscriber()

# ################################################################################################################################

    def _load_users(self, cid:'str') -> 'None':
        """ Load users from security definitions.
        """

        # Prepare our input ..
        service = 'zato.security.basic-auth.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True,
        }

        # .. invoke the service ..
        response = self.backend.invoke_service_with_pubsub(service, request)

        # .. log what we've received ..
        len_response = len(response)
        if len_response == 1:
            logger.info('Loading 1 user')
        elif len_response > 0:
            logger.info(f'Loading {len_response} users')
        else:
            logger.info('No users to load')

        # .. process each user ..
        for item in response:
            try:
                # .. extract what we need ..
                sec_name = item['name']
                username = item['username']
                password = item['password']

                # Add user credentials
                self.create_user(cid, sec_name, username, password)

            except Exception:
                logger.error(f'[{cid}] Error processing user {item}: {format_exc()}')

        logger.info('Finished loading users')

# ################################################################################################################################

    def _load_topics(self, cid:'str') -> 'None':
        """ Load topics from topic definitions.
        """

        # Prepare our input ..
        service = 'zato.pubsub.topic.get-list'
        request = {
            'cluster_id': 1
        }

        # .. invoke the service ..
        response = self.backend.invoke_service_with_pubsub(service, request)

        # .. log what we've received ..
        len_response = len(response)
        if len_response == 1:
            logger.info('Loading 1 topic')
        elif len_response > 0:
            logger.info(f'Loading {len_response} topics')
        else:
            logger.info('No topics to load')

        # .. process each topic ..
        for item in response:
            try:
                # .. extract what we need ..
                topic_name = item['name']

                # Create the topic
                self.backend.create_topic(cid, 'config', topic_name)

            except Exception:
                logger.error(f'[{cid}] Error processing topic {item}: {format_exc()}')

        logger.info('Finished loading topics')

# ################################################################################################################################

    def _load_subscriptions(self, cid:'str') -> 'None':
        """ Load subscriptions from server and set up the pub/sub structure.
        """

        # Prepare our input ..
        service = 'zato.pubsub.subscription.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True
        }

        # .. invoke the service ..
        response = self.backend.invoke_service_with_pubsub(service, request)

        # .. log what we've received ..
        len_response = len(response)
        if len_response == 1:
            logger.info('Loading 1 subscription')
        elif len_response > 0:
            logger.info(f'Loading {len_response} subscriptions')
        else:
            logger.info('No subscriptions to load')

        # Get security definitions for username lookup
        username_to_sec_name = get_username_to_sec_name_mapping(self.backend)

        # .. process each subscription ..
        for item in response:

            try:
                # .. extract what we need ..
                sec_name = item['sec_name']
                username = item['username']
                password = item['password']
                topic_names = item.get('topic_name_list') or []
                sub_key = item['sub_key']

                # Add user credentials
                self.create_user(cid, sec_name, username, password)

                # Handle multiple topics (comma-separated)
                for topic_name in topic_names:

                    topic_name = topic_name.strip()
                    if not topic_name:
                        continue

                    logger.debug(f'[{cid}] Registering subscription: `{username}` -> `{topic_name}`')

                    # Create the subscription
                    _ = self.backend.register_subscription(cid, topic_name, username, username_to_sec_name, sub_key)

            except Exception:
                logger.error(f'[{cid}] Error processing subscription {item}: {format_exc()}')

        logger.info('Finished loading subscriptions')


# ################################################################################################################################

    def _load_permissions(self, cid:'str') -> 'None':
        """ Load permissions from server and set up the matcher structure.
        """

        # Prepare our input ..
        service = 'zato.pubsub.permission.get-list'
        request = {
            'cluster_id': 1,
        }

        try:
            # .. invoke the service ..
            response = self.backend.invoke_service_with_pubsub(service, request)

            # .. log what we've received ..
            len_response = len(response)
            if len_response == 1:
                logger.info('Loading 1 permission')
            elif len_response > 0:
                logger.info(f'Loading {len_response} permissions')
            else:
                logger.info('No permissions to load')

            # Group permissions by sec_name
            permissions_by_sec_name = {}
            for item in response:
                try:
                    sec_name = item['name']
                    pattern = item['pattern']
                    access_type = item['access_type']

                    if sec_name not in permissions_by_sec_name:
                        permissions_by_sec_name[sec_name] = []

                    permissions_by_sec_name[sec_name].append({
                        'pattern': pattern,
                        'access_type': access_type
                    })

                except Exception:
                    logger.error(f'[{cid}] Error processing permission {item}: {format_exc()}')

            # Add permissions to pattern matcher
            total_permissions_loaded = 0
            for sec_name, permissions in permissions_by_sec_name.items():
                # Find username by sec_name
                username = None
                for username_key, config in self.users.items():
                    if config['sec_name'] == sec_name:
                        username = username_key
                        break

                if username:
                    self.backend.pattern_matcher.add_client(username, permissions)
                    total_permissions_loaded += len(permissions)
                    logger.info(f'[{cid}] Added {len(permissions)} permissions for {username}')
                else:
                    logger.info(f'[{cid}] User not found for permission loading: {sec_name}')

            logger.info('Finished loading permissions')
            return total_permissions_loaded

        except Exception:
            logger.warning(f'[{cid}] Could not load permissions: {format_exc()}')
            return 0

# ################################################################################################################################

    def create_user(self, cid:'str', sec_name:'str', username:'str', password:'str') -> 'None':
        if username not in self.users:
            logger.info(f'[{cid}] Adding user credentials for `{username}` (`{sec_name}`)')
            self.users[username] = {'sec_name': sec_name, 'password': password}
        else:
            logger.debug(f'[{cid}] User already exists: `{username}` (`{sec_name}`)')

# ################################################################################################################################

    def edit_user(self, cid:'str', old_username:'str', new_username:'str') -> 'None':

        if old_username not in self.users:
            logger.info(f'[{cid}] User not found: `{old_username}`')
            return

        if new_username in self.users:
            logger.info(f'[{cid}] Cannot change username, target already exists: `{new_username}`')
            return

        # Store the user data
        user_data = self.users[old_username]
        sec_name = user_data['sec_name']
        password = user_data['password']

        # Create the new user entry
        self.users[new_username] = {'sec_name': sec_name, 'password': password}

        # Remove the old username
        del self.users[old_username]

        logger.info(f'[{cid}] Changed username from `{old_username}` to `{new_username}`')

# ################################################################################################################################

    def setup(self) -> 'None':
        """ Set up the server, loading users, topics, and subscriptions from YAML config.
        """
        cid = new_cid()

        # For later use ..
        start = utcnow()

        # .. load all the initial users ..
        self._load_users(cid)

        # .. load all the initial topics ..
        self._load_topics(cid)

        # .. load all the initial subscriptions ..
        self._load_subscriptions(cid)

        # .. load the initial permissions too ..
        permission_count = self._load_permissions(cid)

        # .. we're going to need it in a moment ..
        end = utcnow()

        user_count = len(self.users)
        topic_count = len(self.backend.topics)
        subscription_count = sum(len(subs) for subs in self.backend.subs_by_topic.values())
        client_count = self.backend.pattern_matcher.get_client_count()

        logger.info(f'[{cid}] ✅ Setup complete in {end - start}')
        logger.info(f'[{cid}] 🠊 {user_count} {"user" if user_count == 1 else "users"}')
        logger.info(f'[{cid}] 🠊 {topic_count} {"topic" if topic_count == 1 else "topics"}')
        logger.info(f'[{cid}] 🠊 {subscription_count} {"subscription" if subscription_count == 1 else "subscriptions"}')
        logger.info(f'[{cid}] 🠊 {client_count} {"user" if client_count == 1 else "users"} with {permission_count} {"permission" if permission_count == 1 else "permissions"}')

# ################################################################################################################################
# ################################################################################################################################
