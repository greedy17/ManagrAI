from . import consumers

routes = {
    "Lead": consumers.LeadActionConsumer,
    "Note": consumers.NoteActionConsumer,
    "CallNote": consumers.CallNoteActionConsumer,
    "Action": consumers.ActionActionConsumer,
    "LeadEmail": consumers.LeadEmailActionConsumer,
    "Reminder": consumers.ReminderActionConsumer,
    "LeadMessage": consumers.LeadMessageActionConsumer,
}
