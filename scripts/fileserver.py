import subprocess
import os
import uuid

class PoolFile(object):
   def __init__(self, path, delete_on_exit=True):
      self.path = path
      self.del_once_done = delete_on_exit
   def __del__(self):
      if self.del_once_done:
         print 'deleting %s' % self.path
         os.remove(self.path)

def serve(path):
   if path.startswith('root://'):
      fname = '%s.root' % uuid.uuid1()
      print '%s --> %s' % (path, fname)
      proc = subprocess.Popen(['xrdcp', path, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      exitcode = proc.wait()
      if exitcode != 0:
         _, stderr = proc.communicate()
         raise RuntimeError('Problem copying file %s, Error: %s' % (path, stderr))
      return PoolFile(fname)
   else:
      return PoolFile(path, False)
