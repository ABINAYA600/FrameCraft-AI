import { useEffect, useMemo, useState } from 'react'



import { motion } from 'framer-motion'



import {



  FiCalendar,



  FiCheck,



  FiClock,



  FiExternalLink,



  FiPlay,



  FiRefreshCw,



  FiTrash2,



  FiUploadCloud,



  FiYoutube,



  FiAlertCircle,



  FiMessageCircle



} from 'react-icons/fi'







import Button from '../../components/Button'



import Card from '../../components/Card'



import YouTubeConnection from '../../components/YouTubeConnection'



import { api } from '../../services/api'











const USER_ID = 'demo_user'











// ============================================================



// HELPERS



// ============================================================







const getProjectId = (project) => {



  return (



    project?.id ||



    project?._id ||



    ''



  )



}











const getProjectName = (project) => {



  return (



    project?.name ||



    project?.title ||



    'Untitled Project'



  )



}











const getGeneratedVideos = (project) => {



  if (!project) {



    return []



  }







  const candidates = [



    ...(Array.isArray(project.generated)



      ? project.generated



      : []),







    ...(Array.isArray(project.generated_videos)



      ? project.generated_videos



      : []),







    ...(Array.isArray(project.generatedVideos)



      ? project.generatedVideos



      : [])



  ]







  const seen = new Set()







  return candidates.filter((video) => {



    if (!video) {



      return false



    }







    const path =



      video.path ||



      video.file_path ||



      video.file ||



      video.url ||



      ''







    const filename =



      video.filename ||



      video.name ||



      video.file_name ||



      ''







    const value =



      `${path} ${filename}`.toLowerCase()







    const isMp4 =



      value.includes('.mp4')







    if (!isMp4) {



      return false



    }







    const id =



      video.id ||



      video.video_id ||



      video.filename ||



      video.name ||



      path







    if (seen.has(id)) {



      return false



    }







    seen.add(id)







    return true



  })



}











const getVideoId = (video) => {



  return (



    video?.id ||



    video?.video_id ||



    video?.filename ||



    video?.name ||



    ''



  )



}











const getVideoName = (video) => {



  return (



    video?.name ||



    video?.filename ||



    video?.file_name ||



    'Generated Video'



  )



}











const formatDate = (value) => {



  if (!value) {



    return '—'



  }







  try {



    return new Date(value).toLocaleString()



  } catch {



    return value



  }



}











// ============================================================



// PUBLISHING PAGE



// ============================================================







const Publishing = () => {







  // ----------------------------------------------------------



  // DATA



  // ----------------------------------------------------------







  const [posts, setPosts] = useState([])



  const [projects, setProjects] = useState([])







  const [youtubeConnected, setYoutubeConnected] =



    useState(false)







  // ----------------------------------------------------------



  // UI



  // ----------------------------------------------------------







  const [showForm, setShowForm] =



    useState(false)







  const [loading, setLoading] =



    useState(true)







  const [publishing, setPublishing] =



    useState(false)







  const [scheduling, setScheduling] =



    useState(false)







  const [deletingId, setDeletingId] =



    useState(null)







  const [error, setError] =



    useState('')







  const [success, setSuccess] =



    useState('')



  const [commentAnalysis, setCommentAnalysis] =



    useState(null)



  const [analyzingComments, setAnalyzingComments] =



    useState(false)











  // ----------------------------------------------------------



  // FORM



  // ----------------------------------------------------------







  const [form, setForm] = useState({



    project_id: '',



    video_id: '',



    title: '',



    description: '',



    tags: '',



    scheduled_at: ''



  })











  // ==========================================================



  // SELECTED PROJECT



  // ==========================================================







  const selectedProject = useMemo(() => {







    return projects.find(



      (project) =>



        getProjectId(project) ===



        form.project_id



    )







  }, [



    projects,



    form.project_id



  ])











  // ==========================================================



  // GENERATED VIDEOS



  // ==========================================================







  const generatedVideos = useMemo(() => {







    return getGeneratedVideos(



      selectedProject



    )







  }, [



    selectedProject



  ])











  // ==========================================================



  // SELECTED VIDEO



  // ==========================================================







  const selectedVideo = useMemo(() => {







    return generatedVideos.find(



      (video) =>



        getVideoId(video) ===



        form.video_id



    )







  }, [



    generatedVideos,



    form.video_id



  ])











  // ==========================================================



  // COUNTS



  // ==========================================================







  const scheduledPosts =



    posts.filter(



      (post) =>



        post.status === 'Scheduled'



    )







  const publishedPosts =



    posts.filter(



      (post) =>



        post.status === 'Published'



    )











  // ==========================================================



  // LOAD DATA



  // ==========================================================







  const load = async () => {







    try {







      setLoading(true)



      setError('')







      const [



        postData,



        projectData,



        youtubeData



      ] = await Promise.all([



        api.getPublishingPosts(),



        api.getBackendProjects(),



        api.getYouTubeStatus(USER_ID)



      ])







      const loadedPosts =



        Array.isArray(postData)



          ? postData



          : (



              postData?.posts ||



              []



            )







      const loadedProjects =



        Array.isArray(projectData)



          ? projectData



          : (



              projectData?.projects ||



              []



            )







      setPosts(



        loadedPosts



      )







      setProjects(



        loadedProjects



      )







      setYoutubeConnected(



        youtubeData?.connected === true



      )







    } catch (err) {







      console.error(



        'Publishing load failed:',



        err



      )







      setError(



        err?.message ||



        'Failed to load publishing data.'



      )







    } finally {







      setLoading(false)







    }



  }











  useEffect(() => {

    load()



    const intervalId = setInterval(() => {

      load()

    }, 5000)



    return () => clearInterval(intervalId)

  }, [])











  // ==========================================================



  // HANDLE PROJECT CHANGE



  // ==========================================================







  const handleProjectChange = (



    projectId



  ) => {







    const project =



      projects.find(



        (item) =>



          getProjectId(item) ===



          projectId



      )







    const videos =



      getGeneratedVideos(



        project



      )







    const firstVideo =



      videos.length > 0



        ? getVideoId(videos[0])



        : ''







    setForm((previous) => ({



      ...previous,







      project_id:



        projectId,







      video_id:



        firstVideo



    }))







    setError('')



    setSuccess('')



  }











  // ==========================================================



  // HANDLE VIDEO CHANGE



  // ==========================================================







  const handleVideoChange = (



    videoId



  ) => {







    setForm((previous) => ({



      ...previous,



      video_id: videoId



    }))







    setError('')



    setSuccess('')



  }











  // ==========================================================



  // FORM RESET



  // ==========================================================







  const resetForm = () => {







    setForm({



      project_id: '',



      video_id: '',



      title: '',



      description: '',



      tags: '',



      scheduled_at: ''



    })







    setError('')



    setSuccess('')



  }











  // ==========================================================



  // PARSE TAGS



  // ==========================================================







  const getTags = () => {







    return form.tags



      .split(',')



      .map(



        (tag) =>



          tag.trim()



      )



      .filter(Boolean)



  }











  // ==========================================================



  // PUBLISH NOW



  // ==========================================================







  const handlePublishNow = async () => {







    setError('')



    setSuccess('')







    if (!youtubeConnected) {







      setError(



        'Please connect your YouTube account first.'



      )







      return



    }







    if (!form.project_id) {







      setError(



        'Please select a project.'



      )







      return



    }







    if (!form.video_id) {







      setError(



        'Please select a generated video.'



      )







      return



    }







    if (!form.title.trim()) {







      setError(



        'Please enter a YouTube video title.'



      )







      return



    }







    try {







      setPublishing(true)







      const result =



        await api.publishToYouTube({



          user_id:



            USER_ID,







          project_id:



            form.project_id,







          video_id:



            form.video_id,







          title:



            form.title.trim(),







          description:



            form.description.trim(),







          tags:



            getTags(),







          category_id:



            '22'



        })











      const youtubeVideo =



        result?.youtube







      const videoUrl =



        youtubeVideo?.video_url











      setSuccess(



        videoUrl



          ? `Video published successfully to YouTube.`



          : `Video uploaded successfully to YouTube.`



      )











      if (videoUrl) {







        setSuccess(



          `Video published successfully. YouTube video: ${videoUrl}`



        )







      }











      await load()







      setShowForm(false)







      resetForm()







    } catch (err) {







      console.error(



        'YouTube publish failed:',



        err



      )







      setError(



        err?.message ||



        'Failed to publish video to YouTube.'



      )







    } finally {







      setPublishing(false)







    }



  }











  // ==========================================================



  // SCHEDULE ON YOUTUBE



  // ==========================================================







  const handleSchedule = async () => {







    setError('')



    setSuccess('')







    if (!youtubeConnected) {







      setError(



        'Please connect your YouTube account first.'



      )







      return



    }







    if (!form.project_id) {







      setError(



        'Please select a project.'



      )







      return



    }







    if (!form.video_id) {







      setError(



        'Please select a generated video.'



      )







      return



    }







    if (!form.title.trim()) {







      setError(



        'Please enter a YouTube video title.'



      )







      return



    }







    if (!form.scheduled_at) {







      setError(



        'Please select a future date and time.'



      )







      return



    }











    const selectedDate =



      new Date(



        form.scheduled_at



      )











    if (



      Number.isNaN(



        selectedDate.getTime()



      )



    ) {







      setError(



        'The selected date and time is invalid.'



      )







      return



    }











    if (



      selectedDate.getTime() <=



      Date.now()



    ) {







      setError(



        'Scheduled time must be in the future.'



      )







      return



    }











    try {







      setScheduling(true)







      const result =



        await api.scheduleYouTubeVideo({



          user_id:



            USER_ID,







          project_id:



            form.project_id,







          video_id:



            form.video_id,







          title:



            form.title.trim(),







          description:



            form.description.trim(),







          tags:



            getTags(),







          category_id:



            '22',







          scheduled_at:



            selectedDate.toISOString()



        })











      const youtubeVideo =



        result?.youtube







      const scheduledTime =



        youtubeVideo?.publish_at ||



        form.scheduled_at











      setSuccess(



        `Video uploaded to YouTube and scheduled for ${formatDate(scheduledTime)}.`



      )











      await load()







      setShowForm(false)







      resetForm()







    } catch (err) {







      console.error(



        'YouTube scheduling failed:',



        err



      )







      setError(



        err?.message ||



        'Failed to schedule video on YouTube.'



      )







    } finally {







      setScheduling(false)







    }



  }











    // ============================================================

  // ANALYZE YOUTUBE COMMENTS

    // ============================================================

  // COMMENT ANALYSIS

  // ============================================================



  const renderCommentAnalysis = () => {

    if (!commentAnalysis) {

      return null

    }



    return (

      <Card>

        <div className="flex items-center justify-between mb-6">

          <div>

            <h2 className="text-xl font-bold text-gray-900 dark:text-white">

              YouTube Comment Analysis

            </h2>

            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">

              Sentiment analysis for the selected published video.

            </p>

          </div>



          <button

            type="button"

            onClick={() => setCommentAnalysis(null)}

            className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-white"

          >

            Close

          </button>

        </div>



        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">

          <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50">

            <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>

            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">

              {commentAnalysis.total}

            </p>

          </div>



          <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20">

            <p className="text-sm text-green-700 dark:text-green-300">Positive</p>

            <p className="text-2xl font-bold text-green-700 dark:text-green-300 mt-1">

              {commentAnalysis.positive}

            </p>

          </div>



          <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20">

            <p className="text-sm text-red-700 dark:text-red-300">Negative</p>

            <p className="text-2xl font-bold text-red-700 dark:text-red-300 mt-1">

              {commentAnalysis.negative}

            </p>

          </div>



          <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50">

            <p className="text-sm text-gray-500 dark:text-gray-400">Neutral</p>

            <p className="text-2xl font-bold text-gray-700 dark:text-gray-300 mt-1">

              {commentAnalysis.neutral}

            </p>

          </div>

        </div>



        {Array.isArray(commentAnalysis.comments) &&

          commentAnalysis.comments.length > 0 && (

            <div className="mt-6 space-y-3">

              {commentAnalysis.comments.map((comment, index) => {

                const sentiment = String(

                  comment?.sentiment ||

                  comment?.label ||

                  comment?.category ||

                  'unknown'

                ).toLowerCase()



                const text =

                  comment?.text ||

                  comment?.comment ||

                  comment?.content ||

                  ''



                const author =

                  comment?.author ||

                  comment?.author_name ||

                  'YouTube user'



                return (

                  <div

                    key={

                      comment?.id ||

                      comment?.comment_id ||

                      index

                    }

                    className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600"

                  >

                    <div className="flex items-center justify-between gap-3">

                      <p className="font-medium text-gray-900 dark:text-white">

                        {author}

                      </p>



                      <span className="px-2 py-1 rounded-full text-xs font-medium capitalize bg-white dark:bg-gray-800">

                        {sentiment}

                      </span>

                    </div>



                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">

                      {text}

                    </p>

                  </div>

                )

              })}

            </div>

          )}

      </Card>

    )

  }





// ============================================================



  const handleAnalyzeComments = async (post) => {

    const youtubeVideoId = post?.youtube_video_id



    if (!youtubeVideoId) {

      setError('No YouTube video ID is available for this published video.')

      return

    }



    try {

      setAnalyzingComments(true)

      setError('')

      setSuccess('')

      setCommentAnalysis(null)



      const response = await fetch(

        `http://127.0.0.1:8000/platforms/youtube/video/${youtubeVideoId}/comments?user_id=${encodeURIComponent(USER_ID)}&max_results=100`

      )



      const data = await response.json()



      if (!response.ok) {

        throw new Error(

          data?.detail ||

          data?.message ||

          'Failed to fetch YouTube comments.'

        )

      }



      const comments = Array.isArray(data)

        ? data

        : (data?.comments || [])



      if (comments.length === 0) {

        setCommentAnalysis({

          videoId: youtubeVideoId,

          total: 0,

          positive: 0,

          negative: 0,

          neutral: 0,

          comments: []

        })

        return

      }



      const analysisResponse = await fetch(

        'http://127.0.0.1:8000/comments/analyze-batch',

        {

          method: 'POST',

          headers: {

            'Content-Type': 'application/json'

          },

          body: JSON.stringify({

            comments,

            project_id: post?.project_id || '',

            video_id: youtubeVideoId

          })

        }

      )



      const analysisData = await analysisResponse.json()



      if (!analysisResponse.ok) {

        throw new Error(

          analysisData?.detail ||

          analysisData?.message ||

          'Failed to analyze comments.'

        )

      }



      const analyzedComments =

        Array.isArray(analysisData)

          ? analysisData

          : (

              analysisData?.comments ||

              analysisData?.results ||

              []

            )



      const getSentiment = (comment) =>

        String(

          comment?.sentiment ||

          comment?.label ||

          comment?.category ||

          ''

        ).toLowerCase()



      setCommentAnalysis({

        videoId: youtubeVideoId,

        total: analyzedComments.length || comments.length,

        positive: analyzedComments.filter((comment) =>

          ['positive', 'pos'].includes(getSentiment(comment))

        ).length,

        negative: analyzedComments.filter((comment) =>

          ['negative', 'neg'].includes(getSentiment(comment))

        ).length,

        neutral: analyzedComments.filter((comment) =>

          ['neutral', 'neu'].includes(getSentiment(comment))

        ).length,

        comments: analyzedComments.length

          ? analyzedComments

          : comments

      })

    } catch (err) {

      console.error('Comment analysis failed:', err)



      setError(

        err?.message ||

        'Failed to analyze YouTube comments.'

      )

    } finally {

      setAnalyzingComments(false)

    }

  }





// ==========================================================



  // DELETE FRAMECRAFT RECORD



  // ==========================================================







  const handleDelete = async (



    postId



  ) => {







    const confirmed =



      window.confirm(



        'Delete this FrameCraft publishing record? This does not delete the YouTube video.'



      )







    if (!confirmed) {



      return



    }







    try {







      setDeletingId(



        postId



      )







      setError('')







      await api.deletePublishingPost(



        postId



      )







      await load()







    } catch (err) {







      setError(



        err?.message ||



        'Failed to delete publishing record.'



      )







    } finally {







      setDeletingId(null)







    }



  }











  // ==========================================================



  // OPEN YOUTUBE



  // ==========================================================







  const openYouTube = (



    post



  ) => {







    const url =



      post?.youtube_url ||



      (



        post?.youtube_video_id



          ? `https://www.youtube.com/watch?v=${post.youtube_video_id}`



          : ''



      )







    if (!url) {



      return



    }







    window.open(



      url,



      '_blank',



      'noopener,noreferrer'



    )



  }











  // ==========================================================



  // FORM



  // ==========================================================







  const renderPublishingForm = () => {







    if (!showForm) {



      return null



    }











    return (



      <Card>







        <div className="mb-6">







          <div className="flex items-center gap-3">







            <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">







              <FiYoutube



                className="text-red-600"



                size={22}



              />







            </div>







            <div>







              <h2 className="text-xl font-bold text-gray-900 dark:text-white">







                Publish to YouTube







              </h2>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Upload a generated FrameCraft video directly to your YouTube channel.







              </p>







            </div>







          </div>







        </div>











        {!youtubeConnected && (







          <div className="mb-6 p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">







            <div className="flex gap-3">







              <FiAlertCircle



                className="text-yellow-600 mt-1"



                size={20}



              />







              <div>







                <p className="font-medium text-yellow-800 dark:text-yellow-300">







                  YouTube account is not connected.







                </p>







                <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-1">







                  Connect your YouTube account before publishing or scheduling.







                </p>







              </div>







            </div>







          </div>







        )}











        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">







          {/* PROJECT */}







          <div>







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              FrameCraft Project







            </label>







            <select



              value={form.project_id}



              onChange={(event) =>



                handleProjectChange(



                  event.target.value



                )



              }



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"



            >







              <option value="">



                Select project



              </option>







              {projects.map(



                (project) => {







                  const id =



                    getProjectId(



                      project



                    )







                  return (



                    <option



                      key={id}



                      value={id}



                    >



                      {getProjectName(



                        project



                      )}



                    </option>



                  )



                }



              )}







            </select>







          </div>











          {/* GENERATED VIDEO */}







          <div>







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              Generated Video







            </label>







            <select



              value={form.video_id}



              onChange={(event) =>



                handleVideoChange(



                  event.target.value



                )



              }



              disabled={



                !form.project_id ||



                generatedVideos.length === 0



              }



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500"



            >







              <option value="">







                {!form.project_id



                  ? 'Select a project first'



                  : generatedVideos.length === 0



                    ? 'No generated MP4 videos'



                    : 'Select generated video'}







              </option>







              {generatedVideos.map(



                (video) => {







                  const id =



                    getVideoId(



                      video



                    )







                  return (



                    <option



                      key={id}



                      value={id}



                    >



                      {getVideoName(



                        video



                      )}



                    </option>



                  )



                }



              )}







            </select>







          </div>











          {/* TITLE */}







          <div className="lg:col-span-2">







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              YouTube Title







            </label>







            <input



              type="text"



              maxLength={100}



              value={form.title}



              onChange={(event) =>



                setForm({



                  ...form,



                  title:



                    event.target.value



                })



              }



              placeholder="Enter YouTube video title"



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"



            />







            <p className="text-xs text-gray-400 mt-1">







              {form.title.length}/100







            </p>







          </div>











          {/* DESCRIPTION */}







          <div className="lg:col-span-2">







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              Description







            </label>







            <textarea



              rows={5}



              value={form.description}



              onChange={(event) =>



                setForm({



                  ...form,



                  description:



                    event.target.value



                })



              }



              placeholder="Write the YouTube video description..."



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"



            />







          </div>











          {/* TAGS */}







          <div className="lg:col-span-2">







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              Tags







            </label>







            <input



              type="text"



              value={form.tags}



              onChange={(event) =>



                setForm({



                  ...form,



                  tags:



                    event.target.value



                })



              }



              placeholder="AI, technology, FrameCraft, video"



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"



            />







            <p className="text-xs text-gray-400 mt-1">







              Separate tags with commas.







            </p>







          </div>











          {/* SCHEDULE */}







          <div className="lg:col-span-2">







            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">







              YouTube Schedule Time







            </label>







            <input



              type="datetime-local"



              value={form.scheduled_at}



              onChange={(event) =>



                setForm({



                  ...form,



                  scheduled_at:



                    event.target.value



                })



              }



              className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"



            />







            <p className="text-xs text-gray-400 mt-1">







              Leave this empty when using Publish Now. For scheduling, select a future time.







            </p>







          </div>







        </div>











        {/* SELECTED VIDEO */}







        {selectedVideo && (







          <div className="mt-6 p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50">







            <div className="flex items-center gap-3">







              <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">







                <FiPlay



                  className="text-blue-600"



                />







              </div>







              <div>







                <p className="text-sm font-medium text-gray-900 dark:text-white">







                  Selected video







                </p>







                <p className="text-sm text-gray-500 dark:text-gray-400">







                  {getVideoName(



                    selectedVideo



                  )}







                </p>







              </div>







            </div>







          </div>







        )}











        {/* ACTIONS */}







        <div className="flex flex-col sm:flex-row gap-3 mt-6">







          <Button



            type="button"



            onClick={



              handlePublishNow



            }



            disabled={



              publishing ||



              scheduling ||



              !youtubeConnected



            }



          >







            <FiUploadCloud



              className="mr-2"



            />







            {publishing



              ? 'Uploading to YouTube...'



              : 'Publish Now'}







          </Button>











          <Button



            type="button"



            onClick={



              handleSchedule



            }



            disabled={



              publishing ||



              scheduling ||



              !youtubeConnected



            }



          >







            <FiCalendar



              className="mr-2"



            />







            {scheduling



              ? 'Scheduling on YouTube...'



              : 'Schedule on YouTube'}







          </Button>











          <Button



            type="button"



            variant="secondary"



            onClick={() => {



              resetForm()



              setShowForm(false)



            }}



            disabled={



              publishing ||



              scheduling



            }



          >







            Cancel







          </Button>







        </div>







      </Card>



    )



  }











  // ==========================================================



  // SCHEDULED POSTS



  // ==========================================================







  const renderScheduledPosts = () => {







    return (



      <Card>







        <div className="flex items-center justify-between mb-6">







          <div className="flex items-center gap-3">







            <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">







              <FiClock



                className="text-blue-600"



              />







            </div>







            <div>







              <h2 className="text-xl font-bold text-gray-900 dark:text-white">







                Scheduled on YouTube







              </h2>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Videos uploaded to YouTube with a future publish time.







              </p>







            </div>







          </div>







          <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-medium">







            {scheduledPosts.length}







          </span>







        </div>











        {scheduledPosts.length === 0 ? (







          <div className="py-10 text-center text-gray-500">







            <FiClock



              size={40}



              className="mx-auto mb-3 opacity-40"



            />







            <p>



              No YouTube videos are currently scheduled.



            </p>







          </div>







        ) : (







          <div className="space-y-4">







            {scheduledPosts.map(



              (post, index) => (







                <motion.div



                  key={



                    post.id ||



                    index



                  }



                  initial={{



                    opacity: 0,



                    y: 10



                  }}



                  animate={{



                    opacity: 1,



                    y: 0



                  }}



                  className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600"



                >







                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">







                    <div className="min-w-0">







                      <div className="flex items-center gap-2">







                        <FiYoutube



                          className="text-red-600 flex-shrink-0"



                        />







                        <p className="font-semibold text-gray-900 dark:text-white truncate">







                          {post.title ||



                            'Untitled YouTube Video'}







                        </p>







                      </div>







                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">







                        Scheduled:{' '}







                        {formatDate(



                          post.scheduled_at



                        )}







                      </p>







                      {post.project_name && (







                        <p className="text-xs text-gray-400 mt-1">







                          Project:{' '}







                          {post.project_name}







                        </p>







                      )}







                      {post.youtube_video_id && (







                        <p className="text-xs text-gray-400 mt-1">







                          YouTube ID:{' '}







                          {post.youtube_video_id}







                        </p>







                      )}







                    </div>











                    <div className="flex items-center gap-2 flex-shrink-0">







                      {(post.youtube_url ||



                        post.youtube_video_id) && (







                        <button



                          type="button"



                          onClick={() =>



                            openYouTube(



                              post



                            )



                          }



                          className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-blue-600 hover:bg-blue-50"



                          title="Open YouTube video"



                        >







                          <FiExternalLink />







                        </button>







                      )}











                      <button



                        type="button"



                        onClick={() =>



                          handleDelete(



                            post.id



                          )



                        }



                        disabled={



                          deletingId ===



                          post.id



                        }



                        className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-red-500 hover:bg-red-50 disabled:opacity-50"



                        title="Delete FrameCraft publishing record"



                      >







                        <FiTrash2 />







                      </button>







                    </div>







                  </div>







                </motion.div>







              )



            )}







          </div>







        )}







      </Card>



    )



  }











  // ==========================================================



  // PUBLISHED POSTS



  // ==========================================================







  const renderPublishedPosts = () => {







    return (



      <Card>







        <div className="flex items-center justify-between mb-6">







          <div className="flex items-center gap-3">







            <div className="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">







              <FiCheck



                className="text-green-600"



              />







            </div>







            <div>







              <h2 className="text-xl font-bold text-gray-900 dark:text-white">







                Published on YouTube







              </h2>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Videos successfully uploaded through FrameCraft.







              </p>







            </div>







          </div>







          <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm font-medium">







            {publishedPosts.length}







          </span>







        </div>











        {publishedPosts.length === 0 ? (







          <div className="py-10 text-center text-gray-500">







            <FiCheck



              size={40}



              className="mx-auto mb-3 opacity-40"



            />







            <p>



              No YouTube videos published yet.



            </p>







          </div>







        ) : (







          <div className="space-y-4">







            {publishedPosts.map(



              (post, index) => (







                <motion.div



                  key={



                    post.id ||



                    index



                  }



                  initial={{



                    opacity: 0,



                    y: 10



                  }}



                  animate={{



                    opacity: 1,



                    y: 0



                  }}



                  className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-100 dark:border-gray-600"



                >







                  <div className="flex items-start justify-between gap-4">







                    <div className="min-w-0">







                      <div className="flex items-center gap-2">







                        <FiYoutube



                          className="text-red-600 flex-shrink-0"



                        />







                        <p className="font-semibold text-gray-900 dark:text-white truncate">







                          {post.title ||



                            'Untitled YouTube Video'}







                        </p>







                      </div>







                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">







                        Published:{' '}







                        {formatDate(



                          post.published_at ||



                          post.created_at



                        )}







                      </p>







                      {post.youtube_video_id && (







                        <p className="text-xs text-gray-400 mt-1">







                          YouTube ID:{' '}







                          {post.youtube_video_id}







                        </p>







                      )}







                    </div>                    {post.youtube_video_id && (



                      <button

                        type="button"

                        onClick={() =>

                          handleAnalyzeComments(post)

                        }

                        disabled={analyzingComments}

                        className="px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-purple-600 hover:bg-purple-50 disabled:opacity-50 flex items-center gap-2 flex-shrink-0"

                        title="Analyze YouTube comments"

                      >

                        <FiMessageCircle />



                        {analyzingComments

                          ? 'Analyzing...'

                          : 'Analyze Comments'}

                      </button>



                    )}













                    {(post.youtube_url ||



                      post.youtube_video_id) && (







                      <button



                        type="button"



                        onClick={() =>



                          openYouTube(



                            post



                          )



                        }



                        className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-blue-600 hover:bg-blue-50 flex-shrink-0"



                        title="Open YouTube video"



                      >







                        <FiExternalLink />







                      </button>







                    )}







                  </div>







                </motion.div>







              )



            )}







          </div>







        )}







      </Card>



    )



  }











  // ==========================================================



  // MAIN UI



  // ==========================================================







  return (







    <div className="space-y-8">







      {/* ==================================================== */}



      {/* HEADER */}



      {/* ==================================================== */}







      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">







        <div>







          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">







            YouTube Publishing







          </h1>







          <p className="text-gray-600 dark:text-gray-300">







            Upload and schedule your generated FrameCraft videos directly on YouTube.







          </p>







        </div>











        <div className="flex items-center gap-3">







          <Button



            type="button"



            variant="secondary"



            onClick={load}



            disabled={loading}



          >







            <FiRefreshCw



              className={`mr-2 ${



                loading



                  ? 'animate-spin'



                  : ''



              }`}



            />







            Refresh







          </Button>











          <Button



            type="button"



            onClick={() => {







              setError('')



              setSuccess('')







              setShowForm(



                !showForm



              )







            }}



          >







            <FiUploadCloud



              className="mr-2"



            />







            {showForm



              ? 'Close'



              : 'Publish Video'}







          </Button>







        </div>







      </div>











      {/* ==================================================== */}



      {/* ALERTS */}



      {/* ==================================================== */}







      {error && (







        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">







          <div className="flex gap-3">







            <FiAlertCircle



              className="text-red-600 mt-1 flex-shrink-0"



            />







            <p className="text-red-700 dark:text-red-300">







              {error}







            </p>







          </div>







        </div>







      )}











      {success && (







        <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">







          <div className="flex gap-3">







            <FiCheck



              className="text-green-600 mt-1 flex-shrink-0"



            />







            <p className="text-green-700 dark:text-green-300 break-words">







              {success}







            </p>







          </div>







        </div>







      )}











      {/* ==================================================== */}



      {/* YOUTUBE CONNECTION */}



      {/* ==================================================== */}







      <YouTubeConnection />











      {/* ==================================================== */}



      {/* STATS */}



      {/* ==================================================== */}







      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">







        <Card>







          <div className="flex items-center justify-between">







            <div>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Total Publishing Records







              </p>







              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">







                {posts.length}







              </p>







            </div>







            <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">







              <FiCalendar



                className="text-blue-600"



                size={24}



              />







            </div>







          </div>







        </Card>











        <Card>







          <div className="flex items-center justify-between">







            <div>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Scheduled on YouTube







              </p>







              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">







                {scheduledPosts.length}







              </p>







            </div>







            <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">







              <FiClock



                className="text-purple-600"



                size={24}



              />







            </div>







          </div>







        </Card>











        <Card>







          <div className="flex items-center justify-between">







            <div>







              <p className="text-sm text-gray-500 dark:text-gray-400">







                Published on YouTube







              </p>







              <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">







                {publishedPosts.length}







              </p>







            </div>







            <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">







              <FiCheck



                className="text-green-600"



                size={24}



              />







            </div>







          </div>







        </Card>







      </div>











      {/* ==================================================== */}



      {/* FORM */}



      {/* ==================================================== */}







      {renderPublishingForm()}











      {/* ==================================================== */}



      {/* SCHEDULED + PUBLISHED */}



      {/* ==================================================== */}







      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">







        {renderScheduledPosts()}







        {renderPublishedPosts()}







      </div>







      {renderCommentAnalysis()}











      {/* ==================================================== */}



      {/* WORKFLOW INFORMATION */}



      {/* ==================================================== */}







      <Card>







        <div className="flex items-start gap-4">







          <div className="w-12 h-12 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">







            <FiYoutube



              className="text-red-600"



              size={24}



            />







          </div>







          <div>







            <h2 className="text-xl font-bold text-gray-900 dark:text-white">







              YouTube Publishing Workflow







            </h2>







            <div className="mt-4 space-y-3 text-sm text-gray-600 dark:text-gray-300">







              <p>







                <strong>1.</strong>{' '}



                Generate a video in FrameCraft AI.







              </p>







              <p>







                <strong>2.</strong>{' '}



                Select the generated MP4 from this page.







              </p>







              <p>







                <strong>3.</strong>{' '}



                Enter the YouTube title, description and tags.







              </p>







              <p>







                <strong>4.</strong>{' '}



                Choose <strong>Publish Now</strong> for immediate publishing.







              </p>







              <p>







                <strong>5.</strong>{' '}



                Choose <strong>Schedule on YouTube</strong> to upload the video privately with a future YouTube publication time.







              </p>







              <p>







                <strong>6.</strong>{' '}



                YouTube handles the scheduled publication after the upload.







              </p>







            </div>







          </div>







        </div>







      </Card>







    </div>







  )



}











export default Publishing