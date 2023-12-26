from src.services.user import RepositoryUserDB
from src.services.file import RepositoryFileDB
from src.models.models import User as UserModel
from src.models.models import File as FileModel
from src.schemes.user_schemes import UserRegister


class RepositoryUser(RepositoryUserDB[UserModel, UserRegister]):
    pass

class RepositoryFile(RepositoryFileDB[UserModel]):
    pass

user_service = RepositoryUser(UserModel)
file_service = RepositoryFile(FileModel)
