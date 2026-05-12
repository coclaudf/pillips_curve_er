import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo Gastaldi Cap. 16", layout="wide")

st.title("Simulador Macroeconómico: Inflación, Dinero y Producto")
st.markdown("Basado en *Gastaldi, S. - Capítulo 16: La relación entre inflación, dinero y producto*.")

# --- Sidebar: Parámetros y Shocks ---
st.sidebar.header("Parámetros Estructurales")
y_p = st.sidebar.number_input("Producto Potencial (y_p)", value=100.0)
alpha2 = st.sidebar.slider("Sensibilidad Dinero Real (alpha2)", 0.1, 2.0, 0.5)
beta_gamma = st.sidebar.slider("Pendiente OA (beta * gamma)", 0.1, 2.0, 0.4)

st.sidebar.header("Variables de Política y Expectativas")
m_hat = st.sidebar.slider("Expansión Monetaria (M^)", 0.0, 0.5, 0.10, help="Tasa de crecimiento de la cantidad de dinero")
delta_F = st.sidebar.slider("Cambio Déficit Fiscal (delta F)", -1.0, 1.0, 0.0)
pi_e_inicial = st.sidebar.slider("Inflación Esperada (pi^e)", 0.0, 0.5, 0.10)

# --- Lógica del Modelo ---
def calcular_equilibrio(y_prev, pi_e, m_hat, delta_F, y_p, alpha2, beta_gamma, alpha1=0.2, alpha3=0.1):
    # Resolviendo el sistema DA-OA para pi (Inflación)
    # OA: pi = pi_e + (beta_gamma/y_p) * (y - y_p)
    # DA: y = y_prev + alpha1*delta_F + alpha2*(m_hat - pi) + alpha3*delta_pi_e
    # Simplificando para equilibrio estático (delta_pi_e = 0)
    
    k = beta_gamma / y_p
    numerador = y_prev - y_p + alpha1*delta_F + alpha2*m_hat + (1/k)*pi_e
    denominador = (1/k) + alpha2
    
    pi_star = numerador / denominador
    y_star = y_p + (1/k) * (pi_star - pi_e)
    
    return y_star, pi_star

# --- Simulación Dinámica (10 períodos) ---
periodos = 10
y_hist = [y_p]
pi_hist = [m_hat]
pi_e_hist = [pi_e_inicial]

for t in range(periodos):
    y_t, pi_t = calcular_equilibrio(y_hist[-1], pi_e_hist[-1], m_hat, delta_F, y_p, alpha2, beta_gamma)
    y_hist.append(y_t)
    pi_hist.append(pi_t)
    # Expectativas adaptativas pi_e(t+1) = pi(t)
    pi_e_hist.append(pi_t)

# --- Visualización ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Dinámica del Producto (y)")
    fig_y, ax_y = plt.subplots()
    ax_y.plot(y_hist, marker='o', color='blue')
    ax_y.axhline(y_p, linestyle='--', color='red', label='y_p')
    ax_y.set_xlabel("Período")
    ax_y.legend()
    st.pyplot(fig_y)

with col2:
    st.subheader("Dinámica de la Inflación (pi)")
    fig_pi, ax_pi = plt.subplots()
    ax_pi.plot(pi_hist, marker='s', color='green', label='Inflación')
    ax_pi.plot(pi_e_hist[:-1], marker='x', linestyle=':', color='orange', label='Expectativa')
    ax_pi.set_xlabel("Período")
    ax_pi.legend()
    st.pyplot(fig_pi)

st.info("El modelo muestra cómo una expansión monetaria superior al crecimiento del producto potencial genera inflación en el largo plazo[cite: 31].")