-- Test: Không có giá trị null ở cột doanh thu và số lượng
SELECT * FROM {{ ref('mart_sales_summary') }}
WHERE total_sales IS NULL OR total_quantity IS NULL
