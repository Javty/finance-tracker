# 💸 Finance Tracker App

Aplicación web personal para el seguimiento de ingresos, gastos, préstamos, transferencias y resúmenes por cartera, desarrollada con **Flask** y **SQLite**.

> 🚀 Proyecto 100% funcional, ideal para practicar Python, SQLAlchemy, HTML y automatización de pruebas E2E.

---

## 📸 Vista previa

*(Agrega capturas aquí si gustas más adelante)*

---

## ⚙️ Tecnologías

- Python 3.10+
- Flask
- SQLAlchemy
- HTML (Jinja2 Templates)
- Bootstrap (opcional)
- SQLite

---

## 📦 Instalación y ejecución local

1. **Clona el repositorio:**

```bash
git clone https://github.com/Javty/finance-tracker.git
cd finance-tracker
```

2. **Crea y activa el entorno virtual:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

4. **Inicia la aplicación:**

```bash
python app.py
```

Accede en tu navegador: [http://localhost:5000](http://localhost:5000)

---

## 🔁 Resetear la base de datos

Para reiniciar el sistema con una base vacía:

```bash
python reset_db.py
```

Esto eliminará `finance.db` y creará una nueva desde cero.

---

## 📌 Funcionalidades principales

- [x] Registro de ingresos y gastos por categoría y fecha
- [x] Soporte para múltiples **carteras** (efectivo, banco, crédito, digital)
- [x] Transferencias entre carteras
- [x] Registro y seguimiento de **deudas / préstamos**
- [x] Balance inicial y límite para tarjetas de crédito
- [x] Dashboard con resumen de ingresos, gastos, préstamos y saldo neto

---

## 🛠️ En desarrollo

- Exportar reportes en PDF/CSV
- Gráficas de comportamiento financiero
- Etiquetas y filtros por periodo
- Autenticación de usuario
- Pruebas automatizadas E2E

---

## 🧪 Pruebas

> 💡 Próximamente se integrarán pruebas automatizadas usando `pytest`, `Flask-Testing` o herramientas E2E como Playwright/Selenium.

---

## 📄 Licencia

Este proyecto es de uso personal y educativo. Puedes adaptarlo o expandirlo como quieras.

---

## 🙌 Autor

Desarrollado por **Javty** como parte de su proceso de aprendizaje y crecimiento como **SDET & Python Developer**.

---

¿Listo para automatizarlo? ✨ Te puedo ayudar a preparar las primeras pruebas E2E.
