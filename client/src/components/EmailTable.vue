<template>
  <div class="email-tracking">
    <Modal v-if="emailModalOpen" class="paid-modal">
      <div class="regen-container">
        <div style="background-color: white" class="paid-header sticky-header">
          <div>
            <h3 class="regen-header-title">{{ selectedEmail.subject }}</h3>
          </div>

          <img
            style="cursor: pointer"
            @click="toggleEmailModal"
            src="@/assets/images/close.svg"
            height="18px"
            alt=""
          />
        </div>

        <div class="paid-body">
          <!-- <h4>Activities</h4> -->
          <pre class="pre-text" v-html="selectedEmail.body"></pre>
        </div>

        <div style="padding-top: 1rem" class="flex-end sticky-bottom">
          <div
            style="padding-top: 9px; padding-bottom: 9px"
            class="cancel-button"
            @click="toggleEmailModal"
          >
            Close
          </div>
        </div>
      </div>
    </Modal>
    <Modal v-if="activityModalOpen" class="paid-modal">
      <div class="regen-container">
        <div style="background-color: white" class="paid-header sticky-header">
          <div>
            <h3 class="regen-header-title">{{ selectedEmail.subject }}</h3>
          </div>

          <img
            style="cursor: pointer"
            @click="toggleActivityModal"
            src="@/assets/images/close.svg"
            height="18px"
            alt=""
          />
        </div>

        <div class="paid-body">
          <h4>Activities</h4>
          <p class="paid-item" v-for="(activity, i) in selectedEmail.activity_log" :key="i">
            {{ formatActivityLog(activity, true) }}
          </p>
        </div>

        <div style="padding-top: 1rem" class="flex-end sticky-bottom">
          <div
            style="padding-top: 9px; padding-bottom: 9px"
            class="cancel-button"
            @click="toggleActivityModal"
          >
            Close
          </div>
        </div>
      </div>
    </Modal>
    <table>
      <thead>
        <tr style="position: relative">
          <th v-resizableColumn @click="sortBy('subject')">
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
            <div class="stat" v-if="value === 'Opens' && openRate && userId === user.id">
              <span
                :class="{
                  red: openRate <= 30,
                  yellow: openRate > 30 && openRate < 70,
                  green: openRate >= 70,
                }"
                >{{ openRate }}%</span
              >
            </div>
            <!-- <div class="stat" v-else-if="value === 'Replies' && replyRate && userId === user.id">
              <span
                :class="{
                  red: replyRate <= 30,
                  yellow: replyRate > 30 && replyRate < 70,
                  green: replyRate >= 70,
                }"
                >{{ replyRate }}%</span
              >
            </div> -->
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
          <th class="mobile-width" v-resizableColumn @click="sortBy('lastActivity')">
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
      <tbody v-if="sortedEmails.length">
        <tr v-show="emailDrafts.length" v-for="(email, i) in emailDrafts" :key="i">
          <td
            :class="i % 2 !== 0 ? 'gray-bg' : ''"
            style="cursor: zoom-in"
            @click="toggleEmailModal(email)"
          >
            <div class="email-details">
              <div class="email-info">
                <div class="subject">
                  {{ email.subject }}
                </div>
                <div class="email">{{ email.body.replace(/<[^>]*>/g, '') }}</div>
              </div>
            </div>
            <div class="blur"></div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''" class="set-width">
            <div style="margin-bottom: 4px; font-size: 14px">
              {{ email.name }}
            </div>
            <div style="color: #808080; font-size: 14px">
              {{ email.recipient }}
            </div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div class="turqbox">
              {{ email.status }}
            </div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">0</td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">0</td>
          <td class="mobile-width" :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div>
              <div style="margin-bottom: 4px; font-size: 14px">
                {{
                  email.activity_log.at(-1).split('|')[0].charAt(0).toUpperCase() +
                  email.activity_log.at(-1).split('|')[0].slice(1)
                }}
              </div>
              <div style="color: #808080; font-size: 14px">
                {{ formatActivityLog(email.activity_log.at(-1)) }}
              </div>
            </div>
          </td>
        </tr>

        <tr v-for="(email, i) in sortedEmails" :key="i">
          <td
            :class="i % 2 !== 0 ? 'gray-bg' : ''"
            style="cursor: zoom-in"
            @click="toggleEmailModal(email)"
          >
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
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''" class="set-width">
            <div style="margin-bottom: 4px; font-size: 14px">
              {{ email.name }}
            </div>
            <div style="color: #808080; font-size: 14px">
              {{ email.recipient }}
            </div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div :class="{ redbox: email.failed, greenbox: !email.failed }">
              {{ email.failed ? 'Failed' : 'Delivered' }}
            </div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.opens }}</td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.clicks }}</td>
          <!-- <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.replies }}</td> -->
          <!-- @click="toggleActivityModal(email)" style="cursor: zoom-in"-->
          <td class="mobile-width" :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div>
              <!-- background-color: #fafafa;
                  padding: 2px 6px;
                  border: 0.5px solid rgba(0, 0, 0, 0.1);
                  width: fit-content;
                  border-radius: 8px; -->
              <div style="margin-bottom: 4px; font-size: 14px">
                {{
                  email.activity_log.at(-1).split('|')[0].charAt(0).toUpperCase() +
                  email.activity_log.at(-1).split('|')[0].slice(1)
                }}
              </div>

              <div style="color: #808080; font-size: 14px">
                {{ formatActivityLog(email.activity_log.at(-1)) }}
              </div>
            </div>
          </td>
        </tr>
      </tbody>
      <tbody v-else>
        <div v-if="loading" class="loading">
          Generating
          <div style="margin-left: 12px" class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>

        <div class="mobile-text" style="margin: 16px" v-else>
          Your tracked emails
          <span>
            <img style="margin-right: 4px" src="@/assets/images/email.svg" height="12px" alt="" />
            will appear here.</span
          >
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
      statsKeys: ['To', 'Status', 'Opens', 'Clicks'],
      openRate: 0,
      replyRate: 0,
      emailModalOpen: false,
      activityModalOpen: false,
      selectedEmail: null,
      loading: false,
      emailDrafts: [],
    }
  },
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
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
          email.name.toLowerCase().includes(searchText),
          email.body.toLowerCase().includes(searchText),
          email.opens.toString().includes(searchText),
          email.replies.toString().includes(searchText),
          email.clicks.toString().includes(searchText),
          email.activity_log.at(-1).includes(searchText),
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
          const emailDate = new Date(email.activity_log.at(-1).split('|')[1])
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
            ? new Date(a.activity_log.at(-1).split('|')[1])
            : this.sortKey === 'to'
            ? a.recipient
            : this.sortKey === 'status'
            ? a.failed
            : a[this.sortKey]
        //   this.sortKey === 'subject' ? a.subject : new Date(a.activity_log.at(-1).split('|')[1])
        const bValue =
          this.sortKey === 'lastActivity'
            ? new Date(b.activity_log.at(-1).split('|')[1])
            : this.sortKey === 'to'
            ? b.recipient
            : this.sortKey === 'status'
            ? b.failed
            : b[this.sortKey]
        //    b[this.sortKey]
        //   this.sortKey === 'subject' ? b.subject : new Date(b.activity_log.at(-1).split('|')[1])
        if (aValue < bValue) return -1 * this.sortOrder
        if (aValue > bValue) return 1 * this.sortOrder

        return 0
      })
    },
    user() {
      return this.$store.state.user
    },
  },
  created() {
    this.fetchEmails()
  },
  watch: {
    sortedEmails(newValue) {
      this.$emit('emails-updated', newValue)
    },
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
    test() {
      console.log(this.sortedEmails)
    },
    toggleEmailModal(email = null) {
      this.emailModalOpen = !this.emailModalOpen
      this.selectedEmail = email
    },
    toggleActivityModal(email = null) {
      this.activityModalOpen = !this.activityModalOpen
      this.selectedEmail = email
    },
    async fetchEmails() {
      try {
        const response = await Comms.api.getTrackedEmails()
        this.emails = response.results
        // this.openRate = Math.round(response.rates.open_rate)
        // this.replyRate = response.rates.reply_rate
      } catch (error) {
        console.error('Error fetching email data:', error)
      }
    },
    formatActivityLog(logEntry, fullEntry = false) {
      const [action, dateTime] = logEntry.split('|')
      const date = new Date(dateTime)
      const now = new Date()
      const diffInMilliseconds = now - date
      const diffInMinutes = Math.floor(diffInMilliseconds / (1000 * 60))
      const diffInHours = Math.floor(diffInMilliseconds / (1000 * 60 * 60))
      const diffInDays = Math.floor(diffInMilliseconds / (1000 * 60 * 60 * 24))

      let formattedTime
      if (diffInMinutes < 120) {
        formattedTime = `${diffInMinutes - 60} minute${diffInMinutes - 60 !== 1 ? 's' : ''} ago`
      } else if (diffInHours < 24) {
        formattedTime = `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`
      } else if (diffInDays < 30) {
        formattedTime = `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`
      } else {
        const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(
          date.getFullYear(),
        ).slice(-2)}`
        formattedTime = `on ${formattedDate}`
      }

      if (fullEntry) {
        return `${action.charAt(0).toUpperCase() + action.slice(1)} - ${formattedTime}`
      } else {
        return formattedTime
      }
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
@import '@/styles/buttons';

.gray-bg {
  background-color: $off-white !important;
}

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

  @keyframes fadeIn {
    to {
      opacity: 1;
    }
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;

    tr {
      transition: opacity 1s ease-out;
      opacity: 0;
      animation: fadeIn 1s forwards;
    }

    th,
    td {
      padding: 12px;
      font-size: 15px;
      text-align: left;
      // border-bottom: 1px solid #ddd;
      position: relative;

      .subject,
      .email {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      @media only screen and (max-width: 600px) {
        font-size: 12px;
      }
    }

    thead {
      position: sticky;
      top: 0;
      z-index: 8;
    }

    th {
      background-color: $off-white;
      // font-family: $base-font-family;
      border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
      color: $dark-blue;
      cursor: pointer;
    }

    td {
      z-index: 1;
      background-color: white;
      overflow: hidden;
    }

    .set-width {
      min-width: 10vw;
      width: 12vw;
    }

    .email-details {
      display: flex;
      align-items: center;
      z-index: 0;
      min-width: 10vw;
      width: 12vw;

      .email-info {
        display: flex;
        flex-direction: column;
        flex-grow: 1;

        .subject {
          font-family: $base-font-family;
          margin-bottom: 4px;
          font-weight: 200;
          font-size: 14px;
          line-height: 24px;
        }

        .email {
          color: gray;
          font-family: $thin-font-family;
          font-size: 14px;
        }
      }
    }

    // .tooltip {
    //   position: relative;
    //   cursor: pointer;

    //   &::before {
    //     content: attr(tool-tip);
    //     position: absolute;
    //     top: 16px;
    //     left: 40px;
    //     transform: translateY(-50%);
    //     background-color: $dark-black-blue;
    //     color: white;
    //     padding: 5px;
    //     border-radius: 3px;
    //     white-space: nowrap;
    //     opacity: 0;
    //     pointer-events: none;
    //     transition: opacity 0.4s;
    //     z-index: 3;
    //   }

    //   &:hover::before {
    //     opacity: 1;
    //   }
    // }

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
      background: rgba(255, 255, 255, 0.569);
      filter: blur(8px);
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
      font-weight: 200;
      line-height: 24px;
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

    .stat {
      position: absolute;
      right: 4px;
      top: 14px;
      font-family: $base-font-family;
      font-size: 10px;

      span {
        font-size: 12px;
        padding: 4px 6px;
        border-radius: 11px;
      }

      .red {
        color: $pinky !important;
      }

      .yellow {
        color: $turq !important;
      }

      .green {
        color: $lite-blue !important;
      }
    }
  }

  .redbox {
    background-color: $lite-pink !important;
    color: $pinky !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
    width: fit-content;
  }

  .greenbox {
    background-color: $light-purple !important;
    color: $graper !important;
    font-family: $base-font-family;
    font-size: 12px;
    padding: 6px 12px;
    border-radius: 16px;
    width: fit-content;
  }

  .pre-text {
    color: $base-gray;
    font-family: $thin-font-family;
    font-size: 16px;
    line-height: 32px;
    word-wrap: break-word;
    white-space: pre-wrap;
  }

  .regen-modal {
    margin-top: 84px;
  }
  .paid-modal {
    margin-top: 132px;
    font-family: $thin-font-family;
  }
  .regen-container {
    width: 500px;
    max-height: 500px;
    position: relative;
    overflow-y: scroll;
    font-family: $thin-font-family;

    @media only screen and (max-width: 600px) {
      font-size: 13px !important;
      width: 100% !important;
    }

    @media only screen and (min-width: 601px) and (max-width: 1024px) {
    }
  }

  .paid-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }
  .sticky-header {
    position: sticky;
    top: 0;
  }

  .paid-item {
    opacity: 0.7;
  }

  .paid-center {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
}

.paid-body {
  margin: 0.5rem 0;
  max-height: 350px;
  overflow: scroll;
}

.paid-body::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.paid-body::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.email-container {
  max-height: 250px !important;
  overflow: scroll;
}

.flex-end {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}

.sticky-bottom {
  position: sticky;
  bottom: 0;
  background: white;
}

.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}

.mobile-text {
  font-size: 13px;
}

.mobile-width {
  // width: 15vw;
  @media only screen and (max-width: 600px) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

::v-deep .modal {
  @media only screen and (max-width: 600px) {
    // width: 90%;
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
