# Quy trình sửa lỗi (Fix Bug Workflow)

> Đây là bản dịch tiếng Việt để đọc và tham khảo. File `fix-bug.md` tiếng Anh vẫn là bản hướng dẫn chính thức cho Devkit. Giữ nguyên các tên vai trò và trạng thái kỹ thuật để dễ đối chiếu.

## Mục tiêu

Kiểm tra xem lỗi được báo cáo còn tồn tại hay không và hệ thống có đang hoạt động đúng như mong đợi không. **Không sửa code nếu không có lý do rõ ràng.** Một nhiệm vụ có thể kết thúc bằng việc sửa lỗi mới, xác nhận lỗi đã được sửa trước đó, không cần thay đổi gì, hoặc báo cáo những điều chưa thể xác minh.

## Vai trò

- **Orchestrator (Điều phối):** Quản lý nhiệm vụ, xem xét bằng chứng, quyết định bước tiếp theo và báo cáo kết quả. Không sửa code ứng dụng.
- **Tester (Kiểm thử):** Thử tái hiện lỗi và kiểm tra hành vi thực tế. Không sửa code ứng dụng.
- **Developer (Phát triển):** Tìm nguyên nhân và thực hiện những thay đổi code cần thiết.
- **Reviewer (Đánh giá):** Kiểm tra bản thay đổi code cuối cùng để tìm lỗi và rủi ro. Không sửa code ứng dụng.

Bỏ qua Developer và bước review code nếu không cần thay đổi code. Tuân theo `agents/orchestrator.md` về cách giao việc giữa agents và quyền hạn. Chỉ dùng subagents thật thông qua adapter của nền tảng; không được nói rằng một agent đã chạy nếu thực tế chưa chạy.

## 1. Hiểu lỗi được báo cáo — Orchestrator

Ghi lại:

- **Expected (Hành vi mong đợi):** Điều gì phải xảy ra theo yêu cầu hoặc quy tắc sản phẩm đã thống nhất, không chỉ dựa vào cách code hiện tại hoạt động.
- **Reported (Lỗi được báo cáo):** Điều gì xảy ra sai, cách lỗi xuất hiện, tần suất và mức độ ảnh hưởng.
- **Conditions (Điều kiện):** Phiên bản ứng dụng và code, môi trường, tài khoản, dữ liệu, cài đặt và nền tảng.
- **Key check (Kiểm tra then chốt):** Kết quả nào cho thấy lỗi đang xảy ra, hoặc cho thấy hành vi đã đúng.
- **Success check (Tiêu chí xác nhận):** Cần kiểm tra những gì và có bằng chứng nào thì mới được kết luận.

Chuyển báo cáo lỗi và những bằng chứng đã có cho Tester. Khi cần kiểm tra logs, lịch sử code hoặc pull requests, giao việc đó cho Tester hoặc Developer. Chỉ hỏi người dùng khi còn thiếu một quyết định về sản phẩm hoặc quyền truy cập bắt buộc.

## 2. Thử tái hiện lỗi — Tester

1. Thiết lập điều kiện gần giống báo cáo nhất có thể. Ghi lại mọi khác biệt.
2. Thực hiện các bước được báo cáo trên UI, API, CLI hoặc service đang chạy. Lưu các bước thực hiện, kết quả và logs hoặc ảnh chụp hữu ích.
3. Nếu lỗi không xuất hiện, kiểm tra xem hệ thống đang chạy có đáp ứng **Expected** trong những điều kiện liên quan hay không. Chỉ có unit tests pass hoặc đọc source code là chưa đủ.
4. Kiểm tra logs, các thay đổi trước đây, pull requests đang mở, dữ liệu, cài đặt, thời điểm xảy ra lỗi và khác biệt môi trường để tìm manh mối hoặc dấu hiệu lỗi vẫn còn xuất hiện.

**Không đặt số lần thử cố định.** Thử tiếp khi phép kiểm tra mới có thể trả lời một câu hỏi hữu ích hoặc kiểm chứng một nguyên nhân khả nghi mới. Tuân thủ giới hạn thời gian, chi phí và công cụ được cho phép. Ghi lại mỗi lần thử đã cho thấy điều gì. Không lặp lại một phép thử nếu không có lý do, trừ khi đang đo một lỗi chỉ thỉnh thoảng mới xảy ra.

**Dừng** khi bằng chứng đã trả lời được câu hỏi, không còn phép thử hữu ích, đã hết ngân sách, không thể sử dụng môi trường cần thiết hoặc phải xin thêm quyền. Không được thử mãi không dừng.

Trả về `REPRODUCED`, `NOT_REPRODUCED` hoặc `BLOCKED`, kèm điều kiện, bằng chứng và những điều chưa kiểm tra được. Đây là **kết quả quan sát của Tester**, chưa phải kết quả cuối cùng của nhiệm vụ.

## 3. Quyết định có cần sửa code hay không — Orchestrator

Áp dụng trường hợp đầu tiên có đủ bằng chứng hỗ trợ:

| Tình huống | Cách xử lý |
| --- | --- |
| Một pull request hoặc commit trước đây có thể đã sửa lỗi | **Kiểm tra bản sửa có sẵn** trước. Chưa tạo thêm bản sửa khác. |
| Đã tái hiện được lỗi | Giao Developer điều tra và đề xuất danh sách file cần sửa. Orchestrator phê duyệt phạm vi trước khi sửa code. Tôn trọng người đang chịu trách nhiệm sửa lỗi, nếu có. |
| Không tái hiện được lỗi; **Expected** được xác nhận trong điều kiện liên quan; không còn dấu hiệu lỗi | Kết thúc với `COMPLETED / NO_CHANGE_NEEDED`. Nêu rõ đã kiểm tra những gì. Không khẳng định rằng lỗi chưa từng tồn tại. |
| Không tái hiện được lỗi nhưng còn thiếu điều kiện quan trọng hoặc vẫn có dấu hiệu lỗi | Thực hiện một phép kiểm tra hữu ích khác nếu có thể. Nếu không, kết thúc với `BLOCKED / INCONCLUSIVE`. |
| Thiếu môi trường, công cụ hoặc quyền truy cập cần thiết | Thử khắc phục an toàn trong phạm vi được phép. Nếu không được, kết thúc với `BLOCKED / ENVIRONMENT_BLOCKED`. |
| Hành vi mong đợi cần quyết định về sản phẩm | Kết thúc với `NEEDS_HUMAN / DECISION_REQUIRED` và đưa ra một câu hỏi rõ ràng. |

Một vài lần kiểm tra thành công không xóa bỏ được bằng chứng cho thấy lỗi thực sự đang xảy ra. Không bao giờ yêu cầu Developer sửa code chỉ dựa trên suy đoán.

### Kiểm tra bản sửa có sẵn — Tester

1. Xác định pull request hoặc commit chứa bản sửa và các phiên bản code **trước** và **sau** thay đổi đó.
2. Nếu có thể, chạy cùng một phép kiểm tra trong cùng điều kiện trên cả hai phiên bản. Kiểm tra rằng lỗi xuất hiện ở phiên bản trước và hành vi đúng xuất hiện ở phiên bản sau.
3. Chỉ báo `ALREADY_FIXED_VERIFIED` khi bằng chứng trước và sau đủ để xác nhận. Sau đó Orchestrator quyết định có kết thúc với `COMPLETED / ALREADY_FIXED` hay không. Không sửa bản vá có sẵn hoặc mở pull request khác để cạnh tranh với nó.
4. Nếu cả hai phiên bản vẫn lỗi, báo cáo `DEFECT_PRESENT` kèm bằng chứng. Không tự ý tiếp quản phần việc đã có người khác phụ trách.
5. Nếu không thể kiểm tra phiên bản cũ hoặc không thấy lỗi ở phiên bản cũ, báo `INCONCLUSIVE` đối với bản sửa cũ và cung cấp bằng chứng hiện tại. Orchestrator quyết định kết quả cuối là `NO_CHANGE_NEEDED` hay `INCONCLUSIVE`.

Chỉ có commit message, trạng thái ticket hoặc một bài test pass chưa đủ để chứng minh bản sửa cũ đã xử lý lỗi.

## 4. Điều tra, phê duyệt phạm vi và sửa lỗi — Developer và Orchestrator

**Trước tiên, điều tra — Developer (chưa sửa code).** Orchestrator chuyển báo cáo lỗi, bằng chứng, tiêu chí thành công và những giới hạn hoặc đường dẫn bị cấm đã biết. Developer được đọc các file khác để tìm nguyên nhân nhưng chưa được sửa code.

- Tìm nguyên nhân gây lỗi, không chỉ xử lý triệu chứng. Không đề xuất cách xử lý dựa trên suy đoán.
- Đề xuất danh sách file cần sửa. Giải thích lý do cần sửa từng file và cách kiểm chứng bản sửa.
- Nếu bằng chứng không cho thấy cần thay đổi code, báo cáo kết quả đó. Không tạo bản vá cho có.

**Tiếp theo, phê duyệt phạm vi — Orchestrator.** Đối chiếu danh sách Developer đề xuất với quyền người dùng đã cấp và quy tắc repository. Phê duyệt những file Developer được sửa hoặc yêu cầu Developer giải thích thêm nếu chưa rõ. Orchestrator không tự lựa chọn giải pháp kỹ thuật. Chỉ hỏi người dùng nếu thay đổi cần quyền vượt quá giới hạn được phép.

**Cuối cùng, thực hiện bản sửa — Developer.** Chỉ sửa code sau khi Orchestrator đã phê duyệt phạm vi và chỉ sửa trong phạm vi đó.

- Chỉ thực hiện thay đổi nhỏ nhất cần thiết. Khi khả thi, thêm một test thất bại trước khi sửa và pass sau khi sửa; nếu không thực hiện được, giải thích lý do.
- Nếu cần sửa thêm file khác, giải thích lý do và đề xuất mở rộng phạm vi **trước khi sửa file đó**.
- Không thay đổi những file không liên quan. Báo cáo các đường dẫn đã thay đổi, phiên bản code, những test thực sự đã chạy và rủi ro đã biết.

## 5. Kiểm tra kết quả — Tester

Kiểm tra độc lập trên **phiên bản code mới nhất**:

- Thử lại các bước gây lỗi ban đầu và hành vi mong đợi trên hệ thống đang chạy. Nếu các bước cũ không thể xác nhận bản sửa có hiệu quả hay không, dùng một cách kiểm tra hành vi rõ ràng khác.
- Chạy các bài test liên quan và kiểm tra những hành vi gần đó có thể bị ảnh hưởng.
- Ghi lại phiên bản code, môi trường, lệnh hoặc các bước thực hiện, kết quả và bằng chứng.
- Trả về `PASS`, `FAIL` hoặc `BLOCKED`. Chỉ dùng `PASS` khi có bằng chứng phù hợp về hành vi thực tế. CI xanh, đọc code hoặc lời khẳng định của Developer đều chưa đủ.
- Nếu không thể xác định bản sửa có hoạt động hay không, trả về `BLOCKED` với lý do `INCONCLUSIVE`.

## 6. Review bản thay đổi code — Reviewer

Sau khi Tester trả về `PASS`, review **đúng bản thay đổi mới nhất đã được kiểm tra**. Xem xét nguyên nhân lỗi, tính đúng đắn, nguy cơ tạo lỗi mới, rủi ro bảo mật, phạm vi thay đổi và chất lượng test. Với mỗi vấn đề phát hiện, nêu vị trí trong file và lý do cụ thể.

Không cần review code nếu không có code nào thay đổi. Orchestrator có thể yêu cầu một lượt kiểm tra độc lập, chỉ đọc, nếu đang thiếu bằng chứng cụ thể.

## 7. Xử lý lỗi phát sinh và dừng — Orchestrator

- **Tester trả `FAIL`:** Chuyển bằng chứng thất bại cho Developer, sau đó kiểm tra lại code đã cập nhật.
- **Reviewer phát hiện vấn đề nghiêm trọng:** Chuyển phát hiện đó cho Developer, rồi lặp lại các bài test và bước review bị ảnh hưởng.
- **Công cụ hoặc môi trường lỗi:** Thử khắc phục an toàn. Không được đánh dấu `PASS` cho bài test chưa chạy.
- Cho phép tối đa **hai vòng sửa code sau bản sửa đầu tiên**. Số lần thử tái hiện lỗi **không bị giới hạn cố định**.
- Khi code thay đổi sau bước kiểm thử hoặc review, chạy lại các kiểm tra đã không còn hợp lệ vì thay đổi đó.
- Nếu test bắt buộc hoặc review vẫn thất bại khi phải dừng sửa code, dùng `BLOCKED / CHECKS_FAILED`. Không được gọi một thất bại đã được chứng minh là `INCONCLUSIVE`.
- Dừng khi kết quả đã có đủ bằng chứng, không còn phép thử hữu ích, hết ngân sách hoặc cần thêm quyền. Không được hạ tiêu chuẩn thành công chỉ để kết thúc nhiệm vụ.

## Kết quả cuối cùng — Orchestrator

Chọn **một** kết quả:

| Kết quả | Ý nghĩa |
| --- | --- |
| `COMPLETED / FIXED` | Bản sửa mới nhất đã vượt qua kiểm tra hành vi và review code độc lập. |
| `COMPLETED / ALREADY_FIXED` | Xác nhận một bản sửa trước đó bằng bằng chứng trước và sau. |
| `COMPLETED / NO_CHANGE_NEEDED` | Hành vi hiện tại đáp ứng **Expected** trong điều kiện liên quan và không còn dấu hiệu lỗi chưa được giải quyết. |
| `BLOCKED / CHECKS_FAILED` | Test bắt buộc hoặc review code vẫn thất bại sau khi dừng các vòng sửa. |
| `BLOCKED / INCONCLUSIVE` | Không đủ bằng chứng để kết luận rằng lỗi đã được sửa hoặc không cần thay đổi. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | Thiếu môi trường, công cụ hoặc quyền truy cập cần thiết. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | Cần quyết định về sản phẩm hoặc quyền truy cập mới từ con người. |

Báo cáo hành vi mong đợi và lỗi đã được phản ánh; các bước đã kiểm tra, phiên bản code được kiểm tra, kết quả và bằng chứng; nguyên nhân đã tìm ra hoặc điều chưa biết; các thay đổi code (**hoặc không có thay đổi**); kết quả của Tester và Reviewer; rủi ro còn lại; và đường dẫn pull request **chỉ khi pull request thật sự tồn tại**.

**An toàn:** Tester và Reviewer không sửa code ứng dụng. Developer chỉ làm việc trong phạm vi được phép. Merge, deploy, xóa dữ liệu quan trọng hoặc các thao tác khó hoàn tác khác cần được phê duyệt theo quy định và có quyền từ nền tảng. Không được sửa code theo suy đoán hoặc tạo pull request không cần thiết.
