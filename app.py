import streamlit as st
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
supabase = create_client(url, key)

st.title("Mi Negocio")

with st.form("nuevo_registro"):
    tipo = st.selectbox("Tipo", ["venta", "compra", "factura_emitida", "factura_recibida"])
    descripcion = st.text_input("Descripción")
    monto_texto = st.text_input("Monto (ej: 1.256.000)")
    fecha = st.date_input("Fecha")
    enviado = st.form_submit_button("Guardar")

if enviado:
    try:
        monto = float(monto_texto.replace(".", "").replace(",", "."))
    except ValueError:
        st.error("Escribe el monto solo con números y puntos, ej: 1.256.000")
        st.stop()
    supabase.table("transacciones").insert({
        "tipo": tipo,
        "descripcion": descripcion,
        "monto": monto,
        "fecha": str(fecha),
    }).execute()
    st.success("Guardado correctamente")
    
st.divider()
st.subheader("Movimientos")

datos = supabase.table("transacciones").select("*").order("fecha").execute()
filas = datos.data

st.divider()
st.subheader("Movimientos")

datos = supabase.table("transacciones").select("*").order("fecha").execute()
filas = datos.data

if filas:
    st.dataframe(filas, use_container_width=True)

    signos = {"venta": 1, "compra": -1, "factura_emitida": 1, "factura_recibida": -1}
    saldo = 0
    for f in filas:
        if f["tipo"] in ("venta", "compra") or f.get("estado") == "pagada":
            saldo += signos[f["tipo"]] * float(f["monto"])

    st.metric("Saldo neto", f"${saldo:,.2f}")
else:
    st.info("Aún no hay movimientos registrados.")
    
    
st.divider()
st.subheader("Editar o eliminar")

if filas:
    ids = [f["id"] for f in filas]
    id_seleccionado = st.selectbox("Elige el ID a modificar", ids)
    registro = next(f for f in filas if f["id"] == id_seleccionado)

    with st.form("editar_registro"):
        tipo_e = st.selectbox("Tipo", ["venta", "compra", "factura_emitida", "factura_recibida"],
                               index=["venta", "compra", "factura_emitida", "factura_recibida"].index(registro["tipo"]))
        descripcion_e = st.text_input("Descripción", value=registro["descripcion"])
        monto_e_texto = st.text_input("Monto", value=f"{float(registro['monto']):,.0f}".replace(",", "."))
        col1, col2 = st.columns(2)
        actualizar = col1.form_submit_button("Actualizar")
        eliminar = col2.form_submit_button("Eliminar")

    if actualizar:
        monto_e = float(monto_e_texto.replace(".", "").replace(",", "."))
        supabase.table("transacciones").update({
            "tipo": tipo_e,
            "descripcion": descripcion_e,
            "monto": monto_e,
        }).eq("id", id_seleccionado).execute()
        st.success("Actualizado")
        st.rerun()

    if eliminar:
        supabase.table("transacciones").delete().eq("id", id_seleccionado).execute()
        st.success("Eliminado")
        st.rerun()