import { useEffect, useMemo, useState } from 'react'



import { motion } from 'framer-motion'



import { FiBarChart2, FiUsers, FiMessageCircle, FiThumbsUp, FiAlertCircle, FiSend, FiRefreshCw, FiVideo } from 'react-icons/fi'



import Card from '../../components/Card'



import Button from '../../components/Button'



import { api } from '../../services/api'







const Analytics = () => {



  const [projects, setProjects] = useState([])



  const [projectId, setProjectId] = useState('')



  const [videoId, setVideoId] = useState('')



  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))



  const [summary, setSummary] = useState(null)



  const [comments, setComments] = useState([])



  const [pending, setPending] = useState([])



  const [comment, setComment] = useState('')



  const [loading, setLoading] = useState(true)



  const [analyzing, setAnalyzing] = useState(false)



  const [videoAnalyzing, setVideoAnalyzing] = useState(false)



  const [error, setError] = useState('')
  const [isLive, setIsLive] = useState(true)







  const selectedProject = useMemo(



    () => projects.find((project) => project.id === projectId),



    [projects, projectId]



  )







  const selectedVideos = selectedProject?.videos || []







  const loadProjects = async () => {



    const data = await api.getBackendProjects()



    const list = Array.isArray(data) ? data : (data?.projects || [])



    setProjects(list)



    return list



  }







  const loadAnalytics = async (silent = false) => {
    if (!silent) setLoading(true)

    try {
      const [summaryData, commentsData, pendingData] = await Promise.all([
        api.getCommentSummary({ projectId, videoId, date }),
        api.getLiveComments({ projectId, videoId, date, limit: 100 }),
        api.getPendingReplies(),
      ])

      setSummary(summaryData)
      setComments(commentsData?.comments || [])
      setPending(pendingData?.replies || [])
      setIsLive(true)

      if (!silent) setError('')
    } catch (err) {
      setIsLive(false)
      if (!silent) {
        setError(err.message || 'Failed to load live analytics.')
      }
    } finally {
      if (!silent) setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects().catch((err) => setError(err.message || 'Failed to load projects.'))

    const intervalId = window.setInterval(() => {
      loadProjects().catch(() => {})
    }, 30000)

    return () => window.clearInterval(intervalId)
  }, [])







  useEffect(() => {
    let active = true

    const runLiveAnalytics = async () => {
      if (!active || document.visibilityState !== 'visible') return
      await loadAnalytics(true)
    }

    loadAnalytics(false)

    const intervalId = window.setInterval(runLiveAnalytics, 5000)

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        runLiveAnalytics()
      }
    }

    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      active = false
      window.clearInterval(intervalId)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [projectId, videoId, date])







  const analyze = async () => {



    if (!comment.trim()) return



    setAnalyzing(true)



    setError('')



    try {



      await api.analyzeComment({



        comment: comment.trim(),



        projectId: projectId || null,



        videoId: videoId || null,



        occurredAt: new Date().toISOString(),



      })



      setComment('')



      await loadAnalytics()



    } catch (err) {



      setError(err.message || 'Comment analysis failed.')



    } finally {



      setAnalyzing(false)



    }



  }







  const analyzeVideo = async () => {



    if (!projectId || !videoId) return



    setVideoAnalyzing(true)



    setError('')



    try {



      await api.analyzeProjectVideo(projectId, videoId)



      const list = await loadProjects()



      const refreshed = list.find((project) => project.id === projectId)



      if (refreshed) setProjects(list)



    } catch (err) {



      setError(err.message || 'Video analysis failed.')



    } finally {



      setVideoAnalyzing(false)



    }



  }







  const approve = async (id) => {



    try {



      await api.approveReply(id)



      await loadAnalytics()



    } catch (err) {



      setError(err.message || 'Approval failed.')



    }



  }







  const reject = async (id) => {



    try {



      await api.rejectReply(id)



      await loadAnalytics()



    } catch (err) {



      setError(err.message || 'Rejection failed.')



    }



  }







  const metrics = [



    { label: 'Comments Analyzed', value: summary?.total ?? 0, icon: FiMessageCircle },



    { label: 'Positive Rate', value: `${summary?.positive_rate ?? 0}%`, icon: FiThumbsUp },



    { label: 'Pending Replies', value: summary?.pending ?? 0, icon: FiAlertCircle },



    { label: 'Knowledge Replies', value: summary?.reply_sources?.['knowledge:faq'] ?? 0, icon: FiUsers },



  ]







  return (



    <div className="space-y-8">



      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">



        <div>



          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Analytics</h1>



          <p className="text-gray-600 dark:text-gray-300">Live audience analysis from the selected project, uploaded video and date.</p>



        </div>



        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium ${
            isLive
              ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400'
              : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              isLive ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`} />
            {isLive ? 'Live' : 'Offline'}
          </span>

          <Button
            variant="secondary"
            onClick={() => loadAnalytics(false)}
            disabled={loading}
          >
            <FiRefreshCw className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>


      {error && <div className="p-4 rounded-xl bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">{error}</div>}







      <Card>



        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">



          <div>



            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Project</label>



            <select value={projectId} onChange={(e) => { setProjectId(e.target.value); setVideoId('') }} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600">



              <option value="">All projects</option>



              {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}



            </select>



          </div>



          <div>



            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Uploaded Video</label>



            <select value={videoId} onChange={(e) => setVideoId(e.target.value)} disabled={!projectId} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50">



              <option value="">All videos</option>



              {selectedVideos.map((video) => <option key={video.id} value={video.id}>{video.name}</option>)}



            </select>



          </div>



          <div>



            <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Live Date</label>



            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600" />



          </div>



        </div>







        {projectId && videoId && (



          <div className="mt-4 flex items-center justify-between p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20">



            <div className="flex items-center gap-3">



              <FiVideo className="text-blue-600" />



              <div>



                <p className="font-medium text-gray-900 dark:text-white">{selectedVideos.find(v => v.id === videoId)?.name}</p>



                <p className="text-sm text-gray-500 dark:text-gray-400">Analyze the uploaded video's available metadata and transcript context.</p>



              </div>



            </div>



            <Button onClick={analyzeVideo} loading={videoAnalyzing}>Analyze Video</Button>



          </div>



        )}



      </Card>







      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">



        {metrics.map((metric, index) => {



          const Icon = metric.icon



          return (



            <motion.div key={metric.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.08 }}>



              <Card>



                <div className="flex items-center justify-between">



                  <div>



                    <p className="text-sm text-gray-500 dark:text-gray-400">{metric.label}</p>



                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{loading ? '...' : metric.value}</p>



                  </div>



                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white"><Icon size={24} /></div>



                </div>



              </Card>



            </motion.div>



          )



        })}



      </div>







      <Card>



        <div className="flex items-center gap-3 mb-5"><FiMessageCircle className="text-blue-600" size={22} /><h2 className="text-xl font-bold text-gray-900 dark:text-white">Analyze Live Comment</h2></div>



        <div className="flex flex-col md:flex-row gap-3">



          <input value={comment} onChange={(e) => setComment(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && analyze()} placeholder="Paste a real audience comment to analyze..." className="flex-1 px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600" />



          <Button onClick={analyze} loading={analyzing}><FiSend className="mr-2" /> Analyze Comment</Button>



        </div>



      </Card>







      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">



        <Card>



          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-5">Live Comment Feed</h2>



          <div className="space-y-4 max-h-[520px] overflow-y-auto">



            {comments.length === 0 ? <p className="text-gray-500">No comments analyzed for this filter yet.</p> : comments.map((item) => (



              <div key={item.id} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50">



                <div className="flex justify-between gap-3 mb-2"><span className="text-xs text-gray-400">{new Date(item.occurred_at).toLocaleString()}</span><span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">{item.analysis?.category || 'unknown'}</span></div>



                <p className="text-gray-900 dark:text-white font-medium">{item.comment}</p>



                <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Sentiment: {item.analysis?.sentiment || 'neutral'} · Reply source: {item.reply_source}</p>



                {item.reply && <div className="mt-3 p-3 rounded-lg bg-white dark:bg-gray-800"><span className="font-medium">Reply:</span> {item.reply}</div>}



              </div>



            ))}



          </div>



        </Card>







        <Card>



          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-5">Creator Approval Queue</h2>



          <div className="space-y-4 max-h-[520px] overflow-y-auto">



            {pending.length === 0 ? <p className="text-gray-500">No replies waiting for approval.</p> : pending.map((item) => {



              const id = item.reply_id || item.id



              const analysis = item.analysis || item



              return (



                <div key={id} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50">



                  <p className="font-medium text-gray-900 dark:text-white">{item.comment || analysis.comment || 'Audience comment'}</p>



                  <p className="text-sm text-gray-500 mt-2">{analysis.category || 'unknown'} · {analysis.sentiment || 'neutral'}</p>



                  <div className="flex gap-2 mt-4"><Button onClick={() => approve(id)}>Approve</Button><Button variant="secondary" onClick={() => reject(id)}>Reject</Button></div>



                </div>



              )



            })}



          </div>



        </Card>



      </div>







      <Card>



        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-5">Category Breakdown</h2>



        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">



          {Object.entries(summary?.categories || {}).map(([key, value]) => <div key={key} className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><p className="text-sm text-gray-500">{key}</p><p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p></div>)}



        </div>



      </Card>



    </div>



  )



}







export default Analytics
