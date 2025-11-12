import api from "./api";
import { BottleneckData } from "@/types/bottlenecl";

export const getBottleneckData = async (
  locationId: string,
  selectedCamera: string,
  date: string,
  hour: string,
  minute: string,
):Promise<BottleneckData[]>=>{
  const resp = await api.get(
    `api/predictions/bottleneck-traffic/?locationId=${locationId}&cameraId=${selectedCamera}&date=${date}&hour=${hour}&minute=${minute}&periodsType=monthly`

);
  return resp.data
}

export const NotificationBottleneck = async (
  locationId: string,
  selectedCamera: string,
): Promise<void> => {
  const resp = await api.post(
    `api/predictions/togle-notifications-bottleneck/toggle/`,
    {
      locationId: Number(locationId),
      cameraId: Number(selectedCamera),
    }
  )
  return resp.data
};
  
export const getNotificationBottleneck = async (
  locationId: string,
  selectedCamera: string,
): Promise<any> => {
  const resp = await api.get(
    `api/predictions/togle-notifications-bottleneck/?locationId=${locationId}&cameraId=${selectedCamera}`
  )
  return resp.data
}

