#clases
class Cliente:
    def __init__(self, Nombre, Direccion, Descuento = 0):
        self.Nombre = Nombre
        self.Direccion = Direccion
        self.Descuento = Descuento
        self.PedidosAnteriores = []
        self.PedidosPendientes = []
    def VerCliente(self):
        print(f"------{self.Nombre}------")
        print(f"Direccion: {self.Direccion}")
        
        if len(self.PedidosAnteriores) != 0:
            print("\nPedidos Anteriores:")
            for i in self.PedidosAnteriores:
                print(i)
        if len(self.PedidosPendientes) != 0:
            print("\nPedidos Pendientes:")
            for i in self.PedidosPendientes:
                print(i)

class Receta:
    def __init__(self, Nombre_Platillo, Ingredientes, Procedimiento, PrecioPorcion):
        self.Nombre_Platillo = Nombre_Platillo
        self.Ingredientes = Ingredientes
        self.Procedimiento = Procedimiento
        self.Precio = PrecioPorcion
    def MostrarReceta(self):
        print(f"-----{self.Nombre_Platillo}-----")
        print(f"Precio: {self.Precio}")
        print("Ingredientes:")
        for i in self.Ingredientes:
            for n, c in i.items():
                print(f"Nombre: {n}    Cantidad: {c}")
        print(f"\nProcedimiento:")
        print(self.Procedimiento)

class PedidoSimple:
    def __init__(self, cliente, Direccion, RecetasUtilizar, CantidadPlatillos, Fecha, Anticipo):
        self.cliente = cliente
        self.Direccion = Direccion
        self.RecetasUtilizar = RecetasUtilizar
        self.CantidadPlatillos = CantidadPlatillos
        self.Fecha = Fecha
        self.Anticipo = Anticipo
        self.SubTotal = 0
        self.Total = 0
    def MostrarPedido(self):
        print("-----------------------------")
        print(f"Cliente: {self.cliente}")
        print(f"Direccion: {self.Direccion}")
        print(f"Fecha: {self.Fecha}")
        print("\nRecetas:")
        for r in self.RecetasUtilizar:
            print(f"{r.Nombre_Platillo}")
        print(f"\nSubtotal: {self.SubTotal}")
        print(f"Total: {self.Total}")
        print(f"Anticipo: {self.Anticipo}")
    def PedidoEntregado(self):
        return {"Cliente": self.cliente,
                "Total" : self.Total,
                "Fecha": self.Fecha,
                "Direccion" : self.Direccion,
                "Cantidad de platillos" : self.CantidadPlatillos,
                "Recetas Utilizadas" : [Rec.Nombre_Platillo for Rec in self.RecetasUtilizar]}

class Evento(PedidoSimple):
    def __init__(self, cliente, Direccion, RecetasUtilizar, CantidadPlatillos, Fecha, Anticipo, NombreEvento, Extras = None):
        super().__init__(cliente, Direccion, RecetasUtilizar, CantidadPlatillos, Fecha, Anticipo)
        self.NombreEvento = NombreEvento
        self.Extras = Extras 
    def MostrarPedido(self):
        print(f"---------Nombre del Evento: {self.NombreEvento}---------")
        super().MostrarPedido()
        print(f"Extras: {self.Extras}")
    def PedidoEntregado(self):
        EventoEntregado = {"Evento" : self.NombreEvento}
        NuevoEntregado = self.PedidoEntregado()
        for i, j in NuevoEntregado.items():
            EventoEntregado[i] = j
        return EventoEntregado

#Funciones

def TryCatchInt(ListaOpciones, Texto):
    while True:
        while True:
            try:
                Ingresar = int(input(f"{Texto} ").strip())
            except ValueError:
                print("Ingrese un valor valido")
            else: break
        if ListaOpciones:
            if Ingresar in ListaOpciones:
                return Ingresar
            else: print("Intentelo nuevamente")
        elif not ListaOpciones:
            return Ingresar

def TryCatchString(Texto, Lista=None):
    while True:
        Ingresar = input(f"{Texto} ").strip().title()
        if Ingresar == "":
            print("Ingrese un texto valido")
            continue
        if Lista is None or Ingresar in Lista:
            return Ingresar
        print("Ingrese un valor valido")

def OrdenarClientes(Lista):
    if len(Lista) <= 1:
        return Lista
    
    pivote = Lista[len(Lista)//2].Nombre

    Menores = [cliente for cliente in Lista if cliente.Nombre < pivote]
    Iguales = [cliente for cliente in Lista if cliente.Nombre == pivote]
    Mayores = [cliente for cliente in Lista if cliente.Nombre > pivote]

    return OrdenarClientes(Menores) + Iguales + OrdenarClientes(Mayores)

#estructura de datos
ListaClientes = []
ListaRecetas = []
ListaPedidosPendientes = []
ListaPedidosRealizados = []

ListaMonetaria = []

#Funcionamiento del sistema

def AgregarCliente():
    Name = TryCatchString("Ingrese el nombre del cliente: ", None)
    Direction = TryCatchString("Ingrese la dirección del cliente: ", None)
    Descp = TryCatchInt([1,2], "Tiene un descuento especifico? (1 = si, 2 = no)")

    if Descp == 2:
        Descuento = 0
    else:
        Descuento = TryCatchInt([i for i in range(1, 100)], "Ingrese el descuento del cliente")
        Descuento = Descuento /100

    NewCliente = Cliente(Name, Direction, Descuento)
    ListaClientes.append(NewCliente)

def AgregarReceta():
    Ingredientes = []
    Nombre = TryCatchString("Agregue el nombre del platillo:")

    while True:
        ingrediente = TryCatchString("Agregue un ingrediente (para terminar escriba fin):")

        if ingrediente == "Fin":
            break
        else: pass

        Cantidad = input("Ingrese la cantidad de este ingrediente por porcion:")
        
        Ingredientes.append({ingrediente : Cantidad})
    
    Preparacion = TryCatchString("Escriba la preparacion de la receta: ")

    Precio = TryCatchString("Ingrese el precio del platillo")

    NuevaReceta = Receta(Nombre, Ingredientes, Preparacion, Precio)
    ListaRecetas.append(NuevaReceta)

print("Sistema")

print("Seleccione una opcion: ")

