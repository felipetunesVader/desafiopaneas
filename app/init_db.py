# init_db.py

from main import create_user
from schemas import UserCreate
from database import SessionLocal

# Cria uma sessão do banco de dados
session = SessionLocal()

# Cria um usuário administrador
admin_user = UserCreate(
    username="admin",
    email="admin@example.com",
    password="adminpassword"
)

# Chamada à função create_user para adicionar o usuário administrador
create_user(user=admin_user, session=session)

# Fecha a sessão
session.close()
