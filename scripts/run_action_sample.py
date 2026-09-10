#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from revenue_recovery.engine import analyze_with_actions
from revenue_recovery.models import QuoteRecord
from revenue_recovery.actions import ContactHistory

records=[QuoteRecord('Q-3001','C-30',1800,30,14,'quoted',True,False,False,2,'fixture:Q-3001')]
history=[ContactHistory('Q-3001',attempts=1,last_contact_days_ago=8)]
print(json.dumps(analyze_with_actions(records,history),indent=2))
