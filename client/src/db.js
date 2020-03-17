const lists = [
  {
    id: 1,
    title: 'Q2 Buyers',
    // computed value: total leads in list
  },
  {
    id: 2,
    title: 'New Leads',
    // computed value: total leads in list
  },
  {
    id: 3,
    title: 'Competitor Leads',
    // computed value: total leads in list
  },
  {
    id: 4,
    title: 'Todays Hit List',
    // computed value: total leads in list
  },
  {
    id: 5,
    title: 'Circle Back',
    // computed value: total leads in list
  },
]

const leads = [
  {
    id: 1,
    name: 'Samsung',
    amount: 100000,
    rank: 4,
    primaryNote: 'On competitor',
    secondaryNote: 'Up for renewal in Jan',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/1/20',
    forecast: 'Feeling Lucky',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 2,
    name: 'Tesla',
    amount: 100000,
    rank: 3,
    primaryNote: 'New director of marketing',
    secondaryNote: 'has budget',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Ready',
    lastUpdateDate: '3/2/20',
    forecast: 'NA',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 3,
    name: 'Boston University',
    amount: 100000,
    rank: 3,
    primaryNote: 'Using competitor',
    secondaryNote: 'up for renewal in March',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Ready',
    lastUpdateDate: '3/3/20',
    forecast: 'NA',
    listId: 3,
    // related value: lead has many notes
  },
  {
    id: 4,
    name: 'Georgia Pacific',
    amount: 100000,
    rank: 4,
    primaryNote: 'Was interested last year',
    secondaryNote: 'Q2 is when they buy',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/4/20',
    forecast: 'Strong',
    listId: 4,
    // related value: lead has many notes
  },
  {
    id: 5,
    name: 'Delta Airlines',
    amount: 100000,
    rank: 4,
    primaryNote: 'May not need but have a lot of money',
    secondaryNote: null,
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Waiting',
    lastUpdateDate: '3/5/20',
    forecast: 'Feeling Lucky',
    listId: 5,
    // related value: lead has many notes
  },
  {
    id: 6,
    name: 'Emory University',
    amount: 100000,
    rank: 3,
    primaryNote: 'Launched a sales team for MBA program!',
    secondaryNote: null,
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Waiting',
    lastUpdateDate: '3/6/20',
    forecast: 'Feeling Lucky',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 7,
    name: 'Salesforce',
    amount: 100000,
    rank: 5,
    primaryNote: 'Competitor, tricky..',
    secondaryNote: 'could be good for their new ES team',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/7/20',
    forecast: 'Strong',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 8,
    name: 'Oracle',
    amount: 100000,
    rank: 5,
    primaryNote: 'Competitor, tricky..',
    secondaryNote: 'could be good for their new ES team',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Trial',
    lastUpdateDate: '3/8/20',
    forecast: 'NA',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 9,
    name: 'Amazon Web Services',
    amount: 100000,
    rank: 5,
    primaryNote: 'On competitor',
    secondaryNote: 'Up for renewal in Jan',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/9/20',
    forecast: 'Future',
    listId: 2,
    // related value: lead has many notes
  },
  {
    id: 10,
    name: 'LinkedIn',
    amount: 100000,
    rank: 5,
    primaryNote: 'New director of marketing',
    secondaryNote: 'has budget',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Ready',
    lastUpdateDate: '3/10/20',
    forecast: 'NA',
    listId: 2,
    // related value: lead has many notes
  },
  {
    id: 11,
    name: 'Slack',
    amount: 100000,
    rank: 5,
    primaryNote: 'Using competitor',
    secondaryNote: 'up for renewal in March',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/11/20',
    forecast: 'NA',
    listId: 3,
    // related value: lead has many notes
  },
  {
    id: 12,
    name: 'Tableau',
    amount: 100000,
    rank: 5,
    primaryNote: 'Was interested last year',
    secondaryNote: 'Q2 is when they buy',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Ready',
    lastUpdateDate: '3/12/20',
    forecast: 'NA',
    listId: 3,
    // related value: lead has many notes
  },
  {
    id: 13,
    name: 'Zoom',
    amount: 100000,
    rank: 5,
    primaryNote: 'May not need but have a lot of money',
    secondaryNote: null,
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/13/20',
    forecast: 'Verbal',
    listId: 3,
    // related value: lead has many notes
  },
  {
    id: 14,
    name: 'Uber',
    amount: 100000,
    rank: 4,
    primaryNote: 'Launched a sales team for MBA program!',
    secondaryNote: null,
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Demo',
    lastUpdateDate: '3/14/20',
    forecast: 'Strong',
    listId: 1,
    // related value: lead has many notes
  },
  {
    id: 15,
    name: "Mike's Pastry",
    amount: 100000,
    rank: 5,
    primaryNote: 'Competitor, tricky..',
    secondaryNote: 'could be good for their new ES team',
    // computed value: description, by concatenating primaryNote + secondaryNote
    status: 'Waiting',
    lastUpdateDate: '3/15/20',
    forecast: 'Strong',
    listId: 5,
    // related value: lead has many notes
  },
]

const notes = [
  {
    id: 1,
    leadId: 1,
    content: 'Call went well, speaking next week',
    // date ?
  },
  {
    id: 2,
    leadId: 2,
    content: 'No answer, try again later today',
    // date ?
  },
  {
    id: 3,
    leadId: 3,
    content: 'Scheduled a call for next Monday at 3pm',
    // date ?
  },
  {
    id: 4,
    leadId: 4,
    content: 'Need to circle back next week',
    // date ?
  },
  {
    id: 5,
    leadId: 5,
    content: 'Was told NO, but open to seeing an email to learn more',
    // date ?
  },
  {
    id: 6,
    leadId: 6,
    content: 'Out of office due to Corona Virus :/',
    // date ?
  },
  {
    id: 7,
    leadId: 7,
    content: 'Not the right contact, find a new POC',
    // date ?
  },
  {
    id: 8,
    leadId: 8,
    content: 'Call went well, speaking next week',
    // date ?
  },
  {
    id: 9,
    leadId: 9,
    content: 'No answer, try again later today',
    // date ?
  },
  {
    id: 10,
    leadId: 10,
    content: 'Scheduled a call for next Monday at 3pm',
    // date ?
  },
  {
    id: 11,
    leadId: 11,
    content: 'Need to circle back next week',
    // date ?
  },
  {
    id: 12,
    leadId: 12,
    content: 'Was told NO, but open to seeing an email to learn more',
    // date ?
  },
  {
    id: 13,
    leadId: 13,
    content: 'Will be moving forward!',
    // date ?
  },
  {
    id: 14,
    leadId: 14,
    content: 'Looking good, need another call next week with the team',
    // date ?
  },
  {
    id: 15,
    leadId: 15,
    content: 'Call went well, speaking next week',
    // date ?
  },
]

const contacts = [
  {
    id: 1,
    name: 'John Edsik',
    phone: '202-123-1234',
    email: 'john@samsung.com',
    leadId: 1,
  },
  {
    id: 2,
    name: 'Mike Grod',
    phone: '313-435-9956',
    email: 'mike@telsa.com',
    leadId: 2,
  },
  {
    id: 3,
    name: 'Kendra Sipp',
    phone: null,
    email: 'ksipp@uber.com',
    leadId: 14,
  },
  {
    id: 4,
    name: 'Laura Wagne',
    phone: null,
    email: 'lw@mikespastry.com',
    leadId: 15,
  },
  {
    id: 5,
    name: 'Steven Dasher',
    phone: null,
    email: 'stevend@linkedin.com',
    leadId: 10,
  },
  {
    id: 6,
    name: 'Rachel Shevsky',
    phone: null,
    email: 'rachel.shevsky@oracle.com',
    leadId: 8,
  },
]

/**
 * Given a lead object, produce a serialized lead (new object) that includes contacts and notes
 * @param {lead} - Object
 * @returns {Object} - serialized lead
 */
function serializeLead(lead) {
  // lead has notes and contacts
  let leadCopy = JSON.parse(JSON.stringify(lead))
  let leadContacts = contacts.filter(contact => contact.leadId === leadCopy.id)
  let copyOfLeadContacts = JSON.parse(JSON.stringify(leadContacts))
  let leadNotes = notes.filter(note => note.leadId === leadCopy.id)
  let copyOfLeadNotes = JSON.parse(JSON.stringify(leadNotes))
  leadCopy.contacts = copyOfLeadContacts
  leadCopy.notes = copyOfLeadNotes
  return leadCopy
}

/**
 * Given a list object, produce a serialized list (new object) that includes leads
 * @param {list} - Object
 * @returns {Object} - serialized list
 */
function serializeList(list) {
  // list has leads, lead has notes and contacts
  let copy = JSON.parse(JSON.stringify(list))
  let relatedLeads = leads.filter(lead => lead.listId === list.id)
  let serializedLeads = relatedLeads.map(serializeLead)
  copy.leads = serializedLeads
  return copy
}

/**
 * Simulate a GET request that returns a collection of Lists for current user, each List is serialized with related data
 * @returns {Array} - serialized Lists
 */
export function getSerializedLists() {
  return lists.map(serializeList)
}
