# 🎮 MobileGameChurn: Game Churn Prediction & Player Analytics Pipeline

> **Churn prediction pipeline for mobile games** — Exploratory Data Analysis (EDA), feature engineering, XGBoost modeling, SHAP explainability, and deployment.

---

## 📁 Cấu trúc thư mục (Project Structure)

```text
MobileGameChurn/
├── data/
│   ├── raw/                  # Dữ liệu gốc (online_gaming_behavior_dataset.csv)
│   └── processed/            # Dữ liệu sau tiền xử lý & tạo đặc trưng
├── notebooks/
│   ├── 01_EDA.ipynb          # Phân tích khám phá dữ liệu & hành vi người chơi
│   ├── 02_FeatureEngineering.ipynb # Trích xuất & biến đổi đặc trưng
│   └── 03_Modeling.ipynb     # Thử nghiệm, đánh giá mô hình & SHAP
├── src/
│   ├── data_pipeline.py      # Pipeline tải và làm sạch dữ liệu tự động
│   ├── features.py           # Logic kỹ thuật đặc trưng
│   ├── model.py              # Huấn luyện và lưu trữ mô hình
│   └── api.py                # FastAPI endpoint phục vụ dự đoán Churn
├── reports/                  # Báo cáo, biểu đồ xuất ra
├── dashboard/                # Ứng dụng dashboard giám sát (Streamlit)
├── models/                   # Lưu trữ checkpoint mô hình (.pkl, .joblib)
├── requirements.txt          # Danh sách thư viện cần thiết
└── README.md
```

---

## ⚙️ Cài đặt & Bắt đầu (Quickstart)

### 1. Khởi tạo môi trường ảo
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Chạy Notebook phân tích
Mở [notebooks/01_EDA.ipynb](notebooks/01_EDA.ipynb) trong VS Code hoặc Jupyter Notebook:
```bash
jupyter notebook notebooks/01_EDA.ipynb
```

---

## 📊 Bộ dữ liệu (Dataset)
- **Tập dữ liệu:** `online_gaming_behavior_dataset.csv`
- **Quy mô:** 40,034 người chơi
- **Biến mục tiêu:** `EngagementLevel` (`Low`, `Medium`, `High`)
- **Định nghĩa Churn:** Người chơi thuộc nhóm `EngagementLevel == 'Low'` được coi là nhóm rời bỏ / nguy cơ cao.

---

## 💡 Nhật ký Tối ưu Đặc trưng (Feature Engineering Refinement Log)

Trong quá trình xây dựng **Notebook 02 (Feature Engineering)**, nhóm phát triển đã rà soát và điều chỉnh công thức tính toán chỉ số tốc độ cày cấp và mở khóa thành tựu để phản ánh đúng thực tế nghiệp vụ game:

### 1. Vấn đề nhận diện (Problem Identified):
- Công thức sơ khởi: `PlayTimeHours / (PlayerLevel + 1)`.
- **Hạn chế:**
  - Ở level cao (ví dụ level 99), mẫu số bị cộng thêm 1 (thành 100) làm suy giảm giá trị thực tế của chỉ số một cách vô nghĩa.
  - Về mặt lý tưởng, do độ khó tăng dần theo cấp (ví dụ: cày từ level 1 → 5 chỉ mất 1 giờ, nhưng từ 5 → 10 mất tới 9 giờ), tốc độ lên cấp chuẩn xác nhất cần tính theo hiệu số thời gian giữa các mốc:  
    $$\Delta t = \text{Thời điểm đạt Level } N - \text{Thời điểm đạt Level } (N - 1)$$

### 2. Đánh giá tính khả thi trên dữ liệu (Data Feasibility Check):
- Kiểm tra tập dữ liệu `online_gaming_behavior_dataset.csv`: Đây là tập dữ liệu **tổng hợp tĩnh cấp người chơi (User-level aggregated snapshot)**, mỗi người chơi chỉ có 1 dòng dữ liệu tóm tắt.
- Dữ liệu hiện tại **không có bảng event timestamp logs** ghi nhận thời gian thực đạt từng level, nên chưa thể trích xuất hiệu số thời gian theo từng mốc level liên tiếp.

### 3. Giải pháp chuẩn hóa (Refined Implementation):
Áp dụng cơ chế phân nhánh điều kiện an toàn, chia trực tiếp cho `PlayerLevel` mà không cộng lệch mẫu số:
- **Nếu `PlayerLevel == 0`:** Mặc định `PlayTimePerLevel = PlayTimeHours` (vì người chơi chưa lên được cấp nào).
- **Nếu `PlayerLevel >= 1`:** Tính trực tiếp $\text{PlayTimePerLevel} = \frac{\text{PlayTimeHours}}{\text{PlayerLevel}}$.
- Tương tự với chỉ số thành tựu: $\text{AchievementsPerLevel} = \frac{\text{AchievementsUnlocked}}{\text{PlayerLevel}}$ (với Level 0 giữ nguyên `AchievementsUnlocked`).

```python
# Cập nhật trong notebooks/02_FeatureEngineering.ipynb
df['PlayTimePerLevel'] = np.where(
    df['PlayerLevel'] == 0, 
    df['PlayTimeHours'], 
    df['PlayTimeHours'] / df['PlayerLevel']
)

df['AchievementsPerLevel'] = np.where(
    df['PlayerLevel'] == 0,
    df['AchievementsUnlocked'],
    df['AchievementsUnlocked'] / df['PlayerLevel']
)
```

> **Kết quả:** Các chỉ số phản ánh trung thực tỷ lệ cày cấp trên toàn bộ dải người chơi (Level 1 đến 99) mà không làm méo mó phân phối đặc trưng trước khi đưa vào mô hình Machine Learning.
