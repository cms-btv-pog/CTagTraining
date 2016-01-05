'''
site handling. To confgure the scripts to be run on multiple sites (xrd, batch systems etc..)
'''

import os
import subprocess

proc = subprocess.Popen('dnsdomainname', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
proc.wait()
stdout, _ = proc.communicate()
site = stdout.strip()

#things that MUST be defined by each site option!
local_2_xrd=None
batch_header=None
batch_jobsub=None
if site == 'fnal.gov':
   local_2_xrd=lambda x: 'root://cmseos.fnal.gov//store/%s' % (x.split('store/')[1]) 
   batch_header='''
universe = vanilla
Executable = {BASHSCRIPT}
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
x509userproxy = $ENV(X509_USER_PROXY)
request_memory = 10000
'''
   batch_job='''

Output = con_{jobidx}.stdout
Error = con_{jobidx}.stderr
Log = con_{jobidx}.log 
Arguments = {cliArgs}
Queue

'''
else:
   raise RuntimeError('Site %s is not recognized. Insert proper configuration in site.py!' % site)
