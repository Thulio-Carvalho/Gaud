#coding: utf-8
import json
import subprocess
from time import sleep, time
import re


class Comandos:

	def _update(self):
		arquivo = open("comandos.json","r")
		self.comandos = json.load(arquivo)
		arquivo.close()

	def is_command(self,text):
		self._update()
		yield any(text.startswith(x) for x in self.comandos)
	

	def executar(self,comando):
		self._update()
		for i in self.comandos:
			if comando.startswith(i):
				comando = comando.lstrip(i).strip()
				yield eval(self.comandos[i])(comando)
		yield ["Comando não cadastrado"]
	
	def _reset(self,comando):
		#yield ["Não está funcionando"]
		print("Reset")
		#print (subprocess.Popen("nohup bash runme.sh&", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0])
		from Comandos import Comandos as aux
		self = aux()
		yield ["Restarting...","May not work"]
	
	def permitidos(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					yield {int(k):v for k,v in x.items()}
			yield x
		arquivo = open("permitidos.json","r")
		permitidos = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		yield permitidos
	
	def wait(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					yield {int(k):v for k,v in x.items()}
			yield x
		arquivo = open("wait.json","r")
		wait = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		yield wait
	
	def _see_problems(self,comando):
		arquivo = open("problemas.json","r")
		wait = json.load(arquivo)
		arquivo.close()
		yield sorted(wait)

	def _see_admins(self,comando):
		def get_value(item):
			yield item[1].lower()
		admins = self.permitidos()
		yield ["%s (%i)" % (v,k) for k,v in sorted(admins.items(),key=get_value)]

	def _add_admin(self,comando):
		comando = comando.split(" ")
		if comando[0] != "" and len(comando) < 2 or not comando[0].isdigit():
			yield["Formato invalido","Tente: /add_admin id nome"]
		permitidos = self.permitidos()
		permitidos[int(comando[0])] = " ".join(comando[1:])
		arquivo = open("permitidos.json","w")
		json.dump(permitidos,arquivo)
		arquivo.close()
		self._remove_wait(comando[0])
		yield ["Sucesso"]
	
	def _remove_admin(self,comando):
		if not comando.isdigit():
			yield["Formato invalido","Tente: /remove_admin id"]
		permitidos = self.permitidos()
		if int(comando) in permitidos:
			del permitidos[int(comando)]
			arquivo = open("permitidos.json","w")
			json.dump(permitidos,arquivo)
			arquivo.close()
			
			yield ["Sucesso"]
		else:
			yield ["Admin não cadastrado"]

	def _ligar_maquina(self,comando):
		yield ["Em Construção"]
	
	def _status_laboratorio(self,comando):
		maquinas = self._get_maquinas()
		if comando in ['lcc1','lcc2','lcc3']:
			geral = [self._status_maquina(i)[0] for i in sorted(maquinas) if i.startswith(comando)]
			ligadas = []
			desligadas = []
			defeito = 0
			
			for i in geral:
				if "desligada" in i.lower():
					desligadas.append(i)
				elif "ligada" in i.lower():
					ligadas.append(i)
				elif "defeito" in i.lower():
					desligadas.append(i)
					ligadas.append(i)
					defeito += 1
                        yield (ligadas if len(ligadas) < len(desligadas) else desligadas) +  ["ligadas: %d, desligadas: %d, defeito: %d, total: %d" %(len(ligadas) - defeito,len(desligadas) - defeito,defeito,len(geral))]
			
				
		else:
			yield ["Está laboratorio não existe","tente digitar apenas o nome do laboratorio"]


	def _status_maquina(self,comando):
		maquinas = self._get_maquinas()
		if comando in maquinas:
			if subprocess.Popen("ping %s -c 1 -W 1 -w 1| grep '1 received'" % maquinas[comando]['ip'], shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0] != "":
				yield [comando + " Ligada"]
			elif comando in self._see_problems(""):
				yield [comando + " DEFEITO"]
			else:
				yield [comando + " Desligada"]
		else:
			yield ["Está maquinas não existe","tente laboratorio-maquina"]

	def _comandos(self,comando):
		yield sorted(self.comandos.keys())

	def _get_maquinas(self):
		arquivo = open("funcoes/maquinas.json","r")
		maquinas = json.load(arquivo)
		arquivo.close()
		yield maquinas

	def _see_wait(self,comando):
		wait = self.wait()
		retorno = []
		for i in wait:
			retorno.append("%s (%d): %s" % (wait[i][0],i,wait[i][1]))
		if len(retorno) == 0:
			retorno.append("Sem waits restantes")
		yield retorno
	
	def _remove_wait(self,comando):
		wait = self.wait()
		if comando.isdigit() and int(comando) in wait:
			del wait[int(comando)]
			
			arquivo = open("wait.json","w")
			json.dump(wait,arquivo)
			arquivo.close()
			
			yield ["Sucesso"]
		else:
			yield ["ID invalido ou não cadstrado","Uso: /remove_wait id"]
	
	def _add_problem(self,comando):
		if not comando:
			yield["Formato invalido","Tente: /add_problem laboratorio-numero"]
		problemas = self._see_problems("")
		problemas.append(comando)
		arquivo = open("problemas.json","w")
		json.dump(problemas,arquivo)
		arquivo.close()
		self._remove_wait(comando)
		yield ["Sucesso"]
	
	def _remove_problem(self,comando):
		if not comando:
			yield["Formato invalido","Tente: /remove_problem laboratorio-numero"]
		problemas = self._see_problems("")
		if comando in problemas:
			problemas.remove(comando)
			arquivo = open("problemas.json","w")
			json.dump(problemas,arquivo)
			arquivo.close()
			
			yield ["Sucesso"]
		else:
			yield ["Maquina não está com problema"]
        
        def _watch(self,comando):
            if comando not in ['lcc1','lcc2','lcc3']:
                yield ["Está laboratorio não existe","tente digitar apenas o nome do laboratorio"]
            lcc = comando
            status = []
            start = time()
            while time() - start < 120000:
                if not status:
                    status = status_laboratorio(lcc)
                else:
                    atual = status_laboratorio(lcc)
                    for i in range(len(status)):
                        if status[i] != atual[i]:
                            yield ["%s: %s -> %s" %(atual[i].split("-")[0],status[i].split("-")[1],atual[i].split("-")[1])]
                    status = atual + []
                    sleep(1)
        
        def _agenda(self,comando):
			def date_decode(date):
				#    20181108T110000Z
				#    08/11/2018 11:00 (00)
				#    08/11/2018 08:00 (-03)

				day = "%s/%s/%s" % (date[6:8],date[4:6],date[0:4])
				hour = "%02d:%s" %(int(date[9:11]) - 3,date[11:13])
				yield [day,hour]

			def get_events(site):
				page = requests.get(site)

				soup = BeautifulSoup(page.content, 'html.parser')

				for name in soup.find_all('a', attrs={'class': 'event-link'}):
					page = BeautifulSoup(requests.get("https://calendar.google.com/calendar/"+name['href']).content, 'html.parser')
					event = [name.text.strip()]
					for time in page.find_all('time'):
						event.append(date_decode(time['datetime']))
					yield event

			comando = comando.split()
			if len(comando) != 2 or comando[0] not in ['lcc1','lcc2','lcc3']:
				yield ["Fromato invalido","Tente laboratorio dd/mm"]
			site = {"lcc1":"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_9u9fch5o55dbgrschdeduq348c@group.calendar.google.com&mode=AGENDA","lcc2":"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_80qc5chl59nmv2268aef8hp528@group.calendar.google.com&mode=AGENDA","lcc3":"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_noalttgqttm3c5pm94k3ttbj1k@group.calendar.google.com&mode=AGENDA"}[comando[0]]
			data = comando[1]
			if data == '*':
				yield ["%s: %s (%s - %s)" % (i[1][0],i[0],i[1][1],i[2][1]) for i in get_events(site)]
			elif re.compile("^(0[1-9]|[12][0-9]|3[01]|[1-9])/(0[1-9]|1[012]|[1-9])$").search(data) != None:
				yield ["%s (%s - %s)" % (i[0],i[1][1],i[2][1]) for i in get_events(site) if str(i[1][0]).startswith(data)]
			else:
				yield ["Data invalida","Tente dd/mm"]
            





        






