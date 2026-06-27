"use client";

import { useEffect, useState } from "react";
import DynamicMap from "@/components/ui/DynamicMap";
import { Search, MapPin, Phone, Clock, Navigation, Star } from "lucide-react";
import { Button } from "@/components/ui/Button";
import Link from "next/link";
import { DoctorProfileModal } from "@/components/DoctorProfileModal";
import { useTranslation } from "@/i18n/LanguageContext";

export default function ClinicsPage() {
  const { t, locale } = useTranslation();
  const [clinics, setClinics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCity, setSelectedCity] = useState("Алматы");
  const [selectedClinicId, setSelectedClinicId] = useState<number | null>(null);
  const [expandedClinicId, setExpandedClinicId] = useState<string | null>(null);
  const [clinicDoctors, setClinicDoctors] = useState<Record<string, any[]>>({});
  const [loadingDoctors, setLoadingDoctors] = useState<Record<string, boolean>>({});
  const [selectedDoctor, setSelectedDoctor] = useState<any | null>(null);

  const toggleDoctors = async (clinicId: string) => {
    if (expandedClinicId === clinicId) {
      setExpandedClinicId(null);
      return;
    }
    setExpandedClinicId(clinicId);
    if (!clinicDoctors[clinicId]) {
      setLoadingDoctors(prev => ({...prev, [clinicId]: true}));
      try {
        const res = await fetch(`http://localhost:8000/api/clinics/${clinicId}`);
        if (res.ok) {
          const data = await res.json();
          setClinicDoctors(prev => ({...prev, [clinicId]: data.doctors || []}));
        }
      } catch(e) {}
      setLoadingDoctors(prev => ({...prev, [clinicId]: false}));
    }
  };

  const CITIES = ["Алматы", "Астана", "Шымкент", "Караганда", "Актобе", "Павлодар"];

  useEffect(() => {
    async function fetchClinics() {
      setLoading(true);
      try {
        const url = selectedCity ? `http://localhost:8000/api/clinics?city=${encodeURIComponent(selectedCity)}` : "http://localhost:8000/api/clinics";
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          setClinics(data);
        }
      } catch (err) {
        console.error("Failed to fetch clinics", err);
      } finally {
        setLoading(false);
      }
    }
    fetchClinics();
  }, [selectedCity]);

  return (
    <div className="container mx-auto max-w-[1440px] px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            {locale === 'en' ? 'Clinics on Map' : (locale === 'kk' ? 'Картадағы клиникалар' : 'Клиники на карте')}
          </h1>
          <p className="text-muted-foreground">
            {locale === 'en' ? 'Find the nearest clinic and compare prices' : (locale === 'kk' ? 'Ең жақын клиниканы тауып, бағаларды салыстырыңыз' : 'Найдите ближайшую клинику и сравните цены')}
          </p>
        </div>
        
        <div className="flex gap-3 w-full md:w-auto">
          <select 
            value={selectedCity} 
            onChange={(e) => setSelectedCity(e.target.value)}
            className="px-4 py-2.5 rounded-full border border-border bg-card shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/50 cursor-pointer"
          >
            <option value="">{locale === 'en' ? 'All cities' : (locale === 'kk' ? 'Барлық қалалар' : 'Все города')}</option>
            {CITIES.map(city => (
              <option key={city} value={city}>{city}</option>
            ))}
          </select>
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <input 
              type="text" 
              placeholder={t('clinics.searchPlaceholder')}
              className="w-full pl-10 pr-4 py-2.5 rounded-full border border-border bg-card shadow-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-250px)] min-h-[600px]">
        {/* Sidebar */}
        <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden flex flex-col h-full order-2 lg:order-1">
          <div className="p-4 border-b border-border bg-muted/30">
            <h2 className="font-semibold text-lg">
              {locale === 'en' ? 'Clinics list' : (locale === 'kk' ? 'Клиникалар тізімі' : 'Список клиник')} ({clinics.length})
            </h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {loading ? (
              <div className="p-8 text-center text-muted-foreground">{locale === 'en' ? 'Loading...' : (locale === 'kk' ? 'Жүктелуде...' : 'Загрузка клиник...')}</div>
            ) : clinics.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">{locale === 'en' ? 'No clinics found' : (locale === 'kk' ? 'Клиникалар табылмады' : 'Клиники не найдены')}</div>
            ) : (
              clinics.map((clinic) => (
                <div key={clinic.id} className="p-4 rounded-xl border border-border hover:border-primary/50 hover:bg-muted/30 transition-colors cursor-pointer group">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-medium text-lg group-hover:text-primary transition-colors">{clinic.name}</h3>
                    <div className="flex items-center text-amber-500 text-sm font-medium">
                      <Star className="w-4 h-4 fill-current mr-1" />
                      {clinic.rating || 'N/A'}
                    </div>
                  </div>
                  <div className="space-y-1.5 text-sm text-muted-foreground mt-2">
                    <div className="flex items-start gap-2">
                      <MapPin className="w-4 h-4 mt-0.5 shrink-0" />
                      <span>{clinic.city}, {clinic.address || 'Адрес не указан'}</span>
                    </div>
                    {clinic.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4 shrink-0" />
                        <span>{clinic.phone}</span>
                      </div>
                    )}
                    {clinic.working_hours && (
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 shrink-0" />
                        <span>{clinic.working_hours}</span>
                      </div>
                    )}
                  </div>
                  <div className="mt-4 flex gap-2">
                      <Button size="sm" variant="outline" className="w-full text-xs h-8" onClick={() => setSelectedClinicId(clinic.id)}>
                        {locale === 'en' ? 'Details' : (locale === 'kk' ? 'Толығырақ' : 'Подробнее')}
                      </Button>
                    <Button variant="default" size="sm" className="w-full text-xs bg-primary/10 text-primary hover:bg-primary hover:text-white border-0 shadow-none" onClick={(e) => { e.stopPropagation(); setSelectedClinicId(clinic.id); }}>
                      <Navigation className="w-3 h-3 mr-1" />
                      Маршрут
                    </Button>
                  </div>

                  {/* Expanded Doctors List */}
                  {expandedClinicId === clinic.id && (
                    <div className="mt-4 pt-4 border-t border-border animate-in fade-in slide-in-from-top-2 duration-200">
                      <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3">Врачи клиники</h4>
                      {loadingDoctors[clinic.id] ? (
                        <div className="text-center py-4"><div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div></div>
                      ) : clinicDoctors[clinic.id]?.length > 0 ? (
                        <div className="space-y-3">
                          {clinicDoctors[clinic.id].map(doc => (
                            <div 
                              key={doc.id} 
                              onClick={(e) => { e.stopPropagation(); setSelectedDoctor(doc); }}
                              className="flex gap-3 p-3 bg-muted/30 rounded-xl cursor-pointer hover:bg-muted/50 transition-colors"
                            >
                              <img src={doc.photo_url} alt={doc.first_name} className="w-10 h-10 rounded-full bg-white object-cover shrink-0" />
                              <div className="flex-1">
                                <h6 className="text-sm font-bold">{doc.first_name} {doc.last_name}</h6>
                                <p className="text-xs text-primary mb-1">{doc.specialty}</p>
                                <div className="flex justify-between items-center text-xs">
                                  <span className="text-muted-foreground">{doc.experience_years} лет</span>
                                  <span className="font-semibold">{doc.consultation_price} ₸</span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-4 text-xs text-muted-foreground">Нет информации о врачах</div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Map */}
        <div className="lg:col-span-2 rounded-2xl overflow-hidden border border-border shadow-sm h-[400px] lg:h-full order-1 lg:order-2 z-0 relative">
          <DynamicMap clinics={clinics} selectedClinicId={selectedClinicId} />
        </div>
      </div>
      <DoctorProfileModal 
        doctor={selectedDoctor} 
        isOpen={selectedDoctor !== null} 
        onClose={() => setSelectedDoctor(null)} 
      />
    </div>
  );
}
