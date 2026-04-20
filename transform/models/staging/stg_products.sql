{{ config(materialized='table') }}
SELECT 
	sku_id,
	name,
	category,
	brand,
	cost_price,
	list_price,
	base_price,
	current_price,
	stock_quantity,
	description
FROM {{ source('public', 'inventory') }}