from sqlalchemy import create_engine, text

# Substitua pela sua string de conexão real do arquivo database.py
engine = create_engine("postgresql://postgres:modric19@localhost:5432/users")
print("Iniciando o teste de conexão...")

try:
    print("Tentando conectar ao banco de dados...")
    with engine.connect() as connection:
        print("Conectado ao banco de dados, executando consulta...")
        result = connection.execute(text("SELECT 'Conexão bem-sucedida!'"))
        for row in result:
            print(row)  # Deve imprimir: ('Conexão bem-sucedida!',)
        print("Consulta executada com sucesso!")
except Exception as e:
    print("Exceção capturada durante a conexão ou consulta:", e)

print("Teste de conexão finalizado.")
