import { Routes, Route } from 'react-router-dom'

import { useAuth } from './context/AuthContext'

import ProtectedRoute from './routes/ProtectedRoute'

import LandingPage from './pages/LandingPage'

import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import ForgotPassword from './pages/auth/ForgotPassword'

import DashboardLayout from './layouts/DashboardLayout'

import Dashboard from './pages/dashboard/Dashboard'
import Projects from './pages/dashboard/Projects'
import Analytics from './pages/dashboard/Analytics'
import Publishing from './pages/dashboard/Publishing'
import MLOps from './pages/dashboard/MLOps'
import VoiceStudio from './pages/dashboard/VoiceStudio'
import Profile from './pages/dashboard/Profile'
import Settings from './pages/dashboard/Settings'
import AIVideoStudio from './pages/dashboard/AIVideoStudio'

import ProjectDetail from './pages/ProjectDetail'


function App() {

  const { loading } = useAuth()


  // ==========================================================
  // AUTH LOADING
  // ==========================================================

  if (loading) {

    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px',
          color: '#6b7280'
        }}
      >
        Loading FrameCraft AI...
      </div>
    )

  }


  // ==========================================================
  // ROUTES
  // ==========================================================

  return (

    <Routes>

      {/* ====================================================
          PUBLIC ROUTES
      ==================================================== */}

      <Route
        path="/"
        element={
          <LandingPage />
        }
      />

      <Route
        path="/login"
        element={
          <Login />
        }
      />

      <Route
        path="/register"
        element={
          <Register />
        }
      />

      <Route
        path="/forgot-password"
        element={
          <ForgotPassword />
        }
      />


      {/* ====================================================
          PROTECTED DASHBOARD
      ==================================================== */}

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >

        {/* Dashboard */}

        <Route
          index
          element={
            <Dashboard />
          }
        />


        {/* ==================================================
            PROJECTS
        ================================================== */}

        <Route
          path="projects"
          element={
            <Projects />
          }
        />


        {/* ==================================================
            AI VIDEO STUDIO
        ================================================== */}

        {/* New project */}

        <Route
          path="ai-video-studio"
          element={
            <AIVideoStudio />
          }
        />


        {/* Existing project */}

        <Route
          path="ai-video-studio/:projectId"
          element={
            <AIVideoStudio />
          }
        />


        {/* ==================================================
            OTHER DASHBOARD PAGES
        ================================================== */}

        <Route
          path="analytics"
          element={
            <Analytics />
          }
        />

        <Route
          path="publishing"
          element={
            <Publishing />
          }
        />

        <Route
          path="mlops"
           element={
            <MLOps />
         }
        />

        <Route
          path="voice-studio"
          element={
            <VoiceStudio />
          }
        />

        <Route
          path="profile"
          element={
            <Profile />
          }
        />

        <Route
          path="settings"
          element={
            <Settings />
          }
        />

      </Route>


      {/* ====================================================
          LEGACY PROJECT DETAIL ROUTE
      ==================================================== */}

      {/*
        Keep this route for now so an old saved URL does not
        break.

        IMPORTANT:
        The Projects page will NOT use this route anymore.

        Clicking a project now goes directly to:

        /dashboard/ai-video-studio/:projectId
      */}

      <Route
        path="/project/:id"
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <ProjectDetail />
            </DashboardLayout>
          </ProtectedRoute>
        }
      />

    </Routes>

  )
}


export default App