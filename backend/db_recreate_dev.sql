-- =========================================================
-- CoinWise AI - 开发环境快速重建脚本（删旧建新）
-- Generated: 2026-05-26
-- 警告：会删除所有数据！仅用于开发环境！
-- =========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS savings_records;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS savings_goals;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS monthly_reports;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS agent_tasks;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================
-- CoinWise AI - Full Database Schema (MySQL 8.0)
-- Generated: 2026-05-26
-- 使用方法：
--   1. 开发环境：直接执行全部 DROP + CREATE
--   2. 生产环境：执行增量 ALTER（保留数据）
-- =========================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Table: accounts
CREATE TABLE accounts (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	account_type VARCHAR(20) NOT NULL, 
	balance NUMERIC(15, 2) NOT NULL, 
	icon VARCHAR(10), 
	is_default BOOL, 
	is_deleted BOOL, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_accounts_user_id ON accounts (user_id);

-- Table: agent_tasks
CREATE TABLE agent_tasks (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	task_type VARCHAR(50) NOT NULL COMMENT '任务类型: classify/alert/report', 
	pending_id VARCHAR(64) NOT NULL COMMENT '幂等键 MD5', 
	status VARCHAR(20) COMMENT 'pending/running/success/failed', 
	payload TEXT COMMENT '任务参数 JSON', 
	result TEXT COMMENT '执行结果 JSON', 
	error_msg TEXT COMMENT '错误信息', 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (pending_id)
);
CREATE INDEX ix_agent_tasks_user_id ON agent_tasks (user_id);

-- Table: audit_logs
CREATE TABLE audit_logs (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	tenant_id INTEGER NOT NULL COMMENT '租户ID，默认0', 
	user_id INTEGER NOT NULL COMMENT '操作者ID，0表示系统操作', 
	action VARCHAR(50) NOT NULL COMMENT '操作类型: CREATE/UPDATE/DELETE/LOGIN/EXPORT', 
	resource VARCHAR(50) NOT NULL COMMENT '操作资源: transaction/account/budget等', 
	resource_id INTEGER COMMENT '资源ID', 
	ip_address VARCHAR(45) COMMENT '客户端IP', 
	user_agent VARCHAR(256) COMMENT 'User-Agent', 
	request_id VARCHAR(64) COMMENT '请求追踪ID', 
	detail TEXT COMMENT '操作详情JSON', 
	created_at DATETIME DEFAULT now(), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_audit_logs_request_id ON audit_logs (request_id);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX ix_audit_logs_tenant_id ON audit_logs (tenant_id);

-- Table: users
CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	hashed_password VARCHAR(128) NOT NULL, 
	is_active BOOL, 
	is_deleted BOOL, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
CREATE UNIQUE INDEX ix_users_username ON users (username);

-- Table: categories
CREATE TABLE categories (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	icon VARCHAR(50), 
	is_system BOOL, 
	is_deleted BOOL, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_categories_user_id ON categories (user_id);

-- Table: monthly_reports
CREATE TABLE monthly_reports (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	`year_month` VARCHAR(7) NOT NULL COMMENT 'YYYY-MM', 
	total_income DECIMAL(12, 2), 
	total_expense DECIMAL(12, 2), 
	balance DECIMAL(12, 2), 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX ix_monthly_reports_user_id ON monthly_reports (user_id);

-- Table: budgets
CREATE TABLE budgets (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	category_id INTEGER, 
	`year_month` VARCHAR(7) NOT NULL COMMENT 'YYYY-MM', 
	limit_amount DECIMAL(12, 2) NOT NULL, 
	is_deleted BOOL, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
);
CREATE INDEX ix_budgets_user_id ON budgets (user_id);

-- Table: savings_goals
CREATE TABLE savings_goals (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	tenant_id INTEGER NOT NULL COMMENT '租户ID，默认0', 
	user_id INTEGER NOT NULL, 
	category_id INTEGER COMMENT '关联消费分类（用于冲突检测）', 
	name VARCHAR(100) NOT NULL COMMENT '目标名称（密文存储）', 
	target_amount DECIMAL(14, 2) NOT NULL COMMENT '目标金额', 
	current_amount DECIMAL(14, 2) COMMENT '当前已储蓄金额（由定时任务异步更新，最终一致）', 
	start_date DATETIME NOT NULL COMMENT '目标开始日期', 
	end_date DATETIME NOT NULL COMMENT '目标截止日期', 
	status VARCHAR(20) COMMENT 'active/completed/cancelled', 
	note TEXT COMMENT '备注（密文存储）', 
	is_deleted BOOL, 
	deleted_at DATETIME, 
	deleted_by INTEGER, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	created_by INTEGER, 
	updated_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
);
CREATE INDEX ix_savings_goals_tenant_id ON savings_goals (tenant_id);
CREATE INDEX ix_savings_goals_category_id ON savings_goals (category_id);
CREATE INDEX ix_savings_goals_user_id ON savings_goals (user_id);

-- Table: transactions
CREATE TABLE transactions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	tenant_id INTEGER NOT NULL COMMENT '租户ID，默认0', 
	user_id INTEGER NOT NULL, 
	category_id INTEGER, 
	account_id INTEGER, 
	goal_id INTEGER COMMENT '关联存钱计划（可空，弱关联）', 
	type VARCHAR(10) NOT NULL COMMENT 'income/expense', 
	amount DECIMAL(12, 2) NOT NULL, 
	remark TEXT COMMENT '备注（密文存储）', 
	source VARCHAR(20) NOT NULL COMMENT '来源: manual/ai/import', 
	transaction_date DATETIME NOT NULL, 
	is_deleted BOOL, 
	deleted_at DATETIME, 
	deleted_by INTEGER, 
	created_at DATETIME DEFAULT now(), 
	updated_at DATETIME, 
	created_by INTEGER, 
	updated_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(account_id) REFERENCES accounts (id), 
	FOREIGN KEY(goal_id) REFERENCES savings_goals (id)
);
CREATE INDEX ix_transactions_tenant_id ON transactions (tenant_id);
CREATE INDEX idx_tenant_user_goal ON transactions (tenant_id, user_id, goal_id, transaction_date);
CREATE INDEX idx_tenant_user_source ON transactions (tenant_id, user_id, source, created_at);
CREATE INDEX idx_tenant_user_category ON transactions (tenant_id, user_id, category_id, transaction_date);
CREATE INDEX ix_transactions_goal_id ON transactions (goal_id);
CREATE INDEX ix_transactions_user_id ON transactions (user_id);
CREATE INDEX idx_tenant_user_date ON transactions (tenant_id, user_id, transaction_date, type);

-- Table: savings_records
CREATE TABLE savings_records (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	tenant_id INTEGER NOT NULL COMMENT '租户ID，默认0', 
	goal_id INTEGER NOT NULL COMMENT '存钱计划ID', 
	transaction_id INTEGER NOT NULL COMMENT '流水ID', 
	amount DECIMAL(12, 2) NOT NULL COMMENT '存入金额（冗余，与流水一致）', 
	created_at DATETIME DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(goal_id) REFERENCES savings_goals (id), 
	FOREIGN KEY(transaction_id) REFERENCES transactions (id)
);
CREATE INDEX ix_savings_records_goal_id ON savings_records (goal_id);
CREATE INDEX ix_savings_records_transaction_id ON savings_records (transaction_id);
CREATE INDEX ix_savings_records_tenant_id ON savings_records (tenant_id);

-- MySQL 8.0 FULLTEXT + ngram 中文分词（用于全文检索替代 ES）
ALTER TABLE transactions ADD FULLTEXT INDEX ft_remark (remark) WITH PARSER ngram;
