import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import authService from '../../services/auth.service';

// Import images
import loginDashboardImage from '../../images/images/login_dashboard.svg';
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Animation mount effect
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset states
    setSuccess(false);
    setError(null);
    
    // Basic validation
    const newErrors: { [key: string]: string } = {};
    if (!email) {
      newErrors.email = 'El correo electrónico es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Por favor ingresa un correo electrónico válido';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      await authService.forgotPassword(email);
      setSuccess(true);
    } catch (err: any) {
      console.error('Forgot password error:', err);
      setError(err.response?.data?.error || 'Error al enviar el correo. Por favor intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 lg:flex lg:relative">
      {/* Left Side - Traffic Image with Logo Overlay (Full Coverage) */}
      <div 
        className="hidden lg:block lg:w-[55%] relative overflow-hidden"
        style={{
          backgroundImage: `url(${loginDashboardImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        {/* Dark Overlay for better logo visibility */}
        <div className="absolute inset-0 bg-black bg-opacity-20"></div>

        {/* Logo + Brand Name Overlay - Centered */}
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <div className="flex flex-col items-center">
            <img
              src={logoTraficSmart}
              alt="TrafiSmart Logo"
              className={`h-80 w-auto filter drop-shadow-2xl transition-transform duration-1000 ease-in-out ${mounted ? 'animate-flip-in' : 'opacity-0'}`}
            />
            <h1 className="text-white -mt-8 text-6xl font-bold drop-shadow-2xl">
               {APP_NAME}
            </h1>
          </div>
        </div>
      </div>

      {/* Right Side - White Card Overlapping Image with Rounded Left Border */}
      <div 
        className="w-full lg:w-1/2 lg:-ml-8 relative z-20 bg-white lg:rounded-l-3xl shadow-2xl flex items-center justify-center px-8 py-12 lg:px-16 min-h-screen"
      >
        {/* Form Container */}
        <div className="w-full max-w-md">
          {/* Mobile Logo - Only visible on mobile */}
          <div className="lg:hidden text-center mb-8">
            <img
              src={logoTraficSmart}
              alt="TrafiSmart Logo"
              className="mx-auto h-16 w-auto mb-2"
            />
            <h1 className="text-2xl font-bold text-gray-900">{APP_NAME}</h1>
          </div>

          {/* Success Message - Show after email sent */}
          {success ? (
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 w-full animate-fade-in">
                <div className="flex flex-col items-center">
                  <div className="flex-shrink-0 mb-4">
                    <svg className="h-16 w-16 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-green-800 mb-3">
                      ✅ Solicitud procesada
                    </h3>
                    <p className="text-base text-green-700 mb-2">
                      Si el correo <strong>{email}</strong> está registrado en nuestro sistema, recibirás un enlace para restablecer tu contraseña.
                    </p>
                    <p className="text-sm text-green-600 mb-2">
                      ⏰ El enlace expirará en <strong>2 minutos</strong>. Revisa tu bandeja de entrada y spam.
                    </p>
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-left">
                      <p className="text-xs text-blue-700">
                        🛡️ <strong>Nota de seguridad:</strong> Por razones de privacidad, no revelamos si un correo existe en nuestro sistema.
                      </p>
                    </div>
                    <button
                      onClick={() => navigate('/login')}
                      className="mt-6 inline-block bg-primary-700 hover:bg-primary-600 text-white font-semibold px-8 py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105"
                    >
                      Volver al inicio de sesión
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-1">
                  Recupera tu contraseña
                </h2>
                <p className="text-gray-500 text-sm">
                  Ingresa tu correo electrónico para recibir el enlace de recuperación
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div 
                  className="
                    bg-red-50 border border-red-200 rounded-lg p-3 mb-6
                    animate-shake
                  "
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg 
                        className="h-5 w-5 text-red-500" 
                        viewBox="0 0 20 20" 
                        fill="currentColor"
                      >
                        <path 
                          fillRule="evenodd" 
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                          clipRule="evenodd" 
                        />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-800">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Forgot Password Form */}
              <form className="space-y-5" onSubmit={handleSubmit}>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Correo electrónico <span className="text-red-500">*</span>
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      setErrors({ ...errors, email: '' });
                      setError(null);
                    }}
                    error={errors.email}
                    required
                    placeholder="Introduce tu correo electrónico"
                    className="w-full"
                  />
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full bg-primary-700 hover:bg-primary-500 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105"
                  disabled={isLoading}
                  loading={isLoading}
                >
                  Enviar enlace de recuperación
                </Button>
              </form>

              {/* Back to Login Link */}
              <div className="mt-6 text-center">
                <button
                  onClick={() => navigate('/login')}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  ← Volver al inicio de sesión
                </button>
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
