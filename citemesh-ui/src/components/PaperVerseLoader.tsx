import { useId } from 'react'

type PaperVerseLoaderProps = {
  fullscreen?: boolean
  message?: string
  isExiting?: boolean
}

const PaperVerseLoader = ({
  fullscreen = false,
  message = 'Preparing PaperVerse…',
  isExiting = false
}: PaperVerseLoaderProps) => {
  const gradientId = useId()
  const foldGradientId = useId()

  return (
    <div
      className={[
        'paperverse-loader',
        fullscreen ? 'paperverse-loader--fullscreen' : '',
        isExiting ? 'paperverse-loader--exit' : ''
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <div className="paperverse-loader__logo" aria-hidden="true">
        <svg viewBox="0 0 120 120" role="presentation">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#c084fc" />
              <stop offset="50%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
            <linearGradient id={foldGradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ede9fe" />
              <stop offset="100%" stopColor="#c4b5fd" />
            </linearGradient>
          </defs>
          <path
            d="M20 15h52l28 28v62H20z"
            fill={`url(#${gradientId})`}
            className="paperverse-loader__sheet"
          />
          <path
            d="M72 15v28h28"
            fill={`url(#${foldGradientId})`}
            className="paperverse-loader__fold"
          />
        </svg>
      </div>
      <div className="paperverse-loader__progress" aria-hidden="true">
        <div className="paperverse-loader__progress-track">
          <div className="paperverse-loader__progress-fill" />
        </div>
      </div>
      {message ? (
        <p className="paperverse-loader__message" aria-live="polite">
          {message}
        </p>
      ) : null}
    </div>
  )
}

export default PaperVerseLoader
