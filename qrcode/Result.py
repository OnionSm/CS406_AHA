import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from qr_patterns import ResultPoint
from typing import List, Dict, Optional
from enums import BarcodeFormat
import time
from enums import ResultMetadataType

class Result:
    def __init__(self, text: str,
                 raw_bytes: Optional[bytes],
                 result_points,
                 format: BarcodeFormat,
                 timestamp: Optional[int] = None):
        """
        Khởi tạo một đối tượng `Result` với dữ liệu được giải mã, byte thô, điểm kết quả, định dạng,
        và một dấu thời gian tùy chọn.

        :param text: Văn bản được giải mã từ mã vạch (str).
        :param raw_bytes: Dữ liệu byte thô của mã vạch, nếu có (Optional[bytes]).
        :param result_points: Các điểm liên quan đến kết quả (List[ResultPoint]).
        :param format: Định dạng mã vạch (BarcodeFormat).
        :param timestamp: Dấu thời gian khi kết quả được tạo (Optional[int], mặc định là thời gian hiện tại).
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        self.text = text
        self.raw_bytes = raw_bytes
        self.num_bits = 8 * len(raw_bytes) if raw_bytes else 0
        self.result_points = result_points or []
        self.format = format
        self.result_metadata = None
        self.timestamp = timestamp

    def get_text(self) -> str:
        """
        Trả về văn bản được giải mã từ mã vạch.

        :return: Văn bản giải mã (str).
        """
        return self.text

    def get_raw_bytes(self) -> Optional[bytes]:
        """
        Trả về dữ liệu byte thô của nội dung mã vạch, nếu có.

        :return: Dữ liệu byte thô (Optional[bytes]).
        """
        return self.raw_bytes

    def get_num_bits(self) -> int:
        """
        Trả về số lượng bit trong dữ liệu byte thô.

        :return: Số bit (int).
        """
        return self.num_bits

    def get_result_points(self):
        """
        Trả về danh sách các điểm kết quả liên quan đến mã vạch.

        :return: Danh sách các điểm kết quả (List[ResultPoint]).
        """
        return self.result_points

    def get_barcode_format(self) -> BarcodeFormat:
        """
        Trả về định dạng mã vạch.

        :return: Định dạng mã vạch (BarcodeFormat).
        """
        return self.format

    def get_result_metadata(self):
        """
        Trả về metadata của kết quả, nếu có.

        :return: Metadata của kết quả (Dict[ResultMetadataType, object] hoặc None).
        """
        return self.result_metadata

    def put_metadata(self, type: ResultMetadataType, value: object):
        """
        Thêm một cặp key-value metadata vào kết quả.

        :param type: Loại metadata (ResultMetadataType).
        :param value: Giá trị metadata (object).
        """
        if self.result_metadata is None:
            self.result_metadata = {}
        self.result_metadata[type] = value

    def put_all_metadata(self, metadata):
        """
        Thêm toàn bộ metadata vào kết quả.

        :param metadata: Metadata mới để thêm vào (Dict[ResultMetadataType, object]).
        """
        if metadata:
            if self.result_metadata is None:
                self.result_metadata = metadata
            else:
                self.result_metadata.update(metadata)

    def add_result_points(self, new_points):
        """
        Thêm các điểm kết quả mới vào danh sách hiện có.

        :param new_points: Danh sách các điểm mới (List[ResultPoint]).
        """
        if new_points:
            self.result_points.extend(new_points)

    def get_timestamp(self) -> int:
        """
        Trả về dấu thời gian của kết quả.

        :return: Dấu thời gian (int).
        """
        return self.timestamp

    def __repr__(self):
        """
        Trả về biểu diễn chuỗi của đối tượng, thường là văn bản đã giải mã.

        :return: Chuỗi đại diện (str).
        """
        return self.text
