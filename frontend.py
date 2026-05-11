import calendar
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from models import (
    actualizarCliente,
    actualizarEstadoPedido,
    actualizarReceta,
    eliminarCliente,
    eliminarPedido,
    eliminarReceta,
    insertarCliente,
    insertarPedidoConRecetas,
    insertarReceta,
    obtenerClientePorId,
    obtenerClientes,
    obtenerEventos,
    obtenerHistorial,
    obtenerIngredientesReceta,
    obtenerPedidos,
    obtenerPedidosCalendario,
    obtenerPedidosPorFecha,
    obtenerRecetaPorId,
    obtenerRecetas,
    obtenerResumen,
)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
calendar.setfirstweekday(calendar.MONDAY)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Artesanías con Sabor")
        self.geometry("1240x780")
        self.minsize(1040, 680)
        self.configure(fg_color="#f4f6fb")

        self.colors = {
            "bg": "#f4f6fb",
            "surface": "#ffffff",
            "sidebar": "#111827",
            "sidebar_hover": "#1f2937",
            "primary": "#2563eb",
            "primary_hover": "#1d4ed8",
            "accent": "#f97316",
            "text": "#111827",
            "muted": "#6b7280",
            "line": "#e5e7eb",
            "success": "#16a34a",
            "warning": "#f59e0b",
            "danger": "#dc2626",
        }

        self.current_view = "recetas"
        self.nav_buttons = {}
        self.calendar_month = date.today().replace(day=1)
        self.selected_calendar_date = date.today()

        self._configurar_tablas()
        self._crear_layout()
        self.mostrar_recetas()

    def _configurar_tablas(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Modern.Treeview",
            background="#ffffff",
            foreground="#111827",
            fieldbackground="#ffffff",
            borderwidth=0,
            rowheight=36,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Modern.Treeview.Heading",
            background="#eef2ff",
            foreground="#1f2937",
            borderwidth=0,
            font=("Segoe UI Semibold", 10),
            padding=8,
        )
        style.map("Modern.Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#111827")])

    def _crear_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=230, fg_color=self.colors["sidebar"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=18, pady=(24, 20))
        ctk.CTkLabel(
            brand,
            text="A&S",
            width=48,
            height=48,
            fg_color=self.colors["accent"],
            text_color="#ffffff",
            corner_radius=14,
            font=ctk.CTkFont("Segoe UI", 18, "bold"),
        ).pack(side="left")
        ctk.CTkLabel(
            brand,
            text="Artesanías\ncon Sabor",
            justify="left",
            text_color="#f9fafb",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=12)

        opciones = [
            ("recetas", "Recetas", self.mostrar_recetas),
            ("clientes", "Clientes", self.mostrar_clientes),
            ("eventos", "Eventos", self.mostrar_eventos),
            ("pedidos", "Pedidos", self.mostrar_pedidos),
            ("calendario", "Calendario", self.mostrar_calendario),
            ("historial", "Historial", self.mostrar_historial),
        ]

        for clave, texto, comando in opciones:
            btn = ctk.CTkButton(
                self.sidebar,
                text=texto,
                anchor="w",
                height=44,
                corner_radius=12,
                fg_color="transparent",
                hover_color=self.colors["sidebar_hover"],
                text_color="#d1d5db",
                font=ctk.CTkFont("Segoe UI", 14, "bold"),
                command=comando,
            )
            btn.pack(fill="x", padx=14, pady=4)
            self.nav_buttons[clave] = btn

        self.sidebar_footer = ctk.CTkLabel(
            self.sidebar,
            text="Sistema de recetas,\npedidos y eventos",
            justify="left",
            text_color="#9ca3af",
            font=ctk.CTkFont("Segoe UI", 11),
        )
        self.sidebar_footer.pack(side="bottom", fill="x", padx=22, pady=24)

        self.main = ctk.CTkFrame(self, fg_color=self.colors["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))
        self.header.grid_columnconfigure(0, weight=1)

        self.titulo = ctk.CTkLabel(
            self.header,
            text="Recetas",
            anchor="w",
            text_color=self.colors["text"],
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
        )
        self.titulo.grid(row=0, column=0, sticky="w")
        self.subtitulo = ctk.CTkLabel(
            self.header,
            text="",
            anchor="w",
            text_color=self.colors["muted"],
            font=ctk.CTkFont("Segoe UI", 13),
        )
        self.subtitulo.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.resumen_label = ctk.CTkLabel(
            self.header,
            text="",
            height=42,
            fg_color=self.colors["surface"],
            text_color=self.colors["text"],
            corner_radius=14,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
        )
        self.resumen_label.grid(row=0, column=1, rowspan=2, sticky="e")

        self.contenido = ctk.CTkFrame(self.main, fg_color="transparent")
        self.contenido.grid(row=1, column=0, sticky="nsew", padx=28, pady=(8, 28))
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)

    def cambiar_vista(self, clave, titulo, subtitulo):
        self.current_view = clave
        self.titulo.configure(text=titulo)
        self.subtitulo.configure(text=subtitulo)
        self._actualizar_resumen()
        self._activar_nav(clave)
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def _activar_nav(self, clave):
        for nav_key, boton in self.nav_buttons.items():
            if nav_key == clave:
                boton.configure(fg_color=self.colors["primary"], text_color="#ffffff")
            else:
                boton.configure(fg_color="transparent", text_color="#d1d5db")

    def _actualizar_resumen(self):
        try:
            resumen = obtenerResumen()
            texto = (
                f"{resumen['clientes']} clientes   "
                f"{resumen['recetas']} recetas   "
                f"{resumen['pendientes']} pendientes   "
                f"Q {float(resumen['ingresos']):,.2f} entregado"
            )
            self.resumen_label.configure(text=texto)
        except Exception:
            self.resumen_label.configure(text="Base de datos pendiente")

    def refrescar_vista(self):
        getattr(self, f"mostrar_{self.current_view}")()

    def _toolbar(self, parent, placeholder, acciones):
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 12))
        toolbar.grid_columnconfigure(0, weight=1)

        search_var = tk.StringVar()
        search = ctk.CTkEntry(
            toolbar,
            textvariable=search_var,
            placeholder_text=placeholder,
            height=42,
            corner_radius=12,
            border_color="#d1d5db",
            fg_color="#ffffff",
        )
        search.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        button_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")
        for texto, comando, color in acciones:
            ctk.CTkButton(
                button_frame,
                text=texto,
                height=40,
                corner_radius=12,
                fg_color=color or self.colors["primary"],
                hover_color=self._hover_color(color),
                command=comando,
            ).pack(side="left", padx=4)
        return search_var, search

    def _hover_color(self, color):
        if color == self.colors["danger"]:
            return "#b91c1c"
        if color == self.colors["warning"]:
            return "#d97706"
        if color == self.colors["success"]:
            return "#15803d"
        if color == self.colors["accent"]:
            return "#ea580c"
        return self.colors["primary_hover"]

    def _crear_tabla(self, parent, columnas):
        frame = ctk.CTkFrame(parent, fg_color=self.colors["surface"], corner_radius=16)
        frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        tree = ttk.Treeview(frame, columns=[c[0] for c in columnas], show="headings", style="Modern.Treeview")
        for clave, titulo, ancho, anchor in columnas:
            tree.heading(clave, text=titulo)
            tree.column(clave, width=ancho, minwidth=50, anchor=anchor, stretch=True)

        scrollbar = ctk.CTkScrollbar(frame, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)
        return tree

    def _selected_id(self, tree, nombre="registro"):
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", f"Selecciona un {nombre} primero.")
            return None
        return int(tree.item(seleccion[0], "values")[0])

    def _selected_id_silencioso(self, tree):
        seleccion = tree.selection()
        if not seleccion:
            return None
        return int(tree.item(seleccion[0], "values")[0])

    def _money(self, valor):
        try:
            return f"Q {float(valor):,.2f}"
        except (TypeError, ValueError):
            return "Q 0.00"

    def _percent(self, valor):
        try:
            return f"{float(valor) * 100:.0f}%"
        except (TypeError, ValueError):
            return "0%"

    def _estado_color(self, estado):
        return {
            "Pendiente": self.colors["warning"],
            "En preparación": self.colors["primary"],
            "Entregado": self.colors["success"],
            "Cancelado": self.colors["danger"],
        }.get(estado, self.colors["muted"])

    def _parse_fecha(self, texto):
        valor = texto.strip()
        for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(valor, formato).date().isoformat()
            except ValueError:
                pass
        raise ValueError("Usa una fecha valida: 2026-05-10 o 10/05/2026.")

    def _parse_ingredientes(self, texto):
        ingredientes = []
        for linea in texto.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            if "|" in linea:
                nombre, cantidad = linea.split("|", 1)
            elif ":" in linea:
                nombre, cantidad = linea.split(":", 1)
            elif " - " in linea:
                nombre, cantidad = linea.split(" - ", 1)
            else:
                nombre, cantidad = linea, ""
            if nombre.strip():
                ingredientes.append((nombre.strip(), cantidad.strip()))
        return ingredientes

    def _crear_modal(self, titulo, ancho=620, alto=560):
        modal = ctk.CTkToplevel(self)
        modal.title(titulo)
        modal.geometry(f"{ancho}x{alto}")
        modal.minsize(min(ancho, 520), min(alto, 420))
        modal.configure(fg_color=self.colors["bg"])
        modal.transient(self)
        modal.grab_set()
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(0, weight=1)
        modal.focus_force()
        return modal

    def mostrar_recetas(self):
        self.cambiar_vista("recetas", "Recetas", "Crea, busca y actualiza los platillos que usa la empresa.")
        wrapper = ctk.CTkFrame(self.contenido, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        search_var, search = self._toolbar(
            wrapper,
            "Buscar receta por nombre o preparacion...",
            [
                ("Añadir", lambda: self.abrir_form_receta(), self.colors["primary"]),
                ("Cambiar", lambda: self.abrir_form_receta(tree), self.colors["warning"]),
                ("Eliminar", lambda: self.eliminar_receta(tree), self.colors["danger"]),
            ],
        )

        tree = self._crear_tabla(
            wrapper,
            [
                ("id", "ID", 50, "center"),
                ("nombre", "Receta", 180, "w"),
                ("ingredientes", "Ingredientes", 360, "w"),
                ("precio", "Precio", 90, "e"),
            ],
        )

        detalle = ctk.CTkTextbox(
            wrapper,
            height=160,
            fg_color="#ffffff",
            text_color=self.colors["text"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["line"],
            font=ctk.CTkFont("Segoe UI", 12),
        )
        detalle.pack(fill="x", pady=(12, 0))
        detalle.insert("1.0", "Selecciona una receta para ver su preparacion e ingredientes.")
        detalle.configure(state="disabled")

        def cargar(_event=None):
            tree.delete(*tree.get_children())
            for receta in obtenerRecetas(search_var.get()):
                tree.insert(
                    "",
                    "end",
                    values=(
                        receta["id"],
                        receta["nombrePlatillo"],
                        receta["ingredientes"] or "Sin ingredientes registrados",
                        self._money(receta["precio"]),
                    ),
                )

        def mostrar_detalle(_event=None):
            receta_id = self._selected_id_silencioso(tree)
            detalle.configure(state="normal")
            detalle.delete("1.0", "end")
            if receta_id is None:
                detalle.insert("1.0", "Selecciona una receta para ver su preparacion e ingredientes.")
            else:
                receta = obtenerRecetaPorId(receta_id)
                ingredientes = obtenerIngredientesReceta(receta_id)
                texto_ingredientes = "\n".join(f"- {i['nombre']}: {i['cantidad']}" for i in ingredientes) or "Sin ingredientes registrados"
                detalle.insert(
                    "1.0",
                    f"{receta['nombrePlatillo']}\nPrecio: {self._money(receta['precio'])}\n\nIngredientes:\n{texto_ingredientes}\n\nPreparacion:\n{receta['procedimiento'] or 'Sin preparacion registrada'}",
                )
            detalle.configure(state="disabled")

        search.bind("<KeyRelease>", cargar)
        tree.bind("<<TreeviewSelect>>", mostrar_detalle)
        tree.bind("<Double-1>", lambda _event: self.abrir_form_receta(tree))
        cargar()

    def abrir_form_receta(self, tree=None):
        receta_id = self._selected_id(tree, "receta") if tree else None
        if tree and receta_id is None:
            return

        receta = obtenerRecetaPorId(receta_id) if receta_id else None
        ingredientes = obtenerIngredientesReceta(receta_id) if receta_id else []

        modal = self._crear_modal("Cambiar receta" if receta_id else "Añadir receta", 680, 620)
        form = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        form.grid_columnconfigure(1, weight=1)

        nombre_var = tk.StringVar(value=receta["nombrePlatillo"] if receta else "")
        precio_var = tk.StringVar(value=str(receta["precio"]) if receta else "")

        ctk.CTkLabel(form, text="Nombre del platillo", anchor="w", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        ctk.CTkEntry(form, textvariable=nombre_var, height=40).grid(row=0, column=1, sticky="ew", pady=8)

        ctk.CTkLabel(form, text="Precio por porcion", anchor="w", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        ctk.CTkEntry(form, textvariable=precio_var, height=40, placeholder_text="0.00").grid(row=1, column=1, sticky="ew", pady=8)

        ctk.CTkLabel(form, text="Ingredientes", anchor="w", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="nw", pady=8)
        ingredientes_text = ctk.CTkTextbox(form, height=150, corner_radius=12)
        ingredientes_text.grid(row=2, column=1, sticky="ew", pady=8)
        ingredientes_text.insert("1.0", "\n".join(f"{i['nombre']} | {i['cantidad']}" for i in ingredientes))

        ctk.CTkLabel(form, text="Preparacion", anchor="w", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="nw", pady=8)
        procedimiento_text = ctk.CTkTextbox(form, height=160, corner_radius=12)
        procedimiento_text.grid(row=3, column=1, sticky="ew", pady=8)
        procedimiento_text.insert("1.0", receta["procedimiento"] if receta else "")

        ayuda = ctk.CTkLabel(
            form,
            text="Formato recomendado para ingredientes: Harina | 2 libras",
            text_color=self.colors["muted"],
            anchor="w",
        )
        ayuda.grid(row=4, column=1, sticky="w", pady=(0, 12))

        acciones = ctk.CTkFrame(form, fg_color="transparent")
        acciones.grid(row=5, column=0, columnspan=2, sticky="e", pady=(8, 0))

        def guardar():
            nombre = nombre_var.get().strip()
            if not nombre:
                messagebox.showerror("Dato faltante", "Escribe el nombre de la receta.")
                return
            try:
                precio = float(precio_var.get().replace(",", ".") or 0)
            except ValueError:
                messagebox.showerror("Precio invalido", "El precio debe ser numerico.")
                return
            procedimiento = procedimiento_text.get("1.0", "end").strip()
            ingredientes_guardar = self._parse_ingredientes(ingredientes_text.get("1.0", "end"))
            if receta_id:
                actualizarReceta(receta_id, nombre, procedimiento, precio, ingredientes_guardar)
            else:
                insertarReceta(nombre, procedimiento, precio, ingredientes_guardar)
            modal.destroy()
            self.refrescar_vista()

        ctk.CTkButton(acciones, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=modal.destroy).pack(side="left", padx=5)
        ctk.CTkButton(acciones, text="Guardar receta", command=guardar).pack(side="left", padx=5)

    def eliminar_receta(self, tree):
        receta_id = self._selected_id(tree, "receta")
        if receta_id is None:
            return
        if messagebox.askyesno("Eliminar receta", "¿Deseas eliminar esta receta? Esta accion tambien la quitara de pedidos guardados."):
            eliminarReceta(receta_id)
            self.refrescar_vista()

    def mostrar_clientes(self):
        self.cambiar_vista("clientes", "Clientes", "Directorio de clientes recurrentes, telefonos, direcciones y descuentos.")
        wrapper = ctk.CTkFrame(self.contenido, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        search_var, search = self._toolbar(
            wrapper,
            "Buscar cliente por nombre, telefono o direccion...",
            [
                ("Añadir", lambda: self.abrir_form_cliente(), self.colors["primary"]),
                ("Cambiar", lambda: self.abrir_form_cliente(tree), self.colors["warning"]),
                ("Eliminar", lambda: self.eliminar_cliente(tree), self.colors["danger"]),
            ],
        )

        tree = self._crear_tabla(
            wrapper,
            [
                ("id", "ID", 50, "center"),
                ("nombre", "Cliente", 190, "w"),
                ("telefono", "Telefono", 120, "center"),
                ("direccion", "Direccion", 320, "w"),
                ("descuento", "Descuento", 100, "center"),
            ],
        )

        def cargar(_event=None):
            tree.delete(*tree.get_children())
            for cliente in obtenerClientes(search_var.get()):
                tree.insert(
                    "",
                    "end",
                    values=(cliente["id"], cliente["nombre"], cliente["telefono"], cliente["direccion"], self._percent(cliente["descuento"])),
                )

        search.bind("<KeyRelease>", cargar)
        tree.bind("<Double-1>", lambda _event: self.abrir_form_cliente(tree))
        cargar()

    def abrir_form_cliente(self, tree=None):
        cliente_id = self._selected_id(tree, "cliente") if tree else None
        if tree and cliente_id is None:
            return
        cliente = obtenerClientePorId(cliente_id) if cliente_id else None

        modal = self._crear_modal("Cambiar cliente" if cliente_id else "Añadir cliente", 620, 420)
        form = ctk.CTkFrame(modal, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        form.grid_columnconfigure(1, weight=1)

        nombre_var = tk.StringVar(value=cliente["nombre"] if cliente else "")
        direccion_var = tk.StringVar(value=cliente["direccion"] if cliente else "")
        telefono_var = tk.StringVar(value=cliente["telefono"] if cliente else "")
        descuento_var = tk.StringVar(value=str(float(cliente["descuento"]) * 100) if cliente else "0")

        campos = [
            ("Nombre", nombre_var, "Nombre del cliente"),
            ("Direccion", direccion_var, "Direccion de entrega"),
            ("Telefono", telefono_var, "8 digitos o telefono de contacto"),
            ("Descuento (%)", descuento_var, "0"),
        ]
        for row, (label, variable, placeholder) in enumerate(campos):
            ctk.CTkLabel(form, text=label, anchor="w", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=row, column=0, sticky="w", pady=9)
            ctk.CTkEntry(form, textvariable=variable, placeholder_text=placeholder, height=40).grid(row=row, column=1, sticky="ew", pady=9)

        acciones = ctk.CTkFrame(form, fg_color="transparent")
        acciones.grid(row=5, column=0, columnspan=2, sticky="e", pady=(16, 0))

        def guardar():
            if not nombre_var.get().strip() or not telefono_var.get().strip():
                messagebox.showerror("Dato faltante", "Nombre y telefono son obligatorios.")
                return
            try:
                descuento = float(descuento_var.get().replace(",", ".") or 0) / 100
            except ValueError:
                messagebox.showerror("Descuento invalido", "El descuento debe ser numerico.")
                return
            if cliente_id:
                actualizarCliente(cliente_id, nombre_var.get(), direccion_var.get(), telefono_var.get(), descuento)
            else:
                insertarCliente(nombre_var.get(), direccion_var.get(), telefono_var.get(), descuento)
            modal.destroy()
            self.refrescar_vista()

        ctk.CTkButton(acciones, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=modal.destroy).pack(side="left", padx=5)
        ctk.CTkButton(acciones, text="Guardar cliente", command=guardar).pack(side="left", padx=5)

    def eliminar_cliente(self, tree):
        cliente_id = self._selected_id(tree, "cliente")
        if cliente_id is None:
            return
        if messagebox.askyesno("Eliminar cliente", "¿Deseas eliminar este cliente? Sus pedidos quedaran como cliente eliminado."):
            eliminarCliente(cliente_id)
            self.refrescar_vista()

    def mostrar_pedidos(self):
        self._mostrar_listado_pedidos(
            clave="pedidos",
            titulo="Pedidos",
            subtitulo="Control de pedidos simples y eventos con estado, fecha y total.",
            tipo=None,
            historial=False,
        )

    def mostrar_eventos(self):
        self._mostrar_listado_pedidos(
            clave="eventos",
            titulo="Eventos",
            subtitulo="Pedidos especiales con nombre de evento, extras y fecha de entrega.",
            tipo="Evento",
            historial=False,
        )

    def mostrar_historial(self):
        self._mostrar_listado_pedidos(
            clave="historial",
            titulo="Historial",
            subtitulo="Pedidos entregados o cancelados para consulta posterior.",
            tipo=None,
            historial=True,
        )

    def _mostrar_listado_pedidos(self, clave, titulo, subtitulo, tipo=None, historial=False):
        self.cambiar_vista(clave, titulo, subtitulo)
        wrapper = ctk.CTkFrame(self.contenido, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)

        acciones = [("Detalle", lambda: self.ver_detalle_pedido(tree), self.colors["primary"])]
        if not historial:
            acciones = [
                ("Nuevo pedido", lambda: self.abrir_form_pedido("Pedido simple"), self.colors["primary"]),
                ("Nuevo evento", lambda: self.abrir_form_pedido("Evento"), self.colors["accent"]),
                ("Entregado", lambda: self.cambiar_estado_pedido(tree, "Entregado"), self.colors["success"]),
                ("Preparacion", lambda: self.cambiar_estado_pedido(tree, "En preparación"), self.colors["warning"]),
                ("Cancelar", lambda: self.cambiar_estado_pedido(tree, "Cancelado"), self.colors["danger"]),
                ("Detalle", lambda: self.ver_detalle_pedido(tree), self.colors["primary"]),
            ]
        else:
            acciones.extend(
                [
                    ("Reabrir", lambda: self.cambiar_estado_pedido(tree, "Pendiente"), self.colors["warning"]),
                    ("Eliminar", lambda: self.eliminar_pedido(tree), self.colors["danger"]),
                ]
            )

        search_var, search = self._toolbar(wrapper, "Buscar por cliente, evento, tipo o fecha...", acciones)

        tree = self._crear_tabla(
            wrapper,
            [
                ("id", "ID", 50, "center"),
                ("fecha", "Fecha", 110, "center"),
                ("cliente", "Cliente", 170, "w"),
                ("tipo", "Tipo", 110, "center"),
                ("estado", "Estado", 120, "center"),
                ("recetas", "Recetas", 320, "w"),
                ("total", "Total", 100, "e"),
            ],
        )

        def cargar(_event=None):
            tree.delete(*tree.get_children())
            consulta = obtenerHistorial(search_var.get()) if historial else obtenerPedidos(search_var.get(), tipo=tipo)
            if clave == "eventos":
                consulta = obtenerEventos(search_var.get())
            for pedido in consulta:
                nombre = pedido["evento"] if pedido["tipo"] == "Evento" and pedido["evento"] else pedido["cliente"]
                tree.insert(
                    "",
                    "end",
                    values=(
                        pedido["id"],
                        pedido["fecha"],
                        nombre,
                        pedido["tipo"],
                        pedido["estado"],
                        pedido["recetas"] or "Sin recetas",
                        self._money(pedido["total"]),
                    ),
                )

        search.bind("<KeyRelease>", cargar)
        tree.bind("<Double-1>", lambda _event: self.ver_detalle_pedido(tree))
        cargar()

    def abrir_form_pedido(self, tipo_default="Pedido simple", fecha_default=None):
        clientes = obtenerClientes()
        recetas = obtenerRecetas()
        if not clientes:
            messagebox.showinfo("Clientes", "Primero registra al menos un cliente.")
            self.mostrar_clientes()
            return
        if not recetas:
            messagebox.showinfo("Recetas", "Primero registra al menos una receta.")
            self.mostrar_recetas()
            return

        modal = self._crear_modal("Nuevo evento" if tipo_default == "Evento" else "Nuevo pedido", 820, 720)
        form = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        form.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)
        form.grid_columnconfigure(1, weight=1)

        cliente_labels = {f"{c['id']} - {c['nombre']}": c for c in clientes}
        cliente_var = tk.StringVar(value=next(iter(cliente_labels)))
        fecha_var = tk.StringVar(value=(fecha_default or date.today()).isoformat())
        direccion_var = tk.StringVar(value=cliente_labels[cliente_var.get()]["direccion"])
        anticipo_var = tk.StringVar(value="0")
        tipo_var = tk.StringVar(value=tipo_default)
        evento_var = tk.StringVar(value="")
        extras_var = tk.StringVar(value="")

        ctk.CTkLabel(form, text="Cliente", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", pady=8)
        cliente_menu = ctk.CTkOptionMenu(form, variable=cliente_var, values=list(cliente_labels.keys()), height=40)
        cliente_menu.grid(row=0, column=1, sticky="ew", pady=8)

        def actualizar_direccion(_value=None):
            direccion_var.set(cliente_labels[cliente_var.get()]["direccion"])

        cliente_menu.configure(command=actualizar_direccion)

        ctk.CTkLabel(form, text="Tipo", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", pady=8)
        tipo_menu = ctk.CTkOptionMenu(form, variable=tipo_var, values=["Pedido simple", "Evento"], height=40)
        tipo_menu.grid(row=1, column=1, sticky="ew", pady=8)

        ctk.CTkLabel(form, text="Fecha", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", pady=8)
        fecha_frame = ctk.CTkFrame(form, fg_color="transparent")
        fecha_frame.grid(row=2, column=1, sticky="ew", pady=8)
        fecha_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(fecha_frame, textvariable=fecha_var, height=40, placeholder_text="2026-05-10").grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(fecha_frame, text="Hoy", width=72, command=lambda: fecha_var.set(date.today().isoformat())).grid(row=0, column=1, padx=(8, 0))

        ctk.CTkLabel(form, text="Direccion", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="w", pady=8)
        ctk.CTkEntry(form, textvariable=direccion_var, height=40, placeholder_text="Direccion de entrega o recoger en tienda").grid(row=3, column=1, sticky="ew", pady=8)

        ctk.CTkLabel(form, text="Anticipo", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", pady=8)
        ctk.CTkEntry(form, textvariable=anticipo_var, height=40, placeholder_text="0.00").grid(row=4, column=1, sticky="ew", pady=8)

        evento_frame = ctk.CTkFrame(form, fg_color="#ffffff", corner_radius=14)
        evento_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        evento_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(evento_frame, text="Nombre del evento", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))
        ctk.CTkEntry(evento_frame, textvariable=evento_var, height=38).grid(row=0, column=1, sticky="ew", padx=14, pady=(14, 8))
        ctk.CTkLabel(evento_frame, text="Extras", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 14))
        ctk.CTkEntry(evento_frame, textvariable=extras_var, height=38, placeholder_text="Decoracion, montaje, bebidas, etc.").grid(row=1, column=1, sticky="ew", padx=14, pady=(0, 14))

        def alternar_evento(_value=None):
            if tipo_var.get() == "Evento":
                evento_frame.grid()
            else:
                evento_frame.grid_remove()

        tipo_menu.configure(command=alternar_evento)
        alternar_evento()

        ctk.CTkLabel(form, text="Recetas del pedido", font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(row=6, column=0, columnspan=2, sticky="w", pady=(16, 8))
        recetas_frame = ctk.CTkScrollableFrame(form, height=220, fg_color="#ffffff", corner_radius=14)
        recetas_frame.grid(row=7, column=0, columnspan=2, sticky="nsew")
        recetas_frame.grid_columnconfigure(0, weight=1)

        receta_vars = []
        for idx, receta in enumerate(recetas):
            row = ctk.CTkFrame(recetas_frame, fg_color="transparent")
            row.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            row.grid_columnconfigure(0, weight=1)
            activo = tk.BooleanVar(value=False)
            cantidad_var = tk.StringVar(value="1")
            ctk.CTkCheckBox(
                row,
                text=f"{receta['nombrePlatillo']}  ·  {self._money(receta['precio'])}",
                variable=activo,
                text_color=self.colors["text"],
                font=ctk.CTkFont("Segoe UI", 12),
            ).grid(row=0, column=0, sticky="w", padx=8, pady=6)
            ctk.CTkEntry(row, textvariable=cantidad_var, width=78, height=34, placeholder_text="Cant.").grid(row=0, column=1, padx=8, pady=6)
            receta_vars.append((receta, activo, cantidad_var))

        ctk.CTkLabel(form, text="Notas", font=ctk.CTkFont("Segoe UI", 12, "bold")).grid(row=8, column=0, sticky="nw", pady=(14, 8))
        notas_text = ctk.CTkTextbox(form, height=90, corner_radius=12)
        notas_text.grid(row=8, column=1, sticky="ew", pady=(14, 8))

        acciones = ctk.CTkFrame(form, fg_color="transparent")
        acciones.grid(row=9, column=0, columnspan=2, sticky="e", pady=(16, 0))

        def guardar():
            recetas_seleccionadas = []
            for receta, activo, cantidad_var in receta_vars:
                if activo.get():
                    try:
                        cantidad = int(cantidad_var.get() or 1)
                    except ValueError:
                        messagebox.showerror("Cantidad invalida", f"La cantidad de {receta['nombrePlatillo']} debe ser numerica.")
                        return
                    if cantidad <= 0:
                        messagebox.showerror("Cantidad invalida", "La cantidad debe ser mayor que cero.")
                        return
                    recetas_seleccionadas.append({"recetaID": receta["id"], "cantidad": cantidad})

            if not recetas_seleccionadas:
                messagebox.showerror("Recetas", "Selecciona al menos una receta para el pedido.")
                return

            try:
                fecha = self._parse_fecha(fecha_var.get())
                anticipo = float(anticipo_var.get().replace(",", ".") or 0)
            except ValueError as exc:
                messagebox.showerror("Dato invalido", str(exc))
                return

            cliente_id = cliente_labels[cliente_var.get()]["id"]
            nombre_evento = evento_var.get().strip()
            if tipo_var.get() == "Evento" and not nombre_evento:
                nombre_evento = f"Evento de {cliente_labels[cliente_var.get()]['nombre']}"

            insertarPedidoConRecetas(
                clienteID=cliente_id,
                direccion=direccion_var.get(),
                fecha=fecha,
                anticipo=anticipo,
                tipo=tipo_var.get(),
                recetas=recetas_seleccionadas,
                nombreEvento=nombre_evento,
                extras=extras_var.get(),
                notas=notas_text.get("1.0", "end").strip(),
            )
            modal.destroy()
            self.refrescar_vista()

        ctk.CTkButton(acciones, text="Cancelar", fg_color="#6b7280", hover_color="#4b5563", command=modal.destroy).pack(side="left", padx=5)
        ctk.CTkButton(acciones, text="Guardar", command=guardar).pack(side="left", padx=5)

    def cambiar_estado_pedido(self, tree, estado):
        pedido_id = self._selected_id(tree, "pedido")
        if pedido_id is None:
            return
        actualizarEstadoPedido(pedido_id, estado)
        self.refrescar_vista()

    def eliminar_pedido(self, tree):
        pedido_id = self._selected_id(tree, "pedido")
        if pedido_id is None:
            return
        if messagebox.askyesno("Eliminar pedido", "¿Deseas eliminar definitivamente este pedido?"):
            eliminarPedido(pedido_id)
            self.refrescar_vista()

    def ver_detalle_pedido(self, tree):
        pedido_id = self._selected_id(tree, "pedido")
        if pedido_id is None:
            return
        pedidos = obtenerPedidos()
        pedido = next((p for p in pedidos if p["id"] == pedido_id), None)
        if not pedido:
            return

        modal = self._crear_modal("Detalle del pedido", 620, 560)
        panel = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        titulo = pedido["evento"] if pedido["evento"] else f"Pedido #{pedido['id']}"
        ctk.CTkLabel(panel, text=titulo, anchor="w", font=ctk.CTkFont("Segoe UI", 22, "bold")).pack(fill="x")
        datos = [
            ("Cliente", pedido["cliente"]),
            ("Fecha", pedido["fecha"]),
            ("Tipo", pedido["tipo"]),
            ("Estado", pedido["estado"]),
            ("Direccion", pedido["direccion"] or "Sin direccion"),
            ("Recetas", pedido["recetas"] or "Sin recetas"),
            ("Subtotal", self._money(pedido["subtotal"])),
            ("Anticipo", self._money(pedido["anticipo"])),
            ("Total", self._money(pedido["total"])),
        ]
        if pedido["extras"]:
            datos.append(("Extras", pedido["extras"]))
        if pedido["notas"]:
            datos.append(("Notas", pedido["notas"]))

        for etiqueta, valor in datos:
            fila = ctk.CTkFrame(panel, fg_color="#ffffff", corner_radius=12)
            fila.pack(fill="x", pady=5)
            ctk.CTkLabel(fila, text=etiqueta, width=120, anchor="w", text_color=self.colors["muted"], font=ctk.CTkFont("Segoe UI", 12, "bold")).pack(side="left", padx=12, pady=10)
            ctk.CTkLabel(fila, text=str(valor), anchor="w", justify="left", wraplength=390, text_color=self.colors["text"]).pack(side="left", fill="x", expand=True, padx=12, pady=10)

    def mostrar_calendario(self):
        self.cambiar_vista("calendario", "Calendario", "Agenda mensual interactiva de pedidos y eventos.")
        wrapper = ctk.CTkFrame(self.contenido, fg_color="transparent")
        wrapper.pack(fill="both", expand=True)
        wrapper.grid_columnconfigure(0, weight=3)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(1, weight=1)

        barra = ctk.CTkFrame(wrapper, fg_color="transparent")
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        barra.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(barra, text="Anterior", width=110, command=lambda: self.cambiar_mes(-1)).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkLabel(
            barra,
            text=self.calendar_month.strftime("%B %Y").capitalize(),
            font=ctk.CTkFont("Segoe UI", 18, "bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=1)
        ctk.CTkButton(barra, text="Siguiente", width=110, command=lambda: self.cambiar_mes(1)).grid(row=0, column=2, padx=(8, 0))
        ctk.CTkButton(barra, text="Hoy", width=90, fg_color=self.colors["accent"], hover_color="#ea580c", command=self.ir_hoy).grid(row=0, column=3, padx=(8, 0))

        calendario_frame = ctk.CTkFrame(wrapper, fg_color="#ffffff", corner_radius=18)
        calendario_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        detalle_frame = ctk.CTkScrollableFrame(wrapper, fg_color="#ffffff", corner_radius=18)
        detalle_frame.grid(row=1, column=1, sticky="nsew")

        self._dibujar_calendario(calendario_frame, detalle_frame)

    def cambiar_mes(self, delta):
        mes = self.calendar_month.month + delta
        anio = self.calendar_month.year
        if mes < 1:
            mes = 12
            anio -= 1
        elif mes > 12:
            mes = 1
            anio += 1
        self.calendar_month = date(anio, mes, 1)
        self.selected_calendar_date = self.calendar_month
        self.mostrar_calendario()

    def ir_hoy(self):
        self.calendar_month = date.today().replace(day=1)
        self.selected_calendar_date = date.today()
        self.mostrar_calendario()

    def _dibujar_calendario(self, calendario_frame, detalle_frame):
        for col in range(7):
            calendario_frame.grid_columnconfigure(col, weight=1, uniform="cal")
        for row in range(7):
            calendario_frame.grid_rowconfigure(row, weight=1, minsize=70)

        dias = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
        for col, nombre in enumerate(dias):
            ctk.CTkLabel(
                calendario_frame,
                text=nombre,
                text_color=self.colors["muted"],
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
            ).grid(row=0, column=col, sticky="ew", padx=6, pady=(12, 4))

        pedidos_mes = obtenerPedidosCalendario(self.calendar_month.year, self.calendar_month.month)
        pedidos_por_dia = {}
        for pedido in pedidos_mes:
            dia = datetime.strptime(pedido["fecha"], "%Y-%m-%d").day
            pedidos_por_dia.setdefault(dia, []).append(pedido)

        semanas = calendar.monthcalendar(self.calendar_month.year, self.calendar_month.month)
        for row_idx, semana in enumerate(semanas, start=1):
            for col_idx, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkFrame(calendario_frame, fg_color="#f8fafc", corner_radius=14).grid(row=row_idx, column=col_idx, sticky="nsew", padx=5, pady=5)
                    continue
                fecha = date(self.calendar_month.year, self.calendar_month.month, dia)
                pedidos = pedidos_por_dia.get(dia, [])
                seleccionado = fecha == self.selected_calendar_date
                hoy = fecha == date.today()
                color = "#dbeafe" if seleccionado else "#ffffff"
                borde = self.colors["primary"] if seleccionado or hoy else self.colors["line"]
                cell = ctk.CTkFrame(calendario_frame, fg_color=color, corner_radius=14, border_width=1, border_color=borde)
                cell.grid(row=row_idx, column=col_idx, sticky="nsew", padx=5, pady=5)
                cell.grid_columnconfigure(0, weight=1)
                cell.bind("<Button-1>", lambda _event, f=fecha: self.seleccionar_fecha(f))

                dia_label = ctk.CTkLabel(cell, text=str(dia), anchor="w", font=ctk.CTkFont("Segoe UI", 14, "bold"), text_color=self.colors["text"])
                dia_label.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
                dia_label.bind("<Button-1>", lambda _event, f=fecha: self.seleccionar_fecha(f))

                if pedidos:
                    cuenta = ctk.CTkLabel(
                        cell,
                        text=f"{len(pedidos)} pedido(s)",
                        anchor="w",
                        text_color=self.colors["primary"],
                        font=ctk.CTkFont("Segoe UI", 11, "bold"),
                    )
                    cuenta.grid(row=1, column=0, sticky="w", padx=10)
                    cuenta.bind("<Button-1>", lambda _event, f=fecha: self.seleccionar_fecha(f))
                    primero = pedidos[0]["evento"] or pedidos[0]["cliente"]
                    resumen = ctk.CTkLabel(cell, text=primero[:24], anchor="w", text_color=self.colors["muted"], font=ctk.CTkFont("Segoe UI", 10))
                    resumen.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))
                    resumen.bind("<Button-1>", lambda _event, f=fecha: self.seleccionar_fecha(f))

        self._dibujar_detalle_dia(detalle_frame)

    def seleccionar_fecha(self, fecha):
        self.selected_calendar_date = fecha
        self.mostrar_calendario()

    def _dibujar_detalle_dia(self, panel):
        fecha = self.selected_calendar_date
        ctk.CTkLabel(panel, text=fecha.strftime("%d/%m/%Y"), anchor="w", font=ctk.CTkFont("Segoe UI", 20, "bold"), text_color=self.colors["text"]).pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(panel, text="Pedidos programados", anchor="w", text_color=self.colors["muted"]).pack(fill="x", padx=12, pady=(0, 12))

        pedidos = obtenerPedidosPorFecha(fecha.isoformat())
        if not pedidos:
            ctk.CTkLabel(panel, text="No hay pedidos para este dia.", text_color=self.colors["muted"], anchor="w").pack(fill="x", padx=12, pady=12)
        for pedido in pedidos:
            card = ctk.CTkFrame(panel, fg_color="#f8fafc", corner_radius=14)
            card.pack(fill="x", padx=12, pady=6)
            nombre = pedido["evento"] if pedido["evento"] else pedido["cliente"]
            ctk.CTkLabel(card, text=nombre, anchor="w", font=ctk.CTkFont("Segoe UI", 13, "bold"), text_color=self.colors["text"]).pack(fill="x", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=pedido["recetas"] or "Sin recetas", anchor="w", justify="left", wraplength=260, text_color=self.colors["muted"]).pack(fill="x", padx=12)
            footer = ctk.CTkFrame(card, fg_color="transparent")
            footer.pack(fill="x", padx=12, pady=(6, 10))
            ctk.CTkLabel(footer, text=pedido["estado"], text_color=self._estado_color(pedido["estado"]), font=ctk.CTkFont("Segoe UI", 11, "bold")).pack(side="left")
            ctk.CTkLabel(footer, text=self._money(pedido["total"]), text_color=self.colors["text"], font=ctk.CTkFont("Segoe UI", 11, "bold")).pack(side="right")

        ctk.CTkButton(panel, text="Nuevo pedido este dia", command=lambda: self.abrir_form_pedido("Pedido simple", fecha)).pack(fill="x", padx=12, pady=(16, 6))
        ctk.CTkButton(panel, text="Nuevo evento este dia", fg_color=self.colors["accent"], hover_color="#ea580c", command=lambda: self.abrir_form_pedido("Evento", fecha)).pack(fill="x", padx=12, pady=(0, 12))


if __name__ == "__main__":
    app = App()
    app.mainloop()
