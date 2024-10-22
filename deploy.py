import argparse,json,os
from pathlib import Path
import yaml
from jinja2 import Environment,FileSystemLoader,StrictUndefined
def render(device):
 return Environment(loader=FileSystemLoader(str(Path(__file__).parent/"templates")),undefined=StrictUndefined,autoescape=False).get_template("router.j2").render(**device)
def apply(transport,desired):
 previous=transport.run("show running-config")
 try:
  for command in desired.splitlines():
   if not command.strip():continue
   result=transport.run(command)
   if any(token in result.lower() for token in ("error","invalid","failed")):raise RuntimeError(result)
  current=transport.run("show running-config")
  if not all(line.strip() in current for line in desired.splitlines() if line.strip()):raise RuntimeError("verification mismatch")
  return {"status":"verified","previous":previous}
 except Exception as error:
  try:transport.restore(previous)
  except Exception as rollback:return {"status":"rollback_failed","error":str(error),"rollback_error":str(rollback)}
  return {"status":"rolled_back","error":str(error)}
class SSH:
 def __init__(self,device):
  import paramiko
  self.client=paramiko.SSHClient();self.client.load_system_host_keys()
  self.client.connect(device["host"],username=device["username"],key_filename=os.environ["SSH_KEY"],timeout=10)
 def run(self,command):
  _,stdout,stderr=self.client.exec_command(command,timeout=10)
  result=stdout.read().decode()+stderr.read().decode()
  if stdout.channel.recv_exit_status()!=0:raise RuntimeError(result)
  return result
 def restore(self,text):
  for line in text.splitlines():self.run(line)
 def close(self):self.client.close()
def main():
 p=argparse.ArgumentParser();p.add_argument("inventory");p.add_argument("--dry-run",action="store_true");a=p.parse_args()
 for d in yaml.safe_load(Path(a.inventory).read_text())["devices"]:
  config=render(d)
  if a.dry_run:print(d["name"],config);continue
  ssh=SSH(d)
  try:print(json.dumps({"device":d["name"],**apply(ssh,config)}))
  finally:ssh.close()
if __name__=="__main__":main()
