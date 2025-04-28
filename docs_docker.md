# Hướng dẫn Sử dụng Docker để Triển khai Hệ thống với Python 3.7

## 1. Giới thiệu

Tài liệu này hướng dẫn cách sử dụng Docker để thiết lập môi trường Python 3.7 và cài đặt thư viện `charm-crypto` cùng các thư viện khác cần thiết cho hệ thống bảo mật giao dịch thương mại trực tuyến.

## 2. Yêu cầu Hệ thống

- Docker đã được cài đặt trên máy của bạn
- Docker Compose (tùy chọn, để dễ dàng quản lý)
- Git (để clone mã nguồn nếu cần)

## 3. Cấu trúc Thư mục

Đảm bảo bạn có cấu trúc thư mục dự án như sau:

```
secure_transaction_project/
├── config/
│   └── config.py
├── crypto/
│   ├── __init__.py
│   ├── ib_pke.py
│   ├── hybrid_encryption.py
│   └── dilithium_sign.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── transaction.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── encryption_service.py
│   └── signature_service.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── app.py
├── Dockerfile
├── docker-compose.yml (tùy chọn)
└── requirements.txt
```

## 4. Các Bước Triển khai

### 4.1 Chuẩn bị Dockerfile và requirements.txt

Đã chuẩn bị sẵn hai file:

1. **requirements.txt**: Chứa danh sách các thư viện Python cần thiết
2. **Dockerfile**: Chứa cấu hình để tạo Docker image với Python 3.7 và các thư viện

### 4.2 Xây dựng Docker Image

Mở terminal và di chuyển đến thư mục dự án, sau đó chạy lệnh:

```bash
docker build -t secure-transaction-system .
```

Lệnh này sẽ tạo một Docker image có tên `secure-transaction-system` dựa trên cấu hình trong Dockerfile.

### 4.3 Chạy Container từ Image

Sau khi xây dựng image thành công, bạn có thể chạy container bằng lệnh:

```bash
docker run -it --name secure-transaction secure-transaction-system
```

Lệnh này sẽ khởi động container và chạy ứng dụng theo lệnh mặc định trong Dockerfile (python app.py).

### 4.4 Chạy Shell trong Container

Nếu bạn muốn truy cập vào shell của container để thực hiện các lệnh thủ công:

```bash
docker run -it --name secure-transaction secure-transaction-system /bin/bash
```

Hoặc nếu container đã chạy:

```bash
docker exec -it secure-transaction /bin/bash
```

### 4.5 Sử dụng Docker Compose (Tùy chọn)

Để dễ dàng quản lý, bạn có thể sử dụng Docker Compose. Tạo file `docker-compose.yml` với nội dung:

```yaml
version: '3'

services:
  secure-transaction:
    build: .
    volumes:
      - ./:/app
    # ports:
    #   - "5000:5000"  # Nếu ứng dụng là web service
    command: python app.py
```

Sau đó chạy:

```bash
docker-compose up
```

## 5. Kiểm tra Cài đặt

Để kiểm tra xem `charm-crypto` đã được cài đặt thành công trong container, bạn có thể chạy:

```bash
docker exec -it secure-transaction python -c "import charm; print(charm.__version__)"
```

Nếu lệnh trên hiển thị phiên bản của charm-crypto (ví dụ: 0.43), điều đó có nghĩa là thư viện đã được cài đặt thành công.

## 6. Phát triển và Kiểm thử

### 6.1 Phát triển với Volume

Khi phát triển, bạn có thể mount thư mục dự án vào container để các thay đổi mã nguồn được phản ánh ngay lập tức:

```bash
docker run -it --name secure-transaction -v $(pwd):/app secure-transaction-system /bin/bash
```

### 6.2 Chạy Kiểm thử

Để chạy các bài kiểm thử trong container:

```bash
docker exec -it secure-transaction python -m unittest discover tests
```

## 7. Xử lý Sự cố

### 7.1 Lỗi Cài đặt charm-crypto

Nếu vẫn gặp lỗi khi cài đặt charm-crypto trong container, bạn có thể thử cài đặt từ mã nguồn:

```bash
docker exec -it secure-transaction bash -c "
apt-get update && apt-get install -y git &&
git clone https://github.com/JHUISI/charm.git &&
cd charm &&
./configure.sh &&
make install
"
```

### 7.2 Lỗi Thư viện Khác

Nếu gặp lỗi với các thư viện khác, bạn có thể cài đặt thủ công trong container:

```bash
docker exec -it secure-transaction pip install <tên-thư-viện>
```

## 8. Triển khai Sản xuất

Khi triển khai vào môi trường sản xuất, bạn nên:

1. Tối ưu hóa Dockerfile để giảm kích thước image
2. Sử dụng Docker Compose để quản lý nhiều dịch vụ (nếu cần)
3. Cấu hình các biến môi trường cho các thông số nhạy cảm
4. Thiết lập hệ thống giám sát và ghi log

## 9. Kết luận

Bằng cách sử dụng Docker với Python 3.7, bạn có thể dễ dàng triển khai hệ thống bảo mật giao dịch thương mại trực tuyến mà không gặp vấn đề tương thích với thư viện charm-crypto. Phương pháp này cũng đảm bảo môi trường nhất quán giữa các máy phát triển và môi trường sản xuất.
