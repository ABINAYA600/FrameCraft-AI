import { motion } from 'framer-motion'
import { FiMic, FiPlus, FiPlay, FiDownload, FiStar } from 'react-icons/fi'
import Button from '../../components/Button'
import Card from '../../components/Card'

const VoiceStudio = () => {
  const voices = [
    { name: 'Sarah', accent: 'American English', gender: 'Female', rating: 4.8 },
    { name: 'James', accent: 'British English', gender: 'Male', rating: 4.7 },
    { name: 'Emma', accent: 'Australian English', gender: 'Female', rating: 4.9 },
    { name: 'Michael', accent: 'Canadian English', gender: 'Male', rating: 4.6 },
    { name: 'Sofia', accent: 'Spanish', gender: 'Female', rating: 4.8 },
    { name: 'Lucas', accent: 'French', gender: 'Male', rating: 4.7 }
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Voice Studio</h1>
          <p className="text-gray-600 dark:text-gray-300">Generate AI voiceovers for your videos</p>
        </div>
        <Button className="mt-4 sm:mt-0">
          <FiPlus className="mr-2" />
          New Voiceover
        </Button>
      </div>

      {/* Voice Generator */}
      <Card>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Generate Voiceover</h2>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Enter your script</label>
            <textarea
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={6}
              placeholder="Type your script here..."
            ></textarea>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Voice</label>
              <select className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                {voices.map((voice, i) => (
                  <option key={i}>{voice.name} - {voice.accent}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Speed</label>
              <input type="range" min="0.5" max="2" step="0.1" defaultValue="1" className="w-full" />
            </div>
          </div>

          <div className="flex space-x-4">
            <Button>
              <FiPlay className="mr-2" />
              Preview Voice
            </Button>
            <Button variant="secondary">
              <FiDownload className="mr-2" />
              Generate & Download
            </Button>
          </div>
        </div>
      </Card>

      {/* Available Voices */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Available Voices</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {voices.map((voice, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FiMic size={36} className="text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">{voice.name}</h3>
                <p className="text-gray-500 dark:text-gray-400 mb-2">{voice.accent}</p>
                <p className="text-sm text-gray-400 dark:text-gray-500 mb-4">{voice.gender}</p>
                <div className="flex items-center justify-center mb-4">
                  <FiStar className="text-yellow-500 mr-1" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{voice.rating}</span>
                </div>
                <div className="flex space-x-2">
                  <Button variant="secondary" className="flex-1">
                    <FiPlay className="mr-2" />
                    Sample
                  </Button>
                  <Button variant="ghost">
                    <FiStar />
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default VoiceStudio
