from deploy import apply
class Mock:
 def __init__(self,fail=False):self.config="old";self.fail=fail
 def run(self,c):
  if c=="show running-config":return self.config
  if self.fail:return "ERROR rejected"
  self.config+="\n"+c;return "OK"
 def restore(self,c):self.config=c
def test_deploy():assert apply(Mock(),"hostname test")["status"]=="verified"
def test_rollback():
 m=Mock(True);assert apply(m,"hostname test")["status"]=="rolled_back";assert m.config=="old"
