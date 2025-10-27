## 📌 Tổng quan project

Project kết hợp **ETL pipeline** và **AI classification** để xử lý dữ liệu log tìm kiếm người dùng.

### Mục tiêu chính của project:

1. **Phân tích hành vi người dùng**:

   - Theo dõi các từ khóa người dùng tìm kiếm.
   - Nhận diện các thể loại nội dung mà người dùng quan tâm (phim, show, thể thao, hoạt hình…).

2. **Xử lý dữ liệu lớn & ETL**:

   - Đọc dữ liệu parquet nhiều thư mục, làm sạch dữ liệu thiếu, chuẩn hóa cột.
   - Tính toán top keyword theo từng user, theo tháng (ví dụ tháng 6, tháng 7).
   - Xuất dữ liệu ra CSV phục vụ báo cáo hoặc dashboard.

3. **Sử dụng AI để phân loại keyword**:
   - Chuẩn hóa tên từ khóa (thêm dấu, tách từ, sửa lỗi chính tả).
   - Gán thể loại phù hợp nhất dựa trên danh sách thể loại predefined (Action, Romance, Comedy, Drama, K/C Drama, Animation, Reality Show…).
   - Giúp phân tích chính xác sở thích người dùng, từ đó cải thiện recommendation system hoặc marketing.

### Flow & Kiến trúc:

1. **Data Ingestion**

   - Đọc dữ liệu parquet nhiều thư mục (`log_search/`) bằng PySpark.
   - Dữ liệu thô chứa: `eventID, datetime, user_id, keyword, category, platform, networkType, userPlansMap`.

2. **Data Cleaning & Transformation**

   - Loại bỏ dòng trống, NULL, chuẩn hóa cột `keyword`.
   - Tạo cột `month` từ `datetime`.
   - Tính **top keyword mỗi user theo tháng** (top 1 hoặc top 3).

3. **AI Keyword Classification** ⭐

   - Lấy **top 30 keyword phổ biến nhất** từ dữ liệu tìm kiếm.  
     **Lý do:** sử dụng **API miễn phí (free tier)** để thử nghiệm, giới hạn số lượng request mỗi lần.

- Đây chỉ là **sample test**, giúp kiểm tra pipeline, AI phân loại hoạt động đúng.
- Nếu có kinh phí hoặc API trả phí, hoàn toàn có thể **phân tích toàn bộ keyword**, từ đó thu được insight đầy đủ hơn về hành vi người dùng.

- Quá trình AI Classification:
  1. Chuẩn hóa từ khóa: thêm dấu, tách từ, sửa lỗi chính tả.
  2. Nhận diện ý nghĩa: tên phim, show, đội tuyển, nhân vật, mô tả thể loại.
  3. Gán thể loại phù hợp: `Action, Romance, Comedy, Drama, K/C Drama, Animation, Reality Show, Sports, TV Channel, News, Other`.
  4. Trả về **1 JSON object** `{keyword: category}`.

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
