"""Optional text normalisation shared by the HF runners."""
from __future__ import annotations

import logging

log = logging.getLogger(__name__)
_normalize = None


def get_bangla_normalizer():
    """csebuetnlp `normalizer` (pip install git+https://github.com/csebuetnlp/normalizer).
    Returns a callable or None if the package is unavailable."""
    global _normalize
    if _normalize is not None:
        return _normalize or None
    try:
        from normalizer import normalize  # type: ignore
        _normalize = normalize
    except Exception:
        log.warning("csebuetnlp `normalizer` not installed - BanglaBERT inputs will NOT be normalised "
                    "(pip install git+https://github.com/csebuetnlp/normalizer)")
        _normalize = False
    return _normalize or None


def prepare_texts(texts, normalize_bangla: bool) -> tuple[list[str], bool]:
    texts = [str(t) for t in texts]
    if not normalize_bangla:
        return texts, False
    norm = get_bangla_normalizer()
    if norm is None:
        return texts, False
    return [norm(t) for t in texts], True
