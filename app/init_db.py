from sqlalchemy.orm import Session
from models import User
from auth import get_password_hash
from database import Base, engine, get_session

# Criar tabelas se elas não existirem
Base.metadata.create_all(engine)

# Criar uma sessão com o banco de dados
with Session(engine) as session:
    # Verificar se já existe um usuário administrador
    admin_user = session.query(User).filter_by(is_admin=True).first()
    
    if not admin_user:
        # Criar um novo usuário administrador
        hashed_password = get_password_hash("admin123")
        new_admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
        )
        
        session.add(new_admin_user)
        session.commit()

# Agora você pode iniciar sua aplicação ou realizar outras tarefas de inicialização necessárias
