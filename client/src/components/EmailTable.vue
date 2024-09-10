<template>
  <div class="email-tracking">
    <Modal v-if="emailModalOpen" class="paid-modal">
      <div class="regen-container">
        <div style="background-color: white" class="paid-header sticky-header">
          <div>
            <h3 class="regen-header-title bold-font">{{ selectedEmail.subject }}</h3>
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
            style="padding-top: 9px; padding-bottom: 9px; margin-right: 4px"
            class="secondary-button"
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
            class="secondary-button"
            @click="toggleActivityModal"
          >
            Close
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="draftEmailModalOpen" class="regen-modal">
      <div style="width: 55vw; min-width: 500px" class="regen-container">
        <div style="background-color: white; z-index: 1000" class="paid-header">
          <div class="space-between">
            <h2>Email Draft</h2>

            <!-- <p style="margin-right: 8px">
              {{ selectedEmail.name }}
            </p> -->
            <div class="row">
              <button
                :disabled="loadingDraft"
                @click="updateDraft(false, true, 'Rejected', false)"
                class="secondary-button pinker"
                style="margin-right: 8px"
              >
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/close.svg"
                  height="14px"
                  alt=""
                />
                Reject
              </button>

              <button
                :disabled="loadingDraft"
                @click="updateDraft(true, false, 'Approved', false)"
                class="secondary-button teal"
                style="margin-right: 8px"
              >
                <img
                  style="margin-right: 4px"
                  src="@/assets/images/check.svg"
                  height="12px"
                  alt=""
                />
                Approve
              </button>
            </div>
          </div>
        </div>

        <div style="margin-bottom: 8px; overflow: hidden; height: 400px" class="paid-body">
          <div style="position: relative">
            <!-- <div class="row">
              <div
                class="rowed"
                style="
                  padding-bottom: 12px;
                  border-bottom: 1px solid rgba(0, 0, 0, 0.135);
                  width: 100%;
                "
              >
                <p style="margin: 0; padding: 0; font-size: 18px; margin-right: 8px">From:</p>

                <p class="e-container" style="margin: 0">{{ user.email }}</p>
              </div>
            </div> -->

            <div style="position: relative">
              <p
                style="
                  margin: 0 8px 0 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 20px;
                "
                class="bold-font"
              >
                To:
              </p>
              <input
                style="margin-bottom: 0; padding-left: 26px; padding-top: 6px"
                class="primary-input-underline"
                v-model="targetEmail"
                type="email"
              />
              <!-- <input
                v-else
                style="margin-bottom: 0; padding-left: 26px"
                class="primary-input-underline"
                type="email"
                :class="{ coraltext: emailError, greenText: emailVerified }"
                disabled
              /> -->
              <!-- 
              <div v-if="verifying" style="top: 50%" class="abs-placed loading-small">
                Finding email
                <div style="margin-left: 8px" class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>

              <div v-else-if="emailVerified" class="rowed green-img abs-placed" style="top: 35%">
                <img src="@/assets/images/shield-check.svg" height="18px" alt="" />
              </div>

              <div v-else-if="emailError" class="abs-placed red-img" style="top: 35%">
                <img src="@/assets/images/shield-x.svg" height="14px" alt="" />
              </div> -->
            </div>

            <div style="position: relative; margin-bottom: 8px">
              <p
                style="
                  margin: 0 8px 0 0;
                  padding: 0;
                  font-size: 18px;
                  position: absolute;
                  left: 0;
                  top: 20px;
                "
                class="bold-font"
              >
                Subject:
              </p>
              <input
                class="primary-input-underline"
                v-model="subject"
                type="text"
                placeholder=""
                style="padding-left: 64px; padding-top: 6px"
              />
            </div>

            <quill-editor
              :disabled="loadingDraft || sendingEmail"
              ref="quill"
              :options="{
                modules: {
                  toolbar: toolbarOptions,
                },
                theme: 'snow',
                placeholder: '',
              }"
              v-model:content="revisedPitch"
              class="text-editor"
            />

            <!-- <div v-if="loadingDraft" style="margin-left: 12px" class="loading-small-absolute">
              <p>Generating email</p>
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div> -->
          </div>
        </div>

        <div class="space-between">
          <div class="row">
            <button
              :disabled="loadingDraft || !subject || !targetEmail || sendingEmail || !adviseUpdate"
              @click="
                updateDraft(selectedEmail.is_approved, selectedEmail.is_rejected, 'Updated', true)
              "
              class="secondary-button"
            >
              <img
                v-if="loadingDraft"
                style="margin-right: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Update draft
            </button>

            <div class="row warning-txt" v-show="adviseUpdate">
              <img
                style="margin-left: 16px"
                src="@/assets/images/warning.svg"
                height="12px"
                alt=""
              />
              <p style="padding: 0; margin: 0 0 0 4px; font-size: 13px">
                Update draft before closing
              </p>
            </div>

            <!-- <div style="margin-left: 8px" class="img-container s-wrapper">
              <img
                style="filter: invert(30%)"
                src="@/assets/images/close.svg"
                height="18px"
                alt=""
              />
              <div class="s-tooltip">Reject</div>
            </div>

            <div class="img-container s-wrapper">
              <img class="turq-filter" src="@/assets/images/check.svg" height="14px" alt="" />
              <div class="s-tooltip">Approve</div>
            </div> -->
          </div>

          <div class="row">
            <button
              class="secondary-button"
              :disabled="loadingDraft"
              @click="draftEmailModalOpen = false"
            >
              Close
            </button>

            <button
              @click="sendEmail"
              :disabled="loadingDraft || !subject || !targetEmail || sendingEmail"
              style="margin-right: 4px"
              class="primary-button"
              :class="{ opaque: loadingDraft || !subject || !targetEmail }"
            >
              <img
                v-if="sendingEmail"
                style="margin-right: 4px"
                class="invert rotation"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
              Send
            </button>
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
        <tr v-for="(email, i) in sortedEmails" :key="i">
          <td
            :class="i % 2 !== 0 ? 'gray-bg' : ''"
            style="cursor: pointer"
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
                  <!-- <img
                    v-if="email.is_draft"
                    class="abs-img"
                    src="@/assets/images/edit.svg"
                    height="14px"
                    alt=""
                  /> -->
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
          <td v-if="!email.is_draft" :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div :class="{ redText: email.failed, greenText: !email.failed }">
              {{ email.failed ? 'Failed' : 'Delivered' }}
            </div>
          </td>
          <td
            @click="toggleEmailModal(email)"
            style="cursor: pointer"
            v-else
            :class="i % 2 !== 0 ? 'gray-bg' : ''"
          >
            <div v-if="email.is_approved" class="greenbox">Approved</div>
            <div v-else-if="email.is_rejected" class="redbox">Rejected</div>
            <div v-else class="orangebox">Draft</div>
          </td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.opens }}</td>
          <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.clicks }}</td>
          <!-- <td :class="i % 2 !== 0 ? 'gray-bg' : ''">{{ email.replies }}</td> -->
          <!-- @click="toggleActivityModal(email)" style="cursor: zoom-in"-->
          <td class="mobile-width" :class="i % 2 !== 0 ? 'gray-bg' : ''">
            <div v-if="email.activity_log && email.activity_log.length">
              <div
                v-if="email.is_draft && !email.is_rejected && !email.is_approved"
                style="margin-bottom: 4px; font-size: 14px"
              >
                Draft created
              </div>

              <div v-else style="margin-bottom: 4px; font-size: 14px">
                {{
                  email.activity_log &&
                  email.activity_log.length > 0 &&
                  email.activity_log.at(-1).split('|')[0]
                    ? email.activity_log.at(-1).split('|')[0].charAt(0).toUpperCase() +
                      email.activity_log.at(-1).split('|')[0].slice(1)
                    : ''
                }}
              </div>

              <div style="color: #808080; font-size: 14px">
                {{ formatActivityLog(email.activity_log.at(-1)) }}
              </div>
            </div>
            <div v-else>No activities</div>
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
import { quillEditor } from 'vue-quill-editor'
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

export default {
  name: 'EmailTable',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    quillEditor,
  },

  data() {
    return {
      loadingDraft: false,
      showingStatus: false,
      emails: [],
      sortKey: '',
      sortOrder: 1,
      statsKeys: ['To', 'Status', 'Opens', 'Clicks'],
      openRate: 0,
      replyRate: 0,
      draftEmailModalOpen: false,
      emailModalOpen: false,
      activityModalOpen: false,
      selectedEmail: null,
      loading: false,
      emailDrafts: [],
      targetEmail: '',
      subject: '',
      revisedPitch: '',
      journalistName: '',
      approved: false,
      rejected: false,
      sendingEmail: false,
      originalSubject: '',
      originalRecipient: '',
      originalRevisedPitch: '',
      adviseUpdate: false,
      toolbarOptions: [
        ['bold', 'italic', 'underline', 'strike'], // toggled buttons
        ['link'],
        // next to link - 'image'
        [{ header: 1 }, { header: 2 }], // custom button values
        [{ list: 'ordered' }, { list: 'bullet' }, { list: 'check' }],

        [{ size: ['small', false, 'large', 'huge'] }], // custom dropdown

        ['clean'], // remove formatting button
      ],
    }
  },
  props: {
    searchText: {},
    failedFilter: {
      type: Boolean,
      default: null,
    },
    statusFilter: {
      default: null,
    },
    draftFilter: {
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
        const statusFilter = this.statusFilter !== undefined ? this.statusFilter : null
        const draftFilter = this.draftFilter !== undefined ? this.draftFilter : null
        const activityFilter = this.activityFilter !== undefined ? this.activityFilter : null
        const userFilter = this.userId !== undefined ? this.userId : null

        const searchConditions = [
          email.recipient ? email.recipient.toLowerCase().includes(searchText) : '',
          email.subject ? email.subject.toLowerCase().includes(searchText) : '',
          email.name ? email.name.toLowerCase().includes(searchText) : '',
          email.body ? email.body.toLowerCase().includes(searchText) : '',
          email.opens ? email.opens.toString().includes(searchText) : '',
          email.replies ? email.replies.toString().includes(searchText) : '',
          email.clicks ? email.clicks.toString().includes(searchText) : '',
          email.activity_log && email.activity_log.length > 0
            ? email.activity_log.at(-1).includes(searchText)
            : '',
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

        if (draftFilter !== null) {
          filterConditions.push(
            email.is_draft === true && email.is_approved === false && email.is_rejected === false,
          )
        }

        if (statusFilter !== null) {
          if (statusFilter === 'is_approved') {
            filterConditions.push(email.is_approved === true)
          } else {
            filterConditions.push(email.is_rejected === true)
          }
        }

        if (activityFilter !== null) {
          const [start, end] = activityFilter.split(',')
          const startDate = new Date(start)
          const endDate = new Date(end)
          const emailDate =
            email.activity_log && email.activity_log.length > 0
              ? new Date(email.activity_log.at(-1).split('|')[1])
              : null
          filterConditions.push(emailDate >= startDate && emailDate <= endDate)
        }

        return (
          searchConditions.some((condition) => condition) &&
          filterConditions.every((condition) => condition)
        )
      })

      if (!this.sortKey) return filteredEmails

      return filteredEmails.slice().sort((a, b) => {
        const getStatus = (email) => {
          if (email.is_draft && !email.is_rejected && !email.is_approved) {
            return 'adraft'
          } else if (email.is_draft && !email.is_rejected && email.is_approved) {
            return 'capproved'
          } else if (email.is_draft && email.is_rejected && !email.is_approved) {
            return 'brejected'
          } else if (!email.is_draft && email.failed) {
            return 'dfailed'
          } else if (!email.is_draft && !email.failed) {
            return 'edelivered'
          } else {
            return '' // If no status matches, default to empty string
          }
        }

        const aValue =
          this.sortKey === 'lastActivity'
            ? new Date(a.activity_log.at(-1).split('|')[1])
            : this.sortKey === 'to'
            ? a.recipient
            : this.sortKey === 'status'
            ? getStatus(a)
            : a[this.sortKey]

        const bValue =
          this.sortKey === 'lastActivity'
            ? new Date(b.activity_log.at(-1).split('|')[1])
            : this.sortKey === 'to'
            ? b.recipient
            : this.sortKey === 'status'
            ? getStatus(b)
            : b[this.sortKey]

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

    selectedEmail(val) {
      if (val) {
        this.targetEmail = val.recipient
        this.subject = val.subject
        const replacedText = val.body.replace(/\n/g, '<br>')
        this.revisedPitch = `<p>${replacedText}</p>`
        this.journalistName = val.name
      }
    },
    draftEmailModalOpen(val) {
      if (val === true) {
        // Store the original values when the modal opens
        this.originalSubject = this.subject
        this.originalRecipient = this.targetEmail
        this.originalRevisedPitch = this.revisedPitch
      } else {
        // Reset adviseUpdate when the modal closes
        this.adviseUpdate = false
      }
    },
    subject() {
      this.checkForChanges()
    },
    targetEmail() {
      this.checkForChanges()
    },
    revisedPitch() {
      this.checkForChanges()
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
    checkForChanges() {
      console.log('changing')
      if (
        this.subject !== this.originalSubject ||
        this.targetEmail !== this.originalRecipient ||
        this.revisedPitch !== this.originalRevisedPitch
      ) {
        this.adviseUpdate = true
      } else {
        this.adviseUpdate = false
      }
    },
    async sendEmail() {
      this.sendingEmail = true
      try {
        const res = await Comms.api.sendEmail({
          subject: this.subject,
          body: this.revisedPitch,
          recipient: this.targetEmail,
          name: this.journalistName,
          draftId: this.selectedEmail.id,
        })

        this.draftEmailModalOpen = false
        this.$toast('Pitch sent', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })

        this.sendingEmail = false
      } catch (e) {
        console.log(e)
        this.$toast('Error sending email, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.sendingEmail = false
      } finally {
        this.fetchEmails()
      }
    },

    async updateDraft(approved = false, rejected = false, type, stayOpen) {
      this.loadingDraft = true
      try {
        const res = await Comms.api.updateDraft({
          id: this.selectedEmail.id,
          recipient: this.targetEmail,
          subject: this.subject,
          body: this.revisedPitch,
          name: this.journalistName,
          is_approved: approved,
          is_rejected: rejected,
          activity_type: type,
        })
        if (type === 'Approved') {
          this.$toast('Draft approved', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (type === 'Rejected') {
          this.$toast('Draft rejected', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Draft updated', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } catch (e) {
        this.$toast('Error updating draft, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.loadingDraft = false
        this.adviseUpdate = false
        if (!stayOpen) {
          this.draftEmailModalOpen = false
        }
        this.fetchEmails()
      }
    },
    openStatusMenu() {
      this.showingStatus = true
    },
    hideStatus() {
      this.showingStatus = false
    },
    test() {
      console.log(this.sortedEmails)
    },
    toggleEmailModal(email = null) {
      console.log(email)
      this.selectedEmail = email
      if (email.is_draft) {
        this.draftEmailModalOpen = !this.draftEmailModalOpen
      } else {
        this.emailModalOpen = !this.emailModalOpen
      }
    },
    toggleActivityModal(email = null) {
      this.activityModalOpen = !this.activityModalOpen
      this.selectedEmail = email
    },
    async fetchEmails() {
      try {
        const response = await Comms.api.getTrackedEmails()
        this.emails = response.results
        console.log('EMAILS ARE HERE', this.emails)
        // this.openRate = Math.round(response.rates.open_rate)
        // this.replyRate = response.rates.reply_rate
      } catch (error) {
        console.error('Error fetching email data:', error)
      }
    },
    formatActivityLog(logEntry, fullEntry = false) {
      if (!logEntry) {
        return 'No activity log'
      }

      const [action, dateTime] = logEntry.split('|')

      if (!dateTime) {
        return 'Invalid log entry'
      }

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
    // background-color: $lite-pink !important;
    // color: $pinky !important;
    background-color: $pinky !important;
    color: white !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 16px;
    width: 100px;
    text-align: center;
  }

  .greenbox {
    background-color: $turq !important;
    color: white !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 16px;
    width: 100px;
    text-align: center;
  }

  .greenText {
    // background-color: $turq !important;
    color: $turq !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 16px;
    width: 100px;
    text-align: center;
  }

  .orangebox {
    background-color: $new-orange !important;
    color: white !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 16px;
    width: 100px;
    text-align: center;
  }

  .purplebox {
    background-color: $graper !important;
    color: $white !important;
    font-family: $base-font-family;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 16px;
    width: 100px;
    text-align: center;
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
  border: 1px solid rgba(0, 0, 0, 0.2);
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}

.mobile-text {
  font-size: 13px;
}

.text-editor {
  height: 160px;
  width: 100%;
  border-radius: 8px;
  @media only screen and (max-width: 600px) {
    height: 140px;
  }
}

::v-deep .ql-toolbar.ql-snow {
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

::v-deep .ql-container {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
  padding: 8px 2px;
}

::v-deep .ql-editor {
  font-family: $thin-font-family;
  font-size: 14px;
}

::v-deep .ql-snow.ql-toolbar button {
  background: $soft-gray;
  border-radius: 4px;
  margin-right: 4px;
}

.primary-input-underline {
  width: 100%;
  margin: 1rem 0;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.135);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 16px;
  padding: 4px 20px 16px 18px;
  outline: none;

  @media only screen and (max-width: 600px) {
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
  }
}

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.paid-body {
  margin: 0.5rem 0;
}

.status-dropdown {
  position: absolute;
  top: 40px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 12px;
  height: 300px;
  width: 200px;
  z-index: 1000000000000000;

  .status-dropdown-body {
  }

  .status-dropdown-footer {
    position: sticky;
    bottom: 0;
    width: 100%;
    background-color: white;
  }
}

.abs-img {
  position: absolute;
  right: 0;
  top: 20px;
  z-index: 3;
  filter: invert(40%);
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
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

.img-container {
  cursor: pointer;
  padding: 5px 7px 4px 7px;
  border-radius: 50%;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }
}

.img-container-wide {
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 16px;
  &:hover {
    background-color: $soft-gray;
  }

  img {
    margin: 0;
    padding: 0;
  }
}

.turq-filter {
  filter: invert(56%) sepia(96%) saturate(331%) hue-rotate(139deg) brightness(90%) contrast(87%);
}

.s-tooltip {
  visibility: hidden;
  width: 100px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  bottom: 130%;
  left: 50%;
  margin-left: -50px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  // border: 1px solid rgba(0, 0, 0, 0.328);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-wrapper {
  position: relative;
  display: inline-block;
}

.s-wrapper:hover .s-tooltip,
.s-wrapper:hover .s-tooltip-below {
  visibility: visible;
  opacity: 1;
}

.bold-font {
  font-family: $base-font-family;
}

.no-button-borders {
  button {
    border: none;
    background-color: transparent;
  }
}

.warning-txt {
  color: $pinky;

  img {
    filter: invert(43%) sepia(88%) saturate(559%) hue-rotate(280deg) brightness(86%) contrast(83%) !important;
  }
}

.teal {
  border: 1px solid $turq;
  color: $turq;
  img {
    filter: invert(56%) sepia(96%) saturate(331%) hue-rotate(139deg) brightness(90%) contrast(87%);
  }
  &:hover {
    color: $turq;
  }
}

.pinker {
  border: 1px solid $pinky;
  color: $pinky;
  img {
    filter: invert(43%) sepia(88%) saturate(559%) hue-rotate(280deg) brightness(86%) contrast(83%) !important;
  }

  &:hover {
    color: $pinky;
  }
}
</style>
