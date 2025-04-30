USE GAODA;

-- 1. 当前订单表（存储当前有效的订单信息）
CREATE TABLE IF NOT EXISTS current_orders (
    order_id VARCHAR(50) PRIMARY KEY COMMENT '订单编号，主键',
    customer_id VARCHAR(50) NOT NULL COMMENT '客户编号',
    order_date DATETIME NOT NULL COMMENT '订单创建日期',
    order_status VARCHAR(20) NOT NULL COMMENT '订单当前状态：PENDING-待处理, PROCESSING-处理中, COMPLETED-已完成',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    payment_status VARCHAR(20) NOT NULL COMMENT '支付状态：UNPAID-未支付, PAID-已支付',
    shipping_address TEXT COMMENT '收货地址',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '创建人',
    updated_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后修改时间',
    remark TEXT COMMENT '备注信息',
    source_system VARCHAR(50) DEFAULT 'ORDER_SYSTEM' COMMENT '来源系统',
    data_status VARCHAR(20) DEFAULT 'VALID' COMMENT '数据状态：VALID-有效, INVALID-无效',
    sync_status VARCHAR(20) DEFAULT 'SYNCED' COMMENT '同步状态：SYNCED-已同步, UNSYNCED-未同步',
    batch_id VARCHAR(50) COMMENT '批次号',
    metadata JSON COMMENT '元数据信息'
) COMMENT='当前订单表，存储当前有效的订单信息，包含订单的基本信息，如订单状态、支付状态等';

-- 2. 历史订单表（存储已完成的订单历史记录）
CREATE TABLE IF NOT EXISTS historical_orders (
    order_id VARCHAR(50) PRIMARY KEY COMMENT '订单编号，主键',
    customer_id VARCHAR(50) NOT NULL COMMENT '客户编号',
    order_date DATETIME NOT NULL COMMENT '订单创建日期',
    completion_date DATETIME NOT NULL COMMENT '订单完成日期',
    final_status VARCHAR(20) NOT NULL COMMENT '订单最终状态：COMPLETED-已完成, CANCELLED-已取消',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    payment_method VARCHAR(20) COMMENT '支付方式：ALIPAY-支付宝, WECHAT-微信, BANK-银行转账',
    shipping_address TEXT COMMENT '收货地址',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '创建人',
    updated_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后修改时间',
    remark TEXT COMMENT '备注信息',
    source_system VARCHAR(50) DEFAULT 'ORDER_SYSTEM' COMMENT '来源系统',
    data_status VARCHAR(20) DEFAULT 'VALID' COMMENT '数据状态：VALID-有效, INVALID-无效',
    sync_status VARCHAR(20) DEFAULT 'SYNCED' COMMENT '同步状态：SYNCED-已同步, UNSYNCED-未同步',
    batch_id VARCHAR(50) COMMENT '批次号',
    metadata JSON COMMENT '元数据信息',
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '订单归档时间'
) COMMENT='历史订单表，存储已完成的订单历史记录，包含订单的完成时间和最终状态';

-- 3. 订单明细表（存储订单的详细商品信息）
CREATE TABLE IF NOT EXISTS order_items (
    item_id VARCHAR(50) PRIMARY KEY COMMENT '订单项编号，主键',
    order_id VARCHAR(50) NOT NULL COMMENT '所属订单编号，外键关联current_orders表',
    product_id VARCHAR(50) NOT NULL COMMENT '商品编号',
    product_name VARCHAR(100) NOT NULL COMMENT '商品名称',
    quantity INT NOT NULL COMMENT '商品数量',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '商品单价',
    subtotal DECIMAL(10,2) NOT NULL COMMENT '商品小计金额',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '创建人',
    updated_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后修改时间',
    remark TEXT COMMENT '备注信息',
    source_system VARCHAR(50) DEFAULT 'ORDER_SYSTEM' COMMENT '来源系统',
    data_status VARCHAR(20) DEFAULT 'VALID' COMMENT '数据状态：VALID-有效, INVALID-无效',
    sync_status VARCHAR(20) DEFAULT 'SYNCED' COMMENT '同步状态：SYNCED-已同步, UNSYNCED-未同步',
    batch_id VARCHAR(50) COMMENT '批次号',
    metadata JSON COMMENT '元数据信息',
    FOREIGN KEY (order_id) REFERENCES current_orders(order_id)
) COMMENT='订单明细表，存储订单的详细商品信息，包含商品数量、单价等详细信息';

-- 4. 订单状态变更表（记录订单状态的变化历史）
CREATE TABLE IF NOT EXISTS order_status_changes (
    change_id VARCHAR(50) PRIMARY KEY COMMENT '状态变更记录编号，主键',
    order_id VARCHAR(50) NOT NULL COMMENT '订单编号，外键关联current_orders表',
    previous_status VARCHAR(20) NOT NULL COMMENT '变更前状态',
    new_status VARCHAR(20) NOT NULL COMMENT '变更后状态',
    change_reason TEXT COMMENT '状态变更原因',
    changed_by VARCHAR(50) NOT NULL COMMENT '变更操作人',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '创建人',
    updated_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后修改时间',
    remark TEXT COMMENT '备注信息',
    source_system VARCHAR(50) DEFAULT 'ORDER_SYSTEM' COMMENT '来源系统',
    data_status VARCHAR(20) DEFAULT 'VALID' COMMENT '数据状态：VALID-有效, INVALID-无效',
    sync_status VARCHAR(20) DEFAULT 'SYNCED' COMMENT '同步状态：SYNCED-已同步, UNSYNCED-未同步',
    batch_id VARCHAR(50) COMMENT '批次号',
    metadata JSON COMMENT '元数据信息',
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '变更时间',
    FOREIGN KEY (order_id) REFERENCES current_orders(order_id)
) COMMENT='订单状态变更表，记录订单状态的变化历史，包含状态变更的原因和时间';

-- 5. 订单支付记录表（记录订单的支付信息）
CREATE TABLE IF NOT EXISTS order_payments (
    payment_id VARCHAR(50) PRIMARY KEY COMMENT '支付记录编号，主键',
    order_id VARCHAR(50) NOT NULL COMMENT '订单编号，外键关联current_orders表',
    payment_amount DECIMAL(10,2) NOT NULL COMMENT '支付金额',
    payment_method VARCHAR(20) NOT NULL COMMENT '支付方式：ALIPAY-支付宝, WECHAT-微信, BANK-银行转账',
    payment_status VARCHAR(20) NOT NULL COMMENT '支付状态：PENDING-处理中, SUCCESS-成功, FAILED-失败',
    transaction_id VARCHAR(100) COMMENT '第三方支付平台交易号',
    payment_date DATETIME NOT NULL COMMENT '支付时间',
    version INT DEFAULT 1 COMMENT '版本号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '创建人',
    updated_by VARCHAR(50) DEFAULT 'SYSTEM' COMMENT '更新人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
    last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后修改时间',
    remark TEXT COMMENT '备注信息',
    source_system VARCHAR(50) DEFAULT 'ORDER_SYSTEM' COMMENT '来源系统',
    data_status VARCHAR(20) DEFAULT 'VALID' COMMENT '数据状态：VALID-有效, INVALID-无效',
    sync_status VARCHAR(20) DEFAULT 'SYNCED' COMMENT '同步状态：SYNCED-已同步, UNSYNCED-未同步',
    batch_id VARCHAR(50) COMMENT '批次号',
    metadata JSON COMMENT '元数据信息',
    FOREIGN KEY (order_id) REFERENCES current_orders(order_id)
) COMMENT='订单支付记录表，记录订单的支付信息，包含支付方式、交易ID等支付相关信息';

-- 清空现有数据
TRUNCATE TABLE order_payments;
TRUNCATE TABLE order_status_changes;
TRUNCATE TABLE order_items;
TRUNCATE TABLE historical_orders;
TRUNCATE TABLE current_orders;

-- 插入测试数据
INSERT INTO current_orders (
    order_id, customer_id, order_date, order_status, total_amount, payment_status, shipping_address,
    version, is_active, is_deleted, created_by, updated_by, remark, source_system, data_status, sync_status, batch_id, metadata
)
VALUES 
('ORD001', 'CUST001', '2024-03-20 10:00:00', 'PENDING', 199.99, 'UNPAID', '北京市朝阳区xxx街道',
1, TRUE, FALSE, 'ADMIN', 'ADMIN', '普通订单', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"priority": "normal", "tags": ["urgent"]}'),
('ORD002', 'CUST002', '2024-03-20 11:00:00', 'PROCESSING', 299.99, 'PAID', '上海市浦东新区xxx街道',
1, TRUE, FALSE, 'ADMIN', 'ADMIN', 'VIP订单', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"priority": "high", "tags": ["vip"]}'),
('ORD003', 'CUST003', '2024-03-21 09:00:00', 'PENDING', 399.99, 'UNPAID', '广州市天河区xxx街道',
1, TRUE, FALSE, 'ADMIN', 'ADMIN', '大额订单', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH002', '{"priority": "high", "tags": ["large"]}');

INSERT INTO historical_orders (
    order_id, customer_id, order_date, completion_date, final_status, total_amount, payment_method, shipping_address,
    version, is_active, is_deleted, created_by, updated_by, remark, source_system, data_status, sync_status, batch_id, metadata
)
VALUES 
('ORD004', 'CUST001', '2024-02-01 09:00:00', '2024-02-05 15:00:00', 'COMPLETED', 99.99, 'ALIPAY', '北京市朝阳区xxx街道',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '历史订单1', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"priority": "normal", "tags": ["completed"]}'),
('ORD005', 'CUST002', '2024-02-15 14:00:00', '2024-02-20 10:00:00', 'COMPLETED', 199.99, 'WECHAT', '上海市浦东新区xxx街道',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '历史订单2', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"priority": "normal", "tags": ["completed"]}'),
('ORD006', 'CUST003', '2024-02-28 16:00:00', '2024-03-05 11:00:00', 'CANCELLED', 299.99, 'BANK', '广州市天河区xxx街道',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '已取消订单', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH004', '{"priority": "low", "tags": ["cancelled"]}');

INSERT INTO order_items (
    item_id, order_id, product_id, product_name, quantity, unit_price, subtotal,
    version, is_active, is_deleted, created_by, updated_by, remark, source_system, data_status, sync_status, batch_id, metadata
)
VALUES 
('ITEM001', 'ORD001', 'PROD001', '商品A', 2, 99.99, 199.98,
1, TRUE, FALSE, 'ADMIN', 'ADMIN', '热销商品', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"category": "electronics", "tags": ["popular"]}'),
('ITEM002', 'ORD002', 'PROD002', '商品B', 1, 299.99, 299.99,
1, TRUE, FALSE, 'ADMIN', 'ADMIN', '高端商品', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"category": "luxury", "tags": ["premium"]}'),
('ITEM003', 'ORD003', 'PROD003', '商品C', 3, 133.33, 399.99,
1, TRUE, FALSE, 'ADMIN', 'ADMIN', '促销商品', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH002', '{"category": "promotion", "tags": ["discount"]}'),
('ITEM004', 'ORD004', 'PROD004', '商品D', 1, 99.99, 99.99,
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '历史商品', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"category": "history", "tags": ["archived"]}');

INSERT INTO order_status_changes (
    change_id, order_id, previous_status, new_status, change_reason, changed_by,
    version, is_active, is_deleted, created_by, updated_by, remark, source_system, data_status, sync_status, batch_id, metadata
)
VALUES 
('CHG001', 'ORD001', 'NEW', 'PENDING', '订单已确认', 'SYSTEM',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '状态变更1', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"type": "status_change", "tags": ["initial"]}'),
('CHG002', 'ORD002', 'PENDING', 'PROCESSING', '开始处理订单', 'SYSTEM',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '状态变更2', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"type": "status_change", "tags": ["processing"]}'),
('CHG003', 'ORD003', 'NEW', 'PENDING', '订单已确认', 'SYSTEM',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '状态变更3', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH002', '{"type": "status_change", "tags": ["initial"]}'),
('CHG004', 'ORD004', 'PROCESSING', 'COMPLETED', '订单已完成', 'SYSTEM',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '状态变更4', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"type": "status_change", "tags": ["final"]}');

INSERT INTO order_payments (
    payment_id, order_id, payment_amount, payment_method, payment_status, transaction_id, payment_date,
    version, is_active, is_deleted, created_by, updated_by, remark, source_system, data_status, sync_status, batch_id, metadata
)
VALUES 
('PAY001', 'ORD002', 299.99, 'ALIPAY', 'SUCCESS', 'TRX001', '2024-03-20 11:30:00',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '支付宝支付', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH001', '{"channel": "online", "tags": ["alipay"]}'),
('PAY002', 'ORD004', 99.99, 'WECHAT', 'SUCCESS', 'TRX002', '2024-02-01 09:30:00',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '微信支付', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"channel": "online", "tags": ["wechat"]}'),
('PAY003', 'ORD005', 199.99, 'BANK', 'SUCCESS', 'TRX003', '2024-02-15 14:30:00',
1, TRUE, FALSE, 'SYSTEM', 'SYSTEM', '银行转账', 'ORDER_SYSTEM', 'VALID', 'SYNCED', 'BATCH003', '{"channel": "offline", "tags": ["bank"]}'); 