import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo DA-OA Gastaldi", layout="wide")

st.title("Modelo Macroeconómico: Transición al Largo Plazo")
st.markdown("La DA se desplaza por shocks de política. La OA se desplaza por el ajuste de expectativas.")

# --- BARRA LATERAL ---
st.sidebar.header("1. Expectativas")
tipo_exp = st.sidebar.radio("Mecanismo de formación:", ["Adaptativas (Ajuste gradual)", "Racionales (Ajuste instantáneo)"])

st.sidebar.header("2. Escenario Inicial (Año 0)")
m_hat_0 = st.sidebar.number_input("Expansión Monetaria Inicial (M^_0)", value=0.10, step=0.01)

st.sidebar.header("3. Shocks de Política (A partir del Año 1)")
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (M^_1)", -0.10, 0.50, 0.20, step=0.01)
delta_f = st.sidebar.slider("Shock Fiscal (\u0394F)", -5.0, 5.0, 0.0, step=0.5)

st.sidebar.header("4. Parámetros Estructurales")
y_p = 100.0
k = st.sidebar.slider("Pendiente OA (k)", 0.1, 2.0, 0.8)
alpha2 = st.sidebar.slider("Sensibilidad DA a Saldos Reales (\u03B12)", 0.1, 2.0, 1.0)
alpha1 = st.sidebar.slider("Sensibilidad DA a Política Fiscal (\u03B11)", 0.1, 2.0, 0.5)

st.sidebar.header("5. Visualización temporal")
periodos_totales = 25
t_ver = st.sidebar.slider("Ver curvas en el año (t):", 0, periodos_totales-1, 1)

# --- MOTOR MATEMÁTICO CORREGIDO ---
def simular():
    y_hist = [y_p]
    pi_hist = [m_hat_0]
    pie_hist = [m_hat_0]
    
    # Equilibrio de Largo Plazo (Estado Estacionario)
    pi_ss = m_hat_1 + alpha1 * delta_f

    for t in range(1, periodos_totales):
        if tipo_exp == "Racionales (Ajuste instantáneo)":
            pie_t = pi_ss
            y_t = y_p
            pi_t = pi_ss
        else:
            # Expectativas Adaptativas (inflación pasada)
            pie_t = pi_hist[-1]
            
            # Equilibrio del período t
            # DA: pi_t = M^_1 + alpha1*delta_f - (1/alpha2)*(y_t - y_p)
            # OA: pi_t = pie_t + k*(y_t - y_p)
            # Igualando DA y OA para despejar (y_t - y_p):
            
            interseccion = m_hat_1 + alpha1 * delta_f - pie_t
            denominador = k + (1 / alpha2)
            
            y_t = y_p + (interseccion / denominador)
            pi_t = pie_t + k * (y_t - y_p)
            
        y_hist.append(y_t)
        pi_hist.append(pi_t)
        pie_hist.append(pie_t)
        
    return np.array(y_hist), np.array(pi_hist), np.array(pie_hist), pi_ss

y_v, pi_v, pie_v, pi_estacionaria = simular()

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Plano DA-OA (Año t = {t_ver})")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    y_rango = np.linspace(y_p - 15, y_p + 15, 100)
    
    # DA y OA en el AÑO 0 (Equilibrio Inicial) - GRIS
    da_0 = m_hat_0 - (1/alpha2) * (y_rango - y_p)
    oa_0 = m_hat_0 + k * (y_rango - y_p)
    ax1.plot(y_rango, da_0, color='lightgray', linestyle='--', label='DA (t=0)')
    ax1.plot(y_rango, oa_0, color='lightgray', linestyle='--', label='OA (t=0)')
    
    if t_ver > 0:
        # A partir del año 1, la DA salta a su nueva posición y SE QUEDA AHÍ.
        da_t = m_hat_1 + alpha1 * delta_f - (1/alpha2) * (y_rango - y_p)
        
        # La OA se mueve cada año dependiendo de pi^e
        pie_actual = pie_v[t_ver]
        oa_t = pie_actual + k * (y_rango - y_p)
        
        ax1.plot(y_rango, da_t, color='blue', linewidth=2.5, label='DA (Nuevo nivel)')
        ax1.plot(y_rango, oa_t, color='red', linewidth=2.5, label=f'OA (t={t_ver})')
        
        ax1.scatter(y_v[t_ver], pi_v[t_ver], color='black', s=80, zorder=5)
        ax1.annotate(f"E_{t_ver}", (y_v[t_ver], pi_v[t_ver]), xytext=(5, 5), textcoords='offset points')
    else:
        ax1.scatter(y_p, m_hat_0, color='black', s=80, zorder=5)
        ax1.annotate("E_0", (y_p, m_hat_0), xytext=(5, 5), textcoords='offset points')

    # OALP (Potencial)
    ax1.axvline(y_p, color='black', linewidth=1.5, label='OALP')
    
    # Marcador de Estado Estacionario Final
    ax1.scatter(y_p, pi_estacionaria, color='green', marker='*', s=150, zorder=6, label='Equilibrio Final LP')
    ax1.axhline(pi_estacionaria, color='green', linestyle=':', alpha=0.5)

    ax1.set_ylim(min(m_hat_0, pi_estacionaria) - 0.1, max(m_hat_0, pi_estacionaria) + 0.15)
    ax1.set_xlim(y_p - 10, y_p + 10)
    ax1.set_xlabel("Producto Real (y)")
    ax1.set_ylabel("Inflación ($\pi$)")
    ax1.legend(loc='lower right', fontsize='small')
    ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col2:
    st.subheader("Trayectoria (Años 0 a 25)")
    fig2, (ax2_y, ax2_pi) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Producto
    ax2_y.plot(y_v, marker='.', color='royalblue', label='Producto (y)')
    ax2_y.axhline(y_p, color='black', linestyle='--', label='y_p')
    ax2_y.axvline(t_ver, color='gray', linestyle=':', alpha=0.5) 
    ax2_y.set_ylabel("Producto")
    ax2_y.legend()
    ax2_y.grid(True, alpha=0.3)
    
    # Inflación
    ax2_pi.plot(pi_v, marker='.', color='firebrick', label='Inflación ($\pi$)')
    ax2_pi.plot(pie_v, linestyle='--', color='darkorange', linewidth=2, label='Expectativas ($\pi^e$)')
    ax2_pi.axhline(pi_estacionaria, color='green', linestyle=':', label='$\pi$ Estado Estacionario')
    ax2_pi.axvline(t_ver, color='gray', linestyle=':', alpha=0.5) 
    ax2_pi.set_ylabel("Inflación")
    ax2_pi.set_xlabel("Años (t)")
    ax2_pi.legend()
    ax2_pi.grid(True, alpha=0.3)
    
    st.pyplot(fig2)
