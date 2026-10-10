import { POI, Position } from './types';
export function distance(a: Position, b: Position): number {
  const rad = Math.PI / 180;
  const x = Math.sin((b.latitude-a.latitude)*rad/2)**2 + Math.cos(a.latitude*rad)*Math.cos(b.latitude*rad)*Math.sin((b.longitude-a.longitude)*rad/2)**2;
  return 6371000 * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(Math.max(0,1-x)));
}
// Candidate must remain inside for 3s; do not repeatedly read while standing still.
export class GeofenceEngine {
  private candidate: string | null = null;
  private since = 0;
  private cooldown = new Map<string, number>();
  private visited = new Set<string>();
  resetCandidate() { this.candidate=null; this.since=0; }
  suppress(id: string, time: number) { this.cooldown.set(id,time); this.visited.add(id); }
  update(position: Position, pois: POI[], time: number): POI | null {
    if (position.accuracy != null && position.accuracy > 50) { this.resetCandidate(); return null; }
    for (const p of pois) if (distance(position,p) > p.radius+20) this.visited.delete(p.id);
    const nearest = pois.filter(p => p.content && distance(position,p)<=p.radius)
      .sort((a,b)=>distance(position,a)-distance(position,b))[0];
    if (!nearest || this.visited.has(nearest.id) || time-(this.cooldown.get(nearest.id)??-Infinity)<300000) { this.resetCandidate();return null; }
    if (this.candidate!==nearest.id) { this.candidate=nearest.id;this.since=time;return null; }
    if (time-this.since<3000) return null;
    this.suppress(nearest.id,time);this.resetCandidate();return nearest;
  }
}
