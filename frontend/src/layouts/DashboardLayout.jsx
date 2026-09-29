import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import {
  FiHome,
  FiFolder,
  FiVideo,
  FiBarChart2,
  FiCalendar,
  FiMic,
  FiUser,
  FiSettings,
  FiLogOut,
  FiBell,
  FiSearch,
  FiMenu,
  FiX
} from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const DashboardLayout = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { darkMode, toggleDarkMode } = useTheme()

  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false)

  const menuItems = [
    {
      path: '/dashboard',
      icon: FiHome,
      label: 'Dashboard'
    },
    {
      path: '/dashboard/ai-video-studio',
      icon: FiVideo,
      label: 'AI Video Studio'
    },
    {
      path: '/dashboard/projects',
      icon: FiFolder,
      label: 'Projects'
    },
    {
      path: '/dashboard/analytics',
      icon: FiBarChart2,
      label: 'Analytics'
    },
    {
      path: '/dashboard/publishing',
      icon: FiCalendar,
      label: 'Publishing'
    },
    {
      path: '/dashboard/voice-studio',
      icon: FiMic,
      label: 'Voice Studio'
    },
    {
      path: '/dashboard/profile',
      icon: FiUser,
      label: 'Profile'
    },
    {
      path: '/dashboard/settings',
      icon: FiSettings,
      label: 'Settings'
    }
  ]

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 min-h-screen flex">

        {/* Sidebar */}
        <aside
          className={`fixed inset-y-0 left-0 z-40 w-64 glass border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-300 ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } md:translate-x-0`}
        >

          {/* Logo */}
          <div className="h-20 flex items-center justify-between px-6 border-b border-gray-200 dark:border-gray-700">

            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                F
              </div>

              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                FrameCraft
              </span>
            </Link>

            <button
              className="md:hidden p-2"
              onClick={() => setSidebarOpen(false)}
            >
              <FiX size={20} />
            </button>

          </div>

          {/* Navigation */}
          <nav className="p-4 space-y-2">

            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon size={20} />
                  <span className="font-medium">
                    {item.label}
                  </span>
                </Link>
              )
            })}

          </nav>

          {/* Logout */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">

            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
            >
              <FiLogOut size={20} />

              <span className="font-medium">
                Logout
              </span>
            </button>

          </div>

        </aside>

        {/* Main Content */}
        <main
          className={`flex-1 transition-all duration-300 ${
            sidebarOpen ? 'md:ml-64' : 'md:ml-0'
          }`}
        >

          {/* Top Navbar */}
          <header className="sticky top-0 z-30 glass border-b border-gray-200 dark:border-gray-700">

            <div className="h-20 flex items-center justify-between px-6">

              <div className="flex items-center">

                {/* Mobile Menu */}
                <button
                  className="md:hidden mr-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                >
                  <FiMenu size={24} />
                </button>

                {/* Search */}
                <div className="relative hidden sm:block">

                  <FiSearch
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                    size={18}
                  />

                  <input
                    type="text"
                    placeholder="Search..."
                    className="pl-10 pr-4 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent w-80"
                  />

                </div>

              </div>

              {/* Right Side */}
              <div className="flex items-center space-x-4">

                {/* Dark Mode */}
                <button
                  onClick={toggleDarkMode}
                  className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>

                {/* Notifications */}
                <button
                  className="relative p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <FiBell
                    size={22}
                    className="text-gray-600 dark:text-gray-300"
                  />

                  <span className="absolute top-1 right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                </button>

                {/* Profile */}
                <div className="relative">

                  <button
                    onClick={() =>
                      setProfileDropdownOpen(!profileDropdownOpen)
                    }
                    className="flex items-center space-x-3 p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >

                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                      {user?.name?.charAt(0) || 'U'}
                    </div>

                    <div className="hidden sm:block text-left">

                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {user?.name}
                      </p>

                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {user?.role}
                      </p>

                    </div>

                  </button>

                  {/* Profile Dropdown */}
                  {profileDropdownOpen && (
                    <div className="absolute right-0 top-full mt-2 w-64 glass rounded-xl shadow-lg py-2 z-50">

                      <Link
                        to="/dashboard/profile"
                        className="flex items-center space-x-3 px-4 py-3 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        onClick={() => setProfileDropdownOpen(false)}
                      >
                        <FiUser size={18} />
                        <span>Profile</span>
                      </Link>

                      <Link
                        to="/dashboard/settings"
                        className="flex items-center space-x-3 px-4 py-3 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                        onClick={() => setProfileDropdownOpen(false)}
                      >
                        <FiSettings size={18} />
                        <span>Settings</span>
                      </Link>

                      <hr className="my-2 border-gray-200 dark:border-gray-700" />

                      <button
                        onClick={handleLogout}
                        className="flex items-center space-x-3 px-4 py-3 w-full text-left text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        <FiLogOut size={18} />
                        <span>Logout</span>
                      </button>

                    </div>
                  )}

                </div>

              </div>

            </div>

          </header>

          {/* Page Content */}
          <div className="p-6">
            {children || <Outlet />}
          </div>

        </main>

      </div>
    </div>
  )
}

export default DashboardLayout