from . import consumers

routes = {
    "Lead": consumers.LeadActionConsumer,
    "Note": consumers.NoteActionConsumer,
    "CallNote": consumers.CallNoteActionConsumer,
}
