<template>
  <div class="reports">
    <div>
      <!-- <h1>Settings</h1> -->
      <h1>{{ user.fullName }} - Reports</h1>

      <div class="bar-header">
        <small
          @click="changeActivePage('reports')"
          class="pointer"
          :class="{ active: page === 'reports' }"
          >Reports</small
        >
        <!-- <small @click="changeActivePage('profile')" class="pointer" :class="{ active: page === 'profile' }">Profile</small> -->
      </div>

      <div v-if="page === 'reports'">

        <div class="row margin-top margin-bottom">
          <h3 class="team-width thin-font">Name</h3>
          <!-- <h3 class="team-width thin-font">Date</h3> -->
          <h3 class="team-width thin-font extra-mar-left">Share</h3>
        </div>

        <div v-for="report in reports" :key="report.share_url" class="row smaller-text">
          <div class="team-width thin-font">
            {{ report.title ? report.title : '[NO TITLE]' }}
          </div>
          <!-- <div class="team-width thin-font">
            {{ report.date ? report.date : '--' }}
          </div> -->
          <div @click="copyInvite(report.share_url)" class="invite-link-button-container wrapper thin-font">
            <img 
              src="@/assets/images/link.svg"
              class="invite-link-button"
            />
            <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import User from '@/services/users'

export default {
  name: 'PRReports',
  components: {

  },
  data() {
    return {
      page: 'reports',
      copyTip: 'Copy link',
      reports: [],
    }
  },
  async created() {
    await this.getReports()
  },
  methods: {
    async getReports() {
      try {
        const response = await User.api.getReports({ user: this.user.id })
        console.log('response', response)
        this.reports = response.results
      } catch (e) {
        console.log(e)
      }
    },
    async copyInvite(inv) {
      try {
        await navigator.clipboard.writeText(inv)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          // this.activationLink = ''
          this.copyTip = 'Copy link'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy invite: ', err)
      }
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  }
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/buttons';

.reports {
  padding: 96px 144px 32px 144px;
  height: 100vh;
  font-weight: 400;
  font-family: $base-font-family;
  color: $dark-black-blue;
}

.bar-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  position: sticky;
  top: 0;
  margin: 0;
  padding: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
  // height: 66px;
  // background-color: white;
  z-index: 10;
  font-family: $thin-font-family;

  small {
    font-size: 14px;
    margin-right: 2rem;
    color: $off-gray;
    padding: 16px 0;
  }
}

.input {
  width: 400px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 8px 16px;
  line-height: 1.75;
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family;
  font-weight: 400;
  border: 1px solid rgba(0, 0, 0, 0.1);
  resize: none;
  text-align: left;
  color: $dark-black-blue;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  // justify-content: space-between;
}

.primary-button {
  @include dark-blue-button();
  padding: 11px 12px;
  font-size: 13px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-border-button();
  padding: 11px 12px;
  font-size: 13px;
  border: 1px solid $soft-gray;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.vertical-margin {
  margin: 32px 0;
}

.active {
  color: $dark-black-blue !important;
  border-bottom: 0.75px solid $dark-black-blue;
}

.not-allowed {
  cursor: not-allowed;
}
.pointer {
  cursor: pointer;
}
h3 {
  margin: 0;
}
h1,
h3 {
  font-family: $thin-font-family;
}

.team-width {
  width: 10rem;
  padding: 8px 0;
  overflow-x: auto;
}
.border-right {
  border-right: 1px solid $soft-gray;
}
.profile-img {
  margin-top: 1rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: $off-white;
  border: 1px solid $soft-gray;
  border-radius: 100%;
  height: 120px;
  width: 120px;
}
.profile-name {
  position: absolute;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
  top: 88px;
  background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 12px;
}
.org-timezone-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 4px;
  // justify-content: center;
  font-size: 14px;
  p:first-of-type {
    margin-right: 0rem;
    // color: $grape;
    font-weight: bold;
  }
  p:last-of-type {
    margin-right: 0.5rem;
    color: $light-gray-blue;
  }
}
.small-gap {
  gap: 6px;
}
.underline {
  text-decoration: underline;
}
.smaller-text {
  font-size: 14px;
}
.margin-top {
  margin-top: 1rem;
}
.margin-bottom {
  margin-bottom: 0.25rem;
}
.thin-font {
  font-family: $thin-font-family;
}

.small-text {
  font-family: $thin-font-family;
  font-size: 15px;
}
.extra-margin-top {
  margin-top: 1.5rem;
}
.invite-link-button-container {
  background-color: $dark-black-blue;
  border-radius: 100%;
  width: 1.375rem;
  height: 1.375rem;
  margin-left: 4rem;
  cursor: pointer;
}
.invite-link-button {
  height: 14px;
  filter: invert(99%);
  margin: 0.25rem;
}
.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
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
  left: 53.5%;
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
.mar-left {
  margin-left: 1rem;
}
.extra-mar-left {
  margin-left: 3.5rem;
}
.display-flex {
  display: flex;
}
</style>