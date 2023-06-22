<template>
  <div ref="leftsidebar" class="sidebar" :class="{ open: isOpen }">
    <section>
      <header class="right-bar-header">
        <!-- <button @mouseenter="soonThreadText" @mouseleave="newThreadText" class="primary-button">
          <span style="font-size: 14px; margin-right: 1rem">🚀</span>
          <span> {{ threadButtonText }}</span>
        </button> -->
        <div class="logo-header">
          <img src="@/assets/images/logo.png" height="26px" alt="" />
        </div>

        <!-- <img class="img-spacing pointer" src="@/assets/images/collapse.svg" height="16px" alt="" /> -->
      </header>

      <div class="body">
        <section class="left-section">
          <p class="section-title">Today</p>

          <div>
            <div
              @click="changeView('home')"
              :class="{ 'active-view': currentView === 'home' }"
              class="menu-item"
            >
              <img src="@/assets/images/comment.svg" height="14px" alt="" />
              <p>Home</p>

              <!-- <div class="counter empty"><p>0</p></div> -->
            </div>

            <div
              @click="changeView('meetings')"
              :class="{ 'active-view': currentView === 'meetings' }"
              class="menu-item"
            >
              <img src="@/assets/images/calendar.svg" height="14px" alt="" />
              <p>Meetings</p>

              <!-- <div class="counter empty"><p>0</p></div> -->
            </div>
          </div>
        </section>

        <section class="left-section">
          <p class="section-title">List views</p>

          <div class="flexed-start" v-if="templates.refreshing">
            <div class="loading">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>

          <div v-else-if="templates.list.length">
            <div
              :class="{
                'active-view': currentView.title === alert.title,
                inactive: !(alert.sobjectInstances && alert.sobjectInstances.length),
              }"
              v-for="(alert, i) in templates.list"
              :key="i"
              class="menu-item"
              @click="changeView(alert.title, alert, alert.sobjectInstances.length)"
            >
              <img src="@/assets/images/hashtag.svg" height="12px" alt="" />
              <p>{{ alert.title }}</p>

              <div v-if="alert.sobjectInstances && alert.sobjectInstances.length" class="counter">
                <p>
                  {{ alert.sobjectInstances.length }}
                </p>
              </div>
            </div>
          </div>

          <div v-else>
            <div class="menu-item">
              <img src="@/assets/images/listed.svg" height="14px" alt="" />
              <p>No active lists</p>
            </div>
          </div>
        </section>
      </div>

      <footer>
        <div class="menu-item">
          <img style="margin-left: -3px" src="@/assets/images/settings.svg" height="18px" alt="" />
          <p>Settings</p>
        </div>
        <div @click="toggleTooltip" class="menu-item">
          <img src="@/assets/images/help.png" height="14px" alt="" />
          <p>Support</p>
        </div>
        <div class="menu-item" @click="handleProfileOpen">
          <img src="@/assets/images/profile.svg" height="14px" alt="" />
          <p>Profile</p>
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

export default {
  name: 'LeftSideBar',
  props: {
    handleProfileOpen: { type: Function },
  },
  data() {
    return {
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
    // console.log(this.templates)
  },
  methods: {
    refreshList() {
      this.templates.refresh()
    },
    changeView(view, alert, length) {
      if (length || view === 'home' || view === 'meetings') {
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
      this.barOpen = !this.barOpen

      if (this.barOpen) {
        console.log(this.barOpen)
      } else {
        console.log(this.barOpen)
      }
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
  },
  computed: {
    currentView() {
      return this.$store.state.currentView
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

.leftbarClosed {
  left: -280px;
  position: absolute;
}

.sidebar {
  background-color: white;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
  transition: all 0.3s ease;
  font-size: 14px;

  &.open {
    left: 0;
  }

  section {
    // padding: 1rem 1rem 0 1rem;
  }
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
    left: -280px;

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
  min-height: 66vh;
  padding: 0 1rem;
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
  width: 280px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 1rem 0 0.5rem 0;
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
  padding: 0.75rem 0;
  padding-left: 1.25rem;
  cursor: pointer;
  position: relative;

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    margin: 0;
    width: 150px;
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
  left: 280px;
  top: 1.5rem;
  display: none;
  cursor: pointer;
}

.tooltip {
  display: block;
  width: 250px;
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
  border: none;
  overflow-y: scroll;
  overflow-x: none;
  scroll-behavior: smooth;
  padding-top: 0;
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
  // padding-left: 1.25rem;
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