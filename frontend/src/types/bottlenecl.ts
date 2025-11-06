export interface BottleneckData {
    ds: string;
    yhat_count: number;
    yhat_speed: number;
    IC: number;
    level: 'Fluido' | 'Denso' | 'Embotellamiento';
}