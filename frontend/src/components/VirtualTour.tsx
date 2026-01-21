'use client';

import React, { useState } from 'react';
import { X, Map, ChevronRight } from 'lucide-react';
import Image from 'next/image';

const VirtualTour = () => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            <button
                onClick={() => setIsOpen(true)}
                className="group bg-white/20 hover:bg-white/30 backdrop-blur-md border border-white/50 text-white font-bold py-3 px-8 rounded-full transition-all duration-300 flex items-center gap-3 hover:scale-105 hover:shadow-lg"
            >
                <Map className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                <span>KHÁM PHÁ CAMPUS</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm animate-fade-in p-4">
                    <div className="bg-white rounded-xl overflow-hidden max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl animate-modal-appear">
                        {/* Header */}
                        <div className="p-4 border-b flex justify-between items-center bg-school-red text-white">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <Map className="w-5 h-5" />
                                THAM QUAN TRƯỜNG ĐẠI HỌC AN NINH NHÂN DÂN
                            </h3>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-1 hover:bg-white/20 rounded-full transition-colors"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        {/* Content using NEXT IMAGE for optimization */}
                        <div className="relative flex-1 bg-gray-100 min-h-[400px] flex items-center justify-center p-4">
                            <div className="relative w-full h-full min-h-[400px]">
                                <Image
                                    src="/assests/campus_3d.png"
                                    alt="3D Campus Map"
                                    fill
                                    className="object-contain"
                                    priority
                                />
                            </div>
                            <div className="absolute bottom-6 bg-black/60 text-white px-4 py-2 rounded-full text-sm font-medium backdrop-blur-sm">
                                Góc nhìn tổng quan khuôn viên T04
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 bg-gray-50 border-t text-center text-gray-500 text-sm">
                            Sử dụng chuột để quan sát chi tiết
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default VirtualTour;
