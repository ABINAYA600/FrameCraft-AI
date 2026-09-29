import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { useState } from 'react'
import { useTheme } from '../../context/ThemeContext'
import Button from '../../components/Button'
import Input from '../../components/Input'
import Card from '../../components/Card'

const ForgotPassword = () => {
  const { register, handleSubmit, formState: { errors } } = useForm()
  const { darkMode } = useTheme()
  const [emailSent, setEmailSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      setEmailSent(true)
    } catch (error) {
      console.error('Failed to send reset email:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={`min-h-screen flex items-center justify-center px-4 ${darkMode ? 'dark' : ''}`}>
      <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 min-h-screen w-full flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <Card className="glass">
            <div className="text-center mb-8">
              <Link to="/" className="inline-flex items-center space-x-2 mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold">
                  F
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  FrameCraft AI
                </span>
              </Link>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {emailSent ? 'Check Your Email' : 'Reset Password'}
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                {emailSent 
                  ? 'We have sent you a link to reset your password' 
                  : 'Enter your email and we will send you a reset link'}
              </p>
            </div>

            {!emailSent ? (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <Input
                  label="Email"
                  type="email"
                  placeholder="you@example.com"
                  error={errors.email?.message}
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^\S+@\S+$/i,
                      message: 'Invalid email address'
                    }
                  })}
                />

                <Button type="submit" className="w-full" loading={loading}>
                  Send Reset Link
                </Button>
              </form>
            ) : (
              <div className="text-center">
                <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-4xl">✉️</span>
                </div>
                <Button as="a" href="/login" className="w-full mt-6">
                  Back to Login
                </Button>
              </div>
            )}

            <div className="mt-8 text-center">
              <Link to="/" className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400">
                ← Back to home
              </Link>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default ForgotPassword
