<template>
  <div class="email-tracking">
    <table>
      <thead>
        <tr style="position: relative">
          <th v-resizableColumn @click="sortBy('subject')">
            Email
            <div class="resizer"></div>
          </th>
          <th v-resizableColumn v-for="(value, key) in statsKeys" :key="key">
            {{ value }}
            <div class="resizer"></div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="email in sortedEmails" :key="email.body">
          <td>
            <div class="email-details">
              <div :tool-tip="email.recipient" class="initials-bubble tooltip">
                {{ getInitials(email.recipient) }}
              </div>
              <div class="email-info">
                <div class="subject">
                  {{ email.subject }}
                </div>
                <div class="email">
                  {{ email.body }}
                </div>
              </div>
            </div>
            <div class="blur"></div>
          </td>
          <td>{{ email.recieved ? 'Delivered' : 'Failed' }}</td>
          <td>{{ email.opens }}</td>
          <td>{{ email.clicks }}</td>
          <td>{{ email.replies }}</td>
          <td>{{ formatActivityLog(email.activityLog[0]) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'EmailTable',
  data() {
    return {
      emails: [],
      sortKey: '',
      sortOrder: 1,
      statsKeys: ['Status', 'Opens', 'Clicks', 'Replies', 'Last Activity'],
    }
  },
  props: {
    searchText: {},
  },
  computed: {
    sortedEmails() {
      // Filter emails based on the searchText
      const filteredEmails = this.emails.filter((email) => {
        const searchText = this.searchText.toLowerCase()
        return (
          email.recipient.toLowerCase().includes(searchText) ||
          email.subject.toLowerCase().includes(searchText) ||
          email.body.toLowerCase().includes(searchText) ||
          email.opens.toString().includes(searchText) ||
          email.replies.toString().includes(searchText) ||
          email.clicks.toString().includes(searchText)
          // ||  email.received.toString().toLowerCase().includes(searchText) ||
          //   email.failed.toString().toLowerCase().includes(searchText)
        )
      })

      // Sort the filtered emails
      if (!this.sortKey) return filteredEmails

      return filteredEmails.slice().sort((a, b) => {
        const aValue = this.sortKey === 'subject' ? a.subject : new Date(a.replies)
        const bValue = this.sortKey === 'subject' ? b.subject : new Date(b.replies)

        if (aValue < bValue) return -1 * this.sortOrder
        if (aValue > bValue) return 1 * this.sortOrder
        return 0
      })
    },
  },
  mounted() {
    this.fetchEmails()
  },
  directives: {
    resizableColumn: {
      bind(el) {
        let startWidth = 0
        let startMouseX = 0
        const minWidth = 75 // Set a reasonable minimum width

        el.addEventListener('mousedown', (e) => {
          if (e.target.classList.contains('resizer')) {
            startWidth = el.offsetWidth
            startMouseX = e.clientX
            document.addEventListener('mousemove', onMouseMove)
            document.addEventListener('mouseup', onMouseUp)
            e.preventDefault()
          }
        })

        function onMouseMove(e) {
          const widthDiff = e.clientX - startMouseX
          const newWidth = startWidth + widthDiff
          if (newWidth > minWidth) {
            el.style.width = `${newWidth}px`
          }
        }

        function onMouseUp() {
          document.removeEventListener('mousemove', onMouseMove)
          document.removeEventListener('mouseup', onMouseUp)
        }
      },
    },
  },

  methods: {
    async fetchEmails() {
      try {
        // const response = await axios.get('API_ENDPOINT')
        // this.emails = response.data
        this.emails = [
          {
            recipient: 'Journalisticlylongname Guysnameislongashell',
            subject: 'Hey journalist guy',
            body: 'Hi journalist guy, im emailing you about nothing. Just testing out this table real quick.',
            recieved: true,
            opens: 3,
            replies: 1,
            clicks: 7,
            failed: false,
            recieved: true,
            activityLog: [
              'sent|2024-06-03T12:23:10.867366',
              'opened|2024-06-03T13:13:08.360252',
              'opened|2024-06-03T13:13:08.374611',
              'opened|2024-06-03T13:13:51.934088',
            ],
          },
          {
            recipient: 'Adam Eve',
            subject: 'Search filters',
            body: 'Hi Adam, im testing the search filter',
            recieved: true,
            opens: 5,
            replies: 2,
            clicks: 9,
            failed: false,
            recieved: true,
            activityLog: [
              'sent|2024-06-03T12:23:10.867366',
              'opened|2024-06-03T13:13:08.360252',
              'opened|2024-06-03T13:13:08.374611',
              'opened|2024-06-03T13:13:51.934088',
            ],
          },
        ]
      } catch (error) {
        console.error('Error fetching email data:', error)
      }
    },
    formatActivityLog(logEntry) {
      const [action, dateTime] = logEntry.split('|')
      const date = new Date(dateTime)
      const now = new Date()
      const diffInMilliseconds = now - date
      const diffInHours = Math.floor(diffInMilliseconds / (1000 * 60 * 60))
      const diffInDays = Math.floor(diffInMilliseconds / (1000 * 60 * 60 * 24))

      let formattedTime
      if (diffInHours < 24) {
        formattedTime = `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`
      } else if (diffInDays < 30) {
        formattedTime = `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`
      } else {
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(
          date.getFullYear(),
        ).slice(-2)}`
        formattedTime = `on ${formattedDate}`
      }

      return `${action.charAt(0).toUpperCase() + action.slice(1)} - ${formattedTime}`
    },
    getInitials(name) {
      return name
        .split(' ')
        .map((n) => n[0])
        .join('')
    },
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortOrder *= -1
      } else {
        this.sortKey = key
        this.sortOrder = 1
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.email-tracking {
  width: 100%;
  font-family: $thin-font-family;

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;

    th,
    td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ddd;
      position: relative;

      .subject,
      .email {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    th {
      background-color: white;
      position: sticky;
      top: 0;
      z-index: 5;
    }

    td {
      z-index: 1;
      background-color: white;
      cursor: pointer;
    }

    .email-details {
      display: flex;
      align-items: center;
      z-index: 0;
      min-width: 10vw;
      width: 20vw;

      .initials-bubble {
        border-radius: 50%;
        background-color: $soft-gray;
        color: $dark-black-blue;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-size: 14px;
        padding: 10px;
      }

      .email-info {
        display: flex;
        flex-direction: column;
        flex-grow: 1;

        .subject {
          font-family: $base-font-family;
        }

        .email {
          color: gray;
        }
      }
    }

    .tooltip {
      position: relative;
      cursor: pointer;

      &::before {
        content: attr(tool-tip);
        position: absolute;
        top: 16px;
        left: 40px;
        transform: translateY(-50%);
        background-color: $dark-black-blue;
        color: white;
        padding: 5px;
        border-radius: 3px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.4s;
        z-index: 3;
      }

      &:hover::before {
        opacity: 1;
      }
    }

    .resizer {
      width: 10px;
      cursor: col-resize;
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
    }

    .resizer:hover {
      border-right: 1.5px solid $darker-blue;
    }

    .blur {
      width: 12px;
      background: white; /* adjust the color and opacity to your liking */
      filter: blur(5px);
      cursor: none;
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
    }

    // .actions-header {
    //   display: flex;
    //   align-items: center;
    //   justify-content: space-between;
    // }
  }
}

/* Responsive styles */
@media (max-width: 768px) {
  .email-tracking {
    padding: 10px;

    table {
      th,
      td {
        padding: 8px;
      }
    }
  }
}

@media (max-width: 480px) {
  .email-tracking {
    h1 {
      font-size: 1.5rem;
    }

    table {
      th,
      td {
        padding: 6px;
      }

      .initials-bubble {
        width: 30px;
        height: 30px;
        font-size: 14px;
      }
    }
  }
}
</style>
