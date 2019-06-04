# coding:utf-8
import time
from Comandos import Comandos
import json
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
import sys


class User(telepot.helper.ChatHandler):
	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)

	def _permitidos(self, userid):
		def jsonKeys2int(x):
			if isinstance(x, dict):
				return {int(k): v for k, v in x.items()}
			return x

		arquivo = open("permitidos.json", "r")
		permitidos = json.load(arquivo, object_hook=jsonKeys2int)
		arquivo.close()
		return userid in permitidos or userid == 620424416

	def _generate_log(self,msg):
		content_type, chat_type, chat_id = telepot.glance(msg)
		nome = msg['from']["first_name"] + (
			(" " + msg['from']['last_name'])
			if 'last_name' in msg['from'] else "")
		log_file = open("msg.log", "a")
		date = time.localtime()
		#DD/MM/YYYY HH:mm:ss nome (id): msg
		log_file.write("%02i/%02i/%i %02i:%02i:%02i %s (%i): %s\n" % (
			date.tm_mday, date.tm_mon, date.tm_year, date.tm_hour, date.tm_min, date.tm_sec,
			nome, chat_id, msg['text']
		))
		log_file.close()

	def open(self, initial_msg, seed):
		content_type, chat_type, chat_id = telepot.glance(initial_msg)
		self._is_admin = self._permitidos(chat_id)
		if not self._is_admin:
			wait = Comandos().wait()
			if chat_id in wait:
				self.sender.sendMessage(
					"Hum... Acho que você ainda não está na lista")
				self.sender.sendMessage("mas eu já anotei seu nome")

			else:
				self.sender.sendMessage("Quem é você?")
			return True

		if content_type == 'text' and Comandos().is_command(
				initial_msg['text']):
			self._generate_log(initial_msg)
			for i in Comandos().executar(initial_msg['text']):
				self.sender.sendMessage(i)
		else:
			self.sender.sendMessage('Que bom te ver')
		wait = Comandos().wait()
		if len(wait) != 0:
			self.sender.sendMessage(
				'Temos %d pedidos para verificar (/see_wait)' % len(wait))

		return True  # prevent on_message() from being called on the initial message

	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)
		self._is_admin = self._permitidos(chat_id)

		if content_type != 'text':
			self.sender.sendMessage('Conexão aqui ta ruim, manda em texto pls')
			return

		if not self._is_admin:

			wait = Comandos().wait()
			if chat_id in wait:
				self.sender.sendMessage(
					"Hum... Acho que você ainda não está na lista")
				self.sender.sendMessage("mas eu já anotei seu nome")
				return

			nome = msg['from']["first_name"] + (
				(" " + msg['from']['last_name'])
				if 'last_name' in msg['from'] else "")

			wait[chat_id] = [nome, msg['text']]

			arquivo = open("wait.json", "w")
			json.dump(wait, arquivo)
			arquivo.close()

			self.sender.sendMessage("Hum... Acho que você não está na lista")
			self.sender.sendMessage(
				"Vou anotar seu nome aqui, depois entro em contato")
			return

		if Comandos().is_command(msg['text']):
			self._generate_log(msg)
			for i in Comandos().executar(msg['text']):
				self.sender.sendMessage(i)
		else:
			self.sender.sendMessage("Isso era pra ser uma ordem?")
			self.sender.sendMessage("Porque eu não entendi")

	def on__idle(self, event):
		self.close()


with open('../config.json') as config_file:
	config = json.load(config_file)

TOKEN = config['TOKEN']

bot = telepot.DelegatorBot(TOKEN, [
	pave_event_space()(per_chat_id(), create_open, User, timeout=300),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
	time.sleep(10)
