# Hướng dẫn Triển khai Demo Hệ thống Giao dịch An toàn (Không Charm-Crypto)

## 1. Giới thiệu

Tài liệu này hướng dẫn chi tiết cách triển khai và chạy bản demo của Hệ thống Giao dịch Thương mại Trực tuyến An toàn. Hệ thống này sử dụng các kỹ thuật mã hóa hiện đại để đảm bảo tính bảo mật, toàn vẹn và xác thực cho giao dịch, bao gồm:

*   **Xác thực**: Dựa trên PKI truyền thống (RSA/ECC) sử dụng thư viện `cryptography`.
*   **Mã hóa dữ liệu**: Mã hóa lai kết hợp RSA/ECC và AES-GCM.
*   **Chữ ký số**: Chữ ký hậu lượng tử CRYSTALS-Dilithium.

Bản demo được xây dựng dưới dạng một ứng dụng web Flask và chạy trong môi trường Docker để đảm bảo tính nhất quán và dễ dàng triển khai.

## 2. Yêu cầu Hệ thống

*   **Docker**: Đã được cài đặt trên máy của bạn. Truy cập [https://www.docker.com/get-started](https://www.docker.com/get-started) để cài đặt.
*   **Docker Compose** (Khuyến nghị): Giúp quản lý container dễ dàng hơn. Thường được cài đặt cùng Docker Desktop.
*   **Git** (Tùy chọn): Nếu bạn cần clone mã nguồn từ repository.
*   **Công cụ gọi API**: `curl` (dòng lệnh) hoặc Postman/Insomnia (giao diện đồ họa) để tương tác với web server demo.

## 3. Cấu trúc Thư mục Dự án

Đảm bảo thư mục dự án của bạn có cấu trúc như sau:

```
secure_transaction_project/
├── config/              # (Có thể có nếu bạn tách cấu hình)
├── crypto/
│   ├── __init__.py
│   ├── pki_auth.py         # Module xác thực PKI
│   ├── hybrid_encryption.py # Module mã hóa lai
│   └── dilithium_sign.py   # Module chữ ký Dilithium (không đổi)
├── data/                # Thư mục lưu trữ dữ liệu (khóa, user)
│   ├── ca.pem
│   ├── users.json
│   └── dilithium_keys.json
├── models/              # (Có thể có nếu bạn tách models)
├── services/
│   ├── __init__.py
│   ├── auth_service.py     # Dịch vụ xác thực (đã cập nhật)
│   ├── encryption_service.py # Dịch vụ mã hóa (đã cập nhật)
│   └── signature_service.py # Dịch vụ chữ ký (không đổi)
├── app.py                 # Ứng dụng Flask demo
├── Dockerfile             # File cấu hình Docker (đã cập nhật)
├── docker-compose.yml     # File cấu hình Docker Compose
└── requirements.txt       # Danh sách thư viện Python (đã cập nhật)
```

**Lưu ý**: Thư mục `data/` sẽ được tạo tự động khi chạy ứng dụng lần đầu tiên để lưu trữ khóa CA, thông tin người dùng và khóa Dilithium.

## 4. Thiết lập và Chạy Demo

### Bước 1: Chuẩn bị Mã nguồn

Sao chép tất cả các file mã nguồn (`.py`), `Dockerfile`, `docker-compose.yml`, và `requirements.txt` đã được cung cấp vào thư mục dự án (`secure_transaction_project/`).

### Bước 2: Xây dựng Docker Image

Mở terminal hoặc command prompt, di chuyển vào thư mục gốc của dự án (`secure_transaction_project/`) và chạy lệnh sau:

```bash
docker build -t secure-transaction-demo .
```

Lệnh này sẽ tải base image Python 3.8, cài đặt các phụ thuộc hệ thống và thư viện Python cần thiết, sau đó tạo một image tên là `secure-transaction-demo`.

### Bước 3: Chạy Container

Có hai cách để chạy container:

**Cách 1: Sử dụng `docker run`**

```bash
docker run -it --rm -p 5000:5000 -v $(pwd)/data:/app/data --name secure-demo secure-transaction-demo
```

*   `-it`: Chạy container ở chế độ tương tác và cấp terminal.
*   `--rm`: Tự động xóa container khi dừng.
*   `-p 5000:5000`: Ánh xạ cổng 5000 của máy host vào cổng 5000 của container (nơi Flask chạy).
*   `-v $(pwd)/data:/app/data`: Mount thư mục `data` trên máy host vào `/app/data` trong container. Điều này giúp lưu trữ khóa và thông tin người dùng bền vững ngay cả khi container bị xóa và tạo lại.
*   `--name secure-demo`: Đặt tên cho container.
*   `secure-transaction-demo`: Tên image đã xây dựng.

**Cách 2: Sử dụng `docker-compose` (Khuyến nghị)**

Đảm bảo bạn có file `docker-compose.yml` trong thư mục dự án với nội dung:

```yaml
version: '3.8'

services:
  secure-transaction:
    build: .
    container_name: secure-demo
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data  # Mount thư mục data để lưu trữ bền vững
    # command: python app.py # Lệnh này đã có trong Dockerfile
```

Sau đó chạy lệnh:

```bash
docker-compose up
```

Lệnh này sẽ tự động xây dựng image (nếu chưa có) và khởi chạy container theo cấu hình.

### Bước 4: Kiểm tra Web Server

Sau khi container khởi chạy, bạn sẽ thấy log của ứng dụng Flask trong terminal. Mở trình duyệt hoặc dùng `curl` để kiểm tra:

```bash
curl http://localhost:5000/
```

Bạn sẽ nhận được phản hồi JSON:

```json
{
  "message": "Chào mừng đến với Hệ thống Giao dịch An toàn Demo!"
}
```

## 5. Mô phỏng Luồng Giao dịch An toàn

Bây giờ, chúng ta sẽ sử dụng `curl` (hoặc Postman/Insomnia) để tương tác với các API endpoint và mô phỏng một luồng giao dịch hoàn chỉnh.

**Biến môi trường (Tùy chọn, để dễ dùng curl):**

```bash
API_URL="http://localhost:5000"
SENDER_ID="alice@example.com"
RECEIVER_ID="bob@example.com"
```

### Bước 5.1: Đăng ký Người dùng

Đăng ký người gửi (Alice) và người nhận (Bob).

```bash
# Đăng ký Alice
curl -X POST -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$SENDER_ID\", \"full_name\": \"Alice\", \"phone\": \"111222333\"}" \
     $API_URL/register

# Đăng ký Bob
curl -X POST -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$RECEIVER_ID\", \"full_name\": \"Bob\", \"phone\": \"444555666\"}" \
     $API_URL/register
```

*   **Bảo mật**: Hệ thống tạo cặp khóa RSA (hoặc ECC) và chứng chỉ X.509 cho mỗi người dùng, được ký bởi CA của hệ thống. Đồng thời tạo cặp khóa Dilithium cho chữ ký số.
*   **Lưu ý**: Phản hồi sẽ chứa chứng chỉ và khóa công khai Dilithium (dạng base64). Trong ứng dụng thực tế, khóa riêng RSA/ECC cần được gửi an toàn đến client và lưu trữ bảo mật.

### Bước 5.2: Xác thực Người gửi (Alice)

**a) Yêu cầu Thách thức:**

```bash
curl -X POST -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$SENDER_ID\"}" \
     $API_URL/auth/challenge
```

*   **Bảo mật**: Server tạo một chuỗi ngẫu nhiên (thách thức), mã hóa nó bằng khóa công khai RSA/ECC của Alice (lấy từ chứng chỉ) và gửi lại cho client cùng với `challenge_id`.
*   **Lưu ý**: Lưu lại `challenge_id` và `encrypted_challenge` từ phản hồi.

**b) Giải mã Thách thức (Mô phỏng Client-side):**

Trong ứng dụng thực tế, client (Alice) sẽ dùng khóa riêng RSA/ECC của mình để giải mã `encrypted_challenge`. Vì demo này không có client thực sự, chúng ta bỏ qua bước giải mã thực tế và giả định client đã giải mã đúng.

**c) Gửi Phản hồi để Đăng nhập:**

Lấy `challenge_id` và `encrypted_challenge` từ bước (a). Giả sử client giải mã `encrypted_challenge` thành công và có được `original_text` (trong demo này, server biết `original_text`).

```bash
# Lấy challenge_id và original_text từ bước 5.2.a (cần xem log server hoặc sửa code để lấy)
# Ví dụ:
CHALLENGE_ID="..."
ORIGINAL_TEXT="..."

curl -X POST -H "Content-Type: application/json" \
     -d "{\"user_id\": \"$SENDER_ID\", \"challenge_id\": \"$CHALLENGE_ID\", \"decrypted_challenge\": \"$ORIGINAL_TEXT\"}" \
     $API_URL/auth/login
```

*   **Bảo mật**: Server kiểm tra xem `decrypted_challenge` mà client gửi có khớp với `original_text` của `challenge_id` tương ứng không. Nếu khớp, xác thực thành công.
*   **Lưu ý**: Phản hồi thành công sẽ chứa `token`. Lưu lại token này (trong demo này, token chính là `user_id`).

```bash
TOKEN="$SENDER_ID" # Lưu token (user_id) để dùng cho các yêu cầu sau
```

### Bước 5.3: Tạo Giao dịch

Alice (đã xác thực) tạo một giao dịch gửi tiền cho Bob.

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
     -d "{\"recipient_id\": \"$RECEIVER_ID\", \"amount\": 100.50, \"currency\": \"USD\", \"metadata\": {\"note\": \"Payment for goods\"}}" \
     $API_URL/transactions
```

*   **Bảo mật**: Yêu cầu cần `Authorization` header chứa token đã lấy ở bước đăng nhập.
*   **Lưu ý**: Lưu lại `transaction_id` từ phản hồi.

```bash
TX_ID="..." # Lưu transaction_id
```

### Bước 5.4: Ký Giao dịch

Alice ký vào giao dịch vừa tạo để đảm bảo tính toàn vẹn và chống chối bỏ.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
     $API_URL/transactions/$TX_ID/sign
```

*   **Bảo mật**: Server lấy dữ liệu giao dịch (không bao gồm chữ ký), chuẩn hóa (sắp xếp key JSON), và yêu cầu `SignatureService` ký bằng khóa bí mật Dilithium của Alice. Chữ ký được lưu vào giao dịch.
*   **Lưu ý**: Phản hồi chứa chữ ký (dạng base64).

### Bước 5.5: Xác minh Chữ ký (Tùy chọn)

Bất kỳ ai (ví dụ: Bob hoặc một bên thứ ba) cũng có thể xác minh chữ ký của Alice.

```bash
curl -X POST $API_URL/transactions/$TX_ID/verify
```

*   **Bảo mật**: Server chuẩn hóa lại dữ liệu giao dịch, lấy khóa công khai Dilithium của Alice và chữ ký đã lưu, sau đó gọi `SignatureService` để xác minh.

### Bước 5.6: Mã hóa Thông tin Thanh toán

Alice mã hóa thông tin thẻ tín dụng của mình để chỉ Bob (người nhận) mới có thể đọc được.

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
     -d "{\"payment_info\": {\"card_number\": \"4242424242424242\", \"expiry\": \"12/26\", \"cvv\": \"123\"}}" \
     $API_URL/transactions/$TX_ID/encrypt_payment
```

*   **Bảo mật**: Server lấy thông tin thanh toán, sử dụng `transaction_id` làm "associated data" (dữ liệu liên kết), và gọi `EncryptionService` để thực hiện mã hóa lai:
    1.  Tạo khóa AES ngẫu nhiên.
    2.  Mã hóa thông tin thanh toán bằng AES-GCM (dùng khóa AES và `transaction_id`).
    3.  Mã hóa khóa AES bằng khóa công khai RSA/ECC của Bob.
    4.  Lưu trữ khóa AES đã mã hóa, IV, tag, và ciphertext vào giao dịch.
*   **Lưu ý**: Phản hồi chứa thông tin thanh toán đã mã hóa.

### Bước 5.7: Giải mã Thông tin Thanh toán (Bởi Người nhận - Bob)

Bob (sau khi xác thực) muốn xem thông tin thanh toán để xử lý.

```bash
# Giả sử Bob đã xác thực và có token
BOB_TOKEN="$RECEIVER_ID"

curl -X POST -H "Authorization: Bearer $BOB_TOKEN" \
     $API_URL/transactions/$TX_ID/decrypt_payment
```

*   **Bảo mật**: Server kiểm tra xem người yêu cầu có phải là người nhận (`recipient_id`) của giao dịch không. Nếu đúng, gọi `EncryptionService` để giải mã:
    1.  Giải mã khóa AES bằng khóa riêng RSA/ECC của Bob.
    2.  Sử dụng khóa AES, IV, tag, và `transaction_id` (associated data) để giải mã và xác thực ciphertext bằng AES-GCM.
*   **Lưu ý**: Phản hồi chứa thông tin thanh toán gốc.

## 6. Giải thích Bảo mật

*   **Xác thực**: Việc giải mã thành công thách thức chứng tỏ người dùng sở hữu khóa riêng tương ứng với chứng chỉ, xác thực danh tính của họ.
*   **Mã hóa**: Mã hóa lai đảm bảo chỉ người nhận có khóa riêng phù hợp mới giải mã được thông tin nhạy cảm (khóa AES), trong khi AES-GCM mã hóa hiệu quả dữ liệu lớn và đảm bảo tính toàn vẹn qua tag xác thực và associated data.
*   **Chữ ký số**: Chữ ký Dilithium đảm bảo dữ liệu giao dịch không bị thay đổi sau khi ký (tính toàn vẹn) và người ký không thể chối bỏ hành động của mình (tính không thể chối bỏ), đồng thời kháng lại tấn công từ máy tính lượng tử.
*   **HTTPS/TLS**: Trong môi trường thực tế, toàn bộ giao tiếp giữa client và server phải được bảo vệ bằng HTTPS/TLS để chống nghe lén và tấn công MITM.

## 7. Dọn dẹp

Để dừng và xóa container:

*   Nếu dùng `docker run`: Nhấn `Ctrl+C` trong terminal đang chạy container.
*   Nếu dùng `docker-compose up`: Nhấn `Ctrl+C` trong terminal, sau đó chạy `docker-compose down` để xóa container và network.

Thư mục `data/` trên máy host sẽ vẫn còn chứa khóa và thông tin người dùng.

## 8. Kết luận

Bản demo này minh họa cách tích hợp các kỹ thuật mã hóa PKI, mã hóa lai và chữ ký số hậu lượng tử vào một ứng dụng web để tạo ra một hệ thống giao dịch trực tuyến an toàn. Bạn có thể dựa trên nền tảng này để phát triển các ứng dụng phức tạp hơn.
