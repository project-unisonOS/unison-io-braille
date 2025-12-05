from typing import Optional
import logging

logger = logging.getLogger("unison-io-braille.hid_io")

try:
    import hid  # type: ignore
except Exception:  # pragma: no cover
    hid = None


class HIDWriter:
    """Thin wrapper around hid.Device for writing output reports."""

    def __init__(self, dev) -> None:
        self.dev = dev

    def write(self, data: bytes) -> None:
        try:
            # hidapi expects list/bytes including report id as first byte
            self.dev.write(list(data))
        except Exception as exc:  # pragma: no cover
            logger.warning("hid_write_failed %s", exc)

    def close(self) -> None:
        try:
            self.dev.close()
        except Exception:
            pass


def open_hid_writer(vid_hex: str | None, pid_hex: str | None) -> Optional[HIDWriter]:
    if hid is None or not vid_hex or not pid_hex:
        return None
    try:
        dev = hid.Device(int(vid_hex, 16), int(pid_hex, 16))  # type: ignore[attr-defined]
        return HIDWriter(dev)
    except Exception as exc:  # pragma: no cover
        logger.warning("hid_open_failed %s", exc)
        return None
