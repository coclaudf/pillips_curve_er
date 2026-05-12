import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de página
st.set_page_config(page_title="Simulador Macro Gastaldi", layout="wide")

st.title("Simulador Macroeconómico: Dinámica de Inflación y Producto")
st.markdown("Basado en el **Capítulo 16 de Gastaldi**. Este modelo permite comparar cómo el tipo de expectativas cambia la velocidad de ajuste de la economía.")

# --- Sidebar: Parámetros y Controles ---
st.sidebar.header("Configuración del Modelo")
tipo_expectativa = st.sidebar.radio(
    "Tipo de Expectativas:",
    ("Adaptativas (Basadas en el pasado)", "Racionales (Anticipación total)")
)

st.sidebar.markdown("---")
st.sidebar.header("Variables de Política")
y_p = st.sidebar.number_input("Producto Potencial ($y_p$)", value=100.0)
m_hat_inicial = 0.05
m_hat_nuevo = st.sidebar.slider("Nueva Expansión Monetaria ($\hat{M}$)", 0.0, 0.4, 0.15)
delta_F = st.sidebar.slider("Shock Fiscal ($\Delta F$)", -1.0, 1.0, 0.0)

st.sidebar.header("Parámetros de Sensibilidad")
alpha2 = st.sidebar.slider("Efecto Dinero Real (alpha2)", 0.1, 1.5, 0.5)
slope_oa = st.sidebar.slider("Pendiente de la OA (beta * gamma)", 0.1, 1.0, 0.4)

# --- Lógica del Modelo ---
def simular():
    periodos = 12
    y_hist = [y_p]
    pi_hist = [m_hat_inicial]
    pi_e_hist = [m_hat_inicial]
    
    k = slope_oa / y_p

    for t in range(periodos):
        if tipo_expectativa == "Racionales (Anticipación total)":
            # Con expectativas racionales y sin sorpresas, la inflación salta directo al nuevo m_hat
            # y el producto se mantiene en el potencial (y_p).
            pi_t = m_hat_nuevo
            y_t = y_p
            pi_e_t = m_hat_nuevo
        else:
            # Expectativas Adaptativas: pi_e_t = pi_{t-1}
            pi_e_t = pi_hist[-1]
            # Resolución del sistema DA-OA
            # pi = [ (y_t-1 - yp) + alpha1*dF + alpha2*m_hat + (1/k)*pi_e ] / [ (1/k) + alpha2 ]
            numerador = (y_hist[-1] - y_p) + (0.2 * delta_F) + (alpha2 * m_hat_nuevo) + (pi_e_t / k)
            denominador = (1 / k) + alpha2
            pi_t = numerador / denominador
            y_t = y_p + (1 / k) * (pi_t - pi_e_t)
        
        y_hist.append(y_t)
        pi_hist.append(pi_t)
        pi_e_hist.append(pi_e_t)
        
    return np.array(y_hist), np.array(pi_hist), np.array(pi_e_hist)

y_val, pi_val, pi_e_val = simular()

# --- Visualización Mejorada ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gráfico DA-OA (Espacio $y, \pi$)")
    # Dibujamos las curvas del último período para ver el equilibrio final
    y_range = np.linspace(y_p * 0.9, y_p * 1.1, 100)
    
    # Oferta Agregada (OA): pi = pi_e + k(y - yp)
    oa_final = pi_e_val[-1] + (slope_oa/y_p) * (y_range - y_p)
    # Demanda Agregada (DA): pi = m_hat - (1/alpha2)(y - y_prev)
    da_final = m_hat_nuevo - (1/alpha2) * (y_range - y_val[-2])
    
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(y_range, oa_final, label="Oferta Agregada (OA)", color='red', linewidth=2)
    ax1.plot(y_range, da_final, label="Demanda Agregada (DA)", color='blue', linewidth=2)
    ax1.axvline(y_p, color='black', linestyle='--', alpha=0.5, label="Producto Potencial")
    ax1.scatter(y_val[-1], pi_val[-1], color='black', zorder=5)
    ax1.annotate(f"Equilibrio Final\n$\pi$={pi_val[-1]:.2f}", (y_val[-1], pi_val[-1]), xytext=(5,5), textcoords='offset points')
    ax1.set_xlabel("Producto ($y$)")
    ax1.set_ylabel("Inflación ($\pi$)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with col2:
    st.subheader("Evolución Temporal")
    fig2, ax2 = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
    
    # Subplot Producto
    ax2[0].plot(y_val, label="Producto Real ($y$)", marker='o', color='royalblue')
    ax2[0].axhline(y_p, color='red', linestyle='--', label="$y_p$")
    ax2[0].set_ylabel("Nivel de Producto")
    ax2[0].legend()
    ax2[0].grid(True, alpha=0.2)
    
    # Subplot Inflación
    ax2[1].plot(pi_val, label="Inflación ($\pi$)", marker='s', color='forestgreen')
    ax2[1].plot(pi_e_val, label="Expectativas ($\pi^e$)", linestyle=':', color='orange')
    ax2[1].set_ylabel("Tasa de Inflación")
    ax2[1].set_xlabel("Tiempo (t)")
    ax2[1].legend()
    ax2[1].grid(True, alpha=0.2)
    
    st.pyplot(fig2)

# --- Explicación Económica ---
st.markdown("---")
if tipo_expectativa == "Racionales (Anticipación total)":
    st.success("**Análisis de Expectativas Racionales:** Como los agentes anticipan el aumento de la oferta monetaria, los salarios y precios suben instantáneamente. El producto no se desvía de su nivel potencial ($y_p$) y la inflación salta de inmediato al nuevo nivel de expansión monetaria.")
else:
    st.warning("**Análisis de Expectativas Adaptativas:** Los agentes ajustan sus expectativas lentamente basadas en la inflación pasada. Esto genera una brecha donde el producto aumenta transitoriamente por encima del potencial, pero luego regresa a $y_p$ a medida que la inflación se acelera y erosiona los saldos reales.")
