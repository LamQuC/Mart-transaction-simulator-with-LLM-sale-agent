{{ config(materialized='view') }}
select * from {{ source('public', 'inventory') }}