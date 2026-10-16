"""Copy the frontend's static export into the main repository for Vercel."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent
source = root / 'frontend' / 'dist'
target = root / 'public'
files = ('index.html', 'predictor.html', 'model.json')
for name in files:
    if not (source / name).is_file():
        raise SystemExit(f'Missing {source / name}. Restore the frontend checkout before refreshing the deployment files.')
target.mkdir(exist_ok=True)
for name in files:
    shutil.copyfile(source / name, target / name)
print('Updated public/ for Vercel: ' + ', '.join(files))
