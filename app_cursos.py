import streamlit as st
from datetime import datetime
import gspread 
from google.oauth2.service_account import Credentials

def conectar_google_sheets():
    """Esta función es nuestro puente privado hacia Google Sheets"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Usamos st.secrets para guardar la llave de forma segura
    credenciales = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    cliente = gspread.authorize(credenciales)
    return cliente

# 1. Configuración básica de la página
st.set_page_config(page_title="Inscripción a Cursos", page_icon="📖")

st.title("📖 Inscripción a Cursos Bíblicos")
st.write("Completa el siguiente formulario para registrarte en nuestros cursos de crecimiento espiritual.")

# 2. Creación del Formulario
with st.form("formulario_inscripcion", clear_on_submit=True):
    
    st.subheader("Tus Datos")
    
    # Cajas de texto para que el usuario escriba
    nombre = st.text_input("Nombre completo")
    telefono = st.text_input("Número de teléfono (WhatsApp)")
    
    st.write("¿A qué cursos deseas anotarte? (Puedes elegir más de uno)")
    
    # Casillas de verificación (Checkboxes) en lugar de un menú desplegable
    curso_verdades = st.checkbox("VERDADES FUNDAMENTALES")
    curso_iglesia = st.checkbox("IGLESIA DISCIPULADORA")
    curso_apologetica = st.checkbox("APOLOGÉTICA")
    
    st.write("---") # Agregamos una línea visual separadora
    st.subheader("Estado de Inscripción")
    pago_realizado = st.checkbox("¿Ya realizaste el pago correspondiente?")
    
    # Botón para enviar
    boton_enviar = st.form_submit_button("Inscribirme")

# 3. ¿Qué pasa cuando presionan el botón?
if boton_enviar:
    # Primero armamos una lista con los cursos que el usuario tildó
    cursos_seleccionados = []
    if curso_verdades:
        cursos_seleccionados.append("VERDADES FUNDAMENTALES")
    if curso_iglesia:
        cursos_seleccionados.append("IGLESIA DISCIPULADORA")
    if curso_apologetica:
        cursos_seleccionados.append("APOLOGÉTICA")

    # Verificaciones antes de enviar
    if nombre == "":
        st.error("Por favor, escribe tu nombre antes de enviarlo.")
    elif len(cursos_seleccionados) == 0:
        st.error("Por favor, selecciona al menos un curso para inscribirte.")
    elif not pago_si and not pago_no:
        st.error("Por favor, marca SÍ o NO en la sección de PAGADO.")
    elif pago_si and pago_no:
        st.error("Por favor, marca solo una opción en PAGADO (no ambas).")
    else:
        # Aquí capturamos la fecha actual
        fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Convertimos las casillas en la palabra exacta para tu planilla
        estado_pago = "Sí" if pago_si else "No"
        
        try:
            # 1. Nos conectamos a Google
            cliente = conectar_google_sheets()
            
            # 2. Abrimos tu planilla
            planilla = cliente.open("Inscripciones Cursos")
            
            # 3. Recorremos cada curso que la persona eligió y la anotamos en su pestaña
            for curso in cursos_seleccionados:
                pestana_curso = planilla.worksheet(curso)
                
                # Magia para la Columna A: Calculamos el número "N"
                # Contamos cuántas filas hay. Si solo están los títulos (1 fila), este será el alumno 1.
                filas_actuales = len(pestana_curso.get_all_values())
                numero_n = filas_actuales 
                
                # Armamos la fila exacta respetando tus 7 columnas:
                # [A: "N", B: "Fecha", C: "Nombre", D: "Teléfono", E: "Pagado", F: "Usuario", G: "Obs."]
                fila_a_guardar = [numero_n, fecha_registro, nombre, telefono, estado_pago, "", ""]
                
                pestana_curso.append_row(fila_a_guardar)
            
            # Mensaje de éxito mejorado y agradecimiento
            st.success(f"¡Gloria a Dios! 🎉 {nombre}, te has inscrito exitosamente.")
            st.info("¡Gracias por anotarte! Nos alegra mucho tu decisión de seguir creciendo espiritualmente. Un servidor te contactará pronto por WhatsApp con más detalles.")
            st.balloons() # ¡La lluvia de globos!
            
        except KeyError:
            st.warning("⚠️ Falta configurar la 'Llave de Google' en Streamlit Secrets.")
        except gspread.exceptions.WorksheetNotFound as e:
            st.error(f"¡Ups! No encontré la pestaña en tu Google Sheets. Asegúrate de que existan las pestañas con los nombres exactos.")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al conectar con Google: {e}")
