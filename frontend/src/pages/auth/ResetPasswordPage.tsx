import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import authService from '../../services/auth.service';

// Import images
import loginDashboardImage from '../../images/images/login_dashboard.svg';
import logoTraficSmart from '../../images/logo/logo_trafic_smart.svg';
import { APP_NAME } from '../../config/appConfig';

export const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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

  // Check if token exists
  useEffect(() => {
    if (!token) {
      setError('Token inválido o no proporcionado.');
    }
  }, [token]);

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};
    
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
    
    if (!token) {
      setError('Token inválido o no proporcionado.');
      return;
    }
    
    // Reset states
    setSuccess(false);
    setError(null);
    
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }

    setIsLoading(true);

    try {
      await authService.resetPassword(token, password, confirmPassword);
      setSuccess(true);
    } catch (err: any) {
      console.error('Reset password error:', err);
      
      const errorData = err.response?.data;
      if (errorData?.code === 'TOKEN_EXPIRED') {
        setError('El enlace ha expirado. Por favor solicita uno nuevo.');
      } else if (errorData?.code === 'TOKEN_ALREADY_USED') {
        setError('Este enlace ya ha sido utilizado. Por favor solicita uno nuevo.');
      } else if (errorData?.code === 'TOKEN_NOT_FOUND') {
        setError('Enlace inválido. Por favor verifica el enlace o solicita uno nuevo.');
      } else {
        setError(errorData?.error || 'Error al restablecer la contraseña. Por favor intenta de nuevo.');
      }
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

          {/* Success Message - Show after password reset */}
          {success ? (
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
                      ¡Contraseña actualizada!
                    </h3>
                    <p className="text-base text-green-700 mb-6">
                      Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.
                    </p>
                    <button
                      onClick={() => navigate('/login')}
                      className="inline-block bg-primary-700 hover:bg-primary-600 text-white font-semibold px-8 py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105"
                    >
                      Ir al inicio de sesión
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
                  Crea tu nueva contraseña
                </h2>
                <p className="text-gray-500 text-sm">
                  Ingresa tu nueva contraseña para restablecer el acceso a tu cuenta
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
                    <div className="ml-3 flex-1">
                      <p className="text-sm text-red-800">{error}</p>
                      {(error.includes('expirado') || error.includes('utilizado') || error.includes('inválido')) && (
                        <button
                          onClick={() => navigate('/forgot-password')}
                          className="mt-2 text-sm font-medium text-red-700 hover:text-red-600 underline"
                        >
                          Solicitar nuevo enlace →
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Reset Password Form */}
              <form className="space-y-5" onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Nueva contraseña <span className="text-red-500">*</span>
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
                      placeholder="Ingresa tu nueva contraseña"
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Confirmar contraseña <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        // Limpiar error si ahora coinciden
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
                      placeholder="Confirma tu nueva contraseña"
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full bg-primary-700 hover:bg-primary-500 text-white font-semibold py-3 rounded-button transition-all duration-200 shadow-lg hover:shadow-2xl hover:scale-105"
                  disabled={isLoading || !token}
                  loading={isLoading}
                >
                  Restablecer contraseña
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

export default ResetPasswordPage;
