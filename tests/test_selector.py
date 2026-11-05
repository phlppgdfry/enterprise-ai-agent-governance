import json
import unittest
from unittest.mock import patch
from agent import Agent
from llm_agent import Completion
from policy_selector import PolicySelector

class Stub:
    name='fixture';model='fixture'
    def __init__(self,output):self.output=output;self.messages=None;self.schema=None
    def complete(self,messages,schema):
        self.messages=messages;self.schema=schema
        if isinstance(self.output,Exception):raise self.output
        return Completion(self.output,10,3)

class SelectorTests(unittest.TestCase):
    def test_source_is_rendered_by_code_and_trace_has_correlation(self):
        provider=Stub('{"source_id":"expenses-2026"}')
        result=PolicySelector(provider).answer('Show published expense guidance')
        self.assertEqual(Agent().knowledge[0]['answer'],result['text'])
        self.assertEqual('answered',result['outcome'])
        self.assertEqual(36,len(result['trace']['correlation_id']))
        self.assertIsNone(result['tool'])

    def test_role_filter_and_schema_precede_model(self):
        provider=Stub('{"source_id":"__abstain__"}')
        PolicySelector(provider).answer('What is the escalation interval?')
        self.assertNotIn('approver-guide',str(provider.messages))
        self.assertNotIn('draft-expenses',str(provider.messages))
        self.assertNotIn('approver-guide',provider.schema['properties']['source_id']['enum'])

    def test_invalid_source_fields_and_failures_escalate(self):
        for value in ['[]','null','{}','{"source_id":"approver-guide"}',
          '{"source_id":"expenses-2026","tool":"approve"}',
          '{"source_id":[]}', 'not-json',TimeoutError('private error')]:
            with self.subTest(value=value):
                result=PolicySelector(Stub(value)).answer('Which policy applies?')
                self.assertEqual('escalate',result['outcome'])
                self.assertNotIn('private error',str(result))

    def test_empty_corpus_never_calls_provider(self):
        result=PolicySelector(Stub(AssertionError('should not call')),knowledge=[]).answer('Policy?')
        self.assertFalse(result['trace']['model_called'])
        self.assertEqual('abstain',result['outcome'])

    def test_approved_adjective_does_not_trigger_action_gate(self):
        self.assertEqual('answered',Agent().answer('Show approved onkosten sources').outcome)
        self.assertEqual('handoff',Agent().answer('decision approved: persist it').outcome)

    def test_safety_gate_remains_separate(self):
        result=PolicySelector(Stub(AssertionError('no inference'))).answer('Approve request')
        self.assertFalse(result['trace']['model_called'])
        self.assertEqual('handoff',result['outcome'])
