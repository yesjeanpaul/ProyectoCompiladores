import re
from Triplete import Triplete
from TablaDeSimbolos import TablaDeSimbolos
from Variable import Variable
from Token import Token


def esTriplete(simbolo):
  return isinstance(simbolo, Triplete)

def esToken(simbolo):
  return isinstance(simbolo, Token)

def esVariable(simbolo):
  return isinstance(simbolo, Variable)

def obtenerResultadoMat (simbolo1, simbolo2):
  tipo1 = obtenerTipo(simbolo1)
  tipo2 = obtenerTipo(simbolo2)
  if tipo1 == tipo2:
    return tipo1
  else:
    return "real"

def tieneValor(simbolo):
  if isinstance(simbolo, Token):
    if simbolo.valor == "verdadero" or \
      simbolo.valor == "falso" or \
      simbolo.tipo == "entero" or \
      simbolo.tipo == "real"  or\
      simbolo.tipo == "cadena"  or\
      simbolo.tipo == "caracter" :
      return True
  elif isinstance(simbolo, Variable):
    return simbolo.valor

def obtenerTipo (simbolo):
  if isinstance(simbolo, Token):
    if simbolo.tipo == "cadena" and \
      re.fullmatch(r'\"[\w\d ]?\"', simbolo.valor):
      return "caracter"
    if simbolo.tipo == "numero":
      if "." in simbolo.valor:
        return "real"
      return "entero"
    if simbolo.valor == "verdadero" or \
      simbolo.valor == "falso":
      return "bool"
    return simbolo.tipo
  elif isinstance(simbolo, Variable):
    return simbolo.tipo
  elif esTriplete(simbolo):
    return simbolo.resultado
  else:
    raise NameError("No se puede obtener tipo")

def obtenerValor (simbolo):
  if isinstance(simbolo, Token):
    return simbolo.valor
  elif isinstance(simbolo, Variable):
    return simbolo.valor
  else:
    raise NameError("No se puede obtener valor")

def obtenerTablaActual (semantico):
  return semantico.tablaDeSimbolosActual

def determinarSimbolo(semantico, simbolo):
  if esToken(simbolo):
    if simbolo.tipo == "ID":
      tabla = obtenerTablaActual(semantico)
      variable = tabla.buscarSimbolo(simbolo.valor)
      if variable:
        return variable
      else:
        raise ValueError(f"Simbolo {simbolo.valor} no existe")
    elif tieneValor(simbolo):
      return simbolo
  elif esTriplete(simbolo):
    return simbolo
  else:
    raise NameError(f"No se puede obtener valor de {simbolo}") 

def crearAlcance (semantico):
  tabla = obtenerTablaActual(semantico)
  semantico.tablaDeSimbolosActual = tabla
  Triplete("crearAlcance")

def borrarAlcance (semantico):
  tabla = obtenerTablaActual(semantico)
  if tabla.padre:
    semantico.tablaDeSimbolosActual = semantico.tablaDeSimbolosActual.padre
  del(tabla)
  Triplete("borrarAlcance")

def inicio (semantico):
  Triplete("inicio")

def fin (semantico):
  Triplete("fin")

def push (semantico):
  token = semantico.token
  semantico.pilaSemantica.append(token)

def pop (semantico):
  return semantico.pilaSemantica.pop(-1)
  

def peek (semantico):
  return semantico.pilaSemantica[-1]

def crearVariable (semantico):
  tabla = obtenerTablaActual(semantico)
  token = pop(semantico)
  tipo = peek(semantico)
  variable = Variable(token.valor, tipo.valor)
  tabla.agregarSimbolo(variable)
  Triplete("crearVariable", tipo.valor, token.valor)

##Aqui se hace la verifiacion de tipos para una asignacion 

def obtenerTipoEstricto (simbolo):
  if esToken(simbolo):
    if simbolo.tipo == "cadena" and \
      re.fullmatch(r'\"[\w\d ]?\"', simbolo.valor):
      return "caracter"
    if simbolo.valor == "verdadero" or \
      simbolo.valor == "falso":
      return "bool"
    return simbolo.tipo
  elif esVariable(simbolo):
    return simbolo.tipo
  elif esTriplete(simbolo):
    return simbolo.resultado
  else:
    raise NameError("No se puede obtener tipo")


def verificarTipoEstricto (tipoEsperado, tipoDeVariable):
  tipoE = obtenerTipoEstricto(tipoEsperado)
  tipoV = obtenerTipoEstricto(tipoDeVariable)
  if tipoE == "real" and tipoV == "entero":
    return True
  if tipoE == "cadena" and tipoV == "caracter":
    return True
  return tipoE == tipoV


def verificacionTiposAsignacion(funcion):
  def verificacion(semantico):
    simbolo1 = pop(semantico)
    simbolo2 = pop(semantico)
    valor = determinarSimbolo(semantico, simbolo1)
    variable = determinarSimbolo(semantico, simbolo2)
    if not variable:
      raise ValueError(f"La variable {variable} no existe")
    if verificarTipoEstricto(variable, valor):
      variable.valor = True
      if esTriplete(valor):
        funcion(variable.nombre, valor)
      elif tieneValor(valor):
        funcion(variable.nombre, valor.valor)
      else:
        raise ValueError(f"El valor {valor} no se puede asignar")
    else:
      raise TypeError(f"El tipo de {variable.nombre} no es compatible con {valor}")
  return verificacion

##Hasta aqui la verificacion

#Verificar si existe variable en la tabla de datos
def existeVariable(funcion):
  def existeVar(semantico):
    tabla = obtenerTablaActual(semantico)
    tokenVariable = pop(semantico)
    variable = determinarSimbolo(semantico, tokenVariable)
    if not Variable:
      raise NameError(f"No existe variable {variable}")
    else:
      return funcion(variable)
  return existeVar

def obtenerOperando(semantico, operando):
  if esToken(operando):
    return determinarSimbolo(semantico, operando)
  elif esTriplete(operando):
    return operando

def obtenerValorParaOperar(operando):
  if esToken(operando):
    return operando.valor
  elif esVariable(operando):
    return operando.nombre
  elif esTriplete(operando):
    return operando

def esOperacionMatematica (operando1, operando2):
  tipoOp1 = obtenerTipo(operando1)
  tipoOp2 = obtenerTipo(operando2)
  if (tipoOp1 == "real" or tipoOp1 == "entero") and \
    (tipoOp2 == "real" or tipoOp2 == "entero"):
    return True
  else:
    return False

def verificarOperadoresMatematicos (funcion):
  def verificarOperadores(semantico):
    operando1 = obtenerOperando(semantico, pop(semantico))
    operando2 = obtenerOperando(semantico, pop(semantico))
    print(f"{operando1} | {operando2}")
    if esOperacionMatematica(operando1, operando2):
      resultado = obtenerResultadoMat(operando1, operando2)
      op1 = obtenerValorParaOperar(operando1)
      op2 = obtenerValorParaOperar(operando2)
      triplete = funcion(op1, op2, resultado)
      semantico.pilaSemantica.append(triplete)
    else:
      raise TypeError(f"{operando1} y {operando2} no son compatibles")
  return verificarOperadores

@verificacionTiposAsignacion
def asignar(variable, valor):
  Triplete("asignar", variable, valor)

@existeVariable
def imprimir (variable):
  if variable.valor:
    Triplete("imprimir", variable.nombre, None)
  else:
    raise NameError(f"La variable {variable.nombre} no tiene dato")

@existeVariable
def leer (variable):
  variable.valor = True
  t = Triplete("leer", variable.nombre, None)
  Triplete("asignar", variable.nombre, t)

@verificarOperadoresMatematicos
def sumar (op1, op2, resultado):
  return Triplete("sumar", op1, op2, resultado)

@verificarOperadoresMatematicos
def restar (op1, op2, resultado):
  return Triplete("restar", op1, op2, resultado)

@verificarOperadoresMatematicos
def multiplicar (op1, op2, resultado):
  return Triplete("multiplicar", op1, op2, resultado)

@verificarOperadoresMatematicos
def dividir (op1, op2, resultado):
  return Triplete("dividir", op1, op2, resultado)


def verificarOperadoresRelacionales(funcion):
  def verificarOperadores(semantico):
    operando1 = obtenerOperando(semantico, pop(semantico))
    operando2 = obtenerOperando(semantico, pop(semantico))
    print(f"Operando 1: {operando1} Operando 2: {operando2}")
    print(f"Operando 1: {tieneValor(operando1)} Operando 2: {tieneValor(operando2)}")
    if tieneValor(operando1) and tieneValor(operando2):
      op1 = obtenerValorParaOperar(operando1)
      op2 = obtenerValorParaOperar(operando2)
      triplete = funcion(op1, op2)
      semantico.pilaSemantica.append(triplete)
    else:
      if not tieneValor(operando1):
        raise ValueError(f"El operador {operando1} no es compatible con la operacion" )
      if not tieneValor(operando2):
        raise ValueError(f"El operador {operando2} no es compatible con la operacion" )
  return verificarOperadores

@verificarOperadoresRelacionales
def esIgual (op1, op2):
  return Triplete("esIgual", op1, op2)

@verificarOperadoresRelacionales
def esDiferente (op1, op2):
  return Triplete("esDiferente", op1, op2)

@verificarOperadoresMatematicos
def esMayor (op1, op2, resultado):
  return Triplete("esMayor", op1, op2, resultado)

@verificarOperadoresMatematicos
def esMenor (op1, op2, resultado):
  return Triplete("esMenor", op1, op2, resultado)

@verificarOperadoresMatematicos
def esMayorOigual (op1, op2, resultado):
  return Triplete("esMayorOigual", op1, op2, resultado)

@verificarOperadoresMatematicos
def esMenorOigual (op1, op2, resultado):
  return Triplete("esMenorOigual", op1, op2, resultado)





""" operando1 = obtenerOperando(semantico, pop(semantico))
  operando2 = obtenerOperando(semantico, pop(semantico))
  if verificarTipoEstricto(operando1, operando2):
    op1 = obtenerValorParaOperar(operando1)
    op2 = obtenerValorParaOperar(operando2)
    t = Triplete("esIgual", op1, op2)
    semantico.pilaSemantica.append(t)
  else:
    raise TypeError("No son compatibles")

"""


reglas = {"crearAlcance": crearAlcance,
          "borrarAlcance": borrarAlcance,
          "inicio": inicio,
          "fin": fin,
          "push": push,
          "pop": pop,
          "crearVariable": crearVariable,
          "asignar": asignar,
          "imprimir": imprimir,
          "leer": leer,
          "sumar": sumar,
          "restar": restar,
          "multiplicar": multiplicar,
          "dividir": dividir,
          "esIgual": esIgual,
          "esDiferente": esDiferente,
          "esMayor": esMayor,
          "esMayorOigual": esMayorOigual,
          "esMenor": esMenor,
          "esMenorOigual": esMenorOigual
        }