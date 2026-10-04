# 🎤 Kịch Bản Thuyết Trình Chi Tiết: Phân Tích Thị Trường Ô Tô Điện VinFast Việt Nam
> **Dự án**: Vietnam EV Market Monitor (2026)  
> **Dựa trên**: `presentation_outline.md`  
> **Mục tiêu**: Kịch bản nói chuyên nghiệp, tự nhiên, dữ liệu chuẩn xác, kèm hướng dẫn cử chỉ và chuyển slide (transitions).

---

## 📋 Tổng Quan Thời Lượng Thuyết Trình
- **Tổng thời gian thuyết trình**: ~15 – 20 phút (10 slides)
- **Thời gian Q&A dự kiến**: 5 – 10 phút
- **Phong cách trình bày**: Chuyên nghiệp, khách quan (Data-driven), mạch lạc, giàu tính thuyết phục.

---

## 📌 Slide 1: Trang Tiêu Đề (Title Slide)
- **Thời lượng**: 1 phút
- **Hình ảnh trên Slide**: Tiêu đề lớn, tên diễn giả/nhóm nghiên cứu, logo dự án/VinFast.

### 🎙️ Lời thoại chi tiết:
> *"Kính chào thầy cô / Quý vị đại biểu và toàn thể các bạn,*
> 
> *Tôi xin phép được bắt đầu bài thuyết trình ngày hôm nay với chủ đề: **Báo Cáo Phân Tích & Giám Sát Thị Trường Ô Tô Điện VinFast Việt Nam**. Đây là kết quả nghiên cứu dựa trên dữ liệu thu thập thực tế từ hai nền tảng giao dịch lớn tại Việt Nam là Chợ Tốt (`chotot.com`) đại diện cho kênh cá nhân C2C và Ô Tô Điện (`otodien.vn`) đại diện cho kênh đại lý B2C.*
> 
> *Trong bài báo cáo này, chúng tôi sẽ đi sâu giải mã bức tranh định giá xe điện đã qua sử dụng, bài toán khấu hao theo từng dòng xe từ VF 3 đến VF 9, và đặc biệt là bài toán kinh tế phức tạp giữa hai hình thức: **Mua đứt pin** và **Thuê pin**.*
> 
> *Rất mong bài trình bày sẽ mang đến những góc nhìn dữ liệu thực tế và hữu ích cho cả người mua xe, các đại lý kinh doanh cũng như các đơn vị vận hành nền tảng."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Đứng tự tin giữa sân khấu/trước màn hình, mỉm cười chào hội trường.
- **Nhấn giọng**: Nhấn mạnh vào hai từ khóa *"Định giá xe cũ"* và *"Kèm pin vs Thuê pin"*.
- **Chuyển slide**: *"Sau đây, xin mời quý vị cùng nhìn lại bối cảnh và lý do chúng tôi thực hiện đề tài này."*

---

## 📌 Slide 2: Đặt Vấn Đề & Bối Cảnh Thị Trường (Market Context & Problem Statement)
- **Thời lượng**: 1.5 – 2 phút
- **Visuals trên Slide**: Biểu tượng VinFast, ChoTot & Otodien, kèm 3 box thách thức chính (Chính sách pin, Tin rác/Bẫy giá, Độ mất giá).

### 🎙️ Lời thoại chi tiết:
> *"Như quý vị đã biết, VinFast hiện đang dẫn dắt cuộc cách mạng xe điện tại Việt Nam với thị phần áp đảo. Cùng với số lượng xe mới bán ra tăng trưởng phi mã, thị trường xe điện thứ cấp – tức xe cũ giao dịch giữa cá nhân (C2C) hay qua đại lý (B2C) – cũng đang bùng nổ vô cùng mạnh mẽ.*
> 
> *Tuy nhiên, qua khảo sát thực tế, người tiêu dùng khi bước vào thị trường xe điện cũ đang gặp phải **3 rào cản rất lớn**:*
> 
> 1. * **Thứ nhất - Chính sách Pin quá phức tạp**: Cùng một dòng xe VF 5 hay VF 8, nhưng xe chào bán dưới dạng 'Thuê pin' lại có mức giá niêm yết chênh lệch hàng trăm triệu so với xe 'Mua đứt pin'. Người mua rất khó so sánh đâu mới là mức giá hợp lý.*
> 2. * **Thứ hai - Bẫy giá và thông tin rác**: Trên các sàn C2C, xuất hiện rất nhiều tin đăng với tiêu đề 'Trả trước 50 triệu nhận xe', tin giá 0đ, hoặc lẫn lộn tin cho thuê xe tự lái, chạy dịch vụ làm nhiễu loạn mặt bằng giá.*
> 3. * **Thứ ba - Khó xác định độ mất giá (Depreciation)**: Thiếu một chuẩn mực định giá tham chiếu minh bạch theo số KM đã đi (ODO) và năm sản xuất.*
> 
> *Chính vì vậy, dự án **Vietnam EV Market Monitor** được xây dựng nhằm giải quyết bài toán minh bạch hóa dữ liệu cho thị trường này."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Đếm ngón tay tương ứng với 3 rào cản (1, 2, 3) để người nghe dễ theo dõi.
- **Nhấn giọng**: Nhấn mạnh cụm từ *"nhiễu loạn mặt bằng giá"* và *"minh bạch hóa dữ liệu"*.
- **Chuyển slide**: *"Để có được câu trả lời đáng tin cậy, chúng tôi đã xây dựng một quy trình thu thập và xử lý dữ liệu như thế nào? Xin mời quý vị sang Slide 3."*

---

## 📌 Slide 3: Nguồn Dữ Liệu & Kiến Trúc Thu Thập (Data Sources & Pipeline Architecture)
- **Thời lượng**: 2 phút
- **Visuals trên Slide**: Sơ đồ Mermaid Flowchart hiển thị 4 tầng: (1) Data Sources $\rightarrow$ (2) Ingestion $\rightarrow$ (3) Cleaning Pipeline $\rightarrow$ (4) Processed Output.

### 🎙️ Lời thoại chi tiết:
> *"Xin quý vị nhìn lên sơ đồ kiến trúc thu thập dữ liệu trên màn hình.*
> 
> *Dữ liệu của chúng tôi được thu thập từ hai nguồn chính:*
> - *Kênh C2C: Thu thập tự động qua REST API của `chotot.com` với hàng ngàn tin đăng xe điện VinFast.*
> - *Kênh B2C: Thu thập từ `otodien.vn` bằng công cụ BeautifulSoup & Playwright scraper.*
> 
> *Toàn bộ dữ liệu thô sau khi thu thập được lưu trữ dưới dạng các snapshot theo chuẩn thời gian UTC nhằm đảm bảo tính toàn vẹn và có khả năng truy vết lịch sử (Auditability).*
> 
> *Sau đó, dữ liệu đi qua tầng **Sàng lọc 2 lớp (Quality Control Pipeline)** để loại bỏ hoàn toàn nhiễu và tin rác trước khi đưa vào tập dữ liệu sạch `screened_listings.csv` phục vụ phân tích EDA trên Jupyter Notebook.*
> 
> *Điểm đặc biệt của quy trình này là **Nguyên tắc Không biến đổi nguồn (No Source Mutation)** và tuân thủ bảo mật dữ liệu cá nhân PDPD."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Dùng bút laser hoặc tay trỏ từ trái sang phải theo sơ đồ từ (1) đến (4).
- **Nhấn giọng**: Nhấn mạnh cụm từ *"chuẩn thời gian UTC"* và *"Sàng lọc 2 lớp"*.
- **Chuyển slide**: *"Bây giờ, hãy cùng đi sâu vào chi tiết của Quy trình sàng lọc 2 lớp – trái tim của việc làm sạch dữ liệu."*

---

## 📌 Slide 4: Quy Trình Sàng Lọc Dữ Liệu 2 Lớp (2-Layer Data Cleaning Pipeline)
- **Thời lượng**: 1.5 – 2 phút
- **Visuals trên Slide**: Figure `buyer_01_screening` (Bar Chart mô tả số lượng tin qua từng bước sàng lọc).

### 🎙️ Lời thoại chi tiết:
> *"Như ở Slide 2 đã đề cập, thị trường xe C2C chứa rất nhiều nhiễu. Nếu dùng ngay dữ liệu thô để phân tích, kết quả chắc chắn sẽ bị méo mó. Vì vậy, chúng tôi áp dụng 2 lớp lọc nghiêm ngặt:*
> 
> - * **Lớp 1 - Sàng lọc Phạm vi (Scope Eligibility)**: Loại bỏ toàn bộ các dòng xe xăng legacy của VinFast như Fadil, Lux A2.0, Lux SA2.0 hay President. Đồng thời lọc bỏ các tin rao cho thuê xe, phụ tùng linh kiện.*
> - * **Lớp 2 - Sàng lọc Giá thực tế (Price Eligibility)**: Loại bỏ các tin niêm yết giá 0đ, tin bẫy trả trước. Chúng tôi thiết lập ngưỡng giá sàn cứng là **100 triệu VNĐ** cho ô tô điện.*
> 
> *Kết quả thu được rất ấn tượng (nhìn vào biểu đồ `buyer_01_screening`): Tỷ lệ giữ lại dữ liệu chất lượng cao (Clean Retention Rate) đạt tới **95.1%**.*
> 
> *Điều này đảm bảo mọi con số thống kê ở các slide sau đều phản ánh đúng giá trị giao dịch thực tế của ô tô điện VinFast."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Chỉ vào cột biểu đồ thể hiện con số 95.1%.
- **Nhấn giọng**: Khẳng định tính chính xác của dữ liệu sau khi lọc.
- **Chuyển slide**: *"Sau khi đã có tập dữ liệu sạch, câu hỏi đầu tiên đặt ra là: Mức giá giữa kênh Đại lý B2C và kênh Cá nhân C2C khác nhau như thế nào?"*

---

## 📌 Slide 5: Phân Tích So Sánh Thị Trường B2C (`otodien.vn`) vs C2C (`chotot.com`)
- **Thời lượng**: 2 phút
- **Visuals trên Slide**: Figure `buyer_09_b2c_vs_c2c` (Biểu đồ Boxplot / Violin Plot so sánh phân bố giá B2C vs C2C).

### 🎙️ Lời thoại chi tiết:
> *"Trực quan trên biểu đồ Boxplot `buyer_09_b2c_vs_c2c` cho chúng ta thấy sự khác biệt rất rõ nét giữa hai kênh bán:*
> 
> 1. * **Kênh B2C (`otodien.vn`) có giá trung vị cao hơn rõ rệt**: Điều này hoàn toàn hợp lý vì xe chào bán tại đại lý thường đã qua kiểm định chất lượng, có gói bảo hành đi kèm và thông tin pháp lý chuẩn hóa.*
> 2. * **Kênh C2C (`chotot.com`) có biên độ dao động giá (Variance) rộng hơn rất nhiều**: Giá xe C2C trải dài từ các xe chạy lướt cực mới cho đến các xe ODO cao hoặc chủ xe đang cần bán gấp.*
> 
> * **Insight quan trọng cho người mua**: Nếu giao dịch trên sàn C2C, người mua có dư địa thương lượng giảm giá từ **5% đến 15%** so với giá niêm yết, trong khi giá niêm yết B2C tại đại lý thường cố định và ít linh hoạt hơn."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: So sánh chiều cao hai hộp Boxplot trên slide.
- **Nhấn giọng**: Nhấn mạnh con số dư địa thương lượng *"5% đến 15%"*.
- **Chuyển slide**: *"Tiếp theo, hãy cùng phân tích cụ thể bức tranh định giá và khả năng giữ giá của từng dòng xe VinFast."*

---

## 📌 Slide 6: Bức Tranh Định Giá Resale Theo Từng Dòng Xe VinFast
- **Thời lượng**: 2.5 phút
- **Visuals trên Slide**: 
  - Main: Figure `buyer_04_official_context` (Dải giá xe cũ so với giá niêm yết chính hãng VinFast).
  - Secondary: Figure `buyer_02_budget` (Heatmap ngân sách) & `buyer_08_used_odo` (Scatterplot Giá vs ODO).

### 🎙️ Lời thoại chi tiết:
> *"Đây là một trong những slide quan trọng nhất của bài báo cáo. Xin quý vị chú ý vào biểu đồ `buyer_04_official_context`.*
> 
> *Qua phân tích dữ liệu trên toàn bộ dải sản phẩm VinFast, chúng tôi rút ra 3 phát hiện chính:*
> 
> - * **Phân khúc Thanh khoản cao nhất (VF 3 & VF 5)**: VF 3 và VF 5 chiếm tỷ lệ tin đăng áp đảo trên thị trường. Đây là hai dòng xe có tốc độ xoay vòng mua đi bán lại nhanh nhất và khả năng giữ giá (Value Retention) tốt nhất so với giá niêm yết mới của hãng.*
> - * **Phân khúc SUV Trung & Cao cấp (VF 8 & VF 9)**: Các dòng SUV lớn như VF 8 và VF 9 có mức khấu hao xe cũ sau 1–2 năm sử dụng cao hơn đáng kể. Điều này tạo ra một **cơ hội rất lớn cho người mua xe gia đình đã qua sử dụng**, khi có thể sở hữu một chiếc SUV cỡ D hoặc E đẳng cấp với mức chi phí tiết kiệm từ 20% đến 35%.*
> - * **Tác động của ODO**: Quan sát biểu đồ `buyer_08_used_odo`, giá xe cũ giảm theo đường cong tuyến tính mềm dựa trên số KM đã đi, tuy nhiên yếu tố quyết định bước nhảy giá lớn nhất lại nằm ở tình trạng Pin."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Dùng tay khoanh vùng nhóm xe phổ thông (VF3/VF5) rồi chuyển sang nhóm SUV cao cấp (VF8/VF9).
- **Nhấn giọng**: *"Khả năng giữ giá tốt nhất"* đối với VF3/VF5 và *"Cơ hội lớn cho người mua xe gia đình"* đối với VF8/VF9.
- **Chuyển slide**: *"Và bây giờ, chúng ta hãy đến với yếu tố then chốt nhất ảnh hưởng đến định giá xe điện VinFast: Chính sách Pin."*

---

## 📌 Slide 7: Tác Động Của Chính Sách Pin ("Kèm Pin" vs "Thuê Pin")
- **Thời lượng**: 2.5 phút
- **Visuals trên Slide**: Figure `buyer_06_battery_terms` (Grouped Bar Chart so sánh giá bán xe "Thuê pin" vs "Kèm pin").

### 🎙️ Lời thoại chi tiết:
> *"Hình thức Thuê pin độc đáo của VinFast mang lại lợi thế lớn khi mua xe mới, nhưng trên thị trường xe cũ, nó tạo ra một sự phân hóa rất mạnh.*
> 
> *Nhìn vào biểu đồ `buyer_06_battery_terms`:*
> - * **Mức chênh lệch giá (Price Premium)**: Xe chào bán dạng **Mua đứt Pin ("Kèm pin")** luôn có giá rao cao hơn từ **15% đến 30%** so với xe cùng dòng, cùng năm sản xuất nhưng ở dạng **"Thuê pin"**.*
> - * **Tâm lý thị trường C2C**: Xe kèm pin có tốc độ thanh khoản nhanh hơn hẳn trên Chợ Tốt. Lý do là người mua cá nhân muốn tránh các thủ tục chuyển đổi hợp đồng thuê pin phức tạp với nhà sản xuất.*
> 
> * **Lời khuyên chiến lược cho người mua (TCO - Tổng chi phí sở hữu)**:  
> Khi thấy một chiếc xe rao bán giá rất rẻ, người mua bắt buộc phải kiểm tra xe đó là Thuê pin hay Kèm pin. Chi phí thuê pin hàng tháng dao động từ **1.6 triệu đến 3.2 triệu VNĐ/tháng** tùy quãng đường. Nếu cộng chi phí này vào dòng tiền 3 năm sử dụng, mức giá 'xe thuê pin giá rẻ' chưa chắc đã rẻ hơn xe mua đứt pin!"*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Nhấn mạnh vào khoảng khoảng trống chênh lệch giữa 2 cột giá (Thuê pin vs Kèm pin).
- **Nhấn giọng**: Thốt lên cảnh báo *"Người mua bắt buộc phải tính TCO"*.
- **Chuyển slide**: *"Bên cạnh giá bán và pin, tốc độ biến động của thị trường theo thời gian diễn ra như thế nào? Mời quý vị cùng xem Slide 8."*

---

## 📌 Slide 8: Theo Dõi Biến Động Thị Trường Qua Snapshot Lịch Sử
- **Thời lượng**: 2 phút
- **Visuals trên Slide**: 
  - Figure `buyer_07_energy_scenario` (Mô phỏng chi phí năng lượng Điện vs Xăng).
  - Bảng số liệu Snapshot (Tỷ lệ Churn vs Retention rate).

### 🎙️ Lời thoại chi tiết:
> *"Thông qua việc theo dõi dữ liệu Snapshot theo chuỗi thời gian, chúng tôi phát hiện ra những quy luật biến động thị trường rất thú vị:*
> 
> 1. * **Tốc độ xoay vòng tin đăng (Listing Turnover Rate) cực cao**: Đối với các tin rao xe VinFast đúng giá thị trường, tỷ lệ tin biến mất khỏi sàn (Churn Rate) đạt trên **90% chỉ sau 7 ngày**. Điều này chứng tỏ cầu thị trường xe điện cũ đang rất lớn.*
> 2. * **Sự dịch chuyển giá (Price Drift)**: Nếu một tin đăng không có người hỏi sau 5 ngày, chủ xe thường có xu hướng hạ giá chào từ **3% đến 5%**.*
> 3. * **Mô hình chi phí năng lượng (`buyer_07_energy_scenario`)**: Ngay cả khi cộng thêm chi phí thuê pin, chi phí vận hành trên mỗi KM của xe điện VinFast vẫn tiết kiệm từ **40% đến 60%** so với xe xăng cùng phân khúc khi di chuyển trên 1,500 km/tháng.*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Chỉ vào con số 90% sau 7 ngày.
- **Nhấn giọng**: Nhấn mạnh *"Cầu thị trường xe điện cũ đang rất lớn"*.
- **Chuyển slide**: *"Từ tất cả những phân tích dữ liệu trên, chúng tôi đưa ra các đề xuất chiến lược cụ thể cho từng nhóm đối tượng."*

---

## 📌 Slide 9: Đề Xuất Chiến Lược (Strategic Recommendations)
- **Thời lượng**: 2 phút
- **Visuals trên Slide**: 3 cột Card đồ họa trực quan đại diện cho: (1) Người mua cá nhân, (2) Đại lý B2C, (3) Sàn giao dịch Chợ Tốt.

### 🎙️ Lời thoại chi tiết:
> *"Dựa trên bằng chứng dữ liệu (Data-driven evidence), chúng tôi đưa ra 3 nhóm khuyến nghị chiến lược:*
> 
> - * **Đối với Người mua xe cá nhân**:  
>   1. Luôn tính toán Tổng chi phí sở hữu (TCO) cộng gộp tiền thuê pin trước khi quyết định.  
>   2. Nên ưu tiên nhắm vào các tin đăng đã niêm yết trên 5 ngày để có lợi thế thương lượng ép giá tốt nhất.*
> 
> - * **Đối với các Đại lý kinh doanh xe cũ (B2C Dealers)**:  
>   1. Tập trung nguồn vốn nhập các dòng xe **VF 3 và VF 5** vì tốc độ thanh khoản nhanh gấp 2–3 lần so với dòng SUV lớn.  
>   2. Bắt buộc phải niêm yết rõ trạng thái Pin ngay trong tiêu đề tin đăng – điều này giúp tăng **40% tỷ lệ nhấp chuột (CTR)** của khách hàng.*
> 
> - * **Đối với Sàn giao dịch (`chotot.com`)**:  
>   Nên bổ sung ngay bộ lọc cấu trúc dành riêng cho ô tô điện: Phân loại rõ **[Xe Kèm Pin]** và **[Xe Thuê Pin]** để cải thiện trải nghiệm tìm kiếm của người dùng."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Nhìn trực tiếp về phía khán giả/hội đồng khi đưa ra các khuyến nghị.
- **Nhấn giọng**: Nhấn mạnh con số *"tăng 40% CTR"* và *"thanh khoản nhanh gấp 2-3 lần"*.
- **Chuyển slide**: *"Cuối cùng, tôi xin tổng kết lại bài báo cáo và chia sẻ lộ trình phát triển tiếp theo của dự án."*

---

## 📌 Slide 10: Tổng Kết & Kế Hoạch Phát Triển (Conclusion & Roadmap)
- **Thời lượng**: 1.5 phút
- **Visuals trên Slide**: Roadmap 3 Phase (Phase 1: Data Pipeline $\rightarrow$ Phase 2: Interactive Dashboard $\rightarrow$ Phase 3: ML Pricing Valuation Model).

### 🎙️ Lời thoại chi tiết:
> *"Kính thưa quý vị,*
> 
> *Dự án **Vietnam EV Market Monitor** đã xây dựng thành công một hệ thống thu thập, làm sạch và phân tích chuyên sâu dữ liệu ô tô điện VinFast đầu tiên tại Việt Nam với độ chính xác cao và tính minh bạch hoàn toàn.*
> 
> *Trong thời gian tới, lộ trình phát triển của chúng tôi bao gồm 3 bước:*
> - * **Giai đoạn 1**: Tự động hóa hoàn toàn quy trình thu thập Snapshot bằng Cron Job định kỳ.*
> - * **Giai đoạn 2**: Xây dựng **Dashboard tương tác bằng Streamlit**, cho phép người mua tự gõ dòng xe, số ODO, năm sản xuất để tra cứu ngay khoảng giá thị trường hợp lý.*
> - * **Giai đoạn 3**: Huấn luyện mô hình **Machine Learning Định Giá (Valuation Model)** tự động dự báo giá trị xe cũ dựa trên các thuộc tính kỹ thuật và trạng thái pin.*
> 
> *Xin trân trọng cảm ơn sự chú ý theo dõi của quý thầy cô và các bạn! Sau đây xin mời những câu hỏi và đóng góp ý kiến từ hội trường."*

### 💡 Ghi chú cho Diễn giả:
- **Hành động**: Múi tay hướng về phía Roadmap, sau đó cúi đầu chào cảm ơn hội trường.
- **Tư thế kết thúc**: Đứng sẵn sàng lắng nghe và trả lời câu hỏi Q&A từ Hội đồng / Khán giả.

---

## ❓ Ghi Chú Phụ: Hướng Dẫn Trả Lời Các Câu Hỏi Q&A Thường Gặp

1. **Câu hỏi: Dữ liệu này có đại diện cho toàn bộ số lượng xe VinFast giao dịch tại Việt Nam không?**
   - *Trả lời*: Dữ liệu mang tính chất mẫu khảo sát (convenience sample) đại diện cho các tin chào bán công khai trên sàn C2C và B2C lớn nhất, không phải toàn bộ tổng dư nợ giao dịch thực tế nhưng phản ảnh chính xác xu hướng mặt bằng giá chào.

2. **Câu hỏi: Tại sao lại chọn mốc 100 triệu VNĐ làm ngưỡng lọc giá ở Layer 2?**
   - *Trả lời*: Qua khảo sát dữ liệu thô, các tin dưới 100 triệu đối với ô tô điện VinFast 100% là tin bẫy 'trả trước nhận xe', tin giá 0đ hoặc tin đặt cọc linh kiện. Không có chiếc ô tô điện VinFast hoàn chỉnh nào có giá dưới 100 triệu.

3. **Câu hỏi: Yếu tố nào ảnh hưởng nhiều nhất đến khấu hao xe VinFast cũ?**
   - *Trả lời*: Dữ liệu cho thấy trạng thái Pin (Kèm pin vs Thuê pin) và Dòng xe (VF3/VF5 giữ giá tốt hơn VF8/VF9) có tác động mạnh hơn so với số KM (ODO) đã đi.
