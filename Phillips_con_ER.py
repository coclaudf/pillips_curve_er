import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo Macro Gastaldi v2", layout="wide")

st.title("Simulador Dinámico: DA-OA y Expectativas")
st.markdown("Este modelo visualiza el ajuste de la inflación y el producto según el **Capítulo 16 de Gastaldi**.")

# --- Sidebar ---
st.sidebar.header("Configuración de Expectativas")
tipo_exp = st.sidebar.radio("Tipo de Expectativas:", ["Adaptativas", "Racionales"])

st.sidebar.header("Parámetros de la Economía")
y_p = 100.0  # Producto potencial fijo para facilitar la visualización
# Aumentamos el rango de la pendiente para que sea visualmente clara
k = st.sidebar.slider("Pendiente de la OA (Sensibilidad k)", 0.1, 2.0, 0.8)
alpha2 = st.sidebar.slider("Sensibilidad de la DA (alpha2)", 0.5, 5.0, 2.0)

st.sidebar.header("Shocks de Política")
m_hat_0 = 0.10  # Inflación inicial y expansión monetaria inicial
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (m^)", 0.0, 0.5, 0.20)

# --- Motor de Simulación ---
def simular_modelo(periodos=15):
    y = [y_p]
    pi = [m_hat_0]
    pi_e = [m_hat_0]
    
    for t in range(periodos):
        if tipo_exp == "Racionales":
            # Con expectativas racionales y política anunciada, 
            # pi se ajusta instantáneamente y y no cambia.
            y_t = y_p
            pi_t = m_hat_1
            pi_e_t = m_hat_1
        else:
            # Expectativas Adaptativas: pi_e(t) = pi(t-1)
            pi_e_t = pi[-1]
            
            # Resolviendo el sistema:
            # OA: pi = pi_e + k * (y - yp)
            # DA: y = y_prev + alpha2 * (m_hat - pi)
            # Sustituyendo OA en DA:
            # y = y_prev + alpha2 * (m_hat - (pi_e + k*(y - yp)))
            # y * (1 + alpha2*k) = y_prev + alpha2*m_hat - alpha2*pi_e + alpha2*k*yp
            
            y_prev = y[-1]
            num = y_prev + alpha2 * m_hat_1 - alpha2 * pi_e_t + alpha2 * k * y_p
            den = 1 + alpha2 * k
            y_t = num / den
            pi_t = pi_e_t + k * (y_t - y_p)
            
        y.append(y_t)
        pi.append(pi_t)
        pi_e.append(pi_e_t)
        
    return np.array(y), np.array(pi), np.array(pi_e)

y_vec, pi_vec, pie_vec = simular_modelo()

# --- Visualización ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gráfico DA-OA (Equilibrio de Mercado)")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Rango para las curvas
    y_range = np.linspace(y_p - 15, y_p + 15, 100)
    
    # Oferta Agregada (OA): pi = pi_e + k(y - yp)
    # Mostramos la OA del período de ajuste (t=1)
    oa_curva = pie_vec[1] + k * (y_range - y_p)
    
    # Demanda Agregada (DA): pi = m_hat - (1/alpha2)(y - y_prev)
    da_curva = m_hat_1 - (1/alpha2) * (y_range - y_vec[0])
    
    ax.plot(y_range, oa_curva, color='red', label="Oferta Agregada (OA)", linewidth=2)
    ax.plot(y_range, da_curva, color='blue', label="Demanda Agregada (DA)", linewidth=2)
    
    # Líneas de referencia
    ax.axvline(y_p, color='gray', linestyle='--', label="y potencial")
    ax.axhline(m_hat_1, color='green', linestyle=':', label="Nuevo m^ (Largo Plazo)")
    
    # Punto de equilibrio actual (t=1)
    ax.scatter(y_vec[1], pi_vec[1], color='black', zorder=5)
    ax.annotate(f"Equilibrio t=1\n(y={y_vec[1]:.1f}, $\pi$={pi_vec[1]:.2f})", 
                (y_vec[1], pi_vec[1]), xytext=(10, 10), textcoords='offset points')

    ax.set_ylim(0, m_hat_1 + 0.15)
    ax.set_xlabel("Producto (y)")
    ax.set_ylabel("Inflación ($\pi$)")
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with col2:
    st.subheader("Tránsito al Largo Plazo")
    fig2, ax2 = plt.subplots(2, 1, figsize=(8, 8))
    
    # Producto
    ax2[0].plot(y_vec, marker='o', color='royalblue', label="Producto (y)")
    ax2[0].axhline(y_p, color='red', linestyle='--')
    ax2[0].set_ylabel("Producto")
    ax2[0].legend()
    
    # Inflación
    ax2[1].plot(pi_vec, marker='s', color='forestgreen', label="Inflación ($\pi$)")
    ax2[1].plot(pie_vec, linestyle=':', color='orange', label="Expectativas ($\pi^e$)")
    ax2[1].axhline(m_hat_1, color='black', linestyle='--', alpha=0.3)
    ax2[1].set_ylabel("Inflación")
    ax2[1].set_xlabel("Períodos")
    ax2[1].legend()
    
    st.pyplot(fig2)

# --- Explicación dinámica ---
st.info(f"**Análisis:** En el gráfico de la izquierda, ahora puedes ver claramente la pendiente positiva de la OA. "
        f"Con un k={k}, un aumento del producto genera un aumento proporcional en la inflación.")
