"use client"

import Link from "next/link"
import { Search, Heart, User, Map as MapIcon, Menu, LogOut } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "@/i18n/LanguageContext"
import { Locale } from "@/i18n/dictionaries"

export function Navbar() {
  const { t, locale, setLocale } = useTranslation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    router.push("/");
    router.refresh();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/40 bg-white/70 backdrop-blur-md">
      <div className="container mx-auto max-w-[1440px] px-4 h-20 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-xl shadow-sm">
              M
            </div>
            <span className="font-bold text-xl tracking-tight hidden sm:inline-block">
              MedService<span className="text-primary">Price</span>
            </span>
          </Link>

          <nav className="hidden lg:flex items-center gap-6 text-sm font-medium text-muted-foreground">
            <Link href="/search" className="hover:text-primary transition-colors">{t('navbar.services')}</Link>
            <Link href="/clinics" className="hover:text-primary transition-colors">{t('navbar.clinics')}</Link>
            <Link href="/promotions" className="hover:text-primary transition-colors">{t('navbar.promotions')}</Link>
            <Link href="/about" className="hover:text-primary transition-colors">{t('navbar.about')}</Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-3 mr-2">
            <Link href="/search">
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-black/5">
                <Search className="w-5 h-5" />
              </Button>
            </Link>
            <Link href="/favorites">
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-black/5 text-rose-500 hover:text-rose-600 hover:bg-rose-50">
                <Heart className="w-5 h-5" />
              </Button>
            </Link>
          </div>
          
          <div className="flex gap-1 ml-2 mr-2">
            <button onClick={() => setLocale('ru')} className={`text-xs font-semibold px-2 py-1 rounded transition-colors ${locale === 'ru' ? 'bg-primary text-white' : 'text-zinc-500 hover:bg-zinc-100'}`}>RU</button>
            <button onClick={() => setLocale('kk')} className={`text-xs font-semibold px-2 py-1 rounded transition-colors ${locale === 'kk' ? 'bg-primary text-white' : 'text-zinc-500 hover:bg-zinc-100'}`}>KK</button>
            <button onClick={() => setLocale('en')} className={`text-xs font-semibold px-2 py-1 rounded transition-colors ${locale === 'en' ? 'bg-primary text-white' : 'text-zinc-500 hover:bg-zinc-100'}`}>EN</button>
          </div>

          <Link href="/for-clinics" className="hidden sm:flex">
            <Button variant="outline" className="rounded-full">
              {t('navbar.forClinics')}
            </Button>
          </Link>
          {isAuthenticated ? (
            <Button onClick={handleLogout} variant="outline" className="rounded-full border-zinc-200 hover:bg-zinc-100">
              <LogOut className="w-4 h-4 mr-2 text-zinc-600" />
              <span className="text-zinc-800">{t('navbar.logout')}</span>
            </Button>
          ) : (
            <Link href="/login">
              <Button className="rounded-full shadow-glow">
                <User className="w-4 h-4 mr-2" />
                {t('navbar.login')}
              </Button>
            </Link>
          )}
          
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
            <Menu className="w-6 h-6" />
          </Button>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="lg:hidden absolute top-20 left-0 w-full bg-white border-b border-black/10 shadow-lg py-4 px-4 flex flex-col gap-4 z-40">
          <Link href="/search" className="text-lg font-medium" onClick={() => setIsMobileMenuOpen(false)}>{t('navbar.services')}</Link>
          <Link href="/clinics" className="text-lg font-medium" onClick={() => setIsMobileMenuOpen(false)}>{t('navbar.clinics')}</Link>
          <Link href="/promotions" className="text-lg font-medium" onClick={() => setIsMobileMenuOpen(false)}>{t('navbar.promotions')}</Link>
          <Link href="/about" className="text-lg font-medium" onClick={() => setIsMobileMenuOpen(false)}>{t('navbar.about')}</Link>
          <Link href="/for-clinics" className="text-lg font-medium sm:hidden" onClick={() => setIsMobileMenuOpen(false)}>{t('navbar.forClinics')}</Link>
        </div>
      )}
    </header>
  )
}
