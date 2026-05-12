import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dinámica de Inflación y Producto", layout="wide")

st.title("Dinámica de Ajuste: Inflación y Producto")
st.markdown("Evolución temporal ante un shock monetario bajo distintos supuestos de expectativas.")

# --- BARRA LATERAL ---
st.sidebar.header("1. Supuesto de Expectativas")
tipo_exp = st.sidebar.radio(
    "Mecanismo de formación:", 
    [
        "Adaptativas (Ajuste gradual)", 
        "Racionales (Previsión perfecta)", 
        "Racionales (Sorpresa en t=1)"
    ]
)

st.sidebar.header("2. Escenario y Shocks")
m_hat_0 = st.sidebar.number_input("Expansión Monetaria Inicial (M^_0)", value=0.10, step=0.01)
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (M^_1 a partir de t=1)", 0.0, 0.50, 0.25, step=0.01)

st.sidebar.header("3. Parámetros Estructurales")
y_p = 100.0
k = st.sidebar.slider("Pendiente Curva de Phillips (k)", 0.1, 2.0, 0.5, help="Sensibilidad de la inflación a la brecha de producto")
alpha = st.sidebar.slider("Sensibilidad de la DA (\u03B1)", 0.1, 3.0, 1.0, help="Sensibilidad de la demanda a los saldos reales")

t_max = 20

# --- MOTOR MATEMÁTICO ---
def simular_dinamica():
    y_h, pi_h, pie_h = [y_p], [m_hat_0], [m_hat_0]
    
    for t in range(1, t_max + 1):
        # Determinación de las expectativas según el escenario
        if tipo_exp == "Adaptativas (Ajuste gradual)":
            pie_t = pi_h[-1] # Miran la inflación pasada
            
        elif tipo_exp == "Racionales (Previsión perfecta)":
            pie_t = m_hat_1  # Conocen y creen en el anuncio de política instantáneamente
            
        elif tipo_exp == "Racionales (Sorpresa en t=1)":
            if t == 1:
                pie_t = m_hat_0 # En t=1 los toma por sorpresa, esperaban la política anterior
            else:
                pie_t = m_hat_1 # En t=2 ya ajustan perfectamente a la nueva realidad
                
        # Resolución del sistema para el período t:
        # Brecha de DA: y_t - y_p = alpha * (m_hat_1 - pi_t)
        # Oferta (Phillips): pi_t = pie_t + k * (y_t - y_p)
        #
        # Sustituyendo y despejando obtenemos:
        y_t = y_p + (alpha / (1 + alpha * k)) * (m_hat_1 - pie_t)
        pi_t = pie_t + (alpha * k / (1 + alpha * k)) * (m_hat_1 - pie_t)
            
        y_h.append(y_t)
        pi_h.append(pi_t)
        pie_h.append(pie_t)
        
    return np.array(y_h), np.array(pi_h), np.array(pie_h)

y_v, pi_v, pie_v = simular_dinamica()

# --- VISUALIZACIÓN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Evolución del Producto ($y$)")
    fig_y, ax_y = plt.subplots(figsize=(8, 5))
    ax_y.plot(y_v, marker='o', color='royalblue', linewidth=2, label='Producto Real ($y_t$)')
    ax_y.axhline(y_p, color='black', linestyle='--', linewidth=1.5, label='Producto Potencial ($y_p$)')
    ax_y.axvline(1, color='gray', linestyle=':', alpha=0.5, label='Shock (t=1)')
    
    ax_y.set_xlabel("Períodos (t)", fontsize=11)
    ax_y.set_ylabel("Nivel de Producto", fontsize=11)
    # Margen dinámico para que se vea bien el salto
    margen_y = max(abs(max(y_v) - y_p), abs(min(y_v) - y_p)) * 1.5
    if margen_y == 0: margen_y = 5 # Por si es línea plana
    ax_y.set_ylim(y_p - margen_y, y_p + margen_y)
    
    ax_y.legend()
    ax_y.grid(True, alpha=0.3)
    st.pyplot(fig_y)

with col2:
    st.subheader("Evolución de la Inflación ($\pi$)")
    fig_pi, ax_pi = plt.subplots(figsize=(8, 5))
    ax_pi.plot(pi_v, marker='s', color='firebrick', linewidth=2, label='Inflación Real ($\pi_t$)')
    ax_pi.plot(pie_v, marker='x', linestyle=':', color='darkorange', linewidth=2, label='Expectativas ($\pi^e_t$)')
    ax_pi.axhline(m_hat_1, color='green', linestyle='--', linewidth=1.5, label='Nueva Emisión ($\hat{M}_1$)')
    ax_pi.axvline(1, color='gray', linestyle=':', alpha=0.5, label='Shock (t=1)')
    
    ax_pi.set_xlabel("Períodos (t)", fontsize=11)
    ax_pi.set_ylabel("Tasa de Inflación", fontsize=11)
    # Margen dinámico
    margen_pi = max(abs(m_hat_1 - m_hat_0) * 1.5, 0.05)
    ax_pi.set_ylim(min(m_hat_0, m_hat_1) - margen_pi, max(m_hat_0, m_hat_1) + margen_pi)
    
    ax_pi.legend()
    ax_pi.grid(True, alpha=0.3)
    st.pyplot(fig_pi)

# --- CAJA DE EXPLICACIÓN PEDAGÓGICA ---
st.markdown("---")
if tipo_exp == "Adaptativas (Ajuste gradual)":
    st.info("**Análisis - Adaptativas:** El ajuste es asintótico. El shock genera un error de previsión persistente porque los agentes miran hacia atrás. Esto provoca que el producto se mantenga por encima del potencial durante varios períodos (hay *trade-off* prolongado) hasta que la inflación y las expectativas convergen gradualmente a la nueva tasa de expansión monetaria.")
elif tipo_exp == "Racionales (Previsión perfecta)":
    st.success("**Análisis - Racionales (Anunciado):** La política es totalmente neutral incluso en el corto plazo. Como los agentes confían en el anuncio y comprenden el modelo, ajustan los precios/salarios instantáneamente en $t=1$. El producto jamás se desvía de su nivel potencial; la inflación salta directo al nuevo equilibrio.")
else:
    st.warning("**Análisis - Racionales (Sorpresa):** La política tiene efectos reales pero *solo durante un período*. En $t=1$, el shock inesperado engaña a los agentes, generando un pico de producto. Sin embargo, a partir de $t=2$, los agentes incorporan la nueva información (expectativas racionales) y el producto regresa inmediatamente al potencial, eliminando el *trade-off*.")
