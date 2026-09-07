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
