import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiImage, FiVideo, FiMusic, FiMic, FiTrash2, FiEdit2, FiX, FiCheck, FiEye, FiClock } from 'react-icons/fi'
import { useQuery, useQueryClient } from 'react-query'
import MediaUploader from './MediaUploader'
import Button from './Button'
import Card from './Card'
import { api } from '../services/api'

const mediaTypes = [
  { key: 'images', label: 'Images', icon: FiImage, accept: 'image/*' },
  { key: 'videos', label: 'Videos', icon: FiVideo, accept: 'video/*' },
  { key: 'audio', label: 'Audio', icon: FiMusic, accept: 'audio/*' },
  { key: 'voiceSamples', label: 'Voice Samples', icon: FiMic, accept: 'audio/*' }
]

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  else return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const MediaGallery = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState('images')
  const [uploadingFiles, setUploadingFiles] = useState([])
  const [previewMedia, setPreviewMedia] = useState(null)
  const [editingId, setEditingId] = useState(null)
  const [editName, setEditName] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const queryClient = useQueryClient()
  
  const { data: mediaFiles, isLoading: mediaLoading } = useQuery(
    ['projectMedia', projectId, activeTab],
    () => api.getProjectMedia(projectId, activeTab)
  )
  
  const { data: uploadHistory, isLoading: historyLoading } = useQuery(
    ['uploadHistory', projectId],
    () => api.getUploadHistory(projectId)
  )

  const handleFileUpload = async (file) => {
    const fileId = Date.now()
    setUploadingFiles(prev => [...prev, { id: fileId, name: file.name, progress: 0 }])
    
    try {
      await api.uploadMedia(projectId, activeTab, file, (progress) => {
        setUploadingFiles(prev => 
          prev.map(f => f.id === fileId ? { ...f, progress } : f)
        )
      })
      
      setTimeout(() => {
        setUploadingFiles(prev => prev.filter(f => f.id !== fileId))
        queryClient.invalidateQueries(['projectMedia', projectId, activeTab])
        queryClient.invalidateQueries(['uploadHistory', projectId])
      }, 500)
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadingFiles(prev => prev.filter(f => f.id !== fileId))
    }
  }

  const handleDelete = async (mediaId) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      await api.deleteMedia(projectId, activeTab, mediaId)
      queryClient.invalidateQueries(['projectMedia', projectId, activeTab])
    }
  }

  const handleRename = async (mediaId) => {
    if (editName.trim()) {
      await api.renameMedia(projectId, activeTab, mediaId, editName.trim())
      queryClient.invalidateQueries(['projectMedia', projectId, activeTab])
      setEditingId(null)
      setEditName('')
    }
  }

  const startRename = (file) => {
    setEditingId(file.id)
    setEditName(file.name)
  }

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-xl">
        {mediaTypes.map((type) => {
          const Icon = type.icon
          return (
            <button
              key={type.key}
              onClick={() => setActiveTab(type.key)}
              className={`
                flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-all
                ${activeTab === type.key
                  ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}
              `}
            >
              <Icon size={18} />
              <span>{type.label}</span>
            </button>
          )
        })}
        <button
          onClick={() => setShowHistory(!showHistory)}
          className={`
            flex items-center justify-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-all
            ${showHistory
              ? 'bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}
          `}
        >
          <FiClock size={18} />
          <span>History</span>
        </button>
      </div>

      <AnimatePresence mode="wait">
        {showHistory ? (
          <motion.div
            key="history"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <Card>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Upload History</h3>
              {historyLoading ? (
                <div className="space-y-3">
                  {[1,2,3].map(i => (
                    <div key={i} className="h-16 bg-gray-100 dark:bg-gray-700 rounded-xl animate-pulse"></div>
                  ))}
                </div>
              ) : uploadHistory?.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No upload history yet</p>
              ) : (
                <div className="space-y-3">
                  {uploadHistory?.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                      <div className="flex items-center space-x-3">
                        <div className={`
                          w-10 h-10 rounded-lg flex items-center justify-center
                          ${item.type === 'images' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' :
                            item.type === 'videos' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' :
                            'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'}
                        `}>
                          {item.type === 'images' ? <FiImage /> : item.type === 'videos' ? <FiVideo /> : <FiMusic />}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{item.fileName}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{formatDate(item.uploadedAt)}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        item.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key="media"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            {/* Uploader */}
            <div className="mb-6">
              <MediaUploader 
                accept={mediaTypes.find(t => t.key === activeTab).accept}
                multiple={true}
                onUpload={handleFileUpload}
              />
            </div>

            {/* Uploading files */}
            {uploadingFiles.length > 0 && (
              <div className="space-y-3 mb-6">
                {uploadingFiles.map(file => (
                  <Card key={file.id} className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <FiFile size={20} className="text-gray-400" />
                        <span className="font-medium text-gray-900 dark:text-white">{file.name}</span>
                      </div>
                      <span className="text-blue-600 dark:text-blue-400 font-semibold">{file.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      ></div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Gallery */}
            {mediaLoading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {[1,2,3,4,5,6,7,8,9,10].map(i => (
                  <div key={i} className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
                ))}
              </div>
            ) : mediaFiles?.length === 0 ? (
              <Card className="text-center py-12">
                <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  {(() => { const Icon = mediaTypes.find(t => t.key === activeTab).icon; return <Icon size={40} className="text-gray-400" />})()}
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">No {mediaTypes.find(t => t.key === activeTab).label} yet</h3>
                <p className="text-gray-500 dark:text-gray-400">Upload files to get started</p>
              </Card>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {mediaFiles?.map((file) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="group relative"
                  >
                    <Card className="overflow-hidden p-0 cursor-pointer h-full">
                      <div
                        className="aspect-square relative bg-gray-100 dark:bg-gray-700"
                        onClick={() => setPreviewMedia(file)}
                      >
                        {activeTab === 'images' && (
                          <img
                            src={file.url}
                            alt={file.name}
                            className="w-full h-full object-cover"
                          />
                        )}
                        {activeTab === 'videos' && (
                          <video
                            src={file.url}
                            className="w-full h-full object-cover"
                          />
                        )}
                        {(activeTab === 'audio' || activeTab === 'voiceSamples') && (
                          <div className="flex items-center justify-center w-full h-full">
                            <FiMusic size={48} className="text-gray-400" />
                          </div>
                        )}

                        {/* Overlay */}
                        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center justify-center space-x-2">
                          <Button
                            variant="secondary"
                            size="sm"
                            className="bg-white text-gray-900"
                            onClick={(e) => { e.stopPropagation(); setPreviewMedia(file); }}
                          >
                            <FiEye size={16} />
                          </Button>
                          {editingId === file.id ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              className="bg-green-500 text-white"
                              onClick={(e) => { e.stopPropagation(); handleRename(file.id); }}
                            >
                              <FiCheck size={16} />
                            </Button>
                          ) : (
                            <Button
                              variant="secondary"
                              size="sm"
                              className="bg-white text-gray-900"
                              onClick={(e) => { e.stopPropagation(); startRename(file); }}
                            >
                              <FiEdit2 size={16} />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            className="bg-red-500 text-white hover:bg-red-600"
                            onClick={(e) => { e.stopPropagation(); handleDelete(file.id); }}
                          >
                            <FiTrash2 size={16} />
                          </Button>
                        </div>
                      </div>

                      <div className="p-3">
                        {editingId === file.id ? (
                          <div className="flex items-center space-x-2">
                            <input
                              type="text"
                              value={editName}
                              onChange={(e) => setEditName(e.target.value)}
                              onKeyDown={(e) => { if (e.key === 'Enter') handleRename(file.id); if (e.key === 'Escape') { setEditingId(null); setEditName(''); }}}
                              className="flex-1 px-2 py-1 text-sm border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                              autoFocus
                            />
                          </div>
                        ) : (
                          <>
                            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{file.name}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">{formatFileSize(file.size)}</p>
                          </>
                        )}
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Preview Modal */}
      {previewMedia && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative max-w-4xl w-full max-h-[90vh] overflow-auto"
          >
            <Button
              variant="ghost"
              className="absolute top-4 right-4 bg-black/50 text-white hover:bg-black/70 z-10"
              onClick={() => setPreviewMedia(null)}
            >
              <FiX size={24} />
            </Button>
            
            {activeTab === 'images' && (
              <img
                src={previewMedia.url}
                alt={previewMedia.name}
                className="w-full h-auto rounded-2xl"
              />
            )}
            {activeTab === 'videos' && (
              <video
                src={previewMedia.url}
                controls
                className="w-full rounded-2xl"
              />
            )}
            {(activeTab === 'audio' || activeTab === 'voiceSamples') && (
              <Card className="p-8">
                <div className="text-center mb-6">
                  <FiMusic size={64} className="mx-auto mb-4 text-purple-500" />
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{previewMedia.name}</h3>
                </div>
                <audio
                  src={previewMedia.url}
                  controls
                  className="w-full"
                />
              </Card>
            )}
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default MediaGallery
