{{ config(materialized='view') }}
select * from {{ source('public', 'customers') }}