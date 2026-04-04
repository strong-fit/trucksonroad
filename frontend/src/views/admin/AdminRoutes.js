"use client";
import { useState, useEffect, useRef } from 'react';
import { AdminLayout } from '@/pages/admin/AdminDashboard';
import { useLanguage } from '@/contexts/LanguageContext';
import api from '@/lib/api';
import { toast } from 'sonner';
import { MapPin, Navigation, Clock, Route, Search } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const baseIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
  className: 'leaflet-marker-base',
});

function FitBounds({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length > 0) map.fitBounds(bounds, { padding: [40, 40] });
  }, [bounds, map]);
  return null;
}

export default function AdminRoutes() {
  const { t } = useLanguage();
  const [mapData, setMapData] = useState({ events: [], base: { lat: 47.3231, lon: 8.7994 } });
  const [routeGeo, setRouteGeo] = useState(null);
  const [routeInfo, setRouteInfo] = useState(null);
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [geocodeQuery, setGeocodeQuery] = useState('');
  const [geocoding, setGeocoding] = useState(false);

  useEffect(() => {
    api.get('/admin/events-map').then(r => setMapData(r.data)).catch(() => {});
  }, []);

  const eventsWithCoords = mapData.events.filter(e => e.lat && e.lon);
  const eventsWithoutCoords = mapData.events.filter(e => !e.lat || !e.lon);

  const bounds = eventsWithCoords.length > 0
    ? [[mapData.base.lat, mapData.base.lon], ...eventsWithCoords.map(e => [e.lat, e.lon])]
    : [[mapData.base.lat, mapData.base.lon]];

  const geocodeEvent = async (eventId, address) => {
    setGeocoding(true);
    try {
      const r = await api.get(`/admin/geocode?address=${encodeURIComponent(address)}`);
      if (r.data.found) {
        await api.put(`/admin/inquiries/${eventId}/coords`, { lat: r.data.lat, lon: r.data.lon });
        toast.success('Koordinaten gespeichert');
        const mr = await api.get('/admin/events-map');
        setMapData(mr.data);
      } else {
        toast.error('Adresse nicht gefunden');
      }
    } catch { toast.error('Fehler bei der Geocodierung'); }
    setGeocoding(false);
  };

  const toggleEvent = (id) => {
    setSelectedEvents(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const calculateRoute = async () => {
    if (selectedEvents.length === 0) { toast.error('Mindestens 1 Event auswaehlen'); return; }
    const selected = eventsWithCoords.filter(e => selectedEvents.includes(e.id));
    if (selected.length === 0) { toast.error('Ausgewaehlte Events haben keine Koordinaten'); return; }
    try {
      if (selected.length === 1) {
        const e = selected[0];
        const r = await api.get(`/admin/route?from_lat=${mapData.base.lat}&from_lon=${mapData.base.lon}&to_lat=${e.lat}&to_lon=${e.lon}`);
        if (r.data.found) {
          setRouteGeo(r.data.geometry.coordinates.map(c => [c[1], c[0]]));
          setRouteInfo({ distance_km: r.data.distance_km, duration_min: r.data.duration_min });
        }
      } else {
        const coords = [`${mapData.base.lon},${mapData.base.lat}`, ...selected.map(e => `${e.lon},${e.lat}`)].join(';');
        const r = await api.get(`/admin/route/optimize?coords=${coords}`);
        if (r.data.found) {
          setRouteGeo(r.data.geometry.coordinates.map(c => [c[1], c[0]]));
          setRouteInfo({ distance_km: r.data.distance_km, duration_min: r.data.duration_min });
          toast.success('Optimierte Route berechnet');
        }
      }
    } catch { toast.error('Routenberechnung fehlgeschlagen'); }
  };

  const clearRoute = () => { setRouteGeo(null); setRouteInfo(null); setSelectedEvents([]); };

  const statusColors = { confirmed: '#22c55e', offer_sent: '#a855f7', in_review: '#eab308' };

  return (
    <AdminLayout title={t('admin_routes')}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '1.25rem', alignItems: 'start' }}>
        {/* Map */}
        <div className="adm-detail" style={{ padding: 0, overflow: 'hidden', height: '520px' }} data-testid="route-map">
          <MapContainer center={[mapData.base.lat, mapData.base.lon]} zoom={9} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
            <FitBounds bounds={bounds} />
            {/* Base marker */}
            <Marker position={[mapData.base.lat, mapData.base.lon]} icon={baseIcon}>
              <Popup><strong>TRUCKSonROAD</strong><br/>Wetzikon (Basis)</Popup>
            </Marker>
            {/* Event markers */}
            {eventsWithCoords.map(e => (
              <Marker key={e.id} position={[e.lat, e.lon]}>
                <Popup>
                  <strong>{e.name}</strong><br/>
                  {e.event_date}<br/>
                  {e.location}<br/>
                  <span style={{ fontSize: '0.75rem', color: statusColors[e.status] }}>{e.status}</span>
                </Popup>
              </Marker>
            ))}
            {/* Route polyline */}
            {routeGeo && <Polyline positions={routeGeo} color="#4db6ac" weight={4} opacity={0.8} />}
          </MapContainer>
        </div>

        {/* Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Route info */}
          {routeInfo && (
            <div className="adm-detail" data-testid="route-info">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span className="adm-detail-title" style={{ fontSize: '1rem' }}>Route</span>
                <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={clearRoute}>Zuruecksetzen</button>
              </div>
              <div style={{ display: 'flex', gap: '1.5rem' }}>
                <div>
                  <div className="adm-form-label">Distanz</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 600 }} data-testid="route-distance">{routeInfo.distance_km} km</div>
                </div>
                <div>
                  <div className="adm-form-label">Fahrzeit</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 600 }} data-testid="route-duration">
                    {routeInfo.duration_min >= 60 ? `${Math.floor(routeInfo.duration_min / 60)}h ${routeInfo.duration_min % 60}min` : `${routeInfo.duration_min} min`}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Event selection */}
          <div className="adm-detail" data-testid="route-events-panel">
            <div className="adm-detail-title" style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>Events ({eventsWithCoords.length} mit Koordinaten)</div>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <button className="adm-btn adm-btn-primary adm-btn-sm" onClick={calculateRoute} disabled={selectedEvents.length === 0} data-testid="calc-route-btn">
                <Route size={13} /> Route berechnen
              </button>
            </div>
            <div style={{ maxHeight: '250px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
              {eventsWithCoords.map(e => (
                <label key={e.id} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', padding: '0.4rem 0.5rem', background: selectedEvents.includes(e.id) ? 'var(--adm-hover)' : 'transparent', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}>
                  <input type="checkbox" checked={selectedEvents.includes(e.id)} onChange={() => toggleEvent(e.id)} style={{ marginTop: '0.15rem' }} />
                  <div>
                    <div style={{ fontWeight: 500 }}>{e.name}</div>
                    <div style={{ color: 'var(--adm-text-muted)', fontSize: '0.72rem' }}>{e.event_date} - {e.location}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Events without coordinates */}
          {eventsWithoutCoords.length > 0 && (
            <div className="adm-detail" data-testid="events-no-coords">
              <div className="adm-detail-title" style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: 'var(--adm-text-muted)' }}>Ohne Koordinaten ({eventsWithoutCoords.length})</div>
              <div style={{ maxHeight: '180px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {eventsWithoutCoords.map(e => (
                  <div key={e.id} className="adm-block-item" style={{ padding: '0.5rem 0.6rem' }}>
                    <div style={{ fontSize: '0.78rem' }}>
                      <strong>{e.name}</strong> - {e.location || 'Kein Ort'}
                    </div>
                    <button className="adm-btn adm-btn-secondary adm-btn-sm" onClick={() => geocodeEvent(e.id, e.location)} disabled={geocoding || !e.location} data-testid={`geocode-${e.id}`} style={{ padding: '0.2rem 0.5rem', fontSize: '0.68rem' }}>
                      <MapPin size={11} /> Finden
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
}
