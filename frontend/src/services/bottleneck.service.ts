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

