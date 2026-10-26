import csv
import io
import re
from datetime import datetime
from decimal import Decimal
from typing import List
from xml.etree import ElementTree

from models.transaction import Transaction


class ImportResult:
    def __init__(self):
        self.imported: int = 0
        self.skipped: int = 0
        self.errors: List[str] = []


def parse_csv(content: str, user_id: int, account_id: int) -> List[Transaction]:
    reader = csv.DictReader(io.StringIO(content))
    transactions = []
    for row in reader:
        try:
            amount = Decimal(str(row.get("amount", "0")).strip())
            t_type = "expense" if amount < 0 else "income"
            tx = Transaction(
                user_id=user_id,
                account_id=account_id,
                type=t_type,
                amount=abs(amount),
                remark=row.get("remark", row.get("description", row.get("memo", ""))).strip(),
                source="import",
                transaction_date=datetime.strptime(
                    row.get("date", row.get("transaction_date", "")).strip()[:10],
                    "%Y-%m-%d",
                ),
                tenant_id=0,
                created_by=user_id,
            )
            transactions.append(tx)
        except (ValueError, KeyError):
            continue
    return transactions


def parse_ofx(content: str, user_id: int, account_id: int) -> List[Transaction]:
    transactions = []
    ofx_match = re.search(r"<OFX>(.*?)</OFX>", content, re.DOTALL)
    if not ofx_match:
        return transactions
    try:
        root = ElementTree.fromstring(ofx_match.group(0))
        stmttrn = root.findall(".//STMTTRN")
        for stmt in stmttrn:
            try:
                trntype = stmt.findtext("TRNTYPE", "")
                amount = Decimal(stmt.findtext("TRNAMT", "0"))
                if trntype.upper() in ("DEBIT", "CHECK", "PAYMENT", "FEE", "ATM"):
                    t_type = "expense"
                    amount = abs(amount)
                else:
                    t_type = "income"
                    amount = abs(amount)
                date_str = stmt.findtext("DTPOSTED", "")[:8]
                tx_date = datetime.strptime(date_str, "%Y%m%d") if date_str else datetime.now()
                tx = Transaction(
                    user_id=user_id,
                    account_id=account_id,
                    type=t_type,
                    amount=amount,
                    remark=stmt.findtext("MEMO", "").strip(),
                    source="import",
                    transaction_date=tx_date,
                    tenant_id=0,
                    created_by=user_id,
                )
                transactions.append(tx)
            except (ValueError, TypeError):
                continue
    except ElementTree.ParseError:
        pass
    return transactions


def export_csv(transactions: List[Transaction]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "type", "amount", "category_id", "remark", "source"])
    for tx in transactions:
        writer.writerow([
            tx.transaction_date.strftime("%Y-%m-%d"),
            tx.type,
            float(tx.amount),
            tx.category_id or "",
            tx.remark or "",
            tx.source,
        ])
    return output.getvalue()
