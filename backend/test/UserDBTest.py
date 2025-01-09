from sqlmodel import create_engine, Session
from database.model.User import UserDBO
from database.model.BaseModel import Base

engine = create_engine('sqlite:///:memory:')

def test_userdbo_create():
    Base.metadata.create_all(engine)
    user = {"name": "test", "password": "1234"}
    dbo = UserDBO(name=user["name"])
    dbo.set_password(user["password"])

    with Session(engine) as session:
        session.add(dbo)
        session.commit()
        #session.refresh(dbo)
        print(dbo.guid)

