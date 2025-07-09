/**
 * Tạo ID duy nhất cho tin nhắn
 */
export const generateUniqueId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
};

/**
 * Format timestamp thành định dạng dễ đọc
 * @param timestamp ISO string timestamp
 * @returns Formatted time string (HH:MM)
 */
export const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    
    // Kiểm tra nếu date hợp lệ
    if (isNaN(date.getTime())) {
      return '';
    }
    
    // Format: HH:MM
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return '';
  }
};

/**
 * Rút gọn văn bản nếu quá dài
 * @param text Văn bản cần rút gọn
 * @param maxLength Độ dài tối đa
 * @returns Văn bản đã rút gọn
 */
export const truncateText = (text: string, maxLength: number = 30): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
