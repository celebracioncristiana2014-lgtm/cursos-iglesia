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
    else:
        # Aquí capturamos la fecha actual
        fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        try:
            # 1. Nos conectamos a Google
            cliente = conectar_google_sheets()
            
            # 2. Abrimos tu planilla
            planilla = cliente.open("Inscripciones Cursos")
            
            # 3. Recorremos cada curso que la persona eligió y la anotamos en su pestaña
            for curso in cursos_seleccionados:
                pestana_curso = planilla.worksheet(curso)
                pestana_curso.append_row([fecha_registro, nombre, telefono])
            
            # Mensaje de éxito si todo salió bien
            st.success(f"¡Gloria a Dios! 🎉 {nombre}, te has inscrito exitosamente.")
            st.balloons()
            
        except KeyError:
            st.warning("⚠️ Falta configurar la 'Llave de Google' en Streamlit Secrets.")
        except gspread.exceptions.WorksheetNotFound as e:
            st.error(f"¡Ups! No encontré la pestaña en tu Google Sheets. Asegúrate de que existan las pestañas con los nombres exactos.")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al conectar con Google: {e}")
