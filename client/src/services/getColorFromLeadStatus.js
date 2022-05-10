import Utils from './utils'

// must account for null status (as is the case on Lead creation)

export function getLightenedColor(color, opacity = 0.5) {
  if (color) {
    return Utils.convertToRgba(color, opacity)
  }
  return null
}
