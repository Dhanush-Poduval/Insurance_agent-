import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { CloudSun, Wind, Droplets, Thermometer, MapPin, Info, ZoomIn, ZoomOut, RotateCcw, RefreshCw } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { GlowCard } from './ui/spotlight-card';
import AnimatedList from './ui/animated-list';
import { evaluateAllZones, TriggerEvaluationResult } from '@/src/lib/api';

interface ZoneData {
  id: string;
  name: string;
  aqi: number;
  temp: number;
  rainfall: string;
  status: 'safe' | 'warning' | 'danger';
  coordinates: { x: number; y: number };
}

// Map backend zone_id keys to display names and map positions
const ZONE_META: Record<string, { name: string; coordinates: { x: number; y: number } }> = {
  zone_mumbai_01:    { name: 'Mumbai',    coordinates: { x: 35, y: 72 } },
  zone_delhi_01:     { name: 'Delhi',     coordinates: { x: 48, y: 30 } },
  zone_bangalore_02: { name: 'Bangalore', coordinates: { x: 45, y: 80 } },
  zone_hyderabad_01: { name: 'Hyderabad', coordinates: { x: 50, y: 65 } },
};

/** Convert a backend TriggerEvaluationResult into the UI ZoneData shape */
function mapZoneResult(result: any): ZoneData | null {
  const meta = ZONE_META[result.zone_id];
  if (!meta) return null;

  const weather = result.weather ?? {};
  const aqi: number = typeof weather.aqi === 'number' ? weather.aqi : 100;
  const temp: number = typeof weather.temperature === 'number' ? weather.temperature : 25;
  const rainfallMm: number = typeof weather.rainfall === 'number' ? weather.rainfall : 0;

  // Derive UI status from triggers
  let status: 'safe' | 'warning' | 'danger';
  if (result.payout_triggered || aqi > 300) {
    status = 'danger';
  } else if (aqi > 200 || rainfallMm > 5) {
    status = 'warning';
  } else {
    status = 'safe';
  }

  return {
    id: result.zone_id,
    name: meta.name,
    aqi,
    temp,
    rainfall: `${rainfallMm.toFixed(1)}mm`,
    status,
    coordinates: meta.coordinates,
  };
}

export function WeatherMap() {
  const [zones, setZones] = useState<ZoneData[]>([]);
  const [selectedZone, setSelectedZone] = useState<ZoneData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewState, setViewState] = useState({ scale: 1, x: 0, y: 0 });
  const mapRef = useRef<HTMLDivElement>(null);

  const fetchZones = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await evaluateAllZones();
      const mapped = (data.zones ?? [])
        .map(mapZoneResult)
        .filter(Boolean) as ZoneData[];
      setZones(mapped);
      // Auto-select first zone on first load, preserve selection otherwise
      setSelectedZone(prev => {
        if (!prev && mapped.length > 0) return mapped[0];
        // Refresh selected zone data if it was already selected
        if (prev) {
          const updated = mapped.find(z => z.id === prev.id);
          return updated ?? prev;
        }
        return prev;
      });
    } catch (err: any) {
      setError(err?.message ?? 'Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on mount and refresh every 5 minutes
  useEffect(() => {
    fetchZones();
    const interval = setInterval(fetchZones, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchZones]);

  const handleZoom = (delta: number) => {
    setViewState(prev => ({
      ...prev,
      scale: Math.max(1, Math.min(prev.scale + delta, 3))
    }));
  };

  const resetView = () => {
    setViewState({ scale: 1, x: 0, y: 0 });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':    return 'text-green-500 bg-green-500/10 border-green-500/20';
      case 'warning': return 'text-saffron bg-saffron/10 border-saffron/20';
      case 'danger':  return 'text-red-500 bg-red-500/10 border-red-500/20';
      default:        return 'text-gray-500';
    }
  };

  const getGlowColor = (aqi: number) => {
    if (aqi > 300) return 'red';
    if (aqi > 200) return 'orange';
    return 'green';
  };

  const zoneNames = zones.map(z => z.name);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Sidebar List */}
      <div className="lg:col-span-1 space-y-4">
        <div className="p-4 bg-card/30 rounded-2xl border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <p className="text-[10px] font-bold text-text-secondary uppercase tracking-widest">Select Zone</p>
            <button
              onClick={fetchZones}
              disabled={loading}
              className="p-1.5 rounded-lg hover:bg-white/10 transition-colors text-text-secondary hover:text-white"
              title="Refresh weather data"
            >
              <RefreshCw className={cn("w-3.5 h-3.5", loading && "animate-spin")} />
            </button>
          </div>

          {loading && zones.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-text-secondary text-xs gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Loading live weather…</span>
            </div>
          ) : error ? (
            <div className="py-4 text-center">
              <p className="text-red-400 text-xs mb-2">{error}</p>
              <button
                onClick={fetchZones}
                className="text-xs text-saffron hover:underline"
              >
                Retry
              </button>
            </div>
          ) : (
            <AnimatedList
              items={zoneNames}
              itemClassName="!bg-white/5 !border-white/5 hover:!bg-white/10"
              displayScrollbar={false}
              initialSelectedIndex={0}
              onItemSelect={(name) => {
                const zone = zones.find(z => z.name === name);
                if (zone) setSelectedZone(zone);
              }}
            />
          )}
        </div>

        {/* Legend */}
        <div className="p-6 bg-card/30 backdrop-blur-sm rounded-2xl border border-white/5">
          <p className="text-[10px] font-bold text-text-secondary uppercase tracking-widest mb-4">Risk Levels</p>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
              <div className="flex-1">
                <p className="text-xs font-semibold text-white">Low Risk</p>
                <p className="text-[10px] text-text-secondary">AQI &lt; 200 (Safe)</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-saffron shadow-[0_0_8px_rgba(255,153,51,0.5)]" />
              <div className="flex-1">
                <p className="text-xs font-semibold text-white">Moderate</p>
                <p className="text-[10px] text-text-secondary">200-300 (Caution)</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
              <div className="flex-1">
                <p className="text-xs font-semibold text-white">High Risk</p>
                <p className="text-[10px] text-text-secondary">AQI &gt; 300 (Alert)</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Map Section */}
      <div className="lg:col-span-2">
        <div
          ref={mapRef}
          className="relative aspect-[4/3] bg-card/50 rounded-3xl border border-card-border overflow-hidden cursor-grab active:cursor-grabbing group shadow-inner"
        >
          {/* Zoom Controls */}
          <div className="absolute top-4 right-4 flex flex-col gap-2 z-40">
            <button
              onClick={() => handleZoom(0.2)}
              className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-white"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <button
              onClick={() => handleZoom(-0.2)}
              className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-white"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <button
              onClick={resetView}
              className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-white"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>

          <motion.div
            drag
            dragConstraints={mapRef}
            animate={{ scale: viewState.scale }}
            transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            className="w-full h-full relative"
          >
            {/* Mock Map Background (Stylized SVG) */}
            <svg viewBox="0 0 100 100" className="w-full h-full opacity-30 absolute inset-0 text-text-secondary/20 scale-[2]">
               <path d="M20,40 Q30,20 50,30 T80,40 T70,70 T40,80 T20,40" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 2" />
               <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="0.1" opacity="0.5" />
               <path d="M10,20 Q40,10 70,20 T90,50 T60,90 T20,80 T10,20" fill="none" stroke="currentColor" strokeWidth="0.2" />
            </svg>

            {/* Zone Markers */}
            {zones.map((zone) => (
              <motion.button
                key={zone.id}
                whileHover={{ scale: 1.25 }}
                onClick={() => setSelectedZone(zone)}
                className={cn(
                  "absolute w-4 h-4 rounded-full border-2 border-white shadow-[0_0_15px_rgba(0,0,0,0.5)] transition-all z-20 group/marker",
                  zone.status === 'safe' ? 'bg-green-500' : zone.status === 'warning' ? 'bg-saffron' : 'bg-red-500',
                  selectedZone?.id === zone.id && "ring-4 ring-white/30 scale-125 z-30"
                )}
                style={{ left: `${zone.coordinates.x}%`, top: `${zone.coordinates.y}%` }}
              >
                {/* Marker Pulse Effect */}
                <div className={cn(
                  "absolute inset-0 rounded-full animate-ping opacity-40 -z-10",
                  zone.status === 'safe' ? 'bg-green-500' : zone.status === 'warning' ? 'bg-saffron' : 'bg-red-500'
                )} />

                {/* Tooltip */}
                <div className="absolute -top-20 left-1/2 -translate-x-1/2 whitespace-nowrap bg-white/95 backdrop-blur-sm text-black px-4 py-2.5 rounded-2xl text-[10px] font-bold border border-white opacity-0 group-hover/marker:opacity-100 transition-all pointer-events-none transform translate-y-4 group-hover/marker:translate-y-0 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.3)] z-50">
                  <p className="text-black/40 uppercase tracking-widest mb-0.5 text-[9px]">{zone.name}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-black tracking-tight leading-none">AQI {zone.aqi}</span>
                    <div className={cn(
                      "w-2 h-2 rounded-full",
                      zone.status === 'safe' ? 'bg-green-500' : zone.status === 'warning' ? 'bg-saffron' : 'bg-red-500'
                    )} />
                  </div>
                  <div className="absolute bottom-[-6px] left-1/2 -translate-x-1/2 w-3 h-3 bg-white/95 rotate-45 border-r border-b border-white" />
                </div>
              </motion.button>
            ))}
          </motion.div>

          <div className="absolute bottom-6 right-6 p-3 bg-black/40 backdrop-blur-sm rounded-xl border border-white/5 z-40">
            <p className="text-[10px] text-white/60 font-medium">Pan to explore Map</p>
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="lg:col-span-1 space-y-6">
        <AnimatePresence mode="wait">
          {selectedZone ? (
            <motion.div
              key={selectedZone.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              <GlowCard
                glowColor={getGlowColor(selectedZone.aqi)}
                className="h-full border-none shadow-lg"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-saffron" />
                      {selectedZone.name}
                    </h3>
                    <p className="text-text-secondary text-xs mt-1">Live Zone Analysis</p>
                  </div>
                  <div className={cn("px-3 py-1 rounded-full text-[10px] font-bold border flex items-center gap-1.5", getStatusColor(selectedZone.status))}>
                    <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse",
                      selectedZone.status === 'safe' ? 'bg-green-500' :
                      selectedZone.status === 'warning' ? 'bg-saffron' : 'bg-red-500'
                    )} />
                    {selectedZone.status.toUpperCase()}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-2 text-text-secondary mb-2">
                      <Wind className="w-4 h-4" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">AQI</span>
                    </div>
                    <p className={cn("text-3xl font-bold tracking-tight", selectedZone.aqi > 300 ? 'text-red-500' : selectedZone.aqi > 200 ? 'text-saffron' : 'text-green-500')}>
                      {selectedZone.aqi}
                    </p>
                  </div>

                  <div className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-2 text-text-secondary mb-2">
                      <Thermometer className="w-4 h-4" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">Temp</span>
                    </div>
                    <p className="text-3xl font-bold text-white tracking-tight">{selectedZone.temp}°C</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-2 text-text-secondary mb-2">
                      <Droplets className="w-4 h-4" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">Rain</span>
                    </div>
                    <p className="text-3xl font-bold text-white tracking-tight">{selectedZone.rainfall}</p>
                  </div>

                  <div className="p-4 rounded-2xl bg-white/10 border border-saffron/20 flex flex-col justify-center relative overflow-hidden group/payout">
                    <div className="absolute inset-0 bg-saffron/5 opacity-0 group-hover/payout:opacity-100 transition-opacity" />
                    <div className="flex items-center gap-2 text-saffron relative z-10">
                      <Info className="w-4 h-4" />
                      <span className="text-[10px] font-bold uppercase tracking-wider">Payout</span>
                    </div>
                    <p className="text-xl font-bold text-white mt-1 relative z-10">₹400 Risk</p>
                  </div>
                </div>

                <div className="mt-8 p-5 rounded-2xl bg-white/5 border border-white/10 relative overflow-hidden">
                  <div className={cn("absolute top-0 left-0 w-1 h-full",
                    selectedZone.status === 'safe' ? 'bg-green-500' :
                    selectedZone.status === 'warning' ? 'bg-saffron' : 'bg-red-500'
                  )} />
                  <p className="text-xs text-text-secondary leading-relaxed font-medium">
                    {selectedZone.status === 'danger'
                      ? "High risk triggered. Extra ₹400 payout active for active delivery partners in this zone."
                      : selectedZone.status === 'warning'
                      ? "Monitoring conditions. Potential risk trigger in the next 2-4 hours."
                      : "Safe conditions. Standard earnings apply."}
                  </p>
                </div>
              </GlowCard>
            </motion.div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center p-12 text-center text-text-secondary border-2 border-dashed border-card-border rounded-3xl bg-card/10">
              <MapPin className="w-12 h-12 mb-4 opacity-20" />
              <p className="font-medium">Select a zone on the map or list to view live weather metrics</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
