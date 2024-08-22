#!/usr/bin/env python3

import os
import sys
import sqlite3
import plistlib
import datetime as dt
from contextlib import contextmanager
from wf_common import *

@contextmanager
def database(path):
  db = sqlite3.connect(path)
  yield db
  db.close()

def get_image_hashes(atleast=0, num_clips=None):
  with database(db_res) as db:
    rows = db.execute("SELECT dataHash,dataType from clipboard WHERE dataType IN (1,2) AND ts >= ? ORDER BY rowid DESC", [atleast])
    rc = 0
    for r in rows:
      if num_clips and rc >= num_clips:
        break
      (fn, dtype) = r
      img = os.path.join(i_path, fn)
      if dtype == 2:
        try:
          with open(img, "rb") as fp:
            plistobj = plistlib.load(fp)
        except:
          continue
        imgfiles = [i for i in plistobj if os.path.exists(i) and i.split(os.extsep)[-1].lower() in img_exts]
        for f in imgfiles:
          rc += 1
          print(f)
          if num_clips and rc >= num_clips:
            break
      else:
        rc += 1
        print(fn)
        if num_clips and rc >= num_clips:
          break

if __name__ == '__main__':
  args = sys.argv[1:]
  if args[0] == '--atleast':
    get_image_hashes(atleast=int(args[1]))
  elif args[0] == '--num_clips':
    get_image_hashes(num_clips=int(args[1]))
  else:
    exit(1)
