"""Generate official-baseline-compatible participant-defined 9-qubit Processor B JSON."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from src.processors import processor_spec,validate

def write_json():
    spec=processor_spec('B');validate(spec)
    path=Path(__file__).with_suffix('.json')
    path.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
    return path

if __name__=='__main__':print(write_json())
