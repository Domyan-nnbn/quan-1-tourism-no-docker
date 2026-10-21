# Adaptive geofence 1.3.4

Run `npm.cmd run db:migrate` before starting backend/worker. Back up PostgreSQL first.

Admin > Địa điểm > edit: select circle or polygon. For polygon, paste JSON vertices in `[latitude,longitude]` order. Use public visitor-accessible boundary, not building property outline. The backend validates polygon size and shape. For circles, radius remains in metres. Configure exit buffer, dwell seconds and GPS accuracy per POI.

Mobile only automatically triggers when the application is foregrounded, a recent GPS fix is accurate enough, and the entire GPS uncertainty radius is inside the polygon or circle. A per-POI dwell is required; after a trigger, re-arm only after exiting beyond the configured buffer and cooldown. One closest qualifying POI wins. Manual playback is unchanged. These safeguards reduce false positives but do not guarantee GPS accuracy in dense urban areas.

For existing POIs, the migration defaults to circle, 20m exit buffer, 10s dwell and 25m maximum GPS accuracy. Test each POI outdoors with a real Android phone; polygon boundaries are NOT pre-populated automatically. Existing API clients omitting new fields use defaults, so legacy clients should be upgraded before editing configured polygons to avoid resetting them.
