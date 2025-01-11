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

[^1]: Diederik P. Kingma and Jimmy Ba, *Adam: A method for stochastic optimization*. arXiv preprint [arXiv:1412.6980](https://arxiv.org/abs/1412.6980), 2014.
[^2]: Dongruo Zhou, Jinghui Chen, Yuan Cao, Yiqi Tang, Ziyan Yang, and Quanquan Gu, *On the convergence of adaptive gradient methods for nonconvex optimization*. arXiv preprint [arXiv:1808.05671](https://arxiv.org/abs/1808.05671), 2018.
[^3]: Zhen Zhang, Min Li, Wei Xu, and Yu Wang, *Adopt: Modified adam can converge with any β2 with the optimal rate*. arXiv preprint [arXiv:2411.02853v3](https://arxiv.org/abs/2411.02853), 2024.

[^1]: L.F.F. Belussi and N.S.T. Hirata. Fast component-based qr code detection in arbi-trarily acquired images. Journal of Mathematical Imaging and Vision, 2013. doi: 10.1007/s10851-013-0445-5.
[^2]: P. Bodnár and L.G. Nyúl. Improved qr code localization using boosted cascade of weak classifiers. Acta Cybernetica, 22:21–33, 2015. doi: 10.14232/actacyb.22.1.2015.3.
[^3]: A. Bosch, A. Zisserman, and X. Munoz. Image classification using randomized visual code-books. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2007. URL https://ieeexplore.ieee.org/document/4295202.
[^4]: P. Boˇzek, Y. Nikitin, P. Bezák, G. Fedorko, and M. Fabian. Increasing the production system
productivity using inertial navigation. Manufacturing Technology, 15:274–278, 2015.
[^5]: T.-H. Chou, C.-S. Ho, and Y.-F. Kuo. Qr code detection using convolutional neural networks.
In Proceedings of the 2015 International Conference on Advanced Robotics and Intelligent
Systems (ARIS), pages 1–5, Taipei, Taiwan, 2015. URL https://doi.org/10.1109/
ARIS.2015.7414524.
[^6]: N. Dalal and B. Triggs. Histograms of oriented gradients for human detection. In Proceedings
of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), pages
886–893, 2005. URL https://ieeexplore.ieee.org/document/1467360.
[^7]: P. Frankovsky, M. Pastor, L. Dominik, M. Kicko, P. Trebuna, D. Hroncova, and M. Kelemen.
Wheeled mobile robot in structured environment. In Proceedings of the 12th International
Conference ELEKTRO, Mikulov, Czech Republic, May 2018. 21–23 May 2018.
[^8]: P. Gaur and S. Tiwari. Recognition of 2d barcode images using edge detection and morpho-
logical operation. Int. J. Comput. Sci. Mob. Comput. IJCSMC, 3:1277–1282, 2014.
[^9]: D.K. Hansen, K. Nasrollahi, C.B. Rasmussen, and T.B. Moeslund. Real-time barcode de-
tection and classification using deep learning. IJCCI, 1:321–327, 2017.
[^10]: Denso Wave Incorporated. What is a qr code? http://www.qrcode.com/en/about/, a.
Accessed: 6 September 2018.
[^11]: Denso Wave Incorporated. History of qr code. http://www.qrcode.com/en/history/, b.
Accessed: 6 September 2018.
[^12]: Ladislav Karrach, Elena Pivarˇciová, and Pavol Boˇzek. Identification of qr code perspec-
tive distortion based on edge directions and edge projections analysis. Journal of Imag-
ing, 6(7):67, 2020. doi: 10.3390/jimaging6070067. URL https://doi.org/10.3390/
jimaging6070067. Published: 10 July 2020.
[^13]: S. Kong. Qr code image correction based on corner detection and convex hull algorithm. J.
Multimed., 8:662–668, 2013. URL https://doi.org/10.4304/jm.8.6.662-668.
[^14]: W.C. Kurniawan, H. Okumura, Muladi, and A.N. Handayani. An improvement on qr code
limit angle detection using convolution neural network. In Proceedings of the 2019 Interna-
tional Conference on Electrical, Electronics and Information Engineering (ICEEIE), pages
234–238, Denpasar, Bali, Indonesia, 2019. URL https://doi.org/10.1109/ICEEIE.
2019.8884244.
[^15]: S. Li, J. Shang, Z. Duan, and J. Huang. Fast detection method of quick response code based
on run-length coding. IET Image Processing, 12:546–551, 2018.
[^16]: J.-A. Lin and C.-S. Fuh. 2d barcode image decoding. Mathematical Problems in Engineering,
pages 1–10, 2013.
[^17]: J. Liu, M. Yang, and Z. Zhang. Svm-based human detection and hog feature selection. In
Proceedings of the International Conference on Image Processing (ICIP), pages 73–76,
2009. URL https://ieeexplore.ieee.org/document/5373730.
[^18]: Shaoqing Ren, Kaiming He, Ross Girshick, and Jian Sun. Faster r-
cnn: Towards real-time object detection with region proposal net-
works. In Proceedings of the Neural Information Processing Systems
(NeurIPS), pages 91–99, 2015. URL https://papers.nips.cc/paper/
5638-faster-r-cnn-towards-real-time-object-detection-with-region-proposal-networks.
[^19]: A. Sun, Y. Sun, and C. Liu. The qr-code reorganization in illegible snapshots taken by
mobile phones. In Proceedings of the 2007 International Conference on Computational
Science and its Applications (ICCSA 2007), pages 532–538, Kuala Lumpur, Malaysia,
2007.
[^20]: Ultralytics Team. Yolov8: You only look once for real-time object detection, segmentation,
and classification. 2023. URL https://github.com/ultralytics/yolov8. Available on
GitHub. Accessed on [Insert Date Here].
[^21]: H. Tribak and Y. Zaz. Qr code patterns localization based on hu invariant moments.
International Journal of Advanced Computer Science and Applications, 2017a. doi:
10.14569/IJACSA.2017.080305.
[^22]: H. Tribak and Y. Zaz. Qr code recognition based on principal components analysis method.
International Journal of Advanced Computer Science and Applications, 8, 2017b. doi:
10.14569/IJACSA.2017.080313.
[^23]: A. Zharkov and I. Zagaynov. Universal barcode detector via semantic segmentation. In
Proceedings of the 2019 International Conference on Document Analysis and Recognition
(ICDAR), pages 837–843, Sydney, Australia, 2019.