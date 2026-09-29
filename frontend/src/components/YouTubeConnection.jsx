import { useEffect, useState } from 'react'

import {
  FiAlertCircle,
  FiCheckCircle,
  FiLoader,
  FiLogOut,
  FiRefreshCw,
  FiYoutube
} from 'react-icons/fi'

import { api } from '../services/api'


const YouTubeConnection = () => {

  const [loading, setLoading] =
    useState(true)

  const [connecting, setConnecting] =
    useState(false)

  const [disconnecting, setDisconnecting] =
    useState(false)

  const [connection, setConnection] =
    useState(null)

  const [error, setError] =
    useState('')


  const USER_ID = 'demo_user'


  // ==========================================================
  // CHECK CONNECTION
  // ==========================================================

  const checkConnection = async () => {

    try {

      setLoading(true)

      setError('')


      const result =
        await api.getYouTubeStatus(
          USER_ID
        )


      console.log(
        'YouTube status:',
        result
      )


      setConnection(
        result
      )

    } catch (err) {

      console.error(
        'YouTube status error:',
        err
      )


      setError(
        err?.message ||
        'Failed to check YouTube connection.'
      )

    } finally {

      setLoading(false)

    }

  }


  useEffect(() => {

    checkConnection()

  }, [])


  // ==========================================================
  // CONNECT
  // ==========================================================

  const handleConnect = async () => {

    try {

      setConnecting(true)

      setError('')


      console.log(
        'Starting YouTube OAuth...'
      )


      const result =
        await api.connectYouTube(
          USER_ID
        )


      console.log(
        'YouTube OAuth response:',
        result
      )


      if (
        !result ||
        !result.authorization_url
      ) {

        throw new Error(
          'Backend did not return a YouTube authorization URL.'
        )

      }


      console.log(
        'Redirecting to Google OAuth...'
      )


      // IMPORTANT:
      // Navigate the current browser tab to Google.
      window.location.assign(
        result.authorization_url
      )


    } catch (err) {

      console.error(
        'YouTube connection failed:',
        err
      )


      setError(
        err?.message ||
        'Failed to connect YouTube.'
      )

      setConnecting(false)

    }

  }


  // ==========================================================
  // DISCONNECT
  // ==========================================================

  const handleDisconnect = async () => {

    try {

      setDisconnecting(true)

      setError('')


      await api.disconnectYouTube(
        USER_ID
      )


      setConnection({
        connected: false
      })


    } catch (err) {

      console.error(
        'YouTube disconnect error:',
        err
      )


      setError(
        err?.message ||
        'Failed to disconnect YouTube.'
      )

    } finally {

      setDisconnecting(false)

    }

  }


  // ==========================================================
  // LOADING
  // ==========================================================

  if (loading) {

    return (

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

        <div className="flex items-center gap-3">

          <FiLoader
            className="animate-spin text-red-600"
            size={22}
          />

          <span className="text-sm text-gray-600">

            Checking YouTube connection...

          </span>

        </div>

      </div>

    )

  }


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      {/* HEADER */}

      <div className="flex items-start justify-between gap-4">

        <div className="flex items-center gap-3">

          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600">

            <FiYoutube
              size={25}
            />

          </div>


          <div>

            <h2 className="text-lg font-bold text-gray-900">

              YouTube

            </h2>

            <p className="text-sm text-gray-500">

              Connect your YouTube channel

            </p>

          </div>

        </div>


        {/* STATUS */}

        {connection?.connected ? (

          <div className="flex items-center gap-2 rounded-full bg-green-50 px-3 py-1.5 text-xs font-semibold text-green-700">

            <FiCheckCircle />

            Connected

          </div>

        ) : (

          <div className="rounded-full bg-gray-100 px-3 py-1.5 text-xs font-semibold text-gray-600">

            Not connected

          </div>

        )}

      </div>


      {/* ERROR */}

      {error && (

        <div className="mt-4 flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">

          <FiAlertCircle
            className="mt-0.5 shrink-0"
          />

          <div className="flex-1">

            <p className="font-semibold">

              YouTube connection error

            </p>

            <p className="mt-1">

              {error}

            </p>

          </div>

        </div>

      )}


      {/* CONNECTED */}

      {connection?.connected ? (

        <div className="mt-5">

          <div className="rounded-xl bg-gray-50 p-4">

            <p className="text-sm text-gray-500">

              Connected channel

            </p>

            <p className="mt-1 font-semibold text-gray-900">

              {connection.channel_title ||
                connection.channel?.title ||
                'YouTube Channel'}

            </p>


            {(connection.channel_id ||
              connection.channel?.id) && (

              <p className="mt-1 text-xs text-gray-500">

                Channel ID:{' '}

                {connection.channel_id ||
                  connection.channel?.id}

              </p>

            )}

          </div>


          <div className="mt-4 flex flex-wrap gap-3">

            <button
              type="button"
              onClick={checkConnection}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
            >

              <FiRefreshCw />

              Refresh

            </button>


            <button
              type="button"
              onClick={handleDisconnect}
              disabled={disconnecting}
              className="inline-flex items-center gap-2 rounded-lg border border-red-200 px-4 py-2.5 text-sm font-semibold text-red-600 hover:bg-red-50"
            >

              {disconnecting ? (

                <FiLoader
                  className="animate-spin"
                />

              ) : (

                <FiLogOut />

              )}

              Disconnect

            </button>

          </div>

        </div>

      ) : (

        /* NOT CONNECTED */

        <div className="mt-5">

          <p className="text-sm leading-6 text-gray-600">

            Connect your YouTube account to publish
            and schedule FrameCraft AI videos directly
            from the application.

          </p>


          <button
            type="button"
            onClick={handleConnect}
            disabled={connecting}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-red-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
          >

            {connecting ? (

              <>
                <FiLoader
                  className="animate-spin"
                />

                Opening Google...

              </>

            ) : (

              <>
                <FiYoutube />

                Connect YouTube

              </>

            )}

          </button>

        </div>

      )}

    </div>

  )

}


export default YouTubeConnection