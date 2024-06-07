# Usar una imagen base oficial de Python
FROM python:3.11

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Crear un entorno virtual en el directorio /venv
RUN python -m venv /venv

# Activar el entorno virtual y actualizar pip
RUN /venv/bin/pip install --upgrade pip

# Copiar los requisitos y el archivo de configuración
COPY requirements.txt .

# Instalar las dependencias en el entorno virtual
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Exponer el puerto en el que la aplicación se ejecutará
EXPOSE 8082

# Establecer la variable de entorno para el PATH del entorno virtual
ENV PATH="/venv/bin:$PATH"

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
