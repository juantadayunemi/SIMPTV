import { pdf } from "@react-pdf/renderer";
import { TrafficReportPDF } from "../components/historyTraffic/TrafficExportPDF";
import {
  CongestionData,
  VelocityData,
  VolumeData,
  TrafficType,
} from "../types/historyTraffic";

interface ExportPDFParams {
  trafficType: TrafficType;
  congestionData?: CongestionData | null;
  velocityData?: VelocityData | null;
  volumeData?: VolumeData | null;
  locationName: string;
  cameraName: string;
  dateRange: string;
  chartRef?: React.RefObject<HTMLDivElement>;
}

/*
Convierte un elemento SVG a imagen base64
 */
const svgToImageUrl = async (
  svgElement: SVGElement
): Promise<string> => {
  return new Promise((resolve, reject) => {
    try {
      // Clonar el SVG para no modificar el original
      const clonedSvg = svgElement.cloneNode(true) as SVGElement;
      
      // Asegurar que tenga las dimensiones correctas
      const bbox = svgElement.getBBox();
      clonedSvg.setAttribute("width", String(bbox.width || 1000));
      clonedSvg.setAttribute("height", String(bbox.height || 400));

      // Serializar el SVG
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(clonedSvg);
      
      // Crear un blob del SVG
      const svgBlob = new Blob([svgString], {
        type: "image/svg+xml;charset=utf-8",
      });
      const url = URL.createObjectURL(svgBlob);

      // Crear imagen
      const img = new Image();
      img.onload = () => {
        // Crear canvas
        const canvas = document.createElement("canvas");
        canvas.width = bbox.width || 1000;
        canvas.height = bbox.height || 400;
        
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          reject(new Error("No se pudo obtener el contexto del canvas"));
          return;
        }

        // Fondo blanco
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Dibujar la imagen
        ctx.drawImage(img, 0, 0);
        
        // Convertir a base64
        const imageUrl = canvas.toDataURL("image/png");
        URL.revokeObjectURL(url);
        resolve(imageUrl);
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("Error al cargar la imagen SVG"));
      };

      img.src = url;
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Captura la gráfica como imagen
 */
const captureChartImage = async (
  chartRef?: React.RefObject<HTMLDivElement>
): Promise<string | undefined> => {
  if (!chartRef?.current) return undefined;

  try {
    // Buscar el elemento SVG dentro del div
    const svgElement = chartRef.current.querySelector("svg");
    if (!svgElement) {
      console.warn("No se encontró elemento SVG en la gráfica");
      return undefined;
    }

    const imageUrl = await svgToImageUrl(svgElement);
    return imageUrl;
  } catch (error) {
    console.error("Error al capturar la gráfica:", error);
    return undefined;
  }
};

/*
 Genera y descarga el PDF del reporte de tráfico
*/
export const generateTrafficPDF = async ({
  trafficType,
  congestionData,
  velocityData,
  volumeData,
  locationName,
  cameraName,
  dateRange,
  chartRef,
}: ExportPDFParams): Promise<void> => {
  try {
    // Capturar la imagen de la gráfica
    const chartImageUrl = await captureChartImage(chartRef);

    // Crear el documento PDF
    const doc = TrafficReportPDF({
      trafficType,
      congestionData,
      velocityData,
      volumeData,
      locationName,
      cameraName,
      dateRange,
      chartImageUrl,
    });

    // Generar el blob del PDF
    const blob = await pdf(doc).toBlob();

    // Crear nombre del archivo
    const fileName = `reporte_trafico_${trafficType}_${new Date()
      .toISOString()
      .slice(0, 10)}.pdf`;

    // Descargar el archivo
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar el PDF:", error);
    throw new Error("No se pudo generar el PDF. Por favor, intente nuevamente.");
  }
};



export const formatDateRangeForPDF = (
  dateFrom: string,
  dateTo: string
): string => {
  const from = new Date(dateFrom).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const to = new Date(dateTo).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  return `${from} - ${to}`;
};