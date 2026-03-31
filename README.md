# Odoo 19 Judicial Blockchain MVP

MVP funcional alineado con la arquitectura del proyecto de titulación:
- **Cliente:** Odoo 19 / Odoo 19 Enterprise, portal web y dashboard simple
- **Intermedia:** módulos `judicial_base`, `judicial_blockchain`, `judicial_workflows`, `judicial_reports`, `judicial_portal`
- **Servidor:** PostgreSQL 16 + Polygon/EVM
- **Infraestructura:** Docker Compose, Nginx, GitHub Actions, Prometheus
- **Blockchain:** Hardhat + Solidity + Web3.py

## Estructura

```text
odoo19-judicial-mvp/
├── .github/workflows/ci.yml
├── contracts/
│   └── hardhat/
├── custom_addons/
│   ├── judicial_base/
│   ├── judicial_blockchain/
│   ├── judicial_workflows/
│   ├── judicial_reports/
│   └── judicial_portal/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── odoo.conf
│   └── prometheus.yml
├── scripts/
│   ├── deploy.sh
│   └── export_contract_abi.py
├── requirements.txt
└── .env.example
```

## Alcance del MVP

Incluye:
- gestión de expedientes
- partes procesales
- documentos / evidencias
- dashboard simple
- flujo de estados básico
- anclaje de hash en Polygon
- bitácora de transacciones blockchain
- reporte PDF del expediente
- portal para consulta del expediente por la parte procesal
- monitoreo básico con Prometheus
- pipeline CI inicial con GitHub Actions

No incluye:
- IPFS cluster productivo
- Celery y listeners asíncronos complejos
- firma digital avanzada
- notificaciones complejas
- HA/Kubernetes productivo

## Compatibilidad

El código está escrito para **Odoo 19 Community** y es utilizable también en **Odoo 19 Enterprise** porque no depende de APIs privativas de Enterprise.

## Puesta en marcha rápida

1. Copiar `.env.example` a `.env`
2. Ajustar variables RPC, wallet y dirección del contrato
3. Construir y levantar:

```bash
cd docker
docker compose up --build
```

4. Entrar en Odoo e instalar:
- Judicial Base
- Judicial Blockchain
- Judicial Workflows
- Judicial Reports
- Judicial Portal

## Flujo funcional

1. Crear un expediente judicial
2. Asociar parte procesal y documentos
3. Cambiar estado a `En proceso`
4. Ejecutar **Anclar en blockchain**
5. Guardar `tx_hash`, hash del documento y timestamp
6. Consultar el expediente desde portal
7. Emitir PDF desde reportes

## Despliegue de contrato

```bash
cd contracts/hardhat
cp .env.example .env
npm install
npx hardhat test
npx hardhat run scripts/deploy.ts --network amoy
```

Luego:
- copiar `deployed/JudicialChainOfCustody.json`
- ejecutar `python ../../scripts/export_contract_abi.py`
- pegar ABI y dirección del contrato en Ajustes de Odoo

## Nota de arquitectura

Este MVP implementa la versión **académica y desplegable** del diseño:
- Persistencia sensible en PostgreSQL/Odoo
- Solo hash y metadatos mínimos en blockchain
- Polygon/EVM por costo bajo
- Nginx delante de Odoo
- Docker para portabilidad
- Prometheus para health/telemetría inicial
