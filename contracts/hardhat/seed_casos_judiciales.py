#!/usr/bin/env python3
"""
seed_casos_judiciales.py
========================
Script de datos de prueba para el sistema judicial Odoo 19.
Genera 50 expedientes judiciales listos para pruebas en testnet
(Ethereum Sepolia / Celo Alfajores / Hardhat local).

Uso:
    python seed_casos_judiciales.py \
        --url http://localhost:8069 \
        --db nombre_base \
        --user admin \
        --password admin

Requiere: pip install xmlrpc (ya incluido en Python stdlib)
"""

import argparse
import base64
import hashlib
import xmlrpc.client
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE CONEXIÓN (se sobreescribe con argumentos CLI)
# ---------------------------------------------------------------------------
DEFAULT_URL      = "http://localhost:8069"
DEFAULT_DB       = "anacr"
DEFAULT_USER     = "admin"
DEFAULT_PASSWORD = "admin"

# ---------------------------------------------------------------------------
# DATOS DE LOS 50 EXPEDIENTES
# Cada dict representa un caso con su parte procesal principal (partner) y
# sus documentos adjuntos (al menos uno por expediente).
# ---------------------------------------------------------------------------
CASOS = [
    # ── Casos de Homicidio / Femicidio ──────────────────────────────────────
    {
        "title": "Homicidio culposo en accidente de tránsito",
        "description": "Investigación por muerte de peatón en colisión vehicular en la Av. 9 de Octubre.",
        "state": "in_process",
        "parte_procesal": "Carlos Andrés Muñoz Vera",    # víctima / denunciante
        "responsable_email": "fiscal1@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe forense inicial", "evidence"), ("Providencia de instrucción", "resolution")],
    },
    {
        "title": "Femicidio íntimo – sector norte de Guayaquil",
        "description": "Caso de muerte violenta de mujer a manos de su pareja sentimental.",
        "state": "in_process",
        "parte_procesal": "Lucía Fernanda Bravo Ríos",
        "responsable_email": "fiscal2@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Autopsia médico-legal", "evidence"), ("Informe de criminalística", "evidence")],
    },
    {
        "title": "Homicidio preterintencional – riña callejera",
        "description": "Fallecimiento tras pelea en exteriores de discoteca. Cuatro testigos identificados.",
        "state": "draft",
        "parte_procesal": "Jorge Luis Ponce Alvarado",
        "responsable_email": "fiscal3@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Denuncia policial", "filing"), ("Croquis de la escena", "evidence")],
    },
    # ── Casos de Robo / Extorsión ────────────────────────────────────────────
    {
        "title": "Robo a mano armada – farmacia Los Ceibos",
        "description": "Sustracción de efectivo y medicamentos con uso de arma de fuego.",
        "state": "in_process",
        "parte_procesal": "Farmacia Los Ceibos S.A.",
        "responsable_email": "perito1@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Video CCTV sistematizado", "evidence"), ("Reconocimiento del lugar", "evidence")],
    },
    {
        "title": "Extorsión mediante llamadas telefónicas",
        "description": "Empresario víctima de exigencia de dinero bajo amenaza de muerte.",
        "state": "in_process",
        "parte_procesal": "Miguel Ángel Torres Espinoza",
        "responsable_email": "fiscal4@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Grabaciones de llamadas", "evidence"), ("Escrito acusatorio", "filing")],
    },
    {
        "title": "Robo de vehículo con violencia",
        "description": "Asalto a conductor de taxi en la vía Perimetral. Vehículo recuperado.",
        "state": "anchored",
        "parte_procesal": "Armando Javier Llanos Castro",
        "responsable_email": "fiscal5@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Parte policial de recuperación", "evidence"), ("Pericia mecánica del vehículo", "evidence")],
    },
    # ── Casos de Tráfico de Drogas ───────────────────────────────────────────
    {
        "title": "Tráfico ilícito de sustancias – operativo Puerto Marítimo",
        "description": "Decomiso de 120 kg de cocaína en contenedor frigorífico.",
        "state": "in_process",
        "parte_procesal": "Ministerio Público del Ecuador",
        "responsable_email": "fiscal6@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de decomiso SENAE", "evidence"), ("Análisis químico laboratorio", "evidence"), ("Auto de llamamiento a juicio", "resolution")],
    },
    {
        "title": "Microtráfico en unidad educativa",
        "description": "Distribución de estupefacientes dentro de colegio fiscal. Tres imputados menores.",
        "state": "draft",
        "parte_procesal": "Unidad Educativa Fiscal 28 de Mayo",
        "responsable_email": "fiscal7@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Denuncia DECE", "filing")],
    },
    # ── Casos de Corrupción / Peculado ──────────────────────────────────────
    {
        "title": "Peculado – contratación pública irregular",
        "description": "Presunta malversación de fondos en obra vial adjudicada sin concurso.",
        "state": "in_process",
        "parte_procesal": "Contraloría General del Estado",
        "responsable_email": "fiscal8@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe de auditoría CGE", "evidence"), ("Contratos de obra", "evidence"), ("Providencia de apertura", "resolution")],
    },
    {
        "title": "Cohecho – funcionario de aduana",
        "description": "Recepción de dádivas para facilitar ingreso de mercancía de contrabando.",
        "state": "anchored",
        "parte_procesal": "SENAE – Servicio Nacional de Aduana",
        "responsable_email": "fiscal9@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de allanamiento", "evidence"), ("Informe de inteligencia financiera UAFE", "evidence")],
    },
    # ── Casos de Violencia Intrafamiliar ────────────────────────────────────
    {
        "title": "Violencia física y psicológica en núcleo familiar",
        "description": "Agresión reiterada documentada por el MIES. Medidas de amparo vigentes.",
        "state": "in_process",
        "parte_procesal": "Paola Vanessa Cárdenas Mejía",
        "responsable_email": "juez1@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Informe MIES de riesgo", "evidence"), ("Reconocimiento médico lesiones", "evidence")],
    },
    {
        "title": "Violencia económica – privación de bienes",
        "description": "Cónyuge impide acceso a cuenta bancaria y retiene documentos de identidad.",
        "state": "draft",
        "parte_procesal": "Mariana José Salazar Delgado",
        "responsable_email": "juez2@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Denuncia ante DINAPEN", "filing")],
    },
    # ── Casos Civiles / Contractuales ───────────────────────────────────────
    {
        "title": "Incumplimiento de contrato de arrendamiento comercial",
        "description": "Demanda por falta de pago de 8 meses de canon arrendaticio.",
        "state": "in_process",
        "parte_procesal": "Inversiones Inmobiliarias del Pacífico CIA. LTDA.",
        "responsable_email": "juez3@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Contrato de arrendamiento", "evidence"), ("Demanda civil", "filing"), ("Auto de calificación", "resolution")],
    },
    {
        "title": "Daño moral – publicación difamatoria en redes sociales",
        "description": "Demanda por publicaciones que afectaron reputación profesional del actor.",
        "state": "draft",
        "parte_procesal": "Dr. Héctor Fabián Quiñónez Mera",
        "responsable_email": "juez4@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Capturas de pantalla certificadas", "evidence")],
    },
    {
        "title": "Cobro de pagaré – deuda empresarial",
        "description": "Juicio ejecutivo por pagaré de $45.000 no cancelado en plazo pactado.",
        "state": "in_process",
        "parte_procesal": "Banco del Pacífico S.A.",
        "responsable_email": "juez5@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Pagaré original protocolizado", "evidence"), ("Demanda ejecutiva", "filing")],
    },
    # ── Casos Laborales ─────────────────────────────────────────────────────
    {
        "title": "Despido intempestivo – empleado sector manufacturero",
        "description": "Trabajador con 12 años de servicio despedido sin causa justa ni liquidación.",
        "state": "in_process",
        "parte_procesal": "Roberto Carlos Navarrete Loor",
        "responsable_email": "juez6@funcionjudicial.gob.ec",
        "tipo": "Laboral",
        "docs": [("Contrato de trabajo", "evidence"), ("Carta de despido", "evidence"), ("Demanda laboral", "filing")],
    },
    {
        "title": "Acoso laboral y discriminación salarial",
        "description": "Empleada denuncia diferencia salarial injustificada y hostigamiento sistemático.",
        "state": "draft",
        "parte_procesal": "Andrea Beatriz Romero Tapia",
        "responsable_email": "juez7@funcionjudicial.gob.ec",
        "tipo": "Laboral",
        "docs": [("Informe Inspectoría de Trabajo", "evidence")],
    },
    # ── Casos de Ciberdelito ─────────────────────────────────────────────────
    {
        "title": "Acceso no autorizado a sistemas informáticos bancarios",
        "description": "Intrusión a base de datos de entidad financiera con extracción de 50.000 registros.",
        "state": "in_process",
        "parte_procesal": "Cooperativa de Ahorro JEP",
        "responsable_email": "perito2@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe forense digital", "evidence"), ("Logs del servidor comprometido", "evidence"), ("Denuncia entidad financiera", "filing")],
    },
    {
        "title": "Estafa mediante phishing bancario",
        "description": "Víctima transfirió $12.000 a cuenta fraudulenta tras engaño de correo electrónico falso.",
        "state": "in_process",
        "parte_procesal": "Ana Cecilia Villacís Ortega",
        "responsable_email": "fiscal10@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Correos electrónicos originales", "evidence"), ("Informe de rastreo bancario", "evidence")],
    },
    {
        "title": "Pornografía infantil – distribución por redes sociales",
        "description": "Investigación por difusión de material CSAM detectado por INTERPOL.",
        "state": "in_process",
        "parte_procesal": "Fiscalía Especializada DINAPEN",
        "responsable_email": "fiscal11@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe INTERPOL", "evidence"), ("Evidencia digital preservada", "evidence"), ("Solicitud de cooperación internacional", "filing")],
    },
    # ── Casos de Tránsito ────────────────────────────────────────────────────
    {
        "title": "Accidente de tránsito con heridos graves – vía Durán-Yaguachi",
        "description": "Colisión de bus interprovincial con volqueta deja 7 heridos.",
        "state": "in_process",
        "parte_procesal": "Cooperativa de Transporte Rutas Guayas",
        "responsable_email": "juez8@funcionjudicial.gob.ec",
        "tipo": "Tránsito",
        "docs": [("Croquis del accidente ANT", "evidence"), ("Informe médico de emergencia", "evidence")],
    },
    {
        "title": "Conducción en estado de embriaguez con resultado de muerte",
        "description": "Conductor con 2.1 g/L de alcohol atropella ciclista en vía urbana.",
        "state": "anchored",
        "parte_procesal": "Nathaly Esperanza Guzmán Pino",
        "responsable_email": "fiscal12@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Resultado de alcotest", "evidence"), ("Autopsia médico-legal", "evidence"), ("Auto de llamamiento a juicio", "resolution")],
    },
    # ── Casos de Narcotráfico transnacional ─────────────────────────────────
    {
        "title": "Organización delictiva transnacional – tráfico de armas",
        "description": "Desarticulación de red que introducía armas de fuego desde Colombia.",
        "state": "in_process",
        "parte_procesal": "Comando Conjunto de las Fuerzas Armadas",
        "responsable_email": "fiscal13@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de allanamiento", "evidence"), ("Inventario de armamento decomisado", "evidence"), ("Informe de inteligencia militar", "evidence")],
    },
    # ── Casos de Lavado de Activos ───────────────────────────────────────────
    {
        "title": "Lavado de activos mediante empresa fantasma",
        "description": "Constitución de sociedad ficticia para blanquear fondos del narcotráfico.",
        "state": "in_process",
        "parte_procesal": "Unidad de Análisis Financiero UAFE",
        "responsable_email": "fiscal14@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe UAFE de operaciones inusuales", "evidence"), ("Escritura constitución empresa", "evidence"), ("Movimientos bancarios", "evidence")],
    },
    # ── Casos de Niñez y Adolescencia ───────────────────────────────────────
    {
        "title": "Abuso sexual a menor de edad – entorno escolar",
        "description": "Denuncia por tocamientos indebidos por parte de auxiliar de servicio.",
        "state": "in_process",
        "parte_procesal": "DINAPEN – Policía Nacional",
        "responsable_email": "fiscal15@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Valoración psicológica CAMH", "evidence"), ("Testimonio anticipado", "evidence")],
    },
    {
        "title": "Sustracción de menor de edad por progenitor",
        "description": "Padre incumple sentencia de tenencia y retiene al menor en otra provincia.",
        "state": "draft",
        "parte_procesal": "Daniela Cristina Pazmiño Suárez",
        "responsable_email": "juez9@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Sentencia de tenencia", "evidence"), ("Denuncia por sustracción", "filing")],
    },
    # ── Casos de Propiedad Intelectual ──────────────────────────────────────
    {
        "title": "Piratería de software empresarial",
        "description": "Empresa utiliza 80 licencias de software sin autorización del titular.",
        "state": "in_process",
        "parte_procesal": "IEPI – Instituto Ecuatoriano Propiedad Intelectual",
        "responsable_email": "juez10@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Informe técnico de auditoría de licencias", "evidence"), ("Acta de inspección IEPI", "evidence")],
    },
    # ── Casos de Medio Ambiente ─────────────────────────────────────────────
    {
        "title": "Delito ambiental – vertido de residuos tóxicos en río",
        "description": "Empresa camaronera vierte efluentes sin tratamiento afectando ecosistema manglar.",
        "state": "in_process",
        "parte_procesal": "Ministerio del Ambiente MAE",
        "responsable_email": "fiscal16@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe de monitoreo ambiental", "evidence"), ("Análisis físico-químico del agua", "evidence"), ("Acta de infracción MAE", "evidence")],
    },
    # ── Casos de Estafa ─────────────────────────────────────────────────────
    {
        "title": "Estafa piramidal – captación ilegal de dinero",
        "description": "Organización capta inversiones prometiendo rendimientos del 30% mensual.",
        "state": "in_process",
        "parte_procesal": "Superintendencia de Compañías SCVS",
        "responsable_email": "fiscal17@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe SCVS de captación ilegal", "evidence"), ("Listado de afectados", "evidence"), ("Escrito de acusación particular", "filing")],
    },
    {
        "title": "Estafa en compraventa de inmueble inexistente",
        "description": "Ciudadano pagó $80.000 por terreno con documentos falsificados.",
        "state": "in_process",
        "parte_procesal": "William Enrique Sandoval Mora",
        "responsable_email": "fiscal18@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Escritura falsa notariada", "evidence"), ("Informe Registro de la Propiedad", "evidence")],
    },
    # ── Casos de Falsificación ──────────────────────────────────────────────
    {
        "title": "Falsificación de documentos públicos – cédula de identidad",
        "description": "Red de falsificación de cédulas y pasaportes desarticulada en operativo.",
        "state": "anchored",
        "parte_procesal": "Registro Civil del Ecuador",
        "responsable_email": "fiscal19@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Documentos falsos decomisados", "evidence"), ("Informe dactilar AFIS", "evidence"), ("Auto de llamamiento a juicio", "resolution")],
    },
    {
        "title": "Falsificación de título universitario",
        "description": "Profesional ejercía medicina con título apócrifo durante 3 años.",
        "state": "in_process",
        "parte_procesal": "Universidad de Guayaquil",
        "responsable_email": "fiscal20@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Título universitario cuestionado", "evidence"), ("Informe pericial grafológico", "evidence")],
    },
    # ── Casos de Secuestro ──────────────────────────────────────────────────
    {
        "title": "Plagio con fines de extorsión – empresario liberado",
        "description": "Víctima retenida durante 72 horas. Rescate parcialmente pagado.",
        "state": "closed",
        "parte_procesal": "Guillermo Esteban Hidalgo Romero",
        "responsable_email": "fiscal21@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Grabaciones de negociación", "evidence"), ("Informe operativo GIR", "evidence"), ("Sentencia condenatoria", "resolution")],
    },
    # ── Casos de Terrorismo ─────────────────────────────────────────────────
    {
        "title": "Ataque con explosivos a instalación policial",
        "description": "Detonación de artefacto en UPC periférica. Investigación en curso.",
        "state": "in_process",
        "parte_procesal": "Ministerio del Interior",
        "responsable_email": "fiscal22@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe GEMA peritos explosivos", "evidence"), ("Imágenes CCTV sector", "evidence"), ("Providencia de instrucción fiscal", "resolution")],
    },
    # ── Casos de Delitos Informáticos ───────────────────────────────────────
    {
        "title": "Sabotaje informático a empresa de telecomunicaciones",
        "description": "Ataque ransomware que cifró infraestructura crítica por 48 horas.",
        "state": "in_process",
        "parte_procesal": "CNT E.P.",
        "responsable_email": "perito3@dnafp.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe forense respuesta a incidente", "evidence"), ("Logs de sistemas afectados", "evidence")],
    },
    # ── Casos de Herencia / Sucesión ────────────────────────────────────────
    {
        "title": "Impugnación de testamento por falsedad",
        "description": "Herederos legítimos impugnan testamento que favorece a tercero no familiar.",
        "state": "in_process",
        "parte_procesal": "Sucesión Herederos Bermúdez Cisneros",
        "responsable_email": "juez11@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Testamento cuestionado", "evidence"), ("Informe grafológico", "evidence"), ("Demanda de impugnación", "filing")],
    },
    {
        "title": "Partición de bienes hereditarios – desacuerdo entre coherederos",
        "description": "Cinco herederos no logran acuerdo sobre distribución de bienes inmuebles.",
        "state": "draft",
        "parte_procesal": "Héctor Manuel Bermúdez Pérez",
        "responsable_email": "juez12@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Inventario de bienes", "evidence"), ("Demanda de partición", "filing")],
    },
    # ── Casos de Contrabando ────────────────────────────────────────────────
    {
        "title": "Contrabando de combustible – vía Huaquillas",
        "description": "Decomiso de 8.000 galones de gasolina trasladados ilegalmente desde Perú.",
        "state": "in_process",
        "parte_procesal": "SENAE – Aduana zona sur",
        "responsable_email": "fiscal23@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de incautación combustible", "evidence"), ("Informe técnico de valoración", "evidence")],
    },
    # ── Casos de Fraude Tributario ──────────────────────────────────────────
    {
        "title": "Evasión tributaria – empresa de construcción",
        "description": "Subdeclaración de IVA por $2.3 millones en ejercicios 2021-2023.",
        "state": "in_process",
        "parte_procesal": "Servicio de Rentas Internas SRI",
        "responsable_email": "fiscal24@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe de auditoría tributaria SRI", "evidence"), ("Facturas irregulares", "evidence"), ("Resolución de determinación SRI", "resolution")],
    },
    # ── Casos de Violación ──────────────────────────────────────────────────
    {
        "title": "Violación sexual – víctima mayor de edad",
        "description": "Agresión sexual cometida por desconocido en sector residencial.",
        "state": "in_process",
        "parte_procesal": "Patricia Soledad Jara Estrada",
        "responsable_email": "fiscal25@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Reconocimiento médico-forense", "evidence"), ("Informe de perito psicológico", "evidence"), ("Providencia de instrucción", "resolution")],
    },
    # ── Casos de Usurpación de Tierras ──────────────────────────────────────
    {
        "title": "Usurpación de terreno agrícola – comunidad indígena",
        "description": "Empresa minera ocupa territorio ancestral sin autorización ni consulta previa.",
        "state": "in_process",
        "parte_procesal": "Comunidad Kichwa Sarayacu",
        "responsable_email": "juez13@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Título comunitario de tierras", "evidence"), ("Informe de georreferenciación", "evidence"), ("Acción de protección", "filing")],
    },
    # ── Casos de Insolvencia / Quiebra ──────────────────────────────────────
    {
        "title": "Quiebra fraudulenta de empresa comercial",
        "description": "Administrador declaró insolvencia ocultando activos valorizados en $3M.",
        "state": "in_process",
        "parte_procesal": "Superintendencia de Compañías SCVS",
        "responsable_email": "fiscal26@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Balance general auditado", "evidence"), ("Informe SCVS de quiebra", "evidence")],
    },
    # ── Casos de Abuso de Autoridad ─────────────────────────────────────────
    {
        "title": "Abuso de autoridad policial – detención ilegal",
        "description": "Ciudadano retenido 36 horas sin orden judicial ni flagrancia.",
        "state": "draft",
        "parte_procesal": "José Antonio Intriago Mendoza",
        "responsable_email": "fiscal27@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Habeas corpus presentado", "filing"), ("Certificado médico de lesiones", "evidence")],
    },
    # ── Casos de Patrimonio Cultural ────────────────────────────────────────
    {
        "title": "Tráfico de bienes patrimoniales – arqueología",
        "description": "Exportación ilegal de piezas precolombinas incautadas en aeropuerto.",
        "state": "in_process",
        "parte_procesal": "Ministerio de Cultura del Ecuador",
        "responsable_email": "fiscal28@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de incautación aeropuerto", "evidence"), ("Inventario pericial arqueológico", "evidence")],
    },
    # ── Casos de Delitos Electorales ────────────────────────────────────────
    {
        "title": "Compra de votos en elecciones seccionales",
        "description": "Candidato a alcalde distribuye dinero en efectivo el día de elecciones.",
        "state": "closed",
        "parte_procesal": "Consejo Nacional Electoral CNE",
        "responsable_email": "fiscal29@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Videos de entrega de dinero", "evidence"), ("Testimonios de testigos", "evidence"), ("Resolución del TCE", "resolution")],
    },
    # ── Casos de Discriminación ─────────────────────────────────────────────
    {
        "title": "Discriminación racial en contratación laboral",
        "description": "Candidato afrodescendiente con mejor perfil rechazado por su etnia.",
        "state": "draft",
        "parte_procesal": "Francisco Xavier Caicedo Montaño",
        "responsable_email": "juez14@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Denuncia Defensoría del Pueblo", "filing")],
    },
    # ── Casos de Delitos Migratorios ────────────────────────────────────────
    {
        "title": "Tráfico de personas – migrantes venezolanos",
        "description": "Red cobra $800 por persona para cruce clandestino de frontera norte.",
        "state": "in_process",
        "parte_procesal": "OIM – Organización Internacional para las Migraciones",
        "responsable_email": "fiscal30@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Acta de rescate de migrantes", "evidence"), ("Declaraciones de víctimas", "evidence"), ("Informe Policía de Migración", "evidence")],
    },
    # ── Casos de Delitos Financieros ────────────────────────────────────────
    {
        "title": "Apropiación ilícita de fondos de cooperativa",
        "description": "Gerente transfiere $500.000 de ahorros de socios a cuenta personal.",
        "state": "anchored",
        "parte_procesal": "Cooperativa de Ahorro Luz del Sur",
        "responsable_email": "fiscal31@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Extractos bancarios comparados", "evidence"), ("Informe SEPS", "evidence"), ("Auto de prisión preventiva", "resolution")],
    },
    # ── Casos de Lesiones ───────────────────────────────────────────────────
    {
        "title": "Lesiones graves en riña con arma blanca",
        "description": "Víctima sufrió herida penetrante abdominal en incidente de barrio.",
        "state": "in_process",
        "parte_procesal": "Freddy Leonardo Espinoza Cano",
        "responsable_email": "fiscal32@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe médico IESS emergencia", "evidence"), ("Parte policial", "evidence")],
    },
    # ── Casos de Incendio Doloso ────────────────────────────────────────────
    {
        "title": "Incendio doloso en negocio comercial – conflicto entre socios",
        "description": "Bodega incendiada intencionalmente por ex socio en disputa por bienes.",
        "state": "in_process",
        "parte_procesal": "Distribuidora Comercial Andina S.A.",
        "responsable_email": "fiscal33@fiscalia.gob.ec",
        "tipo": "Penal",
        "docs": [("Informe CBG Cuerpo de Bomberos", "evidence"), ("Pericia química acelerantes", "evidence"), ("Póliza de seguro", "other")],
    },
    # ── Casos de Abandono de Menor ──────────────────────────────────────────
    {
        "title": "Abandono de recién nacido",
        "description": "Neonato encontrado en contenedor. MIES asume custodia provisional.",
        "state": "in_process",
        "parte_procesal": "MIES – Ministerio de Inclusión Económica",
        "responsable_email": "juez15@funcionjudicial.gob.ec",
        "tipo": "Familia",
        "docs": [("Acta de hallazgo policial", "evidence"), ("Informe médico neonatal", "evidence")],
    },
    # ── Casos de Tierras / Catastro ─────────────────────────────────────────
    {
        "title": "Doble titulación de predio rural",
        "description": "Mismo terreno aparece con dos propietarios distintos en el catastro municipal.",
        "state": "in_process",
        "parte_procesal": "GAD Municipal Daule",
        "responsable_email": "juez16@funcionjudicial.gob.ec",
        "tipo": "Civil",
        "docs": [("Escritura propietario A", "evidence"), ("Escritura propietario B", "evidence"), ("Informe Registro de la Propiedad", "evidence")],
    },
    # ── Caso Especial de Prueba Blockchain ──────────────────────────────────
    {
        "title": "Caso de prueba – Validación hash SHA-256 Ethereum Sepolia",
        "description": "Expediente creado exclusivamente para probar el anclaje en Ethereum Sepolia testnet y verificar integridad de hash.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Documento de prueba Sepolia v1", "evidence"), ("Documento de prueba Sepolia v2", "evidence")],
    },
    {
        "title": "Caso de prueba – Validación hash SHA-256 Celo Alfajores",
        "description": "Expediente creado exclusivamente para probar el anclaje en Celo Alfajores testnet.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Documento de prueba Celo v1", "evidence"), ("Documento de prueba Celo v2", "evidence")],
    },
    {
        "title": "Caso de prueba – Validación hash SHA-256 Hardhat local",
        "description": "Expediente creado exclusivamente para probar el anclaje en entorno Hardhat local.",
        "state": "draft",
        "parte_procesal": "Sistema Judicial Digital – Piloto",
        "responsable_email": "admin@judicial.gob.ec",
        "tipo": "Test",
        "docs": [("Documento de prueba Hardhat v1", "evidence")],
    },
]

# ---------------------------------------------------------------------------
# CONTENIDO BINARIO SIMULADO (contenido PDF simple en texto plano)
# ---------------------------------------------------------------------------
def _fake_pdf_content(nombre: str, caso: str) -> bytes:
    """Genera contenido de texto simple que simula un documento judicial."""
    contenido = (
        f"DOCUMENTO JUDICIAL SIMULADO\n"
        f"Expediente: {caso}\n"
        f"Documento: {nombre}\n"
        f"Generado: {datetime.now().isoformat()}\n"
        f"Sistema: Judicial Blockchain Odoo 19\n"
        f"Hash de integridad sera calculado por el sistema.\n"
    )
    return contenido.encode("utf-8")


# ---------------------------------------------------------------------------
# HELPERS XML-RPC
# ---------------------------------------------------------------------------
def connect(url: str, db: str, user: str, password: str):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, password, {})
    if not uid:
        raise SystemExit(f"[ERROR] No se pudo autenticar con {user} en {db}")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    print(f"[OK] Conectado a {url} como uid={uid}")
    return uid, models


def search_or_create_partner(models, db, uid, password, name: str) -> int:
    """Busca un partner existente por nombre o lo crea si no existe."""
    ids = models.execute_kw(
        db, uid, password, "res.partner", "search",
        [[["name", "=", name]]], {"limit": 1}
    )
    if ids:
        return ids[0]
    pid = models.execute_kw(
        db, uid, password, "res.partner", "create",
        [{"name": name, "is_company": False, "comment": "Parte procesal generada para pruebas"}]
    )
    return pid


def search_or_create_user(models, db, uid, password, email: str) -> int:
    """Devuelve uid del usuario por email, o usa admin si no existe."""
    ids = models.execute_kw(
        db, uid, password, "res.users", "search",
        [[["login", "=", email]]], {"limit": 1}
    )
    return ids[0] if ids else uid


# ---------------------------------------------------------------------------
# CREACIÓN DE EXPEDIENTES
# ---------------------------------------------------------------------------
def create_cases(url: str, db: str, user: str, password: str):
    uid, models_proxy = connect(url, db, user, password)

    created = []
    errors  = []

    for i, caso in enumerate(CASOS, 1):
        try:
            # 1. Partner (parte procesal principal)
            partner_id = search_or_create_partner(
                models_proxy, db, uid, password, caso["parte_procesal"]
            )

            # 2. Usuario responsable
            responsable_id = search_or_create_user(
                models_proxy, db, uid, password, caso["responsable_email"]
            )

            # 3. Crear el expediente
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

            # 4. Crear documentos adjuntos
            doc_ids = []
            for doc_nombre, doc_tipo in caso["docs"]:
                contenido_bytes = _fake_pdf_content(doc_nombre, caso["title"])
                b64 = base64.b64encode(contenido_bytes).decode("utf-8")
                sha_local = hashlib.sha256(contenido_bytes).hexdigest()

                doc_id = models_proxy.execute_kw(
                    db, uid, password, "judicial.document", "create",
                    [{
                        "name":                 doc_nombre,
                        "case_id":              case_id,
                        "document_type":        doc_tipo,
                        "attachment":           b64,
                        "filename":             f"{doc_nombre.replace(' ', '_').lower()}.txt",
                        "notes":                f"Documento generado para pruebas. SHA-256 local: {sha_local}",
                        "is_official_evidence": doc_tipo == "evidence",
                    }]
                )
                doc_ids.append(doc_id)

            # 5. Activar el primer documento del expediente
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

    # ── Resumen final ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"  EXPEDIENTES CREADOS : {len(created)}")
    print(f"  ERRORES             : {len(errors)}")
    if errors:
        print("\n  Detalle de errores:")
        for idx, titulo, err in errors:
            print(f"    [{idx:02d}] {titulo[:55]} → {err}")
    print("=" * 70)
    print("\n  Los expedientes están listos para pruebas de anclaje blockchain.")
    print("  Usa la vista Judicial > Expedientes en Odoo para acceder a ellos.\n")


# ---------------------------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera 50 expedientes judiciales de prueba en Odoo 19"
    )
    parser.add_argument("--url",      default=DEFAULT_URL,      help="URL de Odoo (ej: http://localhost:8069)")
    parser.add_argument("--db",       default=DEFAULT_DB,       help="Nombre de la base de datos")
    parser.add_argument("--user",     default=DEFAULT_USER,     help="Usuario administrador")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Contraseña del usuario")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  SEED: Expedientes Judiciales – Sistema Blockchain Odoo 19")
    print(f"  URL: {args.url}  DB: {args.db}  USER: {args.user}")
    print("=" * 70 + "\n")

    create_cases(args.url, args.db, args.user, args.password)
