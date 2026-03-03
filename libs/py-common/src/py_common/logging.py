from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure project-wide logging format for API and worker processes."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
