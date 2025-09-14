const LoadingSpinner: React.FC = () => {
  return (
    <div className="loading-section">
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
      <h3>יוצר דוח מותאם אישית...</h3>
      <p>הבינה המלאכותית מעבדת את הנתונים שלכם ויוצרת דוח מפורט</p>
      <div className="loading-steps">
        <div className="step">
          <span className="step-icon">📋</span>
          <span>עיבוד נתוני העסק</span>
        </div>
        <div className="step">
          <span className="step-icon">🔍</span>
          <span>התאמת דרישות רגולטוריות</span>
        </div>
        <div className="step">
          <span className="step-icon">🤖</span>
          <span>יצירת דוח מותאם אישית</span>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner