<template>
  <div ref="transcriptTop" class="transcripts">
    <div :class="{ opaque: loading }" v-if="!transcript" class="center extra-margin-top">
      <p v-if="!loading">Generate a transcript from your zoom meeting</p>

      <div class="centered blue-bg" v-else>
        <div style="width: 675px" class="row">
          <p class="summary-load-text">Generating summary...</p>
        </div>

        <div class="summary-preview-skeleton shimmer">
          <div class="content">
            <div class="meta-wide"></div>
            <div class="meta-shorter"></div>
            <div class="meta-shortest"></div>
          </div>
        </div>
      </div>

      <div class="input-container" v-if="!loading">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/calendar-day.svg" height="14px" alt="" />
            Date
          </div>

          <input
            :disabled="loading"
            type="date"
            autofocus
            v-model="meetingDate"
            class="date-input padding-left"
          />
        </div>
      </div>

      <div class="input-container" v-clickOutsideMenu v-if="!loading">
        <div class="input-row">
          <div class="main-text">
            <img src="@/assets/images/circle-video.svg" height="14px" alt="" />
            Meeting
          </div>

          <div @click="showDropdown" class="pointer padding-left">{{ selectedMeeting && selectedMeeting ? selectedMeeting.topic : 'No meetings. Select another day' }}</div>
        </div>
        <div v-if="showingMeetingDropdown" class="dropdown">
          <small style="padding-top: 8px" class="gray-text">Your Meetings</small>
          <div
            @click="selectMeeting(meeting)"
            class="dropdown-item"
            v-for="(meeting, i) in meetings"
            :key="i"
          >
            <p>
              {{ meeting.topic }}
            </p>
          </div>
        </div>
      </div>

      <footer>
        <!-- <button :disabled="loading" @click="clearData" class="secondary-button">Clear</button> -->
        <button v-if="!loading" :disabled="loading" @click="generateTranscript" class="primary-button">
          <img
            v-if="loading"
            class="rotate"
            height="14px"
            src="@/assets/images/loading.svg"
            alt=""
          />
          {{ loading ? 'Submitting' : 'Submit' }}
        </button>
      </footer>
    </div>

    <div v-else class="center">
      <div class="transcript-background">
        <div class="transcript-container">
          <div class="title-container">
            <div @click="resetSearch" class="back">
              <img src="@/assets/images/back.svg" height="18px" width="18px" alt="" />
            </div>
            <h1 class="no-text-margin">{{ selectedMeeting && selectedMeeting ? selectedMeeting.topic : "" }}</h1>
            <p class="sub-text">
              Meeting Date: <span>{{ meetingDate }}</span>
            </p>
          </div>
  
          <div class="title-bar">
            <div class="row">
              <!-- toggleRegenerate -->
              <button
                :disabled="loading"
                @click="() => null"
                v-if="!regenerating"
                class="secondary-button"
              >
                <img
                  v-if="loading"
                  class="rotate"
                  height="14px"
                  src="@/assets/images/loading.svg"
                  alt=""
                />
                {{ loading ? 'Generating' : 'Generate' }}
              </button>
              <div style="width: 600px" class="row" v-else>
                <input
                  :disabled="loading"
                  placeholder="provide additional instructions..."
                  autofocus
                  class="regen-input"
                  type="textarea"
                  v-model="instructions"
                />
  
                <button @click="regenerateTranscript" class="primary-button">Regenerate</button>
              </div>
            </div>
  
            <div @click="copyText" v-if="!regenerating" class="wrapper">
              <img
                style="cursor: pointer"
                class="right-mar img-highlight"
                src="@/assets/images/clipboard.svg"
                height="16px"
                alt=""
              />
              <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
            </div>
          </div>
  
          <pre v-html="transcript" class="pre-text"></pre>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { Comms } from '@/services/comms'
import User from '@/services/users'
import Zoom from '@/services/zoom/account'

export default {
  name: 'PRTranscripts',
  components: {},
  data() {
    return {
      meetingDate: '',
      meetings: [],
      output: '',
      persona: '',
      briefing: '',
      transcript: null,
      loading: false,
      zoomLoading: false,
      regenerating: false,
      showingMeetingDropdown: false,
      instructions: '',
      copyTip: 'Copy',
      textToCopy: '',
      currentTask: null,
      checkingTask: false,
      interval: null,
      // meetings: [
      //   { title: 'Bryan Meeting' },
      //   { title: 'Zach Meeting' },
      //   { title: 'Ed Meeting' }
      // ],
      selectedMeeting: {},
    }
  },
  watch: {
    // filteredMeetings: ['changeSelectedMeeting']
    meetingDate: ['getZoomMeetings']
  },
  async created() {
    await this.$store.dispatch('loadMeetings')
    await this.getDate(Date.now())
    await this.getZoomMeetings()
  },
  methods: {
    showDropdown() {
      this.showingMeetingDropdown = true
    },
    hideDropdown() {
      this.showingMeetingDropdown = false
    },
    changeSelectedMeeting() {
      this.selectedMeeting = this.meetings[0]
    },
    getDate(date) {
      const unformattedDate = new Date(date)
      // Extract year, month, and day components
      const year = unformattedDate.getFullYear();
      const month = (unformattedDate.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
      const day = unformattedDate.getDate().toString().padStart(2, '0');

      // Create the desired output string in the format "YYYY-MM-DD"
      const outputDateString = year + '-' + month + '-' + day;
      this.meetingDate = outputDateString;
    },
    selectMeeting(meeting) {
      // console.log('meeting here', meeting)
      // const generatedMeeting = this.$store.state.meetings.filter(meet => meet.meeting_ref.meeting_id == meeting.id)[0]
      // console.log('generatedMeeting', generatedMeeting)
      // if (generatedMeeting.transcript_summary) {
      //   this.transcript = generatedMeeting.transcript_summary
      // } else {
        this.selectedMeeting = meeting
      // }
      this.hideDropdown()
    },
    async copyText() {
      try {
        await navigator.clipboard.writeText(this.transcript)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    resetSearch() {
      this.transcript = null
      // this.meetingDate = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.instructions = ''
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.transcriptTop.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    toggleRegenerate() {
      this.regenerating = !this.regenerating
    },
    async checkTask() {
      this.checkingTask = true
      try {
        const response = await User.api.checkTasks({
            verbose_name: this.currentTask,
          })
        console.log('response checkTask', response)
        if (response.completed) {
          clearInterval(this.interval)
          await this.$store.dispatch('loadMeetings')
          const generatedMeeting = this.$store.state.meetings.filter(meet => meet.meeting_ref.meeting_id == this.selectedMeeting.id)[0]
          this.transcript = generatedMeeting.transcript_summary
          this.loading = false
        }
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.checkingTask = false
        }, 1000)
      }
    },
    async getZoomMeetings() {
      this.zoomLoading = true
      try {
        let res = await Zoom.api.getZoomMeetings({
          user_id: this.$store.state.user.id,
          date: this.meetingDate,
        })
        console.log('res', res)
        this.meetings = res.data
        this.selectedMeeting = res.data.length ? res.data[0] : null
      } catch (e) {
        console.log('ERROR GETTING MEETINGS:', e)
      } finally {
        setTimeout(() => {
          this.zoomLoading = false
        }, 1000)
      }
    },
    async regenerateTranscript() {
      this.regenerating = false
      this.loading = true
      try {
        await User.api
          .submitChatTranscript({
            transcript: this.transcript,
            instructions: this.instructions,
          })
          .then((response) => {
            console.log(response)
            this.transcript = response.transcript
          })
      } catch (e) {
        console.log('ERROR CREATING TRANSCRIPT::', e)
      } finally {
        // this.clearData()
        this.instructions = ''
        this.loading = false
        this.scrollToTop()
      }
    },
    async generateTranscript() {
      if (!this.meetingDate) {
        this.$toast('Meeting Date Required', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      const generatedMeeting = this.$store.state.meetings.filter(meet => meet.meeting_ref.meeting_id == this.selectedMeeting.id)[0]
      if (generatedMeeting && generatedMeeting.transcript_summary) {
        this.transcript = generatedMeeting.transcript_summary
        return
      }
      this.loading = true
      try {
        // return console.log('this.selectedMeeting', this.selectedMeeting)
        const res = await User.api
          .submitChatTranscript({
            user_id: this.$store.state.user.id,
            meeting_id: this.selectedMeeting.id,
          })
          console.log('res here', res)
          this.currentTask = res.verbose_name
          this.interval = setInterval(() => {
            this.checkTask()
          }, 1800)
          // if (res.status === 200) {
          //   console.log(res)
          //   this.$store.dispatch('setMeetingData', {
          //     id: this.selectedMeeting.id,
          //     data: res.data,
          //     success: false,
          //     retry: false,
          //     analysis: res.analysis,
          //   })
          // } else {
          //   this.$store.dispatch('setMeetingData', {
          //     id: this.selectedMeeting.id,
          //     data: res.data,
          //     success: false,
          //     retry: true,
          //     analysis: null,
          //   })
          // }
          // this.transcript = response.transcript
          this.scrollToTop()
      } catch (e) {
        console.log('ERROR CREATING TRANSCRIPT', e)
      } finally {
        // this.clearData()
        // this.loading = false
        this.scrollToTop()
      }
    },
    clearData() {
      // this.meetingDate = ''
      this.output = ''
      this.persona = ''
      this.briefing = ''
      this.sample = ''
    },
  },
  computed: {
    remainingChars() {
      return 1000 - this.output.length
    },
    remainingCharsBrief() {
      return 1000 - this.briefing.length
    },
    // meetings() {
    //   return this.$store.state.meetings
    // },
    // filteredMeetings() {
    //   return this.$store.state.meetings.filter(meeting => this.meetingDate === meeting.start_time.split('T')[0])
    // },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
    clickOutsideMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::placeholder {
  color: $mid-gray;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.title-container {
  position: relative;
  width: 100%;
}

.relative {
  position: relative;
}

.extra-margin-top {
  margin-top: 16px;
}

.absolute-count {
  position: absolute;
  bottom: -2px;
  right: -8px;
  font-size: 11px;
  color: $light-gray-blue;
  background-color: white;
}

.no-text-margin {
  margin: 0;
}

.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
}

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0 0 0;
  font-size: 14px;
  font-weight: bold;
  font-family: $thin-font-family;
  span {
    font-weight: normal;
    word-wrap: break-word;
  }
}

.title-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
  text-align: start !important;

  button:first-of-type {
    margin-right: 1rem;
  }
}

.transcript-background {
  background-color: $off-white;
  padding-top: 16px;
  width: 85%;
  display: flex;
  justify-content: center;
}
.transcript-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;

  margin-right: 8px;
}

.pre-text {
  // background-color: $white-blue;
  border-radius: 4px;
  padding: 16px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.transcripts {
  background-color: white;
  width: 100vw;
  height: 100vh;
  padding: 58px 36px 0 36px;
  display: flex;
  overflow-y: scroll;
  font-family: $base-font-family;
  color: $chat-font-color;
}

.center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  // height: 100%;
  padding-top: 16px;
  font-size: 14px;
  color: $dark-black-blue;
  gap: 24px;
}
.date-input {
  background-color: $offer-white;
  outline: none;
  border: none;
  font-family: $base-font-family;
}
.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem 0.75rem 1.2rem;
  border-radius: 6px;
  width: 675px;
  background-color: $offer-white;
  color: $base-gray;
}
.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $base-font-family;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input:disabled {
  cursor: not-allowed;
}

.area-input::-webkit-scrollbar {
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.regen-input {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 6px;
  width: 400px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 8px 1rem;
  font-family: $base-font-family;
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}
.main-text {
  width: 82px;
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1rem;
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    margin-right: 8px;
    filter: invert(40%);
  }
}

footer {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-bottom: 1rem;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  white-space: nowrap;
  margin-left: 1rem;
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.blue-bg {
  background-color: $white-blue;
}

.opaque {
  opacity: 0.75;
  padding-top: 0 !important;
}

.img-highlight {
  filter: invert(40%);

  &:hover {
    filter: none;
  }
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -20px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}

.back {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0.75rem;
  left: -56px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 3px 2px;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
}

.summary-load-text {
  font-family: $thin-font-family;
  font-size: 14px;
}

.summary-preview-skeleton {
  width: 675px;
  // min-width: 400px;
  padding: 8px 20px 16px 0;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
}

@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  display: inline-block;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
}

.meta-wide {
  width: 100%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shorter {
  width: 80%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shortest {
  width: 60%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.dropdown {
  padding: 8px 0 8px 0;
  position: relative;
  height: fit-content;
  max-height: 232px;
  width: 100%;
  top: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  display: none;
}
.dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.dropdown:hover::-webkit-scrollbar {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 0;
  width: 100%;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  z-index: 2300;

  p {
    margin: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}
.pointer {
  cursor: pointer;
}
.padding-left {
  padding-left: 0.5rem;
}
.gray-text {
  color: $mid-gray;
}
</style>