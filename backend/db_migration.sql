-- =========================================================
-- CoinWise AI - 增量 Migration SQL（生产环境，保留数据）
-- Generated: 2026-05-26
-- 前置条件：MySQL 8.0+（支持 ngram 分词器）
-- =========================================================

SET NAMES utf8mb4;

-- 1. transactions 表新增字段
ALTER TABLE transactions ADD COLUMN tenant_id INT NOT NULL DEFAULT 0 COMMENT "租户ID，默认0";
ALTER TABLE transactions ADD COLUMN goal_id INT DEFAULT NULL COMMENT "关联存钱计划（可空，弱关联）";
ALTER TABLE transactions ADD COLUMN source VARCHAR(20) NOT NULL DEFAULT "manual" COMMENT "来源: manual/ai/import";
ALTER TABLE transactions ADD COLUMN deleted_at DATETIME DEFAULT NULL;
ALTER TABLE transactions ADD COLUMN deleted_by INT DEFAULT NULL;
ALTER TABLE transactions ADD COLUMN created_by INT DEFAULT NULL;
ALTER TABLE transactions ADD COLUMN updated_by INT DEFAULT NULL;
ALTER TABLE transactions CHANGE COLUMN note remark TEXT COMMENT "备注（密文存储）";
CREATE INDEX idx_tenant_user_date ON transactions (tenant_id, user_id, transaction_date, type);
CREATE INDEX idx_tenant_user_category ON transactions (tenant_id, user_id, category_id, transaction_date);
CREATE INDEX idx_tenant_user_goal ON transactions (tenant_id, user_id, goal_id, transaction_date);
CREATE INDEX idx_tenant_user_source ON transactions (tenant_id, user_id, source, created_at);
CREATE INDEX ix_transactions_tenant_id ON transactions (tenant_id);
CREATE INDEX ix_transactions_goal_id ON transactions (goal_id);

-- 2. savings_goals 表新增字段
ALTER TABLE savings_goals ADD COLUMN tenant_id INT NOT NULL DEFAULT 0 COMMENT "租户ID，默认0";
ALTER TABLE savings_goals ADD COLUMN category_id INT DEFAULT NULL COMMENT "关联消费分类（用于冲突检测）";
ALTER TABLE savings_goals ADD COLUMN deleted_at DATETIME DEFAULT NULL;
ALTER TABLE savings_goals ADD COLUMN deleted_by INT DEFAULT NULL;
ALTER TABLE savings_goals ADD COLUMN created_by INT DEFAULT NULL;
ALTER TABLE savings_goals ADD COLUMN updated_by INT DEFAULT NULL;
CREATE INDEX ix_savings_goals_tenant_id ON savings_goals (tenant_id);
CREATE INDEX ix_savings_goals_category_id ON savings_goals (category_id);

-- 3. audit_logs 表新增字段
ALTER TABLE audit_logs ADD COLUMN tenant_id INT NOT NULL DEFAULT 0 COMMENT "租户ID，默认0";
ALTER TABLE audit_logs ADD COLUMN request_id VARCHAR(64) DEFAULT NULL COMMENT "请求追踪ID";
CREATE INDEX ix_audit_logs_request_id ON audit_logs (request_id);
CREATE INDEX ix_audit_logs_tenant_id ON audit_logs (tenant_id);

-- 4. 新表 savings_records
CREATE TABLE IF NOT EXISTS savings_records (
    id INT NOT NULL AUTO_INCREMENT,
    tenant_id INT NOT NULL DEFAULT 0 COMMENT "租户ID，默认0",
    goal_id INT NOT NULL COMMENT "存钱计划ID",
    transaction_id INT NOT NULL COMMENT "流水ID",
    amount DECIMAL(12, 2) NOT NULL COMMENT "存入金额（冗余，与流水一致）",
    created_at DATETIME DEFAULT NOW(),
    PRIMARY KEY (id),
    INDEX ix_savings_records_goal_id (goal_id),
    INDEX ix_savings_records_transaction_id (transaction_id),
    INDEX ix_savings_records_tenant_id (tenant_id),
    FOREIGN KEY (goal_id) REFERENCES savings_goals (id),
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 全文索引（MySQL 8.0 ngram 中文分词）
ALTER TABLE transactions ADD FULLTEXT INDEX ft_remark (remark) WITH PARSER ngram;

-- =========================================================
-- 数据迁移说明：
--   - transactions.source 默认填充为 "manual"（历史数据）
--   - transactions.note -> remark 字段已重命名
--   - savings_goals.current_amount 需要运行一次 reconcile_all_active_goals
--     Celery 任务来重新计算
--   - 加密字段（remark, name, note）的历史明文数据无需处理，
--     crypto.decrypt 会兼容处理（解密失败时原样返回）
-- =========================================================
