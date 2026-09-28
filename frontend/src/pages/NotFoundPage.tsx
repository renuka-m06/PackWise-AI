import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Compass } from 'lucide-react';
import { Button } from '../components/Button';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="py-20 flex flex-col items-center justify-center text-center space-y-4 max-w-md mx-auto">
      <div className="w-14 h-14 rounded-lg bg-sand-100 border border-sand-300 flex items-center justify-center text-olive">
        <Compass className="w-7 h-7" />
      </div>
      <h1 className="text-2xl font-bold text-charcoal">404 — Page Not Found</h1>
      <p className="text-xs text-warmgray leading-relaxed">
        The requested routing destination does not exist within the PackWise packaging intelligence system.
      </p>
      <Link to="/">
        <Button variant="primary" size="md">
          <ArrowLeft className="w-4 h-4 mr-1" /> Return to Dashboard
        </Button>
      </Link>
    </div>
  );
};
