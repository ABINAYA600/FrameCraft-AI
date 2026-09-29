import { useEffect, useMemo, useRef, useState } from 'react'



import { useNavigate, useParams } from 'react-router-dom'



import {



  FiArrowLeft,



  FiCheckCircle,



  FiFilm,



  FiImage,



  FiLoader,



  FiMusic,



  FiMic,



  FiMicOff,



  FiSave,



  FiTrash2,



  FiUpload,



  FiVideo,



  FiAlertCircle



} from 'react-icons/fi'







import { api } from '../../services/api'







const API_BASE_URL = 'http://127.0.0.1:8000'







const MEDIA_TYPES = {



  images: {



    label: 'Images',



    accept: 'image/*',



    icon: FiImage



  },



  videos: {



    label: 'Videos',



    accept: 'video/*',



    icon: FiVideo



  },



  music: {



    label: 'Music',



    accept: 'audio/*,.wav,.mp3,.m4a,.aac,.ogg',



    icon: FiMusic



  }



}







function AIVideoStudio() {



  const { projectId: routeProjectId } = useParams()



  const navigate = useNavigate()







  const [projectId, setProjectId] = useState(



    routeProjectId ||



      localStorage.getItem('framecraft_active_project_id') ||



      ''



  )







  const [projectName, setProjectName] = useState('')



  const [description, setDescription] = useState('')



  const [script, setScript] = useState('')

  const [isListening, setIsListening] = useState(false)

  const speechRecognitionRef = useRef(null)



  const [mediaSource, setMediaSource] = useState('both')
  const [musicMode, setMusicMode] = useState('ai')
  const [selectedMusicId, setSelectedMusicId] = useState('')
  const [musicSearch, setMusicSearch] = useState('')
  const [musicSearchResults, setMusicSearchResults] = useState([])
  const [musicSearching, setMusicSearching] = useState(false)

  const [aiMusicRecommendations, setAiMusicRecommendations] = useState([])
  const [aiMusicAnalysis, setAiMusicAnalysis] = useState(null)
  const [aiMusicLoading, setAiMusicLoading] = useState(false)







  const [images, setImages] = useState([])



  const [videos, setVideos] = useState([])



  const [music, setMusic] = useState([])

  // Files selected before Save Project are queued locally.
  // They are uploaded automatically when the project is saved.
  const [pendingUploads, setPendingUploads] = useState({
    images: [],
    videos: [],
    music: []
  })







  const [loadingProject, setLoadingProject] = useState(false)



  const [saving, setSaving] = useState(false)



  const [generating, setGenerating] = useState(false)



  const [uploadingType, setUploadingType] = useState('')










  const [outputName, setOutputName] = useState('framecraft_output.mp4')
  const [thumbnailTitle, setThumbnailTitle] = useState('FrameCraft AI')










  const [generatedResult, setGeneratedResult] = useState(null)



  // Prevent accidental double-clicks / duplicate generation jobs.

  const generationLockRef = useRef(false)







  const [error, setError] = useState('')



  const [success, setSuccess] = useState('')







  const fileInputRefs = {



    images: useRef(null),



    videos: useRef(null),



    music: useRef(null)



  }







  const isExistingProject = Boolean(projectId)







  // ==========================================================



  // VOICE-TO-SCRIPT
  // Uses the browser's built-in Speech Recognition API.
  // No audio is uploaded to the FrameCraft backend.

  const stopVoiceInput = () => {
    if (speechRecognitionRef.current) {
      speechRecognitionRef.current.stop()
      speechRecognitionRef.current = null
    }
    setIsListening(false)
  }

  const handleVoiceInput = () => {
    if (isListening) {
      stopVoiceInput()
      return
    }

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setError(
        'Voice input is not supported in this browser. Please use Google Chrome or Microsoft Edge.'
      )
      return
    }

    const recognition = new SpeechRecognition()
    speechRecognitionRef.current = recognition

    recognition.lang = 'en-IN'
    recognition.continuous = true
    recognition.interimResults = false

    // Chrome can emit a late `network` error even after it has already
    // returned valid final transcripts. Keep track of whether speech was
    // successfully received so that a successful dictation is not shown
    // as a failure.
    let receivedTranscript = false
    let voiceError = false

    recognition.onstart = () => {
      setIsListening(true)
      setError('')
      setSuccess('Listening... Speak your script.')
    }

    recognition.onresult = (event) => {
      let transcript = ''

      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript
        }
      }

      if (transcript.trim()) {
        receivedTranscript = true
        setError('')
        setScript((currentScript) => {
          const separator = currentScript.trim() ? ' ' : ''
          return `${currentScript}${separator}${transcript.trim()}`
        })
      }
    }

    recognition.onerror = (event) => {
      // Some Chrome versions report `network` after successful speech
      // recognition. If we already received final text, do not surface that
      // late event as an error.
      if (event.error === 'network' && receivedTranscript) {
        return
      }

      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        voiceError = true
        setError(
          'Microphone permission was denied. Allow microphone access in your browser and try again.'
        )
      } else if (event.error === 'no-speech') {
        voiceError = true
        setError('No speech detected. Click Voice and try speaking again.')
      } else if (event.error !== 'aborted') {
        voiceError = true
        setError(`Voice input error: ${event.error}`)
      }

      setIsListening(false)
      speechRecognitionRef.current = null
    }

    recognition.onend = () => {
      setIsListening(false)
      speechRecognitionRef.current = null

      if (receivedTranscript && !voiceError) {
        setError('')
        setSuccess('Voice input added to the script.')
      } else if (!voiceError) {
        setSuccess('')
      }
    }

    recognition.start()
  }

  useEffect(() => {
    return () => {
      if (speechRecognitionRef.current) {
        speechRecognitionRef.current.stop()
        speechRecognitionRef.current = null
      }
    }
  }, [])



  // URL HELPERS



  // ==========================================================







  const handleSearchMusic = async () => {
    try {
      setMusicSearching(true)
      setError('')

      const params = new URLSearchParams()
      const query = musicSearch.trim()

      // Search only the local FrameCraft catalog.
      params.set('source', 'framecraft')
      if (query) {
        params.set('q', query)
      }

      const response = await fetch(
        `${API_BASE_URL}/music/search?${params.toString()}`
      )

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'Music search failed.')
      }

      const data = await response.json()
      const results = Array.isArray(data?.results)
        ? data.results
        : []

      setMusicSearchResults(results)
    } catch (err) {
      console.error('Music search failed:', err)
      setError(err?.message || 'Failed to search music.')
      setMusicSearchResults([])
    } finally {
      setMusicSearching(false)
    }
  }


  // ==========================================================
  // AI MUSIC RECOMMENDATION
  // ==========================================================

  const handleAIMusicSelect = async () => {
    const currentScript = script.trim()

    if (!currentScript) {
      setError('Enter a script first so AI Select can recommend music.')
      return
    }

    try {
      setAiMusicLoading(true)
      setError('')
      setSuccess('')
      setAiMusicRecommendations([])
      setAiMusicAnalysis(null)

      const response = await fetch(`${API_BASE_URL}/music/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          script: currentScript,
          limit: 5
        })
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'AI music recommendation failed.')
      }

      const data = await response.json()

      if (!data?.success) {
        throw new Error(data?.error || 'AI music recommendation failed.')
      }

      const recommendations = Array.isArray(data?.recommendations)
        ? data.recommendations
        : []

      setAiMusicAnalysis({
        mood: data?.mood || 'neutral',
        energy: data?.energy || 'medium'
      })

      setAiMusicRecommendations(recommendations)

      if (recommendations.length > 0) {
        const first = recommendations[0]
        const firstId =
          first?.id ||
          first?.filename ||
          first?.music ||
          first?.name ||
          ''

        if (firstId) {
          setSelectedMusicId(firstId)
        }

        setSuccess(
          `AI selected ${first?.music || first?.name || 'a FrameCraft track'} based on your script.`
        )
      } else {
        setSuccess('No matching FrameCraft music was found.')
      }
    } catch (err) {
      console.error('AI music recommendation failed:', err)
      setError(err?.message || 'Failed to get AI music recommendations.')
    } finally {
      setAiMusicLoading(false)
    }
  }


  const getProjectFileUrl = (projectFilePath, currentProjectId = projectId) => {



    if (!projectFilePath) {



      return ''



    }







    const value = String(projectFilePath)







    // Already a browser URL.



    if (



      value.startsWith('http://') ||



      value.startsWith('https://') ||



      value.startsWith('blob:')



    ) {



      return value



    }







    // Backend-relative URL.



   // Backend-relative URL.

if (value.startsWith('/')) {

  return `${API_BASE_URL}${value}`

}







    // Windows filesystem path:



    // C:\\\\...\backend\projects\project_xxxx\generated\file.mp4



    const normalized = value.replace(/\\/g, '/')







    const projectsMarker = '/projects/'



    const markerIndex = normalized.indexOf(projectsMarker)







    if (markerIndex !== -1) {



      const relativeProjectPath = normalized.substring(



        markerIndex + projectsMarker.length



      )







    return `${API_BASE_URL}/project-files/${relativeProjectPath}`



    }







    // Filename only.



    if (currentProjectId) {
      return `${API_BASE_URL}/project-files/${currentProjectId}/generated/${encodeURIComponent(value)}`
    }










    return value



  }







  const getGeneratedFile = (type) => {



    if (!generatedResult) {



      return null



    }







    const files = generatedResult.generated_files || []







    return files.find((file) => file?.type === type) || null



  }



  // Convert any backend file reference into a browser URL.

  // The backend may return a public URL, a relative URL, or a Windows

  // filesystem path. The UI must always use an HTTP URL.

  const normalizeGeneratedUrl = (value, currentProjectId = projectId) => {

    if (!value) {

      return ''

    }



    if (typeof value === 'object') {

      return normalizeGeneratedUrl(

        value.url ||

          value.path ||

          value.file_url ||

          value.file_path ||

          value.filename ||

          value.name,

        currentProjectId

      )

    }



    return getProjectFileUrl(

      String(value),

      currentProjectId

    )

  }



  const getVideoUrl = () => {

    if (!generatedResult) {

      return ''

    }



    const generatedVideo = getGeneratedFile('video')



    return normalizeGeneratedUrl(

      generatedResult.video_url ||

        generatedVideo?.url ||

        generatedResult.video_path ||

        generatedResult.video ||

        generatedResult.output_video ||

        generatedResult.output_path ||

        generatedVideo?.path ||

        generatedVideo?.file_url ||

        generatedVideo?.file_path

    )

  }



  const getMetadataUrl = () => {

    if (!generatedResult) {

      return ''

    }



    const generatedMetadata =

      getGeneratedFile('metadata')



    return normalizeGeneratedUrl(

      generatedResult.metadata_url ||

        generatedMetadata?.url ||

        generatedResult.metadata_path ||

        generatedMetadata?.path ||

        generatedMetadata?.file_url ||

        generatedMetadata?.file_path

    )

  }









  // ==========================================================



  // NORMALIZE GENERATION RESULT



  // ==========================================================



  const normalizeGenerationResult = (result) => {

    if (!result) {

      return null

    }



    const generatedFiles =

      Array.isArray(result.generated_files)

        ? result.generated_files

        : []



    const videoFile = generatedFiles.find(

      (file) => file?.type === 'video'

    )



    const metadataFile = generatedFiles.find(

      (file) => file?.type === 'metadata'

    )



    return {

      ...result,



      // Always normalize these values. Never put a Windows path

      // directly into <video src="">, <img src="">, or <a href="">.

      video_url: normalizeGeneratedUrl(

        result.video_url ||

          videoFile?.url ||

          result.video_path ||

          result.video ||

          result.output_video ||

          result.output_path ||

          videoFile?.path ||

          videoFile?.file_url ||

          videoFile?.file_path

      ),



      thumbnail_url: normalizeGeneratedUrl(

        result.thumbnail_url ||

          thumbnailFile?.url ||

          result.thumbnail_path ||

          result.thumbnail ||

          thumbnailFile?.path ||

          thumbnailFile?.file_url ||

          thumbnailFile?.file_path

      ),



      metadata_url: normalizeGeneratedUrl(

        result.metadata_url ||

          metadataFile?.url ||

          result.metadata_path ||

          metadataFile?.path ||

          metadataFile?.file_url ||

          metadataFile?.file_path

      )

    }

  }









  // ==========================================================



  // LOAD PROJECT



  // ==========================================================







  const loadProject = async (id) => {



    if (!id) {



      return



    }







    try {



      setLoadingProject(true)



      setError('')



      setSuccess('')







      const result = await api.getBackendProject(id)



      const project = result?.project || result







      if (!project) {



        throw new Error('Project data was not returned by the backend.')



      }







      setProjectId(project.id || id)



      setProjectName(project.name || '')



      setDescription(project.description || '')



      setScript(project.script || '')



      setMediaSource(project.media_source || 'both')
      setMusicMode(project.music_mode || 'ai')
      setSelectedMusicId(project.selected_music_id || '')







      setImages(



        Array.isArray(project.images)



          ? project.images



          : []



      )







      setVideos(



        Array.isArray(project.videos)



          ? project.videos



          : []



      )







      setMusic(



        Array.isArray(project.music)



          ? project.music



          : []



      )







      if (project.id) {



        localStorage.setItem(



          'framecraft_active_project_id',



          project.id



        )



      }







      const generated =



        Array.isArray(project.generated)



          ? project.generated



          : []







      if (generated.length > 0) {



        setGeneratedResult(



          normalizeGenerationResult({



            success: true,



            project_id: project.id,



            project,



            generated_files: generated



          })



        )



      }



    } catch (err) {



      console.error('Failed to load project:', err)







      setError(



        err?.message ||



          'Failed to load project.'



      )



    } finally {



      setLoadingProject(false)



    }



  }







  useEffect(() => {



    if (routeProjectId) {



      setProjectId(routeProjectId)







      localStorage.setItem(



        'framecraft_active_project_id',



        routeProjectId



      )







      loadProject(routeProjectId)



      return



    }







    const storedProjectId =



      localStorage.getItem(



        'framecraft_active_project_id'



      )







    if (storedProjectId) {



      setProjectId(storedProjectId)



      loadProject(storedProjectId)



    }



  }, [routeProjectId])







  // ==========================================================



  // RESET NEW PROJECT



  // ==========================================================







  const handleNewProject = () => {



    localStorage.removeItem(



      'framecraft_active_project_id'



    )







    setProjectId('')



    setProjectName('')



    setDescription('')



    setScript('')



    setMediaSource('both')







    setMusicMode('ai')
    setSelectedMusicId('')
    setMusicSearch('')
    setMusicSearchResults([])

    setImages([])



    setVideos([])



    setMusic([])

    setPendingUploads({
      images: [],
      videos: [],
      music: []
    })







    setGeneratedResult(null)







    setOutputName(



      'framecraft_output.mp4'



    )














    setError('')



    setSuccess('')







    window.scrollTo({



      top: 0,



      behavior: 'smooth'



    })



  }







  // ==========================================================



  // SAVE PROJECT



  // ==========================================================







  const handleSave = async () => {
    if (!projectName.trim()) {
      setError('Please enter a project name before saving.')
      return
    }

    try {
      setSaving(true)
      setError('')
      setSuccess('')

      let result

      if (!projectId) {
        result = await api.createBackendProject({
          name: projectName.trim(),
          description,
          script,
          mediaSource,
          musicMode,
          selectedMusicId
        })
      } else {
        result = await api.updateBackendProject({
          projectId,
          name: projectName.trim(),
          description,
          script,
          mediaSource,
          musicMode,
          selectedMusicId
        })
      }

      const project = result?.project || result
      const savedProjectId =
        project?.id || result?.project_id || projectId

      if (!savedProjectId) {
        throw new Error(
          'Project was saved but no project ID was returned.'
        )
      }

      setProjectId(savedProjectId)

      localStorage.setItem(
        'framecraft_active_project_id',
        savedProjectId
      )

      // Upload files selected before Save Project.
      const queuedUploads = pendingUploads
      const queuedFiles = [
        ...(queuedUploads.images || []).map((item) => ({
          mediaType: 'images',
          file: item.file
        })),
        ...(queuedUploads.videos || []).map((item) => ({
          mediaType: 'videos',
          file: item.file
        })),
        ...(queuedUploads.music || []).map((item) => ({
          mediaType: 'music',
          file: item.file
        }))
      ].filter((item) => item.file)

      if (queuedFiles.length > 0) {
        setUploadingType('queued')

        for (const item of queuedFiles) {
          await api.uploadProjectMedia({
            projectId: savedProjectId,
            mediaType: item.mediaType,
            file: item.file
          })
        }

        setPendingUploads({
          images: [],
          videos: [],
          music: []
        })
      }

      const refreshed =
        await api.getBackendProject(savedProjectId)

      const refreshedProject =
        refreshed?.project || refreshed

      setImages(
        Array.isArray(refreshedProject?.images)
          ? refreshedProject.images
          : []
      )

      setVideos(
        Array.isArray(refreshedProject?.videos)
          ? refreshedProject.videos
          : []
      )

      setMusic(
        Array.isArray(refreshedProject?.music)
          ? refreshedProject.music
          : []
      )

      setSuccess(
        queuedFiles.length > 0
          ? `Project saved and ${queuedFiles.length} selected media file${
              queuedFiles.length > 1 ? 's' : ''
            } uploaded successfully.`
          : projectId
            ? 'Project saved successfully.'
            : 'Project created and saved successfully.'
      )
    } catch (err) {
      console.error('Save failed:', err)
      setError(err?.message || 'Failed to save project.')
    } finally {
      setSaving(false)
      setUploadingType('')
    }
  }










  const handleUpload = async (
    mediaType,
    fileList
  ) => {
    const files = Array.from(fileList || [])

    if (!files.length) {
      return
    }

    try {
      setUploadingType(mediaType)
      setError('')
      setSuccess('')

      // Upload is allowed before Save Project.
      // Until a backend project exists, files are queued locally.
      if (!projectId) {
        const pendingItems = files.map((file, index) => ({
          id: `pending-${mediaType}-${Date.now()}-${index}`,
          name: file.name,
          filename: file.name,
          size: file.size,
          pending: true,
          file,
          url: URL.createObjectURL(file)
        }))

        setPendingUploads((previous) => ({
          ...previous,
          [mediaType]: [
            ...(previous[mediaType] || []),
            ...pendingItems
          ]
        }))

        if (mediaType === 'images') {
          setImages((previous) => [...previous, ...pendingItems])
        } else if (mediaType === 'videos') {
          setVideos((previous) => [...previous, ...pendingItems])
        } else {
          setMusic((previous) => [...previous, ...pendingItems])
        }

        setSuccess(
          `${files.length} ${mediaType} file${
            files.length > 1 ? 's' : ''
          } selected. Save the project to upload them.`
        )

        return
      }

      // Existing project: upload directly.
      for (const file of files) {
        await api.uploadProjectMedia({
          projectId,
          mediaType,
          file
        })
      }

      const result = await api.getBackendProject(projectId)
      const project = result?.project || result

      setImages(
        Array.isArray(project?.images) ? project.images : []
      )
      setVideos(
        Array.isArray(project?.videos) ? project.videos : []
      )
      setMusic(
        Array.isArray(project?.music) ? project.music : []
      )

      setSuccess(
        `${files.length} ${mediaType} file${
          files.length > 1 ? 's' : ''
        } uploaded successfully.`
      )
    } catch (err) {
      console.error(`Upload ${mediaType} failed:`, err)
      setError(
        err?.message || `Failed to upload ${mediaType}.`
      )
    } finally {
      setUploadingType('')
    }
  }




  const handleDeleteMedia = async (
    mediaId
  ) => {
    if (!mediaId) {
      return
    }

    // Pending files are local until the project is saved.
    if (String(mediaId).startsWith('pending-')) {
      const mediaType = String(mediaId).split('-')[1]

      setPendingUploads((previous) => ({
        ...previous,
        [mediaType]: (previous[mediaType] || []).filter(
          (item) => item.id !== mediaId
        )
      }))

      if (mediaType === 'images') {
        setImages((previous) =>
          previous.filter((item) => item.id !== mediaId)
        )
      } else if (mediaType === 'videos') {
        setVideos((previous) =>
          previous.filter((item) => item.id !== mediaId)
        )
      } else if (mediaType === 'music') {
        setMusic((previous) =>
          previous.filter((item) => item.id !== mediaId)
        )
      }

      return
    }

    if (!projectId) {
      return
    }

    try {
      setError('')
      setSuccess('')

      await api.deleteProjectMedia({
        projectId,
        mediaId
      })

      const result = await api.getBackendProject(projectId)
      const project = result?.project || result

      setImages(
        Array.isArray(project?.images) ? project.images : []
      )
      setVideos(
        Array.isArray(project?.videos) ? project.videos : []
      )
      setMusic(
        Array.isArray(project?.music) ? project.music : []
      )

      setSuccess('Media removed successfully.')
    } catch (err) {
      console.error('Delete media failed:', err)
      setError(
        err?.message || 'Failed to delete media.'
      )
    }
  }










  // ==========================================================



  // GENERATE VIDEO



  // ==========================================================



  const handleGenerate = async () => {

    // React state is asynchronous, so use a ref to prevent two

    // generation jobs from starting from rapid clicks.

    if (generationLockRef.current) {

      return

    }



    if (!projectId) {

      setError(

        'Save the project before generating the video.'

      )

      return

    }



    if (!script.trim()) {

      setError(

        'Please enter a script before generating the video.'

      )

      return

    }



    generationLockRef.current = true



    try {

      setGenerating(true)

      setError('')

      setSuccess('')

      setGeneratedResult(null)



      // Save the latest project state first.

      await api.updateBackendProject({

        projectId,

        name: projectName.trim(),

        description,

        script,

        mediaSource,
        musicMode,
        selectedMusicId

      })



      const result =

        await api.generateProjectContent({

          projectId,

          outputName,

          generateThumbnail: true,

          thumbnailTitle,

          musicMode,

          selectedMusicId

        })



      const normalized =

        normalizeGenerationResult(result)



      setGeneratedResult(normalized)



      setSuccess(

        'Video generated successfully.'

      )

    } catch (err) {

      console.error(

        'Video generation failed:',

        err

      )



      setError(

        err?.message ||

          'Video generation failed.'

      )

    } finally {

      setGenerating(false)



      window.setTimeout(() => {

        generationLockRef.current = false

      }, 500)

    }

  }









  // ==========================================================



  // MEDIA PREVIEW URL



  // ==========================================================







  const mediaUrl = (



    media



  ) => {



    if (!media) {



      return ''



    }







    return getProjectFileUrl(



      media.url ||



        media.path ||



        media.filename ||



        media.name



    )



  }







  // ==========================================================



  // COUNTS



  // ==========================================================







  const mediaCounts = useMemo(



    () => ({



      images: images.length,



      videos: videos.length,



      music: music.length



    }),



    [



      images.length,



      videos.length,



      music.length



    ]



  )







  // ==========================================================



  // LOADING



  // ==========================================================







  if (



    loadingProject &&



    projectId



  ) {



    return (



      <div



        style={{



          padding: '50px',



          textAlign: 'center'



        }}



      >



        <FiLoader



          size={28}



          style={{



            animation:



              'spin 1s linear infinite'



          }}



        />







        <p>



          Loading project...



        </p>



      </div>



    )



  }







  // ==========================================================



  // STYLES



  // ==========================================================







  const pageStyle = {



    padding: '24px',



    maxWidth: '1500px',



    margin: '0 auto'



  }







  const cardStyle = {



    background: '#ffffff',



    border: '1px solid #e5e7eb',



    borderRadius: '14px',



    padding: '24px',



    marginBottom: '22px',



    boxShadow:



      '0 1px 3px rgba(0,0,0,0.04)'



  }







  const inputStyle = {



    width: '100%',



    boxSizing: 'border-box',



    border: '1px solid #d1d5db',



    borderRadius: '9px',



    padding: '12px 14px',



    fontSize: '14px',



    outline: 'none'



  }







  const primaryButtonStyle = {



    display: 'inline-flex',



    alignItems: 'center',



    justifyContent: 'center',



    gap: '8px',



    border: 'none',



    borderRadius: '9px',



    padding: '11px 18px',



    background:



      'linear-gradient(135deg, #3b82f6, #7c3aed)',



    color: '#ffffff',



    fontWeight: 700,



    cursor: 'pointer'



  }







  const secondaryButtonStyle = {



    display: 'inline-flex',



    alignItems: 'center',



    justifyContent: 'center',



    gap: '8px',



    border: '1px solid #d1d5db',



    borderRadius: '9px',



    padding: '10px 16px',



    background: '#ffffff',



    color: '#374151',



    fontWeight: 600,



    cursor: 'pointer'



  }







  const sourceCardStyle = (selected) => ({



    flex: 1,



    minWidth: '220px',



    border: selected



      ? '2px solid #7c3aed'



      : '1px solid #d1d5db',



    borderRadius: '12px',



    padding: '18px',



    cursor: 'pointer',



    background: selected



      ? '#faf5ff'



      : '#ffffff'



  })







  // ==========================================================



  // RENDER



  // ==========================================================







  return (



    <div style={pageStyle}>







      {/* ====================================================



          HEADER



      ==================================================== */}







      <div



        style={{



          display: 'flex',



          justifyContent: 'space-between',



          alignItems: 'center',



          gap: '16px',



          marginBottom: '24px',



          flexWrap: 'wrap'



        }}



      >







        <div>







          <button



            type="button"



            onClick={() =>



              navigate('/dashboard/projects')



            }



            style={{



              ...secondaryButtonStyle,



              marginBottom: '12px'



            }}



          >



            <FiArrowLeft />



            Projects



          </button>







          <h1



            style={{



              margin: 0,



              fontSize: '28px',



              fontWeight: 800,



              color: '#111827'



            }}



          >



            AI Video Studio



          </h1>







          <p



            style={{



              marginTop: '7px',



              color: '#6b7280'



            }}



          >



            Create, save, edit and generate



            videos from your project workspace.



          </p>







        </div>







        <button



          type="button"



          onClick={handleNewProject}



          style={secondaryButtonStyle}



        >



          New Project



        </button>







      </div>







      {/* ====================================================



          ALERTS



      ==================================================== */}







      {error && (



        <div



          style={{



            display: 'flex',



            alignItems: 'center',



            gap: '9px',



            padding: '13px 16px',



            marginBottom: '18px',



            borderRadius: '9px',



            background: '#fef2f2',



            color: '#b91c1c',



            border: '1px solid #fecaca'



          }}



        >



          <FiAlertCircle />



          {error}



        </div>



      )}







      {success && (



        <div



          style={{



            display: 'flex',



            alignItems: 'center',



            gap: '9px',



            padding: '13px 16px',



            marginBottom: '18px',



            borderRadius: '9px',



            background: '#f0fdf4',



            color: '#15803d',



            border: '1px solid #bbf7d0'



          }}



        >



          <FiCheckCircle />



          {success}



        </div>



      )}







      {/* ====================================================



          PROJECT INFORMATION



      ==================================================== */}







      <div style={cardStyle}>







        <h2



          style={{



            marginTop: 0,



            fontSize: '20px'



          }}



        >



          Project Information



        </h2>







        <div



          style={{



            display: 'grid',



            gridTemplateColumns:



              'repeat(auto-fit, minmax(260px, 1fr))',



            gap: '18px'



          }}



        >







          <div>



            <label



              style={{



                display: 'block',



                fontWeight: 600,



                marginBottom: '7px'



              }}



            >



              Project Name



            </label>







            <input



              value={projectName}



              onChange={(event) =>



                setProjectName(



                  event.target.value



                )



              }



              placeholder="Enter project name"



              style={inputStyle}



            />



          </div>







          <div>



            <label



              style={{



                display: 'block',



                fontWeight: 600,



                marginBottom: '7px'



              }}



            >



              Description



            </label>







            <input



              value={description}



              onChange={(event) =>



                setDescription(



                  event.target.value



                )



              }



              placeholder="Describe your project"



              style={inputStyle}



            />



          </div>







        </div>







        <div



          style={{



            marginTop: '18px'



          }}



        >







          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              marginBottom: '7px'
            }}
          >
            <label
              style={{
                display: 'block',
                fontWeight: 600,
                margin: 0
              }}
            >
              Script
            </label>

            <button
              type="button"
              onClick={handleVoiceInput}
              title={isListening ? 'Stop voice input' : 'Speak your script'}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '7px',
                border: 'none',
                borderRadius: '10px',
                padding: '8px 12px',
                cursor: 'pointer',
                fontWeight: 600,
                background: isListening ? '#fee2e2' : '#eef2ff',
                color: isListening ? '#dc2626' : '#4f46e5'
              }}
            >
              {isListening ? <FiMicOff size={16} /> : <FiMic size={16} />}
              {isListening ? 'Stop' : 'Voice'}
            </button>
          </div>

          <p
            style={{
              margin: '0 0 9px',
              color: '#6b7280',
              fontSize: '13px'
            }}
          >
            Type your script or click Voice and speak it. Your speech will be converted into text here.
          </p>

          <textarea
            value={script}
            onChange={(event) =>
              setScript(event.target.value)
            }
            placeholder="Write your video script or use Voice..."
            rows={9}
            style={{
              ...inputStyle,
              resize: 'vertical',
              lineHeight: 1.55
            }}
          />







        </div>







      </div>







      {/* ====================================================



          MEDIA SOURCE



      ==================================================== */}







      <div style={cardStyle}>







        <h2



          style={{



            marginTop: 0,



            marginBottom: '5px'



          }}



        >



          Media Source



        </h2>







        <p



          style={{



            marginTop: 0,



            color: '#6b7280',



            fontSize: '14px'



          }}



        >



          Choose how FrameCraft AI should



          select visuals for your video.



        </p>







        <div



          style={{



            display: 'flex',



            gap: '14px',



            flexWrap: 'wrap',



            marginTop: '16px'



          }}



        >







          <div



            onClick={() =>



              setMediaSource('uploaded')



            }



            style={sourceCardStyle(



              mediaSource === 'uploaded'



            )}



          >



            <strong>



              Use my uploaded media



            </strong>







            <p



              style={{



                color: '#6b7280',



                fontSize: '13px',



                marginBottom: 0



              }}



            >



              Use images and videos uploaded



              to this project.



            </p>



          </div>







          <div



            onClick={() =>



              setMediaSource('ai')



            }



            style={sourceCardStyle(



              mediaSource === 'ai'



            )}



          >



            <strong>



              Let FrameCraft AI find media



            </strong>







            <p



              style={{



                color: '#6b7280',



                fontSize: '13px',



                marginBottom: 0



              }}



            >



              Use FrameCraft AI media retrieval



              for the scenes.



            </p>



          </div>







          <div



            onClick={() =>



              setMediaSource('both')



            }



            style={sourceCardStyle(



              mediaSource === 'both'



            )}



          >



            <strong>



              Use both



            </strong>







            <p



              style={{



                color: '#6b7280',



                fontSize: '13px',



                marginBottom: 0



              }}



            >



              Combine uploaded media with



              AI-retrieved media.



            </p>



          </div>







        </div>







      </div>







      {/* ====================================================



          MEDIA UPLOADS



      ==================================================== */}







      <div



        style={{



          display: 'grid',



          gridTemplateColumns:



            'repeat(auto-fit, minmax(280px, 1fr))',



          gap: '22px'



        }}



      >







        {Object.entries(



          MEDIA_TYPES



        ).map(



          ([mediaType, config]) => {







            const Icon = config.icon



            const items =



              mediaType === 'images'



                ? images



                : mediaType === 'videos'



                  ? videos



                  : music







            return (



              <div



                key={mediaType}



                style={cardStyle}



              >







                <div



                  style={{



                    display: 'flex',



                    alignItems: 'center',



                    justifyContent:



                      'space-between',



                    marginBottom: '15px'



                  }}



                >







                  <div



                    style={{



                      display: 'flex',



                      alignItems: 'center',



                      gap: '9px'



                    }}



                  >



                    <Icon />



                    <strong>



                      {config.label}



                    </strong>



                  </div>







                  <span



                    style={{



                      color: '#6b7280',



                      fontSize: '13px'



                    }}



                  >



                    {items.length}



                  </span>







                </div>







                <input



                  ref={



                    fileInputRefs[



                      mediaType



                    ]



                  }



                  type="file"



                  accept={



                    config.accept



                  }



                  multiple



                  hidden



                  disabled={
                    uploadingType === mediaType
                  }



                  onChange={(event) => {



                    handleUpload(



                      mediaType,



                      event.target.files



                    )







                    event.target.value = ''



                  }}



                />







                <button



                  type="button"



                  disabled={
                    uploadingType === mediaType
                  }



                  onClick={() =>



                    fileInputRefs[



                      mediaType



                    ]?.current?.click()



                  }



                  style={{



                    width: '100%',



                    border:



                      '1px dashed #a78bfa',



                    borderRadius: '10px',



                    padding: '16px',



                    background:



                      '#faf5ff',



                    color: '#7c3aed',



                    fontWeight: 700,



                    cursor:
                      uploadingType === mediaType
                        ? 'not-allowed'
                        : 'pointer',
                    opacity:
                      uploadingType === mediaType ? 0.6 : 1



                  }}



                >



                  {uploadingType ===



                  mediaType ? (



                    <>



                      <FiLoader



                        style={{



                          animation:



                            'spin 1s linear infinite'



                        }}



                      />



                      Uploading...



                    </>



                  ) : (



                    <>



                      <FiUpload />



                      {' '}



                      Upload {config.label}



                    </>



                  )}



                </button>







                {!projectId && items.length > 0 && (
                  <p
                    style={{
                      color: '#6b7280',
                      fontSize: '12px',
                      marginBottom: 0
                    }}
                  >
                    Selected files will be uploaded when you save the project.
                  </p>
                )}







                {items.length > 0 && (



                  <div



                    style={{



                      marginTop: '14px',



                      display: 'flex',



                      flexDirection:



                        'column',



                      gap: '8px'



                    }}



                  >







                    {items.map(



                      (item) => (



                        <div



                          key={



                            item.id ||



                            item.filename ||



                            item.name



                          }



                          style={{



                            display: 'flex',



                            alignItems:



                              'center',



                            justifyContent:



                              'space-between',



                            gap: '8px',



                            padding:



                              '9px 10px',



                            border:



                              '1px solid #e5e7eb',



                            borderRadius:



                              '8px',



                            fontSize:



                              '12px'



                          }}



                        >







                          <span



                            style={{



                              overflow:



                                'hidden',



                              textOverflow:



                                'ellipsis',



                              whiteSpace:



                                'nowrap'



                            }}



                            title={



                              item.name



                            }



                          >



                            {item.name ||



                              item.filename}



                          </span>







                          <button



                            type="button"



                            onClick={() =>



                              handleDeleteMedia(



                                item.id



                              )



                            }



                            style={{



                              border:



                                'none',



                              background:



                                'transparent',



                              color:



                                '#dc2626',



                              cursor:



                                'pointer',



                              flexShrink:



                                0



                            }}



                            title="Delete"



                          >



                            <FiTrash2 />



                          </button>







                        </div>



                      )



                    )}







                  </div>



                )}







              </div>



            )



          }



        )}







      </div>







      {/* ====================================================
          GENERATION OPTIONS
      ==================================================== */}

      <div style={cardStyle}>
        <h2 style={{ marginTop: 0 }}>Generation Options</h2>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '18px'
          }}
        >
          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '7px' }}>
              Output File Name
            </label>
            <input
              value={outputName}
              onChange={(event) => setOutputName(event.target.value)}
              placeholder="framecraft_output.mp4"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '7px' }}>
              Thumbnail Title
            </label>
            <input
              value={thumbnailTitle}
              onChange={(event) => setThumbnailTitle(event.target.value)}
              placeholder="FrameCraft AI"
              style={inputStyle}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: '7px' }}>
              Music Mode
            </label>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {[
                ['ai', 'AI Select'],
                ['uploaded', 'My Music'],
                ['search', 'Search Music']
              ].map(([mode, label]) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setMusicMode(mode)}
                  style={{
                    ...secondaryButtonStyle,
                    border: musicMode === mode ? '1px solid #7c3aed' : '1px solid #d1d5db',
                    background: musicMode === mode ? '#f5f3ff' : '#ffffff'
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div style={{ marginTop: '16px' }}>
          {musicMode === 'ai' && (
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px',
                  flexWrap: 'wrap'
                }}
              >
                <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
                  AI Select analyzes your script and recommends music from the FrameCraft catalog.
                </p>

                <button
                  type="button"
                  onClick={handleAIMusicSelect}
                  disabled={aiMusicLoading || !script.trim()}
                  style={{
                    ...secondaryButtonStyle,
                    minWidth: '150px',
                    border: '1px solid #7c3aed',
                    background: '#f5f3ff',
                    opacity: aiMusicLoading || !script.trim() ? 0.6 : 1
                  }}
                >
                  {aiMusicLoading ? 'Analyzing...' : '✨ AI Select Music'}
                </button>
              </div>

              {aiMusicAnalysis && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    background: '#fafafa',
                    border: '1px solid #e5e7eb',
                    fontSize: '12px',
                    color: '#4b5563'
                  }}
                >
                  <strong>Script analysis:</strong>{' '}
                  Mood: {aiMusicAnalysis.mood} • Energy: {aiMusicAnalysis.energy}
                </div>
              )}

              {aiMusicRecommendations.length > 0 && (
                <div style={{ marginTop: '12px', display: 'grid', gap: '8px' }}>
                  {aiMusicRecommendations.map((item, index) => {
                    const id =
                      item?.id ||
                      item?.filename ||
                      item?.music ||
                      item?.name ||
                      `ai-music-${index}`

                    const selected = selectedMusicId === id

                    return (
                      <div
                        key={id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          gap: '12px',
                          padding: '12px',
                          borderRadius: '8px',
                          border: selected
                            ? '1px solid #7c3aed'
                            : '1px solid #e5e7eb',
                          background: selected ? '#f5f3ff' : '#ffffff'
                        }}
                      >
                        <div style={{ minWidth: 0 }}>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <strong>
                              {item?.music || item?.name || item?.filename || 'Untitled track'}
                            </strong>

                            {item?.recommended && (
                              <span
                                style={{
                                  fontSize: '11px',
                                  padding: '3px 7px',
                                  borderRadius: '999px',
                                  background: '#ede9fe',
                                  color: '#6d28d9',
                                  fontWeight: 600
                                }}
                              >
                                AI Recommended
                              </span>
                            )}
                          </div>

                          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                            Match: {Math.round(Number(item?.match_score || 0))}%
                            {item?.match_reason ? ` • ${item.match_reason}` : ''}
                          </div>

                          <div style={{ fontSize: '11px', color: '#059669', marginTop: '4px' }}>
                            FrameCraft catalog • usable in generated videos
                          </div>
                        </div>

                        <button
                          type="button"
                          onClick={() => setSelectedMusicId(id)}
                          style={{
                            ...secondaryButtonStyle,
                            border: selected
                              ? '1px solid #7c3aed'
                              : '1px solid #d1d5db',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {selected ? '✓ Selected' : 'Use'}
                        </button>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}

          {musicMode === 'uploaded' && (
            <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
              Upload music in the Music section above. My Music will use your selected uploaded track.
            </p>
          )}

          {musicMode === 'search' && (
            <div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  value={musicSearch}
                  onChange={(event) => setMusicSearch(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') handleSearchMusic()
                  }}
                  placeholder="Search FrameCraft music by name, mood, genre..."
                  style={{ ...inputStyle, flex: 1 }}
                />
                <button
                  type="button"
                  onClick={handleSearchMusic}
                  disabled={musicSearching}
                  style={{ ...secondaryButtonStyle, minWidth: '110px' }}
                >
                  {musicSearching ? 'Searching...' : 'Search'}
                </button>
              </div>

              <div style={{ marginTop: '10px', display: 'grid', gap: '8px' }}>
                {musicSearchResults.map((item, index) => {
                  const id =
                    item?.id ||
                    item?.filename ||
                    item?.name ||
                    `framecraft-music-${index}`
                  const selected = selectedMusicId === id

                  return (
                    <div
                      key={id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '12px',
                        padding: '12px',
                        borderRadius: '8px',
                        border: selected
                          ? '1px solid #7c3aed'
                          : '1px solid #e5e7eb',
                        background: selected ? '#f5f3ff' : '#ffffff'
                      }}
                    >
                      <div style={{ minWidth: 0 }}>
                        <strong>
                          {item?.name || item?.filename || 'Untitled track'}
                        </strong>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                          {[item?.mood, item?.genre, item?.energy]
                            .filter(Boolean)
                            .join(' • ') || 'FrameCraft music'}
                        </div>
                        <div style={{ fontSize: '11px', color: '#059669', marginTop: '4px' }}>
                          FrameCraft catalog • usable in generated videos
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() => setSelectedMusicId(id)}
                        style={{
                          ...secondaryButtonStyle,
                          border: selected
                            ? '1px solid #7c3aed'
                            : '1px solid #d1d5db',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {selected ? '✓ Selected' : 'Use'}
                      </button>
                    </div>
                  )
                })}

                {!musicSearching && musicSearchResults.length === 0 && (
                  <p style={{ margin: 0, fontSize: '13px', color: '#6b7280' }}>
                    Search the FrameCraft music catalog. Only FrameCraft catalog tracks are available for generated videos.
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ====================================================



          GENERATED RESULT



      ==================================================== */}







      {generatedResult && (



        <div style={cardStyle}>







          <h2



            style={{



              marginTop: 0



            }}



          >



            Generated Result



          </h2>







          {getVideoUrl() ? (



            <video



              controls



              preload="metadata"



              src={getVideoUrl()}



              style={{



                width: '100%',



                maxHeight: '650px',



                borderRadius: '10px',



                background: '#111827',



                display: 'block'



              }}



              onError={(event) => {



                console.error(



                  'Generated video failed to load:',



                  getVideoUrl(),



                  event



                )



              }}



            />



          ) : (



            <div



              style={{



                padding: '30px',



                borderRadius: '10px',



                background: '#f9fafb',



                color: '#6b7280'



              }}



            >



              Video was generated, but



              no public video URL was returned.



            </div>



          )}







          {getMetadataUrl() && (



            <a



              href={getMetadataUrl()}



              target="_blank"



              rel="noreferrer"



              style={{



                display: 'inline-block',



                marginTop: '18px',



                color: '#7c3aed',



                fontWeight: 600



              }}



            >



              Open generated metadata



            </a>



          )}







          <div



            style={{



              marginTop: '18px',



              padding: '14px',



              borderRadius: '9px',



              background: '#f9fafb',



              color: '#374151',



              fontSize: '14px'



            }}



          >



            Metadata generated successfully.



          </div>







        </div>



      )}







      {/* ====================================================



          STICKY ACTION BAR



      ==================================================== */}







      <div



        style={{



          position: 'sticky',



          bottom: '0',



          zIndex: 20,



          display: 'flex',



          justifyContent: 'flex-end',



          gap: '12px',



          padding: '15px',



          marginTop: '8px',



          background:



            'rgba(255,255,255,0.96)',



          borderTop:



            '1px solid #e5e7eb',



          backdropFilter:



            'blur(8px)'



        }}



      >







        <button



          type="button"



          onClick={handleSave}



          disabled={saving}



          style={{



            ...secondaryButtonStyle,



            opacity:



              saving ? 0.7 : 1



          }}



        >



          {saving ? (



            <FiLoader



              style={{



                animation:



                  'spin 1s linear infinite'



              }}



            />



          ) : (



            <FiSave />



          )}







          {saving



            ? 'Saving...'



            : projectId



              ? 'Save Changes'



              : 'Save Project'}



        </button>







        <button



          type="button"



          onClick={handleGenerate}



          disabled={



            generating ||



            !projectId ||



            !script.trim()



          }



          style={{



            ...primaryButtonStyle,



            opacity:



              generating ||



              !projectId ||



              !script.trim()



                ? 0.65



                : 1,



            cursor:



              generating ||



              !projectId ||



              !script.trim()



                ? 'not-allowed'



                : 'pointer'



          }}



        >







          {generating ? (



            <FiLoader



              style={{



                animation:



                  'spin 1s linear infinite'



              }}



            />



          ) : (



            <FiFilm />



          )}







          {generating



            ? 'Generating Video...'



            : 'Generate Video'}







        </button>







      </div>







    </div>



  )



}







export default AIVideoStudio