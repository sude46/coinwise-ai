#!/bin/bash
set -e

# 后台启动 MySQL 标准入口
docker-entrypoint.sh mysqld &

# 等待本地 MySQL 就绪
until mysqladmin ping -h localhost --silent; do
  sleep 1
done

# 等待主库就绪
until mysql -h mysql-master -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; do
  echo "Waiting for mysql-master..."
  sleep 2
done

# 获取主库状态
MASTER_STATUS=$(mysql -h mysql-master -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW MASTER STATUS\G")
LOG_FILE=$(echo "$MASTER_STATUS" | grep "File:" | awk '{print $2}')
LOG_POS=$(echo "$MASTER_STATUS" | grep "Position:" | awk '{print $2}')

echo "Master status: File=$LOG_FILE, Position=$LOG_POS"

# 配置并启动复制
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "
CHANGE MASTER TO
  MASTER_HOST='mysql-master',
  MASTER_USER='replica',
  MASTER_PASSWORD='replica_pass',
  MASTER_LOG_FILE='$LOG_FILE',
  MASTER_LOG_POS=$LOG_POS;
START SLAVE;
"

# 前台保持
wait
