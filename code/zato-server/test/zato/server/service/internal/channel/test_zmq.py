# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import Bunch

# Zato
from zato.common import zato_namespace
from zato.common.odb.model import ChannelZMQ, Service
from zato.common.test import rand_bool, rand_int, rand_string, ServiceTestCase
from zato.server.service.internal.channel.zmq import Create, Edit, Delete, GetList

################################################################################

class GetListTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = GetList
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'cluster_id': rand_int()}
    
    def get_response_data(self):
        return Bunch(
            {'id':rand_int(), 'name':rand_string(), 'is_active':rand_bool(), 'address':rand_string(), 
             'socket_type':rand_string(), 'sub_key':rand_string(),
             'service_name':rand_string(), 'data_format':rand_string()}
        )
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_zmq_get_list_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_zmq_get_list_response')
        self.assertEquals(self.sio.input_required, ('cluster_id',))
        self.assertEquals(self.sio.output_required, ('id', 'name', 'is_active', 'address', 'socket_type', 'sub_key', 'service_name', 'data_format'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.channel.zmq.get-list')
        
##############################################################################

class CreateTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Create
        self.sio = self.service_class.SimpleIO      
    
    def get_request_data(self):
        return {'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'address':rand_string(), 
             'socket_type':rand_string(),'service':rand_string(),
             'sub_key':rand_string(),'data_format':rand_string()}
    
    def get_response_data(self):
        return Bunch({'id':self.id, 'name':self.name})
    
    def test_sio(self):
        
        self.assertEquals(self.sio.request_elem, 'zato_channel_zmq_create_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_zmq_create_response')
        self.assertEquals(self.sio.input_required, ('cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service'))
        self.assertEquals(self.sio.input_optional, ('sub_key', 'data_format',))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
        def test_impl(self):
            self.assertEquals(self.service_class.get_name(), 'zato.channel.zmq.create')
       
###############################################################################
            
class EditTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Edit
        self.sio = self.service_class.SimpleIO
    
    def get_request_data(self):
        return {'id':rand_int(), 'cluster_id':rand_int(), 'name':self.name, 'is_active':rand_bool(), 'address':rand_string(), 
             'socket_type':rand_string(),'service':rand_string(), 'sub_key':rand_string(),'data_format':rand_string()}
    
    def get_response_data(self):
        return Bunch({'id':rand_int(), 'name':self.name})
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_zmq_edit_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_zmq_edit_response')
        self.assertEquals(self.sio.input_required, ('id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type', 'service'))
        self.assertEquals(self.sio.input_optional, ('sub_key', 'data_format',))
        self.assertEquals(self.sio.output_required, ('id', 'name'))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.channel.zmq.edit')

##############################################################################

class DeleteTestCase(ServiceTestCase):
    
    def setUp(self):
        self.service_class = Delete
        self.sio = self.service_class.SimpleIO
        
    def get_request_data(self):
        return {'id': self.id}
    
    def get_response_data(self):
        return Bunch()
    
    def test_sio(self):
        self.assertEquals(self.sio.request_elem, 'zato_channel_zmq_delete_request')
        self.assertEquals(self.sio.response_elem, 'zato_channel_zmq_delete_response')
        self.assertEquals(self.sio.input_required, ('id',))
        self.assertEquals(self.sio.namespace, zato_namespace)
        self.assertRaises(AttributeError, getattr, self.sio, 'input_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_required')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_optional')
        self.assertRaises(AttributeError, getattr, self.sio, 'output_repeated')
        
    def test_impl(self):
        self.assertEquals(self.service_class.get_name(), 'zato.channel.zmq.delete')
