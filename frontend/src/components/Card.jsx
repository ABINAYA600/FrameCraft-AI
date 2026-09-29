import { motion } from 'framer-motion'

const Card = ({ children, className = '', glass = false }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl p-6 ${glass ? 'glass' : 'bg-white dark:bg-gray-800 shadow-lg'} ${className}`}
    >
      {children}
    </motion.div>
  )
}

export default Card
