#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from revenue_recovery.engine import analyze_csv

sample='''quote_id,customer_id,quoted_value,created_days_ago,last_contact_days_ago,status,contactable,opted_out,prior_customer,engagement_count,source_ref
Q-2001,C-10,2400,28,12,quoted,true,false,false,2,fixture:Q-2001
Q-2002,C-11,1250,16,9,estimate_sent,true,false,true,4,fixture:Q-2002
Q-2003,C-12,bad,9,8,quoted,true,false,false,1,fixture:Q-2003
'''
print(json.dumps(analyze_csv(sample),indent=2))
