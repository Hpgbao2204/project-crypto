# Sử dụng base image Python 3.8
FROM python:3.10-slim

# Cài đặt các phụ thuộc hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

# Cài đặt các thư viện Python
# Sử dụng --no-cache-dir để giảm kích thước image
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục dữ liệu
RUN mkdir -p /app/data

# Sao chép toàn bộ mã nguồn dự án vào thư mục làm việc
COPY . .

# Expose port 5000 cho Flask web server
EXPOSE 5000

# Lệnh mặc định để chạy ứng dụng
CMD ["python", "app.py"]
