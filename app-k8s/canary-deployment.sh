#!/bin/bash

# Configuración
OLD_DEPLOYMENT="app-v1"
NEW_DEPLOYMENT="app-canary"
SERVICE="nginx"
NAMESPACE="default"

# Paso 1: Desplegar la versión actual (v1)
echo "Desplegando versión actual (v1)"
kubectl apply -f app-deployment-old.yaml
kubectl apply -f app-service.yaml
kubectl rollout status deployment/$OLD_DEPLOYMENT -n $NAMESPACE

# Paso 2: Desplegar la nueva versión (Canary)
echo "Desplegando la versión Canary (v2)"
kubectl apply -f app-deployment-canary.yaml
kubectl rollout status deployment/$NEW_DEPLOYMENT -n $NAMESPACE

# Paso 3: Incrementar gradualmente las réplicas del Canary
echo "Iniciando el despliegue Canary"
STEPS=(1 2 3)  # Cantidad de réplicas en cada paso
for STEP in "${STEPS[@]}"; do
  echo "Actualizando a ${STEP} réplicas para la versión Canary"
  
  # Actualizar las réplicas de la versión Canary
  kubectl scale deployment $NEW_DEPLOYMENT --replicas=$STEP -n $NAMESPACE
  
  # Ajustar las réplicas de la versión antigua
  OLD_REPLICAS=$((3 - STEP))
  echo "Reduciendo la versión antigua a ${OLD_REPLICAS} réplicas"
  kubectl scale deployment $OLD_DEPLOYMENT --replicas=$OLD_REPLICAS -n $NAMESPACE
  
  # Esperar a que los cambios se apliquen
  sleep 10
  
  # Mostrar el estado actual de los pods
  kubectl get pods -n $NAMESPACE
done

# Paso 4: Completar la migración
echo "Redirigiendo completamente el tráfico a la nueva versión"
kubectl scale deployment $NEW_DEPLOYMENT --replicas=3 -n $NAMESPACE
kubectl delete deployment $OLD_DEPLOYMENT -n $NAMESPACE

# Verificar el estado final
kubectl get all -n $NAMESPACE
