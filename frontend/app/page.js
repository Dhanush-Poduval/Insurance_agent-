'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { CloudRain, Wind, AlertTriangle, Zap, Shield, BarChart2, ArrowRight, Users, IndianRupee, Clock } from 'lucide-react';

const FEATURES = [
  { icon: CloudRain, title: 'Weather Protection', description: 'Auto-payouts when rainfall, storms, or floods disrupt your rides', color: 'blue' },
  { icon: Wind, title: 'Pollution Coverage', description: 'Compensation when AQI spikes make delivery unsafe', color: 'orange' },
  { icon: AlertTriangle, title: 'Policy Restrictions', description: 'Coverage when odd-even rules or curfews reduce earnings', color: 'red' },
  { icon: Zap, title: 'Instant Payouts', description: 'No claim forms — payouts trigger automatically via smart contracts', color: 'green' },
];

const STATS = [
  { icon: Users, value: '1,000+', label: 'Workers Protected' },
  { icon: IndianRupee, value: '₹50L+', label: 'Paid Out' },
  { icon: Clock, value: '24/7', label: 'Monitoring' },
];

const colorMap = {
  blue: { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-600 dark:text-blue-400' },
  orange: { bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-600 dark:text-orange-400' },
  red: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-600 dark:text-red-400' },
  green: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-600 dark:text-green-400' },
};

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white py-24 px-4">
        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm mb-6">
              <Zap className="w-4 h-4 text-yellow-300" />
              <span>Parametric Insurance — Claims without paperwork</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6">
              Instant Insurance<br />
              <span className="text-blue-200">for Gig Workers</span>
            </h1>
            <p className="text-lg sm:text-xl text-blue-100 max-w-2xl mx-auto mb-10 leading-relaxed">
              Protect your earnings from weather disruptions, pollution alerts, and operational restrictions.
              Automatic payouts. No paperwork. No waiting.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/worker"
                className="flex items-center gap-2 bg-white text-blue-700 font-bold px-8 py-3.5 rounded-xl hover:bg-blue-50 transition-colors shadow-lg"
              >
                <Shield className="w-5 h-5" />
                Worker Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/admin"
                className="flex items-center gap-2 bg-white/10 backdrop-blur-sm text-white font-bold px-8 py-3.5 rounded-xl hover:bg-white/20 transition-colors border border-white/20"
              >
                <BarChart2 className="w-5 h-5" />
                Admin Dashboard
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-10 grid grid-cols-3 gap-8">
          {STATS.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.1 }} className="text-center">
                <Icon className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                <p className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">Complete Protection Coverage</h2>
            <p className="text-gray-500 text-lg max-w-xl mx-auto">Everything you need to protect your gig earnings, automatically.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              const { bg, text } = colorMap[feature.color];
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * i }}
                  className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100 dark:border-gray-700"
                >
                  <div className={`inline-flex p-3 rounded-xl mb-4 ${bg}`}>
                    <Icon className={`w-6 h-6 ${text}`} />
                  </div>
                  <h3 className="font-bold text-gray-900 dark:text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-blue-600 text-white text-center">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <h2 className="text-3xl font-bold mb-4">Ready to protect your income?</h2>
          <p className="text-blue-100 mb-8 text-lg">Join 1,000+ gig workers already protected by InsureGig</p>
          <Link href="/worker" className="inline-flex items-center gap-2 bg-white text-blue-700 font-bold px-8 py-3.5 rounded-xl hover:bg-blue-50 transition-colors shadow-lg">
            Get Started — ₹149/week
            <ArrowRight className="w-4 h-4" />
          </Link>
        </motion.div>
      </section>
    </div>
  );
}
