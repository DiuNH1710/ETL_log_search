## 🔹 Kiến trúc ETL + AI & Flow Diagram

Project kết hợp **ETL pipeline** và **AI classification** để xử lý dữ liệu log tìm kiếm người dùng.

### Flow & Kiến trúc:

1. **Data Ingestion**

   - Đọc dữ liệu parquet nhiều thư mục (`log_search/`) bằng PySpark.
   - Dữ liệu thô chứa: `eventID, datetime, user_id, keyword, category, platform, networkType, userPlansMap`.

2. **Data Cleaning & Transformation**

   - Loại bỏ dòng trống, NULL, chuẩn hóa cột `keyword`.
   - Tạo cột `month` từ `datetime`.
   - Tính **top keyword mỗi user theo tháng** (top 1 hoặc top 3).

3. **AI Keyword Classification** ⭐

   - Lấy top 30 keyword phổ biến nhất.
   - Gọi **OpenAI / OpenRouter API** để phân loại keyword theo thể loại:  
     `Action, Romance, Comedy, Drama, K/C Drama, Animation, Reality Show, Sports, TV Channel, News, Other`.
   - Chuẩn hóa từ khóa: thêm dấu, tách từ, sửa lỗi chính tả.
   - Nhận diện ý nghĩa: tên phim, show, đội tuyển, nhân vật, mô tả thể loại.
   - Trả về **1 JSON object** `{keyword: category}`.

4. **Output & Reporting**
   - Lưu kết quả top keyword theo tháng: `most_search_t6`, `most_search_t7`.
   - Lưu kết quả AI phân loại keyword: `keyword_classified_top30.csv`.
   - Dữ liệu sẵn sàng cho **dashboard / BI / recommendation system**.

---

### Flow Diagram

```text
┌─────────────────┐
│ Log Search Data │
│   (Parquet)     │
└────────┬────────┘
         │
         ▼
┌───────────────────────────┐
│ PySpark ETL Processing     │
│ - Clean / Filter          │
│ - Add Month Column        │
│ - Top Keyword per User    │
└────────┬──────────────────┘
         │
         ▼
┌───────────────────────────┐
│ Top 30 Keywords           │
│ (per user / overall)      │
└────────┬──────────────────┘
         │
         ▼
┌───────────────────────────┐
│ AI Keyword Classification │
│ - OpenAI / OpenRouter API │
│ - JSON output: {keyword: category} │
└────────┬──────────────────┘
         │
         ▼
┌───────────────────────────┐
│ CSV Output & Reporting    │
│ - top_keyword_by_month    │
│ - keyword_classified_top30│
└───────────────────────────┘
```
