import Utils from './utils'

const statusToPrimaryColor = {
  lead: '#1C1F1D',
  ready: '#FAB900',
  booked: '#FA646A',
  demo: '#88C9F9',
  trial: 'rgba(165, 55, 253, 1)',
  waiting: '#9596B3',
  closed: '#2F9E54',
  lost: '#1C1F1C',
  null: '#9596B4',
}

const statusToSecondaryColor = {
  lead: 'white',
  ready: '#FEF1CD',
  booked: ' #FFB5B8',
  demo: '#E8F4FE',
  trial: 'rgba(165, 55, 253, 0.5)',
  waiting: '#EFF0F5',
  closed: '#D1ECDD',
  lost: '#CACFCC',
  null: '#EFEFF5',
}

// must account for null status (as is the case on Lead creation)

export function getLightenedColor(color, opacity = 0.5) {
  if (color) {
    return Utils.convertToRgba(color, opacity)
  }
  return null
}
