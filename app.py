from datetime import datetime
import json, os
from typing import List, Dict
import streamlit as st

# --- Lógica de usuario ---
USERS_FILE = "usuarios.json"

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def guardar_usuarios(usuarios):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def registrar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    if usuario in usuarios:
        return False
    usuarios[usuario] = password
    guardar_usuarios(usuarios)
    return True

def validar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    return usuarios.get(usuario) == password


# --- Lógica de gastos ---
class Gasto:
    def __init__(self, descripcion: str, monto: float, categoria: str, fecha: str = None):
        self.descripcion = descripcion
        self.monto = monto
        self.categoria = categoria
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        return {'descripcion': self.descripcion, 'monto': self.monto,
                'categoria': self.categoria, 'fecha': self.fecha}

    @classmethod
    def from_dict(cls, data: Dict) -> 'Gasto':
        return cls(data['descripcion'], data['monto'], data['categoria'], data['fecha'])


class GestorGastos:
    def __init__(self, usuario: str):
        self.archivo_datos = f"gastos_{usuario}.json"
        self.gastos: List[Gasto] = []
        self.cargar_datos()

    def cargar_datos(self):
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                self.gastos = [Gasto.from_dict(d) for d in datos]
            except Exception:
                self.gastos = []

    def guardar_datos(self):
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump([g.to_dict() for g in self.gastos], f, ensure_ascii=False, indent=2)

    def agregar_gasto(self, descripcion, monto, categoria):
        self.gastos.append(Gasto(descripcion, monto, categoria))
        self.guardar_datos()

    def eliminar_gasto(self, indice):
        if 0 <= indice < len(self.gastos):
            self.gastos.pop(indice)
            self.guardar_datos()

    def obtener_categorias(self):
        return sorted(list({g.categoria for g in self.gastos}))

    def total(self):
        return sum(g.monto for g in self.gastos)


# --- Streamlit UI ---
st.set_page_config(page_title="Gestor de Gastos con Usuarios", layout="wide")
st.title("💰 Gestor de Gastos (web)")

# --- Registro / Login ---
if "usuario" not in st.session_state:
    st.session_state.usuario = None

st.sidebar.header("Usuario")
opcion = st.sidebar.radio("Acción", ["Iniciar sesión", "Registrarse"])

if opcion == "Registrarse":
    nuevo_usuario = st.sidebar.text_input("Usuario", key="reg_usuario")
    nueva_password = st.sidebar.text_input("Contraseña", type="password", key="reg_pass")
    if st.sidebar.button("Registrar"):
        if registrar_usuario(nuevo_usuario, nueva_password):
            st.success("Usuario registrado correctamente. Ahora inicia sesión.")
        else:
            st.error("El usuario ya existe.")
else:  # Iniciar sesión
    usuario = st.sidebar.text_input("Usuario", key="login_usuario")
    password = st.sidebar.text_input("Contraseña", type="password", key="login_pass")
    if st.sidebar.button("Ingresar"):
        if validar_usuario(usuario, password):
            st.session_state.usuario = usuario
            st.success(f"Bienvenido {usuario}")
        else:
            st.error("Usuario o contraseña incorrectos")

# Solo mostrar la app si hay usuario logueado
if st.session_state.usuario:
    gestor = GestorGastos(st.session_state.usuario)

    # Sidebar: agregar gasto
    with st.sidebar.form("nuevo_gasto"):
        st.header("Agregar gasto")
        desc = st.text_input("Descripción")
        monto = st.text_input("Monto (ej: 12.50)")
        cat = st.selectbox("Categoría", ["Comida", "Transporte", "Salud", "Educación", "Otros"])
        submitted = st.form_submit_button("Agregar")
        if submitted:
            try:
                m = float(monto)
                if m <= 0:
                    st.error("Monto debe ser mayor a 0")
                else:
                    gestor.agregar_gasto(desc, m, cat)
                    st.success("Gasto agregado")
            except ValueError:
                st.error("Monto inválido")

    # Listado de gastos y filtros
    cols = st.columns([3, 1])
    with cols[0]:
        st.subheader("Listado de gastos")
        filtro_cat = st.selectbox("Filtrar por categoría", ["Todas"] + gestor.obtener_categorias())
        mostrar = gestor.gastos if filtro_cat == "Todas" else [g for g in gestor.gastos if g.categoria == filtro_cat]

        if mostrar:
            for i, g in enumerate(mostrar):
                st.write(f"**{g.descripcion}** — ${g.monto:.2f} — {g.categoria} — {g.fecha}")
                if st.button(f"Eliminar {i}", key=f"del_{i}"):
                    real_index = gestor.gastos.index(mostrar[i])
                    gestor.eliminar_gasto(real_index)
                    st.experimental_rerun()
        else:
            st.info("No hay gastos registrados")

    # Estadísticas
    with cols[1]:
        st.subheader("Estadísticas")
        st.metric("Total gastos", f"${gestor.total():.2f}")
        st.write("Categorías:", ", ".join(gestor.obtener_categorias()))
