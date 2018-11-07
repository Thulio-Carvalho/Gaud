import json
import paramiko
from getpass import getpass

arquivo = open("maquians.json","r")
maquinas = json.load(arquivo)
arquivo.close()

password = getpass('password for "ramonss": ')

chopper = paramiko.SSHClient()
chopper.set_missing_host_key_policy(paramiko.AutoAddPolicy())
chopper.connect('chopper.lcc.ufcg.edu.br', port=23456, username='ramonss', password=password)

r2d2 = paramiko.SSHClient()
r2d2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
r2d2.connect('r2d2.lcc.ufcg.edu.br', port=23456, username='ramonss', password=password)

kirk = paramiko.SSHClient()
kirk.set_missing_host_key_policy(paramiko.AutoAddPolicy())
kirk.connect('kirk.lcc.ufcg.edu.br', port=23456, username='ramonss', password=password)

for i in sorted(maquinas):
    if maquinas[i]["mac"] != "":
        if i.startswith("lcc1-"):
            stdout = chopper.exec_command('wakeonlan %s' %  maquinas[i]["mac"])
            for j in stdout[1]:
                print i,j
        elif i.startswith("lcc2-"):
            stdout = r2d2.exec_command('wakeonlan %s' %  maquinas[i]["mac"])
            for j in stdout[1]:
                print i,j
        else:
            stdout = kirk.exec_command('wakeonlan %s' %  maquinas[i]["mac"])
            for j in stdout[1]:
                print i,j

chopper.close()
r2d2.close()
kirk.close()

