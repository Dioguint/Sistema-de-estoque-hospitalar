import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "estoque_hospitalar"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Cria o banco e as tabelas caso não existam."""
    cfg = {**DB_CONFIG}
    cfg.pop("database")
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4")
    cur.execute(f"USE {DB_CONFIG['database']}")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            nome        VARCHAR(120)   NOT NULL,
            categoria   VARCHAR(80),
            quantidade  INT            NOT NULL DEFAULT 0,
            unidade     VARCHAR(20)    NOT NULL DEFAULT 'un',
            estoque_min INT            NOT NULL DEFAULT 5,
            criado_em   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lotes (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            produto_id  INT            NOT NULL,
            lote        VARCHAR(60),
            validade    DATE           NOT NULL,
            quantidade  INT            NOT NULL DEFAULT 0,
            criado_em   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            produto_id  INT            NOT NULL,
            lote_id     INT,
            tipo        ENUM('entrada','saida') NOT NULL,
            quantidade  INT            NOT NULL,
            observacao  VARCHAR(255),
            data        TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (lote_id)    REFERENCES lotes(id)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✔  Banco de dados inicializado com sucesso.\n")
