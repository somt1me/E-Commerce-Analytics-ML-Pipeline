-- ============================================================================
-- SQL ANALYTICS ENGINE FOR E-COMMERCE 2026
-- ============================================================================

-- 1. Monthly Revenue, AOV & MoM Growth Rate 
WITH MonthlySales AS (
    SELECT 
        strftime('%Y-%m', order_date) AS order_month,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(order_amount), 2) AS total_revenue,
        ROUND(AVG(order_amount), 2) AS average_order_value -- AOV
    FROM fact_orders
    WHERE LOWER(order_status) NOT IN ('cancelled', 'returned')
    GROUP BY order_month
)
SELECT 
    order_month,
    total_orders,
    total_revenue,
    average_order_value,
    LAG(total_revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
    ROUND(
        ((total_revenue - LAG(total_revenue, 1) OVER (ORDER BY order_month)) 
        / LAG(total_revenue, 1) OVER (ORDER BY order_month)) * 100, 2
    ) AS mom_growth_pct
FROM MonthlySales;


-- 2. Category Performance Ranking (Pareto 80/20 Rule)
WITH CategorySales AS (
    SELECT 
        product_category,
        ROUND(SUM(order_amount), 2) AS total_sales,
        COUNT(DISTINCT order_id) AS total_orders
    FROM fact_orders
    WHERE product_category IS NOT NULL 
      AND LOWER(order_status) NOT IN ('cancelled', 'returned')
    GROUP BY product_category
)
SELECT 
    product_category,
    total_sales,
    total_orders,
    DENSE_RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
FROM CategorySales;


-- 3. Order Status Distribution 
SELECT 
    order_status,
    COUNT(order_id) AS order_count,
    ROUND(SUM(order_amount), 2) AS total_amount,
    ROUND(COUNT(order_id) * 100.0 / (SELECT COUNT(*) FROM fact_orders), 2) AS status_percentage
FROM fact_orders
GROUP BY order_status
ORDER BY order_count DESC;