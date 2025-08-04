# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import warnings
from base64 import b64encode
from json import dumps
from unittest import main, TestCase

# Zato
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.common.pubsub.server.rest_base import BadRequestException, UnauthorizedException
from zato.common.pubsub.models import APIResponse
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'
        self.test_topic = 'test.topic'

        # Add test user to server
        self.rest_server.users[self.test_username] = self.test_password

    def _create_basic_auth_header(self, username, password):
        """Helper method to create Basic Auth header"""
        credentials = f'{username}:{password}'
        encoded_credentials = b64encode(credentials.encode('utf-8')).decode('ascii')
        return f'Basic {encoded_credentials}'

    def _create_environ(self, auth_header=None, path_info='/test', method='POST', data=None):
        """Helper method to create WSGI environ dict"""
        environ = {
            'PATH_INFO': path_info,
            'REQUEST_METHOD': method,
            'wsgi.input': None
        }
        if auth_header:
            environ['HTTP_AUTHORIZATION'] = auth_header
        if data:
            json_data = dumps(data).encode('utf-8')
            environ['wsgi.input'] = type('MockInput', (), {
                'read': lambda self, size=-1: json_data,
                'readline': lambda self: b'',
                'readlines': lambda self: []
            })()
            environ['CONTENT_LENGTH'] = str(len(json_data))
        return environ

    def _create_start_response(self):
        """Helper method to create start_response callable"""
        def start_response(status, headers):
            pass
        return start_response

# ################################################################################################################################

    def test_on_publish_with_valid_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create valid message data
        message_data = {
            'data': 'Hello, World!',
            'priority': 5,
            'expiration': 3600,
            'correl_id': 'test-correlation-123',
            'ext_client_id': 'test-client',
            'in_reply_to': 'test-reply-to'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_minimal_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create minimal message data (only required 'data' field)
        message_data = {
            'data': 'Minimal message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_complex_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create complex message data
        complex_data = {
            'user_id': 12345,
            'action': 'user_login',
            'metadata': {
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0',
                'timestamp': '2025-01-01T12:00:00Z'
            },
            'items': [
                {'id': 1, 'name': 'Item 1'},
                {'id': 2, 'name': 'Item 2'}
            ]
        }

        message_data = {
            'data': complex_data,
            'priority': 8,
            'expiration': 7200
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_string_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with string data
        message_data = {
            'data': 'Simple string message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_numeric_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with numeric data
        message_data = {
            'data': 42
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_boolean_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with boolean data
        message_data = {
            'data': True
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_null_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with null data
        message_data = {
            'data': None
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID and message
        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertEqual(cm.exception.message, 'Message data missing')

# ################################################################################################################################

    def test_on_publish_without_data_field(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message without 'data' field
        message_data = {
            'priority': 5,
            'expiration': 3600
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID and message
        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertEqual(cm.exception.message, 'Message data missing')

# ################################################################################################################################

    def test_on_publish_with_empty_json(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create empty JSON
        message_data = {}

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID and message
        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertEqual(cm.exception.message, 'Message data missing')

# ################################################################################################################################

    def test_on_publish_with_no_json_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create environ without JSON data
        environ = self._create_environ(auth_header)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID and message
        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertEqual(cm.exception.message, 'Input data missing')

# ################################################################################################################################

    def test_on_publish_without_authentication(self):

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        # Create environ without auth header
        environ = self._create_environ(data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_invalid_credentials(self):

        # Create invalid auth header
        auth_header = self._create_basic_auth_header('invalid_user', 'invalid_password')

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect exception
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert exception contains correct CID
        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_unicode_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with unicode data
        message_data = {
            'data': 'Unicode message: ñáéíóú 中文 🚀'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_large_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with large data
        large_string = 'x' * 10000  # 10KB string
        message_data = {
            'data': large_string
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_custom_priority(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with custom priority
        message_data = {
            'data': 'High priority message',
            'priority': 9
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_custom_expiration(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with custom expiration
        message_data = {
            'data': 'Message with custom expiration',
            'expiration': 1800  # 30 minutes
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_correlation_id(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with correlation ID
        message_data = {
            'data': 'Message with correlation ID',
            'correl_id': 'custom-correlation-456'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_ext_client_id(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with external client ID
        message_data = {
            'data': 'Message with external client ID',
            'ext_client_id': 'external-client-789'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_in_reply_to(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with in_reply_to
        message_data = {
            'data': 'Reply message',
            'in_reply_to': 'original-message-id-123'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_all_optional_fields(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with all optional fields
        message_data = {
            'data': 'Complete message',
            'priority': 7,
            'expiration': 2400,
            'correl_id': 'full-correlation-999',
            'ext_client_id': 'full-client-888',
            'in_reply_to': 'original-msg-777'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_multiple_messages_same_topic(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        start_response = self._create_start_response()

        # Publish multiple messages to same topic
        for i in range(3):
            message_data = {
                'data': f'Message {i + 1}',
                'correl_id': f'correlation-{i + 1}'
            }

            environ = self._create_environ(auth_header, data=message_data)

            # Call the method under test
            result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

            # Assert each response is correct
            self.assertIsInstance(result, APIResponse)
            self.assertTrue(result.is_ok)
            self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_different_topics(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)
        start_response = self._create_start_response()

        # Test different topic names
        topics = ['topic.one', 'topic.two', 'topic.three']

        for topic in topics:
            message_data = {
                'data': f'Message for {topic}'
            }

            environ = self._create_environ(auth_header, data=message_data)

            # Call the method under test
            result = self.rest_server.on_publish(self.test_cid, environ, start_response, topic)

            # Assert each response is correct
            self.assertIsInstance(result, APIResponse)
            self.assertTrue(result.is_ok)
            self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_zero_priority(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with zero priority
        message_data = {
            'data': 'Low priority message',
            'priority': 0
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_zero_expiration(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with zero expiration
        message_data = {
            'data': 'Message with zero expiration',
            'expiration': 0
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_empty_string_fields(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with empty string fields
        message_data = {
            'data': 'Message with empty strings',
            'correl_id': '',
            'ext_client_id': '',
            'in_reply_to': ''
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
