# Práctica Kubernetes
### En este proyecto se adapta la aplicación realizada en terraform a un entorno de k8s, manteniendo la base de la app y su monitroización. Además, se añaden dos tipos de deployment green-blue y canary, cada uno con su respectivo script para probar su ejecución.
# Setup
## Prerequisitos
### 1. Tener instalado Docker
### 2. Tener instalado Kubernetes/kubectl
### 3. Tener instalado Minikube
## Pasos para aplicar la configuración
### 1. Clonar el repositorio en la máquina
### 2. Iniciar Docker Desktop y ejecutar en consola el comando `minikube start`
### 3. Con el contenedor ejecutado, acceder en bash a la ruta del proyecto clonado
### 4. Ejecutar el script setup.sh con el comando `./setup.sh`
### De esta manera tendremos configurada toda la app y la monitorización en nuestro minikube que podremos comprobar ejecutando minikube dashboard. Para visualizar la app podemos ejecutar el comando `minikube service nginx` y acceder a grafana con `minikube service grafana`.
# Arquitectura del proyecto
![Diagrama](https://i.imgur.com/pBrKD9j.png)

### Como se ve en el diagrama, la parte principal es la app que se apoya por una base de datos y una cache para mostrar la tabla de datos que proporciona la base de datos. Cada parte tiene su propio contenedor del que promtail obtiene logs que pasa a loki, además cada uno tiene asociado un scrapper que obtiene metricas que suministra a prometheus. Estas métricas y logs se pasan como datasource a grafana, que además tiene un configmap que le atribuye un dashboard creado con paneles para mostrar visualmente estas métricas (en este caso, logs, metricas de si los servicios están up y por último request 200 'OK' hacia la app). En el dashboard además hay un panel para alertas que no ha sido posible exportar. Resumidamente son 3 alertas sobre metricas de prometheus que toman el valor up de cada "job" de prometheus (db, app, cache) y si son inferiores a 1 salta la alerta y nos avisa de que dicho servicio esta caido. Estas alertas se pueden crear manulamente dentro de grafana en el aprtado de Alerts>Alert rules>Create new alert Rule.

# Tests
## GitHub Actions
### Primero, cada vez que se ejecuta un push sobre el repertorio el pipeline ejecuta el yaml en la carpeta .github/workflows, en la que lintea el codigo de la app de flask, le hace pasar por el un simple health check pushea la imagen al docker registry del usuario de dockerHub que esta seteado en github secrets y muestra un echo de que hacer para ejecutar el deployment de la nueva app ya que no disponemos de cloud.
## Tests
### Basicamente con el setup.sh se testea la creacion correcta de toda la configuración y se realiza un ajuste directo de la carpeta de grafana/data a nivel de la VM de minikube para dar robustez ya que si una vez ejecutas grafana y realizas `minikube delete` `minikube start` grafana deniega el acceso a la libreria de data exponiendo que no es posible escribir sobre ella y con la linea `minikube ssh "sudo mkdir -p /mnt/data/grafana && sudo chmod 777 /mnt/data/grafana"` se configura para que este problema no se de.
### El resto de tests son los ya realizados sobre el comportamiento de la app y la reaccion de la monitorización en grafana en las prácticas anteriores (Tirar los servicios y ver que la persistencia de la DB y grafana se mantiene, el html muestra correctamente la caida de dichos servicios y la tabla reacciona debidamente ante ello), además sigue mostrando la ip del contenedor/pod de la app para verificar que se esta realizando el balanceo de carga.
