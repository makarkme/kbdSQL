import os
import json
import uuid
import cmd
import sys
from ast import literal_eval
from shlex import split
from btree import *
from indexation import *
from collection import *
from database import *

class DBShell(cmd.Cmd):
    intro = 'JSON DB Shell. Type help or ? to list commands.\n'
    prompt = 'jdb> '
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_collection = None
    
    def do_use(self, arg):
        """Switch to a collection: USE <collection_name>"""
        self.current_collection = self.db.get_collection(arg)
        print(f"Switched to collection '{arg}'")
    
    def do_insert(self, arg):
        """Insert document: INSERT {json_document}"""
        if not self.current_collection:
            print("No collection selected! Use USE first")
            return
            
        try:
            # Заменяем одинарные кавычки на двойные для корректного JSON
            arg = arg.replace("'", '"')
            doc = json.loads(arg)
            doc_id = self.current_collection.insert(doc)
            print(f"Inserted document ID: {doc_id}")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_index(self, arg):
        """Create index: INDEX <field_name>"""
        if not self.current_collection:
            print("No collection selected! Use USE first")
            return
            
        self.current_collection.create_index(arg)
        print(f"Index created on field '{arg}'")
    
    def do_find(self, arg):
        """Find documents: FIND {query_json}"""
        if not self.current_collection:
            print("No collection selected! Use USE first")
            return
            
        try:
            query = literal_eval(arg)
            results = self.current_collection.find(query)
            
            for doc in results:
                print(json.dumps(doc, indent=2))
            print(f"\nFound {len(results)} documents")
        except Exception as e:
            print(f"Query error: {e}")
    
    def do_exit(self, arg):
        """Exit the database shell"""
        print("Exiting...")
        sys.exit(0)
    
    def default(self, line):
        try:
            # Разделяем команду и аргументы по первому пробелу
            parts = line.split(' ', 1)
            command = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ''
        except:
            command, arg = line.upper(), ''

        if command in ['USE', 'INSERT', 'INDEX', 'FIND', 'EXIT']:
            try:
                getattr(self, 'do_' + command.lower())(arg)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Unknown command: {command}")
    
    def emptyline(self):
        pass

def main():
    if len(sys.argv) > 2:
        print("Usage: jdb <database_name>")
        return
    
    #db_name = sys.argv[1]
    db_name = "test_db"
    db = Database(db_name)
    DBShell(db).cmdloop()

if __name__ == "__main__":
    main()