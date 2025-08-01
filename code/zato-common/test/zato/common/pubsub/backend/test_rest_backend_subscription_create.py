# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import Mock

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendSubscriptionCreateTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_single_topic(self):

        # Create the broker message
        msg = {
            'cid': 'test-cid-123',
            'sub_key': 'sk-test-123',
            'sec_name': 'test_user',
            'topic_name_list': ['orders.new']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert subscription was created
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertIn('test_user', self.backend.subs_by_topic['orders.new'])

        subscription = self.backend.subs_by_topic['orders.new']['test_user']
        self.assertEqual(subscription.topic_name, 'orders.new')
        self.assertEqual(subscription.sec_name, 'test_user')
        self.assertEqual(subscription.sub_key, 'sk-test-123')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_multiple_topics(self):

        # Create the broker message
        msg = {
            'cid': 'test-cid-456',
            'sub_key': 'sk-multi-456',
            'sec_name': 'multi_user',
            'topic_name_list': ['orders.new', 'invoices.paid', 'alerts.critical']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert all subscriptions were created
        for topic_name in ['orders.new', 'invoices.paid', 'alerts.critical']:
            self.assertIn(topic_name, self.backend.subs_by_topic)
            self.assertIn('multi_user', self.backend.subs_by_topic[topic_name])

            subscription = self.backend.subs_by_topic[topic_name]['multi_user']
            self.assertEqual(subscription.topic_name, topic_name)
            self.assertEqual(subscription.sec_name, 'multi_user')
            self.assertEqual(subscription.sub_key, 'sk-multi-456')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_creates_topics_if_missing(self):

        # Ensure topics don't exist initially
        self.assertEqual(len(self.backend.topics), 0)

        # Create the broker message
        msg = {
            'cid': 'test-cid-789',
            'sub_key': 'sk-new-topic-789',
            'sec_name': 'topic_creator',
            'topic_name_list': ['new.topic.one', 'new.topic.two']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert topics were created
        self.assertIn('new.topic.one', self.backend.topics)
        self.assertIn('new.topic.two', self.backend.topics)

        # Assert subscriptions were created
        self.assertIn('new.topic.one', self.backend.subs_by_topic)
        self.assertIn('new.topic.two', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_multiple_users_same_topic(self):

        # Create subscriptions for multiple users to the same topic
        msg1 = {
            'cid': 'test-cid-user1',
            'sub_key': 'sk-user1',
            'sec_name': 'user_one',
            'topic_name_list': ['shared.topic']
        }

        msg2 = {
            'cid': 'test-cid-user2',
            'sub_key': 'sk-user2',
            'sec_name': 'user_two',
            'topic_name_list': ['shared.topic']
        }

        # Call the method under test for both users
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg1)
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg2)

        # Assert both subscriptions exist
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        self.assertIn('user_one', self.backend.subs_by_topic['shared.topic'])
        self.assertIn('user_two', self.backend.subs_by_topic['shared.topic'])

        # Assert subscription details are correct
        sub1 = self.backend.subs_by_topic['shared.topic']['user_one']
        sub2 = self.backend.subs_by_topic['shared.topic']['user_two']

        self.assertEqual(sub1.sec_name, 'user_one')
        self.assertEqual(sub1.sub_key, 'sk-user1')
        self.assertEqual(sub2.sec_name, 'user_two')
        self.assertEqual(sub2.sub_key, 'sk-user2')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_overwrites_existing_subscription(self):

        # Create initial subscription
        msg1 = {
            'cid': 'test-cid-initial',
            'sub_key': 'sk-initial',
            'sec_name': 'test_user',
            'topic_name_list': ['test.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg1)

        # Create new subscription for same user and topic
        msg2 = {
            'cid': 'test-cid-overwrite',
            'sub_key': 'sk-new',
            'sec_name': 'test_user',
            'topic_name_list': ['test.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg2)

        # Assert the subscription was overwritten
        subscription = self.backend.subs_by_topic['test.topic']['test_user']
        self.assertEqual(subscription.sub_key, 'sk-new')

        # Assert there's still only one subscription for this user/topic
        self.assertEqual(len(self.backend.subs_by_topic['test.topic']), 1)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_empty_topic_list(self):

        # Create the broker message with empty topic list
        msg = {
            'cid': 'test-cid-empty',
            'sub_key': 'sk-empty',
            'sec_name': 'empty_user',
            'topic_name_list': []
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert no subscriptions were created
        self.assertEqual(len(self.backend.subs_by_topic), 0)
        self.assertEqual(len(self.backend.topics), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_preserves_existing_topics(self):

        # Create a topic manually first
        self.backend.create_topic('setup-cid', 'test', 'existing.topic')
        initial_topic_count = len(self.backend.topics)

        # Create subscription to existing topic
        msg = {
            'cid': 'test-cid-existing',
            'sub_key': 'sk-existing',
            'sec_name': 'existing_user',
            'topic_name_list': ['existing.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert topic count didn't change (no duplicate creation)
        self.assertEqual(len(self.backend.topics), initial_topic_count)

        # Assert subscription was still created
        self.assertIn('existing.topic', self.backend.subs_by_topic)
        self.assertIn('existing_user', self.backend.subs_by_topic['existing.topic'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
