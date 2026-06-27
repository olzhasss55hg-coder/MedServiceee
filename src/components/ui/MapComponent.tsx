"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useTranslation } from "@/i18n/LanguageContext";

// Fix leaflet marker icon issues in next.js
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapComponentProps {
  clinics: any[];
  selectedClinicId?: number | null;
}

export default function MapComponent({ clinics, selectedClinicId }: MapComponentProps) {
  const { locale } = useTranslation();
  const mapRef = useRef<HTMLDivElement>(null);
  const leafletMap = useRef<L.Map | null>(null);
  const markersRef = useRef(new Map<number, {lat: number, lng: number, marker: L.Marker}>());

  useEffect(() => {
    if (!mapRef.current) return;

    // Default to Almaty coordinates if no clinics have coords
    let center: [number, number] = [43.238949, 76.889709]; 
    if (clinics.length > 0) {
      const withCoords = clinics.filter(c => c.latitude && c.longitude);
      if (withCoords.length > 0) {
        center = [withCoords[0].latitude, withCoords[0].longitude];
      }
    }

    if (!leafletMap.current) {
      leafletMap.current = L.map(mapRef.current).setView(center, 12);
      
      L.tileLayer('http://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
        attribution: '&copy; Google Maps'
      }).addTo(leafletMap.current);
    }

    // Clear existing markers
    leafletMap.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        leafletMap.current?.removeLayer(layer);
      }
    });

    // Add markers for clinics
    clinics.forEach(clinic => {
      // If we don't have real coordinates in DB, just place them slightly randomly around Almaty for MVP demonstration
      // In a real app we'd fetch actual geocodes. The TZ allows MVP assumptions.
      const lat = clinic.latitude || 43.238949 + (Math.random() - 0.5) * 0.1;
      const lng = clinic.longitude || 76.889709 + (Math.random() - 0.5) * 0.1;
      
      const noAddress = locale === 'en' ? 'Address not specified' : (locale === 'kk' ? 'Мекенжай көрсетілмеген' : 'Адрес не указан');
      const noRating = locale === 'en' ? 'No ratings' : (locale === 'kk' ? 'Бағалау жоқ' : 'Нет оценок');
      const reviewsStr = locale === 'en' ? 'rev.' : (locale === 'kk' ? 'пікір' : 'отз.');
      const detailsStr = locale === 'en' ? 'Details' : (locale === 'kk' ? 'Толығырақ' : 'Подробнее');

      const marker = L.marker([lat, lng], { icon }).addTo(leafletMap.current!);
      const popupContent = `
        <div style="font-family: sans-serif; min-width: 150px;">
          <h4 style="margin: 0 0 4px 0; font-size: 14px;">${clinic.name}</h4>
          <div style="color: #666; font-size: 12px; margin-bottom: 4px;">
            ${clinic.city}, ${clinic.address || noAddress}
          </div>
          <div style="color: #f59e0b; font-size: 12px; margin-bottom: 8px;">
            ★ ${clinic.rating || noRating} (${clinic.reviews_count || 0} ${reviewsStr})
          </div>
          <a href="/clinics/${clinic.id}" style="display: block; background: #2563eb; color: white; text-align: center; padding: 4px 0; border-radius: 4px; text-decoration: none; font-size: 12px;">${detailsStr}</a>
        </div>
      `;
      marker.bindPopup(popupContent);
      markersRef.current.set(clinic.id, { lat, lng, marker });
    });

    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove();
        leafletMap.current = null;
      }
    };
  }, [clinics]);

  useEffect(() => {
    if (selectedClinicId && leafletMap.current) {
      const data = markersRef.current.get(selectedClinicId);
      if (data) {
        leafletMap.current.flyTo([data.lat, data.lng], 16, { animate: true, duration: 1.5 });
        data.marker.openPopup();
      }
    }
  }, [selectedClinicId]);

  return <div ref={mapRef} className="w-full h-full min-h-[400px] rounded-xl z-0 relative" />;
}
