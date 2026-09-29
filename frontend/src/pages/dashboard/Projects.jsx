import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FiPlus,
  FiFolder,
  FiEdit3,
  FiLoader,
  FiAlertCircle
} from 'react-icons/fi'

import { api } from '../../services/api'


function Projects() {

  const navigate = useNavigate()

  const [projects, setProjects] =
    useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')


  // ==========================================================
  // LOAD REAL BACKEND PROJECTS
  // ==========================================================

  const loadProjects = async () => {

    try {

      setLoading(true)

      setError('')

      const result =
        await api.getBackendProjects()

      setProjects(
        result.projects || []
      )

    } catch (err) {

      console.error(
        'Failed to load projects:',
        err
      )

      setError(
        err.message ||
        'Failed to load projects.'
      )

    } finally {

      setLoading(false)

    }

  }


  useEffect(() => {

    loadProjects()

  }, [])


  // ==========================================================
  // CREATE NEW PROJECT
  // ==========================================================

  const handleNewProject = () => {

    localStorage.removeItem(
      'framecraft_active_project_id'
    )

    navigate(
      '/dashboard/ai-video-studio'
    )

  }


  // ==========================================================
  // OPEN EXISTING PROJECT
  // ==========================================================

  const handleOpenProject = (
    projectId
  ) => {

    // Remember currently opened project

    localStorage.setItem(
      'framecraft_active_project_id',
      projectId
    )

    // IMPORTANT:
    // Open directly in AI Video Studio.
    //
    // Do NOT open ProjectDetail.jsx.

    navigate(
      `/dashboard/ai-video-studio/${projectId}`
    )

  }


  // ==========================================================
  // FORMAT DATE
  // ==========================================================

  const formatDate = (
    date
  ) => {

    if (!date) {
      return 'Not available'
    }

    try {

      return new Date(
        date
      ).toLocaleDateString(
        'en-IN',
        {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        }
      )

    } catch {

      return date

    }

  }


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <div
        style={{
          padding: '40px',
          textAlign: 'center'
        }}
      >

        <FiLoader
          size={24}
          style={{
            animation:
              'spin 1s linear infinite'
          }}
        />

        <p>
          Loading projects...
        </p>

      </div>

    )

  }


  // ==========================================================
  // RENDER
  // ==========================================================

  return (

    <div
      style={{
        padding: '24px',
        maxWidth: '1400px',
        margin: '0 auto'
      }}
    >

      {/* ====================================================
          HEADER
      ==================================================== */}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
          gap: '15px'
        }}
      >

        <div>

          <h1
            style={{
              margin: 0,
              fontSize: '26px',
              fontWeight: 700
            }}
          >
            Projects
          </h1>

          <p
            style={{
              marginTop: '6px',
              color: '#6b7280'
            }}
          >
            Open a project to continue editing,
            upload media or generate your video.
          </p>

        </div>


        <button
          type="button"
          onClick={
            handleNewProject
          }
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '11px 16px',
            border: 'none',
            borderRadius: '8px',
            background: '#7c3aed',
            color: '#ffffff',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >

          <FiPlus />

          New Project

        </button>

      </div>


      {/* ====================================================
          ERROR
      ==================================================== */}

      {error && (

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 15px',
            marginBottom: '20px',
            background: '#fef2f2',
            color: '#b91c1c',
            borderRadius: '8px'
          }}
        >

          <FiAlertCircle />

          {error}

        </div>

      )}


      {/* ====================================================
          EMPTY STATE
      ==================================================== */}

      {!projects.length && !error && (

        <div
          style={{
            background: '#ffffff',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            padding: '50px 20px',
            textAlign: 'center'
          }}
        >

          <FiFolder
            size={40}
            style={{
              marginBottom: '10px'
            }}
          />

          <h2>
            No projects yet
          </h2>

          <p
            style={{
              color: '#6b7280'
            }}
          >
            Create your first FrameCraft AI
            video project.
          </p>

          <button
            type="button"
            onClick={
              handleNewProject
            }
            style={{
              marginTop: '10px',
              padding: '11px 18px',
              border: 'none',
              borderRadius: '8px',
              background: '#7c3aed',
              color: '#ffffff',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Create Project
          </button>

        </div>

      )}


      {/* ====================================================
          PROJECT GRID
      ==================================================== */}

      {projects.length > 0 && (

        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px'
          }}
        >

          {projects.map(
            project => (

              <div
                key={project.id}
                onClick={() =>
                  handleOpenProject(
                    project.id
                  )
                }
                style={{
                  background: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition:
                    'box-shadow 0.2s ease'
                }}
              >

                {/* Project icon */}

                <div
                  style={{
                    width: '46px',
                    height: '46px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '10px',
                    background: '#f3e8ff',
                    marginBottom: '15px'
                  }}
                >

                  <FiFolder
                    size={22}
                  />

                </div>


                {/* Name */}

                <h2
                  style={{
                    margin: 0,
                    fontSize: '18px',
                    fontWeight: 700
                  }}
                >
                  {project.name}
                </h2>


                {/* Description */}

                <p
                  style={{
                    color: '#6b7280',
                    fontSize: '13px',
                    minHeight: '38px',
                    marginTop: '8px'
                  }}
                >
                  {project.description ||
                    'No description'}
                </p>


                {/* Project information */}

                <div
                  style={{
                    display: 'flex',
                    gap: '15px',
                    marginTop: '15px',
                    fontSize: '12px',
                    color: '#6b7280'
                  }}
                >

                  <span>
                    {project.images?.length || 0}
                    {' '}
                    images
                  </span>

                  <span>
                    {project.videos?.length || 0}
                    {' '}
                    videos
                  </span>

                  <span>
                    {project.music?.length || 0}
                    {' '}
                    music
                  </span>

                </div>


                {/* Updated */}

                <div
                  style={{
                    marginTop: '12px',
                    fontSize: '11px',
                    color: '#9ca3af'
                  }}
                >

                  Updated:
                  {' '}
                  {formatDate(
                    project.updated_at
                  )}

                </div>


                {/* Open */}

                <div
                  style={{
                    marginTop: '18px',
                    paddingTop: '15px',
                    borderTop:
                      '1px solid #f0f0f0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '7px',
                    color: '#7c3aed',
                    fontSize: '13px',
                    fontWeight: 600
                  }}
                >

                  <FiEdit3 />

                  Open in AI Video Studio

                </div>

              </div>

            )
          )}

        </div>

      )}

    </div>

  )

}


export default Projects