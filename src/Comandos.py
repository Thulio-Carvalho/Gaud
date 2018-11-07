#coding: utf-8
import json
import subprocess
class Comandos:

	def _update(self):
		arquivo = open("comandos.json","r")
		self.comandos = json.load(arquivo)
		arquivo.close()

	def is_command(self,text):
		self._update()
		return any(text.startswith(x) for x in self.comandos)
	

	def executar(self,comando):
		self._update()
		for i in self.comandos:
			if comando.startswith(i):
				comando = comando.lstrip(i).lstrip()
				return eval(self.comandos[i])(comando)
		return ["Comando não cadastrado"]
	
	def _reset(self,comando):
		#return ["Não está funcionando"]
		print("Reset")
		#print (subprocess.Popen("nohup bash runme.sh&", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0])
		from Comandos import Comandos as aux
		self = aux()
		return ["Restarting...","May not work"]
	
	def permitidos(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					return {int(k):v for k,v in x.items()}
			return x
		arquivo = open("permitidos.json","r")
		permitidos = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		return permitidos
	
	def wait(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					return {int(k):v for k,v in x.items()}
			return x
		arquivo = open("wait.json","r")
		wait = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		return wait

	def _see_admins(self,comando):
		def get_value(item):
			return item[1].lower()
		admins = self.permitidos()
		return ["%s (%i)" % (v,k) for k,v in sorted(admins.items(),key=get_value)]

	def _add_admin(self,comando):
		comando = comando.split(" ")
		print comando
		if comando[0] != "" and len(comando) < 2 or not comando[0].isdigit():
			return["Formato invalido","Tente: /add_admin id nome"]
		permitidos = self.permitidos()
		permitidos[int(comando[0])] = " ".join(comando[1:])
		arquivo = open("permitidos.json","w")
		json.dump(permitidos,arquivo)
		arquivo.close()
		self._remove_wait(comando)
		return ["Sucesso"]
	
	def _remove_admin(self,comando):
		if not comando.isdigit():
			return["Formato invalido","Tente: /remove_admin id"]
		permitidos = self.permitidos()
		if int(comando) in permitidos:
			del permitidos[int(comando)]
			arquivo = open("permitidos.json","w")
			json.dump(permitidos,arquivo)
			arquivo.close()
			
			return ["Sucesso"]
		else:
			return ["Admin não cadastrado"]

	def _ligar_maquina(self,comando):
		return ["Em Construção"]
	
	def _status_laboratorio(self,comando):
		maquinas = self._get_maquinas()
		if comando in ['lcc1','lcc2','lcc3']:
			return [self._status_maquina(i)[0] for i in sorted(maquinas) if i.startswith(comando)]
		else:
			return ["Está laboratorio não existe","tente digitar apenas o nome do laboratorio"]


	def _status_maquina(self,comando):
		maquinas = self._get_maquinas()
		if comando in maquinas:
			if subprocess.Popen("ping %s -c 1 -W 2| grep '1 received'" % maquinas[comando]['ip'], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0] != "":
				return [comando + " Ligada"]
			else:
				return [comando + " Desligada"]
		else:
			return ["Está maquinas não existe","tente laboratorio-maquina"]

	def _comandos(self,comando):
		return sorted(self.comandos.keys())

	def _get_maquinas(self):
		arquivo = open("funcoes/maquinas.json","r")
		maquinas = json.load(arquivo)
		arquivo.close()
		return maquinas

	def _see_wait(self,comando):
		wait = self.wait()
		retorno = []
		for i in wait:
			retorno.append("%s (%d): %s" % (wait[i][0],i,wait[i][1]))
		if len(retorno) == 0:
			retorno.append("Sem waits restantes")
		return retorno
	
	def _remove_wait(self,comando):
		wait = self.wait()
		if comando.isdigit() and int(comando) in wait:
			del wait[int(comando)]
			
			arquivo = open("wait.json","w")
			json.dump(wait,arquivo)
			arquivo.close()
			
			return ["Sucesso"]
		else:
			return ["ID invalido ou não cadstrado","Uso: /remove_wait id"]
