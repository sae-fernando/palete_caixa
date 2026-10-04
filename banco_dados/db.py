from sqlalchemy import Engine
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv("db_palete_caixa.env", override=True)

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("USER")
DATABASE = os.getenv("DATABASE")
PASS = os.getenv("PASS")

url = f"postgresql+psycopg2://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}"
def get_engine() -> Engine:
    return create_engine(url, connect_args={"sslmode": "prefer"}, 
                         pool_pre_ping=True)

def disconnect_engine(engine: Engine):
    engine.dispose()

def criar_usuario(dados: dict, senha: str):
    """Insere novo usuÃ¡rio. Retorna None em caso de sucesso ou mensagem de erro."""
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    print("Criando usuÃ¡rio...")
    print(dados)
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    f"""
                    INSERT INTO clientes
                        (cnpj, razao_social, nome_fantasia, nome_contato,
                         telefone_contato, email_contato, nome_usuario, senha_hash)
                    VALUES ('{dados.get('cnpj', None)}', 
                            '{dados.get('razao_social', None)}', 
                            '{dados.get('nome_fantasia', None)}', 
                            '{dados.get('nome_contato', None)}', 
                            '{dados.get('telefone_contato', None)}', 
                            '{dados.get('email_contato', None)}', 
                            '{dados.get('nome_usuario', None)}',
                            '{senha_hash}'
                            )
                    """
                )
            )
        print("UsuÃ¡rio criado com sucesso.")
        disconnect_engine(engine)
        return None
    except IntegrityError as e:
        diag = getattr(e.orig, "diag", None)
        constraint = (diag.constraint_name if diag else "") or ""
        if "cnpj" in constraint:
            return "CNPJ jÃ¡ cadastrado."
        if "nome_usuario" in constraint:
            return "Nome de usuÃ¡rio jÃ¡ em uso."
        mensagem = diag.message_primary if diag else str(e.orig)
        return f"Erro de integridade: {mensagem}"

def autenticar(nome_usuario: str, senha: str):
    """Retorna dict do usuÃ¡rio se credenciais vÃ¡lidas e status=ativo, senÃ£o None."""
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, nome_usuario, razao_social, status, tipo, senha_hash "
                f"FROM clientes WHERE nome_usuario = '{nome_usuario}' AND deletado = False"
            )).mappings().first()
    if row and bcrypt.checkpw(senha.encode(), row["senha_hash"].encode()):
        if row["status"] == "ativo":
            return dict(row)
        return {"erro": f"Acesso negado â€” status da conta: {row['status']}"}
    return {"erro": "Credenciais invÃ¡lidas."}

def listar_usuarios():
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, nome_usuario, razao_social, nome_contato, email_contato, "
                "status, tipo, data_criacao "
                "FROM clientes WHERE deletado = False ORDER BY razao_social"
            )
        ).mappings().all()
    return [dict(r) for r in rows]

def deletar_usuario(usuario_id: int):
    """Soft-delete: marca deletado=TRUE e registra a data."""
    engine = get_engine()
    with engine.begin() as conn:    # begin() abre transaÃ§Ã£o e faz commit automÃ¡tico ao final
        conn.execute(
            text("UPDATE clientes SET deletado = TRUE, deletado_em = :agora WHERE id = :id"),
            {"agora": datetime.now(), "id": usuario_id},
        )

def alterar_senha(usuario_id: int, nova_senha: str):
    """Atualiza senha do usuÃ¡rio com nova hash."""
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(f"UPDATE clientes SET senha_hash = '{nova_hash}' WHERE id = {usuario_id}")
        )

def listar_tipos_status() -> list[str]:
    """Retorna lista de nome_status da tabela tipos_status para os dropdowns de status
    na pÃ¡gina de alteraÃ§Ã£o de status e criaÃ§Ã£o de usuÃ¡rio."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT nome_status FROM tipos_status ORDER BY nome_status")).all()
    return [r[0] for r in rows]

def listar_tipos_usuario() -> list[str]:
    """Retorna lista de tipo da tabela tipos_usuarios para os dropdowns de tipo na 
    pÃ¡gina de criaÃ§Ã£o de usuÃ¡rio."""
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT tipo FROM tipos_usuarios ORDER BY tipo")).all()
    return [r[0] for r in rows]

def alterar_status(usuario_id: int, novo_status: str):
    """Atualiza o status (ativo/inativo) de um usuÃ¡rio."""
    engine = get_engine()
    with engine.begin() as conn:    # begin() abre transaÃ§Ã£o e faz commit automÃ¡tico ao final
        conn.execute(
            text(f"UPDATE clientes SET status = '{novo_status}' WHERE id = {usuario_id}")
        )