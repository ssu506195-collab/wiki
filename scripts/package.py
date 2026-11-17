from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'outputs'/'Modal_Analysis_LLM_Wiki_HTML_v1.zip'
DEST.parent.mkdir(exist_ok=True)
with ZipFile(DEST,'w',ZIP_DEFLATED) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and not any(x in p.parts for x in ['.git','.openai','__pycache__','node_modules','.sites-runtime']):
   z.write(p,p.relative_to(ROOT).as_posix())
with ZipFile(DEST) as z:
 assert z.testzip() is None
 assert all(x in z.namelist() for x in ['index.html','dist/index.html','dist/wiki/index.html','dist/workflow.html','README.md','SUBMISSION.md','scripts/workflow.py','records/queries.json'])
 assert len([x for x in z.namelist() if x.startswith('sources/') and x.endswith('.md')])==8
 print(str(DEST));print(str(len(z.namelist()))+' files; '+str(DEST.stat().st_size)+' bytes; ZIP integrity passed')
