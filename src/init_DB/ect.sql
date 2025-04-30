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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间'
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    FOREIGN KEY (order_id) REFERENCES current_orders(order_id)
) COMMENT='订单支付记录表，记录订单的支付信息，包含支付方式、交易ID等支付相关信息';

-- 清空现有数据
TRUNCATE TABLE order_payments;
TRUNCATE TABLE order_status_changes;
TRUNCATE TABLE order_items;
TRUNCATE TABLE historical_orders;
TRUNCATE TABLE current_orders;

-- 插入测试数据
INSERT INTO current_orders (order_id, customer_id, order_date, order_status, total_amount, payment_status, shipping_address)
VALUES 
('ORD001', 'CUST001', '2024-03-20 10:00:00', 'PENDING', 199.99, 'UNPAID', '北京市朝阳区xxx街道'),
('ORD002', 'CUST002', '2024-03-20 11:00:00', 'PROCESSING', 299.99, 'PAID', '上海市浦东新区xxx街道');

INSERT INTO historical_orders (order_id, customer_id, order_date, completion_date, final_status, total_amount, payment_method, shipping_address)
VALUES 
('ORD003', 'CUST001', '2024-02-01 09:00:00', '2024-02-05 15:00:00', 'COMPLETED', 99.99, 'ALIPAY', '北京市朝阳区xxx街道'),
('ORD004', 'CUST002', '2024-02-15 14:00:00', '2024-02-20 10:00:00', 'COMPLETED', 199.99, 'WECHAT', '上海市浦东新区xxx街道');

INSERT INTO order_items (item_id, order_id, product_id, product_name, quantity, unit_price, subtotal)
VALUES 
('ITEM001', 'ORD001', 'PROD001', '商品A', 2, 99.99, 199.98),
('ITEM002', 'ORD002', 'PROD002', '商品B', 1, 299.99, 299.99);

INSERT INTO order_status_changes (change_id, order_id, previous_status, new_status, change_reason, changed_by)
VALUES 
('CHG001', 'ORD001', 'NEW', 'PENDING', '订单已确认', 'SYSTEM'),
('CHG002', 'ORD002', 'PENDING', 'PROCESSING', '开始处理订单', 'SYSTEM');

INSERT INTO order_payments (payment_id, order_id, payment_amount, payment_method, payment_status, transaction_id, payment_date)
VALUES 
('PAY001', 'ORD002', 299.99, 'ALIPAY', 'SUCCESS', 'TRX001', '2024-03-20 11:30:00'); 