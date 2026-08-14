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
    # Usamos st.secrets para guardar la llave de forma segura (invisible para el usuario)
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
# Usamos un "form" para que la página no se recargue hasta que presionen el botón
with st.form("formulario_inscripcion", clear_on_submit=True):
    
    st.subheader("Tus Datos")
    
    # Cajas de texto para que el usuario escriba
    nombre = st.text_input("Nombre completo")
    telefono = st.text_input("Número de teléfono (WhatsApp)")
    
    # Menú desplegable (selectbox) para elegir el curso
    lista_cursos = [
        "VERDADES FUNDAMENTALES", 
        "IGLESIA DISCIPULADORA", 
        "APOLOGÉTICA"
    ]
    curso_elegido = st.selectbox("¿A qué curso deseas anotarte?", lista_cursos)
    
    # Botón para enviar
    boton_enviar = st.form_submit_button("Inscribirme al curso")

# 3. ¿Qué pasa cuando presionan el botón?
if boton_enviar:
    # Verificamos que no hayan dejado su nombre vacío
    if nombre == "":
        st.error("Por favor, escribe tu nombre antes de enviarlo.")
    else:
        # Aquí capturamos la fecha actual
        fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        try:
            # 1. Nos conectamos a Google
            cliente = conectar_google_sheets()
            
            # 2. Abrimos tu planilla (Asegúrate de crear una con este nombre exacto)
            planilla = cliente.open("Inscripciones Cursos")
            
            # 3. Elegimos la pestaña correcta según el curso
            pestana_curso = planilla.worksheet(curso_elegido)
            
            # 4. Anotamos la fila con los datos del hermano/a
            pestana_curso.append_row([fecha_registro, nombre, telefono])
            
            st.success(f"¡Gloria a Dios! 🎉 {nombre}, te has inscrito exitosamente en {curso_elegido}.")
            st.balloons()
            
        except KeyError:
            # Si aún no ponemos la llave secreta, avisamos amablemente
            st.warning("⚠️ El formulario funciona, pero falta configurar la 'Llave de Google' para que los datos lleguen a tu planilla.")
            st.info(f"Datos guardados temporalmente: {nombre} - {curso_elegido}")
            
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"¡Ups! No encontré una pestaña llamada '{curso_elegido}' en tu Google Sheets. Por favor créala.")
            
        except Exception as e:
            st.error(f"Ocurrió un error inesperado al conectar con Google: {e}")