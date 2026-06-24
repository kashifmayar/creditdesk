function getInitials(name) {
  if (!name) return '?';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

export default function Avatar({ name, size = 'md' }) {
  const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-9 h-9 text-sm' };
  return (
    <div
      className={`${sizes[size]} rounded-full bg-blue-700 text-white flex items-center justify-center font-medium`}
    >
      {getInitials(name)}
    </div>
  );
}
