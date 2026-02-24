# ==============================================================================
# IMAGE LOADER — Handles image loading with fallback for compatibility
# ==============================================================================

import pygame

try:
    _EXTENDED = pygame.image.get_extended()
except Exception:
    _EXTENDED = False

_pil_available = False
if not _EXTENDED:
    try:
        from PIL import Image as _PILImage
        _pil_available = True
    except ImportError:
        pass


def load_image(path):
    """
    Load an image file and return a pygame Surface.
    Uses Pillow as a fallback when pygame lacks PNG/JPG support.
    """
    if _EXTENDED:
        return pygame.image.load(path)

    if _pil_available:
        pil_img = _PILImage.open(path).convert("RGBA")
        raw = pil_img.tobytes()
        surface = pygame.image.fromstring(raw, pil_img.size, "RGBA")
        return surface

    # Last resort — try pygame anyway (might work for BMP)
    return pygame.image.load(path)


def save_image(surface, path):
    """
    Save a pygame Surface to a file.
    Uses Pillow when pygame cannot save to the target format.
    """
    try:
        pygame.image.save(surface, path)
    except Exception:
        if _pil_available:
            raw = pygame.image.tostring(surface, "RGBA")
            size = surface.get_size()
            pil_img = _PILImage.frombytes("RGBA", size, raw)
            pil_img.save(path)
        else:
            raise
