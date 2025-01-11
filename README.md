<p align="center">
  <a href="https://www.uit.edu.vn/" title="Trường Đại học Công nghệ Thông tin" style="border: 5;">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="Trường Đại học Công nghệ Thông tin | University of Information Technology">
  </a>
</p>

<h1 align="center"><b>XỬ LÝ ẢNH VÀ ỨNG DỤNG</b></h1>


# Giới thiệu
* **Tên môn học:** Xử lý ảnh và ứng dụng - CS406.P11
* **Năm học:** HK1 (2024 - 2025)
* **Giảng viên**: Cáp Phạm Đình Thăng
* **Sinh viên thực hiện:**
  
  | STT | MSSV     | Họ và Tên        | Email                   |
  |-----|----------|------------------|-------------------------|
  |1    | 22520019 | Nguyễn Ấn | 22520019@gm.uit.edu.vn |
  |2    | 22520083 | Trịnh Thị Lan Anh  | 22520083@gm.uit.edu.vn |
  |3    | 22520375 | Vương Dương Thái Hà | 22520375@gm.uit.edu.vn |

# Thông tin đồ án
* **Đề tài:** Detect & Decode QRCode 
* **Giới thiệu chung:**  Mã QR (Quick Response) là một trong những loại mã ma trận hai chiều (2D) phổ biến nhất hiện nay, được sử dụng rộng rãi trong nhiều lĩnh vực. So với mã vạch một chiều (1D), mã ma trận hai chiều có thể mã hóa một lượng dữ liệu đáng kể hơn trong cùng một diện tích. Chúng tôi đã so sánh các thuật toán có khả năng xác định vị trí nhiều mã QR trong một hình ảnh bằng cách sử dụng các mẫu tìm kiếm đặc trưng, thường có mặt ở ba góc của mã QR. Cuối cùng, chúng tôi giới thiệu một phương pháp mới để nhận diện biến dạng phối cảnh bằng cách phân tích hướng của các cạnh ngang và dọc, đồng thời tối ưu hóa độ lệch chuẩn của các phép chiếu ngang và dọc của các cạnh này. Thuật toán này có hiệu quả tính toán cao, hoạt động tốt với hình ảnh có độ phân giải thấp và cũng phù hợp để xử lý trong thời gian thực.
* **Thông tin chi tiết:** [Report](Report.pdf)

* **Cài đặt thư viện** 
1. [Install Python 3.11.0](https://www.python.org/downloads/release/python-3110/)
2. Tạo Môi Trường Ảo Python
```bash
python -m venv myenv
```

3. Kích hoạt môi trường
Để kích hoạt môi trường ảo Python, bạn có thể sử dụng lệnh sau:
```bash
myenv\Scripts\activate
```
Nếu trong quá trình chạy lệnh mà bạn gặp lỗi, hãy kiểm tra chính sách thực thi bằng cách chạy lệnh sau:
```bash
Get-ExecutionPolicy
```
Nếu kết quả hiển thị là Restricted, hãy thực hiện các bước sau:
Mở PowerShell và chọn “Run as administrator”.
Chạy lệnh sau để thay đổi chính sách thực thi:
```powershell
Set-ExecutionPolicy RemoteSigned
```
Có thông báo như này thì chọn Y
```powershell
Execution Policy Change
The execution policy helps protect you from scripts that you do not trust. Changing the execution policy might expose
you to the security risks described in the about_Execution_Policies help topic at
https:/go.microsoft.com/fwlink/?LinkID=135170. Do you want to change the execution policy?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): 
```
Sau đó thử lại lệnh
```bash
myenv\Scripts\activate
```
4. Cài các thư viện cần thiết
Trong file requirements.txt đã có các thư viện cần thiết cho việc thực thi chương trình, chạy lệnh dưới sẽ cài đặt tất cả các thư viện
```
pip install -r requirements.txt
```

5. Chạy demo web
```
streamlit run app.py
```


## References

1. [Belussi, L.F.F., & Hirata, N.S.T. (2013). Fast component-based QR code detection in arbitrarily acquired images. Journal of Mathematical Imaging and Vision. doi:10.1007/s10851-013-0445-5](https://doi.org/10.1007/s10851-013-0445-5)
2. [Bodnár, P., & Nyúl, L.G. (2015). Improved QR code localization using boosted cascade of weak classifiers. Acta Cybernetica, 22:21–33. doi:10.14232/actacyb.22.1.2015.3](https://doi.org/10.14232/actacyb.22.1.2015.3)
3. [Bosch, A., Zisserman, A., & Munoz, X. (2007). Image classification using randomized visual code-books. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). URL: https://ieeexplore.ieee.org/document/4295202](https://ieeexplore.ieee.org/document/4295202)
4. [Bozek, P., Nikitin, Y., Bezak, P., Fedorko, G., & Fabian, M. (2015). Increasing the production system productivity using inertial navigation. Manufacturing Technology, 15:274–278.](https://doi.org/10.xxxxx/yyyy)
5. [Chou, T.-H., Ho, C.-S., & Kuo, Y.-F. (2015). QR code detection using convolutional neural networks. In Proceedings of the 2015 International Conference on Advanced Robotics and Intelligent Systems (ARIS), Taipei, Taiwan. URL: https://doi.org/10.1109/ARIS.2015.7414524](https://doi.org/10.1109/ARIS.2015.7414524)
6. [Dalal, N., & Triggs, B. (2005). Histograms of oriented gradients for human detection. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pages 886–893. URL: https://ieeexplore.ieee.org/document/1467360](https://ieeexplore.ieee.org/document/1467360)
7. [Frankovsky, P., Pastor, M., Dominik, L., Kicko, M., Trebuna, P., Hroncova, D., & Kelemen, M. (2018). Wheeled mobile robot in structured environment. In Proceedings of the 12th International Conference ELEKTRO, Mikulov, Czech Republic.](https://doi.org/10.xxxxx/yyyy)
8. [Gaur, P., & Tiwari, S. (2014). Recognition of 2D barcode images using edge detection and morphological operation. Int. J. Comput. Sci. Mob. Comput. IJCSMC, 3:1277–1282.](https://doi.org/10.xxxxx/yyyy)
9. [Hansen, D.K., Nasrollahi, K., Rasmussen, C.B., & Moeslund, T.B. (2017). Real-time barcode detection and classification using deep learning. IJCCI, 1:321–327.](https://doi.org/10.xxxxx/yyyy)
10. [Denso Wave Incorporated. What is a QR code? Accessed: 6 September 2018.](http://www.qrcode.com/en/about/)
11. [Denso Wave Incorporated. History of QR code. Accessed: 6 September 2018.](http://www.qrcode.com/en/history/)
12. [Karrach, L., Pivarciová, E., & Bozek, P. (2020). Identification of QR code perspective distortion based on edge directions and edge projections analysis. Journal of Imaging, 6(7):67. doi:10.3390/jimaging6070067](https://doi.org/10.3390/jimaging6070067)
13. [Kong, S. (2013). QR code image correction based on corner detection and convex hull algorithm. J. Multimed., 8:662–668. doi:10.4304/jm.8.6.662-668](https://doi.org/10.4304/jm.8.6.662-668)
14. [Kurniawan, W.C., Okumura, H., Muladi, & Handayani, A.N. (2019). An improvement on QR code limit angle detection using convolution neural network. In Proceedings of the 2019 International Conference on Electrical, Electronics and Information Engineering (ICEEIE). doi:10.1109/ICEEIE.2019.8884244](https://doi.org/10.1109/ICEEIE.2019.8884244)
15. [Li, S., Shang, J., Duan, Z., & Huang, J. (2018). Fast detection method of quick response code based on run-length coding. IET Image Processing, 12:546–551.](https://doi.org/10.xxxxx/yyyy)
16. [Lin, J.-A., & Fuh, C.-S. (2013). 2D barcode image decoding. Mathematical Problems in Engineering.](https://doi.org/10.xxxxx/yyyy)
17. [Liu, J., Yang, M., & Zhang, Z. (2009). SVM-based human detection and HOG feature selection. In Proceedings of the International Conference on Image Processing (ICIP). URL: https://ieeexplore.ieee.org/document/5373730](https://ieeexplore.ieee.org/document/5373730)
18. [Ren, S., He, K., Girshick, R., & Sun, J. (2015). Faster R-CNN: Towards real-time object detection with region proposal networks. In Proceedings of NeurIPS.](https://papers.nips.cc/paper/5638-faster-r-cnn-towards-real-time-object-detection-with-region-proposal-networks)
19. [Sun, A., Sun, Y., & Liu, C. (2007). The QR-code reorganization in illegible snapshots taken by mobile phones. In Proceedings of ICCSA 2007.](https://doi.org/10.xxxxx/yyyy)
20. [Ultralytics Team. YOLOv8: You only look once for real-time object detection, segmentation, and classification. Available on GitHub.](https://github.com/ultralytics/yolov8)
21. [Tribak, H., & Zaz, Y. (2017a). QR code patterns localization based on Hu invariant moments. IJACSA. doi:10.14569/IJACSA.2017.080305](https://doi.org/10.14569/IJACSA.2017.080305)
22. [Tribak, H., & Zaz, Y. (2017b). QR code recognition based on principal components analysis method. IJACSA. doi:10.14569/IJACSA.2017.080313](https://doi.org/10.14569/IJACSA.2017.080313)
23. [Zharkov, A., & Zagaynov, I. (2019). Universal barcode detector via semantic segmentation. In Proceedings of ICDAR 2019.](https://doi.org/10.xxxxx/yyyy)
