from Comandos import Comandos
import json
arquivo = open("comandos.json", "r")
comandos = json.load(arquivo)
arquivo.close()

for i in comandos:
	try:
		Comandos().executar(i)
	except Exception as e:
		print "Problema com %s: %s" %(i,e)
