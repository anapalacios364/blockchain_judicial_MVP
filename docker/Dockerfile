FROM odoo:19.0

USER root

# Instalar herramientas de compilación necesarias para lru-dict y otros paquetes C
# Se limpian caches de apt al final para no inflar la imagen innecesariamente
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python para blockchain
# El contexto del build es la raíz del proyecto (context: ..)
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages --ignore-installed -r /tmp/requirements.txt

# Copiar odoo.conf (el volumen en compose lo puede sobrescribir en runtime)
COPY docker/odoo.conf /etc/odoo/odoo.conf

# Copiar módulos custom a la carpeta estándar de addons extra
# El volumen en compose también puede sobrescribir esto en desarrollo
COPY custom_addons /mnt/extra-addons

RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

USER odoo