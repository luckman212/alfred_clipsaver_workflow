#!/usr/bin/env python3

import os
import sys
import time
import json
import sqlite3
import plistlib
from contextlib import contextmanager
#from pathlib import Path

def envvar(v: str, dv: str) -> str:
  return str(os.getenv(v) or dv)

def envvar_to_bool(v: str) -> str:
  return str(bool(os.getenv(v))).lower()

def envvar_to_int(v: str, dv: int=0) -> int:
  try:
    return int(os.getenv(v))
  except:
    pass
  try:
    return int(dv)
  except:
    return 0

#wf vars
db_name = envvar('db_name', 'clipboard.alfdb')
db_path = os.path.expanduser(envvar('db_path', '~/Library/Application Support/Alfred/Databases'))
default_format = envvar('default_format', 'png').lower()
delete_after_convert = envvar_to_bool('delete_after_convert')
dest_dir = os.path.expanduser(envvar('dest_dir', '~/Desktop/saved_clips')).lower()
save_to_current = envvar_to_bool('save_to_current')
sf_clip_limit = envvar_to_int('sf_clip_limit', -1)

#home_path = os.getenv('HOME')
db_res = os.path.join(db_path, db_name)
i_path = db_res + '.data'
uidSeed = str(os.getenv('uidSeed', time.time()))
img_exts = [ 'png', 'gif', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp' ]

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
        "format": fmt.lower()
      },
      "quicklookurl": ''
    })
  with database(db_res) as db:
    #0=filename, 1=title, 2=src app, 3=time, 4=type (1=image from db,2=files)
    rows = db.execute("SELECT dataHash,item,apppath,strftime('%Y-%m-%d %H:%M',ts+978307200,'unixepoch','localtime'),dataType from clipboard WHERE dataType IN (1,2) ORDER BY rowid DESC LIMIT ?", [sf_clip_limit])
    for r in rows:
      srcpath = os.path.join(i_path, r[0])
      if r[4] == 2:
        try:
          with open(srcpath, "rb") as fp:
            plistobj = plistlib.load(fp)
          img = next(i for i in plistobj if i.split(os.extsep)[-1].lower() in img_exts)
          assert os.path.exists(img)
        except:
          continue
        title = ' '.join([ "File:", img ])
        icon = { "path": img }
        sub = "File List"
      elif r[2] is None:
        title = r[1]
        icon = { "path": img }
        sub = "(unknown)"
        #match = 'unknown'
      else:
        img = srcpath
        title = r[1]
        icon = { "path": img }
        sub = r[2]
        #match = sub.replace('/', ' / ')
      items.append({
        "uid": ''.join([ uidSeed, '.', r[0] ]),
        "variables": { "uidSeed": uidSeed },
        "title": title,
        "subtitle": r[3] + f' ↩ save as {fmt.upper()}',
        "arg": img.lower(),
        "type": "file:skipcheck",
        "variables": {
          "format": fmt.lower()
        },
        #"match": match,
        "icon": icon,
        "mods": {
          "alt": {
            "arg": img.lower(),
            "subtitle": ' '.join([ 'from:', sub ])
          },
          "cmd": {
            "arg": img,
            "subtitle": ' '.join([ str(img), '(reveal)' ]),
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
  fmt = default_format
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

variables = {
  'uidSeed': uidSeed,
  'delete_after_convert': delete_after_convert,
  'save_to_current': save_to_current
}
output = { "variables": variables, "skipknowledge": True, "items": items }
json.dump(output, sys.stdout)
