import { useState } from 'react'

interface BusinessProfile {
  business_name?: string
  size_sqm: number
  capacity_people: number
  special_characteristics: string[]
}

interface BusinessQuestionnaireProps {
  onSubmit: (businessData: BusinessProfile) => void
}

const BusinessQuestionnaire: React.FC<BusinessQuestionnaireProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<BusinessProfile>({
    business_name: '',
    size_sqm: 0,
    capacity_people: 0,
    special_characteristics: []
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target
    
    if (type === 'number') {
      setFormData(prev => ({
        ...prev,
        [name]: parseInt(value) || 0
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target
    
    setFormData(prev => ({
      ...prev,
      special_characteristics: checked
        ? [...prev.special_characteristics, value]
        : prev.special_characteristics.filter(char => char !== value)
    }))
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.size_sqm || formData.size_sqm <= 0) {
      newErrors.size_sqm = 'אנא הזינו גודל עסק תקין'
    }

    if (!formData.capacity_people || formData.capacity_people <= 0) {
      newErrors.capacity_people = 'אנא הזינו תפוסה תקינה'
    }

    if (formData.size_sqm > 10000) {
      newErrors.size_sqm = 'גודל העסק לא יכול להיות יותר מ-10,000 מ"ר'
    }

    if (formData.capacity_people > 1000) {
      newErrors.capacity_people = 'תפוסה לא יכולה להיות יותר מ-1,000 אנשים'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onSubmit(formData)
    }
  }

  const specialCharacteristics = [
    { value: 'gas_cooking', label: 'בישול בגז' },
    { value: 'meat_serving', label: 'הגשת בשר' },
    { value: 'delivery_service', label: 'שירות משלוחים' },
    { value: 'outdoor_seating', label: 'ישיבה חיצונית' },
    { value: 'alcohol_service', label: 'הגשת אלכוהול' }
  ]

  return (
    <div className="questionnaire-section">
      <h2>שאלון פרטי העסק</h2>
      <p className="instructions">
        אנא מלאו את הפרטים הבאים לקבלת דוח התאמה מותאם אישית:
      </p>

      <form onSubmit={handleSubmit} className="questionnaire-form">
        {/* Business Name */}
        <div className="form-group">
          <label htmlFor="business-name">שם העסק (אופציונלי):</label>
          <input
            type="text"
            id="business-name"
            name="business_name"
            value={formData.business_name}
            onChange={handleInputChange}
            placeholder="למשל: מסעדת הים התיכון"
            className="form-input"
          />
        </div>

        {/* Size */}
        <div className="form-group">
          <label htmlFor="size-sqm">
            גודל העסק (במטרים רבועים) <span className="required">*</span>:
          </label>
          <input
            type="number"
            id="size-sqm"
            name="size_sqm"
            value={formData.size_sqm || ''}
            onChange={handleInputChange}
            placeholder="למשל: 150"
            className={`form-input ${errors.size_sqm ? 'error' : ''}`}
            min="1"
            max="10000"
            required
          />
          {errors.size_sqm && (
            <span className="error-text">{errors.size_sqm}</span>
          )}
          <small className="help-text">גודל השטח הכולל של העסק</small>
        </div>

        {/* Capacity */}
        <div className="form-group">
          <label htmlFor="capacity-people">
            תפוסה מקסימלית (מספר אנשים) <span className="required">*</span>:
          </label>
          <input
            type="number"
            id="capacity-people"
            name="capacity_people"
            value={formData.capacity_people || ''}
            onChange={handleInputChange}
            placeholder="למשל: 80"
            className={`form-input ${errors.capacity_people ? 'error' : ''}`}
            min="1"
            max="1000"
            required
          />
          {errors.capacity_people && (
            <span className="error-text">{errors.capacity_people}</span>
          )}
          <small className="help-text">
            מספר האנשים המקסימלי שיכול להיות במקום בו זמנית
          </small>
        </div>

        {/* Special Characteristics */}
        <div className="form-group">
          <label>מאפיינים מיוחדים:</label>
          <div className="checkbox-group">
            {specialCharacteristics.map(({ value, label }) => (
              <div key={value} className="checkbox-item">
                <input
                  type="checkbox"
                  id={value}
                  value={value}
                  checked={formData.special_characteristics.includes(value)}
                  onChange={handleCheckboxChange}
                />
                <label htmlFor={value}>{label}</label>
              </div>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="form-actions">
          <button type="submit" className="btn-primary">
            צור דוח התאמה
          </button>
        </div>
      </form>
    </div>
  )
}

export default BusinessQuestionnaire