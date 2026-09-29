import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiUser, FiSave, FiRefreshCw } from 'react-icons/fi'
import Button from '../../components/Button'
import Card from '../../components/Card'
import Input from '../../components/Input'
import { api } from '../../services/api'

const Profile = () => {
  const [profile, setProfile] = useState({
    name: '', username: '', bio: '', niche: '', tone: 'friendly', language: 'English', reply_style: 'short', emoji_preference: 'occasional'
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getCreatorProfile().then((data) => {
      setProfile((prev) => ({ ...prev, ...(data?.creator_profile || {}) }))
    }).catch((err) => setError(err.message)).finally(() => setLoading(false))
  }, [])

  const update = (key, value) => setProfile((prev) => ({ ...prev, [key]: value }))

  const save = async (event) => {
    event.preventDefault()
    setSaving(true); setError(''); setSuccess(false)
    try {
      const data = await api.updateCreatorProfile(profile)
      setProfile((prev) => ({ ...prev, ...(data?.creator_profile || {}) }))
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2500)
    } catch (err) { setError(err.message || 'Failed to save profile.') }
    finally { setSaving(false) }
  }

  return (
    <div className="space-y-8">
      <div><h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Profile</h1><p className="text-gray-600 dark:text-gray-300">This profile is used by FrameCraft comment intelligence to personalize replies.</p></div>
      {error && <div className="p-4 rounded-xl bg-red-100 text-red-700">{error}</div>}
      {success && <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="p-4 rounded-xl bg-green-100 text-green-700">Profile saved. Live comment intelligence is now synchronized.</motion.div>}
      <form onSubmit={save} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2"><Card>
          <div className="flex items-center gap-4 mb-8"><div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">{profile.name?.charAt(0)?.toUpperCase() || 'U'}</div><div><h2 className="text-xl font-bold text-gray-900 dark:text-white">Creator Identity</h2><p className="text-gray-500">Saved to the backend knowledge layer.</p></div></div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <Input label="Name" value={profile.name} onChange={(e) => update('name', e.target.value)} />
            <Input label="Username" value={profile.username} onChange={(e) => update('username', e.target.value)} />
            <Input label="Niche" value={profile.niche} onChange={(e) => update('niche', e.target.value)} />
            <Input label="Language" value={profile.language} onChange={(e) => update('language', e.target.value)} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-6">
            <div><label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Tone</label><select value={profile.tone} onChange={(e) => update('tone', e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600"><option>friendly</option><option>professional</option><option>formal</option><option>enthusiastic</option><option>casual</option></select></div>
            <div><label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Reply Style</label><select value={profile.reply_style} onChange={(e) => update('reply_style', e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600"><option>very short</option><option>short</option><option>medium</option><option>long</option></select></div>
            <div><label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Emoji Preference</label><select value={profile.emoji_preference} onChange={(e) => update('emoji_preference', e.target.value)} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600"><option>none</option><option>occasional</option><option>frequent</option></select></div>
          </div>
          <div className="mt-6"><label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Bio / Creator Context</label><textarea value={profile.bio} onChange={(e) => update('bio', e.target.value)} rows={5} className="w-full px-4 py-3 rounded-xl border dark:bg-gray-700 dark:border-gray-600" placeholder="Tell FrameCraft what your content is about." /></div>
          <Button type="submit" loading={saving} className="mt-6"><FiSave className="mr-2" /> Save Profile</Button>
        </Card></div>
        <Card><h2 className="text-xl font-bold text-gray-900 dark:text-white mb-5">Live AI Context</h2><div className="space-y-4 text-sm"><div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><p className="font-medium">Reply tone</p><p className="text-gray-500 mt-1">{profile.tone}</p></div><div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><p className="font-medium">Language</p><p className="text-gray-500 mt-1">{profile.language}</p></div><div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50"><p className="font-medium">Niche</p><p className="text-gray-500 mt-1">{profile.niche || 'Not set'}</p></div><p className="text-gray-500">When a question arrives, FrameCraft can combine this profile with the selected project's script, uploaded-video context and creator knowledge.</p></div></Card>
      </form>
    </div>
  )
}
export default Profile
