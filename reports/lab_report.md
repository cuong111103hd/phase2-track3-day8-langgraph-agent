# Báo cáo Lab Ngày 08 - Hệ thống Điều phối Agent với LangGraph

## 1. Nhóm / Sinh viên
- **Họ và tên**: Cuong
- **Mã nguồn**: phase2-track3-day8-langgraph-agent
- **Ngày hoàn thành**: 11/05/2026

## 2. Kiến trúc hệ thống (Architecture)
Hệ thống được thiết kế theo mô hình Directed Acyclic Graph (DAG) phức tạp, cho phép xử lý đa luồng và tương tác người dùng linh hoạt:
- **Phân luồng thông minh**: Sử dụng node `classify` để định tuyến dựa trên từ khóa ưu tiên (RISKY > TOOL > MISSING_INFO...).
- **Xử lý song song (Parallel Fan-out)**: Cơ chế `Send()` cho phép kích hoạt đồng thời `shipping_tool` và `inventory_tool` cho các truy vấn phức tạp, giúp giảm độ trễ.
- **Vòng lặp thử lại (Retry Loop)**: Kết hợp giữa `evaluate` và `retry` để tự động xử lý các lỗi tạm thời (transient errors) từ các công cụ.
- **Can thiệp của con người (HITL)**: Sử dụng `interrupt()` để tạm dừng hệ thống tại node `approval` cho các hành động nhạy cảm.

## 3. Cấu trúc trạng thái (State Schema)
Chúng tôi sử dụng `TypedDict` với các hàm `reducer` chuyên biệt:
- `messages`: Sử dụng `add` để lưu vết toàn bộ nhật ký hệ thống và tương tác.
- `tool_results`: Sử dụng `add` để hợp nhất kết quả từ các nhánh chạy song song mà không làm mất dữ liệu.
- `human_feedback`: Lưu trữ ý kiến phản hồi từ người giám sát trong quá trình Time Travel.
- `attempt`: Theo dõi số lần thử lại để ngăn chặn vòng lặp vô hạn.

## 4. Kết quả kịch bản (Scenario Results)
Dựa trên kết quả thực thi thực tế:
- **Tổng số kịch bản**: 15 (8 công khai + 7 ẩn).
- **Tỷ lệ thành công**: 100%.
- **Số nút trung bình đã đi qua**: 7.40.
- **Tổng số lần thử lại (Retry)**: 5.
- **Tổng số lần can thiệp (Interrupt)**: 5.

## 5. Phân tích lỗi (Failure Analysis)
Hệ thống đã được thiết kế để đối phó với 2 tình huống lỗi chính:
1. **Lỗi công cụ tạm thời**: Khi một công cụ trả về "ERROR", node `evaluate` sẽ chuyển hướng sang `retry`. Nếu vượt quá số lần cho phép, hệ thống sẽ chuyển vào `dead_letter` để lưu vết thủ công.
2. **Hành động rủi ro cao**: Mọi hành động liên quan đến xóa hoặc hoàn tiền đều bị chặn bởi node `approval`. Nếu người dùng không phê duyệt, Agent sẽ yêu cầu làm rõ (clarify) thay vì thực thi sai.

## 6. Tính bền bỉ và Phục hồi (Persistence / Recovery)
- **Cơ sở dữ liệu**: Sử dụng `SqliteSaver` để lưu trữ lịch sử trạng thái (checkpoints).
- **Time Travel**: Đã triển khai tính năng cho phép quay ngược trạng thái, sửa đổi đề xuất của Agent (ví dụ: sửa số tiền hoàn lại) và tiếp tục thực thi từ điểm đó. Điều này được minh chứng qua script `demo_hitl_edit.py`.

## 7. Các phần mở rộng (Extension Work)
- **Parallel Fan-out/Fan-in**: Đã triển khai thành công việc chạy nhiều công cụ cùng lúc và hợp nhất kết quả.
- **PII Scrubbing**: Tự động nhận diện và thay thế Email trong câu hỏi của khách hàng để bảo mật.
- **Sơ đồ đồ họa**: Tự động xuất sơ đồ Mermaid chi tiết tại `graph_diagram.md`.

## 8. Kế hoạch cải thiện (Improvement Plan)
Nếu có thêm thời gian, tôi sẽ ưu tiên:
1. **Thay thế Heuristic bằng LLM**: Sử dụng LLM để phân loại ý định và đánh giá kết quả (LLM-as-a-judge) thay vì dùng từ khóa.
2. **Tích hợp giao diện Dashboard**: Xây dựng một Dashboard để người vận hành có thể phê duyệt hoặc sửa đổi trạng thái một cách trực quan hơn thay vì qua dòng lệnh.
