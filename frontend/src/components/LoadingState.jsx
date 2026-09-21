const LoadingState = ({ message = 'Loading insights...' }) => (
  <div className="state-card loading-state">
    <div className="spinner" aria-label="Loading" />
    <p>{message}</p>
  </div>
)

export default LoadingState
