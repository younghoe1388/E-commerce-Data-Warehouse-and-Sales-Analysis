import pandas as pd
import sqlite3

# 连接数据库
conn = sqlite3.connect("online_retail.db")

print("电商数据分析报告")

# 查询1：每月销售额趋势（核心指标）
print("\n1. 每月销售额趋势")
query1 = """
select 
    d.year,
    d.month,
    sum(f.total_amount) as total_sales,
    count(distinct f.InvoiceNo) as order_count
    from fact_sales f join dim_date d on f.date_id = d.date_id
    where f.is_cancelled = 0
    group by d.year,d.month
    order by d.year,d.month
    limit 12;
"""
df1 = pd.read_sql(query1, conn)
print(df1.to_string(index = False))

# 查询2：各国销售额排名（地区分析）
print("\n2. 各国销售额排行")
query2 = """
select 
    c.Country,
    sum(f.total_amount) as total_sales,
    count(distinct f.InvoiceNo) as order_count,
    count(*) as item_count
    from fact_sales f join dim_customer c on f.customer_id = c.CustomerID
    where f.is_cancelled = 0
    group by c.Country
    order by total_sales desc
    limit 12
"""
df2 = pd.read_sql(query2, conn)
print(df2.to_string(index = False))

# 查询3：畅销商品 TOP 10（产品分析）
print("\n3. 前十名畅销产品")
query3 = """
select
    p.Description,
    sum(f.Quantity) as total_quantity,
    sum(f.total_amount) as total_sales
    from fact_sales f join dim_product p on f.product_id = p.StockCode
    where f.is_cancelled = 0
    group by p.StockCode, p.Description
    order by total_sales desc
    limit 10;
"""
df3 = pd.read_sql(query3, conn)
print(df3.to_string(index = False))

# 查询4：退货率分析
print("\n4. 退货率分析")
query4 = """
select 
    count(case when f.is_cancelled = 1 then 1 end) as return_order,
    count(*) as total_orders,
    ROUND(SUM(CASE WHEN is_cancelled = 1 THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) as return_rate
    from (select distinct InvoiceNo, is_cancelled from fact_sales) f
"""
df4 = pd.read_sql(query4, conn)
print(df4.to_string(index = False))

# 查询5：周末 vs 工作日销售对比
print("\n5. 周末 vs 工作日销售对比")
query5 = """
select
    (case when d.is_weekend = 1 then "weekend" else "weekday" end) as day_type,
    sum(f.total_amount) as total_sales,
    count(distinct f.InvoiceNo) as order_count
    from fact_sales f join dim_date d on f.date_id = d.date_id
    where f.is_cancelled = 0
    group by day_type
"""
df5 = pd.read_sql(query5, conn)
print(df5.to_string(index = False))

# 查询6：客户价值分层（RFM简化版）
print("\n6. 客户价值分层")
query6 = """
select 
    f.customer_id,
    sum(f.total_amount) as total_spent,
    count(distinct f.InvoiceNo) as order_count
    from fact_sales f where f.is_cancelled = 0
    group by f.customer_id
    order by total_spent desc
    limit 10
"""
df6 = pd.read_sql(query6, conn)
print(df6.to_string(index = False))

conn.close()