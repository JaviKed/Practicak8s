import unittest
from unittest.mock import patch
from app import app, app_up

class TestHealthEndpoint(unittest.TestCase):
    def setUp(self):
        # Configurar la aplicación en modo de prueba
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.check_db_connection', return_value=True)
    @patch('app.check_redis_connection', return_value=True)
    def test_health_success(self, mock_redis, mock_db):
        """Test when both DB and Redis connections are successful."""
        response = self.app.get('/health')  # Llamar al endpoint
        self.assertEqual(response.status_code, 200)  # Verificar código de estado
        self.assertEqual(response.data.decode(), "App is healthy!")  # Verificar respuesta
        self.assertEqual(app_up._value.get(), 1)  # Verificar si el indicador de Prometheus está en 1



if __name__ == '__main__':
    unittest.main()