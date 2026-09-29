import {
  useEffect,
  useState
} from 'react'

import {
  FiCheck,
  FiRefreshCw,
  FiX,
  FiActivity
} from 'react-icons/fi'

import Card from '../../components/Card'
import Button from '../../components/Button'

import { api } from '../../services/api'


const MLOps = () => {

  const [
    data,
    setData
  ] = useState(null)


  const [
    loading,
    setLoading
  ] = useState(true)


  const [
    working,
    setWorking
  ] = useState(false)


  const [
    error,
    setError
  ] = useState('')


  const [
    message,
    setMessage
  ] = useState('')


  // ========================================================
  // LOAD
  // ========================================================

  const load = async () => {

    try {

      const result =
        await api.getMLOpsStatus()


      setData(result)

      setError('')

    }

    catch (err) {

      setError(
        err.message ||
        'Failed to load MLOps status.'
      )

    }

    finally {

      setLoading(false)

    }

  }


  // ========================================================
  // LIVE POLLING
  // ========================================================

  useEffect(() => {

    load()


    const intervalId =
      window.setInterval(
        load,
        5000
      )


    return () =>
      window.clearInterval(
        intervalId
      )

  }, [])


  // ========================================================
  // MODEL DECISION
  // ========================================================

  const decision = async (
    type
  ) => {

    const version =
      data?.candidate?.version
      ||
      data?.state?.candidate_version


    if (!version) {

      return

    }


    setWorking(true)

    setError('')

    setMessage('')


    try {

      if (
        type === 'approve'
      ) {

        await api.approveMLOpsModel(
          version
        )


        setMessage(
          `Model ${version} approved and promoted to production.`
        )

      }

      else {

        await api.rejectMLOpsModel(
          version
        )


        setMessage(
          `Model ${version} rejected.`
        )

      }


      await load()

    }

    catch (err) {

      setError(
        err.message ||
        'MLOps decision failed.'
      )

    }

    finally {

      setWorking(false)

    }

  }


  // ========================================================
  // RETRAIN
  // ========================================================

  const retrain = async () => {

    setWorking(true)

    setError('')

    setMessage('')


    try {

      const result =
        await api.retrainMLOpsModel(
          'manual_creator_request'
        )


      setMessage(
        `Candidate ${
          result?.candidate?.version
          || 'created'
        }`
      )


      await load()

    }

    catch (err) {

      setError(
        err.message ||
        'Retraining failed.'
      )

    }

    finally {

      setWorking(false)

    }

  }


  const state =
    data?.state || {}


  const candidate =
    data?.candidate


  const metrics =
    candidate?.metrics || {}


  return (

    <div className="space-y-8">

      {/* ================================================== */}
      {/* HEADER */}
      {/* ================================================== */}

      <div className="
        flex
        flex-col
        md:flex-row
        md:items-end
        md:justify-between
        gap-4
      ">

        <div>

          <h1 className="
            text-3xl
            font-bold
            text-gray-900
            dark:text-white
          ">

            MLOps Control Center

          </h1>


          <p className="
            text-gray-600
            dark:text-gray-300
            mt-2
          ">

            Analytics monitoring,
            retraining, model versioning
            and creator-approved deployment.

          </p>

        </div>


        <Button
          onClick={retrain}
          loading={working}
        >

          <FiRefreshCw
            className="mr-2"
          />

          Retrain Now

        </Button>

      </div>


      {/* ================================================== */}
      {/* ERROR */}
      {/* ================================================== */}

      {error && (

        <div className="
          p-4
          rounded-xl
          bg-red-100
          text-red-700
        ">

          {error}

        </div>

      )}


      {/* ================================================== */}
      {/* SUCCESS */}
      {/* ================================================== */}

      {message && (

        <div className="
          p-4
          rounded-xl
          bg-green-100
          text-green-700
        ">

          {message}

        </div>

      )}


      {/* ================================================== */}
      {/* STATUS CARDS */}
      {/* ================================================== */}

      <div className="
        grid
        grid-cols-1
        md:grid-cols-4
        gap-4
      ">

        <Card>

          <p className="text-sm text-gray-500">
            Production
          </p>

          <p className="font-bold mt-2">
            {state.production_version ||
              'Not deployed'}
          </p>

        </Card>


        <Card>

          <p className="text-sm text-gray-500">
            Candidate
          </p>

          <p className="font-bold mt-2">
            {state.candidate_version ||
              'None'}
          </p>

        </Card>


        <Card>

          <p className="text-sm text-gray-500">
            Snapshots
          </p>

          <p className="font-bold mt-2">
            {data?.snapshots ?? 0}
          </p>

        </Card>


        <Card>

          <p className="text-sm text-gray-500">
            Training Rows
          </p>

          <p className="font-bold mt-2">
            {data?.training_rows ?? 0}
          </p>

        </Card>

      </div>


      {/* ================================================== */}
      {/* MONITORING */}
      {/* ================================================== */}

      <Card>

        <div className="
          flex
          items-center
          gap-3
          mb-6
        ">

          <FiActivity
            className="text-blue-600"
          />


          <div>

            <h2 className="
              text-xl
              font-bold
              text-gray-900
              dark:text-white
            ">

              Monitoring

            </h2>


            <p className="
              text-sm
              text-gray-500
            ">

              Status:
              {' '}
              {state.status ||
                'unknown'}

            </p>

          </div>

        </div>


        <div className="
          grid
          grid-cols-1
          md:grid-cols-3
          gap-4
        ">

          <div className="
            p-4
            rounded-xl
            bg-gray-50
            dark:bg-gray-700/50
          ">

            <p className="text-sm text-gray-500">
              Data Drift
            </p>

            <p className="
              text-2xl
              font-bold
              mt-1
            ">

              {Number(
                state.last_drift || 0
              ).toFixed(3)}

            </p>

          </div>


          <div className="
            p-4
            rounded-xl
            bg-gray-50
            dark:bg-gray-700/50
          ">

            <p className="text-sm text-gray-500">
              Last Trigger
            </p>

            <p className="
              font-semibold
              mt-1
            ">

              {state.last_trigger ||
                'None'}

            </p>

          </div>


          <div className="
            p-4
            rounded-xl
            bg-gray-50
            dark:bg-gray-700/50
          ">

            <p className="text-sm text-gray-500">
              Last Snapshot
            </p>

            <p className="
              font-semibold
              mt-1
            ">

              {state.last_snapshot_at ||
                'None'}

            </p>

          </div>

        </div>

      </Card>


      {/* ================================================== */}
      {/* CANDIDATE */}
      {/* ================================================== */}

      {candidate && (

        <Card>

          <h2 className="
            text-xl
            font-bold
            text-gray-900
            dark:text-white
          ">

            Candidate Model

          </h2>


          <p className="
            text-sm
            text-gray-500
            mt-1
          ">

            {candidate.version}

          </p>


          <div className="
            grid
            grid-cols-1
            md:grid-cols-3
            gap-4
            mt-6
          ">

            <div className="
              p-4
              rounded-xl
              bg-gray-50
              dark:bg-gray-700/50
            ">

              <p className="
                text-sm
                text-gray-500
              ">

                MAE

              </p>

              <p className="
                text-xl
                font-bold
              ">

                {metrics.mae ?? '-'}

              </p>

            </div>


            <div className="
              p-4
              rounded-xl
              bg-gray-50
              dark:bg-gray-700/50
            ">

              <p className="
                text-sm
                text-gray-500
              ">

                RMSE

              </p>

              <p className="
                text-xl
                font-bold
              ">

                {metrics.rmse ?? '-'}

              </p>

            </div>


            <div className="
              p-4
              rounded-xl
              bg-gray-50
              dark:bg-gray-700/50
            ">

              <p className="
                text-sm
                text-gray-500
              ">

                R²

              </p>

              <p className="
                text-xl
                font-bold
              ">

                {metrics.r2 ?? '-'}

              </p>

            </div>

          </div>


          {/* ================================================== */}
          {/* DECISION BUTTONS */}
          {/* ================================================== */}

          <div className="
            flex
            flex-wrap
            gap-3
            mt-6
          ">

            <Button
              onClick={() =>
                decision(
                  'approve'
                )
              }
              loading={working}
            >

              <FiCheck
                className="mr-2"
              />

              Approve & Deploy

            </Button>


            <Button
              onClick={() =>
                decision(
                  'reject'
                )
              }
              loading={working}
              className="
                bg-gray-600
                hover:bg-gray-700
              "
            >

              <FiX
                className="mr-2"
              />

              Reject

            </Button>

          </div>

        </Card>

      )}


      {loading && (

        <p className="text-gray-500">

          Loading MLOps status...

        </p>

      )}

    </div>

  )

}


export default MLOps