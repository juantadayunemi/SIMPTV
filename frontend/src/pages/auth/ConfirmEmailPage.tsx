import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../../services/auth.service';

// Import images
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';

export const ConfirmEmailPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const confirmEmail = async () => {
      const token = searchParams.get('token');

      if (!token) {
        setStatus('error');
        setMessage('Token de confirmación no encontrado en la URL.');
        return;
      }

      try {
        const response = await authService.confirmEmail(token);
        setStatus('success');
        setMessage(response.message);
        setUser(response.user);

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 3000);
      } catch (error: any) {
        setStatus('error');
        setMessage(
          error.response?.data?.error || 
          'Error al confirmar el correo electrónico. El enlace puede haber expirado.'
        );
      }
    };

    confirmEmail();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-700 via-primary-600 to-primary-500 flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <img
            src={logoTraficSmart}
            alt="TrafiSmart Logo"
            className="mx-auto h-24 w-auto filter drop-shadow-2xl mb-4"
          />
          <h1 className="text-white text-4xl font-bold drop-shadow-lg">
            {APP_NAME}
          </h1>
        </div>

        {/* Card */}
        <div className="bg-white rounded-card shadow-2xl p-8">
          {/* Loading State */}
          {status === 'loading' && (
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-700 mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Confirmando tu correo...
              </h2>
              <p className="text-gray-600">
                Por favor espera un momento mientras verificamos tu cuenta.
              </p>
            </div>
          )}

          {/* Success State */}
          {status === 'success' && (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                <svg
                  className="h-10 w-10 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                ¡Email Confirmado!
              </h2>
              
              <p className="text-gray-600 mb-4">
                {message}
              </p>

              {user && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-green-800">
                    <strong>Bienvenido, {user.firstName} {user.lastName}!</strong>
                  </p>
                  <p className="text-xs text-green-700 mt-1">
                    Tu cuenta ha sido activada exitosamente.
                  </p>
                </div>
              )}

              <div className="flex items-center justify-center text-sm text-gray-500 mb-4">
                <svg className="animate-spin h-4 w-4 mr-2 text-primary-700" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Redirigiendo al inicio de sesión...
              </div>

              <button
                onClick={() => navigate('/login')}
                className="w-full bg-primary-700 hover:bg-primary-600 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105"
              >
                Ir al Inicio de Sesión
              </button>
            </div>
          )}

          {/* Error State */}
          {status === 'error' && (
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <svg
                  className="h-10 w-10 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Error de Confirmación
              </h2>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-red-800">
                  {message}
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => navigate('/login')}
                  className="w-full bg-primary-700 hover:bg-primary-600 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  Ir al Inicio de Sesión
                </button>
                
                <button
                  onClick={() => navigate('/register')}
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-button transition-all duration-200"
                >
                  Registrarse Nuevamente
                </button>
              </div>

              <p className="text-sm text-gray-600 mt-6">
                Si el enlace ha expirado, puedes solicitar un nuevo correo de confirmación desde la página de inicio de sesión.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-white text-sm mt-6 drop-shadow">
          © 2025 TrafiSmart. Todos los derechos reservados.
        </p>
      </div>
    </div>
  );
};

export default ConfirmEmailPage;
