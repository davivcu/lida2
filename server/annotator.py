################################################################################
# IMPORTS
################################################################################

# >>>> Native <<<<
import os
import collections
import sys
import json
import copy
import time
from typing import Dict, List, Any, Tuple, Hashable, Iterable, Union
import functools

# >>>> Flask <<<<
from flask import Flask, jsonify, request
from flask_cors import CORS

# >>>> Local <<<<
from utils import load_json_file, save_json_file



################################################################################
# CODE
################################################################################

class MultiAnnotator(object):

    """
    The class that governs several DialogueAnnotator(s)
    """
    __GOLD_FILE_NAME = "GOLD_" + str( time.strftime("%Y%m%d-%H%M%S") )
    __DEFAULT_NAME = "FILE_"

    def __init__(self, path):
        self.path = path
        self.allFiles = { MultiAnnotator.__GOLD_FILE_NAME : DialogueAnnotator(self.path, MultiAnnotator.__GOLD_FILE_NAME) }
        self.filesAdded = 0

        self.__load_all_jsons(self.path)

    def get_all_files(self, dialogueId):
        """
        Gets all dialogues
        """
        outList = []

        for fileName, fileObject in self.allFiles.items():

            temp = fileObject.get_dialogue(id=dialogueId)["dialogue"]

            if temp:
                outList.append( temp )

        return outList

    def add_dialogue_file( self, jsonObject, fileName=None ):
        """
        adds a new DialogueAnnotator
        """
        if not fileName:
            fileName = self.__get_new_file_id()
            self.filesAdded += 1

        save_json_file( obj=jsonObject, path= os.path.join( self.path, fileName ) )
        self.allFiles[MultiAnnotator.__GOLD_FILE_NAME].update_dialogues(jsonObject)

        self.allFiles[ fileName ] = DialogueAnnotator( self.path, fileName )
        self.save()

    def get_metadata(self):
        """
        returns the names of the files
        """
        return { "names" : [ {"name":x} for x,_ in self.allFiles.items() ] }

    def get_dialogue_names(self) -> List[str]:
        """Gets a list of the names of the dialogues and checks that all JSON files have the same dialogues."""

        allDialogues = []

        for fname, dialogObj in self.allFiles.items():

            if fname == self.__GOLD_FILE_NAME:
                continue

            allDialogues.append(dialogObj.get_dialogues())

        for dialogue in allDialogues:

            for key in dialogue:

                assert all(key in d for d in allDialogues), "Dialogue in {} that's not in all other dialogues".format(dialogue)

        # By this point we know that all of the dialogues must have the same keys (i.e. dialogue names)
        return list(allDialogues[0].keys())

    def get_dialogues_metadata(self) -> List[Tuple[str, List[str]]]:
        """
        Gets a list of tuples of the dialogue names in each file and a list of the filenames that contain those
        dialogues.
        """
        allDialogues = collections.defaultdict(list)

        for fname, dialogObj in self.allFiles.items():

            if fname == self.__GOLD_FILE_NAME:
                continue

            for dialogueName, turnList in dialogObj.get_dialogues().items():

                allDialogues[dialogueName].append(fname)

        return [(key, val) for key, val in allDialogues.items()]

    def get_gold_dialogue_metadata(self):
        """Gets the metadata of the gold dialogue file"""
        return self.allFiles[self.__GOLD_FILE_NAME].get_dialogues_metadata()

    def dialogue_file_function_call(self, methodName, fileId=None, **args):
        """
        Makes the relevant call from the single dialogue file
        """
        if not fileId:
            fileId = MultiAnnotator.__GOLD_FILE_NAME

        temp = self.allFiles.get( fileId )

        method = getattr(temp, methodName)

        return method(**args)

    def __getattr__(self, attr):
        """
        Magic Methods++
        """

        temp = functools.partial( self.dialogue_file_function_call, attr )

        return temp

    def __load_all_jsons(self, targetPath):
        """
        loads all files from directory
        """
        currentDir = os.path.join( os.getcwd(), targetPath)

        files = [ x for x in os.listdir( currentDir ) if os.path.isfile( os.path.join(currentDir, x) ) ]

        for file in files:

            if file.endswith('.json'):
                jsonObject = load_json_file( os.path.join(currentDir,file) )
                self.add_dialogue_file( jsonObject=jsonObject, fileName=file )

    def __get_new_file_id(self):
        """
        Creates a new file ID
        """
        return self.__DEFAULT_NAME + str( self.filesAdded ) + ".json"








class DialogueAnnotator(object):
    """
    class that handles everything which relates to managing a single dialogues file
    """
    __DEFAULT_FILENAME="USER_1.json"

    __SESSION_USER = "USER_1"


    class dialogues(object):

        def __getitem__(self,key):
            return getattr(self,key)
    
    __dialogues = dialogues()

    def __init__( self, filePath, fileName=None, dialogues=None ):
        """
        """
        self.set_dialogues( self.__SESSION_USER, dialogues )
        self.set_file( filePath, fileName )
        self.addedDialogues = 0

    #def get_file_name(self):
        """
        """
    #    return {"name": self.__fileName}

    def change_file_name(self, newName, remove=False):
        """
        check if the new user has a workspace otherwise it's created
        """
        DialogueAnnotator.__SESSION_USER = newName

        try: 
            self.__dialogues[DialogueAnnotator.__SESSION_USER]
        except:
            self.set_dialogues(newName)

        #oldFileName = self.__fileName
        self.__fileName = newName

        self.save(newName)

        #if remove:
        #    os.remove( os.path.join( self.__filePath, oldFileName ) )

    def set_dialogues( self, newName, dialogues=None ):
        """
        """
        #DialogueAnnotator.__SESSION_USER = newName

        print("updated",newName)

        self.toBeInserted = dialogues if dialogues else {}

        setattr(DialogueAnnotator.__dialogues, DialogueAnnotator.__SESSION_USER, self.toBeInserted )

        print(self.__dialogues[DialogueAnnotator.__SESSION_USER])

    def set_file( self, filePath, fileName=None ):
        """
        sets the file and tries to load it to use
        """
        self.__filePath = filePath

        if fileName:
            self.__fileName = fileName
            try:
                self.__dialogues[DialogueAnnotator.__SESSION_USER] = load_json_file( os.path.join( self.__filePath, self.__fileName ) )
            except FileNotFoundError:
                save_json_file( obj=self.__dialogues[DialogueAnnotator.__SESSION_USER], path=os.path.join( self.__filePath, self.__fileName ) )

        else:
            self.__fileName = DialogueAnnotator.__DEFAULT_FILENAME

    def get_dialogue(self, user, id: Hashable) -> Dict[str, Any]:
        """Gets a single dialogue"""
        DialogueAnnotator.__SESSION_USER = user

        return {"dialogue": self.__dialogues[DialogueAnnotator.__SESSION_USER].get(id)}

    def get_dialogues(self, id=None):
        """
        Returns all dialogues or specific dialogue (as dict {id: dialogue} )
        """
        DialogueAnnotator.__SESSION_USER = user

        return self.__dialogues[DialogueAnnotator.__SESSION_USER]

    def get_dialogues_metadata(self, user):
        """
        Gets the name of dialogues, returns a list
        """
        DialogueAnnotator.__SESSION_USER = user

        metadata = []

        for dialogueID, dialogueTurnList in self.__dialogues[DialogueAnnotator.__SESSION_USER].items():

            metadata.append({"id": dialogueID, "num_turns": len(dialogueTurnList)})

        return metadata


    def update_dialogue(self, user, id, newDialogue ):
        """
        updates the dialogue
        """
        DialogueAnnotator.__SESSION_USER = user

        self.__dialogues[DialogueAnnotator.__SESSION_USER][ id ] = newDialogue

        return {"status" : "success"}


    def update_dialogues(self, user, newDialogues):
        """
        updates all the dialogues with a new dictionary
        """
        DialogueAnnotator.__SESSION_USER = user

        for dId, newDialogue in newDialogues.items():

            temp = self.__dialogues[DialogueAnnotator.__SESSION_USER].get( dId )
            if temp:
                newDialogue = newDialogue if len(newDialogue)>len(temp) else temp


            self.__dialogues[DialogueAnnotator.__SESSION_USER][ dId ] = newDialogue

        return True


    def update_dialogue_name(self, user, id, newName):
        """
        updates the dialogue name
        """
        DialogueAnnotator.__SESSION_USER = user

        self.__dialogues[DialogueAnnotator.__SESSION_USER][newName] = copy.deepcopy( self.__dialogues[DialogueAnnotator.__SESSION_USER][id] )

        del self.__dialogues[DialogueAnnotator.__SESSION_USER][id]


    def add_new_dialogue(self, user, dialogue=None, id=None):
        """
        creates a new dialogue with an optional name
        """
        DialogueAnnotator.__SESSION_USER = user

        self.addedDialogues += 1

        if not id:
            id = self.__get_new_dialogue_id()


        self.__dialogues[DialogueAnnotator.__SESSION_USER][ id ] = dialogue if dialogue else []

        return {"id":id}


    def delete_dialogue(self, user, id):
        """
        Deletes a dialogue
        """
        DialogueAnnotator.__SESSION_USER = user

        del self.__dialogues[DialogueAnnotator.__SESSION_USER][ id ]


    def save(self, user):
        """
        Save the dialogues dictionary
        """
        DialogueAnnotator.__SESSION_USER = user

        save_json_file( obj=self.__dialogues[DialogueAnnotator.__SESSION_USER], path=os.path.join( self.__filePath, self.__fileName+".json" ) )




    def __get_new_dialogue_id(self):
        """
        """
        newId = "Dialogue" + str(self.addedDialogues)

        return newId




        # save_json_file( obj=self.__dialogues, path=self.__filePath )




################################################################################
# MAIN
################################################################################







# EOF
