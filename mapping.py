import os
import json
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. Load .env & API key ---
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(" Không tìm thấy OPENROUTER_API_KEY trong file .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# --- 2. Đọc dữ liệu & làm sạch ---
file_path = r"outputs/top1_keywords/part-00000-2e1801df-6311-4001-9591-2fe8b7cd77fa-c000.csv"
df = pd.read_csv(
    file_path,
    names=["user_id", "keyword", "search_count", "rank"], 
    header=0,                
    on_bad_lines="skip",     # bỏ qua dòng lỗi
    skip_blank_lines=True,   # bỏ dòng trống
    engine="python"         
)

# loại bỏ keyword null / trống
df = df.dropna(subset=["keyword"])
df = df[df["keyword"].str.strip() != ""]

# lấy top 30 keyword
top_keywords = df.head(30)["keyword"].tolist()


# --- 3. tách JSON từ text ---
def extract_json_from_text(text):
    """Tách JSON hợp lệ từ chuỗi có thể chứa text thừa"""
    try:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Không tìm thấy dấu ngoặc JSON")
        json_str = text[start:end+1]
        return json.loads(json_str)
    except Exception:
        return None


# --- 4. Hàm gọi API phân loại ---
def classify_keywords(keywords, retries=3):
    """
    Gửi danh sách keywords cho model GPT để phân loại.
    Trả về dict {keyword: category}
    """
    movie_list = json.dumps(keywords, ensure_ascii=False)

    prompt = f"""
    Bạn là chuyên gia phân loại nội dung phim, chương trình truyền hình và các loại nội dung giải trí.

     Nguyên tắc quan trọng:
    - Không được trả về "Other" nếu có thể đoán được dù chỉ một phần ý nghĩa.
    - Luôn cố gắng sửa lỗi, nhận diện tên gần đúng hoặc đoán thể loại gần đúng.
    - Nếu không chắc → chọn thể loại gần nhất (VD: từ mô tả tình cảm → Romance, tên địa danh thể thao → Sports, chương trình giải trí → Reality Show, v.v.)

     Nhiệm vụ:
    1. **Chuẩn hoá tên**: thêm dấu tiếng Việt nếu cần, tách từ, chỉnh chính tả (vd: "thuyếtminh" → "Thuyết minh", "tramnamu" → "Trăm năm hữu duyên", "capdoi" → "Cặp đôi").
    2. **Nhận diện ý nghĩa gốc**:  
        - Có thể là tên phim, show, series, đội tuyển, quốc gia, nhân vật, hay mô tả thể loại nội dung.  
        - Nếu không rõ ràng, chọn thể loại gần nhất.  
    3. **Gán thể loại phù hợp nhất** trong các nhóm:  
        - Action  
        - Romance  
        - Comedy  
        - Horror  
        - Animation  
        - Drama  
        - C Drama  
        - K Drama  
        - Sports  
        - Music  
        - Reality Show  
        - TV Channel  
        - News  
        - Other

       Một số quy tắc gợi ý nhanh:
    - Có từ “VTV”, “HTV”, “Channel” → TV Channel  
    - Có “running”, “master key”, “reality”, “idol”, “show”, “challenge” → Reality Show  
    - Quốc gia, CLB bóng đá, sự kiện thể thao → Sports hoặc News  
    - Có từ “romantic”, “love”, “kiss” → Romance  
    - Có “potter”, “hogwarts”, “wizard”, “magic” → Drama / Fantasy  
    - Tên phim, diễn viên, hoặc series Trung Quốc → C Drama  
    - Tên phim, diễn viên, hoặc series Hàn Quốc → K Drama  
    - Tên hoạt hình, nhân vật anime → Animation  
    - Các từ mô tả hành động, chiến đấu (“fight”, “gun”, “hero”, “war”) → Action  
    - Các cụm từ mang tính tin tức (“breaking”, “live”, “news”) → News  
    - Nếu chỉ là cụm chung chung (“video”, “clip”, “xem phim”) → Other  

     Chỉ trả về **1 JSON object**.
    - Key = tên gốc trong danh sách.
    - Value = thể loại đã phân loại.

    Ví dụ:
    {{
      "thuyếtminh": "Other",
      "bigfoot": "Horror",
      "capdoi": "Romance",
      "ARGEN": "Sports",
      "nhật ký": "Drama",
      "PENT": "C Drama",
      "running": "Reality Show",
      "VTV3": "TV Channel"
    }}

    Danh sách:
    {movie_list}
    """

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(   # dùng chat.completions thay vì responses.create
            model="tngtech/deepseek-r1t2-chimera:free",         
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

            text = response.choices[0].message.content.strip()
            print("Raw text:\n", text[:500], "\n---\n")
            parsed = extract_json_from_text(text)

            if parsed and isinstance(parsed, dict):
                result = {}
                for k in keywords:
                    result[k] = parsed.get(k, "Other")
                # nếu thiếu key → tự thêm "Other"
                for missing in set(keywords) - set(parsed.keys()):
                    result[missing] = "Other"
                return result
            else:
                print("JSON không hợp lệ, thử lại...")

        except Exception as e:
            print(f" Lỗi API ({e}), thử lại ({attempt+1}/{retries})...")
            time.sleep(3)

    # nếu vẫn thất bại sau retry
    return {k: "Other" for k in keywords}


# --- 5. Chia batch và gọi API ---
batch_size = 10
results = {}

for i in range(0, len(top_keywords), batch_size):
    batch = top_keywords[i:i+batch_size]
    print(f"\n Xử lý batch {i//batch_size + 1} ({len(batch)} keywords)...")
    batch_result = classify_keywords(batch)
    results.update(batch_result)
    print(f" Batch {i//batch_size + 1} có {len(batch_result)} kết quả")


# --- 6. Gộp & lưu kết quả ---
classified_df = pd.DataFrame(list(results.items()), columns=["keyword", "category"])
output_df = classified_df.copy()

# lưu ra file CSV
output_file = "outputs/keyword_classified_top30.csv"
output_df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"\n Đã lưu kết quả 30 keyword vào: {output_file}")
