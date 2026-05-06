# Design: Slice 043 missing-rationale (fixture)

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `src/services/legit.py` | `src/api/foo.py` | `tests/test_foo.py::test_x` | — |
| `src/utils/_helper.py` | — | — | `internal helper, no consumer demanded` |
