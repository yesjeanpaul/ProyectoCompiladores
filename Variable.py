from Simbolo import Simbolo

class Variable (Simbolo):
  def __init__(self, nombre, tipo):
    super().__init__(nombre)
    self.tipo = tipo
    self.valor = None

  def verificarTipo(self, tipoEntrada):
    return self.tipo == tipoEntrada

  def asignarValor (self, valor):
    self.valor = valor