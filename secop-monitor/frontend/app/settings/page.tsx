"use client";

import { useState } from "react";
import { Save, Plus, X, Mail, Bell, RefreshCw } from "lucide-react";

const DEFAULT_KEYWORDS: Record<string, string[]> = {
  "Meta Ads": [
    "meta ads", "facebook ads", "instagram ads", "pauta digital",
    "publicidad digital", "social ads", "community manager",
  ],
  "Desarrollo Web": [
    "desarrollo web", "pagina web", "sitio web", "landing page",
    "tienda virtual", "e-commerce", "plataforma web", "portal web",
  ],
  "Automatizaciones & IA": [
    "inteligencia artificial", "automatizacion", "machine learning",
    "transformacion digital", "rpa", "big data",
  ],
  Chatbot: [
    "chatbot", "asistente virtual", "whatsapp business", "bot conversacional",
  ],
  "Marketing Digital": [
    "marketing digital", "redes sociales", "seo", "sem",
    "contenido digital", "social media", "branding digital",
  ],
  "Consultoria Digital": [
    "consultoria digital", "asesoria digital", "capacitacion digital",
    "gobierno digital", "tic",
  ],
};

export default function SettingsPage() {
  const [keywords, setKeywords] = useState(DEFAULT_KEYWORDS);
  const [alertEmail, setAlertEmail] = useState("equipo@dtgrowthpartners.com");
  const [alertThreshold, setAlertThreshold] = useState(70);
  const [syncEnabled, setSyncEnabled] = useState(true);
  const [newKeyword, setNewKeyword] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);

  const handleAddKeyword = (category: string) => {
    const kw = newKeyword[category]?.trim().toLowerCase();
    if (!kw || keywords[category].includes(kw)) return;
    setKeywords({
      ...keywords,
      [category]: [...keywords[category], kw],
    });
    setNewKeyword({ ...newKeyword, [category]: "" });
  };

  const handleRemoveKeyword = (category: string, kw: string) => {
    setKeywords({
      ...keywords,
      [category]: keywords[category].filter((k) => k !== kw),
    });
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="text-2xl font-bold">Configuracion</h1>
      <p className="mt-1 text-sm text-[#a3a3a3]">
        Ajusta keywords, notificaciones y sincronizacion
      </p>

      {/* Notifications config */}
      <section className="mt-6 rounded-lg border border-[#262626] bg-[#141414] p-6">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <Mail size={16} className="text-brand-blue" />
          Notificaciones por email
        </h2>

        <div className="mt-4 space-y-4">
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Email de alertas
            </label>
            <input
              type="email"
              value={alertEmail}
              onChange={(e) => setAlertEmail(e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-sm text-[#ededed] focus:border-brand-blue focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 flex items-center justify-between text-xs text-[#a3a3a3]">
              <span className="flex items-center gap-1">
                <Bell size={12} />
                Umbral de alerta (score minimo para enviar email)
              </span>
              <span className="font-mono text-[#ededed]">{alertThreshold}</span>
            </label>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={alertThreshold}
              onChange={(e) => setAlertThreshold(Number(e.target.value))}
              className="w-full accent-brand-blue"
            />
          </div>
        </div>
      </section>

      {/* Sync config */}
      <section className="mt-4 rounded-lg border border-[#262626] bg-[#141414] p-6">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <RefreshCw size={16} className="text-brand-blue" />
          Sincronizacion automatica
        </h2>

        <div className="mt-4 flex items-center justify-between">
          <div>
            <p className="text-sm">Sync automatico SECOP II cada 6 horas</p>
            <p className="text-xs text-[#a3a3a3]">
              SECOP I se sincroniza cada 24 horas
            </p>
          </div>
          <button
            onClick={() => setSyncEnabled(!syncEnabled)}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              syncEnabled ? "bg-brand-blue" : "bg-[#363636]"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                syncEnabled ? "left-[22px]" : "left-0.5"
              }`}
            />
          </button>
        </div>
      </section>

      {/* Keywords editor */}
      <section className="mt-4 rounded-lg border border-[#262626] bg-[#141414] p-6">
        <h2 className="text-sm font-semibold">Keywords por servicio</h2>
        <p className="mt-1 text-xs text-[#a3a3a3]">
          Estas palabras clave se usan como pre-filtro antes de enviar a la IA
        </p>

        <div className="mt-4 space-y-6">
          {Object.entries(keywords).map(([category, kws]) => (
            <div key={category}>
              <h3 className="mb-2 text-xs font-semibold text-brand-blue">
                {category}
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {kws.map((kw) => (
                  <span
                    key={kw}
                    className="flex items-center gap-1 rounded-full bg-[#262626] px-2.5 py-1 text-xs text-[#a3a3a3]"
                  >
                    {kw}
                    <button
                      onClick={() => handleRemoveKeyword(category, kw)}
                      className="text-[#525252] hover:text-red-400"
                    >
                      <X size={10} />
                    </button>
                  </span>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  value={newKeyword[category] || ""}
                  onChange={(e) =>
                    setNewKeyword({ ...newKeyword, [category]: e.target.value })
                  }
                  onKeyDown={(e) =>
                    e.key === "Enter" && handleAddKeyword(category)
                  }
                  placeholder="Agregar keyword..."
                  className="flex-1 rounded border border-[#262626] bg-[#0a0a0a] px-2.5 py-1.5 text-xs text-[#ededed] placeholder-[#525252] focus:border-brand-blue focus:outline-none"
                />
                <button
                  onClick={() => handleAddKeyword(category)}
                  className="flex items-center gap-1 rounded bg-[#262626] px-2.5 py-1.5 text-xs text-[#ededed] hover:bg-[#363636]"
                >
                  <Plus size={12} />
                  Agregar
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Save */}
      <div className="mt-6 flex items-center justify-end gap-3">
        {saved && (
          <span className="text-xs text-green-400">
            Configuracion guardada
          </span>
        )}
        <button
          onClick={handleSave}
          className="flex items-center gap-2 rounded-lg bg-brand-blue px-4 py-2 text-sm font-medium text-white hover:bg-[#2563eb]"
        >
          <Save size={16} />
          Guardar configuracion
        </button>
      </div>
    </div>
  );
}
