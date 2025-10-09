import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

// Import images
import loginDashboardImage from '../../images/images/login_dashboard.svg';
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [mounted, setMounted] = useState(false);
  const [showResendActivation, setShowResendActivation] = useState(false);
  const [resendEmail, setResendEmail] = useState('');
  const [resendSuccess, setResendSuccess] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [loginAttempted, setLoginAttempted] = useState(false); // ← NUEVO: Controlar si ya se intentó login
  const { login, isLoading, error, isAuthenticated, clearError } = useAuth();
  const navigate = useNavigate();

  // Animation mount effect
  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect to dashboard if already authenticated (SOLO SI NO HAY ERROR ACTIVO)
  useEffect(() => {
    if (isAuthenticated && !error && loginAttempted) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, error, loginAttempted, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset states
    setShowResendActivation(false);
    setResendSuccess(false);
    setLoginAttempted(true); // ← Marcar que se intentó login
    
    // Basic validation
    const newErrors: { [key: string]: string } = {};
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setLoginAttempted(false); // ← Resetear si hay errores de validación
      return;
    }

    try {
      await login(email, password, rememberMe);
      // Successful login - navigation will be handled by useEffect
    } catch (err: any) {
      // Check if error is due to unconfirmed email
      if (err.response?.data?.code === 'EMAIL_NOT_CONFIRMED') {
        setShowResendActivation(true);
        setResendEmail(err.response.data.email || email);
      }
      // NO resetear loginAttempted aquí - dejar que el error se muestre
    }
  };
  
  const handleResendActivation = async () => {
    setResendLoading(true);
    setResendSuccess(false);
    
    try {
      const authService = (await import('../../services/auth.service')).default;
      await authService.resendConfirmation(resendEmail);
      setResendSuccess(true);
    } catch (err) {
      console.error('Error resending activation:', err);
    } finally {
      setResendLoading(false);
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
        {/* Form Container - No additional card, just content */}
        <div className="w-full max-w-md">
          {/* Mobile Logo - Only visible on mobile */}
          <div className="lg:hidden text-center mb-8">
            <img
              src={logoTraficSmart}
              alt="TrafiSmart Logo"
              className="mx-auto h-16 w-auto mb-2"
            />
            <h1 className="text-2xl font-bold text-gray-900">Trafismart</h1>
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">
              Bienvenido a TrafiSmart
            </h2>
            <p className="text-gray-500 text-sm">
              Inicia sesión en tu cuenta
            </p>
          </div>

          {/* Login Form */}
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Dirección de correo electrónico <span className="text-red-500">*</span>
                </label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setErrors({ ...errors, email: '' });
                    setLoginAttempted(false); // ← Resetear error cuando el usuario edita
                    clearError(); // ← Limpiar error del hook
                  }}
                  error={errors.email}
                  required
                  placeholder="Introduce tu correo electrónico"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Contraseña <span className="text-red-500">*</span>
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErrors({ ...errors, password: '' });
                    setLoginAttempted(false); // ← Resetear error cuando el usuario edita
                    clearError(); // ← Limpiar error del hook
                  }}
                  error={errors.password}
                  required
                  placeholder="Ingresa tu contraseña"
                  className="w-full"
                />
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-4 w-4 text-primary-700 focus:ring-primary-500 border-gray-300 rounded cursor-pointer"
                />
                <label 
                  htmlFor="remember-me" 
                  className="ml-2 block text-sm text-gray-600 cursor-pointer"
                >
                  Recordar mi contraseña
                </label>
              </div>
              
              {/* Forgot Password Link */}
              <div className="text-sm">
                <a 
                  href="/forgot-password" 
                  className="font-medium text-primary-700 hover:text-primary-600 hover:underline"
                >
                  ¿Olvidaste tu contraseña?
                </a>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div 
                className="
                  bg-red-50 border border-red-200 rounded-lg p-3
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
            
            {/* Resend Activation Section */}
            {showResendActivation && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 animate-fade-in">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium text-yellow-800">
                      Cuenta no activada
                    </h3>
                    {!resendSuccess ? (
                      <>
                        <p className="mt-1 text-sm text-yellow-700">
                          Tu cuenta aún no ha sido confirmada. Revisa tu correo <strong>{resendEmail}</strong> para activarla.
                        </p>
                        <p className="mt-2 text-xs text-yellow-600">
                          ¿No recibiste el correo de activación?
                        </p>
                        <button
                          onClick={handleResendActivation}
                          disabled={resendLoading}
                          className="mt-2 text-sm font-medium text-yellow-700 hover:text-yellow-600 underline disabled:opacity-50"
                        >
                          {resendLoading ? 'Enviando...' : 'Reenviar correo de activación →'}
                        </button>
                      </>
                    ) : (
                      <div className="mt-2">
                        <p className="text-sm text-green-700 font-medium">
                          ✅ ¡Correo de activación enviado!
                        </p>
                        <p className="mt-1 text-xs text-green-600">
                          Revisa tu bandeja de entrada en <strong>{resendEmail}</strong>
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-primary-700 hover:bg-primary-500 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl"
              disabled={isLoading}
              loading={isLoading}
            >
              Iniciar sesión
            </Button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              ¿No tienes una cuenta?{' '}
              <a href="/register" className="text-primary-700 hover:text-primary-600 font-semibold hover:underline">
                Regístrate aquí
              </a>
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default LoginPage;