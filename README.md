# Podcast Helper

Descarga episodios con proveedores de podcasts y una interfaz Flask.
Requiere Python 3.12. Para los proveedores Selenium, instala Firefox.

## Ejecutar localmente

```sh
pip install -r requirements.txt
python flask_entry_point.py
```

Abre http://localhost:5000. Introduce la URL del podcast y pulsa **Listar episodios**. Revisa los enlaces del segundo campo (o pega enlaces directamente)
y pulsa **Descargar episodios**. Al terminar se muestran los errores por enlace
o se devuelve el ZIP si se ha seleccionado el modo temporal.
Los trabajos son síncronos: espera la respuesta antes de volver a enviar.

## Estructura

- `services/podcasts.py`: listado y descarga por lotes, sin dependencias de Flask.
- `web/`: aplicación Flask, rutas, plantilla HTML y estilos.
- `flask_entry_point.py`: punto de entrada local y WSGI.
- `main.py`: entrada de consola con el mismo servicio; conserva la lista de enlaces.
- Los módulos de proveedores mantienen la extracción y descarga de cada plataforma.

Los proveedores RSS se configuran para listar sin descargar automáticamente.
Se procesa el resto del lote cuando un episodio lanza una excepción o devuelve False.
Los proveedores que ocultan errores internamente conservan esa limitación.

## Docker

Desde la raíz del proyecto:

```sh
docker compose -f docker/compose.yaml up --build -d
```

Abre http://localhost:5000. El contenedor usa Gunicorn, Firefox sin interfaz y
FFmpeg. Las descargas permanentes y el historial persisten en el volumen
`podcast-output`. Los ZIP temporales se eliminan tras su envío.
`docker/Dockerfile_1` se conserva como nombre alternativo compatible.
La construcción necesita Internet para instalar dependencias y GeckoDriver.

### Escribir en la carpeta local de config.json

Desde la raíz del proyecto, con Docker Desktop en modo contenedores Linux:

```sh
python docker/configure.py --local-output
docker compose -f docker/compose.yaml -f docker/compose.local.json up --build -d
```

El comando lee `res/config.json` (`output_folder`, actualmente `F:\podcast`)
y genera `docker/compose.local.json`. La carpeta debe existir en la máquina
que ejecuta Docker y estar accesible para Docker Desktop. Las rutas relativas
se interpretan desde la raíz del proyecto. Vuelve a ejecutar el comando si
cambias `output_folder`. Dentro del contenedor se sigue usando `/app/output`,
que apunta al almacenamiento montado; la ruta de Windows nunca se usa como ruta Linux.

En Linux, el directorio debe ser escribible por el usuario del contenedor.
Puedes pasar `PODCAST_UID` y `PODCAST_GID` al construir (por defecto 1000):

```sh
PODCAST_UID=$(id -u) PODCAST_GID=$(id -g) docker compose -f docker/compose.yaml -f docker/compose.local.json up --build -d
```

No se modifican recursivamente los permisos de la biblioteca local.
Cambiar entre montaje local y volumen no copia los archivos de uno a otro.

### SFTP cuando no se puede montar la carpeta local

SFTP está incluido en el mismo contenedor y se activa al proporcionar una clave
pública. Usa una clave existente o crea una (elige una frase de paso cuando se solicite):

```sh
ssh-keygen -t ed25519 -f podcast_sftp
python docker/configure.py --sftp-key podcast_sftp.pub
docker compose -f docker/compose.yaml -f docker/compose.local.json up --build -d
sftp -i podcast_sftp -P 2222 podcast@localhost
```

La clave privada `podcast_sftp` permanece en el cliente; solo se monta la `.pub`.
En el cliente SFTP, los archivos están en `/downloads`:

```text
cd /downloads
ls
get -R nombre-del-podcast
```

En FileZilla/WinSCP: protocolo SFTP, servidor `localhost`, puerto `2222`, usuario
`podcast`, autenticación con la clave privada. SFTP permite leer y descargar,
sin acceso de shell, escritura ni túneles. Las claves del servidor se conservan
en el volumen `podcast-ssh`, evitando que cambie su identidad en cada reinicio.
Para comprobar su huella antes de aceptar la primera conexión:

```sh
docker compose -f docker/compose.yaml -f docker/compose.local.json exec podcast-helper ssh-keygen -lf /var/lib/podcast-ssh/ssh_host_ed25519_key.pub
```

También puedes combinar ambas opciones:

```sh
python docker/configure.py --local-output --sftp-key podcast_sftp.pub
```

Sin `--local-output`, se usa el volumen `podcast-output`; no se intenta montar
la ruta de `config.json`. Elige este modo si Docker no puede acceder a esa ruta.
La generación reemplaza el override anterior, por lo que debes indicar juntas
las opciones que quieras conservar. Usa siempre ambos `-f` también para `logs`,
`down` y otras operaciones de ese despliegue. No uses `down -v` si quieres
conservar las descargas y las claves del servidor.

Los puertos web y SFTP se publican solo en localhost. Para un cliente en otra
máquina, ajusta explícitamente la dirección publicada del puerto SFTP según tu red.
SFTP permite recuperar las descargas permanentes: desmarca **Descargar como ZIP
temporal** en el formulario para conservarlas. No sirve para recuperar ZIP ya borrados.

`PODCAST_OUTPUT_FOLDER` cambia la carpeta de salida. `FIREFOX_BINARY` y
`GECKODRIVER_PATH` permiten usar binarios instalados explícitamente.
El servicio comparte un controlador Selenium y serializa sus operaciones.
En modo permanente, los archivos se conservan hasta que se eliminen de la carpeta o volumen. Esta interfaz está pensada para uso local de confianza,
sin autenticación; Compose publica el puerto solo en localhost.

## Historial de descargas

Se crea automáticamente `downloads.sqlite3` en la carpeta de salida. SQLite
viene incluido en Python: no necesita servidor ni instalaciones adicionales.
En la web, todos los lotes comparten el mismo historial, fuera de los ZIP.
El volumen de Docker conserva también este archivo.

SQLite utiliza una única tabla, `downloads`, con todos los datos de cada archivo.
Las URLs se conservan como metadatos en la misma fila (lista JSON en la columna
`episode_urls`), sin intervenir en la comparación de duplicados. Si la base no
existe, se crea desde cero. No se realizan migraciones de esquemas anteriores.

Se guardan nombre del podcast (artista del MP3), título, fecha de descarga en
UTC, álbum, fecha de publicación, número de pista, URL de origen, identificador
de YouTube cuando existe, duración, tamaño y ruta del archivo. Las etiquetas
ausentes quedan vacías. Solo se registran MP3 nuevos o modificados que puedan
leerse como audio y cuyo proveedor no haya indicado un fallo.

CLI y web comparan exclusivamente **nombre del podcast + título del episodio**,
con coincidencia exacta de ambos textos. Los proveedores consultan el historial
tras extraer esos nombres y antes de descargar el audio. Un episodio se omite
aunque cambie su URL o se haya eliminado o movido el archivo. La web muestra
«Ya descargado». El mismo título en otro podcast no se considera duplicado.
Las URLs y los identificadores se conservan únicamente como metadatos.
Las llamadas directas a módulos de proveedores no pasan por este historial.

Para incorporar los MP3 anteriores (sin descargarlos de nuevo):

```sh
python -m services.download_history "ruta/a/las/descargas"
python -m services.download_history "otra/carpeta" --database "ruta/a/las/descargas/downloads.sqlite3"
```

La importación puede repetirse sin duplicar una misma ruta. Usa la fecha de
modificación como estimación y la marca como `file_mtime`; las descargas nuevas
se marcan como `download`. Los archivos ilegibles se muestran y se omiten.
Los archivos importados se comparan por podcast y título sin necesitar una URL.
El nombre se obtiene del álbum si tiene el formato `Podcast <nombre>`; en otro
caso se utiliza el artista.
Conserva el archivo SQLite para mantener el historial al mover la biblioteca.

## Pruebas

```sh
python -m unittest discover -s tests -v
```

Las pruebas simulan proveedores para no descargar contenido real.

## Destino de las descargas web

La casilla **Descargar como ZIP temporal** está desmarcada por defecto.
Sin marcar, se usa `output_folder` de `res/config.json`, con la misma estructura
por podcast e historial SQLite que la CLI. `PODCAST_OUTPUT_FOLDER` permite
sobrescribir ese destino en Flask (Compose usa `/app/output`).

Con la casilla marcada se trabaja en un directorio temporal, con el mismo historial persistente que el modo permanente. El registro se
conserva aunque se eliminen los archivos temporales y permite detectar duplicados. Se devuelve directamente un ZIP que conserva los subdirectorios;
si hay errores parciales se incluyen en `errores.txt`. Al cerrar la respuesta
se borran el ZIP y el directorio temporal, también si se interrumpe el envío.
Si no se genera ningún archivo, se muestran los resultados en el formulario.
La limpieza requiere que el proceso siga vivo; un cierre forzado puede dejar
restos en el directorio temporal del sistema.

Referencias de la configuración Docker/SFTP: [montajes Docker](https://docs.docker.com/engine/storage/bind-mounts/) y [configuración OpenSSH](https://man.openbsd.org/sshd_config).
