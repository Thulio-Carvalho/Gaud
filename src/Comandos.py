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
				comando.lstrip(i)
				return eval(self.comandos[i])(comando)
		return ["Comando não cadastrado"]
	
	def _reset(self,comando):
		#return ["Não está funcionando"]
		print("Reset")
		print (subprocess.Popen("nohup bash runme.sh&", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0])
		return ["Restarting..."]
	
	def permitidos(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					return {int(k):v for k,v in x.items()}
			return x
		arquivo = open("permitidos.json","r")
		permitidos = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		return permitidos

	def _see_admins(self,comando):
		def get_value(item):
			return item[1].lower()
		admins = self.permitidos()
		return ["%s (%i)" % (v,k) for k,v in sorted(admins.items(),key=get_value)]

	def _add_admin(self,comando):
		comando = comando.split("")
		if len(comando) < 2 or not comando[0].isdigit():
			return["Formato invalido","Tente: /add_admin id nome"]
		permitidos = self.permitidos()
		permitidos[comando[0]] = " ".join(comando[1:])
		arquivo = open("permitidos.json","w")
		json.dump(permitidos,arquivo)
		arquivo.close()
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
	def _ligr_maquina(self,comando):
		return ["Em Construção"]
		
        def _comandos(self,comando):
            return sorted(self.comandos.keys())

