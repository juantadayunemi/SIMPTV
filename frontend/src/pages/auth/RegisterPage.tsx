import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

// Import images
import loginDashboardImage from '../../images/images/login_dashboard.svg';
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';

export const RegisterPage: React.FC = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [mounted, setMounted] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const [apiError, setApiError] = useState<{ message: string; suggestion?: string; code?: string } | null>(null);
  const { register, isLoading, error, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Animation mount effect
  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};
    
    if (!firstName) {
      newErrors.firstName = 'El nombre es requerido';
    }
    
    if (!lastName) {
      newErrors.lastName = 'Los apellidos son requeridos';
    }
    
    if (!email) {
      newErrors.email = 'El correo electrónico es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Por favor ingresa un correo electrónico válido';
    }
    
    if (!password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (password.length < 8) {
      newErrors.password = 'La contraseña debe tener al menos 8 caracteres';
    }
    
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Por favor confirma tu contraseña';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Reset API error
    setApiError(null);
    
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    try {
      await register(firstName, lastName, email, password, confirmPassword);
      
      // Registration successful - show success message
      setRegistrationSuccess(true);
      
    } catch (err: any) {
      console.error('Registration error:', err);
      
      // Check if it's a structured API error
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Check if we have our custom error structure
        if (errorData.code && errorData.error) {
          setApiError({
            message: errorData.error,
            suggestion: errorData.suggestion || '',
            code: errorData.code
          });
        }
        // Check if it's a field validation error
        else if (errorData.errors?.email) {
          const emailError = Array.isArray(errorData.errors.email) 
            ? errorData.errors.email[0] 
            : errorData.errors.email;
          
          // Parse error message if it contains our format: [CODE] Message
          if (typeof emailError === 'string' && emailError.startsWith('[')) {
            const codeEnd = emailError.indexOf(']');
            if (codeEnd > 0) {
              const code = emailError.substring(1, codeEnd);
              const fullMessage = emailError.substring(codeEnd + 2).trim();
              
              // Split into message and suggestion
              const parts = fullMessage.split('. ');
              const message = parts[0] + '.';
              const suggestion = parts.slice(1).join('. ');
              
              setApiError({
                message,
                suggestion,
                code
              });
            } else {
              setApiError({
                message: emailError,
                code: 'VALIDATION_ERROR'
              });
            }
          } else {
            setApiError({
              message: emailError,
              code: 'VALIDATION_ERROR'
            });
          }
        }
        // Generic error
        else {
          setApiError({
            message: errorData.error || errorData.message || 'Error al registrar usuario',
            code: 'UNKNOWN_ERROR'
          });
        }
      } else {
        // Network error or unexpected error
        setApiError({
          message: 'Error de conexión. Por favor verifica tu conexión a internet.',
          code: 'NETWORK_ERROR'
        });
      }
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
            <h1 className="text-2xl font-bold text-gray-900">{APP_NAME}</h1>
          </div>

          {/* Success Message - Show after registration (CENTERED AND FULL SCREEN) */}
          {registrationSuccess ? (
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 w-full animate-fade-in">
                <div className="flex flex-col items-center">
                  <div className="flex-shrink-0 mb-4">
                    <svg className="h-16 w-16 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-green-800 mb-3">
                      ¡Registro exitoso!
                    </h3>
                    <p className="text-base text-green-700 mb-4">
                      Hemos enviado un correo de confirmación a <strong>{email}</strong>. 
                      Por favor revisa tu bandeja de entrada y haz clic en el enlace para activar tu cuenta.
                    </p>
                    <p className="text-sm text-green-600 mb-6">
                      ⏰ El enlace expirará en 3 minutos. Por favor confírmalo de inmediato.
                    </p>
                    <button
                      onClick={() => navigate('/login')}
                      className="inline-block bg-primary-700 hover:bg-primary-600 text-white font-semibold px-8 py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105"
                    >
                      Ir al inicio de sesión →
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
                  ¡Crea tu cuenta!
                </h2>
                <p className="text-gray-500 text-sm">
                  Ingrese sus datos completos
                </p>
              </div>

          {/* API Error Messages - Email already exists, invalid domain, etc */}
          {apiError && (
            <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 animate-shake">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    {apiError.message}
                  </h3>
                  {apiError.suggestion && (
                    <p className="mt-2 text-sm text-yellow-700">
                      💡 {apiError.suggestion}
                    </p>
                  )}
                  
                  {/* Show "Forgot Password" link if email exists */}
                  {apiError.code === 'EMAIL_ALREADY_EXISTS' && (
                    <div className="mt-3">
                      <a 
                        href="/forgot-password" 
                        className="text-sm font-medium text-yellow-700 hover:text-yellow-600 underline"
                      >
                        ¿Olvidaste tu contraseña? →
                      </a>
                    </div>
                  )}
                  
                  {/* Show "Resend Activation" link if email not confirmed */}
                  {apiError.code === 'EMAIL_NOT_CONFIRMED' && (
                    <div className="mt-3">
                      <button
                        onClick={() => navigate('/login')}
                        className="text-sm font-medium text-yellow-700 hover:text-yellow-600 underline"
                      >
                        Ir a activar mi cuenta →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Register Form */}
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* Nombres */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Nombres <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={firstName}
                  onChange={(e) => {
                    setFirstName(e.target.value);
                    setErrors({ ...errors, firstName: '' });
                  }}
                  error={errors.firstName}
                  required
                  placeholder="Introduce tus nombres"
                  className="w-full"
                />
              </div>

              {/* Apellidos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Apellidos <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={lastName}
                  onChange={(e) => {
                    setLastName(e.target.value);
                    setErrors({ ...errors, lastName: '' });
                  }}
                  error={errors.lastName}
                  required
                  placeholder="Introduce tus apellidos"
                  className="w-full"
                />
              </div>

              {/* Correo electrónico */}
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
                  }}
                  error={errors.email}
                  required
                  placeholder="Introduce tu correo electrónico"
                  className="w-full"
                />
              </div>

              {/* Contraseña */}
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
                    // Limpiar error de confirmación si ahora coinciden
                    if (confirmPassword && e.target.value === confirmPassword) {
                      setErrors({ ...errors, password: '', confirmPassword: '' });
                    }
                  }}
                  error={errors.password}
                  required
                  placeholder="Ingresa tu contraseña"
                  className="w-full"
                />
              </div>

              {/* Confirmar contraseña */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Confirmar contraseña <span className="text-red-500">*</span>
                </label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    // Limpiar error si ahora coinciden con la contraseña
                    if (password && e.target.value === password) {
                      setErrors({ ...errors, confirmPassword: '' });
                    } else if (password && e.target.value !== password) {
                      setErrors({ ...errors, confirmPassword: 'Las contraseñas no coinciden' });
                    } else {
                      setErrors({ ...errors, confirmPassword: '' });
                    }
                  }}
                  error={errors.confirmPassword}
                  required
                  placeholder="Confirma tu contraseña"
                  className="w-full"
                />
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

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-primary-700 hover:bg-primary-500 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105 hover:-translate-y-0.5"
              disabled={isLoading}
              loading={isLoading}
            >
              Continuar
            </Button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              ¿Tienes una cuenta?{' '}
              <a href="/login" className="text-primary-700 hover:text-primary-600 font-semibold hover:underline">
                Iniciar sesión
              </a>
            </p>
          </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default RegisterPage;