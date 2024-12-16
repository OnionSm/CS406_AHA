class FinderPatternInfo:
    def __init__(self, pattern_centers):
        """
        Khởi tạo đối tượng FinderPatternInfo với thông tin về ba Finder Patterns:
        bottom-left, top-left và top-right.
        
        :param pattern_centers: Danh sách chứa ba FinderPattern theo thứ tự [bottomLeft, topLeft, topRight]
        """
        self.bottom_left = pattern_centers[0]
        self.top_left = pattern_centers[1]
        self.top_right = pattern_centers[2]

    def get_bottom_left(self):
        """
        Lấy FinderPattern ở vị trí bottom-left.
        :return: FinderPattern bottom-left.
        """
        return self.bottom_left

    def get_top_left(self):
        """
        Lấy FinderPattern ở vị trí top-left.
        :return: FinderPattern top-left.
        """
        return self.top_left

    def get_top_right(self):
        """
        Lấy FinderPattern ở vị trí top-right.
        :return: FinderPattern top-right.
        """
        return self.top_right
