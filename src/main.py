#coding:utf-8

import time
from Comandos import Comandos
import json
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space

class User(telepot.helper.ChatHandler):

	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)

	def _permitido(self,userid):
		def jsonKeys2int(x):
			if isinstance(x, dict):
					return {int(k):v for k,v in x.items()}
			return x
		arquivo = open("permitidos.json","r")
		permitidos = json.load(arquivo,object_hook=jsonKeys2int)
		arquivo.close()
		return userid in permitidos

	def open(self, initial_msg, seed):
		content_type, chat_type, chat_id = telepot.glance(initial_msg)
		self._is_admin = chat_id in Comandos().permitidos()
		if not self._is_admin:
			self.sender.sendMessage("Quem é você?")
			return True
		self.sender.sendMessage('Que bom te ver')
		if content_type == 'text' and Comandos().is_command(initial_msg['text']):
			for i in Comandos().executar(initial_msg['text']):
				self.sender.sendMessage(i)
		return True  # prevent on_message() from being called on the initial message

	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)

		if content_type != 'text':
			self.sender.sendMessage('Conexão aqui ta ruim, manda em texto pls')
			return

		if not self._is_admin:
			self.sender.sendMessage("Hum... Acho que você não está na lista")
			self.sender.sendMessage("Vou anotar seu nome aqui, depois entro em contato")
			
		
		if Comandos().is_command(msg['text']):
			for i in Comandos().executar(msg['text']):
				self.sender.sendMessage(i)
		else:
			self.sender.sendMessage("Isso era pra ser uma ordem?")
			self.sender.sendMessage("Porque eu não entendi")
		

	def on__idle(self):
		self.sender.sendMessage('Já que você não quer nada comigo eu vou fazer outra coisa.')
		self.close()
#LCCControllerBot
TOKEN = "685454659:AAE3IoeYN-dZyabaeDxIQLaxX-9jid-Pd6k"

bot = telepot.DelegatorBot(TOKEN, [
	pave_event_space()(
		per_chat_id(), create_open, User, timeout=300),
])
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
	time.sleep(10)
