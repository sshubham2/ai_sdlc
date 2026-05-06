# Design: Slice 042 missing-cells (fixture)

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `src/services/widget.py` | `src/api/widgets.py` | `tests/test_widgets.py::test_create` | — |
| `src/services/orphan.py` | — | — | — |
