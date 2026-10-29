# Source snapshots

These two files preserve same-named variants from the original working folder that differ from the versions already tracked in `BT/ESP32 side/`:

- `Forward_V2-original-folder.py` has the startup `stand()` call commented out.
- `main-original-folder.py` contains a BLE-ready handshake variant.

They are preserved for comparison and are not selected as the default firmware entry point.
