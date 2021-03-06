# coding: utf-8
import json
import subprocess
import re
from time import sleep, time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import paramiko


class Comandos:
	def _update(self):
		arquivo = open("comandos.json", "r")
		self.comandos = json.load(arquivo)
		arquivo.close()

	def is_command(self, text):
		self._update()
		return any(text.startswith(x) for x in self.comandos)

	def executar(self, comando):
		self._update()
		for i in self.comandos:
			if comando.startswith(i):
				comando = comando.lstrip(i).strip()
				return eval(self.comandos[i])(comando)
		return ["Comando não cadastrado"]

	def _reset(self, comando):
		# return ["Não está funcionando"]
		print("Reset")
		# print (subprocess.Popen("nohup bash runme.sh&", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, universal_newlines=True).communicate()[0])
		from Comandos import Comandos as aux
		self = aux()
		return ["Restarting...", "May not work"]

	def permitidos(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
				return {int(k): v for k, v in x.items()}
			return x

		arquivo = open("permitidos.json", "r")
		permitidos = json.load(arquivo, object_hook=jsonKeys2int)
		arquivo.close()
		return permitidos

	def wait(self):
		def jsonKeys2int(x):
			if isinstance(x, dict):
				return {int(k): v for k, v in x.items()}
			return x

		arquivo = open("wait.json", "r")
		wait = json.load(arquivo, object_hook=jsonKeys2int)
		arquivo.close()
		return wait

	def _see_problems(self, comando):
		def decode(x):
			if isinstance(x, list):
				return [k.decode().encode('utf-8') for k in x]
			return x

		arquivo = open("problemas.json", "r")
		wait = json.load(arquivo, object_hook=decode)
		arquivo.close()
		return sorted(wait)

	def _see_admins(self, comando):
		def get_value(item):
			return item[1].lower()

		admins = self.permitidos()
		return [
			"%s (%i)" % (v, k)
			for k, v in sorted(admins.items(), key=get_value)
		]

	def _add_admin(self, comando):
		comando = comando.split(" ")
		if comando[0] != "" and len(comando) < 2 or not comando[0].isdigit():
			return ["Formato invalido", "Uso: /add_admin id nome"]
		permitidos = self.permitidos()
		permitidos[int(comando[0])] = " ".join(comando[1:])
		arquivo = open("permitidos.json", "w")
		json.dump(permitidos, arquivo)
		arquivo.close()
		self._remove_wait(comando[0])
		return ["Sucesso"]

	def _remove_admin(self, comando):
		if not comando.isdigit():
			return ["Formato invalido", "Uso: /remove_admin id"]
		permitidos = self.permitidos()
		if int(comando) in permitidos:
			del permitidos[int(comando)]
			arquivo = open("permitidos.json", "w")
			json.dump(permitidos, arquivo)
			arquivo.close()

			return ["Sucesso"]
		else:
			return ["Admin não cadastrado"]

	def _ligar_laboratorio(self, comando):
		yield "Em Construção"
		return
		if comando not in ['lcc1', 'lcc2', 'lcc3']:
			yield "Está laboratorio não existe",
			yield "tente digitar apenas o nome do laboratorio"
			return

		yield "Comançando (Talvez nem todas as maquinas liguem)"
		maquinas = self._get_maquinas()

		username = "USERNAME"
		password = "SENHA"
		site = {
			"lcc1":
				"chopper.lcc.ufcg.edu.br",
			"lcc2":
				"r2d2.lcc.ufcg.edu.br",
			"lcc3":
				"kirk.lcc.ufcg.edu.br"
		}[comando]

		sever = paramiko.SSHClient()
		sever.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		sever.connect('sever.lcc.ufcg.edu.br', port=23456, username=username, password=password)

		for i in maquinas:
			if i.startswith(comando) and maquinas[i]["mac"] != "":
				sever.exec_command('wakeonlan %s' % maquinas[i]["mac"])

		sever.close()
		yield "Finalizado"

	def _status_laboratorio(self, comando):
		maquinas = self._get_maquinas()
		if comando in ['lcc1', 'lcc2', 'lcc3']:
			yield "Espera que eu vou verificar"
			geral = [
				self._status_maquina(i)[0] for i in sorted(maquinas)
				if i.startswith(comando)
			]
			ligadas = []
			desligadas = []
			defeito = 0

			for i in geral:
				if "defeito" in i.lower():
					desligadas.append(i)
					ligadas.append(i)
					defeito += 1
				elif "desligada" in i.lower():
					desligadas.append(i)
				elif "ligada" in i.lower():
					ligadas.append(i)

			for i in (ligadas if len(ligadas) < len(desligadas) else desligadas):
				yield i

			yield ("ligadas: %d, desligadas: %d, defeito: %d, total: %d" % (
				len(ligadas) - defeito, len(desligadas) - defeito, defeito, len(geral)))

		else:
			yield "Formato invalido"
			yield "Uso: /status_laboratorio laboratorio"

	def _status_maquina(self, comando):
		maquinas = self._get_maquinas()
		if comando in maquinas:
			if subprocess.Popen(
					"ping %s -c 1 -W 2| grep '1 received'" %
					maquinas[comando]['ip'],
					shell=True,
					stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT,
					universal_newlines=True).communicate()[0] != "":
				erro = " (está na lista de defeitos)" if comando in self._see_problems("") else ""
				return [
					comando + " Ligada" + erro]
			elif comando in self._see_problems(""):
				return [comando + " DEFEITO"]
			else:
				return [comando + " Desligada"]
		else:
			return ["Está maquinas não existe", "Uso: /status_maquina laboratorio-maquina"]
			

	def _status(self, comando):
		maquinas = self._get_maquinas()
		if comando in ['lcc1', 'lcc2', 'lcc3']:
			return self._status_laboratorio(comando)
		elif comando in maquinas:
			return self._status_maquina(comando)
		else:
			return ["Uso: /status laboratorio ou /status laboratorio-maquina"]
	
	def _comandos(self, comando):
		return sorted(self.comandos.keys())

	def _get_maquinas(self):
		def unicode_to_utf(code):
			# return {i.decode().encode("utf-8"):j for i,j in code.items()}
			return {i: j for i, j in code.items()}

		arquivo = open("funcoes/maquinas.json", "r")
		maquinas = json.load(arquivo, object_hook=unicode_to_utf)
		arquivo.close()
		return maquinas

	def _see_wait(self, comando):
		wait = self.wait()
		retorno = []
		for i in wait:
			retorno.append("%s (%d): %s" % (wait[i][0], i, wait[i][1]))
		if len(retorno) == 0:
			retorno.append("Sem waits restantes")
		return retorno

	def _remove_wait(self, comando):
		wait = self.wait()
		if comando.isdigit() and int(comando) in wait:
			del wait[int(comando)]

			arquivo = open("wait.json", "w")
			json.dump(wait, arquivo)
			arquivo.close()

			return ["Sucesso"]
		else:
			return ["ID invalido ou não cadstrado", "Uso: /remove_wait id"]

	def _add_problem(self, comando):
		if not comando:
			return [
				"Formato invalido", "Uso: /add_problem laboratorio-numero"
			]
		problemas = self._see_problems("")
		problemas.append(comando)
		arquivo = open("problemas.json", "w")
		json.dump(problemas, arquivo)
		arquivo.close()
		self._remove_wait(comando)
		return ["Sucesso"]

	def _remove_problem(self, comando):
		if not comando:
			return [
				"Formato invalido", "Uso: /remove_problem laboratorio-numero"
			]
		problemas = self._see_problems("")
		if comando in problemas:
			problemas.remove(comando)
			arquivo = open("problemas.json", "w")
			json.dump(problemas, arquivo)
			arquivo.close()

			return ["Sucesso"]
		else:
			return ["Maquina não está com problema"]

	def _watch(self, comando):
		def status_laboratorio(comando):
			maquinas = self._get_maquinas()
			geral = [
				self._status_maquina(i)[0] for i in sorted(maquinas)
				if i.startswith(comando)
			]
			return geral

		comando = comando.split()
		if len(comando) == 0 or comando[0] not in ['lcc1', 'lcc2', 'lcc3']:
			if len(comando) != 0:
				yield "Está laboratorio não existe"
				yield "tente digitar apenas o nome do laboratorio"
			yield "Uso: /watch laboratorio tempo"
			return
		lcc = comando[0]
		status = status_laboratorio(lcc)
		start = time()
		limite = 60 * (float(comando[1]) if len(comando) == 2 and comando[1].isdigit() else 2)

		yield "Começando, Tempo de espera: %d min" % (limite / 60)

		while time() - start < limite:

			atual = status_laboratorio(lcc)
			for i in range(len(status)):
				if status[i] != atual[i]:
					yield ("%s: %s -> %s" % (atual[i].split(" ")[0],
					                         status[i].split(" ")[1],
					                         atual[i].split(" ")[1]))
			status = atual
			sleep(1)
		yield "Watch finalizado"

	def _agenda(self, comando):
		def date_decode(date):
			#    20181108T110000Z
			#    2018 11 08 T 11 00 00 Z
			#    08/11/2018 11:00 (00)
			#    08/11/2018 08:00 (-03)

			day = "%s/%s/%s" % (date[6:8], date[4:6], date[0:4])
			hour = "%02d:%s" % (int(date[9:11]) - 3, date[11:13])
			return [day, hour]

		def get_events(site):
			page = requests.get(site)

			soup = BeautifulSoup(page.content, 'lxml')

			for name in soup.find_all('a', attrs={'class': 'event-link'}):
				page = BeautifulSoup(requests.get("https://calendar.google.com/calendar/" + name['href']).content,
				                     'lxml')
				event = [name.text.strip()]
				for tempo in page.find_all('time'):
					event.append(date_decode(tempo['datetime']))
				#        event.append("https://calendar.google.com/calendar/"+name['href'])
				yield event

		comando = comando.split()
		if len(comando) < 1 or comando[0] not in ['lcc1', 'lcc2', 'lcc3']:
			yield "Fromato invalido"
			yield "Uso: /agenda laboratorio dd/mm"
			return
		site = {
			"lcc1":
				"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_9u9fch5o55dbgrschdeduq348c@group.calendar.google.com&mode=AGENDA",
			"lcc2":
				"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_80qc5chl59nmv2268aef8hp528@group.calendar.google.com&mode=AGENDA",
			"lcc3":
				"https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_noalttgqttm3c5pm94k3ttbj1k@group.calendar.google.com&mode=AGENDA"
		}[comando[0]]
		if len(comando) == 1:
			data = ("%02d/%02d" % (datetime.now().day, datetime.now().month))
		else:
			data = comando[1]
		yield "Vou dar uma olhada"
		if data == '*':
			cont = 0
			for i in get_events(site):
				yield ("%s: %s (%s - %s)" % (i[1][0], i[0], i[1][1], i[2][1]))
				cont += 1
			if not cont:
				yield "Hum..., parece que não temos nada previsto"
		elif re.compile("^(0[1-9]|[12][0-9]|3[01]|[1-9])/(0[1-9]|1[012]|[1-9])$").search(data) != None:
			cont = 0
			for i in get_events(site):

				if i[1][0].startswith(data):
					yield ("%s (%s - %s)" % (i[0], i[1][1], i[2][1]))
					cont += 1
				elif cont:
					return
			if not cont:
				yield "Hum..., parece que não temos nada previsto"

		else:
			yield "Data invalida"
			yield "Uso: /agenda laboratorio dd/mm"
