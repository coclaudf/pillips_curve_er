import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo DA-OA Estándar", layout="wide")

st.title("Simulador Macroeconómico: Modelo DA-OA Dinámico")
st.markdown("Basado en el marco teórico de Gastaldi. La DA responde a la política, la OA al ajuste de expectativas.")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("1. Mecanismo de Expectativas")
tipo_exp = st.sidebar.radio("Tipo:", ["Adaptativas (Ajuste gradual)", "Racionales (Ajuste instantáneo)"])

st.sidebar.header("2. Equilibrio Inicial (Año 0)")
pi_0 = st.sidebar.number_input("Inflación Inicial ($\pi_0$)", value=0.10, step=0.01)

st.sidebar.header("3. Shocks de Política (Año 1 en adelante)")
m_hat = st.sidebar.slider("Nueva Expansión Monetaria ($\hat{M}$)", -0.10, 0.60, 0.25, step=0.01)
delta_f = st.sidebar.slider("Shock Fiscal ($\Delta F$)", -10.0, 10.0, 0.0, step=0.5)

st.sidebar.header("4. Sensibilidades (Pendientes)")
y_p = 100.0 # Producto Potencial
k = st.sidebar.slider("Pendiente OA (k)", 0.2, 2.0, 0.7)
alpha2 = st.sidebar.slider("Sensibilidad DA (alpha2)", 0.2, 3.0, 1.2)
alpha1 = 0.5 # Sensibilidad fiscal fija

st.sidebar.header("5. Control de Tiempo")
t_max = 20
t_ver = st.sidebar.slider("Año a visualizar:", 0, t_max, 1)

# --- MOTOR LÓGICO ---
def calcular_trayectoria():
    y_h, pi_h, pie_h = [y_p], [pi_0], [pi_0]
    
    # Inflación de Largo Plazo (Estado Estacionario)
    # En el LP: y = yp, por lo tanto pi = m_hat + (alpha1/alpha2)*delta_f
    pi_ss = m_hat + (alpha1 / alpha2) * delta_f

    for t in range(1, t_max + 1):
        if tipo_exp == "Racionales (Ajuste instantáneo)":
            pie_t = pi_ss
            y_t = y_p
            pi_t = pi_ss
        else:
            # Adaptativas: pi^e = pi_{t-1}
            pie_t = pi_h[-1]
            
            # Sistema de Ecuaciones:
            # DA: pi = (m_hat + (alpha1/alpha2)*delta_f) - (1/alpha2)*(y - y_p)
            # OA: pi = pie_t + k*(y - y_p)
            
            intercepto_da = m_hat + (alpha1 / alpha2) * delta_f
            # Resolviendo para (y - y_p):
            gap_y = (intercepto_da - pie_t) / (k + (1 / alpha2))
            
            y_t = y_p + gap_y
            pi_t = pie_t + k * gap_y
            
        y_h.append(y_t)
        pi_h.append(pi_t)
        pie_h.append(pie_t)
        
    return np.array(y_h), np.array(pi_h), np.array(pie_h), pi_ss

y_v, pi_v, pie_v, pi_ss = calcular_trayectoria()

# --- INTERFAZ GRÁFICA ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Plano Inflación - Producto (Año {t_ver})")
    fig, ax = plt.subplots(figsize=(10, 7))
    y_range = np.linspace(y_p - 15, y_p + 15, 100)
    
    # 1. CURVAS AÑO 0 (Gris)
    da_0 = pi_0 - (1/alpha2) * (y_range - y_p)
    oa_0 = pi_0 + k * (y_range - y_p)
    ax.plot(y_range, da_0, color='lightgray', linestyle='--', label='DA inicial (t=0)')
    ax.plot(y_range, oa_0, color='lightgray', linestyle='--', label='OA inicial (t=0)')
    
    # 2. CURVAS DINÁMICAS
    if t_ver > 0:
        # La DA se mueve en t=1 y se queda AHÍ
        da_t = (m_hat + (alpha1 / alpha2) * delta_f) - (1/alpha2) * (y_range - y_p)
        # La OA se mueve cada período según pie_v[t_ver]
        oa_t = pie_v[t_ver] + k * (y_range - y_p)
        
        ax.plot(y_range, da_t, color='blue', linewidth=3, label='Demanda Agregada (DA)')
        ax.plot(y_range, oa_t, color='red', linewidth=3, label=f'Oferta Agregada (OA t={t_ver})')
        
        # Punto de equilibrio actual
        ax.scatter(y_v[t_ver], pi_v[t_ver], color='black', s=100, zorder=5)
        ax.annotate(f"E_{t_ver}", (y_v[t_ver], pi_v[t_ver]), xytext=(10, 10), textcoords='offset points', weight='bold')
    else:
        ax.scatter(y_p, pi_0, color='black', s=100, zorder=5)
    
    # Referencias de Largo Plazo
    ax.axvline(y_p, color='black', linewidth=1, label='OALP (Potencial)')
    ax.axhline(pi_ss, color='green', linestyle=':', alpha=0.6, label='$\pi$ de Largo Plazo')
    ax.scatter(y_p, pi_ss, color='green', marker='*', s=200, label='Equilibrio Final')

    ax.set_xlabel("Producto Real (y)", fontsize=12)
    ax.set_ylabel("Tasa de Inflación ($\pi$)", fontsize=12)
    ax.set_ylim(min(pi_0, pi_ss) - 0.1, max(pi_0, pi_ss) + 0.15)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with col2:
    st.subheader("Series Temporales")
    # Gráfico de Producto
    fig_y, ax_y = plt.subplots(figsize=(5, 4))
    ax_y.plot(y_v, color='blue', marker='.')
    ax_y.axhline(y_p, color='black', linestyle='--')
    ax_y.axvline(t_ver, color='red', alpha=0.3)
    ax_y.set_title("Evolución del Producto")
    st.pyplot(fig_y)
    
    # Gráfico de Inflación
    fig_pi, ax_pi = plt.subplots(figsize=(5, 4))
    ax_pi.plot(pi_v, color='red', marker='.')
    ax_pi.plot(pie_v, color='orange', linestyle=':', label='$\pi^e$')
    ax_pi.axhline(pi_ss, color='green', linestyle='--')
    ax_pi.axvline(t_ver, color='blue', alpha=0.3)
    ax_pi.set_title("Evolución de la Inflación")
    st.pyplot(fig_pi)

st.info("**Guía para la clase:** Notarás que en t=1 la DA salta y genera un aumento del producto (brecha positiva). Desde t=2 en adelante, la DA no cambia, pero la línea roja (OA) sube año tras año buscando la nueva inflación esperada, lo que 'empuja' el equilibrio hacia atrás por la curva de demanda hasta que el producto vuelve al potencial.")
