from sqlalchemy import create_engine
import os
from model.BaseModel import Base
from sqlalchemy.orm import sessionmaker
from model.User import User
from model.exchanges.BaseExchange import BaseExchange
import json
import uuid
from .util import create_HMAC

namespace = uuid.UUID("1b4b0697-54a1-4e3b-b3c4-ca83f29e2499")

class DBConnector():
    def __init__(self, path):
        self.path = path
        self.sql_path = "initData"
        pass

    def connect(self):
        self.engine = create_engine(f"sqlite:///{self.path}", echo=True)


        self.buildStructure()
        self.initData()
      

    def buildStructure(self):
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def initData(self):
        if self.session.query(User).count() == 0:
            with open(os.path.join(os.getcwd(),self.sql_path, "user.json")) as file:
                users = json.load(file)
                
                users = [{**u, "guid": str(uuid.uuid5(namespace, f"user:{u['name']}")), "salt": str(uuid.uuid4())} for u in users]
                users = [{**u, "password": create_HMAC(u["password"], u["salt"])} for u in users]
                users = [User(**u) for u in users]
   
                self.session.add_all(users)
                self.session.commit()

        