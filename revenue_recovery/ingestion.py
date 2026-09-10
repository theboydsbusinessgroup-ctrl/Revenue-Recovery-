from __future__ import annotations
import csv
import io
from dataclasses import dataclass, asdict
from typing import Iterable
from .models import QuoteRecord

TRUE_VALUES={"1","true","yes","y"}
FALSE_VALUES={"0","false","no","n",""}

ALIASES={
 "quote_id":["quote_id","quote","estimate_id","proposal_id","id"],
 "customer_id":["customer_id","client_id","contact_id","customer","client"],
 "quoted_value":["quoted_value","amount","quote_value","estimate_amount","value"],
 "created_days_ago":["created_days_ago","age_days","days_since_created"],
 "last_contact_days_ago":["last_contact_days_ago","days_since_contact","days_since_last_contact"],
 "status":["status","quote_status","stage"],
 "contactable":["contactable","can_contact","contact_allowed"],
 "opted_out":["opted_out","do_not_contact","dnc"],
 "prior_customer":["prior_customer","existing_customer","repeat_customer"],
 "engagement_count":["engagement_count","touches","activity_count"],
 "source_ref":["source_ref","source","record_url","crm_ref"],
}

@dataclass
class RejectedRow:
 row_number:int
 reasons:list[str]
 raw:dict[str,str]

@dataclass
class IngestionResult:
 records:list[QuoteRecord]
 rejected:list[RejectedRow]
 total_rows:int

 def summary(self)->dict:
  return {"total_rows":self.total_rows,"accepted":len(self.records),"rejected":len(self.rejected),"rejections":[asdict(r) for r in self.rejected]}


def _lookup(row:dict[str,str], field:str)->str|None:
 normalized={str(k).strip().lower():v for k,v in row.items() if k is not None}
 for alias in ALIASES[field]:
  if alias in normalized:
   return normalized[alias]
 return None


def _bool(value:str|None, default:bool)->bool:
 if value is None: return default
 v=str(value).strip().lower()
 if v in TRUE_VALUES:return True
 if v in FALSE_VALUES:return False
 raise ValueError("invalid_boolean")


def _int(value:str|None, default:int=0)->int:
 if value is None or str(value).strip()=="": return default
 x=int(float(str(value).strip()))
 if x<0: raise ValueError("negative_integer")
 return x


def _money(value:str|None)->float:
 if value is None: raise ValueError("missing_value")
 cleaned=str(value).strip().replace("$","").replace(",","")
 x=float(cleaned)
 if x<0: raise ValueError("negative_value")
 return round(x,2)


def normalize_row(row:dict[str,str], row_number:int)->QuoteRecord|RejectedRow:
 reasons=[]
 quote_id=(_lookup(row,"quote_id") or "").strip()
 customer_id=(_lookup(row,"customer_id") or "").strip()
 status=(_lookup(row,"status") or "").strip()
 if not quote_id: reasons.append("missing_quote_id")
 if not customer_id: reasons.append("missing_customer_id")
 if not status: reasons.append("missing_status")
 try: value=_money(_lookup(row,"quoted_value"))
 except (ValueError,TypeError): value=0.0; reasons.append("invalid_quoted_value")
 try: created=_int(_lookup(row,"created_days_ago"))
 except (ValueError,TypeError): created=0; reasons.append("invalid_created_days_ago")
 try: last=_int(_lookup(row,"last_contact_days_ago"))
 except (ValueError,TypeError): last=0; reasons.append("invalid_last_contact_days_ago")
 try: contactable=_bool(_lookup(row,"contactable"),True)
 except ValueError: contactable=False; reasons.append("invalid_contactable")
 try: opted_out=_bool(_lookup(row,"opted_out"),False)
 except ValueError: opted_out=True; reasons.append("invalid_opted_out")
 try: prior=_bool(_lookup(row,"prior_customer"),False)
 except ValueError: prior=False; reasons.append("invalid_prior_customer")
 try: engagement=_int(_lookup(row,"engagement_count"),0)
 except (ValueError,TypeError): engagement=0; reasons.append("invalid_engagement_count")
 if reasons:
  return RejectedRow(row_number=row_number,reasons=sorted(set(reasons)),raw={str(k):str(v or "") for k,v in row.items()})
 return QuoteRecord(quote_id,customer_id,value,created,last,status,contactable,opted_out,prior,engagement,(_lookup(row,"source_ref") or f"csv:row:{row_number}").strip())


def ingest_csv_text(text:str)->IngestionResult:
 reader=csv.DictReader(io.StringIO(text))
 records=[]; rejected=[]; total=0
 for idx,row in enumerate(reader,start=2):
  total+=1
  item=normalize_row(row,idx)
  (rejected if isinstance(item,RejectedRow) else records).append(item)
 return IngestionResult(records,rejected,total)
