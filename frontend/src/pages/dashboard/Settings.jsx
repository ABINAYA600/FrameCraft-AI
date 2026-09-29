import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiBell, FiGlobe, FiKey, FiSave, FiRefreshCw } from 'react-icons/fi'
import { useTheme } from '../../context/ThemeContext'
import Button from '../../components/Button'
import Card from '../../components/Card'
import { api } from '../../services/api'

const Settings = () => {
  const { darkMode, toggleDarkMode } = useTheme()
  const [settings, setSettings] = useState({ auto_reply_enabled: true, confidence_threshold: 0.75, notifications_enabled: true, default_music_mode: 'ai', default_media_source: 'both' })
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getSettings().then((data) => setSettings((prev) => ({ ...prev, ...(data?.settings || {}) }))).catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  const update = (key, value) => setSettings((prev) => ({ ...prev, [key]: value }))

  const save = async () => {
    setSaving(true); setError(''); setSuccess(false)
    try {
      const data = await api.updateSettings(settings)
      setSettings((prev) => ({ ...prev, ...(data?.settings || {}) }))
      setSuccess(true); setTimeout(() => setSuccess(false), 2500)
    } catch (err) { setError(err.message || 'Failed to save settings.') }
    finally { setSaving(false) }
  }

  return (
    <div className="space-y-8">
      <div><h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1><p className="text-gray-600 dark:text-gray-300">These settings directly control the live FrameCraft backend.</p></div>
      {error && <div className="p-4 rounded-xl bg-red-100 text-red-700">{error}</div>}
      {success && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 rounded-xl bg-green-100 text-green-700">Settings saved and applied to the active comment pipeline.</motion.div>}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card><div className="flex items-center gap-3 mb-6"><FiBell className="text-purple-600" /><h2 className="text-xl font-bold">Comment Intelligence</h2></div><div className="space-y-5"><label className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><div><p className="font-medium">Automatic replies</p><p className="text-sm text-gray-500">Allow safe high-confidence replies automatically.</p></div><input type="checkbox" checked={settings.auto_reply_enabled} onChange={(e) => update('auto_reply_enabled', e.target.checked)} className="w-5 h-5" /></label><div><label className="block text-sm font-medium mb-2">Confidence threshold: {Number(settings.confidence_threshold).toFixed(2)}</label><input type="range" min="0" max="1" step="0.05" value={settings.confidence_threshold} onChange={(e) => update('confidence_threshold', Number(e.target.value))} className="w-full" /></div><label className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><div><p className="font-medium">Notifications</p><p className="text-sm text-gray-500">Receive product notifications.</p></div><input type="checkbox" checked={settings.notifications_enabled} onChange={(e) => update('notifications_enabled', e.target.checked)} className="w-5 h-5" /></label></div></Card>
        <Card><div className="flex items-center gap-3 mb-6"><FiGlobe className="text-blue-600" /><h2 className="text-xl font-bold">Content Defaults</h2></div><div className="space-y-5"><div><label className="block text-sm font-medium mb-2">Default media source</label><select value={settings.default_media_source} onChange={(e) => update('default_media_source', e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600"><option value="both">Uploaded + AI</option><option value="uploaded">Uploaded only</option><option value="ai">AI only</option></select></div><div><label className="block text-sm font-medium mb-2">Default music mode</label><select value={settings.default_music_mode} onChange={(e) => update('default_music_mode', e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600"><option value="ai">AI</option><option value="uploaded">My Music</option><option value="search">Search</option></select></div></div></Card>
        <Card><div className="flex items-center gap-3 mb-6"><FiGlobe className="text-green-600" /><h2 className="text-xl font-bold">Appearance</h2></div><div className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><div><p className="font-medium">Dark Mode</p><p className="text-sm text-gray-500">Toggle the application theme.</p></div><button type="button" onClick={toggleDarkMode} className={`w-14 h-7 rounded-full ${darkMode ? 'bg-blue-500' : 'bg-gray-300'}`}><div className={`w-5 h-5 bg-white rounded-full shadow transform ${darkMode ? 'translate-x-8' : 'translate-x-1'}`} /></button></div></Card>
        <Card><div className="flex items-center gap-3 mb-6"><FiKey className="text-orange-600" /><h2 className="text-xl font-bold">AI Provider</h2></div><p className="text-gray-500">Contextual general-question replies can use the backend <code>OPENROUTER_API_KEY</code> when configured. The key is never sent to the React frontend.</p></Card>
      </div>
      <div className="flex justify-end"><Button onClick={save} loading={saving}><FiSave className="mr-2" /> Save All Changes</Button></div>
    </div>
  )
}
export default Settings
