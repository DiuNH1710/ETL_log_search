# User Search Log Analysis – ETL + AI Classification + EDA Visualization

## Tổng quan Project

Project kết hợp **ETL pipeline**, **AI classification** và **EDA visualization** để xử lý và phân tích dữ liệu log tìm kiếm người dùng.

---

## Mục tiêu chính

1. **Phân tích hành vi người dùng**

   - Theo dõi các từ khóa người dùng tìm kiếm.
   - Nhận diện các thể loại nội dung mà người dùng quan tâm (phim, show, thể thao, hoạt hình…).

2. **Xử lý dữ liệu lớn & ETL**

   - Đọc dữ liệu parquet nhiều thư mục, làm sạch dữ liệu thiếu, chuẩn hóa cột.
   - Tính toán top keyword theo từng user, theo tháng (ví dụ tháng 6, tháng 7).
   - Xuất dữ liệu ra CSV phục vụ báo cáo hoặc dashboard.

3. **AI Keyword Classification**

   - Chuẩn hóa tên từ khóa (thêm dấu, tách từ, sửa lỗi chính tả).
   - Gán thể loại phù hợp nhất dựa trên danh sách thể loại predefined (Action, Romance, Comedy, Drama, K/C Drama, Animation, Reality Show…).
   - Giúp phân tích chính xác sở thích người dùng, hỗ trợ recommendation system hoặc marketing.

4. **Phân tích & Trực quan hóa (EDA)**
   - Khám phá và minh họa xu hướng tìm kiếm giữa **tháng 6 và tháng 7**.
   - Phân tích **mức độ thay đổi độ phổ biến** của từng từ khóa.
   - So sánh **tỷ lệ người dùng giữ nguyên top1 keyword** giữa hai tháng.
   - Thống kê **phân bố thể loại** trong top keyword phổ biến.

---

## Flow & Kiến trúc tổng quan

1. **Data Ingestion**

   - Đọc dữ liệu parquet nhiều thư mục (`log_search/`) bằng PySpark.
   - Dữ liệu thô gồm: `eventID, datetime, user_id, keyword, category, platform, networkType, userPlansMap`.

2. **Data Cleaning & Transformation**

   - Loại bỏ dòng trống, NULL, chuẩn hóa cột `keyword`.
   - Tạo cột `month` từ `datetime`.
   - Tính **top keyword mỗi user theo tháng** (top 1 hoặc top 3).

3. **AI Keyword Classification**

   - Lấy top 30 keyword phổ biến → gọi API để gán thể loại phù hợp.
   - Xuất kết quả JSON và CSV (`keyword_classified_top30.csv`).

4. **EDA & Visualization**

   - Thực hiện bằng file `eda_keyword.py`.
   - Sử dụng `matplotlib` và `seaborn` để vẽ biểu đồ.
   - Tự động lưu biểu đồ ra thư mục `outputs/charts/` dưới dạng `.png`.

   **Các biểu đồ chính:**

   - **Top 20 từ khóa phổ biến (tổng hợp 2 tháng)**
   - **Heatmap:** So sánh tần suất tìm kiếm tháng 6 vs tháng 7
   - **User behavior:** So sánh top1 tháng 6 → top1 tháng 7
   - **Xu hướng tìm kiếm tháng 6 và tháng 7**
   - **Phân tích thể loại trong top 30 từ khóa phổ biến**

---

## 📂 Cấu trúc thư mục

```bash
LOG_SEARCH_ETL/
│
├── log_search/ # (dữ liệu gốc)
│
├── outputs/
│ ├── charts/ # Lưu biểu đồ đầu ra (PNG)
│ ├── top_keyword_by_month/ # Top từ khóa theo từng tháng
│ ├── top1_keywords/ # Từ khóa top 1 mỗi tháng
│ └── top3_keywords/ # Top 3 từ khóa mỗi tháng
│ └── keyword_classified_top30.csv # 30 từ khóa phổ biến nhất
│
├── .env # Thông tin môi trường (API key, config)
├── .gitignore # Loại trừ các file không cần commit
│
├── ai_keyword_classifier.py # Script AI phân loại nội dung từ khóa
├── eda_keywords.ipynb # Notebook phân tích khám phá dữ liệu (EDA)
├── ETL_log_search.ipynb
│
├── top_keyword_by_month.py # Tính toán top từ khóa theo tháng
├── top_keywords_analysis.py # Phân tích từ khóa tổng thể
│
└── README.md # Tài liệu mô tả dự án

```

## 📊 Ví dụ biểu đồ

- **Top 20 từ khóa được tìm kiếm nhiều nhất:**
  ![alt text](image.png)

- **Heatmap:** So sánh tần suất tìm kiếm tháng 6 vs tháng 7
  ![alt text](image-1.png)

- **User behavior:** So sánh top1 tháng 6 → top1 tháng 7
  ![alt text](image-2.png)

- **Xu hướng tìm kiếm tháng 6 và tháng 7**
  ![alt text](image-3.png)

- **Phân tích thể loại trong top 30 từ khóa phổ biến**
  ![alt text](image-4.png)

![alt text](image-5.png)
