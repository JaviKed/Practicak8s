# Build de la imagen de la app
minikube image build -t app-image:latest .

# Setup del archivo de datos de grafana (evita problemas al reiniciar minikube)
minikube ssh "sudo mkdir -p /mnt/data/grafana && sudo chmod 777 /mnt/data/grafana"

# Apply de todos los servicios
kubectl apply -f ./db
kubectl apply -f ./cache
kubectl apply -f ./app-k8s/app-service.yaml
kubectl apply -f ./app-k8s/app-deployment-old.yaml # Deploy de la version v1 original que es la que funciona con el servicio por defecto
kubectl apply -f ./monitoring
kubectl apply -f ./grafana