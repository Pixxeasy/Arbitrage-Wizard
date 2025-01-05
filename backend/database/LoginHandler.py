from model.User import  User
from model.api.LoginCredentials import LoginCredentials
from sqlalchemy.orm.session import Session
from util import create_HMAC

def checkPassword(password, salt, hashed_password):
    hash = create_HMAC(password, salt)
    return hash == hashed_password

def handleLogin(credentials: LoginCredentials, session: Session):
    user = session.query(User).filter(User.name == credentials.username).one()
    if user.check_password(credentials.password, user.salt, user.password):
        return


