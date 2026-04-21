# Odoo 19 Judicial Blockchain MVP

MVP funcional orientado a la gestión, trazabilidad e integridad de evidencias digitales en expedientes judiciales mediante **Odoo 19**, **smart contracts** y redes blockchain EVM públicas de prueba.

## Descripción

Este proyecto implementa un producto mínimo viable (MVP) para registrar expedientes judiciales, documentos de evidencia y eventos de trazabilidad, manteniendo la información sensible **off-chain** en Odoo/PostgreSQL y utilizando la blockchain únicamente para registrar **hashes criptográficos y metadatos mínimos** de integridad y cadena de custodia.

El sistema está preparado para ejecutarse en entorno local y en nube pública mediante una arquitectura dockerizada con soporte para monitoreo, proxy inverso y validación continua.

## Stack tecnológico

- **ERP / Backend:** Odoo 19 Community / Odoo 19 Enterprise
- **Base de datos:** PostgreSQL 16
- **Blockchain:** Ethereum Sepolia y Celo Sepolia
- **Contratos inteligentes:** Solidity
- **Framework blockchain:** Hardhat
- **Integración blockchain:** Web3.py
- **Infraestructura:** Docker Compose
- **Reverse proxy:** Nginx
- **Monitoreo:** Prometheus
- **CI/CD inicial:** GitHub Actions

## Estructura del proyecto

```text
odoo19-judicial-mvp/
├── .github/
│   └── workflows/
│       └── ci.yml
├── contracts/
│   └── hardhat/
│       ├── contracts/
│       ├── scripts/
│       ├── test/
│       ├── hardhat.config.ts
│       ├── package.json
│       └── .env.example
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
├── .env.example
├── requirements.txt
└── README.md
```

## Alcance del MVP

### Incluye

- gestión de expedientes judiciales
- asociación de partes procesales
- carga y gestión de documentos / evidencias
- selección de documento activo
- cálculo de hash del documento
- anclaje de hash en blockchain EVM
- bitácora blockchain de transacciones
- visualización de `tx_hash`, `case_id`, wallet y fecha de anclaje
- flujo básico de estados del expediente
- reportes PDF
- portal básico de consulta
- monitoreo inicial con Prometheus
- pipeline CI inicial con GitHub Actions
- despliegue dockerizado para entorno local y nube pública

### No incluye

- almacenamiento de archivos en blockchain
- cifrado on-chain del documento
- IPFS productivo
- firma digital avanzada
- alta disponibilidad productiva
- Kubernetes
- listeners asíncronos complejos

## Cómo funciona el componente blockchain

El archivo de evidencia **no se almacena en blockchain**.

Flujo implementado:

1. El documento se carga y se almacena en Odoo/PostgreSQL.
2. El sistema calcula el hash criptográfico del documento activo.
3. Se genera un identificador del expediente (`caseId`).
4. El smart contract recibe únicamente:
   - `caseId`
   - `documentHash`
5. La blockchain registra:
   - hash del documento
   - timestamp
   - wallet que realizó el anclaje
   - existencia del registro
6. Odoo almacena localmente:
   - `tx_hash`
   - `case_id`
   - hash del documento
   - wallet ancla
   - fecha de anclaje

De esta forma, la blockchain se utiliza como mecanismo de **integridad, inmutabilidad y trazabilidad**, mientras que el archivo real permanece **off-chain**.

## Compatibilidad

El código está escrito para **Odoo 19 Community** y puede ser utilizado también en **Odoo 19 Enterprise**, ya que el MVP no depende de APIs exclusivas de Enterprise.

## Redes blockchain objetivo

El MVP está preparado para realizar pruebas comparativas sobre dos redes EVM públicas de prueba:

- **Ethereum Sepolia**
- **Celo Sepolia**

La lógica funcional del sistema será la misma en ambas redes; lo que variará será el proveedor RPC, el `chain_id`, la wallet de firma y la dirección del contrato desplegado.

## Variables de entorno

### Proyecto principal

Copiar el archivo:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Ejemplo conceptual:

```env
POSTGRES_DB=postgres
POSTGRES_USER=odoo19
POSTGRES_PASSWORD=odoo19
ODOO_ADMIN_PASSWORD=admin
ODOO_DB_HOST=db
ODOO_DB_PORT=5432
ODOO_DB_USER=odoo19
ODOO_DB_PASSWORD=odoo19

JUDICIAL_EVM_RPC_URL=
JUDICIAL_CHAIN_ID=
JUDICIAL_PRIVATE_KEY=
JUDICIAL_CONTRACT_ADDRESS=
JUDICIAL_CONTRACT_ABI=
```

### Hardhat

Dentro de `contracts/hardhat/` copiar:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

Ejemplo conceptual:

```env
SEPOLIA_RPC_URL=
CELO_SEPOLIA_RPC_URL=
PRIVATE_KEY=
```

## Puesta en marcha rápida

### Opción A — entorno dockerizado

Desde la carpeta `docker/`:

```bash
docker compose up --build
```

Luego ingresar a Odoo e instalar:

- Judicial Base
- Judicial Blockchain
- Judicial Workflows
- Judicial Reports
- Judicial Portal

### Opción B — ejecución local con Odoo Python

1. Configurar `odoo.conf`
2. Configurar PostgreSQL
3. Instalar dependencias Python
4. Ejecutar Odoo con los módulos custom
5. Instalar los módulos del MVP

## Flujo funcional

1. Crear un expediente judicial
2. Asociar la parte procesal principal
3. Subir uno o más documentos de evidencia
4. Calcular el hash del documento
5. Definir el documento activo
6. Cambiar el estado del expediente a `En proceso`
7. Ejecutar **Anclar en blockchain**
8. Registrar:
   - `TX Hash`
   - `Case ID bytes32`
   - `Wallet ancla`
   - `Fecha de anclaje`
9. Consultar la bitácora blockchain
10. Emitir reporte PDF o consultar el expediente desde portal

## Despliegue del contrato

### Preparación

```bash
cd contracts/hardhat
npm install
npx hardhat compile
npx hardhat test
```

### Despliegue en Ethereum Sepolia

```bash
npx hardhat run scripts/deploy.ts --network sepolia
```

### Despliegue en Celo Sepolia

```bash
npx hardhat run scripts/deploy.ts --network celoSepolia
```

Luego:

1. guardar la dirección del contrato desplegado
2. exportar el ABI
3. configurar Odoo con:
   - RPC URL
   - chain ID
   - private key
   - contract address
   - ABI

## Monitoreo

El proyecto incorpora **Prometheus** como componente base de observabilidad para monitoreo inicial del entorno dockerizado y del despliegue en nube pública.

Objetivos iniciales:

- disponibilidad del stack
- estado de contenedores
- consumo básico de recursos
- monitoreo inicial del entorno de ejecución

## CI/CD

El repositorio incluye una configuración inicial de **GitHub Actions** para validaciones automáticas del proyecto, incluyendo controles de calidad de código y pruebas técnicas del entorno blockchain.

## Seguridad y buenas prácticas

- no subir archivos `.env` al repositorio
- no subir llaves privadas ni archivos `.pem`
- no exponer PostgreSQL públicamente
- no exponer Odoo directamente si se utilizará Nginx como reverse proxy
- no almacenar documentos sensibles directamente en blockchain
- mantener el contrato como repositorio mínimo de integridad y trazabilidad

## Nota metodológica

Este MVP corresponde a la fase experimental del proyecto de investigación y se utilizará para comparar el comportamiento del sistema en distintos entornos de ejecución y sobre distintas redes blockchain EVM de prueba. En particular, se evaluará su operación en entorno local y en nube pública, así como su comportamiento sobre **Ethereum Sepolia** y **Celo Sepolia**, manteniendo constante la lógica funcional del sistema.

## Estado actual del modelo

El MVP está orientado a:

- validar el anclaje de evidencias digitales mediante hashes
- comprobar integridad documental
- registrar trazabilidad mínima de cadena de custodia
- medir comportamiento en redes blockchain públicas de prueba
- facilitar una comparación técnica entre distintas configuraciones de infraestructura y blockchain