import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Generación de Datos (Simulando Consumo Eléctrico Municipal de Datos.gob.mx)
np.random.seed(42)
# Rango de tiempo para el análisis (Serie de tiempo)
meses = pd.date_range(start='2018-01-01', periods=60, freq='ME')
# Señal: Crecimiento anual de consumo + variabilidad estacional (verano/invierno)
consumo_base = np.linspace(1000, 1500, 60) + np.sin(np.linspace(0, 10, 60)) * 200
ruido = np.random.normal(0, 50, 60)
lecturas = consumo_base + ruido

# INYECCIÓN DE ANOMALÍAS (Errores de reporte o saltos en el dataset)
lecturas[25] = 2800  # Error de captura (Duplicación de valor)
lecturas[45:48] = np.nan  # Valores nulos (Falta de reporte mensual)

df = pd.DataFrame({'Mes': meses, 'Consumo_MWh': lecturas})
df.set_index('Mes', inplace=True)

# Llenado de nulos para poder graficar (Interpolación)
df['Consumo_Limpio'] = df['Consumo_MWh'].interpolate()

# 2. Inspección Temporal
plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Consumo_MWh'], 'ro', label='Datos Crudos (con errores)', alpha=0.5)
plt.plot(df.index, df['Consumo_Limpio'], label='Tendencia de Consumo', color='#1f77b4')
plt.title("Análisis de Consumo Eléctrico Municipal (Simulación Datos.gob.mx)")
plt.ylabel("Consumo (MWh)")
plt.grid(True, linestyle='--')
plt.legend()
plt.show()

# 3. Análisis de Distribución (Para detectar sesgos en el consumo)
plt.figure(figsize=(7, 4))
sns.boxplot(x=df['Consumo_Limpio'], color='lightgreen')
plt.title("Detección de Outliers en el Consumo")
plt.show()

# 4. Estadística Descriptiva
print("=== Perfil Estadístico del Consumo Energético ===")
print(df['Consumo_Limpio'].describe())