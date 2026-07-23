"""Test Concentric constraint signatures."""
import sys
sys.path.insert(0, 'Freecadsolver_feedback/api_probe')
from probe_lib import get_modules
app, Part, Sketcher = get_modules()

print('Testing Concentric signatures:')
for args in [(0, 3, 1, 3), (0, -1, 1, -1), (0, 1, 2, 3), (0, 1)]:
    try:
        c = Sketcher.Constraint('Concentric', *args)
        print(f'  {args}: OK -> {c}')
    except Exception as e:
        print(f'  {args}: FAIL {type(e).__name__}: {str(e)[:80]}')
