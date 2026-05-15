import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  title?: string
  padding?: 'sm' | 'md' | 'lg'
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  padding = 'md'
}) => {
  const paddingStyles = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }

  return (
    <div className={`
      bg-white rounded-xl shadow-sm border border-gray-200
      ${paddingStyles[padding]}
      ${className}
    `}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  )
}
