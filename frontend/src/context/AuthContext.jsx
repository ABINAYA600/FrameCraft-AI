import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    if (token && userData) {
      setUser(JSON.parse(userData))
    }
    setLoading(false)
  }, [])

  const login = (email, password) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const userData = {
          id: 1,
          name: 'John Doe',
          email,
          role: 'Creator',
          organization: 'FrameCraft AI'
        }
        setUser(userData)
        localStorage.setItem('token', 'dummy-token')
        localStorage.setItem('user', JSON.stringify(userData))
        resolve(userData)
      }, 1000)
    })
  }

  const register = (name, email, password) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const userData = {
          id: 1,
          name,
          email,
          role: 'Creator',
          organization: 'FrameCraft AI'
        }
        setUser(userData)
        localStorage.setItem('token', 'dummy-token')
        localStorage.setItem('user', JSON.stringify(userData))
        resolve(userData)
      }, 1000)
    })
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const updateProfile = (data) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const updatedUser = { ...user, ...data }
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
        resolve(updatedUser)
      }, 500)
    })
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
