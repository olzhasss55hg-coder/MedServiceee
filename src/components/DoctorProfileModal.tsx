"use client";

import { useState } from "react";
import { X, Star, Clock, Award, Check } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DoctorModalProps {
  doctor: any;
  isOpen: boolean;
  onClose: () => void;
}

export function DoctorProfileModal({ doctor, isOpen, onClose }: DoctorModalProps) {
  const [isBooked, setIsBooked] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: "", email: "", time: "" });

  const handleClose = () => {
    setIsBooked(false);
    setShowForm(false);
    setFormData({ name: "", email: "", time: "" });
    onClose();
  };

  if (!isOpen || !doctor) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 animate-in fade-in duration-200" onClick={handleClose}>
      <div className="bg-white rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl relative animate-in zoom-in-95 duration-200" onClick={e => e.stopPropagation()}>
        <button onClick={handleClose} className="absolute top-4 right-4 p-2 bg-black/5 rounded-full hover:bg-black/10 transition-colors z-10">
          <X className="w-5 h-5" />
        </button>
        
        <div className="p-6 md:p-8">
          <div className="flex flex-col items-center text-center mb-6">
            <img src={doctor.photo_url || doctor.photo} alt={doctor.first_name || doctor.name} className="w-24 h-24 rounded-full border-4 border-primary/10 mb-4 object-cover" />
            <h2 className="text-2xl font-bold text-foreground">
              {doctor.first_name ? `${doctor.first_name} ${doctor.last_name}` : doctor.name}
            </h2>
            <p className="text-primary font-medium text-lg">{doctor.specialty}</p>
            <div className="flex items-center gap-2 mt-2">
              <div className="flex items-center gap-1 text-sm font-bold bg-amber-500/10 text-amber-600 px-2 py-1 rounded-md">
                <Star className="w-4 h-4 fill-current" /> {doctor.rating}
              </div>
              <span className="text-sm text-muted-foreground">{doctor.reviews_count} отзывов</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-black/5 p-4 rounded-2xl text-center">
              <Award className="w-6 h-6 mx-auto mb-2 text-primary" />
              <p className="text-xs text-muted-foreground mb-1">Стаж работы</p>
              <p className="font-bold">{doctor.experience_years} лет</p>
            </div>
            <div className="bg-black/5 p-4 rounded-2xl text-center">
              <Clock className="w-6 h-6 mx-auto mb-2 text-primary" />
              <p className="text-xs text-muted-foreground mb-1">Стоимость приема</p>
              <p className="font-bold">{(doctor.consultation_price || doctor.price || 0).toLocaleString('ru-RU')} ₸</p>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="font-bold text-lg mb-2">О враче</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              {doctor.description || "Информация о враче не указана."}
            </p>
          </div>

          {showForm && !isBooked && (
            <div className="mb-6 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
              <div>
                <label className="text-sm font-semibold text-muted-foreground mb-1 block">Ваше имя</label>
                <input 
                  type="text" 
                  placeholder="Иван Иванов" 
                  className="w-full h-12 px-4 rounded-xl border border-black/10 bg-black/5 focus:bg-white focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-1 block">Email</label>
                  <input 
                    type="email" 
                    placeholder="example@mail.com" 
                    className="w-full h-12 px-4 rounded-xl border border-black/10 bg-black/5 focus:bg-white focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold text-muted-foreground mb-1 block">Желаемое время</label>
                  <input 
                    type="time" 
                    className="w-full h-12 px-4 rounded-xl border border-black/10 bg-black/5 focus:bg-white focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                    value={formData.time}
                    onChange={e => setFormData({...formData, time: e.target.value})}
                  />
                </div>
              </div>
            </div>
          )}

          <Button 
            className={`w-full h-14 text-lg transition-all ${isBooked ? 'bg-green-500 hover:bg-green-600 text-white' : ''}`}
            onClick={() => {
              if (!showForm && !isBooked) {
                setShowForm(true);
              } else if (showForm && !isBooked) {
                // Here we would typically send an API request to send an email
                setIsBooked(true);
                setShowForm(false);
              }
            }}
            disabled={isBooked || (showForm && (!formData.name || !formData.email || !formData.time))}
          >
            {isBooked ? (
              <span className="flex items-center justify-center gap-2">
                <Check className="w-5 h-5" /> Заявка отправлена
              </span>
            ) : showForm ? (
              "Отправить заявку"
            ) : (
              "Записаться на прием"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
