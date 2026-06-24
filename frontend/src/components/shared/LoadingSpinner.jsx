export default function LoadingSpinner({ size = 'md' }) {
  const sizes = { sm: 'w-4 h-4 border', md: 'w-6 h-6 border-2' };
  return (
    <div
      className={`${sizes[size]} border-gray-200 border-t-blue-700 rounded-full animate-spin`}
      role="status"
      aria-label="Loading"
    />
  );
}
