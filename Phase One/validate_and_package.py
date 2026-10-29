"""Run end-to-end experiments, tests, regenerate report and package new evidence."""
import subprocess,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent

def run(args):
    print('RUNNING:', ' '.join(args),flush=True)
    subprocess.run([sys.executable,*args],cwd=root,check=True)

run(['-m','unittest','discover','-s','tests','-v'])
run(['run_experiment.py'])
run(['-m','src.full_six_reference'])
run(['-m','src.finalize_report'])
import json
six=json.loads((root/'results/full_six_qubit_reference.json').read_text())
assert six['status']=='FULL_6Q_EXECUTED'
assert sum(six['counts_bitstring_msb_first'].values())==six['shots']==4096
assert six['best_observed_cut']<=six['optimum']==16
assert len(six['optimizer_restarts'])>=3
assert 'ideal_optimal_bitstring_probability' in six
assert 'routing_diagnostic_swaps' in six['processor_B']
assert '## 10. Organiser clarifications' in (root/'report.md').read_text()
output=root.parent/'qff-2026-ps-o1-enhanced-validated.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(root.rglob('*')):
        if not f.is_file() or '.git' in f.parts or '__pycache__' in f.parts or f.suffix=='.pyc':continue
        z.write(f,arcname=str(Path(root.name)/f.relative_to(root)))
print('FULL VALIDATION SUCCEEDED:',output,flush=True)
