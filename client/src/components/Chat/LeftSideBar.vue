<template>
  <div ref="leftsidebar" class="sidebar" :class="{ open: isOpen }">
    <section>
      <header class="right-bar-header">
        <div class="logo-header">
          <img src="@/assets/images/logo.png" height="26px" alt="" />
        </div>
      </header>

      <div class="body">
        <section class="left-section">
          <div :class="{ 'pad-l': !leftbarClosed }" class="pad-l-r">
            <div
              @click="changeView('home')"
              :class="{ 'active-view': currentView === 'home' }"
              class="menu-item"
            >
              <img src="@/assets/images/comment.svg" height="14px" alt="" />
            </div>
          </div>
        </section>

        <section class="left-section">
          <div :class="{ 'pad-l': !leftbarClosed }" class="pad-l-r">
            <div
              @click="changeView('pipeline')"
              :class="{ 'active-view pad-right': currentView !== 'home' }"
              class="menu-item"
            >
              <img src="@/assets/images/pipeline.svg" height="14px" alt="" />
            </div>

            <!-- <div
              :class="{
                'active-view': currentView.title === alert.title,
                inactive: !(alert.sobjectInstances && alert.sobjectInstances.length),
              }"
              v-for="(alert, i) in templates.list"
              :key="i"
              class="menu-item"
              @click="changeView(alert.title, alert, alert.sobjectInstances.length)"
            >
              <div class="right-margin"></div>
              <p>{{ alert.title }}</p>

              <div v-if="alert.sobjectInstances && alert.sobjectInstances.length" class="counter">
                <p>
                  {{ alert.sobjectInstances.length }}
                </p>
              </div>
            </div> -->
          </div>
        </section>
      </div>

      <footer>
        <div @click="handleConfigureOpen" class="menu-item">
          <img style="margin-left: -3px" src="@/assets/images/settings.svg" height="18px" alt="" />
        </div>
        <div @click="toggleTooltip" class="menu-item">
          <img src="@/assets/images/help.png" height="14px" alt="" />
        </div>
        <div class="menu-item" @click="handleProfileOpen">
          <img src="@/assets/images/profile.svg" height="14px" alt="" />
        </div>

        <div :class="{ 'showing-tooltip': showTooltip }" class="tooltip">
          <header>
            <p>Need help ?</p>

            <p @click="toggleTooltip">x</p>
          </header>
          <p>Email: cx@mymanagr.com</p>
        </div>
      </footer>
    </section>

    <div @click="toggleSidebar" v-if="isOpen" class="close">
      <font-awesome-icon
        style="height: 30px; width: 30px; color: white"
        icon="fa-solid fa-square-xmark"
      />
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users'
import { decryptData } from '../../encryption'

export default {
  name: 'LeftSideBar',
  props: {
    handleProfileOpen: { type: Function },
    handleConfigureOpen: { type: Function },
  },
  data() {
    return {
      leftbarClosed: true,
      showTooltip: false,
      isOpen: false,
      threadButtonText: 'Start New Thread',
      view: 'home',
      templates: CollectionManager.create({
        ModelClass: AlertTemplate,
        filters: { forPipeline: true },
      }),
      barOpen: true,
    }
  },
  mounted() {
    this.templates.refresh()
  },
  methods: {
    refreshList() {
      this.templates.refresh()
    },
    changeView(view, alert, length) {
      if (length || view === 'home' || view === 'pipeline') {
        this.view = view
        if (view === 'meetings') {
          this.$store.dispatch('loadMeetings')
        }
        if (alert) {
          this.$store.dispatch('setCurrentView', alert)
        } else {
          this.$store.dispatch('setCurrentView', view)
        }
      }
    },
    toggleSidebar() {
      this.isOpen = !this.isOpen

      if (this.isOpen) {
        this.$emit('show-background')
      } else {
        this.$emit('hide-background')
      }
    },
    toggleLeftbar() {
      this.leftbarClosed = !this.leftbarClosed
      this.$emit('toggle-Left-bar')
    },
    toggleTooltip() {
      this.showTooltip = !this.showTooltip
    },
    soonThreadText() {
      this.threadButtonText = 'Coming Soon!'
    },
    newThreadText() {
      this.threadButtonText = 'Start New Thread'
    },
    async sendNewEmailTest() {
      const data = {
        to: [{ name: 'Big Boy Bryan', email: 'bryan@mymanagr.com' }],
        subject: 'Mike, My Managur 100',
        body: `Hey Mike,<br><br>In the depths of a vast and troubled sea,<br>Where confusion reigns and darkness be,<br>I navigate the currents, lost and unsure,<br>Seeking clarity, yearning for a cure.<br><br>Oh, dear boss, hear my heartfelt plea,<br>For within this tempest, I long to break free.<br>I'm swimming in waves of uncertainty's tide,<br>Yet, still, I strive to keep my dreams alive.<br><br>In this churning abyss, I find no light,<br>Yet, I refuse to surrender without a fight.<br>With every stroke, I battle the unknown,<br>Aiming to carve a path uniquely my own.<br><br>The waters are deep, my vision unclear,<br>But I hold onto hope, suppressing my fear.<br>For though I'm surrounded by shadows and doubt,<br>I'm determined to rise, and find my way out.<br><br>Through the trials and tribulations I endure,<br>I promise, dear boss, to give nothing but pure,<br>Effort and dedication, a relentless drive,<br>To keep pushing forward, to truly thrive.<br><br>Though my path may be foggy, my steps unsure,<br>I'll keep striving, knowing I'm not obscure.<br>For in this sea of confusion and night,<br>I'll find strength within and shine with my might.<br><br>So, dear boss, please understand my plight,<br>That I'm doing my best, despite the fight.<br>In this vast ocean, I'm a swimmer indeed,<br>Working hard to succeed, planting a hopeful seed.<br><br>Through the waves of confusion and darkness, I go,<br>With every stroke, my determination does grow.<br>Trust in my resilience, for I'll never rest,<br>Until I conquer this sea and emerge at my best.<br><br>Poem written by ChatGPT.`,
      }
      const res = await User.api.sendNewEmail(data)
    },
  },
  computed: {
    currentView() {
      return this.$store.state.currentView
    },
    user() {
      const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return decryptedUser
    },
  },
  created() {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';

.sidebar {
  background-color: $off-white;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
  font-size: 14px;

  &.open {
    left: 0;
  }
}

.right-margin {
  margin-right: 1.75rem;
}

.pad-l-r {
  padding: 0 0.5rem;
}

.pad-l {
  padding: 0 0.25rem;

  div {
    margin-bottom: 0.5rem;
  }
}

.collapsed {
  margin-left: 1.25rem;
  margin-top: 1.25rem !important;
}

.inactive {
  opacity: 0.3;
  cursor: not-allowed !important;

  &:hover {
    opacity: 0.3 !important;
  }
}

.absolute-img {
  position: absolute;
  left: 1rem;
  top: 0.5rem;
  height: 100%;
  border-left: 1px solid rgba(0, 0, 0, 0.1);

  img {
    position: inherit;
    left: -8px;
    background-color: white;
    padding: 2px 0px;
    height: 22px;
  }
}

.active-view {
  background-color: $dark-green;
  border-radius: 5px;
  color: white;
  img {
    filter: invert(90%);
  }
}

.logo-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-left: 1rem;
  margin-top: 1rem;

  p {
    font-family: $base-font-family;
    color: $chat-font-color;
    font-size: 20px;
    color: $base-gray;
    margin: 0;
    -webkit-text-stroke: 0.2px white;
  }

  img {
    filter: brightness(0%) invert(65%) sepia(7%) saturate(2970%) hue-rotate(101deg) brightness(94%)
      contrast(89%);
    margin-right: 0.5rem;
  }
}

.right-bar-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pointer {
  cursor: pointer;
}

.large-font {
  font-size: 18px;
  padding: 0;
  margin: 0;
}

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

@media (max-width: 1000px) {
  .sidebar {
    position: absolute;
    left: -260px;

    &.open {
      left: 0;
      z-index: 999;
      background-color: $off-white;
    }
  }

  .close {
    display: block !important;
  }
}

.body {
  margin-top: 1rem;
  min-height: 66vh;
  overflow-y: scroll;
  overflow-x: hidden;
  text-overflow: ellipsis;
}

@media (max-height: 600px) {
  .body {
    min-height: 56vh;
  }
}

@media (max-height: 750px) {
  .body {
    min-height: 66vh;
  }
}

@media (min-height: 875px) {
  .body {
    min-height: 70vh;
  }
}

@media (min-height: 1025px) {
  .body {
    min-height: 75vh;
  }
}

@media (min-height: 1200px) {
  .body {
    min-height: 78vh;
  }
}

footer {
  position: fixed;
  bottom: 0;
  width: 260px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem 0 0.5rem 0.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.primary-button {
  @include chat-button();
  width: 100%;
  margin-bottom: 0.5rem;
  font-size: 12px;
  color: white;
  background-color: $base-gray;

  span {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    font-family: $base-font-family;
  }

  &:hover {
    cursor: not-allowed;
    opacity: 0.8;
    scale: none;
  }
}

.menu-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  font-size: 14px;
  padding: 0.625rem 0;
  padding-left: 1rem;
  cursor: pointer;
  position: relative;

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    margin: 0;
    width: 144px;
  }

  &:hover {
    opacity: 0.65;
  }
}

.counter {
  position: absolute;
  right: 1rem;
  background-color: $white-green;
  color: $dark-green;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;

  p {
    font-size: 12px;
    width: fit-content;
  }
}

// .empty {
//   background-color: $soft-gray;
//   color: $light-gray-blue;
// }

svg,
img {
  margin-right: 1rem;
}

.close {
  position: absolute;
  top: 0;
  left: 260px;
  top: 1.5rem;
  display: none;
  cursor: pointer;
}

.closedBar {
  position: absolute;
  left: 250px;
  z-index: 100;
  left: 100px;
  z-index: 10;
  left: 260px;
  top: 2px;
  padding-top: 0.5rem;

  img {
    z-index: 200;
    position: fixed;
    left: 0.25rem;
  }
}

.tooltip {
  display: block;
  width: 230px;
  height: auto;
  position: absolute;
  top: 0;
  left: 1rem;
  font-size: 14px;
  background: $base-gray;
  color: white;
  padding: 6px 8px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);

  header {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    p {
      margin: 0;
      padding: 0;
      margin-top: 0.25rem;
    }

    p:last-of-type {
      cursor: pointer;
      margin-top: -4px;
    }
  }
}

.tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $base-gray;
  bottom: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.showing-tooltip {
  top: -30px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.left-section {
  padding: 1rem 0;
  padding-bottom: 0;
}

.left-section:last-of-type {
  // border: none;
  // overflow-y: scroll;
  // overflow-x: none;
  // scroll-behavior: smooth;
  // height: 100%;
}

.left-section:last-of-type::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.left-section:last-of-type::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px !important;
}
.left-section:last-of-type:hover::-webkit-scrollbar-thumb {
  background-color: $base-gray;
}

.section-title {
  color: $light-gray-blue;
  padding-left: 1.25rem;
}

.img-spacing {
  margin-top: 0.75rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
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

.flexed-start {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-left: 0.5rem;
}
</style>