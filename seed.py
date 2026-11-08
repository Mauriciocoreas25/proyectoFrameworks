"""
Script para inicializar la base de datos con roles, usuarios iniciales y datos de catálogo
para demostración y pruebas inmediatas según los requisitos del docente.
"""
from sqlmodel import Session, select
from config.db import engine, crear_db_y_tablas
from models.rol import Rol
from models.usuario import Usuario
from models.categoria import Categoria
from models.autor import Autor
from models.libro import Libro
from lib.pwd import get_password_hash

def poblar_datos():
    crear_db_y_tablas()
    with Session(engine) as session:
        # 1. Crear Roles si no existen
        roles_data = [
            {"id": 1, "nombre": "Administrador", "descripcion": "Control total del sistema y usuarios"},
            {"id": 2, "nombre": "Bibliotecario", "descripcion": "Gestión de catálogo, préstamos y devoluciones"},
            {"id": 3, "nombre": "Lector", "descripcion": "Consulta de catálogo y préstamos personales"},
        ]
        for r in roles_data:
            existente = session.exec(select(Rol).where(Rol.id == r["id"])).first()
            if not existente:
                rol = Rol(id=r["id"], nombre=r["nombre"], descripcion=r["descripcion"])
                session.add(rol)
        session.commit()
        print("Roles asegurados.")

        # 2. Crear Usuarios iniciales
        usuarios_data = [
            {
                "username": "admin",
                "password": get_password_hash("admin123"),
                "nombre": "Administrador",
                "apellido": "Sistema",
                "telefono": "77778888",
                "correo": "admin@biblioteca.com",
                "id_rol": 1,
            },
            {
                "username": "bibliotecario",
                "password": get_password_hash("biblio123"),
                "nombre": "Carlos",
                "apellido": "Rovira",
                "telefono": "77779999",
                "correo": "bibliotecario@biblioteca.com",
                "id_rol": 2,
            },
            {
                "username": "lector",
                "password": get_password_hash("lector123"),
                "nombre": "Juan",
                "apellido": "Pérez",
                "telefono": "77770000",
                "correo": "lector@biblioteca.com",
                "id_rol": 3,
            },
        ]
        for u in usuarios_data:
            existente = session.exec(select(Usuario).where(Usuario.username == u["username"])).first()
            if not existente:
                usuario = Usuario(**u)
                session.add(usuario)
        session.commit()
        print("Usuarios asegurados.")

        # 3. Categorías iniciales
        cats_data = [
            {"nombre": "Informática y Software", "descripcion": "Libros de programación, frameworks y arquitectura"},
            {"nombre": "Ciencia Ficción", "descripcion": "Novelas y relatos futuristas"},
            {"nombre": "Literatura Clásica", "descripcion": "Obras cumbres de la literatura universal"},
        ]
        for c in cats_data:
            existente = session.exec(select(Categoria).where(Categoria.nombre == c["nombre"])).first()
            if not existente:
                cat = Categoria(**c)
                session.add(cat)
        session.commit()
        print("Categorías aseguradas.")

        # 4. Autores iniciales
        autores_data = [
            {"nombre": "Robert C. Martin", "nacionalidad": "Estadounidense", "biografia": "Autor y consultor de desarrollo de software conocido como Uncle Bob"},
            {"nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana", "biografia": "Premio Nobel de Literatura 1982"},
            {"nombre": "Isaac Asimov", "nacionalidad": "Rusa-Estadounidense", "biografia": "Escritor y bioquímico prolífico"},
        ]
        for a in autores_data:
            existente = session.exec(select(Autor).where(Autor.nombre == a["nombre"])).first()
            if not existente:
                autor = Autor(**a)
                session.add(autor)
        session.commit()
        print("Autores asegurados.")

        # 5. Libros iniciales
        cat_info = session.exec(select(Categoria).where(Categoria.nombre == "Informática y Software")).first()
        autor_bob = session.exec(select(Autor).where(Autor.nombre == "Robert C. Martin")).first()
        if cat_info and autor_bob:
            libro1 = session.exec(select(Libro).where(Libro.titulo == "Clean Code")).first()
            if not libro1:
                l1 = Libro(
                    titulo="Clean Code",
                    isbn="9780132350884",
                    descripcion="Manual de estilo para desarrollo ágil de software",
                    id_autor=autor_bob.id,
                    id_categoria=cat_info.id,
                    total_ejemplares=2,
                    ejemplares_disponibles=2,
                    disponible=True,
                )
                session.add(l1)

        cat_lit = session.exec(select(Categoria).where(Categoria.nombre == "Literatura Clásica")).first()
        autor_gabo = session.exec(select(Autor).where(Autor.nombre == "Gabriel García Márquez")).first()
        if cat_lit and autor_gabo:
            libro2 = session.exec(select(Libro).where(Libro.titulo == "Cien Años de Soledad")).first()
            if not libro2:
                l2 = Libro(
                    titulo="Cien Años de Soledad",
                    isbn="9780307474728",
                    descripcion="Obra maestra de realismo mágico",
                    id_autor=autor_gabo.id,
                    id_categoria=cat_lit.id,
                    total_ejemplares=1,
                    ejemplares_disponibles=1,
                    disponible=True,
                )
                session.add(l2)

        session.commit()
        print("Libros asegurados.")
        print("¡Base de datos lista para pruebas!")

if __name__ == "__main__":
    poblar_datos()
