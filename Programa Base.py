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
        print("\nPedidos Anteriores:")
        for i in self.PedidosAnteriores:
            print(i)
        print("\nPedidos Pendientes:")
        for i in self.PedidosPendientes:
            print(i)

class Receta:
    def __init__(self, Nombre_Platillo, Ingredientes, Procedimiento):
        self.Nombre_Platillo = Nombre_Platillo
        self.Ingredientes = Ingredientes
        self.Procedimiento = Procedimiento
    def MostrarReceta(self):
        print(f"-----{self.Nombre_Platillo}-----")
        print("Ingredientes:")
        for i in self.Ingredientes:
            print(i)
        print(f"\nProcedimiento:")
        print(self.Procedimiento)

class Pedidos:
    def __init__(self, Cliente, RecetaUtilizar, Codigo, FechaEvento):
        self.Cliente = Cliente
        self.RecetaUtilizar = RecetaUtilizar
        self.Codigo = Codigo
        self.Fecha = FechaEvento
    def PedidoEntregado(self):
        return {"Codigo" : self.Codigo, "Cliente": self.Cliente, "Fecha": self.Fecha, "Receta Utilizada" : self.RecetaUtilizar}

#Funciones
def NuevoCliente(Name, Direction, Lista):
    Nueva = Cliente(Name, Direction)
    Lista.append(Nueva)

def NuevaReceta(Nombre, Ingredientes, Procedimiento, Lista):
    Nueva = Receta(Nombre, Ingredientes, Procedimiento)
    Lista.append(Nueva)

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

print("Sistema")

print("Seleccione una opcion: ")

