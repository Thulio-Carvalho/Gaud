#coding: utf-8

from pymongo import MongoClient
import logging

class PermissionsHandler(object):

    def __init__(self):
        logging.basicConfig(
            filename='server.log', 
            level=logging.INFO)

        logging.info('Setting up mongo')
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.gaudDB
        self.users = self.db.users_collection
        self.roles = self.db.roles_collection


    def addUser(self, uid, role):
        logging.info('Adding user with uid %s' % str(uid))
        newUser = {
                "_id": uid,
                "role": role,
                "extra_perms": []
               }
        self.users.insert_one(newUser)

    def __findUser(self, uid):
        logging.info('Finding user with uid %s' % str(uid))
        return self.users.find_one({"_id": uid})

    def retrieveUserRole(self, uid):
        logging.info('Retrieving role for uid %s' % str(uid))
        user = self.__findUser(uid)
        return user['role']
    
    def retrieveUserPermissions(self, uid):
        logging.info('Retrieving permissions for uid %s' % str(uid))
        user = self.__findUser(uid)
        role = self.roles.find_one({"role": user['role']})
        return role['permissions']
    
