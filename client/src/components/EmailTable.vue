<template>
  <div class="email-tracking">
    <table>
      <thead>
        <tr style="position: relative">
          <th style="cursor: pointer; d" v-resizableColumn @click="sortBy('subject')">
            Email

            <img
              v-if="sortKey === 'subject' && sortOrder === -1"
              src="@/assets/images/arrowDrop.svg"
              height="14px"
              alt=""
            />

            <img
              v-else-if="sortKey === 'subject' && sortOrder !== -1"
              src="@/assets/images/arrowDropUp.svg"
              height="14px"
              alt=""
            />

            <div class="resizer"></div>
          </th>
          <th
            v-resizableColumn
            v-for="(value, key) in statsKeys"
            :key="key"
            @click="sortBy(value.charAt(0).toLowerCase() + value.slice(1))"
          >
            {{ value }}

            <img
              v-if="sortKey === value.charAt(0).toLowerCase() + value.slice(1) && sortOrder === -1"
              src="@/assets/images/arrowDrop.svg"
              height="14px"
              alt=""
            />

            <img
              v-else-if="
                sortKey === value.charAt(0).toLowerCase() + value.slice(1) && sortOrder !== -1
              "
              src="@/assets/images/arrowDropUp.svg"
              height="14px"
              alt=""
            />
            <div class="resizer"></div>
          </th>
          <th style="cursor: pointer" v-resizableColumn @click="sortBy('lastActivity')">
            Last Activity
            <img
              v-if="sortKey === 'lastActivity' && sortOrder === -1"
              src="@/assets/images/arrowDrop.svg"
              height="14px"
              alt=""
            />

            <img
              v-else-if="sortKey === 'lastActivity' && sortOrder !== -1"
              src="@/assets/images/arrowDropUp.svg"
              height="14px"
              alt=""
            />
            <div class="resizer"></div>
          </th>
        </tr>
      </thead>
      <tbody v-if="sortedEmails">
        <tr v-for="email in sortedEmails" :key="email.body">
          <td>
            <div class="email-details">
              <!-- <div style="width: 40px">
                <div :tool-tip="email.recipient" class="initials-bubble tooltip">
                  {{ email.recipient[0].toUpperCase() }}
                </div>
              </div> -->

              <div class="email-info">
                <div class="subject">
                  {{ email.subject }}
                </div>
                <div class="email">{{ email.body.replace(/<[^>]*>/g, '') }}</div>
              </div>
            </div>
            <div class="blur"></div>
          </td>
          <td>{{ email.recipient }}</td>
          <td>{{ email.failed ? 'Failed' : 'Delivered' }}</td>
          <td>{{ email.opens }}</td>
          <td>{{ email.clicks }}</td>
          <td>{{ email.replies }}</td>
          <td>
            <div>
              <div class="base-font" style="margin-bottom: 4px">
                {{
                  email.activity_log[0].split('|')[0].charAt(0).toUpperCase() +
                  email.activity_log[0].split('|')[0].slice(1)
                }}
              </div>

              <div style="color: gray; font-size: 15px">
                {{ formatActivityLog(email.activity_log[0]) }}
              </div>
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-else>
        <div class="loading">
          Generating
          <div style="margin-left: 12px" class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </tbody>
    </table>
  </div>
</template>

<script>
import { Comms } from '@/services/comms'

export default {
  name: 'EmailTable',
  data() {
    return {
      emails: [],
      sortKey: '',
      sortOrder: 1,
      statsKeys: ['To', 'Status', 'Opens', 'Clicks', 'Replies'],
    }
  },
  props: {
    searchText: {},
    failedFilter: {
      type: Boolean,
      default: null,
    },
    activityFilter: {
      default: null,
    },
    userId: {
      default: null,
    },
  },
  computed: {
    sortedEmails() {
      let filteredEmails = this.emails.filter((email) => {
        const searchText = this.searchText.toLowerCase()
        const failedFilter = this.failedFilter !== undefined ? this.failedFilter : null
        const activityFilter = this.activityFilter !== undefined ? this.activityFilter : null
        const userFilter = this.userId !== undefined ? this.userId : null

        const searchConditions = [
          email.recipient.toLowerCase().includes(searchText),
          email.subject.toLowerCase().includes(searchText),
          email.body.toLowerCase().includes(searchText),
          email.opens.toString().includes(searchText),
          email.replies.toString().includes(searchText),
          email.clicks.toString().includes(searchText),
          email.activity_log[0].includes(searchText),
          searchText.includes('delivered') && !email.failed,
          searchText.includes('failed') && email.failed,
        ]

        const filterConditions = []

        if (userFilter !== null) {
          filterConditions.push(email.user === userFilter)
        }

        if (failedFilter !== null) {
          filterConditions.push(email.failed === failedFilter)
        }

        if (activityFilter !== null) {
          const [start, end] = activityFilter.split(',')
          const startDate = new Date(start)
          const endDate = new Date(end)
          const emailDate = new Date(email.activity_log[0].split('|')[1])
          filterConditions.push(emailDate >= startDate && emailDate <= endDate)
        }

        return (
          searchConditions.some((condition) => condition) &&
          filterConditions.every((condition) => condition)
        )
      })

      if (!this.sortKey) return filteredEmails

      return filteredEmails.slice().sort((a, b) => {
        const aValue =
          this.sortKey === 'lastActivity'
            ? new Date(a.activity_log[0].split('|')[1])
            : this.sortKey === 'to'
            ? a.recipient
            : this.sortKey === 'status'
            ? a.failed
            : a[this.sortKey]
        //   this.sortKey === 'subject' ? a.subject : new Date(a.activity_log[0].split('|')[1])
        const bValue =
          this.sortKey === 'lastActivity'
            ? new Date(b.activity_log[0].split('|')[1])
            : this.sortKey === 'to'
            ? b.recipient
            : this.sortKey === 'status'
            ? b.failed
            : b[this.sortKey]
        //    b[this.sortKey]
        //   this.sortKey === 'subject' ? b.subject : new Date(b.activity_log[0].split('|')[1])
        if (aValue < bValue) return -1 * this.sortOrder
        if (aValue > bValue) return 1 * this.sortOrder

        return 0
      })
    },
  },
  created() {
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
        const response = await Comms.api.getTrackedEmails()
        // console.log(response.trackers)
        this.emails = response.trackers
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

      //   return `${action.charAt(0).toUpperCase() + action.slice(1)} - ${formattedTime}`
      return formattedTime
    },
    // getInitials(name) {
    //   return name
    //     .split(' ')
    //     .map((n) => n[0])
    //     .join('')
    // },
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

  @keyframes bounce {
    0%,
    80%,
    100% {
      transform: scale(0);
      opacity: 0;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }

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
      overflow: hidden;
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
        margin-right: 12px;
        font-size: 16px;
        padding: 5px 9px;
      }

      .email-info {
        display: flex;
        flex-direction: column;
        flex-grow: 1;

        .subject {
          font-family: $base-font-family;
          margin-bottom: 4px;
        }

        .email {
          color: gray;
          font-family: $thin-font-family;
          font-size: 15px;
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

    .relative {
      position: relative;
    }

    .dropdown {
      position: absolute;
      top: 48px;
      border: 1px solid rgba(0, 0, 0, 0.1);
      padding: 8px;
      left: 4px;
      z-index: 4;
      width: 96%;
      min-height: 100px;
      background-color: white;
      border-radius: 4px;
      box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);

      .dropdown-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        img {
          margin-right: 8px;
        }
      }

      .dropdown-body {
        padding: 0 8px;
      }

      .dropdown-footer {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding: 8px;
      }
    }

    .base-font {
      font-family: $base-font-family;
    }

    .dot {
      width: 4px;
      height: 4px;
      margin: 0 6px;
      background: rgb(97, 96, 96);
      border-radius: 50%;
      animation: bounce 1.2s infinite ease-in-out;
    }

    .dot:nth-child(2) {
      animation-delay: -0.4s;
    }

    .dot:nth-child(3) {
      animation-delay: -0.2s;
    }

    .loading {
      display: flex;
      align-items: center;
      border-radius: 6px;
      margin-left: 16px;
      padding: 1.5rem 0;

      p {
        margin-right: 8px;
      }
    }
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
