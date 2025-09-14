import { useState } from 'react'
import './App.css'
import BusinessQuestionnaire from './components/BusinessQuestionnaire'
import ReportDisplay from './components/ReportDisplay'
import LoadingSpinner from './components/LoadingSpinner'

interface BusinessProfile {
  business_name?: string
  size_sqm: number
  capacity_people: number
  special_characteristics: string[]
}

interface AIReport {
  report_content: string
  generation_timestamp: string
  model_used: string
  tokens_used?: number
  processing_time?: number
}

function App() {
  const [currentView, setCurrentView] = useState<'questionnaire' | 'loading' | 'report' | 'error'>('questionnaire')
  const [report, setReport] = useState<AIReport | null>(null)
  const [error, setError] = useState<string>('')

  const handleQuestionnaireSubmit = async (businessData: BusinessProfile) => {
    setCurrentView('loading')
    setError('')

    try {
      // Call the FastAPI backend to generate report
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          business_name: businessData.business_name,
          business_size_sqm: businessData.size_sqm,
          seating_capacity: businessData.capacity_people,
          uses_gas: businessData.special_characteristics.includes('gas_cooking'),
          serves_meat: businessData.special_characteristics.includes('meat_serving'),
          offers_delivery: businessData.special_characteristics.includes('delivery_service'),
          serves_alcohol: businessData.special_characteristics.includes('alcohol_service'),
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const reportData: AIReport = await response.json()
      setReport(reportData)
      setCurrentView('report')
    } catch (err) {
      console.error('Error generating report:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate report')
      setCurrentView('error')
    }
  }

  const handleBackToQuestionnaire = () => {
    setCurrentView('questionnaire')
    setReport(null)
    setError('')
  }

  const handleRetry = () => {
    setCurrentView('questionnaire')
    setError('')
  }

  return (
    <div className="app" dir="rtl" lang="he">
      <header className="app-header">
        <h1>regu-biz / רגו-ביז</h1>
        <p>מערכת הערכת רישוי עסקים מבוססת בינה מלאכותית</p>
      </header>

      <main className="app-main">
        {currentView === 'questionnaire' && (
          <BusinessQuestionnaire onSubmit={handleQuestionnaireSubmit} />
        )}

        {currentView === 'loading' && (
          <LoadingSpinner />
        )}

        {currentView === 'report' && report && (
          <ReportDisplay 
            report={report} 
            onBack={handleBackToQuestionnaire} 
          />
        )}

        {currentView === 'error' && (
          <div className="error-section">
            <h3>אירעה שגיאה</h3>
            <p className="error-message">{error}</p>
            <div className="error-actions">
              <button onClick={handleRetry} className="btn-primary">
                נסה שוב
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>מערכת regu-biz / רגו-ביז - מבוססת על בינה מלאכותית לעיבוד רגולציות בטיחות אש</p>
      </footer>
    </div>
  )
}

export default App