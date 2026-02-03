'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronRight, MessageCircle, ArrowRight } from 'lucide-react';
import { BANNER_SLIDES } from '@/data/constants';

const Banner = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const slides = BANNER_SLIDES;

  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  }, [slides.length]);

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  // Auto-play slideshow
  useEffect(() => {
    if (!isHovered) {
      const timer = setInterval(nextSlide, 6000);
      return () => clearInterval(timer);
    }
  }, [nextSlide, isHovered]);

  return (
    <div
      className="relative w-full h-[600px] overflow-hidden group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 3D Background Image - Static for now, can be dynamic per slide if we generate more */}
      <div className="absolute inset-0 w-full h-full">
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/50 to-transparent z-10" />
        <img
          src="/assests/campus_3d.png"
          alt="Truong Dai hoc An ninh Nhan dan"
          className="w-full h-full object-cover transform scale-105 animate-slow-zoom"
        />
      </div>

      {/* Content Container */}
      <div className="relative z-20 w-full h-full flex items-center">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl">
            {/* Animated Text Content */}
            <div className="space-y-6 transition-all duration-500 ease-in-out">
              <div
                key={`badge-${currentSlide}`}
                className="inline-flex items-center space-x-2 bg-yellow-500/20 backdrop-blur-md border border-yellow-500/50 text-yellow-400 px-4 py-1.5 rounded-full font-bold text-sm tracking-wide uppercase animate-fade-in-up"
              >
                <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></span>
                <span>{slides[currentSlide].title}</span>
              </div>

              <h2
                key={`title-${currentSlide}`}
                className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight animate-fade-in-up delay-100"
              >
                {slides[currentSlide].subtitle}
              </h2>

              <p
                key={`desc-${currentSlide}`}
                className="text-lg md:text-xl text-gray-200 leading-relaxed max-w-2xl animate-fade-in-up delay-200"
              >
                {slides[currentSlide].description}
              </p>

              <div className="flex flex-wrap gap-4 pt-4 animate-fade-in-up delay-300">
                <Link
                  href="/admin/dashboard"
                  className="group relative bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-8 rounded-full transition-all duration-300 hover:shadow-[0_0_20px_rgba(220,38,38,0.5)] hover:-translate-y-1 overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    Quản Trị Viên
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-red-800 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Link>

                <Link
                  href="/chat-bot"
                  className="group flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/30 hover:bg-white/20 text-white font-bold py-3 px-8 rounded-full transition-all duration-300 hover:shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:-translate-y-1"
                >
                  <MessageCircle className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                  Hỏi đáp AI
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Arrows */}
      <button
        onClick={prevSlide}
        className="absolute left-4 lg:left-8 top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-red-700/80 backdrop-blur-sm text-white p-3 rounded-full transition-all duration-300 hover:scale-110 border border-white/10 group-hover:opacity-100 opacity-0 z-30"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      <button
        onClick={nextSlide}
        className="absolute right-4 lg:right-8 top-1/2 transform -translate-y-1/2 bg-black/30 hover:bg-red-700/80 backdrop-blur-sm text-white p-3 rounded-full transition-all duration-300 hover:scale-110 border border-white/10 group-hover:opacity-100 opacity-0 z-30"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* Visual Slide Indicators */}
      <div className="absolute bottom-8 left-0 right-0 z-30">
        <div className="container mx-auto px-4">
          <div className="flex items-center gap-2">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`group relative h-1 rounded-full transition-all duration-500 ${index === currentSlide ? 'w-12 bg-yellow-500' : 'w-4 bg-white/50 hover:bg-white/80'
                  }`}
              >
                <span className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap pointer-events-none mb-1">
                  Slide {index + 1}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Decorative Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#f9fafb] to-transparent z-20 pointer-events-none" />

      {/* Styles for animation */}
      <style jsx>{`
        @keyframes slow-zoom {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
        .animate-slow-zoom {
          animation: slow-zoom 20s infinite ease-in-out alternate;
        }
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .delay-100 { animation-delay: 0.1s; }
        .delay-200 { animation-delay: 0.2s; }
        .delay-300 { animation-delay: 0.3s; }
      `}</style>
    </div>
  );
};

export default Banner;
