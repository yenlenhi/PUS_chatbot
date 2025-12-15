'use client';

import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, FileText, Download, Clock, MapPin, CheckCircle, AlertCircle, X, ArrowRight } from 'lucide-react';

// Types for Guided Flow
export interface FlowStep {
  id: string;
  question: string;
  questionEn?: string;
  options: FlowOption[];
  type: 'single' | 'multi' | 'info';
}

export interface FlowOption {
  id: string;
  label: string;
  labelEn?: string;
  description?: string;
  descriptionEn?: string;
  nextStep?: string; // ID of next step, null means end
  value?: string;
}

export interface FlowResult {
  title: string;
  titleEn?: string;
  requirements: string[];
  requirementsEn?: string[];
  location: string;
  locationEn?: string;
  processingTime: string;
  processingTimeEn?: string;
  notes?: string[];
  notesEn?: string[];
  downloadLinks?: { label: string; labelEn?: string; url: string }[];
}

export interface GuidedFlowConfig {
  id: string;
  title: string;
  titleEn?: string;
  description: string;
  descriptionEn?: string;
  icon: React.ReactNode;
  steps: FlowStep[];
  getResult: (answers: Record<string, string>) => FlowResult;
}

// Flow configurations
export const GUIDED_FLOWS: GuidedFlowConfig[] = [
  {
    id: 'student-confirmation',
    title: 'Xin giấy xác nhận sinh viên',
    titleEn: 'Request Student Confirmation Letter',
    description: 'Hướng dẫn thủ tục xin các loại giấy xác nhận',
    descriptionEn: 'Guide for requesting confirmation letters',
    icon: <FileText className="w-5 h-5" />,
    steps: [
      {
        id: 'confirmation-type',
        question: 'Bạn cần loại giấy xác nhận nào?',
        questionEn: 'What type of confirmation do you need?',
        type: 'single',
        options: [
          {
            id: 'study-status',
            label: 'Xác nhận đang học',
            labelEn: 'Enrollment Confirmation',
            description: 'Dùng cho vay vốn, miễn giảm, ưu tiên...',
            descriptionEn: 'For loans, discounts, priority...',
            nextStep: 'education-type',
          },
          {
            id: 'graduation',
            label: 'Xác nhận tốt nghiệp',
            labelEn: 'Graduation Confirmation',
            description: 'Dùng cho xin việc, học tiếp...',
            descriptionEn: 'For job applications, further study...',
            nextStep: 'education-type',
          },
          {
            id: 'transcript',
            label: 'Bảng điểm / Kết quả học tập',
            labelEn: 'Transcript / Academic Results',
            description: 'Bảng điểm tạm thời hoặc chính thức',
            descriptionEn: 'Temporary or official transcript',
            nextStep: 'education-type',
          },
          {
            id: 'other',
            label: 'Giấy xác nhận khác',
            labelEn: 'Other Confirmation',
            description: 'Xác nhận vay vốn, BHYT, quân sự...',
            descriptionEn: 'Loan, insurance, military confirmation...',
            nextStep: 'education-type',
          },
        ],
      },
      {
        id: 'education-type',
        question: 'Bạn đang học hệ đào tạo nào?',
        questionEn: 'What education program are you in?',
        type: 'single',
        options: [
          {
            id: 'regular',
            label: 'Chính quy',
            labelEn: 'Regular Program',
            nextStep: 'result',
          },
          {
            id: 'second-degree',
            label: 'Văn bằng 2',
            labelEn: 'Second Degree',
            nextStep: 'result',
          },
          {
            id: 'continuing',
            label: 'Liên thông',
            labelEn: 'Continuing Education',
            nextStep: 'result',
          },
          {
            id: 'postgrad',
            label: 'Sau đại học',
            labelEn: 'Postgraduate',
            nextStep: 'result',
          },
        ],
      },
    ],
    getResult: (answers) => {
      const confirmationType = answers['confirmation-type'];
      const educationType = answers['education-type'];
      
      const baseResult: FlowResult = {
        title: 'Thủ tục xin giấy xác nhận sinh viên',
        titleEn: 'Student Confirmation Letter Procedure',
        requirements: [
          'Thẻ học viên / Thẻ sinh viên (bản photo hoặc mang theo bản gốc)',
          'Đơn xin cấp giấy xác nhận (theo mẫu)',
          'CMND/CCCD (bản photo)',
        ],
        requirementsEn: [
          'Student ID card (copy or original)',
          'Confirmation request form (template)',
          'National ID card (copy)',
        ],
        location: 'Phòng Quản lý học viên - Tầng 2, Nhà A1',
        locationEn: 'Student Management Office - 2nd Floor, Building A1',
        processingTime: '3-5 ngày làm việc',
        processingTimeEn: '3-5 working days',
        notes: [
          'Nộp hồ sơ vào các ngày thứ 2, 4, 6 (sáng: 8h-11h30)',
          'Nhận kết quả vào thứ 3, 5 (chiều: 14h-16h30)',
          'Phí cấp giấy: Miễn phí (lần đầu), 20.000đ/bản (từ lần 2)',
        ],
        notesEn: [
          'Submit documents on Monday, Wednesday, Friday (morning: 8am-11:30am)',
          'Collect results on Tuesday, Thursday (afternoon: 2pm-4:30pm)',
          'Fee: Free (first time), 20,000 VND/copy (from 2nd time)',
        ],
        downloadLinks: [
          {
            label: 'Tải mẫu đơn xin giấy xác nhận',
            labelEn: 'Download Confirmation Request Form',
            url: '/documents/mau-don-xin-giay-xac-nhan.pdf',
          },
        ],
      };

      // Customize based on confirmation type
      if (confirmationType === 'transcript') {
        baseResult.requirements.push('Đóng lệ phí in bảng điểm (nếu có)');
        baseResult.requirementsEn?.push('Pay transcript printing fee (if applicable)');
        baseResult.processingTime = '5-7 ngày làm việc';
        baseResult.processingTimeEn = '5-7 working days';
      }

      if (confirmationType === 'graduation') {
        baseResult.requirements.push('Bản photo bằng tốt nghiệp (nếu đã nhận)');
        baseResult.requirementsEn?.push('Copy of graduation certificate (if received)');
      }

      // Customize based on education type
      if (educationType === 'postgrad') {
        baseResult.location = 'Phòng Đào tạo Sau đại học - Tầng 3, Nhà A1';
        baseResult.locationEn = 'Postgraduate Training Office - 3rd Floor, Building A1';
      }

      return baseResult;
    },
  },
  {
    id: 'temporary-leave',
    title: 'Xin nghỉ học tạm thời',
    titleEn: 'Request Temporary Leave of Absence',
    description: 'Hướng dẫn thủ tục bảo lưu kết quả học tập',
    descriptionEn: 'Guide for academic leave and result preservation',
    icon: <Clock className="w-5 h-5" />,
    steps: [
      {
        id: 'leave-reason',
        question: 'Lý do bạn xin nghỉ học tạm thời?',
        questionEn: 'What is your reason for temporary leave?',
        type: 'single',
        options: [
          {
            id: 'health',
            label: 'Lý do sức khỏe',
            labelEn: 'Health Reasons',
            description: 'Bệnh tật, điều trị dài ngày...',
            descriptionEn: 'Illness, long-term treatment...',
            nextStep: 'leave-duration',
          },
          {
            id: 'family',
            label: 'Lý do gia đình',
            labelEn: 'Family Reasons',
            description: 'Hoàn cảnh gia đình khó khăn...',
            descriptionEn: 'Family difficulties...',
            nextStep: 'leave-duration',
          },
          {
            id: 'military',
            label: 'Thực hiện nghĩa vụ quân sự',
            labelEn: 'Military Service',
            description: 'Nhập ngũ theo quy định',
            descriptionEn: 'Enlistment as required',
            nextStep: 'leave-duration',
          },
          {
            id: 'other',
            label: 'Lý do khác',
            labelEn: 'Other Reasons',
            description: 'Lý do cá nhân, tài chính...',
            descriptionEn: 'Personal, financial reasons...',
            nextStep: 'leave-duration',
          },
        ],
      },
      {
        id: 'leave-duration',
        question: 'Bạn dự kiến nghỉ trong bao lâu?',
        questionEn: 'How long do you plan to take leave?',
        type: 'single',
        options: [
          {
            id: '1-semester',
            label: '1 học kỳ',
            labelEn: '1 semester',
            nextStep: 'result',
          },
          {
            id: '2-semesters',
            label: '2 học kỳ (1 năm)',
            labelEn: '2 semesters (1 year)',
            nextStep: 'result',
          },
          {
            id: 'more',
            label: 'Trên 1 năm',
            labelEn: 'More than 1 year',
            nextStep: 'result',
          },
        ],
      },
    ],
    getResult: (answers) => {
      const reason = answers['leave-reason'];
      const duration = answers['leave-duration'];
      
      const baseResult: FlowResult = {
        title: 'Thủ tục xin nghỉ học tạm thời / Bảo lưu',
        titleEn: 'Temporary Leave / Academic Preservation Procedure',
        requirements: [
          'Đơn xin nghỉ học tạm thời (theo mẫu)',
          'Thẻ học viên / Thẻ sinh viên',
          'CMND/CCCD (bản photo)',
          'Xác nhận của gia đình (có chữ ký phụ huynh)',
        ],
        requirementsEn: [
          'Temporary leave application form (template)',
          'Student ID card',
          'National ID card (copy)',
          'Family confirmation (parent signature)',
        ],
        location: 'Phòng Quản lý học viên - Tầng 2, Nhà A1',
        locationEn: 'Student Management Office - 2nd Floor, Building A1',
        processingTime: '7-10 ngày làm việc',
        processingTimeEn: '7-10 working days',
        notes: [
          'Thời hạn bảo lưu tối đa: 2 năm',
          'Phải hoàn thành nghĩa vụ học phí trước khi bảo lưu',
          'Khi quay lại học cần đăng ký trước 2 tuần',
          'Hết thời hạn bảo lưu mà không quay lại sẽ bị xóa tên',
        ],
        notesEn: [
          'Maximum preservation period: 2 years',
          'Must complete tuition payment before preservation',
          'Must register 2 weeks before returning',
          'Name will be removed if not returning after preservation period',
        ],
        downloadLinks: [
          {
            label: 'Tải mẫu đơn xin nghỉ học tạm thời',
            labelEn: 'Download Temporary Leave Form',
            url: '/documents/mau-don-nghi-hoc-tam-thoi.pdf',
          },
          {
            label: 'Tải mẫu cam kết của gia đình',
            labelEn: 'Download Family Commitment Form',
            url: '/documents/mau-cam-ket-gia-dinh.pdf',
          },
        ],
      };

      // Customize based on reason
      if (reason === 'health') {
        baseResult.requirements.push('Giấy xác nhận của cơ sở y tế (bệnh viện cấp huyện trở lên)');
        baseResult.requirementsEn?.push('Medical confirmation from healthcare facility (district hospital or higher)');
      }

      if (reason === 'military') {
        baseResult.requirements.push('Giấy gọi nhập ngũ hoặc xác nhận của Ban CHQS địa phương');
        baseResult.requirementsEn?.push('Military enlistment notice or local military command confirmation');
        baseResult.notes?.push('Thời gian nghỉ được tính theo thời gian thực hiện nghĩa vụ');
        baseResult.notesEn?.push('Leave period calculated based on service duration');
      }

      // Customize based on duration
      if (duration === 'more') {
        baseResult.notes?.unshift('⚠️ Lưu ý: Nghỉ trên 1 năm cần được Hiệu trưởng phê duyệt');
        baseResult.notesEn?.unshift('⚠️ Note: Leave over 1 year requires Principal approval');
      }

      return baseResult;
    },
  },
  {
    id: 'tuition-payment',
    title: 'Đóng học phí',
    titleEn: 'Tuition Payment',
    description: 'Hướng dẫn các hình thức đóng học phí',
    descriptionEn: 'Guide for tuition payment methods',
    icon: <FileText className="w-5 h-5" />,
    steps: [
      {
        id: 'payment-method',
        question: 'Bạn muốn đóng học phí theo hình thức nào?',
        questionEn: 'How would you like to pay tuition?',
        type: 'single',
        options: [
          {
            id: 'bank-transfer',
            label: 'Chuyển khoản ngân hàng',
            labelEn: 'Bank Transfer',
            description: 'Chuyển qua tài khoản ngân hàng của trường',
            descriptionEn: 'Transfer to school bank account',
            nextStep: 'result',
          },
          {
            id: 'cash',
            label: 'Nộp tiền mặt tại trường',
            labelEn: 'Cash Payment at School',
            description: 'Nộp trực tiếp tại phòng Tài vụ',
            descriptionEn: 'Pay directly at Finance Office',
            nextStep: 'result',
          },
          {
            id: 'online',
            label: 'Thanh toán online',
            labelEn: 'Online Payment',
            description: 'Qua cổng thanh toán điện tử',
            descriptionEn: 'Via electronic payment portal',
            nextStep: 'result',
          },
        ],
      },
    ],
    getResult: (answers) => {
      const method = answers['payment-method'];
      
      if (method === 'bank-transfer') {
        return {
          title: 'Hướng dẫn chuyển khoản học phí',
          titleEn: 'Bank Transfer Payment Guide',
          requirements: [
            'Tên TK: Trường Đại học An ninh Nhân dân',
            'Số TK: 1234567890123',
            'Ngân hàng: Vietcombank - Chi nhánh Hà Nội',
            'Nội dung CK: [Mã SV] - [Họ tên] - Học phí HK[X] năm [YYYY]',
          ],
          requirementsEn: [
            'Account Name: People\'s Security University',
            'Account Number: 1234567890123',
            'Bank: Vietcombank - Hanoi Branch',
            'Transfer content: [Student ID] - [Full name] - Tuition Semester[X] year [YYYY]',
          ],
          location: 'Chuyển khoản 24/7',
          locationEn: 'Transfer 24/7',
          processingTime: 'Xác nhận trong 1-2 ngày làm việc',
          processingTimeEn: 'Confirmation within 1-2 working days',
          notes: [
            'Giữ lại biên lai chuyển khoản để đối chiếu',
            'Kiểm tra trạng thái thanh toán trên cổng sinh viên sau 2 ngày',
            'Liên hệ phòng Tài vụ nếu sau 3 ngày chưa cập nhật',
          ],
          notesEn: [
            'Keep transfer receipt for verification',
            'Check payment status on student portal after 2 days',
            'Contact Finance Office if not updated after 3 days',
          ],
        };
      } else if (method === 'cash') {
        return {
          title: 'Hướng dẫn nộp tiền mặt',
          titleEn: 'Cash Payment Guide',
          requirements: [
            'Thẻ học viên / Thẻ sinh viên',
            'Số tiền học phí theo thông báo',
          ],
          requirementsEn: [
            'Student ID card',
            'Tuition amount as notified',
          ],
          location: 'Phòng Tài vụ - Tầng 1, Nhà A2',
          locationEn: 'Finance Office - 1st Floor, Building A2',
          processingTime: 'Xác nhận ngay sau khi nộp',
          processingTimeEn: 'Confirmed immediately after payment',
          notes: [
            'Thời gian làm việc: Thứ 2-6, 8h-11h30 và 14h-16h30',
            'Không thu tiền vào thứ 7, Chủ nhật và ngày lễ',
            'Nhận biên lai và giữ cẩn thận',
          ],
          notesEn: [
            'Working hours: Mon-Fri, 8am-11:30am and 2pm-4:30pm',
            'No collection on Saturday, Sunday and holidays',
            'Receive and keep receipt carefully',
          ],
        };
      } else {
        return {
          title: 'Hướng dẫn thanh toán online',
          titleEn: 'Online Payment Guide',
          requirements: [
            'Tài khoản cổng sinh viên',
            'Thẻ ngân hàng / Ví điện tử',
          ],
          requirementsEn: [
            'Student portal account',
            'Bank card / E-wallet',
          ],
          location: 'https://sinhvien.psu.edu.vn/thanhtoan',
          locationEn: 'https://sinhvien.psu.edu.vn/thanhtoan',
          processingTime: 'Xác nhận ngay lập tức',
          processingTimeEn: 'Confirmed immediately',
          notes: [
            'Hỗ trợ các ngân hàng: Vietcombank, BIDV, Techcombank, VPBank...',
            'Hỗ trợ ví: MoMo, ZaloPay, VNPay',
            'Phí giao dịch: Miễn phí',
          ],
          notesEn: [
            'Supported banks: Vietcombank, BIDV, Techcombank, VPBank...',
            'Supported wallets: MoMo, ZaloPay, VNPay',
            'Transaction fee: Free',
          ],
          downloadLinks: [
            {
              label: 'Hướng dẫn chi tiết thanh toán online',
              labelEn: 'Detailed Online Payment Guide',
              url: '/documents/huong-dan-thanh-toan-online.pdf',
            },
          ],
        };
      }
    },
  },
  {
    id: 'dorm-registration',
    title: 'Đăng ký ký túc xá',
    titleEn: 'Dormitory Registration',
    description: 'Hướng dẫn đăng ký chỗ ở nội trú',
    descriptionEn: 'Guide for dormitory registration',
    icon: <MapPin className="w-5 h-5" />,
    steps: [
      {
        id: 'student-type',
        question: 'Bạn là sinh viên/học viên năm mấy?',
        questionEn: 'What year student are you?',
        type: 'single',
        options: [
          {
            id: 'freshman',
            label: 'Sinh viên năm nhất (mới nhập học)',
            labelEn: 'Freshman (newly enrolled)',
            nextStep: 'result',
          },
          {
            id: 'current',
            label: 'Sinh viên các năm tiếp theo',
            labelEn: 'Continuing student',
            nextStep: 'result',
          },
        ],
      },
    ],
    getResult: (answers) => {
      const studentType = answers['student-type'];
      
      if (studentType === 'freshman') {
        return {
          title: 'Đăng ký KTX cho sinh viên năm nhất',
          titleEn: 'Dormitory Registration for Freshmen',
          requirements: [
            'Giấy báo nhập học',
            'CMND/CCCD (bản photo)',
            'Ảnh 3x4 (2 tấm)',
            'Đơn đăng ký ở KTX (theo mẫu)',
          ],
          requirementsEn: [
            'Admission notice',
            'National ID card (copy)',
            'Photo 3x4 (2 copies)',
            'Dormitory registration form (template)',
          ],
          location: 'Phòng Quản lý KTX - Khu KTX',
          locationEn: 'Dormitory Management Office - Dormitory Area',
          processingTime: 'Xếp phòng trong tuần nhập học',
          processingTimeEn: 'Room assignment during orientation week',
          notes: [
            'Ưu tiên sinh viên ở xa (cách trường trên 50km)',
            'Ưu tiên sinh viên thuộc diện chính sách',
            'Phí KTX: 300.000 - 500.000đ/tháng (tùy loại phòng)',
            'Đăng ký trong thời gian nhập học',
          ],
          notesEn: [
            'Priority for students from far away (over 50km)',
            'Priority for policy-beneficiary students',
            'Dormitory fee: 300,000 - 500,000 VND/month (depending on room type)',
            'Register during orientation period',
          ],
          downloadLinks: [
            {
              label: 'Tải đơn đăng ký KTX',
              labelEn: 'Download Dormitory Registration Form',
              url: '/documents/don-dang-ky-ktx.pdf',
            },
          ],
        };
      } else {
        return {
          title: 'Gia hạn KTX cho sinh viên các năm',
          titleEn: 'Dormitory Extension for Continuing Students',
          requirements: [
            'Đơn xin gia hạn ở KTX',
            'Thẻ sinh viên',
            'Biên lai đóng phí KTX kỳ trước',
          ],
          requirementsEn: [
            'Dormitory extension application',
            'Student ID card',
            'Previous semester dormitory fee receipt',
          ],
          location: 'Phòng Quản lý KTX - Khu KTX',
          locationEn: 'Dormitory Management Office - Dormitory Area',
          processingTime: 'Xác nhận trong 3-5 ngày',
          processingTimeEn: 'Confirmation within 3-5 days',
          notes: [
            'Đăng ký gia hạn trước khi học kỳ mới bắt đầu 2 tuần',
            'Sinh viên vi phạm nội quy có thể bị từ chối',
            'Ưu tiên sinh viên có thành tích học tập tốt',
          ],
          notesEn: [
            'Register for extension 2 weeks before new semester',
            'Students with rule violations may be rejected',
            'Priority for students with good academic performance',
          ],
          downloadLinks: [
            {
              label: 'Tải đơn gia hạn KTX',
              labelEn: 'Download Dormitory Extension Form',
              url: '/documents/don-gia-han-ktx.pdf',
            },
          ],
        };
      }
    },
  },
];

// Props for the component
interface GuidedFlowProps {
  language: 'vi' | 'en';
  onClose: () => void;
  onAskBot: (message: string) => void;
}

// Main GuidedFlow Component
const GuidedFlow: React.FC<GuidedFlowProps> = ({ language, onClose, onAskBot }) => {
  const [selectedFlow, setSelectedFlow] = useState<GuidedFlowConfig | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showResult, setShowResult] = useState(false);

  const handleSelectFlow = (flow: GuidedFlowConfig) => {
    setSelectedFlow(flow);
    setCurrentStepIndex(0);
    setAnswers({});
    setShowResult(false);
  };

  const handleSelectOption = (stepId: string, optionId: string, nextStep?: string) => {
    const newAnswers = { ...answers, [stepId]: optionId };
    setAnswers(newAnswers);

    if (nextStep === 'result' || !nextStep) {
      setShowResult(true);
    } else {
      // Find next step index
      const nextStepIndex = selectedFlow?.steps.findIndex(s => s.id === nextStep);
      if (nextStepIndex !== undefined && nextStepIndex >= 0) {
        setCurrentStepIndex(nextStepIndex);
      } else {
        setShowResult(true);
      }
    }
  };

  const handleBack = () => {
    if (showResult) {
      setShowResult(false);
      // Go back to last step
      if (selectedFlow && currentStepIndex > 0) {
        // Remove last answer
        const lastStepId = selectedFlow.steps[currentStepIndex].id;
        const newAnswers = { ...answers };
        delete newAnswers[lastStepId];
        setAnswers(newAnswers);
      }
    } else if (currentStepIndex > 0) {
      // Remove current answer and go back
      const currentStepId = selectedFlow?.steps[currentStepIndex].id;
      if (currentStepId) {
        const newAnswers = { ...answers };
        delete newAnswers[currentStepId];
        setAnswers(newAnswers);
      }
      setCurrentStepIndex(currentStepIndex - 1);
    } else {
      // Go back to flow selection
      setSelectedFlow(null);
    }
  };

  const handleReset = () => {
    setSelectedFlow(null);
    setCurrentStepIndex(0);
    setAnswers({});
    setShowResult(false);
  };

  const handleAskMore = (topic: string) => {
    onClose();
    onAskBot(topic);
  };

  // Render flow selection
  if (!selectedFlow) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">
                {language === 'vi' ? '🧭 Hướng dẫn thủ tục' : '🧭 Procedure Guide'}
              </h3>
              <p className="text-blue-100 text-sm mt-1">
                {language === 'vi' 
                  ? 'Chọn thủ tục bạn cần thực hiện' 
                  : 'Select the procedure you need'}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              title={language === 'vi' ? 'Đóng' : 'Close'}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="p-4 space-y-3">
          {GUIDED_FLOWS.map((flow) => (
            <button
              key={flow.id}
              onClick={() => handleSelectFlow(flow)}
              className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-xl transition-all duration-200 text-left group"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-blue-100 group-hover:bg-blue-200 rounded-xl flex items-center justify-center text-blue-600 transition-colors">
                {flow.icon}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 group-hover:text-blue-700 transition-colors">
                  {language === 'vi' ? flow.title : (flow.titleEn || flow.title)}
                </h4>
                <p className="text-sm text-gray-500 mt-0.5 truncate">
                  {language === 'vi' ? flow.description : (flow.descriptionEn || flow.description)}
                </p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
            </button>
          ))}
        </div>

        <div className="px-4 pb-4">
          <p className="text-xs text-gray-500 text-center">
            {language === 'vi' 
              ? '💡 Hoặc bạn có thể chat trực tiếp với bot để được hỗ trợ'
              : '💡 Or you can chat directly with the bot for assistance'}
          </p>
        </div>
      </div>
    );
  }

  // Render result
  if (showResult && selectedFlow) {
    const result = selectedFlow.getResult(answers);
    
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-6 h-6" />
              <div>
                <h3 className="font-semibold">
                  {language === 'vi' ? result.title : (result.titleEn || result.title)}
                </h3>
                <p className="text-green-100 text-sm">
                  {language === 'vi' ? 'Thông tin chi tiết' : 'Detailed Information'}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
          {/* Requirements */}
          <div className="bg-blue-50 rounded-xl p-4">
            <h4 className="font-medium text-blue-900 flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4" />
              {language === 'vi' ? 'Hồ sơ cần chuẩn bị' : 'Required Documents'}
            </h4>
            <ul className="space-y-2">
              {(language === 'vi' ? result.requirements : (result.requirementsEn || result.requirements)).map((req, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                  <span className="flex-shrink-0 w-5 h-5 bg-blue-200 rounded-full flex items-center justify-center text-xs font-medium">
                    {idx + 1}
                  </span>
                  {req}
                </li>
              ))}
            </ul>
          </div>

          {/* Location & Time */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-purple-50 rounded-xl p-4">
              <h4 className="font-medium text-purple-900 flex items-center gap-2 mb-2">
                <MapPin className="w-4 h-4" />
                {language === 'vi' ? 'Nơi nộp hồ sơ' : 'Submission Location'}
              </h4>
              <p className="text-sm text-purple-800">
                {language === 'vi' ? result.location : (result.locationEn || result.location)}
              </p>
            </div>
            <div className="bg-orange-50 rounded-xl p-4">
              <h4 className="font-medium text-orange-900 flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4" />
                {language === 'vi' ? 'Thời gian xử lý' : 'Processing Time'}
              </h4>
              <p className="text-sm text-orange-800">
                {language === 'vi' ? result.processingTime : (result.processingTimeEn || result.processingTime)}
              </p>
            </div>
          </div>

          {/* Notes */}
          {result.notes && result.notes.length > 0 && (
            <div className="bg-amber-50 rounded-xl p-4">
              <h4 className="font-medium text-amber-900 flex items-center gap-2 mb-3">
                <AlertCircle className="w-4 h-4" />
                {language === 'vi' ? 'Lưu ý quan trọng' : 'Important Notes'}
              </h4>
              <ul className="space-y-2">
                {(language === 'vi' ? result.notes : (result.notesEn || result.notes)).map((note, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-amber-800">
                    <span className="flex-shrink-0">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Download Links */}
          {result.downloadLinks && result.downloadLinks.length > 0 && (
            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-medium text-gray-900 flex items-center gap-2 mb-3">
                <Download className="w-4 h-4" />
                {language === 'vi' ? 'Tài liệu mẫu' : 'Template Documents'}
              </h4>
              <div className="space-y-2">
                {result.downloadLinks.map((link, idx) => (
                  <a
                    key={idx}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors group"
                  >
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-red-600" />
                    </div>
                    <span className="flex-1 text-sm text-gray-700 group-hover:text-blue-700">
                      {language === 'vi' ? link.label : (link.labelEn || link.label)}
                    </span>
                    <Download className="w-4 h-4 text-gray-400 group-hover:text-blue-500" />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex flex-col sm:flex-row gap-2">
            <button
              onClick={handleBack}
              className="flex items-center justify-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              {language === 'vi' ? 'Quay lại' : 'Back'}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center justify-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition-colors"
            >
              {language === 'vi' ? 'Thủ tục khác' : 'Other Procedure'}
            </button>
            <button
              onClick={() => handleAskMore(language === 'vi' 
                ? `Tôi cần hỗ trợ thêm về ${selectedFlow.title}`
                : `I need more help with ${selectedFlow.titleEn || selectedFlow.title}`
              )}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {language === 'vi' ? 'Hỏi thêm bot' : 'Ask bot more'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render current step
  const currentStep = selectedFlow.steps[currentStepIndex];
  const progress = ((currentStepIndex + 1) / (selectedFlow.steps.length + 1)) * 100;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header with progress */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {selectedFlow.icon}
            <div>
              <h3 className="font-semibold">
                {language === 'vi' ? selectedFlow.title : (selectedFlow.titleEn || selectedFlow.title)}
              </h3>
              <p className="text-blue-100 text-sm">
                {language === 'vi' 
                  ? `Bước ${currentStepIndex + 1} / ${selectedFlow.steps.length}`
                  : `Step ${currentStepIndex + 1} / ${selectedFlow.steps.length}`}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        {/* Progress bar */}
        <div className="h-2 bg-white/20 rounded-full overflow-hidden">
          <div 
            className="h-full bg-white rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="p-4">
        <h4 className="text-lg font-medium text-gray-900 mb-4">
          {language === 'vi' ? currentStep.question : (currentStep.questionEn || currentStep.question)}
        </h4>

        {/* Options */}
        <div className="space-y-2">
          {currentStep.options.map((option) => (
            <button
              key={option.id}
              onClick={() => handleSelectOption(currentStep.id, option.id, option.nextStep)}
              className="w-full flex items-center gap-4 p-4 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-xl transition-all duration-200 text-left group"
            >
              <div className="flex-shrink-0 w-5 h-5 rounded-full border-2 border-gray-300 group-hover:border-blue-500 transition-colors" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 group-hover:text-blue-700 transition-colors">
                  {language === 'vi' ? option.label : (option.labelEn || option.label)}
                </div>
                {option.description && (
                  <p className="text-sm text-gray-500 mt-0.5">
                    {language === 'vi' ? option.description : (option.descriptionEn || option.description)}
                  </p>
                )}
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4 bg-gray-50">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          {language === 'vi' ? 'Quay lại' : 'Back'}
        </button>
      </div>
    </div>
  );
};

export default GuidedFlow;
