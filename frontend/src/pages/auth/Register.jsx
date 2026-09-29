import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import Button from '../../components/Button'
import Input from '../../components/Input'
import Card from '../../components/Card'

const registerSchema = z.object({
  name: z
    .string()
    .min(3, 'Name must be at least 3 characters')
    .nonempty('Name is required'),
  email: z
    .string()
    .email('Invalid email address')
    .nonempty('Email is required'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      'Password must include uppercase, lowercase, number, and special character'
    ),
  confirmPassword: z
    .string()
    .nonempty('Please confirm your password'),
  terms: z
    .boolean()
    .refine((val) => val === true, 'You must accept the terms and conditions')
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})

const Register = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting, touchedFields }, watch } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      terms: false
    },
    mode: 'onTouched'
  })
  const { register: registerUser } = useAuth()
  const { darkMode } = useTheme()
  const navigate = useNavigate()

  const onSubmit = async (data) => {
    console.log('Form submitted with data:', data)
    try {
      await registerUser(data.name, data.email, data.password)
      navigate('/dashboard')
    } catch (error) {
      console.error('Registration failed:', error)
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
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Create Account</h1>
              <p className="text-gray-600 dark:text-gray-300">Start creating amazing videos today</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <Input
                label="Full Name"
                type="text"
                placeholder="John Doe"
                error={touchedFields.name && errors.name?.message}
                {...register('name')}
              />

              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                error={touchedFields.email && errors.email?.message}
                {...register('email')}
              />

              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                error={touchedFields.password && errors.password?.message}
                {...register('password')}
              />

              <Input
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                error={touchedFields.confirmPassword && errors.confirmPassword?.message}
                {...register('confirmPassword')}
              />

              <label className="flex items-start">
                <input 
                  type="checkbox" 
                  className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 mt-1"
                  {...register('terms')}
                />
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-300">
                  I agree to the <a href="#" className="text-blue-600 hover:text-blue-700">Terms of Service</a> and <a href="#" className="text-blue-600 hover:text-blue-700">Privacy Policy</a>
                </span>
              </label>
              {touchedFields.terms && errors.terms && (
                <p className="text-sm text-red-500">{errors.terms.message}</p>
              )}

              <Button type="submit" className="w-full" loading={isSubmitting}>
                Create Account
              </Button>
            </form>

            <div className="mt-8 text-center">
              <p className="text-gray-600 dark:text-gray-300">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium dark:text-blue-400">
                  Sign in
                </Link>
              </p>
            </div>

            <div className="mt-6 text-center">
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

export default Register
