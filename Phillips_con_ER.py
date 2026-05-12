import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Modelo Dinámico Gastaldi", layout="wide")

st.title("Modelo Macroeconómico: DA-OA Dinámico")
st.markdown("Visualización período a período de la convergencia (Gastaldi Cap. 16).")

# --- BARRA LATERAL ---
st.sidebar.header("1. Expectativas")
tipo_exp = st.sidebar.radio("Mecanismo:", ["Adaptativas", "Racionales"])

st.sidebar.header("2. Shocks de Política (Expansivos o Contractivos)")
m_hat_0 = 0.10  # Estado inicial
m_hat_1 = st.sidebar.slider("Nueva Expansión Monetaria (M^_1)", -0.20, 0.50, 0.20, step=0.01, help="Valores < 0.10 son contractivos respecto al inicio")
delta_f = st.sidebar.slider("Shock Fiscal (\u0394F)", -10.0, 10.0, 5.0, step=0.5, help="Cambio en el déficit. Negativo = Ajuste fiscal")

st.sidebar.header("3. Parámetros Estructurales")
y_p = 100.0
k = st.sidebar.slider("Pendiente OA (k)", 0.1, 2.0, 0.5)
alpha2 = st.sidebar.slider("Sensibilidad DA a Saldos Reales (\u03B12)", 0.1, 2.0, 1.0)
alpha1 = st.sidebar.slider("Sensibilidad DA a Política Fiscal (\u03B11)", 0.1, 2.0, 0.5)

st.sidebar.header("4. Visualización DA-OA")
periodos_totales = 30
# Este slider es la clave: permite ver la foto exacta de las curvas en un período t
t_ver = st.sidebar.slider("Ver curvas en el período (t):", 0, periodos_totales-1, 1)

# --- MOTOR DE SIMULACIÓN ---
def simular():
    y_hist = [y_p]
    pi_hist = [m_hat_0]
    pie_hist = [m_hat_0]
    
    # En el largo plazo, el producto vuelve a yp.
    # Si yp = yp + alpha1*delta_f + alpha2*(m_hat_1 - pi_ss), entonces:
    pi_ss = m_hat_1 + (alpha1 * delta_f) / alpha2

    for t in range(1, periodos_totales):
        if tipo_exp == "Racionales":
            # Salto directo al nuevo equilibrio estacionario previsto
            pie_t = pi_ss
            y_t = y_p
            pi_t = pi_ss
        else:
            # Adaptativas: la OA de este período usa la inflación pasada
            pie_t = pi_hist[-1]
            y_prev = y_hist[-1]
            
            # Equilibrio de corto plazo (cruce simultáneo DA_t y OA_t)
            # DA: y_t = y_prev + alpha1*delta_f + alpha2*(m_hat_1 - pi_t)
            # OA: pi_t = pie_t + k*(y_t - y_p)
            num_y = y_prev + alpha1 * delta_f + alpha2 * m_hat_1 - alpha2 * pie_t + alpha2 * k * y_p
            den_y = 1 + alpha2 * k
            y_t = num_y / den_y
            pi_t = pie_t + k * (y_t - y_p)
            
        y_hist.append(y_t)
        pi_hist.append(pi_t)
        pie_hist.append(pie_t)
        
    return np.array(y_hist), np.array(pi_hist), np.array(pie_hist), pi_ss

y_v, pi_v, pie_v, pi_estacionaria = simular()

# --- GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Plano DA-OA en t = {t_ver}")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    y_rango = np.linspace(y_p - 15, y_p + 15, 100)
    
    # Curvas Base (Referencia t=0) en gris claro
    da_0 = m_hat_0 + (y_p - y_rango) / alpha2
    oa_0 = m_hat_0 + k * (y_rango - y_p)
    ax1.plot(y_rango, da_0, color='lightgray', linestyle='--', label='DA inicial (t=0)')
    ax1.plot(y_rango, oa_0, color='lightgray', linestyle='--', label='OA inicial (t=0)')
    
    if t_ver > 0:
        # Curvas en el período seleccionado (t_ver)
        y_prev = y_v[t_ver - 1]
        pie_actual = pie_v[t_ver]
        
        # Ecuación gráfica de la DA en t_ver
        da_t = m_hat_1 + (alpha1 * delta_f + y_prev - y_rango) / alpha2
        # Ecuación gráfica de la OA en t_ver
        oa_t = pie_actual + k * (y_rango - y_p)
        
        ax1.plot(y_rango, da_t, color='blue', linewidth=2.5, label=f'DA (t={t_ver})')
        ax1.plot(y_rango, oa_t, color='red', linewidth=2.5, label=f'OA (t={t_ver})')
        
        # Punto de equilibrio en t_ver
        ax1.scatter(y_v[t_ver], pi_v[t_ver], color='black', s=80, zorder=5)
        ax1.annotate(f"E_{t_ver}", (y_v[t_ver], pi_v[t_ver]), xytext=(5, 5), textcoords='offset points')
    else:
        ax1.scatter(y_p, m_hat_0, color='black', s=80, zorder=5)
        ax1.annotate("E_0", (y_p, m_hat_0), xytext=(5, 5), textcoords='offset points')

    # OALP y Nuevo Estado Estacionario
    ax1.axvline(y_p, color='black', linewidth=1.5, label='OALP (Potencial)')
    ax1.axhline(pi_estacionaria, color='green', linestyle=':', label='Inflación LP ($\pi_{ss}$)')
    
    # Marcador de destino final
    ax1.scatter(y_p, pi_estacionaria, color='green', marker='*', s=150, zorder=6, label='Equilibrio Final')

    # Ajuste dinámico de ejes para que no salten al animar
    margen_pi = max(abs(pi_estacionaria - m_hat_0) * 1.5, 0.1)
    ax1.set_ylim(min(m_hat_0, pi_estacionaria) - margen_pi, max(m_hat_0, pi_estacionaria) + margen_pi)
    
    ax1.set_xlabel("Producto Real (y)")
    ax1.set_ylabel("Inflación ($\pi$)")
    ax1.legend(loc='lower right', fontsize='small')
    ax1.grid(True, linestyle=':', alpha=0.6)
    st.pyplot(fig1)

with col2:
    st.subheader("Trayectoria a Largo Plazo")
    fig2, (ax2_y, ax2_pi) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    
    # Gráfico de Producto
    ax2_y.plot(y_v, marker='.', color='royalblue', label='Producto (y)')
    ax2_y.axhline(y_p, color='black', linestyle='--', label='y_p (Estado Estacionario)')
    ax2_y.axvline(t_ver, color='gray', linestyle=':', alpha=0.5) # Marca el t actual
    ax2_y.set_ylabel("Producto")
    ax2_y.legend()
    ax2_y.grid(True, alpha=0.3)
    
    # Gráfico de Inflación
    ax2_pi.plot(pi_v, marker='.', color='firebrick', label='Inflación Real ($\pi$)')
    ax2_pi.plot(pie_v, linestyle='--', color='darkorange', linewidth=2, label='Expectativas ($\pi^e$)')
    ax2_pi.axhline(pi_estacionaria, color='green', linestyle=':', label='$\pi_{ss}$ (Largo Plazo)')
    ax2_pi.axvline(t_ver, color='gray', linestyle=':', alpha=0.5) # Marca el t actual
    ax2_pi.set_ylabel("Inflación")
    ax2_pi.set_xlabel("Períodos (t)")
    ax2_pi.legend()
    ax2_pi.grid(True, alpha=0.3)
    
    st.pyplot(fig2)

# Mensaje dinámico según expectativas
if tipo_exp == "Adaptativas":
    st.info("💡 **Tip de visualización:** Mueve el slider de 'Ver curvas en el período (t)'. Notarás que al pasar de t=0 a t=1, **solo se desplaza la DA**. La OA se queda 'quieta' en su posición inicial, lo que genera el aumento temporal de producto. Recién a partir de t=2 la OA comienza a subir para perseguir a la inflación.")
else:
    st.success("💡 **Tip de visualización:** Bajo expectativas racionales, el ajuste es instantáneo. En t=1, la DA salta por la política, y simultáneamente la OA salta porque los agentes ajustaron sus expectativas instantáneamente. El producto jamás se desvía de $y_p$.")
