import pandas as pd;
df = pd.read_excel("Online Retail.xlsx")

# 初步处理数据
print("数据行政：", df.shape)

print("\n前五行数据：")
print(df.head())

print("\n数据类型： ")
print(df.dtypes)
print("\n缺失值数量：")
print(df.isnull().sum())

print("\n数据概述：")
print(df.describe())

print("\n各列数据的名称：")
print(df.info())


# 处理数据缺失值和异常值
missing_count = df.isna().sum()

# df.isna().sum() = 每列的缺失值数量， len(df) = 数据框总行数
missing_ratio = missing_count / len(df) * 100
print("\n每列数据的缺失值比例：", missing_ratio)

# Description 缺失值处理：若一件物品缺失简介 则无法判断其物品为何物 因此删除所有Description为NA的行
before = len(df)
df = df.dropna(subset=["Description"])
after = len(df)
print("\nDescription部分共删除数据行数为：", before - after)

# CustomerID缺失值处理
# CustomerID缺失量过大 不宜删除 因此填充Unknown代替
df["CustomerID"] = df["CustomerID"].fillna("Unknown")
print(f"\nCustomerID 缺失值已填充为 'Unknown'")

print("\n处理后缺失数据总数：")
print(df.isnull().sum()[df.isnull().sum() > 0])

# Quantity异常值处理：Quantity不可能小于0
quantity_wrong = df[df["Quantity"] < 0]
quantity_ratio = len(quantity_wrong) / len(df) * 100

# UnitPrice异常值：UnitPrice = 0意味着物品有可能为赠品
up_zero = df[df["UnitPrice"] == 0]
up_ratio = len(up_zero) / len(df) * 100

# UnitPrice异常值：UnitPrice价格过高 UnitPrice > 1000
up_outlier = df[df["UnitPrice"] > 1000]
up_outlier_ratio = len(up_outlier) / len(df) * 100

# UnitPrice异常值：UnitPrice不应小于0
up_neg = df[df["UnitPrice"] < 0]
up_neg_ratio = len(up_neg) / len(df) * 100

print("\n异常值统计：")
print(f"Quantity < 0（数据错误）: {len(quantity_wrong)} 条，占比 {quantity_ratio:.4f}%")
print(f"UnitPrice = 0（赠品）: {len(up_zero)} 条，占比 {up_ratio:.4f}%")
print(f"UnitPrice > 1000（价格异常高）: {len(up_outlier)} 条，占比 {up_outlier_ratio:.4f}%")
print(f"UnitPrice < 0（价格负数）: {len(up_neg)} 条，占比 {up_neg_ratio:.4f}%")

# 异常值处理
# 1. Quantity < 0：保留，标记为退货（不删除，不改为0）
df["is_cancelled"] = df["Quantity"] < 0 # 新增一列标记退货
print(f"\n退货记录：{df["is_cancelled"].sum()} 条, 已进行标记")

# 2. UnitPrice = 0：保留（赠品），不做处理
print(f"赠品总数：{(df["UnitPrice"] == 0).sum()}")

# 3. UnitPrice < 0：删除（只有2条）
before1 = len(df)
df = df[df["UnitPrice"] >= 0] # 剔除单价小于0的物品
after1 = len(df)
print(f"共删除{before1 - after1}条单价小于0的数据")

# 4. UnitPrice > 1000：先看看具体是什么商品
high_price = df[df["UnitPrice"] > 1000]
print(f"\nUnitPrice > 1000的商品有：")
print(high_price[['StockCode', 'Description', 'UnitPrice']].head(10))

# 处理取消订单：InvoiceNo以'C'开头
df["is_cancel"] = df["InvoiceNo"].astype(str).str.startswith('C')
cancel_count = df["is_cancel"].sum()
print(f"取消订单记录 (InvoiceNo以C开头): {cancel_count}")

# 检查：取消订单是否都是退货？退货是否都是取消订单？
print("\n验证数据一致性：")
print(f"同时标记为退货和取消的: {((df["is_cancel"] == True) & (df["is_cancelled"] == True)).sum()}")
print(f"仅标记为退货但不是取消: {((df["is_cancelled"] == True) & (df["is_cancel"] == False)).sum()}")
print(f"仅标记为取消但不是退货: {((df["is_cancelled"] == False) & (df["is_cancel"] == True)).sum()}")

# 构建星型模型
# 1. 添加总金额列
df["total_amount"] = df["Quantity"] * df["UnitPrice"]
print(f"已增加 total_amount 列: 其范围为 {df['total_amount'].min():.2f} ~ {df['total_amount'].max():.2f}")

# 2. 确保 InvoiceDate 是 datetime 类型
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# 3. 构建维度表
# 3.1 日期维度表 (dim_date)
dim_date = df[["InvoiceDate"]].drop_duplicates().reset_index(drop=True)
dim_date["date_id"] = dim_date["InvoiceDate"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["InvoiceDate"].dt.year
dim_date["month"] = dim_date["InvoiceDate"].dt.month
dim_date["day"] = dim_date["InvoiceDate"].dt.day
dim_date["weekday"] = dim_date["InvoiceDate"].dt.weekday # 0=周一, 6=周日
dim_date["is_weekend"] = dim_date["weekday"] >= 5
print(f"日期维度表: {len(dim_date)}")

# 3.2 产品维度表 (dim_product)
dim_product = df[["StockCode", "Description"]].drop_duplicates().reset_index(drop=True)
print(f"产品维度表: {len(dim_product)}")

# 3.3 客户维度表 (dim_customer)
dim_customer = df[["CustomerID", "Country"]].groupby("CustomerID").agg(lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]).reset_index().drop_duplicates(subset=['CustomerID']).reset_index(drop=True)
dim_customer["CustomerID"] = dim_customer["CustomerID"].astype(str)
print(f"客户维度表: {len(dim_customer)}")

# 4. 构建事实表
# 给 df 添加 date_id（用于关联日期维度）
df["date_id"] = df["InvoiceDate"].dt.strftime("%Y%m%d").astype(int)

# 事实表
fact_sales = df[['InvoiceNo', 'StockCode', 'CustomerID', 'date_id', 'Quantity', 'UnitPrice',
                 'total_amount', 'is_cancelled']].copy()
fact_sales = fact_sales.rename(columns={'StockCode': 'product_id', 'CustomerID': 'customer_id'})

# 将 customer_id 转为字符串（与维度表一致）
fact_sales["customer_id"] = fact_sales["customer_id"].astype(str)
print(f"事实表: {len(fact_sales)}")

# 5. 验证外键关系
print(f"事实表 product_id 在 dim_product 中: {fact_sales['product_id'].isin(dim_product['StockCode']).all()}")
print(f"事实表 customer_id 在 dim_customer 中: {fact_sales['customer_id'].isin(dim_customer['CustomerID']).all()}")
print(f"事实表 date_id 在 dim_date 中: {fact_sales['date_id'].isin(dim_date['date_id']).all()}")

# 6. 保存到 SQLite 数据库
import sqlite3
conn = sqlite3.connect('online_retail.db')

dim_date.to_sql('dim_date', conn, index=False, if_exists='replace')
dim_product.to_sql('dim_product', conn, index=False, if_exists='replace')
dim_customer.to_sql('dim_customer', conn, index=False, if_exists='replace')
fact_sales.to_sql('fact_sales', conn, index=False, if_exists='replace')
conn.close()

print("所有数据均已存入 online_retail.db")

# 7. 查看各表前几行
conn = sqlite3.connect("online_retail.db")

print("\n【dim_date】日期维度表:")
print(pd.read_sql("SELECT * FROM dim_date LIMIT 5", conn))

print("\n【dim_product】产品维度表:")
print(pd.read_sql("SELECT * FROM dim_product LIMIT 5", conn))

print("\n【dim_customer】客户维度表:")
print(pd.read_sql("SELECT * FROM dim_customer LIMIT 5", conn))

print("\n【fact_sales】事实表:")
print(pd.read_sql("SELECT * FROM fact_sales LIMIT 5", conn))

conn.close()