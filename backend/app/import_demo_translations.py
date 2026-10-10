"""Explicit one-time import for untouched demo scripts; never overwrites translations."""
import json
from pathlib import Path
from sqlalchemy import select
from .db import Session
from .models import POI, Content
from .seed import PLACES

def run():
    translations=json.loads(Path(__file__).with_name('demo_translations.json').read_text(encoding='utf-8'))
    original={row[0]:(row[-2],row[-1]) for row in PLACES}
    changed=0
    with Session.begin() as db:
        for c,p in db.execute(select(Content,POI).join(POI,Content.poi_id==POI.id)):
            if c.source.get('type')!='demo_original' or p.name not in original:continue
            if (c.vi,c.en)!=original[p.name]:continue
            for lang,value in translations[p.name].items():
                if not getattr(c,lang).strip():setattr(c,lang,value);changed+=1
    print(f'Imported {changed} missing demo translations. Existing translations and edited scripts preserved.')

if __name__=='__main__':run()
