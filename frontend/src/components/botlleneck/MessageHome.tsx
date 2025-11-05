import * as Icons from '@heroicons/react/24/outline'; // Importa todos los iconos

type MessageHomeProps = {
  placeholder?: string;
  icon: keyof typeof Icons; 
};

export default function MessageHome({ placeholder, icon }: MessageHomeProps) {
  const Icon = Icons[icon]; 

  return (
    <div className="w-full p-6 flex flex-col items-center justify-center h-64 space-y-3">
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <Icon className="h-12 w-12 text-gray-300 mb-2" /> 
        <span className="select-none">
          {placeholder || 'No hay datos disponibles para el rango seleccionado.'}
        </span>
      </div>
    </div>
  );
}
