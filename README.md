# Guía de Configuración Inicial de GitHub - UNAD

## 1. Instalar Git en Windows

Descarga el instalador en: https://git-scm.com/download/win

### Verificar la instalación

Abrir terminal o cmd:

```bash
git --version
```

## 2. Crear cuenta en GitHub

https://github.com/

---

## Configuración del Grupo

### 1 — Crear la organización

1. Ir a github.com → clic en "+" arriba a la derecha
2. Seleccionar "New organization"
3. Elegir plan **Free**
4. Ponerle nombre a la organización (ej: `grupo5-UNAD`)
5. Add organization members
6. Continuar y completar el setup

### 2 — Crear el repositorio dentro de la organización

1. Entrar a la organización → botón "New repository"
2. Ponerle nombre (ej: `proyecto-final`)
3. Marcar **"Add a README file"**
4. Clic en **Create repository**

### 3 — Invitar a los compañeros

1. Dentro del repositorio → **Settings** → **Collaborators and teams**
2. Clic en **Add people**
3. Buscar el usuario de GitHub de cada compañero
4. Asignarles rol **"Write"**
5. Cada compañero debe aceptar la invitación en su correo

---

## Cómo subir tu proyecto de Visual Studio Code a GitHub

**Link:** https://github.com/login

Entramos a GitHub, iniciamos sesión, y hacemos clic en **New repository**.

Hacemos clic en **Create repository**. GitHub mostrará una página con instrucciones — ahí estará la URL del repo, por ejemplo:
`https://github.com/tu-usuario/mi-proyecto.git`

### Inicializar Git

```bash
git init
```

> Sirve para que Git empiece a rastrear esta carpeta. Crea una carpeta oculta `.git` donde se guarda todo el historial. Solo se hace **una vez** por proyecto.

### Agregar archivos para subir a GitHub

```bash
git add .
git status
```

Si solo se quiere agregar un archivo específico:

```bash
git add index.html
```

### Configurar usuario

```bash
git config --global user.name "Jhon Harold"
git config --global user.email "jhonha.ing@gmail.com"
```

### Conectar tu proyecto con GitHub

```bash
git remote add origin https://github.com/tu-usuario/mi-proyecto.git
```

> Esto le dice a Git: "el repositorio remoto (en GitHub) se llama `origin` y está en esta URL". Es como darle a Git la dirección de destino. Solo se hace **una vez**.

### Hacer el primer commit (guardar el estado)

```bash
git commit -m "primer commit"
```

> Sirve para guardar el estado del proyecto en ese momento. Git guarda ese historial para siempre y se puede volver a cualquier punto.

### Verificar y cambiar rama

```bash
git branch                  # ver en qué rama estamos
git branch -M main          # cambiarnos a rama principal main
```

### Subir tu código a GitHub

```bash
git push -u origin main
```

Si sale error al cargar:

```bash
git pull origin main --allow-unrelated-histories
# o también:
git pull origin main --rebase
```

> - `push` → sube tus commits al servidor
> - `origin` → el nombre que le diste a GitHub
> - `main` → la rama que estás subiendo
> - `-u` → guarda esta configuración, así la próxima vez solo escribes `git push`

### El ciclo de trabajo (de ahí en adelante)

1. Haces cambios en tus archivos
2. Los agregas: `git add .`
3. Los confirmas con un mensaje: `git commit -m "descripción de lo que cambiaste"`
4. Los subes: `git push`

---

## Cada estudiante de forma individual

### 4 — Clonar el repositorio

Cada uno ejecuta esto en su terminal:

```bash
git clone https://github.com/nombre-organizacion/proyecto-final.git
cd proyecto-final
```

> - **username:** usuario_git
> - **password:** generar token

### 5 — Crear su propia rama

```bash
git switch main
git pull

# Crear su rama con su nombre
git switch -c feature/tu-nombre
```

Para cambiar de rama:

```bash
git switch nombre-de-la-rama
```

### 7 — Subir la rama a GitHub

```bash
git push -u origin feature/tu-nombre
```

### 8 — Trabajar y guardar cambios

```bash
git status                          # Ver qué archivos cambiaron
git add .                           # Agregar los cambios
git commit -m "descripción de lo que hice"   # Guardar con un mensaje
```

### Abrir Pull Request para unir el trabajo

1. En GitHub → entrar al repositorio
2. Verás un banner **"Compare & pull request"** sobre tu rama → clic ahí
3. Ponerle título y descripción
4. Clic en **Create pull request**

### 9 — El líder aprueba y fusiona

1. Entrar al Pull Request
2. Revisar los cambios → **"Review changes"**
3. Seleccionar **"Approve"**
4. Clic en **"Merge pull request"** → **"Confirm merge"**

### 10 — Todos se actualizan después de cada merge

```bash
git switch main
git pull
git switch feature/tu-nombre
git merge main
```

---

## Reglas importantes para el grupo

- Nadie trabaja directamente en `main`
- Cada uno solo modifica sus propios archivos
- Hacer `git pull` siempre antes de empezar a trabajar
- Un mensaje de commit claro por cada cambio importante
