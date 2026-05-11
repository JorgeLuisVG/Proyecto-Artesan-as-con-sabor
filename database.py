import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("artesanias.db")


def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def _ensure_column(cur, table, column, definition):
    columnas = {row["name"] for row in cur.execute(f"PRAGMA table_info({table})")}
    if column not in columnas:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def crearTablas():
    con = conectar()
    cur = con.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT DEFAULT '',
            telefono TEXT NOT NULL,
            descuento REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombrePlatillo TEXT NOT NULL,
            procedimiento TEXT,
            precio REAL NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS ingredientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recetaID INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            cantidad TEXT,
            FOREIGN KEY (recetaID) REFERENCES recetas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clienteID INTEGER,
            direccion TEXT,
            fecha TEXT NOT NULL,
            anticipo REAL DEFAULT 0,
            subtotal REAL DEFAULT 0,
            total REAL DEFAULT 0,
            tipo TEXT DEFAULT 'Pedido simple',
            estado TEXT DEFAULT 'Pendiente',
            notas TEXT DEFAULT '',
            FOREIGN KEY (clienteID) REFERENCES clientes(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS pedidosReceta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedidoID INTEGER NOT NULL,
            recetaID INTEGER NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (pedidoID) REFERENCES pedidos(id) ON DELETE CASCADE,
            FOREIGN KEY (recetaID) REFERENCES recetas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedidoID INTEGER NOT NULL,
            nombreEvento TEXT,
            extras TEXT,
            FOREIGN KEY (pedidoID) REFERENCES pedidos(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha);
        CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado);
        CREATE INDEX IF NOT EXISTS idx_recetas_nombre ON recetas(nombrePlatillo);
        CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);
        """
    )

    # Small migrations for databases created with previous classroom versions.
    _ensure_column(cur, "clientes", "direccion", "TEXT DEFAULT ''")
    _ensure_column(cur, "pedidos", "clienteID", "INTEGER")
    _ensure_column(cur, "pedidos", "estado", "TEXT DEFAULT 'Pendiente'")
    _ensure_column(cur, "pedidos", "notas", "TEXT DEFAULT ''")

    con.commit()
    con.close()


if __name__ == "__main__":
    crearTablas()
    print(f"Base de datos lista en: {DB_PATH}")
