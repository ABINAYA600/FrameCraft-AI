const API_BASE_URL = 'http\://127.0.0.1:8000'



// ============================================================

// RESPONSE HELPER

// ============================================================



const handleResponse = async (

  response,

  defaultMessage

) => {

  if (!response.ok) {

    let errorMessage = defaultMessage



    try {

      const errorData = await response.json()



      if (

        typeof errorData?.detail === 'string'

      ) {

        errorMessage = errorData.detail

      } else if (

        typeof errorData?.message === 'string'

      ) {

        errorMessage = errorData.message

      } else if (

        typeof errorData?.error === 'string'

      ) {

        errorMessage = errorData.error

      }

    } catch {

      try {

        const text = await response.text()



        if (text) {

          errorMessage = text

        }

      } catch {

        // Keep default error message.

      }

    }



    throw new Error(errorMessage)

  }



  return response.json()

}





// ============================================================

// API

// ============================================================



export const api = {



  // ==========================================================

  // HEALTH / STATUS

  // ==========================================================



  getStatus: async () => {

    const response = await fetch(

      `${API_BASE_URL}/status`

    )



    return handleResponse(

      response,

      'Failed to get backend status.'

    )

  },





  // ==========================================================

  // GENERIC CONTENT GENERATION

  // ==========================================================



  generateContent: async ({

    script,

    outputName = 'framecraft_output.mp4',

    generateThumbnail = true,

    thumbnailTitle = null

  }) => {



    const response = await fetch(

      `${API_BASE_URL}/generate`,

      {

        method: 'POST',



        headers: {

          'Content-Type': 'application/json'

        },



        body: JSON.stringify({

          script,

          output_name: outputName,

          generate_thumbnail: generateThumbnail,

          thumbnail_title: thumbnailTitle

        })

      }

    )



    return handleResponse(

      response,

      'Failed to generate content.'

    )

  },





  // ==========================================================

  // PROJECTS

  // ==========================================================



  getBackendProjects: async () => {

    const response = await fetch(

      `${API_BASE_URL}/projects`

    )



    return handleResponse(

      response,

      'Failed to load projects.'

    )

  },





  getBackendProject: async (

    projectId

  ) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}`

    )



    return handleResponse(

      response,

      'Failed to load project.'

    )

  },





  createBackendProject: async ({

    name,

    description = '',

    script = '',

    mediaSource = 'both'

  }) => {



    const response = await fetch(

      `${API_BASE_URL}/projects`,

      {

        method: 'POST',



        headers: {

          'Content-Type': 'application/json'

        },



        body: JSON.stringify({

          name,

          description,

          script,

          media_source: mediaSource

        })

      }

    )



    return handleResponse(

      response,

      'Failed to create project.'

    )

  },





  updateBackendProject: async ({

    projectId,

    name,

    description = '',

    script = '',

    mediaSource = 'both'

  }) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}`,

      {

        method: 'PUT',



        headers: {

          'Content-Type': 'application/json'

        },



        body: JSON.stringify({

          name,

          description,

          script,

          media_source: mediaSource

        })

      }

    )



    return handleResponse(

      response,

      'Failed to update project.'

    )

  },





  // ==========================================================

  // PROJECT MEDIA

  // ==========================================================



  uploadProjectMedia: async ({

    projectId,

    mediaType,

    file

  }) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    if (!mediaType) {

      throw new Error(

        'Media type is required.'

      )

    }



    if (!file) {

      throw new Error(

        'Please select a file.'

      )

    }



    const formData = new FormData()



    formData.append(

      'media_type',

      mediaType

    )



    formData.append(

      'file',

      file

    )



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/media`,

      {

        method: 'POST',

        body: formData

      }

    )



    return handleResponse(

      response,

      'Failed to upload project media.'

    )

  },





  deleteProjectMedia: async ({

    projectId,

    mediaId

  }) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    if (!mediaId) {

      throw new Error(

        'Media ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/media/${encodeURIComponent(mediaId)}`,

      {

        method: 'DELETE'

      }

    )



    return handleResponse(

      response,

      'Failed to delete project media.'

    )

  },





  // ==========================================================

  // PROJECT VIDEO GENERATION

  // ==========================================================



  generateProjectContent: async ({

    projectId,

    outputName = 'framecraft_output.mp4',

    generateThumbnail = true,

    thumbnailTitle = null

  }) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required before generating the video.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/generate`,

      {

        method: 'POST',



        headers: {

          'Content-Type': 'application/json'

        },



        body: JSON.stringify({

          output_name: outputName,

          generate_thumbnail: generateThumbnail,

          thumbnail_title: thumbnailTitle

        })

      }

    )



    return handleResponse(

      response,

      'Failed to generate project video.'

    )

  },





  getProjectGeneratedFiles: async (

    projectId

  ) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/generated`

    )



    return handleResponse(

      response,

      'Failed to load generated project files.'

    )

  },





  // ==========================================================

  // MUSIC

  // ==========================================================



  getMusicCatalog: async ({

    source = 'framecraft',

    mood = '',

    genre = '',

    energy = '',

    market = 'IN',

    offset = 0,

    limit = 50

  } = {}) => {



    const params = new URLSearchParams()



    params.set(

      'source',

      source

    )



    params.set(

      'offset',

      String(offset)

    )



    params.set(

      'limit',

      String(limit)

    )



    if (mood) {

      params.set(

        'mood',

        mood

      )

    }



    if (genre) {

      params.set(

        'genre',

        genre

      )

    }



    if (energy) {

      params.set(

        'energy',

        energy

      )

    }



    if (market) {

      params.set(

        'market',

        market

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/music/search?${params.toString()}`

    )



    return handleResponse(

      response,

      'Failed to load music catalog.'

    )

  },





  searchMusic: async ({

    query = '',

    source = 'all',

    mood = '',

    genre = '',

    energy = '',

    market = 'IN',

    offset = 0,

    limit = 50

  } = {}) => {



    const params = new URLSearchParams()



    params.set(

      'q',

      query

    )



    params.set(

      'source',

      source

    )



    params.set(

      'offset',

      String(offset)

    )



    params.set(

      'limit',

      String(limit)

    )



    if (mood) {

      params.set(

        'mood',

        mood

      )

    }



    if (genre) {

      params.set(

        'genre',

        genre

      )

    }



    if (energy) {

      params.set(

        'energy',

        energy

      )

    }



    if (market) {

      params.set(

        'market',

        market

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/music/search?${params.toString()}`

    )



    return handleResponse(

      response,

      'Failed to search music.'

    )

  },





  recommendMusic: async ({

    script,

    limit = 5

  }) => {



    if (!script?.trim()) {

      throw new Error(

        'Script is required for AI music recommendation.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/music/recommend`,

      {

        method: 'POST',



        headers: {

          'Content-Type': 'application/json'

        },



        body: JSON.stringify({

          script,

          limit

        })

      }

    )



    return handleResponse(

      response,

      'Failed to get AI music recommendations.'

    )

  },





  // ==========================================================

  // DASHBOARD

  // ==========================================================



  getDashboardOverview: async () => {



    const response = await fetch(

      `${API_BASE_URL}/dashboard/overview`

    )



    return handleResponse(

      response,

      'Failed to load dashboard overview.'

    )

  },





  getDashboardStats: async () => {



    const data =

      await api.getDashboardOverview()



    return (

      data?.stats || {

        totalProjects: 0,

        videosGenerated: 0,

        scheduledPosts: 0,

        audienceEngagement: 0

      }

    )

  },





  getProjects: async () => {



    const data =

      await api.getBackendProjects()



    const projects =

      Array.isArray(data)

        ? data

        : (

            data?.projects || []

          )



    return projects.map(

      (project) => ({

        ...project,



        date:

          project.date ||

          project.updated_at ||

          project.created_at ||

          'Recently',



        status:

          project.status ||

          (

            project.generated_videos?.length

              ? 'Completed'

              : 'In Progress'

          ),



        views:

          Number(

            project.views || 0

          )

      })

    )

  },





  getActivityTimeline: async () => {



    const data =

      await api.getDashboardOverview()



    return (

      data?.activities || []

    )

  },





  // ==========================================================

  // COMMENTS

  // ==========================================================



  processComment: async ({

    comment,

    creatorId = null

  }) => {



    const response = await fetch(

      `${API_BASE_URL}/comments/process`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          comment,

          creator_id: creatorId

        })

      }

    )



    return handleResponse(

      response,

      'Failed to process comment.'

    )

  },





  analyzeComment: async ({

    comment,

    creatorId = null,

    projectId = null,

    videoId = null,

    occurredAt = null

  }) => {



    const response = await fetch(

      `${API_BASE_URL}/comments/analyze`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          comment,

          creator_id: creatorId,

          project_id: projectId,

          video_id: videoId,

          occurred_at: occurredAt

        })

      }

    )



    return handleResponse(

      response,

      'Failed to analyze comment.'

    )

  },





  analyzeCommentsBatch: async ({

    comments = [],

    projectId = null,

    videoId = null

  }) => {



    const response = await fetch(

      `${API_BASE_URL}/comments/analyze-batch`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          comments,

          project_id: projectId,

          video_id: videoId

        })

      }

    )



    return handleResponse(

      response,

      'Failed to analyze comments.'

    )

  },





  getCommentSummary: async ({

    projectId = null,

    videoId = null,

    date = null

  } = {}) => {



    const params = new URLSearchParams()



    if (projectId) {

      params.set(

        'project_id',

        projectId

      )

    }



    if (videoId) {

      params.set(

        'video_id',

        videoId

      )

    }



    if (date) {

      params.set(

        'date',

        date

      )

    }



    const query =

      params.toString()



    const response = await fetch(

      `${API_BASE_URL}/comments/summary${query ? `?${query}` : ''}`

    )



    return handleResponse(

      response,

      'Failed to load comment summary.'

    )

  },





  getLiveComments: async ({

    projectId = null,

    videoId = null,

    date = null,

    limit = 100

  } = {}) => {



    const params = new URLSearchParams()



    if (projectId) {

      params.set(

        'project_id',

        projectId

      )

    }



    if (videoId) {

      params.set(

        'video_id',

        videoId

      )

    }



    if (date) {

      params.set(

        'date',

        date

      )

    }



    params.set(

      'limit',

      String(limit)

    )



    const response = await fetch(

      `${API_BASE_URL}/comments/live?${params.toString()}`

    )



    return handleResponse(

      response,

      'Failed to load live comments.'

    )

  },





  getPendingReplies: async () => {



    const response = await fetch(

      `${API_BASE_URL}/comments/pending`

    )



    return handleResponse(

      response,

      'Failed to load pending replies.'

    )

  },





  getAllReplies: async () => {



    const response = await fetch(

      `${API_BASE_URL}/comments/replies`

    )



    return handleResponse(

      response,

      'Failed to load replies.'

    )

  },





  approveReply: async (

    replyId

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/comments/${encodeURIComponent(replyId)}/approve`,

      {

        method: 'POST'

      }

    )



    return handleResponse(

      response,

      'Failed to approve reply.'

    )

  },





  rejectReply: async (

    replyId

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/comments/${encodeURIComponent(replyId)}/reject`,

      {

        method: 'POST'

      }

    )



    return handleResponse(

      response,

      'Failed to reject reply.'

    )

  },





  // ==========================================================

  // VIDEO ANALYSIS

  // ==========================================================



  analyzeProjectVideo: async (

    projectId,

    videoId

  ) => {



    if (!projectId) {

      throw new Error(

        'Project ID is required.'

      )

    }



    if (!videoId) {

      throw new Error(

        'Video ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/projects/${encodeURIComponent(projectId)}/videos/${encodeURIComponent(videoId)}/analyze`,

      {

        method: 'POST'

      }

    )



    return handleResponse(

      response,

      'Failed to analyze uploaded video.'

    )

  },





  // ==========================================================

  // CREATOR

  // ==========================================================



  analyzeCreator: async (

    creatorData = {}

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/creator/analyze`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify(

          creatorData

        )

      }

    )



    return handleResponse(

      response,

      'Failed to analyze creator.'

    )

  },





  getCreatorProfile: async () => {



    const response = await fetch(

      `${API_BASE_URL}/creator/profile`

    )



    return handleResponse(

      response,

      'Failed to load creator profile.'

    )

  },





  updateCreatorProfile: async (

    profile

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/creator/profile`,

      {

        method: 'PUT',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify(

          profile

        )

      }

    )



    return handleResponse(

      response,

      'Failed to update creator profile.'

    )

  },





  // ==========================================================

  // SETTINGS

  // ==========================================================



  getSettings: async () => {



    const response = await fetch(

      `${API_BASE_URL}/settings`

    )



    return handleResponse(

      response,

      'Failed to load settings.'

    )

  },





  updateSettings: async (

    settings

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/settings`,

      {

        method: 'PUT',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify(

          settings

        )

      }

    )



    return handleResponse(

      response,

      'Failed to update settings.'

    )

  },





  // ==========================================================

  // PUBLISHING RECORDS

  // ==========================================================



  getPublishingPosts: async () => {



    const response = await fetch(

      `${API_BASE_URL}/publishing`

    )



    return handleResponse(

      response,

      'Failed to load publishing posts.'

    )

  },





  createPublishingPost: async (

    post

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/publishing`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify(

          post

        )

      }

    )



    return handleResponse(

      response,

      'Failed to create publishing record.'

    )

  },





  updatePublishingPost: async (

    postId,

    status

  ) => {



    if (!postId) {

      throw new Error(

        'Publishing post ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/publishing/${encodeURIComponent(postId)}`,

      {

        method: 'PUT',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          status

        })

      }

    )



    return handleResponse(

      response,

      'Failed to update publishing post.'

    )

  },





  deletePublishingPost: async (

    postId

  ) => {



    if (!postId) {

      throw new Error(

        'Publishing post ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/publishing/${encodeURIComponent(postId)}`,

      {

        method: 'DELETE'

      }

    )



    return handleResponse(

      response,

      'Failed to delete publishing post.'

    )

  },





  // ==========================================================

  // YOUTUBE OAUTH CONNECTION

  // ==========================================================



  getYouTubeStatus: async (

    userId = 'demo_user'

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/status?user_id=${encodeURIComponent(userId)}`

    )



    return handleResponse(

      response,

      'Failed to get YouTube connection status.'

    )

  },





  connectYouTube: async (

    userId = 'demo_user'

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/connect?user_id=${encodeURIComponent(userId)}`

    )



    return handleResponse(

      response,

      'Failed to initialize YouTube connection.'

    )

  },





  disconnectYouTube: async (

    userId = 'demo_user'

  ) => {



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/disconnect?user_id=${encodeURIComponent(userId)}`,

      {

        method: 'POST'

      }

    )



    return handleResponse(

      response,

      'Failed to disconnect YouTube.'

    )

  },





  isYouTubeConnected: async (

    userId = 'demo_user'

  ) => {



    const result =

      await api.getYouTubeStatus(

        userId

      )



    return Boolean(

      result?.connected === true

    )

  },





  // ==========================================================

  // YOUTUBE — PUBLISH NOW

  // ==========================================================

  //

  // This performs an ACTUAL YouTube upload.

  //

  // It does NOT merely create a local FrameCraft

  // publishing record.

  //

  // Backend:

  //

  // POST /platforms/youtube/publish

  //

  // ==========================================================



  publishToYouTube: async ({

    project_id,

    video_id = null,

    title,

    description = '',

    tags = [],

    category_id = '22',

    user_id = 'demo_user'

  }) => {



    if (!project_id) {

      throw new Error(

        'Project ID is required for YouTube publishing.'

      )

    }



    if (!title?.trim()) {

      throw new Error(

        'YouTube video title is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/publish`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          user_id,

          project_id,

          video_id,

          title: title.trim(),

          description,

          tags: Array.isArray(tags)

            ? tags

            : [],

          category_id

        })

      }

    )



    return handleResponse(

      response,

      'Failed to publish video to YouTube.'

    )

  },





  // ==========================================================

  // YOUTUBE — SCHEDULE

  // ==========================================================



  scheduleYouTubeVideo: async ({

    project_id,

    video_id = null,

    title,

    description = '',

    tags = [],

    category_id = '22',

    scheduled_at,

    user_id = 'demo_user'

  }) => {



    if (!project_id) {

      throw new Error(

        'Project ID is required for YouTube scheduling.'

      )

    }



    if (!title?.trim()) {

      throw new Error(

        'YouTube video title is required.'

      )

    }



    if (!scheduled_at) {

      throw new Error(

        'Scheduled date and time are required.'

      )

    }



    const scheduledDate =

      new Date(scheduled_at)



    if (

      Number.isNaN(

        scheduledDate.getTime()

      )

    ) {

      throw new Error(

        'Invalid scheduled date and time.'

      )

    }



    if (

      scheduledDate.getTime() <=

      Date.now()

    ) {

      throw new Error(

        'Scheduled time must be in the future.'

      )

    }



    const utcScheduledAt =

      scheduledDate.toISOString()



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/schedule`,

      {

        method: 'POST',



        headers: {

          'Content-Type':

            'application/json'

        },



        body: JSON.stringify({

          user_id,

          project_id,

          video_id,

          title: title.trim(),

          description,

          tags: Array.isArray(tags)

            ? tags

            : [],

          category_id,

          scheduled_at:

            utcScheduledAt

        })

      }

    )



    return handleResponse(

      response,

      'Failed to schedule video on YouTube.'

    )

  },





  // ==========================================================

  // YOUTUBE — VIDEO STATUS

  // ==========================================================



  getYouTubeVideoStatus: async (

    videoId,

    userId = 'demo_user'

  ) => {



    if (!videoId) {

      throw new Error(

        'YouTube video ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/video/${encodeURIComponent(videoId)}/status?user_id=${encodeURIComponent(userId)}`

    )



    return handleResponse(

      response,

      'Failed to get YouTube video status.'

    )

  },





  // ==========================================================

  // YOUTUBE — OPTIONAL DELETE

  // ==========================================================



  deleteYouTubeVideo: async (

    videoId,

    userId = 'demo_user'

  ) => {



    if (!videoId) {

      throw new Error(

        'YouTube video ID is required.'

      )

    }



    const response = await fetch(

      `${API_BASE_URL}/platforms/youtube/video/${encodeURIComponent(videoId)}?user_id=${encodeURIComponent(userId)}`,

      {

        method: 'DELETE'

      }

    )



    return handleResponse(

      response,

      'Failed to delete YouTube video.'

    )

  },


  // ==========================================================
  // MLOPS
  // ==========================================================

  getMLOpsStatus: async () => {

    const response = await fetch(

      `${API_BASE_URL}/mlops/status`

    )



    return handleResponse(

      response,

      'Failed to load MLOps status.'

    )

  },



  getMLOpsSuggestions: async () => {

    const response = await fetch(

      `${API_BASE_URL}/mlops/suggestions`

    )



    return handleResponse(

      response,

      'Failed to load MLOps suggestions.'

    )

  },



  snapshotMLOps: async () => {

    const response = await fetch(

      `${API_BASE_URL}/mlops/snapshot`,

      {

        method: 'POST'

      }

    )



    return handleResponse(

      response,

      'Failed to collect MLOps snapshot.'

    )

  },



  retrainMLOpsModel: async (

    reason = 'manual'

  ) => {

    const response = await fetch(

      `${API_BASE_URL}/mlops/retrain`,

      {

        method: 'POST',

        headers: {

          'Content-Type': 'application/json'

        },

        body: JSON.stringify({

          reason

        })

      }

    )



    return handleResponse(

      response,

      'Failed to retrain MLOps model.'

    )

  },

}