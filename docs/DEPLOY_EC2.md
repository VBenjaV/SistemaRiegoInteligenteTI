# Despliegue en AWS EC2

Guía para publicar el **Sistema de Riego Inteligente** en una instancia EC2 usando Docker Compose (backend FastAPI, frontend Vue/nginx, MongoDB local, AWS IoT Core).

## Arquitectura en el servidor

```mermaid
flowchart LR
  Internet -->|:80| FE[frontend nginx]
  FE -->|/api /auth| BE[backend FastAPI]
  BE --> MongoDB[(MongoDB)]
  BE -->|MQTT TLS 8883| IoT[AWS IoT Core]
  BE --> Supabase[(Supabase Postgres)]
  BE --> OWM[OpenWeatherMap]
```

El usuario solo accede al puerto **80**. La API REST se sirve por el proxy de nginx (`/api/`, `/auth/`).

---

## 1. Crear la instancia EC2

| Parámetro | Recomendación |
|-----------|----------------|
| AMI | Ubuntu Server 22.04 LTS o 24.04 LTS |
| Tipo | `t3.small` o superior (MongoDB + build frontend) |
| Disco | 20–30 GB gp3 |
| Par de claves | Crear/descargar `.pem` para SSH |
| IP pública | Asignar Elastic IP (opcional pero recomendado) |

### Security Group (entrada)

| Puerto | Origen | Uso |
|--------|--------|-----|
| 22 | Tu IP (`x.x.x.x/32`) | SSH |
| 80 | `0.0.0.0/0` | HTTP (dashboard) |
| 443 | `0.0.0.0/0` | HTTPS (cuando configures SSL) |

No abras **27017** (MongoDB) ni **8000** (API directa) a Internet en producción; `docker-compose.prod.yml` ya los deja solo en la red Docker.

---

## 2. Conectar por SSH

```bash
chmod 400 tu-clave.pem
ssh -i tu-clave.pem ubuntu@<IP_PUBLICA_EC2>
```

En Amazon Linux el usuario suele ser `ec2-user`; en Ubuntu, `ubuntu`.

---

## 3. Clonar la rama de deploy

Los archivos de producción están en la rama **`DeployAWS`** (no en `main`):

```bash
git clone -b DeployAWS https://github.com/VBenjaV/SistemaRiegoInteligenteTI.git
cd SistemaRiegoInteligenteTI
```

Si el repositorio es **privado**, usa SSH o un token:

```bash
git clone -b DeployAWS git@github.com:VBenjaV/SistemaRiegoInteligenteTI.git
# o: git clone -b DeployAWS https://<TOKEN>@github.com/VBenjaV/SistemaRiegoInteligenteTI.git
```

Si ya clonaste `main`, cambia de rama:

```bash
cd SistemaRiegoInteligenteTI
git fetch origin
git checkout DeployAWS
git pull origin DeployAWS
```

---

## 4. Instalar Docker en el servidor

Desde la raíz del repo clonado:

```bash
cd SistemaRiegoInteligenteTI
chmod +x scripts/*.sh
bash scripts/ec2-setup.sh
```

Cierra sesión y vuelve a entrar (para el grupo `docker`), o ejecuta `newgrp docker`.

Verifica:

```bash
docker --version
docker compose version
```

---

## 5. Variables de entorno y secretos

### 5.1 `backend/.env`

```bash
cp backend/.env.example backend/.env
nano backend/.env   # o vim
```

Ajusta al menos:

- `DEBUG=False`
- `SUPABASE_URL`, `SUPABASE_KEY` (clave **anon**, no service_role)
- `SUPABASE_DB_URL` (pooler de Supabase)
- `WEATHER_API_KEY`
- `AWS_IOT_ENDPOINT` y topics MQTT

En Docker, **no hace falta** cambiar `MONGODB_URL`: `docker-compose.yml` ya usa `mongodb://mongodb:27017`.

### 5.2 Certificados AWS IoT (`IotCore/`)

La carpeta `IotCore/` no está en Git (`.gitignore`). Cópiala desde tu máquina local:

```bash
# Desde tu PC (PowerShell o bash)
scp -i tu-clave.pem -r IotCore ubuntu@<IP_EC2>:~/SistemaRiegoInteligenteTI/
```

Debe contener, entre otros:

- `AmazonRootCA1.pem`
- `*-certificate.pem.crt`
- `*-private.pem.key`

---

## 6. Levantar la aplicación

```bash
cd SistemaRiegoInteligenteTI
chmod +x scripts/deploy-prod.sh
./scripts/deploy-prod.sh
```

Comando equivalente:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Comprobar

```bash
curl -s http://localhost/health
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend
```

En el navegador: `http://<IP_PUBLICA_EC2>/`  
Documentación API: `http://<IP_PUBLICA_EC2>/docs`

---

## 7. HTTPS con Let's Encrypt (opcional)

Opción sencilla: **Caddy** o **nginx** en el host como reverse proxy. Ejemplo con Certbot en Ubuntu:

```bash
sudo apt-get install -y certbot
# Detén temporalmente el contenedor que usa el puerto 80 si hace falta
sudo certbot certonly --standalone -d riego.tudominio.com
```

Luego configura un proxy en el host que termine TLS en 443 y reenvíe a `127.0.0.1:80`, o monta certificados en un servicio nginx adicional. Para un dominio fijo, asocia un registro **A** en Route 53 hacia la Elastic IP.

---

## 8. Actualizar tras cambios en el código

En tu PC, sube la rama:

```bash
git push origin DeployAWS
```

En EC2:

```bash
cd SistemaRiegoInteligenteTI
./scripts/deploy-prod.sh
```

(`deploy-prod.sh` hace pull de `DeployAWS` por defecto; otra rama: `GIT_BRANCH=main ./scripts/deploy-prod.sh`)

---

## 9. Supabase y registro de usuarios

Si el registro devuelve **400 Bad Request**, revisa en [Supabase Dashboard](https://supabase.com/dashboard):

1. **Authentication → Providers → Email**
   - Email habilitado
   - Si **Confirm email** está activo, tras registrarte debes confirmar el correo antes de iniciar sesión

2. **Authentication → URL Configuration**

   Supabase **no permite** URLs con palabras bloqueadas (`ec2`, `amazonaws`, `compute`, etc.).  
   No uses: `http://ec2-xx-xx.compute.amazonaws.com` → dará *"Site URL contains blocked keywords"*.

   **Opción A — IP pública (rápida)**  
   - **Site URL:** `http://18.230.144.33` (solo la IP, sin hostname AWS)  
   - **Redirect URLs:** `http://18.230.144.33:5173/**` y/o `http://18.230.144.33/**`

   **Opción B — Dominio propio (recomendada)**  
   - Registra un dominio y apunta un registro **A** a la IP de la EC2.  
   - **Site URL:** `http://riego.tudominio.com`  
   - **Redirect URLs:** `http://riego.tudominio.com/**`

   **Opción C — Solo desarrollo / sin confirmación por email**  
   - **Site URL:** `http://localhost:5173`  
   - Desactiva **Confirm email** en Providers → Email (ver abajo).

3. **`backend/.env` en el servidor**
   - `SUPABASE_URL` = URL del proyecto (`https://xxxxx.supabase.co`)
   - `SUPABASE_KEY` = clave **anon** / publishable (`eyJ...`), **no** `service_role`

4. **429 email rate limit exceeded** (logs de Supabase en `/signup`):
   - Supabase limita cuántos correos de confirmación envía por hora (plan gratuito: pocos por hora).
   - **Solución rápida:** Authentication → Providers → Email → desactivar **Confirm email**.
   - O esperar 30–60 minutos antes de volver a registrar el mismo correo.
   - El usuario `doriacat4@gmail.com` puede ya existir: prueba **Iniciar sesión** o confirma el correo si llegó el link.

5. Causas habituales del 400:
   - Email ya registrado → inicia sesión o usa otro correo
   - Contraseña menor a 8 caracteres o sin cumplir política de Supabase
   - Registro deshabilitado en Providers

Tras cambiar `.env` en EC2: `docker compose up -d --force-recreate backend`

- **Auth (login/registro):** la Site URL debe coincidir con la URL del navegador (`http://<IP_EC2>` o `:5173`).
- **Base de datos:** Supabase ya está en la nube; la EC2 solo necesita salida a Internet (puerto 5432 al pooler).
- **AWS IoT:** la policy del certificado del backend debe permitir `subscribe`/`publish` en los topics configurados.

---

## 10. Solución de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| `502` en `/api` | `docker compose logs backend`; health del backend |
| Backend no arranca | `backend/.env`, certificados en `IotCore/` |
| Sin lecturas de sensor | `GET /api/debug/mqtt` vía proxy; policy IoT |
| Login falla | `SUPABASE_KEY` anon; Site URL en Supabase |
| MongoDB vacío | Normal en instancia nueva; el ESP debe publicar a IoT |

```bash
# Logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Reinicio limpio
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 11. Resumen de comandos

```bash
# En EC2 (primera vez)
git clone -b DeployAWS https://github.com/VBenjaV/SistemaRiegoInteligenteTI.git
cd SistemaRiegoInteligenteTI
bash scripts/ec2-setup.sh
# (re-login SSH)
cp backend/.env.example backend/.env && nano backend/.env
# scp IotCore desde tu PC
./scripts/deploy-prod.sh
```

---

## Alternativa sin Docker

No recomendada para este repo (hay tres servicios + certs). Si la necesitas: instala Python 3.11, Node 20, MongoDB y Mosquitto/AWS IoT manualmente siguiendo `README.md` y `ARCHITECTURE.md`.
