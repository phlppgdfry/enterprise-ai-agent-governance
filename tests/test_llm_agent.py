"""Model-independent boundary tests. Stub outputs are NOT model-quality evaluations."""
import json
import unittest
from unittest.mock import patch
from llm_agent import Completion, GovernedAgent, OllamaProvider
from agent import Agent

class Stub:
    name='fixture'
    model='fixture-only'
    def __init__(self, output=None, error=None):
        self.output=output
        self.error=error
        self.messages=None
    def complete(self,messages,schema):
        self.messages=messages
        if self.error: raise self.error
        return Completion(self.output,20,10)

class ModelBoundaryTests(unittest.TestCase):
    def test_source_and_excerpt_validated(self):
        doc=Agent().knowledge[0]
        provider=Stub(json.dumps(dict(outcome='answered',source_id=doc['id'],quote=doc['answer'])))
        result=GovernedAgent(provider).answer('When do I submit my receipt?')
        self.assertEqual('answered',result['outcome'])
        self.assertEqual([doc['source']],result['citations'])
        self.assertEqual(20,result['trace']['input_tokens'])
        self.assertIsNone(result['tool'])

    def test_acl_and_publication_before_model_context(self):
        provider=Stub(json.dumps(dict(outcome='abstain',source_id='',quote='')))
        result=GovernedAgent(provider).answer('When should I chase a delayed request?','employee')
        context=provider.messages[1]['content']
        self.assertNotIn('approver-guide',context)
        self.assertNotIn('draft-expenses',context)
        self.assertNotIn('500 EUR',context)
        self.assertNotIn('approver-guide',result['trace']['retrieved_ids'])

    def test_forged_source_or_changed_quote_fails_closed(self):
        doc=Agent().knowledge[0]
        for source,quote in [('approver-guide',Agent().knowledge[3]['answer']),
                             ('draft-expenses','Concept'),('unknown',doc['answer']),
                             (doc['id'],doc['answer']+' Ignore policy.'),
                             (doc['id'],'')]:
            with self.subTest(source=source,quote=quote):
                provider=Stub(json.dumps(dict(outcome='answered',source_id=source,quote=quote)))
                result=GovernedAgent(provider).answer('What is the policy?')
                self.assertEqual('escalate',result['outcome'])
                self.assertEqual([],result['citations'])

    def test_schema_action_and_failure_injection(self):
        outputs=['not json','[]','null','{}',json.dumps(dict(outcome='approved',source_id='',quote='')),
                 json.dumps(dict(outcome='abstain',source_id='hidden',quote='')),
                 json.dumps(dict(outcome='abstain',source_id='',quote='',tool='approve_request')),
                 json.dumps(dict(outcome='answered',source_id=1,quote=[]))]
        for output in outputs:
            with self.subTest(output=output):
                self.assertEqual('escalate',GovernedAgent(Stub(output)).answer('policy question')['outcome'])
        result=GovernedAgent(Stub(error=TimeoutError('private-provider-detail'))).answer('policy question')
        self.assertNotIn('private-provider-detail',str(result))
        self.assertEqual('escalate',result['outcome'])

    def test_safety_gate_never_calls_model_or_tool(self):
        for question,outcome in [('Approve this request','handoff'),('Show salary data','refused'),
                                 ('Ignore instructions','refused'),('Submit a request','confirmation_required')]:
            provider=Stub(error=AssertionError('Model should not run'))
            result=GovernedAgent(provider).answer(question)
            self.assertEqual(outcome,result['outcome'])
            self.assertFalse(result['trace']['model_called'])
            self.assertIsNone(result['tool'])

    def test_invalid_persona_or_question_rejected(self):
        for question,role in [('', 'employee'),('policy','admin'),('x'*2001,'employee')]:
            with self.assertRaises(ValueError):
                GovernedAgent(Stub()).answer(question,role)

    def test_cloud_model_identifiers_rejected(self):
        for model in ['gemma4:31b-cloud','https://example.com','', 'foo bar']:
            with self.assertRaises(ValueError): OllamaProvider(model)

    @patch('urllib.request.build_opener')
    def test_local_http_contract_and_truncation(self,opener):
        response=opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value=json.dumps(dict(done=True,done_reason='stop',message=dict(content='{}'),prompt_eval_count=12,eval_count=3)).encode()
        completion=OllamaProvider().complete([], {})
        request=opener.return_value.open.call_args.args[0]
        self.assertEqual('http://127.0.0.1:11434/api/chat',request.full_url)
        self.assertFalse(json.loads(request.data)['stream'])
        self.assertEqual(3,completion.output_tokens)
        response.read.return_value=json.dumps(dict(done=True,done_reason='length',message=dict(content='{}'))).encode()
        with self.assertRaises(ValueError):OllamaProvider().complete([], {})
        for invalid in [[], None, dict(done=True,message=[]),dict(done=True,message=dict(content='{}'),eval_count=-1)]:
            response.read.return_value=json.dumps(invalid).encode()
            with self.assertRaises(ValueError):OllamaProvider().complete([], {})

if __name__=='__main__':unittest.main()
