
# Configuración
OLD_DEPLOYMENT="app-v1"
NEW_DEPLOYMENT="app-v2"
SERVICE="nginx"
NAMESPACE="default"

# Paso 1: Desplegar la versión antigua (Green)
echo "Desplegando versión antigua (Green)"
kubectl apply -f app-deployment-old.yaml
kubectl apply -f app-service.yaml

# Espera a que los pods de la versión antigua estén listos
kubectl rollout status deployment/$OLD_DEPLOYMENT -n $NAMESPACE
sleep 10
# Paso 2: Desplegar la nueva versión (Blue)
echo "Desplegando la nueva versión (Blue)"
kubectl apply -f app-deployment-new.yaml
kubectl rollout status deployment/$NEW_DEPLOYMENT -n $NAMESPACE

# Verificar pods en ejecución
kubectl get pods -n $NAMESPACE

# Paso 3: Cambiar el tráfico al Blue
echo "Cambiando el tráfico hacia la nueva versión (Blue)"
kubectl patch service $SERVICE \
  -n $NAMESPACE --patch "$(cat <<EOF
spec:
  selector:
    app: app
    version: v2
EOF
)"

# Verifica que el tráfico ahora apunte a la nueva versión
kubectl get service $SERVICE -n $NAMESPACE

# Paso 4: Opcional, eliminar la versión antigua (Green)
echo "Eliminando la versión antigua (Green)"
kubectl delete deployment $OLD_DEPLOYMENT -n $NAMESPACE

