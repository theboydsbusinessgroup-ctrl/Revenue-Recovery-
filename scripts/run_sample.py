#!/usr/bin/env python3
from revenue_recovery.engine import analyze
from revenue_recovery.models import QuoteRecord
import json

records = [
    QuoteRecord("Q-1001","C-1",1800,21,14,"quoted",True,False,False,2,"fixture:Q-1001"),
    QuoteRecord("Q-1002","C-2",950,12,9,"estimate_sent",True,False,True,4,"fixture:Q-1002"),
    QuoteRecord("Q-1003","C-3",2200,16,10,"quoted",True,True,False,3,"fixture:Q-1003"),
]
print(json.dumps(analyze(records), indent=2))
