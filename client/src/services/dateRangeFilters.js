import moment from 'moment'
import Forecast from '@/services/forecasts'

export function dateRangeParamsFromPreset(preset) {
  return switcher[preset]()
}

const switcher = {
  [Forecast.TODAY_ONWARD]: todayOnward,
  [Forecast.TODAY]: today,
  [Forecast.YESTERDAY]: yesterday,
  [Forecast.THIS_WEEK]: thisWeek,
  [Forecast.LAST_WEEK]: lastWeek,
  [Forecast.THIS_MONTH]: thisMonth,
  [Forecast.LAST_MONTH]: lastMonth,
  [Forecast.NEXT_MONTH]: nextMonth,
  [Forecast.THIS_QUARTER]: thisQuarter,
  [Forecast.LAST_QUARTER]: lastQuarter,
  [Forecast.NEXT_QUARTER]: nextQuarter,
  [Forecast.THIS_YEAR]: thisYear,
  [Forecast.LAST_YEAR]: lastYear,
  [Forecast.ALL_TIME]: allTime,
}

function todayOnward() {
  return {
    dateRangeFrom: moment()
      .startOf('day')
      .toISOString(),
    dateRangeTo: null,
  }
}

function today() {
  return {
    dateRangeFrom: moment()
      .startOf('day')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('day')
      .toISOString(),
  }
}

function yesterday() {
  return {
    dateRangeFrom: moment()
      .startOf('day')
      .subtract(1, 'days')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('day')
      .subtract(1, 'days')
      .toISOString(),
  }
}

function thisWeek() {
  // moment weeks are Sun - Sat
  // UX requires Mon - Sun
  return {
    dateRangeFrom: moment()
      .startOf('week')
      .add(1, 'days')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('week')
      .add(1, 'days')
      .toISOString(),
  }
}

function lastWeek() {
  // moment weeks are Sun - Sat
  // UX requires Mon - Sun
  return {
    dateRangeFrom: moment()
      .startOf('week')
      .add(1, 'days')
      .subtract(1, 'weeks')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('week')
      .add(1, 'days')
      .subtract(1, 'weeks')
      .toISOString(),
  }
}

function thisMonth() {
  return {
    dateRangeFrom: moment()
      .startOf('month')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('month')
      .toISOString(),
  }
}

function lastMonth() {
  // Need to account for non-consistent month length
  return {
    dateRangeFrom: moment()
      .startOf('month')
      .subtract(1, 'days')
      .startOf('month')
      .toISOString(),
    dateRangeTo: moment()
      .startOf('month')
      .subtract(1, 'days')
      .endOf('month')
      .toISOString(),
  }
}

function nextMonth() {
  // Need to account for non-consistent month length
  return {
    dateRangeFrom: moment()
      .endOf('month')
      .add(1, 'days')
      .startOf('month')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('month')
      .add(1, 'days')
      .endOf('month')
      .toISOString(),
  }
}

function thisQuarter() {
  return {
    dateRangeFrom: moment()
      .startOf('quarter')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('quarter')
      .toISOString(),
  }
}

function lastQuarter() {
  return {
    dateRangeFrom: moment()
      .startOf('quarter')
      .subtract(1, 'days')
      .startOf('quarter')
      .toISOString(),
    dateRangeTo: moment()
      .startOf('quarter')
      .subtract(1, 'days')
      .endOf('quarter')
      .toISOString(),
  }
}

function nextQuarter() {
  return {
    dateRangeFrom: moment()
      .endOf('quarter')
      .add(1, 'days')
      .startOf('quarter')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('quarter')
      .add(1, 'days')
      .endOf('quarter')
      .toISOString(),
  }
}

function thisYear() {
  return {
    dateRangeFrom: moment()
      .startOf('year')
      .toISOString(),
    dateRangeTo: moment()
      .endOf('year')
      .toISOString(),
  }
}

function lastYear() {
  return {
    dateRangeFrom: moment()
      .startOf('year')
      .subtract(1, 'days')
      .startOf('year')
      .toISOString(),
    dateRangeTo: moment()
      .startOf('year')
      .subtract(1, 'days')
      .endOf('year')
      .toISOString(),
  }
}

function allTime() {
  return {
    dateRangeFrom: null,
    dateRangeTo: null,
  }
}
