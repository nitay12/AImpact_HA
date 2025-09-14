interface AIReport {
  report_content: string
  generation_timestamp: string
}

interface ReportDisplayProps {
  report: AIReport
  onBack: () => void
}

const ReportDisplay: React.FC<ReportDisplayProps> = ({ report, onBack }) => {
  const handlePrint = () => {
    window.print()
  }

  const formatDate = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleString('he-IL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatReportContent = (content: string) => {
    // Split content by double newlines to create paragraphs
    const paragraphs = content.split('\n\n').filter(p => p.trim())
    
    return paragraphs.map((paragraph, index) => {
      // Check if it's a header (starts with a number or bullet)
      if (paragraph.match(/^\d+\.\s/) || paragraph.includes('##') || paragraph.includes('**')) {
        return (
          <div key={index} className="report-section">
            <h3>{paragraph.replace(/[#*]/g, '').trim()}</h3>
          </div>
        )
      }
      
      // Check if it's a list item
      if (paragraph.includes('•') || paragraph.includes('-')) {
        const listItems = paragraph.split('\n').filter(item => item.trim())
        return (
          <ul key={index} className="report-list">
            {listItems.map((item, itemIndex) => (
              <li key={itemIndex}>{item.replace(/^[•-]\s*/, '').trim()}</li>
            ))}
          </ul>
        )
      }
      
      // Regular paragraph
      return (
        <p key={index} className="report-paragraph">
          {paragraph.trim()}
        </p>
      )
    })
  }

  return (
    <div className="report-section">
      <div className="report-header">
        <div className="report-title">
          <h2>דוח התאמה לרישוי עסק</h2>
          <div className="report-meta">
            <span className="generation-time">
              נוצר בתאריך: {formatDate(report.generation_timestamp)}
            </span>
          </div>
        </div>
        <div className="report-actions">
          <button onClick={onBack} className="btn-secondary">
            חזרה לשאלון
          </button>
        </div>
      </div>

      <div className="report-content">
        <div className="report-body">
          {formatReportContent(report.report_content)}
        </div>
      </div>

      <div className="report-footer">
        <div className="report-actions">
          <button onClick={handlePrint} className="btn-secondary">
            🖨️ הדפס דוח
          </button>
          <button onClick={onBack} className="btn-secondary">
            חזרה לשאלון
          </button>
        </div>
        
        <div className="disclaimer">
          <p>
            <strong>הערה:</strong> דוח זה נוצר באמצעות בינה מלאכותית ומיועד להכוונה בלבד. 
            יש להתייעץ עם גורמים מקצועיים לפני ביצוע פעולות.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ReportDisplay