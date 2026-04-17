import React from 'react';
import { cn } from '../../lib/utils';

interface DeliveryScooterProps {
  className?: string;
}

const DeliveryScooter: React.FC<DeliveryScooterProps> = ({ className }) => {
  return (
    <div className={cn("relative w-full flex items-center justify-center py-10 overflow-hidden", className)}>
      {/* Container for the scooter and road */}
      <div className="relative w-[320px] h-[240px]">
        
        {/* Road line with movement animation */}
        <div className="absolute bottom-10 left-0 w-full h-1 bg-white/10 rounded-full overflow-hidden">
          <div className="absolute top-0 h-full w-20 bg-white/20 animate-road-line"></div>
        </div>

        {/* Scooter Group */}
        <div className="absolute bottom-10 left-12 animate-scooter-float">
          
          <svg width="240" height="200" viewBox="0 0 240 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="drop-shadow-lg">
            {/* Windshield */}
            <path d="M190 60 L210 100" stroke="white" strokeWidth="4" strokeLinecap="round" opacity="0.3" />
            
            {/* Main Chassi with depth */}
            <path d="M50 145 C50 120 70 115 90 115 L180 115 C200 115 210 125 210 145 Z" fill="#F97316" className="animate-pulse" />
            <path d="M185 115 L200 55 C203 45 210 45 215 50" stroke="white" strokeWidth="8" strokeLinecap="round" />
            
            {/* Front apron */}
            <path d="M185 115 C185 100 200 90 215 90" stroke="#FB923C" strokeWidth="12" strokeLinecap="round" />

            {/* Handlebar Details */}
            <rect x="195" y="42" width="22" height="7" rx="3.5" fill="white" />
            <circle cx="218" cy="62" r="6" fill="#60A5FA" className="animate-pulse" /> {/* Headlight bulb */}
            <path d="M222 62 L250 62" stroke="#60A5FA" strokeWidth="20" strokeLinecap="butt" opacity="0.1" className="blur-md" /> {/* Beam */}

            {/* Delivery Box - More detailed */}
            <rect x="35" y="55" width="85" height="80" rx="14" fill="#FB923C" className="shadow-inner" />
            <path d="M35 85 L120 85" stroke="white" strokeWidth="1" opacity="0.2" />
            <rect x="45" y="65" width="65" height="40" rx="6" fill="white" fillOpacity="0.05" />
            <text x="77" y="105" textAnchor="middle" fill="white" fontSize="42" fontWeight="900" style={{ fontFamily: 'Inter, sans-serif', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}>S</text>
            
            {/* Driver - Refined silhouette */}
            <path d="M105 115 L120 65 C125 55 135 50 150 55 L185 60" stroke="#ffffff" strokeWidth="14" strokeLinecap="round" />
            <path d="M105 115 Q125 105 145 115 L165 115" stroke="#ffffff" strokeWidth="8" strokeLinecap="round" opacity="0.8" />
            {/* Scarf / Cape of speed */}
            <path d="M125 55 Q100 50 80 60" stroke="#F97316" strokeWidth="6" strokeLinecap="round" className="animate-pulse" />

            {/* Helmet - Premium finish */}
            <circle cx="140" cy="40" r="19" fill="white" />
            <path d="M130 45 L155 45" stroke="#0F172A" strokeWidth="6" strokeLinecap="round" />
            <rect x="140" y="30" width="18" height="6" rx="3" fill="#F97316" /> {/* Helmet stripe */}
            
            {/* Wheels - Detailed hubs */}
            <g className="animate-spin-slow origin-[185px_150px]">
              <circle cx="185" cy="150" r="24" stroke="white" strokeWidth="8" strokeDasharray="14 10" />
              <circle cx="185" cy="150" r="10" fill="white" />
              <circle cx="185" cy="150" r="4" fill="#F97316" />
            </g>
            
            <g className="animate-spin-slow origin-[65px_150px]">
              <circle cx="65" cy="150" r="24" stroke="white" strokeWidth="8" strokeDasharray="14 10" />
              <circle cx="65" cy="150" r="10" fill="white" />
              <circle cx="65" cy="150" r="4" fill="#F97316" />
            </g>
          </svg>
          
          {/* Exhaust Fluff - More dynamic */}
          <div className="absolute -left-6 bottom-12 flex flex-col gap-1 items-end">
            <div className="w-2 h-2 rounded-full bg-white/30 animate-exhaust-1"></div>
            <div className="w-3 h-3 rounded-full bg-white/20 animate-exhaust-2"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-white/40 animate-exhaust-1 delay-75"></div>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scooter-float {
          0%, 100% { transform: translateY(0) rotate(0); }
          50% { transform: translateY(-8px) rotate(-1deg); }
        }
        @keyframes road-line {
          0% { transform: translateX(-150px); opacity: 0; }
          50% { opacity: 1; }
          100% { transform: translateX(350px); opacity: 0; }
        }
        @keyframes exhaust-1 {
          0% { transform: scale(0) translateX(0); opacity: 1; }
          100% { transform: scale(2) translateX(-20px); opacity: 0; }
        }
        @keyframes exhaust-2 {
          0% { transform: scale(0) translateX(0); opacity: 1; }
          100% { transform: scale(2) translateX(-40px); opacity: 0; }
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-scooter-float { animation: scooter-float 3s ease-in-out infinite; will-change: transform; }
        .animate-road-line { animation: road-line 1.5s linear infinite; will-change: transform; }
        .animate-exhaust-1 { animation: exhaust-1 0.8s ease-out infinite; will-change: transform, opacity; }
        .animate-exhaust-2 { animation: exhaust-2 1.2s ease-out infinite; will-change: transform, opacity; }
        .animate-spin-slow { animation: spin-slow 1s linear infinite; will-change: transform; }
      `}} />
    </div>
  );
};

export default DeliveryScooter;
