"""Export the exact API contract without starting the server or touching its DB."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.main import app

def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else 'openapi.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'API contract exported: {target}')

if __name__ == '__main__':
    main()
