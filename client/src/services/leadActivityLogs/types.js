// Define constants for the types of model events that can happen.
export const CREATED = 'CREATED'
export const UPDATED = 'UPDATED'
export const DELETED = 'DELETED'
export const CLAIMED = 'CLAIMED' // Leads only
export const RELEASED = 'RELEASED' // Leads only
export const CLOSED = 'CLOSED' // Leads only

// Possible Lead actions
export const LEAD_CREATED = 'Lead.CREATED'
export const LEAD_UPDATED = 'Lead.UPDATED'
export const LEAD_DELETED = 'Lead.DELETED'
export const LEAD_CLAIMED = 'Lead.CLAIMED'
export const LEAD_RELEASED = 'Lead.RELEASED'
export const LEAD_CLOSED = 'Lead.CLOSED'
export const LEAD_RESET = 'Lead.RESET'

export const LEAD_ACTIVITY_LOG_EXCLUDE = [LEAD_UPDATED, LEAD_CLAIMED, LEAD_RELEASED, LEAD_RESET]
// Possible Note actions
export const NOTE_CREATED = 'Note.CREATED'
export const NOTE_UPDATED = 'Note.UPDATED'
export const NOTE_DELETED = 'Note.DELETED'

export const CALL_NOTE_CREATED = 'CallNote.CREATED'
export const CALL_NOTE_UPDATED = 'CallNote.UPDATED'
export const CALL_NOTE_DELETED = 'CallNote.DELETED'

export const FILE_CREATED = 'File.CREATED'
export const FILE_UPDATED = 'File.UPDATED'
export const FILE_DELETED = 'File.DELETED'

export const REMINDER_CREATED = 'Reminder.CREATED'
export const REMINDER_UPDATED = 'Reminder.UPDATED'
export const REMINDER_DELETED = 'Reminder.DELETED'

export const ACTION_CREATED = 'Action.CREATED'
export const ACTION_UPDATED = 'Action.UPDATED'
export const ACTION_DELETED = 'Action.DELETED'

export const EMAIL_SENT = 'LeadEmail.SENT'
export const EMAIL_RECEIVED = 'LeadEmail.RECEIVED'

export default {
  CREATED,
  UPDATED,
  DELETED,
  CLAIMED,
  RELEASED,
  CLOSED,
  LEAD_CREATED,
  LEAD_UPDATED,
  LEAD_DELETED,
  LEAD_CLAIMED,
  LEAD_RELEASED,
  LEAD_CLOSED,
  NOTE_CREATED,
  NOTE_UPDATED,
  NOTE_DELETED,
  CALL_NOTE_CREATED,
  CALL_NOTE_UPDATED,
  CALL_NOTE_DELETED,
  FILE_CREATED,
  FILE_UPDATED,
  FILE_DELETED,
  REMINDER_CREATED,
  REMINDER_UPDATED,
  REMINDER_DELETED,
  ACTION_CREATED,
  ACTION_UPDATED,
  ACTION_DELETED,
  EMAIL_SENT,
  EMAIL_RECEIVED,
  LEAD_ACTIVITY_LOG_EXCLUDE,
}
