# Dashboard khai cuộc cờ vua

Ứng dụng cho bài tập lớn Trực quan hóa dữ liệu, dữ liệu Lichess Rated Blitz lịch sử 01–06/2015.

## Cấu trúc kho GitHub

```text
app.py
dashboard_core.py
requirements.txt
README.md
data/
  games_dashboard.csv.gz
  dataset_info.json
```

Đưa các file và thư mục đã giải nén lên gốc kho GitHub, không chỉ tải file ZIP lên. Chọn `app.py` là main file trên Streamlit Community Cloud. Chọn Python 3.11 để phù hợp bộ phiên bản thư viện này. Không đưa dữ liệu thô, thông tin đăng nhập, hay toàn bộ Google Drive lên kho dashboard.

Nếu chạy trên máy có Python: `pip install -r requirements.txt` rồi `streamlit run app.py`.

## Cách sử dụng

- Lọc tháng, nhóm Elo, màu quân dùng tính tỷ lệ điểm, số ván tối thiểu và chênh lệch Elo.
- Tổng quan: C1 và C3. Xu hướng: C2 và C7. So sánh hiệu quả: C4, C5, C6.
- Tab dữ liệu hiển thị tối đa 1.000 dòng nhưng tải CSV toàn bộ phạm vi lọc, gồm cả chưa nhận diện.
- C7 cần ít nhất 4 tháng; tỷ lệ thiếu mẫu được để trống, không nối qua khoảng trống.
- Chọn vài khai cuộc trên C2 không làm thay đổi mẫu số tỷ trọng theo tháng.
- C6 loại nhãn đúng bằng tên nhóm khi so sánh biến thể, dùng một nhóm Elo cố định.

## Đối chiếu bộ dữ liệu đầu tiên

Khi không giới hạn bộ lọc, dự kiến 236.690 ván, 233.346 nhận diện được và 3.344 chưa nhận diện. Nếu cập nhật nguồn, số liệu có thể thay đổi và cần ghi nhận phiên bản mới. Số nhóm khai cuộc phải tính từ tập thực tế, không gán bằng số nhóm của toàn bộ danh mục.

## Kiểm tra và ảnh báo cáo

1. Kiểm tra số ván mặc định so với dữ liệu Colab.
2. Chỉ tháng 01/2015: đối chiếu 32.549 ván và 32.112 nhận diện (với bộ đầu tiên).
3. Bỏ tất cả nhóm Elo: thông báo không có dữ liệu, ứng dụng không lỗi.
4. Chuyển Trắng/Đen: hai tỷ lệ điểm cộng thành 100%; cơ cấu thắng–hòa–thua không thay đổi.
5. Kiểm tra ô thiếu mẫu và CSV tải về.

Ảnh 23: Tổng quan mặc định. Ảnh 24: Xu hướng với chú giải. Ảnh 25: So sánh hiệu quả (có thể 25a–25c). Ảnh 26: Dữ liệu và phương pháp. Ảnh 27: Một phạm vi bộ lọc khác để minh họa thay đổi số ván. Chụp màn hình giao diện; xuất PNG của Plotly nếu chỉ cần hình biểu đồ.

## Cập nhật

Chạy pipeline dữ liệu ở Colab trước, sau đó chạy lại notebook đóng gói để cập nhật `data/games_dashboard.csv.gz` và `dataset_info.json`. Cập nhật hai file trên GitHub, ứng dụng nạp lại dữ liệu mới khi chạy. Nút đọc lại dữ liệu chỉ làm mới file đã cung cấp. Không có lịch tự tải nguồn.

## Giới hạn

Nhận diện theo vị trí khớp sau cùng trong 36 ply đầu. Dùng cùng danh mục qua các tháng. Độ bao phủ không phải độ chính xác; nhãn tổng quát không bao gồm tự động mọi nhánh con được gán nhãn khác. Phân tích mẫu lịch sử, không chứng minh quan hệ nhân quả hay khai cuộc tốt nhất. Ngưỡng mẫu chỉ phục vụ trình bày.

Nguồn: https://database.lichess.org/ và https://github.com/lichess-org/chess-openings

Dữ liệu thô, bộ dữ liệu sạch đầy đủ, notebook và báo cáo nằm trong thư mục dự án chính để nộp. ZIP dashboard chỉ là một thành phần của bài nộp.
