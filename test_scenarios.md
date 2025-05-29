# Kịch bản kiểm thử ứng dụng web mã hóa và chữ ký số

## 1. Kiểm thử xác thực người dùng

### 1.1. Đăng ký người dùng
- **Mục đích**: Kiểm tra chức năng đăng ký người dùng mới
- **Các bước**:
  1. Truy cập trang đăng ký
  2. Điền thông tin người dùng (username, email, password)
  3. Chọn vai trò (Data Owner, Reader, Authority)
  4. Chọn các thuộc tính (Doctor, Nurse, Admin, Researcher)
  5. Nhấn nút đăng ký
- **Kết quả mong đợi**: 
  - Tài khoản được tạo thành công
  - Khóa mã hóa và chữ ký số được tạo tự động
  - Chuyển hướng đến trang đăng nhập với thông báo thành công

### 1.2. Đăng nhập
- **Mục đích**: Kiểm tra chức năng đăng nhập
- **Các bước**:
  1. Truy cập trang đăng nhập
  2. Nhập username và password
  3. Nhấn nút đăng nhập
- **Kết quả mong đợi**: 
  - Đăng nhập thành công
  - Chuyển hướng đến trang chủ
  - Hiển thị thông tin người dùng trên thanh điều hướng

### 1.3. Quản lý hồ sơ
- **Mục đích**: Kiểm tra chức năng xem và cập nhật hồ sơ người dùng
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang hồ sơ
  3. Cập nhật thông tin (email, thuộc tính)
  4. Lưu thay đổi
- **Kết quả mong đợi**: 
  - Thông tin được cập nhật thành công
  - Khóa mã hóa được cập nhật nếu thuộc tính thay đổi

### 1.4. Đổi mật khẩu
- **Mục đích**: Kiểm tra chức năng đổi mật khẩu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang đổi mật khẩu
  3. Nhập mật khẩu hiện tại và mật khẩu mới
  4. Xác nhận mật khẩu mới
  5. Lưu thay đổi
- **Kết quả mong đợi**: 
  - Mật khẩu được cập nhật thành công
  - Khóa chữ ký số được mã hóa lại với mật khẩu mới

## 2. Kiểm thử quản lý tài liệu

### 2.1. Tải lên tài liệu
- **Mục đích**: Kiểm tra chức năng tải lên tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang tải lên tài liệu
  3. Chọn file từ máy tính (PDF, TXT, DOC, DOCX)
  4. Nhấn nút tải lên
- **Kết quả mong đợi**: 
  - Tài liệu được tải lên thành công
  - Hiển thị trong danh sách tài liệu của người dùng

### 2.2. Xem danh sách tài liệu
- **Mục đích**: Kiểm tra chức năng xem danh sách tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Lọc theo loại tài liệu (tất cả, gốc, đã mã hóa, đã ký)
- **Kết quả mong đợi**: 
  - Hiển thị danh sách tài liệu theo bộ lọc
  - Hiển thị đúng thông tin và trạng thái của từng tài liệu

### 2.3. Xem chi tiết tài liệu
- **Mục đích**: Kiểm tra chức năng xem chi tiết tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Nhấn vào nút xem chi tiết của một tài liệu
- **Kết quả mong đợi**: 
  - Hiển thị đầy đủ thông tin chi tiết của tài liệu
  - Hiển thị các hành động có thể thực hiện với tài liệu

### 2.4. Tải xuống tài liệu
- **Mục đích**: Kiểm tra chức năng tải xuống tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Nhấn vào nút tải xuống của một tài liệu
- **Kết quả mong đợi**: 
  - Tài liệu được tải xuống thành công
  - Tên file và định dạng giữ nguyên

### 2.5. Xóa tài liệu
- **Mục đích**: Kiểm tra chức năng xóa tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Nhấn vào nút xóa của một tài liệu
  4. Xác nhận xóa
- **Kết quả mong đợi**: 
  - Tài liệu được xóa khỏi hệ thống
  - Không còn hiển thị trong danh sách tài liệu

## 3. Kiểm thử mã hóa và giải mã

### 3.1. Mã hóa tài liệu với Hybrid ABE
- **Mục đích**: Kiểm tra chức năng mã hóa tài liệu sử dụng Hybrid ABE
- **Các bước**:
  1. Đăng nhập vào hệ thống với vai trò Data Owner
  2. Tải lên một tài liệu mới
  3. Truy cập trang mã hóa
  4. Chọn phương thức mã hóa Hybrid ABE
  5. Định nghĩa chính sách truy cập (ví dụ: "Doctor@Hospital OR Admin@Hospital")
  6. Nhấn nút mã hóa
- **Kết quả mong đợi**: 
  - Tài liệu được mã hóa thành công
  - Hiển thị trong danh sách tài liệu với trạng thái đã mã hóa
  - Chính sách truy cập được lưu trữ

### 3.2. Mã hóa tài liệu với MA-ABE
- **Mục đích**: Kiểm tra chức năng mã hóa tài liệu sử dụng MA-ABE
- **Các bước**:
  1. Đăng nhập vào hệ thống với vai trò Data Owner
  2. Tải lên một tài liệu mới
  3. Truy cập trang mã hóa
  4. Chọn phương thức mã hóa MA-ABE
  5. Định nghĩa chính sách truy cập (ví dụ: "Doctor@Hospital AND Researcher@Hospital")
  6. Nhấn nút mã hóa
- **Kết quả mong đợi**: 
  - Tài liệu được mã hóa thành công
  - Hiển thị trong danh sách tài liệu với trạng thái đã mã hóa
  - Chính sách truy cập được lưu trữ

### 3.3. Giải mã tài liệu (thành công)
- **Mục đích**: Kiểm tra chức năng giải mã tài liệu khi người dùng có đủ thuộc tính
- **Các bước**:
  1. Đăng nhập vào hệ thống với người dùng có thuộc tính phù hợp với chính sách truy cập
  2. Truy cập trang danh sách tài liệu
  3. Tìm tài liệu đã mã hóa
  4. Nhấn nút giải mã
  5. Xác nhận giải mã
- **Kết quả mong đợi**: 
  - Tài liệu được giải mã thành công
  - Tài liệu gốc có thể xem và tải xuống

### 3.4. Giải mã tài liệu (thất bại)
- **Mục đích**: Kiểm tra chức năng giải mã tài liệu khi người dùng không có đủ thuộc tính
- **Các bước**:
  1. Đăng nhập vào hệ thống với người dùng không có thuộc tính phù hợp với chính sách truy cập
  2. Truy cập trang danh sách tài liệu
  3. Tìm tài liệu đã mã hóa
  4. Nhấn nút giải mã
  5. Xác nhận giải mã
- **Kết quả mong đợi**: 
  - Giải mã thất bại
  - Hiển thị thông báo lỗi rõ ràng về việc không đủ thuộc tính

### 3.5. Sử dụng công cụ tạo chính sách
- **Mục đích**: Kiểm tra công cụ hỗ trợ tạo chính sách truy cập
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang công cụ tạo chính sách
  3. Chọn các thuộc tính và toán tử để tạo chính sách
  4. Sao chép chính sách
  5. Sử dụng chính sách trong quá trình mã hóa
- **Kết quả mong đợi**: 
  - Chính sách được tạo đúng cú pháp
  - Chính sách hoạt động chính xác khi sử dụng để mã hóa

## 4. Kiểm thử chữ ký số

### 4.1. Tạo khóa chữ ký số
- **Mục đích**: Kiểm tra chức năng tạo cặp khóa chữ ký số
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang quản lý khóa chữ ký số
  3. Nhập mật khẩu
  4. Nhấn nút tạo khóa mới
- **Kết quả mong đợi**: 
  - Cặp khóa được tạo thành công
  - Khóa công khai hiển thị trên giao diện
  - Khóa riêng tư được mã hóa và lưu trữ an toàn

### 4.2. Xuất khóa công khai
- **Mục đích**: Kiểm tra chức năng xuất khóa công khai
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang quản lý khóa chữ ký số
  3. Nhấn nút tải xuống khóa công khai
- **Kết quả mong đợi**: 
  - File khóa công khai được tải xuống thành công
  - Định dạng file là PEM

### 4.3. Ký tài liệu
- **Mục đích**: Kiểm tra chức năng ký tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Chọn một tài liệu gốc
  4. Nhấn nút ký tài liệu
  5. Nhập mật khẩu để truy cập khóa riêng tư
  6. Xác nhận ký
- **Kết quả mong đợi**: 
  - Tài liệu được ký thành công
  - Hiển thị trong danh sách tài liệu với trạng thái đã ký
  - Chữ ký được lưu trữ

### 4.4. Xác minh chữ ký (hợp lệ)
- **Mục đích**: Kiểm tra chức năng xác minh chữ ký hợp lệ
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Chọn một tài liệu đã ký
  4. Nhấn nút xác minh chữ ký
- **Kết quả mong đợi**: 
  - Xác minh thành công
  - Hiển thị thông báo chữ ký hợp lệ
  - Hiển thị thông tin người ký và thời gian ký

### 4.5. Xác minh chữ ký (không hợp lệ)
- **Mục đích**: Kiểm tra chức năng xác minh chữ ký không hợp lệ
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Chọn một tài liệu đã ký
  4. Sửa đổi tài liệu hoặc chữ ký (thông qua can thiệp trực tiếp vào cơ sở dữ liệu)
  5. Nhấn nút xác minh chữ ký
- **Kết quả mong đợi**: 
  - Xác minh thất bại
  - Hiển thị thông báo chữ ký không hợp lệ

### 4.6. Tải xuống chữ ký
- **Mục đích**: Kiểm tra chức năng tải xuống file chữ ký
- **Các bước**:
  1. Đăng nhập vào hệ thống
  2. Truy cập trang danh sách tài liệu
  3. Chọn một tài liệu đã ký
  4. Nhấn nút tải xuống chữ ký
- **Kết quả mong đợi**: 
  - File chữ ký được tải xuống thành công

## 5. Kiểm thử tích hợp

### 5.1. Mã hóa và ký tài liệu
- **Mục đích**: Kiểm tra quy trình mã hóa sau đó ký tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống với vai trò Data Owner
  2. Tải lên một tài liệu mới
  3. Mã hóa tài liệu với chính sách truy cập
  4. Giải mã tài liệu
  5. Ký tài liệu đã giải mã
- **Kết quả mong đợi**: 
  - Tài liệu được mã hóa thành công
  - Tài liệu được giải mã thành công
  - Tài liệu được ký thành công

### 5.2. Ký và mã hóa tài liệu
- **Mục đích**: Kiểm tra quy trình ký sau đó mã hóa tài liệu
- **Các bước**:
  1. Đăng nhập vào hệ thống với vai trò Data Owner
  2. Tải lên một tài liệu mới
  3. Ký tài liệu
  4. Mã hóa tài liệu đã ký với chính sách truy cập
- **Kết quả mong đợi**: 
  - Tài liệu được ký thành công
  - Tài liệu được mã hóa thành công

### 5.3. Kiểm tra đồng thời nhiều người dùng
- **Mục đích**: Kiểm tra hệ thống với nhiều người dùng đồng thời
- **Các bước**:
  1. Tạo nhiều tài khoản người dùng với các vai trò và thuộc tính khác nhau
  2. Đăng nhập đồng thời với các tài khoản khác nhau
  3. Thực hiện các hoạt động mã hóa, giải mã, ký và xác minh
- **Kết quả mong đợi**: 
  - Hệ thống hoạt động ổn định
  - Không có xung đột giữa các người dùng
  - Các chính sách truy cập được thực thi chính xác

## 6. Kiểm thử giao diện người dùng

### 6.1. Kiểm tra responsive
- **Mục đích**: Kiểm tra giao diện trên các kích thước màn hình khác nhau
- **Các bước**:
  1. Truy cập ứng dụng trên desktop (>= 1200px)
  2. Truy cập ứng dụng trên tablet (768px - 1199px)
  3. Truy cập ứng dụng trên mobile (< 768px)
- **Kết quả mong đợi**: 
  - Giao diện hiển thị phù hợp trên mọi kích thước màn hình
  - Các chức năng vẫn hoạt động bình thường

### 6.2. Kiểm tra trình duyệt
- **Mục đích**: Kiểm tra ứng dụng trên các trình duyệt khác nhau
- **Các bước**:
  1. Truy cập ứng dụng trên Chrome
  2. Truy cập ứng dụng trên Firefox
  3. Truy cập ứng dụng trên Safari (nếu có)
  4. Truy cập ứng dụng trên Edge
- **Kết quả mong đợi**: 
  - Ứng dụng hoạt động nhất quán trên các trình duyệt
  - Không có lỗi hiển thị hoặc chức năng

### 6.3. Kiểm tra thông báo lỗi
- **Mục đích**: Kiểm tra hiển thị thông báo lỗi
- **Các bước**:
  1. Thực hiện các hành động gây lỗi (nhập sai mật khẩu, tải lên file không hợp lệ, v.v.)
  2. Quan sát thông báo lỗi
- **Kết quả mong đợi**: 
  - Thông báo lỗi rõ ràng và hữu ích
  - Hướng dẫn người dùng cách khắc phục

### 6.4. Kiểm tra trải nghiệm người dùng
- **Mục đích**: Đánh giá trải nghiệm người dùng tổng thể
- **Các bước**:
  1. Thực hiện các luồng công việc chính từ đầu đến cuối
  2. Đánh giá tính dễ sử dụng, hiệu quả và sự hài lòng
- **Kết quả mong đợi**: 
  - Luồng công việc mượt mà và trực quan
  - Người dùng có thể hoàn thành nhiệm vụ một cách hiệu quả

## 7. Kiểm thử bảo mật

### 7.1. Kiểm tra xác thực
- **Mục đích**: Kiểm tra tính bảo mật của hệ thống xác thực
- **Các bước**:
  1. Thử truy cập các trang yêu cầu đăng nhập khi chưa đăng nhập
  2. Thử đăng nhập với thông tin không hợp lệ
  3. Thử truy cập tài nguyên của người dùng khác
- **Kết quả mong đợi**: 
  - Chuyển hướng đến trang đăng nhập khi chưa đăng nhập
  - Hiển thị thông báo lỗi khi đăng nhập không hợp lệ
  - Không thể truy cập tài nguyên của người dùng khác

### 7.2. Kiểm tra mã hóa
- **Mục đích**: Kiểm tra tính bảo mật của hệ thống mã hóa
- **Các bước**:
  1. Mã hóa tài liệu với chính sách truy cập phức tạp
  2. Thử giải mã với người dùng không có đủ thuộc tính
  3. Kiểm tra dữ liệu được lưu trữ trong cơ sở dữ liệu
- **Kết quả mong đợi**: 
  - Chỉ người dùng có đủ thuộc tính mới giải mã được
  - Dữ liệu được lưu trữ ở dạng mã hóa

### 7.3. Kiểm tra chữ ký số
- **Mục đích**: Kiểm tra tính bảo mật của hệ thống chữ ký số
- **Các bước**:
  1. Ký tài liệu
  2. Sửa đổi tài liệu
  3. Xác minh chữ ký
- **Kết quả mong đợi**: 
  - Xác minh thất bại khi tài liệu bị sửa đổi
  - Khóa riêng tư không bao giờ được hiển thị hoặc truyền qua mạng

## 8. Kiểm thử hiệu năng

### 8.1. Kiểm tra thời gian phản hồi
- **Mục đích**: Đánh giá thời gian phản hồi của ứng dụng
- **Các bước**:
  1. Đo thời gian tải trang
  2. Đo thời gian thực hiện các hoạt động chính (mã hóa, giải mã, ký, xác minh)
- **Kết quả mong đợi**: 
  - Thời gian tải trang < 2 giây
  - Thời gian thực hiện các hoạt động chính hợp lý

### 8.2. Kiểm tra xử lý file lớn
- **Mục đích**: Kiểm tra khả năng xử lý file lớn
- **Các bước**:
  1. Tải lên file có kích thước lớn (5MB, 10MB, 16MB)
  2. Mã hóa và giải mã file lớn
  3. Ký và xác minh file lớn
- **Kết quả mong đợi**: 
  - Hệ thống xử lý được file lớn
  - Hiển thị thanh tiến trình hoặc thông báo phù hợp

## 9. Kiểm thử triển khai

### 9.1. Kiểm tra cài đặt
- **Mục đích**: Kiểm tra quy trình cài đặt ứng dụng
- **Các bước**:
  1. Cài đặt ứng dụng trên môi trường mới
  2. Cấu hình cơ sở dữ liệu và các thông số khác
  3. Khởi động ứng dụng
- **Kết quả mong đợi**: 
  - Ứng dụng được cài đặt thành công
  - Không có lỗi khi khởi động

### 9.2. Kiểm tra triển khai
- **Mục đích**: Kiểm tra quy trình triển khai ứng dụng
- **Các bước**:
  1. Triển khai ứng dụng lên môi trường sản xuất
  2. Kiểm tra các chức năng chính
  3. Kiểm tra hiệu năng trên môi trường sản xuất
- **Kết quả mong đợi**: 
  - Ứng dụng hoạt động bình thường trên môi trường sản xuất
  - Hiệu năng đáp ứng yêu cầu
