import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Image,
  Font,
} from "@react-pdf/renderer";
import {
  CongestionData,
  VelocityData,
  VolumeData,
  TrafficType,
} from "../../types/historyTraffic";


// Estilos para el PDF
const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontSize: 10,
    fontFamily: "Helvetica",
  },
  header: {
    marginBottom: 20,
    borderBottom: "2 solid #2563eb",
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#1e40af",
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 12,
    color: "#64748b",
  },
  section: {
    marginTop: 15,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#1e293b",
    marginBottom: 10,
    paddingBottom: 5,
    borderBottom: "1 solid #e2e8f0",
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  statCard: {
    width: "48%",
    padding: 12,
    backgroundColor: "#f8fafc",
    borderRadius: 8,
    border: "1 solid #e2e8f0",
  },
  statTitle: {
    fontSize: 9,
    color: "#64748b",
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#0f172a",
    marginBottom: 3,
  },
  statSubtitle: {
    fontSize: 8,
    color: "#94a3b8",
  },
  chartContainer: {
    marginTop: 15,
    marginBottom: 15,
    padding: 15,
    backgroundColor: "#ffffff",
    borderRadius: 8,
    border: "1 solid #e2e8f0",
  },
  chartTitle: {
    fontSize: 12,
    fontWeight: "bold",
    color: "#0f172a",
    marginBottom: 5,
  },
  chartSubtitle: {
    fontSize: 9,
    color: "#64748b",
    marginBottom: 10,
  },
  chartImage: {
    width: "100%",
    height: "auto",
  },
  dataTable: {
    marginTop: 10,
  },
  tableHeader: {
    flexDirection: "row",
    backgroundColor: "#f1f5f9",
    padding: 8,
    borderRadius: 4,
    marginBottom: 5,
  },
  tableRow: {
    flexDirection: "row",
    padding: 8,
    borderBottom: "1 solid #e2e8f0",
  },
  tableCell: {
    flex: 1,
    fontSize: 9,
  },
  tableCellHeader: {
    flex: 1,
    fontSize: 9,
    fontWeight: "bold",
    color: "#475569",
  },
  footer: {
    position: "absolute",
    bottom: 30,
    left: 30,
    right: 30,
    textAlign: "center",
    color: "#94a3b8",
    fontSize: 8,
    borderTop: "1 solid #e2e8f0",
    paddingTop: 10,
  },
  metadata: {
    marginTop: 10,
    padding: 10,
    backgroundColor: "#fef3c7",
    borderRadius: 6,
    border: "1 solid #fde047",
  },
  metadataText: {
    fontSize: 9,
    color: "#854d0e",
    marginBottom: 3,
  },
});

interface TrafficReportPDFProps {
  trafficType: TrafficType;
  congestionData?: CongestionData | null;
  velocityData?: VelocityData | null;
  volumeData?: VolumeData | null;
  locationName: string;
  cameraName: string;
  dateRange: string;
  chartImageUrl?: string;
}

export const TrafficReportPDF = ({
  trafficType,
  congestionData,
  velocityData,
  volumeData,
  locationName,
  cameraName,
  dateRange,
  chartImageUrl,
}: TrafficReportPDFProps) => {
  const currentDate = new Date().toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const renderCongestionStats = () => {
    if (!congestionData) return null;

    return (
      <>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Velocidad Promedio</Text>
            <Text style={styles.statValue}>
              {Math.round(congestionData.avg_velocity)} km/h
            </Text>
            <Text style={styles.statSubtitle}>En el periodo seleccionado</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Congestión Promedio</Text>
            <Text style={styles.statValue}>
              {(congestionData.avg_congestion * 100).toFixed(2)}%
            </Text>
            <Text style={styles.statSubtitle}>Nivel de congestión</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Hora Pico</Text>
            <Text style={styles.statValue}>
              {congestionData.rush_hour.hour}:00
            </Text>
            <Text style={styles.statSubtitle}>
              {Math.round(congestionData.rush_hour.count_vehicles)} vehículos
            </Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Días Analizados</Text>
            <Text style={styles.statValue}>
              {congestionData.days_analyzed}
            </Text>
            <Text style={styles.statSubtitle}>Periodo de análisis</Text>
          </View>
        </View>

        {congestionData.congestion_per_day &&
          congestionData.congestion_per_day.length > 0 && (
            <View style={styles.dataTable}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableCellHeader}>Fecha</Text>
                <Text style={styles.tableCellHeader}>Congestión</Text>
              </View>
              {congestionData.congestion_per_day.slice(0, 10).map((day, idx) => (
                <View key={idx} style={styles.tableRow}>
                  <Text style={styles.tableCell}>
                    {new Date(day.day).toLocaleDateString("es-ES")}
                  </Text>
                  <Text style={styles.tableCell}>
                    {day.total.toFixed(2)}%
                  </Text>
                </View>
              ))}
            </View>
          )}
      </>
    );
  };

  const renderVelocityStats = () => {
    if (!velocityData) return null;

    return (
      <>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Velocidad Promedio</Text>
            <Text style={styles.statValue}>
              {Math.round(velocityData.avg_velocity)} km/h
            </Text>
            <Text style={styles.statSubtitle}>En el periodo seleccionado</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Velocidad Máxima</Text>
            <Text style={styles.statValue}>
              {Math.round(velocityData.max_velocity)} km/h
            </Text>
            <Text style={styles.statSubtitle}>Velocidad registrada</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Velocidad Mínima</Text>
            <Text style={styles.statValue}>
              {Math.round(velocityData.min_velocity)} km/h
            </Text>
            <Text style={styles.statSubtitle}>Velocidad registrada</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Días Analizados</Text>
            <Text style={styles.statValue}>{velocityData.days_analyzed}</Text>
            <Text style={styles.statSubtitle}>Periodo de análisis</Text>
          </View>
        </View>

        {velocityData.velocity_per_day &&
          velocityData.velocity_per_day.length > 0 && (
            <View style={styles.dataTable}>
              <View style={styles.tableHeader}>
                <Text style={styles.tableCellHeader}>Fecha</Text>
                <Text style={styles.tableCellHeader}>Velocidad (km/h)</Text>
              </View>
              {velocityData.velocity_per_day.slice(0, 10).map((day, idx) => (
                <View key={idx} style={styles.tableRow}>
                  <Text style={styles.tableCell}>
                    {new Date(day.day).toLocaleDateString("es-ES")}
                  </Text>
                  <Text style={styles.tableCell}>
                    {Math.round(day.total)}
                  </Text>
                </View>
              ))}
            </View>
          )}
      </>
    );
  };

  const renderVolumeStats = () => {
    if (!volumeData) return null;

    return (
      <>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Cantidad Total de Vehículos</Text>
            <Text style={styles.statValue}>
              {Math.round(volumeData.total_volume)}
            </Text>
            <Text style={styles.statSubtitle}>En el periodo seleccionado</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>
              Promedio de Vehículos por Hora
            </Text>
            <Text style={styles.statValue}>
              {Math.round(volumeData.avg_vehicles_per_hour)}
            </Text>
            <Text style={styles.statSubtitle}>Vehículos/hora</Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Hora Pico de Tráfico</Text>
            <Text style={styles.statValue}>
              {volumeData.rush_hour.hour}:00
            </Text>
            <Text style={styles.statSubtitle}>
              {volumeData.rush_hour.count_vehicles} vehículos
            </Text>
          </View>

          <View style={styles.statCard}>
            <Text style={styles.statTitle}>Días Analizados</Text>
            <Text style={styles.statValue}>{volumeData.days_analyzed}</Text>
            <Text style={styles.statSubtitle}>Periodo de análisis</Text>
          </View>
        </View>

        {volumeData.volume_per_day && volumeData.volume_per_day.length > 0 && (
          <View style={styles.dataTable}>
            <View style={styles.tableHeader}>
              <Text style={styles.tableCellHeader}>Fecha</Text>
              <Text style={styles.tableCellHeader}>Volumen</Text>
            </View>
            {volumeData.volume_per_day.slice(0, 10).map((day, idx) => (
              <View key={idx} style={styles.tableRow}>
                <Text style={styles.tableCell}>
                  {new Date(day.day).toLocaleDateString("es-ES")}
                </Text>
                <Text style={styles.tableCell}>{Math.round(day.total)}</Text>
              </View>
            ))}
          </View>
        )}
      </>
    );
  };

  const getReportTitle = () => {
    switch (trafficType) {
      case "congestion":
        return "Reporte de Congestión de Tráfico";
      case "velocity":
        return "Reporte de Velocidad de Tráfico";
      case "volume":
        return "Reporte de Volumen de Tráfico";
      default:
        return "Reporte de Tráfico";
    }
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{getReportTitle()}</Text>
          <Text style={styles.subtitle}>
            Generado el {currentDate}
          </Text>
        </View>

        {/* Metadata */}
        <View style={styles.metadata}>
          <Text style={styles.metadataText}>
              Ubicación: {locationName?.trim()}
          </Text>
          <Text style={styles.metadataText}>Cámara: {cameraName?.trim()}</Text>
          <Text style={styles.metadataText}>Periodo: {dateRange?.trim()}</Text>
        </View>

        {/* Statistics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Estadísticas del Periodo</Text>
          {trafficType === "congestion" && renderCongestionStats()}
          {trafficType === "velocity" && renderVelocityStats()}
          {trafficType === "volume" && renderVolumeStats()}
        </View>

        {/* Chart */}
        {chartImageUrl && (
          <View style={styles.chartContainer}>
            <Text style={styles.chartTitle}>Gráfica de Tendencia</Text>
            <Text style={styles.chartSubtitle}>{locationName}</Text>
            <Image src={chartImageUrl} style={styles.chartImage} />
          </View>
        )}

        {/* Footer */}
        <Text style={styles.footer}>
          TrafficSmart - Reporte generado automáticamente
        </Text>
      </Page>
    </Document>
  );
};