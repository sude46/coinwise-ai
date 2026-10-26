"""单元测试：CSV/OFX 导入导出服务"""
import pytest
from services.import_export import parse_csv, parse_ofx, export_csv
from models.transaction import Transaction


CSV_SAMPLE = """date,amount,remark
2026-06-01,-50.00,午餐
2026-06-02,2000.00,工资
2026-06-03,-15.50,咖啡
"""

OFX_SAMPLE = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<BANKTRANLIST>
<STMTTRN>
<TRNTYPE>DEBIT</TRNTYPE>
<DTPOSTED>20260601</DTPOSTED>
<TRNAMT>-50.00</TRNAMT>
<MEMO>午餐</MEMO>
</STMTTRN>
<STMTTRN>
<TRNTYPE>CREDIT</TRNTYPE>
<DTPOSTED>20260602</DTPOSTED>
<TRNAMT>2000.00</TRNAMT>
<MEMO>工资</MEMO>
</STMTTRN>
</BANKTRANLIST>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""


class TestParseCSV:
    def test_parse_expense(self):
        txs = parse_csv(CSV_SAMPLE, user_id=1, account_id=2)
        assert len(txs) == 3
        assert txs[0].type == "expense"
        assert float(txs[0].amount) == 50.0
        assert txs[0].remark == "午餐"
        assert txs[0].source == "import"
        assert txs[0].user_id == 1
        assert txs[0].account_id == 2

    def test_parse_income(self):
        txs = parse_csv(CSV_SAMPLE, user_id=1, account_id=1)
        income_tx = [t for t in txs if t.type == "income"]
        assert len(income_tx) == 1
        assert float(income_tx[0].amount) == 2000.0
        assert income_tx[0].remark == "工资"

    def test_empty_csv(self):
        txs = parse_csv("date,amount\n", user_id=1, account_id=1)
        assert len(txs) == 0


class TestParseOFX:
    def test_parse_ofx_transactions(self):
        txs = parse_ofx(OFX_SAMPLE, user_id=1, account_id=1)
        assert len(txs) == 2
        assert txs[0].type == "expense"
        assert float(txs[0].amount) == 50.0
        assert txs[1].type == "income"
        assert float(txs[1].amount) == 2000.0

    def test_invalid_ofx(self):
        txs = parse_ofx("not ofx content", user_id=1, account_id=1)
        assert len(txs) == 0


class TestExportCSV:
    def test_export_format(self):
        from datetime import datetime
        txs = [
            Transaction(type="expense", amount=50, remark="test",
                        transaction_date=datetime(2026, 6, 1), source="manual",
                        user_id=1, tenant_id=0),
        ]
        csv_out = export_csv(txs)
        assert "date,type,amount" in csv_out
        assert "2026-06-01" in csv_out
        assert "expense" in csv_out
        assert "50.0" in csv_out

    def test_export_empty(self):
        assert export_csv([]) == "date,type,amount,category_id,remark,source\n"
