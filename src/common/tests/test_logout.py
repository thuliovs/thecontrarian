"""
Tests for the logout functionality.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()

class LogoutTestCase(TestCase):
    """
    Test case for the logout functionality.
    
    This test case verifies that:
    1. The logout view correctly logs out the user
    2. The session is properly invalidated
    3. The user is redirected to the home page
    4. The response includes the correct cache control headers
    """
    
    def setUp(self):
        """
        Set up the test case by creating a test user and logging in.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
    def test_logout_view(self):
        """
        Test that the logout view correctly logs out the user.
        """
        # Verificar que o usuário está autenticado
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Fazer logout
        response = self.client.get(reverse('logout'))
        
        # Verificar que o usuário foi redirecionado para a página inicial
        self.assertRedirects(response, reverse('home'))
        
        # Verificar que o usuário não está mais autenticado
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Verificar que os cabeçalhos de cache control estão presentes
        self.assertEqual(response.get('Cache-Control'), 'no-cache, no-store, must-revalidate')
        self.assertEqual(response.get('Pragma'), 'no-cache')
        self.assertEqual(response.get('Expires'), '0')
        
    def test_session_invalidation(self):
        """
        Test that the session is properly invalidated after logout.
        """
        # Obter o ID da sessão antes do logout
        session_key = self.client.session.session_key
        
        # Verificar que a sessão existe no banco de dados
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())
        
        # Fazer logout
        self.client.get(reverse('logout'))
        
        # Verificar que a sessão antiga não existe mais ou foi invalidada
        session = Session.objects.filter(session_key=session_key).first()
        if session:
            # Se a sessão ainda existe, verificar que ela foi invalidada
            # (não contém mais o ID do usuário)
            session_data = session.get_decoded()
            self.assertFalse('_auth_user_id' in session_data) 