import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { FiUpload, FiFile, FiX } from 'react-icons/fi'

const MediaUploader = ({ onUpload, accept = '*', multiple = false }) => {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files)
      files.forEach(file => onUpload(file))
    }
  }, [onUpload])

  const handleFileChange = useCallback((e) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files)
      files.forEach(file => onUpload(file))
    }
  }, [onUpload])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer
        ${isDragging 
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
          : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/10'}
      `}
    >
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      
      <div className="space-y-4">
        <div className={`
          w-20 h-20 mx-auto rounded-full flex items-center justify-center transition-colors
          ${isDragging 
            ? 'bg-blue-100 dark:bg-blue-900/30' 
            : 'bg-gray-100 dark:bg-gray-700'}
        `}>
          <FiUpload size={40} className={isDragging ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'} />
        </div>
        
        <div>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {isDragging ? 'Drop files here' : 'Drag & drop files here'}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            or click to browse
          </p>
        </div>
      </div>
    </motion.div>
  )
}

export default MediaUploader
