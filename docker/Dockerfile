FROM odoo:19.0

USER root
COPY ../requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ../custom_addons /mnt/extra-addons

RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf
USER odoo
