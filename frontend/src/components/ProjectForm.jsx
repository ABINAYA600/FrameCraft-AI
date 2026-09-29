import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { motion } from 'framer-motion'
import Button from './Button'
import Input from './Input'

const categories = ['Marketing', 'Product', 'Brand', 'Social Proof', 'Education', 'Entertainment']
const platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitter/X', 'LinkedIn', 'Website']
const languages = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese', 'Portuguese', 'Arabic']

const ProjectForm = ({ project, onSubmit, onCancel, loading }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm({
    defaultValues: project || {
      name: '',
      description: '',
      category: '',
      targetPlatform: [],
      language: '',
      thumbnail: ''
    }
  })

  const [thumbnailPreview, setThumbnailPreview] = useState(
    project?.thumbnail || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop'
  )

  const selectedPlatforms = watch('targetPlatform') || []

  const handleThumbnailChange = (e) => {
    const url = e.target.value
    setThumbnailPreview(url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop')
    setValue('thumbnail', url)
  }

  const togglePlatform = (platform) => {
    const current = watch('targetPlatform') || []
    if (current.includes(platform)) {
      setValue('targetPlatform', current.filter(p => p !== platform))
    } else {
      setValue('targetPlatform', [...current, platform])
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Thumbnail */}
        <div className="lg:col-span-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Project Thumbnail
          </label>
          <div className="glass rounded-2xl p-4">
            <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded-xl overflow-hidden mb-4">
              <img
                src={thumbnailPreview}
                alt="Thumbnail preview"
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop'
                }}
              />
            </div>
            <input
              type="text"
              placeholder="Image URL"
              className="w-full px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              value={watch('thumbnail') || ''}
              onChange={handleThumbnailChange}
            />
          </div>
        </div>

        {/* Main Fields */}
        <div className="lg:col-span-2 space-y-4">
          <Input
            label="Project Name"
            placeholder="Enter project name"
            error={errors.name?.message}
            {...register('name', {
              required: 'Project name is required'
            })}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              rows={4}
              placeholder="Describe your project"
              {...register('description', {
                required: 'Description is required'
              })}
            ></textarea>
            {errors.description && (
              <p className="text-sm text-red-500 mt-1">{errors.description.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Category
              </label>
              <select
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                {...register('category', {
                  required: 'Category is required'
                })}
              >
                <option value="">Select category</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
              {errors.category && (
                <p className="text-sm text-red-500 mt-1">{errors.category.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Language
              </label>
              <select
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                {...register('language', {
                  required: 'Language is required'
                })}
              >
                <option value="">Select language</option>
                {languages.map(lang => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </select>
              {errors.language && (
                <p className="text-sm text-red-500 mt-1">{errors.language.message}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Platforms
            </label>
            <div className="flex flex-wrap gap-2">
              {platforms.map(platform => (
                <button
                  key={platform}
                  type="button"
                  onClick={() => togglePlatform(platform)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedPlatforms.includes(platform)
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {platform}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <Button variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" onClick={handleSubmit(onSubmit)} loading={loading}>
          {project ? 'Update Project' : 'Save Project'}
        </Button>
      </div>
    </motion.div>
  )
}

export default ProjectForm
