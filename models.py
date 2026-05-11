from datetime import date

from database import conectar, crearTablas


crearTablas()


def _to_float(valor, default=0.0):
    try:
        if valor is None or valor == "":
            return default
        return float(str(valor).replace(",", "."))
    except ValueError:
        return default


def _to_int(valor, default=1):
    try:
        numero = int(valor)
        return numero if numero > 0 else default
    except (TypeError, ValueError):
        return default


def _normalizar_descuento(valor):
    descuento = _to_float(valor)
    if descuento > 1:
        descuento = descuento / 100
    return max(0, min(descuento, 0.95))


def _normalizar_ingredientes(ingredientes):
    normalizados = []
    for item in ingredientes or []:
        if isinstance(item, dict):
            for nombre, cantidad in item.items():
                if str(nombre).strip():
                    normalizados.append((str(nombre).strip(), str(cantidad).strip()))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            nombre, cantidad = item[0], item[1]
            if str(nombre).strip():
                normalizados.append((str(nombre).strip(), str(cantidad).strip()))
        elif str(item).strip():
            normalizados.append((str(item).strip(), ""))
    return normalizados


def _normalizar_recetas_pedido(recetas):
    normalizadas = []
    for item in recetas or []:
        receta_id = None
        cantidad = 1
        if isinstance(item, dict):
            receta_id = item.get("recetaID") or item.get("receta_id") or item.get("id")
            cantidad = item.get("cantidad", 1)
        elif isinstance(item, (list, tuple)) and len(item) >= 1:
            receta_id = item[0]
            cantidad = item[1] if len(item) > 1 else 1
        if receta_id is not None:
            normalizadas.append((int(receta_id), _to_int(cantidad)))
    return normalizadas


def insertarCliente(nombre, direccion, telefono, descuento=0):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO clientes (nombre, direccion, telefono, descuento)
        VALUES (?, ?, ?, ?)
        """,
        (nombre.strip(), direccion.strip(), str(telefono).strip(), _normalizar_descuento(descuento)),
    )
    cliente_id = cur.lastrowid
    con.commit()
    con.close()
    return cliente_id


def obtenerClientes(busqueda=""):
    con = conectar()
    cur = con.cursor()
    patron = f"%{busqueda.strip().lower()}%"
    cur.execute(
        """
        SELECT id, nombre, COALESCE(direccion, '') AS direccion, telefono,
               COALESCE(descuento, 0) AS descuento
        FROM clientes
        WHERE LOWER(nombre) LIKE ? OR LOWER(telefono) LIKE ? OR LOWER(COALESCE(direccion, '')) LIKE ?
        ORDER BY nombre COLLATE NOCASE
        """,
        (patron, patron, patron),
    )
    datos = cur.fetchall()
    con.close()
    return datos


def obtenerClientePorId(clienteID):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, nombre, COALESCE(direccion, '') AS direccion, telefono,
               COALESCE(descuento, 0) AS descuento
        FROM clientes
        WHERE id = ?
        """,
        (clienteID,),
    )
    dato = cur.fetchone()
    con.close()
    return dato


def actualizarCliente(clienteID, nombre, direccion, telefono, descuento=0):
    con = conectar()
    con.execute(
        """
        UPDATE clientes
        SET nombre = ?, direccion = ?, telefono = ?, descuento = ?
        WHERE id = ?
        """,
        (nombre.strip(), direccion.strip(), str(telefono).strip(), _normalizar_descuento(descuento), clienteID),
    )
    con.commit()
    con.close()


def eliminarCliente(clienteID):
    con = conectar()
    con.execute("DELETE FROM clientes WHERE id = ?", (clienteID,))
    con.commit()
    con.close()


def insertarReceta(nombre, procedimiento, precio, ingredientes=None):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO recetas (nombrePlatillo, procedimiento, precio)
        VALUES (?, ?, ?)
        """,
        (nombre.strip(), procedimiento.strip(), _to_float(precio)),
    )
    receta_id = cur.lastrowid
    for ingrediente, cantidad in _normalizar_ingredientes(ingredientes):
        cur.execute(
            """
            INSERT INTO ingredientes (recetaID, nombre, cantidad)
            VALUES (?, ?, ?)
            """,
            (receta_id, ingrediente, cantidad),
        )
    con.commit()
    con.close()
    return receta_id


def insertarIngrediente(recetaID, nombre, cantidad):
    con = conectar()
    con.execute(
        """
        INSERT INTO ingredientes (recetaID, nombre, cantidad)
        VALUES (?, ?, ?)
        """,
        (recetaID, nombre.strip(), str(cantidad).strip()),
    )
    con.commit()
    con.close()


def obtenerRecetas(busqueda=""):
    con = conectar()
    cur = con.cursor()
    patron = f"%{busqueda.strip().lower()}%"
    cur.execute(
        """
        SELECT r.id, r.nombrePlatillo, COALESCE(r.procedimiento, '') AS procedimiento,
               COALESCE(r.precio, 0) AS precio,
               COALESCE(GROUP_CONCAT(i.nombre || ' (' || COALESCE(i.cantidad, '') || ')', ', '), '') AS ingredientes
        FROM recetas r
        LEFT JOIN ingredientes i ON i.recetaID = r.id
        WHERE LOWER(r.nombrePlatillo) LIKE ? OR LOWER(COALESCE(r.procedimiento, '')) LIKE ?
        GROUP BY r.id
        ORDER BY r.nombrePlatillo COLLATE NOCASE
        """,
        (patron, patron),
    )
    datos = cur.fetchall()
    con.close()
    return datos


def obtenerRecetaPorId(recetaID):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, nombrePlatillo, COALESCE(procedimiento, '') AS procedimiento,
               COALESCE(precio, 0) AS precio
        FROM recetas
        WHERE id = ?
        """,
        (recetaID,),
    )
    dato = cur.fetchone()
    con.close()
    return dato


def obtenerIngredientesReceta(recetaID):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, recetaID, nombre, COALESCE(cantidad, '') AS cantidad
        FROM ingredientes
        WHERE recetaID = ?
        ORDER BY id
        """,
        (recetaID,),
    )
    datos = cur.fetchall()
    con.close()
    return datos


def actualizarReceta(recetaID, nombre, procedimiento, precio, ingredientes=None):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        UPDATE recetas
        SET nombrePlatillo = ?, procedimiento = ?, precio = ?
        WHERE id = ?
        """,
        (nombre.strip(), procedimiento.strip(), _to_float(precio), recetaID),
    )
    cur.execute("DELETE FROM ingredientes WHERE recetaID = ?", (recetaID,))
    for ingrediente, cantidad in _normalizar_ingredientes(ingredientes):
        cur.execute(
            """
            INSERT INTO ingredientes (recetaID, nombre, cantidad)
            VALUES (?, ?, ?)
            """,
            (recetaID, ingrediente, cantidad),
        )
    con.commit()
    con.close()


def eliminarReceta(recetaID):
    con = conectar()
    con.execute("DELETE FROM recetas WHERE id = ?", (recetaID,))
    con.commit()
    con.close()


def _calcular_totales(cur, clienteID, recetas):
    subtotal = 0.0
    for receta_id, cantidad in recetas:
        row = cur.execute("SELECT precio FROM recetas WHERE id = ?", (receta_id,)).fetchone()
        if row:
            subtotal += _to_float(row["precio"]) * cantidad

    descuento = 0.0
    if clienteID:
        cliente = cur.execute("SELECT descuento FROM clientes WHERE id = ?", (clienteID,)).fetchone()
        if cliente:
            descuento = _normalizar_descuento(cliente["descuento"])

    total = max(subtotal * (1 - descuento), 0)
    return round(subtotal, 2), round(total, 2)


def insertarPedido(clienteID, direccion, fecha, anticipo, subtotal, total, tipo, estado="Pendiente", notas=""):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO pedidos (clienteID, direccion, fecha, anticipo, subtotal, total, tipo, estado, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (clienteID, direccion.strip(), fecha, _to_float(anticipo), _to_float(subtotal), _to_float(total), tipo, estado, notas),
    )
    pedido_id = cur.lastrowid
    con.commit()
    con.close()
    return pedido_id


def insertarPedidoReceta(pedidoID, recetaID, cantidad):
    con = conectar()
    con.execute(
        """
        INSERT INTO pedidosReceta (pedidoID, recetaID, cantidad)
        VALUES (?, ?, ?)
        """,
        (pedidoID, recetaID, _to_int(cantidad)),
    )
    con.commit()
    con.close()


def insertarEvento(pedidoID, nombreEvento, extras):
    con = conectar()
    con.execute(
        """
        INSERT INTO eventos (pedidoID, nombreEvento, extras)
        VALUES (?, ?, ?)
        """,
        (pedidoID, nombreEvento.strip(), extras.strip()),
    )
    con.commit()
    con.close()


def insertarPedidoConRecetas(
    clienteID,
    direccion,
    fecha,
    anticipo,
    tipo,
    recetas,
    nombreEvento="",
    extras="",
    notas="",
    estado="Pendiente",
):
    recetas_normalizadas = _normalizar_recetas_pedido(recetas)
    if not recetas_normalizadas:
        raise ValueError("Debe seleccionar al menos una receta para el pedido.")

    con = conectar()
    cur = con.cursor()
    subtotal, total = _calcular_totales(cur, clienteID, recetas_normalizadas)

    if not direccion.strip() and clienteID:
        cliente = cur.execute("SELECT direccion FROM clientes WHERE id = ?", (clienteID,)).fetchone()
        direccion = cliente["direccion"] if cliente else ""

    cur.execute(
        """
        INSERT INTO pedidos (clienteID, direccion, fecha, anticipo, subtotal, total, tipo, estado, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (clienteID, direccion.strip(), fecha, _to_float(anticipo), subtotal, total, tipo, estado, notas.strip()),
    )
    pedido_id = cur.lastrowid

    for receta_id, cantidad in recetas_normalizadas:
        cur.execute(
            """
            INSERT INTO pedidosReceta (pedidoID, recetaID, cantidad)
            VALUES (?, ?, ?)
            """,
            (pedido_id, receta_id, cantidad),
        )

    if tipo == "Evento":
        cur.execute(
            """
            INSERT INTO eventos (pedidoID, nombreEvento, extras)
            VALUES (?, ?, ?)
            """,
            (pedido_id, nombreEvento.strip(), extras.strip()),
        )

    con.commit()
    con.close()
    return pedido_id


def obtenerPedidos(busqueda="", estado=None, tipo=None, fecha=None, historial=False):
    con = conectar()
    cur = con.cursor()
    condiciones = []
    parametros = []

    if busqueda.strip():
        patron = f"%{busqueda.strip().lower()}%"
        condiciones.append(
            """
            (LOWER(COALESCE(c.nombre, '')) LIKE ?
             OR LOWER(COALESCE(e.nombreEvento, '')) LIKE ?
             OR LOWER(COALESCE(p.tipo, '')) LIKE ?
             OR LOWER(COALESCE(p.fecha, '')) LIKE ?)
            """
        )
        parametros.extend([patron, patron, patron, patron])

    if estado:
        condiciones.append("p.estado = ?")
        parametros.append(estado)

    if tipo:
        condiciones.append("p.tipo = ?")
        parametros.append(tipo)

    if fecha:
        condiciones.append("p.fecha = ?")
        parametros.append(fecha)

    if historial:
        condiciones.append("p.estado <> 'Pendiente'")

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    cur.execute(
        f"""
        SELECT p.id, p.clienteID, COALESCE(c.nombre, 'Cliente eliminado') AS cliente,
               COALESCE(c.telefono, '') AS telefono,
               COALESCE(p.direccion, '') AS direccion,
               p.fecha, COALESCE(p.anticipo, 0) AS anticipo,
               COALESCE(p.subtotal, 0) AS subtotal, COALESCE(p.total, 0) AS total,
               COALESCE(p.tipo, 'Pedido simple') AS tipo,
               COALESCE(p.estado, 'Pendiente') AS estado,
               COALESCE(p.notas, '') AS notas,
               COALESCE(e.nombreEvento, '') AS evento,
               COALESCE(e.extras, '') AS extras,
               COALESCE(GROUP_CONCAT(r.nombrePlatillo || ' x' || pr.cantidad, ', '), '') AS recetas
        FROM pedidos p
        LEFT JOIN clientes c ON c.id = p.clienteID
        LEFT JOIN eventos e ON e.pedidoID = p.id
        LEFT JOIN pedidosReceta pr ON pr.pedidoID = p.id
        LEFT JOIN recetas r ON r.id = pr.recetaID
        {where}
        GROUP BY p.id
        ORDER BY p.fecha DESC, p.id DESC
        """,
        parametros,
    )
    datos = cur.fetchall()
    con.close()
    return datos


def obtenerPedidoDetalle(pedidoID):
    pedido = obtenerPedidos(busqueda="")
    pedido = next((p for p in pedido if p["id"] == pedidoID), None)

    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        SELECT pr.recetaID, r.nombrePlatillo, pr.cantidad, r.precio,
               (pr.cantidad * r.precio) AS subtotalLinea
        FROM pedidosReceta pr
        JOIN recetas r ON r.id = pr.recetaID
        WHERE pr.pedidoID = ?
        ORDER BY r.nombrePlatillo COLLATE NOCASE
        """,
        (pedidoID,),
    )
    recetas = cur.fetchall()
    con.close()
    return pedido, recetas


def actualizarEstadoPedido(pedidoID, estado):
    con = conectar()
    con.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (estado, pedidoID))
    con.commit()
    con.close()


def eliminarPedido(pedidoID):
    con = conectar()
    con.execute("DELETE FROM pedidos WHERE id = ?", (pedidoID,))
    con.commit()
    con.close()


def obtenerPedidosPorFecha(fecha):
    return obtenerPedidos(fecha=fecha)


def obtenerPedidosCalendario(anio, mes):
    inicio = date(anio, mes, 1).isoformat()
    fin = date(anio + (mes == 12), 1 if mes == 12 else mes + 1, 1).isoformat()

    con = conectar()
    cur = con.cursor()
    cur.execute(
        """
        SELECT p.id, p.fecha, COALESCE(p.tipo, 'Pedido simple') AS tipo,
               COALESCE(p.estado, 'Pendiente') AS estado,
               COALESCE(c.nombre, 'Cliente eliminado') AS cliente,
               COALESCE(e.nombreEvento, '') AS evento,
               COALESCE(GROUP_CONCAT(r.nombrePlatillo || ' x' || pr.cantidad, ', '), '') AS recetas,
               COALESCE(p.total, 0) AS total
        FROM pedidos p
        LEFT JOIN clientes c ON c.id = p.clienteID
        LEFT JOIN eventos e ON e.pedidoID = p.id
        LEFT JOIN pedidosReceta pr ON pr.pedidoID = p.id
        LEFT JOIN recetas r ON r.id = pr.recetaID
        WHERE p.fecha >= ? AND p.fecha < ?
        GROUP BY p.id
        ORDER BY p.fecha ASC, p.id ASC
        """,
        (inicio, fin),
    )
    datos = cur.fetchall()
    con.close()
    return datos


def obtenerEventos(busqueda=""):
    return obtenerPedidos(busqueda=busqueda, tipo="Evento")


def obtenerHistorial(busqueda=""):
    return obtenerPedidos(busqueda=busqueda, historial=True)


def obtenerResumen():
    con = conectar()
    cur = con.cursor()
    resumen = {
        "clientes": cur.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"],
        "recetas": cur.execute("SELECT COUNT(*) AS total FROM recetas").fetchone()["total"],
        "pendientes": cur.execute("SELECT COUNT(*) AS total FROM pedidos WHERE estado = 'Pendiente'").fetchone()["total"],
        "ingresos": cur.execute("SELECT COALESCE(SUM(total), 0) AS total FROM pedidos WHERE estado = 'Entregado'").fetchone()["total"],
    }
    con.close()
    return resumen
