#!/usr/bin/env python3

import os
import re
import sys
import json
import sqlite3
import plistlib
import datetime as dt
from contextlib import contextmanager
from wf_common import *
#from pathlib import Path

@contextmanager
def database(path):
  db = sqlite3.connect(path)
  yield db
  db.close()

def append_item(fn, img, title, sub, srcapp, ctime):
  global uidSeed, fmt, items
  if not os.path.exists(img):
    return
  il = img.lower()
  if not any(i['arg'] == il for i in items):
    items.append({
      "uid": ''.join([ uidSeed, '.', fn ]),
      "variables": { "uidSeed": uidSeed },
      "title": title,
      "subtitle": f'{ctime} ↩ save as {fmt.upper()}',
      "arg": il,
      "type": "file:skipcheck",
      "variables": {
        "format": fmt.lower(),
        "dataHash": fn,
        "action": 'single'
      },
      "icon": { "path": img },
      "mods": {
        "ctrl": {
          "arg": img,
          "subtitle": f'{ctime} ↩ copy to clipboard',
          "variables": { "action": 'copy' }
        },
        "alt": {
          "arg": il,
          "subtitle": f'from: {sub}'
        },
        "cmd": {
          "arg": img,
          "subtitle": f'{ctime} ↩ reveal in Finder',
          "variables": { "action": 'reveal' }
        }
      },
      "quicklookurl": img
    })

def listitems(fmt='png', num=1, since=None, human=None):
  if since and human:
    atleast = int(dt.datetime.now().timestamp()) - since - 978307200
    items.append({
      "title": f'↩ save time-filtered clips below (last {human}) as {fmt.upper()}',
      "arg": atleast,
      "icon": { "path": "clock.png" },
      "variables": {
        "action": 'multisave_time',
        "format": fmt.lower()
      },
      "quicklookurl": ''
    })
  else:
    atleast = 0
  if num > 1:
    items.append({
      "title": f'↩ save last {num} clips as {fmt.upper()}',
      "arg": num,
      "variables": {
        "action": 'multisave',
        "format": fmt.lower()
      },
      "quicklookurl": ''
    })
  with database(db_res) as db:
    #0=filename, 1=title, 2=src app, 3=time, 4=type (1=image from db,2=files)
    rows = db.execute("SELECT dataHash,item,apppath,ts,dataType from clipboard WHERE dataType IN (1,2) AND ts >= ? ORDER BY rowid DESC LIMIT ?", [atleast, sf_clip_limit])
    for r in rows:
      (fn, title, srcapp, ts, dtype) = r
      ts += 978307200
      ctime = dt.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
      img = os.path.join(i_path, fn)
      if dtype == 2:
        try:
          with open(img, "rb") as fp:
            plistobj = plistlib.load(fp)
        except:
          continue
        imgfiles = [i for i in plistobj if os.path.exists(i) and i.split(os.extsep)[-1].lower() in img_exts]
        for f in imgfiles:
          title = ' '.join([ "File:", f ])
          sub = f"File List {fn}"
          append_item(fn,f,title,sub,srcapp,ctime)
      else:
        sub = srcapp or "(unknown)"
        append_item(fn,img,title,sub,srcapp,ctime)

try:
  args = sys.argv[1].split()
except:
  args = []
  pass

items = []
arg = fmt = sr_n = sr_str = None
num = 1

# poor man's arg parser
for a in args:
  try:
    num = int(a)
    continue
  except:
    pass
  try:
    sr = re.match(r'([0-9]+)([smhd])', a, re.IGNORECASE)
    sr_str = sr.group(0)
    sr_n = int(sr.group(1))
    sr_u = sr.group(2).lower()
    if sr_u == 'm':
      sr_n *= 60
    if sr_u == 'h':
      sr_n *= 3600
    if sr_u == 'd':
      sr_n *= 86400
    continue
  except:
    pass
  fmt = a.lower()

if num < 1:
  num = 1
if fmt is None or len(str(fmt)) < 3:
  fmt = default_format
if fmt and fmt.upper() == 'JPG':
  fmt = 'jpeg'

"""
print(f'fmt:{fmt}',file=sys.stderr)
print(f'num:{num}',file=sys.stderr)
print(f'sr_n:{sr_n}',file=sys.stderr)
"""

listitems(fmt=fmt, num=num, since=sr_n, human=sr_str)

if not items:
  items = [{
    "title": "No image clips found",
    "subtitle": "clipboard history may be empty",
    "icon": { "path": "error.png" },
    "valid": False
  }]

variables = {
  'uidSeed': uidSeed,
  'delete_after_convert': delete_after_convert,
  'save_to_current': save_to_current,
  'db_name': db_name,
  'db_path': db_path,
  'dest_dir': dest_dir,
  'default_format': default_format
}

items.insert(0, {
  "title": "Grid View",
  "subtitle": "Display results in enlarged Grid View",
  "arg": "",
  "icon": { "path": "grid.png" },
  "variables": { "action": "grid" }
})

output = {
  "variables": variables,
  "skipknowledge": True,
  "items": items
}

json.dump(output, sys.stdout)
