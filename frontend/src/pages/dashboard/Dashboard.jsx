import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery } from 'react-query'
import { FiFolder, FiVideo, FiCalendar, FiUsers, FiPlus, FiTrendingUp, FiMessageCircle } from 'react-icons/fi'
import { api } from '../../services/api'
import Button from '../../components/Button'
import Card from '../../components/Card'

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboardStats', api.getDashboardStats, { refetchInterval: 5000 })
  const { data: projects, isLoading: projectsLoading } = useQuery('projects', api.getProjects, { refetchInterval: 5000 })
  const { data: activities, isLoading: activitiesLoading } = useQuery('activities', api.getActivityTimeline, { refetchInterval: 5000 })

  const quickActions = [
    { title: 'Create New Project', icon: FiFolder, color: 'from-blue-500 to-blue-600', path: '/dashboard/projects' },
    { title: 'Generate Video', icon: FiVideo, color: 'from-purple-500 to-purple-600', path: '/dashboard/ai-video-studio' },
    { title: 'Upload Media', icon: FiFolder, color: 'from-green-500 to-green-600', path: '/dashboard/ai-video-studio' },
    { title: 'Analyze Feedback', icon: FiUsers, color: 'from-orange-500 to-orange-600', path: '/dashboard/analytics' },
  ]

  const statCards = [
    { label: 'Total Projects', value: stats?.totalProjects ?? 0, icon: FiFolder, color: 'from-blue-500 to-purple-600', detail: 'Live backend count' },
    { label: 'Videos Generated', value: stats?.videosGenerated ?? 0, icon: FiVideo, color: 'from-purple-500 to-pink-600', detail: 'Generated files' },
    { label: 'Scheduled Posts', value: stats?.scheduledPosts ?? 0, icon: FiCalendar, color: 'from-green-500 to-teal-600', detail: 'Backend schedule' },
    { label: 'Audience Engagement', value: `${stats?.audienceEngagement ?? 0}%`, icon: FiUsers, color: 'from-orange-500 to-red-600', detail: `${stats?.commentsAnalyzed ?? 0} comments analyzed` },
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between"><div><h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1><p className="text-gray-600 dark:text-gray-300">Live FrameCraft project, video, publishing and audience data.</p></div><Link to="/dashboard/projects"><Button className="mt-4 sm:mt-0"><FiPlus className="mr-2" />New Project</Button></Link></div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">{statCards.map((stat,index)=>{const Icon=stat.icon;return <motion.div key={stat.label} initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} transition={{delay:index*.08}}><Card><div className="flex items-center justify-between"><div><p className="text-gray-500 dark:text-gray-400 text-sm">{stat.label}</p><p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">{statsLoading?'...':stat.value}</p><p className="text-gray-500 dark:text-gray-400 text-xs mt-2 flex items-center"><FiTrendingUp className="mr-1" />{stat.detail}</p></div><div className={`w-14 h-14 bg-gradient-to-br ${stat.color} rounded-2xl flex items-center justify-center`}><Icon size={28} className="text-white"/></div></div></Card></motion.div>})}</div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8"><div className="lg:col-span-2"><Card><div className="flex items-center justify-between mb-6"><h2 className="text-xl font-bold">Recent Projects</h2><Link to="/dashboard/projects" className="text-blue-600 text-sm font-medium">View All</Link></div><div className="space-y-4">{projectsLoading?Array(4).fill(0).map((_,i)=><div key={i} className="h-16 bg-gray-100 dark:bg-gray-700 rounded-xl animate-pulse"/>):projects?.length?projects.map(project=><Link key={project.id} to={`/dashboard/ai-video-studio/${project.id}`} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700"><div className="flex items-center space-x-4"><div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">{project.name?.charAt(0)||'P'}</div><div><p className="font-medium">{project.name}</p><p className="text-sm text-gray-500">{project.date}</p></div></div><span className="px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-700">{project.status}</span></Link>):<p className="text-gray-500">No projects yet.</p>}</div></Card></div><div className="space-y-8"><Card><h2 className="text-xl font-bold mb-6">Quick Actions</h2><div className="grid grid-cols-2 gap-4">{quickActions.map(action=>{const Icon=action.icon;return <Link key={action.title} to={action.path}><motion.div whileHover={{scale:1.04}} className={`p-4 rounded-xl bg-gradient-to-br ${action.color} text-white text-center`}><Icon size={28} className="mx-auto mb-2"/><p className="font-medium text-sm">{action.title}</p></motion.div></Link>})}</div></Card><Card><h2 className="text-xl font-bold mb-6">Recent Activity</h2><div className="space-y-4">{activitiesLoading?<div className="text-gray-400">Loading...</div>:activities?.length?activities.map(activity=><div key={activity.id} className="flex space-x-3"><div className="w-2 h-2 bg-blue-500 rounded-full mt-2"/><div><p className="text-sm"><span className="font-medium">{activity.action}</span><span className="text-gray-500"> - {activity.project}</span></p><p className="text-xs text-gray-400">{activity.time?new Date(activity.time).toLocaleString():''}</p></div></div>):<p className="text-gray-500">No activity yet.</p>}</div></Card></div></div>
      <Card><div className="flex items-center gap-3"><FiMessageCircle className="text-blue-600"/><div><h2 className="font-bold">Comment Intelligence</h2><p className="text-sm text-gray-500">{stats?.commentsAnalyzed ?? 0} live comments analyzed · {stats?.pendingReplies ?? 0} waiting for creator approval.</p></div><Link to="/dashboard/analytics" className="ml-auto text-blue-600 text-sm">Open Analytics</Link></div></Card>
    </div>
  )
}
export default Dashboard
