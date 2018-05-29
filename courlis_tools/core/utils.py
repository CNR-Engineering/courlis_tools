
class GeometryRequestException(Exception):
    """Custom exception for geometry parser"""
    def __init__(self, message):
        super().__init__(message)
