<template>
  <div class="row">
    <button @click="changeWidth" class="notis" :style="`right: ${notiRight}px`">
      <img v-if="notiRight === 0" src="@/assets/images/dropdown-arrow.svg" height="16px" alt="" />
      <img v-else src="@/assets/images/dropdown-arrow.svg" class="rotate" height="16px" alt="" />
      <!-- <small class="red">5</small> -->
    </button>
    <section @click="test" id="mySidenav" :style="`width: ${navWidth}px`" class="sidenav">
      <h3 class="neg-mar-bottom">{{ `${day} ${today}` }}</h3>
      <div class="noti-section">
        <p class="sticky">
          Meetings <small class="yellow-bg">{{ meetings ? meetings.length : 0 }}</small>
          <button class="yellow-button" @click="goToMeetings">View</button>
        </p>
        <span v-if="meetings ? !meetings.length : null"
          ><a class="yellow-border no-cursor">No meetings today.</a></span
        >

        <div v-else>
          <span :key="i" v-for="(meeting, i) in meetings"
            ><a class="yellow-border no-cursor"
              >{{
                meeting.meeting_ref.event_data
                  ? meeting.meeting_ref.event_data.title
                  : meeting.meeting_ref.topic
              }}
              <span class="grey">{{
                formatDateTimeToTime(
                  meeting.meeting_ref.event_data
                    ? meeting.meeting_ref.event_data.times.start_time
                    : meeting.meeting_ref.start_time,
                )
              }}</span>
              <p
                :class="
                  meeting.is_completed ? 'small-font no-margin yellow' : 'small-font no-margin'
                "
              >
                {{ meeting.is_completed ? 'Logged' : 'Please log' }}
              </p>
            </a></span
          >
        </div>
      </div>

      <div class="noti-section-lg">
        <p class="sticky">
          Pipeline <small class="green-bg">{{ templates.list ? templates.list.length : 0 }}</small>
          <button :disabled="!templates.list.length" class="green-button" @click="runWorkflows">
            Refresh
          </button>
        </p>
        <span v-if="!templates.list.length"
          ><a class="green-border no-cursor">No active workflow.</a></span
        >
        <span @click="goToWorkflow(alert.id)" :key="i" v-for="(alert, i) in templates.list"
          ><a class="green-border">
            {{ alert.title }} <small class="green">{{ workflows[i] ? workflows[i] : '--' }}</small>
            <p class="small-font no-margin grey">owner: {{ users ? owner(alert.user) : '' }}</p>
          </a>
        </span>

        <!-- <span><a class="green-border" href="">Pipeline 3</a></span>  -->
      </div>

      <!-- <div class="noti-section">
        <p class="sticky light-gray">Task<small class="light-gray-bg">0</small></p>
        <span><a style="pointer-events: none" class="red-border" href="">Coming Soon</a></span>
      </div> -->
    </section>
  </div>
</template>

<script>
import { MeetingWorkflows } from '@/services/salesforce'
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users'

export default {
  name: 'SideDrawer',
  data() {
    return {
      notiRight: 0,
      navWidth: 18,
      meetings: null,
      today: null,
      day: null,
      workflows: [],
      days: {
        0: 'Sunday',
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
      },
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      users: CollectionManager.create({ ModelClass: User }),
      //   months: {
      //       01:'January',
      //       02:'February',
      //       03:'March',
      //       04:'April',
      //       05:'May',
      //       06:'June',
      //       07:'July',
      //       08:'August',
      //       09:'September',
      //       10:'October',
      //       11:'November',
      //       12:'December',
      //   }
    }
  },
  methods: {
    async runWorkflows() {
      let ids = this.templates.list.map((wf) => wf.id)
      console.log(ids)
      try {
        for (let i = 0; i < ids.length; i++) {
          let res = await AlertTemplate.api.runAlertTemplateNow(ids[i], {
            fromWorkflow: true,
          })
          this.workflows.push(res.data.ids.length)
        }
      } catch (error) {
        console.log(error)
      }
    },
    owner(usr) {
      return this.users.list.filter((user) => user.id === usr)[0].fullName
    },
    formatDateTimeToTime(input) {
      let preDate = new Date(input)
      let newTime = preDate.toLocaleTimeString('en-US')
      let amPm = newTime.split(' ')[1]
      let hour = newTime.split(':')[0]
      let noSeconds = newTime.replace(':', ' ')
      let noAmPm = newTime.replace(amPm, '')
      let noAmPmSeconds = noAmPm.replace(':', ' ')

      if (parseInt(hour) < 10) {
        newTime = '0' + newTime
        noAmPm = '0' + noAmPm
        noSeconds = '0' + noSeconds
        noAmPmSeconds = '0' + noAmPmSeconds
      }
      noSeconds = noSeconds.replace(' ', ':')
      noSeconds = noSeconds.split(':')
      noSeconds = noSeconds[0] + ':' + noSeconds[1] + amPm
      return noSeconds
    },
    goToWorkflow(id) {
      this.$router.push({ path: `/pipelines/${id}` })
    },
    goToMeetings() {
      this.$router.push({ name: 'Meetings' })
    },
    test() {
      console.log(this.users.list)
      console.log(this.templates.list)
    },
    async getMeetingList() {
      try {
        const res = await MeetingWorkflows.api.getMeetingList()
        this.meetings = res.results
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    changeWidth() {
      this.notiRight === 0 ? (this.notiRight = 235) : (this.notiRight = 0)
      this.navWidth === 18 ? (this.navWidth = 250) : (this.navWidth = 18)
    },
    setDate() {
      let today = new Date()
      let day = today.getDay()
      this.day = this.days[day]
      let dd = String(today.getDate()).padStart(2, '0')
      let mm = String(today.getMonth() + 1).padStart(2, '0')

      let yyyy = today.getFullYear()
      today = '  ' + mm + '/' + dd + '/' + yyyy
      this.today = today
    },
  },
  async created() {
    this.getMeetingList()
    this.templates.refresh()
    this.users.refresh()
  },
  mounted() {
    this.setDate()
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

button:disabled {
  color: $very-light-gray;
  border: 1px solid $very-light-gray;
  cursor: text;
}
.no-margin {
  margin: 0 0 0 -3px;
}
.small-font {
  font-size: 10px !important;
}
.no-cursor {
  cursor: text !important;
}
.col {
  display: flex;
  flex-direction: column;
}
.grey {
  color: $gray;
}
.light-gray-bg {
  border-radius: 50%;
  background-color: $very-light-gray;
  color: white;
  padding: 2px 6px;
  margin-left: 5px;
}
.yellow-bg {
  border-radius: 50%;
  background-color: $yellow;
  color: white;
  padding: 2px 6px;
  margin-left: 5px;
}
.yellow-button {
  border: 1px solid $yellow;
  border-radius: 4px;
  background-color: white;
  color: $yellow;
  margin-left: 65px;
  cursor: pointer;
}
.yellow {
  color: $yellow !important;
}
.green-bg {
  border-radius: 50%;
  background-color: $dark-green;
  color: white;
  padding: 2px 6px;
  margin-left: 5px;
}
.green-button {
  border: 1px solid $dark-green;
  border-radius: 4px;
  background-color: white;
  color: $dark-green;
  margin-left: 55px;
  cursor: pointer;
}
.green {
  color: $dark-green;
}
.red-bg {
  border-radius: 50%;
  background-color: $coral;
  color: white;
  padding: 2px 6px;
  margin-left: 5px;
}
.sticky {
  position: sticky;
  top: 0;
  height: 35px;
  background-color: white;
}
.neg-mar-bottom {
  margin-bottom: -5px;
}
.noti-section-lg {
  height: 350px;
  overflow-y: scroll;
  padding: 0px 16px;
  border-bottom: 1px solid $soft-gray;
  margin: 0px 0px 5px 0px;
  width: 100%;
}
.noti-section {
  height: 200px;
  overflow-y: scroll;
  padding: 0px 16px;
  border-bottom: 1px solid $soft-gray;
  margin: 0px 0px 5px 0px;
  width: 100%;
}
.soft-gray-bg {
  background-color: $off-white;
  height: 26px;
}
.yellow-border {
  border: 1px solid $yellow;
  border-radius: 4px;
  min-height: 56px;
  margin-bottom: 3px;
}
.green-border {
  border: 1px solid $dark-green;
  border-radius: 4px;
  min-height: 56px;
  margin-bottom: 3px;
}
.red-border {
  border: 1px solid $very-light-gray;
  border-radius: 4px;
  height: 46px;
  margin-bottom: 3px;
  color: $very-light-gray !important;
  cursor: text;
}
.light-gray {
  color: $very-light-gray !important;
}
.red {
  color: red;
  padding: 2px 4px;
}
.row {
  display: flex;
  flex-direction: row;
}
.notis {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: fixed;
  z-index: 21;
  right: 0;
  bottom: 2rem;
  border: 1px solid $soft-gray;
  border-radius: 50%;
  background-color: white;
  padding: 6px;
  transition: 0.5s;
  cursor: pointer;

  img {
    transform: rotate(90deg);
  }
}
.rotate {
  transform: rotate(270deg) !important;
}

.sidenav {
  height: 100%;
  width: 0;
  position: fixed;
  z-index: 20;
  top: 0;
  right: 0;
  border-left: 1px solid #e8e8e8;
  background-color: white;
  overflow-x: hidden;
  padding-top: 60px;
  transition: 0.5s;
}

h3 {
  font-size: 12px;
  padding: 4px 8px 2px 20px;
  color: $base-gray;
  letter-spacing: 0.75px;
}

.sidenav p {
  padding: 8px 8px 8px 4px;
  letter-spacing: 0.75px;
  font-size: 14px;
  font-weight: bolder;
  color: $base-gray;
  display: block;
  transition: 0.3s;
}

.sidenav a {
  padding: 8px 8px 8px 20px;
  letter-spacing: 0.5px;
  text-decoration: none;
  font-size: 11px;
  color: $base-gray;
  display: block;
  transition: 0.3s;
  cursor: pointer;
}

.sidenav a:hover {
  color: #c0bcbc;
}

.sidenav .closebtn {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 36px;
  margin-left: 50px;
}

#main {
  transition: margin-left 0.5s;
  padding: 20px;
}
@media screen and (max-height: 450px) {
  .sidenav {
    padding-top: 15px;
  }
  .sidenav a {
    font-size: 18px;
  }
}

//  ::-webkit-scrollbar {
//     width: 2px; /* Mostly for vertical scrollbars */
//     height: 0px; /* Mostly for horizontal scrollbars */
//   }
//   ::-webkit-scrollbar-thumb {
//     background-image: linear-gradient(100deg, $darker-green 0%, $lighter-green 99%);
//     box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
//     border-radius: 0.3rem;
//   }
//   ::-webkit-scrollbar-track {
//     box-shadow: inset 2px 2px 4px 0 $soft-gray;
//     border-radius: 0.3rem;
//   }
//   ::-webkit-scrollbar-track-piece {
//     margin-top: 1rem;
//   }
</style>