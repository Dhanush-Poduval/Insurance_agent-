import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { 
  LayoutDashboard, 
  ShieldCheck, 
  FileText, 
  CloudSun, 
  Users, 
  User, 
  HelpCircle, 
  Bell, 
  LogOut, 
  Menu, 
  X,
  ChevronRight,
  Copy,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  CreditCard,
  Wallet,
  Smartphone,
  Sun,
  Moon
} from 'lucide-react';
import { cn } from './lib/utils';
import { GlowCard } from './components/ui/spotlight-card';
import { WeatherMap } from './components/WeatherMap';
import AnimatedList from './components/ui/animated-list';
import DeliveryScooter from './components/ui/DeliveryScooter';

// --- Types ---
const API_BASE = (import.meta as any).env?.VITE_API_BASE || '';

async function safeFetch(endpoint: string, options?: RequestInit) {
  if (!endpoint) throw new Error("API endpoint missing");
  const fullUrl = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(fullUrl, options);
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  } catch (err) {
    console.error(`Fetch failed for ${endpoint}:`, err);
    throw err;
  }
}

interface UserData {
  name: string;
  phone: string;
  email: string;
  pan: string;
  aadhaar: string;
  platform: string;
  zone: string;
  dailyEarnings: number;
  isBoarded: boolean;
}

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: 'info' | 'success' | 'warning';
}

// --- Mock Data ---
const MOCK_NOTIFICATIONS: Notification[] = [
  { id: '1', title: 'Coverage Active', message: 'Your weekly coverage is now active.', time: '2h ago', read: false, type: 'success' },
  { id: '2', title: 'Weather Alert', message: 'High AQI predicted in Delhi NCR tomorrow.', time: '5h ago', read: false, type: 'warning' },
  { id: '3', title: 'Payment Received', message: 'Payout for Claim #1234 has been processed.', time: '1d ago', read: true, type: 'info' },
];

// --- Components ---

const AuthHero = () => (
  <div className="w-full flex-1 relative flex flex-col justify-center p-8 lg:p-12">
    {/* Depth layers */}
    <div className="absolute top-20 left-10 w-[400px] h-[400px] bg-orange-300/20 blur-xl rounded-full animate-pulse-slow will-change-transform"></div>
    <div className="absolute bottom-10 right-10 w-[300px] h-[300px] bg-yellow-300/20 blur-xl rounded-full animate-float will-change-transform"></div>

    <div className="relative z-10">
      <div className="flex items-center gap-3 mb-12">
        <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
          <ShieldCheck className="text-white w-6 h-6" />
        </div>
        <span className="text-2xl font-bold text-white tracking-tight">SAFAR</span>
      </div>

      <h1 className="text-5xl font-extrabold text-white leading-tight tracking-tight">
        Insurance for the <br />
        <span className="text-white/90">modern gig worker</span>
      </h1>

      <p className="mt-6 text-white/80 text-lg max-w-md leading-relaxed">
        Get automatic payouts during extreme weather conditions.  
        No paperwork. Instant claims. Zero stress.
      </p>

      {/* DELIVERY ANIMATION */}
      <div className="mt-10 h-[360px] flex items-center justify-center relative">
        {/* soft glow behind animation */}
        <div className="absolute w-[300px] h-[300px] bg-orange-400/20 blur-xl rounded-full opacity-30 will-change-transform"></div>
        <div className="relative z-10 hover:scale-105 transition duration-500 w-full h-full max-w-[400px]">
          <DeliveryScooter />
        </div>
      </div>

      {/* 7-DAY CARD UPGRADE */}
      <div className="mt-10 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 shadow-md">
        <h3 className="text-white font-semibold text-lg flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-white" />
          7-Day Activity Requirement
        </h3>

        <p className="text-white/70 text-sm mt-2">
          Coverage activates after 7 active delivery days.
        </p>

        <div className="flex gap-3 mt-6">
          {[1,2,3,4,5,6,7].map((d) => (
            <div
              key={d}
              className={cn(
                "w-9 h-9 flex items-center justify-center rounded-full transition-all duration-300 font-bold",
                d <= 2 
                  ? 'bg-white text-orange-600 shadow-md scale-110' 
                  : 'bg-white/20 text-white/70 border border-white/10'
              )}
            >
              {d}
            </div>
          ))}
        </div>
        
        <div className="flex justify-between mt-6">
          <span className="text-[10px] items-center flex gap-1 font-bold text-white uppercase tracking-widest bg-white/10 px-3 py-1 rounded-full">
            <div className="w-1 h-1 rounded-full bg-white animate-pulse" />
            2 Days Active
          </span>
          <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest">5 Days Remaining</span>
        </div>
      </div>
    </div>
  </div>
);

const ThemeToggle = ({ theme, toggleTheme }: { theme: 'light' | 'dark', toggleTheme: () => void }) => (
  <button
    onClick={toggleTheme}
    className="w-10 h-10 rounded-xl bg-card border border-card-border flex items-center justify-center hover:bg-background/50 transition-all text-text-secondary hover:text-saffron shadow-sm"
    title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
  >
    {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
  </button>
);

const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'outline' | 'ghost' }>(
  ({ className, variant = 'primary', ...props }, ref) => {
    const variants = {
      primary: 'bg-saffron text-white hover:bg-saffron-hover shadow-lg shadow-saffron/20',
      secondary: 'bg-white/10 text-white hover:bg-white/20',
      outline: 'border border-white/20 text-white hover:bg-white/5',
      ghost: 'text-white/60 hover:text-white hover:bg-white/5',
    };
    return (
      <button
        ref={ref}
        className={cn(
          'px-4 py-2 rounded-xl font-medium transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none flex items-center justify-center gap-2',
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

const Card = ({ children, className, title, subtitle, action }: { children: React.ReactNode; className?: string; title?: string; subtitle?: string; action?: React.ReactNode }) => (
  <div className={cn('bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/5 shadow-lg transition-all duration-300', className)}>
    {(title || action) && (
      <div className="flex items-center justify-between mb-6">
        <div>
          {title && <h3 className="text-lg font-bold text-white tracking-tight">{title}</h3>}
          {subtitle && <p className="text-xs font-medium text-text-secondary uppercase tracking-widest mt-1">{subtitle}</p>}
        </div>
        {action}
      </div>
    )}
    {children}
  </div>
);

const Input = ({ label, error, ...props }: { label?: string; error?: string } & React.InputHTMLAttributes<HTMLInputElement>) => (
  <div className="space-y-1.5 w-full">
    {label && <label className="text-sm font-medium text-text-secondary ml-1">{label}</label>}
    <input
      className={cn(
        'w-full bg-background/50 border border-card-border rounded-xl px-4 py-3 text-text-primary placeholder:text-text-secondary/30 focus:outline-none focus:ring-2 focus:ring-saffron/50 transition-all',
        error && 'border-red-500/50 focus:ring-red-500/50',
        props.className
      )}
      {...props}
    />
    {error && <p className="text-xs text-red-400 ml-1">{error}</p>}
  </div>
);

// --- Layout ---

const Sidebar = ({ activeTab, setActiveTab }: { activeTab: string; setActiveTab: (t: string) => void }) => {
  const navigate = useNavigate();
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { id: 'coverage', label: 'Coverage', icon: ShieldCheck, path: '/coverage' },
    { id: 'claims', label: 'Claims', icon: FileText, path: '/claims' },
    { id: 'weather', label: 'Zone Weather', icon: CloudSun, path: '/weather' },
    { id: 'referrals', label: 'Referrals', icon: Users, path: '/referrals' },
    { id: 'profile', label: 'Profile', icon: User, path: '/profile' },
    { id: 'support', label: 'Support', icon: HelpCircle, path: '/support' },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-sidebar-border h-screen sticky top-0 hidden lg:flex flex-col p-6">
      <div className="flex items-center gap-3 mb-10 px-2">
        <div className="w-10 h-10 saffron-gradient rounded-xl flex items-center justify-center shadow-lg shadow-saffron/20">
          <ShieldCheck className="text-white w-6 h-6" />
        </div>
        <span className="text-2xl font-bold tracking-tight text-saffron">SAFAR</span>
      </div>

      <nav className="flex-1 space-y-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => {
              setActiveTab(item.id);
              navigate(item.path);
            }}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all group',
              activeTab === item.id 
                ? 'bg-saffron/10 text-saffron' 
                : 'text-text-secondary hover:text-text-primary hover:bg-background/50'
            )}
          >
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={activeTab === item.id ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
              className="absolute left-0 w-1 h-6 bg-saffron rounded-r-full"
            />
            <item.icon className={cn('w-5 h-5 transition-all group-hover:scale-110', activeTab === item.id ? 'text-saffron' : 'text-text-secondary group-hover:text-text-primary')} />
            <span className="font-semibold tracking-wide">{item.label}</span>
          </button>
        ))}
      </nav>

      <button 
        onClick={() => {
          localStorage.removeItem('isLoggedIn');
          navigate('/login');
        }}
        className="flex items-center gap-3 px-4 py-3 rounded-xl text-text-secondary hover:text-red-400 hover:bg-red-400/5 transition-all mt-auto"
      >
        <LogOut className="w-5 h-5" />
        <span className="font-medium">Logout</span>
      </button>
    </div>
  );
};

const TopBar = ({ title, userData, onMenuClick, theme, toggleTheme }: { title: string; userData: UserData; onMenuClick: () => void; theme: 'light' | 'dark'; toggleTheme: () => void }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState(MOCK_NOTIFICATIONS);

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="h-20 border-b border-card-border flex items-center justify-between px-6 lg:px-10 sticky top-0 bg-background/80 backdrop-blur-sm z-30">
      <div className="flex items-center gap-4">
        <button 
          onClick={onMenuClick}
          className="lg:hidden w-10 h-10 rounded-xl bg-card border border-card-border flex items-center justify-center hover:bg-background/50 transition-all"
        >
          <Menu className="w-5 h-5 text-text-secondary" />
        </button>
        <h1 className="text-xl font-semibold text-text-primary">{title}</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
        
        <div className="relative">
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-10 h-10 rounded-xl bg-card border border-card-border flex items-center justify-center hover:bg-background/50 transition-all relative"
          >
            <Bell className="w-5 h-5 text-text-secondary" />
            {unreadCount > 0 && (
              <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-saffron rounded-full border-2 border-background" />
            )}
          </button>

          <AnimatePresence>
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)} />
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute right-0 mt-3 w-80 bg-card border border-white/10 rounded-2xl shadow-lg z-50 overflow-hidden"
                >
                  <div className="p-4 border-b border-white/5 flex items-center justify-between">
                    <span className="font-semibold">Notifications</span>
                    <button 
                      onClick={() => setNotifications(notifications.map(n => ({ ...n, read: true })))}
                      className="text-xs text-saffron hover:underline"
                    >
                      Mark all read
                    </button>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((n) => (
                        <div key={n.id} className={cn('p-4 border-b border-white/5 hover:bg-white/5 transition-all cursor-pointer', !n.read && 'bg-saffron/5')}>
                          <div className="flex gap-3">
                            <div className={cn('w-2 h-2 rounded-full mt-1.5 shrink-0', n.type === 'success' ? 'bg-green-500' : n.type === 'warning' ? 'bg-saffron' : 'bg-blue-500')} />
                            <div>
                              <p className="text-sm font-medium text-white">{n.title}</p>
                              <p className="text-xs text-white/40 mt-0.5">{n.message}</p>
                              <p className="text-[10px] text-white/20 mt-2">{n.time}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-10 text-center text-white/20">No notifications</div>
                    )}
                  </div>
                  <button 
                    onClick={() => setNotifications([])}
                    className="w-full p-3 text-xs text-white/40 hover:text-white hover:bg-white/5 transition-all"
                  >
                    Clear all
                  </button>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        <div className="flex items-center gap-3 pl-4 border-l border-white/5">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-white">{userData.name || 'User'}</p>
            <p className="text-xs text-white/40">ID: SF-{userData.phone.slice(-4)}</p>
          </div>
          <div className="w-10 h-10 rounded-xl saffron-gradient flex items-center justify-center text-white font-bold shadow-lg shadow-saffron/20">
            {userData.name ? userData.name[0] : 'U'}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Pages ---

const LoginPage = () => {
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.length !== 10) {
      setError('Please enter a valid 10-digit number');
      return;
    }
    setError('');
    
    try {
      // Mock validation with safeFetch pattern
      // await safeFetch('/api/otp', { method: 'POST', body: JSON.stringify({ phone }) });
      localStorage.setItem('tempPhone', phone);
      navigate('/otp');
    } catch (err) {
      setError('Failed to reach authentication server. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#020617] selection:bg-saffron/30">
      {/* Left Side - Hero (50%) */}
      <div className="lg:w-1/2 flex flex-col order-1 lg:order-1 lg:h-screen lg:sticky lg:top-0 border-r border-white/5 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 overflow-y-auto no-scrollbar">
        <AuthHero />
      </div>

      {/* Right Side - Form (50%) */}
      <div className="lg:w-1/2 min-h-screen flex items-center justify-center p-6 lg:p-20 relative order-2 lg:order-2 bg-background">
        {/* Decorative background blobs - reduced blur for performance */}
        <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-saffron/10 rounded-full blur-[40px] animate-pulse-slow will-change-transform" />
        <div className="absolute bottom-1/4 left-1/4 w-64 h-64 bg-blue-500/5 rounded-full blur-[40px] animate-pulse will-change-transform" />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md relative z-10"
        >
          <div className="bg-card border border-card-border rounded-[40px] p-10 lg:p-12 shadow-lg shadow-black/30 backdrop-blur-sm overflow-hidden relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-saffron/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            
            <div className="relative text-center mb-10">
              <h1 className="text-4xl font-black text-text-primary tracking-tighter mb-3">Welcome back</h1>
              <p className="text-text-secondary font-medium tracking-tight">Enter your phone number to continue</p>
            </div>

            <form onSubmit={handleSendOTP} className="relative space-y-8">
              <div className="space-y-4">
                <label className="text-xs font-bold text-text-secondary uppercase tracking-[0.2em] ml-1">Phone Number</label>
                <div className="relative group/input">
                  <span className="absolute left-6 top-1/2 -translate-y-1/2 text-saffron font-black text-xl tracking-tight">+91</span>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => {
                      setPhone(e.target.value.replace(/\D/g, ''));
                      setError('');
                    }}
                    placeholder="Enter 10 digit number"
                    className={cn(
                      'w-full bg-slate-100 dark:bg-white/5 border border-card-border rounded-[28px] pl-16 pr-8 py-5 text-text-primary text-xl font-bold placeholder:text-text-secondary/30 outline-none focus:border-saffron focus:ring-4 focus:ring-saffron/10 focus:bg-background transition-all duration-300',
                      error && 'border-red-500/50 focus:ring-red-500/10'
                    )}
                  />
                </div>
                {error && <p className="text-xs text-red-400 ml-1 font-bold flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {error}
                </p>}
              </div>

              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-orange-500 to-orange-600 py-6 rounded-[28px] text-white text-xl font-black shadow-lg shadow-orange-500/10 hover:scale-[1.03] active:scale-[0.97] transition-all duration-300 flex items-center justify-center gap-2"
              >
                Get OTP
                <ArrowRight className="w-6 h-6" />
              </button>
            </form>

            <div className="relative mt-12 text-center">
              <p className="text-text-secondary font-medium tracking-tight">
                Don't have an account? 
                <button onClick={() => navigate('/signup')} className="text-saffron ml-2 font-black hover:text-text-primary transition-colors">Sign Up</button>
              </p>
            </div>

            <p className="relative text-center text-[10px] text-text-secondary/50 mt-12 leading-relaxed uppercase tracking-[0.15em] font-bold">
              Secure & Encrypted • Powered by SAFAR Node
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

const SignUpPage = () => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please enter your full name');
      return;
    }
    if (phone.length !== 10) {
      setError('Please enter a valid 10-digit number');
      return;
    }
    setError('');

    try {
      // await safeFetch('/api/signup', { method: 'POST', body: JSON.stringify({ name, phone }) });
      localStorage.setItem('tempPhone', phone);
      localStorage.setItem('tempName', name);
      navigate('/otp');
    } catch (err) {
      setError('Connection error. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#020617] selection:bg-saffron/30">
      {/* Left Side - Hero (50%) */}
      <div className="lg:w-1/2 flex flex-col order-1 lg:order-1 lg:h-screen lg:sticky lg:top-0 border-r border-white/5 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 overflow-y-auto no-scrollbar">
        <AuthHero />
      </div>

      {/* Right Side - Form (50%) */}
      <div className="lg:w-1/2 min-h-screen flex items-center justify-center p-6 lg:p-20 relative order-2 lg:order-2 bg-background">
        <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-saffron/10 rounded-full blur-[40px] animate-pulse-slow will-change-transform" />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md relative z-10"
        >
          <div className="bg-card border border-card-border rounded-[40px] p-10 lg:p-12 shadow-lg shadow-black/30 backdrop-blur-sm">
            <div className="text-center mb-10">
              <h1 className="text-3xl font-black text-text-primary tracking-tighter mb-2">Create Account</h1>
              <p className="text-text-secondary font-medium">Join SAFAR and protect your earnings</p>
            </div>

            <form onSubmit={handleSignUp} className="space-y-6">
              <div className="space-y-3">
                <label className="text-xs font-bold text-text-secondary uppercase tracking-widest ml-1">Full Name</label>
                <div className="relative group/input">
                  <User className="absolute left-6 top-1/2 -translate-y-1/2 text-saffron w-5 h-5" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => {
                      setName(e.target.value);
                      setError('');
                    }}
                    placeholder="Enter your full name"
                    className="w-full bg-slate-100 dark:bg-white/5 border border-card-border rounded-[24px] pl-16 pr-8 py-4 text-text-primary font-bold placeholder:text-text-secondary/30 outline-none focus:border-saffron focus:ring-4 focus:ring-saffron/10 focus:bg-background transition-all duration-300"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-xs font-bold text-text-secondary uppercase tracking-widest ml-1">Phone Number</label>
                <div className="relative group/input">
                  <span className="absolute left-6 top-1/2 -translate-y-1/2 text-saffron font-black text-lg tracking-tight">+91</span>
                  <input
                    type="tel"
                    maxLength={10}
                    value={phone}
                    onChange={(e) => {
                      setPhone(e.target.value.replace(/\D/g, ''));
                      setError('');
                    }}
                    placeholder="Enter 10 digit number"
                    className={cn(
                      'w-full bg-slate-100 dark:bg-white/5 border border-card-border rounded-[24px] pl-16 pr-8 py-4 text-text-primary font-bold placeholder:text-text-secondary/30 outline-none focus:border-saffron focus:ring-4 focus:ring-saffron/10 focus:bg-background transition-all duration-300',
                      error && error.includes('phone') && 'border-red-500/50'
                    )}
                  />
                </div>
                {error && <p className="text-xs text-red-400 ml-1 font-bold">{error}</p>}
              </div>

              <button 
                type="submit" 
                className="w-full bg-gradient-to-r from-orange-500 to-orange-600 py-5 rounded-[24px] text-white font-black hover:scale-[1.03] active:scale-[0.97] transition-all duration-300 shadow-xl shadow-orange-500/20 flex items-center justify-center gap-2"
              >
                Create Account
                <ArrowRight className="w-6 h-6" />
              </button>
            </form>

            <div className="mt-8 text-center">
              <p className="text-text-secondary font-medium">
                Already have an account? 
                <button onClick={() => navigate('/login')} className="text-saffron ml-2 font-black hover:text-text-primary transition-colors">Login</button>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

const OTPPage = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const phone = localStorage.getItem('tempPhone') || '9999999999';

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handleVerify = () => {
    if (otp.join('').length !== 6) {
      setError('Please enter all 6 digits');
      return;
    }
    // Mock verification
    localStorage.setItem('isLoggedIn', 'true');
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    if (userData.isBoarded) {
      navigate('/dashboard');
    } else {
      navigate('/onboarding');
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-background">
      {/* Left Side - Hero (50%) */}
      <div className="lg:w-1/2 flex flex-col order-1 lg:h-screen lg:sticky lg:top-0 border-r border-card-border/5 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 overflow-y-auto no-scrollbar">
        <AuthHero />
      </div>

      {/* Right Side - Form (50%) */}
      <div className="lg:w-1/2 flex items-center justify-center p-10 lg:p-20 relative order-2">
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-text-primary tracking-tight">Verify OTP</h1>
            <p className="text-text-secondary mt-2">Sent to +91 {phone}</p>
          </div>

          <Card className="p-8">
            <div className="space-y-8">
              <div className="flex justify-between gap-2">
                {otp.map((digit, i) => (
                  <input
                    key={i}
                    id={`otp-${i}`}
                    type="text"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(i, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(i, e)}
                    className="w-12 h-14 bg-background/50 border border-card-border rounded-xl text-center text-xl font-bold text-text-primary focus:outline-none focus:ring-2 focus:ring-saffron focus:border-saffron transition-all"
                  />
                ))}
              </div>

              {error && <p className="text-center text-sm text-red-400">{error}</p>}

              <div className="space-y-4">
                <Button onClick={handleVerify} className="w-full py-4 text-lg">
                  Verify & Continue
                </Button>
                <button className="w-full text-sm text-text-secondary hover:text-saffron transition-all">
                  Resend OTP in 24s
                </button>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

const OnboardingPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<UserData>({
    name: localStorage.getItem('tempName') || '',
    phone: localStorage.getItem('tempPhone') || '',
    email: '',
    pan: '',
    aadhaar: '',
    platform: '',
    zone: 'Delhi NCR',
    dailyEarnings: 650,
    isBoarded: false
  });
  const navigate = useNavigate();

  const handleComplete = () => {
    const finalData = { ...formData, isBoarded: true };
    localStorage.setItem('userData', JSON.stringify(finalData));
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-background">
      {/* Left Side - Hero (50%) */}
      <div className="lg:w-1/2 flex flex-col order-1 h-screen lg:h-screen lg:sticky lg:top-0 border-r border-card-border/5 bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 overflow-y-auto no-scrollbar">
        <AuthHero />
      </div>

      {/* Right Side - Form (50%) */}
      <div className="lg:w-1/2 p-10 lg:p-20 flex items-center justify-center order-2">
        <div className="w-full max-w-md">
          <div className="mb-10 text-center lg:text-left">
            <h2 className="text-2xl font-bold text-text-primary">Complete your profile</h2>
            <p className="text-text-secondary mt-1">We need a few more details to get you started</p>
          </div>

          <div className="space-y-8">
            <div className="space-y-6">
              <Input 
                label="Full Name" 
                placeholder="Enter your name" 
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <div className="flex gap-4">
                <Input 
                  label="PAN Number" 
                  placeholder="ABCDE1234F" 
                  className="uppercase"
                  value={formData.pan}
                  onChange={(e) => setFormData({ ...formData, pan: e.target.value })}
                />
                <div className="pt-8">
                  <span className="text-xs text-green-500 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Verified
                  </span>
                </div>
              </div>
              <Input 
                label="Aadhaar Number" 
                placeholder="XXXX XXXX 9012" 
                value={formData.aadhaar}
                onChange={(e) => setFormData({ ...formData, aadhaar: e.target.value })}
              />
            </div>

            <div className="space-y-4">
              <label className="text-sm font-medium text-text-secondary ml-1">Select Primary Platform</label>
              <div className="grid grid-cols-2 gap-3">
                {['Zomato', 'Swiggy', 'Amazon', 'Flipkart'].map((p) => (
                  <button
                    key={p}
                    onClick={() => setFormData({ ...formData, platform: p })}
                    className={cn(
                      'p-4 rounded-2xl border transition-all flex flex-col items-center gap-2',
                      formData.platform === p 
                        ? 'border-saffron bg-saffron/5 text-saffron' 
                        : 'border-card-border bg-card text-text-secondary hover:border-saffron/50'
                    )}
                  >
                    <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center font-bold text-lg', 
                      p === 'Zomato' ? 'bg-red-500 text-white' : 
                      p === 'Swiggy' ? 'bg-orange-500 text-white' : 
                      p === 'Amazon' ? 'bg-black text-white' : 'bg-blue-600 text-white'
                    )}>
                      {p[0]}
                    </div>
                    <span className="text-sm font-medium">{p}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-text-secondary ml-1">Work Zone</label>
                <select 
                  className="w-full bg-background/50 border border-card-border rounded-xl px-4 py-3 text-text-primary focus:outline-none focus:ring-2 focus:ring-saffron/50 transition-all appearance-none"
                  value={formData.zone}
                  onChange={(e) => setFormData({ ...formData, zone: e.target.value })}
                >
                  <option>Delhi NCR</option>
                  <option>Mumbai</option>
                  <option>Bangalore</option>
                  <option>Hyderabad</option>
                </select>
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-medium text-text-secondary ml-1">Average Daily Earnings</label>
                  <span className="text-saffron font-bold">₹{formData.dailyEarnings}</span>
                </div>
                <input 
                  type="range" 
                  min="50" 
                  max="1000" 
                  step="50"
                  value={formData.dailyEarnings}
                  onChange={(e) => setFormData({ ...formData, dailyEarnings: parseInt(e.target.value) })}
                  className="w-full h-2 bg-card-border rounded-lg appearance-none cursor-pointer accent-saffron"
                />
                <div className="flex justify-between text-[10px] text-text-secondary/50">
                  <span>₹50</span>
                  <span>₹1000+</span>
                </div>
              </div>
            </div>

            <Button onClick={handleComplete} className="w-full py-4 mt-8">
              Complete Setup
              <ChevronRight className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

const DashboardPage = ({ userData }: { userData: UserData }) => {
  return (
    <div className="space-y-8 relative pb-20">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-50px] left-[-50px] w-64 h-64 bg-saffron/5 rounded-full blur-[30px] pointer-events-none -z-10 will-change-transform" />
      <div className="absolute bottom-[-50px] right-[-50px] w-64 h-64 bg-blue-500/5 rounded-full blur-[30px] pointer-events-none -z-10 will-change-transform" />

      {/* Hero Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <GlowCard className="lg:col-span-2 saffron-gradient border-none p-8 flex flex-col justify-between min-h-[220px] relative overflow-hidden group shadow-lg shadow-saffron/20">
          <div className="absolute top-0 right-0 p-6 opacity-20 transform translate-x-4 -translate-y-4 group-hover:translate-x-2 group-hover:-translate-y-2 transition-transform duration-500">
            <Wallet className="w-32 h-32 text-white" />
          </div>
          <div>
            <p className="text-white/80 text-sm font-bold uppercase tracking-widest">Available Wallet Balance</p>
            <h2 className="text-5xl font-bold text-white mt-2 tracking-tight">₹840.45</h2>
          </div>
          <div className="flex items-center gap-3 relative z-10">
            <Button className="bg-white text-saffron hover:bg-white/90 font-bold px-6 shadow-xl">
              Withdraw Funds
            </Button>
            <button className="p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-all text-white backdrop-blur-sm border border-white/10">
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </GlowCard>

        <GlowCard className="lg:col-span-1 border-none bg-white/5 backdrop-blur-sm group hover:-translate-y-1 transition-all duration-300">
          <p className="text-text-secondary text-xs font-bold uppercase tracking-widest">Weekly Earnings</p>
          <div className="flex items-end gap-2 mt-2">
            <h2 className="text-3xl font-bold text-white tracking-tight">₹12,450</h2>
            <span className="text-green-500 text-xs font-bold mb-1">+12%</span>
          </div>
          <div className="mt-8 h-12 flex items-end gap-1">
            {[40, 70, 45, 90, 65, 80, 55].map((h, i) => (
              <div key={i} className="flex-1 bg-white/10 rounded-t-sm group-hover:bg-saffron/40 transition-all duration-500" style={{ height: `${h}%` }} />
            ))}
          </div>
          <p className="text-[10px] text-text-secondary mt-3">Calculated from 42 deliveries</p>
        </GlowCard>

        <GlowCard className="lg:col-span-1 border-none bg-white/5 backdrop-blur-sm group hover:-translate-y-1 transition-all duration-300">
          <p className="text-text-secondary text-xs font-bold uppercase tracking-widest">Active Coverage</p>
          <div className="flex items-center justify-between mt-2">
            <h2 className="text-3xl font-bold text-white tracking-tight">₹72</h2>
            <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center text-green-500 shadow-inner">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-6 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs font-bold text-green-500 uppercase tracking-wide">Live Protection</span>
          </div>
          <p className="text-[10px] text-text-secondary mt-2">Next renewal in 2 days</p>
        </GlowCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Weather Widget */}
        <GlowCard className="lg:col-span-1 border-none bg-white/5 backdrop-blur-sm" glowColor="red">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-white">Zone Weather</h3>
              <p className="text-sm text-text-secondary">{userData.zone} • Delhi NCR</p>
            </div>
            <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center border border-red-500/20 shadow-lg shadow-red-500/10">
              <CloudSun className="text-red-500 w-6 h-6" />
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-saffron/10 flex items-center justify-center">
                  <CloudSun className="text-saffron w-7 h-7" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-white tracking-tight">32°</p>
                  <p className="text-[10px] text-text-secondary font-bold uppercase tracking-widest">Haze Condition</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-saffron">AQI 342</p>
                <div className="bg-red-500/20 px-2 py-0.5 rounded-lg border border-red-500/30 inline-block mt-1">
                  <p className="text-[9px] text-red-500 font-bold uppercase tracking-widest">CRITICAL</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {['Mon', 'Tue', 'Wed'].map((day, i) => (
                <div key={day} className="bg-white/5 rounded-2xl p-4 text-center border border-white/5 group hover:border-saffron/30 transition-all duration-300">
                  <p className="text-[10px] text-text-secondary uppercase font-bold tracking-widest">{day}</p>
                  <CloudSun className="w-6 h-6 text-saffron mx-auto my-3 group-hover:scale-110 transition-transform" />
                  <p className="text-xs font-bold text-white tracking-tight">34°/26°</p>
                </div>
              ))}
            </div>

            <motion.div 
               className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 flex gap-4 backdrop-blur-sm"
            >
              <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center shrink-0">
                 <AlertCircle className="text-red-500 w-5 h-5" />
              </div>
              <p className="text-xs text-red-200 leading-relaxed font-semibold">
                High AQI Alert: Risk premium increase likely within 24hrs.
              </p>
            </motion.div>
          </div>
        </GlowCard>

        {/* Recent Activity */}
        <Card className="lg:col-span-2 bg-white/5 backdrop-blur-sm border-white/5" title="Recent Activity" action={<Button variant="ghost" className="text-xs font-bold uppercase tracking-wider text-saffron">History</Button>}>
          <div className="space-y-4">
            {[
              { title: 'Premium Paid', desc: 'Weekly coverage (Oct 19 - 25)', amount: '-₹72', time: 'Today, 10:30 AM', type: 'expense' },
              { title: 'Claim Settled', desc: 'Extreme Heat Payout', amount: '+₹400', time: 'Yesterday, 4:15 PM', type: 'income' },
              { title: 'Referral Bonus', desc: 'From Rahul K.', amount: '+₹50', time: 'Oct 15, 2:00 PM', type: 'income' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-2xl hover:bg-background/50 transition-all border border-transparent hover:border-card-border">
                <div className="flex items-center gap-4">
                  <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', item.type === 'income' ? 'bg-green-500/10 text-green-500' : 'bg-background/50 text-text-secondary')}>
                    {item.type === 'income' ? <CheckCircle2 className="w-5 h-5" /> : <CreditCard className="w-5 h-5" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text-primary">{item.title}</p>
                    <p className="text-xs text-text-secondary">{item.desc}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={cn('text-sm font-bold', item.type === 'income' ? 'text-green-500' : 'text-text-primary')}>{item.amount}</p>
                  <p className="text-[10px] text-text-secondary/50">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

const CoveragePage = ({ userData }: { userData: UserData }) => {
  const [paymentMethod, setPaymentMethod] = useState('upi');

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-2 text-text-secondary text-sm">
        <button className="hover:text-text-primary transition-all">Dashboard</button>
        <ChevronRight className="w-4 h-4" />
        <span className="text-text-primary">Premium Purchase</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Breakdown */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Premium Breakdown" subtitle="Coverage valid for 19 Oct - 25 Oct">
            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 rounded-2xl bg-saffron/5 border border-saffron/10">
                <div>
                  <p className="text-xs text-saffron/60 font-medium uppercase tracking-wider">Final Premium Amount</p>
                  <h2 className="text-4xl font-bold text-saffron mt-1">₹72</h2>
                </div>
                <div className="text-right">
                  <p className="text-xs text-red-500 flex items-center gap-1 justify-end">
                    <AlertCircle className="w-3 h-3" /> 15% vs last week
                  </p>
                  <p className="text-[10px] text-text-secondary/50 mt-1">Based on weather forecast</p>
                </div>
              </div>

              <div className="space-y-4 px-2">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Expected Loss Base</span>
                  <span className="text-text-primary font-medium">₹32.00</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Platform Integration Fee</span>
                  <span className="text-text-primary font-medium">₹11.00</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Risk Margin ({userData.zone})</span>
                  <span className="text-text-primary font-medium">₹18.00</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Seasonal Loading (Monsoon/Heat)</span>
                  <span className="text-text-primary font-medium">₹11.00</span>
                </div>
              </div>

              <div className="pt-6 border-t border-card-border">
                <div className="p-4 rounded-2xl bg-background/50 border border-card-border space-y-3">
                  <div className="flex items-center gap-2 text-saffron">
                    <AlertCircle className="w-4 h-4" />
                    <span className="text-sm font-semibold">Why is your premium ₹72 this week?</span>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    Our AI has analyzed the conditions for your specific zone ({userData.zone}) and adjusted the premium based on the following key factors:
                  </p>
                  <ul className="space-y-2 mt-4">
                    <li className="flex gap-3 text-xs text-text-secondary">
                      <div className="w-1.5 h-1.5 rounded-full bg-saffron mt-1.5 shrink-0" />
                      <span>Severe AQI Forecast (Diwali Week): Forecast predicts AQI above 350 for 3 days next week.</span>
                    </li>
                    <li className="flex gap-3 text-xs text-text-secondary">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-1.5 shrink-0" />
                      <span>Safe Driving Bonus: You maintained a 4.8+ rating last week, reducing your base premium by 5%.</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Payment */}
        <Card className="lg:col-span-1" title="Complete Purchase">
          <div className="space-y-6">
            <div className="space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">Coverage</span>
                <span className="text-text-primary font-medium">Weather & Disruption</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">Period</span>
                <span className="text-text-primary font-medium">19 Oct - 25 Oct</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">Max Payout</span>
                <span className="text-text-primary font-bold text-saffron">₹500 / day</span>
              </div>
            </div>

            <div className="space-y-3 pt-6 border-t border-card-border">
              <p className="text-xs font-medium text-text-secondary ml-1">Select Payment Method</p>
              {[
                { id: 'upi', label: 'UPI (GPay, PhonePe, Paytm)', icon: Smartphone },
                { id: 'card', label: 'Debit / Credit Card', icon: CreditCard },
                { id: 'wallet', label: 'Wallet (Amazon Pay, Mobikwik)', icon: Wallet },
              ].map((m) => (
                <button
                  key={m.id}
                  onClick={() => setPaymentMethod(m.id)}
                  className={cn(
                    'w-full flex items-center justify-between p-4 rounded-xl border transition-all',
                    paymentMethod === m.id 
                      ? 'border-saffron bg-saffron/5' 
                      : 'border-card-border bg-background/50 hover:border-saffron/50'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <m.icon className={cn('w-5 h-5', paymentMethod === m.id ? 'text-saffron' : 'text-text-secondary')} />
                    <span className={cn('text-sm', paymentMethod === m.id ? 'text-text-primary font-medium' : 'text-text-secondary')}>{m.label}</span>
                  </div>
                  <div className={cn('w-4 h-4 rounded-full border-2 flex items-center justify-center', 
                    paymentMethod === m.id ? 'border-saffron' : 'border-card-border'
                  )}>
                    {paymentMethod === m.id && <div className="w-2 h-2 rounded-full bg-saffron" />}
                  </div>
                </button>
              ))}
            </div>

            <div className="space-y-4 pt-6">
              <div className="flex gap-3">
                <input type="checkbox" className="mt-1 accent-saffron" defaultChecked />
                <p className="text-[10px] text-text-secondary leading-relaxed">
                  I accept the <span className="text-saffron underline">Terms & Conditions</span>, Coverage Exclusions, and acknowledge that payouts require me to be actively on-duty.
                </p>
              </div>
              <Button className="w-full py-4">
                Pay ₹72 & Activate Coverage
              </Button>
              <p className="text-[10px] text-center text-text-secondary/50 flex items-center justify-center gap-1">
                <ShieldCheck className="w-3 h-3" /> Secure 256-bit encrypted payment
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

const ReferralsPage = () => {
  const [copied, setCopied] = useState(false);
  const referralCode = 'SAFAR915';

  const handleCopy = () => {
    navigator.clipboard.writeText(referralCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <Card className="saffron-gradient border-none p-10 text-center">
        <Users className="w-16 h-16 text-white mx-auto mb-6" />
        <h2 className="text-3xl font-bold text-white">Refer & Earn ₹50</h2>
        <p className="text-white/80 mt-2 max-w-md mx-auto">
          Invite your friends to SAFAR. You both get ₹50 when they complete their first weekly coverage.
        </p>
        
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <div className="bg-white/20 backdrop-blur-md rounded-xl px-6 py-4 flex items-center gap-4 border border-white/20">
            <span className="text-2xl font-mono font-bold tracking-widest text-white">{referralCode}</span>
            <button onClick={handleCopy} className="p-2 hover:bg-white/20 rounded-lg transition-all">
              {copied ? <CheckCircle2 className="w-5 h-5 text-green-300" /> : <Copy className="w-5 h-5 text-white" />}
            </button>
          </div>
          <Button className="bg-white text-saffron hover:bg-white/90 py-4 px-8">
            Share on WhatsApp
          </Button>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card title="Referral Stats">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-background/50 border border-card-border">
              <p className="text-xs text-text-secondary">Total Referrals</p>
              <p className="text-2xl font-bold text-text-primary mt-1">12</p>
            </div>
            <div className="p-4 rounded-2xl bg-background/50 border border-card-border">
              <p className="text-xs text-text-secondary">Earnings</p>
              <p className="text-2xl font-bold text-saffron mt-1">₹600</p>
            </div>
          </div>
        </Card>

        <Card title="Referral History">
          <div className="space-y-4">
            {[
              { name: 'Rahul K.', status: 'Completed', amount: '+₹50', date: 'Oct 15' },
              { name: 'Suresh M.', status: 'Pending', amount: '₹0', date: 'Oct 12' },
              { name: 'Amit P.', status: 'Completed', amount: '+₹50', date: 'Oct 10' },
            ].map((ref, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-background/50 flex items-center justify-center text-[10px] font-bold text-text-primary">
                    {ref.name[0]}
                  </div>
                  <div>
                    <p className="text-text-primary font-medium">{ref.name}</p>
                    <p className="text-[10px] text-text-secondary/50">{ref.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={cn('font-bold', ref.status === 'Completed' ? 'text-green-500' : 'text-text-secondary')}>{ref.amount}</p>
                  <p className="text-[10px] text-text-secondary/50">{ref.status}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

const ProfilePage = ({ userData, setUserData }: { userData: UserData; setUserData: (d: UserData) => void }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [tempData, setTempData] = useState(userData);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setUserData(tempData);
    localStorage.setItem('userData', JSON.stringify(tempData));
    setIsEditing(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-2xl space-y-8">
      <Card>
        <div className="flex flex-col items-center text-center pb-8 border-b border-card-border">
          <div className="relative group">
            <div className="w-24 h-24 saffron-gradient rounded-3xl flex items-center justify-center text-3xl font-bold text-white shadow-lg shadow-saffron/30">
              {userData.name ? userData.name[0] : 'U'}
            </div>
            <button className="absolute -bottom-2 -right-2 w-8 h-8 bg-card border border-card-border rounded-xl flex items-center justify-center hover:bg-background/50 transition-all">
              <User className="w-4 h-4 text-saffron" />
            </button>
          </div>
          <h2 className="text-2xl font-bold text-text-primary mt-6">{userData.name}</h2>
          <p className="text-text-secondary text-sm">Gig Partner since Oct 2025</p>
        </div>

        <div className="pt-8 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-text-primary">Personal Details</h3>
            <button 
              onClick={() => setIsEditing(!isEditing)}
              className="text-sm text-saffron hover:underline"
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input 
              label="Full Name" 
              value={tempData.name} 
              disabled={!isEditing}
              onChange={(e) => setTempData({ ...tempData, name: e.target.value })}
            />
            <Input 
              label="Phone Number" 
              value={tempData.phone} 
              disabled={true} 
            />
            <Input 
              label="Email Address" 
              value={tempData.email} 
              disabled={!isEditing}
              onChange={(e) => setTempData({ ...tempData, email: e.target.value })}
            />
            <Input 
              label="Work Zone" 
              value={tempData.zone} 
              disabled={!isEditing}
              onChange={(e) => setTempData({ ...tempData, zone: e.target.value })}
            />
          </div>

          {isEditing && (
            <Button onClick={handleSave} className="w-full py-4">
              Save Changes
            </Button>
          )}

          {saved && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 text-green-500 text-sm text-center"
            >
              Profile updated successfully!
            </motion.div>
          )}
        </div>
      </Card>

      <Card title="KYC Status">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 rounded-2xl bg-background/50 border border-card-border">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
              <span className="text-sm font-medium text-text-primary">PAN Verification</span>
            </div>
            <span className="text-xs text-text-secondary">{userData.pan}</span>
          </div>
          <div className="flex items-center justify-between p-4 rounded-2xl bg-background/50 border border-card-border">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
              <span className="text-sm font-medium text-text-primary">Aadhaar Verification</span>
            </div>
            <span className="text-xs text-text-secondary">XXXX XXXX {userData.aadhaar.slice(-4)}</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

const ClaimsPage = () => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Claims & Payouts</h2>
          <p className="text-text-secondary text-sm">Track your parametric insurance payouts</p>
        </div>
        <Button variant="outline" className="text-xs">
          How it works?
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlowCard className="border-none bg-white/5 backdrop-blur-sm">
          <p className="text-text-secondary text-[10px] font-bold uppercase tracking-widest">Active Claims</p>
          <h2 className="text-3xl font-bold text-white mt-1">1</h2>
          <p className="text-[10px] text-saffron font-bold mt-4 uppercase">Processing...</p>
        </GlowCard>
        <GlowCard className="border-none bg-white/5 backdrop-blur-sm">
          <p className="text-text-secondary text-[10px] font-bold uppercase tracking-widest">Total Payouts</p>
          <h2 className="text-3xl font-bold text-white mt-1">₹1,200</h2>
          <p className="text-[10px] text-green-500 font-bold mt-4 uppercase">3 claims settled</p>
        </GlowCard>
        <GlowCard className="border-none bg-white/5 backdrop-blur-sm">
          <p className="text-text-secondary text-[10px] font-bold uppercase tracking-widest">Avg. Settlement</p>
          <h2 className="text-3xl font-bold text-white mt-1">₹400</h2>
          <p className="text-[10px] text-text-secondary/50 font-bold mt-4 uppercase">Per event</p>
        </GlowCard>
      </div>

      <Card title="Claims History">
        <div className="space-y-4">
          {[
            { id: 'CLM-9821', event: 'Extreme Heat (>42°C)', date: 'Oct 12, 2025', amount: '₹400', status: 'Settled' },
            { id: 'CLM-9810', event: 'Heavy Rainfall', date: 'Oct 05, 2025', amount: '₹400', status: 'Settled' },
            { id: 'CLM-9799', event: 'Extreme Heat (>42°C)', date: 'Sep 28, 2025', amount: '₹400', status: 'Settled' },
            { id: 'CLM-9844', event: 'High AQI (>350)', date: 'Oct 18, 2025', amount: '₹400', status: 'Processing' },
          ].map((claim, i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-background/50 border border-transparent hover:border-card-border transition-all">
              <div className="flex items-center gap-4">
                <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center', claim.status === 'Settled' ? 'bg-green-500/10 text-green-500' : 'bg-saffron/10 text-saffron')}>
                  {claim.status === 'Settled' ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                </div>
                <div>
                  <p className="text-sm font-medium text-text-primary">{claim.event}</p>
                  <p className="text-xs text-text-secondary">{claim.id} • {claim.date}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-text-primary">{claim.amount}</p>
                <p className={cn('text-[10px] font-medium px-2 py-0.5 rounded-full inline-block', 
                  claim.status === 'Settled' ? 'bg-green-500/10 text-green-500' : 'bg-saffron/10 text-saffron'
                )}>
                  {claim.status}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

const WeatherPage = ({ userData }: { userData: UserData }) => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Zone Weather</h2>
          <p className="text-text-secondary text-sm">Real-time monitoring and zone analysis</p>
        </div>
        <div className="flex items-center gap-2 bg-background/50 px-4 py-2 rounded-xl border border-card-border">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs font-medium text-text-secondary">Live Monitoring</span>
        </div>
      </div>

      {/* NEW: Interactive Weather Map Section */}
      <WeatherMap />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <GlowCard className="lg:col-span-2 border-none">
           <div className="flex items-center justify-between mb-8">
            <h3 className="text-lg font-semibold text-white">Weather Forecast</h3>
          </div>
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 saffron-gradient rounded-3xl flex items-center justify-center shadow-lg shadow-saffron/30">
                  <CloudSun className="w-10 h-10 text-white" />
                </div>
                <div>
                  <h3 className="text-4xl font-bold text-white">32°C</h3>
                  <p className="text-text-secondary">Haze • Delhi NCR - Zone A</p>
                </div>
              </div>
              <div className="text-right">
                <div className="bg-red-500/10 border border-red-500/20 px-4 py-2 rounded-xl">
                  <p className="text-xs text-red-500 font-medium uppercase tracking-wider">AQI Level</p>
                  <p className="text-2xl font-bold text-red-500">342</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Humidity', value: '45%', icon: CloudSun },
                { label: 'Wind', value: '12 km/h', icon: CloudSun },
                { label: 'Rain Chance', value: '5%', icon: CloudSun },
                { label: 'Visibility', value: '2.5 km', icon: CloudSun },
              ].map((stat, i) => (
                <div key={i} className="bg-white/5 rounded-2xl p-4 border border-white/5">
                  <p className="text-[10px] text-text-secondary uppercase font-bold">{stat.label}</p>
                  <p className="text-lg font-bold text-white mt-1">{stat.value}</p>
                </div>
              ))}
            </div>

            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-text-secondary">7-Day Forecast</h4>
              <div className="space-y-2">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
                  <div key={day} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-transparent hover:border-white/5 transition-all">
                    <span className="w-12 text-sm font-medium text-text-secondary">{day}</span>
                    <CloudSun className="w-5 h-5 text-saffron" />
                    <div className="flex-1 mx-8 h-1.5 bg-white/5 rounded-full overflow-hidden relative">
                      <div className="absolute top-0 left-1/4 right-1/4 h-full saffron-gradient" />
                    </div>
                    <span className="text-sm font-bold text-white">34° / 26°</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </GlowCard>

        <div className="space-y-6">
          <Card title="Risk Indicators">
            <div className="space-y-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Heat Risk</span>
                  <span className="text-xs font-bold text-saffron">Medium</span>
                </div>
                <div className="h-2 bg-card-border rounded-full overflow-hidden">
                  <div className="h-full bg-saffron w-[60%]" />
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Rain Risk</span>
                  <span className="text-xs font-bold text-green-500">Low</span>
                </div>
                <div className="h-2 bg-card-border rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 w-[15%]" />
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Pollution Risk</span>
                  <span className="text-xs font-bold text-red-500">High</span>
                </div>
                <div className="h-2 bg-card-border rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[85%]" />
                </div>
              </div>
            </div>
          </Card>

          <Card className="bg-saffron/5 border-saffron/20">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-saffron shrink-0" />
              <div>
                <p className="text-sm font-bold text-saffron">Parametric Trigger</p>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  If AQI stays above 350 for more than 4 hours tomorrow, a payout of ₹400 will be automatically credited to your wallet.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const SupportPage = () => {
  const [activeFaq, setActiveFaq] = useState<number | null>(0);
  const [submitted, setSubmitted] = useState(false);

  const faqs = [
    { q: 'How do weather payouts work?', a: 'Payouts are automatically triggered when weather sensors in your zone detect extreme conditions (Heat > 42°C, AQI > 400, or Heavy Rain). No manual claim filing is required.' },
    { q: 'When is the premium deducted?', a: 'Premiums are deducted every Monday for the upcoming week. You can pay via UPI, Card, or your SAFAR wallet.' },
    { q: 'Can I cancel my coverage?', a: 'Yes, you can opt-out of the next week\'s coverage anytime before Sunday midnight.' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl">
      <div className="space-y-8">
        <Card title="Frequently Asked Questions">
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-card-border rounded-xl overflow-hidden">
                <button 
                  onClick={() => setActiveFaq(activeFaq === i ? null : i)}
                  className="w-full p-4 flex items-center justify-between text-left hover:bg-background/50 transition-all"
                >
                  <span className="text-sm font-medium text-text-primary">{faq.q}</span>
                  <ChevronRight className={cn('w-4 h-4 text-text-secondary/40 transition-transform', activeFaq === i && 'rotate-90')} />
                </button>
                <AnimatePresence>
                  {activeFaq === i && (
                    <motion.div 
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="px-4 pb-4 text-xs text-text-secondary/40 leading-relaxed"
                    >
                      {faq.a}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Contact Support">
          {submitted ? (
            <div className="text-center py-10">
              <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
              <h3 className="text-lg font-bold text-text-primary">Message Sent!</h3>
              <p className="text-sm text-text-secondary/40 mt-2">Our team will get back to you within 2 hours.</p>
              <Button variant="ghost" onClick={() => setSubmitted(false)} className="mt-6 mx-auto">Send another message</Button>
            </div>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); setSubmitted(true); }} className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs text-text-secondary/40 ml-1">Issue Category</label>
                <select className="w-full bg-background/50 border border-card-border rounded-xl px-4 py-3 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-saffron/50 appearance-none">
                  <option>Payment Issue</option>
                  <option>Claim Dispute</option>
                  <option>App Technical Error</option>
                  <option>Other</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs text-text-secondary/40 ml-1">Message</label>
                <textarea 
                  rows={4}
                  placeholder="Describe your issue in detail..."
                  className="w-full bg-background/50 border border-card-border rounded-xl px-4 py-3 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-saffron/50 placeholder:text-text-secondary/20"
                />
              </div>
              <Button type="submit" className="w-full py-4">Send Message</Button>
            </form>
          )}
        </Card>
      </div>

      <div className="space-y-8">
        <Card title="Live Chat Support" className="h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 p-2">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg saffron-gradient flex items-center justify-center shrink-0">
                <ShieldCheck className="w-4 h-4 text-white" />
              </div>
              <div className="bg-background/50 rounded-2xl rounded-tl-none p-4 max-w-[80%] border border-card-border">
                <p className="text-xs text-text-primary/80 leading-relaxed">
                  Hi! I'm Safar Assistant. How can I help you today?
                </p>
                <p className="text-[10px] text-text-secondary/20 mt-2">10:30 AM</p>
              </div>
            </div>
            <div className="flex gap-3 flex-row-reverse">
              <div className="w-8 h-8 rounded-lg bg-background/50 flex items-center justify-center shrink-0 border border-card-border">
                <User className="w-4 h-4 text-text-primary" />
              </div>
              <div className="bg-saffron/10 rounded-2xl rounded-tr-none p-4 max-w-[80%] border border-saffron/20">
                <p className="text-xs text-text-primary/80 leading-relaxed">
                  I have a question about my claim payout.
                </p>
                <p className="text-[10px] text-text-secondary/20 mt-2">10:32 AM</p>
              </div>
            </div>
          </div>
          <div className="pt-4 border-t border-card-border">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Type your message..."
                className="w-full bg-background/50 border border-card-border rounded-xl pl-4 pr-12 py-3 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-saffron/50"
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-saffron hover:bg-saffron/10 rounded-lg transition-all">
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// --- Main App ---

const AppContent = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as 'light' | 'dark') || 'dark';
  });

  const [userData, setUserData] = useState<UserData>({
    name: '',
    phone: '',
    email: '',
    pan: '',
    aadhaar: '',
    platform: '',
    zone: 'Delhi NCR',
    dailyEarnings: 650,
    isBoarded: false
  });
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const savedData = localStorage.getItem('userData');
    if (savedData) {
      setUserData(JSON.parse(savedData));
    }

    const path = location.pathname.substring(1);
    if (path) setActiveTab(path);
    setIsSidebarOpen(false);
  }, [location]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

  if (!isLoggedIn && !['login', 'signup', 'otp'].includes(location.pathname.substring(1))) {
    return <Navigate to="/login" />;
  }

  if (isLoggedIn && !userData.isBoarded && location.pathname !== '/onboarding') {
    return <Navigate to="/onboarding" />;
  }

  const isAuthPage = ['login', 'signup', 'otp', 'onboarding'].includes(location.pathname.substring(1));

  if (isAuthPage) {
    return (
      <div className="relative bg-background min-h-screen scroll-smooth overflow-x-hidden">
        <div className="fixed top-6 right-6 z-50">
          <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
        </div>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/otp" element={<OTPPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
        </Routes>
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-background text-text-primary transition-colors relative overflow-x-hidden">
      {/* Global Background Blobs - Reduced even further for performance */}
      <div className="fixed top-[-20%] left-[-10%] w-[60%] h-[60%] bg-saffron/5 rounded-full blur-[30px] pointer-events-none -z-0 will-change-transform" />
      <div className="fixed bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/5 rounded-full blur-[30px] pointer-events-none -z-0 will-change-transform" />
      
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsSidebarOpen(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed inset-y-0 left-0 w-72 bg-card z-50 lg:hidden"
            >
              <div className="p-6 flex flex-col h-full">
                <div className="flex items-center justify-between mb-10">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 saffron-gradient rounded-xl flex items-center justify-center">
                      <ShieldCheck className="text-white w-6 h-6" />
                    </div>
                    <span className="text-2xl font-bold text-saffron">SAFAR</span>
                  </div>
                  <button onClick={() => setIsSidebarOpen(false)} className="p-2 text-text-secondary hover:text-text-primary transition-colors">
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <nav className="flex-1 space-y-1">
                  {[
                    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
                    { id: 'coverage', label: 'Coverage', icon: ShieldCheck, path: '/coverage' },
                    { id: 'claims', label: 'Claims', icon: FileText, path: '/claims' },
                    { id: 'weather', label: 'Zone Weather', icon: CloudSun, path: '/weather' },
                    { id: 'referrals', label: 'Referrals', icon: Users, path: '/referrals' },
                    { id: 'profile', label: 'Profile', icon: User, path: '/profile' },
                    { id: 'support', label: 'Support', icon: HelpCircle, path: '/support' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        navigate(item.path);
                        setIsSidebarOpen(false);
                      }}
                      className={cn(
                        'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all',
                        activeTab === item.id 
                          ? 'bg-saffron/10 text-saffron' 
                          : 'text-text-secondary hover:text-text-primary hover:bg-background/50'
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </button>
                  ))}
                </nav>

                <button 
                  onClick={() => {
                    localStorage.removeItem('isLoggedIn');
                    navigate('/login');
                  }}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-text-secondary hover:text-red-400 hover:bg-red-400/5 transition-all mt-auto"
                >
                  <LogOut className="w-5 h-5" />
                  <span className="font-medium">Logout</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <div className="flex-1 flex flex-col min-w-0 relative z-10">
        <TopBar 
          title={activeTab === 'weather' ? 'Zone Weather' : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} 
          userData={userData} 
          onMenuClick={() => setIsSidebarOpen(true)}
          theme={theme}
          toggleTheme={toggleTheme}
        />
        <main className="flex-1 p-6 lg:p-10">
          {/* Top Insight Bar */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 flex items-center gap-3 bg-saffron/5 border border-saffron/20 px-4 py-2 rounded-2xl backdrop-blur-md w-fit mx-auto lg:mx-0"
          >
            <div className="w-2 h-2 rounded-full bg-saffron animate-ping" />
            <span className="text-[10px] sm:text-xs font-bold text-saffron uppercase tracking-[0.2em]">
              Smart Insight: Your risk premium may increase tomorrow due to AQI spike
            </span>
          </motion.div>

          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Routes>
                <Route path="/dashboard" element={<DashboardPage userData={userData} />} />
                <Route path="/coverage" element={<CoveragePage userData={userData} />} />
                <Route path="/claims" element={<ClaimsPage />} />
                <Route path="/weather" element={<WeatherPage userData={userData} />} />
                <Route path="/referrals" element={<ReferralsPage />} />
                <Route path="/profile" element={<ProfilePage userData={userData} setUserData={setUserData} />} />
                <Route path="/support" element={<SupportPage />} />
                <Route path="*" element={<Navigate to="/dashboard" />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
