import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export const handleExport = async (
  pageRef: React.RefObject<HTMLDivElement>
) => {
  if (!pageRef?.current) return;

  //Clonar el nodo completo
  const element = pageRef.current.cloneNode(true) as HTMLElement;

  element.style.width = "297mm"; // ancho A4 horsssizontal
  element.style.minHeight = "210mm";
  element.style.padding = "20mm";
  element.style.backgroundColor = "white";
  element.style.overflow = "hidden";
  element.style.position = "fixed";
  element.style.top = "-9999px";
  element.style.left = "0";

  document.body.appendChild(element);

  try {
    // Capturar canvas
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF({
      orientation: "portrait",
      unit: "mm",
      format: "a4",
    });

    const pdfWidth = pdf.internal.pageSize.getWidth(); 
    const pdfHeight = pdf.internal.pageSize.getHeight(); 
    const imgProps = canvas.width / canvas.height;
    let pdfImgWidth = pdfWidth;
    let pdfImgHeight = pdfWidth / imgProps;

    if (pdfImgHeight > pdfHeight) {
      pdfImgHeight = pdfHeight;
      pdfImgWidth = pdfHeight * imgProps;
    }

    // Centrar horizontal y vertical
    const xOffset = (pdfWidth - pdfImgWidth) / 2;
    const yOffset = 10;

    pdf.addImage(imgData, "PNG", xOffset, yOffset, pdfImgWidth, pdfImgHeight);
    pdf.save("reporte-trafico.pdf");
  } catch (err) {
    console.error("Error al exportar PDF:", err);
  } finally {
    // Eliminar clon temporal
    document.body.removeChild(element);
  }
};
