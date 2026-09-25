const ErrorState = ({ message = 'Something went wrong while loading the data.' }) => (
  <div className="state-card error-state">
    <h3>Unable to load data</h3>
    <p>{message}</p>
  </div>
)

export default ErrorState
