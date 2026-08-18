"""Image encoding helpers for multimodal generation.

Converts ComfyUI ``IMAGE`` tensors ([B,H,W,C], float 0-1) into base64 PNG data
URLs that both backends can consume. ``numpy``/``PIL`` are imported lazily so the
rest of the package stays importable without them.
"""

from __future__ import annotations

import base64
import io as _io
from typing import Any


def _tensor_to_data_url(frame: Any) -> str:
    import numpy as np
    from PIL import Image

    array = frame.detach().cpu().numpy() if hasattr(frame, "detach") else np.asarray(frame)
    array = np.clip(array * 255.0, 0, 255).astype("uint8")
    image = Image.fromarray(array)
    buffer = _io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def tensors_to_data_urls(*image_inputs: Any) -> list[str]:
    """Flatten one or more IMAGE batches into a list of PNG data URLs."""
    urls: list[str] = []
    for image in image_inputs:
        if image is None:
            continue
        batch = image if getattr(image, "ndim", 0) == 4 else [image]
        for frame in batch:
            urls.append(_tensor_to_data_url(frame))
    return urls
