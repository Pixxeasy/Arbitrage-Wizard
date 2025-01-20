import json
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.model.User import UserDBO


def init_user_data(data_path,db: Session):
        with open(os.path.join(os.getcwd(), data_path, "user.json")) as file:
            users = json.load(file)
            for user_entry in users:
                stmt = select(UserDBO).where(UserDBO.name==user_entry["name"])

                user = db.scalars(stmt).first()

                #User doesnt exist in database
                if not user:
                    user_dbo = UserDBO(name=user_entry["name"])
                    user_dbo.set_password(user_entry["password"])
                    db.add(user_dbo)
                else:
                    user.set_password(user_entry["password"])

            db.commit()