class TradeUnifoxError(Exception):
    """Base exception for TradeUnifox SDK"""

class AuthenticationError(TradeUnifoxError):
    """Invalid credentials or token"""

class APIError(TradeUnifoxError):
    """General API error"""

class NetworkError(TradeUnifoxError):
    """Request failed due to connection issues"""
