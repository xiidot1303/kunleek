class OrderError(Exception):
    def __init__(self, message, order_id=None):
        super().__init__(message)
        self.order_id = order_id

class BillzAPIError(OrderError):
    def __init__(self, message, url=None, response_data=None):
        super().__init__(message)
        self.url = url
        self.response_data = response_data
        