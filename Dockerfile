# Sử dụng base image Python 3.7
FROM python:3.7-slim

# Cài đặt các phụ thuộc hệ thống cần thiết cho charm-crypto và các thư viện khác
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgmp-dev \
    libssl-dev \
    # libpbc-dev # Có thể cần nếu charm-crypto được cấu hình để sử dụng PBC
    && rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các thư viện Python
# Sử dụng --no-cache-dir để giảm kích thước image
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn dự án vào thư mục làm việc
COPY . .

# (Tùy chọn) Expose port nếu ứng dụng là web service (ví dụ: Flask)
# EXPOSE 5000

# Lệnh mặc định để chạy ứng dụng
CMD ["python", "app.py"]

