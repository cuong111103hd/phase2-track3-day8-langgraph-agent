# Báo cáo Lab Ngày 08 - Hệ thống Điều phối Agent với LangGraph

## 1. Nhóm / Sinh viên
- **Họ và tên**: Nguyễn Đức Cường
- **Mã nguồn**: phase2-track3-day8-langgraph-agent
- **Ngày hoàn thành**: 11/05/2026

## 2. Tóm tắt chỉ số (Metrics Summary)
- **Tổng số kịch bản**: 23 (8 công khai + 15 ẩn)
- **Tỷ lệ thành công**: 100.00%
- **Số nút trung bình**: 7.40
- **Tổng số lần thử lại (Retries)**: 8
- **Tổng số lần can thiệp (Interrupts)**: 7

## 3. Chi tiết kịch bản công khai (Public Scenarios)
| Scenario | Success | Expected | Actual | Nodes | Retries |
|---|---|---|---|---:|---:|
| S01_simple | ✅ | simple | simple | 4 | 0 |
| S02_tool | ✅ | tool | tool | 10 | 0 |
| S03_missing | ✅ | missing_info | missing_info | 4 | 0 |
| S04_risky | ✅ | risky | risky | 8 | 0 |
| S05_error | ✅ | error | error | 10 | 2 |
| S06_delete | ✅ | risky | risky | 6 | 0 |
| S07_dead_letter | ✅ | error | error | 5 | 1 |
| S08_multi | ✅ | tool | tool | 11 | 0 |

## 4. Chi tiết kịch bản ẩn (Hidden Scenarios)
| Scenario | Success | Expected | Actual | Nodes | Retries |
|---|---|---|---|---:|---:|
| G01_simple | ✅ | simple | simple | 4 | 0 |
| G02_simple2 | ✅ | simple | simple | 4 | 0 |
| G03_tool | ✅ | tool | tool | 10 | 0 |
| G04_tool2 | ✅ | tool | tool | 10 | 0 |
| G05_tool3 | ✅ | tool | tool | 10 | 0 |
| G06_missing | ✅ | missing_info | missing_info | 4 | 0 |
| G07_missing2 | ✅ | missing_info | missing_info | 4 | 0 |
| G08_risky | ✅ | risky | risky | 8 | 0 |
| G09_risky2 | ✅ | risky | risky | 8 | 0 |
| G10_risky3 | ✅ | risky | risky | 8 | 0 |
| G11_risky4 | ✅ | risky | risky | 8 | 0 |
| G12_error | ✅ | error | error | 10 | 2 |
| G13_error2 | ✅ | error | error | 10 | 2 |
| G14_dead | ✅ | error | error | 5 | 1 |
| G15_mixed | ✅ | risky | risky | 8 | 0 |

## 5. Kiến trúc hệ thống (Architecture)
Hệ thống được thiết kế để xử lý linh hoạt các tình huống thực tế:
- **Phân luồng thông minh**: Định tuyến dựa trên từ khóa ưu tiên (RISKY > TOOL...).
- **Parallel Fan-out**: Sử dụng `Send()` để thực thi đồng thời `shipping_tool` và `inventory_tool`.
- **HITL**: Sử dụng `interrupt()` tại node `approval` để tạm dừng cho con người kiểm duyệt.

## 6. Tính bền bỉ và Phục hồi (Persistence / Recovery)
- **Cơ sở dữ liệu**: Sử dụng `SqliteSaver` (checkpoints.db).
- **Time Travel**: Cho phép khôi phục trạng thái, chỉnh sửa phản hồi và chạy tiếp qua `update_state`.

## 7. Các phần mở rộng (Extension Work)
- **Parallel Fan-out/Fan-in**: Đã triển khai thành công mô hình map-reduce.
- **PII Scrubbing**: Tự động xóa Email khỏi câu truy vấn của người dùng.
- **Sơ đồ đồ họa**: Có tại `graph_diagram.md`.

## 8. Kế hoạch cải thiện (Improvement Plan)
- Ưu tiên sử dụng LLM để phân loại ý định thay vì dùng từ khóa (Heuristic).
- Xây dựng giao diện Web (Streamlit) cho phần phê duyệt HITL.
