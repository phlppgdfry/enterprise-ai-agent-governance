import json
import unittest
from unittest.mock import patch
from agent import NoRedirect,submit_request

class ToolFailures(unittest.TestCase):
    @patch('agent.open_local')
    def test_invalid_arguments_never_reach_network(self,network):
        for args in [('x','materials',float('nan')),('x','access',1),('x','expense',True),('x','materials',1.001),('x\n','materials',1)]:
            with self.assertRaises(ValueError):submit_request(*args,confirmed=True,token='demo-alice',idempotency_key='safe')
        network.assert_not_called()

    @patch('agent.open_local')
    def test_unexpected_api_response_is_not_success(self,network):
        for raw in [b'[]',b'not-json',b'{"status":"approved"}',b'x'*65537]:
            network.return_value.__enter__.return_value.read.return_value=raw
            with self.assertRaises(ValueError):submit_request('x','materials',1,confirmed=True,token='demo-alice',idempotency_key='safe')

    def test_redirect_is_denied(self):
        with self.assertRaises(ValueError):NoRedirect().redirect_request(None,None,302,'',{},'http://example.invalid')

    @patch('agent.open_local',side_effect=TimeoutError('timeout'))
    def test_tool_timeout_has_no_automatic_retry(self,network):
        with self.assertRaises(TimeoutError):submit_request('x','materials',1,confirmed=True,token='demo-alice',idempotency_key='stable')
        self.assertEqual(1,network.call_count)
