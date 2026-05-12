import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo DA-OA: Dinámica y Expectativas", layout="wide")

st.title("Modelo Macroeconómico: Demanda y Oferta Agregada")
st.markdown("Visualización estática (la cruz DA-OA) y dinámica (trayectoria temporal) ante shocks de política.")

# --- BARRA LATERAL: PARÁMETROS ---
st.sidebar.header("1. Expectativas")
tipo_exp = st.sidebar.radio("Mecanismo de formación:", ["Adaptativas (Ajuste gradual)", "Racionales (Ajuste instantáneo)"])

st.sidebar.header("2. Shocks de Política")
m_hat_0 = st.sidebar.number_input("Expansión Monetaria Inicial (M^_0)", value=0.10, step=0.01)
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (M^_1)", 0.0, 0.50, 0.20, step=0.01)
delta_f = st.sidebar.slider("Shock Fiscal (Delta F)", -5.0, 5.0, 0.0, step=0.5)

st.sidebar.header("3. Parámetros Estructurales")
y_p = st.sidebar.number_input("Producto Potencial (y_p)", value=100.0, step=10.0)
k = st.sidebar.slider("Pendiente OA (Sensibilidad k)", 0.1, 2.0, 0.5, help="Sensibilidad de la inflación a la brecha de producto")
alpha2 = st.sidebar.slider("Pendiente DA (Sensibilidad alpha2)", 0.1, 2.0, 1.0, help="Sensibilidad de la demanda a los saldos reales")
alpha1 = st.sidebar.slider("Sensibilidad Fiscal (alpha1)", 0.1, 2.0, 0.5)

# --- MOTOR MATEMÁTICO ---
def simular():
    periodos = 15
    y_hist = [y_p]
    pi_hist = [m_hat_0]
    pie_hist = [m_hat_0]
    
    for t in range(periodos):
        if tipo_exp == "Racionales (Ajuste instantáneo)":
            # Con expectativas racionales, los agentes anticipan M^_1 y Delta F.
            # Asumimos que conocen el modelo. pi^e salta al nuevo nivel de equilibrio previsto.
            # Equilibrio de LP previsto: y = yp + efecto fiscal permanente (simplificado aquí como transitorio)
            pie_t = m_hat_1 
        else:
            # Expectativas Adaptativas: pi^e_t = pi_{t-1}
            pie_t = pi_hist[-1]
            
        # Sistema de ecuaciones simultáneas para el período t:
        # OA: pi_t = pie_t + k*(y_t - y_p)
        # DA: y_t = y_{t-1} + alpha1*delta_f + alpha2*(m_hat_1 - pi_t)
        
        y_prev = y_hist[-1]
        
        # Despejando y_t algebraicamente de la sustitución de OA en DA:
        numerador_y = y_prev + alpha1 * delta_f + alpha2 * m_hat_1 - alpha2 * pie_t + alpha2 * k * y_p
        denominador_y = 1 + alpha2 * k
        y_t = numerador_y / denominador_y
        
        # Despejando pi_t de la OA:
        pi_t = pie_t + k * (y_t - y_p)
        
        y_hist.append(y_t)
        pi_hist.append(pi_t)
        pie_hist.append(pie_t)
        
    return np.array(y_hist), np.array(pi_hist), np.array(pie_hist)

y_v, pi_v, pie_v = simular()

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("La Cruz DA-OA (Equilibrio en t=1)")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    
    # Rango del eje X para graficar las rectas centrado en yp
    y_rango = np.linspace(y_p - 10, y_p + 10, 100)
    
    # Ecuación gráfica de la OA en t=1: pi = pie_1 + k*(y - yp)
    oa_t1 = pie_v[1] + k * (y_rango - y_p)
    
    # Ecuación gráfica de la DA en t=1: pi = M^_1 + (alpha1*df + y_0 - y) / alpha2
    da_t1 = m_hat_1 + (alpha1 * delta_f + y_v[0] - y_rango) / alpha2
    
    # Trazamos la "Cruz"
    ax1.plot(y_rango, oa_t1, color='red', linewidth=2.5, label='Oferta Agregada (SRAS t=1)')
    ax1.plot(y_rango, da_t1, color='blue', linewidth=2.5, label='Demanda Agregada (AD t=1)')
    
    # Línea de Producto Potencial (Oferta de Largo Plazo)
    ax1.axvline(y_p, color='black', linestyle='--', alpha=0.7, label='Producto Potencial (LRAS)')
    
    # Marcamos el punto de equilibrio exacto de la intersección
    ax1.scatter(y_v[1], pi_v[1], color='black', s=80, zorder=5)
    ax1.annotate(f"Eq. Corto Plazo\n(y={y_v[1]:.1f}, $\pi$={pi_v[1]:.2f})", 
                 (y_v[1], pi_v[1]), xytext=(15, 0), textcoords='offset points', 
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    ax1.set_xlabel("Producto Real (y)")
    ax1.set_ylabel("Tasa de Inflación ($\pi$)")
    ax1.set_title("Desplazamiento inicial tras el shock")
    ax1.legend(loc='lower right')
    ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col2:
    st.subheader("Trayectoria Temporal y Convergencia")
    fig2, (ax2_y, ax2_pi) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Evolución del Producto
    ax2_y.plot(y_v, marker='o', color='royalblue', label='Producto (y)')
    ax2_y.axhline(y_p, color='black', linestyle='--', label='y Potencial')
    ax2_y.set_ylabel("Nivel de Producto")
    ax2_y.legend()
    ax2_y.grid(True, alpha=0.3)
    
    # Evolución de Inflación y Expectativas
    ax2_pi.plot(pi_v, marker='s', color='firebrick', label='Inflación Real ($\pi$)')
    ax2_pi.plot(pie_v, marker='x', linestyle=':', color='darkorange', linewidth=2, label='Expectativas ($\pi^e$)')
    ax2_pi.axhline(m_hat_1, color='gray', linestyle='--', alpha=0.5, label='M^ (Estado Estacionario)')
    ax2_pi.set_ylabel("Tasa de Inflación")
    ax2_pi.set_xlabel("Períodos (t)")
    ax2_pi.legend()
    ax2_pi.grid(True, alpha=0.3)
    
    st.pyplot(fig2)
