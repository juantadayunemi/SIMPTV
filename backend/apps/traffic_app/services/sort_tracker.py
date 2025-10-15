"""
SORT (Simple Online and Realtime Tracking) Tracker
Implementación ligera y rápida para YOLOv5

Basado en: https://github.com/abewley/sort
Optimizado para tracking de vehículos en tiempo real

Características:
- Kalman Filter para predicción de movimiento
- Hungarian Algorithm para asociación de detecciones
- IOU-based matching (rápido y eficiente)
- Re-ID básico por posición

Rendimiento:
- ~1-2ms por frame (muy rápido)
- Funciona bien con YOLOv5 (20-35ms + 1-2ms = 21-37ms total)
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter


class KalmanBoxTracker:
    """
    Tracker de un solo objeto usando Kalman Filter
    
    Estado: [x, y, s, r, vx, vy, vs]
    - x, y: centro del bbox
    - s: área (scale)
    - r: aspect ratio
    - vx, vy, vs: velocidades
    """
    
    count = 0  # Contador global de IDs
    
    def __init__(self, bbox, class_id=None):
        """
        Inicializa tracker con detección inicial
        
        Args:
            bbox: [x1, y1, x2, y2] o [x1, y1, x2, y2, score] (formato YOLO)
            class_id: ID de clase YOLO (2=car, 3=moto, 5=bus, 7=truck)
        """
        # Guardar clase original de YOLOv5
        self.class_id = class_id
        # Kalman Filter de 7 dimensiones
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        
        # Matriz de transición (movimiento constante)
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1]
        ])
        
        # Matriz de observación (solo medimos posición)
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0]
        ])
        
        # Ruido de medición (baja incertidumbre en detecciones YOLO)
        self.kf.R[2:, 2:] *= 10.
        
        # Covarianza inicial (alta para velocidades desconocidas)
        self.kf.P[4:, 4:] *= 1000.
        self.kf.P *= 10.
        
        # Ruido de proceso (movimiento suave)
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01
        
        # Estado inicial
        self.kf.x[:4] = self._convert_bbox_to_z(bbox)
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
    
    def update(self, bbox):
        """
        Actualiza el tracker con nueva detección
        
        Args:
            bbox: [x1, y1, x2, y2]
        """
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        self.kf.update(self._convert_bbox_to_z(bbox))
    
    def predict(self):
        """
        Predice estado siguiente (Kalman prediction)
        
        Returns:
            bbox predicho [x1, y1, x2, y2]
        """
        # Evitar área negativa
        if self.kf.x[6] + self.kf.x[2] <= 0:
            self.kf.x[6] *= 0.0
        
        self.kf.predict()
        self.age += 1
        
        if self.time_since_update > 0:
            self.hit_streak = 0
        
        self.time_since_update += 1
        self.history.append(self._convert_x_to_bbox(self.kf.x))
        
        return self.history[-1]
    
    def get_state(self):
        """
        Retorna estado actual como bbox
        
        Returns:
            [x1, y1, x2, y2]
        """
        return self._convert_x_to_bbox(self.kf.x)
    
    @staticmethod
    def _convert_bbox_to_z(bbox):
        """
        Convierte [x1, y1, x2, y2] a [x, y, s, r]
        
        Args:
            bbox: [x1, y1, x2, y2]
            
        Returns:
            [x, y, s, r] para Kalman
        """
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = bbox[0] + w / 2.
        y = bbox[1] + h / 2.
        s = w * h  # área
        r = w / float(h + 1e-6)  # aspect ratio
        return np.array([x, y, s, r]).reshape((4, 1))
    
    @staticmethod
    def _convert_x_to_bbox(x, score=None):
        """
        Convierte estado Kalman [x, y, s, r] a [x1, y1, x2, y2]
        
        Args:
            x: Estado Kalman [x, y, s, r, vx, vy, vs]
            score: Confianza (opcional)
            
        Returns:
            [x1, y1, x2, y2] o [x1, y1, x2, y2, score]
        """
        w = np.sqrt(x[2] * x[3])
        h = x[2] / (w + 1e-6)
        
        if score is None:
            return np.array([
                x[0] - w / 2.,
                x[1] - h / 2.,
                x[0] + w / 2.,
                x[1] + h / 2.
            ]).reshape((1, 4))
        else:
            return np.array([
                x[0] - w / 2.,
                x[1] - h / 2.,
                x[0] + w / 2.,
                x[1] + h / 2.,
                score
            ]).reshape((1, 5))


def iou_batch(bboxes1, bboxes2):
    """
    Calcula IOU entre dos listas de bboxes
    
    Args:
        bboxes1: (N, 4) [x1, y1, x2, y2]
        bboxes2: (M, 4) [x1, y1, x2, y2]
        
    Returns:
        (N, M) matriz de IOUs
    """
    bboxes2 = np.expand_dims(bboxes2, 0)
    bboxes1 = np.expand_dims(bboxes1, 1)
    
    # Coordenadas de intersección
    xx1 = np.maximum(bboxes1[..., 0], bboxes2[..., 0])
    yy1 = np.maximum(bboxes1[..., 1], bboxes2[..., 1])
    xx2 = np.minimum(bboxes1[..., 2], bboxes2[..., 2])
    yy2 = np.minimum(bboxes1[..., 3], bboxes2[..., 3])
    
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    
    intersection = w * h
    
    # Áreas
    area1 = (bboxes1[..., 2] - bboxes1[..., 0]) * (bboxes1[..., 3] - bboxes1[..., 1])
    area2 = (bboxes2[..., 2] - bboxes2[..., 0]) * (bboxes2[..., 3] - bboxes2[..., 1])
    
    union = area1 + area2 - intersection
    
    iou = intersection / (union + 1e-6)
    
    return iou


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """
    Asocia detecciones a trackers usando Hungarian Algorithm
    
    Args:
        detections: (N, 5) [x1, y1, x2, y2, score]
        trackers: (M, 5) [x1, y1, x2, y2, id]
        iou_threshold: Umbral mínimo de IOU
        
    Returns:
        matches: (K, 2) pares [det_idx, trk_idx]
        unmatched_detections: (P,) índices de detecciones sin match
        unmatched_trackers: (Q,) índices de trackers sin match
    """
    if len(trackers) == 0:
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0,), dtype=int)
    
    # Calcular matriz de IOU
    iou_matrix = iou_batch(detections, trackers)
    
    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            # Matching simple (1-to-1)
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            # Hungarian Algorithm (optimal assignment)
            matched_indices = linear_sum_assignment(-iou_matrix)
            matched_indices = np.array(list(zip(*matched_indices)))
    else:
        matched_indices = np.empty(shape=(0, 2))
    
    # Filtrar matches con IOU < threshold
    matches = []
    for m in matched_indices:
        if iou_matrix[m[0], m[1]] < iou_threshold:
            continue
        matches.append(m.reshape(1, 2))
    
    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)
    
    # Detecciones sin match
    unmatched_detections = []
    for d in range(len(detections)):
        if d not in matches[:, 0]:
            unmatched_detections.append(d)
    
    # Trackers sin match
    unmatched_trackers = []
    for t in range(len(trackers)):
        if t not in matches[:, 1]:
            unmatched_trackers.append(t)
    
    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort:
    """
    SORT Tracker (Simple Online and Realtime Tracking)
    
    Tracking multi-objeto rápido y eficiente para YOLOv5
    
    Args:
        max_age: Frames máximos sin detección antes de eliminar tracker
        min_hits: Hits mínimos antes de confirmar tracker
        iou_threshold: Umbral IOU para matching
    """
    
    def __init__(self, max_age=150, min_hits=3, iou_threshold=0.3):
        """
        Args:
            max_age: Frames sin detección antes de eliminar (150 = 5 seg @ 30fps)
            min_hits: Detecciones necesarias para confirmar tracker
            iou_threshold: Umbral IOU para matching (0.3 = balance)
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0
    
    def update(self, detections, class_ids=None):
        """
        Actualiza trackers con nuevas detecciones
        
        Args:
            detections: (N, 5) [x1, y1, x2, y2, score]
            class_ids: (N,) array de class IDs de YOLOv5 (opcional)
            
        Returns:
            (M, 6) [x1, y1, x2, y2, track_id, class_id] de objetos confirmados
        """
        self.frame_count += 1
        
        # Predecir posiciones
        trks = np.zeros((len(self.trackers), 5))
        to_del = []
        
        for t, trk in enumerate(trks):
            pos = self.trackers[t].predict()[0]
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(t)
        
        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        
        # Eliminar trackers con NaN
        for t in reversed(to_del):
            self.trackers.pop(t)
        
        # Asociar detecciones con trackers
        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(
            detections, trks, self.iou_threshold
        )
        
        # Actualizar matched trackers (mantener clase original)
        for m in matched:
            self.trackers[m[1]].update(detections[m[0], :])
            # Actualizar clase si se proporciona (puede cambiar con mejor detección)
            if class_ids is not None and m[0] < len(class_ids):
                self.trackers[m[1]].class_id = class_ids[m[0]]
        
        # Crear nuevos trackers para detecciones sin match
        for i in unmatched_dets:
            class_id = class_ids[i] if class_ids is not None and i < len(class_ids) else None
            trk = KalmanBoxTracker(detections[i, :], class_id=class_id)
            self.trackers.append(trk)
        
        # Retornar trackers confirmados con clase
        ret = []
        i = len(self.trackers)
        
        for trk in reversed(self.trackers):
            d = trk.get_state()[0]
            
            # Solo retornar trackers confirmados (min_hits)
            if (trk.time_since_update < 1) and (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits):
                # Retornar: [x1, y1, x2, y2, track_id, class_id]
                track_id = trk.id + 1  # +1 para IDs desde 1
                class_id = trk.class_id if trk.class_id is not None else -1
                ret.append(np.concatenate((d, [track_id, class_id])).reshape(1, -1))
            
            i -= 1
            
            # Eliminar trackers perdidos
            if trk.time_since_update > self.max_age:
                self.trackers.pop(i)
        
        if len(ret) > 0:
            return np.concatenate(ret)
        
        return np.empty((0, 6))  # 6 columnas: [x1, y1, x2, y2, track_id, class_id]
