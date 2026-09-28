import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { StatusBanner } from '../components/StatusBanner';

export const MainLayout: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-offwhite text-charcoal selection:bg-olive selection:text-white">
      <StatusBanner />
      <Navbar />
      <main className="flex-grow max-w-[1280px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
