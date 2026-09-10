import tempfile,unittest
from pathlib import Path
from revenue_recovery.actions import ContactHistory,OutreachItem
from revenue_recovery.persistence import RecoveryStore
from revenue_recovery.providers import CallbackDraftProvider
from revenue_recovery.drafting import create_recovery_draft

class PersistenceDraftTests(unittest.TestCase):
 def store(self):
  td=tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup); return RecoveryStore(Path(td.name)/'state.db')

 def test_contact_history_persists(self):
  s=self.store(); s.save_history(ContactHistory('Q1',2,5,True)); h=s.get_history('Q1')
  self.assertEqual(h.attempts,2); self.assertTrue(h.negative_reply)

 def test_draft_created_once(self):
  s=self.store(); calls=[]
  p=CallbackDraftProvider(lambda payload: calls.append(payload) or {'draft_id':'r-test'})
  item=OutreachItem('O1','Q1','C1','Subject','Body',True,False,None)
  first=create_recovery_draft(item,'self@example.com',p,s); second=create_recovery_draft(item,'self@example.com',p,s)
  self.assertTrue(first['created']); self.assertEqual(second['reason'],'duplicate_draft'); self.assertEqual(len(calls),1)

 def test_suppressed_item_never_calls_provider(self):
  s=self.store(); calls=[]; p=CallbackDraftProvider(lambda payload: calls.append(payload) or {'draft_id':'bad'})
  item=OutreachItem('O2','Q2','C2','Subject','Body',True,True,'customer_opted_out')
  result=create_recovery_draft(item,'self@example.com',p,s)
  self.assertFalse(result['created']); self.assertEqual(calls,[])

if __name__=='__main__':unittest.main()
