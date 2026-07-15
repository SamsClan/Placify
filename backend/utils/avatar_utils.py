"""
Avatar generation utility using Pydenticon library.
Generates unique pixel art style avatars based on identifiers.
"""
from pydenticon import Generator
import hashlib
import base64

def _get_generator():
    return Generator(5, 5, foreground=['#004f9d', '#5295d3', '#28a745', '#0d47a1', '#1565c0'], digest=hashlib.sha256)

def generate_avatar(identifier, size=128):
    """
    Generate avatar as base64 data URL (for <img src=""> use).
    """
    hash_hex = hashlib.sha256(identifier.encode()).hexdigest()
    generator = _get_generator()
    png_bytes = generator.generate(hash_hex, size, size)
    img_base64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"

def generate_avatar_png(identifier, size=128):
    """
    Generate avatar and return raw PNG bytes (for Flask Response).
    """
    hash_hex = hashlib.sha256(identifier.encode()).hexdigest()
    generator = _get_generator()
    return generator.generate(hash_hex, size, size)
