#!/usr/bin/env python3

import os
import sys
import time
import json
import sqlite3
from contextlib import contextmanager

home_path = os.getenv('HOME')
db_path = os.getenv('db_path') or 'Library/Application Support/Alfred/Databases'
db_name = os.getenv('db_name') or 'clipboard.alfdb'
db_res = os.path.join(home_path, db_path, db_name)
i_path = db_res + '.data'
sf_clip_limit = os.getenv('sf_clip_limit') or -1
uidSeed = str(os.getenv('uidSeed', time.time()))

@contextmanager
def database(path):
  db = sqlite3.connect(path)
  yield db
  db.close()

def listitems(fmt='png',num=1):
  if num > 1:
    items.append({
      "title": f'↩ save last {num} clips as {fmt.upper()}',
      "arg": num,
      "variables": {
        "action": 'multisave',
        "format": fmt.lower(),
      },
      "quicklookurl": ''
    })
  with database(db_res) as db:
    rows = db.execute("SELECT dataHash,item,apppath,strftime('%Y-%m-%d %H:%M',ts+978307200,'unixepoch','localtime') from clipboard WHERE dataType = 1 ORDER BY rowid DESC LIMIT ?", [sf_clip_limit])
    for r in rows:
      if r[2] is None:
        icon = { "path": "generic.png" }
        sub = "(unknown)"
        #match = 'unknown'
      else:
        img = os.path.join(i_path, r[0])
        icon = { "path": img }
        sub = r[2]
        #match = sub.replace('/', ' / ')
      items.append({
        "uid": ''.join([ uidSeed, '.', r[0] ]),
        "variables": { "uidSeed": uidSeed },
        "title": r[1],
        "subtitle": r[3] + f' ↩ save as {fmt.upper()}',
        "arg": img,
        "type": "file:skipcheck",
        "variables": {
          "format": fmt.lower(),
        },
        #"match": match,
        "icon": icon,
        "mods": {
          "alt": {
            "arg": img,
            "subtitle": ' '.join([ 'from:', sub ])
          },
          "cmd": {
            "arg": img,
            "subtitle": ' '.join([ str(r[0]), '(reveal)' ]),
            "variables": {
              "action": 'reveal'
            }
          }
        },
        "quicklookurl": img
      })

try:
  args = sys.argv[1].split()
except:
  args = []
  pass

items = []
arg = fmt = None
num = 1

while len(args):
  arg = args[0]
  args = args[1:]
  try:
    num = int(arg)
  except:
    fmt = arg
    pass

if num < 1:
  num = 1
if fmt is None or len(str(fmt)) < 3:
  fmt = os.getenv('default_format') or 'png'
if fmt and fmt.upper() == 'JPG':
  fmt = 'jpeg'

#print(f'fmt:{fmt}',file=sys.stderr)
#print(f'num:{num}',file=sys.stderr)
listitems(fmt=fmt,num=num)

if not items:
  items = [{
    "title": "No image clips found",
    "subtitle": "clipboard history may be empty",
    "icon": { "path": "error.png" },
    "valid": False
  }]

variables = { 'uidSeed': uidSeed }
output = { "variables": variables, "skipknowledge": True, "items": items }
json.dump(output, sys.stdout)
