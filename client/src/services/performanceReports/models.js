import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import PerformanceReportAPI from './api'

export default class PerformanceReport {
  static api = PerformanceReportAPI.create(PerformanceReport)

  // Date Range Presets
  static THIS_MONTH = 'THIS_MONTH'
  static LAST_MONTH = 'LAST_MONTH'
  static THIS_QUARTER = 'THIS_QUARTER'
  static LAST_QUARTER = 'LAST_QUARTER'
  static THIS_YEAR = 'THIS_YEAR'
  static LAST_YEAR = 'LAST_YEAR'

  constructor({
    id = '',
    representative = null,
    representativeRef = null,
    dateRangePreset = null,
    dateRangeFrom = null,
    dateRangeTo = null,
    data = null,
    datetimeGenerated = null,
    datetimeCreated = null,
    generatedBy = '',
    isRepresentativeReport = null,
    isOrganizationReport = null,
  } = {}) {
    Object.assign(this, {
      id,
      representative,
      representativeRef,
      dateRangePreset,
      dateRangeFrom,
      dateRangeTo,
      data,
      datetimeGenerated,
      datetimeCreated,
      generatedBy,
      isRepresentativeReport,
      isOrganizationReport,
    })
  }

  static create(opts) {
    return new PerformanceReport(opts)
  }

  static fromAPI(json) {
    return new PerformanceReport(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new PerformanceReport(this)
  }
}
