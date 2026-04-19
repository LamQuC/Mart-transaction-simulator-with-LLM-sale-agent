# Data Pipeline Doanh Nghiệp (Bronze/Silver/Gold)

## Luồng hoạt động

1. **Giao dịch (Bronze)**
	- Customer/Supplier mô phỏng sinh dữ liệu thực tế (orders, nhập hàng, log) vào Postgres.
2. **Thông minh (Bronze)**
	- AI Manager đọc dữ liệu từ Postgres, phân tích, điều chỉnh giá, ghi lại quyết định vào Postgres.
3. **Phân tích (dbt Silver/Gold)**
	- dbt lấy dữ liệu từ Postgres, staging/clean/join (Silver), tổng hợp phân tích/feature (Gold).
4. **Hiển thị (Dashboard)**
	- Streamlit Dashboard đọc dữ liệu từ dbt (Gold) để hiển thị báo cáo, phân tích.

## Lưu ý
- **Không dùng seed mẫu ngoài**. Dữ liệu sinh ra hoàn toàn từ simulation (customer/supplier/AI).
- **Migrations.sql**: Dùng để khởi tạo các bảng Postgres đúng chuẩn.
- **Các model dbt**: Đã được chỉnh để lấy dữ liệu từ các bảng thực tế (orders, inventory, ...).

## Cấu trúc thư mục transform/models
- staging/: Chuẩn hóa dữ liệu raw từ Postgres
- intermediate/: Join, enrich, làm sạch dữ liệu
- mart/: Tổng hợp phân tích
- features/: Feature cho ML

## Khởi tạo database
```sql
-- Chạy file migrations.sql trên Postgres để tạo bảng
```

## Chạy pipeline
1. Chạy mô phỏng (customer/supplier) để sinh dữ liệu thực tế
2. Chạy AI Manager để sinh log/ra quyết định
3. Chạy dbt run để build các bảng phân tích
4. Chạy dashboard để hiển thị
