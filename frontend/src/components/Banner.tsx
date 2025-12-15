'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { ChevronLeft, ChevronRight, MessageCircle } from 'lucide-react';
import { BANNER_SLIDES } from '@/data/constants';

const Banner = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = BANNER_SLIDES;

  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  }, [slides.length]);

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  // Auto-play slideshow
  useEffect(() => {
    const timer = setInterval(nextSlide, 5000);
    return () => clearInterval(timer);
  }, [nextSlide]);

  return (
    <div className="relative w-full h-96 bg-gradient-to-r from-red-600 to-red-700 overflow-hidden">
      {/* Slide Content */}
      <div className="relative w-full h-full flex items-center">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            {/* Text Content */}
            <div className="text-white space-y-4">
              <div className="inline-block bg-yellow-500 text-red-800 px-4 py-2 rounded-lg font-bold text-lg">
                {slides[currentSlide].title}
              </div>
              <h2 className="text-2xl lg:text-3xl font-bold leading-tight">
                {slides[currentSlide].subtitle}
              </h2>
              <p className="text-lg text-yellow-100">
                {slides[currentSlide].description}
              </p>
              <div className="flex flex-wrap gap-3 mt-6">
                <Link 
                  href="/tuyen-sinh"
                  className="bg-yellow-500 hover:bg-yellow-400 text-red-800 font-bold py-2 px-6 rounded-lg transition-colors duration-200"
                >
                  Xem chi tiết
                </Link>
                <Link 
                  href="/chat-bot"
                  className="flex items-center gap-2 border-2 border-white text-white hover:bg-white hover:text-red-700 font-bold py-2 px-6 rounded-lg transition-colors duration-200"
                >
                  <MessageCircle className="w-5 h-5" />
                  Hỏi đáp AI
                </Link>
              </div>
            </div>

            {/* Image */}
            <div className="hidden lg:block">
              <div className="w-full h-64 rounded-lg shadow-xl overflow-hidden">
                <img 
                  src="/assests/t04_1.jpg" 
                  alt="Hình ảnh sự kiện" 
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Arrows */}
      <button
        onClick={prevSlide}
        className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-2 rounded-full transition-all duration-200"
      >
        <ChevronLeft className="w-6 h-6" />
      </button>
      <button
        onClick={nextSlide}
        className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 hover:bg-opacity-75 text-white p-2 rounded-full transition-all duration-200"
      >
        <ChevronRight className="w-6 h-6" />
      </button>

      {/* Slide Indicators */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-3 h-3 rounded-full transition-all duration-200 ${
              index === currentSlide ? 'bg-yellow-400' : 'bg-white bg-opacity-50'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

export default Banner;
