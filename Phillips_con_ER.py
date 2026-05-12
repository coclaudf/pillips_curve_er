import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo Dinámico DA-OA", layout="wide")

st.title("Modelo Macroeconómico: Transición del Corto al Largo Plazo")
st.markdown("Visualización de la convergencia hacia el estado estacionario ante un shock monetario.")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("1. Expectativas")
tipo_exp = st.sidebar.radio("Mecanismo de formación:", 
                            ["Adaptativas (Ajuste gradual)", "Racionales (Ajuste instantáneo)"])

st.sidebar.header("2. Shocks de Política")
m_hat_0 = 0.10  # Inflación y expansión inicial en estado estacionario
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (M^_1)", 0.0, 0.50, 0.25, step=0.01)

st.sidebar.header("3. Parámetros Estructurales")
y_p = 100.0
k = st.sidebar.slider("Pendiente OA (k)", 0.1, 2.0, 0.6, help="Respuesta de la inflación a la brecha de producto")
alpha2 = st.sidebar.slider("Sensibilidad DA (alpha2)", 0.1, 3.0, 1.5, help="Respuesta de la demanda a saldos reales")

# --- MOTOR MATEMÁTICO (40 PERÍODOS PARA VER CONVERGENCIA) ---
def simular():
    periodos = 40
    y_hist = [y_p]
    pi_hist = [m_hat_0]
    pie_hist = [m_hat_0]
    
    for t in range(1, periodos):
        if tipo_exp == "Racionales (Ajuste instantáneo)":
            # Salto directo al equilibrio de largo plazo
            pie_t = m_hat_1
            y_t = y_p
            pi_t = m_hat_1
        else:
            # Expectativas Adaptativas
            pie_t = pi_hist[-1]
            y_prev = y_hist[-1]
            
            # Sistema DA-OA dinámico
            # DA: y_t = y_{t-1} + alpha2*(m_hat_1 - pi_t)
            # OA: pi_t = pie_t + k*(y_t - y_p)
            numerador_y = y_prev + alpha2 * m_hat_1 - alpha2 * pie_t + alpha2 * k * y_p
            denominador_y = 1 + alpha2 * k
            y_t = numerador_y / denominador_y
            pi_t = pie_t + k * (y_t - y_p)
            
        y_hist.append(y_t)
        pi_hist.append(pi_t)
        pie_hist.append(pie_t)
        
    return np.array(y_hist), np.array(pi_hist), np.array(pie_hist)

y_v, pi_v, pie_v = simular()

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Plano DA-OA: Del Corto al Largo Plazo")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    y_rango = np.linspace(y_p - 15, y_p + 15, 100)
    
    # 1. ESTADO INICIAL (t=0)
    da_0 = m_hat_0 + (y_p - y_rango) / alpha2
    oa_0 = m_hat_0 + k * (y_rango - y_p)
    ax1.plot(y_rango, da_0, color='lightblue', linestyle='--', label='DA_0 (Inicial)')
    ax1.plot(y_rango, oa_0, color='lightcoral', linestyle='--', label='OA_0 (Inicial)')
    ax1.scatter(y_p, m_hat_0, color='gray', zorder=5)
    
    # 2. CORTO PLAZO (t=1) - Shock Monetario
    da_1 = m_hat_1 + (y_v[0] - y_rango) / alpha2  # La DA se desplaza por el nuevo M^
    oa_1 = pie_v[1] + k * (y_rango - y_p)         # OA_1 se mantiene o ajusta marginalmente
    
    if tipo_exp == "Adaptativas (Ajuste gradual)":
        ax1.plot(y_rango, da_1, color='blue', linewidth=2, label='DA_1 (Corto Plazo)')
        ax1.plot(y_rango, oa_1, color='red', linewidth=2, label='OA_1 (Corto Plazo)')
        ax1.scatter(y_v[1], pi_v[1], color='black', zorder=5)
        ax1.annotate("E_1 (Corto Plazo)", (y_v[1], pi_v[1]), xytext=(5, -15), textcoords='offset points')
    
    # 3. LARGO PLAZO (t=final) - Convergencia
    da_final = m_hat_1 + (y_v[-2] - y_rango) / alpha2
    oa_final = pie_v[-1] + k * (y_rango - y_p)
    
    ax1.plot(y_rango, da_final, color='navy', linestyle=':', linewidth=2.5, label='DA_final')
    ax1.plot(y_rango, oa_final, color='darkred', linestyle=':', linewidth=2.5, label='OA_final')
    
    # OFERTA AGREGADA DE LARGO PLAZO (Vertical)
    ax1.axvline(y_p, color='black', linewidth=2, label='OALP (Potencial)')
    ax1.scatter(y_p, m_hat_1, color='black', marker='*', s=150, zorder=6)
    ax1.annotate("E_final (Largo Plazo)", (y_p, m_hat_1), xytext=(-30, 15), textcoords='offset points')

    ax1.set_xlabel("Producto Real (y)")
    ax1.set_ylabel("Inflación ($\pi$)")
    ax1.legend(loc='upper right', fontsize='small')
    ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col2:
    st.subheader("Convergencia Temporal (40 períodos)")
    fig2, (ax2_y, ax2_pi) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Producto: Muestra la bonanza temporal y el regreso al potencial
    ax2_y.plot(y_v, marker='.', color='royalblue', label='Producto (y)')
    ax2_y.axhline(y_p, color='black', linestyle='--', label='y Potencial (Estado Estacionario)')
    ax2_y.set_ylabel("Producto")
    ax2_y.legend()
    ax2_y.grid(True, alpha=0.3)
    
    # Inflación: Muestra el overshoot o la convergencia a M^_1
    ax2_pi.plot(pi_v, marker='.', color='firebrick', label='Inflación Real ($\pi$)')
    ax2_pi.plot(pie_v, linestyle='--', color='darkorange', linewidth=2, label='Expectativas ($\pi^e$)')
    ax2_pi.axhline(m_hat_1, color='black', linestyle='--', label='Nueva M^ (Largo Plazo)')
    ax2_pi.set_ylabel("Inflación")
    ax2_pi.set_xlabel("Períodos (t)")
    ax2_pi.legend()
    ax2_pi.grid(True, alpha=0.3)
    
    st.pyplot(fig2)

st.info("**Dinámica observada:** El aumento en la expansión monetaria desplaza primero la DA. En **Adaptativas**, "
        "la economía se mueve a un nivel de producto superior al potencial temporalmente. Con el tiempo, "
        "las expectativas de inflación se corrigen, la OA se desplaza hacia arriba, y la economía "
        "converge nuevamente a la OALP vertical, donde el producto vuelve a ser $y_p$ pero con mayor inflación.")
