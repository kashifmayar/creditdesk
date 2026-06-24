const VARIANTS = {
  default: 'bg-gray-100 text-gray-700',
  ai: 'bg-teal-50 text-teal-700 border border-teal-100',
};

export default function Badge({ children, variant = 'default', className = '' }) {
  return (
    <span
      className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${VARIANTS[variant] || ''} ${className}`}
    >
      {children}
    </span>
  );
}
