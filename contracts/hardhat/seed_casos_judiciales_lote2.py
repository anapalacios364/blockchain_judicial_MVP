#!/usr/bin/env python3
"""
seed_casos_judiciales_lote2.py
==============================
Segundo lote de 50 expedientes judiciales de prueba – casos completamente
distintos al lote 1, orientados a probar la segunda testnet
(Celo Alfajores / Ethereum Sepolia según configuración activa en Ajustes).

Uso:
    python seed_casos_judiciales_lote2.py \
        --url http://localhost:8069 \
        --db nombre_base \
        --user admin \
        --password admin

Requiere: xmlrpc (stdlib de Python — sin dependencias externas)
"""

import argparse
import base64
import hashlib
import xmlrpc.client
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN POR DEFECTO
# ---------------------------------------------------------------------------
DEFAULT_URL      = "http://localhost:8069"
DEFAULT_DB       = "anacr"
DEFAULT_USER     = "admin"
DEFAULT_PASSWORD = "admin"

# ---------------------------------------------------------------------------
# 50 EXPEDIENTES – LOTE 2  (distintos al lote 1 en tipo, actor y hechos)
# ---------------------------------------------------------------------------
CASOS = [
    # ── Delitos Económicos y Financieros ────────────────────────────────────
    {
        "title": "Defraudación en licitación pública hospitalaria",
        "description": "Consorcio presenta documentación falsa para ganar contrato de equipamiento médico por $4.2M en el Hospital del IESS Guayaquil.",
        "state": "in_process",
        "parte_procesal": "Instituto Ecuatoriano de Seguridad Social IESS",
        "responsable_email": "fiscal1b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Pliegos de licitación originales", "evidence"), ("Documentación falsa presentada", "evidence"), ("Informe de auditoría SERCOP", "evidence")],
    },
    {
        "title": "Desfalco en empresa pública de agua potable",
        "description": "Gerente de EMAPAG desvía $780.000 de fondos de mantenimiento a cuentas personales durante 18 meses.",
        "state": "in_process",
        "parte_procesal": "EMAPAG EP – Empresa de Agua Potable Guayaquil",
        "responsable_email": "fiscal2b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Auditoría interna EMAPAG", "evidence"), ("Transferencias bancarias", "evidence"), ("Resolución de auditoría CGE", "resolution")],
    },
    {
        "title": "Especulación financiera con fondos de pensiones",
        "description": "Administradora de fondos invierte recursos previsionales en instrumentos de alto riesgo no autorizados generando pérdida de $12M.",
        "state": "in_process",
        "parte_procesal": "Superintendencia de Bancos SB",
        "responsable_email": "fiscal3b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe SB de inversiones", "evidence"), ("Portafolio de instrumentos", "evidence")],
    },
    # ── Delitos contra la Salud Pública ─────────────────────────────────────
    {
        "title": "Comercialización de medicamentos adulterados",
        "description": "Red distribuidora vende insulina falsificada en cadenas de farmacias. Tres pacientes hospitalizados.",
        "state": "in_process",
        "parte_procesal": "ARCSA – Agencia de Regulación y Control Sanitario",
        "responsable_email": "fiscal4b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Análisis químico ARCSA", "evidence"), ("Acta de decomiso farmacias", "evidence"), ("Informe médico afectados", "evidence")],
    },
    {
        "title": "Ejercicio ilegal de la medicina sin título habilitante",
        "description": "Persona realiza procedimientos quirúrgicos estéticos sin formación médica en clínica clandestina.",
        "state": "in_process",
        "parte_procesal": "Ministerio de Salud Pública MSP",
        "responsable_email": "fiscal5b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de clausura del local", "evidence"), ("Declaraciones de pacientes", "evidence"), ("Informe médico forense de víctimas", "evidence")],
    },
    {
        "title": "Tráfico de órganos – red hospitalaria clandestina",
        "description": "Organización capta donantes vulnerables para extracción y venta de riñones en el extranjero.",
        "state": "in_process",
        "parte_procesal": "Fiscalía Especializada Delitos Graves",
        "responsable_email": "fiscal6b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe Interpol red de órganos", "evidence"), ("Registros médicos comprometidos", "evidence"), ("Declaraciones de víctimas", "evidence")],
    },
    # ── Delitos Informáticos Avanzados ──────────────────────────────────────
    {
        "title": "Ataque DDoS a infraestructura del Banco Central del Ecuador",
        "description": "Ciberataque coordinado inhabilita sistemas de pagos interbancarios por 6 horas.",
        "state": "in_process",
        "parte_procesal": "Banco Central del Ecuador BCE",
        "responsable_email": "perito1b@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe técnico de respuesta al incidente", "evidence"), ("Logs de tráfico anómalo", "evidence"), ("Evaluación de impacto económico", "evidence")],
    },
    {
        "title": "Clonación masiva de tarjetas de crédito – skimming en cajeros",
        "description": "Dispositivos capturadores instalados en 23 cajeros automáticos de Guayaquil y Quito.",
        "state": "in_process",
        "parte_procesal": "Asociación de Bancos Privados ASOBANCA",
        "responsable_email": "perito2b@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Dispositivos skimmer decomisados", "evidence"), ("Registro de transacciones fraudulentas", "evidence"), ("Informe forense digital", "evidence")],
    },
    {
        "title": "Deepfake de funcionario público para fraude electoral",
        "description": "Vídeo manipulado con IA difunde declaraciones falsas del Presidente del CNE días antes de elecciones.",
        "state": "in_process",
        "parte_procesal": "Consejo Nacional Electoral CNE",
        "responsable_email": "perito3b@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Vídeo original vs. deepfake", "evidence"), ("Análisis forense de metadatos", "evidence"), ("Informe de perito en IA forense", "evidence")],
    },
    {
        "title": "Espionaje corporativo mediante software espía",
        "description": "Ex empleado instala keylogger en servidores de empresa farmacéutica para robar fórmulas patentadas.",
        "state": "in_process",
        "parte_procesal": "Laboratorios Pharma Ecuador S.A.",
        "responsable_email": "perito4b@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe forense del servidor", "evidence"), ("Registro de accesos sospechosos", "evidence"), ("Denuncia empresa afectada", "filing")],
    },
    # ── Delitos contra el Orden Público ─────────────────────────────────────
    {
        "title": "Motín carcelario con toma de rehenes – Penitenciaría del Litoral",
        "description": "Banda interna toma control de pabellón y retiene 8 guías penitenciarios durante 14 horas.",
        "state": "closed",
        "parte_procesal": "Servicio Nacional de Atención Integral SNAI",
        "responsable_email": "fiscal7b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe SNAI del incidente", "evidence"), ("Declaraciones de rehenes liberados", "evidence"), ("Sentencia de resolución", "resolution")],
    },
    {
        "title": "Asociación ilícita – pandilla juvenil sector suburbano",
        "description": "Organización de 15 menores y 4 mayores de edad comete extorsiones sistemáticas a comerciantes.",
        "state": "in_process",
        "parte_procesal": "Fiscalía de Adolescentes Infractores",
        "responsable_email": "fiscal8b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe policial de operativo", "evidence"), ("Actas de decomiso de armas", "evidence"), ("Testimonio de comerciantes", "evidence")],
    },
    # ── Delitos de Tránsito Graves ───────────────────────────────────────────
    {
        "title": "Carrera ilegal de vehículos con víctima fatal",
        "description": "Dos vehículos disputando velocidad atropellan a ciclista en malecón a las 03h00.",
        "state": "in_process",
        "parte_procesal": "Municipio de Guayaquil – ANT",
        "responsable_email": "juez1b@funcionjudicial.gob.ec",
        "tipo": "Tránsito",
        "docs": [("Video carrera ANT", "evidence"), ("Autopsia forense", "evidence"), ("Parte de tránsito", "evidence")],
    },
    {
        "title": "Fuga de conductor responsable de accidente múltiple",
        "description": "Vehículo pesado impacta cuatro autos en intersección y conductor huye. Identificado 48h después.",
        "state": "in_process",
        "parte_procesal": "Transporte Pesado Interandino S.A.",
        "responsable_email": "juez2b@funcionjudicial.gob.ec",
        "tipo": "Tránsito",
        "docs": [("Croquis vial ANT", "evidence"), ("Identificación vehicular RTV", "evidence"), ("Informes médicos de lesionados", "evidence")],
    },
    # ── Casos de Familia y Niñez ─────────────────────────────────────────────
    {
        "title": "Privación de patria potestad por negligencia grave",
        "description": "Menores encontrados en situación de desnutrición severa y sin escolarización por 3 años.",
        "state": "in_process",
        "parte_procesal": "Junta Cantonal de Protección de Derechos",
        "responsable_email": "juez3b@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Informe nutricional médico", "evidence"), ("Informe psicosocial MIES", "evidence"), ("Demanda de privación de patria potestad", "filing")],
    },
    {
        "title": "Pensión alimenticia incumplida por más de 24 meses",
        "description": "Progenitor adeuda $14.400 en pensiones alimenticias. Solicitud de apremio personal.",
        "state": "in_process",
        "parte_procesal": "Karina Alejandra Vélez Montoya",
        "responsable_email": "juez4b@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Liquidación de pensiones adeudadas", "evidence"), ("Auto de apremio", "resolution")],
    },
    {
        "title": "Adopción internacional – impugnación por irregularidades",
        "description": "ONG intermediaria actuó sin habilitación del MIES en proceso de adopción de dos hermanos.",
        "state": "in_process",
        "parte_procesal": "MIES Unidad de Adopciones",
        "responsable_email": "juez5b@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Expediente de adopción cuestionado", "evidence"), ("Informe MIES de irregularidades", "evidence"), ("Acción de impugnación", "filing")],
    },
    # ── Casos Civiles Complejos ──────────────────────────────────────────────
    {
        "title": "Responsabilidad civil por colapso de edificio",
        "description": "Estructura de 8 pisos colapsa por vicios de construcción. 12 familias afectadas demandan al constructor.",
        "state": "in_process",
        "parte_procesal": "Copropietarios Edificio Torre Mar",
        "responsable_email": "juez6b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Informe pericial estructural", "evidence"), ("Planos aprobados por municipio", "evidence"), ("Demanda colectiva", "filing"), ("Auto de calificación", "resolution")],
    },
    {
        "title": "Nulidad de contrato de compraventa por error esencial",
        "description": "Comprador adquirió terreno creyendo tener acceso a agua potable municipal que no existe.",
        "state": "draft",
        "parte_procesal": "Hernán Rodrigo Cevallos Freire",
        "responsable_email": "juez7b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Contrato de compraventa", "evidence"), ("Informe EMAPAG de conexión", "evidence"), ("Demanda de nulidad", "filing")],
    },
    {
        "title": "Reivindicación de marca comercial registrada",
        "description": "Empresa usa marca idéntica a la de competidor registrado en el SENADI cinco años antes.",
        "state": "in_process",
        "parte_procesal": "Industrias Alimenticias Pronaca S.A.",
        "responsable_email": "juez8b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Certificado de registro SENADI", "evidence"), ("Muestras de productos confundibles", "evidence"), ("Demanda de reivindicación de marca", "filing")],
    },
    {
        "title": "Resolución de fideicomiso por incumplimiento del fiduciario",
        "description": "Fiduciaria no ejecutó instrucciones de inversión causando pérdida del 40% del patrimonio fideicometido.",
        "state": "in_process",
        "parte_procesal": "Fideicomiso Inmobiliario Costa Verde",
        "responsable_email": "juez9b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Contrato de fideicomiso", "evidence"), ("Informe de gestión fiduciaria", "evidence"), ("Dictamen actuarial de pérdidas", "evidence")],
    },
    # ── Delitos Laborales Complejos ──────────────────────────────────────────
    {
        "title": "Trabajo infantil en plantación bananera",
        "description": "Inspección del Ministerio de Trabajo detecta 11 menores entre 10 y 15 años trabajando en labores agrícolas.",
        "state": "in_process",
        "parte_procesal": "Ministerio de Trabajo MDT",
        "responsable_email": "juez10b@funcionjudicial.gob.ec",
        "tipo": "Laboral",
        "docs": [("Acta de infracción MDT", "evidence"), ("Informe de inspección", "evidence"), ("Registro de menores identificados", "evidence")],
    },
    {
        "title": "Simulación de relación laboral con tercerización ilegal",
        "description": "Empresa usa plataforma de outsourcing para evadir beneficios sociales de 200 trabajadores durante 4 años.",
        "state": "in_process",
        "parte_procesal": "Comité de Empresa Trabajadores Unidos",
        "responsable_email": "juez11b@funcionjudicial.gob.ec",
        "tipo": "Laboral",
        "docs": [("Contratos de prestación de servicios", "evidence"), ("Informe de auditoría laboral", "evidence"), ("Demanda colectiva laboral", "filing")],
    },
    # ── Delitos contra el Patrimonio del Estado ─────────────────────────────
    {
        "title": "Sobreprecio en importación de equipos militares",
        "description": "Ministerio de Defensa adquiere radares a precio triplicado mediante intermediario con conflicto de interés.",
        "state": "in_process",
        "parte_procesal": "Contraloría General del Estado",
        "responsable_email": "fiscal9b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe técnico de valoración CGE", "evidence"), ("Contratos de adquisición", "evidence"), ("Resolución de responsabilidad", "resolution")],
    },
    {
        "title": "Concesión irregular de frecuencias de radio",
        "description": "Funcionarios de ARCOTEL otorgan frecuencias AM y FM a empresas vinculadas sin proceso de selección.",
        "state": "in_process",
        "parte_procesal": "ARCOTEL – Agencia de Regulación",
        "responsable_email": "fiscal10b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Resoluciones de concesión cuestionadas", "evidence"), ("Informe auditoría ARCOTEL", "evidence")],
    },
    # ── Delitos contra la Naturaleza ─────────────────────────────────────────
    {
        "title": "Pesca ilegal de tiburón en aguas de Galápagos",
        "description": "Embarcación extranjera captura 357 tiburones de especie protegida dentro de la Reserva Marina.",
        "state": "in_process",
        "parte_procesal": "Parque Nacional Galápagos PNG",
        "responsable_email": "fiscal11b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de intercepción Armada Nacional", "evidence"), ("Registro de captura ilegal", "evidence"), ("Informe técnico PNG", "evidence")],
    },
    {
        "title": "Deforestación ilegal en zona de protección hídrica",
        "description": "Empresa maderera tala 450 hectáreas de bosque primario en zona buffer del Parque Cotacachi-Cayapas.",
        "state": "in_process",
        "parte_procesal": "MAE – Ministerio del Ambiente",
        "responsable_email": "fiscal12b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Imágenes satelitales de deforestación", "evidence"), ("Informe técnico forestal", "evidence"), ("Acta de allanamiento operativo MAE", "evidence")],
    },
    {
        "title": "Minería ilegal con mercurio en zona amazónica",
        "description": "Operación clandestina contamina afluente del río Napo afectando comunidades indígenas aguas abajo.",
        "state": "in_process",
        "parte_procesal": "Nacionalidad Waorani del Ecuador",
        "responsable_email": "fiscal13b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Análisis de contaminación por mercurio", "evidence"), ("Informe Arcom", "evidence"), ("Declaración comunidades afectadas", "filing")],
    },
    # ── Casos de Violencia de Género ─────────────────────────────────────────
    {
        "title": "Acoso sexual en entorno universitario por docente",
        "description": "Tres estudiantes denuncian conductas de acoso continuado por parte de profesor titular.",
        "state": "in_process",
        "parte_procesal": "Universidad Estatal de Guayaquil",
        "responsable_email": "fiscal14b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Declaraciones de las tres denunciantes", "evidence"), ("Mensajes de texto comprometedores", "evidence"), ("Informe comisión universitaria", "evidence")],
    },
    {
        "title": "Stalking digital y amenazas a través de redes sociales",
        "description": "Víctima recibe 800 mensajes amenazantes en 30 días desde perfiles falsos con datos personales filtrados.",
        "state": "in_process",
        "parte_procesal": "Valeria Monserrate Chávez Intriago",
        "responsable_email": "fiscal15b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Capturas de mensajes amenazantes", "evidence"), ("Informe pericial de trazabilidad digital", "evidence"), ("Denuncia formal", "filing")],
    },
    # ── Casos de Crimen Organizado ───────────────────────────────────────────
    {
        "title": "Desarticulación de célula terrorista con nexos internacionales",
        "description": "Operativo binacional Ecuador-Colombia desmantela grupo que planificaba atentado a oleoducto.",
        "state": "in_process",
        "parte_procesal": "Ministerio del Interior – Policía Antiterrorista",
        "responsable_email": "fiscal16b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe Inteligencia Policial", "evidence"), ("Material incautado – explosivos", "evidence"), ("Comunicaciones intervenidas", "evidence"), ("Informe colaboración Interpol", "evidence")],
    },
    {
        "title": "Sicariato por encargo – víctima empresario bananero",
        "description": "Empresario asesinado por sicario contratado por competidor. Cadena de contratación rastreada.",
        "state": "in_process",
        "parte_procesal": "Marisol Esperanza Delgado Vera",
        "responsable_email": "fiscal17b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe balístico", "evidence"), ("Registros de transferencias al sicario", "evidence"), ("Testimonios de testigos protegidos", "evidence")],
    },
    # ── Delitos de Corrupción Judicial ───────────────────────────────────────
    {
        "title": "Prevaricato – juez dicta sentencia a cambio de dádivas",
        "description": "Juez de garantías penales resuelve sobreseimiento a cambio de $30.000 en efectivo.",
        "state": "in_process",
        "parte_procesal": "Consejo de la Judicatura CJ",
        "responsable_email": "fiscal18b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Grabaciones de entrega de dinero", "evidence"), ("Resolución judicial cuestionada", "evidence"), ("Informe Consejo Judicatura", "evidence")],
    },
    {
        "title": "Tráfico de influencias en nombramiento de funcionarios",
        "description": "Alto funcionario acepta pago para garantizar nombramiento de personas en cargos públicos.",
        "state": "in_process",
        "parte_procesal": "Secretaría Nacional de la Administración Pública SNAP",
        "responsable_email": "fiscal19b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Comunicaciones comprometedoras", "evidence"), ("Registro de pagos", "evidence"), ("Nombramiento irregular", "evidence")],
    },
    # ── Delitos contra los Derechos de Autor ────────────────────────────────
    {
        "title": "Plagio académico de tesis doctoral publicada",
        "description": "Funcionario público presenta como propia tesis de posgrado copiada en un 78% sin citar fuentes.",
        "state": "draft",
        "parte_procesal": "SENESCYT – Secretaría de Educación Superior",
        "responsable_email": "juez12b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Informe de similitud Turnitin", "evidence"), ("Tesis original y copia", "evidence"), ("Denuncia autor original", "filing")],
    },
    {
        "title": "Reproducción masiva no autorizada de obra musical ecuatoriana",
        "description": "Plataforma digital cobra suscripciones usando catálogo de artistas nacionales sin contratos ni regalías.",
        "state": "in_process",
        "parte_procesal": "SAYCE – Sociedad de Autores del Ecuador",
        "responsable_email": "juez13b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Catálogo de obras vulneradas", "evidence"), ("Demanda SAYCE", "filing"), ("Auto de medida cautelar", "resolution")],
    },
    # ── Casos de Derecho Administrativo ─────────────────────────────────────
    {
        "title": "Impugnación de acto administrativo – suspensión de permiso de operación",
        "description": "Aerolínea nacional impugna suspensión de rutas decretada sin audiencia previa por DGAC.",
        "state": "in_process",
        "parte_procesal": "Aerolíneas del Ecuador ADE S.A.",
        "responsable_email": "juez14b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Resolución DGAC impugnada", "evidence"), ("Recurso de apelación administrativo", "filing"), ("Informe técnico DGAC", "evidence")],
    },
    {
        "title": "Acción de incumplimiento de sentencia constitucional",
        "description": "Municipio no ejecuta obras de reparación de vía ordenadas por Corte Constitucional hace 18 meses.",
        "state": "in_process",
        "parte_procesal": "Barrio Los Olivos – Representante Comunitario",
        "responsable_email": "juez15b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Sentencia Corte Constitucional", "evidence"), ("Informe de incumplimiento", "evidence"), ("Acción de incumplimiento", "filing")],
    },
    # ── Delitos de Explotación Laboral ───────────────────────────────────────
    {
        "title": "Trata de personas con fines de explotación laboral doméstica",
        "description": "Familia retiene a dos adolescentes indígenas como trabajadoras domésticas sin sueldo ni libertad de movimiento.",
        "state": "in_process",
        "parte_procesal": "OIT – Organización Internacional del Trabajo",
        "responsable_email": "fiscal20b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de rescate policial", "evidence"), ("Declaraciones de víctimas", "evidence"), ("Informe psicosocial", "evidence")],
    },
    # ── Casos de Crímenes contra Periodistas ─────────────────────────────────
    {
        "title": "Amenaza de muerte a periodista de investigación",
        "description": "Reportero recibe amenazas tras publicar investigación sobre contrabando en zona fronteriza.",
        "state": "in_process",
        "parte_procesal": "Fundación PERIODISTAS EN RIESGO Ecuador",
        "responsable_email": "fiscal21b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Mensajes amenazantes originales", "evidence"), ("Informe de análisis de amenazas", "evidence"), ("Denuncia Unión Nacional de Periodistas UNP", "filing")],
    },
    # ── Casos de Seguros ─────────────────────────────────────────────────────
    {
        "title": "Fraude a aseguradora mediante accidente vehicular simulado",
        "description": "Red orquesta colisiones falsas para cobrar seguros de vehículos. 14 reclamos fraudulentos identificados.",
        "state": "in_process",
        "parte_procesal": "Seguros Sucre S.A.",
        "responsable_email": "fiscal22b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe investigación siniestros", "evidence"), ("Videos de accidentes simulados", "evidence"), ("Reclamos fraudulentos documentados", "evidence")],
    },
    {
        "title": "Cobro de seguro de vida mediante muerte simulada",
        "description": "Beneficiario presenta certificado de defunción falso para cobrar póliza de $200.000.",
        "state": "closed",
        "parte_procesal": "Equivida Compañía de Seguros",
        "responsable_email": "fiscal23b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Certificado de defunción falso", "evidence"), ("Informe Registro Civil", "evidence"), ("Sentencia condenatoria", "resolution")],
    },
    # ── Casos de Migración y Refugio ─────────────────────────────────────────
    {
        "title": "Negativa ilegal de refugio a solicitante venezolano",
        "description": "Autoridad migratoria rechaza solicitud sin evaluación de riesgo real en violación de Convención de Ginebra.",
        "state": "in_process",
        "parte_procesal": "ACNUR – Alto Comisionado ONU para Refugiados",
        "responsable_email": "juez16b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Solicitud de refugio presentada", "evidence"), ("Resolución denegatoria", "evidence"), ("Recurso de apelación", "filing")],
    },
    # ── Casos de Telecomunicaciones ──────────────────────────────────────────
    {
        "title": "Interceptación ilegal de comunicaciones de opositor político",
        "description": "Operativo de vigilancia sin orden judicial monitorea llamadas y correos de candidato presidencial.",
        "state": "in_process",
        "parte_procesal": "Defensoría del Pueblo del Ecuador",
        "responsable_email": "fiscal24b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe técnico de interceptación", "evidence"), ("Logs de acceso sistemas", "evidence"), ("Denuncia ante la Defensoría", "filing")],
    },
    # ── Casos de Responsabilidad Médica ─────────────────────────────────────
    {
        "title": "Negligencia médica – error quirúrgico con daño permanente",
        "description": "Cirujano opera extremidad equivocada causando amputación innecesaria. Demanda por $800.000.",
        "state": "in_process",
        "parte_procesal": "Clínica Kennedy S.A.",
        "responsable_email": "juez17b@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Historia clínica original", "evidence"), ("Informe Tribunal de Honor Médico", "evidence"), ("Pericia médica independiente", "evidence"), ("Demanda civil de daños", "filing")],
    },
    {
        "title": "Muerte por error en dispensación de medicamento hospitalario",
        "description": "Enfermera administra dosis diez veces superior a la prescrita. Paciente fallece 48h después.",
        "state": "in_process",
        "parte_procesal": "Herederos de Carmen Luisa Pinto Aguilar",
        "responsable_email": "fiscal25b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Historia clínica y prescripción", "evidence"), ("Informe Comité de Seguridad del Paciente", "evidence"), ("Autopsia médico-legal", "evidence")],
    },
    # ── Casos de Construcción y Urbanismo ───────────────────────────────────
    {
        "title": "Construcción en zona de riesgo sin permiso municipal",
        "description": "Urbanizadora construye 80 viviendas en ladera inestable sin estudio geotécnico ni permiso.",
        "state": "in_process",
        "parte_procesal": "GAD Municipal Guayaquil – Dirección de Urbanismo",
        "responsable_email": "fiscal26b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe geotécnico de riesgo", "evidence"), ("Acta de infracción urbanística", "evidence"), ("Resolución de demolición", "resolution")],
    },
    # ── Casos de Delitos Aduaneros ───────────────────────────────────────────
    {
        "title": "Subfacturación de importación de maquinaria industrial",
        "description": "Empresa declara valor inferior al real en 35 importaciones para evadir $1.8M en aranceles.",
        "state": "in_process",
        "parte_procesal": "SENAE – Dirección Antifraude",
        "responsable_email": "fiscal27b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Facturas comerciales reales vs. declaradas", "evidence"), ("Informe técnico de valoración aduanera", "evidence"), ("Actas de aprehensión", "evidence")],
    },
    # ── Casos de Catástrofe y Responsabilidad Civil ──────────────────────────
    {
        "title": "Explosión en planta industrial por negligencia de seguridad",
        "description": "Deficiencia en mantenimiento de calderas causa explosión con 3 muertos y 15 heridos.",
        "state": "in_process",
        "parte_procesal": "Industria Acero del Pacífico S.A.",
        "responsable_email": "fiscal28b@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe IESS de accidente laboral", "evidence"), ("Pericia técnica ingeniería industrial", "evidence"), ("Informes médicos de víctimas", "evidence"), ("Demanda de herederos", "filing")],
    },
    # ── Caso de Prueba Testnet 2 ─────────────────────────────────────────────
    {
        "title": "Caso prueba lote 2 – Anclaje comparativo Celo Alfajores",
        "description": "Expediente generado para pruebas comparativas de latencia y costo de gas entre Ethereum Sepolia y Celo Alfajores. Lote 2.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto Lote 2",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Evidencia prueba Celo lote 2 – doc A", "evidence"), ("Evidencia prueba Celo lote 2 – doc B", "evidence"), ("Evidencia prueba Celo lote 2 – doc C", "evidence")],
    },
    {
        "title": "Caso prueba lote 2 – Medición TPS Ethereum Sepolia",
        "description": "Expediente para medir throughput (TPS) y tiempo de confirmación on-chain en Ethereum Sepolia. Lote 2.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto Lote 2",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Evidencia prueba Sepolia lote 2 – doc A", "evidence"), ("Evidencia prueba Sepolia lote 2 – doc B", "evidence")],
    },
    {
        "title": "Caso prueba lote 2 – Verificación integridad hash SHA-256 cross-network",
        "description": "Anclaje simultáneo en ambas redes para comparar coherencia del hash SHA-256 almacenado on-chain.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto Lote 2",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Documento cross-network A", "evidence"), ("Documento cross-network B", "evidence"), ("Acta de verificación cruzada", "other")],
    },
]

# ---------------------------------------------------------------------------
# CONTENIDO SIMULADO
# ---------------------------------------------------------------------------
def _fake_pdf_content(nombre: str, caso: str) -> bytes:
    contenido = (
        f"DOCUMENTO JUDICIAL SIMULADO – LOTE 2\n"
        f"Expediente: {caso}\n"
        f"Documento: {nombre}\n"
        f"Generado: {datetime.now().isoformat()}\n"
        f"Red objetivo: Segunda testnet configurada en Ajustes Odoo\n"
        f"Hash de integridad calculado por el sistema al anclar.\n"
    )
    return contenido.encode("utf-8")


# ---------------------------------------------------------------------------
# HELPERS XML-RPC
# ---------------------------------------------------------------------------
def connect(url, db, user, password):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, password, {})
    if not uid:
        raise SystemExit(f"[ERROR] Autenticación fallida: {user}@{db}")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    print(f"[OK] Conectado a {url} — uid={uid}")
    return uid, models


def search_or_create_partner(models, db, uid, password, name):
    ids = models.execute_kw(db, uid, password, "res.partner", "search",
                            [[["name", "=", name]]], {"limit": 1})
    if ids:
        return ids[0]
    return models.execute_kw(db, uid, password, "res.partner", "create",
                             [{"name": name, "is_company": False,
                               "comment": "Parte procesal – lote 2 de pruebas"}])


def search_or_create_user(models, db, uid, password, email):
    ids = models.execute_kw(db, uid, password, "res.users", "search",
                            [[["login", "=", email]]], {"limit": 1})
    return ids[0] if ids else uid


# ---------------------------------------------------------------------------
# CREACIÓN
# ---------------------------------------------------------------------------
def create_cases(url, db, user, password):
    uid, models_proxy = connect(url, db, user, password)
    created, errors = [], []

    for i, caso in enumerate(CASOS, 1):
        try:
            partner_id     = search_or_create_partner(models_proxy, db, uid, password, caso["parte_procesal"])
            responsable_id = search_or_create_user(models_proxy, db, uid, password, caso["responsable_email"])

            case_id = models_proxy.execute_kw(
                db, uid, password, "judicial.case", "create",
                [{
                    "title":            caso["title"],
                    "description":      caso["description"],
                    "state":            caso["state"],
                    "partner_id":       partner_id,
                    "assigned_user_id": responsable_id,
                }]
            )

            doc_ids = []
            for doc_nombre, doc_tipo in caso["docs"]:
                contenido_bytes = _fake_pdf_content(doc_nombre, caso["title"])
                b64       = base64.b64encode(contenido_bytes).decode("utf-8")
                sha_local = hashlib.sha256(contenido_bytes).hexdigest()

                doc_id = models_proxy.execute_kw(
                    db, uid, password, "judicial.document", "create",
                    [{
                        "name":                 doc_nombre,
                        "case_id":              case_id,
                        "document_type":        doc_tipo,
                        "attachment":           b64,
                        "filename":             f"{doc_nombre.replace(' ', '_').lower()[:60]}.txt",
                        "notes":                f"Lote 2 – SHA-256 local: {sha_local}",
                        "is_official_evidence": doc_tipo == "evidence",
                    }]
                )
                doc_ids.append(doc_id)

            if doc_ids:
                models_proxy.execute_kw(
                    db, uid, password, "judicial.case", "write",
                    [[case_id], {"active_document_id": doc_ids[0]}]
                )

            created.append((i, case_id, caso["title"]))
            print(f"  [{i:02d}/50] ✅  ID={case_id}  {caso['title'][:65]}")

        except Exception as e:
            errors.append((i, caso["title"], str(e)))
            print(f"  [{i:02d}/50] ❌  {caso['title'][:65]} → {e}")

    print("\n" + "=" * 70)
    print(f"  LOTE 2 – EXPEDIENTES CREADOS : {len(created)}")
    print(f"  LOTE 2 – ERRORES             : {len(errors)}")
    if errors:
        print("\n  Detalle de errores:")
        for idx, titulo, err in errors:
            print(f"    [{idx:02d}] {titulo[:55]} → {err}")
    print("=" * 70)
    print("\n  Lote 2 listo. Cambia la red en Ajustes > Blockchain antes de anclar.\n")


# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera 50 expedientes judiciales de prueba – Lote 2"
    )
    parser.add_argument("--url",      default=DEFAULT_URL)
    parser.add_argument("--db",       default=DEFAULT_DB)
    parser.add_argument("--user",     default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  SEED LOTE 2: Expedientes Judiciales – Segunda Testnet")
    print(f"  URL: {args.url}  DB: {args.db}  USER: {args.user}")
    print("=" * 70 + "\n")

    create_cases(args.url, args.db, args.user, args.password)
