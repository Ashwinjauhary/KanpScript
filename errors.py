class KanpError(Exception):
    def __init__(self, message, line_num, error_type):
        self.message = message
        self.line_num = line_num
        self.error_type = error_type

    def __str__(self):
        return f"\n❌ {self.error_type}:\n{self.message}\nLine {self.line_num} pe kaand ho gaya"

class BaklolError(KanpError):
    def __init__(self, message, line_num):
        super().__init__(message, line_num, "BaklolError")

class BhaukaalError(KanpError):
    def __init__(self, message, line_num):
        super().__init__(message, line_num, "BhaukaalError (Serious System Fail)")

class GyaanPelWarning(KanpError):
    def __init__(self, message, line_num):
        super().__init__(message, line_num, "GyaanPelWarning")

    def __str__(self):
        return f"\n⚠️ {self.error_type}:\n{self.message}\nLine {self.line_num}: Zyada mat socho"
