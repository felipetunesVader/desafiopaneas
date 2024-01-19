# Paneas desafio - FastAPi - Felipe Antunes

Esse é um projeto CRUD de usuários que se integra com diversas tecnologias e roda 100% via Docker.

# Pré requisitos
- Docker 

# Tecnologias usadas

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker
- ELK stack
- Prometheus
- Grafana
- Celery
- RabbitMQ

# .env exemplo
use esse arquivo que está no repositório para guardar as variáveis de ambiente.

```
# Database configurations
POSTGRES_USER=postgres
POSTGRES_PASSWORD=modric19
POSTGRES_DB=users
POSTGRES_HOST=db
POSTGRES_PORT=5432

SQLALCHEMY_DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}


# Security
SECRET_KEY=umasecretmuitosecreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=100
YOUR_EMAIL=youremailhere  - must be a microsoft account. 
YOUR_PASSWORD=yourpassword

```

# Como rodar o projeto? 

- Clone o repositório `git clone https://github.com/felipetunesVader/desafiopaneas`
  
- Crie um ambiente virtual: `python -m venv venv`
  
- Ative sua venv: `venv\Scripts\activate`
  
- Agora construa a sua Dockerfile: `docker-compose build`
  
- Rode seu compose: `docker-compose up`


# API Documentation

- Documentação disponível em: `http://localhost:8080/docs#/`
- O primeiro usuário que você cadastrar no banco terá o status de admin
- Rotas de update e delete requerem um acesso de admin para fazer tais modificações
- O valor em minutos de validade do token pode ser editado no .env
- Se você tentar cadastrar um usuário que foge dos padrões de username (a-z | 0-9) retornará padrão de username inválido
- Se você cadastrar um usuário com email fora do padrão (exemplo@.com) retornará endereço de email inválido
- O mesmo se aplica para usuários com campos únicos repetidos no request  | retornará que o campo já existe no banco.

# Rotas da API 
![image](https://github.com/felipetunesVader/desafiopaneas/assets/46753840/279068da-8078-4c72-9eef-0a89d19b11a9)

- /register - método: POST

Examplo do  Schema: 
```
  username: str = Field(..., example="felipeantunes", description="The unique username for the user.")
  email: EmailStr = Field(..., example="jota@example.com", description="The email address of the user.")
  hashed_password: str = Field(..., example="hashedpassword", description="The hashed password for the user.")
```
obs: todo usuário é cadastrado como regular(não é admin)

- /users  - método: GET
 
Retorna todos os usuários do banco


- /users/{user_id} - método: PUT - requer permissão de administrador
  
Atualiza um usuário no banco

Examplo do Schema:

```
  username: str | None = Field(default=None, example="newfelipe", description="The new username for the user if you wish to change it.")
  email: EmailStr | None = Field(default=None, example="newjota@example.com", description="The new email address for the user if you wish to change it.")
  is_active: bool | None = Field(default=None, example=True, description="Indicates whether the user is active or not.")
  is_admin: bool | None = Field(default=None, example=False, description="Indicates whether the user has admin privileges or not.")
```
- /users/{user_id} - método: DELETE - requer permissão de administrador
  
  Remove um usuário do banco e retorna o username do usuário deletado


- /login - método: POST
  
  Rota de login para exemplificar input de dados cadastrais errados e retorno do erro


- obs: os tokens de acesso JWT são gerados ao criar um novo usuário e renovados ao logar



# Como usar o RabbitMQ
acesse - `http://localhost:15672/#/`
user = guest
password = guest

# Como usar ELK stack
logstash - `http://localhost:5000/`  --obs: json parser não está 100% mas integração está funcionando
elasticsearch -  `http://localhost:9200/`
kibana -  `http://localhost:5601/app/home`


# Como usar Grafana
user = admin
password = admin
acesse - `http://localhost:3000/?orgId=1`

# Prometheus
acesse - `http://localhost:9090/`

