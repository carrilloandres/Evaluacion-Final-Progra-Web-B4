# Lo primero que hice fue importar Flask y las funciones que necesito para mostrar
# las páginas HTML, leer los formularios, redirigir y manejar errores de rutas
from flask import Flask, render_template, request, redirect, url_for, abort


app = Flask(__name__)

PRECIO_TARRO = 9000

# Aquí dejé registrados en memoria los dos usuarios que pide el Ejercicio 2
USUARIOS_REGISTRADOS = {
    "juan": {"contrasena": "admin", "rol": "Administrador"},
    "pepe": {"contrasena": "user", "rol": "Usuario"},
}


# ------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN (las hice para que no pase ningún dato malo)
# ------------------------------------------------------------------

# En esta función valido campos de texto que deben ser solo letras y sin espacios
def validar_solo_letras(valor, nombre_campo):
    
    if valor is None or valor == "":
        return None, f"El campo {nombre_campo} no puede estar vacío."

    if any(caracter.isspace() for caracter in valor):
        return None, f"El campo {nombre_campo} no puede tener espacios."
    if not valor.isalpha():
        return None, f"El campo {nombre_campo} solo puede contener letras (sin números ni símbolos)."

    # Reviso que el nombre tenga al menos 2 letras y no sea exageradamente largo
    if len(valor) < 2:
        return None, f"El campo {nombre_campo} debe tener al menos 2 letras."
    if len(valor) > 50:
        return None, f"El campo {nombre_campo} es demasiado largo (máximo 50 letras)."

    return valor, None


# En esta función valido que un campo sea un número entero válido y dentro de un rango lógico
def validar_numero_entero(valor, nombre_campo, minimo, maximo):
    
    if valor is None or valor == "":
        return None, f"El campo {nombre_campo} no puede estar vacío."

    if any(caracter.isspace() for caracter in valor):
        return None, f"El campo {nombre_campo} no puede tener espacios."

    if "." in valor or "," in valor:
        return None, f"El campo {nombre_campo} debe ser un número entero, sin decimales."

    if valor.startswith("-") and valor[1:].isdigit():
        return None, f"El campo {nombre_campo} no puede ser un número negativo."

    if not (valor.isascii() and valor.isdigit()):
        return None, f"El campo {nombre_campo} solo puede contener números."

    # Convierto el texto a número entero de forma segura
    try:
        numero = int(valor)
    except ValueError:
        return None, f"El campo {nombre_campo} debe ser un número válido."

    # Por último reviso que el número esté dentro del rango permitido
    if numero < minimo or numero > maximo:
        return None, f"El campo {nombre_campo} debe estar entre {minimo} y {maximo}."

    return numero, None


# En esta función valido que la contraseña no venga vacía ni con espacios
def validar_contrasena(valor):
    if valor is None or valor == "":
        return None, "El campo Contraseña no puede estar vacío."

    if any(caracter.isspace() for caracter in valor):
        return None, "El campo Contraseña no puede tener espacios."

    return valor, None


# ------------------------------------------------------------------
# FUNCIONES DE LÓGICA DE NEGOCIO (cálculos y verificación de usuarios)
# ------------------------------------------------------------------

# Esta función lo que hago es calcular el total sin descuento, el porcentaje, el descuento y el total final
def calcular_compra(edad, cantidad_tarros):
    total_sin_descuento = cantidad_tarros * PRECIO_TARRO

    # Según la edad aplico el porcentaje de descuento que pide el enunciado
    if edad > 30:
        porcentaje_descuento = 25
    elif edad >= 18 and edad <= 30:
        porcentaje_descuento = 15
    else:
        porcentaje_descuento = 0

    # Calculo el monto del descuento y el total final redondeando a 1 decimal
    descuento = round(total_sin_descuento * (porcentaje_descuento / 100), 1)
    total_pagar = round(total_sin_descuento - descuento, 1)

    return total_sin_descuento, porcentaje_descuento, descuento, total_pagar


# Aqui lo que hice fue que esta función revisa si el usuario y la contraseña coinciden con los usuarios registrados
def verificar_usuario(usuario, contrasena):
    if usuario in USUARIOS_REGISTRADOS:
        datos_usuario = USUARIOS_REGISTRADOS[usuario]
        if datos_usuario["contrasena"] == contrasena:
            rol = datos_usuario["rol"]
            return True, f"Bienvenido {rol} {usuario}"

    return False, "Usuario o contraseña incorrectos"


# ------------------------------------------------------------------
# RUTAS DE MI APLICACIÓN WEB
# ------------------------------------------------------------------

# Ruta principal: muestra el menú inicial con los dos botones de colores
@app.route("/")
def index():
    return render_template("index.html")


# Creé esta ruta con parámetro por URL (/ejercicio/1 o /ejercicio/2) para redirigir
# y si ingresan otro número, corto la conexión con error 404
@app.route("/ejercicio/<int:numero>")
def ir_a_ejercicio(numero):
    if numero == 1:
        return redirect(url_for("ejercicio1"))
    elif numero == 2:
        return redirect(url_for("ejercicio2"))
    else:
        abort(404)


# Ruta del Ejercicio 1: Cálculo de compras de tarros de pintura
@app.route("/ejercicio1", methods=["GET", "POST"])
def ejercicio1():
    errores = []
    resultado = None
    datos = {"nombre": "", "edad": "", "cantidad": ""}

    if request.method == "POST":
        # Lo siguiente que hice fue recoger los datos tal como los escribió el usuario
        datos = {
            "nombre": request.form.get("nombre", ""),
            "edad": request.form.get("edad", ""),
            "cantidad": request.form.get("cantidad", ""),
        }

        # Valido cada uno de los 3 campos usando mis funciones
        nombre, error_nombre = validar_solo_letras(datos["nombre"], "Nombre")
        edad, error_edad = validar_numero_entero(datos["edad"], "Edad", 1, 120)
        cantidad, error_cantidad = validar_numero_entero(
            datos["cantidad"], "Cantidad de tarros", 1, 10000
        )

        for error in [error_nombre, error_edad, error_cantidad]:
            if error:
                errores.append(error)

        # Solo si no hay ningún error hago el cálculo de la compra
        if len(errores) == 0:
            total_sin_descuento, porcentaje, descuento, total_pagar = calcular_compra(
                edad, cantidad
            )
            resultado = {
                "nombre": nombre,
                "total_sin_descuento": total_sin_descuento,
                "porcentaje": porcentaje,
                "descuento": descuento,
                "total_pagar": total_pagar,
            }

    return render_template(
        "ejercicio1.html",
        errores=errores,
        resultado=resultado,
        datos=datos,
    )


# Ruta del Ejercicio 2: Inicio de sesión con usuarios registrados
@app.route("/ejercicio2", methods=["GET", "POST"])
def ejercicio2():
    errores = []
    mensaje = None
    acceso_correcto = False
    datos = {"usuario": ""}

    if request.method == "POST":
        # Recojo el nombre de usuario y la contraseña enviados desde el formulario
        usuario_ingresado = request.form.get("usuario", "")
        contrasena_ingresada = request.form.get("contrasena", "")
        datos["usuario"] = usuario_ingresado

        # Primero valido que el usuario sea solo letras sin espacios y la contraseña no esté vacía ni con espacios
        usuario, error_usuario = validar_solo_letras(usuario_ingresado, "Nombre")
        contrasena, error_contrasena = validar_contrasena(contrasena_ingresada)

        for error in [error_usuario, error_contrasena]:
            if error:
                errores.append(error)

        # Solo si pasaron las validaciones de formato verifico las credenciales
        if len(errores) == 0:
            acceso_correcto, mensaje = verificar_usuario(usuario, contrasena)

    return render_template(
        "ejercicio2.html",
        errores=errores,
        mensaje=mensaje,
        acceso_correcto=acceso_correcto,
        datos=datos,
    )


# Aca manejo de error 404 para mostrar una página mas presentable si entran a una ruta que no existe
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404


# Aquí arranco mi aplicación en modo debug para ver los cambios al instante
if __name__ == "__main__":
    app.run(debug=True)
