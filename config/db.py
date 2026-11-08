import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME", "biblioteca_db")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

print(f"Connecting to database at {DATABASE_URL}")

# En SQLite check_same_thread=False es necesario; para MySQL/otros se omite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def crear_db_y_tablas():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Error en la base de datos: {e}")

def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            print(f"Error en la sesión de la base de datos: {e}")
            raise
