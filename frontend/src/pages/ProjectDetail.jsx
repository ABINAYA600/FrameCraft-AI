import { useParams, Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import { FiArrowLeft, FiEdit, FiTrash2, FiCalendar, FiGlobe, FiType, FiFolder, FiVideo, FiMic } from 'react-icons/fi'
import { api } from '../services/api'
import Button from '../components/Button'
import Card from '../components/Card'
import MediaGallery from '../components/MediaGallery'

const ProjectDetail = () => {
  const { id } = useParams()
  const { data: project, isLoading, error } = useQuery(['project', id], () => api.getProjectById(id))

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Project not found</h1>
        <Link to="/dashboard/projects">
          <Button>
            <FiArrowLeft className="mr-2" />
            Back to Projects
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Link
          to="/dashboard/projects"
          className="inline-flex items-center text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 mb-4"
        >
          <FiArrowLeft className="mr-2" />
          Back to Projects
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">{project.name}</h1>
            <p className="text-gray-600 dark:text-gray-300 text-lg">{project.description}</p>
          </div>
          <div className="flex space-x-3">
            <Button variant="secondary">
              <FiEdit className="mr-2" />
              Edit Project
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Project Info */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                <FiType size={24} className="text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Category</p>
                <p className="font-semibold text-gray-900 dark:text-white">{project.category}</p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                <FiGlobe size={24} className="text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Language</p>
                <p className="font-semibold text-gray-900 dark:text-white">{project.language}</p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                <FiCalendar size={24} className="text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Last Updated</p>
                <p className="font-semibold text-gray-900 dark:text-white">{project.lastUpdated}</p>
              </div>
            </div>
          </Card>
          
          <Card>
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                project.status === 'Completed' ? 'bg-green-100 dark:bg-green-900/30' :
                project.status === 'In Progress' ? 'bg-blue-100 dark:bg-blue-900/30' :
                'bg-gray-100 dark:bg-gray-700'
              }`}>
                <FiFolder size={24} className={`${
                  project.status === 'Completed' ? 'text-green-600 dark:text-green-400' :
                  project.status === 'In Progress' ? 'text-blue-600 dark:text-blue-400' :
                  'text-gray-600 dark:text-gray-400'
                }`} />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                  project.status === 'Completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                  project.status === 'In Progress' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                  'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {project.status}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </motion.div>

      {/* Target Platforms */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Target Platforms</h3>
          <div className="flex flex-wrap gap-2">
            {project.targetPlatform?.map((platform, idx) => (
              <span
                key={idx}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-xl text-gray-700 dark:text-gray-300 font-medium"
              >
                {platform}
              </span>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Media Gallery */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <MediaGallery projectId={project.id} />
      </motion.div>
    </div>
  )
}

export default ProjectDetail
