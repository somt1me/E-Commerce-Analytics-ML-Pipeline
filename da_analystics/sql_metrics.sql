-- ============================================================================
-- SQL ANALYTICS FOR OLIST E-COMMERCE
-- ============================================================================

-- 1. Monthly Revenue & Growth Rate 
-- Using CTE and LAG() Window Function 
WITH MonthlySales AS (
    SELECT 
        strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(p.payment_value), 2) AS total_revenue
    FROM orders o
    JOIN order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
)
SELECT 
    order_month,
    total_orders,
    total_revenue,
    -- Get previous month's revenue / Lấy doanh thu của tháng trước
    LAG(total_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
    -- Calculate MoM growth percentage / Tính % tăng trưởng so với tháng trước
    ROUND(
        (total_revenue - LAG(total_revenue, 1) OVER (ORDER BY order_month)) 
        / LAG(total_revenue, 1) OVER (ORDER BY order_month) * 100, 2
    ) AS mom_growth_percentage
FROM MonthlySales;


-- 2. Top 5 Product Categories per Year / Top 5 Danh mục sản phẩm có doanh thu cao nhất theo năm
-- Using DENSE_RANK() Window Function / Sử dụng hàm xếp hạng DENSE_RANK()
WITH CategoryRevenue AS (
    SELECT 
        strftime('%Y', o.order_purchase_timestamp) AS order_year,
        p.product_category_name,
        ROUND(SUM(i.price), 2) AS category_revenue
    FROM orders o
    JOIN order_items i ON o.order_id = i.order_id
    JOIN products p ON i.product_id = p.product_id
    WHERE o.order_status = 'delivered' AND p.product_category_name IS NOT NULL
    GROUP BY order_year, p.product_category_name
),
RankedCategories AS (
    SELECT 
        order_year,
        product_category_name,
        category_revenue,
        DENSE_RANK() OVER (PARTITION BY order_year ORDER BY category_revenue DESC) AS category_rank
    FROM CategoryRevenue
)
SELECT * FROM RankedCategories 
WHERE category_rank <= 5;