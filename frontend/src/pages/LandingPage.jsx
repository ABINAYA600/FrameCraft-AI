import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiPlay, FiCheck, FiChevronDown, FiMenu, FiX } from 'react-icons/fi'
import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import Button from '../components/Button'

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { darkMode, toggleDarkMode } = useTheme()

  const features = [
    {
      title: 'AI Video Generation',
      description: 'Convert scripts into professional videos in minutes with our advanced AI models',
      icon: '🎬'
    },
    {
      title: 'Smart Music Recommendations',
      description: 'AI suggests perfect background music that matches your video content and mood',
      icon: '🎵'
    },
    {
      title: 'Scheduled Publishing',
      description: 'Plan and schedule your posts across multiple platforms automatically',
      icon: '📅'
    },
    {
      title: 'Audience Analytics',
      description: 'Get deep insights into audience engagement and feedback for continuous improvement',
      icon: '📊'
    },
    {
      title: 'Voice Studio',
      description: 'Generate natural-sounding voiceovers in multiple languages and tones',
      icon: '🎙️'
    },
    {
      title: 'MLOps Pipeline',
      description: 'Our AI continuously learns and improves based on real-world usage data',
      icon: '🤖'
    }
  ]

  const workflowSteps = [
    { step: 1, title: 'Write Your Script', description: 'Create or upload your marketing script' },
    { step: 2, title: 'Upload Assets', description: 'Add your images, logos, and brand materials' },
    { step: 3, title: 'AI Magic', description: 'Our AI generates a professional video for you' },
    { step: 4, title: 'Publish & Analyze', description: 'Schedule posts and monitor performance' }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Content Creator',
      text: 'FrameCraft AI has saved me countless hours. What used to take days now takes minutes!',
      avatar: 'SC'
    },
    {
      name: 'Michael Rodriguez',
      role: 'Small Business Owner',
      text: 'Finally, an affordable video marketing solution that actually works. My sales are up 40%!',
      avatar: 'MR'
    },
    {
      name: 'Emily Watson',
      role: 'NGO Director',
      text: 'We use FrameCraft to create awareness videos. The AI voiceovers sound incredibly natural.',
      avatar: 'EW'
    }
  ]

  const pricingPlans = [
    {
      name: 'Starter',
      price: '$29',
      period: '/month',
      features: ['10 videos/month', 'Basic AI voices', 'Standard quality', 'Email support'],
      popular: false
    },
    {
      name: 'Professional',
      price: '$99',
      period: '/month',
      features: ['50 videos/month', 'Premium AI voices', '4K quality', 'Priority support', 'Analytics'],
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      features: ['Unlimited videos', 'Custom AI training', 'White-label solution', 'Dedicated account manager', 'API access'],
      popular: false
    }
  ]

  const faqs = [
    {
      question: 'How long does it take to generate a video?',
      answer: 'Most videos are generated in 2-5 minutes, depending on length and complexity.'
    },
    {
      question: 'Can I use my own voiceovers?',
      answer: 'Yes! You can upload your own voiceovers or use our AI-generated ones.'
    },
    {
      question: 'Is there a free trial?',
      answer: 'Yes, we offer a 14-day free trial with all Professional features included.'
    },
    {
      question: 'What platforms do you support for publishing?',
      answer: 'We support YouTube, Instagram, TikTok, Facebook, LinkedIn, and Twitter/X.'
    }
  ]

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 min-h-screen">
        
        {/* Navbar */}
        <nav className="fixed top-0 left-0 right-0 z-50 glass">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-20">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                  F
                </div>
                <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  FrameCraft AI
                </span>
              </div>

              {/* Desktop Menu */}
              <div className="hidden md:flex items-center space-x-8">
                <a href="#features" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Features</a>
                <a href="#pricing" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Pricing</a>
                <a href="#faq" className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">FAQ</a>
                <button onClick={toggleDarkMode} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                  {darkMode ? '☀️' : '🌙'}
                </button>
                <Link to="/login">
                  <Button variant="ghost">Login</Button>
                </Link>
                <Link to="/register">
                  <Button>Get Started</Button>
                </Link>
              </div>

              {/* Mobile Menu Button */}
              <button 
                className="md:hidden p-2"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="md:hidden glass border-t"
            >
              <div className="px-4 py-6 space-y-4">
                <a href="#features" className="block text-gray-600 dark:text-gray-300">Features</a>
                <a href="#pricing" className="block text-gray-600 dark:text-gray-300">Pricing</a>
                <a href="#faq" className="block text-gray-600 dark:text-gray-300">FAQ</a>
                <div className="pt-4 space-y-3">
                  <Link to="/login" className="block w-full">
                    <Button variant="ghost" className="w-full">Login</Button>
                  </Link>
                  <Link to="/register" className="block w-full">
                    <Button className="w-full">Get Started</Button>
                  </Link>
                </div>
              </div>
            </motion.div>
          )}
        </nav>

        {/* Hero Section */}
        <section className="pt-32 pb-20 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h1 className="text-5xl md:text-7xl font-bold text-gray-900 dark:text-white mb-6 leading-tight">
                  Transform Scripts into<br />
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Professional Marketing Videos
                  </span>
                  <br />with AI
                </h1>
                <p className="text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-3xl mx-auto">
                  FrameCraft AI helps creators and businesses automate video generation, publishing, audience analysis, and continuous AI improvement.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link to="/register">
                    <Button size="lg" className="text-lg">
                      Get Started Free
                    </Button>
                  </Link>
                  <Button variant="secondary" size="lg" className="text-lg">
                    <FiPlay className="mr-2" />
                    Watch Demo
                  </Button>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="mt-16"
              >
                <div className="glass rounded-3xl p-4 shadow-2xl max-w-5xl mx-auto">
                  <div className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-2xl aspect-video flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <FiPlay size={40} className="text-white ml-1" />
                      </div>
                      <p className="text-gray-600 dark:text-gray-300">Video Demo Preview</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Powerful Features</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">Everything you need to create amazing marketing videos</p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="glass rounded-2xl p-8 hover:shadow-xl transition-all duration-300"
                >
                  <div className="text-5xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Workflow Section */}
        <section className="py-20 px-4 bg-white/50 dark:bg-gray-800/50">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">How It Works</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">Create professional videos in 4 simple steps</p>
            </motion.div>

            <div className="grid md:grid-cols-4 gap-8">
              {workflowSteps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="text-center"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-6">
                    {step.step}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{step.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{step.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">What Our Users Say</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">Trusted by thousands of creators and businesses</p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="glass rounded-2xl p-8"
                >
                  <p className="text-gray-600 dark:text-gray-300 mb-6 italic">"{testimonial.text}"</p>
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                      {testimonial.avatar}
                    </div>
                    <div>
                      <p className="font-bold text-gray-900 dark:text-white">{testimonial.name}</p>
                      <p className="text-gray-500 dark:text-gray-400 text-sm">{testimonial.role}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-20 px-4 bg-white/50 dark:bg-gray-800/50">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Simple Pricing</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">Choose the plan that fits your needs</p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {pricingPlans.map((plan, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className={`rounded-2xl p-8 ${plan.popular ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-2xl scale-105' : 'glass'}`}
                >
                  {plan.popular && (
                    <div className="text-center mb-4">
                      <span className="bg-white/20 text-white px-4 py-1 rounded-full text-sm font-medium">Most Popular</span>
                    </div>
                  )}
                  <h3 className={`text-2xl font-bold mb-2 ${plan.popular ? 'text-white' : 'text-gray-900 dark:text-white'}`}>{plan.name}</h3>
                  <div className="mb-6">
                    <span className={`text-4xl font-bold ${plan.popular ? 'text-white' : 'text-gray-900 dark:text-white'}`}>{plan.price}</span>
                    <span className={`${plan.popular ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>{plan.period}</span>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, i) => (
                      <li key={i} className={`flex items-center ${plan.popular ? 'text-white/90' : 'text-gray-600 dark:text-gray-300'}`}>
                        <FiCheck className="mr-3 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Button 
                    variant={plan.popular ? 'secondary' : 'primary'} 
                    className="w-full"
                  >
                    Get Started
                  </Button>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-20 px-4">
          <div className="max-w-3xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Frequently Asked Questions</h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">Have questions? We have answers</p>
            </motion.div>

            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                  className="glass rounded-2xl p-6"
                >
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{faq.question}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{faq.answer}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-16 px-4 bg-gray-900 text-white">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-12">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                    F
                  </div>
                  <span className="text-2xl font-bold">FrameCraft AI</span>
                </div>
                <p className="text-gray-400">Transforming ideas into professional videos with AI.</p>
              </div>
              <div>
                <h4 className="font-bold mb-4">Product</h4>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold mb-4">Company</h4>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold mb-4">Legal</h4>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
              <p>© 2024 FrameCraft AI. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default LandingPage
