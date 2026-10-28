IF DB_ID('olist_source') IS NULL CREATE DATABASE olist_source;
GO
USE olist_source;
GO

CREATE TABLE dbo.customers (
    customer_id              VARCHAR(50)  NOT NULL PRIMARY KEY,
    customer_unique_id       VARCHAR(50)  NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city            NVARCHAR(100),
    customer_state           CHAR(2),
    updated_at               DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.sellers (
    seller_id              VARCHAR(50) NOT NULL PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city            NVARCHAR(100),
    seller_state           CHAR(2),
    updated_at             DATETIME2   NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.products (
    product_id                 VARCHAR(50) NOT NULL PRIMARY KEY,
    product_category_name      NVARCHAR(100),
    product_name_lenght        INT,
    product_description_lenght INT,
    product_photos_qty         INT,
    product_weight_g           INT,
    product_length_cm          INT,
    product_height_cm          INT,
    product_width_cm           INT,
    updated_at                 DATETIME2   NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.orders (
    order_id                      VARCHAR(50) NOT NULL PRIMARY KEY,
    customer_id                   VARCHAR(50) NOT NULL,
    order_status                  VARCHAR(20),
    order_purchase_timestamp      DATETIME2,
    order_approved_at             DATETIME2,
    order_delivered_carrier_date  DATETIME2,
    order_delivered_customer_date DATETIME2,
    order_estimated_delivery_date DATETIME2,
    updated_at                    DATETIME2   NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.order_items (
    order_id            VARCHAR(50)   NOT NULL,
    order_item_id       INT           NOT NULL,
    product_id          VARCHAR(50)   NOT NULL,
    seller_id           VARCHAR(50)   NOT NULL,
    shipping_limit_date DATETIME2,
    price               DECIMAL(10,2),
    freight_value       DECIMAL(10,2),
    updated_at          DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT pk_order_items PRIMARY KEY (order_id, order_item_id)
);

CREATE TABLE dbo.order_payments (
    order_id             VARCHAR(50)   NOT NULL,
    payment_sequential   INT           NOT NULL,
    payment_type         VARCHAR(20),
    payment_installments INT,
    payment_value        DECIMAL(10,2),
    updated_at           DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT pk_order_payments PRIMARY KEY (order_id, payment_sequential)
);
GO